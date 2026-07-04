import datetime
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class AxisScheduleProjection:
    schedule: object
    start_delta_hours: float
    end_delta_hours: float
    is_interval: bool
    category_color: str
    category_name: str
    importance: int
    is_completed: bool


@dataclass(frozen=True)
class AxisCategoryOption:
    category_id: int
    name: str
    color: str


class ScheduleAxisService:
    MIN_RANGE_HOURS = 24.0
    MAX_RANGE_HOURS = 365.0 * 24.0
    FALLBACK_COLOR = "#ffffff"

    @classmethod
    def load_category_options(cls):
        from src.repositories.category_repository import CategoryRepository

        categories = CategoryRepository().get_active_categories("schedule")
        return [
            AxisCategoryOption(
                category_id=category.id,
                name=category.name,
                color=getattr(category, "color", None) or cls.FALLBACK_COLOR,
            )
            for category in categories
        ]

    @classmethod
    def load_current_projection(cls, now=None):
        from src.repositories.category_repository import CategoryRepository
        from src.repositories.schedule_repository import ScheduleRepository

        schedules = ScheduleRepository().get_all_schedules()
        category_map = CategoryRepository().get_category_map()
        return cls.build_projection(schedules, category_map, now)

    @classmethod
    def build_projection(cls, schedules, category_map, now=None):
        now = now or datetime.datetime.now()
        projections = []
        furthest_hours = 0.0

        for schedule in schedules:
            if getattr(schedule, "item_type", "schedule") != "schedule":
                continue
            status = int(getattr(schedule, "status", 0) or 0)
            if status == 2:
                continue

            start_time = cls._as_datetime(getattr(schedule, "start_time", None))
            end_time = cls._as_datetime(getattr(schedule, "end_time", None))
            if start_time is None and end_time is None:
                continue

            if start_time is None:
                start_time = end_time
            if end_time is None:
                end_time = start_time

            start_delta = (start_time - now).total_seconds() / 3600.0
            end_delta = (end_time - now).total_seconds() / 3600.0
            is_interval = start_time != end_time
            if start_delta > end_delta:
                start_delta, end_delta = end_delta, start_delta

            category = category_map.get(getattr(schedule, "category_id", None))
            category_color = getattr(category, "color", None) or cls.FALLBACK_COLOR
            category_name = getattr(category, "name", None) or "未分类"
            importance = max(0, min(int(getattr(schedule, "priority", 0)), 2))

            projections.append(
                AxisScheduleProjection(
                    schedule=schedule,
                    start_delta_hours=start_delta,
                    end_delta_hours=end_delta,
                    is_interval=is_interval,
                    category_color=category_color,
                    category_name=category_name,
                    importance=importance,
                    is_completed=status == 1,
                )
            )
            furthest_hours = max(furthest_hours, abs(start_delta), abs(end_delta))

        range_hours = max(cls.MIN_RANGE_HOURS, furthest_hours)
        range_hours = min(range_hours, cls.MAX_RANGE_HOURS)
        return projections, range_hours

    @classmethod
    def map_delta_to_x(
        cls,
        delta_hours,
        range_hours,
        left,
        right,
        log_scale=1.0,
    ):
        range_hours = max(float(range_hours), cls.MIN_RANGE_HOURS)
        delta_hours = max(-range_hours, min(float(delta_hours), range_hours))
        center = (float(left) + float(right)) / 2.0
        half_width = max((float(right) - float(left)) / 2.0, 0.0)
        if delta_hours == 0 or half_width == 0:
            return center

        log_scale = max(float(log_scale), 1e-12)
        normalized = math.log1p(log_scale * abs(delta_hours)) / math.log1p(
            log_scale * range_hours
        )
        direction = -1.0 if delta_hours < 0 else 1.0
        return center + direction * normalized * half_width

    @classmethod
    def map_x_to_delta(
        cls,
        x,
        range_hours,
        left,
        right,
        log_scale=1.0,
    ):
        range_hours = max(float(range_hours), cls.MIN_RANGE_HOURS)
        center = (float(left) + float(right)) / 2.0
        half_width = max((float(right) - float(left)) / 2.0, 0.0)
        if half_width == 0:
            return 0.0

        normalized = max(-1.0, min(1.0, (float(x) - center) / half_width))
        direction = -1.0 if normalized < 0 else 1.0
        magnitude = abs(normalized)
        log_scale = max(float(log_scale), 1e-12)
        delta = math.expm1(
            magnitude * math.log1p(log_scale * range_hours)
        ) / log_scale
        return direction * delta

    @classmethod
    def solve_log_scale(cls, range_hours, focus_hours, target_fraction):
        range_hours = max(float(range_hours), cls.MIN_RANGE_HOURS)
        focus_hours = max(0.0, min(float(focus_hours), range_hours))
        target_fraction = max(0.0, min(float(target_fraction), 1.0))
        linear_fraction = focus_hours / range_hours
        if focus_hours == 0 or target_fraction <= linear_fraction:
            return 1e-12
        if target_fraction >= 1.0:
            return 1e12

        low = 1e-12
        high = 1e12
        for _ in range(96):
            middle = math.sqrt(low * high)
            fraction = math.log1p(middle * focus_hours) / math.log1p(
                middle * range_hours
            )
            if fraction < target_fraction:
                low = middle
            else:
                high = middle
        return math.sqrt(low * high)

    @staticmethod
    def format_range(range_hours):
        if range_hours >= 365 * 24:
            return "1年"
        if range_hours >= 30 * 24:
            return f"{max(1, round(range_hours / (30 * 24)))}个月"
        if range_hours >= 24:
            return f"{max(1, round(range_hours / 24))}天"
        return f"{max(1, round(range_hours))}小时"

    @staticmethod
    def _as_datetime(value):
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, datetime.date):
            return datetime.datetime.combine(value, datetime.time.min)
        return None
