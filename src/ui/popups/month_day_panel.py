import colorsys
import datetime
import math
import random

from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMenu,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt, QPointF, QRectF, QSize, QSettings, pyqtSignal
from PyQt6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QFont,
    QFontMetrics,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)

from ...config import AppConfig
from ...utils.timetable_preferences import (
    get_timetable_preferences,
    set_timetable_schedule_color,
)
from ..utils.icon_loader import load_colored_svg_pixmap


class _MonthScheduleItemFrame(QFrame):
    double_clicked = pyqtSignal(object)
    status_change_requested = pyqtSignal(object, int)

    def __init__(self, schedule, parent=None):
        super().__init__(parent)
        self.schedule = schedule

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.schedule)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        menu = self._build_context_menu()
        menu.exec(event.globalPos())
        event.accept()

    def _build_context_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(
            """
            QMenu {
                background-color: rgba(255, 255, 255, 0.96);
                border: 1px solid rgba(0, 0, 0, 0.10);
                border-radius: 6px;
                padding: 4px;
                color: #333333;
            }
            QMenu::item {
                padding: 6px 18px 6px 8px;
                border-radius: 4px;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
            }
            QMenu::item:selected {
                background-color: rgba(12, 192, 223, 0.14);
            }
            QMenu::item:disabled {
                color: #999999;
            }
            """
        )

        is_completed = int(getattr(self.schedule, "status", 0) or 0) == 1
        text = "未完成" if is_completed else "完成日程"
        target_status = 0 if is_completed else 1
        icon_name = "uncheck.svg" if is_completed else "check.svg"
        icon_pixmap = load_colored_svg_pixmap(
            f"assets/icons/{icon_name}",
            "#333333",
            16,
            16,
            self.devicePixelRatioF(),
        )
        action = QAction(QIcon(icon_pixmap), text, menu)
        action.triggered.connect(
            lambda: self.status_change_requested.emit(self.schedule, target_status)
        )
        menu.addAction(action)
        return menu


class _ElidedTitleLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._full_text = text
        self.setToolTip(text)
        self._update_elided_text()

    def setText(self, text):
        self._full_text = text or ""
        self.setToolTip(self._full_text)
        self._update_elided_text()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_elided_text()

    def sizeHint(self):
        hint = super().sizeHint()
        return QSize(0, hint.height())

    def minimumSizeHint(self):
        hint = super().minimumSizeHint()
        return QSize(0, hint.height())

    def _update_elided_text(self):
        available_width = max(self.contentsRect().width(), 0)
        display_text = self.fontMetrics().elidedText(
            self._full_text,
            Qt.TextElideMode.ElideRight,
            available_width,
        )
        if super().text() != display_text:
            super().setText(display_text)


