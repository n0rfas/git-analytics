from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import List

from git_analytics.entities import AnalyticsCommit, AnalyticsResult
from git_analytics.interfaces import CommitAnalyzer


@dataclass
class LinesStatistics:
    date: date
    lines: int


@dataclass
class Result(AnalyticsResult):
    items: List[LinesStatistics]


class LinesAnalyzer(CommitAnalyzer):
    name = "lines_statistics"

    def __init__(self) -> None:
        self._lines_in_day = {}

    def process(self, commit: AnalyticsCommit) -> None:
        self._lines_in_day[commit.committed_datetime] = (
            commit.lines_insertions - commit.lines_deletions
        )

    def result(self) -> Result:
        dict_number_lines = defaultdict(int)

        old_rows = 0
        sort_day = list(self._lines_in_day.keys())
        sort_day.sort()
        for day in sort_day:
            number_rows = self._lines_in_day[day]
            dict_number_lines[day] = old_rows + number_rows
            old_rows = old_rows + number_rows

        return Result(
            items=[
                LinesStatistics(date=day.date(), lines=lines)
                for day, lines in dict_number_lines.items()
            ]
        )
