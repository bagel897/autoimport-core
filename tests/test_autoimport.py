from __future__ import annotations

from pathlib import Path

from autoimport_core import AutoImport


def test_simple_case(importer: AutoImport) -> None:
    assert [] == importer.search("A")


def test_update_resource(importer: AutoImport, mod1: Path) -> None:
    with mod1.open("w") as f:
        f.write("myvar = None\n")
    importer.update_path(mod1)
    assert "from mod1 import myvar" == importer.search("myva")


def test_update_non_existent_module(importer: AutoImport, project: Path) -> None:
    importer.update_pathproject / "does_not_exists_this"
    assert [] == importer.search("myva")


def test_module_with_syntax_errors(
    importer: AutoImport, project: Path, mod1: Path
) -> None:
    mod1.write("this is a syntax error\n")
    importer.update_path(mod1)
    assert [] == importer.search("myva")


def test_excluding_imported_names(importer: AutoImport, mod1: Path) -> None:
    mod1.write("import pkg\n")
    importer.update_path(importer.mod1)
    assert [] == importer.search("pkg")


def test_get_modules(importer: AutoImport) -> None:
    mod1.write("myvar = None\n")
    importer.update_path(importer.mod1)
    assert ["mod1"] == importer.get_modules("myvar")


def test_get_modules_inside_packages(importer: AutoImport, mod1: Path) -> None:
    mod1.write("myvar = None\n")
    mod2.write("myvar = None\n")
    importer.update_path(importer.mod1)
    importer.update_path(importer.mod2)
    assert {"mod1", "pkg.mod2"} == set(importer.get_modules("myvar"))


def test_empty_cache(importer: AutoImport, mod1: Path) -> None:
    mod1.write("myvar = None\n")
    importer.update_path(importer.mod1)
    assert ["mod1"] == importer.get_modules("myvar")
    importer.clear_cache()
    assert [] == importer.get_modules("myvar")


def test_not_caching_underlined_names(importer: AutoImport, mod1: Path) -> None:
    mod1.write("_myvar = None\n")
    importer.update_path(importer.mod1, underlined=False)
    assert [] == importer.get_modules("_myvar")
    importer.update_path(importer.mod1, underlined=True)
    assert ["mod1"] == importer.get_modules("_myvar")


def test_caching_underlined_names_passing_to_the_constructor(
    mod1: Path, project: Path
) -> None:
    importer = autoimport.AutoImport(project, False, True)
    mod1.write("_myvar = None\n")
    importer.update_path(mod1)
    assert ["mod1"] in importer.get_modules("_myvar")


def test_handling_builtin_modules(importer: AutoImport) -> None:
    importer.update_module("sys")
    assert "sys" in importer.get_modules("exit")


def test_search_submodule(importer: AutoImport) -> None:
    importer.update_module("build")
    import_statement = ("from build import env", "env")
    assert import_statement in importer.search("env", exact_match=True)
    assert import_statement in importer.search("en")
    assert import_statement in importer.search("env")


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
    """The single thread test takes much longer than the multithread test but is easier to debug"""
    single_thread = False
    importer.generate_modules_cache(single_thread=single_thread)
    assert ("from typing import Dict", "Dict") in importer.search("Dict")
    assert len(importer._dump_all()) > 0
    for table in importer._dump_all():
        assert len(table) > 0
