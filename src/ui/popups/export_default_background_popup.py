from __future__ import annotations

from functools import lru_cache

from PyQt6.QtCore import QEvent, QPoint, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QGuiApplication,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
)
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.config import AppConfig
from src.services.export_background_presets import (
    DEFAULT_EXPORT_BACKGROUND_PRESETS,
    get_export_background_image_path,
    get_export_background_preset,
)


@lru_cache(maxsize=None)
def _load_background_image(path):
    return QImage(path)


def _cover_source_rect(image, target_rect):
    image_width = image.width()
    image_height = image.height()
    if (
        image_width <= 0
        or image_height <= 0
        or target_rect.width() <= 0
        or target_rect.height() <= 0
    ):
        return QRectF()
    target_ratio = target_rect.width() / target_rect.height()
    image_ratio = image_width / image_height
    if image_ratio > target_ratio:
        source_width = image_height * target_ratio
        return QRectF(
            (image_width - source_width) / 2,
            0,
            source_width,
            image_height,
        )
    source_height = image_width / target_ratio
    return QRectF(
        0,
        (image_height - source_height) / 2,
        image_width,
        source_height,
    )


def paint_default_background_pattern(painter, rect, index):
    preset = get_export_background_preset(index)
    image_path = get_export_background_image_path(preset)
    if image_path is not None:
        image = _load_background_image(str(image_path))
        if not image.isNull():
            painter.drawImage(rect, image, _cover_source_rect(image, rect))
            return

    gradient = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())
    gradient.setColorAt(0.0, QColor(preset.top_color))
    gradient.setColorAt(1.0, QColor(preset.bottom_color))
    painter.fillRect(rect, gradient)

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(255, 255, 255, 68))
    painter.drawEllipse(
        QRectF(
            rect.left() - rect.width() * 0.28,
            rect.top() + rect.height() * 0.09,
            rect.width() * 0.82,
            rect.width() * 0.82,
        )
    )
    painter.setBrush(QColor(255, 255, 255, 92))
    painter.drawEllipse(
        QRectF(
            rect.right() - rect.width() * 0.52,
            rect.top() + rect.height() * 0.39,
            rect.width() * 0.73,
            rect.width() * 0.73,
        )
    )


class _CircularBackgroundCarousel(QWidget):
    selection_changed = pyqtSignal(int)

    visible_count = 5
    card_width = 66
    card_height = 112
    card_spacing = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self._first_index = 0
        self._selected_index = 0
        width = (
            self.visible_count * self.card_width
            + (self.visible_count - 1) * self.card_spacing
        )
        self.setFixedSize(width, self.card_height + 8)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    @property
    def visible_indices(self):
        count = len(DEFAULT_EXPORT_BACKGROUND_PRESETS)
        return tuple(
            (self._first_index + offset) % count
            for offset in range(self.visible_count)
        )

    @property
    def selected_index(self):
        return self._selected_index

    def rotate(self, steps):
        if not steps:
            return
        self._first_index = (
            self._first_index + int(steps)
        ) % len(DEFAULT_EXPORT_BACKGROUND_PRESETS)
        self.update()

    def set_selected_index(self, index):
        self._selected_index = int(index) % len(DEFAULT_EXPORT_BACKGROUND_PRESETS)
        if self._selected_index not in self.visible_indices:
            self._first_index = self._selected_index
        self.update()

    def card_rects(self):
        return tuple(
            (
                background_index,
                QRectF(
                    offset * (self.card_width + self.card_spacing),
                    4,
                    self.card_width,
                    self.card_height,
                ),
            )
            for offset, background_index in enumerate(self.visible_indices)
        )

    def wheelEvent(self, event):
        delta = event.angleDelta().y() or event.angleDelta().x()
        if delta:
            self.rotate(1 if delta < 0 else -1)
            event.accept()
            return
        super().wheelEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            for background_index, rect in self.card_rects():
                if rect.contains(event.position()):
                    self._selected_index = background_index
                    self.selection_changed.emit(background_index)
                    self.update()
                    event.accept()
                    return
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        for background_index, rect in self.card_rects():
            path = QPainterPath()
            path.addRoundedRect(rect, 6, 6)
            painter.save()
            painter.setClipPath(path)
            paint_default_background_pattern(painter, rect, background_index)
            label_rect = QRectF(
                rect.left(),
                rect.bottom() - 27,
                rect.width(),
                27,
            )
            painter.fillRect(label_rect, QColor(255, 255, 255, 190))
            painter.restore()

            selected = background_index == self._selected_index
            painter.setPen(
                QColor(AppConfig.COLOR_GRADIENT_START)
                if selected
                else QColor(255, 255, 255, 224)
            )
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(
                rect.adjusted(1, 1, -1, -1),
                5,
                5,
            )
            if selected:
                painter.drawRoundedRect(
                    rect.adjusted(2, 2, -2, -2),
                    4,
                    4,
                )

            painter.setPen(QColor("#30445A"))
            painter.drawText(
                QRectF(rect.left(), rect.top() + 22, rect.width(), 28),
                Qt.AlignmentFlag.AlignCenter,
                f"{background_index + 1:02d}",
            )
            painter.drawText(
                QRectF(rect.left(), rect.bottom() - 27, rect.width(), 27),
                Qt.AlignmentFlag.AlignCenter,
                get_export_background_preset(background_index).name,
            )


