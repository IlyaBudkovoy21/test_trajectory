from datetime import datetime
from typing import Optional


def parse_date(date: str) -> Optional[datetime]:
    try:
        return datetime.strptime(date, "%Y-%d-%m")
    except ValueError as e:
        print("")
