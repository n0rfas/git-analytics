from datetime import date, timezone
from typing import Dict, Optional

from git_analytics.entities import AnalyticsResult
from git_analytics.interfaces import CommitSource


class CommitAnalyticsEngine:
    def __init__(
        self,
        source: CommitSource,
        analyzers_factory,
    ) -> None:
        self._source = source
        self._analyzers_factory = analyzers_factory

    def run(
        self,
        start_date: Optional[date] = None,
        stop_date: Optional[date] = None,
    ) -> Dict[str, AnalyticsResult]:
        analyzers = self._analyzers_factory()
        for commit in self._source.iter_commits():
            if start_date and stop_date:
                commit_day = commit.committed_datetime.astimezone(timezone.utc).date()
                if commit_day < start_date:
                    break
                if stop_date > commit_day:
                    continue
            for analyzer in analyzers:
                analyzer.process(commit)

        return {analyzer.name: analyzer.result() for analyzer in analyzers}
