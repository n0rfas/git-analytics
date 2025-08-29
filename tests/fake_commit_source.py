from typing import Iterator, List
from git_analytics.entities import AnalyticsCommit
from git_analytics.interfaces import CommitSource


class FakeCommitSource(CommitSource):
    def __init__(self, commits: List[AnalyticsCommit]) -> None:
        self._commits = commits

    def iter_commits(self) -> Iterator[AnalyticsCommit]:
        for commit in self._commits:
            yield commit