class MonthDayTimetableFrame(QFrame):
    schedule_double_clicked = pyqtSignal(object)
    status_change_requested = pyqtSignal(object, int)
    dark_mode_toggle_requested = pyqtSignal()

    DAY_MINUTES = 24 * 60
    MIN_VISIBLE_HOURS = 3
    MAX_VISIBLE_HOURS = 6
    HOUR_ROW_HEIGHT = 42.0
    BORDER_WIDTH = 2.0
    CORNER_RADIUS = 8.0
    TIME_AXIS_WIDTH = 40.0
    DDL_LINE_HEIGHT = 3.0
    EVENT_GAP = 2.0
    EVENT_BLOCK_COLUMN_GAP = 2.0
    EVENT_COLUMN_GAP = 1.0
    EVENT_RADIUS = 3.0
    EVENT_PALETTE = (
        "#ff6b6b",
        "#4d96ff",
        "#6bcb77",
        "#ffd93d",
        "#9b5de5",
        "#f15bb5",
        "#00bbf9",
        "#00f5d4",
        "#ff9f1c",
        "#845ec2",
        "#2ec4b6",
        "#e76f51",
        "#577590",
        "#90be6d",
        "#f94144",
        "#43aa8b",
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.panel_date = None
        self.schedules = []
        self.visible_start_minutes = 0
        self.visible_minutes = self.MIN_VISIBLE_HOURS * 60
        preferences = get_timetable_preferences()
        self._schedule_colors = {}
        self._schedule_color_overrides = dict(
            preferences.get("schedule_colors", {})
        )
        self._palette_order = list(self.EVENT_PALETTE)
        random.SystemRandom().shuffle(self._palette_order)
        self._next_color_index = 0
        self._hit_regions = []
        self._visible_event_labels = []
        self._visible_ddl_labels = []
        self._occupied_label_rects = []
        self._dark_mode = False
        self.setMouseTracking(True)
        self.setStyleSheet("background: transparent; border: none;")

    def set_dark_mode(self, dark):
        self._dark_mode = bool(dark)
        self.update()

    def set_schedule_data(self, qdate, schedules):
        self.panel_date = qdate
        self.schedules = list(schedules or [])
        self._ensure_schedule_colors(self.schedules)
        self.visible_start_minutes, self.visible_minutes = self._initial_window()
        self.setFixedHeight(
            int(
                self.visible_minutes / 60.0 * self.HOUR_ROW_HEIGHT
                + self.BORDER_WIDTH * 2
            )
        )
        self.update()

    def sizeHint(self):
        return QSize(206, self.height() or 130)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta == 0:
            event.ignore()
            return

        max_start = max(0, self.DAY_MINUTES - int(self.visible_minutes))
        step = -60 if delta > 0 else 60
        next_start = min(max(self.visible_start_minutes + step, 0), max_start)
        if next_start != self.visible_start_minutes:
            self.visible_start_minutes = next_start
            self.update()
        event.accept()

    def _day_bounds(self):
        target_date = self.panel_date.toPyDate()
        day_start = datetime.datetime.combine(target_date, datetime.time.min)
        day_end = day_start + datetime.timedelta(days=1)
        return day_start, day_end

    @staticmethod
    def _minutes_from_day_start(day_start, value):
        delta = value - day_start
        return max(0.0, min(1440.0, delta.total_seconds() / 60.0))

    def _day_items(self):
        day_start, day_end = self._day_bounds()
        intervals = []
        ddl_points = []
        for schedule in self.schedules:
            start_time = getattr(schedule, "start_time", None)
            end_time = getattr(schedule, "end_time", None)
            if start_time and end_time and start_time != end_time:
                interval_start = max(start_time, day_start)
                interval_end = min(end_time, day_end)
                if interval_end > interval_start:
                    intervals.append(
                        {
                            "schedule": schedule,
                            "start": self._minutes_from_day_start(
                                day_start,
                                interval_start,
                            ),
                            "end": self._minutes_from_day_start(
                                day_start,
                                interval_end,
                            ),
                        }
                    )
                continue

            point_time = end_time or start_time
            if point_time and day_start <= point_time < day_end:
                ddl_points.append(
                    {
                        "schedule": schedule,
                        "point": self._minutes_from_day_start(day_start, point_time),
                    }
                )
        return intervals, ddl_points

    def _content_bounds(self):
        intervals, ddl_points = self._day_items()
        values = []
        for interval in intervals:
            values.extend([interval["start"], interval["end"]])
        for ddl_point in ddl_points:
            values.append(ddl_point["point"])
        if not values:
            return 0.0, 180.0
        return min(values), max(values)

    def _initial_window(self):
        top, bottom = self._content_bounds()
        earliest_hour = int(top // 60)
        span_minutes = max(0.0, bottom - top)

        if span_minutes <= self.MIN_VISIBLE_HOURS * 60:
            visible_hours = self.MIN_VISIBLE_HOURS
            start_hour = earliest_hour
            if start_hour + visible_hours > 24:
                start_hour = 24 - visible_hours
            return start_hour * 60, visible_hours * 60

        if span_minutes > self.MAX_VISIBLE_HOURS * 60:
            visible_hours = self.MAX_VISIBLE_HOURS
            start_hour = min(earliest_hour, 24 - visible_hours)
            return start_hour * 60, visible_hours * 60

        end_hour = min(24, max(earliest_hour + 1, int(math.ceil(bottom / 60.0))))
        visible_hours = max(
            self.MIN_VISIBLE_HOURS,
            min(self.MAX_VISIBLE_HOURS, end_hour - earliest_hour),
        )
        start_hour = earliest_hour
        if start_hour + visible_hours > 24:
            start_hour = 24 - visible_hours
        return start_hour * 60, visible_hours * 60

    def _ensure_schedule_colors(self, schedules):
        for schedule in schedules:
            raw_schedule_id = getattr(schedule, "id", None)
            schedule_id = raw_schedule_id if raw_schedule_id is not None else id(schedule)
            if schedule_id in self._schedule_colors:
                continue
            override_color = (
                self._schedule_color_overrides.get(str(raw_schedule_id))
                if raw_schedule_id is not None
                else None
            )
            if override_color:
                color = QColor(override_color)
                if color.isValid():
                    color.setAlpha(218)
                    self._schedule_colors[schedule_id] = color
                    continue

            color = self._next_event_color()
            self._schedule_colors[schedule_id] = color
            if raw_schedule_id is not None:
                stored_color = color.name()
                self._schedule_color_overrides[str(raw_schedule_id)] = stored_color
                set_timetable_schedule_color(raw_schedule_id, stored_color)

    def _next_event_color(self):
        if self._next_color_index < len(self._palette_order):
            color = QColor(self._palette_order[self._next_color_index])
        else:
            hue = (self._next_color_index * 0.61803398875) % 1.0
            red, green, blue = colorsys.hsv_to_rgb(hue, 0.64, 0.94)
            color = QColor(round(red * 255), round(green * 255), round(blue * 255))
        self._next_color_index += 1
        color.setAlpha(218)
        return color

    def _color_for_schedule(self, schedule):
        schedule_id = getattr(schedule, "id", id(schedule))
        color = self._schedule_colors.get(schedule_id)
        if color is None:
            color = self._next_event_color()
            self._schedule_colors[schedule_id] = color
        return QColor(color)

    @staticmethod
    def _is_completed(schedule):
        return int(getattr(schedule, "status", 0) or 0) == 1

    @staticmethod
    def _is_expired(schedule):
        if MonthDayTimetableFrame._is_completed(schedule):
            return False
        end_time = getattr(schedule, "end_time", None)
        return bool(end_time and end_time < datetime.datetime.now())

    def _display_style_for_schedule(self, schedule):
        if self._is_completed(schedule):
            if self._dark_mode:
                return {
                    "fill": QColor(58, 58, 58, 230),
                    "line": QColor(80, 80, 80, 230),
                    "border": QColor(110, 110, 110, 190),
                    "text": QColor(235, 235, 235, 230),
                    "shadow": QColor(0, 0, 0, 0),
                }
            return {
                "fill": QColor(255, 255, 255, 238),
                "line": QColor(255, 255, 255, 245),
                "border": QColor(170, 184, 192, 210),
                "text": QColor(AppConfig.COLOR_GRADIENT_START),
                "shadow": QColor(255, 255, 255, 0),
            }
        if self._is_expired(schedule):
            color = QColor(156, 166, 171, 218)
            return {
                "fill": color,
                "line": color,
                "border": None,
                "text": QColor(255, 255, 255, 235),
                "shadow": QColor(0, 0, 0, 65),
            }

        color = self._color_for_schedule(schedule)
        return {
            "fill": color,
            "line": color,
            "border": QColor(255, 255, 255, 245),
            "text": QColor(255, 255, 255, 235),
            "shadow": QColor(0, 0, 0, 65),
        }

    @staticmethod
    def _format_schedule_time_text(schedule):
        start_time = getattr(schedule, "start_time", None)
        end_time = getattr(schedule, "end_time", None)
        if start_time and end_time and start_time != end_time:
            return f"{start_time:%H:%M}-{end_time:%H:%M}"
        target_time = end_time or start_time
        if target_time:
            return f"{target_time:%H:%M}"
        return ""

    def _schedule_region_at_position(self, position):
        for region in reversed(self._hit_regions):
            if region["rect"].contains(position):
                return region
        return None

    def _minute_to_y(self, minute, visible_start, grid_top):
        return grid_top + (minute - visible_start) / 60.0 * self.HOUR_ROW_HEIGHT

    def _grid_rects(self):
        outer = QRectF(self.rect()).adjusted(
            self.BORDER_WIDTH,
            self.BORDER_WIDTH,
            -self.BORDER_WIDTH,
            -self.BORDER_WIDTH,
        )
        axis_rect = QRectF(
            outer.left(),
            outer.top(),
            self.TIME_AXIS_WIDTH,
            outer.height(),
        )
        content_rect = QRectF(
            axis_rect.right(),
            outer.top(),
            max(1.0, outer.width() - self.TIME_AXIS_WIDTH),
            outer.height(),
        )
        return outer, axis_rect, content_rect

    def _layout_interval_groups(self, intervals):
        if not intervals:
            return []

        sorted_intervals = sorted(
            intervals,
            key=lambda item: (
                item["start"],
                item["end"],
                getattr(item["schedule"], "id", 0),
            ),
        )
        groups = []
        current_group = []
        current_group_end = None
        for interval in sorted_intervals:
            if current_group_end is None or interval["start"] < current_group_end:
                current_group.append(interval)
                current_group_end = max(current_group_end or interval["end"], interval["end"])
            else:
                groups.append(current_group)
                current_group = [interval]
                current_group_end = interval["end"]
        if current_group:
            groups.append(current_group)

        positioned = []
        for group in groups:
            columns_end = []
            for interval in group:
                assigned_column = None
                for column_index, column_end in enumerate(columns_end):
                    if column_end <= interval["start"]:
                        assigned_column = column_index
                        columns_end[column_index] = interval["end"]
                        break
                if assigned_column is None:
                    assigned_column = len(columns_end)
                    columns_end.append(interval["end"])
                interval["column"] = assigned_column

            column_count = max(1, len(columns_end))
            for interval in group:
                interval["column_count"] = column_count
                positioned.append(interval)
        return positioned

    def _visible_items(self):
        intervals, ddl_points = self._day_items()
        visible_start = float(self.visible_start_minutes)
        visible_end = visible_start + float(self.visible_minutes)
        all_intervals = []
        for interval in intervals:
            visible_interval_start = max(interval["start"], visible_start)
            visible_interval_end = min(interval["end"], visible_end)
            if visible_interval_end > visible_interval_start:
                all_intervals.append(
                    {
                        **interval,
                        "visible_start": visible_interval_start,
                        "visible_end": visible_interval_end,
                    }
                )
        visible_intervals = self._layout_interval_groups(all_intervals)
        visible_points = [
            point
            for point in ddl_points
            if visible_start <= point["point"] <= visible_end
        ]
        return visible_intervals, visible_points

    def _draw_background(self, painter, outer, axis_rect, content_rect):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        background = QColor(43, 43, 43, 246) if self._dark_mode else QColor(255, 255, 255, 245)
        border = QColor(255, 255, 255, 76) if self._dark_mode else QColor(255, 255, 255, 235)
        divider = QColor(255, 255, 255, 58) if self._dark_mode else QColor(205, 216, 224, 210)
        background_path = QPainterPath()
        background_path.addRoundedRect(
            QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5),
            self.CORNER_RADIUS,
            self.CORNER_RADIUS,
        )
        painter.fillPath(background_path, background)
        painter.setPen(QPen(border, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(background_path)
        painter.fillRect(axis_rect, background)
        painter.fillRect(content_rect, background)
        painter.setPen(QPen(divider, 1))
        painter.drawLine(
            QPointF(axis_rect.right(), outer.top()),
            QPointF(axis_rect.right(), outer.bottom()),
        )
        painter.restore()

    def _draw_hour_grid(self, painter, axis_rect, content_rect):
        visible_start = int(self.visible_start_minutes)
        visible_hours = int(self.visible_minutes // 60)
        painter.save()
        if self._dark_mode:
            line_color = QColor(255, 255, 255, 55)
            text_color = QColor(235, 235, 235, 220)
        else:
            line_color = QColor(205, 216, 224, 220)
            text_color = QColor(78, 94, 108, 235)
        painter.setPen(QPen(line_color, 1))
        font = QFont("Microsoft YaHei")
        font.setPixelSize(10)
        painter.setFont(font)
        metrics = QFontMetrics(font)
        for row in range(visible_hours + 1):
            y_value = content_rect.top() + row * self.HOUR_ROW_HEIGHT
            painter.setPen(QPen(line_color, 1))
            painter.drawLine(
                QPointF(content_rect.left(), y_value),
                QPointF(content_rect.right(), y_value),
            )
            hour_value = (visible_start // 60) + row
            if row < visible_hours and 0 <= hour_value < 24:
                label_rect = QRectF(
                    axis_rect.left() + 4.0,
                    y_value + 2.0,
                    axis_rect.width() - 8.0,
                    metrics.height(),
                )
                painter.setPen(text_color)
                painter.drawText(
                    label_rect,
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                    f"{hour_value:02d}:00",
                )
        painter.restore()

    def _draw_interval_items(self, painter, intervals, content_rect):
        visible_start = float(self.visible_start_minutes)
        for interval in intervals:
            column_count = interval["column_count"]
            column_gap = self.EVENT_BLOCK_COLUMN_GAP
            available_width = max(
                1.0,
                content_rect.width() - column_gap * (column_count + 1),
            )
            rect_width = max(1.0, available_width / column_count)
            rect_x = content_rect.left() + column_gap + interval["column"] * (
                rect_width + column_gap
            )
            rect_y = self._minute_to_y(
                interval["visible_start"],
                visible_start,
                content_rect.top(),
            )
            rect_bottom = self._minute_to_y(
                interval["visible_end"],
                visible_start,
                content_rect.top(),
            )
            rect_y = max(content_rect.top() + self.EVENT_GAP, rect_y + self.EVENT_GAP)
            rect_bottom = min(content_rect.bottom() - self.EVENT_GAP, rect_bottom - self.EVENT_GAP)
            rect_height = max(3.0, rect_bottom - rect_y)
            if rect_height <= 0:
                continue

            event_rect = QRectF(rect_x, rect_y, rect_width, rect_height)
            event_path = QPainterPath()
            event_path.addRoundedRect(event_rect, self.EVENT_RADIUS, self.EVENT_RADIUS)
            display_style = self._display_style_for_schedule(interval["schedule"])
            painter.fillPath(event_path, display_style["fill"])
            if display_style["border"] is not None:
                painter.save()
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(QPen(display_style["border"], 1))
                painter.drawPath(event_path)
                painter.restore()
            self._hit_regions.append(
                {
                    "rect": event_rect,
                    "schedule": interval["schedule"],
                    "kind": "interval",
                }
            )
            self._occupied_label_rects.append(event_rect)
            self._visible_event_labels.append(
                {
                    "rect": event_rect,
                    "schedule": interval["schedule"],
                    "style": display_style,
                }
            )

    def _draw_interval_labels(self, painter):
        if not self._visible_event_labels:
            return

        title_font = QFont("Microsoft YaHei")
        title_font.setPixelSize(10)
        title_font.setBold(True)
        time_font = QFont(title_font)
        time_font.setPixelSize(9)
        time_font.setBold(False)
        title_metrics = QFontMetrics(title_font)
        time_metrics = QFontMetrics(time_font)
        total_text_height = title_metrics.height() + time_metrics.height() + 1
        for item in self._visible_event_labels:
            rect = item["rect"]
            if rect.width() < 24 or rect.height() < total_text_height:
                continue
            schedule = item["schedule"]
            display_style = item["style"]
            text_rect = rect.adjusted(4.0, 0.0, -4.0, 0.0)
            title = str(getattr(schedule, "title", "") or "未命名日程")
            time_text = self._format_schedule_time_text(schedule)
            title_text = title_metrics.elidedText(
                title,
                Qt.TextElideMode.ElideRight,
                max(1, int(text_rect.width())),
            )
            time_text = time_metrics.elidedText(
                time_text,
                Qt.TextElideMode.ElideRight,
                max(1, int(text_rect.width())),
            )
            group_top = rect.center().y() - total_text_height / 2
            title_rect = QRectF(
                text_rect.left(),
                group_top,
                text_rect.width(),
                title_metrics.height(),
            )
            time_rect = QRectF(
                text_rect.left(),
                group_top + title_metrics.height() + 1,
                text_rect.width(),
                time_metrics.height(),
            )
            if display_style["shadow"].alpha() > 0:
                painter.setPen(display_style["shadow"])
                painter.setFont(title_font)
                painter.drawText(
                    title_rect.translated(0.8, 0.8),
                    Qt.AlignmentFlag.AlignCenter,
                    title_text,
                )
                painter.setFont(time_font)
                painter.drawText(
                    time_rect.translated(0.8, 0.8),
                    Qt.AlignmentFlag.AlignCenter,
                    time_text,
                )
            painter.setPen(display_style["text"])
            painter.setFont(title_font)
            painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, title_text)
            painter.setFont(time_font)
            painter.drawText(time_rect, Qt.AlignmentFlag.AlignCenter, time_text)

    def _draw_ddl_items(self, painter, ddl_points, content_rect):
        if not ddl_points:
            return

        points_by_minute = {}
        for ddl_point in ddl_points:
            points_by_minute.setdefault(round(ddl_point["point"] * 1000), []).append(ddl_point)

        visible_start = float(self.visible_start_minutes)
        for points in points_by_minute.values():
            points.sort(key=lambda item: getattr(item["schedule"], "id", 0))
            segment_count = max(1, len(points))
            segment_gap = self.EVENT_COLUMN_GAP
            available_width = max(
                1.0,
                content_rect.width() - segment_gap * (segment_count + 1),
            )
            segment_width = max(1.0, available_width / segment_count)
            for point_index, ddl_point in enumerate(points):
                line_y = self._minute_to_y(
                    ddl_point["point"],
                    visible_start,
                    content_rect.top(),
                )
                line_y = min(
                    max(content_rect.top() + self.DDL_LINE_HEIGHT, line_y),
                    content_rect.bottom() - self.DDL_LINE_HEIGHT,
                )
                line_x = content_rect.left() + segment_gap + point_index * (
                    segment_width + segment_gap
                )
                line_rect = QRectF(
                    line_x,
                    line_y - self.DDL_LINE_HEIGHT / 2,
                    segment_width,
                    self.DDL_LINE_HEIGHT,
                )
                display_style = self._display_style_for_schedule(ddl_point["schedule"])
                painter.fillRect(line_rect, display_style["line"])
                self._hit_regions.append(
                    {
                        "rect": line_rect.adjusted(0.0, -4.0, 0.0, 4.0),
                        "schedule": ddl_point["schedule"],
                        "kind": "ddl",
                    }
                )
                self._queue_ddl_label(
                    ddl_point["schedule"],
                    display_style,
                    line_rect,
                    content_rect,
                )

    def _queue_ddl_label(self, schedule, display_style, line_rect, content_rect):
        font = QFont("Microsoft YaHei")
        font.setPixelSize(9)
        font.setBold(True)
        metrics = QFontMetrics(font)
        label_height = metrics.height()
        if line_rect.width() < 28:
            return

        label_bottom = line_rect.top() - 2.0
        label_top = label_bottom - label_height
        if label_top < content_rect.top() + 1 or label_bottom > content_rect.bottom():
            return

        label_rect = QRectF(line_rect.left(), label_top, line_rect.width(), label_height)
        for occupied_rect in self._occupied_label_rects:
            if label_rect.intersects(occupied_rect.adjusted(-1.0, -1.0, 1.0, 1.0)):
                return

        title = str(getattr(schedule, "title", "") or "未命名日程")
        time_text = self._format_schedule_time_text(schedule)
        text = f"{title} {time_text}".strip()
        self._visible_ddl_labels.append(
            {
                "rect": label_rect,
                "text": metrics.elidedText(
                    text,
                    Qt.TextElideMode.ElideRight,
                    max(1, int(label_rect.width())),
                ),
                "font": font,
                "style": display_style,
            }
        )
        self._occupied_label_rects.append(label_rect)

    def _draw_ddl_labels(self, painter):
        for item in self._visible_ddl_labels:
            painter.setFont(item["font"])
            painter.setPen(
                QColor(235, 235, 235, 215)
                if self._dark_mode
                else QColor(80, 92, 104, 225)
            )
            painter.drawText(
                item["rect"],
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                item["text"],
            )

    def _draw_current_time_line(self, painter, content_rect):
        if self.panel_date is None or self.panel_date.toPyDate() != datetime.date.today():
            return
        now = datetime.datetime.now()
        current_minutes = now.hour * 60 + now.minute + now.second / 60.0
        visible_start = float(self.visible_start_minutes)
        visible_end = visible_start + float(self.visible_minutes)
        if not (visible_start <= current_minutes <= visible_end):
            return

        line_y = self._minute_to_y(current_minutes, visible_start, content_rect.top())
        painter.save()
        pen = QPen(
            QColor(235, 235, 235, 200)
            if self._dark_mode
            else QColor(120, 120, 120, 200),
            1,
        )
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setDashPattern([4, 4])
        painter.setPen(pen)
        painter.drawLine(
            QPointF(content_rect.left(), line_y),
            QPointF(content_rect.right(), line_y),
        )
        painter.restore()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        outer, axis_rect, content_rect = self._grid_rects()
        self._draw_background(painter, outer, axis_rect, content_rect)

        self._hit_regions = []
        self._visible_event_labels = []
        self._visible_ddl_labels = []
        self._occupied_label_rects = []
        intervals, ddl_points = self._visible_items()
        self._draw_interval_items(painter, intervals, content_rect)
        self._draw_ddl_items(painter, ddl_points, content_rect)
        self._draw_hour_grid(painter, axis_rect, content_rect)
        self._draw_interval_labels(painter)
        self._draw_ddl_labels(painter)
        self._draw_current_time_line(painter, content_rect)
        super().paintEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            region = self._schedule_region_at_position(QPointF(event.pos()))
            if region is not None:
                self.schedule_double_clicked.emit(region["schedule"])
                event.accept()
                return
            self.dark_mode_toggle_requested.emit()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        region = self._schedule_region_at_position(QPointF(event.pos()))
        if region is None:
            super().contextMenuEvent(event)
            return

        item_proxy = _MonthScheduleItemFrame(region["schedule"], self)
        item_proxy.status_change_requested.connect(self.status_change_requested.emit)
        menu = item_proxy._build_context_menu()
        menu.exec(event.globalPos())
        event.accept()


class MonthDayPanel(QWidget):
    closed = pyqtSignal(object)
    schedule_double_clicked = pyqtSignal(object, object)
    schedule_status_requested = pyqtSignal(object, int)

    def __init__(self, qdate, schedules, parent=None):
        super().__init__(parent, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.panel_date = qdate
        self._schedules = []
        self.schedule_display_mode = get_timetable_preferences().get(
            "display_mode",
            "card",
        )
        self._dark_mode = self._default_dark_mode()
        self._closed_emitted = False
        self._drag_offset = None
        self.child_detail_popups = []

        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedWidth(280)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(14, 12, 14, 12)
        self._layout.setSpacing(8)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        self.date_label = QLabel()
        self.date_label.setWordWrap(True)
        self.date_label.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei'; font-size: 14px; font-weight: bold;"
        )
        header_layout.addWidget(self.date_label, 1)

        self.btn_close = QPushButton("×")
        self.btn_close.setFixedSize(22, 22)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.92);
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.18);
                border-radius: 11px;
            }
            """
        )
        self.btn_close.clicked.connect(self.close)
        header_layout.addWidget(self.btn_close, 0, Qt.AlignmentFlag.AlignTop)
        self._layout.addLayout(header_layout)

        self.empty_label = QLabel("当日暂无日程")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setWordWrap(True)
        self.empty_label.setStyleSheet(
            "color: rgba(255, 255, 255, 0.86); font-family: 'Microsoft YaHei'; "
            "font-size: 12px; padding: 18px 8px;"
        )
        self._layout.addWidget(self.empty_label)

        self.body_scroll = QScrollArea()
        self.body_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.body_scroll.setWidgetResizable(True)
        self.body_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.body_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.body_scroll.setStyleSheet(
            """
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.35);
                border-radius: 2px;
                min-height: 18px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
                background: transparent;
            }
            """
        )

        self.body_container = QWidget()
        self.body_container.setStyleSheet("background: transparent;")
        self.body_layout = QVBoxLayout(self.body_container)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(4)
        self.body_layout.addStretch()
        self.body_scroll.setWidget(self.body_container)
        self._layout.addWidget(self.body_scroll)

        self.timetable_frame = MonthDayTimetableFrame()
        self.timetable_frame.schedule_double_clicked.connect(
            self._emit_schedule_double_clicked
        )
        self.timetable_frame.status_change_requested.connect(
            self.schedule_status_requested.emit
        )
        self.timetable_frame.dark_mode_toggle_requested.connect(self._toggle_dark_mode)
        self._layout.addWidget(self.timetable_frame)
        self.timetable_frame.hide()

        self.summary_label = QLabel()
        self.summary_label.setStyleSheet(
            "color: rgba(255, 255, 255, 0.78); font-family: 'Microsoft YaHei'; font-size: 11px;"
        )
        self._layout.addWidget(self.summary_label)

        self.set_panel_data(qdate, schedules)

    def _default_dark_mode(self):
        return QSettings("Lankor", "DesktopSchedule").value(
            "week/dark_mode",
            False,
            type=bool,
        )

    def _timetable_dark_mode_enabled(self):
        return self.schedule_display_mode == "timetable" and self._dark_mode

    def set_dark_mode(self, dark):
        self._dark_mode = bool(dark)
        self.timetable_frame.set_dark_mode(self._dark_mode)
        self.update()

    def _toggle_dark_mode(self):
        if self.schedule_display_mode != "timetable":
            return
        self.set_dark_mode(not self._dark_mode)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))

        painter.setPen(QPen(QColor(255, 255, 255, 110), 1))
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(rect, 12, 12)

        super().paintEvent(event)

    def set_panel_data(self, qdate, schedules):
        self.panel_date = qdate
        self._schedules = list(schedules or [])
        week_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        self.date_label.setText(
            f"{qdate.toString('yyyy-MM-dd')} {week_names[qdate.dayOfWeek() - 1]}"
        )

        self._clear_schedule_items()
        self.timetable_frame.hide()

        if not schedules:
            self.setFixedWidth(280)
            self.empty_label.show()
            self.body_scroll.hide()
            self.summary_label.hide()
            self.adjustSize()
            return

        self.empty_label.hide()

        if self.schedule_display_mode == "timetable":
            self.setFixedWidth(234)
            self.body_scroll.hide()
            self.timetable_frame.show()
            self.timetable_frame.set_dark_mode(self._dark_mode)
            self.timetable_frame.set_schedule_data(qdate, self._schedules)
            self.summary_label.setText(f"共 {len(self._schedules)} 条")
            self.summary_label.show()
            self.adjustSize()
            return

        self.setFixedWidth(280)
        self.body_scroll.show()

        visible_items = list(self._schedules)
        insert_at = self.body_layout.count() - 1
        for schedule in visible_items:
            self.body_layout.insertWidget(insert_at, self._build_schedule_item(schedule))
            insert_at += 1

        item_height = 30
        item_spacing = 4
        visible_height = len(visible_items) * item_height + max(len(visible_items) - 1, 0) * item_spacing
        self.body_scroll.setFixedHeight(min(visible_height + 2, 270))

        if len(schedules) > 8:
            self.summary_label.setText(f"... 共 {len(schedules)} 条")
        else:
            self.summary_label.setText(f"共 {len(schedules)} 条")
        self.summary_label.show()

        self.adjustSize()

    def set_schedule_display_mode(self, mode_id):
        if mode_id not in {"card", "timetable"}:
            return
        if self.schedule_display_mode == mode_id:
            return
        self.schedule_display_mode = mode_id
        if mode_id == "timetable":
            self.timetable_frame.set_dark_mode(self._dark_mode)
        self.set_panel_data(self.panel_date, self._schedules)

    def mouseDoubleClickEvent(self, event):
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.schedule_display_mode == "timetable"
        ):
            self._toggle_dark_mode()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def _clear_schedule_items(self):
        while self.body_layout.count() > 1:
            item = self.body_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _build_schedule_item(self, schedule):
        item_frame = _MonthScheduleItemFrame(schedule)
        item_frame.setObjectName("monthDayPanelItem")
        item_frame.setFixedHeight(30)
        item_frame.setStyleSheet(
            """
            QFrame#monthDayPanelItem {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.22);
                border-radius: 7px;
            }
            """
        )

        layout = QHBoxLayout(item_frame)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        time_label = QLabel(self._format_time_text(schedule))
        time_label.setFixedWidth(40)
        time_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        time_label.setStyleSheet(
            "background: transparent; border: none; color: white; "
            "font-family: 'Segoe UI'; font-size: 11px; font-weight: bold;"
        )
        layout.addWidget(time_label)

        title_label = _ElidedTitleLabel(self._format_title_text(schedule))
        title_label.setMinimumWidth(0)
        title_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        title_label.setWordWrap(False)
        title_label.setStyleSheet(
            "background: transparent; border: none; color: white; "
            "font-family: 'Microsoft YaHei'; font-size: 11px; font-weight: bold;"
        )
        layout.addWidget(title_label, 1)

        meta_label = QLabel(
            f"{self._format_priority_text(schedule)}/{self._format_status_text(schedule)}"
        )
        meta_label.setFixedWidth(66)
        meta_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        meta_label.setStyleSheet(
            "background: transparent; border: none; color: rgba(255, 255, 255, 0.84); "
            "font-family: 'Microsoft YaHei'; font-size: 10px;"
        )
        layout.addWidget(meta_label)

        item_frame.double_clicked.connect(self._emit_schedule_double_clicked)
        item_frame.status_change_requested.connect(self.schedule_status_requested.emit)
        return item_frame

    def _emit_schedule_double_clicked(self, schedule):
        self.schedule_double_clicked.emit(schedule, self)

    def _format_time_text(self, schedule):
        start_time = getattr(schedule, "start_time", None)
        end_time = getattr(schedule, "end_time", None)
        if start_time:
            return start_time.strftime("%H:%M")
        if end_time:
            return end_time.strftime("%H:%M")
        return "--:--"

    def _format_title_text(self, schedule):
        return getattr(schedule, "title", "") or "未命名日程"

    def _format_priority_text(self, schedule):
        priority = int(getattr(schedule, "priority", 0))
        return {2: "高", 1: "中", 0: "低"}.get(priority, "低")

    def _format_status_text(self, schedule):
        return "已完成" if getattr(schedule, "status", 0) == 1 else "未完成"

    def register_child_detail_popup(self, popup):
        if popup is None:
            return

        self._prune_child_detail_popups()
        if popup in self.child_detail_popups:
            return

        self.child_detail_popups.append(popup)

        if hasattr(popup, "popup_closed"):
            popup.popup_closed.connect(self._handle_child_popup_closed)
        popup.destroyed.connect(lambda *_: self._unregister_child_detail_popup(popup))

    def _handle_child_popup_closed(self, popup):
        self._unregister_child_detail_popup(popup)

    def _unregister_child_detail_popup(self, popup):
        self.child_detail_popups = [child for child in self.child_detail_popups if child is not popup]

    def _prune_child_detail_popups(self):
        valid_popups = []
        for popup in self.child_detail_popups:
            try:
                if popup is not None:
                    valid_popups.append(popup)
            except RuntimeError:
                continue
        self.child_detail_popups = valid_popups

    def closeEvent(self, event):
        self._close_child_detail_popups()
        if not self._closed_emitted:
            self._closed_emitted = True
            self.closed.emit(self)
        super().closeEvent(event)

    def _close_child_detail_popups(self):
        for popup in list(self.child_detail_popups):
            try:
                if popup is not None and hasattr(popup, "close"):
                    popup.close()
            except RuntimeError:
                pass
        self.child_detail_popups.clear()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
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
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = None
            event.accept()
            return
        super().mouseReleaseEvent(event)
