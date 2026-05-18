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

    @staticmethod
    def delete_future_schedules_for_group(schedule_model, old_group_id, schedule_id, current_schedule):
        """Delete future items from a repeat group using the legacy fallback order."""
        if current_schedule.start_time:
            return schedule_model.delete().where(
                (schedule_model.group_id == old_group_id) &
                (schedule_model.id != schedule_id) &
                (schedule_model.start_time > current_schedule.start_time)
            ).execute()

        if current_schedule.end_time:
            return schedule_model.delete().where(
                (schedule_model.group_id == old_group_id) &
                (schedule_model.id != schedule_id) &
                (schedule_model.end_time > current_schedule.end_time)
            ).execute()

        return schedule_model.delete().where(
            (schedule_model.group_id == old_group_id) &
            (schedule_model.id > schedule_id)
        ).execute()
