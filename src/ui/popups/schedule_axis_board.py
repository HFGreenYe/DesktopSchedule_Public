import datetime
import math
import zlib

from PyQt6.QtCore import (
    QEvent,
    QPoint,
    QPointF,
    QRect,
    QRectF,
    QSize,
    Qt,
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
    QAbstractButton,
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.config import AppConfig
from src.services.schedule_axis_service import ScheduleAxisService
from src.ui.common.themed_color_dialog import ThemedColorDialog
from src.ui.utils.icon_loader import load_colored_svg_pixmap
from src.utils.signals import global_signals
from src.utils.window_preferences import set_window_pin_state


class _AxisSchedulePreview(QFrame):
    OUTER_RADIUS = 8.0
    INNER_MARGIN = 6.0
    INNER_RADIUS = 6.0

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
        layout.setContentsMargins(17, 15, 17, 15)
        layout.setSpacing(5)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(0)
        self.title_label = QLabel()
        self.title_label.setWordWrap(True)
        header.addWidget(self.title_label, 1)
        self.close_button = None
        if persistent:
            self.close_button = QPushButton("×")
            self.close_button.setFixedSize(20, 20)
            self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.close_button.clicked.connect(self.hide)
            header.addWidget(self.close_button)
        layout.addLayout(header)

        self.time_label = QLabel()
        self.meta_label = QLabel()
        for label in (self.time_label, self.meta_label):
            label.setWordWrap(True)
            layout.addWidget(label)

        self.note_label = None
        if persistent:
            self.note_label = QLabel("单击详情样本：当前只读")
            layout.addWidget(self.note_label)
        self._apply_theme_text_colors()

    def _apply_theme_text_colors(self):
        title_color = QColor(AppConfig.COLOR_GRADIENT_START)
        time_color = QColor("#FFFFFF")
        detail_color = QColor(AppConfig.COLOR_GRADIENT_END)
        if not title_color.isValid():
            title_color = QColor("#222222")
        if not time_color.isValid():
            time_color = QColor("#222222")
        if not detail_color.isValid():
            detail_color = QColor("#555555")
        self.title_label.setStyleSheet(
            f"color: {title_color.name()}; "
            "font-size: 12px; font-weight: bold; "
            "font-family: 'Microsoft YaHei'; background: transparent;"
        )
        self.time_label.setStyleSheet(
            f"color: {time_color.name()}; "
            "font-size: 10px; font-family: 'Microsoft YaHei'; "
            "background: transparent;"
        )
        self.meta_label.setStyleSheet(
            f"color: {detail_color.name()}; "
            "font-size: 10px; font-family: 'Microsoft YaHei'; "
            "background: transparent;"
        )
        if self.note_label is not None:
            self.note_label.setStyleSheet(
                f"color: {detail_color.name()}; "
                "font-size: 9px; font-family: 'Microsoft YaHei'; "
                "background: transparent;"
            )
        if self.close_button is not None:
            self.close_button.setStyleSheet(
                "QPushButton { "
                f"color: {detail_color.name()}; "
                "background: transparent; border: none; font-size: 14px; "
                "font-weight: bold; } "
                "QPushButton:hover { background: rgba(255,255,255,90); "
                "border-radius: 10px; }"
            )

    def set_projection(self, projection):
        self._apply_theme_text_colors()
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
        outer_rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        outer_path = QPainterPath()
        outer_path.addRoundedRect(
            outer_rect,
            self.OUTER_RADIUS,
            self.OUTER_RADIUS,
        )
        gradient = QLinearGradient(outer_rect.topLeft(), outer_rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        painter.fillPath(outer_path, QBrush(gradient))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(0, 0, 0, 28), 1))
        painter.drawPath(outer_path)

        inner_rect = outer_rect.adjusted(
            self.INNER_MARGIN,
            self.INNER_MARGIN,
            -self.INNER_MARGIN,
            -self.INNER_MARGIN,
        )
        painter.setPen(QPen(QColor("#ffffff"), 2.0))
        painter.setBrush(QColor(255, 255, 255, 190))
        painter.drawRoundedRect(
            inner_rect,
            self.INNER_RADIUS,
            self.INNER_RADIUS,
        )
        super().paintEvent(event)


