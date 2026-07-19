import colorsys
import datetime
import random

from PyQt6.QtWidgets import (
    QApplication,
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
from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF, QSize, QTimer, pyqtSignal
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
from ...utils.styles import StyleManager
from ...utils.timetable_preferences import (
    get_timetable_preferences,
    set_timetable_schedule_color,
)
from ...utils.window_preferences import (
    get_primary_pin_preference,
    set_window_pin_state,
)
from ..utils.icon_loader import load_colored_svg_pixmap
from ..components import get_colored_icon
from ...data.database import db_manager


class _MonthScheduleItemFrame(QFrame):
    double_clicked = pyqtSignal(object)
    status_change_requested = pyqtSignal(object, int)
    selection_toggled = pyqtSignal(int)

    def __init__(self, schedule, parent=None):
        super().__init__(parent)
        self.schedule = schedule
        self._multi_select_mode = False
        self._selected_for_batch = False

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.schedule)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if (
            self._multi_select_mode
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self.selection_toggled.emit(self.schedule.id)
            event.accept()
            return
        super().mousePressEvent(event)

    def set_multi_select_state(self, active, selected=False):
        self._multi_select_mode = bool(active)
        self._selected_for_batch = bool(selected) if active else False
        self._apply_multi_select_style()

    def _apply_multi_select_style(self):
        if not self._multi_select_mode:
            if hasattr(self, "_base_style"):
                self.setStyleSheet(self._base_style)
            else:
                self.setStyleSheet(
                    """
                    QFrame#monthDayPanelItem {
                        background: rgba(255, 255, 255, 0.15);
                        border: 1px solid rgba(255, 255, 255, 0.22);
                        border-radius: 7px;
                    }
                    """
                )
            return
        if self._selected_for_batch:
            self.setStyleSheet(
                "QFrame#monthDayPanelItem {"
                "background: rgba(255, 255, 255, 0.25);"
                "border: 1px solid white;"
                "border-radius: 7px;"
                "}"
            )
        else:
            if hasattr(self, "_base_style"):
                self.setStyleSheet(self._base_style)
            else:
                self.setStyleSheet(
                    """
                    QFrame#monthDayPanelItem {
                        background: rgba(255, 255, 255, 0.15);
                        border: 1px solid rgba(255, 255, 255, 0.22);
                        border-radius: 7px;
                    }
                    """
                )

    def contextMenuEvent(self, event):
        if self._multi_select_mode:
            return
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

    def setStrikeOut(self, strike):
        font = self.font()
        font.setStrikeOut(strike)
        self.setFont(font)

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
    schedule_time_changed = pyqtSignal(object, object, object)
    empty_area_context_requested = pyqtSignal(object)

    DAY_MINUTES = 24 * 60
    VISIBLE_HOURS = 6
    HOUR_ROW_HEIGHT = 42.0
    TIME_AXIS_WIDTH = 34.0
    DIVIDER_WIDTH = 1.0
    DDL_LINE_HEIGHT = 3.0
    EVENT_GAP = 2.0
    EVENT_BLOCK_COLUMN_GAP = 2.0
    EVENT_COLUMN_GAP = 1.0
    EVENT_RADIUS = 3.0
    EDIT_EDGE_HANDLE_PX = 10.0
    EDIT_SNAP_MINUTES = 1
    EDIT_MIN_DURATION_MINUTES = 5
    EDIT_AUTO_SCROLL_MARGIN_PX = 22.0
    EDIT_AUTO_SCROLL_STEP_MINUTES = 1
    EDIT_AUTO_SCROLL_INTERVAL_MS = 120
    SELECTION_COLOR = QColor("#FFD700")
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
        self.visible_minutes = self.VISIBLE_HOURS * 60
        preferences = get_timetable_preferences()
        self._schedule_colors = {}
        self._schedule_color_overrides = dict(
            preferences.get("schedule_colors", {})
        )
        self.edit_snap_minutes = self._normalize_edit_snap_minutes(
            preferences.get("drag_snap_minutes", self.EDIT_SNAP_MINUTES)
        )
        self._palette_order = list(self.EVENT_PALETTE)
        random.SystemRandom().shuffle(self._palette_order)
        self._next_color_index = 0
        self._hit_regions = []
        self._visible_event_labels = []
        self._visible_ddl_labels = []
        self._occupied_label_rects = []
        self._selected_interval_rects = []
        self._selected_ddl_rects = []
        self._selected_schedule_id = None
        self._pressed_schedule = None
        self._pending_time_edit = None
        self._active_time_edit = None
        self._last_time_edit_pos = None
        self._time_edit_hint = self._create_time_edit_hint()
        self.setMouseTracking(True)
        self.setStyleSheet("background: transparent; border: none;")
        self._time_edit_scroll_timer = QTimer(self)
        self._time_edit_scroll_timer.setInterval(
            self.EDIT_AUTO_SCROLL_INTERVAL_MS
        )
        self._time_edit_scroll_timer.timeout.connect(
            self._handle_time_edit_auto_scroll
        )

    def set_schedule_data(self, qdate, schedules):
        self.panel_date = qdate
        self.schedules = list(schedules or [])
        self._ensure_schedule_colors(self.schedules)
        if (
            self._selected_schedule_id is not None
            and self._selected_schedule_id
            not in {self._schedule_id(schedule) for schedule in self.schedules}
        ):
            self._selected_schedule_id = None
        self.visible_start_minutes, self.visible_minutes = self._initial_window()
        self.setFixedHeight(
            int(self.visible_minutes / 60.0 * self.HOUR_ROW_HEIGHT)
        )
        self.update()

    @staticmethod
    def _normalize_edit_snap_minutes(minutes):
        try:
            normalized = int(minutes)
        except (TypeError, ValueError):
            return 1
        return normalized if normalized in {1, 5} else 1

    def set_drag_snap_minutes(self, minutes):
        self.edit_snap_minutes = self._normalize_edit_snap_minutes(minutes)

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
        top, _ = self._content_bounds()
        earliest_hour = int(top // 60)
        start_hour = min(earliest_hour, 24 - self.VISIBLE_HOURS)
        return start_hour * 60, self.VISIBLE_HOURS * 60

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
            return {
                "fill": QColor(255, 255, 255, 238),
                "line": QColor(255, 255, 255, 245),
                "border": None,
                "text": self._color_for_schedule(schedule),
                "shadow": QColor(255, 255, 255, 0),
            }
        if self._is_expired(schedule):
            color = QColor(156, 166, 171, 218)
            return {
                "fill": color,
                "line": color,
                "border": None,
                "text": QColor(255, 255, 255, 238),
                "shadow": QColor(0, 0, 0, 95),
            }

        color = self._color_for_schedule(schedule)
        return {
            "fill": color,
            "line": color,
            "border": QColor(255, 255, 255, 245),
            "text": QColor(255, 255, 255, 238),
            "shadow": QColor(0, 0, 0, 95),
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

    @staticmethod
    def _schedule_id(schedule):
        return getattr(schedule, "id", None)

    def _is_schedule_selected(self, schedule):
        schedule_id = self._schedule_id(schedule)
        return (
            schedule_id is not None
            and schedule_id == self._selected_schedule_id
        )

    def _set_selected_schedule(self, schedule):
        selected_id = self._schedule_id(schedule)
        if selected_id != self._selected_schedule_id:
            self._selected_schedule_id = selected_id
            self.update()

    def _clear_selected_schedule(self):
        self._pending_time_edit = None
        self._active_time_edit = None
        self._last_time_edit_pos = None
        self._time_edit_scroll_timer.stop()
        self._hide_time_edit_hint()
        self.unsetCursor()
        if self._selected_schedule_id is not None:
            self._selected_schedule_id = None
            self.update()

    @staticmethod
    def _interval_times_for_edit(schedule):
        start_time = getattr(schedule, "start_time", None)
        end_time = getattr(schedule, "end_time", None)
        if start_time is None or end_time is None or start_time == end_time:
            return None, None
        if start_time > end_time:
            start_time, end_time = end_time, start_time
        return start_time, end_time

    @staticmethod
    def _point_time_for_edit(schedule):
        start_time = getattr(schedule, "start_time", None)
        end_time = getattr(schedule, "end_time", None)
        if (
            start_time is not None
            and end_time is not None
            and start_time != end_time
        ):
            return None
        return end_time if end_time is not None else start_time

    def _time_edit_action_for_region(self, region, position):
        if region is None:
            return None
        schedule = region.get("schedule")
        if not self._is_schedule_selected(schedule):
            return None
        if region.get("kind") == "ddl":
            return (
                "move_point"
                if self._point_time_for_edit(schedule) is not None
                else None
            )
        if region.get("kind") != "interval":
            return None

        start_time, end_time = self._interval_times_for_edit(schedule)
        if start_time is None or end_time is None:
            return None
        rect = region["rect"]
        if position.y() <= rect.top() + self.EDIT_EDGE_HANDLE_PX:
            return "resize_start"
        if position.y() >= rect.bottom() - self.EDIT_EDGE_HANDLE_PX:
            return "resize_end"
        return "move"

    def _set_cursor_for_time_edit_action(self, action):
        if action in {"resize_start", "resize_end"}:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif action in {"move", "move_point"}:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.unsetCursor()

    def _create_time_edit_hint(self):
        hint = QLabel()
        hint.setWindowFlags(
            Qt.WindowType.ToolTip
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        hint.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        hint.setStyleSheet(
            """
            QLabel {
                background: rgba(43, 43, 43, 235);
                color: white;
                border: 1px solid rgba(255, 255, 255, 220);
                border-radius: 6px;
                padding: 6px 8px;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
            }
            """
        )
        return hint

    def _hide_time_edit_hint(self):
        self._time_edit_hint.hide()

    @staticmethod
    def _format_time_edit_range(start_time, end_time):
        return f"{start_time:%H:%M} - {end_time:%H:%M}"

    def _show_time_edit_hint(self, edit_state, start_time, end_time, position):
        action_text = {
            "resize_start": f"开始 {start_time:%H:%M}",
            "resize_end": f"结束 {end_time:%H:%M}",
            "move": "移动日程",
            "move_point": f"移动到 {end_time:%H:%M}",
        }.get(edit_state.get("action"), "调整日程")
        detail_text = (
            end_time.strftime("%H:%M")
            if edit_state.get("action") == "move_point"
            else self._format_time_edit_range(start_time, end_time)
        )
        self._time_edit_hint.setText(f"{action_text}\n{detail_text}")
        self._time_edit_hint.adjustSize()

        global_pos = self.mapToGlobal(position.toPoint())
        target_x = self.window().frameGeometry().left() - self._time_edit_hint.width() - 8
        target_y = global_pos.y() - self._time_edit_hint.height() // 2
        screen = QApplication.screenAt(global_pos)
        if screen is not None:
            available = screen.availableGeometry()
            target_x = max(
                available.left() + 4,
                min(
                    target_x,
                    available.right() - self._time_edit_hint.width() - 4,
                ),
            )
            target_y = max(
                available.top() + 4,
                min(
                    target_y,
                    available.bottom() - self._time_edit_hint.height() - 4,
                ),
            )
        self._time_edit_hint.move(int(target_x), int(target_y))
        self._time_edit_hint.show()

    def _build_time_edit_state(self, region, position):
        action = self._time_edit_action_for_region(region, position)
        if action is None:
            return None
        schedule = region["schedule"]
        start_time = getattr(schedule, "start_time", None)
        end_time = getattr(schedule, "end_time", None)
        point_time = None
        if action == "move_point":
            point_time = self._point_time_for_edit(schedule)
            if point_time is None:
                return None
        else:
            start_time, end_time = self._interval_times_for_edit(schedule)
            if start_time is None or end_time is None:
                return None

        rect = region["rect"]
        return {
            "schedule": schedule,
            "action": action,
            "press_pos": QPointF(position),
            "locked_left": float(rect.left()),
            "locked_width": float(rect.width()),
            "original_start": start_time,
            "original_end": end_time,
            "original_point": point_time,
            "preview_start": start_time,
            "preview_end": end_time,
            "preview_point": point_time,
            "update_start_time": start_time is not None and (
                action != "move_point"
                or end_time is None
                or start_time == end_time
            ),
            "update_end_time": end_time is not None,
            "visible_start_minutes": self.visible_start_minutes,
            "changed": False,
        }

    def _snap_minutes(self, raw_minutes):
        snap = max(1, int(self.edit_snap_minutes))
        return int(round(raw_minutes / snap) * snap)

    def _snapped_delta_minutes(self, delta_pixels, scroll_delta_minutes=0.0):
        raw_minutes = (
            delta_pixels / self.HOUR_ROW_HEIGHT * 60.0
            + scroll_delta_minutes
        )
        return self._snap_minutes(raw_minutes)

    def _clamp_point_to_panel_day(self, value):
        day_start, day_end = self._day_bounds()
        latest = day_end - datetime.timedelta(minutes=self.edit_snap_minutes)
        return max(day_start, min(value, latest))

    def _clamp_moved_interval_to_panel_day(self, start_time, end_time):
        day_start, day_end = self._day_bounds()
        duration = end_time - start_time
        if duration >= day_end - day_start:
            return day_start, day_end
        if start_time < day_start:
            end_time += day_start - start_time
            start_time = day_start
        if end_time > day_end:
            start_time -= end_time - day_end
            end_time = day_end
        return start_time, end_time

    def _apply_time_edit_preview(self, edit_state, position):
        if edit_state is None:
            return

        schedule = edit_state["schedule"]
        scroll_delta = (
            self.visible_start_minutes - edit_state["visible_start_minutes"]
        )
        delta_minutes = self._snapped_delta_minutes(
            position.y() - edit_state["press_pos"].y(),
            scroll_delta,
        )
        delta = datetime.timedelta(minutes=delta_minutes)
        min_duration = datetime.timedelta(
            minutes=self.EDIT_MIN_DURATION_MINUTES
        )
        day_start, day_end = self._day_bounds()
        original_start = edit_state["original_start"]
        original_end = edit_state["original_end"]

        if edit_state["action"] == "move":
            next_start, next_end = self._clamp_moved_interval_to_panel_day(
                original_start + delta,
                original_end + delta,
            )
        elif edit_state["action"] == "move_point":
            next_point = self._clamp_point_to_panel_day(
                edit_state["original_point"] + delta
            )
            next_start = (
                next_point
                if edit_state["update_start_time"]
                else original_start
            )
            next_end = (
                next_point
                if edit_state["update_end_time"]
                else original_end
            )
            self._show_time_edit_hint(
                edit_state,
                next_point,
                next_point,
                position,
            )
            if next_point == edit_state["preview_point"]:
                return
            if edit_state["update_start_time"]:
                schedule.start_time = next_point
            if edit_state["update_end_time"]:
                schedule.end_time = next_point
            edit_state["preview_point"] = next_point
            edit_state["preview_start"] = next_start
            edit_state["preview_end"] = next_end
            edit_state["changed"] = True
            return
        elif edit_state["action"] == "resize_start":
            next_end = min(original_end, day_end)
            latest_start = next_end - min_duration
            next_start = max(day_start, min(original_start + delta, latest_start))
        elif edit_state["action"] == "resize_end":
            next_start = max(original_start, day_start)
            earliest_end = next_start + min_duration
            next_end = min(day_end, max(original_end + delta, earliest_end))
        else:
            return

        self._show_time_edit_hint(
            edit_state,
            next_start,
            next_end,
            position,
        )
        if (
            next_start == edit_state["preview_start"]
            and next_end == edit_state["preview_end"]
        ):
            return
        schedule.start_time = next_start
        schedule.end_time = next_end
        edit_state["preview_start"] = next_start
        edit_state["preview_end"] = next_end
        edit_state["changed"] = True

    def _time_edit_auto_scroll_direction(self, position):
        if position.y() < self.EDIT_AUTO_SCROLL_MARGIN_PX:
            return -1
        if position.y() > self.height() - self.EDIT_AUTO_SCROLL_MARGIN_PX:
            return 1
        return 0

    def _update_time_edit_auto_scroll(self, position):
        self._last_time_edit_pos = QPointF(position)
        if self._active_time_edit is None:
            self._time_edit_scroll_timer.stop()
            return
        if self._time_edit_auto_scroll_direction(position):
            if not self._time_edit_scroll_timer.isActive():
                self._time_edit_scroll_timer.start()
        else:
            self._time_edit_scroll_timer.stop()

    def _handle_time_edit_auto_scroll(self):
        if self._active_time_edit is None or self._last_time_edit_pos is None:
            self._time_edit_scroll_timer.stop()
            return
        direction = self._time_edit_auto_scroll_direction(
            self._last_time_edit_pos
        )
        if direction == 0:
            self._time_edit_scroll_timer.stop()
            return

        max_start = max(0, self.DAY_MINUTES - int(self.visible_minutes))
        next_start = min(
            max(
                self.visible_start_minutes
                + direction * self.EDIT_AUTO_SCROLL_STEP_MINUTES,
                0,
            ),
            max_start,
        )
        if next_start == self.visible_start_minutes:
            return
        self.visible_start_minutes = next_start
        self._apply_time_edit_preview(
            self._active_time_edit,
            self._last_time_edit_pos,
        )
        self.update()

    def _restore_time_edit_original(self, edit_state):
        if edit_state is None:
            return
        schedule = edit_state["schedule"]
        schedule.start_time = edit_state["original_start"]
        schedule.end_time = edit_state["original_end"]

    def _finish_time_edit(self, commit):
        edit_state = self._active_time_edit or self._pending_time_edit
        self._time_edit_scroll_timer.stop()
        self._hide_time_edit_hint()
        self._pending_time_edit = None
        self._active_time_edit = None
        self._last_time_edit_pos = None
        self._pressed_schedule = None
        self.unsetCursor()
        if edit_state is None:
            return
        if not commit or not edit_state.get("changed"):
            self._restore_time_edit_original(edit_state)
            self.update()
            return
        self.schedule_time_changed.emit(
            edit_state["schedule"],
            edit_state["preview_start"],
            edit_state["preview_end"],
        )

    def _maybe_activate_pending_time_edit(self, position):
        if self._pending_time_edit is None or self._active_time_edit is not None:
            return False
        drag_distance = (
            position - self._pending_time_edit["press_pos"]
        ).manhattanLength()
        if drag_distance < QApplication.startDragDistance():
            return False
        self._active_time_edit = self._pending_time_edit
        self._pending_time_edit = None
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        self._update_time_edit_auto_scroll(position)
        self._apply_time_edit_preview(self._active_time_edit, position)
        self.update()
        return True

    def _is_active_time_edit_schedule(self, schedule):
        return (
            self._active_time_edit is not None
            and self._active_time_edit.get("schedule") is schedule
        )

    def _minute_to_y(self, minute, visible_start, grid_top):
        return grid_top + (minute - visible_start) / 60.0 * self.HOUR_ROW_HEIGHT

    def _grid_rects(self):
        outer = QRectF(self.rect())
        axis_rect = QRectF(
            outer.left(),
            outer.top(),
            self.TIME_AXIS_WIDTH,
            outer.height(),
        )
        content_left = axis_rect.right() + self.DIVIDER_WIDTH
        content_rect = QRectF(
            content_left,
            outer.top(),
            max(1.0, outer.right() - content_left),
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

    def _draw_background(self, painter, outer, axis_rect):
        painter.save()
        line_color = QColor(222, 230, 234, 230)
        painter.fillRect(axis_rect, QColor(255, 255, 255, 64))
        painter.fillRect(
            QRectF(
                axis_rect.right(),
                outer.top(),
                self.DIVIDER_WIDTH,
                outer.height(),
            ),
            line_color,
        )
        painter.restore()

    def _draw_hour_grid(self, painter, outer, axis_rect, content_rect):
        visible_start = int(self.visible_start_minutes)
        visible_hours = int(self.visible_minutes // 60)
        painter.save()
        line_color = QColor(222, 230, 234, 230)
        text_color = QColor(
            StyleManager.mix_colors(
                AppConfig.COLOR_GRADIENT_START,
                AppConfig.COLOR_GRADIENT_END,
                0.5,
            )
        )
        font = QFont("Microsoft YaHei")
        font.setPixelSize(10)
        painter.setFont(font)
        metrics = QFontMetrics(font)
        for row in range(visible_hours + 1):
            y_value = content_rect.top() + row * self.HOUR_ROW_HEIGHT
            if row == 0:
                line_rect = QRectF(outer.left(), outer.top(), outer.width(), 1.0)
            elif row == visible_hours:
                line_rect = QRectF(
                    outer.left(),
                    max(outer.top(), outer.bottom() - 1.0),
                    outer.width(),
                    1.0,
                )
            else:
                line_rect = QRectF(
                    content_rect.left(),
                    y_value,
                    content_rect.width(),
                    1.0,
                )
            painter.fillRect(line_rect, line_color)
            hour_value = (visible_start // 60) + row
            if row < visible_hours and 0 <= hour_value < 24:
                label_rect = QRectF(
                    axis_rect.left(),
                    y_value + 3.0,
                    axis_rect.width(),
                    metrics.height(),
                )
                painter.setPen(text_color)
                painter.drawText(
                    label_rect,
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                    f"{hour_value:02d}:00",
                )
        painter.restore()

    def _draw_interval_items(self, painter, intervals, content_rect):
        visible_start = float(self.visible_start_minutes)
        ordered_intervals = sorted(
            intervals,
            key=lambda item: self._is_active_time_edit_schedule(
                item["schedule"]
            ),
        )
        for interval in ordered_intervals:
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
            if self._is_active_time_edit_schedule(interval["schedule"]):
                rect_x = self._active_time_edit["locked_left"]
                rect_width = self._active_time_edit["locked_width"]
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
            if self._is_schedule_selected(interval["schedule"]):
                self._selected_interval_rects.append(event_rect)
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
                line_width = segment_width
                if self._is_active_time_edit_schedule(
                    ddl_point["schedule"]
                ):
                    line_x = self._active_time_edit["locked_left"]
                    line_width = self._active_time_edit["locked_width"]
                line_rect = QRectF(
                    line_x,
                    line_y - self.DDL_LINE_HEIGHT / 2,
                    line_width,
                    self.DDL_LINE_HEIGHT,
                )
                display_style = self._display_style_for_schedule(ddl_point["schedule"])
                painter.fillRect(line_rect, display_style["line"])
                if self._is_schedule_selected(ddl_point["schedule"]):
                    self._selected_ddl_rects.append(line_rect)
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
            display_style = item["style"]
            painter.setFont(item["font"])
            if display_style["shadow"].alpha() > 0:
                painter.setPen(display_style["shadow"])
                painter.drawText(
                    item["rect"].translated(0.8, 0.8),
                    Qt.AlignmentFlag.AlignCenter,
                    item["text"],
                )
            painter.setPen(display_style["text"])
            painter.drawText(
                item["rect"],
                Qt.AlignmentFlag.AlignCenter,
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
        pen = QPen(QColor(AppConfig.COLOR_GRADIENT_END), 1)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setDashPattern([4, 4])
        painter.setPen(pen)
        painter.drawLine(
            QPointF(content_rect.left(), line_y),
            QPointF(content_rect.right(), line_y),
        )
        painter.restore()

    def _draw_selected_schedule_overlays(self, painter):
        if self._selected_schedule_id is None:
            return
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.SELECTION_COLOR, 2))
        for rect in self._selected_interval_rects:
            painter.drawRoundedRect(
                rect,
                self.EVENT_RADIUS,
                self.EVENT_RADIUS,
            )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.SELECTION_COLOR)
        for rect in self._selected_ddl_rects:
            painter.drawRect(rect)
        painter.restore()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        outer, axis_rect, content_rect = self._grid_rects()
        self._draw_background(painter, outer, axis_rect)

        self._hit_regions = []
        self._visible_event_labels = []
        self._visible_ddl_labels = []
        self._occupied_label_rects = []
        self._selected_interval_rects = []
        self._selected_ddl_rects = []
        intervals, ddl_points = self._visible_items()
        self._draw_interval_items(painter, intervals, content_rect)
        self._draw_ddl_items(painter, ddl_points, content_rect)
        self._draw_hour_grid(painter, outer, axis_rect, content_rect)
        self._draw_interval_labels(painter)
        self._draw_ddl_labels(painter)
        self._draw_selected_schedule_overlays(painter)
        self._draw_current_time_line(painter, content_rect)
        super().paintEvent(event)

    def mouseMoveEvent(self, event):
        if self._active_time_edit is not None:
            self._apply_time_edit_preview(
                self._active_time_edit,
                event.position(),
            )
            self._update_time_edit_auto_scroll(event.position())
            self.update()
            event.accept()
            return
        if self._maybe_activate_pending_time_edit(event.position()):
            event.accept()
            return

        region = self._schedule_region_at_position(event.position())
        action = self._time_edit_action_for_region(
            region,
            event.position(),
        )
        self._set_cursor_for_time_edit_action(action)
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pending_time_edit = None
            region = self._schedule_region_at_position(event.position())
            self._pressed_schedule = (
                region["schedule"] if region is not None else None
            )
            if self._pressed_schedule is not None:
                self._set_selected_schedule(self._pressed_schedule)
                self._pending_time_edit = self._build_time_edit_state(
                    region,
                    event.position(),
                )
                if self._pending_time_edit is not None:
                    self._set_cursor_for_time_edit_action(
                        self._pending_time_edit["action"]
                    )
                event.accept()
                return
            self._clear_selected_schedule()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._active_time_edit is not None:
                self._apply_time_edit_preview(
                    self._active_time_edit,
                    event.position(),
                )
                self._finish_time_edit(True)
                event.accept()
                return
            if self._pending_time_edit is not None:
                self._finish_time_edit(False)
                event.accept()
                return
            self._pressed_schedule = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._finish_time_edit(False)
            region = self._schedule_region_at_position(QPointF(event.pos()))
            if region is not None:
                self._set_selected_schedule(region["schedule"])
                self.schedule_double_clicked.emit(region["schedule"])
                event.accept()
                return
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        region = self._schedule_region_at_position(QPointF(event.pos()))
        if region is None:
            self._clear_selected_schedule()
            self.empty_area_context_requested.emit(event.globalPos())
            event.accept()
            return

        self._set_selected_schedule(region["schedule"])
        item_proxy = _MonthScheduleItemFrame(region["schedule"], self)
        item_proxy.status_change_requested.connect(self.status_change_requested.emit)
        menu = item_proxy._build_context_menu()
        menu.exec(event.globalPos())
        event.accept()

    def leaveEvent(self, event):
        if self._active_time_edit is None and self._pending_time_edit is None:
            self.unsetCursor()
        super().leaveEvent(event)

    def hideEvent(self, event):
        if self._active_time_edit is not None or self._pending_time_edit is not None:
            self._finish_time_edit(False)
        self._hide_time_edit_hint()
        super().hideEvent(event)


class MonthDayPanel(QWidget):
    closed = pyqtSignal(object)
    schedule_double_clicked = pyqtSignal(object, object)
    schedule_status_requested = pyqtSignal(object, int)
    schedule_time_changed = pyqtSignal(object, object, object)
    blank_context_requested = pyqtSignal(object, object, object)
    timetable_empty_context_requested = pyqtSignal(object, object)

    CORNER_RADIUS = 12
    PIN_ICON_SIZE = 14
    TIMETABLE_BOTTOM_CLEARANCE = 10
    TIMETABLE_FOOTER_HEIGHT = CORNER_RADIUS + TIMETABLE_BOTTOM_CLEARANCE

    def __init__(self, qdate, schedules, parent=None, initial_pinned=None):
        if initial_pinned is None:
            initial_pinned = get_primary_pin_preference()
        window_flags = Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
        if initial_pinned:
            window_flags |= Qt.WindowType.WindowStaysOnTopHint
        super().__init__(parent, window_flags)
        self.panel_date = qdate
        self._schedules = []
        self.is_pinned = bool(initial_pinned)
        self.schedule_display_mode = get_timetable_preferences().get(
            "display_mode",
            "card",
        )
        self._closed_emitted = False
        self._drag_offset = None
        self.child_detail_popups = []
        self._multi_select_active = False
        self._selected_schedule_ids = set()

        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedWidth(280)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(14, 12, 14, 12)
        self._layout.setSpacing(8)

        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(10)

        self.date_label = QLabel()
        self.date_label.setWordWrap(False)
        self.date_label.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei'; font-size: 14px; font-weight: bold;"
        )
        self.date_label.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.date_label.customContextMenuRequested.connect(
            lambda position: self._on_blank_context_menu(
                self.date_label,
                position,
            )
        )
        self.header_layout.addWidget(self.date_label, 1)

        self.header_actions_layout = QHBoxLayout()
        self.header_actions_layout.setContentsMargins(0, 0, 0, 0)
        self.header_actions_layout.setSpacing(2)

        self.btn_pin = QPushButton()
        self.btn_pin.setFixedSize(22, 22)
        self.btn_pin.setIconSize(
            QSize(self.PIN_ICON_SIZE, self.PIN_ICON_SIZE)
        )
        self.btn_pin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pin.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.18);
                border-radius: 11px;
            }
            """
        )
        self.btn_pin.clicked.connect(self._toggle_pin)
        self.header_actions_layout.addWidget(
            self.btn_pin,
            0,
            Qt.AlignmentFlag.AlignTop,
        )

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
        self.header_actions_layout.addWidget(
            self.btn_close,
            0,
            Qt.AlignmentFlag.AlignTop,
        )
        self.header_layout.addLayout(self.header_actions_layout)
        self._layout.addLayout(self.header_layout)

        self._create_multi_select_bar()
        self._layout.addWidget(self.multi_select_bar)
        self.multi_select_bar.hide()

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
        self.timetable_frame.schedule_time_changed.connect(
            self.schedule_time_changed.emit
        )
        self.timetable_frame.empty_area_context_requested.connect(
            lambda global_position: self.timetable_empty_context_requested.emit(
                self,
                global_position,
            )
        )

        self.timetable_summary_label = QLabel()
        self.timetable_summary_label.setFixedHeight(
            self.TIMETABLE_FOOTER_HEIGHT
        )
        self.timetable_summary_label.setContentsMargins(14, 0, 0, 0)
        self.timetable_summary_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.timetable_summary_label.setStyleSheet(
            "color: rgba(255, 255, 255, 0.74); font-family: 'Microsoft YaHei'; font-size: 8px;"
        )

        self.timetable_container = QWidget()
        self.timetable_container.setStyleSheet("background: transparent;")
        self.timetable_layout = QVBoxLayout(self.timetable_container)
        self.timetable_layout.setContentsMargins(0, 0, 0, 0)
        self.timetable_layout.setSpacing(0)
        self.timetable_layout.addWidget(self.timetable_frame)
        self.timetable_layout.addWidget(self.timetable_summary_label)
        self._layout.addWidget(self.timetable_container)
        self.timetable_container.hide()

        self.summary_label = QLabel()
        self.summary_label.setStyleSheet(
            "color: rgba(255, 255, 255, 0.78); font-family: 'Microsoft YaHei'; font-size: 11px;"
        )
        self.summary_label.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.summary_label.customContextMenuRequested.connect(
            lambda position: self._on_blank_context_menu(
                self.summary_label,
                position,
            )
        )
        self._layout.addWidget(self.summary_label)

        self._update_pin_button()
        self.set_panel_data(qdate, schedules)

    def _create_multi_select_bar(self):
        """内嵌多选操作栏：按键排列和设计与 ScheduleMultiSelectPopup 一致。"""
        self.multi_select_bar = QWidget(self)
        self.multi_select_bar.setFixedHeight(44)
        self.multi_select_bar.setStyleSheet(
            "QWidget { background: transparent; border-radius: 7px; }"
        )
        bar_layout = QHBoxLayout(self.multi_select_bar)
        bar_layout.setContentsMargins(10, 0, 10, 0)
        bar_layout.setSpacing(0)

        ACTIONS = (
            ("select_all", "Multiplechoice.svg", "全选 / 全不选"),
            ("complete", "finished.svg", "完成"),
            ("undo", "withdraw.svg", "撤销"),
            ("delete", "delete.svg", "删除"),
            ("exit", "exit.svg", "退出"),
        )
        self._ms_action_buttons = {}
        for action_index, (action_id, icon_name, tooltip) in enumerate(ACTIONS):
            button = QPushButton()
            button.setFixedSize(36, 36)
            button.setIconSize(QSize(18, 18))
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setToolTip(tooltip)
            button.clicked.connect(
                lambda _checked=False, value=action_id: (
                    self._handle_multi_select_action(value)
                )
            )
            self._ms_action_buttons[action_id] = button
            bar_layout.addWidget(button)
            if action_index < len(ACTIONS) - 1:
                bar_layout.addStretch(1)
            self._update_ms_action_button(button, icon_name, enabled=False)

    @staticmethod
    def _ms_button_bg_color():
        return StyleManager.mix_colors(
            AppConfig.COLOR_GRADIENT_START,
            AppConfig.COLOR_GRADIENT_END,
            0.5,
        )

    def _update_ms_action_button(self, button, icon_name, *, enabled):
        icon_color = "#FFFFFF" if enabled else "#8A8A8A"
        pixmap = get_colored_icon(icon_name, icon_color, 18)
        button.setIcon(
            QIcon(pixmap)
            if not pixmap.isNull()
            else QIcon(f"assets/icons/{icon_name}")
        )
        button.setEnabled(enabled)
        button.setStyleSheet(
            "QPushButton {"
            f"background: {self._ms_button_bg_color()};"
            "border: 1px solid rgba(255, 255, 255, 0.5); border-radius: 5px; padding: 0;"
            "}"
            "QPushButton:hover { background: rgba(255, 255, 255, 0.24); }"
            "QPushButton:pressed { background: rgba(0, 0, 0, 0.12); }"
            "QPushButton:disabled {"
            f"background: {self._ms_button_bg_color()};"
            "border: 1px solid rgba(255, 255, 255, 0.2);"
            "}"
        )

    def _ms_schedule_items(self):
        items = []
        for index in range(self.body_layout.count()):
            item = self.body_layout.itemAt(index)
            widget = item.widget() if item is not None else None
            if isinstance(widget, _MonthScheduleItemFrame):
                items.append(widget)
        return items

    def enter_multi_select_mode(self):
        if self.schedule_display_mode != "card" or not self._schedules:
            return
        self._multi_select_active = True
        self._selected_schedule_ids.clear()
        self.multi_select_bar.show()
        self._sync_multi_select_state()
        self.adjustSize()

    def exit_multi_select_mode(self):
        if not self._multi_select_active:
            return
        self._multi_select_active = False
        self._selected_schedule_ids.clear()
        self.multi_select_bar.hide()
        for item in self._ms_schedule_items():
            item.set_multi_select_state(False)
        self.adjustSize()

    def _toggle_item_selection(self, schedule_id):
        if not self._multi_select_active:
            return
        if schedule_id in self._selected_schedule_ids:
            self._selected_schedule_ids.remove(schedule_id)
        else:
            self._selected_schedule_ids.add(schedule_id)
        self._sync_multi_select_state()

    def _sync_multi_select_state(self):
        items = self._ms_schedule_items()
        visible_ids = {item.schedule.id for item in items}
        self._selected_schedule_ids.intersection_update(visible_ids)

        for item in items:
            item.set_multi_select_state(
                self._multi_select_active,
                item.schedule.id in self._selected_schedule_ids,
            )

        if not self._multi_select_active:
            return

        selected_items = [
            item for item in items
            if item.schedule.id in self._selected_schedule_ids
        ]
        has_selection = bool(selected_items)
        all_selected = bool(items) and len(selected_items) == len(items)
        can_complete = has_selection and any(
            getattr(item.schedule, "status", 0) != 1
            for item in selected_items
        )
        can_undo = has_selection and any(
            getattr(item.schedule, "status", 0) == 1
            for item in selected_items
        )

        self._update_ms_action_button(
            self._ms_action_buttons["select_all"],
            "all_no.svg" if all_selected else "Multiplechoice.svg",
            enabled=bool(items),
        )
        self._update_ms_action_button(
            self._ms_action_buttons["complete"],
            "finished.svg",
            enabled=can_complete,
        )
        self._update_ms_action_button(
            self._ms_action_buttons["undo"],
            "withdraw.svg",
            enabled=can_undo,
        )
        self._update_ms_action_button(
            self._ms_action_buttons["delete"],
            "delete.svg",
            enabled=has_selection,
        )
        self._update_ms_action_button(
            self._ms_action_buttons["exit"],
            "exit.svg",
            enabled=True,
        )

    def _handle_multi_select_action(self, action_id):
        if action_id == "exit":
            self.exit_multi_select_mode()
            return

        items = self._ms_schedule_items()
        visible_ids = {item.schedule.id for item in items}
        selected_ids = sorted(self._selected_schedule_ids & visible_ids)

        if action_id == "select_all":
            if items and len(selected_ids) == len(items):
                self._selected_schedule_ids.clear()
            else:
                self._selected_schedule_ids = set(visible_ids)
            self._sync_multi_select_state()
            return

        if not selected_ids:
            return

        if action_id == "complete":
            if not any(
                getattr(item.schedule, "status", 0) != 1
                for item in items
                if item.schedule.id in self._selected_schedule_ids
            ):
                return
            success = db_manager.update_schedule_statuses(selected_ids, 1)
            if success:
                for s in self._schedules:
                    if getattr(s, "id", None) in selected_ids:
                        s.status = 1
        elif action_id == "undo":
            if not any(
                getattr(item.schedule, "status", 0) == 1
                for item in items
                if item.schedule.id in self._selected_schedule_ids
            ):
                return
            success = db_manager.update_schedule_statuses(selected_ids, 0)
            if success:
                for s in self._schedules:
                    if getattr(s, "id", None) in selected_ids:
                        s.status = 0
        elif action_id == "delete":
            success = db_manager.delete_schedules(selected_ids)
            if success:
                self._selected_schedule_ids.clear()
                selected_id_set = set(selected_ids)
                self._schedules = [
                    s for s in self._schedules
                    if getattr(s, "id", None) not in selected_id_set
                ]
                for popup in list(self.child_detail_popups):
                    try:
                        if (
                            popup is not None
                            and getattr(getattr(popup, "data", None), "id", None)
                            in selected_ids
                        ):
                            popup.close()
                    except RuntimeError:
                        pass
        else:
            return

        if success:
            self.set_panel_data(self.panel_date, self._schedules)

    def _on_blank_context_menu(self, source, position):
        if self.schedule_display_mode != "card" or not self._schedules:
            return

        global_position = source.mapToGlobal(position)
        body_position = self.body_container.mapFromGlobal(global_position)
        child = self.body_container.childAt(body_position)
        current = child
        while current is not None and current is not self.body_container:
            if isinstance(current, _MonthScheduleItemFrame):
                return
            current = current.parentWidget()
        self.blank_context_requested.emit(self, self.panel_date, global_position)

    def _toggle_pin(self):
        self.set_pinned(not self.is_pinned)

    def set_pinned(self, enabled):
        self.is_pinned = bool(enabled)
        set_window_pin_state(self, self.is_pinned)
        self._update_pin_button()

    def _update_pin_button(self):
        pin_color = (
            QColor(255, 255, 255, 255)
            if self.is_pinned
            else QColor(255, 255, 255, 150)
        )
        pin_pixmap = load_colored_svg_pixmap(
            "assets/icons/pin.svg",
            pin_color,
            self.PIN_ICON_SIZE,
            self.PIN_ICON_SIZE,
            self.devicePixelRatioF(),
        )
        self.btn_pin.setIcon(QIcon(pin_pixmap))
        self.btn_pin.setToolTip(
            "取消窗口置顶" if self.is_pinned else "窗口置顶"
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))

        painter.setPen(QPen(QColor(255, 255, 255, 110), 1))
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(
            rect,
            self.CORNER_RADIUS,
            self.CORNER_RADIUS,
        )

        if (
            self.schedule_display_mode == "timetable"
            and self.timetable_container.isVisible()
        ):
            surface_top = self.timetable_frame.mapTo(self, QPoint(0, 0)).y()
            painter.fillRect(
                0,
                surface_top,
                self.width(),
                self.timetable_frame.height(),
                QColor(255, 255, 255, 153),
            )

        super().paintEvent(event)

    def set_panel_data(self, qdate, schedules):
        self.panel_date = qdate
        self._schedules = list(schedules or [])
        self.btn_pin.setVisible(True)
        week_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        self.date_label.setText(
            f"{qdate.toString('yyyy-MM-dd')} {week_names[qdate.dayOfWeek() - 1]}"
        )

        self._clear_schedule_items()
        self.timetable_container.hide()
        self.summary_label.hide()

        if not schedules:
            self._layout.setContentsMargins(14, 12, 14, 12)
            self.header_layout.setContentsMargins(0, 0, 0, 0)
            self.setFixedWidth(280)
            self.empty_label.show()
            self.body_scroll.hide()
            self.adjustSize()
            return

        self.empty_label.hide()

        if self.schedule_display_mode == "timetable":
            self._layout.setContentsMargins(0, 0, 0, 0)
            self.header_layout.setContentsMargins(14, 12, 14, 0)
            self.setFixedWidth(234)
            self.body_scroll.hide()
            self.timetable_frame.set_schedule_data(qdate, self._schedules)
            self.timetable_container.setFixedHeight(
                self.timetable_frame.height()
                + self.timetable_layout.spacing()
                + self.timetable_summary_label.height()
            )
            self.timetable_summary_label.setText(f"共 {len(self._schedules)} 条")
            self.timetable_container.show()
            self.adjustSize()
            return

        self._layout.setContentsMargins(14, 12, 14, 12)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
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

        if self._multi_select_active and not self._schedules:
            self.exit_multi_select_mode()
        elif self._multi_select_active:
            self._sync_multi_select_state()

    def set_schedule_display_mode(self, mode_id):
        if mode_id not in {"card", "timetable"}:
            return
        if self.schedule_display_mode == mode_id:
            return
        if mode_id != "card" and self._multi_select_active:
            self.exit_multi_select_mode()
        self.schedule_display_mode = mode_id
        self.set_panel_data(self.panel_date, self._schedules)

    def _clear_schedule_items(self):
        while self.body_layout.count() > 1:
            item = self.body_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _build_schedule_item(self, schedule):
        is_completed = int(getattr(schedule, "status", 0) or 0) == 1
        now = datetime.datetime.now()
        end_time = getattr(schedule, "end_time", None)
        is_expired = (
            not is_completed
            and end_time is not None
            and end_time < now
        )

        item_frame = _MonthScheduleItemFrame(schedule)
        item_frame.setObjectName("monthDayPanelItem")
        item_frame.setFixedHeight(30)

        if is_expired:
            bg = "rgba(190, 190, 190, 0.7)"
            border = "1px solid rgba(255, 255, 255, 0.22)"
        elif is_completed:
            bg = "rgba(255, 255, 255, 0.10)"
            border = "1px solid rgba(255, 255, 255, 0.22)"
        else:
            bg = "rgba(255, 255, 255, 0.15)"
            border = "1px solid rgba(255, 255, 255, 0.22)"
        item_frame.setStyleSheet(
            "QFrame#monthDayPanelItem {"
            f"background: {bg};"
            f"border: {border};"
            "border-radius: 7px;"
            "}"
        )
        item_frame._base_style = item_frame.styleSheet()

        layout = QHBoxLayout(item_frame)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        text_color = "rgba(255, 255, 255, 0.5)" if is_completed else "white"
        time_label = QLabel(self._format_time_text(schedule))
        time_label.setFixedWidth(40)
        time_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        time_label.setStyleSheet(
            f"background: transparent; border: none; color: {text_color}; "
            "font-family: 'Segoe UI'; font-size: 11px; font-weight: bold;"
        )
        layout.addWidget(time_label)

        title_label = _ElidedTitleLabel(self._format_title_text(schedule))
        title_label.setMinimumWidth(0)
        title_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        title_label.setWordWrap(False)
        title_label.setStyleSheet(
            f"background: transparent; border: none; color: {text_color}; "
            "font-family: 'Microsoft YaHei'; font-size: 11px; font-weight: bold;"
        )
        if is_completed:
            title_label.setStrikeOut(True)
        layout.addWidget(title_label, 1)

        meta_label = QLabel(
            f"{self._format_priority_text(schedule)}/{self._format_status_text(schedule)}"
        )
        meta_label.setFixedWidth(66)
        meta_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        meta_label.setStyleSheet(
            f"background: transparent; border: none; color: {text_color}; "
            "font-family: 'Microsoft YaHei'; font-size: 10px;"
        )
        layout.addWidget(meta_label)

        item_frame.double_clicked.connect(self._emit_schedule_double_clicked)
        item_frame.status_change_requested.connect(self.schedule_status_requested.emit)
        item_frame.selection_toggled.connect(self._toggle_item_selection)
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
