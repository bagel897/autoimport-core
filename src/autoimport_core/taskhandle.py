from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Sequence


class BaseJobSet(ABC):
    name: str = ""
    job_name: str = ""

    @abstractmethod
    def started_job(self, name: str) -> None:
        pass

    @abstractmethod
    def finished_job(self) -> None:
        pass

    @abstractmethod
    def check_status(self) -> None:
        pass

    @abstractmethod
    def get_percent_done(self) -> float | None:
        pass


class BaseTaskHandle(ABC):
    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def current_jobset(self) -> BaseJobSet | None:
        pass

    @abstractmethod
    def is_stopped(self) -> bool:
        pass

    @abstractmethod
    def get_jobsets(self) -> Sequence[BaseJobSet]:
        pass

    def create_jobset(
        self, name: str = "JobSet", count: int | None = None
    ) -> BaseJobSet:
        pass

    def _inform_observers(self) -> None:
        pass


class NullTaskHandle(BaseTaskHandle):
    def __init__(self) -> None:
        pass

    def is_stopped(self) -> bool:
        return False

    def stop(self) -> None:
        pass

    def create_jobset(
        self, name: str = "JobSet", count: int | None = None
    ) -> NullJobSet:
        return NullJobSet()

    def get_jobsets(self) -> list[BaseJobSet]:
        return []

    def current_jobset(self) -> None:
        """Return the current `JobSet`"""
        return None


class NullJobSet(BaseJobSet):
    def __init__(self, *args) -> None:
        pass

    def started_job(self, name: str) -> None:
        pass

    def finished_job(self) -> None:
        pass

    def check_status(self) -> None:
        pass

    def get_percent_done(self) -> None:
        pass
