import datetime

from PyQt6.QtCore import QPoint, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QCursor,
    QGuiApplication,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
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
from src.services.schedule_axis_service import ScheduleAxisService


class _AxisSchedulePreview(QFrame):
    def __init__(self, persistent=False, parent=None):
        flags = Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
        if not persistent:
            flags = Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint
        super().__init__(parent, flags)
        self.persistent = persistent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, not persistent)
        if not persistent:
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setMinimumWidth(190)
        self.setMaximumWidth(280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(5)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        self.title_label = QLabel()
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet(
            "color: #222222; font-size: 12px; font-weight: bold; "
            "font-family: 'Microsoft YaHei'; background: transparent;"
        )
        header.addWidget(self.title_label, 1)
        if persistent:
            close_button = QPushButton("×")
            close_button.setFixedSize(20, 20)
            close_button.setCursor(Qt.CursorShape.PointingHandCursor)
            close_button.setStyleSheet(
                "QPushButton { color: #555555; background: transparent; border: none; "
                "font-size: 14px; font-weight: bold; } "
                "QPushButton:hover { background: rgba(12,192,223,0.12); border-radius: 10px; }"
            )
            close_button.clicked.connect(self.hide)
            header.addWidget(close_button)
        layout.addLayout(header)

        self.time_label = QLabel()
        self.meta_label = QLabel()
        for label in (self.time_label, self.meta_label):
            label.setWordWrap(True)
            label.setStyleSheet(
                "color: #555555; font-size: 10px; "
                "font-family: 'Microsoft YaHei'; background: transparent;"
            )
            layout.addWidget(label)

        if persistent:
            note = QLabel("单击详情样本：当前只读")
            note.setStyleSheet(
                "color: #0aa9c5; font-size: 9px; "
                "font-family: 'Microsoft YaHei'; background: transparent;"
            )
            layout.addWidget(note)

    def set_projection(self, projection):
        schedule = projection.schedule
        self.title_label.setText(getattr(schedule, "title", "") or "未命名日程")
        self.time_label.setText(self._format_time_text(schedule))
        importance = {0: "低", 1: "中", 2: "高"}.get(projection.importance, "低")
        status = "已完成" if int(getattr(schedule, "status", 0)) == 1 else "未完成"
        self.meta_label.setText(
            f"{projection.category_name} · {importance}重要性 · {status}"
        )
        self.adjustSize()

    def show_near(self, global_pos):
        x = global_pos.x() + 12
        y = global_pos.y() + 12
        screen = QGuiApplication.screenAt(global_pos) or QGuiApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            x = max(available.left(), min(x, available.right() - self.width() + 1))
            y = max(available.top(), min(y, available.bottom() - self.height() + 1))
        self.move(x, y)
        self.show()
        self.raise_()

    @staticmethod
    def _format_time_text(schedule):
        start = getattr(schedule, "start_time", None)
        end = getattr(schedule, "end_time", None)
        if start and end and start != end:
            return f"{start:%Y-%m-%d %H:%M}  →  {end:%Y-%m-%d %H:%M}"
        target = start or end
        if target:
            return f"时间：{target:%Y-%m-%d %H:%M}"
        return "时间未设置"

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        painter.setPen(QPen(QColor(0, 0, 0, 28), 1))
        painter.setBrush(QColor(255, 255, 255, 246))
        painter.drawRoundedRect(rect, 8, 8)
        super().paintEvent(event)


class _ScheduleAxisCanvas(QWidget):
    hover_requested = pyqtSignal(object, object)
    item_clicked = pyqtSignal(object, object)

    POINT_DIAMETERS = {0: 8.0, 1: 12.0, 2: 16.0}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.projections = []
        self.range_hours = ScheduleAxisService.MIN_RANGE_HOURS
        self.hit_regions = []
        self._hovered_projection = None

    def set_data(self, projections, range_hours):
        self.projections = list(projections)
        self.range_hours = range_hours
        self._hovered_projection = None
        self.hit_regions.clear()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.hit_regions.clear()

        left = 20.0
        right = max(float(self.width() - 20), left + 1)
        axis_y = float(self.height()) / 2.0
        center_x = (left + right) / 2.0

        painter.setPen(QPen(QColor(255, 255, 255, 205), 1.5))
        painter.drawLine(QPoint(round(left), round(axis_y)), QPoint(round(right), round(axis_y)))
        painter.drawLine(QPoint(round(left), round(axis_y)), QPoint(round(left + 6), round(axis_y - 4)))
        painter.drawLine(QPoint(round(left), round(axis_y)), QPoint(round(left + 6), round(axis_y + 4)))
        painter.drawLine(QPoint(round(right), round(axis_y)), QPoint(round(right - 6), round(axis_y - 4)))
        painter.drawLine(QPoint(round(right), round(axis_y)), QPoint(round(right - 6), round(axis_y + 4)))

        painter.setPen(QPen(QColor(255, 255, 255, 125), 1))
        painter.drawLine(QPoint(round(center_x), round(axis_y - 10)), QPoint(round(center_x), round(axis_y + 10)))

        range_text = ScheduleAxisService.format_range(self.range_hours)
        painter.setPen(QColor(255, 255, 255, 220))
        painter.drawText(QRectF(left, axis_y + 8, 70, 18), Qt.AlignmentFlag.AlignLeft, f"过去 {range_text}")
        painter.drawText(QRectF(center_x - 25, axis_y + 8, 50, 18), Qt.AlignmentFlag.AlignCenter, "现在")
        painter.drawText(QRectF(right - 70, axis_y + 8, 70, 18), Qt.AlignmentFlag.AlignRight, f"未来 {range_text}")

        if not self.projections:
            painter.setPen(QColor(255, 255, 255, 190))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "暂无带时间的日程")
            return

        markers = self._layout_markers(left, right, axis_y)
        for marker in markers:
            self._draw_marker(painter, marker, axis_y)

    def _layout_markers(self, left, right, axis_y):
        lane_offsets = (-30, 30, -58, 58, -82, 82)
        lanes = [axis_y + offset for offset in lane_offsets]
        lanes = [y for y in lanes if 18 <= y <= self.height() - 22]
        if not lanes:
            lanes = [axis_y - 24]
        occupied = [[] for _ in lanes]

        raw_markers = []
        for projection in self.projections:
            x1 = ScheduleAxisService.map_delta_to_x(
                projection.start_delta_hours, self.range_hours, left, right
            )
            x2 = ScheduleAxisService.map_delta_to_x(
                projection.end_delta_hours, self.range_hours, left, right
            )
            diameter = self.POINT_DIAMETERS[projection.importance]
            raw_markers.append((min(x1, x2), max(x1, x2), diameter, projection))
        raw_markers.sort(key=lambda item: (item[0], item[1]))

        markers = []
        for index, (x1, x2, diameter, projection) in enumerate(raw_markers):
            interval_left = x1 - diameter / 2.0 - 5
            interval_right = x2 + diameter / 2.0 + 5
            lane_index = None
            for candidate, intervals in enumerate(occupied):
                if all(
                    interval_right < used_left or interval_left > used_right
                    for used_left, used_right in intervals
                ):
                    lane_index = candidate
                    break
            if lane_index is None:
                lane_index = index % len(lanes)
            occupied[lane_index].append((interval_left, interval_right))
            markers.append(
                {
                    "x1": x1,
                    "x2": x2,
                    "y": lanes[lane_index],
                    "diameter": diameter,
                    "projection": projection,
                }
            )
        return markers

    def _draw_marker(self, painter, marker, axis_y):
        x1 = marker["x1"]
        x2 = marker["x2"]
        y = marker["y"]
        diameter = marker["diameter"]
        radius = diameter / 2.0
        projection = marker["projection"]
        color = QColor(projection.category_color)
        if not color.isValid():
            color = QColor(ScheduleAxisService.FALLBACK_COLOR)

        anchor_x = (x1 + x2) / 2.0
        painter.setPen(QPen(QColor(255, 255, 255, 90), 1, Qt.PenStyle.DotLine))
        painter.drawLine(QPoint(round(anchor_x), round(axis_y)), QPoint(round(anchor_x), round(y)))

        painter.setPen(QPen(QColor(255, 255, 255, 225), 1))
        painter.setBrush(QBrush(color))
        path = QPainterPath()
        if projection.is_interval and abs(x2 - x1) >= 3:
            painter.setPen(QPen(color, max(3.0, diameter / 3.0), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(QPoint(round(x1), round(y)), QPoint(round(x2), round(y)))
            painter.setPen(QPen(QColor(255, 255, 255, 225), 1))
            painter.drawEllipse(QRectF(x1 - radius / 2, y - radius / 2, radius, radius))
            painter.drawEllipse(QRectF(x2 - radius / 2, y - radius / 2, radius, radius))
            path.moveTo(x1, y)
            path.lineTo(x2, y)
            stroker = QPainterPathStroker()
            stroker.setWidth(max(12.0, diameter))
            hit_path = stroker.createStroke(path)
        else:
            point_rect = QRectF(x1 - radius, y - radius, diameter, diameter)
            painter.drawEllipse(point_rect)
            hit_path = QPainterPath()
            hit_path.addEllipse(point_rect.adjusted(-3, -3, 3, 3))

        self.hit_regions.append((hit_path, projection))

    def _projection_at(self, pos):
        for path, projection in reversed(self.hit_regions):
            if path.contains(pos):
                return projection
        return None

    def mouseMoveEvent(self, event):
        projection = self._projection_at(event.position())
        if projection is not self._hovered_projection:
            self._hovered_projection = projection
            self.hover_requested.emit(projection, event.globalPosition().toPoint())
        elif projection is not None:
            self.hover_requested.emit(projection, event.globalPosition().toPoint())
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if projection is not None else Qt.CursorShape.ArrowCursor
        )
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self._hovered_projection = None
        self.hover_requested.emit(None, QCursor.pos())
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            projection = self._projection_at(event.position())
            if projection is not None:
                self.item_clicked.emit(projection, event.globalPosition().toPoint())
                event.accept()
                return
        super().mousePressEvent(event)


class ScheduleAxisBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(380, 300)
        self._drag_offset = None
        self._detail_opener = None
        self._detail_popups = {}
        self.hover_preview = _AxisSchedulePreview(False)
        self.persistent_preview = _AxisSchedulePreview(True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(0)

        panel = QFrame()
        panel.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        title = QLabel("坐标显示")
        title.setStyleSheet(
            "color: white; font-size: 17px; font-weight: bold; "
            "font-family: 'Microsoft YaHei'; background: transparent;"
        )
        header.addWidget(title)
        header.addStretch()
        self.range_label = QLabel()
        self.range_label.setStyleSheet(
            "color: rgba(255,255,255,0.78); font-size: 9px; background: transparent;"
        )
        header.addWidget(self.range_label)
        close_button = QPushButton("×")
        close_button.setFixedSize(24, 24)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setStyleSheet(
            "QPushButton { color: white; background: transparent; border: none; "
            "font-size: 17px; font-weight: bold; } "
            "QPushButton:hover { background: rgba(255,255,255,0.18); border-radius: 12px; }"
        )
        close_button.clicked.connect(self.close)
        header.addWidget(close_button)
        layout.addLayout(header)

        self.canvas = _ScheduleAxisCanvas()
        self.canvas.hover_requested.connect(self._show_hover_preview)
        self.canvas.item_clicked.connect(self._show_persistent_preview)
        layout.addWidget(self.canvas, 1)

        legend = QLabel("圆点：单时间  ·  线段：起止时间  ·  大小：重要性  ·  颜色：清单")
        legend.setAlignment(Qt.AlignmentFlag.AlignCenter)
        legend.setStyleSheet(
            "color: rgba(255,255,255,0.78); font-size: 9px; "
            "font-family: 'Microsoft YaHei'; background: transparent;"
        )
        layout.addWidget(legend)
        outer.addWidget(panel)

        self.refresh_data()

    def refresh_data(self):
        projections, range_hours = ScheduleAxisService.load_current_projection(
            datetime.datetime.now()
        )
        self.canvas.set_data(projections, range_hours)
        self.range_label.setText(f"范围 ±{ScheduleAxisService.format_range(range_hours)}")

    def set_detail_opener(self, opener):
        self._detail_opener = opener

    def _show_hover_preview(self, projection, global_pos):
        if projection is None:
            self.hover_preview.hide()
            return
        self.hover_preview.set_projection(projection)
        self.hover_preview.show_near(global_pos)

    def _show_persistent_preview(self, projection, global_pos):
        self.hover_preview.hide()
        if self._detail_opener is not None:
            schedule_id = getattr(projection.schedule, "id", id(projection.schedule))
            popup = self._detail_popups.get(schedule_id)
            try:
                if popup is not None:
                    popup.show()
                    popup.raise_()
                    popup.activateWindow()
                    self._position_detail_popup(popup, global_pos)
                    return
            except RuntimeError:
                self._detail_popups.pop(schedule_id, None)

            popup = self._detail_opener(projection.schedule)
            if popup is not None:
                self._detail_popups[schedule_id] = popup
                if hasattr(popup, "popup_closed"):
                    popup.popup_closed.connect(
                        lambda _popup=None, sid=schedule_id: self._detail_popups.pop(sid, None)
                    )
                self._position_detail_popup(popup, global_pos)
                return

        self.persistent_preview.set_projection(projection)
        self.persistent_preview.show_near(global_pos)

    @staticmethod
    def _position_detail_popup(popup, global_pos):
        popup.adjustSize()
        x = global_pos.x() + 12
        y = global_pos.y() + 12
        screen = QGuiApplication.screenAt(global_pos) or QGuiApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            x = max(available.left(), min(x, available.right() - popup.width() + 1))
            y = max(available.top(), min(y, available.bottom() - popup.height() + 1))
        popup.move(x, y)
        popup.show()
        popup.raise_()

    def showEvent(self, event):
        self.refresh_data()
        super().showEvent(event)

    def closeEvent(self, event):
        self.hover_preview.hide()
        self.persistent_preview.hide()
        super().closeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(10, 10, self.width() - 20, self.height() - 20)
        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        painter.fillPath(path, QBrush(gradient))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(0, 0, 0, 26), 1))
        painter.drawPath(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() <= 52:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_offset = None
        super().mouseReleaseEvent(event)
