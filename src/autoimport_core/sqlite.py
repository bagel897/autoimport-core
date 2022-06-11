"""AutoImport module for rope."""
from __future__ import annotations

import sqlite3
import sys
from collections import OrderedDict
from concurrent.futures import Future, ProcessPoolExecutor, as_completed
from itertools import chain
from pathlib import Path
from typing import Generator, Iterable

from pytoolconfig import PyToolConfig

from autoimport_core import taskhandle
from autoimport_core.defs import (
    ModuleFile,
    ModuleInfo,
    Name,
    NameType,
    Package,
    PackageType,
    SearchResult,
    Source,
)
from autoimport_core.parse import get_names
from autoimport_core.prefs import Prefs
from autoimport_core.utils import (
    get_files,
    get_modname_from_path,
    get_package_tuple,
    sort_and_deduplicate_tuple,
)


def _get_future_names(
    to_index: list[tuple[ModuleInfo, Package]],
    underlined: bool,
    job_set: taskhandle.BaseJobSet,
) -> Generator[Future[list[Name]], None, None]:
    """Get all names as futures."""
    with ProcessPoolExecutor() as executor:
        for module, package in to_index:
            job_set.started_job(module.modname)
            yield executor.submit(get_names, module, package)


def filter_packages(
    packages: Iterable[Package], underlined: bool, existing: list[str]
) -> Iterable[Package]:
    """Filter list of packages to parse."""
    if underlined:

        def filter_package(package: Package) -> bool:
            return package.name not in existing

    else:

        def filter_package(package: Package) -> bool:
            return package.name not in existing and not package.name.startswith("_")

    return filter(filter_package, packages)


