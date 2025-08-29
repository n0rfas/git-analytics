from abc import ABC, abstractmethod
from typing import Iterator

from git_analytics.entities import AnalyticsCommit, AnalyticsResult


class CommitSource(ABC):
    @abstractmethod
    def iter_commits(self) -> Iterator[AnalyticsCommit]: ...


class CommitAnalyzer(ABC):
    name: str

    @abstractmethod
    def process(self, commit: AnalyticsCommit) -> None: ...

    @abstractmethod
    def result(self) -> AnalyticsResult: ...
