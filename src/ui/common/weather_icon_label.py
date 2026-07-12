import math

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtWidgets import QGridLayout, QLabel, QWidget

from src.ui.utils.icon_loader import load_colored_svg_pixmap


class WeatherIconLabel(QWidget):
    """Weather icon widget with an isolated loading layer."""

    double_clicked = pyqtSignal()

    def __init__(
        self,
        icon_size,
        parent=None,
        color="#FFFFFF",
        loading_timeout_ms=3000,
        frame_interval_ms=50,
        loading_icon_scale=0.78,
    ):
        super().__init__(parent)
        self.icon_size = icon_size
        self.icon_color = color
        self.loading_icon_scale = loading_icon_scale
        self._phase = 0
        self._loading_base = QPixmap()
        self._loading_icon_path = "assets/icons/hourglass.svg"
        self._current_icon_path = None
        self._alignment = Qt.AlignmentFlag.AlignCenter
        self._active_layer = "weather"
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._loading_label = QLabel(self)
        self._loading_label.setFixedSize(icon_size, icon_size)
        self._loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._loading_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

        self._weather_label = QLabel(self)
        self._weather_label.setFixedSize(icon_size, icon_size)
        self._weather_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._weather_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

        self._layout.addWidget(self._loading_label, 0, 0)
        self._layout.addWidget(self._weather_label, 0, 0)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._show_weather_layer()

        self._frame_timer = QTimer(self)
        self._frame_timer.timeout.connect(self._render_loading_frame)

        self._loading_timeout_timer = QTimer(self)
        self._loading_timeout_timer.setSingleShot(True)
        self._loading_timeout_timer.timeout.connect(self._finish_loading_timeout)

        self._loading_timeout_ms = loading_timeout_ms
        self._frame_interval_ms = frame_interval_ms

    def start_loading(self):
        self._loading_base = self._load_svg(self._loading_icon_path)
        if self._loading_base.isNull():
            self.set_unavailable_icon()
            return

        self._phase = 0
        self._show_loading_layer()
        self._render_loading_frame()
        self._frame_timer.start(self._frame_interval_ms)
        self._loading_timeout_timer.start(self._loading_timeout_ms)

    def set_weather_icon(self, icon_path):
        if icon_path == "assets/weather/999-fill.svg" and self._loading_timeout_timer.isActive():
            return True

        self._stop_loading()
        pixmap = self._load_svg(icon_path)
        if pixmap.isNull():
            self.set_unavailable_icon()
            return False

        self._current_icon_path = icon_path
        self._weather_label.setText("")
        self._weather_label.setPixmap(pixmap)
        self._show_weather_layer()
        return True

    def set_unavailable_icon(self):
        self._stop_loading()
        icon_path = "assets/weather/999-fill.svg"
        pixmap = self._load_svg(icon_path)
        if pixmap.isNull():
            self._current_icon_path = None
            self._weather_label.clear()
            self._show_weather_layer()
            return False

        self._current_icon_path = icon_path
        self._weather_label.setText("")
        self._weather_label.setPixmap(pixmap)
        self._show_weather_layer()
        return True

    def set_icon_color(self, color):
        if self.icon_color == color:
            return

        self.icon_color = color
        if self._active_layer == "loading":
            self._loading_base = self._load_svg(self._loading_icon_path)
            if not self._loading_base.isNull():
                self._render_loading_frame()
            return

        if not self._current_icon_path:
            return

        pixmap = self._load_svg(self._current_icon_path)
        if pixmap.isNull():
            return

        self._weather_label.setText("")
        self._weather_label.setPixmap(pixmap)

    def setAlignment(self, alignment):
        self._alignment = alignment
        self._layout.setAlignment(self._loading_label, alignment)
        self._layout.setAlignment(self._weather_label, alignment)

    def pixmap(self):
        active_label = self._loading_label if self._active_layer == "loading" else self._weather_label
        pixmap = active_label.pixmap()
        return pixmap if pixmap is not None else QPixmap()

    def text(self):
        active_label = self._loading_label if self._active_layer == "loading" else self._weather_label
        return active_label.text()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def _load_svg(self, icon_path):
        return load_colored_svg_pixmap(
            icon_path,
            self.icon_color,
            self.icon_size,
            self.icon_size,
            self.devicePixelRatio(),
        )

    def _stop_loading(self):
        self._frame_timer.stop()
        self._loading_timeout_timer.stop()

    def _finish_loading_timeout(self):
        self.set_unavailable_icon()

    def _show_loading_layer(self):
        self._active_layer = "loading"
        self._weather_label.hide()
        self._loading_label.show()

    def _show_weather_layer(self):
        self._active_layer = "weather"
        self._loading_label.hide()
        self._weather_label.show()

    def _render_loading_frame(self):
        if self._loading_base.isNull():
            self.set_unavailable_icon()
            return

        ratio = self.devicePixelRatio()
        pixel_size = max(1, int(self.icon_size * ratio))
        canvas = QPixmap(pixel_size, pixel_size)
        canvas.setDevicePixelRatio(ratio)
        canvas.fill(Qt.GlobalColor.transparent)

        raw_scale_y = math.cos(math.radians(self._phase))
        if abs(raw_scale_y) < 0.12:
            scale_y = 0.12 if raw_scale_y >= 0 else -0.12
        else:
            scale_y = raw_scale_y

        draw_size = self.icon_size * self.loading_icon_scale
        draw_offset = -draw_size / 2

        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        center = QPointF(self.icon_size / 2, self.icon_size / 2)
        painter.translate(center)
        painter.scale(1.0, scale_y)
        painter.drawPixmap(
            QRectF(draw_offset, draw_offset, draw_size, draw_size),
            self._loading_base,
            QRectF(self._loading_base.rect()),
        )
        painter.end()

        self._loading_label.setText("")
        self._loading_label.setPixmap(canvas)
        self._phase = (self._phase + 18) % 360
