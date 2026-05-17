"""Service boundary for schedule query/filter logic.

Round 3-1 only defines importable boundaries.
Concrete date filtering and todo/schedule partition logic is deferred to 3-2.
"""

from __future__ import annotations

from datetime import date
from typing import Iterable, List, Sequence, TypeVar


T = TypeVar("T")


class ScheduleQueryService:
    """Pure query/filter service boundary."""

    @staticmethod
    def filter_for_date(items: Iterable[T], target_date: date) -> List[T]:
        """Filter schedules/todos for target_date.

        Implementation is intentionally deferred to round 3-2.
        """
        raise NotImplementedError("Implemented in round 3-2.")

    @staticmethod
    def split_schedule_and_todo(items: Sequence[T]) -> tuple[List[T], List[T]]:
        """Split into (schedules, todos) with legacy-compatible rules.

        Implementation is intentionally deferred to round 3-2.
        """
        raise NotImplementedError("Implemented in round 3-2.")
