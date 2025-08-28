from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Dict

from git_analytics.entities import AnalyticsCommit, AnalyticsResult
from git_analytics.interfaces import CommitAnalyzer


class CommitType(Enum):
    FEATURE = "feature"
    FIX = "fix"
    DOCS = "docs"
    STYLE = "style"
    REFACTOR = "refactor"
    TEST = "test"
    CHORE = "chore"
    WIP = "wip"
    MERGE = "merge"
    UNKNOWN = "unknown"


@dataclass
class Result(AnalyticsResult):
    items: Dict[date, Dict[str, int]]


TYPE_COMMIT_LIST: tuple = tuple(ct.value for ct in CommitType)


def _get_type_list(commit_message: str):
    result = [tag for tag in TYPE_COMMIT_LIST if tag in commit_message]
    if result:
        return result
    return [CommitType.UNKNOWN.value]


class CommitTypeAnalyzer(CommitAnalyzer):
    name = "commit_type"

    def __init__(self) -> None:
        self._commit_types_by_date = defaultdict(Counter)

    def process(self, commit: AnalyticsCommit) -> None:
        commit_types = _get_type_list(commit.message)
        for commit_type in commit_types:
            self._commit_types_by_date[commit.committed_datetime.date()][
                commit_type
            ] += 1

    def result(self) -> Result:
        days = defaultdict(dict)
        for dt, st in self._commit_types_by_date.items():
            days[str(dt)] = dict(st)

        return Result(items=dict(days))
