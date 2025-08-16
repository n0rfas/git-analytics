from collections import Counter, defaultdict
from typing import Dict

from git_analytics.entities import AnalyticsCommit


class HistoricalStatisticsAnalyzer:
    name = "historical_statistics"

    def __init__(self) -> None:
        self._dict_hour_of_day = defaultdict(Counter)
        self._dict_day_of_week = defaultdict(Counter)
        self._dict_day_of_month = defaultdict(Counter)

    def update(self, c: AnalyticsCommit) -> None:
        self._dict_day_of_week[c.committed_datetime.weekday()][c.commit_author] += 1
        self._dict_hour_of_day[c.committed_datetime.hour][c.commit_author] += 1
        self._dict_day_of_month[c.committed_datetime.day][c.commit_author] += 1

    def result(self) -> Dict[str, int]:
        return {
            "dict_hour_of_day": self._dict_hour_of_day,
            "dict_day_of_week": self._dict_day_of_week,
            "dict_day_of_month": self._dict_day_of_month,
        }
