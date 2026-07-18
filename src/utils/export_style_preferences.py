import json
import re

from PyQt6.QtCore import QSettings

from src.config import AppConfig


_ORGANIZATION = "Wanji"
_APPLICATION = "DesktopSchedule"
_SETTINGS_KEY = "schedule_export/style_preferences"
_FORMATS = ("Markdown", "PDF", "PNG")
_FONT_FIELDS = ("标题", "详情", "备注")
_LANGUAGES = {"中", "英"}
_BACKGROUND_MODES = {"solid", "gradient", "default", "custom"}
_SIZE_PRESETS = {"2:3", "16:9", "3:4", "1:1", "9:16", "custom"}
_HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")


def _settings_instance(settings=None):
    if settings is not None:
        return settings
    return QSettings(_ORGANIZATION, _APPLICATION)


def _normalize_color(value, fallback):
    color = str(value or "").strip()
    if not _HEX_COLOR_PATTERN.fullmatch(color):
        return fallback
    return color.upper()


def _normalize_crop(value):
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        return None
    try:
        x, y, width, height = (float(item) for item in value)
    except (TypeError, ValueError):
        return None
    if width <= 0 or height <= 0:
        return None
    if x < 0 or y < 0 or x + width > 1.001 or y + height > 1.001:
        return None
    return [
        round(max(0.0, min(item, 1.0)), 8)
        for item in (x, y, width, height)
    ]


def _normalize_dimension(value, fallback):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return fallback
    return max(320, min(value, 8192))


def _normalize_path(value):
    return str(value or "").strip()[:2048]


def _default_font_state(field):
    return {
        "language": "中",
        "choices": {
            "中": "微软雅黑",
            "英": "Times New Roman",
        },
        "color": AppConfig.COLOR_GRADIENT_START.upper(),
        "bold": field == "标题",
        "italic": False,
    }


def _default_format_state():
    return {
        "background": {
            "mode": "solid",
            "solid_color": "#FFFFFF",
            "gradient_start": AppConfig.COLOR_GRADIENT_START.upper(),
            "gradient_end": AppConfig.COLOR_GRADIENT_END.upper(),
            "default_identifier": "name:默认 1",
            "crop": None,
            "custom_path": "",
            "custom_crop": None,
        },
        "fonts": {
            field: _default_font_state(field)
            for field in _FONT_FIELDS
        },
        "size": {
            "preset": "9:16",
            "width": 1080,
            "height": 1920,
        },
    }


def _normalize_font_state(value, field):
    default = _default_font_state(field)
    if not isinstance(value, dict):
        return default
    language = str(value.get("language", default["language"]))
    if language not in _LANGUAGES:
        language = default["language"]
    choices = value.get("choices")
    if not isinstance(choices, dict):
        choices = {}
    normalized_choices = {}
    for key in _LANGUAGES:
        family = str(choices.get(key, default["choices"][key]) or "").strip()
        normalized_choices[key] = family[:100] or default["choices"][key]
    return {
        "language": language,
        "choices": normalized_choices,
        "color": _normalize_color(value.get("color"), default["color"]),
        "bold": bool(value.get("bold", default["bold"])),
        "italic": bool(value.get("italic", default["italic"])),
    }


def _normalize_format_state(value):
    default = _default_format_state()
    if not isinstance(value, dict):
        value = {}

    background = value.get("background")
    if not isinstance(background, dict):
        background = {}
    mode = str(background.get("mode", default["background"]["mode"]))
    if mode not in _BACKGROUND_MODES:
        mode = default["background"]["mode"]
    default_identifier = str(
        background.get(
            "default_identifier",
            default["background"]["default_identifier"],
        )
        or ""
    ).strip()[:260]

    fonts = value.get("fonts")
    if not isinstance(fonts, dict):
        fonts = {}

    size = value.get("size")
    if not isinstance(size, dict):
        size = {}
    preset = str(size.get("preset", default["size"]["preset"]))
    if preset not in _SIZE_PRESETS:
        preset = default["size"]["preset"]
    width = _normalize_dimension(size.get("width"), default["size"]["width"])
    height = _normalize_dimension(size.get("height"), default["size"]["height"])
    if width * height > 40_000_000:
        width = default["size"]["width"]
        height = default["size"]["height"]

    return {
        "background": {
            "mode": mode,
            "solid_color": _normalize_color(
                background.get("solid_color"),
                default["background"]["solid_color"],
            ),
            "gradient_start": _normalize_color(
                background.get("gradient_start"),
                default["background"]["gradient_start"],
            ),
            "gradient_end": _normalize_color(
                background.get("gradient_end"),
                default["background"]["gradient_end"],
            ),
            "default_identifier": (
                default_identifier
                or default["background"]["default_identifier"]
            ),
            "crop": _normalize_crop(background.get("crop")),
            "custom_path": _normalize_path(background.get("custom_path")),
            "custom_crop": _normalize_crop(background.get("custom_crop")),
        },
        "fonts": {
            field: _normalize_font_state(fonts.get(field), field)
            for field in _FONT_FIELDS
        },
        "size": {
            "preset": preset,
            "width": width,
            "height": height,
        },
    }


def normalize_export_style_preferences(value):
    if not isinstance(value, dict):
        value = {}
    formats = value.get("formats")
    if not isinstance(formats, dict):
        formats = {}
    return {
        "version": 2,
        "formats": {
            export_format: _normalize_format_state(formats.get(export_format))
            for export_format in _FORMATS
        },
    }


def get_export_style_preferences(settings=None):
    raw_value = _settings_instance(settings).value(_SETTINGS_KEY, "")
    if not raw_value:
        return normalize_export_style_preferences({})
    try:
        value = json.loads(str(raw_value))
    except (TypeError, ValueError, json.JSONDecodeError):
        value = {}
    return normalize_export_style_preferences(value)


def set_export_style_preferences(preferences, settings=None):
    settings_instance = _settings_instance(settings)
    settings_instance.setValue(
        _SETTINGS_KEY,
        json.dumps(
            normalize_export_style_preferences(preferences),
            ensure_ascii=False,
            separators=(",", ":"),
        ),
    )
    settings_instance.sync()
