import datetime

from PyQt6.QtCore import (
    QEasingCurve,
    QEvent,
    QPoint,
    QPointF,
    QPropertyAnimation,
    QRect,
    QRectF,
    QSize,
    Qt,
    QVariantAnimation,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QCursor,
    QGuiApplication,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.config import AppConfig
from src.services.schedule_axis_service import ScheduleAxisService
from src.ui.utils.icon_loader import load_colored_svg_pixmap
from src.utils.window_preferences import set_window_pin_state


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
        header.setSpacing(0)
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
    AXIS_COLOR = "#333333"
    hover_requested = pyqtSignal(object, object)
    item_clicked = pyqtSignal(object, object)

    MARKER_HEIGHTS = {0: 9.0, 1: 12.0, 2: 15.0}
    DEADLINE_WIDTH = 2.0
    LANE_GAP = 1.0
    AXIS_MARKER_GAP = 6.0
    MONTH_RANGE_HOURS = 30.0 * 24.0
    FOCUS_HOURS = 7.0 * 24.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.projections = []
        self.range_hours = self.MONTH_RANGE_HOURS
        self.hit_regions = []
        self._hovered_projection = None
        self.virtual_axis_width = 960.0
        self.log_scale = 1.0
        self.zoom = 1.0
        self.view_center_x = self.virtual_axis_width / 2.0
        self.vertical_offset = 0.0
        self._pan_start = None
        self._pan_center_start = 0.0
        self._pan_vertical_start = 0.0

    def configure_month_demo(self, virtual_axis_width, default_viewport_width):
        self.virtual_axis_width = max(float(virtual_axis_width), 1.0)
        visible_fraction = max(
            0.05,
            min(float(default_viewport_width) / self.virtual_axis_width, 1.0),
        )
        self.log_scale = ScheduleAxisService.solve_log_scale(
            self.MONTH_RANGE_HOURS,
            self.FOCUS_HOURS,
            visible_fraction,
        )
        self.range_hours = self.MONTH_RANGE_HOURS
        self.zoom = 1.0
        self.view_center_x = self.virtual_axis_width / 2.0
        self.vertical_offset = 0.0
        self.update()

    def set_data(self, projections, range_hours):
        del range_hours
        self.projections = [
            projection
            for projection in projections
            if projection.end_delta_hours >= -self.MONTH_RANGE_HOURS
            and projection.start_delta_hours <= self.MONTH_RANGE_HOURS
        ]
        self.range_hours = self.MONTH_RANGE_HOURS
        self._hovered_projection = None
        self.hit_regions.clear()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.hit_regions.clear()

        canvas_rect = QRectF(self.rect()).adjusted(1.0, 1.0, -1.0, -1.0)
        painter.setPen(QPen(QColor("#ffffff"), 2.0))
        painter.setBrush(QColor(255, 255, 255, 190))
        painter.drawRoundedRect(canvas_rect, 6, 6)

        left = 20.0
        right = max(float(self.width() - 20), left + 1)
        axis_y = float(self.height()) * 0.7 + self.vertical_offset
        origin_x = self._virtual_to_screen(self.virtual_axis_width / 2.0, left, right)

        axis_color = QColor(self.AXIS_COLOR)
        painter.setPen(QPen(axis_color, 1.5))
        painter.drawLine(QPoint(round(left), round(axis_y)), QPoint(round(right), round(axis_y)))
        painter.drawLine(QPoint(round(left), round(axis_y)), QPoint(round(left + 6), round(axis_y - 4)))
        painter.drawLine(QPoint(round(left), round(axis_y)), QPoint(round(left + 6), round(axis_y + 4)))
        painter.drawLine(QPoint(round(right), round(axis_y)), QPoint(round(right - 6), round(axis_y - 4)))
        painter.drawLine(QPoint(round(right), round(axis_y)), QPoint(round(right - 6), round(axis_y + 4)))

        if left <= origin_x <= right:
            center_tick_color = QColor(axis_color)
            center_tick_color.setAlpha(150)
            painter.setPen(QPen(center_tick_color, 1))
            painter.drawLine(
                QPoint(round(origin_x), round(axis_y - 10)),
                QPoint(round(origin_x), round(axis_y + 10)),
            )
            painter.setPen(axis_color)
            painter.drawText(
                QRectF(origin_x - 25, axis_y + 8, 50, 18),
                Qt.AlignmentFlag.AlignCenter,
                "现在",
            )

        left_delta = self._screen_to_delta(left, left, right)
        right_delta = self._screen_to_delta(right, left, right)
        painter.setPen(axis_color)
        painter.drawText(
            QRectF(left, axis_y + 8, 92, 18),
            Qt.AlignmentFlag.AlignLeft,
            self._format_edge_delta(left_delta),
        )
        painter.drawText(
            QRectF(right - 92, axis_y + 8, 92, 18),
            Qt.AlignmentFlag.AlignRight,
            self._format_edge_delta(right_delta),
        )

        if not self.projections:
            empty_color = QColor(axis_color)
            empty_color.setAlpha(170)
            painter.setPen(empty_color)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "暂无带时间的日程")
            return

        markers = self._layout_markers(left, right, axis_y)
        hovered_marker = None
        for marker in markers:
            self._draw_marker(painter, marker)
            if marker["projection"] is self._hovered_projection:
                hovered_marker = marker
        if hovered_marker is not None:
            self._draw_hover_time_guides(
                painter,
                hovered_marker,
                axis_y,
                left,
                right,
            )

    def _layout_markers(self, left, right, axis_y):
        occupied_by_status = {False: [], True: []}
        lane_heights_by_status = {False: [], True: []}

        raw_markers = []
        for projection in self.projections:
            virtual_x1 = ScheduleAxisService.map_delta_to_x(
                projection.start_delta_hours,
                self.range_hours,
                0.0,
                self.virtual_axis_width,
                self.log_scale,
            )
            virtual_x2 = ScheduleAxisService.map_delta_to_x(
                projection.end_delta_hours,
                self.range_hours,
                0.0,
                self.virtual_axis_width,
                self.log_scale,
            )
            x1 = self._virtual_to_screen(virtual_x1, left, right)
            x2 = self._virtual_to_screen(virtual_x2, left, right)
            height = self.MARKER_HEIGHTS[projection.importance]
            raw_markers.append((min(x1, x2), max(x1, x2), height, projection))
        raw_markers.sort(key=lambda item: (item[0], item[1]))

        markers = []
        for x1, x2, height, projection in raw_markers:
            completed = projection.is_completed
            occupied = occupied_by_status[completed]
            interval_left = x1 - 7.0
            interval_right = x2 + 7.0
            lane_index = None
            for candidate, intervals in enumerate(occupied):
                if all(
                    interval_right < used_left or interval_left > used_right
                    for used_left, used_right in intervals
                ):
                    lane_index = candidate
                    break
            if lane_index is None:
                lane_index = len(occupied)
                occupied.append([])
                lane_heights_by_status[completed].append(0.0)
            occupied[lane_index].append((interval_left, interval_right))
            lane_heights_by_status[completed][lane_index] = max(
                lane_heights_by_status[completed][lane_index],
                height,
            )
            markers.append(
                {
                    "x1": x1,
                    "x2": x2,
                    "lane_index": lane_index,
                    "height": height,
                    "projection": projection,
                }
            )

        lane_centers_by_status = {}
        for completed, lane_heights in lane_heights_by_status.items():
            cursor = axis_y + self.AXIS_MARKER_GAP if completed else axis_y - self.AXIS_MARKER_GAP
            centers = []
            for lane_height in lane_heights:
                if completed:
                    center = cursor + lane_height / 2.0
                    cursor += lane_height + self.LANE_GAP
                else:
                    center = cursor - lane_height / 2.0
                    cursor -= lane_height + self.LANE_GAP
                centers.append(center)
            lane_centers_by_status[completed] = centers

        for marker in markers:
            completed = marker["projection"].is_completed
            marker["y"] = lane_centers_by_status[completed][marker["lane_index"]]
        return markers

    def _draw_marker(self, painter, marker):
        x1 = marker["x1"]
        x2 = marker["x2"]
        y = marker["y"]
        marker_height = marker["height"]
        projection = marker["projection"]
        color = QColor(projection.category_color)
        if not color.isValid():
            color = QColor(ScheduleAxisService.FALLBACK_COLOR)

        if projection.is_interval:
            marker_rect = QRectF(
                x1,
                y - marker_height / 2.0,
                max(self.DEADLINE_WIDTH, x2 - x1),
                marker_height,
            )
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawRect(marker_rect)
        else:
            marker_rect = QRectF(
                x1 - self.DEADLINE_WIDTH / 2.0,
                y - marker_height / 2.0,
                self.DEADLINE_WIDTH,
                marker_height,
            )
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(
                QPen(
                    color,
                    self.DEADLINE_WIDTH,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.FlatCap,
                )
            )
            painter.drawLine(
                QPoint(round(x1), round(marker_rect.top())),
                QPoint(round(x1), round(marker_rect.bottom())),
            )

        hit_path = QPainterPath()
        hit_path.addRect(marker_rect.adjusted(-4, -4, 4, 4))

        self.hit_regions.append((hit_path, projection))

    def _draw_hover_time_guides(self, painter, marker, axis_y, left, right):
        projection = marker["projection"]
        marker_height = marker["height"]
        marker_y = marker["y"]
        marker_edge_y = (
            marker_y - marker_height / 2.0
            if projection.is_completed
            else marker_y + marker_height / 2.0
        )
        guide_xs = [marker["x1"]]
        if projection.is_interval:
            guide_xs.append(marker["x2"])

        guide_color = QColor(self.AXIS_COLOR)
        guide_color.setAlpha(150)
        painter.save()
        painter.setPen(QPen(guide_color, 1.0, Qt.PenStyle.DashLine))
        for guide_x in guide_xs:
            painter.drawLine(
                QPointF(guide_x, marker_edge_y),
                QPointF(guide_x, axis_y),
            )

        schedule = projection.schedule
        if projection.is_interval:
            labels = [
                self._format_marker_time(getattr(schedule, "start_time", None)),
                self._format_marker_time(getattr(schedule, "end_time", None)),
            ]
        else:
            labels = [
                self._format_marker_time(
                    getattr(schedule, "start_time", None)
                    or getattr(schedule, "end_time", None)
                )
            ]
        self._draw_time_labels(
            painter,
            guide_xs,
            labels,
            axis_y,
            projection.is_completed,
            left,
            right,
        )
        painter.restore()

    def _draw_time_labels(
        self,
        painter,
        guide_xs,
        labels,
        axis_y,
        completed,
        left,
        right,
    ):
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        label_y = axis_y + 5.0 if completed else axis_y - metrics.height() - 5.0
        label_rects = []
        for guide_x, label in zip(guide_xs, labels):
            text_width = metrics.horizontalAdvance(label)
            label_left = max(left, min(guide_x - text_width / 2.0, right - text_width))
            label_rects.append(QRectF(label_left, label_y, text_width, metrics.height()))

        if len(label_rects) == 2 and label_rects[0].adjusted(-2, 0, 2, 0).intersects(label_rects[1]):
            label_rects[0].moveRight(max(left, guide_xs[0] - 3.0))
            label_rects[1].moveLeft(min(right - label_rects[1].width(), guide_xs[1] + 3.0))

        painter.setPen(QColor(self.AXIS_COLOR))
        for label_rect, label in zip(label_rects, labels):
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, label)

    @staticmethod
    def _format_marker_time(value):
        if isinstance(value, datetime.datetime):
            return value.strftime("%m-%d %H:%M")
        if isinstance(value, datetime.date):
            return value.strftime("%m-%d")
        return "未设置"

    def _virtual_to_screen(self, virtual_x, left, right):
        screen_center = (float(left) + float(right)) / 2.0
        return screen_center + (float(virtual_x) - self.view_center_x) * self.zoom

    def _screen_to_virtual(self, screen_x, left, right):
        screen_center = (float(left) + float(right)) / 2.0
        return self.view_center_x + (float(screen_x) - screen_center) / self.zoom

    def _screen_to_delta(self, screen_x, left, right):
        virtual_x = self._screen_to_virtual(screen_x, left, right)
        return ScheduleAxisService.map_x_to_delta(
            virtual_x,
            self.range_hours,
            0.0,
            self.virtual_axis_width,
            self.log_scale,
        )

    @staticmethod
    def _format_edge_delta(delta_hours):
        direction = "过去" if delta_hours < 0 else "未来"
        hours = abs(delta_hours)
        if hours >= 24.0:
            return f"{direction} {max(1, round(hours / 24.0))}天"
        return f"{direction} {max(1, round(hours))}小时"

    def _clamp_view_center(self, left, right):
        viewport_width = max(float(right) - float(left), 1.0)
        half_visible = viewport_width / (2.0 * self.zoom)
        if half_visible * 2.0 >= self.virtual_axis_width:
            self.view_center_x = self.virtual_axis_width / 2.0
            return
        self.view_center_x = max(
            half_visible,
            min(self.virtual_axis_width - half_visible, self.view_center_x),
        )

    def _projection_at(self, pos):
        for path, projection in reversed(self.hit_regions):
            if path.contains(pos):
                return projection
        return None

    def mouseMoveEvent(self, event):
        if self._pan_start is not None and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.position() - self._pan_start
            left = 20.0
            right = max(float(self.width() - 20), left + 1.0)
            self.view_center_x = self._pan_center_start - delta.x() / self.zoom
            self.vertical_offset = self._pan_vertical_start + delta.y()
            self._clamp_view_center(left, right)
            self._hovered_projection = None
            self.hover_requested.emit(None, event.globalPosition().toPoint())
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.update()
            event.accept()
            return

        projection = self._projection_at(event.position())
        if projection is not self._hovered_projection:
            self._hovered_projection = projection
            self.hover_requested.emit(projection, event.globalPosition().toPoint())
            self.update()
        elif projection is not None:
            self.hover_requested.emit(projection, event.globalPosition().toPoint())
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if projection is not None else Qt.CursorShape.OpenHandCursor
        )
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self._hovered_projection = None
        self.hover_requested.emit(None, QCursor.pos())
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            projection = self._projection_at(event.position())
            if projection is not None:
                self.item_clicked.emit(projection, event.globalPosition().toPoint())
                event.accept()
                return
            self._pan_start = event.position()
            self._pan_center_start = self.view_center_x
            self._pan_vertical_start = self.vertical_offset
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._pan_start is not None:
            self._pan_start = None
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        left = 20.0
        right = max(float(self.width() - 20), left + 1.0)
        cursor_x = event.position().x()
        virtual_under_cursor = self._screen_to_virtual(cursor_x, left, right)
        factor = 1.18 if event.angleDelta().y() > 0 else 1.0 / 1.18
        minimum_zoom = min(1.0, max((right - left) / self.virtual_axis_width, 0.1))
        new_zoom = max(minimum_zoom, min(8.0, self.zoom * factor))
        screen_center = (left + right) / 2.0
        self.zoom = new_zoom
        self.view_center_x = virtual_under_cursor - (cursor_x - screen_center) / self.zoom
        self._clamp_view_center(left, right)
        self.update()
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        left = 20.0
        right = max(float(self.width() - 20), left + 1.0)
        self._clamp_view_center(left, right)


class ScheduleAxisBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self._resize_edges = ()
        self._resize_origin = None
        self._resize_geometry = None
        self._resize_margin = 12
        self._resize_event_widgets = set()
        screen = QGuiApplication.primaryScreen()
        available_width = screen.availableGeometry().width() if screen is not None else 1920
        self._month_virtual_axis_width = max(480, round(available_width * 0.5))
        self._month_default_axis_viewport_width = max(360, round(available_width * 0.375))
        default_board_width = min(
            available_width - 40,
            self._month_default_axis_viewport_width + 92,
        )
        self.setMinimumSize(420, 260)
        self.resize(max(420, default_board_width), 300)
        self.is_pinned = False
        self._drag_offset = None
        self._detail_opener = None
        self._detail_popups = {}
        self._settings_open = False
        self._settings_target_open = False
        self._settings_transitioning = False
        self._settings_icon_angle = 0.0
        self._settings_icon_source = QPixmap()
        self._content_expanded_height = 0
        self._content_animation = None
        self._settings_rotation_animation = None
        self.hover_preview = _AxisSchedulePreview(False)
        self.persistent_preview = _AxisSchedulePreview(True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(0)

        panel = QFrame()
        panel.setStyleSheet("background: transparent;")
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(6)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addStrut(24)
        self.title_label = QLabel("坐标看板", self)
        self.title_label.setStyleSheet(
            "color: white; font-size: 17px; font-weight: bold; "
            "font-family: 'Microsoft YaHei'; background: transparent;"
        )
        header.addStretch()
        self.range_label = QLabel(self)
        self.range_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.range_label.setStyleSheet(
            "color: rgba(255,255,255,0.78); font-size: 9px; background: transparent;"
        )
        self._annotation_text = ""
        button_style = (
            "QPushButton { background: transparent; border: none; border-radius: 4px; } "
            "QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }"
        )

        self.btn_settings = QPushButton(self)
        self.btn_settings.setFixedSize(30, 30)
        self.btn_settings.setIconSize(QSize(24, 24))
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.setToolTip("显示设置")
        self.btn_settings.setStyleSheet(button_style)
        self.btn_settings.clicked.connect(self._toggle_settings_page)

        self.btn_pin = QPushButton(self)
        self.btn_pin.setFixedSize(30, 30)
        self.btn_pin.setIconSize(QSize(16, 16))
        self.btn_pin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pin.setToolTip("窗口置顶")
        self.btn_pin.setStyleSheet(button_style)
        self.btn_pin.clicked.connect(self._toggle_pin)

        self.btn_close = QPushButton(self)
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setIconSize(QSize(12, 12))
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setToolTip("关闭看板")
        self.btn_close.setStyleSheet(
            "QPushButton { background: transparent; border: none; "
            "border-top-right-radius: 12px; } "
            "QPushButton:hover { background: #ff4d4f; }"
        )
        self.btn_close.clicked.connect(self.close)
        layout.addLayout(header)

        self._update_header_icons()
        self._update_header_button_positions()

        self.content_host = QWidget()
        self.content_host.setStyleSheet("background: transparent;")
        self.content_host.installEventFilter(self)

        self.content_stack = QStackedWidget(self.content_host)
        self.content_stack.setStyleSheet("background: transparent;")

        self.display_page = QWidget()
        self.display_page.setStyleSheet("background: transparent;")
        display_layout = QVBoxLayout(self.display_page)
        display_layout.setContentsMargins(0, 0, 0, 0)
        display_layout.setSpacing(0)

        self.canvas = _ScheduleAxisCanvas()
        self.canvas.configure_month_demo(
            self._month_virtual_axis_width,
            self._month_default_axis_viewport_width,
        )
        self.canvas.hover_requested.connect(self._show_hover_preview)
        self.canvas.item_clicked.connect(self._show_persistent_preview)
        display_layout.addWidget(self.canvas, 1)

        self.legend = self.range_label
        self.settings_page = QWidget()
        self.settings_page.setStyleSheet("background: transparent;")
        self.settings_placeholder = QLabel("显示设置\n选项内容待实现", self.content_host)
        self.settings_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.settings_placeholder.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )
        self.settings_placeholder.setStyleSheet(
            "color: rgba(255,255,255,0.88); font-size: 14px; "
            "font-family: 'Microsoft YaHei'; background: transparent;"
        )
        self.settings_placeholder.hide()

        self.content_stack.addWidget(self.display_page)
        self.content_stack.addWidget(self.settings_page)
        self.content_stack.setCurrentWidget(self.display_page)
        layout.addWidget(self.content_host, 1)
        outer.addWidget(panel, 1)

        self._update_header_button_positions()

        self.refresh_data()
        self._install_resize_event_filters()

    def refresh_data(self):
        projections, _range_hours = ScheduleAxisService.load_current_projection(
            datetime.datetime.now()
        )
        self.canvas.set_data(projections, _range_hours)
        self._annotation_text = (
            "线上：未完成 · 线下：已完成 · 竖线：DDL/单时间 · "
            "横条：时间段 · 拖动平移/滚轮缩放 · 范围 ±1个月"
        )
        if hasattr(self, "btn_settings"):
            self._update_header_button_positions()

    def set_detail_opener(self, opener):
        self._detail_opener = opener

    def _load_header_icon(self, icon_name, color):
        return load_colored_svg_pixmap(
            f"assets/icons/{icon_name}",
            color,
            16,
            16,
            self.devicePixelRatioF(),
        )

    def _update_header_icons(self):
        settings_icon = self._load_header_icon("set.svg", "#FFFFFF")
        if not settings_icon.isNull():
            self._settings_icon_source = settings_icon
            self._set_settings_icon_angle(self._settings_icon_angle)

        pin_color = "#FFFFFF" if self.is_pinned else "#96FFFFFF"
        pin_icon = self._load_header_icon("pin.svg", pin_color)
        if not pin_icon.isNull():
            self.btn_pin.setIcon(QIcon(pin_icon))

        close_icon = QPixmap("assets/icons/close.png")
        if not close_icon.isNull():
            self.btn_close.setIcon(QIcon(close_icon))

    def _set_settings_icon_angle(self, angle):
        self._settings_icon_angle = float(angle)
        if self._settings_icon_source.isNull():
            return

        canvas_size = 24.0
        icon_size = 16.0
        ratio = max(self._settings_icon_source.devicePixelRatio(), 1.0)
        pixmap = QPixmap(round(canvas_size * ratio), round(canvas_size * ratio))
        pixmap.setDevicePixelRatio(ratio)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.translate(canvas_size / 2.0, canvas_size / 2.0)
        painter.rotate(self._settings_icon_angle)
        painter.drawPixmap(
            QPointF(-icon_size / 2.0, -icon_size / 2.0),
            self._settings_icon_source,
        )
        painter.end()
        self.btn_settings.setIcon(QIcon(pixmap))

    def _toggle_settings_page(self):
        if self._settings_transitioning:
            return

        self.hover_preview.hide()
        self._settings_transitioning = True
        self._settings_target_open = not self._settings_open
        host_rect = self.content_host.rect()
        self._content_expanded_height = max(host_rect.height(), 1)

        target_angle = 180.0 if self._settings_target_open else 0.0
        self._settings_rotation_animation = QVariantAnimation(self)
        self._settings_rotation_animation.setDuration(360)
        self._settings_rotation_animation.setStartValue(self._settings_icon_angle)
        self._settings_rotation_animation.setEndValue(target_angle)
        self._settings_rotation_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._settings_rotation_animation.valueChanged.connect(self._set_settings_icon_angle)
        self._settings_rotation_animation.start()

        self._content_animation = QPropertyAnimation(
            self.content_stack,
            b"geometry",
            self,
        )
        self._content_animation.setDuration(180)
        self._content_animation.setStartValue(self.content_stack.geometry())
        self._content_animation.setEndValue(
            QRect(0, 0, max(host_rect.width(), 1), 0)
        )
        self._content_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self._content_animation.finished.connect(self._swap_settings_page)
        self._content_animation.start()

    def _swap_settings_page(self):
        target_page = self.settings_page if self._settings_target_open else self.display_page
        self.content_stack.setCurrentWidget(target_page)
        self.settings_placeholder.setVisible(self._settings_target_open)
        if self._settings_target_open:
            self.settings_placeholder.raise_()
        host_rect = self.content_host.rect()
        collapsed_rect = QRect(0, 0, max(host_rect.width(), 1), 0)
        self.content_stack.setGeometry(collapsed_rect)

        self._content_animation = QPropertyAnimation(
            self.content_stack,
            b"geometry",
            self,
        )
        self._content_animation.setDuration(180)
        self._content_animation.setStartValue(collapsed_rect)
        self._content_animation.setEndValue(host_rect)
        self._content_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._content_animation.finished.connect(self._finish_settings_transition)
        self._content_animation.start()

    def _finish_settings_transition(self):
        self.content_stack.setGeometry(self.content_host.rect())
        self._settings_open = self._settings_target_open
        self._settings_transitioning = False

    def eventFilter(self, watched, event):
        if watched is self.content_host and event.type() == QEvent.Type.Resize:
            host_rect = self.content_host.rect()
            if hasattr(self, "settings_placeholder"):
                self.settings_placeholder.setGeometry(host_rect)
            if not self._settings_transitioning:
                self.content_stack.setGeometry(host_rect)

        if watched in self._resize_event_widgets:
            if event.type() == QEvent.Type.Leave:
                watched.unsetCursor()
            if event.type() == QEvent.Type.MouseMove and not event.buttons():
                board_pos = watched.mapTo(self, event.position().toPoint())
                self._apply_resize_cursor(watched, self._resize_edges_at(board_pos))
            if (
                event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
            ):
                board_pos = watched.mapTo(self, event.position().toPoint())
                resize_edges = self._resize_edges_at(board_pos)
                if resize_edges:
                    self._start_resize(
                        resize_edges,
                        event.globalPosition().toPoint(),
                    )
                    event.accept()
                    return True
            if (
                event.type() == QEvent.Type.MouseMove
                and self._resize_edges
                and event.buttons() & Qt.MouseButton.LeftButton
            ):
                self._perform_resize(event.globalPosition().toPoint())
                event.accept()
                return True
            if (
                event.type() == QEvent.Type.MouseButtonRelease
                and event.button() == Qt.MouseButton.LeftButton
                and self._resize_edges
            ):
                self._finish_resize()
                event.accept()
                return True
        return super().eventFilter(watched, event)

    def _toggle_pin(self):
        self.set_pinned(not self.is_pinned)

    def set_pinned(self, enabled):
        self.is_pinned = bool(enabled)
        set_window_pin_state(self, self.is_pinned)
        self._update_header_icons()
        self.raise_()

    def _update_header_button_positions(self):
        offset = 40
        for button in (self.btn_close, self.btn_pin, self.btn_settings):
            button.move(self.width() - offset, 10)
            button.raise_()
            offset += 30

        if hasattr(self, "title_label"):
            self.title_label.adjustSize()
            self.title_label.move(26, 18)
            self.title_label.raise_()

        if hasattr(self, "range_label"):
            annotation_left = self.title_label.geometry().right() + 12
            annotation_right = self.btn_settings.x() - 6
            annotation_width = max(0, annotation_right - annotation_left)
            annotation_height = max(18, self.range_label.fontMetrics().height())
            annotation_y = self.title_label.geometry().bottom() - annotation_height + 1
            elided_text = self.range_label.fontMetrics().elidedText(
                self._annotation_text,
                Qt.TextElideMode.ElideRight,
                annotation_width,
            )
            self.range_label.setText(elided_text)
            self.range_label.setGeometry(
                annotation_left,
                annotation_y,
                annotation_width,
                annotation_height,
            )
            self.range_label.setVisible(annotation_width > 12)
            self.range_label.raise_()

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

    def _install_resize_event_filters(self):
        self._resize_event_widgets.clear()
        for widget in self.findChildren(QWidget):
            widget.setMouseTracking(True)
            widget.installEventFilter(self)
            self._resize_event_widgets.add(widget)

    def _start_resize(self, edges, global_pos):
        self._drag_offset = None
        if self._start_system_resize(edges):
            self._finish_resize()
            return
        self._begin_resize(edges, global_pos)

    def _start_system_resize(self, edges):
        window = self.windowHandle()
        if window is None:
            return False
        edge_map = {
            "left": Qt.Edge.LeftEdge,
            "right": Qt.Edge.RightEdge,
            "top": Qt.Edge.TopEdge,
            "bottom": Qt.Edge.BottomEdge,
        }
        qt_edges = None
        for edge in edges:
            qt_edge = edge_map[edge]
            qt_edges = qt_edge if qt_edges is None else qt_edges | qt_edge
        if qt_edges is None:
            return False
        try:
            return bool(window.startSystemResize(qt_edges))
        except (AttributeError, RuntimeError, TypeError):
            return False

    def _begin_resize(self, edges, global_pos):
        self._drag_offset = None
        self._resize_edges = tuple(edges)
        self._resize_origin = global_pos
        self._resize_geometry = self.geometry()

    def _finish_resize(self):
        self._resize_edges = ()
        self._resize_origin = None
        self._resize_geometry = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            edges = self._resize_edges_at(event.position().toPoint())
            if edges:
                self._start_resize(edges, event.globalPosition().toPoint())
                event.accept()
                return

        if event.button() == Qt.MouseButton.LeftButton and event.position().y() <= 52:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resize_edges and event.buttons() & Qt.MouseButton.LeftButton:
            self._perform_resize(event.globalPosition().toPoint())
            event.accept()
            return
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        if not event.buttons():
            self._update_resize_cursor(event.position().toPoint())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_offset = None
        self._finish_resize()
        self._update_resize_cursor(event.position().toPoint())
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        if not self._resize_edges:
            self.unsetCursor()
        super().leaveEvent(event)

    def _resize_edges_at(self, pos):
        margin = self._resize_margin
        edges = []
        if pos.x() <= margin:
            edges.append("left")
        elif pos.x() >= self.width() - margin:
            edges.append("right")
        if pos.y() <= margin:
            edges.append("top")
        elif pos.y() >= self.height() - margin:
            edges.append("bottom")
        return tuple(edges)

    def _update_resize_cursor(self, pos):
        self._apply_resize_cursor(self, self._resize_edges_at(pos))

    @staticmethod
    def _apply_resize_cursor(widget, edges):
        edges = set(edges)
        if edges in ({"left", "top"}, {"right", "bottom"}):
            widget.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edges in ({"right", "top"}, {"left", "bottom"}):
            widget.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif "left" in edges or "right" in edges:
            widget.setCursor(Qt.CursorShape.SizeHorCursor)
        elif "top" in edges or "bottom" in edges:
            widget.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            widget.unsetCursor()

    def _perform_resize(self, global_pos):
        if self._resize_origin is None or self._resize_geometry is None:
            return
        delta = global_pos - self._resize_origin
        rect = QRect(self._resize_geometry)
        edges = set(self._resize_edges)
        if "left" in edges:
            rect.setLeft(rect.left() + delta.x())
        if "right" in edges:
            rect.setRight(rect.right() + delta.x())
        if "top" in edges:
            rect.setTop(rect.top() + delta.y())
        if "bottom" in edges:
            rect.setBottom(rect.bottom() + delta.y())

        if rect.width() < self.minimumWidth():
            if "left" in edges:
                rect.setLeft(rect.right() - self.minimumWidth() + 1)
            else:
                rect.setRight(rect.left() + self.minimumWidth() - 1)
        if rect.height() < self.minimumHeight():
            if "top" in edges:
                rect.setTop(rect.bottom() - self.minimumHeight() + 1)
            else:
                rect.setBottom(rect.top() + self.minimumHeight() - 1)
        self.setGeometry(rect)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "btn_close"):
            self._update_header_button_positions()
