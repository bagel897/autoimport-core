"""Definitions of types for the Autoimport program."""
from __future__ import annotations

from enum import Enum
from typing import NamedTuple


class Source(Enum):
    """Describes the source of the package, for sorting purposes."""

    PROJECT = 0  # Obviously any project packages come first
    MANUAL = 1  # Placeholder since Autoimport classifies manually added modules
    BUILTIN = 2
    STANDARD = 3  # We want to favor standard library items
    SITE_PACKAGE = 4
    UNKNOWN = 5


class NameType(Enum):
    """Describes the type of Name for lsp completions. Taken from python lsp server."""

    Text = 1
    Method = 2
    Function = 3
    Constructor = 4
    Field = 5
    Variable = 6
    Class = 7
    Interface = 8
    Module = 9
    Property = 10
    Unit = 11
    Value = 12
    Enum = 13
    Keyword = 14
    Snippet = 15
    Color = 16
    File = 17
    Reference = 18
    Folder = 19
    EnumMember = 20
    Constant = 21
    Struct = 22
    Event = 23
    Operator = 24
    TypeParameter = 25


class SearchResult(NamedTuple):
    """Search Result."""

    import_statement: str
    name: str
    source: Source
    itemkind: NameType
