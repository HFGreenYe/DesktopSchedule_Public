"""Service for schedule write coordination (minimal scope)."""

from __future__ import annotations


class ScheduleService:
    """Minimal schedule service for single item creation."""

    @staticmethod
    def create_single_schedule(schedule_model, data):
        """Create one schedule record without mutating caller data."""
        payload = dict(data or {})
        schedule_model.create(**payload)
        return True