class _ScheduleAxisCanvas(QWidget):
    hover_requested = pyqtSignal(object, object)
    item_clicked = pyqtSignal(object, object)

    MARKER_HEIGHTS = {0: 9.0, 1: 12.0, 2: 15.0}
    DEADLINE_WIDTH = 2.0
    LANE_GAP = 1.0
    AXIS_MARKER_GAP = 6.0
    AXIS_VERTICAL_RATIO = 0.618
    CENTER_TICK_HALF_HEIGHT = 5.0
    DEFAULT_RANGE_KEY = "month"
    DEFAULT_DIRECTION = "both"
    FOCUS_HOURS = 7.0 * 24.0
    TICK_COUNTS = {
        "day": 2,
        "week": 4,
        "two_weeks": 6,
        "month": 8,
        "year": 11,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.all_projections = []
        self.projections = []
        self.range_key = self.DEFAULT_RANGE_KEY
        self.range_hours = ScheduleAxisService.range_hours_for_key(self.range_key)
        self.direction = self.DEFAULT_DIRECTION
        self.hit_regions = []
        self._hovered_projection = None
        self.virtual_axis_width = 960.0
        self._default_visible_fraction = 0.75
        self.nonlinear_enabled = True
        self._nonlinear_log_scale = 1.0
        self.log_scale = 1.0
        self.zoom = 1.0
        self.view_center_x = self.virtual_axis_width / 2.0
        self._view_pristine = True
        self.vertical_offset = 0.0
        self.axis_color = QColor(AppConfig.COLOR_GRADIENT_START)
        self.font_color = QColor(AppConfig.COLOR_GRADIENT_START)
        self.category_colors = {}
        self._pan_start = None
        self._pan_center_start = 0.0
        self._pan_vertical_start = 0.0

    def configure_viewport(self, virtual_axis_width, default_viewport_width):
        self.virtual_axis_width = max(float(virtual_axis_width), 1.0)
        self._default_visible_fraction = max(
            0.05,
            min(float(default_viewport_width) / self.virtual_axis_width, 1.0),
        )
        self._recalculate_log_scale()
        self._reset_view()
        self.update()

    def _recalculate_log_scale(self):
        focus_hours = min(self.FOCUS_HOURS, self.range_hours / 4.0)
        self._nonlinear_log_scale = ScheduleAxisService.solve_log_scale(
            self.range_hours,
            focus_hours,
            self._default_visible_fraction,
        )
        self.log_scale = (
            self._nonlinear_log_scale if self.nonlinear_enabled else 1e-12
        )

    def _reset_view(self):
        self.zoom = 1.0
        self.vertical_offset = 0.0
        self._view_pristine = True
        self._apply_default_view_anchor()

    def _apply_default_view_anchor(self):
        left = 20.0
        right = max(float(self.width() - 20), left + 1.0)
        visible_width = min((right - left) / self.zoom, self.virtual_axis_width)
        if self.direction == "future":
            self.view_center_x = visible_width / 2.0
        elif self.direction == "past":
            self.view_center_x = self.virtual_axis_width - visible_width / 2.0
        else:
            self.view_center_x = self.virtual_axis_width / 2.0
        self._clamp_view_center(left, right)

    def set_nonlinear_enabled(self, enabled):
        self.set_display_options(
            self.direction,
            self.range_key,
            bool(enabled),
        )

    def set_display_options(self, direction, range_key, nonlinear_enabled):
        normalized_direction = ScheduleAxisService.normalize_direction(direction)
        normalized_range_key = (
            range_key
            if range_key in ScheduleAxisService.RANGE_HOURS_BY_KEY
            else self.DEFAULT_RANGE_KEY
        )
        changed = (
            normalized_direction != self.direction
            or normalized_range_key != self.range_key
            or bool(nonlinear_enabled) != self.nonlinear_enabled
        )
        self.direction = normalized_direction
        self.range_key = normalized_range_key
        self.range_hours = ScheduleAxisService.range_hours_for_key(self.range_key)
        self.nonlinear_enabled = bool(nonlinear_enabled)
        self._recalculate_log_scale()
        self._apply_projection_filter()
        if changed:
            self._reset_view()
        self.update()

    def set_data(self, projections, range_hours):
        del range_hours
        self.all_projections = list(projections)
        self._apply_projection_filter()
        self._hovered_projection = None
        self.hit_regions.clear()
        self.update()

    def _apply_projection_filter(self):
        minimum_delta, maximum_delta = ScheduleAxisService.display_bounds(
            self.range_hours,
            self.direction,
        )
        self.projections = [
            projection
            for projection in self.all_projections
            if projection.end_delta_hours >= minimum_delta
            and projection.start_delta_hours <= maximum_delta
        ]
        self._hovered_projection = None
        self.hit_regions.clear()

    def set_appearance(self, axis_color, font_color, category_colors):
        self.axis_color = QColor(axis_color)
        if not self.axis_color.isValid():
            self.axis_color = QColor(AppConfig.COLOR_GRADIENT_START)
        self.font_color = QColor(font_color)
        if not self.font_color.isValid():
            self.font_color = QColor(AppConfig.COLOR_GRADIENT_START)
        self.category_colors = {
            category_id: QColor(color)
            for category_id, color in category_colors.items()
            if QColor(color).isValid()
        }
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
        axis_y = float(self.height()) * self.AXIS_VERTICAL_RATIO + self.vertical_offset
        origin_virtual_x = ScheduleAxisService.map_delta_to_x(
            0.0,
            self.range_hours,
            0.0,
            self.virtual_axis_width,
            self.log_scale,
            self.direction,
        )
        origin_x = self._virtual_to_screen(origin_virtual_x, left, right)

        axis_color = QColor(self.axis_color)
        font_color = QColor(self.font_color)
        painter.setPen(QPen(axis_color, 1.5))
        painter.drawLine(QPoint(round(left), round(axis_y)), QPoint(round(right), round(axis_y)))
        if self.direction != "future":
            painter.drawLine(QPoint(round(left), round(axis_y)), QPoint(round(left + 6), round(axis_y - 4)))
            painter.drawLine(QPoint(round(left), round(axis_y)), QPoint(round(left + 6), round(axis_y + 4)))
        if self.direction != "past":
            painter.drawLine(QPoint(round(right), round(axis_y)), QPoint(round(right - 6), round(axis_y - 4)))
            painter.drawLine(QPoint(round(right), round(axis_y)), QPoint(round(right - 6), round(axis_y + 4)))

        self._draw_scale_ticks(painter, axis_y, left, right, axis_color)

        if left <= origin_x <= right:
            center_tick_color = self._color_with_alpha_factor(axis_color, 0.65)
            painter.setPen(QPen(center_tick_color, 1))
            painter.drawLine(
                QPoint(
                    round(origin_x),
                    round(axis_y - self.CENTER_TICK_HALF_HEIGHT),
                ),
                QPoint(
                    round(origin_x),
                    round(axis_y + self.CENTER_TICK_HALF_HEIGHT),
                ),
            )

        left_delta = self._screen_to_delta(left, left, right)
        right_delta = self._screen_to_delta(right, left, right)

        if not self.projections:
            empty_color = self._color_with_alpha_factor(font_color, 0.7)
            painter.setPen(empty_color)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "暂无带时间的日程")
            self._draw_axis_text(
                painter,
                axis_y,
                left,
                right,
                origin_x,
                left_delta,
                right_delta,
                font_color,
            )
            return

        markers = self._layout_markers(left, right, axis_y)
        hovered_marker = None
        painter.save()
        painter.setClipRect(
            QRectF(left, canvas_rect.top(), right - left, canvas_rect.height())
        )
        for marker in markers:
            self._draw_marker(painter, marker, left, right)
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
        painter.restore()
        self._draw_axis_text(
            painter,
            axis_y,
            left,
            right,
            origin_x,
            left_delta,
            right_delta,
            font_color,
        )

    def _draw_axis_text(
        self,
        painter,
        axis_y,
        left,
        right,
        origin_x,
        left_delta,
        right_delta,
        font_color,
    ):
        painter.setPen(font_color)
        if self.direction == "both" and left <= origin_x <= right:
            painter.drawText(
                QRectF(origin_x - 25, axis_y + 8, 50, 18),
                Qt.AlignmentFlag.AlignCenter,
                "现在",
            )
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
                self.direction,
            )
            virtual_x2 = ScheduleAxisService.map_delta_to_x(
                projection.end_delta_hours,
                self.range_hours,
                0.0,
                self.virtual_axis_width,
                self.log_scale,
                self.direction,
            )
            x1 = self._virtual_to_screen(virtual_x1, left, right)
            x2 = self._virtual_to_screen(virtual_x2, left, right)
            x1, x2 = min(x1, x2), max(x1, x2)
            if projection.is_interval:
                if x2 < left or x1 > right:
                    continue
                x1 = max(left, x1)
                x2 = min(right, x2)
            elif not left <= x1 <= right:
                continue
            height = self.MARKER_HEIGHTS[projection.importance]
            raw_markers.append((x1, x2, height, projection))
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

    def _draw_marker(self, painter, marker, left, right):
        x1 = marker["x1"]
        x2 = marker["x2"]
        y = marker["y"]
        marker_height = marker["height"]
        projection = marker["projection"]
        category_id = getattr(projection.schedule, "category_id", None)
        color = QColor(self.category_colors.get(category_id, projection.category_color))
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
        hit_rect = marker_rect.adjusted(-4, -4, 4, 4)
        hit_rect.setLeft(max(left, hit_rect.left()))
        hit_rect.setRight(min(right, hit_rect.right()))
        hit_path.addRect(hit_rect)

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

        guide_color = self._color_with_alpha_factor(self.axis_color, 0.65)
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

        painter.setPen(self.font_color)
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
            self.direction,
        )

    @staticmethod
    def _format_edge_delta(delta_hours):
        if abs(delta_hours) < 0.01:
            return "现在"
        direction = "过去" if delta_hours < 0 else "未来"
        hours = abs(delta_hours)
        if hours >= 24.0:
            return f"{direction} {max(1, round(hours / 24.0))}天"
        return f"{direction} {max(1, round(hours))}小时"

    def _draw_scale_ticks(self, painter, axis_y, left, right, axis_color):
        tick_count = self.TICK_COUNTS.get(self.range_key, self.TICK_COUNTS["month"])
        tick_color = self._color_with_alpha_factor(axis_color, 0.65)
        painter.setPen(QPen(tick_color, 1.0))
        signs = []
        if self.direction in {"past", "both"}:
            signs.append(-1.0)
        if self.direction in {"future", "both"}:
            signs.append(1.0)
        for sign in signs:
            for index in range(1, tick_count + 1):
                delta_hours = sign * self.range_hours * index / (tick_count + 1.0)
                virtual_x = ScheduleAxisService.map_delta_to_x(
                    delta_hours,
                    self.range_hours,
                    0.0,
                    self.virtual_axis_width,
                    self.log_scale,
                    self.direction,
                )
                screen_x = self._virtual_to_screen(virtual_x, left, right)
                if left <= screen_x <= right:
                    painter.drawLine(
                        QPointF(screen_x, axis_y - 2.0),
                        QPointF(screen_x, axis_y + 2.0),
                    )

    @staticmethod
    def _color_with_alpha_factor(color, factor):
        adjusted = QColor(color)
        adjusted.setAlpha(max(0, min(255, round(adjusted.alpha() * factor))))
        return adjusted

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
            self._view_pristine = False
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
        self._view_pristine = False
        self.view_center_x = virtual_under_cursor - (cursor_x - screen_center) / self.zoom
        self._clamp_view_center(left, right)
        self.update()
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        left = 20.0
        right = max(float(self.width() - 20), left + 1.0)
        if self._view_pristine:
            self._apply_default_view_anchor()
        else:
            self._clamp_view_center(left, right)


