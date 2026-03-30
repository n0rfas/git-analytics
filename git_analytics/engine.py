from typing import Dict, Iterable, Protocol

from git import Commit

from .history import CommitContext, GitHistoryWalker


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
