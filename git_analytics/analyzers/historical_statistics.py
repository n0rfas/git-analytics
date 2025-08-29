from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict

from git_analytics.entities import AnalyticsCommit, AnalyticsResult
from git_analytics.interfaces import CommitAnalyzer


@dataclass
class Result(AnalyticsResult):
    hour_of_day: Dict[int, int]
    day_of_week: Dict[str, int]
    day_of_month: Dict[int, int]


def get_day_name(day_index: int) -> str:
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    return days[day_index]


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
        hour_of_day = {hour: 0 for hour in range(24)}
        for hour, authors in self._dict_hour_of_day.items():
            hour_of_day[hour] = dict(authors)

        day_of_week = {get_day_name(day): 0 for day in range(7)}
        for day, authors in self._dict_day_of_week.items():
            day_of_week[get_day_name(day)] = dict(authors)

        day_of_month = {day: 0 for day in range(1, 32)}
        for day, authors in self._dict_day_of_month.items():
            day_of_month[day] = dict(authors)

        return Result(
            hour_of_day=hour_of_day,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
        )
