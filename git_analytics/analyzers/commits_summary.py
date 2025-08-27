from dataclasses import dataclass
from datetime import date

from git_analytics.entities import AnalyticsCommit, AnalyticsResult
from git_analytics.interfaces import CommitAnalyzer


@dataclass
class Result(AnalyticsResult):
    date_first_commit: date
    date_last_commit: date
    total_number_commit: int
    total_number_authors: int


class CommitsSummaryAnalyzer(CommitAnalyzer):
    name = "commits_summary"

    def __init__(self) -> None:
        self._date_first_commit = None
        self._date_last_commit = None
        self._total_number_commit = 0
        self._list_authors = set()

    def process(self, commit: AnalyticsCommit) -> None:
        if (
            self._date_first_commit is None
            or commit.committed_datetime < self._date_first_commit
        ):
            self._date_first_commit = commit.committed_datetime
        if (
            self._date_last_commit is None
            or commit.committed_datetime > self._date_last_commit
        ):
            self._date_last_commit = commit.committed_datetime
        self._total_number_commit += 1
        self._list_authors.add(commit.commit_author)

    def result(self) -> Result:
        return Result(
            date_first_commit=self._date_first_commit.date(),
            date_last_commit=self._date_last_commit.date(),
            total_number_commit=self._total_number_commit,
            total_number_authors=len(self._list_authors),
        )
