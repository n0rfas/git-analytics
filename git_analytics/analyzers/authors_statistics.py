from collections import defaultdict
from dataclasses import dataclass
from typing import Dict

from git_analytics.entities import AnalyticsCommit, AnalyticsResult
from git_analytics.interfaces import CommitAnalyzer


@dataclass
class AuthorStatistics:
    commits: int = 0
    insertions: int = 0
    deletions: int = 0


@dataclass
class Result(AnalyticsResult):
    authors: Dict[str, AuthorStatistics]


class AuthorsStatisticsAnalyzer(CommitAnalyzer):
    name = "authors_statistics"

    def __init__(self) -> None:
        self._authors: Dict[str, AuthorStatistics] = defaultdict(AuthorStatistics)

    def process(self, commit: AnalyticsCommit) -> None:
        author: AuthorStatistics = self._authors[commit.commit_author]
        author.commits += 1
        author.insertions += commit.lines_insertions
        author.deletions += commit.lines_deletions

    def result(self) -> Result:
        return Result(authors=dict(self._authors))