class ExportDefaultBackgroundPopup(QWidget):
    background_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._drag_offset = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.header_holder = QWidget()
        self.header_holder.setFixedHeight(42)
        header = QHBoxLayout(self.header_holder)
        header.setContentsMargins(14, 8, 38, 2)
        self.title = QLabel("默认背景 · 01")
        self.title.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei UI'; "
            "font-size: 16px; font-weight: bold; background: transparent; border: none;"
        )
        header.addWidget(self.title)
        header.addStretch(1)
        root.addWidget(self.header_holder)

        self.body_frame = QFrame()
        self.body_frame.setObjectName("defaultBackgroundBody")
        self.body_frame.setStyleSheet(
            "QFrame#defaultBackgroundBody { "
            "background-color: rgba(255, 255, 255, 0.70); "
            "border: 2px solid rgba(255, 255, 255, 0.96); "
            "border-top: none; border-bottom-left-radius: 10px; "
            "border-bottom-right-radius: 10px; }"
        )
        body = QVBoxLayout(self.body_frame)
        body.setContentsMargins(16, 12, 16, 12)
        body.setSpacing(6)

        self.carousel = _CircularBackgroundCarousel(self.body_frame)
        self.carousel.selection_changed.connect(self._handle_selection_changed)
        body.addWidget(self.carousel, 0, Qt.AlignmentFlag.AlignCenter)

        self.hint_label = QLabel("滚动鼠标滚轮横向浏览 · 点击方框选择")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet(
            "color: #40566B; font-family: 'Microsoft YaHei UI'; "
            "font-size: 10px; background: transparent; border: none;"
        )
        body.addWidget(self.hint_label)
        root.addWidget(self.body_frame)

        self.close_button = QPushButton("×", self)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setStyleSheet(
            "QPushButton { color: white; background: transparent; border: none; "
            "font-size: 20px; } QPushButton:hover { background: #ff4d4f; "
            "border-top-right-radius: 9px; border-bottom-left-radius: 4px; }"
        )
        self.close_button.clicked.connect(self.close)

        self.header_holder.installEventFilter(self)
        self.title.installEventFilter(self)
        self.body_frame.installEventFilter(self)
        self.hint_label.installEventFilter(self)
        self.setFixedSize(self.carousel.width() + 32, 202)
        self._update_close_button_position()

    def _handle_selection_changed(self, index):
        self.title.setText(
            f"默认背景 · {get_export_background_preset(index).name}"
        )
        self.background_selected.emit(index)

    def set_selected_index(self, index):
        self.carousel.set_selected_index(index)
        self.title.setText(
            "默认背景 · "
            f"{get_export_background_preset(self.carousel.selected_index).name}"
        )

    def show_near(self, anchor):
        if anchor is not None:
            anchor_rect = anchor.frameGeometry()
            x = anchor_rect.x() + anchor_rect.width() + 8
            y = anchor_rect.y()
            screen = (
                QGuiApplication.screenAt(anchor_rect.center())
                or QGuiApplication.primaryScreen()
            )
            if screen is not None:
                available = screen.availableGeometry()
                if x + self.width() > available.right() + 1:
                    x = anchor_rect.x() - self.width() - 8
                x = max(available.left(), min(x, available.right() - self.width() + 1))
                y = max(available.top(), min(y, available.bottom() - self.height() + 1))
            self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()

    def eventFilter(self, watched, event):
        draggable = watched in (
            self.header_holder,
            self.title,
            self.body_frame,
            self.hint_label,
        )
        if draggable:
            if (
                event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
            ):
                self._drag_offset = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
                event.accept()
                return True
            if (
                event.type() == QEvent.Type.MouseMove
                and self._drag_offset is not None
                and event.buttons() & Qt.MouseButton.LeftButton
            ):
                self.move(event.globalPosition().toPoint() - self._drag_offset)
                event.accept()
                return True
            if (
                event.type() == QEvent.Type.MouseButtonRelease
                and self._drag_offset is not None
            ):
                self._drag_offset = None
                event.accept()
                return True
        return super().eventFilter(watched, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_close_button_position()

    def _update_close_button_position(self):
        self.close_button.move(self.width() - self.close_button.width(), 0)
        self.close_button.raise_()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 10, 10)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        painter.fillPath(path, gradient)
