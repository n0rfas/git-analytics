from typing import Iterator

from git import Repo
from git.objects import Commit

from git_analytics.entities import AnalyticsCommit
from git_analytics.interfaces import CommitSource


class GitCommitSource(CommitSource):
    def __init__(self, repo: Repo) -> None:
        self._repo = repo

    def iter_commits(self) -> Iterator[AnalyticsCommit]:
        for commit in self._repo.iter_commits():
            yield self.git_commit_to_analytics_commit(commit)

    @staticmethod
    def git_commit_to_analytics_commit(commit: Commit) -> AnalyticsCommit:
        return AnalyticsCommit(
            sha=commit.hexsha,
            commit_author=str(commit.author.name),
            committed_datetime=commit.committed_datetime,
            lines_insertions=commit.stats.total["insertions"],
            lines_deletions=commit.stats.total["deletions"],
            files_changed=commit.stats.total["files"],
            message=str(commit.summary).strip(),
        )
