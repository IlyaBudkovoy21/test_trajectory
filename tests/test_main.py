import pytest
import logging

from src.main import Worker


@pytest.fixture
def worker_fixture():
    return Worker(
        days=[
            {"id": 1, "date": "2024-10-10", "start": "09:00", "end": "18:00"},
            {"id": 2, "date": "2024-10-11", "start": "08:00", "end": "17:00"}
        ],
        timeslot=[
            {"id": 1, "day_id": 1, "start": "11:00", "end": "12:00"},
            {"id": 3, "day_id": 2, "start": "09:30", "end": "16:00"},
            {"id": 4, "day_id": 1, "start": "13:00", "end": "16:00"}
        ]
    )


@pytest.fixture(autouse=True)
def disable_logging_globally():
    logging.disable(logging.CRITICAL)


class TestWorker:
    def test_get_day_id_by_date(self, worker_fixture):
        worker = worker_fixture

        test_date1 = "2024-10-10"
        assert worker._get_day_id_by_date(test_date1) == 1

        test_date2 = "2024-10-11"
        assert worker._get_day_id_by_date(test_date2) == 2

        test_date3 = "2024-11-11"
        assert worker._get_day_id_by_date(test_date3) is None

    def test_get_busy_intervals_by_day(self, worker_fixture):
        worker = worker_fixture

        test1 = worker._get_busy_intervals_by_day(1)
        assert test1[0]["id"] == 1 and test1[1]["id"] == 4

        test2 = worker._get_busy_intervals_by_day(2)
        assert test2[0]["id"] == 3

        test3 = worker._get_busy_intervals_by_day(5)
        assert test3 is None
