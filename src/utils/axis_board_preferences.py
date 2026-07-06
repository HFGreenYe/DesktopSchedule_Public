import json
import re

from PyQt6.QtCore import QSettings


_ORGANIZATION = "Wanji"
_APPLICATION = "DesktopSchedule"
_SETTINGS_KEY = "axis_board/display_settings"
_HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")
_VALID_DIRECTIONS = {"future", "both", "past"}
_VALID_RANGES = {"day", "week", "two_weeks", "month", "year"}


def _normalize_color(value):
    color = str(value or "").strip()
    if not _HEX_COLOR_PATTERN.fullmatch(color):
        return None
    return color.lower()


def _normalize_alpha(value):
    try:
        return max(0, min(int(value), 100))
    except (TypeError, ValueError):
        return 100


def _normalize_appearance(value):
    if not isinstance(value, dict):
        return None
    color = _normalize_color(value.get("color"))
    if color is None:
        return None
    return {
        "color": color,
        "alpha": _normalize_alpha(value.get("alpha", 100)),
    }


def normalize_axis_board_preferences(value):
    if not isinstance(value, dict):
        value = {}

    state = value.get("state")
    if not isinstance(state, dict):
        state = {}
    direction = state.get("direction", "both")
    if direction not in _VALID_DIRECTIONS:
        direction = "both"
    range_value = state.get("range", "month")
    if range_value not in _VALID_RANGES:
        range_value = "month"
    nonlinear = state.get("nonlinear", True)
    if not isinstance(nonlinear, bool):
        nonlinear = True
    show_completed = state.get("show_completed", True)
    if not isinstance(show_completed, bool):
        show_completed = True

    appearance = value.get("appearance")
    if not isinstance(appearance, dict):
        appearance = {}
    normalized_appearance = {}
    for key in ("axis", "font"):
        normalized = _normalize_appearance(appearance.get(key))
        if normalized is not None:
            normalized_appearance[key] = normalized

    categories = value.get("categories")
    if not isinstance(categories, dict):
        categories = {}
    normalized_categories = {}
    for category_id, category_appearance in categories.items():
        try:
            normalized_id = str(int(category_id))
        except (TypeError, ValueError):
            continue
        normalized = _normalize_appearance(category_appearance)
        if normalized is not None:
            normalized_categories[normalized_id] = normalized

    return {
        "version": 1,
        "state": {
            "nonlinear": nonlinear,
            "show_completed": show_completed,
            "direction": direction,
            "range": range_value,
        },
        "appearance": normalized_appearance,
        "categories": normalized_categories,
    }


def get_axis_board_preferences():
    raw_value = QSettings(_ORGANIZATION, _APPLICATION).value(_SETTINGS_KEY, "")
    if not raw_value:
        return normalize_axis_board_preferences({})
    try:
        value = json.loads(str(raw_value))
    except (TypeError, ValueError, json.JSONDecodeError):
        value = {}
    return normalize_axis_board_preferences(value)


def set_axis_board_preferences(preferences):
    settings = QSettings(_ORGANIZATION, _APPLICATION)
    settings.setValue(
        _SETTINGS_KEY,
        json.dumps(
            normalize_axis_board_preferences(preferences),
            ensure_ascii=False,
            separators=(",", ":"),
        ),
    )
    settings.sync()
