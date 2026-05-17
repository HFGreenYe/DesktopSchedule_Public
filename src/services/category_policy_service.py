"""Service boundary for category state/delete policy.

Round 3-1 only defines importable boundaries.
Concrete policy migration is deferred to 3-4.
"""

from __future__ import annotations

from enum import Enum
from typing import Iterable, TypeVar


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
    def evaluate_status(items: Iterable[T]) -> CategoryStatus:
        """Evaluate category status with legacy-compatible semantics."""
        raise NotImplementedError("Implemented in round 3-4.")

    @staticmethod
    def choose_delete_action(status: CategoryStatus) -> CategoryDeleteAction:
        """Map status to delete action with legacy-compatible semantics."""
        raise NotImplementedError("Implemented in round 3-4.")
