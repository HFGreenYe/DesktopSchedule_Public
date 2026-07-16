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


DEFAULT_EXPORT_BACKGROUND_PRESETS = (
    ExportBackgroundPreset("默认 1", "#EAF6FF", "#9CCFFF"),
    ExportBackgroundPreset("默认 2", "#FFF0F4", "#FFB2C8"),
    ExportBackgroundPreset("默认 3", "#F0F7E8", "#B9D998"),
    ExportBackgroundPreset("默认 4", "#FFF6E5", "#F2C879"),
    ExportBackgroundPreset("默认 5", "#F1ECFF", "#B9A6F6"),
    ExportBackgroundPreset("默认 6", "#E8FAF6", "#83D8C5"),
    ExportBackgroundPreset("默认 7", "#FFF1E9", "#EBA783"),
    ExportBackgroundPreset("默认 8", "#E9EEF9", "#9DB1DD"),
    ExportBackgroundPreset(
        "GreenLeaf",
        "#0B3431",
        "#081E27",
        "GreenLeaf.jpg",
    ),
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
    path = (
        Path(__file__).resolve().parents[2]
        / "assets"
        / "Output_Background"
        / preset.image_file
    )
    return path if path.is_file() else None
