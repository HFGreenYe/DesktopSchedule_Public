from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QIcon, QPainterPath, QPalette, QRegion
from PyQt6.QtWidgets import (
    QColorDialog,
    QDialog,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class _ColorDialogHeader(QLabel):
    def __init__(self, title, accent, parent=None):
        super().__init__(parent)
        self._drag_offset = None
        self.setFixedHeight(32)
        self.setObjectName("ColorDialogHeader")
        self.setStyleSheet(
            "QLabel#ColorDialogHeader { "
            f"background-color: {accent}; border: none; "
            "border-top-left-radius: 12px; border-top-right-radius: 12px; }"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 0, 0)
        layout.setSpacing(6)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(
            "color: white; font-size: 13px; font-weight: bold; "
            "background: transparent; border: none;"
        )
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.close_button = QPushButton()
        self.close_button.setFixedSize(30, 30)
        self.close_button.setIconSize(QSize(12, 12))
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setToolTip("关闭")
        self.close_button.setStyleSheet(
            "QPushButton { color: white; background: transparent; border: none; "
            "border-top-right-radius: 12px; } "
            "QPushButton:hover { background-color: #ff4d4f; }"
        )
        close_icon = QIcon("assets/icons/close.png")
        if not close_icon.isNull():
            self.close_button.setIcon(close_icon)
        else:
            self.close_button.setText("×")
        self.close_button.clicked.connect(parent.reject)
        layout.addWidget(self.close_button)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.window().toggle_content_theme()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

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


class ThemedColorDialog(QDialog):
    CONTENT_SCALE = 0.75
    CORNER_RADIUS = 12

    _TEXT_TRANSLATIONS = {
        "Basic colors": "基本颜色",
        "Pick Screen Color": "拾取屏幕颜色",
        "Custom colors": "自定义颜色",
        "Add to Custom Colors": "添加到自定义颜色",
        "Hue:": "色相：",
        "Sat:": "饱和度：",
        "Val:": "明度：",
        "Red:": "R：",
        "Green:": "G：",
        "Blue:": "B：",
        "Alpha channel:": "透明度：",
        "HTML:": "HTML：",
        "OK": "确定",
        "Cancel": "取消",
    }

    def __init__(self, initial_color, title, accent, parent=None):
        super().__init__(parent)
        accent_color = QColor(accent)
        if not accent_color.isValid():
            accent_color = QColor("#0cc0df")
        self._accent = accent_color
        self._dark_content = False
        self._spin_buttons = []

        self.setObjectName("themedColorDialog")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowTitle(title)

        self._color_dialog = QColorDialog(initial_color)
        self._color_dialog.setOption(
            QColorDialog.ColorDialogOption.DontUseNativeDialog,
            True,
        )
        self._color_dialog.setWindowFlags(Qt.WindowType.Widget)
        self._color_dialog.accepted.connect(self.accept)
        self._color_dialog.rejected.connect(self.reject)
        self._translate_qt_controls()
        self._install_spin_controls()
        self._apply_content_theme()

        inner_layout = self._color_dialog.layout()
        inner_layout.setContentsMargins(10, 4, 10, 8)
        inner_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self._color_dialog.adjustSize()
        compact_height = self._color_dialog.height()
        inner_layout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self._color_dialog.setFixedSize(652, compact_height)

        self._scene = QGraphicsScene(self)
        self._color_dialog.move(0, 0)
        self._proxy = self._scene.addWidget(self._color_dialog)
        self._proxy.setPos(0, 0)
        self._proxy.setScale(self.CONTENT_SCALE)
        inner_size = self._color_dialog.size()
        scaled_width = round(inner_size.width() * self.CONTENT_SCALE)
        scaled_height = round(inner_size.height() * self.CONTENT_SCALE)
        self._scene.setSceneRect(QRectF(0, 0, scaled_width, scaled_height))

        self._view = QGraphicsView(self._scene, self)
        self._view.setFrameShape(QGraphicsView.Shape.NoFrame)
        self._view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._view.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._view.setFixedSize(scaled_width, scaled_height)
        self._view.setStyleSheet("QGraphicsView { border: none; background: transparent; }")

        self._header = _ColorDialogHeader(title, self._accent.name(), self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._header)
        layout.addWidget(self._view)
        self.setFixedSize(scaled_width, self._header.height() + scaled_height)
        self._update_window_mask()

    @staticmethod
    def _normalized_text(text):
        return str(text).replace("&", "").strip()

    def _translate_qt_controls(self):
        for label in self._color_dialog.findChildren(QLabel):
            normalized = self._normalized_text(label.text())
            translated = self._TEXT_TRANSLATIONS.get(normalized)
            if translated is not None:
                label.setText(translated)

        for button in self._color_dialog.findChildren(QPushButton):
            normalized = self._normalized_text(button.text())
            translated = self._TEXT_TRANSLATIONS.get(normalized)
            if translated is not None:
                button.setText(translated)

    def _install_spin_controls(self):
        for spin in self._color_dialog.findChildren(QSpinBox):
            spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
            spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
            spin.setFixedHeight(22)

            up_button = QPushButton("▴", spin)
            down_button = QPushButton("▾", spin)
            for button in (up_button, down_button):
                button.setCursor(Qt.CursorShape.PointingHandCursor)
                button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                button.setFixedSize(13, 11)
            up_button.clicked.connect(spin.stepUp)
            down_button.clicked.connect(spin.stepDown)
            up_button.move(max(spin.width() - 14, 0), 0)
            down_button.move(max(spin.width() - 14, 0), 11)
            up_button.raise_()
            down_button.raise_()
            self._spin_buttons.append((spin, up_button, down_button))

    def _apply_content_theme(self):
        dark = self._dark_content
        background = "#242424" if dark else "#ffffff"
        secondary = "#303030" if dark else "#f5f5f5"
        text = "#ffffff" if dark else "#333333"
        border = "#555555" if dark else "#cfcfcf"
        arrow = "#ffffff" if dark else self._accent.name()

        palette = self._color_dialog.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(background))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(text))
        palette.setColor(QPalette.ColorRole.Base, QColor(background))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(secondary))
        palette.setColor(QPalette.ColorRole.Text, QColor(text))
        palette.setColor(QPalette.ColorRole.Button, QColor(secondary))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(text))
        palette.setColor(QPalette.ColorRole.Highlight, self._accent)
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        self._color_dialog.setPalette(palette)
        self._color_dialog.setStyleSheet(
            "QColorDialog { "
            f"background-color: {background}; color: {text}; }}"
            "QColorDialog QLabel { "
            f"color: {text}; background: transparent; }}"
            "QColorDialog QLineEdit { "
            f"background-color: {background}; color: {text}; "
            f"border: 1px solid {border}; border-radius: 3px; "
            f"padding: 2px 4px; selection-background-color: {self._accent.name()}; }}"
            "QColorDialog QSpinBox { "
            f"background: transparent; color: {arrow}; border: none; padding-right: 14px; }}"
            "QColorDialog QSpinBox QLineEdit { "
            f"background: transparent; color: {arrow}; border: none; padding: 0px; }}"
            "QColorDialog QPushButton { "
            f"background-color: {secondary}; color: {text}; "
            f"border: 1px solid {border}; border-radius: 4px; padding: 3px 10px; }}"
            "QColorDialog QPushButton:hover { "
            f"background-color: {'#3a3a3a' if dark else '#e9e9e9'}; }}"
        )
        for _spin, up_button, down_button in self._spin_buttons:
            arrow_style = (
                "QPushButton { background: transparent; border: none; padding: 0px; "
                f"color: {arrow}; font-size: 8px; }}"
                "QPushButton:hover { background: transparent; }"
            )
            up_button.setStyleSheet(arrow_style)
            down_button.setStyleSheet(arrow_style)

    def toggle_content_theme(self):
        self._dark_content = not self._dark_content
        self._apply_content_theme()

    def _update_window_mask(self):
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self.CORNER_RADIUS, self.CORNER_RADIUS)
        polygon = path.toFillPolygon().toPolygon()
        self.setMask(QRegion(polygon))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_window_mask()

    def currentColor(self):
        return self._color_dialog.currentColor()

    @classmethod
    def get_color(cls, initial_color, title, accent, parent=None):
        dialog = cls(initial_color, title, accent, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.currentColor()
        return QColor()
