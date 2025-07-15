import pytest
from datetime import datetime

from src.validators import parse_date


@pytest.mark.parametrize(
    "test_date, exp_result",
    (
            ("2023-01-01", datetime),
            ("2020-32-01", None),
            ("2020-01-13", None),
    )
)
def test_parse_date(test_date: str, exp_result: datetime | None):
    result = parse_date(test_date)
    if exp_result is None:
        assert result is None
    else:
        assert isinstance(result, datetime)
        year, day, month = map(int, test_date.split('-'))
        assert result.year == year
        assert result.month == month
        assert result.day == day