class AutoImport:
    """A class for finding the module that provides a name.

    This class maintains a cache of global names in python modules.
    Note that this cache is not accurate and might be out of date.

    """

    _connection: sqlite3.Connection
    project: Path
    project_package: Package
    prefs: Prefs

    def __init__(
        self,
        project: Path,
        underlined: bool = False,
        index: str | None = None,
    ):
        """Construct an AutoImport object.

        Parameters
        ___________
        project : Path
            the project to use for project imports
        observe : bool
            if true, listen for project changes and update the cache.
        underlined : bool
            If `underlined` is `True`, underlined names are cached, too.
        index
            if None, don't persist to disk
        """
        self.project = project
        project_package = get_package_tuple(project, project)
        assert project_package is not None
        assert project_package.path is not None
        self.project_package = project_package
        self.underlined = underlined
        if index is None:
            index = ":memory:"
        self.connection = sqlite3.connect(index)
        self._setup_db()

        self.prefs = PyToolConfig("autoimport_core", project, Prefs).parse()
        # TODO add observer support

    def _setup_db(self) -> None:
        packages_table = "(package TEXT)"
        names_table = (
            "(name TEXT, module TEXT, package TEXT, source INTEGER, type INTEGER)"
        )
        self.connection.execute(f"create table if not exists names{names_table}")
        self.connection.execute(f"create table if not exists packages{packages_table}")
        self.connection.execute("CREATE INDEX IF NOT EXISTS name on names(name)")
        self.connection.execute("CREATE INDEX IF NOT EXISTS module on names(module)")
        self.connection.execute("CREATE INDEX IF NOT EXISTS package on names(package)")
        self.connection.commit()

    def search(self, name: str, exact_match: bool = False) -> list[tuple[str, str]]:
        """
        Search both modules and names for an import string.

        This is a simple wrapper around search_full with basic sorting based on Source.

        Returns a sorted list of import statement, modname pairs
        """
        results: list[tuple[str, str, int]] = [
            (statement, import_name, source)
            for statement, import_name, source, type in self.search_full(
                name, exact_match
            )
        ]
        return sort_and_deduplicate_tuple(results)

    def search_full(
        self,
        name: str,
        exact_match: bool = False,
        ignored_names: set[str] | None = None,
    ) -> Generator[SearchResult, None, None]:
        """
        Search both modules and names for an import string.

        Parameters
        __________
        name: str
            Name to search for
        exact_match: bool
            If using exact_match, only search for that name.
            Otherwise, search for any name starting with that name.
        ignored_names : Set[str]
            Will ignore any names in this set

        Return
        __________
        Unsorted Generator of SearchResults. Each is guaranteed to be unique.
        """
        results = set(self._search_name(name, exact_match))
        results = results.union(self._search_module(name, exact_match))
        if ignored_names is not None:
            for result in results:
                if result.name not in ignored_names:
                    yield result
        else:
            yield from results

    def _search_name(
        self, name: str, exact_match: bool = False
    ) -> Generator[SearchResult, None, None]:
        """
        Search both names for available imports.

        Returns the import statement, import name, source, and type.
        """
        if not exact_match:
            name = name + "%"  # Makes the query a starts_with query
        for import_name, module, source, name_type in self.connection.execute(
            "SELECT name, module, source, type FROM names WHERE name LIKE (?)", (name,)
        ):
            yield (
                SearchResult(
                    f"from {module} import {import_name}",
                    import_name,
                    source,
                    name_type,
                )
            )

    def _search_module(
        self, name: str, exact_match: bool = False
    ) -> Generator[SearchResult, None, None]:
        """
        Search both modules for available imports.

        Returns the import statement, import name, source, and type.
        """
        if not exact_match:
            name = name + "%"  # Makes the query a starts_with query
        for module, source in self.connection.execute(
            "Select module, source FROM names where module LIKE (?)",
            ("%." + name,),
        ):
            parts = module.split(".")
            import_name = parts[-1]
            remaining = parts[0]
            for part in parts[1:-1]:
                remaining += "."
                remaining += part
            yield (
                SearchResult(
                    f"from {remaining} import {import_name}",
                    import_name,
                    source,
                    NameType.Module.value,
                )
            )
        for module, source in self.connection.execute(
            "Select module, source from names where module LIKE (?)", (name,)
        ):
            if "." in module:
                continue
            yield SearchResult(
                f"import {module}", module, source, NameType.Module.value
            )

    def _dump_all(self) -> tuple[list[Name], list[Package]]:
        """Dump the entire database."""
        name_results = self.connection.execute("select * from names").fetchall()
        package_results = self.connection.execute("select * from packages").fetchall()
        return name_results, package_results

    def generate_cache(
        self,
        package_names: list[str] | None = None,
        files: list[Path] | None = None,
        underlined: bool = False,
        task_handle: taskhandle.BaseTaskHandle | None = None,
        single_thread: bool = False,
        remove_extras: bool = False,
    ) -> None:
        """
        This will work under 3 modes:
        1. packages or files are specified. Autoimport will only index these.
        2. PEP 621 is configured. Only these dependencies are indexed.
        3. Index only standard library modules.
        """
        if self.underlined:
            underlined = True
        if task_handle is None:
            task_handle = taskhandle.NullTaskHandle()
        packages: list[Package] = []
        existing = self._get_existing()
        to_index: list[tuple[ModuleInfo, Package]] = []
        if files is not None:
            assert package_names is None  # Cannot have both package_names and files.
            for file in files:
                to_index.append(
                    (self._path_to_module(file, underlined), self.project_package)
                )
        else:
            if package_names is None:
                packages = self._get_available_packages()
            else:
                for modname in package_names:
                    package = self._find_package_path(modname)
                    if package is None:
                        continue
                    packages.append(package)
            packages = list(filter_packages(packages, underlined, existing))
            for package in packages:
                for module in get_files(package, underlined):
                    to_index.append((module, package))
            self._add_packages(packages)
        if len(to_index) == 0:
            return
        job_set = task_handle.create_jobset(
            "Generating autoimport cache", len(to_index)
        )
        if single_thread:
            for module, package in to_index:
                job_set.started_job(module.modname)
                for name in get_names(module, package):
                    self._add_name(name)
                    job_set.finished_job()
        else:
            for future_name in as_completed(
                _get_future_names(to_index, underlined, job_set)
            ):
                self._add_names(future_name.result())
                job_set.finished_job()

        self.connection.commit()

    def close(self) -> None:
        """Close the autoimport database."""
        self.connection.commit()
        self.connection.close()

    def clear_cache(self) -> None:
        """Clear all entries in global-name cache.

        It might be a good idea to use this function before
        regenerating global names.

        """
        self.connection.execute("drop table names")
        self._setup_db()
        self.connection.commit()

    def update_path(self, path: Path, underlined: bool = False) -> None:
        """Update the cache for global names in `resource`."""
        underlined = underlined if underlined else self.underlined
        module = self._path_to_module(path, underlined)
        self._del_if_exist(module_name=module.modname, commit=False)
        self.generate_cache(files=[path], underlined=underlined)

    def _changed(self, path: Path) -> None:
        if not path.is_dir():
            self.update_path(path)

    def _moved(self, old_path: Path, new_path: Path) -> None:
        if not old_path.is_dir():
            modname = self._path_to_module(old_path).modname
            self._del_if_exist(modname)
            self.generate_cache(files=[new_path])

    def _del_if_exist(self, module_name: str, commit: bool = True) -> None:
        self.connection.execute("delete from names where module = ?", (module_name,))
        if commit:
            self.connection.commit()

    def _get_python_folders(self) -> list[Path]:
        def filter_folders(folder: Path) -> bool:
            return folder.is_dir() and folder.as_posix() != "/usr/bin"

        folders = sys.path
        folder_paths = map(lambda folder: Path(folder), folders)
        filtered_paths = filter(filter_folders, folder_paths)
        return list(OrderedDict.fromkeys(filtered_paths))

    def update_module(self, module: str) -> None:
        self.generate_cache(package_names=[module])

    def _get_available_packages(self) -> list[Package]:
        packages: list[Package] = [
            Package(module, Source.BUILTIN, None, PackageType.BUILTIN)
            for module in sys.builtin_module_names
        ]
        for folder in self._get_python_folders():
            for package in folder.iterdir():
                package_tuple = get_package_tuple(package, self.project)
                if package_tuple is None:
                    continue
                packages.append(package_tuple)
        return packages

    def _add_packages(self, packages: list[Package]) -> None:
        for package in packages:
            self.connection.execute("INSERT into packages values(?)", (package.name,))

    def _get_existing(self) -> list[str]:
        existing: list[str] = list(
            chain(*self.connection.execute("select * from packages").fetchall())
        )
        existing.append(self.project_package.name)
        return existing

    def remove(self, location: Path) -> None:
        if location.is_dir():
            for file in location.glob("*.py"):
                self.remove(file)
        else:
            modname = self._path_to_module(location).modname
            self._del_if_exist(modname)

    def _add_names(self, names: Iterable[Name]) -> None:
        for name in names:
            self._add_name(name)

    def _add_name(self, name: Name) -> None:
        self.connection.execute(
            "insert into names values (?,?,?,?,?)",
            (
                name.name,
                name.modname,
                name.package,
                name.source.value,
                name.name_type.value,
            ),
        )

    def _find_package_path(self, target_name: str) -> Package | None:
        if target_name in sys.builtin_module_names:
            return Package(target_name, Source.BUILTIN, None, PackageType.BUILTIN)
        for folder in self._get_python_folders():
            for package in folder.iterdir():
                package_tuple = get_package_tuple(package, self.project)
                if package_tuple is None:
                    continue
                name, source, package_path, package_type = package_tuple
                if name == target_name:
                    return package_tuple

        return None

    def _path_to_module(self, path: Path, underlined: bool = False) -> ModuleFile:
        assert self.project_package.path
        underlined = underlined if underlined else self.underlined
        # The project doesn't need its name added to the path,
        # since the standard python file layout accounts for that
        # so we set add_package_name to False
        resource_modname: str = get_modname_from_path(
            path, self.project_package.path, add_package_name=False
        )
        return ModuleFile(
            path,
            resource_modname,
            underlined,
            path.name == "__init__.py",
        )

    @property
    def _project_package(self) -> Package:
        result = get_package_tuple(self.project, self.project)
        assert result is not None
        return result
