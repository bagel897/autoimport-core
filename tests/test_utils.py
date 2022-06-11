"""Tests for autoimport utility functions, written in pytest"""

from __future__ import annotations

from pathlib import Path

from autoimport_core import _utils
from autoimport_core._defs import Package, PackageType
from autoimport_core.defs import Source


def test_get_package_source(mod1: Path, project: Path) -> None:
    assert _utils.get_package_source(mod1, project, "") == Source.PROJECT


def test_get_package_source_not_project(mod1: Path) -> None:
    assert _utils.get_package_source(mod1, None, "") == Source.UNKNOWN


def test_get_package_source_packaging(packaging_path: Path) -> None:
    # packaging is not installed as part of the standard library
    # but should be installed into site_packages,
    # so it should return Source.SITE_PACKAGE
    assert (
        _utils.get_package_source(packaging_path, None, "packaging")
        == Source.SITE_PACKAGE
    )


def test_get_package_source_typing(typing_path: Path) -> None:

    assert _utils.get_package_source(typing_path, None, "typing") == Source.STANDARD


def test_get_modname_project_no_add(mod1: Path, project: Path) -> None:

    assert _utils.get_modname_from_path(mod1, project, False) == "mod1"


def test_get_modname_single_file(typing_path: Path) -> None:

    assert _utils.get_modname_from_path(typing_path, typing_path) == "typing"


def test_get_modname_folder(
    packaging_path: Path, packaging_requirment_path: Path
) -> None:

    assert (
        _utils.get_modname_from_path(packaging_requirment_path, packaging_path)
        == "packaging.requirements"
    )


def test_get_package_tuple_sample(project: Path) -> None:
    assert Package(
        project.stem, Source.UNKNOWN, project, PackageType.STANDARD
    ) == _utils.get_package_tuple(project)


def test_get_package_tuple_typing(typing_path: Path) -> None:

    assert Package(
        "typing", Source.STANDARD, typing_path, PackageType.SINGLE_FILE
    ) == _utils.get_package_tuple(typing_path)


def test_get_package_tuple_compiled(zlib_path: Path) -> None:
    assert Package(
        "zlib", Source.STANDARD, zlib_path, PackageType.COMPILED
    ) == _utils.get_package_tuple(zlib_path)
