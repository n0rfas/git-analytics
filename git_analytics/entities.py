from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any, Dict


@dataclass
class AnalyticsCommit:
    sha: str
    commit_author: str
    committed_datetime: datetime
    lines_insertions: int
    lines_deletions: int
    files_changed: int
    message: str


@dataclass
class AnalyticsResult:
    def to_dict(self) -> Dict[str, Any]:
        return self._make_json_safe(asdict(self))

    @staticmethod
    def _make_json_safe(obj):
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, list):
            return [AnalyticsResult._make_json_safe(x) for x in obj]
        if isinstance(obj, dict):
            return {k: AnalyticsResult._make_json_safe(v) for k, v in obj.items()}
        return obj
