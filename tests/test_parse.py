from __future__ import annotations

from pathlib import Path

from autoimport_core import Source
from autoimport_core._defs import Name, NameType, Package, PackageType, PartialName
from autoimport_core._parse import get_names_from_compiled, get_names_from_file


def test_typing_names(typing_path: Path) -> None:
    names = list(get_names_from_file(typing_path, "typing"))
    assert PartialName("Text", NameType.Variable) in names


def test_find_sys() -> None:
    package = Package("sys", Source.BUILTIN, None, PackageType.COMPILED)
    names = list(get_names_from_compiled(package))
    assert Name("exit", "sys", package, NameType.Function) in names


def test_find_underlined() -> None:
    package = Package("os", Source.BUILTIN, None, PackageType.COMPILED, underlined=True)
    names = list(get_names_from_compiled(package))
    assert Name("_exit", "os", package, NameType.Function) in names
