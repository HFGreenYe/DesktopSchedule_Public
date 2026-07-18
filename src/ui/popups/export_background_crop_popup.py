from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QEvent, QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QGuiApplication,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
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


class _BackgroundCropCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._image = QImage()
        self._crop_rect = QRectF()
        self._maximum_crop_size = (0.0, 0.0)
        self._target_ratio = 1.0
        self._drag_position = None
        self.setFixedSize(440, 330)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setMouseTracking(True)

    def set_source(self, image_path, target_ratio, normalized_crop=None):
        self._image = QImage(str(image_path))
        self._target_ratio = max(0.01, float(target_ratio))
        self._drag_position = None
        self._update_maximum_crop_size()
        if not self._apply_normalized_crop(normalized_crop):
            self.reset_crop()
        self.update()

    def has_valid_image(self):
        return not self._image.isNull()

    def normalized_crop(self):
        if self._image.isNull() or self._crop_rect.isEmpty():
            return None
        image_width = self._image.width()
        image_height = self._image.height()
        return tuple(
            round(value, 8)
            for value in (
                self._crop_rect.x() / image_width,
                self._crop_rect.y() / image_height,
                self._crop_rect.width() / image_width,
                self._crop_rect.height() / image_height,
            )
        )

    def reset_crop(self):
        if self._image.isNull():
            self._crop_rect = QRectF()
            self.update()
            return
        crop_width, crop_height = self._maximum_crop_size
        self._crop_rect = QRectF(
            (self._image.width() - crop_width) / 2,
            (self._image.height() - crop_height) / 2,
            crop_width,
            crop_height,
        )
        self.update()

    def _update_maximum_crop_size(self):
        if self._image.isNull():
            self._maximum_crop_size = (0.0, 0.0)
            return
        image_width = float(self._image.width())
        image_height = float(self._image.height())
        if image_width / image_height > self._target_ratio:
            crop_height = image_height
            crop_width = crop_height * self._target_ratio
        else:
            crop_width = image_width
            crop_height = crop_width / self._target_ratio
        self._maximum_crop_size = (crop_width, crop_height)

    def _apply_normalized_crop(self, normalized_crop):
        if self._image.isNull() or not normalized_crop or len(normalized_crop) != 4:
            return False
        try:
            x, y, width, height = (float(value) for value in normalized_crop)
        except (TypeError, ValueError):
            return False
        if width <= 0 or height <= 0:
            return False
        image_width = float(self._image.width())
        image_height = float(self._image.height())
        crop_rect = QRectF(
            x * image_width,
            y * image_height,
            width * image_width,
            height * image_height,
        )
        ratio_error = abs(crop_rect.width() / crop_rect.height() - self._target_ratio)
        if ratio_error > max(0.002, self._target_ratio * 0.002):
            return False
        if (
            crop_rect.left() < 0
            or crop_rect.top() < 0
            or crop_rect.right() > image_width + 0.5
            or crop_rect.bottom() > image_height + 0.5
        ):
            return False
        self._crop_rect = crop_rect
        self._clamp_crop_position()
        return True

    def _frame_rect(self):
        bounds = QRectF(self.rect()).adjusted(22, 18, -22, -18)
        if bounds.width() / bounds.height() > self._target_ratio:
            height = bounds.height()
            width = height * self._target_ratio
        else:
            width = bounds.width()
            height = width / self._target_ratio
        return QRectF(
            bounds.center().x() - width / 2,
            bounds.center().y() - height / 2,
            width,
            height,
        )

    def _clamp_crop_position(self):
        if self._image.isNull() or self._crop_rect.isEmpty():
            return
        maximum_x = max(0.0, self._image.width() - self._crop_rect.width())
        maximum_y = max(0.0, self._image.height() - self._crop_rect.height())
        self._crop_rect.moveLeft(max(0.0, min(self._crop_rect.x(), maximum_x)))
        self._crop_rect.moveTop(max(0.0, min(self._crop_rect.y(), maximum_y)))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.fillRect(self.rect(), QColor(24, 39, 46, 224))
        frame_rect = self._frame_rect()
        if self._image.isNull():
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(
                frame_rect,
                Qt.AlignmentFlag.AlignCenter,
                "背景图片读取失败",
            )
            return

        frame_path = QPainterPath()
        frame_path.addRoundedRect(frame_rect, 5, 5)
        painter.save()
        painter.setClipPath(frame_path)
        painter.drawImage(frame_rect, self._image, self._crop_rect)
        painter.restore()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255, 235), 2))
        painter.drawRoundedRect(frame_rect, 5, 5)
        grid_pen = QPen(QColor(255, 255, 255, 105), 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        for fraction in (1 / 3, 2 / 3):
            x = frame_rect.left() + frame_rect.width() * fraction
            y = frame_rect.top() + frame_rect.height() * fraction
            painter.drawLine(QPointF(x, frame_rect.top()), QPointF(x, frame_rect.bottom()))
            painter.drawLine(QPointF(frame_rect.left(), y), QPointF(frame_rect.right(), y))

    def mousePressEvent(self, event):
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self._frame_rect().contains(event.position())
            and not self._image.isNull()
        ):
            self._drag_position = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self._drag_position is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            frame_rect = self._frame_rect()
            delta = event.position() - self._drag_position
            self._drag_position = event.position()
            self._crop_rect.translate(
                -delta.x() * self._crop_rect.width() / frame_rect.width(),
                -delta.y() * self._crop_rect.height() / frame_rect.height(),
            )
            self._clamp_crop_position()
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._drag_position is not None:
            self._drag_position = None
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        if self._image.isNull() or not self._frame_rect().contains(event.position()):
            super().wheelEvent(event)
            return
        delta = event.angleDelta().y() or event.angleDelta().x()
        if not delta:
            return
        frame_rect = self._frame_rect()
        relative_x = (event.position().x() - frame_rect.left()) / frame_rect.width()
        relative_y = (event.position().y() - frame_rect.top()) / frame_rect.height()
        focus_x = self._crop_rect.x() + relative_x * self._crop_rect.width()
        focus_y = self._crop_rect.y() + relative_y * self._crop_rect.height()
        factor = 0.88 if delta > 0 else 1.14
        maximum_width, maximum_height = self._maximum_crop_size
        minimum_width = maximum_width * 0.10
        new_width = max(minimum_width, min(maximum_width, self._crop_rect.width() * factor))
        new_height = new_width / self._target_ratio
        if new_height > maximum_height:
            new_height = maximum_height
            new_width = new_height * self._target_ratio
        self._crop_rect = QRectF(
            focus_x - relative_x * new_width,
            focus_y - relative_y * new_height,
            new_width,
            new_height,
        )
        self._clamp_crop_position()
        self.update()
        event.accept()


