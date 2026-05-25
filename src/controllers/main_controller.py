"""Minimal coordinator entry for routing and refresh boundaries."""

from __future__ import annotations

from .refresh_coordinator import RefreshCoordinator
from .view_router import ViewRouter


class MainController:
    """Compose routing and refresh helpers without direct UI coupling."""

    def __init__(self, view_router=None, refresh_coordinator=None):
        self.view_router = view_router or ViewRouter()
        self.refresh_coordinator = refresh_coordinator or RefreshCoordinator()

    def normalize_view(self, view_name):
        """Normalize an incoming view name."""
        return self.view_router.normalize_view_name(view_name)

    def is_view_supported(self, view_name):
        """Check whether a view name is supported."""
        return self.view_router.is_known_view(view_name)

    def resolve_view(self, view_name, default="day"):
        """Resolve a view name with a deterministic fallback."""
        return self.view_router.resolve_or_default(view_name, default=default)

    def register_refresh_target(self, name, callback):
        """Register named refresh callback."""
        self.refresh_coordinator.register(name, callback)

    def unregister_refresh_target(self, name):
        """Remove named refresh callback."""
        self.refresh_coordinator.unregister(name)

    def request_refresh(self, name, *args, **kwargs):
        """Trigger one registered refresh callback."""
        return self.refresh_coordinator.trigger(name, *args, **kwargs)

    def request_refresh_many(self, names, *args, **kwargs):
        """Trigger multiple registered refresh callbacks."""
        return self.refresh_coordinator.trigger_many(names, *args, **kwargs)

    @staticmethod
    def resolve_add_source(current_widget, dashboard_widget, todo_widget, existing_source=None):
        """Resolve add-page source view while preserving prior source when unknown."""
        if current_widget is dashboard_widget or current_widget is todo_widget:
            return current_widget
        return existing_source

    @staticmethod
    def resolve_add_return_target(source_view, dashboard_widget):
        """Resolve add-page return target with dashboard as fallback."""
        return source_view if source_view is not None else dashboard_widget

    @staticmethod
    def default_to_schedule_for_add(current_widget, todo_widget):
        """Determine add-page default type based on entry view."""
        return current_widget is not todo_widget
