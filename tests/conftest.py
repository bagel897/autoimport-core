from __future__ import annotations

import pathlib
from pathlib import Path

import pytest

from autoimport_core import AutoImport


@pytest.fixture
def project(tmpdir) -> Path:
    project = Path(tmpdir)
    yield project


@pytest.fixture
def mod1(project: Path) -> Path:
    mod1 = project / "mod1.py"
    mod1.touch()
    yield mod1
    del mod1


@pytest.fixture
def mod2(project: Path) -> Path:
    package = project / "pkg"
    package.mkdir()
    mod2 = package / "mod2.py"
    mod2.touch()
    yield mod2
    del mod2
    del package


@pytest.fixture
def typing_path() -> Path:
    import typing

    yield pathlib.Path(typing.__file__)


@pytest.fixture
def packaging_requirment_path() -> Path:
    from packaging import requirements

    yield pathlib.Path(requirements.__file__)


@pytest.fixture
def packaging_path() -> Path:
    import packaging

    # Uses __init__.py so we need the parent

    yield pathlib.Path(packaging.__file__).parent


@pytest.fixture
def zlib_path() -> Path:
    import zlib

    yield pathlib.Path(zlib.__file__)


@pytest.fixture
def importer(project) -> AutoImport:
    autoimport = AutoImport(project)
    yield autoimport
    autoimport.close()
