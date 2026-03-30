from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from git_analytics.history import CommitContext


class WeeklyCollector(ABC):
    def __init__(self):
        self._weeks_data: Dict[str, List[Any]] = {}
        self._min_date: Optional[datetime] = None
        self._max_date: Optional[datetime] = None

    def consume(self, ctx: CommitContext) -> None:
        commit_date = ctx.committed_datetime
        if self._min_date is None or commit_date < self._min_date:
            self._min_date = commit_date
        if self._max_date is None or commit_date > self._max_date:
            self._max_date = commit_date

        week_key = self._get_week_key(commit_date)

        if week_key not in self._weeks_data:
            self._weeks_data[week_key] = []

        self._aggregate_commit(week_key, ctx)

    @abstractmethod
    def _aggregate_commit(self, week_key: str, ctx: CommitContext) -> None:
        pass

    def build_report(self) -> Dict[str, List[Any]]:
        if self._min_date is None or self._max_date is None:
            return {}

        all_weeks = self._generate_week_range(self._min_date, self._max_date)

        result = {}
        for week_key in all_weeks:
            result[week_key] = self._weeks_data.get(week_key, [])

        return result

    @staticmethod
    def _get_week_key(dt: datetime) -> str:
        iso_year, iso_week, _ = dt.isocalendar()
        return f"{iso_year % 100:02d}W{iso_week:02d}"

    @staticmethod
    def _generate_week_range(start: datetime, end: datetime) -> List[str]:
        from datetime import timedelta

        weeks = []
        current = start

        while current <= end:
            week_key = WeeklyCollector._get_week_key(current)
            if not weeks or weeks[-1] != week_key:
                weeks.append(week_key)
            current += timedelta(days=7)

        return weeks
