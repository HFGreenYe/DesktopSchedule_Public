from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QCursor, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from src.config import AppConfig


class AllSchedulesPanel(QWidget):
    RESIZE_MARGIN = 8

    def __init__(self, parent_window=None):
        super().__init__(
            parent_window,
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint,
        )
        self.parent_window = parent_window
        self._drag_offset = None
        self._resize_edge = None
        self._resize_start_pos = None
        self._resize_start_geometry = None
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._setup_ui()
        self.reset_geometry_for_parent()

    def reset_geometry_for_parent(self):
        parent = self.parent_window
        if parent is None:
            self.setFixedWidth(260)
            self.setMinimumHeight(384)
            self.resize(260, 384)
            return

        parent_rect = parent.frameGeometry()
        width = max(220, int(parent_rect.width() * 0.75))
        height = max(260, int(parent_rect.height() * 2 / 3))
        self.setFixedWidth(width)
        self.setMinimumHeight(height)
        self.resize(width, height)
        self.move(
            parent_rect.left() + (parent_rect.width() - width) // 2,
            parent_rect.top() + (parent_rect.height() - height) // 2,
        )

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.title_label = QLabel("日程查看")
        self.title_label.setFixedHeight(26)
        self.title_label.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei'; "
            "font-size: 16px; font-weight: bold; background: transparent; border: none;"
        )
        layout.addWidget(self.title_label)

        self.display_frame = QFrame()
        self.display_frame.setObjectName("allSchedulesDisplayFrame")
        self.display_frame.setStyleSheet(
            """
            QFrame#allSchedulesDisplayFrame {
                background-color: rgba(255, 255, 255, 0.75);
                border: 2px solid white;
                border-radius: 8px;
            }
            """
        )
        layout.addWidget(self.display_frame, 1)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        painter.fillPath(path, QBrush(gradient))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(0, 0, 0, 28), 1))
        painter.drawPath(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._hit_resize_edge(event.position().y())
            if edge:
                self._resize_edge = edge
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_geometry = self.geometry()
                event.accept()
                return
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resize_edge and self._resize_start_pos and self._resize_start_geometry:
            delta_y = event.globalPosition().toPoint().y() - self._resize_start_pos.y()
            geometry = self._resize_start_geometry
            if self._resize_edge == "bottom":
                new_height = max(self.minimumHeight(), geometry.height() + delta_y)
                self.resize(self.width(), new_height)
            elif self._resize_edge == "top":
                new_height = max(self.minimumHeight(), geometry.height() - delta_y)
                consumed_delta = geometry.height() - new_height
                self.setGeometry(
                    geometry.x(),
                    geometry.y() + consumed_delta,
                    geometry.width(),
                    new_height,
                )
            event.accept()
            return

        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return

        edge = self._hit_resize_edge(event.position().y())
        self.setCursor(
            Qt.CursorShape.SizeVerCursor
            if edge
            else Qt.CursorShape.ArrowCursor
        )
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = None
            self._resize_edge = None
            self._resize_start_pos = None
            self._resize_start_geometry = None
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        if self._resize_edge is None:
            self.unsetCursor()
        super().leaveEvent(event)

    def _hit_resize_edge(self, y):
        if y <= self.RESIZE_MARGIN:
            return "top"
        if y >= self.height() - self.RESIZE_MARGIN:
            return "bottom"
        return None
