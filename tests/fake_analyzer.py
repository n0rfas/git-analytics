from dataclasses import dataclass, field
from typing import List

from git_analytics.entities import AnalyticsCommit, AnalyticsResult
from git_analytics.interfaces import CommitAnalyzer


@dataclass
class Result(AnalyticsResult):
    list_sha: List[str] = field(default_factory=list)


class FakeAnalyzer(CommitAnalyzer):
    name = "fake_analyzer"

    def __init__(self) -> None:
        self._result = Result()

    def process(self, commit: AnalyticsCommit) -> None:
        self._result.list_sha.append(commit.sha)

    def result(self) -> Result:
        return self._result
