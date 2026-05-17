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
    def sort_for_day_view(items: Iterable[T]) -> List[T]:
        """Sort rule for day view (legacy-compatible).

        Implementation is intentionally deferred to round 3-3.
        """
        raise NotImplementedError("Implemented in round 3-3.")

    @staticmethod
    def sort_for_week_view(items: Iterable[T]) -> List[T]:
        """Sort rule for week view (legacy-compatible)."""
        raise NotImplementedError("Implemented in round 3-3.")

    @staticmethod
    def sort_for_todo_list(items: Iterable[T]) -> List[T]:
        """Sort rule for todo list (legacy-compatible)."""
        raise NotImplementedError("Implemented in round 3-3.")

    @staticmethod
    def sort_for_todo_board(items: Iterable[T]) -> List[T]:
        """Sort rule for todo board read path (legacy-compatible)."""
        raise NotImplementedError("Implemented in round 3-3.")
