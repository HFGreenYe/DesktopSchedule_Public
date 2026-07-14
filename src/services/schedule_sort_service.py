"""Service boundary for schedule/todo sort strategies."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class ScheduleSortOptions:
    include_completed: bool = True
    include_overdue: bool = True
    item_scope: str = "all"
    scheme: str = "time"
    enabled: bool = False

    def is_default(self) -> bool:
        return (
            not self.enabled
            and self.include_completed
            and self.include_overdue
            and self.item_scope == "all"
            and self.scheme == "time"
        )


class ScheduleSortService:
    """Pure display sort and visibility strategy service boundary."""

    DEFAULT_OPTIONS = ScheduleSortOptions()

    @staticmethod
    def _legacy_ui_sort_key(item: T) -> tuple[int, int, float]:
        rank_pin = 0 if getattr(item, "is_pinned", False) else 1
        rank_status = 3 if getattr(item, "status", 0) == 1 else 1
        sort_val = -getattr(item, "sort_order", 0.0)
        return (rank_pin, rank_status, sort_val)

    @staticmethod
    def _is_completed(item: T) -> bool:
        return int(getattr(item, "status", 0) or 0) == 1

    @staticmethod
    def _is_interval(item: T) -> bool:
        start_time = getattr(item, "start_time", None)
        end_time = getattr(item, "end_time", None)
        return bool(
            start_time is not None
            and end_time is not None
            and start_time != end_time
        )

    @staticmethod
    def _effective_time(item: T) -> datetime:
        if ScheduleSortService._is_interval(item):
            value = getattr(item, "end_time", None)
        else:
            value = getattr(item, "end_time", None) or getattr(item, "start_time", None)
        if isinstance(value, datetime):
            return value
        created_at = getattr(item, "created_at", None)
        if isinstance(created_at, datetime):
            return created_at
        return datetime.max

    @staticmethod
    def _is_overdue(item: T, now: datetime) -> bool:
        if ScheduleSortService._is_completed(item):
            return False
        effective_time = ScheduleSortService._effective_time(item)
        return effective_time != datetime.max and effective_time < now

    @staticmethod
    def _matches_scope(item: T, item_scope: str) -> bool:
        if item_scope == "all":
            return True
        is_interval = ScheduleSortService._is_interval(item)
        if item_scope == "interval":
            return is_interval
        if item_scope == "point":
            return not is_interval
        return True

    @staticmethod
    def _visible_items(
        items: Iterable[T],
        options: ScheduleSortOptions,
        now: datetime | None = None,
    ) -> List[T]:
        current_time = now or datetime.now()
        visible: List[T] = []
        for item in items:
            if not options.include_completed and ScheduleSortService._is_completed(item):
                continue
            if not options.include_overdue and ScheduleSortService._is_overdue(item, current_time):
                continue
            if not ScheduleSortService._matches_scope(item, options.item_scope):
                continue
            visible.append(item)
        return visible

    @staticmethod
    def _display_sort_key(item: T, options: ScheduleSortOptions) -> tuple:
        rank_pin = 0 if getattr(item, "is_pinned", False) else 1
        rank_status = 3 if ScheduleSortService._is_completed(item) else 1
        effective_time = ScheduleSortService._effective_time(item)
        priority_rank = -int(getattr(item, "priority", 0) or 0)
        item_id = int(getattr(item, "id", 0) or 0)

        if options.scheme == "priority":
            primary = (priority_rank, effective_time)
        else:
            primary = (effective_time, priority_rank)
        return (rank_pin, rank_status, *primary, item_id)

    @staticmethod
    def _sort_items(
        items: Iterable[T],
        options: ScheduleSortOptions | None,
        now: datetime | None = None,
    ) -> List[T]:
        normalized_options = options or ScheduleSortService.DEFAULT_OPTIONS
        if not normalized_options.enabled:
            return sorted(list(items), key=ScheduleSortService._legacy_ui_sort_key)
        visible = ScheduleSortService._visible_items(
            items,
            normalized_options,
            now=now,
        )
        return sorted(
            visible,
            key=lambda item: ScheduleSortService._display_sort_key(
                item,
                normalized_options,
            ),
        )

    @staticmethod
    def sort_for_day_view(
        items: Iterable[T],
        options: ScheduleSortOptions | None = None,
    ) -> List[T]:
        """Sort rule for day view."""
        return ScheduleSortService._sort_items(items, options)

    @staticmethod
    def sort_for_week_view(
        items: Iterable[T],
        options: ScheduleSortOptions | None = None,
    ) -> List[T]:
        """Sort rule for week view."""
        return ScheduleSortService._sort_items(items, options)

    @staticmethod
    def sort_for_month_day_panel(
        items: Iterable[T],
        options: ScheduleSortOptions | None = None,
    ) -> List[T]:
        """Sort rule for month date popup list."""
        return ScheduleSortService._sort_items(items, options)

    @staticmethod
    def sort_for_todo_list(
        items: Iterable[T],
        options: ScheduleSortOptions | None = None,
    ) -> List[T]:
        """Sort rule for todo list."""
        return ScheduleSortService._sort_items(items, options)

    @staticmethod
    def sort_for_todo_board(items: Iterable[T]) -> List[T]:
        """Sort rule for todo board read path (legacy-compatible)."""
        return sorted(
            list(items),
            key=lambda item: (
                0 if getattr(item, "is_pinned", False) else 1,
                -getattr(item, "sort_order", 0.0),
            ),
        )
