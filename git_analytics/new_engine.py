from dataclasses import dataclass

import os

from pathlib import Path
from typing import Protocol, Dict, Iterator, Iterable, Optional, List, Tuple
from git import Commit, Repo
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class FileChangeStats:
    insertions: int
    deletions: int


@dataclass(frozen=True)
class CommitContext:
    commit: Commit
    commit_author: str
    committed_datetime: datetime


class GitHistoryWalker:
    def __init__(
        self,
        path: str = ".",
        branch: str = "main",
        since_days: int = 365,
    ) -> None:
        self._repo = Repo(path)
        self._branch = branch
        self._since_days = since_days

    def iter_commits(self) -> Iterator[Commit]:
        shas = self._repo.git.rev_list(
            f"--since={self._since_days + 21}.days.ago",
            "--first-parent",
            "--reverse",
            self._branch,
        ).splitlines()

        self._number_of_commits = len(shas)

        for sha in shas:
            yield self._repo.commit(sha)


class MetricCollector(Protocol):
    name: str

    def consume(self, ctx: CommitContext) -> None: ...

    def build_report(self) -> object: ...


class MetricsEngine:
    def __init__(self, history: GitHistoryWalker, collectors: Iterable[MetricCollector]) -> None:
        self._history = history
        self._collectors = collectors

    def run(self) -> Dict[str, object]:
        for current, commit in enumerate(self._history.iter_commits(), start=1):
            total = getattr(self._history, "_number_of_commits", "?")
            print(f"\rProcessing commits: {current}/{total}", end="", flush=True)
            ctx = self._build_commit_context(commit)

            for collector in self._collectors:
                collector.consume(ctx)

        return {collector.name: collector.build_report() for collector in self._collectors}

    def _build_commit_context(self, commit: Commit) -> CommitContext:
        return CommitContext(
            commit=commit,
            commit_author=str(commit.author.name),
            committed_datetime=commit.committed_datetime,
        )


# ///====================


# @dataclass
# class AuthorStatistics:
#     commits: int = 0
#     insertions: int = 0
#     deletions: int = 0


# @dataclass
# class Result:
#     authors: Dict[str, AuthorStatistics]


class AuthorCommitsCounter:
    name = "authors_statistics"
    authors = {}

    def consume(self, ctx: CommitContext) -> None:
        if ctx.commit_author not in self.authors:
            self.authors[ctx.commit_author] = {}
            self.authors[ctx.commit_author]["commits"] = 0
            self.authors[ctx.commit_author]["insertions"] = 0
            self.authors[ctx.commit_author]["deletions"] = 0

        self.authors[ctx.commit_author]["commits"] += 1
        self.authors[ctx.commit_author]["insertions"] += ctx.commit.stats.total["insertions"]
        self.authors[ctx.commit_author]["deletions"] += ctx.commit.stats.total["deletions"]

    def build_report(self) -> object:
        return self.authors


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


# /======

NO_EXTENSION = "(no extension)"


@dataclass(frozen=True)
class RepositoryCompositionReport:
    files_by_extension: Dict[str, int]
    lines_by_extension: Dict[str, int]
    total_files: int
    total_lines: int


class RepositoryCompositionEngine:
    def __init__(self, root_path: str = ".") -> None:
        self._root = Path(root_path).resolve()

        self._ignore_dirs = {
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            "htmlcov",
            ".pytest_cache",
            ".mypy_cache",
            ".tox",
            "dist",
            "build",
            "coverage",
            ".coverage",
            "vendor",
        }

        self._ignore_file_names = {
            "poetry.lock",
            "Pipfile.lock",
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            "Cargo.lock",
        }

        self._ignore_suffixes = (
            ".min.js",
            ".min.css",
            ".pyc",
            ".pyo",
            ".so",
            ".dll",
            ".dylib",
            ".class",
            ".jar",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
            ".ico",
            ".pdf",
            ".zip",
            ".tar",
            ".gz",
        )

    def run(self) -> RepositoryCompositionReport:
        files_by_extension: Dict[str, int] = {}
        lines_by_extension: Dict[str, int] = {}

        total_files = 0
        total_lines = 0

        for root, dirs, files in os.walk(self._root):
            dirs[:] = [d for d in dirs if d not in self._ignore_dirs]

            for file_name in files:
                if file_name in self._ignore_file_names:
                    continue

                file_path = Path(root) / file_name

                if self._should_skip_file(file_path):
                    continue

                extension = self._extract_extension(file_path)

                try:
                    line_count = self._count_lines(file_path)
                except (UnicodeDecodeError, PermissionError, OSError):
                    continue

                files_by_extension[extension] = files_by_extension.get(extension, 0) + 1
                lines_by_extension[extension] = lines_by_extension.get(extension, 0) + line_count

                total_files += 1
                total_lines += line_count

        return RepositoryCompositionReport(
            files_by_extension=dict(sorted(files_by_extension.items())),
            lines_by_extension=dict(sorted(lines_by_extension.items())),
            total_files=total_files,
            total_lines=total_lines,
        )

    def _should_skip_file(self, file_path: Path) -> bool:
        if not file_path.exists():
            return True

        if not file_path.is_file():
            return True

        if file_path.is_symlink():
            return True

        file_name = file_path.name
        if file_name in self._ignore_file_names:
            return True

        path_str = str(file_path)

        if path_str.endswith(self._ignore_suffixes):
            return True

        if self._is_binary_file(file_path):
            return True

        return False

    @staticmethod
    def _extract_extension(file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        return suffix if suffix else NO_EXTENSION

    @staticmethod
    def _count_lines(file_path: Path) -> int:
        with file_path.open("r", encoding="utf-8") as f:
            return sum(1 for _ in f)

    @staticmethod
    def _is_binary_file(file_path: Path, sample_size: int = 8192) -> bool:
        with file_path.open("rb") as f:
            chunk = f.read(sample_size)
        return b"\x00" in chunk