class ExportBackgroundCropPopup(QWidget):
    crop_confirmed = pyqtSignal(object, object)

    def __init__(self, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._drag_offset = None
        self._source_id = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.header_holder = QWidget()
        self.header_holder.setFixedHeight(42)
        header = QHBoxLayout(self.header_holder)
        header.setContentsMargins(14, 0, 36, 0)
        self.title = QLabel("裁剪默认背景")
        self.title.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei UI'; font-size: 15px; "
            "font-weight: bold; background: transparent; border: none;"
        )
        header.addWidget(self.title)
        header.addStretch(1)
        root.addWidget(self.header_holder)

        body_frame = QFrame()
        body_frame.setObjectName("backgroundCropBody")
        body_frame.setStyleSheet(
            "QFrame#backgroundCropBody { background-color: rgba(255, 255, 255, 0.70); "
            "border: 2px solid rgba(255, 255, 255, 0.96); border-top: none; "
            "border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; }"
        )
        body = QVBoxLayout(body_frame)
        body.setContentsMargins(14, 10, 14, 12)
        body.setSpacing(7)

        self.canvas = _BackgroundCropCanvas(body_frame)
        body.addWidget(self.canvas, 0, Qt.AlignmentFlag.AlignCenter)

        self.hint_label = QLabel("拖动图片调整位置 · 滚轮缩放 · 白框为最终导出范围")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet(
            "color: #40566B; font-family: 'Microsoft YaHei UI'; font-size: 10px; "
            "background: transparent; border: none;"
        )
        body.addWidget(self.hint_label)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(8)
        self.target_label = QLabel()
        self.target_label.setStyleSheet(
            "color: #40566B; font-family: 'Microsoft YaHei UI'; font-size: 10px; "
            "background: transparent; border: none;"
        )
        action_row.addWidget(self.target_label)
        action_row.addStretch(1)
        self.reset_button = self._create_action_button("重置", primary=False)
        self.cancel_button = self._create_action_button("取消", primary=False)
        self.confirm_button = self._create_action_button("确认裁剪", primary=True)
        self.reset_button.clicked.connect(self.canvas.reset_crop)
        self.cancel_button.clicked.connect(self.close)
        self.confirm_button.clicked.connect(self._confirm_crop)
        action_row.addWidget(self.reset_button)
        action_row.addWidget(self.cancel_button)
        action_row.addWidget(self.confirm_button)
        body.addLayout(action_row)
        root.addWidget(body_frame)

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
        self.setFixedSize(472, 452)
        self._update_close_button_position()

    @staticmethod
    def _create_action_button(text, primary):
        button = QPushButton(text)
        button.setFixedSize(72 if primary else 54, 26)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        if primary:
            button.setStyleSheet(
                f"QPushButton {{ color: white; background: {AppConfig.COLOR_GRADIENT_START}; "
                "border: none; border-radius: 6px; font-family: 'Microsoft YaHei UI'; "
                "font-size: 11px; font-weight: bold; } QPushButton:hover { "
                "background: rgba(0, 0, 0, 0.18); }"
            )
        else:
            button.setStyleSheet(
                f"QPushButton {{ color: {AppConfig.COLOR_GRADIENT_START}; "
                "background: rgba(255,255,255,0.45); "
                "border: 1px solid rgba(90,110,120,0.45); border-radius: 6px; "
                "font-family: 'Microsoft YaHei UI'; font-size: 11px; } "
                "QPushButton:hover { background: rgba(255,255,255,0.72); }"
            )
        return button

    def configure(
        self,
        source_id,
        image_path,
        display_name,
        target_width,
        target_height,
        target_text,
        initial_crop=None,
    ):
        self._source_id = source_id
        self.title.setText(f"裁剪背景 · {display_name}")
        self.target_label.setText(target_text)
        self.canvas.set_source(
            Path(image_path),
            float(target_width) / float(target_height),
            initial_crop,
        )
        self.confirm_button.setEnabled(self.canvas.has_valid_image())

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

    def _confirm_crop(self):
        crop = self.canvas.normalized_crop()
        if crop is None:
            return
        self.crop_confirmed.emit(self._source_id, crop)
        self.close()

    def eventFilter(self, watched, event):
        if watched in (self.header_holder, self.title):
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
