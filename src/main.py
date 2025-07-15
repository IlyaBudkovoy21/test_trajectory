from typing import Optional

from src.validators import parse_date
from typing import Optional, TypeVar, Union, List

T = TypeVar('T', bound=dict[str, Union[str, int]])

BusyIntervalsType = Optional[List[T]]
WorkingDays = Optional[List[T]]


class Worker:
    def __init__(self, days: WorkingDays, timeslot: BusyIntervalsType):
        self.days = sorted(days, key=lambda day: day["date"])
        self.timeslot = sorted(timeslot, key=lambda day: day["day_id"])

    def _get_day_id_by_date(self, date: str) -> Optional[int]:
        for day in self.days:
            if day["date"] == date:
                return day["id"]
        return None

    def _get_busy_intervals_by_day(self, day_id: int) -> Optional[BusyIntervalsType]:
        result_list = []
        for slot in self.timeslot:
            if slot["day_id"] == day_id:
                result_list.append(slot)
            if day_id < slot["day_id"]:
                break
        if not result_list:
            return None
        return result_list

    def get_all_timeslots_by_date(self, date: str) -> Optional[BusyIntervalsType]:
        valid_date = parse_date(date)
        if valid_date is None:
            raise ValueError("Некорректная дата")

        day_id = self._get_day_id_by_date(valid_date)
        if day_id is None:
            raise ValueError("Данная дата не входит в рабочее расписание работника")

        busy_intervals = self._get_busy_intervals_by_day(day_id)
        if busy_intervals is None:
            return None
        return busy_intervals


