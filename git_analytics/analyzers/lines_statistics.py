from dataclasses import dataclass
from datetime import date
from typing import Dict, List

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
        self._daily_delta: Dict[date, int] = {}

    def process(self, commit: AnalyticsCommit) -> None:
        d = commit.committed_datetime.date()
        delta = commit.lines_insertions - commit.lines_deletions
        self._daily_delta[d] = self._daily_delta.get(d, 0) + delta

    def result(self) -> Result:
        items: List[LinesStatistics] = []
        total = 0
        for d in sorted(self._daily_delta.keys()):
            total += self._daily_delta[d]
            items.append(LinesStatistics(date=d, lines=total))
        return Result(items=items)
