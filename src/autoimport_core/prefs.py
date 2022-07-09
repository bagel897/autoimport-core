from __future__ import annotations

import sys
from dataclasses import dataclass

from packaging.requirements import Requirement
from pytoolconfig import UniversalKey, field


@dataclass
class Prefs:
    underlined: str = field(
        default="project", description="Can be 'project', 'none', or 'all'"
    )
    dependencies: list[str] | None = field(default=None, init=False)
    _dependencies: list[Requirement] | None = field(
        universal_config=UniversalKey.dependencies, default=None
    )
    _optional_dependencies: dict[str, list[Requirement]] | None = field(
        universal_config=UniversalKey.optional_dependencies, default=None
    )

    def __post_init__(self) -> None:
        if self._dependencies is None:
            if sys.version_info >= (3, 10, 0):
                self.dependencies = sys.stdlib_module_names
        else:
            self.dependencies = [requirement.name for requirement in self._dependencies]
            if self._optional_dependencies is not None:
                for dependency_group in self._optional_dependencies.values():
                    self.dependencies.extend(
                        [requirement.name for requirement in dependency_group]
                    )
