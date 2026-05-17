"""Service boundary for category state/delete policy.

Round 3-1 only defines importable boundaries.
Concrete policy migration is deferred to 3-4.
"""

from __future__ import annotations

import datetime
from enum import Enum
from typing import Iterable, TypeVar, Union


T = TypeVar("T")


class CategoryStatus(str, Enum):
    EMPTY = "empty"
    ACTIVE = "active"
    HISTORICAL = "historical"


class CategoryDeleteAction(str, Enum):
    BLOCK = "block"
    SOFT_DELETE = "soft_delete"
    HARD_DELETE = "hard_delete"


class CategoryPolicyService:
    """Pure category policy service boundary."""

    @staticmethod
    def evaluate_status(items: Iterable[T], now=None) -> CategoryStatus:
        """Evaluate category status with legacy-compatible semantics."""
        schedules = list(items)
        if not schedules:
            return CategoryStatus.EMPTY

        if now is None:
            now = datetime.datetime.now()

        for schedule in schedules:
            status = getattr(schedule, "status", 0)
            end_time = getattr(schedule, "end_time", None)
            is_completed = status == 1
            is_expired = bool(end_time and end_time < now and not is_completed)
            if not is_completed and not is_expired:
                return CategoryStatus.ACTIVE
        return CategoryStatus.HISTORICAL

    @staticmethod
    def choose_delete_action(status: Union[CategoryStatus, str]) -> CategoryDeleteAction:
        """Map status to delete action with legacy-compatible semantics."""
        if isinstance(status, CategoryStatus):
            normalized = status.value
        else:
            normalized = str(status)

        if normalized == CategoryStatus.ACTIVE.value:
            return CategoryDeleteAction.BLOCK
        if normalized == CategoryStatus.HISTORICAL.value:
            return CategoryDeleteAction.SOFT_DELETE
        if normalized == CategoryStatus.EMPTY.value:
            return CategoryDeleteAction.HARD_DELETE
        return CategoryDeleteAction.BLOCK
