"""Pure schedule query and filter helpers."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from typing import ClassVar, Iterable, List, Optional, Sequence, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class ScheduleQueryOptions:
    ALL_CATEGORIES = None
    UNCATEGORIZED = -1

    category_id: Optional[int] = ALL_CATEGORIES
    priority: Optional[int] = None
    status: Optional[int] = None
    time_kind: str = "all"
    search_scope: str = "title"
    match_mode: str = "fuzzy"

    def has_filter_constraints(self) -> bool:
        return any(
            (
                self.category_id is not self.ALL_CATEGORIES,
                self.priority is not None,
                self.status is not None,
                self.time_kind != "all",
            )
        )

    def with_search_preferences(self, search_scope: str, match_mode: str):
        return replace(
            self,
            search_scope=search_scope,
            match_mode=match_mode,
        )


@dataclass(frozen=True)
class WeekScheduleQueryOptions(ScheduleQueryOptions):
    ALL_WEEKDAYS: ClassVar[tuple[int, ...]] = tuple(range(7))

    weekdays: tuple[int, ...] = ALL_WEEKDAYS

    def __post_init__(self):
        normalized = tuple(
            sorted(
                {
                    int(weekday)
                    for weekday in self.weekdays
                    if 0 <= int(weekday) <= 6
                }
            )
        )
        object.__setattr__(self, "weekdays", normalized)

    def has_filter_constraints(self) -> bool:
        return (
            super().has_filter_constraints()
            or self.weekdays != self.ALL_WEEKDAYS
        )


class ScheduleQueryService:
    """Pure query/filter service boundary."""

    @staticmethod
    def filter_for_date(items: Iterable[T], target_date: date) -> List[T]:
        """Filter schedules/todos for target_date.

        Legacy-compatible date filtering rules extracted from repository.
        """
        filtered: List[T] = []
        for item in items:
            item_type = item.item_type
            if item_type == "todo":
                if not item.end_time:
                    filtered.append(item)
                    continue

            start_date = item.start_time.date() if item.start_time else None
            end_date = item.end_time.date() if item.end_time else None

            if start_date and end_date:
                if start_date <= target_date <= end_date:
                    filtered.append(item)
            elif end_date:
                if end_date == target_date:
                    filtered.append(item)
            else:
                filtered.append(item)

        return filtered

    @staticmethod
    def split_schedule_and_todo(items: Sequence[T]) -> tuple[List[T], List[T]]:
        """Split into (schedules, todos) with legacy-compatible rules."""
        schedules: List[T] = []
        todos: List[T] = []
        for item in items:
            if ScheduleQueryService.is_todo(item):
                todos.append(item)
            else:
                schedules.append(item)
        return schedules, todos

    @staticmethod
    def is_todo(item: T) -> bool:
        """Legacy todo predicate used by dashboard/todo/todo_board."""
        item_type = getattr(item, "item_type", None)
        legacy_type = getattr(item, "type", 0)
        return item_type == "todo" or legacy_type == 1

    @staticmethod
    def is_schedule(item: T) -> bool:
        """Legacy schedule predicate aligned with current week view semantics."""
        return getattr(item, "item_type", None) == "schedule"

    @staticmethod
    def apply_options(
        items: Iterable[T],
        options: ScheduleQueryOptions,
        keyword: str = "",
    ) -> List[T]:
        normalized_keyword = ScheduleQueryService._normalize_text(keyword)
        return [
            item
            for item in items
            if ScheduleQueryService._matches_options(
                item,
                options,
                normalized_keyword,
            )
        ]

    @staticmethod
    def _matches_options(item, options, normalized_keyword):
        category_id = getattr(item, "category_id", None)
        if options.category_id == ScheduleQueryOptions.UNCATEGORIZED:
            if category_id is not None:
                return False
        elif options.category_id is not None and category_id != options.category_id:
            return False

        if options.priority is not None:
            if int(getattr(item, "priority", 0) or 0) != options.priority:
                return False

        if options.status is not None:
            if int(getattr(item, "status", 0) or 0) != options.status:
                return False

        if not ScheduleQueryService._matches_time_kind(item, options.time_kind):
            return False

        if not normalized_keyword:
            return True

        fields = [getattr(item, "title", "")]
        if options.search_scope == "title_description":
            fields.append(getattr(item, "description", ""))
        normalized_fields = [
            ScheduleQueryService._normalize_text(field)
            for field in fields
        ]
        if options.match_mode == "exact":
            return any(field == normalized_keyword for field in normalized_fields)
        return any(normalized_keyword in field for field in normalized_fields)

    @staticmethod
    def _matches_time_kind(item, time_kind):
        if time_kind == "all":
            return True
        start_time = getattr(item, "start_time", None)
        end_time = getattr(item, "end_time", None)
        is_interval = bool(
            start_time is not None
            and end_time is not None
            and start_time != end_time
        )
        if time_kind == "interval":
            return is_interval
        if time_kind == "point":
            return not is_interval
        return True

    @staticmethod
    def _normalize_text(value):
        return str(value or "").strip().casefold()
