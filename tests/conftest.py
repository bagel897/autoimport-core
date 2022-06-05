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
    mod1 = project / "mod1"
    mod1.touch()
    yield mod1
    del mod1


@pytest.fixture
def typing_path() -> Path:
    import typing

    yield pathlib.Path(typing.__file__)


@pytest.fixture
def pytoolconfig_documentation_path() -> Path:
    from pytoolconfig import documentation

    yield pathlib.Path(documentation.__file__)


@pytest.fixture
def pytoolconfig_path() -> Path:
    import pytoolconfig

    # Uses __init__.py so we need the parent

    yield pathlib.Path(pytoolconfig.__file__).parent


@pytest.fixture
def zlib_path() -> Path:
    import zlib

    yield pathlib.Path(zlib.__file__)


@pytest.fixture
def importer(project) -> AutoImport:
    autoimport = AutoImport(project)
    yield autoimport
    autoimport.close()
