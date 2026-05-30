"""Minimal refresh callback coordinator."""

from __future__ import annotations

class RefreshCoordinator:
    """Store and trigger named refresh callbacks explicitly."""

    def __init__(self):
        self._callbacks = {}

    def register(self, name, callback):
        """Register a callable refresh target by name."""
        if not isinstance(name, str):
            raise TypeError("name must be str")
        if not callable(callback):
            raise TypeError("callback must be callable")
        self._callbacks[name] = callback

    def unregister(self, name):
        """Remove a refresh callback by name."""
        self._callbacks.pop(name, None)

    def has(self, name):
        """Return ``True`` when a callback is registered."""
        return name in self._callbacks

    def trigger(self, name, *args, **kwargs):
        """Invoke a named callback if it exists."""
        callback = self._callbacks.get(name)
        if callback is None:
            return False
        callback(*args, **kwargs)
        return True

    def trigger_many(self, names, *args, **kwargs):
        """Invoke callbacks for a sequence of names, preserving order."""
        invoked = 0
        for name in names:
            if self.trigger(name, *args, **kwargs):
                invoked += 1
        return invoked
