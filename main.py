import requests
from datetime import datetime


class Worker:
    def __init__(self, days: list[dict[str, str | int]], timeslot: list[dict[str, str | int]]):
        self.days = days.sort(key=lambda day: day["date"])
        self.timeslot = timeslot.sort(key=lambda day: day["day_id"])