class _ElidedLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self._full_text = str(text)
        self.setToolTip(self._full_text)
        self.setMinimumWidth(0)
        self.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Preferred,
        )

    def set_full_text(self, text):
        self._full_text = str(text)
        self.setToolTip(self._full_text)
        self._update_elided_text()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_elided_text()

    def _update_elided_text(self):
        self.setText(
            self.fontMetrics().elidedText(
                self._full_text,
                Qt.TextElideMode.ElideRight,
                max(self.width() - 2, 0),
            )
        )


class _AxisVisualOption:
    def __init__(self, option_id, name, color):
        self.category_id = option_id
        self.name = name
        self.color = color


class _AxisCategoryRow(QWidget):
    appearance_changed = pyqtSignal()

    def __init__(self, category, parent=None):
        super().__init__(parent)
        self.category_id = category.category_id
        self.color_value = category.color
        self.source_color = category.color
        self.setFixedHeight(22)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.name_label = _ElidedLabel(category.name)
        self.name_label.setStyleSheet(
            "color: #333333; font-size: 10px; background: transparent;"
        )
        layout.addWidget(self.name_label, 1)

        self.color_button = QPushButton()
        self.color_button.setFixedSize(15, 15)
        self.color_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.color_button.setToolTip("选择清单颜色")
        self.color_button.clicked.connect(self._choose_color)
        layout.addWidget(self.color_button)

        self.alpha_spin = QSpinBox()
        self.alpha_spin.setRange(0, 100)
        self.alpha_spin.setValue(100)
        self.alpha_spin.setSuffix("%")
        self.alpha_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.alpha_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.alpha_spin.setFixedSize(42, 18)
        self.alpha_spin.setToolTip("透明度")
        self.alpha_spin.setStyleSheet(
            "QSpinBox { color: #333333; background: rgba(255,255,255,0.7); "
            "border: 1px solid rgba(0,0,0,0.18); border-radius: 3px; "
            "font-size: 9px; padding: 0px 2px; }"
        )
        self.alpha_spin.valueChanged.connect(
            lambda _value: self.appearance_changed.emit()
        )
        layout.addWidget(self.alpha_spin)
        self._apply_color_button_style()

    def update_category(self, category):
        self.category_id = category.category_id
        self.name_label.set_full_text(category.name)
        incoming_color = QColor(category.color)
        if not incoming_color.isValid():
            incoming_color = QColor(ScheduleAxisService.FALLBACK_COLOR)
        previous_source = QColor(self.source_color)
        current_color = QColor(self.color_value)
        if (
            not previous_source.isValid()
            or current_color.name() == previous_source.name()
        ):
            self.color_value = incoming_color.name()
            self._apply_color_button_style()
        self.source_color = incoming_color.name()

    def set_compact_spacing(self, spacing):
        self.layout().setSpacing(max(2, int(spacing)))

    def _apply_color_button_style(self):
        color = QColor(self.color_value)
        if not color.isValid():
            color = QColor(ScheduleAxisService.FALLBACK_COLOR)
        self.color_value = color.name()
        self.color_button.setStyleSheet(
            "QPushButton { "
            f"background-color: {self.color_value}; "
            "border: 1px solid rgba(0,0,0,0.35); border-radius: 2px; "
            "} QPushButton:hover { border: 1px solid #333333; }"
        )

    def _choose_color(self):
        if self.category_id == "axis":
            title = "选择数轴轴体颜色"
        elif self.category_id == "font":
            title = "选择数轴字体颜色"
        else:
            title = f"选择清单{self.name_label._full_text}颜色"
        selected = ThemedColorDialog.get_color(
            QColor(self.color_value),
            title,
            AppConfig.COLOR_GRADIENT_START,
            self,
        )
        if selected.isValid():
            self.color_value = selected.name()
            self._apply_color_button_style()
            self.appearance_changed.emit()


