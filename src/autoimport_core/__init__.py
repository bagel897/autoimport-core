"""AutoImport module for rope."""
from __future__ import annotations

from .defs import NameType, SearchResult, Source
from .sqlite import AutoImport

__version__ = "0.1.0"
__all__ = ["AutoImport", "SearchResult", "Source", "NameType"]
