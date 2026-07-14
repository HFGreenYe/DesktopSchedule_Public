import json

from PyQt6.QtCore import QSettings

from src.services.schedule_sort_service import ScheduleSortOptions


_ORGANIZATION = "Wanji"
_APPLICATION = "DesktopSchedule"
_SETTINGS_KEY = "schedule_sort/display_settings"
_SCOPES = {"day", "week", "month", "todo"}
_ITEM_SCOPES = {"all", "point", "interval"}
_SCHEMES = {"time", "priority"}


def _normalize_view_scope(value):
    scope = str(value or "").strip().lower()
    return scope if scope in _SCOPES else "day"


def _normalize_item_scope(value):
    item_scope = str(value or "").strip().lower()
    return item_scope if item_scope in _ITEM_SCOPES else "all"


def _normalize_scheme(value):
    scheme = str(value or "").strip().lower()
    return scheme if scheme in _SCHEMES else "time"


def _normalize_bool(value, default=True):
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def normalize_schedule_sort_preferences(value):
    if not isinstance(value, dict):
        value = {}

    normalized = {"version": 1, "views": {}}
    views = value.get("views")
    if not isinstance(views, dict):
        views = {}

    for view_scope in _SCOPES:
        raw_options = views.get(view_scope, {})
        if not isinstance(raw_options, dict):
            raw_options = {}
        normalized["views"][view_scope] = {
            "enabled": _normalize_bool(
                raw_options.get("enabled"),
                default=False,
            ),
            "include_completed": _normalize_bool(
                raw_options.get("include_completed"),
                default=True,
            ),
            "include_overdue": _normalize_bool(
                raw_options.get("include_overdue"),
                default=True,
            ),
            "item_scope": _normalize_item_scope(raw_options.get("item_scope")),
            "scheme": _normalize_scheme(raw_options.get("scheme")),
        }
    return normalized


def get_schedule_sort_preferences():
    raw_value = QSettings(_ORGANIZATION, _APPLICATION).value(_SETTINGS_KEY, "")
    if not raw_value:
        return normalize_schedule_sort_preferences({})
    try:
        value = json.loads(str(raw_value))
    except (TypeError, ValueError, json.JSONDecodeError):
        value = {}
    return normalize_schedule_sort_preferences(value)


def set_schedule_sort_preferences(preferences):
    settings = QSettings(_ORGANIZATION, _APPLICATION)
    settings.setValue(
        _SETTINGS_KEY,
        json.dumps(
            normalize_schedule_sort_preferences(preferences),
            ensure_ascii=False,
            separators=(",", ":"),
        ),
    )
    settings.sync()


def get_schedule_sort_options(view_scope):
    preferences = get_schedule_sort_preferences()
    scope = _normalize_view_scope(view_scope)
    value = preferences["views"].get(scope, {})
    return ScheduleSortOptions(
        include_completed=bool(value.get("include_completed", True)),
        include_overdue=bool(value.get("include_overdue", True)),
        item_scope=_normalize_item_scope(value.get("item_scope")),
        scheme=_normalize_scheme(value.get("scheme")),
        enabled=bool(value.get("enabled", False)),
    )


def set_schedule_sort_options(view_scope, options):
    preferences = get_schedule_sort_preferences()
    scope = _normalize_view_scope(view_scope)
    preferences["views"][scope] = {
        "enabled": bool(getattr(options, "enabled", False)),
        "include_completed": bool(getattr(options, "include_completed", True)),
        "include_overdue": bool(getattr(options, "include_overdue", True)),
        "item_scope": _normalize_item_scope(getattr(options, "item_scope", "all")),
        "scheme": _normalize_scheme(getattr(options, "scheme", "time")),
    }
    set_schedule_sort_preferences(preferences)
    return get_schedule_sort_options(scope)