class _AxisCategoryGrid(QWidget):
    ROW_HEIGHT = 20
    ROW_GAP = 2
    LINE_WIDTH = 2

    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.rows = [_AxisCategoryRow(category, self) for category in categories]
        self.column_lines = []
        self.overflow_label = QLabel("…", self)
        self.overflow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overflow_label.setStyleSheet(
            "color: #555555; font-size: 15px; font-weight: bold; "
            "background: transparent;"
        )
        self.overflow_label.hide()
        self.empty_label = QLabel("暂无清单", self)
        self.empty_label.setStyleSheet(
            "color: #777777; font-size: 10px; background: transparent;"
        )
        self.empty_label.hide()
        self._rows_per_column = 1
        self._visible_columns = 1
        self._overflowed = False

    def set_categories(self, categories):
        existing = {row.category_id: row for row in self.rows}
        synchronized_rows = []
        added_rows = []
        for category in categories:
            row = existing.pop(category.category_id, None)
            if row is None:
                row = _AxisCategoryRow(category, self)
                added_rows.append(row)
            else:
                row.update_category(category)
            synchronized_rows.append(row)

        for removed_row in existing.values():
            removed_row.hide()
            removed_row.setParent(None)
            removed_row.deleteLater()
        self.rows = synchronized_rows
        return added_rows

    @classmethod
    def rows_per_column(cls, height):
        pitch = cls.ROW_HEIGHT + cls.ROW_GAP
        return max(1, (max(int(height), cls.ROW_HEIGHT) + cls.ROW_GAP) // pitch)

    def needed_columns(self, height, first_column_top=0):
        height = max(self.ROW_HEIGHT, int(height))
        first_column_top = max(0, min(int(first_column_top), height - self.ROW_HEIGHT))
        first_capacity = self.rows_per_column(height - first_column_top)
        remaining = max(0, len(self.rows) - first_capacity)
        if remaining == 0:
            return 1
        full_capacity = self.rows_per_column(height)
        return 1 + (remaining + full_capacity - 1) // full_capacity

    def _ensure_lines(self, count):
        while len(self.column_lines) < count:
            line = QFrame(self)
            line.setStyleSheet(
                f"background-color: {AppConfig.COLOR_GRADIENT_START}; "
                "border: none; border-radius: 1px;"
            )
            self.column_lines.append(line)

    def reflow(
        self,
        width,
        height,
        visible_columns,
        column_width,
        column_gap,
        line_gap,
        first_column_top=0,
    ):
        width = max(1, int(width))
        height = max(self.ROW_HEIGHT, int(height))
        visible_columns = max(1, int(visible_columns))
        column_width = max(1, int(column_width))
        column_gap = max(0, int(column_gap))
        line_gap = max(2, int(line_gap))
        first_column_top = max(
            0,
            min(int(first_column_top), height - self.ROW_HEIGHT),
        )
        first_capacity = self.rows_per_column(height - first_column_top)
        full_capacity = self.rows_per_column(height)
        capacity = first_capacity + max(visible_columns - 1, 0) * full_capacity
        overflowed = len(self.rows) > capacity
        visible_row_count = min(
            len(self.rows),
            max(0, capacity - (1 if overflowed else 0)),
        )

        self._rows_per_column = first_capacity
        self._full_rows_per_column = full_capacity
        self._visible_columns = visible_columns
        self._overflowed = overflowed
        self.setGeometry(0, 0, width, height)
        self._ensure_lines(visible_columns)

        def slot_for_index(item_index):
            if item_index < first_capacity:
                return 0, item_index
            remainder = item_index - first_capacity
            return 1 + remainder // full_capacity, remainder % full_capacity

        def column_metrics(column):
            top = first_column_top if column == 0 else 0
            column_capacity = first_capacity if column == 0 else full_capacity
            available_height = max(self.ROW_HEIGHT, height - top)
            if column_capacity > 1:
                gap = max(
                    float(self.ROW_GAP),
                    (available_height - column_capacity * self.ROW_HEIGHT)
                    / (column_capacity - 1),
                )
            else:
                gap = 0.0
            return top, column_capacity, gap, self.ROW_HEIGHT + gap

        for index, row_widget in enumerate(self.rows):
            if index >= visible_row_count:
                row_widget.hide()
                continue
            column, row = slot_for_index(index)
            column_top, _capacity, _gap, row_pitch = column_metrics(column)
            column_x = column * (column_width + column_gap)
            row_x = column_x + self.LINE_WIDTH + line_gap
            row_width = max(1, column_width - self.LINE_WIDTH - line_gap)
            row_widget.set_compact_spacing(max(2, line_gap - 1))
            row_widget.setGeometry(
                row_x,
                column_top + round(row * row_pitch),
                row_width,
                self.ROW_HEIGHT,
            )
            row_widget.show()

        if overflowed:
            overflow_index = visible_row_count
            column, row = slot_for_index(overflow_index)
            column_top, _capacity, _gap, row_pitch = column_metrics(column)
            column_x = column * (column_width + column_gap)
            self.overflow_label.setGeometry(
                column_x + self.LINE_WIDTH + line_gap,
                column_top + round(row * row_pitch),
                max(1, column_width - self.LINE_WIDTH - line_gap),
                self.ROW_HEIGHT,
            )
            self.overflow_label.setToolTip(
                f"还有 {len(self.rows) - visible_row_count} 个清单未显示"
            )
            self.overflow_label.show()
        else:
            self.overflow_label.hide()

        if not self.rows:
            self.empty_label.setGeometry(
                self.LINE_WIDTH + line_gap,
                first_column_top,
                max(1, column_width - self.LINE_WIDTH - line_gap),
                self.ROW_HEIGHT,
            )
            self.empty_label.show()
        else:
            self.empty_label.hide()

        counts = [0] * visible_columns
        for index in range(visible_row_count):
            column, _row = slot_for_index(index)
            counts[column] += 1
        if overflowed:
            column, _row = slot_for_index(visible_row_count)
            counts[column] += 1
        if not self.rows:
            counts[0] = 1

        for index, line in enumerate(self.column_lines):
            if index >= visible_columns:
                line.hide()
                continue
            item_count = counts[index]
            if item_count <= 0:
                line.hide()
                continue
            column_top, column_capacity, row_gap, _row_pitch = column_metrics(index)
            line_height = (
                item_count * self.ROW_HEIGHT
                + max(item_count - 1, 0) * row_gap
            )
            if item_count == column_capacity:
                line_height = height - column_top
            line.setGeometry(
                index * (column_width + column_gap),
                column_top,
                self.LINE_WIDTH,
                round(line_height),
            )
            line.show()


class _AxisColorPanel(QWidget):
    TITLE_HEIGHT = 17
    TITLE_GAP = 3

    def __init__(self, categories, heading_style, parent=None):
        super().__init__(parent)
        self.category_count = len(categories)
        axis_options = (
            _AxisVisualOption("axis", "轴体", AppConfig.COLOR_GRADIENT_START),
            _AxisVisualOption("font", "字体", "#333333"),
        )
        self.axis_title_label = QLabel("数轴", self)
        self.axis_title_label.setStyleSheet(heading_style)
        self.axis_grid = _AxisCategoryGrid(axis_options, self)
        self.category_title_label = QLabel("清单", self)
        self.category_title_label.setStyleSheet(heading_style)
        self.category_grid = _AxisCategoryGrid(categories, self)

    def set_categories(self, categories):
        categories = list(categories)
        self.category_count = len(categories)
        return self.category_grid.set_categories(categories)

    def _category_grid_y(self):
        axis_rows_height = (
            2 * _AxisCategoryGrid.ROW_HEIGHT + _AxisCategoryGrid.ROW_GAP
        )
        return (
            self.TITLE_HEIGHT
            + self.TITLE_GAP
            + axis_rows_height
            + 5
            + self.TITLE_HEIGHT
            + self.TITLE_GAP
        )

    def needed_columns(self, height):
        return self.category_grid.needed_columns(
            max(_AxisCategoryGrid.ROW_HEIGHT, int(height)),
            self._category_grid_y(),
        )

    def set_layout_density(
        self,
        width,
        height,
        visible_columns,
        column_width,
        column_gap,
        line_gap,
    ):
        self.resize(max(1, int(width)), max(1, int(height)))
        self.axis_title_label.setGeometry(0, 0, self.width(), self.TITLE_HEIGHT)
        axis_grid_y = self.TITLE_HEIGHT + self.TITLE_GAP
        axis_grid_height = (
            2 * _AxisCategoryGrid.ROW_HEIGHT + _AxisCategoryGrid.ROW_GAP
        )
        self.axis_grid.reflow(
            self.width(),
            axis_grid_height,
            1,
            column_width,
            column_gap,
            line_gap,
        )
        self.axis_grid.move(0, axis_grid_y)
        category_title_y = axis_grid_y + axis_grid_height + 5
        self.category_title_label.setGeometry(
            0,
            category_title_y,
            self.width(),
            self.TITLE_HEIGHT,
        )
        grid_y = self._category_grid_y()
        self.category_grid.reflow(
            self.width(),
            max(_AxisCategoryGrid.ROW_HEIGHT, self.height()),
            visible_columns,
            column_width,
            column_gap,
            line_gap,
            grid_y,
        )
        self.category_grid.move(0, 0)
        self.category_grid.lower()
        self.axis_title_label.raise_()
        self.axis_grid.raise_()
        self.category_title_label.raise_()


class _AxisToggleSwitch(QAbstractButton):
    def __init__(self, accent, parent=None):
        super().__init__(parent)
        self.accent = QColor(accent)
        if not self.accent.isValid():
            self.accent = QColor("#0cc0df")
        self.setCheckable(True)
        self.setFixedSize(28, 16)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        track = QRectF(0.5, 1.5, self.width() - 1.0, self.height() - 3.0)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.accent if self.isChecked() else QColor("#d5d5d5"))
        painter.drawRoundedRect(track, track.height() / 2.0, track.height() / 2.0)

        knob_size = 12.0
        knob_x = self.width() - knob_size - 2.0 if self.isChecked() else 2.0
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(QRectF(knob_x, 2.0, knob_size, knob_size))


