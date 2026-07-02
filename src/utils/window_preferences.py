from PyQt6.QtCore import QSettings, Qt


_ORGANIZATION = "Wanji"
_APPLICATION = "DesktopSchedule"
_PRIMARY_PIN_KEY = "window/primary_always_on_top"


def get_primary_pin_preference(default=True):
    value = QSettings(_ORGANIZATION, _APPLICATION).value(
        _PRIMARY_PIN_KEY,
        default,
    )
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def set_primary_pin_preference(enabled):
    settings = QSettings(_ORGANIZATION, _APPLICATION)
    settings.setValue(_PRIMARY_PIN_KEY, bool(enabled))
    settings.sync()


def set_window_pin_state(window, enabled):
    enabled = bool(enabled)
    current = bool(window.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)
    if current == enabled:
        return False

    was_visible = window.isVisible()
    window.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, enabled)
    if was_visible:
        window.show()
    return True
