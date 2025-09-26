from collections import defaultdict
from dataclasses import dataclass
from typing import Dict

from git_analytics.entities import AnalyticsCommit, AnalyticsResult
from git_analytics.interfaces import CommitAnalyzer


@dataclass
class FileExtensionChangeStats:
    insertions: int = 0
    deletions: int = 0


@dataclass
class Result(AnalyticsResult):
    files_extensions_total: Dict[str, FileExtensionChangeStats]
    files_extensions_by_author: Dict[str, Dict[str, FileExtensionChangeStats]]


def _get_file_extension(file_path: str) -> str:
    filename = file_path.split("/")[-1]
    filename_parts = filename.split(".")
    if len(filename_parts) == 1 or filename_parts[0] == "":
        return "no_extension"
    return filename_parts[-1].lower().replace("}", "")


class LanguageAnalyzer(CommitAnalyzer):
    name = "language_statistics"

    def __init__(self) -> None:
        self._total: Dict[str, FileExtensionChangeStats] = defaultdict(FileExtensionChangeStats)
        self._by_author: Dict[str, Dict[str, FileExtensionChangeStats]] = defaultdict(
            lambda: defaultdict(FileExtensionChangeStats)
        )

    def process(self, commit: AnalyticsCommit) -> None:
        for changed_file in commit.files:
            file_extension = _get_file_extension(changed_file)
            self._total[file_extension].insertions += commit.files[changed_file].insertions
            self._total[file_extension].deletions += commit.files[changed_file].deletions
            self._by_author[commit.commit_author][file_extension].insertions += commit.files[changed_file].insertions
            self._by_author[commit.commit_author][file_extension].deletions += commit.files[changed_file].deletions

    def result(self) -> Result:
        return Result(
            files_extensions_total=dict(sorted(self._total.items(), key=lambda item: item[1].insertions, reverse=True)),
            files_extensions_by_author={
                author: dict(sorted(counter.items(), key=lambda item: item[1].insertions, reverse=True))
                for author, counter in self._by_author.items()
            },
        )
