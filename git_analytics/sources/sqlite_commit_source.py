import hashlib
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterator

from git_analytics.entities import AnalyticsCommit, FileChangeStats
from git_analytics.interfaces import CommitSource


def user_data_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "git-analytics"


def repo_db_path(repo_path: str = ".") -> Path:
    full_path = str(Path(repo_path).resolve())
    name = Path(full_path).name
    path_hash = hashlib.sha1(full_path.encode()).hexdigest()[:8]
    return user_data_dir() / name / f"{name}_{path_hash}.db"


_CREATE_COMMITS = """
CREATE TABLE IF NOT EXISTS commits (
    sha                TEXT PRIMARY KEY,
    commit_author       TEXT NOT NULL,
    committed_datetime  TEXT NOT NULL,
    lines_insertions    INTEGER NOT NULL,
    lines_deletions     INTEGER NOT NULL,
    files_changed       INTEGER NOT NULL,
    message             TEXT NOT NULL
)
"""

_CREATE_COMMIT_FILES = """
CREATE TABLE IF NOT EXISTS commit_files (
    sha         TEXT NOT NULL REFERENCES commits(sha),
    filepath    TEXT NOT NULL,
    insertions  INTEGER NOT NULL,
    deletions   INTEGER NOT NULL
)
"""


def populate_sqlite(source: CommitSource, db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(_CREATE_COMMITS)
        conn.execute(_CREATE_COMMIT_FILES)
        with conn:
            for commit in source.iter_commits():
                conn.execute(
                    "INSERT OR REPLACE INTO commits VALUES (?,?,?,?,?,?,?)",
                    (
                        commit.sha,
                        commit.commit_author,
                        commit.committed_datetime.isoformat(),
                        commit.lines_insertions,
                        commit.lines_deletions,
                        commit.files_changed,
                        commit.message,
                    ),
                )
                for filepath, stats in commit.files.items():
                    conn.execute(
                        "INSERT INTO commit_files VALUES (?,?,?,?)",
                        (commit.sha, filepath, stats.insertions, stats.deletions),
                    )
    finally:
        conn.close()


class SqliteCommitSource(CommitSource):
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def iter_commits(self) -> Iterator[AnalyticsCommit]:
        conn = sqlite3.connect(self._db_path)
        try:
            rows = conn.execute(
                "SELECT sha, commit_author, committed_datetime, lines_insertions, "
                "lines_deletions, files_changed, message "
                "FROM commits ORDER BY committed_datetime DESC"
            ).fetchall()

            for row in rows:
                sha, author, dt_str, insertions, deletions, files_changed, message = row
                files_rows = conn.execute(
                    "SELECT filepath, insertions, deletions FROM commit_files WHERE sha=?",
                    (sha,),
                ).fetchall()
                files = {
                    filepath: FileChangeStats(insertions=ins, deletions=dels)
                    for filepath, ins, dels in files_rows
                }
                yield AnalyticsCommit(
                    sha=sha,
                    commit_author=author,
                    committed_datetime=datetime.fromisoformat(dt_str),
                    lines_insertions=insertions,
                    lines_deletions=deletions,
                    files_changed=files_changed,
                    message=message,
                    files=files,
                )
        finally:
            conn.close()
