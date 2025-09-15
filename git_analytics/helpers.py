from datetime import date, datetime
from typing import Union


def get_number_week(dt: Union[date, datetime]) -> str:
    year = dt.year
    week = dt.isocalendar()[1]
    return f"{year}-W{week:02d}"  # ISO-8601 week number
