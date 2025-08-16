from collections import defaultdict
from typing import Dict

from git_analytics.entities import AnalyticsCommit


class LinesAnalyzer:
    name = "lines_statistics"

    def __init__(self) -> None:
        self._lines_in_day = {}

    def update(self, c: AnalyticsCommit) -> None:
        self._lines_in_day[c.committed_datetime] = (
            c.lines_insertions - c.lines_deletions
        )

    def result(self) -> Dict[str, int]:
        dict_number_lines = defaultdict(int)

        old_rows = 0
        sort_day = list(self._lines_in_day.keys())
        sort_day.sort()
        for day in sort_day:
            number_rows = self._lines_in_day[day]
            dict_number_lines[day] = old_rows + number_rows
            old_rows = old_rows + number_rows

        return [
            {"date": int(date.timestamp()), "value": value}
            for date, value in dict_number_lines.items()
        ]
