from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from git_analytics.entities import AnalyticsResult
from git_analytics.interfaces import CommitAnalyzer, CommitSource


class CommitAnalyticsEngine:
    def __init__(
        self,
        source: CommitSource,
        analyzers: List[CommitAnalyzer],
        default_time_interval: timedelta = timedelta(days=365),
    ) -> None:
        self._source = source
        self._analyzers = analyzers
        self._default_time_interval = default_time_interval

    def run(
        self,
        start_date: Optional[date] = None,
        stop_date: Optional[date] = None,
        time_interval: Optional[timedelta] = None,
    ) -> Dict[str, AnalyticsResult]:
        start_dt, stop_dt = self._resolve_window(start_date, stop_date, time_interval)

        for commit in self._source.iter_commits():
            dt = self._as_utc(commit.committed_datetime)
            if start_dt <= dt <= stop_dt:
                for analyzer in self._analyzers:
                    analyzer.process(commit)

        return {analyzer.name: analyzer.result() for analyzer in self._analyzers}

    def _resolve_window(
        self,
        start_date: Optional[datetime],
        stop_date: Optional[datetime],
        time_interval: Optional[timedelta],
    ) -> Tuple[datetime, datetime]:
        interval = time_interval or self._default_time_interval

        if start_date is None and stop_date is None:
            stop_date = datetime.now(timezone.utc)
            start_date = stop_date - interval
        elif start_date is None and stop_date is not None:
            start_date = stop_date - interval
        elif start_date is not None and stop_date is None:
            stop_date = start_date + interval

        start_dt = self._as_utc(start_date)
        stop_dt = self._as_utc(stop_date)

        return start_dt, stop_dt

    @staticmethod
    def _as_utc(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
