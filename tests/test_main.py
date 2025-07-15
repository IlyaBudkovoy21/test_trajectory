"""
Модуль тестирования функционала класса Worker.

Для запуска тестов необходимо:

1. Установить зависимости:
   pip install pytest

2. Выполнить тесты командой:
   - pytest tests/test_worker.py -v
"""

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
        assert worker._get_day_info_by_date(test_date1)["id"] == 1

        test_date2 = "2024-10-11"
        assert worker._get_day_info_by_date(test_date2)["id"] == 2

        test_date3 = "2024-11-11"
        assert worker._get_day_info_by_date(test_date3) is None

    def test_get_busy_intervals_by_day(self, worker_fixture):
        worker = worker_fixture

        test1 = worker._get_busy_intervals_by_day_id(1)
        assert test1[0]["id"] == 1 and test1[1]["id"] == 4

        test2 = worker._get_busy_intervals_by_day_id(2)
        assert test2[0]["id"] == 3

        test3 = worker._get_busy_intervals_by_day_id(5)
        assert test3 is None

    def test_get_free_time_by_date(self, worker_fixture):
        worker = worker_fixture

        assert worker.get_free_time_by_date("2024-10-11") == ["08:00-09:30", "16:00-17:00"]

        assert worker.get_free_time_by_date("2024-10-10") == ["09:00-11:00", "12:00-13:00", "16:00-18:00"]

        with pytest.raises(ValueError):
            worker.get_free_time_by_date("2024-10-20")

        with pytest.raises(ValueError):
            worker.get_free_time_by_date("2024-20-10")

    def test_is_time_available_free_slot(self, worker_fixture):
        worker = worker_fixture
        assert worker.is_time_available("2024-10-10", "12:00", "13:00") is True

    def test_is_time_available_busy_slot(self, worker_fixture):
        worker = worker_fixture
        assert worker.is_time_available("2024-10-10", "11:30", "12:30") is False

    def test_is_time_available_outside_work_hours(self, worker_fixture):
        worker = worker_fixture
        assert worker.is_time_available("2024-10-10", "08:00", "09:30") is False

    def test_find_available_slots_basic(self, worker_fixture):
        worker = worker_fixture
        slots = worker.find_available_slots("2024-10-10", 60)
        assert slots == ['09:00-11:00', '12:00-13:00', '16:00-18:00']

    def test_find_available_slots_with_buffer(self, worker_fixture):
        worker = worker_fixture
        slots = worker.find_available_slots("2024-10-10", 60, 30)
        assert slots == ['09:00-10:30', '16:30-18:00']

    def test_find_available_slots_no_match(self, worker_fixture):
        worker = worker_fixture
        slots = worker.find_available_slots("2024-10-11", 240)  # 4 часа
        assert len(slots) == 0
