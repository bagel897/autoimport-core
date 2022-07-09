from __future__ import annotations

from pathlib import Path

import pytest

from autoimport_core import AutoImport


def test_simple_case(importer: AutoImport) -> None:
    assert [] == importer.search("A")


def test_update_resource(importer: AutoImport, mod1: Path) -> None:
    with mod1.open("w") as f:
        f.write("myvar = None\n")
    importer.update_path(mod1)
    assert [("from mod1 import myvar", "myvar")] == importer.search("myva")


def test_update_non_existent_module(importer: AutoImport, project: Path) -> None:
    with pytest.raises(FileNotFoundError):
        importer.update_path(project / "does_not_exists_this")


def test_module_with_syntax_errors(
    importer: AutoImport, project: Path, mod1: Path
) -> None:
    with mod1.open(mode="w") as f:
        f.write("this is a syntax error\n")
    importer.update_path(mod1)
    assert [] == importer.search("myva")


def test_excluding_imported_names(importer: AutoImport, mod1: Path) -> None:
    with mod1.open(mode="w") as f:
        f.write("import pkg\n")
    importer.update_path(mod1)
    assert [] == importer.search("pkg")


def test_get_modules(importer: AutoImport, mod1: Path) -> None:
    with mod1.open(mode="w") as f:
        f.write("myvar = None\n")
    importer.update_path(mod1)
    assert [("from mod1 import myvar", "myvar")] == importer.search("myvar")


def test_get_modules_inside_packages(
    importer: AutoImport, mod1: Path, mod2: Path
) -> None:
    with mod1.open(mode="w") as f:
        f.write("myvar = None\n")
    with mod2.open(mode="w") as f:
        f.write("myvar = None\n")
    importer.update_path(mod1)
    importer.update_path(mod2)
    assert {
        ("from mod1 import myvar", "myvar"),
        ("from pkg.mod2 import myvar", "myvar"),
    } == set(importer.search("myvar"))


def test_empty_cache(importer: AutoImport, mod1: Path) -> None:
    with mod1.open(mode="w") as f:
        f.write("myvar = None\n")
    importer.update_path(mod1)
    assert [("from mod1 import myvar", "myvar")] == importer.search("myvar")
    importer.clear_cache()
    assert [] == importer.search("myvar")


def test_not_caching_underlined_names(importer: AutoImport, mod1: Path) -> None:
    with mod1.open(mode="w") as f:
        f.write("_myvar = None\n")
    importer.update_path(mod1, underlined=False)
    assert [] == importer.search("_myvar")
    importer.update_path(mod1, underlined=True)
    assert [("from mod1 import _myvar", "_myvar")] == importer.search("_myvar")


def test_caching_underlined_names_passing_to_the_constructor(
    mod1: Path, project: Path
) -> None:
    importer = AutoImport(project, True, None)
    with mod1.open(mode="w") as f:
        f.write("_myvar = None\n")
    importer.update_path(mod1)
    assert [("from mod1 import _myvar", "_myvar")] == importer.search("_myvar")


def test_handling_builtin_modules(importer: AutoImport) -> None:
    importer.update_module("sys")
    assert [("from sys import exit", "exit")] == importer.search("exit")


def test_search_submodule(importer: AutoImport) -> None:
    importer.update_module("packaging")
    import_statement = ("from packaging import requirements", "requirements")
    assert import_statement in importer.search("requirements", exact_match=True)
    assert import_statement in importer.search("requirements")
    assert import_statement in importer.search("requirements")


def test_search_module(importer: AutoImport) -> None:
    importer.update_module("os")
    import_statement = ("import os", "os")
    assert import_statement in importer.search("os", exact_match=True)
    assert import_statement in importer.search("os")
    assert import_statement in importer.search("o")


def test_search(importer: AutoImport) -> None:
    importer.update_module("typing")
    import_statement = ("from typing import Dict", "Dict")
    assert import_statement in importer.search("Dict", exact_match=True)
    assert import_statement in importer.search("Dict")
    assert import_statement in importer.search("Dic")
    assert import_statement in importer.search("Di")
    assert import_statement in importer.search("D")


def test_generate_full_cache(importer: AutoImport) -> None:
    # The single thread test takes much longer than the multithread test
    # but it is easier to debug
    single_thread = False
    importer._generate_cache(single_thread=single_thread)
    assert ("from typing import Dict", "Dict") in importer.search("Dict")
    assert len(importer._dump_all()) > 0
    for table in importer._dump_all():
        assert len(table) > 0
