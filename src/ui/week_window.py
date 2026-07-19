# src/ui/week_window.py
#import requests
import colorsys
import random
import time
from types import SimpleNamespace

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QToolButton, QLineEdit, QSizePolicy, QStackedWidget, QScrollArea, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QTime, QTimer, QPointF, QRectF, QSize, QSettings, QEvent
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QBrush, QLinearGradient, QIcon, QPixmap, QCursor, QPen, QFont, QFontMetrics, QImage
from PyQt6.QtSvg import QSvgRenderer
from qframelesswindow import FramelessMainWindow
from zhdate import ZhDate
from datetime import datetime, timedelta

from ..config import AppConfig
from ..utils.win_api import apply_24h2_border_fix
from ..utils.styles import StyleManager
from ..utils.timetable_preferences import (
    get_timetable_preferences,
    set_timetable_drag_snap_minutes,
    set_timetable_schedule_color,
)
from ..utils.schedule_sort_preferences import (
    get_schedule_sort_options,
    set_schedule_sort_options,
)

# 引入主界面的添加与选择组件
from .add_view_week import AddScheduleViewWeek
from .time_picker_week import TimePickerViewWeek
from .alarm_picker_week import AlarmPickerViewWeek
from .list_picker import ListPickerView
from ..data.database import db_manager
from ..services.schedule_query_service import (
    ScheduleQueryService,
    WeekScheduleQueryOptions,
)
from ..services.schedule_sort_service import ScheduleSortOptions, ScheduleSortService
from .header import ToolTipFilter
from .dashboard import AdaptiveLabel 
from .components import CountdownToolTipFilter, get_colored_icon, get_padded_colored_icon
from .common.week_day_block import DayBlock
from .common.action_context_menu import ActionContextMenu
from .common.card_step_scroll_area import CardStepScrollArea
from .common.weather_icon_label import WeatherIconLabel
from .popups.schedule_multi_select_popup import ScheduleMultiSelectPopup
from .utils.window_drag_controller import WindowDragController


class WeekContentBorderOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._border_color = QColor(120, 120, 120, 72)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

    def set_border_color(self, color):
        self._border_color = QColor(color)
        self.update()

    def paintEvent(self, event):
        width = self.width()
        height = self.height()
        if width <= 1 or height <= 1:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        radius = 8.0
        left = 0.5
        right = width - 0.5
        bottom = height - 0.5
        path = QPainterPath()
        path.moveTo(left, 0.0)
        path.lineTo(left, bottom - radius)
        path.quadTo(left, bottom, left + radius, bottom)
        path.lineTo(right - radius, bottom)
        path.quadTo(right, bottom, right, bottom - radius)
        path.lineTo(right, 0.0)

        pen = QPen(self._border_color, 1)
        pen.setCosmetic(True)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(pen)
        painter.drawPath(path)


class WeekContentSurface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._background_color = QColor("#FFFFFF")
        self._border_color = QColor(120, 120, 120, 72)
        self._column_backgrounds = []
        self._border_overlay = WeekContentBorderOverlay(self)

    def set_surface_colors(self, background_color, border_color):
        self._background_color = QColor(background_color)
        self._border_color = QColor(border_color)
        self._border_overlay.set_border_color(self._border_color)
        self._border_overlay.raise_()
        self.update()

    def set_column_backgrounds(self, colors):
        self._column_backgrounds = [QColor(color) for color in colors]
        self._border_overlay.raise_()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        width = self.width()
        height = self.height()
        if width <= 1 or height <= 1:
            return

        radius = 8.0
        fill_path = QPainterPath()
        fill_path.moveTo(0.0, 0.0)
        fill_path.lineTo(width, 0.0)
        fill_path.lineTo(width, height - radius)
        fill_path.quadTo(width, height, width - radius, height)
        fill_path.lineTo(radius, height)
        fill_path.quadTo(0.0, height, 0.0, height - radius)
        fill_path.lineTo(0.0, 0.0)
        painter.fillPath(fill_path, self._background_color)

        if self._column_backgrounds:
            inner_left = 1.0
            inner_width = max(0.0, width - 2.0)
            inner_height = max(0.0, height - 1.0)
            column_width = inner_width / len(self._column_backgrounds)
            for index, color in enumerate(self._column_backgrounds):
                column_path = QPainterPath()
                column_path.addRect(
                    QRectF(
                        inner_left + index * column_width,
                        0.0,
                        column_width,
                        inner_height,
                    )
                )
                painter.fillPath(fill_path.intersected(column_path), color)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._border_overlay.setGeometry(self.rect())
        self._border_overlay.raise_()


