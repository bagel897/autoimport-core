"""Internal definitions of types for the Autoimport program."""
from __future__ import annotations

import pathlib
from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple
from .defs import NameType, Source

@dataclass
class ModuleInfo:
    """Descriptor of information to get names from a module."""

    filepath: pathlib.Path | None
    modname: str
    underlined: bool
    process_imports: bool


@dataclass
class ModuleFile(ModuleInfo):
    """Descriptor of information to get names from a file using ast."""

    filepath: pathlib.Path
    modname: str
    underlined: bool
    process_imports: bool


@dataclass
class ModuleCompiled(ModuleInfo):
    """Descriptor of information to get names using imports."""

    filepath = None
    modname: str
    underlined: bool
    process_imports: bool


class PackageType(Enum):
    """Describes the type of package, to determine how to get the names from it."""

    BUILTIN = 0  # No file exists, compiled into python. IE: Sys
    STANDARD = 1  # Just a folder
    COMPILED = 2  # .so module
    SINGLE_FILE = 3  # a .py file


class Package(NamedTuple):
    """Attributes of a package."""

    name: str
    source: Source
    path: pathlib.Path | None
    type: PackageType


class Name(NamedTuple):
    """A Name to be added to the database."""

    name: str
    modname: str
    package: str
    source: Source
    name_type: NameType


class PartialName(NamedTuple):
    """Partial information of a Name."""

    name: str
    name_type: NameType
