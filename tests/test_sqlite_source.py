import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from git_analytics.entities import AnalyticsCommit, FileChangeStats
from git_analytics.sources import SqliteCommitSource, populate_sqlite
from tests.fakes import FAKE_COMMITS, FakeCommitSource


def _round_trip(commits):
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "test.db"
        populate_sqlite(FakeCommitSource(commits), db)
        return list(SqliteCommitSource(db).iter_commits())


def test_round_trip_count():
    result = _round_trip(FAKE_COMMITS)
    assert len(result) == len(FAKE_COMMITS)


def test_round_trip_fields():
    result = _round_trip(FAKE_COMMITS)
    # SqliteCommitSource yields newest-first; FAKE_COMMITS is already newest-first
    original = FAKE_COMMITS[0]
    loaded = result[0]
    assert loaded.sha == original.sha
    assert loaded.commit_author == original.commit_author
    assert loaded.lines_insertions == original.lines_insertions
    assert loaded.lines_deletions == original.lines_deletions
    assert loaded.files_changed == original.files_changed
    assert loaded.message == original.message


def test_round_trip_timezone_preserved():
    result = _round_trip(FAKE_COMMITS)
    original = FAKE_COMMITS[0]
    loaded = result[0]
    assert loaded.committed_datetime == original.committed_datetime
    assert loaded.committed_datetime.tzinfo is not None


def test_round_trip_ordering_newest_first():
    result = _round_trip(FAKE_COMMITS)
    datetimes = [c.committed_datetime for c in result]
    assert datetimes == sorted(datetimes, reverse=True)


def test_round_trip_with_files():
    tz = timezone(timedelta(hours=2))
    commits = [
        AnalyticsCommit(
            sha="abc123",
            commit_author="Alice",
            committed_datetime=datetime(2025, 6, 1, 10, 0, 0, tzinfo=tz),
            lines_insertions=10,
            lines_deletions=5,
            files_changed=2,
            message="feat: add files",
            files={
                "src/foo.py": FileChangeStats(insertions=8, deletions=3),
                "src/bar.py": FileChangeStats(insertions=2, deletions=2),
            },
        )
    ]
    result = _round_trip(commits)
    assert len(result) == 1
    loaded = result[0]
    assert set(loaded.files.keys()) == {"src/foo.py", "src/bar.py"}
    assert loaded.files["src/foo.py"].insertions == 8
    assert loaded.files["src/foo.py"].deletions == 3


def test_round_trip_empty_files():
    result = _round_trip(FAKE_COMMITS)
    # All FAKE_COMMITS have files={}, should round-trip cleanly
    for commit in result:
        assert commit.files == {}


def test_load_nonexistent_db_raises():
    source = SqliteCommitSource(Path("/nonexistent/path/db.sqlite"))
    with pytest.raises(Exception):
        list(source.iter_commits())


def test_populate_creates_parent_dirs():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "nested" / "dir" / "test.db"
        populate_sqlite(FakeCommitSource([]), db)
        assert db.exists()
