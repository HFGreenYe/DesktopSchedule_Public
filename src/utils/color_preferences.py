from PyQt6.QtCore import QSettings


_ORGANIZATION = "Wanji"
_APPLICATION = "DesktopSchedule"
_CUSTOM_COLORS_KEY = "color_dialog/custom_colors"


def get_color_dialog_custom_colors():
    value = QSettings(_ORGANIZATION, _APPLICATION).value(
        _CUSTOM_COLORS_KEY,
        [],
    )
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    return [str(color).strip() for color in value if str(color).strip()]


def set_color_dialog_custom_colors(colors):
    settings = QSettings(_ORGANIZATION, _APPLICATION)
    settings.setValue(
        _CUSTOM_COLORS_KEY,
        [str(color).strip() for color in colors if str(color).strip()],
    )
    settings.sync()
