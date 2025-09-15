from datetime import date, datetime

import freezegun

from git_analytics.helpers import get_number_week


def test_helpers_get_number_week():
    with freezegun.freeze_time("2025-01-01"):
        assert get_number_week(datetime.now()) == "2025-W01"
        assert get_number_week(date.today()) == "2025-W01"

    with freezegun.freeze_time("2024-03-11"):
        assert get_number_week(datetime.now()) == "2024-W11"
        assert get_number_week(date.today()) == "2024-W11"
