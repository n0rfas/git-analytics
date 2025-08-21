from dataclasses import dataclass
from datetime import datetime
from enum import Enum


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
class AuthorStatistics:
    commits: int = 0
    insertions: int = 0
    deletions: int = 0


class CommitType(Enum):
    FEATURE = "feature"
    FIX = "fix"
    DOCS = "docs"
    STYLE = "style"
    REFACTOR = "refactor"
    TEST = "test"
    CHORE = "chore"
    MERGE = "merge"
    WIP = "wip"
