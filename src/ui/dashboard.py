# src/ui/dashboard.py
import datetime
import colorsys
import random
from types import SimpleNamespace
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QFrame, QSizePolicy,
                             QPushButton, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QTimer, QPointF, QRectF, QEvent
from PyQt6.QtGui import (QColor, QFont, QFontMetrics, QPainter, QPainterPath, QPen)

from ..data.database import db_manager
from ..config import AppConfig
from ..services.schedule_query_service import (
    ScheduleQueryOptions,
    ScheduleQueryService,
)
from ..services.schedule_sort_service import ScheduleSortService
from ..utils.timetable_preferences import (
    get_timetable_preferences,
    set_timetable_drag_snap_minutes,
    set_timetable_schedule_color,
)
from .schedule_detail_pop import ScheduleDetailPop
from .common.action_context_menu import ActionContextMenu

class DraggableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            window = self.window()
            self.drag_pos = event.globalPosition().toPoint() - window.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos:
            window = self.window()
            window.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None


class ViewSelectorCard(QFrame):
    """
    视图切换按键组：伪装成一个普通的日程卡片
    """
    view_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_view = "day"
        self.buttons_by_id = {}
        self.setFixedHeight(60) # 改成 60，和日程卡片的高度完全一致
        
        self.setStyleSheet("""
            ViewSelectorCard {
                background-color: rgba(255, 255, 255, 0.10);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.4);
            }
            QPushButton {
                background: transparent;
                color: white;
                font-family: 'Microsoft YaHei';
                font-size: 13px;
                font-weight: bold;
                border-radius: 6px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(5)

        # 定义四个视图按钮
        self.views = {
            "day": "日视图",
            "week": "周视图",
            "month": "月视图",
            "todo": "待办"
        }

        for view_id, view_name in self.views.items():
            btn = QPushButton(view_name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor) # 加个手型光标
            btn.clicked.connect(lambda checked, v=view_id: self.view_selected.emit(v))
            self.buttons_by_id[view_id] = btn
            layout.addWidget(btn)

        self.set_current_view(self.current_view)

    def _button_style(self, selected=False):
        if selected:
            return """
                QPushButton {
                    background: transparent;
                    color: white;
                    font-family: 'Microsoft YaHei';
                    font-size: 13px;
                    font-weight: bold;
                    border: none;
                    border-radius: 6px;
                    min-height: 34px;
                    padding: 0 8px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.12);
                }
            """
        return """
            QPushButton {
                background: transparent;
                color: rgba(255, 255, 255, 0.58);
                font-family: 'Microsoft YaHei';
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                min-height: 34px;
                padding: 0 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """

    def set_current_view(self, view_id):
        self.current_view = view_id
        for btn_view_id, btn in self.buttons_by_id.items():
            btn.setStyleSheet(self._button_style(btn_view_id == view_id))
        
class AdaptiveLabel(QLabel):
    def __init__(self, text="", parent=None, max_size=16, min_size=11):
        super().__init__(text, parent)
        self._original_text = text # 保存原始完整文本
        self.max_font_size = max_size
        self.min_font_size = min_size
        self.base_font = QFont('Microsoft YaHei', self.max_font_size)
        self.base_font.setBold(True)
        self.setFont(self.base_font)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.is_strike = False

    def setText(self, text):
        # 确保被外部更新文字时，记录下原本的内容
        self._original_text = text 
        super().setText(text)
        self.adjust_font_to_fit()

    def setStrikeOut(self, strike):
        self.is_strike = strike
        font = self.font()
        font.setStrikeOut(strike)
        self.setFont(font)

    def adjust_font_to_fit(self):
        available_width = self.width()
        if available_width <= 0: return
        
        # 始终根据原始文本去计算，而不是已经被截断成省略号的文本
        text = self._original_text 
        font = self.font()
        font.setStrikeOut(self.is_strike)
        
        # 尝试缩小字号以适应宽度
        for size in range(self.max_font_size, self.min_font_size - 1, -1):
            font.setPixelSize(size)
            fm = QFontMetrics(font)
            text_width = fm.horizontalAdvance(text)
            if text_width <= available_width:
                self.setFont(font)
                super().setText(text)
                return
                
        # 如果缩小到最小字号 (min_size) 还是超出宽度，则截取文字并添加三点省略号
        font.setPixelSize(self.min_font_size)
        self.setFont(font)
        fm = QFontMetrics(font)
        elided_text = fm.elidedText(text, Qt.TextElideMode.ElideRight, available_width)
        super().setText(elided_text)

    def resizeEvent(self, event):
        self.adjust_font_to_fit()
        super().resizeEvent(event)


class ScheduleCard(QFrame):
    """单个日程卡片"""
    req_delete = pyqtSignal(int)
    req_refresh = pyqtSignal()
    req_status = pyqtSignal(int, int)
    req_show_detail = pyqtSignal(object) # 请求显示详情弹窗的信号

    def __init__(self, schedule_data, parent=None):
        super().__init__(parent)
        self.data = schedule_data
        self.setFixedHeight(60) 
        self.setCursor(Qt.CursorShape.PointingHandCursor) # 增加鼠标手型
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        self.is_completed = (self.data.status == 1)
        self.is_expired = False
        
        now = datetime.datetime.now()
        if self.data.end_time and self.data.end_time < now and not self.is_completed:
            self.is_expired = True

        self._setup_ui()
        self._apply_state_style() 

        from .components import CountdownToolTipFilter
        self._tooltip_filter = CountdownToolTipFilter(self.data, self)
        self.installEventFilter(self._tooltip_filter)

    # 拦截左键点击，打开弹窗
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._click_pos = event.pos()
            event.accept() 
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not hasattr(self, '_click_pos'):
            return
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
            # 加上 "ScheduleCard" 类名，严格限制虚线只画在最外层，不感染内部容器
            self.setStyleSheet("ScheduleCard { background: transparent; border: 2px dashed rgba(255, 255, 255, 0.4); border-radius: 8px; }")
            
            # 遍历布局，暴力隐藏里面的所有东西（包括左容器、竖线、右容器）
            for i in range(self.layout().count()):
                if self.layout().itemAt(i).widget():
                    self.layout().itemAt(i).widget().hide()
            
            # 开始执行拖拽
            drag.exec(Qt.DropAction.MoveAction)
            
            # 拖拽结束，恢复样式，并把里面的东西全部显示回来
            self.setStyleSheet(original_style)
            for i in range(self.layout().count()):
                if self.layout().itemAt(i).widget():
                    self.layout().itemAt(i).widget().show()
                
            if hasattr(container, 'current_drag_widget'):
                container.current_drag_widget = None
            if hasattr(self, '_click_pos'): 
                del self._click_pos
            event.accept() 
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and hasattr(self, '_click_pos'):
            if (event.pos() - self._click_pos).manhattanLength() < 5:
                self.req_show_detail.emit(self.data)
            del self._click_pos 
            event.accept() 
        else:
            super().mouseReleaseEvent(event)

    def _apply_state_style(self):
        bg_color = "background-color: rgba(255, 255, 255, 0.10);"
        border_style = "border: 1px solid rgba(255, 255, 255, 0.4);"
        title_color = "white"
        time_color = "white"
        strike_out = False
        dot_opacity = 1.0

        if self.is_completed:
            bg_color = "background-color: rgba(255, 255, 255, 0.10);"
            if self.data.is_pinned:
                # 如果置顶了，保留实心白色边框
                border_style = "border: 1px solid white;"
            else:
                # 如果没置顶，沿用半透明边框
                border_style = "border: 1px solid rgba(255, 255, 255, 0.4);"
            title_color = "rgba(255, 255, 255, 0.5)"
            time_color = "rgba(255, 255, 255, 0.5)"
            strike_out = True
            dot_opacity = 1.0 

        elif self.is_expired:
            if self.data.is_pinned:
                border_style = "border: 1px solid white;"
            else:
                border_style = "border: 1px solid rgba(255, 255, 255, 0.4);"
            bg_color = "background-color: rgba(190, 190, 190, 0.7);"
            border_style = "border: 1px solid rgba(255, 255, 255, 0.4);"
            title_color = "rgba(255, 255, 255, 0.9)" 
            time_color = "#ff4d4f" 
            strike_out = False
            
        elif self.data.is_pinned:
            bg_color = "background-color: rgba(255, 255, 255, 0.2);"
            border_style = "border: 1px solid white;"

        self.setStyleSheet(f"""
            ScheduleCard {{
                {bg_color}
                border-radius: 8px;
                {border_style}
            }}
            ScheduleCard:hover {{
                background-color: rgba(255, 255, 255, 0.15);
            }}
            QLabel {{
                background-color: transparent;
                color: {title_color};
                font-family: 'Microsoft YaHei';
                border: none;
            }}
        """)
        
        self.lbl_title.setStrikeOut(strike_out)
        self.lbl_time.setStyleSheet(f"font-size: 10px; color: {time_color};")
        
        effect = self.priority_dot.graphicsEffect()
        if not effect: 
             from PyQt6.QtWidgets import QGraphicsOpacityEffect
             op = QGraphicsOpacityEffect(self.priority_dot)
             op.setOpacity(dot_opacity)
             self.priority_dot.setGraphicsEffect(op)
        else:
             effect.setOpacity(dot_opacity)

    def _show_context_menu(self, pos):
        from .components import ScheduleContextMenu
        
        menu = ScheduleContextMenu(self.data, self)
        menu.setup_actions(
            status_callback=lambda status: self.req_status.emit(self.data.id, status),
            pin_callback=lambda is_pinned: self._handle_pin_action(), # 沿用原有的置顶处理函数
            delete_callback=self._handle_delete_action
        )
        menu.exec(self.mapToGlobal(pos))

    def _handle_pin_action(self):
        if db_manager.toggle_pin_status(self.data.id, self.data.is_pinned):
            self.req_refresh.emit()

    def _handle_delete_action(self):
        if db_manager.delete_schedule(self.data.id):
            self.req_delete.emit(self.data.id)

    def _setup_ui(self):
        from .components import get_colored_icon
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 0, 15, 0)
        main_layout.setSpacing(10)

        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self.priority_dot = QLabel()
        self.priority_dot.setFixedSize(10, 10)
        p_color = {2: "#ff4d4f", 1: "#faad14", 0: "#52c41a"}.get(self.data.priority, "#52c41a")
        self.priority_dot.setStyleSheet(f"""
            background-color: {p_color};
            border-radius: 5px;
            border: 1px solid rgba(255,255,255,0.8);
        """)
        left_layout.addWidget(self.priority_dot)

        self.lbl_title = AdaptiveLabel(self.data.title, max_size=16, min_size=11)
        left_layout.addWidget(self.lbl_title, stretch=1)
        
        reminder_widget = QWidget()
        reminder_layout = QHBoxLayout(reminder_widget)
        reminder_layout.setContentsMargins(4, 0, 0, 0)
        reminder_layout.setSpacing(4)
        
        self.icon_bell = QLabel()
        self.icon_bell.setFixedSize(12, 12) 
        self.lbl_reminder = QLabel()

        icon_color = QColor(255, 255, 255, 127) if self.is_completed else QColor(255, 255, 255, 255)

        if self.data.reminder_time:
            self.icon_bell.setPixmap(get_colored_icon("alarm.svg", icon_color, 12))
            r_time = self.data.reminder_time
            base_dt = self.data.start_time if self.data.start_time else self.data.end_time
            time_str = r_time.strftime("%H:%M")
            
            if base_dt and r_time.date() < base_dt.date():
                self.lbl_reminder.setText(f"前一天\n{time_str}")
                self.lbl_reminder.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.lbl_reminder.setStyleSheet(f"font-size: 10px; color: {icon_color.name()}; font-weight: bold;")
            else:
                self.lbl_reminder.setText(time_str)
                self.lbl_reminder.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.lbl_reminder.setStyleSheet(f"font-size: 11px; color: {icon_color.name()}; font-weight: bold;")
        else:
            self.icon_bell.setPixmap(get_colored_icon("alarm_off.svg", icon_color, 12))
            self.lbl_reminder.setText("不提醒")
            self.lbl_reminder.setStyleSheet(f"font-size: 11px; color: {icon_color.name()};") 

        reminder_layout.addWidget(self.icon_bell)
        reminder_layout.addWidget(self.lbl_reminder)
        reminder_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        left_layout.addWidget(reminder_widget)

        line = QFrame()
        line.setFixedWidth(1)   
        line.setFixedHeight(40) 
        line.setStyleSheet(f"background-color: {icon_color.name()}; opacity: 0.6;")

        right_container = QWidget()
        right_container.setFixedWidth(60) 
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(2) 
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_time = QLabel()
        self.lbl_time.setStyleSheet(f"font-size: 10px; color: {icon_color.name()};") 
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.data.start_time and self.data.end_time:
            t_str = f"{self.data.start_time.strftime('%H:%M')}-{self.data.end_time.strftime('%H:%M')}"
        elif self.data.end_time:
            t_str = self.data.end_time.strftime('%H:%M')
        else:
            t_str = "全天"
        self.lbl_time.setText(t_str)
        
        repeat_container = QWidget()
        repeat_layout = QHBoxLayout(repeat_container)
        repeat_layout.setContentsMargins(0, 0, 0, 0)
        repeat_layout.setSpacing(4)
        repeat_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_repeat = QLabel()
        self.icon_repeat.setFixedSize(12, 12)
        self.lbl_repeat = QLabel()
        self.lbl_repeat.setStyleSheet(f"font-size: 11px; color: {icon_color.name()};padding-bottom: 2px;")

        rule = self.data.repeat_rule.strip()
        if rule and rule != "无" and rule != "none":
            self.icon_repeat.setPixmap(get_colored_icon("repeat.svg", icon_color, 12))
            self.lbl_repeat.setText(rule)
        else:
            self.icon_repeat.setPixmap(get_colored_icon("repeat_off.svg", icon_color, 12))
            self.lbl_repeat.setText("不重复")
            
        repeat_layout.addWidget(self.icon_repeat, 0, Qt.AlignmentFlag.AlignVCenter)
        repeat_layout.addWidget(self.lbl_repeat, 0, Qt.AlignmentFlag.AlignVCenter)

        right_layout.addWidget(self.lbl_time)
        right_layout.addWidget(repeat_container)

        main_layout.addWidget(left_container)
        main_layout.addWidget(line)
        main_layout.addWidget(right_container)

class TimetablePlaceholderFrame(QFrame):
    day_offset_requested = pyqtSignal(int)
    schedule_clicked = pyqtSignal(object, object)
    schedule_context_requested = pyqtSignal(object, object)
    empty_area_context_requested = pyqtSignal(object)
    schedule_time_changed = pyqtSignal(object, object, object)

    BORDER_WIDTH = 2
    CORNER_RADIUS = 8
    DIVIDER_WIDTH = 1
    TIME_AXIS_WIDTH = 40
    HOUR_COUNT = 24
    DAY_MINUTES = 24 * 60
    HOUR_ROW_HEIGHT = 57.0
    EVENT_GAP = 2.0
    EVENT_BLOCK_COLUMN_GAP = 2.0
    EVENT_COLUMN_GAP = 1.0
    GRID_LEFT_INSET = 0.0
    GRID_RIGHT_INSET = 2.0
    EVENT_RADIUS = 3.0
    DDL_LINE_HEIGHT = 3.0
    EDIT_EDGE_HANDLE_PX = 10.0
    EDIT_SNAP_MINUTES = 1
    EDIT_MIN_DURATION_MINUTES = 5
    EDIT_AUTO_SCROLL_MARGIN_PX = 24.0
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
        self.visible_start_minutes = self._default_visible_start_minutes()
        self.current_date = datetime.date.today()
        self.schedules = []
        self.category_map = {}
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
        self._hovered_schedule = None
        self._pressed_schedule = None
        self._pending_time_edit = None
        self._active_time_edit = None
        self._last_time_edit_pos = None
        self._hover_preview = None
        self._time_edit_hint = self._create_time_edit_hint()
        try:
            from .popups.schedule_axis_board import _AxisSchedulePreview

            self._hover_preview = _AxisSchedulePreview(False)
        except Exception:
            self._hover_preview = None
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setMouseTracking(True)
        self._time_edit_scroll_timer = QTimer(self)
        self._time_edit_scroll_timer.setInterval(self.EDIT_AUTO_SCROLL_INTERVAL_MS)
        self._time_edit_scroll_timer.timeout.connect(
            self._handle_time_edit_auto_scroll
        )
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
            self.destroyed.connect(lambda: app.removeEventFilter(self))

    def _default_visible_start_minutes(self):
        now = datetime.datetime.now()
        return now.hour * 60

    def reset_to_current_time(self):
        self.visible_start_minutes = self._default_visible_start_minutes()
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

    def set_schedule_data(self, current_date, schedules, category_map=None):
        self.current_date = current_date
        self.schedules = list(schedules or [])
        self.category_map = dict(category_map or {})
        self._ensure_schedule_colors(self.schedules)
        if (
            self._selected_schedule_id is not None
            and self._selected_schedule_id
            not in {self._schedule_id(schedule) for schedule in self.schedules}
        ):
            self._selected_schedule_id = None
        self._hide_hover_preview()
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta == 0:
            event.ignore()
            return

        step_minutes = -60 if delta > 0 else 60
        next_start_minutes = self.visible_start_minutes + step_minutes
        day_offset = 0
        if next_start_minutes >= self.DAY_MINUTES:
            next_start_minutes -= self.DAY_MINUTES
            day_offset = 1
        elif next_start_minutes < 0:
            next_start_minutes += self.DAY_MINUTES
            day_offset = -1

        self.visible_start_minutes = next_start_minutes
        self._hide_hover_preview()
        self.update()
        if day_offset:
            self.day_offset_requested.emit(day_offset)
        event.accept()

    def _format_minutes(self, total_minutes):
        total_minutes = int(total_minutes) % self.DAY_MINUTES
        return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"

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
            color = QColor(
                round(red * 255),
                round(green * 255),
                round(blue * 255),
            )
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
        if TimetablePlaceholderFrame._is_completed(schedule):
            return False
        end_time = getattr(schedule, "end_time", None)
        return bool(end_time and end_time < datetime.datetime.now())

    @staticmethod
    def _is_active_now(schedule):
        if (
            TimetablePlaceholderFrame._is_completed(schedule)
            or TimetablePlaceholderFrame._is_expired(schedule)
        ):
            return False
        start_time = getattr(schedule, "start_time", None)
        end_time = getattr(schedule, "end_time", None)
        if start_time is None or end_time is None or start_time == end_time:
            return False
        if start_time > end_time:
            start_time, end_time = end_time, start_time
        now = datetime.datetime.now()
        return start_time <= now <= end_time

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
        self._hide_time_edit_hint()
        if self._selected_schedule_id is not None:
            self._selected_schedule_id = None
            self.update()

    def _schedule_region_at_position(self, position):
        for region in reversed(self._hit_regions):
            if region["rect"].contains(position):
                return region
        return None

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
        return date_time.strftime("%m-%d %H:%M")

    @staticmethod
    def _format_time_edit_range(start_time, end_time):
        return f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"

    def _show_time_edit_hint(self, edit_state, start_time, end_time, position):
        if self._time_edit_hint is None:
            return

        action_text = {
            "resize_start": f"开始 {self._format_time_edit_point(start_time)}",
            "resize_end": f"结束 {self._format_time_edit_point(end_time)}",
            "move": "移动日程",
            "move_point": f"移动到 {self._format_time_edit_point(end_time)}",
        }.get(edit_state.get("action"), "调整日程")
        if edit_state.get("action") == "move_point":
            detail_text = end_time.strftime("%H:%M")
        else:
            detail_text = self._format_time_edit_range(start_time, end_time)
        self._time_edit_hint.setText(f"{action_text}\n{detail_text}")
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
                action != "move_point" or end_time is None or start_time == end_time
            ),
            "update_end_time": end_time is not None,
            "visible_start_minutes": self.visible_start_minutes,
            "changed": False,
        }

    def _snap_minutes(self, raw_minutes):
        snap = max(1, int(getattr(self, "edit_snap_minutes", self.EDIT_SNAP_MINUTES)))
        return int(round(raw_minutes / snap) * snap)

    def _snapped_delta_minutes(self, delta_pixels, scroll_delta_minutes=0.0):
        raw_minutes = (
            delta_pixels / max(1.0, self.HOUR_ROW_HEIGHT) * 60.0
            + scroll_delta_minutes
        )
        return self._snap_minutes(raw_minutes)

    def _apply_time_edit_preview(self, edit_state, position):
        if edit_state is None:
            return

        schedule = edit_state["schedule"]
        scroll_delta = self.visible_start_minutes - edit_state["visible_start_minutes"]
        delta_minutes = self._snapped_delta_minutes(
            position.y() - edit_state["press_pos"].y(),
            scroll_delta,
        )
        min_duration = datetime.timedelta(minutes=self.EDIT_MIN_DURATION_MINUTES)
        original_start = edit_state["original_start"]
        original_end = edit_state["original_end"]

        if edit_state["action"] == "move":
            delta = datetime.timedelta(minutes=delta_minutes)
            next_start = original_start + delta
            next_end = original_end + delta
        elif edit_state["action"] == "move_point":
            delta = datetime.timedelta(minutes=delta_minutes)
            next_point = edit_state["original_point"] + delta
            next_start = next_point if edit_state["update_start_time"] else original_start
            next_end = next_point if edit_state["update_end_time"] else original_end
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
            next_start = original_start + datetime.timedelta(minutes=delta_minutes)
            next_end = original_end
            if next_end - next_start < min_duration:
                next_start = next_end - min_duration
        elif edit_state["action"] == "resize_end":
            next_start = original_start
            next_end = original_end + datetime.timedelta(minutes=delta_minutes)
            if next_end - next_start < min_duration:
                next_end = next_start + min_duration
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

        direction = self._time_edit_auto_scroll_direction(self._last_time_edit_pos)
        if direction == 0:
            self._time_edit_scroll_timer.stop()
            return

        next_start = self.visible_start_minutes + (
            direction * self.EDIT_AUTO_SCROLL_STEP_MINUTES
        )
        next_start = max(-self.DAY_MINUTES, min(self.DAY_MINUTES * 2, next_start))
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

    def _display_style_for_schedule(self, schedule):
        if self._is_completed(schedule):
            return {
                "fill": QColor(255, 255, 255, 238),
                "line": QColor(255, 255, 255, 245),
                "text": QColor(self._color_for_schedule(schedule)),
                "shadow": QColor(255, 255, 255, 0),
                "border": None,
            }
        if self._is_expired(schedule):
            color = QColor(156, 166, 171, 218)
            return {
                "fill": color,
                "line": color,
                "text": QColor(255, 255, 255, 238),
                "shadow": QColor(0, 0, 0, 95),
                "border": None,
            }

        color = self._color_for_schedule(schedule)
        return {
            "fill": color,
            "line": color,
            "text": QColor(255, 255, 255, 238),
            "shadow": QColor(0, 0, 0, 95),
            "border": QColor(255, 255, 255, 245),
        }

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

    def _minutes_from_current_date(self, date_time):
        if date_time is None:
            return None
        if isinstance(date_time, datetime.date) and not isinstance(date_time, datetime.datetime):
            date_time = datetime.datetime.combine(date_time, datetime.time())
        day_delta = (date_time.date() - self.current_date).days
        return (
            day_delta * self.DAY_MINUTES
            + date_time.hour * 60
            + date_time.minute
            + date_time.second / 60.0
        )

    def _minute_to_y(self, minute_value, visible_start, top):
        return top + (
            (minute_value - visible_start) / 60.0
        ) * self.HOUR_ROW_HEIGHT

    def _build_visible_items(self, visible_start, visible_end):
        all_intervals = []
        ddl_points = []
        for schedule in self.schedules:
            if getattr(schedule, "status", 0) == 2:
                continue
            if ScheduleQueryService.is_todo(schedule):
                continue

            start_minutes = self._minutes_from_current_date(
                getattr(schedule, "start_time", None)
            )
            end_minutes = self._minutes_from_current_date(
                getattr(schedule, "end_time", None)
            )

            if start_minutes is not None and end_minutes is not None and start_minutes != end_minutes:
                interval_start = min(start_minutes, end_minutes)
                interval_end = max(start_minutes, end_minutes)
                all_intervals.append(
                    {
                        "schedule": schedule,
                        "start": interval_start,
                        "end": interval_end,
                        "visible_start": max(interval_start, visible_start),
                        "visible_end": min(interval_end, visible_end),
                    }
                )
                continue

            point_minutes = end_minutes if end_minutes is not None else start_minutes
            if point_minutes is None:
                continue
            if visible_start <= point_minutes <= visible_end:
                ddl_points.append(
                    {
                        "schedule": schedule,
                        "point": point_minutes,
                    }
                )

        visible_intervals = [
            interval
            for interval in self._layout_interval_groups(all_intervals)
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

    def _draw_interval_items(
        self,
        painter,
        intervals,
        visible_start,
        top,
        bottom,
        grid_left,
        grid_width,
    ):
        ordered_intervals = sorted(
            intervals,
            key=lambda item: self._is_active_time_edit_schedule(item["schedule"]),
        )
        for interval in ordered_intervals:
            column_count = interval["column_count"]
            column_gap = self.EVENT_BLOCK_COLUMN_GAP
            available_width = max(
                1.0,
                grid_width - column_gap * (column_count + 1),
            )
            rect_width = max(1.0, available_width / column_count)
            rect_x = grid_left + column_gap + interval["column"] * (
                rect_width + column_gap
            )
            if self._is_active_time_edit_schedule(interval["schedule"]):
                rect_x = self._active_time_edit["locked_left"]
                rect_width = self._active_time_edit["locked_width"]
            rect_y = self._minute_to_y(interval["visible_start"], visible_start, top)
            rect_bottom = self._minute_to_y(interval["visible_end"], visible_start, top)
            rect_y = max(top + self.EVENT_GAP, rect_y + self.EVENT_GAP)
            rect_bottom = min(bottom - self.EVENT_GAP, rect_bottom - self.EVENT_GAP)
            rect_height = max(3.0, rect_bottom - rect_y)
            if rect_height <= 0:
                continue

            event_rect = QRectF(rect_x, rect_y, rect_width, rect_height)
            event_path = QPainterPath()
            event_path.addRoundedRect(
                event_rect,
                self.EVENT_RADIUS,
                self.EVENT_RADIUS,
            )
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

        title_font = painter.font()
        title_font.setFamily("Microsoft YaHei")
        title_font.setPixelSize(10)
        title_font.setBold(True)
        time_font = QFont(title_font)
        time_font.setPixelSize(9)
        time_font.setBold(False)
        title_metrics = QFontMetrics(title_font)
        time_metrics = QFontMetrics(time_font)
        title_height = title_metrics.height()
        time_height = time_metrics.height()
        line_gap = 1

        for item in self._visible_event_labels:
            rect = item["rect"]
            total_text_height = title_height + time_height + line_gap
            if rect.width() < 22 or rect.height() < total_text_height:
                continue

            title = str(getattr(item["schedule"], "title", "") or "未命名日程")
            time_text = self._format_schedule_time_text(item["schedule"])
            text_rect = rect.adjusted(4.0, 0.0, -4.0, 0.0)
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
                title_height,
            )
            time_rect = QRectF(
                text_rect.left(),
                group_top + title_height + line_gap,
                text_rect.width(),
                time_height,
            )
            display_style = item.get("style") or self._display_style_for_schedule(
                item["schedule"]
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
            painter.drawText(
                title_rect,
                Qt.AlignmentFlag.AlignCenter,
                title_text,
            )
            painter.setFont(time_font)
            painter.setPen(display_style["text"])
            painter.drawText(
                time_rect,
                Qt.AlignmentFlag.AlignCenter,
                time_text,
            )

    def _draw_ddl_items(
        self,
        painter,
        ddl_points,
        visible_start,
        top,
        bottom,
        grid_left,
        grid_width,
    ):
        points_by_minute = {}
        for ddl_point in ddl_points:
            point_key = round(ddl_point["point"] * 1000)
            points_by_minute.setdefault(point_key, []).append(ddl_point)

        for points in points_by_minute.values():
            points.sort(key=lambda item: getattr(item["schedule"], "id", 0))
            segment_count = max(1, len(points))
            segment_gap = self.EVENT_COLUMN_GAP
            available_width = max(
                1.0,
                grid_width - segment_gap * (segment_count + 1),
            )
            segment_width = max(1.0, available_width / segment_count)
            for point_index, ddl_point in enumerate(points):
                line_y = self._minute_to_y(ddl_point["point"], visible_start, top)
                line_y = min(
                    max(top + self.DDL_LINE_HEIGHT, line_y),
                    bottom - self.DDL_LINE_HEIGHT,
                )
                line_x = grid_left + segment_gap + point_index * (
                    segment_width + segment_gap
                )
                line_width = segment_width
                if self._is_active_time_edit_schedule(ddl_point["schedule"]):
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
                    top,
                    bottom,
                )

    def _queue_ddl_label(self, schedule, display_style, line_rect, top, bottom):
        font = QFont("Microsoft YaHei")
        font.setPixelSize(9)
        font.setBold(True)
        metrics = QFontMetrics(font)
        label_height = metrics.height()
        if line_rect.width() < 22:
            return

        label_bottom = line_rect.top() - 2.0
        label_top = label_bottom - label_height
        if label_top < top + 1 or label_bottom > bottom:
            return

        label_rect = QRectF(
            line_rect.left(),
            label_top,
            line_rect.width(),
            label_height,
        )
        for occupied_rect in self._occupied_label_rects:
            if label_rect.intersects(occupied_rect.adjusted(-1.0, -1.0, 1.0, 1.0)):
                return

        title = str(getattr(schedule, "title", "") or "未命名日程")
        time_text = self._format_schedule_time_text(schedule)
        text = f"{title} {time_text}".strip()
        elided_text = metrics.elidedText(
            text,
            Qt.TextElideMode.ElideRight,
            max(1, int(label_rect.width())),
        )
        self._visible_ddl_labels.append(
            {
                "rect": label_rect,
                "text": elided_text,
                "font": font,
                "style": display_style,
            }
        )
        self._occupied_label_rects.append(label_rect)

    def _draw_ddl_labels(self, painter):
        for item in self._visible_ddl_labels:
            rect = item["rect"]
            display_style = item["style"]
            painter.setFont(item["font"])
            if display_style["shadow"].alpha() > 0:
                painter.setPen(display_style["shadow"])
                painter.drawText(
                    rect.translated(0.8, 0.8),
                    Qt.AlignmentFlag.AlignCenter,
                    item["text"],
                )
            painter.setPen(display_style["text"])
            painter.drawText(
                rect,
                Qt.AlignmentFlag.AlignCenter,
                item["text"],
            )

    def _draw_current_time_line(self, painter, visible_start, visible_end, grid_left, grid_width, top):
        if self.current_date != datetime.date.today():
            return
        now = datetime.datetime.now()
        current_minutes = now.hour * 60 + now.minute + now.second / 60.0
        if not (visible_start <= current_minutes <= visible_end):
            return

        line_y = self._minute_to_y(current_minutes, visible_start, top)
        painter.save()
        pen = QPen(QColor(235, 238, 240, 215), 1)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setDashPattern([4, 4])
        painter.setPen(pen)
        painter.drawLine(
            QPointF(float(grid_left), float(line_y)),
            QPointF(float(grid_left + grid_width), float(line_y)),
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
            painter.drawRoundedRect(rect, self.EVENT_RADIUS, self.EVENT_RADIUS)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.SELECTION_COLOR)
        for rect in self._selected_ddl_rects:
            painter.drawRect(rect)
        painter.restore()

    def _global_pos_from_mouse_event(self, obj, event):
        if hasattr(event, "globalPosition"):
            return event.globalPosition().toPoint()
        if isinstance(obj, QWidget) and hasattr(event, "position"):
            return obj.mapToGlobal(event.position().toPoint())
        return None

    def _is_schedule_region_at_global_pos(self, global_pos):
        local_pos = self.mapFromGlobal(global_pos)
        if not self.rect().contains(local_pos):
            return False
        return self._schedule_region_at_position(QPointF(local_pos)) is not None

    def _event_targets_timetable(self, obj):
        while isinstance(obj, QWidget):
            if obj is self:
                return True
            obj = obj.parentWidget()
        return False

    def eventFilter(self, obj, event):
        if (
            event.type() == QEvent.Type.MouseButtonPress
            and event.button() == Qt.MouseButton.LeftButton
            and self._selected_schedule_id is not None
            and self.isVisible()
        ):
            global_pos = self._global_pos_from_mouse_event(obj, event)
            if global_pos is not None and not (
                self._event_targets_timetable(obj)
                and self._is_schedule_region_at_global_pos(global_pos)
            ):
                self._clear_selected_schedule()
        return super().eventFilter(obj, event)

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

        if self._maybe_activate_pending_time_edit(event.position()):
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
        schedule = self._schedule_at_position(QPointF(event.pos()))
        if schedule is None:
            self._clear_selected_schedule()
            self.empty_area_context_requested.emit(event.globalPos())
            event.accept()
            return

        self._set_selected_schedule(schedule)
        self._hide_hover_preview()
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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        if width <= self.TIME_AXIS_WIDTH + self.DIVIDER_WIDTH + self.BORDER_WIDTH * 2 or height <= 0:
            return

        line_color = QColor(222, 230, 234, 230)
        boundary_color = QColor(255, 255, 255, 245)
        content_left = float(self.BORDER_WIDTH)
        top = float(self.BORDER_WIDTH)
        right = float(width - self.BORDER_WIDTH)
        left_axis_right = content_left + float(self.TIME_AXIS_WIDTH)
        grid_left_x = (
            left_axis_right
            + float(self.DIVIDER_WIDTH)
            + float(self.GRID_LEFT_INSET)
        )
        grid_right = right - self.GRID_RIGHT_INSET
        bottom = float(height - self.BORDER_WIDTH)

        frame_line_width = 2
        frame_rect = QRectF(content_left, top, right - content_left, bottom - top)
        frame_path = QPainterPath()
        frame_path.addRoundedRect(
            frame_rect,
            float(self.CORNER_RADIUS),
            float(self.CORNER_RADIUS),
        )

        painter.save()
        painter.setClipPath(frame_path)
        painter.fillRect(
            int(round(content_left)),
            int(round(top)),
            max(0, int(round(left_axis_right - content_left))),
            max(0, int(round(bottom - top))),
            QColor(255, 255, 255, 26),
        )
        painter.restore()

        grid_height = max(1.0, bottom - top)
        visible_start_minutes = float(self.visible_start_minutes)
        visible_duration_minutes = grid_height / self.HOUR_ROW_HEIGHT * 60.0
        last_visible_minutes = visible_start_minutes + visible_duration_minutes

        painter.save()
        painter.setClipPath(frame_path)
        grid_left = int(round(grid_left_x))
        grid_width = max(0, int(round(grid_right - grid_left_x)))
        first_hour_minutes = (
            (self.visible_start_minutes + 59) // 60
        ) * 60
        self._hit_regions = []
        self._visible_event_labels = []
        self._visible_ddl_labels = []
        self._occupied_label_rects = []
        self._selected_interval_rects = []
        self._selected_ddl_rects = []
        intervals, ddl_points = self._build_visible_items(
            visible_start_minutes,
            last_visible_minutes,
        )
        self._draw_interval_items(
            painter,
            intervals,
            visible_start_minutes,
            top,
            bottom,
            float(grid_left),
            float(grid_width),
        )
        self._draw_ddl_items(
            painter,
            ddl_points,
            visible_start_minutes,
            top,
            bottom,
            float(grid_left),
            float(grid_width),
        )
        hour_minutes = first_hour_minutes
        while hour_minutes <= last_visible_minutes + 0.01:
            hour_y = top + (
                (hour_minutes - visible_start_minutes) / 60.0
            ) * self.HOUR_ROW_HEIGHT
            painter.fillRect(
                grid_left,
                int(round(hour_y)),
                grid_width,
                1,
                line_color,
            )
            hour_minutes += 60
        self._draw_current_time_line(
            painter,
            visible_start_minutes,
            last_visible_minutes,
            grid_left,
            grid_width,
            top,
        )
        self._draw_selected_schedule_overlays(painter)
        self._draw_ddl_labels(painter)
        self._draw_interval_labels(painter)
        painter.restore()

        painter.save()
        painter.setClipPath(frame_path)
        painter.setPen(line_color)
        font = painter.font()
        font.setFamily("Microsoft YaHei")
        font.setPixelSize(11)
        painter.setFont(font)
        text_x = int(round(content_left))
        text_width = max(1, int(round(self.TIME_AXIS_WIDTH)))
        text_height = 14
        hour_minutes = first_hour_minutes
        while hour_minutes <= last_visible_minutes + 0.01:
            hour_y = top + (
                (hour_minutes - visible_start_minutes) / 60.0
            ) * self.HOUR_ROW_HEIGHT
            text_y = hour_y + 3.0
            if text_y + text_height > bottom:
                hour_minutes += 60
                continue
            painter.drawText(
                text_x,
                int(round(text_y)),
                text_width,
                text_height,
                Qt.AlignmentFlag.AlignCenter,
                self._format_minutes(hour_minutes),
            )
            hour_minutes += 60

        painter.fillRect(
            int(round(left_axis_right)),
            int(round(top)),
            self.DIVIDER_WIDTH,
            max(0, int(round(bottom - top))),
            line_color,
        )
        painter.restore()

        painter.setPen(QPen(boundary_color, frame_line_width))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(
            frame_rect.adjusted(
                frame_line_width / 2,
                frame_line_width / 2,
                -frame_line_width / 2,
                -frame_line_width / 2,
            ),
            float(self.CORNER_RADIUS),
            float(self.CORNER_RADIUS),
        )

from .todo import TodoListContainer
class DashboardView(QWidget):
    req_edit_time = pyqtSignal(object, str)
    req_edit_alarm = pyqtSignal(object, str) 
    req_edit_list = pyqtSignal(object, str)
    req_refresh_all = pyqtSignal()
    context_action_requested = pyqtSignal(str)
    context_view_requested = pyqtSignal(str)
    context_mode_requested = pyqtSignal(str)
    date_change_requested = pyqtSignal(object)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_pos = None 
        self.open_popups = []
        self.schedule_display_mode = "card"
        
        self.current_date = datetime.date.today()
        self._filter_options = ScheduleQueryOptions()
        self._search_options = None
        self._search_keyword = ""
        self._last_search_scope = "title"
        self._last_match_mode = "fuzzy"
        self._card_schedule_source = []
        self._timetable_schedule_source = []
        self._schedule_category_map = {}
        
        self._setup_ui()
        
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000) 
        
        self.refresh_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 20)
        layout.setSpacing(8)

        # 实例化视图选择器，并放置在主布局的最上方，默认隐藏
        self.view_selector = ViewSelectorCard(self)
        self.view_selector.hide()
        layout.addWidget(self.view_selector)

        self.lbl_empty = QLabel("您还没有日程记录，请点击添加")
        self.lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            font-size: 16px;
            font-family: 'Microsoft YaHei';
        """)
        layout.addWidget(self.lbl_empty)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        
        self.scroll_content = TodoListContainer(self) 
        self.scroll_content.card_dropped.connect(self._handle_card_drop)
        self.scroll_content.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.scroll_content.setStyleSheet("background: transparent;")
        
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8) 
        self.list_layout.addStretch()
        
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area, stretch=1)

        self.timetable_placeholder = TimetablePlaceholderFrame()
        self.timetable_placeholder.setObjectName("TimetablePlaceholderFrame")
        self.timetable_placeholder.day_offset_requested.connect(
            self._handle_timetable_day_offset
        )
        self.timetable_placeholder.schedule_clicked.connect(
            self._show_timetable_detail_popup
        )
        self.timetable_placeholder.schedule_time_changed.connect(
            self._handle_timetable_time_changed
        )
        self.timetable_placeholder.schedule_context_requested.connect(
            self._show_timetable_context_menu
        )
        self.timetable_placeholder.empty_area_context_requested.connect(
            self._show_dashboard_context_menu
        )
        self.timetable_placeholder.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.timetable_placeholder.setStyleSheet("background: transparent; border: none;")
        self.timetable_placeholder.hide()
        layout.addWidget(self.timetable_placeholder, stretch=1)

        self.lbl_empty.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.lbl_empty.customContextMenuRequested.connect(self._show_context_menu_for_empty)

        self.scroll_content.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.scroll_content.customContextMenuRequested.connect(self._show_context_menu_for_scroll_content)

    # 增加一个供外部调用的切换方法
    def toggle_view_selector(self):
        if self.view_selector.isVisible():
            self.view_selector.hide()
        else:
            self.view_selector.show()

    def set_schedule_display_mode(self, mode_id):
        if mode_id not in {"card", "timetable"}:
            return
        entering_timetable = (
            mode_id == "timetable"
            and self.schedule_display_mode != "timetable"
        )
        self.schedule_display_mode = mode_id
        if entering_timetable:
            self.timetable_placeholder.reset_to_current_time()
        self._sync_schedule_area_visibility()

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
        self._render_query_results()

    def apply_search_options(self, options):
        self._search_options = options
        self._last_search_scope = options.search_scope
        self._last_match_mode = options.match_mode
        if self._search_keyword:
            self._render_query_results()

    def set_search_keyword(self, keyword):
        normalized_keyword = str(keyword or "").strip()
        if normalized_keyword:
            if self._search_options is None:
                self._search_options = self.search_options_for_panel()
            self._search_keyword = normalized_keyword
        else:
            self._search_keyword = ""
            self._search_options = None
        self._render_query_results()

    def has_active_filter(self):
        return self._filter_options.has_filter_constraints()

    def has_active_query(self):
        return bool(self._search_keyword) or self.has_active_filter()

    def _apply_schedule_query(self, schedules):
        if self._search_keyword:
            options = self._search_options or self.search_options_for_panel()
            return ScheduleQueryService.apply_options(
                schedules,
                options,
                self._search_keyword,
            )
        return ScheduleQueryService.apply_options(
            schedules,
            self._filter_options,
        )

    def _clear_schedule_cards(self):
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _render_card_query_results(self):
        self._clear_schedule_cards()
        dashboard_schedules = self._apply_schedule_query(self._card_schedule_source)
        dashboard_schedules = ScheduleSortService.sort_for_day_view(dashboard_schedules)

        for index, item in enumerate(dashboard_schedules):
            card = ScheduleCard(item)
            card.req_delete.connect(self._remove_card_from_view)
            card.req_refresh.connect(self.refresh_data)
            card.req_refresh.connect(self.req_refresh_all.emit)
            card.req_status.connect(self._handle_status_change)
            card.req_show_detail.connect(self._show_detail_popup)
            self.list_layout.insertWidget(index, card)

        self.lbl_empty.setText(
            "没有符合条件的日程"
            if self.has_active_query()
            else "您还没有日程记录，请点击添加"
        )
        self._sync_schedule_area_visibility(bool(dashboard_schedules))

    def _render_timetable_query_results(self):
        timetable_schedules = self._apply_schedule_query(
            self._timetable_schedule_source
        )
        self.timetable_placeholder.set_schedule_data(
            self.current_date,
            timetable_schedules,
            self._schedule_category_map,
        )

    def _render_query_results(self):
        self._render_card_query_results()
        self._render_timetable_query_results()

    def reset_timetable_to_current_time(self):
        self.timetable_placeholder.reset_to_current_time()

    def _handle_timetable_day_offset(self, offset_days):
        self.date_change_requested.emit(
            self.current_date + datetime.timedelta(days=offset_days)
        )

    def _show_timetable_detail_popup(self, schedule_data, timetable_color):
        self._show_detail_popup(
            schedule_data,
            source_view="dashboard",
            timetable_color=timetable_color,
        )

    def _show_timetable_context_menu(self, schedule_data, global_pos):
        from .components import ScheduleContextMenu

        menu = ScheduleContextMenu(schedule_data, self)
        is_completed = TimetablePlaceholderFrame._is_completed(schedule_data)
        menu._add_centered_action(
            "撤销完成" if is_completed else "完成日程",
            "undo.svg" if is_completed else "check.svg",
            "#333333",
            lambda: self._handle_timetable_status_change(
                schedule_data,
                0 if is_completed else 1,
            ),
        )
        if is_completed:
            menu._add_centered_action(
                "隐藏日程",
                "hide.svg",
                "#333333",
                lambda: self._handle_timetable_status_change(schedule_data, 2),
            )
        menu.addSeparator()
        menu._add_centered_action(
            "删除日程",
            "delete.svg",
            "#333333",
            lambda: self._handle_timetable_delete(schedule_data),
        )
        menu.exec(global_pos)

    def _handle_timetable_status_change(self, schedule_data, status):
        schedule_id = getattr(schedule_data, "id", None)
        if schedule_id is None:
            return
        if db_manager.update_schedule_status(schedule_id, status):
            self.refresh_data()
            self.req_refresh_all.emit()

    def _handle_timetable_time_changed(self, schedule_data, start_time, end_time):
        schedule_id = getattr(schedule_data, "id", None)
        if schedule_id is None:
            self.refresh_data()
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
            self.refresh_data()
            return

        schedule_data.start_time = start_time
        schedule_data.end_time = end_time
        for popup in self.open_popups:
            if getattr(getattr(popup, "data", None), "id", None) == schedule_id:
                popup.data.start_time = start_time
                popup.data.end_time = end_time
                if hasattr(popup, "refresh_time_display"):
                    popup.refresh_time_display()
        self.refresh_data()
        self.req_refresh_all.emit()

    def _handle_timetable_delete(self, schedule_data):
        schedule_id = getattr(schedule_data, "id", None)
        if schedule_id is None:
            return
        if db_manager.delete_schedule(schedule_id):
            set_timetable_schedule_color(schedule_id, None)
            self.refresh_data()
            self.req_refresh_all.emit()

    def _handle_timetable_color_changed(self, schedule_data, color):
        applied_color = self.timetable_placeholder.set_schedule_color(
            schedule_data,
            color,
        )
        if not applied_color.isValid():
            return

        set_timetable_schedule_color(
            getattr(schedule_data, "id", None),
            QColor(color).name(),
        )
        for popup in self.open_popups:
            if (
                getattr(getattr(popup, "data", None), "id", None)
                == getattr(schedule_data, "id", None)
                and hasattr(popup, "set_timetable_color")
            ):
                popup.set_timetable_color(applied_color)

    def _sync_schedule_area_visibility(self, has_cards=None):
        if self.schedule_display_mode == "timetable":
            self.lbl_empty.hide()
            self.scroll_area.hide()
            self.timetable_placeholder.show()
            self.timetable_placeholder.update()
            return

        self.timetable_placeholder.hide()
        if has_cards is None:
            has_cards = self.list_layout.count() > 1
        if has_cards:
            self.lbl_empty.hide()
            self.scroll_area.show()
        else:
            self.lbl_empty.show()
            self.scroll_area.hide()

    def _show_context_menu_for_empty(self, pos):
        global_pos = self.lbl_empty.mapToGlobal(pos)
        self._show_dashboard_context_menu(global_pos)

    def _show_context_menu_for_scroll_content(self, pos):
        child = self.scroll_content.childAt(pos)
        if self._is_schedule_card_hit(child):
            return
        global_pos = self.scroll_content.mapToGlobal(pos)
        self._show_dashboard_context_menu(global_pos)

    def _is_schedule_card_hit(self, widget):
        current = widget
        while current is not None:
            if isinstance(current, ScheduleCard):
                return True
            current = current.parentWidget()
        return False

    def _show_dashboard_context_menu(self, global_pos):
        menu = ActionContextMenu(
            self,
            show_drag_options=self.schedule_display_mode == "timetable",
            drag_snap_minutes=self.timetable_placeholder.edit_snap_minutes,
        )
        menu.action_requested.connect(self.context_action_requested.emit)
        menu.view_requested.connect(self.context_view_requested.emit)
        menu.mode_requested.connect(self.context_mode_requested.emit)
        menu.drag_snap_requested.connect(self._handle_timetable_drag_snap_change)
        menu.exec(global_pos)

    def _handle_timetable_drag_snap_change(self, minutes):
        self.timetable_placeholder.set_drag_snap_minutes(minutes)
        set_timetable_drag_snap_minutes(minutes)

    def refresh_data(self):
        schedules = db_manager.get_schedules_for_date(self.current_date)
        timetable_schedules = list(schedules)
        seen_timetable_ids = {
            getattr(schedule, "id", id(schedule))
            for schedule in timetable_schedules
        }
        for schedule in db_manager.get_schedules_for_date(
            self.current_date + datetime.timedelta(days=1)
        ):
            schedule_id = getattr(schedule, "id", id(schedule))
            if schedule_id in seen_timetable_ids:
                continue
            timetable_schedules.append(schedule)
            seen_timetable_ids.add(schedule_id)

        def visible_schedules(source):
            return [
                schedule
                for schedule in source
                if getattr(schedule, "status", 0) != 2
                and not ScheduleQueryService.is_todo(schedule)
            ]

        self._card_schedule_source = visible_schedules(schedules)
        self._timetable_schedule_source = visible_schedules(timetable_schedules)
        self._schedule_category_map = db_manager.get_category_map()
        self._render_query_results()

    # 弹出并管理详情面板
    def _show_detail_popup(
        self,
        schedule_data,
        source_view="dashboard",
        initial_pinned=None,
        timetable_color=None,
        on_timetable_color_changed=None,
        dark_mode=False,
    ):
        for p in self.open_popups:
            if p.data.id == schedule_data.id:
                if timetable_color is not None and hasattr(p, "set_timetable_color"):
                    p.set_timetable_color(timetable_color)
                p.show()
                p.raise_()
                p.activateWindow()
                return

        # 把参数传给弹窗实例
        pop = ScheduleDetailPop(schedule_data, source_view=source_view, dark_mode=dark_mode)
        if timetable_color is not None and hasattr(pop, "set_timetable_color"):
            pop.set_timetable_color(timetable_color)
        if initial_pinned is None:
            initial_pinned = bool(
                self.window().windowFlags() & Qt.WindowType.WindowStaysOnTopHint
            )
        pop.set_pinned(initial_pinned)
        pop.schedule_updated.connect(self.refresh_data)
        pop.schedule_updated.connect(self.req_refresh_all.emit) 
        
        pop.req_edit_time.connect(lambda data, sv=source_view: self.req_edit_time.emit(data, sv))
        pop.req_edit_alarm.connect(lambda data, sv=source_view: self.req_edit_alarm.emit(data, sv)) 
        pop.req_edit_list.connect(lambda data, sv=source_view: self.req_edit_list.emit(data, sv))
        if hasattr(pop, "timetable_color_changed"):
            if on_timetable_color_changed is not None:
                pop.timetable_color_changed.connect(on_timetable_color_changed)
            else:
                pop.timetable_color_changed.connect(self._handle_timetable_color_changed)
        pop.popup_closed.connect(self._remove_detail_popup)
        self.open_popups.append(pop)
        
        pos = self.mapToGlobal(QPoint(self.width() + 10, 0))
        pop.move(pos)
        pop.show()

    def _remove_detail_popup(self, popup):
        self.open_popups = [p for p in self.open_popups if p is not popup]

    def restore_detail_popups(self):
        for popup in tuple(self.open_popups):
            popup_pos = popup.pos()
            popup.hide()
            popup.show()
            popup.move(popup_pos)
            popup.raise_()

    def _remove_card_from_view(self, schedule_id):
        self._card_schedule_source = [
            schedule
            for schedule in self._card_schedule_source
            if getattr(schedule, "id", None) != schedule_id
        ]
        self._timetable_schedule_source = [
            schedule
            for schedule in self._timetable_schedule_source
            if getattr(schedule, "id", None) != schedule_id
        ]
        self._render_timetable_query_results()
        sender_card = self.sender()
        if sender_card:
            self.list_layout.removeWidget(sender_card)
            sender_card.deleteLater()
            self._sync_schedule_area_visibility(self.list_layout.count() > 1)
                
            # 删除日程后，发射全局刷新信号
            self.req_refresh_all.emit() 

    def _handle_status_change(self, schedule_id, new_status):
        if db_manager.update_schedule_status(schedule_id, new_status):
            self.refresh_data()
            
            # 勾选/取消完成状态后，发射全局刷新信号
            self.req_refresh_all.emit()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.window().pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos:
            self.window().move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def _handle_card_drop(self, dragged_id, target_index):
        # 从已被底层物理排序好的 layout 中直接提取最新顺序
        schedules = []
        for i in range(self.list_layout.count() - 1):
            widget = self.list_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'data'):
                schedules.append(widget.data)
                
        dragged_item = next((s for s in schedules if s.id == dragged_id), None)
        if not dragged_item: return

        # 身份识别，防止越界排序
        target_pin = getattr(dragged_item, 'is_pinned', False)
        target_status = getattr(dragged_item, 'status', 0)

        group_items = [s for s in schedules if getattr(s, 'is_pinned', False) == target_pin and getattr(s, 'status', 0) == target_status]

        if len(group_items) <= 1: return
        idx = group_items.index(dragged_item)

        # 计算最新的浮点排序权重
        if idx == 0:
            new_order = getattr(group_items[1], 'sort_order', 0.0) + 100.0
        elif idx == len(group_items) - 1:
            new_order = getattr(group_items[-2], 'sort_order', 0.0) - 100.0
        else:
            new_order = (getattr(group_items[idx-1], 'sort_order', 0.0) + getattr(group_items[idx+1], 'sort_order', 0.0)) / 2.0

        # 更新数据库并刷新
        db_manager.update_schedule_fields(dragged_item.id, sort_order=new_order)
        self.refresh_data()
        self.req_refresh_all.emit()
