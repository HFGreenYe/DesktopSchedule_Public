import json
import re

from PyQt6.QtCore import QSettings


_ORGANIZATION = "Wanji"
_APPLICATION = "DesktopSchedule"
_SETTINGS_KEY = "timetable/display_settings"
_HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")
_DISPLAY_MODES = {"card", "timetable"}
_DRAG_SNAP_MINUTES = {1, 5}


def _normalize_color(value):
    color = str(value or "").strip()
    if not _HEX_COLOR_PATTERN.fullmatch(color):
        return None
    return color.lower()


def _normalize_display_mode(value):
    mode = str(value or "").strip().lower()
    return mode if mode in _DISPLAY_MODES else "card"


def _normalize_drag_snap_minutes(value):
    try:
        minutes = int(value)
    except (TypeError, ValueError):
        return 1
    return minutes if minutes in _DRAG_SNAP_MINUTES else 1


def normalize_timetable_preferences(value):
    if not isinstance(value, dict):
        value = {}

    schedule_colors = value.get("schedule_colors")
    if not isinstance(schedule_colors, dict):
        schedule_colors = {}

    normalized_schedule_colors = {}
    for schedule_id, color in schedule_colors.items():
        try:
            normalized_id = str(int(schedule_id))
        except (TypeError, ValueError):
            continue
        normalized_color = _normalize_color(color)
        if normalized_color is not None:
            normalized_schedule_colors[normalized_id] = normalized_color

    return {
        "version": 1,
        "display_mode": _normalize_display_mode(value.get("display_mode")),
        "drag_snap_minutes": _normalize_drag_snap_minutes(
            value.get("drag_snap_minutes")
        ),
        "schedule_colors": normalized_schedule_colors,
    }


def get_timetable_preferences():
    raw_value = QSettings(_ORGANIZATION, _APPLICATION).value(_SETTINGS_KEY, "")
    if not raw_value:
        return normalize_timetable_preferences({})
    try:
        value = json.loads(str(raw_value))
    except (TypeError, ValueError, json.JSONDecodeError):
        value = {}
    return normalize_timetable_preferences(value)


def set_timetable_preferences(preferences):
    settings = QSettings(_ORGANIZATION, _APPLICATION)
    settings.setValue(
        _SETTINGS_KEY,
        json.dumps(
            normalize_timetable_preferences(preferences),
            ensure_ascii=False,
            separators=(",", ":"),
        ),
    )
    settings.sync()


def set_timetable_schedule_color(schedule_id, color):
    preferences = get_timetable_preferences()
    schedule_colors = dict(preferences.get("schedule_colors", {}))
    try:
        normalized_id = str(int(schedule_id))
    except (TypeError, ValueError):
        return preferences

    normalized_color = _normalize_color(color)
    if normalized_color is None:
        schedule_colors.pop(normalized_id, None)
    else:
        schedule_colors[normalized_id] = normalized_color

    preferences["schedule_colors"] = schedule_colors
    set_timetable_preferences(preferences)
    return preferences


def set_timetable_display_mode(mode_id):
    preferences = get_timetable_preferences()
    preferences["display_mode"] = _normalize_display_mode(mode_id)
    set_timetable_preferences(preferences)
    return preferences


def set_timetable_drag_snap_minutes(minutes):
    preferences = get_timetable_preferences()
    preferences["drag_snap_minutes"] = _normalize_drag_snap_minutes(minutes)
    set_timetable_preferences(preferences)
    return preferences
