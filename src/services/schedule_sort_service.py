"""Service boundary for schedule/todo sort strategies.

Round 3-1 only defines importable boundaries.
Concrete sort key migration is deferred to 3-3.
"""

from __future__ import annotations

from typing import Iterable, List, TypeVar


T = TypeVar("T")


class ScheduleSortService:
    """Pure sort strategy service boundary."""

    @staticmethod
    def _legacy_ui_sort_key(item: T) -> tuple[int, int, float]:
        rank_pin = 0 if getattr(item, "is_pinned", False) else 1
        rank_status = 3 if getattr(item, "status", 0) == 1 else 1
        sort_val = -getattr(item, "sort_order", 0.0)
        return (rank_pin, rank_status, sort_val)

    @staticmethod
    def sort_for_day_view(items: Iterable[T]) -> List[T]:
        """Sort rule for day view (legacy-compatible)."""
        return sorted(list(items), key=ScheduleSortService._legacy_ui_sort_key)

    @staticmethod
    def sort_for_week_view(items: Iterable[T]) -> List[T]:
        """Sort rule for week view (legacy-compatible)."""
        return sorted(list(items), key=ScheduleSortService._legacy_ui_sort_key)

    @staticmethod
    def sort_for_todo_list(items: Iterable[T]) -> List[T]:
        """Sort rule for todo list (legacy-compatible)."""
        return sorted(list(items), key=ScheduleSortService._legacy_ui_sort_key)

    @staticmethod
    def sort_for_todo_board(items: Iterable[T]) -> List[T]:
        """Sort rule for todo board read path (legacy-compatible)."""
        raise NotImplementedError("Implemented in round 3-3.")
