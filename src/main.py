from typing import Optional

from datetime import datetime, timedelta
from src.validators import parse_date
from typing import Optional, TypeVar, Union, List

DayDict = dict[str, str | int]
TimeSlotDict = DayDict
WorkerDayList = List[DayDict]
TimeSlotList = List[TimeSlotDict]


class Worker:
    def __init__(self, days: DayDict, timeslot: TimeSlotDict):
        self.days = sorted(days, key=lambda day: day["date"])
        self.timeslot = sorted(timeslot, key=lambda slot: (slot["day_id"], slot["start"]))

    def _get_day_info_by_date(self, date: str) -> Optional[DayDict]:
        """Возвращает информацию о рабочем дне по дате или None если не найден"""
        for day in self.days:
            if day["date"] == date:
                return day
        return None

    def _get_busy_intervals_by_day_id(self, day_id: int) -> Optional[TimeSlotList]:
        """Возвращает занятые интервалы для указанного дня или None если их нет"""
        result_list = []
        for slot in self.timeslot:
            if slot["day_id"] == day_id:
                result_list.append(slot)
            if day_id < slot["day_id"]:
                break
        if not result_list:
            return None
        return result_list

    def get_all_timeslots_by_date(self, date: str) -> Optional[TimeSlotList]:
        """Возвращает все занятые слоты для указанной даты"""
        valid_date = parse_date(date)

        day_info = self._get_day_info_by_date(valid_date)
        if day_info is None:
            raise ValueError("This date is not included in the employee's work schedule.")

        day_id = day_info["id"]

        busy_intervals = self._get_busy_intervals_by_day_id(day_id)
        if busy_intervals is None:
            return None
        return busy_intervals

    def _get_free_time_by_day_info(self, day_info: DayDict) -> list[str]:
        """Вычисляет свободные интервалы для указанного рабочего дня"""
        work_start = datetime.strptime(day_info["start"], "%H:%M")
        work_end = datetime.strptime(day_info["end"], "%H:%M")

        day_id = day_info["id"]
        busy_slots = self._get_busy_intervals_by_day_id(day_id) or []

        busy_intervals = []
        for slot in busy_slots:
            start = datetime.strptime(slot["start"], "%H:%M")
            end = datetime.strptime(slot["end"], "%H:%M")
            busy_intervals.append((start, end))

        busy_intervals.sort()

        free_slots = []
        prev_end = work_start

        for busy_start, busy_end in busy_intervals:
            if busy_start > prev_end:
                free_slots.append((
                    prev_end.strftime("%H:%M"),
                    busy_start.strftime("%H:%M")
                ))
            prev_end = max(prev_end, busy_end)

        if prev_end < work_end:
            free_slots.append((
                prev_end.strftime("%H:%M"),
                work_end.strftime("%H:%M")
            ))

        return [f"{start}-{end}" for start, end in free_slots]

    def get_free_time_by_date(self, date: str) -> list[str]:
        """Возвращает свободные интервалы времени для указанной даты"""
        valid_date = parse_date(date)

        day_info = self._get_day_info_by_date(valid_date)
        if day_info is None:
            raise ValueError("This date is not included in the employee's work schedule.")

        result = self._get_free_time_by_day_info(day_info)
        return result

    def is_time_available(self, date: str, start_time: str, end_time: str) -> bool:
        """Проверяет доступность указанного временного промежутка в заданную дату"""
        day_info = self._get_day_info_by_date(parse_date(date))
        if not day_info:
            raise ValueError("This date is not available for the employee.")

        # Пересечение с рабочим днём
        work_start = datetime.strptime(day_info["start"], "%H:%M")
        work_end = datetime.strptime(day_info["end"], "%H:%M")
        req_start = datetime.strptime(start_time, "%H:%M")
        req_end = datetime.strptime(end_time, "%H:%M")

        if req_start < work_start or req_end > work_end:
            return False

        # Пересечение с занятыми слотами
        busy_slots = self._get_busy_intervals_by_day_id(day_info["id"]) or []
        for slot in busy_slots:
            slot_start = datetime.strptime(slot["start"], "%H:%M")
            slot_end = datetime.strptime(slot["end"], "%H:%M")

            if not (req_end <= slot_start or req_start >= slot_end):
                return False

        return True

    def find_available_slots(
            self,
            date: str,
            duration_minutes: int,
            buffer_minutes: int = 0
    ) -> List[str]:
        """Возвращает список доступных временных слотов для заданной продолжительности."""
        day_info = self._get_day_info_by_date(parse_date(date))
        if not day_info:
            return []

        duration = timedelta(minutes=duration_minutes)
        buffer = timedelta(minutes=buffer_minutes)

        work_start = datetime.strptime(day_info["start"], "%H:%M")
        work_end = datetime.strptime(day_info["end"], "%H:%M")

        busy_slots = self._get_busy_intervals_by_day_id(day_info["id"]) or []
        busy_intervals = []
        for slot in busy_slots:
            start = datetime.strptime(slot["start"], "%H:%M")
            end = datetime.strptime(slot["end"], "%H:%M")
            busy_intervals.append((start - buffer, end + buffer))

        busy_intervals.sort()

        available_slots = []
        prev_end = work_start

        for busy_start, busy_end in busy_intervals:
            slot_start = prev_end
            slot_end = busy_start

            if slot_end > slot_start and (slot_end - slot_start) >= duration:
                available_slots.append(f"{slot_start.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}")

            prev_end = max(prev_end, busy_end)

        slot_start = prev_end
        slot_end = work_end
        if slot_end > slot_start and (slot_end - slot_start) >= duration:
            available_slots.append(f"{slot_start.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}")

        return available_slots
