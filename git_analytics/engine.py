from datetime import date, timezone
from typing import Any, Dict, Optional

from git_analytics.entities import AnalyticsResult
from git_analytics.interfaces import CommitSource


class CommitAnalyticsEngine:
    def __init__(
        self,
        source: CommitSource,
        analyzers_factory,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._source = source
        self._analyzers_factory = analyzers_factory
        self._additional_data = additional_data

    def run(
        self,
        start_date: Optional[date] = None,
        stop_date: Optional[date] = None,
    ) -> Dict[str, AnalyticsResult]:
        analyzers = self._analyzers_factory()

        if start_date and stop_date and start_date > stop_date:
            start_date, stop_date = stop_date, start_date

        for commit in self._source.iter_commits():
            commit_day = commit.committed_datetime.astimezone(timezone.utc).date()

            if stop_date and commit_day > stop_date:
                continue

            if start_date and commit_day < start_date:
                break

            for analyzer in analyzers:
                analyzer.process(commit)

        result = {analyzer.name: analyzer.result() for analyzer in analyzers}
        if self._additional_data:
            result["additional_data"] = self._additional_data
        return result
