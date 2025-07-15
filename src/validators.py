from datetime import datetime
from typing import Optional

from src.config.logger import logger


def parse_date(date: str) -> Optional[str]:
    try:
        datetime.strptime(date, "%Y-%d-%m")
        return date
    except ValueError as e:
        logger.error(e)
        raise ValueError("Uncorrect date")
