import datetime


class CategoryRepository:
    """Thin repository wrapper for low-risk Category operations."""

    def __init__(self, category_model=None, schedule_model=None):
        if category_model is None or schedule_model is None:
            from src.data.database import Category, Schedule

            if category_model is None:
                category_model = Category
            if schedule_model is None:
                schedule_model = Schedule

        self._category_model = category_model
        self._schedule_model = schedule_model

    def get_active_categories(self, list_type=None):
        query = self._category_model.select().where(self._category_model.is_deleted == False)
        if list_type:
            query = query.where(self._category_model.list_type == list_type)
        return list(query.order_by(self._category_model.sort_order.desc(), self._category_model.created_at.asc()))

    def update_category_fields(self, cat_id, **kwargs):
        try:
            self._category_model.update(**kwargs).where(self._category_model.id == cat_id).execute()
            return True
        except Exception as e:
            print(f"[DB] update category fields failed: {e}")
            return False

    def get_category_map(self):
        categories = self._category_model.select()
        return {c.id: c for c in categories}

    def get_category(self, cat_id):
        try:
            return self._category_model.get_by_id(cat_id)
        except Exception:
            return None

    def add_category(self, name, color="#0cc0df", list_type="schedule"):
        try:
            category = self._category_model.create(name=name, color=color, list_type=list_type)
            return category.id
        except Exception:
            return None

    def check_category_status(self, cat_id):
        schedules = list(self._schedule_model.select().where(self._schedule_model.category_id == cat_id))
        if not schedules:
            return "empty"

        now = datetime.datetime.now()
        for schedule in schedules:
            is_completed = schedule.status == 1
            is_expired = bool(schedule.end_time and schedule.end_time < now and not is_completed)
            if not is_completed and not is_expired:
                return "active"
        return "historical"

    def soft_delete_category(self, cat_id):
        try:
            self._category_model.update(is_deleted=True).where(self._category_model.id == cat_id).execute()
            return True
        except Exception:
            return False

    def hard_delete_category(self, cat_id):
        try:
            self._category_model.delete().where(self._category_model.id == cat_id).execute()
            return True
        except Exception:
            return False

