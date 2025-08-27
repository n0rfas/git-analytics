from git_analytics.analyzers.authors_statistics import AuthorsStatisticsAnalyzer
from git_analytics.engine import CommitAnalyticsEngine

from fake_commit_source import FakeCommitSource
from fake_data import FAKE_COMMITS


def test_first():
    assert 1 == 1


def test_authors_statistics_list_of_authors():
    source = FakeCommitSource(FAKE_COMMITS)

    analyzer = AuthorsStatisticsAnalyzer()
    for commit in source.iter_commits():
        analyzer.process(commit)
    result = analyzer.result()

    assert set(result.authors.keys()) == {"Alice", "Bob", "Carol", "Dave", "Oscar"}
