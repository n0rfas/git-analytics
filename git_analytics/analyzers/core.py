from typing import Any, Dict, Iterable

from git_analytics.entities import AnalyticsCommit


# Protocol for commit analyzers
class CommitAnalyzer:
    name: str

    def update(self, commit: AnalyticsCommit) -> None: ...
    def result(self) -> Any: ...


class CommitAnalyticsRunner:
    def __init__(self, analyzers: Iterable[CommitAnalyzer]) -> None:
        self._analyzers = list(analyzers)

    def run(self, commits: Iterable[AnalyticsCommit]) -> Dict[str, Any]:
        for c in commits:
            for a in self._analyzers:
                a.update(c)
        return {a.name: a.result() for a in self._analyzers}

    def feed(self, c: AnalyticsCommit) -> None:
        for a in self._analyzers:
            a.update(c)

    def collect(self) -> Dict[str, Any]:
        return {a.name: a.result() for a in self._analyzers}
