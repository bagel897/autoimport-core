"""Internal definitions of types for the Autoimport program."""
from __future__ import annotations

import pathlib
from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple

from .defs import NameType, Source


@dataclass(frozen=True)
class ModuleInfo:
    """Descriptor of information to get names from a module."""

    filepath: pathlib.Path | None
    modname: str
    process_imports: bool


@dataclass(frozen=True)
class ModuleFile(ModuleInfo):
    """Descriptor of information to get names from a file using ast."""

    filepath: pathlib.Path
    modname: str
    process_imports: bool


@dataclass(frozen=True)
class ModuleCompiled(ModuleInfo):
    """Descriptor of information to get names using imports."""

    filepath = None
    modname: str
    process_imports: bool


class PackageType(Enum):
    """Describes the type of package, to determine how to get the names from it."""

    BUILTIN = 0  # No file exists, compiled into python. IE: Sys
    STANDARD = 1  # Just a folder
    COMPILED = 2  # .so module
    SINGLE_FILE = 3  # a .py file


@dataclass
class Package:
    """Attributes of a package."""

    name: str
    source: Source
    path: pathlib.Path | None
    type: PackageType
    modified: float
    underlined: bool
    indexed: bool = False


class Name(NamedTuple):
    """A Name to be added to the database."""

    name: str
    modname: str
    package: str
    source: Source
    name_type: NameType


@dataclass(frozen=True)
class PartialName:
    """Partial information of a Name."""

    name: str
    name_type: NameType
