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
        self._dict_authors = defaultdict(AuthorStatistics)

    def process(self, commit: AnalyticsCommit) -> None:
        author = self._dict_authors[commit.commit_author]
        author.commits += 1
        author.insertions += commit.lines_insertions
        author.deletions += commit.lines_deletions

    def result(self) -> Result:
        return Result(
            authors={
                name: AuthorStatistics(
                    commits=st.commits,
                    insertions=st.insertions,
                    deletions=st.deletions,
                )
                for name, st in self._dict_authors.items()
            }
        )
