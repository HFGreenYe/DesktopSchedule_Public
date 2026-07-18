import json
from datetime import date, timedelta
from uuid import uuid4

from PyQt6.QtCore import QSettings


_ORGANIZATION = "Wanji"
_APPLICATION = "DesktopSchedule"
_SETTINGS_KEY = "commemoration_dates/items"
_REMINDER_DAYS = {0, 1, 3, 5, 7}


def _settings_instance(settings=None):
    if settings is not None:
        return settings
    return QSettings(_ORGANIZATION, _APPLICATION)


def _as_bool(value, default=True):
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def normalize_commemoration_item(value):
    if not isinstance(value, dict):
        return None

    name = str(value.get("name", "")).strip()
    date_text = str(value.get("date", "")).strip()
    if not name or not date_text:
        return None

    try:
        date.fromisoformat(date_text)
    except ValueError:
        return None

    item_id = str(value.get("id", "")).strip() or uuid4().hex
    try:
        reminder_days = int(value.get("reminder_days", 0))
    except (TypeError, ValueError):
        reminder_days = 0
    if reminder_days not in _REMINDER_DAYS:
        reminder_days = 0
    return {
        "id": item_id,
        "name": name,
        "date": date_text,
        "annual": _as_bool(value.get("annual"), True),
        "reminder_enabled": _as_bool(
            value.get("reminder_enabled"),
            False,
        ),
        "reminder_days": reminder_days,
    }


def create_commemoration_item(
    name,
    target_date,
    annual=True,
    reminder_enabled=False,
    reminder_days=0,
):
    if isinstance(target_date, date):
        date_text = target_date.isoformat()
    else:
        date_text = str(target_date).strip()

    return normalize_commemoration_item(
        {
            "id": uuid4().hex,
            "name": name,
            "date": date_text,
            "annual": annual,
            "reminder_enabled": reminder_enabled,
            "reminder_days": reminder_days,
        }
    )


def _annual_date(source_date, year):
    try:
        return date(year, source_date.month, source_date.day)
    except ValueError:
        return date(year, 2, 28)


def get_due_commemoration_dates(today=None, settings=None):
    today = today or date.today()
    due_items = []
    for item in load_commemoration_dates(settings):
        if not item["reminder_enabled"]:
            continue

        source_date = date.fromisoformat(item["date"])
        if item["annual"]:
            occurrences = (
                _annual_date(source_date, today.year),
                _annual_date(source_date, today.year + 1),
            )
        else:
            occurrences = (source_date,)

        advance = timedelta(days=item["reminder_days"])
        if any(
            today == occurrence or today == occurrence - advance
            for occurrence in occurrences
        ):
            due_items.append(item)
    return due_items


def load_commemoration_dates(settings=None):
    raw_value = _settings_instance(settings).value(_SETTINGS_KEY, "")
    if not raw_value:
        return []

    try:
        values = json.loads(str(raw_value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return []

    if not isinstance(values, list):
        return []

    items = []
    for value in values:
        normalized = normalize_commemoration_item(value)
        if normalized is not None:
            items.append(normalized)
    return items


def save_commemoration_dates(items, settings=None):
    normalized_items = []
    for item in items:
        normalized = normalize_commemoration_item(item)
        if normalized is not None:
            normalized_items.append(normalized)

    settings_instance = _settings_instance(settings)
    settings_instance.setValue(
        _SETTINGS_KEY,
        json.dumps(normalized_items, ensure_ascii=False, separators=(",", ":")),
    )
    settings_instance.sync()
    return normalized_items
