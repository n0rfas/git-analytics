from fake_commit_source import FakeCommitSource
from fake_data import FAKE_COMMITS


def test_first():
    assert 1 == 1


def test_second():
    source = FakeCommitSource(FAKE_COMMITS)
    assert len(list(source.iter_commits())) == 40
