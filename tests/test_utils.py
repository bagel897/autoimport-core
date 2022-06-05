"""Tests for autoimport utility functions, written in pytest"""

from __future__ import annotations

from pathlib import Path

from autoimport_core import utils
from autoimport_core.defs import Package, PackageType, Source


def test_get_package_source(mod1: Path, project: Path) -> None:
    assert utils.get_package_source(mod1, project, "") == Source.PROJECT


def test_get_package_source_not_project(mod1: Path) -> None:
    assert utils.get_package_source(mod1, None, "") == Source.UNKNOWN


def test_get_package_source_pytoolconfig(pytoolconfig_path: Path) -> None:
    # pytest is not installed as part of the standard library
    # but should be installed into site_packages,
    # so it should return Source.SITE_PACKAGE
    assert (
        utils.get_package_source(pytoolconfig_path, None, "pytoolconfig")
        == Source.SITE_PACKAGE
    )


def test_get_package_source_typing(typing_path: Path) -> None:

    assert utils.get_package_source(typing_path, None, "typing") == Source.STANDARD


def test_get_modname_project_no_add(mod1: Path, project: Path) -> None:

    assert utils.get_modname_from_path(mod1, project, False) == "mod1"


def test_get_modname_single_file(typing_path: Path) -> None:

    assert utils.get_modname_from_path(typing_path, typing_path) == "typing"


def test_get_modname_folder(
    pytoolconfig_path: Path, pytoolconfig_documentation_path: Path
) -> None:

    assert (
        utils.get_modname_from_path(pytoolconfig_documentation_path, pytoolconfig_path)
        == "pytoolconfig.documentation"
    )


def test_get_package_tuple_sample(project: Path) -> None:
    assert Package(
        project.stem, Source.UNKNOWN, project, PackageType.STANDARD
    ) == utils.get_package_tuple(project)


def test_get_package_tuple_typing(typing_path: Path) -> None:

    assert Package(
        "typing", Source.STANDARD, typing_path, PackageType.SINGLE_FILE
    ) == utils.get_package_tuple(typing_path)


def test_get_package_tuple_compiled(zlib_path: Path) -> None:
    assert Package(
        "zlib", Source.STANDARD, zlib_path, PackageType.COMPILED
    ) == utils.get_package_tuple(zlib_path)
