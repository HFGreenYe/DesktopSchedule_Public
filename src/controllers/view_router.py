"""Minimal routing decision helpers."""

from __future__ import annotations


class ViewRouter:
    """Pure helpers for view-name normalization and validation."""

    KNOWN_VIEWS = ("day", "week", "month", "todo")
    MAIN_SWITCH_VIEWS = ("day", "week", "month", "todo", "priority")

    @classmethod
    def normalize_view_name(cls, view_name):
        """Return normalized view name or ``None`` when unknown."""
        if not isinstance(view_name, str):
            return None
        candidate = view_name.strip().lower()
        return candidate if candidate in cls.KNOWN_VIEWS else None

    @classmethod
    def is_known_view(cls, view_name):
        """Check whether a view name is recognized."""
        return cls.normalize_view_name(view_name) is not None

    @classmethod
    def resolve_or_default(cls, view_name, default="day"):
        """Resolve to known view name, otherwise fallback to default."""
        normalized = cls.normalize_view_name(view_name)
        if normalized is not None:
            return normalized
        fallback = cls.normalize_view_name(default)
        return fallback if fallback is not None else "day"

    @classmethod
    def classify_main_view(cls, view_name):
        """Classify top-level view targets by exact string match."""
        if not isinstance(view_name, str):
            return None
        return view_name if view_name in cls.MAIN_SWITCH_VIEWS else None
