from datetime import date, datetime
from typing import Union


def get_number_week(dt: Union[date, datetime]) -> str:
    return f"w{dt.isocalendar()[1]:02d}"
