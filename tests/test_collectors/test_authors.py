from datetime import datetime

from git_analytics.collectors import AuthorCommitsCounter
from git_analytics.engine import MetricsEngine
from git_analytics.history import GitHistoryWalker


def test_author_commits_counter():
    history = GitHistoryWalker(
        since_date=datetime(2021, 11, 1),
        until_date=datetime(2026, 11, 1),
    )
    collector = AuthorCommitsCounter()
    engine = MetricsEngine(history, [collector])
    result = engine.run()

    assert list(result["authors_statistics"].keys()) == ["Anton", "n0rfas", "Anton Safronov"]
    assert result["authors_statistics"]["Anton"]["commits"] == 2
    assert result["authors_statistics"]["n0rfas"]["commits"] == 11
    assert result["authors_statistics"]["Anton Safronov"]["commits"] == 23
