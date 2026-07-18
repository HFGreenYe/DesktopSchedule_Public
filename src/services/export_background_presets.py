"""Built-in decorative backgrounds shared by export UI and renderers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExportBackgroundPreset:
    name: str
    top_color: str
    bottom_color: str
    image_file: str = ""
    label_color: str = ""


DEFAULT_EXPORT_BACKGROUND_DISPLAY_NAMES = {
    "BlueCorridor": "深蓝回廊",
    "BlueVibe": "蓝调氛围",
    "CityDrive": "城市驾驶",
    "DeviceWorld": "设备世界",
    "GreenLeaf": "幽绿之叶",
    "LonelyHouse": "孤独小屋",
    "OrderOfNature": "自然秩序",
    "RhythmOfColor1": "颜色律动1",
    "RhythmOfColor2": "颜色律动2",
    "RhythmOfColor3": "颜色律动3",
    "RhythmOfColor4": "颜色律动4",
    "SeaCliff": "海边悬崖",
    "SilenceBoat": "沉静之船",
    "SilenceNight": "幽宁之夜",
    "SkyofStars": "星河天空",
    "SpaceDream": "太空梦想",
    "SpiritedAway1": "千与千寻1",
    "SpiritedAway2": "千与千寻2",
    "SpiritedAway3": "千与千寻3",
    "TourOfVikings": "维京之旅",
}


DEFAULT_EXPORT_BACKGROUND_LABEL_COLORS = {
    "GreenLeaf": "#CDEED8",
}


_GRADIENT_EXPORT_BACKGROUND_PRESETS = (
    ExportBackgroundPreset("默认 1", "#EAF6FF", "#9CCFFF"),
    ExportBackgroundPreset("默认 2", "#E8FAF6", "#83D8C5"),
    ExportBackgroundPreset("默认 3", "#E9EEF9", "#9DB1DD"),
)


def _background_directory() -> Path:
    return Path(__file__).resolve().parents[2] / "assets" / "Output_Background"


def _discover_image_presets() -> tuple[ExportBackgroundPreset, ...]:
    directory = _background_directory()
    if not directory.is_dir():
        return ()
    supported_suffixes = {".jpg", ".jpeg", ".png", ".webp"}
    presets = []
    for path in sorted(directory.iterdir(), key=lambda item: item.name.casefold()):
        if not path.is_file() or path.suffix.casefold() not in supported_suffixes:
            continue
        resource_name = path.stem
        presets.append(
            ExportBackgroundPreset(
                DEFAULT_EXPORT_BACKGROUND_DISPLAY_NAMES.get(
                    resource_name,
                    resource_name,
                ),
                "#DDEFE8",
                "#A9D6C5",
                path.name,
                DEFAULT_EXPORT_BACKGROUND_LABEL_COLORS.get(resource_name, ""),
            )
        )
    return tuple(presets)


DEFAULT_EXPORT_BACKGROUND_PRESETS = (
    _GRADIENT_EXPORT_BACKGROUND_PRESETS + _discover_image_presets()
)


def get_export_background_preset(index: int) -> ExportBackgroundPreset:
    return DEFAULT_EXPORT_BACKGROUND_PRESETS[
        int(index) % len(DEFAULT_EXPORT_BACKGROUND_PRESETS)
    ]


def get_export_background_image_path(
    preset: ExportBackgroundPreset,
) -> Path | None:
    if not preset.image_file:
        return None
    path = _background_directory() / preset.image_file
    return path if path.is_file() else None
