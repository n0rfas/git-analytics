import os
from datetime import date, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from git_analytics.entities import AnalyticsResult
from git_analytics.interfaces import CommitSource


class FileAnalyticsEngine:
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path

    def run(self) -> Dict[str, Tuple[int, int]]:
        stats: Dict[str, Tuple[int, int]] = {}

        repo_path = Path(self.repo_path).resolve()

        ignore_dirs = {
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            "htmlcov",
            ".pytest_cache",
            ".mypy_cache",
            "dist",
            "build",
        }

        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            for file in files:
                file_path = Path(root) / file

                extension = file_path.suffix if file_path.suffix else "(no extension)"

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        line_count = sum(1 for _ in f)
                except (UnicodeDecodeError, PermissionError, OSError):
                    line_count = 0

                if extension in stats:
                    file_count, total_lines = stats[extension]
                    stats[extension] = (file_count + 1, total_lines + line_count)
                else:
                    stats[extension] = (1, line_count)

        return dict(sorted(stats.items()))


class CommitAnalyticsEngine:
    def __init__(
        self,
        source: CommitSource,
        analyzers_factory,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._source = source
        self._analyzers_factory = analyzers_factory
        self._additional_data = additional_data

    def run(
        self,
        start_date: Optional[date] = None,
        stop_date: Optional[date] = None,
    ) -> Dict[str, AnalyticsResult]:
        analyzers = self._analyzers_factory()

        if start_date and stop_date and start_date > stop_date:
            start_date, stop_date = stop_date, start_date

        for commit in self._source.iter_commits():
            commit_day = commit.committed_datetime.astimezone(timezone.utc).date()

            if stop_date and commit_day > stop_date:
                continue

            if start_date and commit_day < start_date:
                break

            for analyzer in analyzers:
                analyzer.process(commit)

        result = {analyzer.name: analyzer.result() for analyzer in analyzers}
        if self._additional_data:
            result["additional_data"] = self._additional_data
        return result
