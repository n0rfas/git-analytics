from datetime import date

import freezegun
from fake_analyzer import FakeAnalyzer
from fake_commit_source import FakeCommitSource
from fake_data import FAKE_COMMITS

from git_analytics.engine import CommitAnalyticsEngine


def test_number_of_calls_without_start_and_stop_date():
    source = FakeCommitSource(FAKE_COMMITS)
    engine = CommitAnalyticsEngine(source=source, analyzers_factory=lambda: [FakeAnalyzer()])

    number_of_calls = engine.run()["fake_analyzer"]

    assert len(number_of_calls.list_sha) == 40


@freezegun.freeze_time("2025-07-02 00:05:00.000000")
def test_number_of_calls_with_start_date():
    source = FakeCommitSource(FAKE_COMMITS)
    engine = CommitAnalyticsEngine(source=source, analyzers_factory=lambda: [FakeAnalyzer()])

    start_date = date(2025, 6, 24)
    result = engine.run(start_date=start_date)["fake_analyzer"]

    assert len(result.list_sha) == 6


@freezegun.freeze_time("2025-07-02 00:05:00.000000")
def test_number_of_calls_with_stop_date():
    source = FakeCommitSource(FAKE_COMMITS)
    engine = CommitAnalyticsEngine(source=source, analyzers_factory=lambda: [FakeAnalyzer()])

    stop_date = date(2025, 6, 24)
    result = engine.run(stop_date=stop_date)["fake_analyzer"]

    assert len(result.list_sha) == 34


@freezegun.freeze_time("2025-07-02 00:05:00.000000")
def test_number_of_calls_with_start_and_stop_date():
    source = FakeCommitSource(FAKE_COMMITS)
    engine = CommitAnalyticsEngine(source=source, analyzers_factory=lambda: [FakeAnalyzer()])

    start_date = date(2025, 1, 1)
    stop_date = date(2025, 5, 1)
    result = engine.run(start_date=start_date, stop_date=stop_date)["fake_analyzer"]

    assert len(result.list_sha) == 9


@freezegun.freeze_time("2025-07-02 00:05:00.000000")
def test_number_of_calls_with_start_and_stop_date_are_mixed_up():
    source = FakeCommitSource(FAKE_COMMITS)
    engine = CommitAnalyticsEngine(source=source, analyzers_factory=lambda: [FakeAnalyzer()])

    start_date = date(2025, 5, 1)  # mistake
    stop_date = date(2025, 1, 1)  # mistake
    result = engine.run(start_date=start_date, stop_date=stop_date)["fake_analyzer"]

    assert len(result.list_sha) == 9
