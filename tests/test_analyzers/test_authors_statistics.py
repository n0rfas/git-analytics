from git_analytics.analyzers.authors_statistics import AuthorsStatisticsAnalyzer
from tests.fakes import FAKE_COMMITS, FakeCommitSource


def test_authors_statistics_list_of_authors():
    source = FakeCommitSource(FAKE_COMMITS)

    analyzer = AuthorsStatisticsAnalyzer()
    for commit in source.iter_commits():
        analyzer.process(commit)
    result = analyzer.result()

    assert set(result.authors.keys()) == {"Alice", "Bob", "Carol", "Dave", "Oscar"}


def test_authors_statistics_commits_count_per_author():
    source = FakeCommitSource(FAKE_COMMITS)

    analyzer = AuthorsStatisticsAnalyzer()
    for commit in source.iter_commits():
        analyzer.process(commit)
    result = analyzer.result()

    assert result.authors["Alice"].commits == 11
    assert result.authors["Bob"].commits == 6
    assert result.authors["Carol"].commits == 4
    assert result.authors["Dave"].commits == 11
    assert result.authors["Oscar"].commits == 8


def test_authors_statistics_insertions_count_per_author():
    source = FakeCommitSource(FAKE_COMMITS)

    analyzer = AuthorsStatisticsAnalyzer()
    for commit in source.iter_commits():
        analyzer.process(commit)
    result = analyzer.result()

    assert result.authors["Alice"].insertions == 517 + 225 + 391 + 572 + 582 + 179 + 109 + 304 + 47 + 387 + 270
    assert result.authors["Bob"].insertions == 781 + 760 + 314 + 461 + 442 + 1078
    assert result.authors["Carol"].insertions == 614 + 102 + 280 + 303
    assert result.authors["Dave"].insertions == 118 + 100 + 214 + 35 + 52 + 140 + 243 + 147 + 68 + 236 + 212
    assert result.authors["Oscar"].insertions == 599 + 623 + 429 + 544 + 579 + 138 + 287 + 494


def test_authors_statistics_deletions_count_per_author():
    source = FakeCommitSource(FAKE_COMMITS)

    analyzer = AuthorsStatisticsAnalyzer()
    for commit in source.iter_commits():
        analyzer.process(commit)
    result = analyzer.result()

    assert result.authors["Alice"].deletions == 40 + 164 + 162 + 276 + 89 + 115 + 221 + 8 + 292 + 181 + 119
    assert result.authors["Bob"].deletions == 513 + 165 + 172 + 665 + 146 + 384
    assert result.authors["Carol"].deletions == 305 + 273 + 93 + 369
    assert result.authors["Dave"].deletions == 23 + 54 + 110 + 6 + 52 + 63 + 120 + 33 + 105 + 117 + 87
    assert result.authors["Oscar"].deletions == 343 + 381 + 140 + 276 + 389 + 325 + 288 + 6
