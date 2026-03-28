from dataclasses import dataclass

from typing import Iterator
from git import InvalidGitRepositoryError, Repo, Commit
from datetime import datetime


@dataclass(frozen=True)
class CommitContext:
    commit: Commit
    commit_author: str
    committed_datetime: datetime


class InvalidGitRepositoryException(Exception):
    pass


class GitHistoryWalker:
    def __init__(
        self,
        path: str = ".",
        # branch: str = "main",  # TODO master/main autodetect
        since_days: int = 365,
    ) -> None:
        try:
            self._repo = Repo(path)
        except InvalidGitRepositoryError:
            raise InvalidGitRepositoryException(f"Error: '{path}' is not a git repository.")

        active_branch = self._repo.active_branch.name  # TODO master/main autodetect

        self._shas = self._repo.git.rev_list(
            f"--since={since_days}.days.ago",
            "--first-parent",
            "--reverse",
            active_branch,
        ).splitlines()

    @property
    def number_of_commits(self) -> int:
        return len(self._shas)

    def iter_commits(self) -> Iterator[Commit]:
        for sha in self._shas:
            yield self._repo.commit(sha)
