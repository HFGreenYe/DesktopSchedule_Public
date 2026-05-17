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
        """Split into (schedules, todos) with legacy-compatible rules.

        Implementation is intentionally deferred to round 3-2.
        """
        raise NotImplementedError("Implemented in round 3-2.")
