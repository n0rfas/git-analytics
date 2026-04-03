from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterator, Optional

from git import InvalidGitRepositoryError, Repo
from git.objects.commit import Commit


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
        since_days: Optional[int] = None,
        since_date: Optional[date] = None,
        until_date: Optional[date] = None,
    ) -> None:
        try:
            self._repo = Repo(path)
        except InvalidGitRepositoryError:
            raise InvalidGitRepositoryException(f"Error: '{path}' is not a git repository.")

        active_branch = self._repo.active_branch.name  # TODO master/main autodetect

        args = []

        if since_date:
            args.append(f"--since={since_date.isoformat()}")
        elif since_days:
            args.append(f"--since={since_days}.days.ago")

        if until_date:
            args.append(f"--until={until_date.isoformat()}")

        args.extend(["--first-parent", "--reverse", active_branch])

        self._shas = self._repo.git.rev_list(*args).splitlines()

    @property
    def number_of_commits(self) -> int:
        return len(self._shas)

    def iter_commits(self) -> Iterator[Commit]:
        for sha in self._shas:
            yield self._repo.commit(sha)
