from typing import Optional

from datetime import datetime
from src.validators import parse_date
from typing import Optional, TypeVar, Union, List

DayDict = dict[str, str | int]
TimeSlotDict = dict[str, str | int]
WorkerDayList = List[DayDict]
TimeSlotList = List[TimeSlotDict]


class Worker:
    def __init__(self, days: DayDict, timeslot: TimeSlotDict):
        self.days = sorted(days, key=lambda day: day["date"])
        self.timeslot = sorted(timeslot, key=lambda slot: (slot["day_id"], slot["start"]))

    def _get_day_info_by_date(self, date: str) -> Optional[DayDict]:
        for day in self.days:
            if day["date"] == date:
                return day
        return None

    def _get_busy_intervals_by_day_id(self, day_id: int) -> Optional[TimeSlotList]:
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
        valid_date = parse_date(date)

        day_info = self._get_day_info_by_date(valid_date)
        if day_info is None:
            raise ValueError("This date is not included in the employee's work schedule.")

        result = self._get_free_time_by_day_info(day_info)
        return result


