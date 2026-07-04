from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import (
    QColorDialog,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
)


class _ColorDialogHeader(QFrame):
    def __init__(self, title, accent, parent=None):
        super().__init__(parent)
        self._drag_offset = None
        self.setFixedHeight(36)
        self.setStyleSheet(
            f"QFrame {{ background-color: {accent}; border: none; }}"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 4, 0)
        layout.setSpacing(6)
        title_label = QLabel(title)
        title_label.setStyleSheet(
            "color: white; font-size: 13px; font-weight: bold; "
            "background: transparent; border: none;"
        )
        layout.addWidget(title_label)
        layout.addStretch()

        close_button = QPushButton("×")
        close_button.setFixedSize(28, 28)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setStyleSheet(
            "QPushButton { color: white; background: transparent; border: none; "
            "font-size: 18px; border-radius: 4px; } "
            "QPushButton:hover { background-color: #ff4d4f; }"
        )
        close_button.clicked.connect(parent.reject)
        layout.addWidget(close_button)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.window().pos()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self._drag_offset is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.window().move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_offset = None
        super().mouseReleaseEvent(event)


class ThemedColorDialog(QColorDialog):
    def __init__(self, initial_color, title, accent, parent=None):
        super().__init__(initial_color, parent)
        accent_color = QColor(accent)
        if not accent_color.isValid():
            accent_color = QColor("#0cc0df")
        accent = accent_color.name()
        self.setObjectName("themedColorDialog")
        self.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
        )
        self.setWindowTitle(title)
        self._apply_light_palette(accent_color)
        self.setStyleSheet(
            "QColorDialog#themedColorDialog { background-color: #ffffff; color: #333333; }"
            "QColorDialog#themedColorDialog QLabel { color: #333333; background: transparent; }"
            "QColorDialog#themedColorDialog QLineEdit, "
            "QColorDialog#themedColorDialog QSpinBox { background-color: #ffffff; "
            "color: #333333; border: 1px solid #cfcfcf; border-radius: 3px; "
            "padding: 2px 4px; selection-background-color: " + accent + "; }"
            "QColorDialog#themedColorDialog QPushButton { background-color: #f5f5f5; "
            "color: #333333; border: 1px solid #cfcfcf; border-radius: 4px; "
            "padding: 4px 12px; }"
            "QColorDialog#themedColorDialog QPushButton:hover { background-color: #e9e9e9; }"
        )

        header = _ColorDialogHeader(title, accent, self)
        dialog_layout = self.layout()
        if hasattr(dialog_layout, "insertWidget"):
            dialog_layout.setContentsMargins(0, 0, 0, 8)
            dialog_layout.insertWidget(0, header)
        self._header = header

    def _apply_light_palette(self, accent):
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#333333"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f5f5f5"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#333333"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#f5f5f5"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#333333"))
        palette.setColor(QPalette.ColorRole.Highlight, accent)
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        self.setPalette(palette)

    @classmethod
    def get_color(cls, initial_color, title, accent, parent=None):
        dialog = cls(initial_color, title, accent, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.currentColor()
        return QColor()
