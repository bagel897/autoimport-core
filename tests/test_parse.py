from __future__ import annotations

from autoimport_core import parse
from autoimport_core.defs import Name, NameType, PartialName, Source
from pathlib import Path

def test_typing_names(typing_path: Path) -> None:
    names = list(parse.get_names_from_file(typing_path))
    assert PartialName("Text", NameType.Variable) in names


def test_find_sys() -> None:
    names = list(parse.get_names_from_compiled("sys", Source.BUILTIN))
    assert Name("exit", "sys", "sys", Source.BUILTIN, NameType.Function) in names


def test_find_underlined() -> None:
    names = list(parse.get_names_from_compiled("os", Source.BUILTIN, underlined=True))
    assert Name("_exit", "os", "os", Source.BUILTIN, NameType.Function) in names
