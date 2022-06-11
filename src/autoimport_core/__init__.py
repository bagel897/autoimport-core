"""AutoImport module for rope."""
from __future__ import annotations

from .sqlite import AutoImport
from .defs import SearchResult, Source, NameType
__version__ = "0.1.0"
__all__ = ["AutoImport", "SearchResult", "Source", "NameType"]
