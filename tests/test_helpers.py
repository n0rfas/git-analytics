from datetime import date, datetime

import freezegun

from git_analytics.helpers import get_number_week


def test_helpers_get_number_week():
    with freezegun.freeze_time("2025-01-01"):
        assert get_number_week(datetime.now()) == "w01"
        assert get_number_week(date.today()) == "w01"

    with freezegun.freeze_time("2025-03-10"):
        assert get_number_week(datetime.now()) == "w11"
        assert get_number_week(date.today()) == "w11"
