from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QApplication, QWidget


class ThemeManager:
    """Basic theme helper for reading and applying QSS files."""
    DEFAULT_PRESET = "light.qss"
    SUPPORTED_PRESETS = ("light.qss", "dark.qss")

    def __init__(self, theme_dir: str | Path | None = None) -> None:
        default_dir = Path(__file__).resolve().parent
        self._theme_dir = Path(theme_dir) if theme_dir else default_dir

    @classmethod
    def get_available_presets(cls) -> tuple[str, ...]:
        return cls.SUPPORTED_PRESETS

    @classmethod
    def is_supported_preset(cls, file_name: str) -> bool:
        return file_name in cls.SUPPORTED_PRESETS

    def resolve_preset(self, file_name: str | None) -> str:
        if isinstance(file_name, str) and self.is_supported_preset(file_name):
            return file_name
        return self.DEFAULT_PRESET

    def get_qss_path(self, file_name: str) -> Path:
        return self._theme_dir / file_name

    def read_qss(self, file_name: str) -> str:
        qss_path = self.get_qss_path(file_name)
        return qss_path.read_text(encoding="utf-8")

    def read_qss_safe(self, file_name: str | None, fallback: str = "") -> str:
        if not file_name:
            return fallback
        try:
            return self.read_qss(file_name)
        except (OSError, UnicodeDecodeError):
            return fallback

    def apply_qss(self, app: QApplication, qss_content: str) -> None:
        app.setStyleSheet(qss_content)

    def apply_theme(self, app: QApplication, file_name: str | None) -> None:
        preset = self.resolve_preset(file_name)
        qss_content = self.read_qss_safe(preset, fallback="")
        self.apply_qss(app, qss_content)

    def refresh_widget_style(self, widget: QWidget) -> None:
        style = widget.style()
        style.unpolish(widget)
        style.polish(widget)
        widget.update()
