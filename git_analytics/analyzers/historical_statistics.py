from dataclasses import dataclass, field
from typing import Dict

from git_analytics.entities import AnalyticsCommit, AnalyticsResult
from git_analytics.interfaces import CommitAnalyzer


@dataclass
class Result(AnalyticsResult):
    hour_of_day: Dict[int, Dict[str, int]] = field(default_factory=lambda: {h: {} for h in range(24)})
    day_of_week: Dict[str, Dict[str, int]] = field(
        default_factory=lambda: {d: {} for d in [_get_day_name(i) for i in range(7)]}
    )
    day_of_month: Dict[int, Dict[str, int]] = field(default_factory=lambda: {d: {} for d in range(1, 32)})


def _get_day_name(day_index: int) -> str:
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
        self._result = Result()

    def process(self, commit: AnalyticsCommit) -> None:
        author = commit.commit_author
        hour = commit.committed_datetime.hour
        day = commit.committed_datetime.weekday()
        month_day = commit.committed_datetime.day

        self._result.hour_of_day[hour][author] = self._result.hour_of_day[hour].get(author, 0) + 1
        day_name = _get_day_name(day)
        self._result.day_of_week[day_name][author] = self._result.day_of_week[day_name].get(author, 0) + 1
        self._result.day_of_month[month_day][author] = self._result.day_of_month[month_day].get(author, 0) + 1

    def result(self) -> Result:
        return self._result
