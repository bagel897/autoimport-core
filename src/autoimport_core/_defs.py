"""Internal definitions of types for the Autoimport program."""
from __future__ import annotations

import enum
import pathlib
from dataclasses import dataclass

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import declarative_base, relationship

from .defs import NameType, Source

Base = declarative_base()


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


class PackageType(enum.Enum):
    """Describes the type of package, to determine how to get the names from it."""

    BUILTIN = 0  # No file exists, compiled into python. IE: Sys
    STANDARD = 1  # Just a folder
    COMPILED = 2  # .so module
    SINGLE_FILE = 3  # a .py file


class Package(Base):
    """Attributes of a package."""

    __tablename__ = "packages"
    name: str = Column(String, primary_key=True)
    source: Source = Column(Enum(Source))
    _path: str | None = Column(String)
    type: PackageType = Column(Enum(PackageType))
    modified: float | None = Column(DateTime)
    underlined: bool = Column(Boolean)
    indexed: bool = Column(Boolean, default=False)
    names: list[Name] = relationship("Name")

    def __init__(
        self,
        name: str,
        source: Source,
        path: pathlib.Path | None,
        type: PackageType,
        modified: float | None = None,
        underlined: bool = False,
        indexed: bool = False,
    ):
        if modified is None and path is not None:
            modified = path.stat().st_mtime
        self.name = name
        self.source = source
        self._path = path.as_uri() if path is not None else None
        self.type = type
        self.underlined = underlined
        self.indexed = indexed

    @property
    def path(self) -> pathlib.Path | None:
        if self._path is None:
            return None
        return pathlib.Path(self._path)


class Name(Base):
    """A Name to be added to the database."""

    __tablename__ = "names"
    name: str = Column(String, primary_key=True)
    modname: str = Column(String, primary_key=True)
    package: Package = Column(String, ForeignKey("packages.name"))
    name_type: NameType = Column(Enum(NameType))

    def __init__(self, name: str, modname: str, package: Package, name_type: NameType):
        self.name = name
        self.modname = modname
        self.package = package
        self.name_type = name_type


@dataclass(frozen=True)
class PartialName:
    """Partial information of a Name."""

    name: str
    name_type: NameType