class WeekScheduleCard(QFrame):
    """周视图中的单条日程小卡片"""
    CARD_HEIGHT = 46

    clicked = pyqtSignal(object)
    # 右键菜单需要的三个信号
    req_status = pyqtSignal(int, int) # id, status
    req_pin = pyqtSignal(int, bool)   # id, is_pinned
    req_delete = pyqtSignal(int)      # id
    drag_started = pyqtSignal(object)
    drag_finished = pyqtSignal(object, object)
    selection_toggled = pyqtSignal(int)

    def __init__(self, schedule_obj, parent=None):
        super().__init__(parent)
        self.setProperty("windowDragDisabled", True)
        self.data = schedule_obj
        self.schedule_obj = schedule_obj
        self._dark_mode = False
        self._multi_select_mode = False
        self._selected_for_batch = False

        self.setStyleSheet("""
            WeekScheduleCard {
                background-color: transparent;
                border: none;
                border-radius: 0px;
            }
            WeekScheduleCard:hover {
                background-color: rgba(0, 0, 0, 0.04);
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(self.CARD_HEIGHT)

        # 开启右键菜单策略
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(2)

        # --- 上半部分：圆点 + 标题 ---
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(4)

        # 优先级圆点
        self.dot = QWidget()
        self.dot.setFixedSize(8, 8)
        self.dot.installEventFilter(self)

        # 根据是否已完成动态调整标题和圆点样式
        self.lbl_title = AdaptiveLabel(schedule_obj.title, max_size=11, min_size=10)
        self._is_completed = getattr(self.schedule_obj, 'status', 0) == 1
        self._priority = schedule_obj.priority

        self._apply_card_style()

        top_layout.addWidget(self.dot)
        top_layout.addWidget(self.lbl_title, stretch=1)

        # 3. 排版防遮挡。如果置顶了，就强制给右上角留出 16px 空白；否则使用弹簧顶到最右侧
        is_pinned = getattr(self.schedule_obj, 'is_pinned', False)
        if is_pinned:
            top_layout.addSpacing(16)
        else:
            top_layout.addStretch()

        # --- 下半部分：时间 ---
        self.lbl_time = QLabel()
        self._apply_time_style()
        
        st = schedule_obj.start_time
        et = schedule_obj.end_time

        if st and et and st != et:
            self.lbl_time.setText(f"{st.strftime('%H:%M')} - {et.strftime('%H:%M')}")
        elif et:
            self.lbl_time.setText(f"{et.strftime('%H:%M')}")
        else:
            self.lbl_time.setText("未设置")

        layout.addLayout(top_layout)
        layout.addWidget(self.lbl_time)

        self._tooltip_filter = CountdownToolTipFilter(self.schedule_obj, self)
        self.installEventFilter(self._tooltip_filter)

        if is_pinned:
            self.icon_pin = QLabel(self)
            self.icon_pin.setFixedSize(16, 16)
            pixmap = get_colored_icon("week_top_color.svg", AppConfig.COLOR_GRADIENT_START, 16)
            self.icon_pin.setPixmap(pixmap)
            #self.icon_pin.setScaledContents(True)
            self.icon_pin.setStyleSheet("background: transparent;")

    def set_dark_mode(self, dark):
        """切换卡片暗色模式 — 更新标题/时间/悬停样式"""
        self._dark_mode = dark
        self._apply_card_style()
        self._apply_time_style()
        if dark:
            self.setStyleSheet("""
                WeekScheduleCard {
                    background-color: transparent;
                    border: none;
                    border-radius: 0px;
                }
                WeekScheduleCard:hover {
                    background-color: rgba(255, 255, 255, 0.06);
                }
            """)
        else:
            self.setStyleSheet("""
                WeekScheduleCard {
                    background-color: transparent;
                    border: none;
                    border-radius: 0px;
                }
                WeekScheduleCard:hover {
                    background-color: rgba(0, 0, 0, 0.04);
                }
            """)

    def _apply_card_style(self):
        """根据完成状态和暗色模式设置圆点+标题样式"""
        self._apply_dot_style()
        if self._is_completed:
            if self._dark_mode:
                self.lbl_title.setStyleSheet(
                    "color: rgba(255, 255, 255, 0.4); font-weight: bold; border: none; background: transparent;"
                )
            else:
                self.lbl_title.setStyleSheet(
                    "color: rgba(51, 51, 51, 0.5); font-weight: bold; border: none; background: transparent;"
                )
            self.lbl_title.setStrikeOut(True)
        else:
            if self._dark_mode:
                self.lbl_title.setStyleSheet(
                    "color: #FFFFFF; font-weight: bold; border: none; background: transparent;"
                )
            else:
                self.lbl_title.setStyleSheet(
                    "color: #333333; font-weight: bold; border: none; background: transparent;"
                )

    def _apply_dot_style(self):
        if self._multi_select_mode:
            dot_color = (
                StyleManager.color_to_rgba(
                    AppConfig.COLOR_GRADIENT_START,
                    0.65,
                )
                if self._selected_for_batch
                else "#FFFFFF"
            )
            border = "1px solid rgba(255, 255, 255, 0.8)"
        elif self._is_completed:
            dot_color = "#CCCCCC"
            border = "none"
        else:
            dot_color = {
                2: "#FF4D4F",
                1: "#FAAD14",
                0: "#52C41A",
            }.get(self._priority, "#52C41A")
            border = "none"
        self.dot.setStyleSheet(
            f"background-color: {dot_color}; border-radius: 4px; "
            f"border: {border};"
        )

    def set_multi_select_state(self, active, selected=False):
        self._multi_select_mode = bool(active)
        self._selected_for_batch = bool(selected) if active else False
        self.dot.setCursor(
            Qt.CursorShape.PointingHandCursor
            if self._multi_select_mode
            else Qt.CursorShape.ArrowCursor
        )
        self._apply_dot_style()

    def eventFilter(self, watched, event):
        if (
            watched is self.dot
            and self._multi_select_mode
            and event.type() == QEvent.Type.MouseButtonRelease
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self.selection_toggled.emit(self.data.id)
            return True
        return super().eventFilter(watched, event)

    def _apply_time_style(self):
        """根据暗色模式设置时间标签颜色"""
        if self._dark_mode:
            self.lbl_time.setStyleSheet(
                "color: #AAAAAA; padding-left: 10px; font-size: 9px; border: none; background: transparent;"
            )
        else:
            self.lbl_time.setStyleSheet(
                "color: #888888; padding-left: 10px; font-size: 9px; border: none; background: transparent;"
            )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._click_pos = event.pos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not hasattr(self, '_click_pos'): return
        if (event.pos() - self._click_pos).manhattanLength() > 10:
            from PyQt6.QtGui import QDrag
            from PyQt6.QtCore import QMimeData
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(str(self.data.id))
            drag.setMimeData(mime_data)
            
            drag.setPixmap(self.grab())
            drag.setHotSpot(event.pos())
            
            container = self.parentWidget()
            if hasattr(container, 'current_drag_widget'):
                container.current_drag_widget = self
            
            original_style = self.styleSheet()
            # 限制虚线样式只在当前卡片生效
            self.setStyleSheet("WeekScheduleCard { background: transparent; border: 2px dashed rgba(0, 0, 0, 0.3); border-radius: 0px; }")
            
            # 隐藏内部组件
            self.dot.hide()
            self.lbl_title.hide()
            self.lbl_time.hide()
            if hasattr(self, 'icon_pin'): self.icon_pin.hide()
            
            self.drag_started.emit(self)
            drag_result = drag.exec(Qt.DropAction.MoveAction)
            self.drag_finished.emit(self, drag_result)
            
            # 恢复样式和组件
            self.setStyleSheet(original_style)
            self.dot.show()
            self.lbl_title.show()
            self.lbl_time.show()
            if hasattr(self, 'icon_pin'): self.icon_pin.show()
            
            if hasattr(container, 'current_drag_widget'):
                container.current_drag_widget = None
            if hasattr(self, '_click_pos'): del self._click_pos
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and hasattr(self, '_click_pos'):
            if (
                not self._multi_select_mode
                and (event.pos() - self._click_pos).manhattanLength() < 5
            ):
                self.clicked.emit(self.schedule_obj)
            del self._click_pos
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if (
            self._multi_select_mode
            and event.button() == Qt.MouseButton.LeftButton
        ):
            if hasattr(self, '_click_pos'):
                del self._click_pos
            self.clicked.emit(self.schedule_obj)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'icon_pin'):
            # self.width() - 18 意味着图标右侧距离边缘保留 2px，上方距离 2px，这样在卡片上视觉最贴合
            self.icon_pin.move(self.width() - 18, 2)

    # 对接公用的菜单组件
    def _show_context_menu(self, pos):
        from .components import ScheduleContextMenu
        menu = ScheduleContextMenu(self.schedule_obj, self)
        menu.setup_actions(
            status_callback=lambda status: self.req_status.emit(self.schedule_obj.id, status),
            pin_callback=lambda is_pinned: self.req_pin.emit(self.schedule_obj.id, is_pinned),
            delete_callback=lambda: self.req_delete.emit(self.schedule_obj.id)
        )
        menu.exec(self.mapToGlobal(pos))


class WeekTimetableBoard(QFrame):
    schedule_clicked = pyqtSignal(object, object)
    schedule_context_requested = pyqtSignal(object, object)
    empty_area_context_requested = pyqtSignal(object)
    day_selected = pyqtSignal(QDate)
    schedule_time_changed = pyqtSignal(object, object, object)
    time_edit_week_turn_requested = pyqtSignal(int, int, int)

    DAY_COUNT = 7
    HOUR_ROWS = 7
    DAY_MINUTES = 24 * 60
    DDL_LINE_HEIGHT = 3.0
    EVENT_GAP = 2.0
    EVENT_COLUMN_GAP = 2.0
    EVENT_RADIUS = 3.0
    EDIT_EDGE_HANDLE_PX = 8.0
    EDIT_SNAP_MINUTES = 1
    EDIT_MIN_DURATION_MINUTES = 5
    EDIT_AUTO_SCROLL_MARGIN_PX = 22.0
    EDIT_AUTO_SCROLL_INTERVAL_MS = 650
    EDIT_WEEK_TURN_EDGE_PX = 28.0
    EDIT_WEEK_TURN_Y_TOLERANCE_PX = 30.0
    EDIT_WEEK_TURN_DELAY_SEC = 0.45
    EDIT_WEEK_TURN_INTERVAL_SEC = 0.7
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
        self.setProperty("windowDragDisabled", True)
        today = QDate.currentDate()
        self.current_monday = today.addDays(-(today.dayOfWeek() - 1))
        self.schedules_by_day = {day_index: [] for day_index in range(self.DAY_COUNT)}
        self.category_map = {}
        self._visible_start_hours = {}
        self._visible_hours_anchor = None
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
        self._dark_mode = False
        self._occupied_label_rects = []
        self._selected_interval_rects = []
        self._selected_ddl_rects = []
        self._selected_schedule_id = None
        self.selected_day_index = None
        self._hovered_schedule = None
        self._pressed_schedule = None
        self._pending_time_edit = None
        self._active_time_edit = None
        self._last_time_edit_pos = None
        self._time_edit_week_turn_direction = 0
        self._time_edit_week_turn_entered_at = 0.0
        self._time_edit_week_turn_last_at = 0.0
        self._hover_preview = None
        self._time_edit_hint = self._create_time_edit_hint()
        try:
            from .popups.schedule_axis_board import _AxisSchedulePreview

            self._hover_preview = _AxisSchedulePreview(False, outer_frame=False)
        except Exception:
            self._hover_preview = None
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setMouseTracking(True)
        self._time_edit_scroll_timer = QTimer(self)
        self._time_edit_scroll_timer.setInterval(self.EDIT_AUTO_SCROLL_INTERVAL_MS)
        self._time_edit_scroll_timer.timeout.connect(
            self._handle_time_edit_auto_scroll
        )
        self._time_edit_week_turn_timer = QTimer(self)
        self._time_edit_week_turn_timer.setInterval(80)
        self._time_edit_week_turn_timer.timeout.connect(
            self._handle_time_edit_week_turn
        )
        self.setStyleSheet("background: transparent; border: none;")

    def set_dark_mode(self, dark):
        """切换暗色模式并触发重绘"""
        self._dark_mode = dark
        self.update()

    def _default_visible_start_hour(self):
        return min(max(datetime.now().hour, 0), 23)

    def reset_to_current_time(self):
        self._reset_visible_start_hours()
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

    def set_visible_start_hour_for_day(self, day_index, hour):
        if not (0 <= int(day_index) < self.DAY_COUNT):
            return
        max_start_hour = max(0, 24 - self.HOUR_ROWS)
        try:
            normalized_hour = int(hour)
        except (TypeError, ValueError):
            normalized_hour = 0
        self._ensure_visible_start_hours()
        self._visible_start_hours[int(day_index)] = min(
            max(normalized_hour, 0),
            max_start_hour,
        )
        self.update()

    def set_week_data(self, current_monday, schedules_by_day, category_map=None):
        self.current_monday = current_monday
        self.category_map = dict(category_map or {})
        self._ensure_visible_start_hours()
        self.schedules_by_day = {
            day_index: list((schedules_by_day or {}).get(day_index, []))
            for day_index in range(self.DAY_COUNT)
        }
        all_schedules = [
            schedule
            for schedules in self.schedules_by_day.values()
            for schedule in schedules
        ]
        self._ensure_schedule_colors(all_schedules)
        active_schedule_id = (
            self._schedule_id(self._active_time_edit.get("schedule"))
            if self._active_time_edit is not None
            else None
        )
        if (
            self._selected_schedule_id is not None
            and self._selected_schedule_id
            not in {self._schedule_id(schedule) for schedule in all_schedules}
            and self._selected_schedule_id != active_schedule_id
        ):
            self._selected_schedule_id = None
        self.update()

    def set_selected_day(self, qdate):
        if qdate is None:
            self.selected_day_index = None
            self.update()
            return
        monday = self.current_monday.toPyDate()
        target = qdate.toPyDate() if hasattr(qdate, "toPyDate") else qdate
        day_index = (target - monday).days
        if 0 <= day_index < self.DAY_COUNT:
            self.selected_day_index = day_index
        else:
            self.selected_day_index = None
        self.update()

    def _visible_anchor(self):
        return (
            self.current_monday.toPyDate(),
            QDate.currentDate().toPyDate(),
        )

    def _reset_visible_start_hours(self):
        today = QDate.currentDate()
        default_today_hour = min(
            self._default_visible_start_hour(),
            max(0, 24 - self.HOUR_ROWS),
        )
        self._visible_start_hours = {}
        for day_index in range(self.DAY_COUNT):
            iter_date = self.current_monday.addDays(day_index)
            self._visible_start_hours[day_index] = (
                default_today_hour if iter_date == today else 0
            )
        self._visible_hours_anchor = self._visible_anchor()

    def _ensure_visible_start_hours(self):
        if self._visible_hours_anchor != self._visible_anchor():
            self._reset_visible_start_hours()

    def _visible_start_hour_for_day(self, day_index):
        self._ensure_visible_start_hours()
        return self._visible_start_hours.get(day_index, 0)

    def _day_index_at_x(self, x):
        width = max(1.0, float(self.width()))
        day_width = width / self.DAY_COUNT
        return min(max(int(float(x) / day_width), 0), self.DAY_COUNT - 1)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta == 0:
            event.ignore()
            return

        day_index = self._day_index_at_x(event.position().x())
        step = -1 if delta > 0 else 1
        max_start_hour = max(0, 24 - self.HOUR_ROWS)
        current_hour = self._visible_start_hour_for_day(day_index)
        next_hour = min(max(current_hour + step, 0), max_start_hour)
        if next_hour != current_hour:
            self._visible_start_hours[day_index] = next_hour
            self._hide_hover_preview()
            self.update()
        event.accept()

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

    def set_schedule_color(self, schedule, color):
        schedule_id = getattr(schedule, "id", None)
        if schedule_id is None:
            return QColor()

        color_obj = QColor(color)
        if not color_obj.isValid():
            return QColor()

        stored_color = color_obj.name()
        display_color = QColor(stored_color)
        display_color.setAlpha(218)
        self._schedule_color_overrides[str(schedule_id)] = stored_color
        self._schedule_colors[schedule_id] = display_color
        self.update()
        return QColor(display_color)

    @staticmethod
    def _is_completed(schedule):
        return int(getattr(schedule, "status", 0) or 0) == 1

    @staticmethod
    def _is_expired(schedule):
        if WeekTimetableBoard._is_completed(schedule):
            return False
        end_time = getattr(schedule, "end_time", None)
        return bool(end_time and end_time < datetime.now())

    @staticmethod
    def _is_active_now(schedule):
        if WeekTimetableBoard._is_completed(schedule) or WeekTimetableBoard._is_expired(schedule):
            return False
        start_time = getattr(schedule, "start_time", None)
        end_time = getattr(schedule, "end_time", None)
        if start_time is None or end_time is None or start_time == end_time:
            return False
        if start_time > end_time:
            start_time, end_time = end_time, start_time
        now = datetime.now()
        return start_time <= now <= end_time

    def _text_color_for_schedule(self, schedule):
        if self._is_completed(schedule):
            color = QColor(self._color_for_schedule(schedule))
            color.setAlpha(230)
            return color
        return QColor(255, 255, 255, 235)

    @staticmethod
    def _format_schedule_time_text(schedule):
        start_time = getattr(schedule, "start_time", None)
        end_time = getattr(schedule, "end_time", None)
        if start_time and end_time and start_time != end_time:
            return f"{start_time:%H:%M}", f"{end_time:%H:%M}"
        target_time = end_time or start_time
        if target_time:
            return None, f"{target_time:%H:%M}"
        return None, None

    def _display_style_for_schedule(self, schedule):
        if self._is_completed(schedule):
            if self._dark_mode:
                return {
                    "fill": QColor(58, 58, 58, 230),
                    "line": QColor(80, 80, 80, 230),
                    "border": QColor(100, 100, 100, 180),
                }
            return {
                "fill": QColor(255, 255, 255, 238),
                "line": QColor(255, 255, 255, 245),
                "border": QColor(170, 184, 192, 210),
            }
        if self._is_expired(schedule):
            color = QColor(156, 166, 171, 218)
            return {
                "fill": color,
                "line": color,
                "border": None,
            }

        color = self._color_for_schedule(schedule)
        return {
            "fill": color,
            "line": color,
            "border": QColor(255, 255, 255, 245),
        }

    @staticmethod
    def _schedule_id(schedule):
        return getattr(schedule, "id", None)

    def _is_schedule_selected(self, schedule):
        schedule_id = self._schedule_id(schedule)
        return schedule_id is not None and schedule_id == self._selected_schedule_id

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
        self._reset_time_edit_week_turn_state()
        self._hide_time_edit_hint()
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
        if start_time is not None and end_time is not None and start_time != end_time:
            return None
        point_time = end_time if end_time is not None else start_time
        if point_time is None:
            return None
        return point_time

    def _schedule_region_at_position(self, position):
        for region in reversed(self._hit_regions):
            if region["rect"].contains(position):
                return region
        return None

    def _day_start_datetime(self, day_index):
        day_date = self.current_monday.addDays(day_index).toPyDate()
        return datetime.combine(day_date, datetime.min.time())

    def _board_metrics(self):
        board_rect = QRectF(0.0, 0.0, float(self.width()), float(self.height()))
        day_width = board_rect.width() / max(1, self.DAY_COUNT)
        row_height = board_rect.height() / max(1, self.HOUR_ROWS)
        return board_rect, day_width, row_height

    def _minutes_at_position(self, day_index, position):
        _, _, row_height = self._board_metrics()
        y_value = max(0.0, min(float(self.height()), float(position.y())))
        visible_start = self._visible_start_hour_for_day(day_index) * 60
        minutes = visible_start + y_value / max(1.0, row_height) * 60.0
        return max(0.0, min(float(self.DAY_MINUTES), minutes))

    def _datetime_for_day_minutes(self, day_index, minutes):
        return self._day_start_datetime(day_index) + timedelta(minutes=minutes)

    def _time_edit_action_for_region(self, region, position):
        if region is None:
            return None
        schedule = region.get("schedule")
        if not self._is_schedule_selected(schedule):
            return None
        if region.get("kind") == "ddl":
            return "move_point" if self._point_time_for_edit(schedule) is not None else None
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
        if self._time_edit_hint is not None:
            self._time_edit_hint.hide()

    @staticmethod
    def _format_time_edit_point(date_time):
        return f"{date_time:%m-%d %H:%M}"

    @staticmethod
    def _format_time_edit_range(start_time, end_time):
        return f"{start_time:%m-%d %H:%M} - {end_time:%m-%d %H:%M}"

    def _show_time_edit_hint(self, edit_state, start_time, end_time, position):
        if self._time_edit_hint is None:
            return
        action_text = {
            "resize_start": f"开始 {start_time:%m-%d %H:%M}",
            "resize_end": f"结束 {end_time:%m-%d %H:%M}",
            "move": f"移动到 {start_time:%m-%d %H:%M}",
        }.get(edit_state.get("action"), "调整日程")
        self._time_edit_hint.setText(
            f"{action_text}\n{self._format_time_edit_range(start_time, end_time)}"
        )
        self._time_edit_hint.adjustSize()
        if edit_state.get("action") == "move_point":
            self._time_edit_hint.setText(
                f"移动到 {self._format_time_edit_point(end_time)}\n{end_time:%H:%M}"
            )
            self._time_edit_hint.adjustSize()

        global_pos = self.mapToGlobal(position.toPoint())
        window_left = self.window().frameGeometry().left()
        target_x = window_left - self._time_edit_hint.width() - 8
        target_y = global_pos.y() - self._time_edit_hint.height() // 2

        screen = QApplication.screenAt(global_pos)
        if screen is not None:
            available = screen.availableGeometry()
            target_x = max(
                available.left() + 4,
                min(target_x, available.right() - self._time_edit_hint.width() - 4),
            )
            target_y = max(
                available.top() + 4,
                min(target_y, available.bottom() - self._time_edit_hint.height() - 4),
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
            interval_start, interval_end = self._interval_times_for_edit(schedule)
            if interval_start is None or interval_end is None:
                return None
            start_time = interval_start
            end_time = interval_end

        day_index = int(region.get("day_index", self._day_index_at_x(position.x())))
        board_rect, day_width, _ = self._board_metrics()
        day_left = board_rect.left() + day_index * day_width
        press_offset = 0.0
        if action != "move_point":
            press_time = self._datetime_for_day_minutes(
                day_index,
                self._minutes_at_position(day_index, position),
            )
            press_offset = (press_time - start_time).total_seconds() / 60.0
        rect = region["rect"]
        return {
            "schedule": schedule,
            "action": action,
            "press_pos": QPointF(position),
            "original_day_index": day_index,
            "preview_day_index": day_index,
            "locked_inset": float(rect.left() - day_left),
            "locked_width": float(rect.width()),
            "press_offset_minutes": press_offset,
            "original_start": start_time,
            "original_end": end_time,
            "original_point": point_time,
            "preview_start": start_time,
            "preview_end": end_time,
            "preview_point": point_time,
            "update_start_time": start_time is not None and (
                action != "move_point" or end_time is None or start_time == end_time
            ),
            "update_end_time": end_time is not None,
            "changed": False,
        }

    def _snap_minutes(self, raw_minutes):
        snap = max(1, int(getattr(self, "edit_snap_minutes", self.EDIT_SNAP_MINUTES)))
        return int(round(raw_minutes / snap) * snap)

    def _apply_time_edit_preview(self, edit_state, position):
        if edit_state is None:
            return

        schedule = edit_state["schedule"]
        min_duration = timedelta(minutes=self.EDIT_MIN_DURATION_MINUTES)
        original_start = edit_state["original_start"]
        original_end = edit_state["original_end"]

        if edit_state["action"] == "move":
            duration = original_end - original_start
            target_day = self._day_index_at_x(position.x())
            target_minutes = self._minutes_at_position(target_day, position)
            next_start_minutes = self._snap_minutes(
                target_minutes - edit_state["press_offset_minutes"]
            )
            next_start_minutes = max(
                0,
                min(self.DAY_MINUTES - 1, next_start_minutes),
            )
            next_start = self._datetime_for_day_minutes(
                target_day,
                next_start_minutes,
            )
            next_end = next_start + duration
            edit_state["preview_day_index"] = target_day
            self.selected_day_index = target_day
        elif edit_state["action"] == "move_point":
            target_day = self._day_index_at_x(position.x())
            next_point_minutes = self._snap_minutes(
                self._minutes_at_position(target_day, position)
            )
            next_point_minutes = max(
                0,
                min(self.DAY_MINUTES - 1, next_point_minutes),
            )
            next_point = self._datetime_for_day_minutes(target_day, next_point_minutes)
            next_start = next_point if edit_state["update_start_time"] else original_start
            next_end = next_point if edit_state["update_end_time"] else original_end
            edit_state["preview_day_index"] = target_day
            self.selected_day_index = target_day
            self._show_time_edit_hint(edit_state, next_point, next_point, position)
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
            day_index = edit_state["original_day_index"]
            next_start_minutes = self._snap_minutes(
                self._minutes_at_position(day_index, position)
            )
            next_start = self._datetime_for_day_minutes(day_index, next_start_minutes)
            next_end = original_end
            if next_end - next_start < min_duration:
                next_start = next_end - min_duration
            edit_state["preview_day_index"] = day_index
            self.selected_day_index = day_index
        elif edit_state["action"] == "resize_end":
            day_index = edit_state["original_day_index"]
            next_start = original_start
            next_end_minutes = self._snap_minutes(
                self._minutes_at_position(day_index, position)
            )
            next_end = self._datetime_for_day_minutes(day_index, next_end_minutes)
            if next_end - next_start < min_duration:
                next_end = next_start + min_duration
            edit_state["preview_day_index"] = day_index
            self.selected_day_index = day_index
        else:
            return

        self._show_time_edit_hint(edit_state, next_start, next_end, position)

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

    def _time_edit_auto_scroll_day(self, position):
        if self._active_time_edit is None:
            return None
        if self._active_time_edit.get("action") in {"move", "move_point"}:
            return self._day_index_at_x(position.x())
        return self._active_time_edit.get("original_day_index")

    def _time_edit_auto_scroll_direction(self, position):
        if position.y() < self.EDIT_AUTO_SCROLL_MARGIN_PX:
            return -1
        if position.y() > self.height() - self.EDIT_AUTO_SCROLL_MARGIN_PX:
            return 1
        return 0

    def _reset_time_edit_week_turn_state(self, stop_timer=True):
        self._time_edit_week_turn_direction = 0
        self._time_edit_week_turn_entered_at = 0.0
        self._time_edit_week_turn_last_at = 0.0
        if stop_timer:
            self._time_edit_week_turn_timer.stop()

    def _time_edit_week_turn_direction_at(self, position):
        if self._active_time_edit is None:
            return 0
        if self._active_time_edit.get("action") not in {"move", "move_point"}:
            return 0
        if (
            position.y() < -self.EDIT_WEEK_TURN_Y_TOLERANCE_PX
            or position.y() > self.height() + self.EDIT_WEEK_TURN_Y_TOLERANCE_PX
        ):
            return 0
        if position.x() <= self.EDIT_WEEK_TURN_EDGE_PX:
            return -1
        if position.x() >= self.width() - self.EDIT_WEEK_TURN_EDGE_PX:
            return 1
        return 0

    def _update_time_edit_week_turn(self, position):
        direction = self._time_edit_week_turn_direction_at(position)
        now = time.monotonic()
        if direction != self._time_edit_week_turn_direction:
            self._time_edit_week_turn_direction = direction
            self._time_edit_week_turn_entered_at = now if direction else 0.0
            self._time_edit_week_turn_last_at = 0.0
            if direction:
                if not self._time_edit_week_turn_timer.isActive():
                    self._time_edit_week_turn_timer.start()
            else:
                self._time_edit_week_turn_timer.stop()
            return

        if direction and not self._time_edit_week_turn_timer.isActive():
            self._time_edit_week_turn_timer.start()

    def _update_time_edit_auto_scroll(self, position):
        self._last_time_edit_pos = QPointF(position)
        if self._active_time_edit is None:
            self._time_edit_scroll_timer.stop()
            self._reset_time_edit_week_turn_state()
            return
        self._update_time_edit_week_turn(position)
        if self._time_edit_auto_scroll_direction(position):
            if not self._time_edit_scroll_timer.isActive():
                self._time_edit_scroll_timer.start()
        else:
            self._time_edit_scroll_timer.stop()

    def _handle_time_edit_auto_scroll(self):
        if self._active_time_edit is None or self._last_time_edit_pos is None:
            self._time_edit_scroll_timer.stop()
            return
        direction = self._time_edit_auto_scroll_direction(self._last_time_edit_pos)
        day_index = self._time_edit_auto_scroll_day(self._last_time_edit_pos)
        if direction == 0 or day_index is None or not (0 <= day_index < self.DAY_COUNT):
            self._time_edit_scroll_timer.stop()
            return

        max_start_hour = max(0, 24 - self.HOUR_ROWS)
        current_hour = self._visible_start_hour_for_day(day_index)
        next_hour = min(max(current_hour + direction, 0), max_start_hour)
        if next_hour == current_hour:
            return
        self._visible_start_hours[day_index] = next_hour
        self._apply_time_edit_preview(
            self._active_time_edit,
            self._last_time_edit_pos,
        )
        self.update()

    def _handle_time_edit_week_turn(self):
        if self._active_time_edit is None or self._last_time_edit_pos is None:
            self._reset_time_edit_week_turn_state()
            return

        direction = self._time_edit_week_turn_direction_at(self._last_time_edit_pos)
        if direction == 0:
            self._reset_time_edit_week_turn_state()
            return

        now = time.monotonic()
        if direction != self._time_edit_week_turn_direction:
            self._time_edit_week_turn_direction = direction
            self._time_edit_week_turn_entered_at = now
            self._time_edit_week_turn_last_at = 0.0
            return
        if now - self._time_edit_week_turn_entered_at < self.EDIT_WEEK_TURN_DELAY_SEC:
            return
        if (
            self._time_edit_week_turn_last_at
            and now - self._time_edit_week_turn_last_at < self.EDIT_WEEK_TURN_INTERVAL_SEC
        ):
            return

        day_index = self._time_edit_auto_scroll_day(self._last_time_edit_pos)
        if day_index is None or not (0 <= day_index < self.DAY_COUNT):
            return
        visible_start_hour = self._visible_start_hour_for_day(day_index)
        self._time_edit_week_turn_last_at = now
        self._time_edit_week_turn_entered_at = now
        self.time_edit_week_turn_requested.emit(
            direction,
            int(day_index),
            int(visible_start_hour),
        )
        if self._active_time_edit is not None:
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
        self._reset_time_edit_week_turn_state()
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

    def _maybe_activate_pending_time_edit(self, position, buttons=Qt.MouseButton.NoButton):
        if self._pending_time_edit is None or self._active_time_edit is not None:
            return False
        if not (buttons & Qt.MouseButton.LeftButton):
            self._finish_time_edit(False)
            return False
        drag_distance = (
            position - self._pending_time_edit["press_pos"]
        ).manhattanLength()
        if drag_distance < QApplication.startDragDistance():
            return False

        self._active_time_edit = self._pending_time_edit
        self._pending_time_edit = None
        self._hide_hover_preview()
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

    def _datetime_value(self, value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if hasattr(value, "toPyDateTime"):
            return value.toPyDateTime()
        return None

    def _minutes_from_day_start(self, date_time, day_start):
        return (date_time - day_start).total_seconds() / 60.0

    def _build_day_items(self, day_index, visible_start, visible_end):
        day_date = self.current_monday.addDays(day_index).toPyDate()
        day_start = datetime.combine(day_date, datetime.min.time())
        intervals = []
        ddl_points = []

        active_schedule = (
            self._active_time_edit.get("schedule")
            if self._active_time_edit is not None
            else None
        )
        active_day_index = (
            self._active_time_edit.get("preview_day_index")
            if self._active_time_edit is not None
            else None
        )
        day_schedules = [
            schedule
            for schedule in self.schedules_by_day.get(day_index, [])
            if schedule is not active_schedule
        ]
        if active_schedule is not None and active_day_index == day_index:
            day_schedules.append(active_schedule)

        for schedule in day_schedules:
            if getattr(schedule, "status", 0) == 2:
                continue
            if ScheduleQueryService.is_todo(schedule):
                continue

            start_time = self._datetime_value(getattr(schedule, "start_time", None))
            end_time = self._datetime_value(getattr(schedule, "end_time", None))

            if start_time and end_time and start_time != end_time:
                if start_time > end_time:
                    start_time, end_time = end_time, start_time
                start_minutes = max(0.0, self._minutes_from_day_start(start_time, day_start))
                end_minutes = min(float(self.DAY_MINUTES), self._minutes_from_day_start(end_time, day_start))
                if end_minutes <= 0 or start_minutes >= self.DAY_MINUTES or end_minutes <= start_minutes:
                    continue
                intervals.append(
                    {
                        "schedule": schedule,
                        "start": start_minutes,
                        "end": end_minutes,
                        "visible_start": max(start_minutes, visible_start),
                        "visible_end": min(end_minutes, visible_end),
                    }
                )
                continue

            point_time = end_time or start_time
            if point_time is None:
                continue
            point_minutes = self._minutes_from_day_start(point_time, day_start)
            if visible_start <= point_minutes <= visible_end:
                ddl_points.append(
                    {
                        "schedule": schedule,
                        "point": point_minutes,
                    }
                )

        visible_intervals = [
            interval
            for interval in self._layout_interval_groups(intervals)
            if interval["visible_end"] > visible_start
            and interval["visible_start"] < visible_end
        ]
        return visible_intervals, ddl_points

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

    def _minute_to_y(self, minute_value, visible_start, top, row_height):
        return top + ((minute_value - visible_start) / 60.0) * row_height

    def _draw_interval_items(self, painter, intervals, visible_start, top, bottom, day_left, day_width, row_height, day_index):
        ordered_intervals = sorted(
            intervals,
            key=lambda item: self._is_active_time_edit_schedule(item["schedule"]),
        )
        for interval in ordered_intervals:
            column_count = interval["column_count"]
            available_width = max(
                1.0,
                day_width - self.EVENT_COLUMN_GAP * (column_count + 1),
            )
            rect_width = max(1.0, available_width / column_count)
            rect_x = day_left + self.EVENT_COLUMN_GAP + interval["column"] * (
                rect_width + self.EVENT_COLUMN_GAP
            )
            if self._is_active_time_edit_schedule(interval["schedule"]):
                rect_x = day_left + self._active_time_edit["locked_inset"]
                rect_width = self._active_time_edit["locked_width"]
            rect_y = self._minute_to_y(interval["visible_start"], visible_start, top, row_height)
            rect_bottom = self._minute_to_y(interval["visible_end"], visible_start, top, row_height)
            rect_y = max(top + self.EVENT_GAP, rect_y + self.EVENT_GAP)
            rect_bottom = min(bottom - self.EVENT_GAP, rect_bottom - self.EVENT_GAP)
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
                    "day_index": day_index,
                }
            )
            self._occupied_label_rects.append(event_rect)
            self._visible_event_labels.append(
                {
                    "rect": event_rect,
                    "schedule": interval["schedule"],
                }
            )

    def _wrap_title_lines(self, title, available_width, font_metrics):
        """将标题按宽度折行，返回行列表"""
        if not title:
            return []
        lines = []
        current_line = ""
        for ch in title:
            test = current_line + ch
            if font_metrics.horizontalAdvance(test) <= available_width:
                current_line = test
            else:
                if current_line:
                    lines.append(current_line)
                current_line = ch
        if current_line:
            lines.append(current_line)
        return lines

    def _draw_interval_labels(self, painter):
        if not self._visible_event_labels:
            return

        title_font = painter.font()
        title_font.setFamily("Microsoft YaHei")
        title_font.setPixelSize(10)
        title_font.setBold(True)
        time_font = QFont(title_font)
        time_font.setPixelSize(8)
        time_font.setBold(False)
        title_metrics = QFontMetrics(title_font)
        time_metrics = QFontMetrics(time_font)
        title_line_height = title_metrics.height()
        time_height = time_metrics.height()
        gap = 1

        for item in self._visible_event_labels:
            rect = item["rect"]
            schedule = item["schedule"]
            start_label, end_label = self._format_schedule_time_text(schedule)
            text_color = self._text_color_for_schedule(schedule)

            padded = rect.adjusted(3.0, 1.0, -3.0, -1.0)
            if padded.width() < 22:
                continue

            # 时间标签固定占用高度
            time_total = 0.0
            if start_label:
                time_total += time_height + gap
            if end_label:
                time_total += time_height + gap
            if time_total > 0:
                time_total -= gap  # 去掉最后一个 gap

            title_available_height = padded.height() - time_total
            if title_available_height < 0:
                # 空间连时间都放不下，什么都不显示
                continue

            has_time = start_label or end_label
            max_title_lines = max(0, int(title_available_height / (title_line_height + gap)))

            # 绘制时间标签
            painter.setPen(text_color)
            if start_label:
                painter.setFont(time_font)
                painter.drawText(
                    QRectF(padded.left(), padded.top(), padded.width(), time_height),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                    start_label,
                )
            if end_label:
                painter.setFont(time_font)
                painter.drawText(
                    QRectF(padded.left(), padded.bottom() - time_height, padded.width(), time_height),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                    end_label,
                )

            if max_title_lines <= 0:
                # 空间只够显示时间，不显示标题
                continue

            title = str(getattr(schedule, "title", None) or "未命名日程")
            all_wrapped = self._wrap_title_lines(title, padded.width(), title_metrics)
            needed_lines = len(all_wrapped)
            text_cap = min(max_title_lines, 3)

            # 计算标题可用区域的顶部
            title_top = padded.top()
            if start_label:
                title_top += time_height + gap
            title_area_height = title_available_height

            painter.setFont(title_font)

            if needed_lines <= text_cap:
                # 标题完整放得下，居中绘制
                total_text_height = needed_lines * (title_line_height + gap) - gap
                start_y = title_top + (title_area_height - total_text_height) / 2.0
                for i, line in enumerate(all_wrapped[:text_cap]):
                    line_y = start_y + i * (title_line_height + gap)
                    elided = title_metrics.elidedText(
                        line, Qt.TextElideMode.ElideRight, max(1, int(padded.width()))
                    )
                    painter.drawText(
                        QRectF(padded.left(), line_y, padded.width(), title_line_height),
                        Qt.AlignmentFlag.AlignCenter,
                        elided,
                    )
            else:
                # 放不下，需要截断
                display_lines = min(max_title_lines, 4)  # 最多用 4 行（3 正文 + 1 省略号）
                if display_lines == 1:
                    # 1 行：首字 + ...
                    short = title[0] + "..."
                    elided = title_metrics.elidedText(
                        short, Qt.TextElideMode.ElideRight, max(1, int(padded.width()))
                    )
                    line_y = title_top + (title_area_height - title_line_height) / 2.0
                    painter.drawText(
                        QRectF(padded.left(), line_y, padded.width(), title_line_height),
                        Qt.AlignmentFlag.AlignCenter,
                        elided,
                    )
                else:
                    # 前 N-1 行放正文，最后一行放 "..."
                    text_lines_count = display_lines - 1
                    total_text_height = display_lines * (title_line_height + gap) - gap
                    start_y = title_top + (title_area_height - total_text_height) / 2.0
                    for i in range(text_lines_count):
                        line_y = start_y + i * (title_line_height + gap)
                        line_text = all_wrapped[i] if i < len(all_wrapped) else ""
                        elided = title_metrics.elidedText(
                            line_text, Qt.TextElideMode.ElideRight, max(1, int(padded.width()))
                        )
                        painter.drawText(
                            QRectF(padded.left(), line_y, padded.width(), title_line_height),
                            Qt.AlignmentFlag.AlignCenter,
                            elided,
                        )
                    # 省略号行
                    ellipsis_y = start_y + text_lines_count * (title_line_height + gap)
                    painter.drawText(
                        QRectF(padded.left(), ellipsis_y, padded.width(), title_line_height),
                        Qt.AlignmentFlag.AlignCenter,
                        "...",
                    )

    def _draw_ddl_items(self, painter, ddl_points, visible_start, top, day_left, day_width, row_height, day_index):
        if not ddl_points:
            return

        grouped_points = {}
        for point in ddl_points:
            grouped_points.setdefault(round(point["point"], 2), []).append(point)

        for same_time_points in grouped_points.values():
            same_time_points.sort(key=lambda item: getattr(item["schedule"], "id", 0))
            count = len(same_time_points)
            available_width = max(
                1.0,
                day_width - self.EVENT_COLUMN_GAP * (count + 1),
            )
            line_width = max(1.0, available_width / count)
            for index, point in enumerate(same_time_points):
                line_x = day_left + self.EVENT_COLUMN_GAP + index * (
                    line_width + self.EVENT_COLUMN_GAP
                )
                if self._is_active_time_edit_schedule(point["schedule"]):
                    line_x = day_left + self._active_time_edit["locked_inset"]
                    line_width = self._active_time_edit["locked_width"]
                line_y = self._minute_to_y(point["point"], visible_start, top, row_height)
                line_rect = QRectF(
                    line_x,
                    line_y - self.DDL_LINE_HEIGHT / 2,
                    line_width,
                    self.DDL_LINE_HEIGHT,
                )
                painter.fillRect(line_rect, self._display_style_for_schedule(point["schedule"])["line"])
                if self._is_schedule_selected(point["schedule"]):
                    self._selected_ddl_rects.append(line_rect)
                self._hit_regions.append(
                    {
                        "rect": line_rect.adjusted(0.0, -4.0, 0.0, 4.0),
                        "schedule": point["schedule"],
                        "kind": "ddl",
                        "day_index": day_index,
                    }
                )
                # 收集 DDL 时间标签
                _, time_label = self._format_schedule_time_text(point["schedule"])
                if time_label and line_width >= 22:
                    self._visible_ddl_labels.append(
                        {
                            "rect": line_rect,
                            "time_label": time_label,
                            "schedule": point["schedule"],
                        }
                    )

    def _draw_ddl_labels(self, painter):
        if not self._visible_ddl_labels:
            return

        font = painter.font()
        font.setFamily("Microsoft YaHei")
        font.setPixelSize(8)
        font.setBold(False)
        metrics = QFontMetrics(font)
        label_height = metrics.height()

        for item in self._visible_ddl_labels:
            line_rect = item["rect"]
            if line_rect.width() < 22:
                continue

            label_bottom = line_rect.top() - 2.0
            label_top = label_bottom - label_height
            label_rect = QRectF(
                line_rect.left(),
                label_top,
                line_rect.width(),
                label_height,
            )

            # 避免与日程块重叠
            overlaps = False
            for occupied in self._occupied_label_rects:
                if label_rect.adjusted(-1.0, -1.0, 1.0, 1.0).intersects(occupied):
                    overlaps = True
                    break
            if overlaps:
                continue

            painter.save()
            painter.setFont(font)
            if self._dark_mode:
                painter.setPen(QColor(190, 190, 190))
            else:
                painter.setPen(QColor(140, 140, 140))
            elided = metrics.elidedText(
                item["time_label"],
                Qt.TextElideMode.ElideRight,
                max(1, int(label_rect.width())),
            )
            painter.drawText(
                label_rect,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                elided,
            )
            painter.restore()

    def _draw_hour_labels_for_selected_day(self, painter, board_rect, day_width, row_height):
        """仅在选中的日列绘制整时标签（主题上沿色，自动随主题切换），避开日程块"""
        if self.selected_day_index is None:
            return
        day_index = self.selected_day_index
        if not (0 <= day_index < self.DAY_COUNT):
            return

        visible_start_hour = self._visible_start_hour_for_day(day_index)
        day_left = board_rect.left() + day_index * day_width

        painter.save()
        font = painter.font()
        font.setFamily("Microsoft YaHei")
        font.setPixelSize(9)
        painter.setFont(font)
        if self._dark_mode:
            hour_color = QColor(255, 255, 255, 210)
        else:
            hour_color = QColor(AppConfig.COLOR_GRADIENT_START)
            hour_color = hour_color.lighter(155)
            hour_color.setAlpha(210)
        painter.setPen(hour_color)
        metrics = QFontMetrics(font)
        label_height = metrics.height()

        for row_index in range(self.HOUR_ROWS):
            hour_value = visible_start_hour + row_index
            if hour_value >= 24:
                continue

            cell_top = board_rect.top() + row_index * row_height
            # 标签放在每格左上角
            label_rect = QRectF(
                day_left + 4.0,
                cell_top + 2.0,
                day_width - 6.0,
                label_height,
            )

            # 检查是否与任何已占用区域重叠
            overlaps = False
            for occupied in self._occupied_label_rects:
                if label_rect.adjusted(-2.0, -2.0, 2.0, 2.0).intersects(occupied):
                    overlaps = True
                    break
            if overlaps:
                continue

            painter.drawText(
                label_rect,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                f"{hour_value:02d}:00",
            )
        painter.restore()

    def _draw_day_schedules(self, painter, board_rect, day_index, day_width, row_height):
        day_left = board_rect.left() + day_index * day_width
        visible_start = float(self._visible_start_hour_for_day(day_index) * 60)
        visible_end = visible_start + self.HOUR_ROWS * 60.0
        intervals, ddl_points = self._build_day_items(day_index, visible_start, visible_end)
        self._draw_interval_items(
            painter,
            intervals,
            visible_start,
            board_rect.top(),
            board_rect.bottom(),
            day_left,
            day_width,
            row_height,
            day_index,
        )
        self._draw_ddl_items(
            painter,
            ddl_points,
            visible_start,
            board_rect.top(),
            day_left,
            day_width,
            row_height,
            day_index,
        )

    def _draw_current_time_line(self, painter, board_rect, day_width, row_height):
        today = QDate.currentDate()
        day_index = self.current_monday.daysTo(today)
        if day_index < 0 or day_index >= self.DAY_COUNT:
            return

        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute + now.second / 60.0
        visible_start = float(self._visible_start_hour_for_day(day_index) * 60)
        visible_end = visible_start + self.HOUR_ROWS * 60.0
        if current_minutes < visible_start or current_minutes > visible_end:
            return

        line_y = board_rect.top() + (
            (current_minutes - visible_start) / 60.0
        ) * row_height
        day_left = board_rect.left() + day_index * day_width
        day_right = day_left + day_width

        painter.save()
        if self._dark_mode:
            line_color = QColor(200, 200, 200, 200)
        else:
            line_color = QColor(120, 120, 120, 200)
        pen = QPen(line_color, 1)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setDashPattern([4, 4])
        painter.setPen(pen)
        painter.drawLine(
            int(round(day_left)),
            int(round(line_y)),
            int(round(day_right)),
            int(round(line_y)),
        )
        painter.restore()

    def _draw_selected_schedule_overlays(self, painter):
        if not self._selected_interval_rects and not self._selected_ddl_rects:
            return
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.SELECTION_COLOR, 2))
        for rect in self._selected_interval_rects:
            painter.drawRoundedRect(rect, self.EVENT_RADIUS, self.EVENT_RADIUS)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.SELECTION_COLOR)
        for rect in self._selected_ddl_rects:
            painter.drawRect(rect)
        painter.restore()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        width = self.width()
        height = self.height()
        if width <= 0 or height <= 0:
            return

        board_rect = QRectF(0.0, 0.0, float(width), float(height))
        radius = 7.0
        board_clip_path = QPainterPath()
        board_clip_path.moveTo(board_rect.left(), board_rect.top())
        board_clip_path.lineTo(board_rect.right(), board_rect.top())
        board_clip_path.lineTo(board_rect.right(), board_rect.bottom() - radius)
        board_clip_path.quadTo(
            board_rect.right(),
            board_rect.bottom(),
            board_rect.right() - radius,
            board_rect.bottom(),
        )
        board_clip_path.lineTo(board_rect.left() + radius, board_rect.bottom())
        board_clip_path.quadTo(
            board_rect.left(),
            board_rect.bottom(),
            board_rect.left(),
            board_rect.bottom() - radius,
        )
        board_clip_path.closeSubpath()
        day_width = board_rect.width() / self.DAY_COUNT
        row_height = board_rect.height() / self.HOUR_ROWS

        # 选中日列高亮（暗色模式用白色半透明，亮色用黑色半透明）
        if self.selected_day_index is not None and 0 <= self.selected_day_index < self.DAY_COUNT:
            highlight_rect = QRectF(
                board_rect.left() + self.selected_day_index * day_width,
                0.0,
                day_width,
                float(height),
            )
            painter.save()
            painter.setPen(Qt.PenStyle.NoPen)
            highlight_path = QPainterPath()
            highlight_path.addRect(highlight_rect)
            if self._dark_mode:
                painter.fillPath(
                    board_clip_path.intersected(highlight_path),
                    QColor(255, 255, 255, 18),
                )
            else:
                painter.fillPath(
                    board_clip_path.intersected(highlight_path),
                    QColor(0, 0, 0, 15),
                )
            painter.restore()

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setClipPath(board_clip_path)
        self._hit_regions = []
        self._visible_event_labels = []
        self._visible_ddl_labels = []
        self._occupied_label_rects = []
        self._selected_interval_rects = []
        self._selected_ddl_rects = []
        for day_index in range(self.DAY_COUNT):
            self._draw_day_schedules(
                painter,
                board_rect,
                day_index,
                day_width,
                row_height,
            )
        # 在日程块上绘制文字标签
        self._draw_interval_labels(painter)
        # 在 DDL 线段上方绘制时间
        self._draw_ddl_labels(painter)
        painter.restore()
        self._draw_current_time_line(painter, board_rect, day_width, row_height)
        self._draw_selected_schedule_overlays(painter)

        # 空日程占位文字
        days_with_content = set()
        for region in self._hit_regions:
            day_idx = int(region["rect"].left() / day_width)
            if 0 <= day_idx < self.DAY_COUNT:
                days_with_content.add(day_idx)

        empty_font = painter.font()
        empty_font.setFamily("Microsoft YaHei")
        empty_font.setPixelSize(11)
        painter.save()
        painter.setFont(empty_font)
        if self._dark_mode:
            painter.setPen(QColor(220, 220, 220))
        else:
            painter.setPen(QColor(185, 185, 185))
        for day_index in range(self.DAY_COUNT):
            if day_index in days_with_content:
                continue
            cell_rect = QRectF(
                board_rect.left() + day_index * day_width,
                0.0,
                day_width,
                float(height),
            )
            painter.drawText(
                cell_rect,
                Qt.AlignmentFlag.AlignCenter,
                "空日程",
            )
        painter.restore()

        # 选中日列显示白色整时标签
        self._draw_hour_labels_for_selected_day(
            painter, board_rect, day_width, row_height
        )

    def _projection_for_schedule(self, schedule):
        category = self.category_map.get(getattr(schedule, "category_id", None))
        category_name = getattr(category, "name", None) or "未分类"
        importance = max(0, min(int(getattr(schedule, "priority", 0) or 0), 2))
        return SimpleNamespace(
            schedule=schedule,
            category_name=category_name,
            importance=importance,
        )

    def _hide_hover_preview(self):
        self._hovered_schedule = None
        if self._hover_preview is not None:
            self._hover_preview.hide()

    def _schedule_at_position(self, position):
        region = self._schedule_region_at_position(position)
        return region["schedule"] if region is not None else None

    def mouseMoveEvent(self, event):
        if self._active_time_edit is not None:
            self._apply_time_edit_preview(self._active_time_edit, event.position())
            self._update_time_edit_auto_scroll(event.position())
            self.update()
            event.accept()
            return

        if self._maybe_activate_pending_time_edit(event.position(), event.buttons()):
            event.accept()
            return

        region = self._schedule_region_at_position(event.position())
        action = self._time_edit_action_for_region(region, event.position())
        self._set_cursor_for_time_edit_action(action)
        schedule = region["schedule"] if region is not None else None
        if schedule is None:
            self._hide_hover_preview()
            super().mouseMoveEvent(event)
            return

        if self._hover_preview is not None:
            if schedule is not self._hovered_schedule:
                self._hovered_schedule = schedule
                self._hover_preview.set_projection(
                    self._projection_for_schedule(schedule)
                )
            self._hover_preview.show_near(event.globalPosition().toPoint())
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pending_time_edit = None
            region = self._schedule_region_at_position(event.position())
            self._pressed_schedule = region["schedule"] if region is not None else None
            if self._pressed_schedule is not None:
                self._set_selected_schedule(self._pressed_schedule)
                self.selected_day_index = int(
                    region.get("day_index", self._day_index_at_x(event.position().x()))
                )
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
            day_index = self._day_index_at_x(event.position().x())
            if 0 <= day_index < self.DAY_COUNT:
                self._clear_selected_schedule()
                self.selected_day_index = day_index
                selected_date = self.current_monday.addDays(day_index)
                self.day_selected.emit(selected_date)
                self.update()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._active_time_edit is not None:
                self._apply_time_edit_preview(self._active_time_edit, event.position())
                self._finish_time_edit(True)
                event.accept()
                return
            if self._pending_time_edit is not None:
                self._finish_time_edit(False)
                event.accept()
                return
            released_schedule = self._schedule_at_position(event.position())
            if (
                released_schedule is not None
                and released_schedule is self._pressed_schedule
            ):
                self._pressed_schedule = None
                event.accept()
                return
            self._pressed_schedule = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._finish_time_edit(False)
            schedule = self._schedule_at_position(event.position())
            if schedule is not None:
                self._set_selected_schedule(schedule)
                self._hide_hover_preview()
                self.schedule_clicked.emit(
                    schedule,
                    self._color_for_schedule(schedule),
                )
                event.accept()
                return
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        region = self._schedule_region_at_position(QPointF(event.pos()))
        if region is None:
            self.empty_area_context_requested.emit(event.globalPos())
            event.accept()
            return

        schedule = region["schedule"]
        self._hide_hover_preview()
        self._set_selected_schedule(schedule)
        self.selected_day_index = int(
            region.get("day_index", self._day_index_at_x(event.pos().x()))
        )
        self.schedule_context_requested.emit(schedule, event.globalPos())
        event.accept()

    def leaveEvent(self, event):
        if self._active_time_edit is not None or self._pending_time_edit is not None:
            super().leaveEvent(event)
            return
        self._pressed_schedule = None
        self._hide_hover_preview()
        super().leaveEvent(event)

    def hideEvent(self, event):
        if self._active_time_edit is not None or self._pending_time_edit is not None:
            self._finish_time_edit(False)
        self._hide_time_edit_hint()
        super().hideEvent(event)


from .todo import TodoListContainer
from ..utils.window_preferences import get_primary_pin_preference
class WeekWindow(FramelessMainWindow):
    """
    680x400 独立周视图窗口 (去线极简版)
    """
    restore_requested = pyqtSignal()
    suspend_requested = pyqtSignal()
    request_schedule_detail = pyqtSignal(object)
    request_timetable_schedule_detail = pyqtSignal(object, object)
    view_selected = pyqtSignal(str)
    schedule_updated = pyqtSignal(object)
    day_double_clicked = pyqtSignal(QDate)
    schedule_display_mode_requested = pyqtSignal(str)

    def set_schedule_display_mode(self, mode_id):
        self.schedule_display_mode_requested.emit(mode_id)

    def apply_schedule_display_mode(self, mode_id):
        if mode_id not in {"card", "timetable"}:
            return
        if mode_id != "card" and self._week_multi_select_active:
            self.exit_week_multi_select_mode()
        self.schedule_display_mode = mode_id
        self._sync_schedule_display_mode_ui()

    def __init__(self):
        super().__init__()
        self.setFixedSize(680, 414) 
        window_flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        if get_primary_pin_preference():
            window_flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(window_flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.titleBar.hide()

        self.current_selected_date = QDate.currentDate()
        self.current_monday = self._get_monday(self.current_selected_date)
        self._active_drag_card = None
        self._drag_edge_direction = 0
        self.schedule_display_mode = "card"
        self._filter_options = WeekScheduleQueryOptions()
        self._search_options = None
        self._search_keyword = ""
        self._last_search_scope = "title"
        self._last_match_mode = "fuzzy"
        self._sort_options = get_schedule_sort_options("week")
        self._search_options_panel = None
        self._filter_options_panel = None
        self._sort_options_panel = None
        self._week_multi_select_active = False
        self._week_multi_select_days = set(range(7))
        self._week_selected_schedule_ids = set()
        self._week_multi_select_popup = None
        self._drag_edge_entered_at = 0.0
        self._drag_last_turn_at = 0.0
        self._drag_edge_timer = QTimer(self)
        self._drag_edge_timer.setInterval(60)
        self._drag_edge_timer.timeout.connect(self._check_drag_week_edge)
        # 编辑模式状态位，控制背景渲染！
        self.is_edit_mode = False
        # 暗色模式
        self._dark_mode = QSettings("Lankor", "DesktopSchedule").value(
            "week/dark_mode", False, type=bool
        )

        self._setup_ui()
        self._apply_dark_mode()  # 应用初始暗色模式状态
        self._window_drag_controller = WindowDragController(
            self,
            drag_started=self._on_window_drag_started,
        )
        self._start_clock()
        self.refresh_week_data()
        #self._start_weather_fetch()
        current_style = self.styleSheet()
        self.setStyleSheet(current_style + StyleManager.get_tooltip_style())
        apply_24h2_border_fix(int(self.winId()))

    def _setup_ui(self):
        self.central_widget = QWidget(self)
        self.central_widget.setStyleSheet(StyleManager.get_tooltip_style())
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==========================================
        # 1. 顶部区域整体
        # ==========================================
        self.top_container = QWidget()
        self.top_container.setObjectName("week_top_surface")
        self.top_container.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.top_container.customContextMenuRequested.connect(
            self._show_week_header_context_menu
        )
        self.top_container.setStyleSheet("""
            QWidget#week_top_surface {
                background: transparent;
                border-top: 1px solid rgba(120, 120, 120, 72);
                border-left: 1px solid rgba(120, 120, 120, 72);
                border-right: 1px solid rgba(120, 120, 120, 72);
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """)
        self.top_container.setFixedHeight(125) 
        top_layout = QVBoxLayout(self.top_container)
        top_layout.setContentsMargins(0, 0, 0, 0) 
        top_layout.setSpacing(4)

        self.header_container = QWidget()
        header_layout = QHBoxLayout(self.header_container)
        header_layout.setContentsMargins(15, 0, 8, 0) 
        
        status_row = QHBoxLayout()
        status_row.setContentsMargins(0, 0, 0, 0)

        self.time_container = QWidget()
        self.time_container.setFixedSize(60, 55)
        time_layout = QVBoxLayout(self.time_container)
        time_layout.setContentsMargins(0, 5, 0, 0)
        time_layout.setSpacing(0)
        time_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter) 
        
        self.lbl_time = QLabel("00:00")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_time.setStyleSheet('color: white; font-family: "Segoe UI Variable Display"; font-size: 26px; font-weight: 200;') 
        self.lbl_week_num = QLabel("--月 第--周")
        self.lbl_week_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_week_num.setStyleSheet('color: white; font-size: 10px;') 
        
        time_layout.addWidget(self.lbl_time)
        time_layout.addWidget(self.lbl_week_num)
        
        self.weather_container = QWidget()
        self.weather_container.setFixedSize(35, 55)
        weather_layout = QVBoxLayout(self.weather_container)
        weather_layout.setContentsMargins(0, 10, 0, 0)
        weather_layout.setSpacing(2)
        weather_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.lbl_weather_icon = WeatherIconLabel(28, self)
        self.lbl_weather_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_weather_icon.setStyleSheet('color: white; font-size: 18px;')
        self.lbl_weather_icon.start_loading()
        self.lbl_temp = QLabel("--°C")
        self.lbl_temp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_temp.setStyleSheet('color: white; font-size: 10px;') 
        
        weather_layout.addWidget(self.lbl_weather_icon)
        weather_layout.addWidget(self.lbl_temp)

        self.tools_container = QWidget()
        self.tools_container.setFixedHeight(55)
        tools_layout = QVBoxLayout(self.tools_container)
        tools_layout.setContentsMargins(0, 5, 0, 0)
        tools_layout.setSpacing(4)
        tools_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        icons_row = QHBoxLayout()
        icons_row.setSpacing(6) 
        self.toolbar_buttons = {}
        self._toolbar_icon_names = {}
        for icon_name in ["skin.svg", "view.svg", "add.svg", "sort.svg", "filter.svg"]:
            btn = QPushButton()
            btn.setIcon(QIcon(f"assets/icons/{icon_name}"))
            btn.setIconSize(QSize(16, 16)) 
            btn.setFixedSize(20, 20) 
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            btn_default_style = "QPushButton { background: transparent; border: none; } QPushButton:hover { background: rgba(255,255,255,0.2); border-radius: 3px; }"
            btn.setStyleSheet(btn_default_style)
            
            tip_map = {"skin.svg": "换肤", "view.svg": "视图选择", "add.svg": "添加日程", "sort.svg": "排序", "filter.svg": "筛选"}
            btn._tooltip_filter = ToolTipFilter(tip_map[icon_name], btn)
            btn.installEventFilter(btn._tooltip_filter)
            self.toolbar_buttons[icon_name.split(".")[0]] = btn
            self._toolbar_icon_names[icon_name.split(".")[0]] = icon_name
            
            if icon_name == "view.svg":
                self.btn_view_toggle = btn 
                self.btn_view_toggle.clicked.connect(self.toggle_view_selector)
            elif icon_name == "add.svg":
                btn.clicked.connect(self.switch_to_add_page)
            elif icon_name == "sort.svg":
                btn.clicked.connect(self._on_sort_clicked)
            elif icon_name == "filter.svg":
                btn.clicked.connect(self.toggle_filter_options_panel)

            icons_row.addWidget(btn)
        icons_row.addStretch()
        tools_layout.addLayout(icons_row)

        # 1. 搜索框 
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索日程...")
        self.search_box.setFixedSize(123, 18) 
        self.search_action = self.search_box.addAction(
            QIcon(),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        self.search_action.setToolTip("周搜索设置")
        self.search_action.triggered.connect(
            lambda _checked=False: self.toggle_search_options_panel()
        )
        self.search_clear_action = self.search_box.addAction(
            QIcon(),
            QLineEdit.ActionPosition.TrailingPosition,
        )
        self.search_clear_action.setToolTip("清空搜索")
        self.search_clear_action.setVisible(False)
        self.search_clear_action.triggered.connect(self.search_box.clear)
        self.search_box.textChanged.connect(self._on_search_text_changed)
        self.search_box.setStyleSheet(StyleManager.get_search_input_style() + " QLineEdit { font-size: 10px; padding: 0px 1px; }")
        
        # 2. 视图选择器 
        self.view_selector_container = QFrame()
        self.view_selector_container.setFixedWidth(124)
        self.view_selector_container.setFixedHeight(22) 
        self.view_selector_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }
            QPushButton {
                background: transparent; color: white;
                font-family: 'Microsoft YaHei'; font-size: 11px; font-weight: bold;
                border-radius: 4px; border: none; padding: 2px 5px;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }
        """)
        vs_layout = QHBoxLayout(self.view_selector_container)
        vs_layout.setContentsMargins(2, 2, 2, 2) 
        vs_layout.setSpacing(2)
        self.view_selector_buttons = {}
        
        views = {"day": "日", "week": "周", "month": "月", "todo": "待办"}
        for vid, vname in views.items():
            v_btn = QPushButton(vname)
            v_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            if vid == "week":
                v_btn.setStyleSheet("background-color: rgba(0, 0, 0, 0.15); color: white;")
                
            v_btn.clicked.connect(lambda _, v=vid: self._on_view_selected(v))
            vs_layout.addWidget(v_btn, 1)
            self.view_selector_buttons[vid] = v_btn
            
        self.view_selector_container.hide()
        self.bottom_action_container = QWidget()
        self.bottom_action_container.setFixedHeight(22)
        bottom_action_row = QHBoxLayout(self.bottom_action_container)
        bottom_action_row.setContentsMargins(0, 0, 0, 0)
        bottom_action_row.setSpacing(0)
        bottom_action_row.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        
        bottom_action_row.addWidget(self.search_box)
        bottom_action_row.addWidget(self.view_selector_container)
        bottom_action_row.addStretch() 
        
        tools_layout.addWidget(
            self.bottom_action_container,
            alignment=Qt.AlignmentFlag.AlignLeft,
        )

        # ==========================================
        # 组装顶层 status_row 
        # ==========================================
        status_row.addWidget(self.time_container, alignment=Qt.AlignmentFlag.AlignVCenter)
        status_row.addSpacing(0)
        status_row.addWidget(self.weather_container, alignment=Qt.AlignmentFlag.AlignVCenter)
        status_row.addSpacing(0)
        status_row.addWidget(self.tools_container, alignment=Qt.AlignmentFlag.AlignVCenter)
        # 暗色模式双击热区（搜索框右侧空白区域）
        self._dark_mode_trigger = QWidget()
        self._dark_mode_trigger.setStyleSheet("background: transparent;")
        self._dark_mode_trigger.setCursor(Qt.CursorShape.PointingHandCursor)
        self._dark_mode_trigger.setToolTip("双击切换暗色模式")
        self._dark_mode_trigger.installEventFilter(self)
        status_row.addWidget(self._dark_mode_trigger, stretch=1)

        self.btn_suspend = QPushButton(self.top_container)
        self.btn_suspend.setIcon(QIcon("assets/icons/hang_up.png"))
        self.btn_suspend.setIconSize(QSize(14, 14))
        self.btn_suspend.setFixedSize(24, 24) 
        self.btn_suspend.move((self.width() - self.btn_suspend.width()) // 2, 0)
        self.btn_suspend.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_suspend.setStyleSheet("QPushButton { background: transparent; border: none; } QPushButton:hover { background: rgba(255,255,255,0.2); border-radius: 12px; }")
        self.btn_suspend._tooltip_filter = ToolTipFilter("挂起周视图", self.btn_suspend)
        self.btn_suspend.installEventFilter(self.btn_suspend._tooltip_filter)
        self.btn_suspend.clicked.connect(self.suspend_requested.emit)

        status_row.addStretch()

        win_ctrl_layout = QHBoxLayout()
        win_ctrl_layout.setSpacing(2)
        win_ctrl_layout.setContentsMargins(0, 8, 0, 0)
        
        self.btn_more = QToolButton()
        self.btn_more.setIcon(QIcon("assets/icons/more.png"))
        self.btn_more.setIconSize(QSize(12, 12))
        self.btn_more.setFixedSize(20, 20)
        self.btn_more.setStyleSheet(StyleManager.get_window_control_style(is_close=False))
        
        from .components import SharedMoreMenu
        self.shared_more_menu = SharedMoreMenu(self, self.btn_more, show_festival_option=True)
        self.btn_more.clicked.connect(self.shared_more_menu.show_menu)
        
        win_ctrl_layout.addWidget(self.btn_more)

        self.btn_sync = QToolButton()
        self.btn_sync.setIcon(QIcon("assets/icons/sync.png"))
        self.btn_sync.setIconSize(QSize(12, 12))
        self.btn_sync.setFixedSize(20, 20)
        self.btn_sync.setStyleSheet(StyleManager.get_window_control_style(is_close=False))
        win_ctrl_layout.addWidget(self.btn_sync)

        self.btn_close = QToolButton()
        self.btn_close.setIcon(QIcon("assets/icons/close.png"))
        self.btn_close.setIconSize(QSize(12, 12))
        self.btn_close.setFixedSize(20, 20)
        self.btn_close.setStyleSheet(StyleManager.get_window_control_style(is_close=True))
        self.btn_close.clicked.connect(self.close)
        win_ctrl_layout.addWidget(self.btn_close)

        status_row.addLayout(win_ctrl_layout)
        status_row.setAlignment(win_ctrl_layout, Qt.AlignmentFlag.AlignTop)

        header_layout.addLayout(status_row)
        top_layout.addWidget(self.header_container)

        self.nav_container = QWidget()
        nav_layout = QHBoxLayout(self.nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        
        week_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        self.day_blocks = []
        self.weekday_labels = []
        
        for i in range(7):
            col_widget = QWidget()
            col_widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
            
            col_layout = QVBoxLayout(col_widget)
            col_layout.setContentsMargins(2, 0, 2, 0)
            col_layout.setSpacing(4)
            
            lbl_week = QLabel(week_names[i])
            lbl_week.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_week.setStyleSheet("color: white; font-size: 10px; font-weight: bold; font-family: 'Microsoft YaHei';")
            self.weekday_labels.append(lbl_week)
            
            block = DayBlock()
            block.clicked.connect(self._on_day_clicked)
            block.double_clicked.connect(self._on_day_double_clicked)
            self.day_blocks.append(block)
            
            col_layout.addWidget(lbl_week)
            col_layout.addWidget(block)
            
            nav_layout.addWidget(col_widget, stretch=1)
                
        top_layout.addWidget(self.nav_container)

        self.btn_prev = QPushButton("〈", self.top_container)
        self.btn_prev.setFixedSize(32, 36)
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.setStyleSheet("QPushButton { color: white; font-size: 14px; font-weight: bold; border: none; background: transparent; text-align: left; padding-left: 6px; } QPushButton:hover{ background: rgba(255,255,255,0.2); border-radius: 4px; }")
        self.btn_prev.clicked.connect(self._go_prev_week)

        self.btn_next = QPushButton("〉", self.top_container)
        self.btn_next.setFixedSize(32, 36)
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setStyleSheet("QPushButton { color: white; font-size: 14px; font-weight: bold; border: none; background: transparent; text-align: right; padding-right: 6px; } QPushButton:hover{ background: rgba(255,255,255,0.2); border-radius: 4px; }")
        self.btn_next.clicked.connect(self._go_next_week)

        main_layout.addWidget(self.top_container)
        self.btn_suspend.raise_()

        # ==========================================
        # 2. 底部区域 
        # ==========================================
        self.content_area = WeekContentSurface()
        self.content_area.setObjectName("week_content_surface")
        self.content_area.set_surface_colors(
            QColor("#FFFFFF"),
            QColor(120, 120, 120, 72),
        )
        self._week_column_backgrounds = ["#FFFFFF"] * 7
        
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(1, 0, 1, 1)
        
        # 创建堆栈容器
        self.body_stack = QStackedWidget()
        self.body_stack.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.body_stack.setStyleSheet("QStackedWidget { background: transparent; border: none; }")
        content_layout.addWidget(self.body_stack)
        
        # --- 第0页：周日程展示板 ---
        self.page_week_board = QWidget()
        week_board_layout = QHBoxLayout(self.page_week_board)
        week_board_layout.setContentsMargins(0, 0, 0, 0)
        week_board_layout.setSpacing(0)
        
        self.bottom_panels = []
        self.bottom_scroll_areas = []
        self.placeholder_labels = [] 
        
        # 给每一列配置专属的“文字”和“对齐方式”
        placeholder_config = {
            2: ("  ", Qt.AlignmentFlag.AlignRight),   # 周三：靠右
            3: ("点击添加日程", Qt.AlignmentFlag.AlignHCenter), # 周四：居中
            4: ("  ", Qt.AlignmentFlag.AlignLeft)     # 周五：靠左
        }
        
        for i in range(7):
            scroll_area = CardStepScrollArea(
                WeekScheduleCard.CARD_HEIGHT,
                2,
            )
            scroll_area.setWidgetResizable(True) 
            scroll_area.setFrameShape(QFrame.Shape.NoFrame) 
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) 
            scroll_area.setObjectName(f"week_day_scroll_area_{i}")
            scroll_area.setStyleSheet(
                f"QScrollArea#{scroll_area.objectName()} {{ background: transparent; border: none; }}"
            )
            scroll_area.viewport().setAutoFillBackground(False)
            scroll_area.viewport().setStyleSheet("background: transparent;")

            panel = TodoListContainer(self)
            panel.setObjectName(f"week_day_panel_{i}")
            panel.setStyleSheet(f"QWidget#{panel.objectName()} {{ background-color: transparent; }}")
            panel.installEventFilter(self)
            panel.card_dropped.connect(lambda d_id, t_idx, col=i: self._handle_card_drop(d_id, t_idx, col))
            p_layout = QVBoxLayout(panel)
            
            p_layout.setContentsMargins(0, 0, 0, 0) 
            
            p_layout.setSpacing(2) 
            
            
            
            if i in placeholder_config:
                text, align_flag = placeholder_config[i]
                lbl_placeholder = QLabel(text)
                lbl_placeholder.setStyleSheet("color: #CCCCCC; font-size: 15px; font-weight: bold; font-family: 'Microsoft YaHei'; padding-top: 60px;") 
                lbl_placeholder.setAlignment(align_flag | Qt.AlignmentFlag.AlignTop)
                p_layout.addWidget(lbl_placeholder)
                self.placeholder_labels.append(lbl_placeholder)
                
        
            p_layout.addStretch()
            
            scroll_area.setWidget(panel)
            self.bottom_panels.append(panel)
            self.bottom_scroll_areas.append(scroll_area)
            week_board_layout.addWidget(scroll_area, stretch=1)
            
        self.body_stack.addWidget(self.page_week_board)

        self.page_week_timetable_placeholder = WeekTimetableBoard(self)
        self.page_week_timetable_placeholder.schedule_clicked.connect(
            self.request_timetable_schedule_detail.emit
        )
        self.page_week_timetable_placeholder.schedule_time_changed.connect(
            self._handle_timetable_time_changed
        )
        self.page_week_timetable_placeholder.time_edit_week_turn_requested.connect(
            self._handle_timetable_week_turn_during_edit
        )
        self.page_week_timetable_placeholder.schedule_context_requested.connect(
            self._show_timetable_schedule_context_menu
        )
        self.page_week_timetable_placeholder.empty_area_context_requested.connect(
            self._show_timetable_empty_area_context_menu
        )
        self.page_week_timetable_placeholder.day_selected.connect(
            self._on_day_clicked
        )
        self.body_stack.addWidget(self.page_week_timetable_placeholder)
        
        # --- 第1~4页：复用主界面的组件 ---
        self.page_add = AddScheduleViewWeek()
        self.page_time = TimePickerViewWeek()
        self.page_alarm = AlarmPickerViewWeek()
        self.page_list = ListPickerView()
        self.page_list.btn_suspend.hide()
        self.page_list.btn_close.hide()
        
        self.body_stack.addWidget(self.page_add)
        self.body_stack.addWidget(self.page_time)
        self.body_stack.addWidget(self.page_alarm)
        self.body_stack.addWidget(self.page_list)
        
        self.body_stack.setCurrentIndex(0)
        self._sync_schedule_display_mode_ui()
        main_layout.addWidget(self.content_area, stretch=1)
        
        self._setup_routing_signals()


    def _main_schedule_page(self):
        if getattr(self, "schedule_display_mode", "card") == "timetable":
            return self.page_week_timetable_placeholder
        return self.page_week_board

    def _header_foreground_color(self):
        return "#2b2b2b" if getattr(self, "_dark_mode", False) else "#FFFFFF"

    def _header_hover_background(self):
        if getattr(self, "_dark_mode", False):
            return "rgba(43, 43, 43, 0.18)"
        return "rgba(255, 255, 255, 0.2)"

    def _toolbar_button_style(self, active=False):
        bg = "rgba(43, 43, 43, 0.22)" if getattr(self, "_dark_mode", False) else "rgba(255,255,255,0.3)"
        if not active:
            bg = "transparent"
        return (
            "QPushButton { "
            f"background: {bg}; color: {self._header_foreground_color()}; "
            "border: none; border-radius: 3px; "
            "} "
            f"QPushButton:hover {{ background: {self._header_hover_background()}; border-radius: 3px; }}"
        )

    def _toolbar_button_is_active(self, button_key):
        if button_key == "view":
            return self.view_selector_container.isVisible()
        if button_key == "filter":
            return self._filter_options.has_filter_constraints()
        if button_key == "sort":
            return (
                getattr(self, "schedule_display_mode", "card") == "card"
                and not self._sort_options.is_default()
            )
        return False

    def _sync_filter_button_state(self):
        button = getattr(self, "toolbar_buttons", {}).get("filter")
        if button is not None:
            button.setStyleSheet(
                self._toolbar_button_style(
                    active=self._toolbar_button_is_active("filter")
                )
            )

    def _sync_sort_button_state(self):
        button = getattr(self, "toolbar_buttons", {}).get("sort")
        if button is not None:
            button.setStyleSheet(
                self._toolbar_button_style(
                    active=self._toolbar_button_is_active("sort")
                )
            )

    def _search_input_style(self):
        foreground = self._header_foreground_color()
        placeholder = "rgba(43, 43, 43, 0.65)" if getattr(self, "_dark_mode", False) else "rgba(255, 255, 255, 0.7)"
        return f"""
            QLineEdit {{
                background-color: rgba(255, 255, 255, 0.16);
                border: 2px solid {foreground};
                border-radius: 6px;
                color: {foreground};
                placeholder-text-color: {placeholder};
                padding: 0px 1px;
                font-family: "Microsoft YaHei UI";
                font-size: 10px;
            }}
            QLineEdit:hover {{
                background-color: rgba(255, 255, 255, 0.12);
                border: 2px solid {foreground};
            }}
            QLineEdit:focus {{
                background-color: rgba(255, 255, 255, 0.16);
                border: 2px solid {foreground};
            }}
        """

    def _view_selector_style(self):
        foreground = self._header_foreground_color()
        hover = self._header_hover_background()
        return f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.16);
                border-radius: 4px;
            }}
            QPushButton {{
                background: transparent;
                color: {foreground};
                font-family: 'Microsoft YaHei';
                font-size: 11px;
                font-weight: bold;
                border-radius: 4px;
                border: none;
                padding: 2px 5px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
        """

    def _view_selector_button_style(self, selected=False):
        foreground = self._header_foreground_color()
        background = "rgba(43, 43, 43, 0.18)" if selected else "transparent"
        return (
            "QPushButton { "
            f"background-color: {background}; color: {foreground}; "
            "font-family: 'Microsoft YaHei'; font-size: 11px; font-weight: bold; "
            "border-radius: 4px; border: none; padding: 2px 5px; "
            "} "
            f"QPushButton:hover {{ background-color: {self._header_hover_background()}; }}"
        )

    def _nav_button_style(self, side):
        foreground = self._header_foreground_color()
        text_align = "left" if side == "left" else "right"
        padding = "padding-left: 6px;" if side == "left" else "padding-right: 6px;"
        return (
            "QPushButton { "
            f"color: {foreground}; font-size: 14px; font-weight: bold; "
            "border: none; background: transparent; "
            f"text-align: {text_align}; {padding} "
            "} "
            f"QPushButton:hover {{ background: {self._header_hover_background()}; border-radius: 4px; }}"
        )

    def _window_control_style(self, is_close=False):
        hover = "#ff4d4f" if is_close else self._header_hover_background()
        pressed = "#d9363e" if is_close else (
            "rgba(43, 43, 43, 0.26)" if getattr(self, "_dark_mode", False) else "rgba(255, 255, 255, 0.3)"
        )
        return f"""
            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                margin: 0px;
                padding: 0px;
            }}
            QToolButton:hover {{
                background-color: {hover};
            }}
            QToolButton:pressed {{
                background-color: {pressed};
            }}
        """

    def _tinted_pixmap(self, icon_path, color_hex, icon_size):
        source = QPixmap(icon_path)
        if source.isNull():
            return QPixmap()
        ratio = self.devicePixelRatio()
        pixmap = source.scaled(
            int(icon_size * ratio),
            int(icon_size * ratio),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        image = pixmap.toImage().convertToFormat(QImage.Format.Format_ARGB32)
        painter = QPainter(image)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(image.rect(), QColor(color_hex))
        painter.end()
        tinted = QPixmap.fromImage(image)
        tinted.setDevicePixelRatio(ratio)
        return tinted

    def _set_tinted_png_icon(self, button, icon_path, icon_size):
        pixmap = self._tinted_pixmap(icon_path, self._header_foreground_color(), icon_size)
        button.setIcon(QIcon(pixmap) if not pixmap.isNull() else QIcon(icon_path))

    def _apply_view_selector_button_styles(self):
        for vid, button in getattr(self, "view_selector_buttons", {}).items():
            button.setStyleSheet(self._view_selector_button_style(selected=(vid == "week")))

    def _apply_search_icon(self):
        if not hasattr(self, "search_action"):
            return

        foreground = self._header_foreground_color()
        pixmap = get_padded_colored_icon("search.svg", foreground, icon_size=10, canvas_size=16)
        self.search_action.setIcon(QIcon(pixmap) if not pixmap.isNull() else QIcon("assets/icons/search.svg"))
        if hasattr(self, "search_clear_action"):
            clear_pixmap = get_padded_colored_icon(
                "search_clear.svg",
                foreground,
                icon_size=8,
                canvas_size=14,
            )
            self.search_clear_action.setIcon(
                QIcon(clear_pixmap)
                if not clear_pixmap.isNull()
                else QIcon("assets/icons/search_clear.svg")
            )

    def _apply_week_header_foreground(self):
        foreground = self._header_foreground_color()

        if hasattr(self, "lbl_time"):
            self.lbl_time.setStyleSheet(f'color: {foreground}; font-family: "Segoe UI Variable Display"; font-size: 26px; font-weight: 200;')
        if hasattr(self, "lbl_week_num"):
            self.lbl_week_num.setStyleSheet(f"color: {foreground}; font-size: 10px;")
        if hasattr(self, "lbl_temp"):
            self.lbl_temp.setStyleSheet(f"color: {foreground}; font-size: 10px;")
        if hasattr(self, "lbl_weather_icon"):
            self.lbl_weather_icon.setStyleSheet(f"color: {foreground}; font-size: 18px;")
            if hasattr(self.lbl_weather_icon, "set_icon_color"):
                self.lbl_weather_icon.set_icon_color(foreground)
            else:
                self.lbl_weather_icon.icon_color = foreground

        for label in getattr(self, "weekday_labels", []):
            label.setStyleSheet(f"color: {foreground}; font-size: 10px; font-weight: bold; font-family: 'Microsoft YaHei';")

        for key, button in getattr(self, "toolbar_buttons", {}).items():
            icon_name = getattr(self, "_toolbar_icon_names", {}).get(key)
            if icon_name:
                pixmap = get_colored_icon(icon_name, foreground, 16)
                button.setIcon(QIcon(pixmap) if not pixmap.isNull() else QIcon(f"assets/icons/{icon_name}"))
            button.setStyleSheet(
                self._toolbar_button_style(
                    active=self._toolbar_button_is_active(key)
                )
            )

        if hasattr(self, "search_box"):
            self.search_box.setStyleSheet(self._search_input_style())
            self._apply_search_icon()
        if hasattr(self, "view_selector_container"):
            self.view_selector_container.setStyleSheet(self._view_selector_style())
            self._apply_view_selector_button_styles()
        if hasattr(self, "btn_suspend"):
            self._set_tinted_png_icon(self.btn_suspend, "assets/icons/hang_up.png", 14)
            self.btn_suspend.setStyleSheet(
                "QPushButton { background: transparent; border: none; border-radius: 12px; } "
                f"QPushButton:hover {{ background: {self._header_hover_background()}; border-radius: 12px; }}"
            )
        if hasattr(self, "btn_more"):
            self._set_tinted_png_icon(self.btn_more, "assets/icons/more.png", 12)
            self.btn_more.setStyleSheet(self._window_control_style(is_close=False))
        if hasattr(self, "btn_sync"):
            self._set_tinted_png_icon(self.btn_sync, "assets/icons/sync.png", 12)
            self.btn_sync.setStyleSheet(self._window_control_style(is_close=False))
        if hasattr(self, "btn_close"):
            self._set_tinted_png_icon(self.btn_close, "assets/icons/close.png", 12)
            self.btn_close.setStyleSheet(self._window_control_style(is_close=True))

        if hasattr(self, "btn_prev"):
            self.btn_prev.setStyleSheet(self._nav_button_style("left"))
        if hasattr(self, "btn_next"):
            self.btn_next.setStyleSheet(self._nav_button_style("right"))

    def _set_toolbar_button_icon(self, button_key, icon_name, tooltip):
        button = getattr(self, "toolbar_buttons", {}).get(button_key)
        if button is None:
            return
        self._toolbar_icon_names[button_key] = icon_name
        old_filter = getattr(button, "_tooltip_filter", None)
        if old_filter is not None:
            button.removeEventFilter(old_filter)
        pixmap = get_colored_icon(icon_name, self._header_foreground_color(), 16)
        button.setIcon(QIcon(pixmap) if not pixmap.isNull() else QIcon(f"assets/icons/{icon_name}"))
        button.setStyleSheet(
            self._toolbar_button_style(
                active=self._toolbar_button_is_active(button_key)
            )
        )
        button._tooltip_filter = ToolTipFilter(tooltip, button)
        button.installEventFilter(button._tooltip_filter)

    def _sync_schedule_display_mode_ui(self):
        if not hasattr(self, "body_stack"):
            return
        if getattr(self, "schedule_display_mode", "card") == "timetable":
            self._set_toolbar_button_icon("sort", "refresh.svg", "刷新课表")
        else:
            self._set_toolbar_button_icon("sort", "sort.svg", "排序")
        self._sync_sort_button_state()

        if self.body_stack.currentWidget() in (
            self.page_week_board,
            self.page_week_timetable_placeholder,
        ):
            self.body_stack.setCurrentWidget(self._main_schedule_page())
        self._sync_content_surface_column_backgrounds()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path_bg = QPainterPath()
        rect_bg = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path_bg.addRoundedRect(rect_bg, 8.0, 8.0)

        
        if self.is_edit_mode:
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
            gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
            painter.fillPath(path_bg, QBrush(gradient))
            
        
        else:
            painter.fillPath(path_bg, QColor("#FFFFFF"))

            path_top = QPainterPath()
            path_top.setFillRule(Qt.FillRule.WindingFill)
            rect_top = QRectF(0, 0, self.width(), self.top_container.height())
            path_top.addRoundedRect(rect_top, 8.0, 8.0)
            path_top.addRect(0, self.top_container.height() - 10, self.width(), 10)
            
            gradient = QLinearGradient(0, 0, 0, self.top_container.height())
            gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
            gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
            painter.fillPath(path_top, QBrush(gradient))

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(120, 120, 120, 140), 1))
        painter.drawPath(path_bg)

    def _set_edit_mode_bg(self, is_edit):
        """动态切换下半部分盒子的颜色，并命令窗口重绘自己"""
        self.is_edit_mode = is_edit
        if is_edit:
            self.content_area.set_surface_colors(
                QColor(0, 0, 0, 0),
                QColor(120, 120, 120, 72),
            )
        else:
            self.content_area.set_surface_colors(
                QColor("#FFFFFF"),
                QColor(120, 120, 120, 72),
            )
        
        self._sync_content_surface_column_backgrounds()
        self.update() # 实现 paintEvent 重绘

    def show_toast(self, message):
        from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
        from PyQt6.QtCore import Qt, QTimer
        from .components import get_colored_icon 
        
        if hasattr(self, 'toast_widget') and self.toast_widget.isVisible():
            self.toast_widget.close()
            
        self.toast_widget = QWidget(self)
        self.toast_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.75);
                border-radius: 8px;
            }
            QLabel {
                background: transparent;
                color: white;
                font-family: 'Microsoft YaHei';
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
        """)
        
        # 使用水平布局来容纳图标和文字
        layout = QHBoxLayout(self.toast_widget)
        layout.setContentsMargins(20, 12, 24, 12) 
        layout.setSpacing(8) # 图标和文字之间的间距
        
        # 1. 注入 SVG 图标 
        icon_label = QLabel()
        icon_label.setFixedSize(16, 16)
        pixmap = get_colored_icon("pop_error.svg", "#FAAD14", 16) 
        icon_label.setPixmap(pixmap)
        icon_label.setScaledContents(True)
        
        # 2. 注入提示文字
        text_label = QLabel(message)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 拼装进布局
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        
        self.toast_widget.adjustSize()
        self.toast_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) # 鼠标穿透
        
        # 让弹窗完美居中
        x = (self.width() - self.toast_widget.width()) // 2
        y = (self.height() - self.toast_widget.height()) // 2
        self.toast_widget.move(x, y)
        self.toast_widget.show()
        
        # 定时 1.5 秒后自动销毁关闭
        QTimer.singleShot(1500, self.toast_widget.close)

    # ==========================================
    # 页面路由与业务逻辑中枢
    # ==========================================
    def _setup_routing_signals(self):
        self.page_add.btn_cancel.clicked.connect(self.switch_to_main_board)
        self.page_add.saved.connect(self.on_schedule_saved)
        
        self.page_add.req_open_time_picker.connect(self.go_to_time_picker)
        self.page_time.back_requested.connect(self.back_from_time_picker) 
        self.page_time.confirm_requested.connect(self.on_time_confirmed)

        self.page_add.req_open_alarm_picker.connect(self.go_to_alarm_picker)
        self.page_alarm.back_requested.connect(self.back_from_alarm_picker) 
        self.page_alarm.confirm_requested.connect(self.on_alarm_confirmed)

        self.page_add.req_open_list_picker.connect(self.go_to_list_picker)
        self.page_list.back_requested.connect(self.back_from_list_picker) 
        self.page_list.confirm_requested.connect(self.on_list_confirmed)

    def switch_to_add_page(self):
        self._hide_week_query_panels()
        if self.body_stack.currentWidget() == self.page_add:
            self.switch_to_main_board()
            return
        
        today = datetime.now().date()
        if self.current_selected_date.toPyDate() < today:
            print("该日期已过期，无法添加日程") 
            return

        self.exit_week_multi_select_mode()
        self.page_add.reset()
        self.body_stack.setCurrentWidget(self.page_add)
        self._set_edit_mode_bg(True)

    def switch_to_main_board(self):
        self.body_stack.setCurrentWidget(self._main_schedule_page())
        # 恢复原状
        self._set_edit_mode_bg(False)

    def on_schedule_saved(self):
        self.switch_to_main_board()
        self.refresh_week_data()
        self.schedule_updated.emit(None)
        print("✅ 成功在周视图中添加了日程并存入数据库！")

    def go_to_time_picker(self, start, end):
        self.time_picker_mode = 'add' # 重置为添加模式
        self.page_time.set_title("设置时间")
        if not start and not end:
            dashboard_date = self.current_selected_date.toPyDate()
            now = datetime.now()
            end = datetime(dashboard_date.year, dashboard_date.month, dashboard_date.day, now.hour, now.minute)
        self.page_time.set_initial_data(start, end)
        self.body_stack.setCurrentWidget(self.page_time)

    def go_to_time_picker_for_edit(self, schedule_data):
        """周界面的时间修改路由"""
        self.time_picker_mode = 'edit'
        self.editing_schedule = schedule_data
        
        # 智能截断标题防止 UI 撑爆
        display_title = schedule_data.title if len(schedule_data.title) <= 8 else schedule_data.title[:7] + "..."
        self.page_time.set_title(f"修改【{display_title}】时间")
        self.page_time.set_initial_data(schedule_data.start_time, schedule_data.end_time)
        
        self.body_stack.setCurrentWidget(self.page_time)
        self._set_edit_mode_bg(True) 

    def back_from_time_picker(self):
        """统一的返回逻辑：从哪来的回哪去"""
        if getattr(self, 'time_picker_mode', 'add') == 'edit':
            self.switch_to_main_board() 
        else:
            self.body_stack.setCurrentWidget(self.page_add)

    def on_time_confirmed(self, start, end):
        if getattr(self, 'time_picker_mode', 'add') == 'edit' and hasattr(self, 'editing_schedule') and self.editing_schedule:
            def _do_update(update_future):
                now = datetime.now()
                new_data = {'start_time': start, 'end_time': end, 'created_at': now}
                db_manager.update_schedule_with_repeat(self.editing_schedule.id, new_data, update_future)
                
                self.editing_schedule.start_time = start
                self.editing_schedule.end_time = end
                self.editing_schedule.created_at = now
                if not update_future: self.editing_schedule.group_id = None
                
                self.refresh_week_data()
                self.schedule_updated.emit(self.editing_schedule)
                self.back_from_time_picker()
            self._check_repeat_and_execute(self.editing_schedule, _do_update)
        else:
            self.page_add.set_time_data(start, end)
            self.back_from_time_picker()

    def go_to_alarm_picker(self, target_time, is_alarm, duration):
        self.alarm_picker_mode = 'add'
        self.page_alarm.set_title("设置提醒")
        self.page_alarm.set_initial_data(target_time, is_alarm, duration) 
        self.body_stack.setCurrentWidget(self.page_alarm)

    def go_to_alarm_picker_for_edit(self, schedule_data):
        """周界面的提醒修改路由"""
        self.alarm_picker_mode = 'edit'
        self.editing_schedule = schedule_data
        
        display_title = schedule_data.title if len(schedule_data.title) <= 8 else schedule_data.title[:7] + "..."
        self.page_alarm.set_title(f"修改【{display_title}】提醒")
        
        target = schedule_data.start_time if schedule_data.start_time else schedule_data.end_time
        if not target: 
            target = datetime.now()
            
        self.page_alarm.set_initial_data(target, schedule_data.is_alarm, schedule_data.alarm_duration)
        self.body_stack.setCurrentWidget(self.page_alarm)
        self._set_edit_mode_bg(True)

    def back_from_alarm_picker(self):
        if getattr(self, 'alarm_picker_mode', 'add') == 'edit':
            self.switch_to_main_board() 
        else:
            self.body_stack.setCurrentWidget(self.page_add)

    def on_alarm_confirmed(self, remind_dt, is_alarm, duration):
        if getattr(self, 'alarm_picker_mode', 'add') == 'edit' and hasattr(self, 'editing_schedule') and self.editing_schedule:
            def _do_update(update_future):
                now = datetime.now()
                new_data = {'reminder_time': remind_dt, 'is_alarm': is_alarm, 'alarm_duration': duration, 'created_at': now}
                db_manager.update_schedule_with_repeat(self.editing_schedule.id, new_data, update_future)
                
                self.editing_schedule.reminder_time = remind_dt
                self.editing_schedule.is_alarm = is_alarm
                self.editing_schedule.alarm_duration = duration
                self.editing_schedule.created_at = now
                if not update_future: self.editing_schedule.group_id = None
                
                self.refresh_week_data()
                self.schedule_updated.emit(self.editing_schedule) 
                self.back_from_alarm_picker()
            self._check_repeat_and_execute(self.editing_schedule, _do_update)
        else:
            self.page_add.set_alarm_data(remind_dt, is_alarm, duration)
            self.back_from_alarm_picker()

    def go_to_list_picker(self, current_category_id):
        self.list_picker_mode = 'add'
        self.page_list.set_title("选择清单")
        self.page_list.load_data(current_category_id)
        self.body_stack.setCurrentWidget(self.page_list)

    def go_to_list_picker_for_edit(self, schedule_data):
        """周界面的清单修改路由"""
        self.list_picker_mode = 'edit'
        self.editing_schedule = schedule_data
        
        display_title = schedule_data.title if len(schedule_data.title) <= 8 else schedule_data.title[:7] + "..."
        self.page_list.set_title(f"修改【{display_title}】清单")
        
        self.page_list.load_data(schedule_data.category_id)
        self.body_stack.setCurrentWidget(self.page_list)
        self._set_edit_mode_bg(True)

    def back_from_list_picker(self):
        if getattr(self, 'list_picker_mode', 'add') == 'edit':
            self.switch_to_main_board() 
        else:
            self.body_stack.setCurrentWidget(self.page_add)

    def on_list_confirmed(self, category_id):
        if getattr(self, 'list_picker_mode', 'add') == 'edit' and hasattr(self, 'editing_schedule') and self.editing_schedule:
            def _do_update(update_future):
                now = datetime.now()
                new_data = {'category_id': category_id, 'created_at': now}
                db_manager.update_schedule_with_repeat(self.editing_schedule.id, new_data, update_future)
                
                self.editing_schedule.category_id = category_id
                self.editing_schedule.created_at = now
                if not update_future: self.editing_schedule.group_id = None
                
                self.refresh_week_data()
                self.schedule_updated.emit(self.editing_schedule) 
                self.back_from_list_picker()
            self._check_repeat_and_execute(self.editing_schedule, _do_update)
        else:
            self.page_add.set_list_data(category_id)
            self.back_from_list_picker()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_week_data()

    def hideEvent(self, event):
        self._hide_week_query_panels()
        super().hideEvent(event)

    def closeEvent(self, event):
        self._exit_sort_state_for_close()
        self._hide_week_query_panels()
        super().closeEvent(event)

    def _exit_sort_state_for_close(self):
        if self._sort_options.is_default():
            return
        self.freeze_current_card_order()
        self.apply_sort_options(ScheduleSortOptions())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'btn_prev') and hasattr(self, 'btn_next'):
            btn_y = self.top_container.height() - 40 
            self.btn_prev.move(4, btn_y) 
            self.btn_next.move(self.width() - 36, btn_y)

    # --- 后续的逻辑处理代码保持不变 ---
    def _start_clock(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)
        self._update_time()

    def _update_time(self):
        self.lbl_time.setText(QTime.currentTime().toString("HH:mm"))

    def _get_monday(self, date):
        return date.addDays(-(date.dayOfWeek() - 1))

    def get_lunar_str(self, qdate):
        py_date = qdate.toPyDate()
        py_datetime = datetime(py_date.year, py_date.month, py_date.day)
        #清明节为错误的日期，后面单独处理
        solar_festivals = {
            (1, 1): "元旦", (2, 14): "情人节", (3, 8): "妇女节",
            (4, 4): "清明节", (4, 5): "清明节", (5, 1): "劳动节",
            (6, 1): "儿童节", (10, 1): "国庆", (12, 25): "圣诞"
        }
        if (py_date.month, py_date.day) in solar_festivals:
            return solar_festivals[(py_date.month, py_date.day)]

        try:
            lunar_date = ZhDate.from_datetime(py_datetime)
            lunar_festivals = {
                (1, 1): "春节", (1, 15): "元宵", (5, 5): "端午",
                (7, 7): "七夕", (8, 15): "中秋", (9, 9): "重阳",
                (12, 8): "腊八", (12, 23): "小年"
            }
            if (lunar_date.lunar_month, lunar_date.lunar_day) in lunar_festivals:
                return lunar_festivals[(lunar_date.lunar_month, lunar_date.lunar_day)]

            next_day = py_datetime + timedelta(days=1)
            next_lunar = ZhDate.from_datetime(next_day)
            if next_lunar.lunar_month == 1 and next_lunar.lunar_day == 1:
                return "除夕"

            if lunar_date.lunar_day == 1:
                month_names = ["正月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "冬月", "腊月"]
                return month_names[lunar_date.lunar_month - 1]
            else:
                day_names = [
                    "", "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
                    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
                    "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
                ]
                return day_names[lunar_date.lunar_day]
        except Exception as e:
            print(f"农历转换错误: {e}")
            return "未知"

    def _week_board_column_background(self, is_selected: bool) -> str:
        if self._dark_mode:
            return "#3A3A3A" if is_selected else "#2b2b2b"
        return "#F0F0F0" if is_selected else "#FFFFFF"

    def _apply_week_board_column_background(self, index: int, is_selected: bool):
        bg_color = self._week_board_column_background(is_selected)

        if hasattr(self, 'bottom_scroll_areas') and index < len(self.bottom_scroll_areas):
            scroll_area = self.bottom_scroll_areas[index]
            scroll_area.setStyleSheet(
                f"QScrollArea#{scroll_area.objectName()} {{ background: transparent; border: none; }}"
            )
            scroll_area.viewport().setAutoFillBackground(False)
            scroll_area.viewport().setStyleSheet("background: transparent;")

        if hasattr(self, 'bottom_panels') and index < len(self.bottom_panels):
            panel = self.bottom_panels[index]
            panel.setStyleSheet(f"QWidget#{panel.objectName()} {{ background-color: transparent; }}")

        if hasattr(self, '_week_column_backgrounds'):
            self._week_column_backgrounds[index] = bg_color
            self._sync_content_surface_column_backgrounds()

    def _sync_content_surface_column_backgrounds(self):
        if not hasattr(self, 'content_area'):
            return
        if (
            getattr(self, 'schedule_display_mode', 'card') == 'card'
            and not getattr(self, 'is_edit_mode', False)
        ):
            colors = getattr(self, '_week_column_backgrounds', [])
        else:
            colors = []
        self.content_area.set_column_backgrounds(colors)

    def refresh_week_data(self):
        for i in range(7):
            iter_date = self.current_monday.addDays(i)
            block = self.day_blocks[i]
            block.set_data(iter_date, self.get_lunar_str(iter_date))
            block.set_selected(iter_date == self.current_selected_date)
            is_selected = (iter_date == self.current_selected_date)
            block.set_selected(is_selected)
            
            self._apply_week_board_column_background(i, is_selected)

        month = self.current_monday.month()    
        week_num = self.current_monday.weekNumber()[0]
        self.lbl_week_num.setText(f"{month}月 第{week_num}周")
        self.load_week_schedules_from_db()

    def filter_options(self):
        return self._filter_options

    def search_options_for_panel(self):
        if self._search_options is not None:
            return self._search_options
        return self._filter_options.with_search_preferences(
            self._last_search_scope,
            self._last_match_mode,
        )

    def apply_filter_options(self, options):
        self._filter_options = options
        self._sync_filter_button_state()
        self.refresh_week_data()

    def apply_search_options(self, options):
        self._search_options = options
        self._last_search_scope = options.search_scope
        self._last_match_mode = options.match_mode
        if self._search_keyword:
            self.refresh_week_data()

    def set_search_keyword(self, keyword):
        normalized_keyword = str(keyword or "").strip()
        if normalized_keyword:
            if self._search_options is None:
                self._search_options = self.search_options_for_panel()
            self._search_keyword = normalized_keyword
        else:
            self._search_keyword = ""
            self._search_options = None
        self.refresh_week_data()

    def _active_query_options(self):
        if self._search_keyword:
            return self._search_options or self.search_options_for_panel()
        return self._filter_options

    def _apply_schedule_query(self, schedules, day_index):
        options = self._active_query_options()
        if day_index not in options.weekdays:
            return []
        return ScheduleQueryService.apply_options(
            schedules,
            options,
            self._search_keyword,
        )

    def sort_options(self):
        return self._sort_options

    def apply_sort_options(self, options):
        self._sort_options = options
        set_schedule_sort_options("week", options)
        self._sync_sort_button_state()
        self.refresh_week_data()

    def freeze_current_card_order(self):
        seen_ids = set()
        for panel in self.bottom_panels:
            layout = panel.layout()
            if layout is None:
                continue
            schedules = []
            for index in range(layout.count()):
                item = layout.itemAt(index)
                widget = item.widget() if item is not None else None
                if not isinstance(widget, WeekScheduleCard):
                    continue
                schedule_id = getattr(widget.data, "id", None)
                if schedule_id is None or schedule_id in seen_ids:
                    continue
                seen_ids.add(schedule_id)
                schedules.append(widget.data)
            self._write_manual_sort_order(schedules)

    @staticmethod
    def _write_manual_sort_order(schedules):
        base_order = datetime.now().timestamp()
        for index, schedule in enumerate(schedules):
            schedule_id = getattr(schedule, "id", None)
            if schedule_id is None:
                continue
            new_order = base_order - index * 100.0
            schedule.sort_order = new_order
            db_manager.update_schedule_fields(schedule_id, sort_order=new_order)

    def _on_search_text_changed(self, text):
        self.search_clear_action.setVisible(bool(text))
        self.set_search_keyword(text)

    def toggle_search_options_panel(self):
        panel = self._ensure_week_query_panel("search")
        if panel.isVisible():
            panel.close()
            return
        if self._filter_options_panel is not None:
            self._filter_options_panel.close()
        panel.set_options(
            self.search_options_for_panel(),
            db_manager.get_active_categories("schedule"),
        )
        self._show_week_query_panel(panel)

    def toggle_filter_options_panel(self):
        panel = self._ensure_week_query_panel("filter")
        if panel.isVisible():
            panel.close()
            return
        if self._search_options_panel is not None:
            self._search_options_panel.close()
        panel.set_options(
            self.filter_options(),
            db_manager.get_active_categories("schedule"),
        )
        self._show_week_query_panel(panel)

    def toggle_sort_options_panel(self):
        panel = self._ensure_week_sort_panel()
        if panel.isVisible():
            panel.close()
            return
        self._hide_week_query_panels()
        panel.set_options(self.sort_options())
        self._show_week_query_panel(panel)

    def _ensure_week_query_panel(self, panel_mode):
        from .popups.week_query_options_panel import WeekQueryOptionsPanel

        attribute_name = (
            "_search_options_panel"
            if panel_mode == "search"
            else "_filter_options_panel"
        )
        panel = getattr(self, attribute_name)
        if panel is None:
            panel = WeekQueryOptionsPanel(panel_mode, self)
            if panel_mode == "search":
                panel.options_changed.connect(self.apply_search_options)
                panel.applied.connect(self._handle_search_options_applied)
            else:
                panel.options_changed.connect(self.apply_filter_options)
                panel.applied.connect(self._handle_filter_options_applied)
            setattr(self, attribute_name, panel)
        return panel

    def _ensure_week_sort_panel(self):
        from .popups.schedule_sort_options_panel import ScheduleSortOptionsPanel

        if self._sort_options_panel is None:
            panel = ScheduleSortOptionsPanel("week", self)
            panel.options_changed.connect(self.apply_sort_options)
            panel.applied.connect(self._handle_sort_options_applied)
            self._sort_options_panel = panel
        return self._sort_options_panel

    def _handle_search_options_applied(self, options):
        self.apply_search_options(options)
        if self._search_options_panel is not None:
            self._search_options_panel.close()

    def _handle_filter_options_applied(self, options):
        self.apply_filter_options(options)
        if self._filter_options_panel is not None:
            self._filter_options_panel.close()

    def _handle_sort_options_applied(self, options):
        if options.is_default() and not self._sort_options.is_default():
            self.freeze_current_card_order()
        self.apply_sort_options(options)
        if self._sort_options_panel is not None:
            self._sort_options_panel.close()

    def _show_week_query_panel(self, panel):
        self._position_week_query_panel(panel)
        panel.show()
        panel.raise_()
        panel.activateWindow()

    def _position_week_query_panel(self, panel):
        window_geometry = self.frameGeometry()
        x = window_geometry.left() - panel.width() - 8
        y = window_geometry.top() + 8
        screen = QApplication.screenAt(window_geometry.center()) or QApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            if x < available.left():
                x = window_geometry.left() + 8
            x = max(available.left(), min(x, available.right() - panel.width() + 1))
            y = max(available.top(), min(y, available.bottom() - panel.height() + 1))
        panel.move(x, y)

    def _hide_week_query_panels(self):
        for panel in (
            self._search_options_panel,
            self._filter_options_panel,
            self._sort_options_panel,
        ):
            if panel is not None and panel.isVisible():
                panel.close()

    def load_week_schedules_from_db(self):
        """直接从数据库读取本周所有数据，并渲染到 7 个面板"""
        has_any_card_schedule = False
        has_any_timetable_schedule = False
        week_timetable_schedules = {}
        category_map = db_manager.get_category_map()
        active_drag_card = self._active_drag_card
        active_drag_id = (
            getattr(getattr(active_drag_card, "data", None), "id", None)
            if active_drag_card is not None
            else None
        )
        
        # 1. 精准清理旧卡片
        for panel in self.bottom_panels:
            layout = panel.layout()
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                if item.widget() and isinstance(item.widget(), WeekScheduleCard):
                    widget = item.widget()
                    layout.removeWidget(widget)
                    if widget is active_drag_card:
                        widget.setParent(self.page_week_board)
                        widget.move(-10000, -10000)
                        widget.show()
                    else:
                        widget.deleteLater()
            panel.current_drag_widget = active_drag_card

        # 2. 一次查询全量日程，按日期分发到 7 天（替代 7 次全表扫描）
        all_schedules = db_manager.get_all_schedules()
        for day_index in range(7):
            target_date = self.current_monday.addDays(day_index).toPyDate()
            daily_schedules = ScheduleQueryService.filter_for_date(
                all_schedules, target_date
            )
            valid_schedules = [
                s for s in daily_schedules
                if ScheduleQueryService.is_schedule(s)
                and getattr(s, "status", 0) != 2
            ]
            valid_schedules = self._apply_schedule_query(
                valid_schedules,
                day_index,
            )
            week_timetable_schedules[day_index] = list(valid_schedules)
            if valid_schedules:
                has_any_timetable_schedule = True

            card_schedules = ScheduleSortService.sort_for_week_view(
                valid_schedules,
                self._sort_options,
            )
            if card_schedules:
                has_any_card_schedule = True
                panel_layout = self.bottom_panels[day_index].layout()

                for sched_obj in card_schedules:
                    if active_drag_id is not None and sched_obj.id == active_drag_id:
                        continue
                    card = WeekScheduleCard(sched_obj)
                    if self._dark_mode:
                        card.set_dark_mode(True)
                    card.clicked.connect(self.request_schedule_detail.emit)
                    card.req_status.connect(self._handle_schedule_status_change)
                    card.req_pin.connect(self._handle_schedule_pin_change)
                    card.req_delete.connect(self._handle_schedule_delete)
                    card.drag_started.connect(self._begin_card_drag)
                    card.drag_finished.connect(self._finish_card_drag)
                    card.selection_toggled.connect(
                        self._toggle_week_schedule_selection
                    )
                    card.set_multi_select_state(
                        self._week_multi_select_active,
                        sched_obj.id in self._week_selected_schedule_ids,
                    )
                    panel_layout.insertWidget(panel_layout.count() - 1, card)

        has_any_schedule = (
            has_any_timetable_schedule
            if getattr(self, "schedule_display_mode", "card") == "timetable"
            else has_any_card_schedule
        )
        self.update_placeholder_visibility(has_any_schedule)
        self.page_week_timetable_placeholder.set_week_data(
            self.current_monday,
            week_timetable_schedules,
            category_map,
        )
        self.page_week_timetable_placeholder.set_selected_day(
            self.current_selected_date
        )
        if self._week_multi_select_active:
            self._sync_week_multi_select_state()
        self._sync_panel_scroll_heights()

    def update_placeholder_visibility(self, has_any_schedule: bool):
        """
        核心控制：根据本周是否含有任何日程，统一显示或隐藏跨列提示字
        """
        for lbl in self.placeholder_labels:
            lbl.setVisible(not has_any_schedule)

    def _sync_panel_scroll_heights(self):
        for day_index, panel in enumerate(self.bottom_panels):
            layout = panel.layout()
            if layout is not None:
                card_count = sum(
                    1
                    for item_index in range(layout.count())
                    if isinstance(
                        layout.itemAt(item_index).widget(),
                        WeekScheduleCard,
                    )
                )
                self.bottom_scroll_areas[day_index].set_card_count(card_count)

    def update_weather_ui(self, data):
        if not data: return
        icon_code = data['icon']
        svg_path = f"assets/weather/{icon_code}-fill.svg"
        
        self.lbl_weather_icon.set_weather_icon(svg_path)
            
        self.lbl_temp.setText(f"{data['temp']}°C")
        tooltip = f"{data['city']}: {data['text']} {data['temp']}°C"
        # 清除旧的气泡过滤器，防止重复绑定
        if hasattr(self.lbl_weather_icon, '_tooltip_filter'):
            self.lbl_weather_icon.removeEventFilter(self.lbl_weather_icon._tooltip_filter)
            self.lbl_temp.removeEventFilter(self.lbl_temp._tooltip_filter)
            self.lbl_weather_icon._tooltip_filter.deleteLater()
            self.lbl_temp._tooltip_filter.deleteLater()

        # 重新绑定新天气的气泡
        self.lbl_weather_icon._tooltip_filter = ToolTipFilter(tooltip, self.lbl_weather_icon)
        self.lbl_weather_icon.installEventFilter(self.lbl_weather_icon._tooltip_filter)
        
        self.lbl_temp._tooltip_filter = ToolTipFilter(tooltip, self.lbl_temp)
        self.lbl_temp.installEventFilter(self.lbl_temp._tooltip_filter)

    def _load_colored_svg(self, icon_path, color_hex, width, height):
        renderer = QSvgRenderer(icon_path)
        if not renderer.isValid(): return QPixmap()
        ratio = self.devicePixelRatio()
        pixel_width = int(width * ratio)
        pixel_height = int(height * ratio)
        pixmap = QPixmap(pixel_width, pixel_height)
        pixmap.fill(Qt.GlobalColor.transparent)
        pixmap.setDevicePixelRatio(ratio)
        painter = QPainter(pixmap)
        renderer.render(painter, QRectF(0, 0, width, height))
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(QRectF(0, 0, width, height), QColor(color_hex))
        painter.end()
        return pixmap

    def _go_prev_week(self):
        self.current_monday = self.current_monday.addDays(-7)
        self.refresh_week_data()

    def _go_next_week(self):
        self.current_monday = self.current_monday.addDays(7)
        self.refresh_week_data()

    def _begin_card_drag(self, card):
        self._active_drag_card = card
        self._drag_edge_direction = 0
        self._drag_edge_entered_at = 0.0
        self._drag_last_turn_at = 0.0
        for panel in self.bottom_panels:
            panel.current_drag_widget = card
        self._drag_edge_timer.start()

    def _finish_card_drag(self, card, result):
        if card is not self._active_drag_card:
            return
        if result != Qt.DropAction.MoveAction:
            QTimer.singleShot(0, lambda: self._cancel_card_drag(card))
            return
        QTimer.singleShot(250, lambda: self._cancel_card_drag(card))

    def _cancel_card_drag(self, card):
        if card is not self._active_drag_card:
            return
        self._clear_card_drag_state(delete_card=True)
        self.refresh_week_data()

    def _clear_card_drag_state(self, delete_card=False):
        card = self._active_drag_card
        self._active_drag_card = None
        self._drag_edge_timer.stop()
        self._drag_edge_direction = 0
        self._drag_edge_entered_at = 0.0
        self._drag_last_turn_at = 0.0
        for panel in self.bottom_panels:
            panel.current_drag_widget = None
        if delete_card and card is not None:
            card.hide()
            card.deleteLater()

    def _check_drag_week_edge(self):
        if self._active_drag_card is None:
            self._drag_edge_timer.stop()
            return

        local_pos = self.mapFromGlobal(QCursor.pos())
        if local_pos.y() < -30 or local_pos.y() > self.height() + 30:
            direction = 0
        elif local_pos.x() <= 28:
            direction = -1
        elif local_pos.x() >= self.width() - 28:
            direction = 1
        else:
            direction = 0

        now = time.monotonic()
        if direction != self._drag_edge_direction:
            self._drag_edge_direction = direction
            self._drag_edge_entered_at = now if direction else 0.0
            return
        if direction == 0:
            return
        if now - self._drag_edge_entered_at < 0.45:
            return
        if self._drag_last_turn_at and now - self._drag_last_turn_at < 0.7:
            return

        self._drag_last_turn_at = now
        self._drag_edge_entered_at = now
        self._turn_week_during_drag(direction)

    def _turn_week_during_drag(self, direction):
        if self._active_drag_card is None or direction not in (-1, 1):
            return
        days = direction * 7
        self.current_monday = self.current_monday.addDays(days)
        self.current_selected_date = self.current_selected_date.addDays(days)
        self.refresh_week_data()

    def _on_day_clicked(self, qdate):
        self.current_selected_date = qdate
        if hasattr(self, "page_week_timetable_placeholder"):
            self.page_week_timetable_placeholder.set_selected_day(qdate)
        self.refresh_week_data()

    def _on_day_double_clicked(self, qdate):
        self._on_day_clicked(qdate)
        self.day_double_clicked.emit(qdate)

    def _week_schedule_cards_by_day(self):
        cards_by_day = {}
        for day_index, panel in enumerate(self.bottom_panels):
            layout = panel.layout()
            cards_by_day[day_index] = [
                layout.itemAt(item_index).widget()
                for item_index in range(layout.count())
                if isinstance(
                    layout.itemAt(item_index).widget(),
                    WeekScheduleCard,
                )
            ]
        return cards_by_day

    def _week_schedule_cards(self):
        cards_by_day = self._week_schedule_cards_by_day()
        return [
            card
            for day_index in range(7)
            for card in cards_by_day[day_index]
        ]

    def is_week_multi_select_active(self):
        return self._week_multi_select_active

    def toggle_week_multi_select_mode(self):
        if self._week_multi_select_active:
            self.exit_week_multi_select_mode()
        else:
            self.enter_week_multi_select_mode()

    def _open_week_multi_select_popup(self):
        popup = self._week_multi_select_popup
        if popup is not None:
            try:
                popup.show_near(self)
                return
            except RuntimeError:
                self._week_multi_select_popup = None

        popup = ScheduleMultiSelectPopup("week", self)
        popup.day_scope_toggled.connect(
            self._toggle_week_multi_select_day
        )
        popup.action_requested.connect(
            self._handle_week_multi_select_action
        )
        popup.closed.connect(self._handle_week_multi_select_popup_closed)
        self._week_multi_select_popup = popup
        popup.show_near(self)

    def _handle_week_multi_select_popup_closed(self, popup):
        if self._week_multi_select_popup is popup:
            self._week_multi_select_popup = None
        if self._week_multi_select_active:
            self.exit_week_multi_select_mode(close_popup=False)

    def enter_week_multi_select_mode(self):
        if (
            self.schedule_display_mode != "card"
            or self.body_stack.currentWidget() is not self.page_week_board
        ):
            return
        cards = self._week_schedule_cards()
        if not cards:
            return
        self.close_view_selector()
        self._hide_week_query_panels()
        self._week_multi_select_active = True
        self._week_multi_select_days = set(range(7))
        self._week_selected_schedule_ids.clear()
        self._open_week_multi_select_popup()
        self._sync_week_multi_select_state()

    def exit_week_multi_select_mode(self, close_popup=True):
        if (
            not self._week_multi_select_active
            and self._week_multi_select_popup is None
        ):
            return
        self._week_multi_select_active = False
        self._week_selected_schedule_ids.clear()
        popup = self._week_multi_select_popup
        self._week_multi_select_popup = None
        if close_popup and popup is not None:
            try:
                popup.close()
            except RuntimeError:
                pass
        for card in self._week_schedule_cards():
            card.set_multi_select_state(False)

    def _toggle_week_multi_select_day(self, day_index):
        if not self._week_multi_select_active:
            return
        if day_index == 7:
            self._week_multi_select_days = (
                set()
                if len(self._week_multi_select_days) == 7
                else set(range(7))
            )
        elif 0 <= day_index < 7:
            if day_index in self._week_multi_select_days:
                self._week_multi_select_days.remove(day_index)
            else:
                self._week_multi_select_days.add(day_index)
        self._sync_week_multi_select_state()

    def _toggle_week_schedule_selection(self, schedule_id):
        if not self._week_multi_select_active:
            return
        if schedule_id in self._week_selected_schedule_ids:
            self._week_selected_schedule_ids.remove(schedule_id)
        else:
            self._week_selected_schedule_ids.add(schedule_id)
        self._sync_week_multi_select_state()

    def _sync_week_multi_select_state(self):
        cards_by_day = self._week_schedule_cards_by_day()
        cards = [
            card
            for day_index in range(7)
            for card in cards_by_day[day_index]
        ]
        visible_ids = {card.data.id for card in cards}
        active_drag_card = self._active_drag_card
        if active_drag_card is not None:
            active_drag_id = getattr(
                getattr(active_drag_card, "data", None),
                "id",
                None,
            )
            if active_drag_id is not None:
                visible_ids.add(active_drag_id)
        self._week_selected_schedule_ids.intersection_update(visible_ids)

        for card in cards:
            card.set_multi_select_state(
                self._week_multi_select_active,
                card.data.id in self._week_selected_schedule_ids,
            )

        if not self._week_multi_select_active:
            return

        scope_cards = [
            card
            for day_index in self._week_multi_select_days
            for card in cards_by_day.get(day_index, [])
        ]
        scope_ids = {card.data.id for card in scope_cards}
        selected_cards = [
            card
            for card in cards
            if card.data.id in self._week_selected_schedule_ids
        ]
        has_selection = bool(selected_cards)
        all_scope_selected = bool(scope_ids) and scope_ids.issubset(
            self._week_selected_schedule_ids
        )
        can_complete = has_selection and any(
            getattr(card.data, "status", 0) != 1
            for card in selected_cards
        )
        can_undo = has_selection and any(
            getattr(card.data, "status", 0) == 1
            for card in selected_cards
        )

        popup = self._week_multi_select_popup
        if popup is None:
            return
        popup.set_scope_state(
            self._week_multi_select_days
        )
        popup.set_action_state(
            has_scope_cards=bool(scope_ids),
            all_scope_selected=all_scope_selected,
            can_complete=can_complete,
            can_undo=can_undo,
            can_delete=has_selection,
        )

    def _handle_week_multi_select_action(self, action_id):
        if action_id == "exit":
            self.exit_week_multi_select_mode()
            return
        if not self._week_multi_select_active:
            return

        cards_by_day = self._week_schedule_cards_by_day()
        cards = [
            card
            for day_index in range(7)
            for card in cards_by_day[day_index]
        ]
        visible_ids = {card.data.id for card in cards}

        if action_id == "select_all":
            scope_ids = {
                card.data.id
                for day_index in self._week_multi_select_days
                for card in cards_by_day.get(day_index, [])
            }
            if not scope_ids:
                return
            if scope_ids.issubset(self._week_selected_schedule_ids):
                self._week_selected_schedule_ids.difference_update(scope_ids)
            else:
                self._week_selected_schedule_ids.update(scope_ids)
            self._sync_week_multi_select_state()
            return

        selected_ids = sorted(
            self._week_selected_schedule_ids & visible_ids
        )
        if not selected_ids:
            return

        if action_id == "complete":
            if not any(
                getattr(card.data, "status", 0) != 1
                for card in cards
                if card.data.id in selected_ids
            ):
                return
            success = db_manager.update_schedule_statuses(selected_ids, 1)
        elif action_id == "undo":
            if not any(
                getattr(card.data, "status", 0) == 1
                for card in cards
                if card.data.id in selected_ids
            ):
                return
            success = db_manager.update_schedule_statuses(selected_ids, 0)
        elif action_id == "delete":
            success = db_manager.delete_schedules(selected_ids)
            if success:
                self._week_selected_schedule_ids.difference_update(
                    selected_ids
                )
        else:
            return

        if success:
            self.refresh_week_data()
            self.schedule_updated.emit(None)

    def _handle_week_context_action(self, action_name):
        if action_name == "add":
            self.switch_to_add_page()
        elif action_name == "multiple_choice":
            self.toggle_week_multi_select_mode()

    def _handle_week_context_view(self, view_name):
        self._on_view_selected(view_name)

    def _handle_week_context_mode(self, mode_id):
        """右键菜单 → 模式切换（卡片/课表）"""
        self.set_schedule_display_mode(mode_id)

    def _show_week_header_context_menu(self, position):
        is_timetable = (
            getattr(self, "schedule_display_mode", "card") == "timetable"
        )
        menu = ActionContextMenu(
            self,
            show_drag_options=is_timetable,
            drag_snap_minutes=self.page_week_timetable_placeholder.edit_snap_minutes,
            show_multiple_choice=not is_timetable,
            multiple_choice_active=self._week_multi_select_active,
        )
        menu.action_requested.connect(self._handle_week_context_action)
        menu.view_requested.connect(self._handle_week_context_view)
        menu.mode_requested.connect(self._handle_week_context_mode)
        menu.drag_snap_requested.connect(self._handle_timetable_drag_snap_change)
        menu.exec(self.top_container.mapToGlobal(position))

    def mousePressEvent(self, event):
        # 如果视图选择器正开着，点窗口上半部分任何空白处都会关掉它
        if hasattr(self, 'view_selector_container') and self.view_selector_container.isVisible():
            self.close_view_selector()
        super().mousePressEvent(event)

    def _on_window_drag_started(self):
        self.close_view_selector()
        self._hide_week_query_panels()

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent

        # 暗色模式双击热区
        if hasattr(self, '_dark_mode_trigger') and obj is self._dark_mode_trigger:
            if event.type() == QEvent.Type.MouseButtonDblClick and event.button() == Qt.MouseButton.LeftButton:
                self._toggle_dark_mode()
                return True

        # 拦截底层 7 个面板的鼠标事件
        if hasattr(self, 'bottom_panels') and obj in self.bottom_panels:
            if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.RightButton:
                child = obj.childAt(event.pos())
                current = child
                while current is not None:
                    if isinstance(current, WeekScheduleCard):
                        return False
                    current = current.parentWidget()

                index = self.bottom_panels.index(obj)
                target_date = self.current_monday.addDays(index)
                self._on_day_clicked(target_date)

                menu = ActionContextMenu(
                    self,
                    show_multiple_choice=True,
                    multiple_choice_active=self._week_multi_select_active,
                )
                menu.action_requested.connect(self._handle_week_context_action)
                menu.view_requested.connect(self._handle_week_context_view)
                menu.mode_requested.connect(self._handle_week_context_mode)
                menu.exec(obj.mapToGlobal(event.pos()))
                return True

            if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                
                # 如果视图选择器正开着，点下半部分也会关掉它，并且不触发进入这一天的操作
                if hasattr(self, 'view_selector_container') and self.view_selector_container.isVisible():
                    self.close_view_selector()
                    return True

                # 找到被点击面板的索引 (0-6)
                index = self.bottom_panels.index(obj)
                
                # 根据索引，推算出对应的 QDate 并触发点击
                target_date = self.current_monday.addDays(index)
                self._on_day_clicked(target_date)
                return True # 拦截完毕，事件不再往下传
                
        return super().eventFilter(obj, event)

    def wheelEvent(self, event):
        """
        拦截鼠标滚轮事件：
        只在非编辑模式、且鼠标位于顶部导航区域时，允许使用滚轮切换上下周。
        """
        # 1. 如果当前正在添加/修改日程（处于其他堆栈页），不响应滚轮翻页
        if self.is_edit_mode or self.body_stack.currentWidget() not in (
            self.page_week_board,
            self.page_week_timetable_placeholder,
        ):
            super().wheelEvent(event)
            return

        # 2. 获取鼠标在窗口内的实时 Y 坐标
        mouse_y = event.position().y()

        # 3. 分区判定：鼠标是否在顶部区域 (top_container 内)
        if mouse_y < self.top_container.height():
            angle = event.angleDelta().y()
            if angle > 0:
                self._go_prev_week()  # 向上滚动，切换到上一周
            elif angle < 0:
                self._go_next_week()  # 向下滚动，切换到下一周
            event.accept() # 事件已处理，不再向下传递
        else:
            # 如果鼠标在下方列表区，把事件还给父类，让 QScrollArea 正常处理上下滑动
            super().wheelEvent(event)

    def _on_sort_clicked(self):
        """卡片模式打开排序设置；课表模式重置可见范围到当前时间。"""
        if getattr(self, "schedule_display_mode", "card") == "timetable":
            self.page_week_timetable_placeholder.reset_to_current_time()
            self.refresh_week_data()
            return
        self.toggle_sort_options_panel()

    def _toggle_dark_mode(self):
        """切换暗色模式并持久化"""
        self._dark_mode = not self._dark_mode
        QSettings("Lankor", "DesktopSchedule").setValue(
            "week/dark_mode", self._dark_mode
        )
        self._apply_dark_mode()

    def _apply_dark_mode(self):
        """根据 _dark_mode 状态更新所有 UI 元素"""
        dark = self._dark_mode
        bg = QColor("#2b2b2b") if dark else QColor("#FFFFFF")
        border_qcolor = QColor(255, 255, 255, 44) if dark else QColor(120, 120, 120, 72)
        border_color = "rgba(255, 255, 255, 44)" if dark else "rgba(120, 120, 120, 72)"

        self.top_container.setStyleSheet(f"""
            QWidget#week_top_surface {{
                background: transparent;
                border-top: 1px solid {border_color};
                border-left: 1px solid {border_color};
                border-right: 1px solid {border_color};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
        """)

        # content_area 背景与底部圆角描边
        self.content_area.set_surface_colors(bg, border_qcolor)

        # 卡片模式面板
        if hasattr(self, 'bottom_panels'):
            for i in range(len(self.bottom_panels)):
                iter_date = self.current_monday.addDays(i)
                self._apply_week_board_column_background(
                    i,
                    iter_date == self.current_selected_date,
                )

        # 课表模式
        if hasattr(self, 'page_week_timetable_placeholder'):
            self.page_week_timetable_placeholder.set_dark_mode(dark)

        # DayBlock 头部日期文字
        if hasattr(self, 'day_blocks'):
            for block in self.day_blocks:
                block.set_dark_mode(dark)

        # 卡片模式日程卡片
        if hasattr(self, 'bottom_panels'):
            for panel in self.bottom_panels:
                for card in panel.findChildren(WeekScheduleCard):
                    card.set_dark_mode(dark)

        # 强制刷新
        self._apply_week_header_foreground()
        self.update()

    def dark_mode(self):
        """供外部查询当前暗色模式状态"""
        return self._dark_mode

    def toggle_view_selector(self):
        """点击视图图标时，自动判断是展开还是收起"""
        if self.view_selector_container.isVisible():
            self.close_view_selector()
        else:
            self.open_view_selector()

    def open_view_selector(self):
        """隐藏搜索框，显示视图选择器，并高亮顶部视图图标"""
        self._hide_week_query_panels()
        self.search_box.hide()
        self.view_selector_container.show()
        self._apply_week_header_foreground()

    def close_view_selector(self):
        """隐藏视图选择器，恢复搜索框，并取消图标高亮"""
        self.view_selector_container.hide()
        self.search_box.show()
        self._apply_week_header_foreground()

    def _on_view_selected(self, vid):
        """处理视图点击事件"""
        self.close_view_selector()
        if vid == "week":
            pass # 当前已经在周视图，无操作
        else:
            self.exit_week_multi_select_mode()
            # 无论是日视图、月视图还是待办，统交由主路由处理
            self.view_selected.emit(vid)

    def _check_repeat_and_execute(self, schedule_data, update_callback):
        from PyQt6.QtWidgets import QMessageBox
        
        rule = getattr(schedule_data, 'repeat_rule', '')
        if rule and str(rule).strip() not in ["", "无", "none", "不重复"]:
            msg = QMessageBox(self)
            msg.setWindowTitle("修改重复日程")
            msg.setText(f"当前日程包含【{rule}】的重复规则。\n您的修改将会应用到该系列的所有日程。")
            
            msg.setStyleSheet("""
                QMessageBox { background-color: white; }
                QPushButton { padding: 6px 15px; border-radius: 4px; background-color: #f0f0f0; font-family: 'Microsoft YaHei'; }
                QPushButton:hover { background-color: #e0e0e0; }
            """)
            
            btn_all = msg.addButton("修改所有", QMessageBox.ButtonRole.AcceptRole)
            btn_single = msg.addButton("仅修改本次", QMessageBox.ButtonRole.ActionRole)
            btn_cancel = msg.addButton("取消", QMessageBox.ButtonRole.RejectRole)
            
            msg.exec()
            
            if msg.clickedButton() == btn_all:
                update_callback(True)   # 传 True: 修改未来的所有日程
            elif msg.clickedButton() == btn_single:
                update_callback(False)  # 传 False: 脱离队伍，仅修改当前这条
            else:
                pass 
        else:
            update_callback(False)

    # ==========================================
    # 右键菜单功能响应槽函数
    # ==========================================
    def _handle_schedule_status_change(self, schedule_id, new_status):
        """处理更改完成状态的请求"""
        if db_manager.update_schedule_status(schedule_id, new_status):
            self.refresh_week_data()         # 刷新当前周视图
            self.schedule_updated.emit(None) # 通知主界面也同步刷新

    def _handle_schedule_pin_change(self, schedule_id, current_pin_status):
        """处理更改置顶状态的请求"""
        if db_manager.toggle_pin_status(schedule_id, current_pin_status):
            self.refresh_week_data()
            self.schedule_updated.emit(None)

    def _handle_schedule_delete(self, schedule_id):
        """处理删除日程的请求"""
        if db_manager.delete_schedule(schedule_id):
            self.refresh_week_data()
            self.schedule_updated.emit(None)

    def _handle_timetable_color_changed(self, schedule_data, color):
        """课表模式下颜色变更：同步更新 board + 持久化"""
        from ..utils.timetable_preferences import set_timetable_schedule_color

        applied = self.page_week_timetable_placeholder.set_schedule_color(
            schedule_data, color,
        )
        if not applied.isValid():
            return
        set_timetable_schedule_color(
            getattr(schedule_data, "id", None),
            QColor(color).name(),
        )

    def _handle_timetable_time_changed(self, schedule_data, start_time, end_time):
        """课表模式下拖拽 / 拉伸修改时间。"""
        schedule_id = getattr(schedule_data, "id", None)
        if schedule_id is None:
            self.refresh_week_data()
            return

        if getattr(schedule_data, "group_id", None):
            success = db_manager.update_schedule_with_repeat(
                schedule_id,
                {
                    "start_time": start_time,
                    "end_time": end_time,
                },
                update_future=False,
            )
            if success:
                schedule_data.group_id = None
        else:
            success = db_manager.update_schedule_fields(
                schedule_id,
                start_time=start_time,
                end_time=end_time,
            )

        if not success:
            self.refresh_week_data()
            return

        schedule_data.start_time = start_time
        schedule_data.end_time = end_time
        selected_time = start_time or end_time
        if selected_time is None:
            self.refresh_week_data()
            return
        self.current_selected_date = QDate(
            selected_time.year,
            selected_time.month,
            selected_time.day,
        )
        self.current_monday = self._get_monday(self.current_selected_date)
        self.refresh_week_data()
        self.schedule_updated.emit(schedule_data)

    def _handle_timetable_week_turn_during_edit(
        self,
        direction,
        day_index,
        visible_start_hour,
    ):
        if direction not in (-1, 1):
            return
        if not hasattr(self, "page_week_timetable_placeholder"):
            return

        try:
            normalized_day_index = int(day_index)
        except (TypeError, ValueError):
            normalized_day_index = 0
        normalized_day_index = min(max(normalized_day_index, 0), 6)

        self.current_monday = self.current_monday.addDays(direction * 7)
        self.current_selected_date = self.current_monday.addDays(normalized_day_index)
        self.refresh_week_data()
        self.page_week_timetable_placeholder.set_visible_start_hour_for_day(
            normalized_day_index,
            visible_start_hour,
        )

    def _show_timetable_empty_area_context_menu(self, global_pos):
        """课表板空白区右键 → 页面级菜单"""
        from .common.action_context_menu import ActionContextMenu

        menu = ActionContextMenu(
            self,
            show_drag_options=True,
            drag_snap_minutes=self.page_week_timetable_placeholder.edit_snap_minutes,
        )
        menu.action_requested.connect(self._handle_week_context_action)
        menu.view_requested.connect(self._handle_week_context_view)
        menu.mode_requested.connect(self._handle_week_context_mode)
        menu.drag_snap_requested.connect(self._handle_timetable_drag_snap_change)
        menu.exec(global_pos)

    def _handle_timetable_drag_snap_change(self, minutes):
        self.page_week_timetable_placeholder.set_drag_snap_minutes(minutes)
        set_timetable_drag_snap_minutes(minutes)

    def _show_timetable_schedule_context_menu(self, schedule_obj, global_pos):
        from .components import ScheduleContextMenu

        menu = ScheduleContextMenu(schedule_obj, self)
        status = getattr(schedule_obj, "status", 0)
        is_completed = status == 1
        menu._add_centered_action(
            "撤销完成" if is_completed else "完成日程",
            "undo.svg" if is_completed else "check.svg",
            "#333333",
            lambda: self._handle_schedule_status_change(
                schedule_obj.id,
                0 if is_completed else 1,
            ),
        )
        if status == 1:
            menu._add_centered_action(
                "隐藏日程",
                "hide.svg",
                "#333333",
                lambda: self._handle_schedule_status_change(schedule_obj.id, 2),
            )
        menu.addSeparator()
        menu._add_centered_action(
            "删除日程",
            "delete.svg",
            "#333333",
            lambda: self._handle_schedule_delete(schedule_obj.id),
        )
        menu.exec(global_pos)

    def _handle_card_drop(self, dragged_id, target_index, col_index):
        panel_layout = self.bottom_panels[col_index].layout()
        
        # 1. 提取当前列被 Qt 物理挪位后的真实卡片顺序
        schedules = []
        for i in range(panel_layout.count() - 1): 
            widget = panel_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'data'):
                schedules.append(widget.data)
                
        dragged_item = next((s for s in schedules if s.id == dragged_id), None)
        if not dragged_item: 
            self._clear_card_drag_state(delete_card=True)
            self.refresh_week_data()
            return

        # ==========================================
        # 核心：跨天拖拽的时间平移逻辑
        # ==========================================
        target_date = self.current_monday.addDays(col_index).toPyDate()
        from datetime import datetime
        today = datetime.now().date()
        if target_date < today:
            self.show_toast("无法将日程移动到过去的日期！")
            self._clear_card_drag_state(delete_card=True)
            self.refresh_week_data() # 刷新看板，让被错误拖拽的卡片弹回原位
            return
        original_date = dragged_item.start_time.date() if dragged_item.start_time else (dragged_item.end_time.date() if dragged_item.end_time else None)
        
        if original_date and original_date != target_date:
            # 算出在界面上把它拖跨了几天
            days_diff = (target_date - original_date).days
            from datetime import timedelta, datetime
            
            # 平移所有时间点
            if dragged_item.start_time:
                dragged_item.start_time += timedelta(days=days_diff)
            if dragged_item.end_time:
                dragged_item.end_time += timedelta(days=days_diff)
            if dragged_item.reminder_time:
                dragged_item.reminder_time += timedelta(days=days_diff)
                
            dragged_item.group_id = None # 跨天拖拽视为脱离循环的单次修改
            dragged_item.created_at = datetime.now()
            
            # 存入数据库
            db_manager.update_schedule_fields(
                dragged_item.id, 
                start_time=dragged_item.start_time, 
                end_time=dragged_item.end_time,
                reminder_time=dragged_item.reminder_time,
                group_id=None,
                created_at=dragged_item.created_at
            )

        # ==========================================
        # 排序权重计算逻辑
        # ==========================================
        target_pin = getattr(dragged_item, 'is_pinned', False)
        target_status = getattr(dragged_item, 'status', 0)

        group_items = [s for s in schedules if getattr(s, 'is_pinned', False) == target_pin and getattr(s, 'status', 0) == target_status]

        if len(group_items) > 1:
            idx = group_items.index(dragged_item)
            if idx == 0:
                new_order = getattr(group_items[1], 'sort_order', 0.0) + 100.0
            elif idx == len(group_items) - 1:
                new_order = getattr(group_items[-2], 'sort_order', 0.0) - 100.0
            else:
                new_order = (getattr(group_items[idx-1], 'sort_order', 0.0) + getattr(group_items[idx+1], 'sort_order', 0.0)) / 2.0
        else:
            from datetime import datetime
            new_order = datetime.now().timestamp()
            
        db_manager.update_schedule_fields(dragged_item.id, sort_order=new_order)

        self._clear_card_drag_state()
        self.refresh_week_data()
        self.schedule_updated.emit(None) # 同步让主界面也刷新
