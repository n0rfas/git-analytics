from typing import Dict, Optional, List, Tuple

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from git_analytics.engines.metrics import CommitContext


class CodeChurnCollector:
    name = "code_churn_21d"

    def __init__(
        self,
        reporting_days: int = 365,
        churn_days: int = 21,
        now: Optional[datetime] = None,
    ) -> None:
        self._reporting_days = reporting_days
        self._churn_days = churn_days
        self._now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)

        self._report_start = self._now - timedelta(days=reporting_days)
        self._churn_window_seconds = churn_days * 24 * 60 * 60

        # file_path -> normalized_line -> deque[birth_ts]
        self._live_lines: Dict[str, Dict[str, deque[int]]] = defaultdict(lambda: defaultdict(deque))

        self._added_lines_in_period = 0
        self._short_lived_deleted_lines = 0
        self._file_churn_counts: Dict[str, int] = defaultdict(int)

    def consume(self, ctx: CommitContext) -> None:
        commit = ctx.commit

        if not commit.parents:
            return

        parent = commit.parents[0]
        commit_dt = ctx.committed_datetime.astimezone(timezone.utc)
        commit_ts = int(commit_dt.timestamp())
        is_in_reporting_period = commit_dt >= self._report_start

        diffs = parent.diff(commit, create_patch=True)

        for diff_item in diffs:
            file_path = diff_item.b_path or diff_item.a_path
            if not file_path:
                continue

            if self._should_skip_path(file_path):
                continue

            if diff_item.renamed_file:
                continue

            patch_bytes = diff_item.diff
            if not patch_bytes:
                continue

            try:
                patch_text = patch_bytes.decode("utf-8", errors="ignore")
            except Exception:
                continue

            added_lines, deleted_lines = self._parse_unified_patch(patch_text)

            self._consume_deleted_lines(
                file_path=file_path,
                deleted_lines=deleted_lines,
                commit_ts=commit_ts,
                is_in_reporting_period=is_in_reporting_period,
            )
            self._consume_added_lines(
                file_path=file_path,
                added_lines=added_lines,
                commit_ts=commit_ts,
                is_in_reporting_period=is_in_reporting_period,
            )

    def build_report(self) -> object:
        churn_ratio = (
            self._short_lived_deleted_lines / self._added_lines_in_period if self._added_lines_in_period > 0 else 0.0
        )

        hottest_files = dict(
            sorted(
                self._file_churn_counts.items(),
                key=lambda item: item[1],
                reverse=True,
            )[:20]
        )

        return {
            "churn_ratio": churn_ratio,
            "added_lines_in_period": self._added_lines_in_period,
            "short_lived_deleted_lines": self._short_lived_deleted_lines,
            "hottest_files": hottest_files,
        }

    def _consume_added_lines(
        self,
        file_path: str,
        added_lines: List[str],
        commit_ts: int,
        is_in_reporting_period: bool,
    ) -> None:
        for raw_line in added_lines:
            normalized = self._normalize_line(raw_line)
            if not normalized:
                continue

            self._live_lines[file_path][normalized].append(commit_ts)

            if is_in_reporting_period:
                self._added_lines_in_period += 1

    def _consume_deleted_lines(
        self,
        file_path: str,
        deleted_lines: List[str],
        commit_ts: int,
        is_in_reporting_period: bool,
    ) -> None:
        if not is_in_reporting_period:
            return

        file_bucket = self._live_lines.get(file_path)
        if not file_bucket:
            return

        for raw_line in deleted_lines:
            normalized = self._normalize_line(raw_line)
            if not normalized:
                continue

            births = file_bucket.get(normalized)
            if not births:
                continue

            born_ts = births.popleft()
            age_seconds = commit_ts - born_ts

            if age_seconds <= self._churn_window_seconds:
                self._short_lived_deleted_lines += 1
                self._file_churn_counts[file_path] += 1

            if not births:
                del file_bucket[normalized]

        if not file_bucket:
            del self._live_lines[file_path]

    @staticmethod
    def _parse_unified_patch(patch_text: str) -> Tuple[List[str], List[str]]:
        added: list[str] = []
        deleted: list[str] = []

        for line in patch_text.splitlines():
            if not line:
                continue
            if line.startswith("@@"):
                continue
            if line.startswith("+++ ") or line.startswith("--- "):
                continue

            if line.startswith("+"):
                added.append(line[1:])
            elif line.startswith("-"):
                deleted.append(line[1:])

        return added, deleted

    @staticmethod
    def _normalize_line(line: str) -> str:
        return " ".join(line.strip().split())

    @staticmethod
    def _should_skip_path(path: str) -> bool:
        skip_prefixes = (
            "node_modules/",
            "dist/",
            "build/",
            "vendor/",
            ".venv/",
            "venv/",
        )
        skip_suffixes = (
            ".lock",
            ".min.js",
            ".min.css",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
            ".svg",
            ".pdf",
        )
        return path.startswith(skip_prefixes) or path.endswith(skip_suffixes)
