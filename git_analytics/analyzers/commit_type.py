from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, List

from git_analytics.entities import AnalyticsCommit, AnalyticsResult
from git_analytics.helpers import get_number_week
from git_analytics.interfaces import CommitAnalyzer


@dataclass
class Result(AnalyticsResult):
    commit_type_by_week: Dict[str, Dict[str, int]]
    commit_type_counter: Dict[str, int]
    author_commit_type_by_week: Dict[str, Dict[str, Dict[str, int]]]
    author_commit_type_counter: Dict[str, Dict[str, int]]


LIST_OF_TYPE_COMMIT: List[str] = ["feature", "fix", "docs", "style", "refactor", "test", "chore", "wip", "merge"]


def _get_type_list(commit_message: str) -> List[str]:
    result = [tag for tag in LIST_OF_TYPE_COMMIT if tag in commit_message.lower()]
    if result:
        return result
    return ["unknown"]


class CommitTypeAnalyzer(CommitAnalyzer):
    name = "commit_type"

    def __init__(self) -> None:
        self._commit_type_by_week: Dict[str, Counter] = defaultdict(Counter)
        self._commit_type_counter: Counter = Counter()
        self._author_commit_type_by_week: Dict[str, Dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
        self._author_commit_type_counter: Dict[str, Counter] = defaultdict(Counter)

    def process(self, commit: AnalyticsCommit) -> None:
        week_number = get_number_week(commit.committed_datetime)
        commit_types = _get_type_list(commit.message)
        for commit_type in commit_types:
            self._commit_type_by_week[week_number][commit_type] += 1
            self._commit_type_counter[commit_type] += 1
            self._author_commit_type_by_week[commit.commit_author][week_number][commit_type] += 1
            self._author_commit_type_counter[commit.commit_author][commit_type] += 1

    def result(self) -> Result:
        return Result(
            commit_type_by_week={wn: dict(sorted(c.items())) for wn, c in sorted(self._commit_type_by_week.items())},
            commit_type_counter=dict(sorted(self._commit_type_counter.items())),
            author_commit_type_by_week={
                a: {wn: dict(sorted(c.items())) for wn, c in sorted(weeks.items())}
                for a, weeks in sorted(self._author_commit_type_by_week.items())
            },
            author_commit_type_counter={
                a: dict(sorted(c.items())) for a, c in sorted(self._author_commit_type_counter.items())
            },
        )
