import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

NO_EXTENSION = "(no extension)"


@dataclass(frozen=True)
class CodebaseSnapshotReport:
    files_by_extension: Dict[str, int]
    lines_by_extension: Dict[str, int]
    total_files: int
    total_lines: int


class CodebaseSnapshot:
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

    def run(self) -> CodebaseSnapshotReport:
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

        return CodebaseSnapshotReport(
            files_by_extension=dict(sorted(files_by_extension.items(), key=lambda x: x[1], reverse=True)),
            lines_by_extension=dict(sorted(lines_by_extension.items(), key=lambda x: x[1], reverse=True)),
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
