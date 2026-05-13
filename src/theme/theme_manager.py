from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QApplication, QWidget


class ThemeManager:
    """Basic theme helper for reading and applying QSS files."""

    def __init__(self, theme_dir: str | Path | None = None) -> None:
        default_dir = Path(__file__).resolve().parent
        self._theme_dir = Path(theme_dir) if theme_dir else default_dir

    def get_qss_path(self, file_name: str) -> Path:
        return self._theme_dir / file_name

    def read_qss(self, file_name: str) -> str:
        qss_path = self.get_qss_path(file_name)
        return qss_path.read_text(encoding="utf-8")

    def apply_qss(self, app: QApplication, qss_content: str) -> None:
        app.setStyleSheet(qss_content)

    def apply_theme(self, app: QApplication, file_name: str) -> None:
        qss_content = self.read_qss(file_name)
        self.apply_qss(app, qss_content)

    def refresh_widget_style(self, widget: QWidget) -> None:
        style = widget.style()
        style.unpolish(widget)
        style.polish(widget)
        widget.update()

