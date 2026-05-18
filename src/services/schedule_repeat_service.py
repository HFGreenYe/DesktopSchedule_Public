"""Pure date-shift helpers for schedule repeat rules."""

from __future__ import annotations

import datetime


class ScheduleRepeatService:
    """Pure repeat date calculation service."""

    NON_REPEAT_RULES = ("none", "无", "不重复", "")
    REPEAT_COUNTS = {"每天": 365, "每周": 52, "每月": 12}

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

    @staticmethod
    def is_non_repeat_rule(rule):
        """Whether a rule is treated as non-repeat by legacy semantics."""
        return (rule or "").strip() in ScheduleRepeatService.NON_REPEAT_RULES

    @staticmethod
    def get_repeat_count(rule):
        """Get legacy future item count for a repeat rule."""
        return ScheduleRepeatService.REPEAT_COUNTS.get((rule or "").strip(), 0)

    @staticmethod
    def build_repeat_insert_plan(base_data, rule, group_id, include_base=True):
        """Build insert plan dict list for legacy repeat generation."""
        normalized_rule = (rule or "").strip()
        base_item = dict(base_data or {})
        base_item["group_id"] = group_id
        if ScheduleRepeatService.is_non_repeat_rule(normalized_rule):
            return [base_item] if include_base else []

        repeat_count = ScheduleRepeatService.get_repeat_count(normalized_rule)
        if repeat_count == 0:
            return [base_item] if include_base else []

        plan = []
        if include_base:
            plan.append(base_item.copy())

        base_start = base_item.get("start_time")
        base_end = base_item.get("end_time")
        base_reminder = base_item.get("reminder_time")

        for i in range(1, repeat_count + 1):
            new_item = base_item.copy()
            shifted_start, shifted_end, shifted_reminder = ScheduleRepeatService.shift_triplet(
                base_start, base_end, base_reminder, normalized_rule, i
            )
            if base_start:
                new_item["start_time"] = shifted_start
            if base_end:
                new_item["end_time"] = shifted_end
            if base_reminder:
                new_item["reminder_time"] = shifted_reminder
            plan.append(new_item)

        return plan
