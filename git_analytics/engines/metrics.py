from dataclasses import dataclass

import os

from pathlib import Path
from typing import Protocol, Dict, Iterator, Iterable, Optional, List, Tuple
from git import InvalidGitRepositoryError, Repo, Commit
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone


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

        active_branch = self._repo.active_branch.name

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


class MetricCollector(Protocol):
    name: str

    def consume(self, ctx: CommitContext) -> None: ...

    def build_report(self) -> object: ...


class ProgressReporter(Protocol):
    def start(self, total: int) -> None: ...
    def advance(self, current: int, total: int) -> None: ...
    def finish(self) -> None: ...


class ConsoleProgressReporter:
    def start(self, total: int) -> None:
        print(f"Processing {total} commits...")

    def advance(self, current: int, total: int) -> None:
        print(f"\rProcessing commits: {current}/{total}", end="", flush=True)

    def finish(self) -> None:
        print("\nProcessing completed.")


class MetricsEngine:
    def __init__(
        self,
        history: GitHistoryWalker,
        collectors: Iterable[MetricCollector],
        reporter: ProgressReporter = ConsoleProgressReporter(),
    ) -> None:
        self._history = history
        self._collectors = collectors
        self._reporter = reporter

    def run(self) -> Dict[str, object]:
        total = self._history.number_of_commits
        self._reporter.start(total=total)
        for current, commit in enumerate(self._history.iter_commits(), start=1):
            self._reporter.advance(current, total)
            ctx = self._build_commit_context(commit)

            for collector in self._collectors:
                collector.consume(ctx)
        self._reporter.finish()

        return {collector.name: collector.build_report() for collector in self._collectors}

    def _build_commit_context(self, commit: Commit) -> CommitContext:
        return CommitContext(
            commit=commit,
            commit_author=str(commit.author.name),
            committed_datetime=commit.committed_datetime,
        )
