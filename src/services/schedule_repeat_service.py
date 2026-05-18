"""Pure date-shift helpers for schedule repeat rules."""

from __future__ import annotations

import datetime


class ScheduleRepeatService:
    """Pure repeat date calculation service."""

    @staticmethod
    def add_months(sourcedate, months):
        """Add months with month-end and leap-year compatibility."""
        if not sourcedate:
            return None
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(
            sourcedate.day,
            [
                31,
                29 if year % 4 == 0 and not year % 100 == 0 or year % 400 == 0 else 28,
                31,
                30,
                31,
                30,
                31,
                31,
                30,
                31,
                30,
                31,
            ][month - 1],
        )
        return sourcedate.replace(year=year, month=month, day=day)

    @staticmethod
    def shift_datetime(value, rule, step):
        """Shift one datetime value by legacy repeat rule."""
        if not value:
            return None
        if rule == "每天":
            return value + datetime.timedelta(days=step)
        if rule == "每周":
            return value + datetime.timedelta(weeks=step)
        if rule == "每月":
            return ScheduleRepeatService.add_months(value, step)
        return value

    @staticmethod
    def shift_triplet(start_time, end_time, reminder_time, rule, step):
        """Shift start/end/reminder trio by legacy repeat rule."""
        return (
            ScheduleRepeatService.shift_datetime(start_time, rule, step),
            ScheduleRepeatService.shift_datetime(end_time, rule, step),
            ScheduleRepeatService.shift_datetime(reminder_time, rule, step),
        )
