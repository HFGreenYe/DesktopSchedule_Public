import datetime


class ScheduleRepository:
    """Thin repository wrapper for low-risk Schedule operations."""

    def __init__(self, schedule_model=None):
        if schedule_model is None:
            from src.data.models import Schedule

            schedule_model = Schedule
        self._schedule_model = schedule_model

    def delete_schedule(self, schedule_id):
        try:
            self._schedule_model.delete().where(self._schedule_model.id == schedule_id).execute()
            return True
        except Exception:
            return False

    def update_schedule_status(self, schedule_id, new_status):
        try:
            self._schedule_model.update(status=new_status).where(
                self._schedule_model.id == schedule_id
            ).execute()
            return True
        except Exception:
            return False

    def update_schedule_fields(self, schedule_id, **kwargs):
        try:
            self._schedule_model.update(**kwargs).where(self._schedule_model.id == schedule_id).execute()
            return True
        except Exception as e:
            print(f"[DB] update schedule fields failed: {e}")
            return False

    def toggle_pin_status(self, schedule_id, current_pin_status):
        try:
            new_status = not current_pin_status
            self._schedule_model.update(is_pinned=new_status).where(
                self._schedule_model.id == schedule_id
            ).execute()
            return True
        except Exception:
            return False

    def get_all_schedules(self):
        return list(
            self._schedule_model.select().order_by(self._schedule_model.created_at.desc())
        )

    def get_schedules_for_date(self, target_date: datetime.date):
        all_data = list(self._schedule_model.select())
        filtered = []
        for schedule in all_data:
            item_type = schedule.item_type
            if item_type == "todo":
                if not schedule.end_time:
                    filtered.append(schedule)
                    continue

            start_date = schedule.start_time.date() if schedule.start_time else None
            end_date = schedule.end_time.date() if schedule.end_time else None

            if start_date and end_date:
                if start_date <= target_date <= end_date:
                    filtered.append(schedule)
            elif end_date:
                if end_date == target_date:
                    filtered.append(schedule)
            else:
                filtered.append(schedule)

        now = datetime.datetime.now()

        def sort_key(item):
            rank_pin = 0 if item.is_pinned else 1
            is_completed = item.status == 1
            is_expired = bool(item.end_time and item.end_time < now and not is_completed)

            if is_completed:
                rank_status = 3
            elif is_expired:
                rank_status = 2
            else:
                rank_status = 1

            time_val = item.start_time if item.start_time else item.created_at
            if not time_val:
                time_val = datetime.datetime.min
            return (rank_pin, rank_status, time_val)

        filtered.sort(key=sort_key)
        return filtered
