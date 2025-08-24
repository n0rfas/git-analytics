from collections import Counter, defaultdict
from typing import Dict

from dataclasses import dataclass

from git_analytics.entities import AnalyticsCommit, AnalyticsResult
from git_analytics.interfaces import CommitAnalyzer


@dataclass
class Result(AnalyticsResult):
    hour_of_day: Dict[int, int]
    day_of_week: Dict[int, int]
    day_of_month: Dict[int, int]


class HistoricalStatisticsAnalyzer(CommitAnalyzer):
    name = "historical_statistics"

    def __init__(self) -> None:
        self._dict_hour_of_day = defaultdict(Counter)
        self._dict_day_of_week = defaultdict(Counter)
        self._dict_day_of_month = defaultdict(Counter)

    def process(self, commit: AnalyticsCommit) -> None:
        c = commit
        self._dict_day_of_week[c.committed_datetime.weekday()][c.commit_author] += 1
        self._dict_hour_of_day[c.committed_datetime.hour][c.commit_author] += 1
        self._dict_day_of_month[c.committed_datetime.day][c.commit_author] += 1

    def result(self) -> Result:
        return Result(
            hour_of_day={
                hour: sum(authors.values())
                for hour, authors in self._dict_hour_of_day.items()
            },
            day_of_week={
                day: sum(authors.values())
                for day, authors in self._dict_day_of_week.items()
            },
            day_of_month={
                day: sum(authors.values())
                for day, authors in self._dict_day_of_month.items()
            },
        )