class _AxisOptionColumn(QWidget):
    TITLE_HEIGHT = 17
    MODE_ROW_HEIGHT = 22
    GROUP_GAP = 4

    def __init__(self, state, state_changed, accent, heading_style, parent=None):
        super().__init__(parent)
        self.state = state
        self._state_changed = state_changed
        self._button_groups = []
        self.nonlinear_label = QLabel("非均匀显示", self)
        self.nonlinear_label.setStyleSheet(heading_style)
        self.nonlinear_switch = _AxisToggleSwitch(accent, self)
        self.nonlinear_switch.setChecked(bool(self.state.get("nonlinear", True)))
        self.nonlinear_switch.setToolTip("开启 log(t+1) 非均匀刻度")
        self.nonlinear_switch.toggled.connect(
            lambda checked: self._state_changed(
                "nonlinear",
                bool(checked),
                True,
            )
        )
        self.range_title = QLabel("范围", self)
        self.range_title.setStyleSheet(heading_style)
        self.time_title = QLabel("跨度", self)
        self.time_title.setStyleSheet(heading_style)
        self.range_line = self._create_line(accent)
        self.time_line = self._create_line(accent)
        self.direction_buttons = self._create_buttons(
            "direction",
            (
                ("future", "未来"),
                ("both", "未来&&过去"),
                ("past", "过去"),
            ),
            "both",
            accent,
        )
        self.range_buttons = self._create_buttons(
            "range",
            (
                ("day", "一天"),
                ("week", "一周"),
                ("two_weeks", "两周"),
                ("month", "一月"),
                ("year", "一年"),
            ),
            "month",
            accent,
        )

    def _create_line(self, accent):
        line = QFrame(self)
        line.setStyleSheet(
            f"background-color: {accent}; border: none; border-radius: 1px;"
        )
        return line

    def _create_buttons(self, state_key, options, selected, accent):
        group = QButtonGroup(self)
        group.setExclusive(True)
        self._button_groups.append(group)
        radio_style = f"""
            QRadioButton {{
                color: #333333;
                background: transparent;
                font-size: 10px;
                spacing: 5px;
            }}
            QRadioButton::indicator {{
                width: 9px;
                height: 9px;
                border: 1px solid #777777;
                border-radius: 5px;
                background: transparent;
            }}
            QRadioButton::indicator:checked {{
                border: 1px solid {accent};
                background-color: {accent};
            }}
        """
        buttons = []
        for value, label in options:
            radio = QRadioButton(label, self)
            radio.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            radio.setStyleSheet(radio_style)
            radio.setChecked(value == selected)
            radio.toggled.connect(
                lambda checked, key=state_key, option=value: self._state_changed(
                    key,
                    option,
                    checked,
                )
            )
            group.addButton(radio)
            buttons.append(radio)
        return buttons

    def set_layout_density(self, width, height, line_gap):
        self.resize(max(1, int(width)), max(1, int(height)))
        line_gap = max(2, int(line_gap))
        option_count = len(self.direction_buttons) + len(self.range_buttons)
        option_space = max(
            option_count * 15,
            self.height()
            - self.MODE_ROW_HEIGHT
            - self.TITLE_HEIGHT * 2
            - self.GROUP_GAP,
        )
        option_pitch = option_space / option_count
        self.nonlinear_label.setGeometry(
            0,
            0,
            max(1, self.width() - self.nonlinear_switch.width() - 5),
            self.MODE_ROW_HEIGHT,
        )
        self.nonlinear_switch.move(
            max(0, self.width() - self.nonlinear_switch.width()),
            max(0, (self.MODE_ROW_HEIGHT - self.nonlinear_switch.height()) // 2),
        )
        range_title_y = self.MODE_ROW_HEIGHT
        direction_top = range_title_y + self.TITLE_HEIGHT
        direction_height = option_pitch * len(self.direction_buttons)
        time_title_y = direction_top + direction_height + self.GROUP_GAP
        time_top = time_title_y + self.TITLE_HEIGHT
        time_height = max(1.0, self.height() - time_top)

        self.range_title.setGeometry(0, range_title_y, self.width(), self.TITLE_HEIGHT)
        self.time_title.setGeometry(
            0,
            round(time_title_y),
            self.width(),
            self.TITLE_HEIGHT,
        )
        self.range_line.setGeometry(
            0,
            round(direction_top),
            2,
            max(1, round(direction_height)),
        )
        self.time_line.setGeometry(
            0,
            round(time_top),
            2,
            max(1, round(time_height)),
        )

        button_x = 2 + line_gap
        button_width = max(1, self.width() - button_x)
        for index, button in enumerate(self.direction_buttons):
            center_y = direction_top + option_pitch * (index + 0.5)
            button_height = min(17, max(13, round(option_pitch - 1)))
            button.setGeometry(
                button_x,
                round(center_y - button_height / 2),
                button_width,
                button_height,
            )
        time_pitch = time_height / max(len(self.range_buttons), 1)
        for index, button in enumerate(self.range_buttons):
            center_y = time_top + time_pitch * (index + 0.5)
            button_height = min(17, max(13, round(time_pitch - 1)))
            button.setGeometry(
                button_x,
                round(center_y - button_height / 2),
                button_width,
                button_height,
            )


class _AxisSettingsPreview(QFrame):
    HORIZONTAL_PADDING = 12.0
    VERTICAL_PADDING = 10.0
    INTERVAL_WIDTH_LIMITS = {
        "day": (0.12, 0.30),
        "week": (0.06, 0.16),
        "two_weeks": (0.04, 0.11),
        "month": (0.025, 0.075),
        "year": (0.012, 0.035),
    }
    SPAN_LABELS = {
        "day": "1天",
        "week": "1周",
        "two_weeks": "2周",
        "month": "1个月",
        "year": "1年",
    }
    TICK_COUNTS = {
        "day": 2,
        "week": 4,
        "two_weeks": 6,
        "month": 8,
        "year": 11,
    }
    LOG_CURVATURE = 9.0
    ORIGIN_TICK_HALF_HEIGHT = 3.0
    SCALE_TICK_HALF_HEIGHT = 2.0

    def __init__(self, state, axis_rows, category_rows, parent=None):
        super().__init__(parent)
        self.state = state
        self.axis_rows = list(axis_rows)
        self.category_rows = []
        self._connected_row_ids = set()
        self.setObjectName("AxisSettingsPreview")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.setStyleSheet(
            "QFrame#AxisSettingsPreview { background-color: #ffffff; "
            "border: 1px solid #d8d8d8; border-radius: 5px; }"
        )
        self.set_category_rows(category_rows)
        self._connect_rows(self.axis_rows)

    def _connect_rows(self, rows):
        for row in rows:
            row_id = id(row)
            if row_id in self._connected_row_ids:
                continue
            row.appearance_changed.connect(self.update)
            self._connected_row_ids.add(row_id)

    def set_category_rows(self, rows):
        self.category_rows = list(rows)
        self._connect_rows(self.category_rows)
        self.update()

    @staticmethod
    def _stable_seed(row):
        key = f"{row.category_id}:{row.name_label._full_text}"
        return zlib.crc32(key.encode("utf-8")) & 0xFFFFFFFF

    @staticmethod
    def _row_color(row):
        color = QColor(row.color_value)
        if not color.isValid():
            color = QColor(ScheduleAxisService.FALLBACK_COLOR)
        color.setAlphaF(max(0.0, min(row.alpha_spin.value() / 100.0, 1.0)))
        return color

    def _build_preview_items(self, left, right, axis_y):
        count = len(self.category_rows)
        if count == 0:
            return []

        slot_width = max((right - left) / count, 1.0)
        axis_width = max(right - left, 1.0)
        minimum_ratio, maximum_ratio = self.INTERVAL_WIDTH_LIMITS.get(
            self.state.get("range", "month"),
            self.INTERVAL_WIDTH_LIMITS["month"],
        )
        items = []
        for index, row in enumerate(self.category_rows):
            seed = self._stable_seed(row)
            is_interval = bool(seed & 1)
            importance = (seed >> 1) % 3
            completed = bool((seed >> 3) % 3 == 0)
            marker_height = _ScheduleAxisCanvas.MARKER_HEIGHTS[importance]
            slot_left = left + index * slot_width
            slot_right = slot_left + slot_width
            center_ratio = 0.35 + ((seed >> 5) % 31) / 100.0
            center_x = slot_left + slot_width * center_ratio

            if is_interval:
                width_ratio = minimum_ratio + (
                    ((seed >> 16) % 101) / 100.0
                ) * (maximum_ratio - minimum_ratio)
                desired_width = axis_width * width_ratio
                slot_inset = min(max(slot_width * 0.08, 1.0), 4.0)
                available_width = max(
                    _ScheduleAxisCanvas.DEADLINE_WIDTH,
                    slot_width - slot_inset * 2.0,
                )
                marker_width = min(desired_width, available_width)
                center_x = max(
                    slot_left + slot_inset + marker_width / 2.0,
                    min(
                        center_x,
                        slot_right - slot_inset - marker_width / 2.0,
                    ),
                )
                x1 = center_x - marker_width / 2.0
                x2 = center_x + marker_width / 2.0
            else:
                x1 = center_x
                x2 = center_x

            lane = (seed >> 10) % 3
            lane_step = 18.0
            if completed:
                center_y = axis_y + 8.0 + marker_height / 2.0 + lane * lane_step
            else:
                center_y = axis_y - 8.0 - marker_height / 2.0 - lane * lane_step
            items.append(
                {
                    "category_id": row.category_id,
                    "is_interval": is_interval,
                    "importance": importance,
                    "completed": completed,
                    "height": marker_height,
                    "x1": x1,
                    "x2": x2,
                    "y": center_y,
                    "color": self._row_color(row),
                }
            )
        return items

    def _axis_origin_x(self, left, right):
        direction = self.state.get("direction", "both")
        if direction == "future":
            return left
        if direction == "past":
            return right
        return (left + right) / 2.0

    def _axis_labels(self):
        direction = self.state.get("direction", "both")
        span = self.SPAN_LABELS.get(
            self.state.get("range", "month"),
            self.SPAN_LABELS["month"],
        )
        if direction == "future":
            return "现在", "", span
        if direction == "past":
            return span, "", "现在"
        return span, "现在", span

    def _tick_positions(self, left, right):
        direction = self.state.get("direction", "both")
        tick_count = self.TICK_COUNTS.get(
            self.state.get("range", "month"),
            self.TICK_COUNTS["month"],
        )
        nonlinear = bool(self.state.get("nonlinear", True))
        origin_x = self._axis_origin_x(left, right)
        positions = []

        def mapped_ratio(index):
            ratio = index / (tick_count + 1.0)
            if not nonlinear:
                return ratio
            return math.log1p(self.LOG_CURVATURE * ratio) / math.log1p(
                self.LOG_CURVATURE
            )

        if direction in {"future", "both"}:
            side_width = right - origin_x
            positions.extend(
                origin_x + mapped_ratio(index) * side_width
                for index in range(1, tick_count + 1)
            )
        if direction in {"past", "both"}:
            side_width = origin_x - left
            positions.extend(
                origin_x - mapped_ratio(index) * side_width
                for index in range(1, tick_count + 1)
            )
        return sorted(positions)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        left = self.HORIZONTAL_PADDING
        right = max(float(self.width()) - self.HORIZONTAL_PADDING, left + 1.0)
        top = self.VERTICAL_PADDING
        bottom = max(float(self.height()) - self.VERTICAL_PADDING, top + 1.0)
        axis_y = top + (bottom - top) * _ScheduleAxisCanvas.AXIS_VERTICAL_RATIO

        axis_row = self.axis_rows[0] if self.axis_rows else None
        font_row = self.axis_rows[1] if len(self.axis_rows) > 1 else None
        axis_color = self._row_color(axis_row) if axis_row else QColor(AppConfig.COLOR_GRADIENT_START)
        font_color = self._row_color(font_row) if font_row else QColor("#333333")

        painter.setPen(QPen(axis_color, 1.2))
        painter.drawLine(QPointF(left, axis_y), QPointF(right, axis_y))
        arrow_size = 4.0
        direction = self.state.get("direction", "both")
        if direction != "future":
            painter.drawLine(
                QPointF(left, axis_y),
                QPointF(left + arrow_size, axis_y - arrow_size * 0.65),
            )
            painter.drawLine(
                QPointF(left, axis_y),
                QPointF(left + arrow_size, axis_y + arrow_size * 0.65),
            )
        if direction != "past":
            painter.drawLine(
                QPointF(right, axis_y),
                QPointF(right - arrow_size, axis_y - arrow_size * 0.65),
            )
            painter.drawLine(
                QPointF(right, axis_y),
                QPointF(right - arrow_size, axis_y + arrow_size * 0.65),
            )
        origin_x = self._axis_origin_x(left, right)
        tick_color = QColor(axis_color)
        tick_color.setAlpha(max(1, round(axis_color.alpha() * 0.65)))
        painter.setPen(QPen(tick_color, 1.0))
        for tick_x in self._tick_positions(left, right):
            painter.drawLine(
                QPointF(tick_x, axis_y - self.SCALE_TICK_HALF_HEIGHT),
                QPointF(tick_x, axis_y + self.SCALE_TICK_HALF_HEIGHT),
            )
        painter.setPen(QPen(axis_color, 1.2))
        painter.drawLine(
            QPointF(origin_x, axis_y - self.ORIGIN_TICK_HALF_HEIGHT),
            QPointF(origin_x, axis_y + self.ORIGIN_TICK_HALF_HEIGHT),
        )

        for item in self._build_preview_items(left, right, axis_y):
            color = item["color"]
            height = item["height"]
            if item["is_interval"]:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(color)
                painter.drawRect(
                    QRectF(
                        item["x1"],
                        item["y"] - height / 2.0,
                        max(_ScheduleAxisCanvas.DEADLINE_WIDTH, item["x2"] - item["x1"]),
                        height,
                    )
                )
            else:
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(
                    QPen(
                        color,
                        _ScheduleAxisCanvas.DEADLINE_WIDTH,
                        Qt.PenStyle.SolidLine,
                        Qt.PenCapStyle.FlatCap,
                    )
                )
                painter.drawLine(
                    QPointF(item["x1"], item["y"] - height / 2.0),
                    QPointF(item["x1"], item["y"] + height / 2.0),
                )

        painter.setPen(font_color)
        left_label, center_label, right_label = self._axis_labels()
        label_y = axis_y + 4.0
        painter.drawText(
            QRectF(left, label_y, max((right - left) * 0.34, 1.0), 14.0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            left_label,
        )
        if center_label:
            painter.drawText(
                QRectF(origin_x - 25.0, label_y, 50.0, 14.0),
                Qt.AlignmentFlag.AlignCenter,
                center_label,
            )
        painter.drawText(
            QRectF(right - max((right - left) * 0.34, 1.0), label_y, max((right - left) * 0.34, 1.0), 14.0),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            right_label,
        )
        if not self.category_rows:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "暂无清单")


class _AxisSettingsPanel(QWidget):
    option_changed = pyqtSignal(str, object)
    appearance_changed = pyqtSignal()

    OUTER_LEFT = 12
    OUTER_TOP = 8
    OUTER_RIGHT = 12
    OUTER_BOTTOM = 10
    TITLE_HEIGHT = 20
    BODY_TOP = 24
    RANGE_NATURAL_WIDTH = 132
    RANGE_MIN_WIDTH = 108
    COLOR_NATURAL_WIDTH = 164
    COLOR_MIN_WIDTH = 118
    PANEL_NATURAL_GAP = 12
    PANEL_MIN_GAP = 6
    COLUMN_NATURAL_GAP = 8
    COLUMN_MIN_GAP = 4
    LINE_NATURAL_GAP = 8
    LINE_MIN_GAP = 4
    PREVIEW_MIN_WIDTH = 100

    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.state = {
            "nonlinear": True,
            "direction": "both",
            "range": "month",
        }
        accent = AppConfig.COLOR_GRADIENT_START
        heading_style = (
            "color: #333333; font-size: 11px; font-weight: bold; "
            "background: transparent;"
        )

        self.controls_container = QWidget(self)
        self.controls_container.setStyleSheet("background: transparent;")
        self.title_label = QLabel("显示设置", self.controls_container)
        self.title_label.setStyleSheet(
            "color: #222222; font-size: 15px; font-weight: bold; "
            "background: transparent;"
        )
        self.range_panel = _AxisOptionColumn(
            self.state,
            self._set_option,
            accent,
            heading_style,
            self.controls_container,
        )
        self._button_groups = self.range_panel._button_groups
        self.color_panel = _AxisColorPanel(
            categories,
            heading_style,
            self.controls_container,
        )

        self.preview_frame = _AxisSettingsPreview(
            self.state,
            self.color_panel.axis_grid.rows,
            self.color_panel.category_grid.rows,
            self,
        )
        self._connected_appearance_row_ids = set()
        self._connect_appearance_rows(self.color_panel.axis_grid.rows)
        self._connect_appearance_rows(self.color_panel.category_grid.rows)
        self._layout_snapshot = {}

    @staticmethod
    def _interpolate(minimum, natural, factor):
        return int(minimum + (natural - minimum) * factor)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._relayout()

    def showEvent(self, event):
        super().showEvent(event)
        self._relayout()

    def _required_controls_width(
        self,
        visible_columns,
        range_width,
        color_width,
        panel_gap,
        column_gap,
    ):
        color_total = (
            visible_columns * color_width
            + max(visible_columns - 1, 0) * column_gap
        )
        return range_width + panel_gap + color_total

    def _relayout(self):
        inner_width = max(
            1,
            self.width() - self.OUTER_LEFT - self.OUTER_RIGHT,
        )
        inner_height = max(
            1,
            self.height() - self.OUTER_TOP - self.OUTER_BOTTOM,
        )
        body_height = max(1, inner_height - self.BODY_TOP)
        needed_columns = self.color_panel.needed_columns(body_height)
        visible_columns = needed_columns

        def required_with_preview(
            columns,
            range_width,
            color_width,
            panel_gap,
            column_gap,
        ):
            return (
                self._required_controls_width(
                    columns,
                    range_width,
                    color_width,
                    panel_gap,
                    column_gap,
                )
                + panel_gap
                + self.PREVIEW_MIN_WIDTH
            )

        while visible_columns > 1 and required_with_preview(
            visible_columns,
            self.RANGE_MIN_WIDTH,
            self.COLOR_MIN_WIDTH,
            self.PANEL_MIN_GAP,
            self.COLUMN_MIN_GAP,
        ) > inner_width:
            visible_columns -= 1

        natural_required = required_with_preview(
            visible_columns,
            self.RANGE_NATURAL_WIDTH,
            self.COLOR_NATURAL_WIDTH,
            self.PANEL_NATURAL_GAP,
            self.COLUMN_NATURAL_GAP,
        )
        minimum_required = required_with_preview(
            visible_columns,
            self.RANGE_MIN_WIDTH,
            self.COLOR_MIN_WIDTH,
            self.PANEL_MIN_GAP,
            self.COLUMN_MIN_GAP,
        )
        if natural_required <= inner_width:
            density = 1.0
        elif minimum_required >= inner_width:
            density = 0.0
        else:
            density = (inner_width - minimum_required) / (
                natural_required - minimum_required
            )

        range_width = self._interpolate(
            self.RANGE_MIN_WIDTH,
            self.RANGE_NATURAL_WIDTH,
            density,
        )
        color_width = self._interpolate(
            self.COLOR_MIN_WIDTH,
            self.COLOR_NATURAL_WIDTH,
            density,
        )
        panel_gap = self._interpolate(
            self.PANEL_MIN_GAP,
            self.PANEL_NATURAL_GAP,
            density,
        )
        column_gap = self._interpolate(
            self.COLUMN_MIN_GAP,
            self.COLUMN_NATURAL_GAP,
            density,
        )
        line_gap = self._interpolate(
            self.LINE_MIN_GAP,
            self.LINE_NATURAL_GAP,
            density,
        )
        controls_width = self._required_controls_width(
            visible_columns,
            range_width,
            color_width,
            panel_gap,
            column_gap,
        )
        preview_width = max(
            1,
            inner_width - controls_width - panel_gap,
        )

        self.controls_container.setGeometry(
            self.OUTER_LEFT,
            self.OUTER_TOP,
            controls_width,
            inner_height,
        )
        self.title_label.setGeometry(
            0,
            0,
            controls_width,
            self.TITLE_HEIGHT,
        )
        self.range_panel.setGeometry(
            0,
            self.BODY_TOP,
            range_width,
            body_height,
        )
        self.range_panel.set_layout_density(
            range_width,
            body_height,
            line_gap,
        )
        color_x = range_width + panel_gap
        color_total_width = (
            visible_columns * color_width
            + max(visible_columns - 1, 0) * column_gap
        )
        self.color_panel.setGeometry(
            color_x,
            self.BODY_TOP,
            color_total_width,
            body_height,
        )
        self.color_panel.set_layout_density(
            color_total_width,
            body_height,
            visible_columns,
            color_width,
            column_gap,
            line_gap,
        )
        preview_x = self.OUTER_LEFT + controls_width + panel_gap
        self.preview_frame.setGeometry(
            preview_x,
            self.OUTER_TOP,
            preview_width,
            inner_height,
        )
        self._layout_snapshot = {
            "needed_columns": needed_columns,
            "visible_columns": visible_columns,
            "range_width": range_width,
            "color_width": color_width,
            "panel_gap": panel_gap,
            "column_gap": column_gap,
            "line_gap": line_gap,
            "preview_width": preview_width,
            "overflowed": visible_columns < needed_columns,
        }

    def _set_option(self, key, value, checked):
        if checked:
            self.state[key] = value
            if hasattr(self, "preview_frame"):
                self.preview_frame.update()
            self.option_changed.emit(key, value)

    def _connect_appearance_rows(self, rows):
        for row in rows:
            row_id = id(row)
            if row_id in self._connected_appearance_row_ids:
                continue
            row.appearance_changed.connect(self.appearance_changed.emit)
            self._connected_appearance_row_ids.add(row_id)

    def appearance_snapshot(self):
        axis_rows = self.color_panel.axis_grid.rows
        axis_color = (
            _AxisSettingsPreview._row_color(axis_rows[0])
            if axis_rows
            else QColor(AppConfig.COLOR_GRADIENT_START)
        )
        font_color = (
            _AxisSettingsPreview._row_color(axis_rows[1])
            if len(axis_rows) > 1
            else QColor(AppConfig.COLOR_GRADIENT_START)
        )
        category_colors = {
            row.category_id: _AxisSettingsPreview._row_color(row)
            for row in self.color_panel.category_grid.rows
        }
        return axis_color, font_color, category_colors

    def reload_categories(self, categories):
        added_rows = self.color_panel.set_categories(categories)
        self._connect_appearance_rows(added_rows)
        self.preview_frame.set_category_rows(
            self.color_panel.category_grid.rows
        )
        self._relayout()
        self.update()
        self.appearance_changed.emit()


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
        self._settings_icon_angle = 0.0
        self._settings_icon_source = QPixmap()
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
        self.canvas.configure_viewport(
            self._month_virtual_axis_width,
            self._month_default_axis_viewport_width,
        )
        self.canvas.hover_requested.connect(self._show_hover_preview)
        self.canvas.item_clicked.connect(self._show_persistent_preview)
        display_layout.addWidget(self.canvas, 1)

        self.legend = self.range_label
        self.settings_page = QFrame(self.content_host)
        self.settings_page.setObjectName("AxisSettingsPage")
        self.settings_page.setStyleSheet(
            "QFrame#AxisSettingsPage { "
            "background-color: rgba(255, 255, 255, 190); "
            "border: 2px solid #ffffff; border-radius: 6px; "
            "}"
        )
        settings_layout = QVBoxLayout(self.settings_page)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        self.settings_panel = _AxisSettingsPanel(
            ScheduleAxisService.load_category_options(),
            self.settings_page,
        )
        self.settings_panel.option_changed.connect(self._on_setting_option_changed)
        self.settings_panel.appearance_changed.connect(
            self._on_setting_appearance_changed
        )
        settings_layout.addWidget(self.settings_panel)
        self.settings_page.hide()

        self.content_stack.addWidget(self.display_page)
        self.content_stack.raise_()
        layout.addWidget(self.content_host, 1)
        outer.addWidget(panel, 1)

        self._update_header_button_positions()

        self.refresh_data()
        global_signals.category_changed.connect(self.refresh_categories)
        self._install_resize_event_filters()

    def refresh_data(self):
        self.refresh_categories()
        projections, _range_hours = ScheduleAxisService.load_current_projection(
            datetime.datetime.now()
        )
        self.canvas.set_data(projections, _range_hours)
        self._apply_settings_to_canvas()
        self._update_annotation_text()
        if hasattr(self, "btn_settings"):
            self._update_header_button_positions()

    def refresh_categories(self):
        if not hasattr(self, "settings_panel"):
            return
        self.settings_panel.reload_categories(
            ScheduleAxisService.load_category_options()
        )

    def _on_setting_option_changed(self, key, value):
        del value
        self._apply_display_options()
        if key in {"direction", "range"}:
            self._update_annotation_text()
            self._update_header_button_positions()

    def _on_setting_appearance_changed(self):
        if not hasattr(self, "settings_panel"):
            return
        axis_color, font_color, category_colors = (
            self.settings_panel.appearance_snapshot()
        )
        self.canvas.set_appearance(axis_color, font_color, category_colors)

    def _apply_display_options(self):
        state = self.settings_panel.state
        self.canvas.set_display_options(
            state.get("direction", "both"),
            state.get("range", "month"),
            bool(state.get("nonlinear", True)),
        )

    def _apply_settings_to_canvas(self):
        self._apply_display_options()
        self._on_setting_appearance_changed()

    def _update_annotation_text(self):
        if not hasattr(self, "settings_panel"):
            return
        state = self.settings_panel.state
        span = _AxisSettingsPreview.SPAN_LABELS.get(
            state.get("range", "month"),
            _AxisSettingsPreview.SPAN_LABELS["month"],
        )
        direction = state.get("direction", "both")
        if direction == "future":
            range_text = f"未来{span}"
        elif direction == "past":
            range_text = f"过去{span}"
        else:
            range_text = f"±{span}"
        self._annotation_text = (
            "线上：未完成 · 线下：已完成 · 竖线：DDL/单时间 · "
            "横条：时间段 · 拖动平移/滚轮缩放 · "
            f"范围 {range_text}"
        )

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
        self.hover_preview.hide()
        host_rect = self.content_host.rect()
        self.settings_page.setGeometry(host_rect)
        self.content_stack.setGeometry(host_rect)
        self._settings_open = not self._settings_open
        self._set_settings_icon_angle(180.0 if self._settings_open else 0.0)
        if self._settings_open:
            self.content_stack.hide()
            self.settings_page.show()
            self.settings_page.raise_()
        else:
            self.settings_page.hide()
            self.content_stack.show()
            self.content_stack.raise_()

    def eventFilter(self, watched, event):
        if watched is self.content_host and event.type() == QEvent.Type.Resize:
            host_rect = self.content_host.rect()
            if hasattr(self, "settings_page"):
                self.settings_page.setGeometry(host_rect)
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
        self._settings_open = False
        self._set_settings_icon_angle(0.0)
        self.settings_page.hide()
        self.content_stack.show()
        self.content_stack.raise_()
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
