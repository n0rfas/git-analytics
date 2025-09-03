from fake_data import FAKE_COMMITS


def test_count_commit():
    assert len(FAKE_COMMITS) == 40


def test_sequence_commit():
    for i in range(40 - 1):
        assert FAKE_COMMITS[i].committed_datetime > FAKE_COMMITS[i + 1].committed_datetime
