from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from datetime import date, datetime
from enum import Enum
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
    def _make_json_safe(obj: Any) -> Any:
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()

        if isinstance(obj, Enum):
            return obj.value

        if isinstance(obj, Mapping):
            safe: Dict[str, Any] = {}
            for k, v in obj.items():
                if isinstance(k, (date, datetime)):
                    key = k.isoformat()
                elif isinstance(k, Enum):
                    key = k.value
                elif isinstance(k, (str, int, float, bool)) or k is None:
                    key = str(k)
                else:
                    key = str(k)
                safe[key] = AnalyticsResult._make_json_safe(v)
            return safe

        if isinstance(obj, Iterable) and not isinstance(obj, (str, bytes)):
            return [AnalyticsResult._make_json_safe(x) for x in obj]

        return obj
