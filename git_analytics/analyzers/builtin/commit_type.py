from collections import Counter, defaultdict
from typing import Dict

from git_analytics.entities import AnalyticsCommit, CommitType

TYPE_COMMIT_LIST: tuple = tuple(ct.value for ct in CommitType)


def _get_type_list(commit_message: str):
    return [tag for tag in TYPE_COMMIT_LIST if tag in commit_message]


class CommitTypeAnalyzer:
    name = "commit_type"

    def __init__(self) -> None:
        self._commit_types_by_date = defaultdict(Counter)

    def update(self, c: AnalyticsCommit) -> None:
        commit_types = _get_type_list(c.message)
        for commit_type in commit_types:
            self._commit_types_by_date[c.committed_datetime.date()][commit_type] += 1

    def result(self) -> Dict[str, int]:
        return self._commit_types_by_date
