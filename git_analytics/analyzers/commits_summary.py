from dataclasses import dataclass
from datetime import date
from typing import Optional, Set

from git_analytics.entities import AnalyticsCommit, AnalyticsResult
from git_analytics.interfaces import CommitAnalyzer


@dataclass
class Result(AnalyticsResult):
    date_first_commit: Optional[date] = None
    date_last_commit: Optional[date] = None
    total_number_commit: int = 0
    total_number_authors: int = 0


class CommitsSummaryAnalyzer(CommitAnalyzer):
    name = "commits_summary"

    def __init__(self) -> None:
        self._result = Result()
        self._authors: Set[str] = set()

    def process(self, commit: AnalyticsCommit) -> None:
        dt = commit.committed_datetime.date()
        if self._result.date_first_commit is None or dt < self._result.date_first_commit:
            self._result.date_first_commit = dt
        if self._result.date_last_commit is None or dt > self._result.date_last_commit:
            self._result.date_last_commit = dt
        self._result.total_number_commit += 1
        self._authors.add(commit.commit_author)

    def result(self) -> Result:
        self._result.total_number_authors = len(self._authors)
        return self._result
