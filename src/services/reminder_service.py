"""Pure reminder decision helpers for reminder scan flow."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional


class ReminderService:
    """Stateless helper for reminder-time checks."""

    @staticmethod
    def has_reminder_time(schedule: Any) -> bool:
        """Return True when schedule has a non-empty reminder_time."""
        return getattr(schedule, "reminder_time", None) is not None

    @staticmethod
    def get_reminder_diff_seconds(schedule: Any, now: datetime) -> Optional[float]:
        """Return (now - reminder_time).seconds or None when no reminder_time."""
        reminder_time = getattr(schedule, "reminder_time", None)
        if reminder_time is None:
            return None
        return (now - reminder_time).total_seconds()

    @staticmethod
    def is_in_trigger_window(diff_seconds: Optional[float]) -> bool:
        """Legacy trigger window: 0 <= diff < 60."""
        if diff_seconds is None:
            return False
        return 0 <= diff_seconds < 60

    def should_trigger(self, schedule: Any, now: datetime) -> bool:
        """Return whether schedule should trigger at `now` (without dedup state)."""
        if not self.has_reminder_time(schedule):
            return False
        diff_seconds = self.get_reminder_diff_seconds(schedule, now)
        return self.is_in_trigger_window(diff_seconds)

    @staticmethod
    def select_target_time(schedule: Any):
        """Legacy target_time selector: start_time first, then end_time, else None."""
        start_time = getattr(schedule, "start_time", None)
        if start_time is not None:
            return start_time
        return getattr(schedule, "end_time", None)

