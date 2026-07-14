# src/ui/main_window.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QApplication
from PyQt6.QtCore import Qt, QRectF, QTimer, QEvent, QPoint
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QLinearGradient, QColor, QPen
from qframelesswindow import FramelessMainWindow
from datetime import datetime, timedelta
import winsound

from .header import HeaderBar
from ..utils.win_api import apply_24h2_border_fix
from ..config import AppConfig
from .suspend_window import SuspendWindow
from .add_view import AddScheduleView
from .dashboard import DashboardView
from .time_picker import TimePickerView 
from .alarm_picker import AlarmPickerView 
from .list_picker import ListPickerView 
from .reminder_pop import ReminderPop 
from ..data.database import db_manager 
from ..utils.styles import StyleManager
from .month_window import MonthWindow
from .calendar_pop import CalendarPop
from .week_window import WeekWindow
from .suspend_window_week import SuspendWindowWeek
from .suspend_window_month import SuspendWindowMonth
from .todo import TodoView
from .schedule_detail_pop import ScheduleDetailPop
from .common.toast import show_center_toast
from ..services.reminder_service import ReminderService
from ..controllers.main_controller import MainController
from ..controllers.view_router import ViewRouter
from ..utils.signals import global_signals
from ..utils.window_preferences import (
    get_primary_pin_preference,
    set_primary_pin_preference,
    set_window_pin_state,
)
from ..utils.timetable_preferences import (
    get_timetable_preferences,
    set_timetable_display_mode,
)

class MainWindow(FramelessMainWindow):
    def __init__(self):
        super().__init__()
        self.main_controller = MainController()
        self.axis_board = None
        self.weather_board = None
        self.search_options_panel = None
        self.day_filter_panel = None
        self.todo_search_options_panel = None
        self.todo_filter_panel = None
        self._vertical_resize_margin = 8
        self._vertical_resize_edge = None
        self._vertical_resize_start_pos = QPoint()
        self._vertical_resize_start_geometry = None
        
        self.setFixedWidth(AppConfig.DEFAULT_WIDTH)
        self.setMinimumHeight(600) 
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        main_flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        if get_primary_pin_preference():
            main_flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(main_flags)
        self.titleBar.hide()
        self.setResizeEnabled(True)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

        self.header = HeaderBar(self)
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
        self.main_layout.addWidget(self.header)
        
        # --- 页面堆栈 ---
        self.body_stack = QStackedWidget()
        self.main_layout.addWidget(self.body_stack)

        # Page 0: 看板
        self.page_dashboard = DashboardView() 
        self.body_stack.addWidget(self.page_dashboard)

        # Page 1: 添加页
        self.page_add = AddScheduleView()
        self.body_stack.addWidget(self.page_add)
        
        # Page 2: 时间选择页
        self.page_time = TimePickerView()
        self.body_stack.addWidget(self.page_time)

        # Page 3: 提醒选择页
        self.page_alarm = AlarmPickerView()
        self.body_stack.addWidget(self.page_alarm)

        # Page 4: 清单选择页 
        self.page_list = ListPickerView()
        self.body_stack.addWidget(self.page_list)
        
        self.body_stack.setCurrentIndex(0)

        self.page_dashboard.view_selector.view_selected.connect(self.switch_view)
        self.page_dashboard.context_action_requested.connect(self._handle_dashboard_context_action)
        self.page_dashboard.context_view_requested.connect(self._handle_dashboard_context_view)
        self.page_dashboard.context_mode_requested.connect(self.set_schedule_display_mode)
        self.page_dashboard.date_change_requested.connect(self.on_calendar_date_picked)

        self.page_dashboard.req_refresh_all.connect(self._refresh_week_if_visible)
        self.page_dashboard.req_refresh_all.connect(self._refresh_axis_if_visible)

        self.page_todo = TodoView()
        self.body_stack.addWidget(self.page_todo)
        self.page_todo.req_change_view.connect(self.switch_view)
        self.page_todo.req_refresh_all.connect(self.page_dashboard.refresh_data)
        self.page_todo.req_refresh_all.connect(self._refresh_axis_if_visible)
        self.page_dashboard.req_refresh_all.connect(self.page_todo.refresh_data)
        self.suspend_window = SuspendWindow()
        self.week_window = WeekWindow()
        self.month_window = MonthWindow()
        self.week_window.schedule_updated.connect(self._on_week_schedule_updated)
        self.month_window.schedule_updated.connect(self._on_week_schedule_updated)
        self.week_window.schedule_display_mode_requested.connect(self.set_schedule_display_mode)
        self.month_window.schedule_display_mode_requested.connect(self.set_schedule_display_mode)
        if hasattr(self.header, 'weather_updated'):
            self.header.weather_updated.connect(self.week_window.update_weather_ui)
            self.header.weather_updated.connect(self.month_window.update_weather_ui)
        self.suspend_window_week = SuspendWindowWeek()
        self.suspend_window_month = SuspendWindowMonth()
        self.week_window.restore_requested.connect(self.restore_from_week_view)
        self.week_window.view_selected.connect(self.switch_view)
        self.week_window.request_schedule_detail.connect(
            lambda data: self.page_dashboard._show_detail_popup(
                data,
                source_view="week",
                initial_pinned=bool(
                    self.week_window.windowFlags()
                    & Qt.WindowType.WindowStaysOnTopHint
                ),
                dark_mode=self.week_window.dark_mode(),
            )
        )
        self.week_window.request_timetable_schedule_detail.connect(
            lambda data, color: self.page_dashboard._show_detail_popup(
                data,
                source_view="week",
                initial_pinned=bool(
                    self.week_window.windowFlags()
                    & Qt.WindowType.WindowStaysOnTopHint
                ),
                timetable_color=color,
                on_timetable_color_changed=(
                    self.week_window._handle_timetable_color_changed
                ),
                dark_mode=self.week_window.dark_mode(),
            )
        )
        self.week_window.day_double_clicked.connect(self.jump_to_date)
        self.week_window.suspend_requested.connect(self.switch_week_to_suspend)
        self.month_window.restore_requested.connect(self.restore_from_month_view)
        self.month_window.suspend_requested.connect(self.switch_month_to_suspend)
        self.month_window.view_selected.connect(self.switch_view)
        self.month_window.date_selected.connect(self.jump_to_date_from_month)
        self.month_window.schedule_detail_requested.connect(self.open_schedule_detail_from_month_panel)
        self.header.lbl_weather_icon.double_clicked.connect(
            lambda: self.toggle_weather_board(self)
        )
        self.week_window.lbl_weather_icon.double_clicked.connect(
            lambda: self.toggle_weather_board(self.week_window)
        )
        self.month_window.lbl_weather_icon.double_clicked.connect(
            lambda: self.toggle_weather_board(self.month_window)
        )
        self.suspend_window_week.restore_requested.connect(self.switch_suspend_to_week)
        self.suspend_window_month.restore_requested.connect(self.switch_suspend_to_month)
        hwnd = int(self.winId())
        apply_24h2_border_fix(hwnd)

        # --- 信号连接 ---
        self.header.suspend_requested.connect(self.switch_to_suspend)
        self.suspend_window.restore_requested.connect(self.switch_to_normal)
        self.header.action_requested.connect(self.handle_header_action)
        self.header.search_requested.connect(self.toggle_search_options_panel)
        self.header.search_text_changed.connect(self._handle_search_text_changed)
        self.header.view_requested.connect(self.switch_view)
        self.header.mode_requested.connect(self.set_schedule_display_mode)
        # 实例化日历弹窗
        self.calendar_pop = CalendarPop(self)
        # 监听日历选中的日期
        self.calendar_pop.date_selected.connect(self.on_calendar_date_picked)
        # 监听 Header 发出的打开日历请求
        self.header.req_open_calendar.connect(self.show_calendar_popup)
        # 监听 Header 发出的跨天信号
        self.header.midnight_rollover.connect(self.handle_midnight_rollover)
        # 为顶部日期文本安装事件过滤器
        self.header.lbl_date_info.installEventFilter(self)
        self._restore_schedule_display_mode()
        # 软件刚打开时，强制执行一次“选中今天”的逻辑，确保所有UI同步到今天
        self.on_calendar_date_picked(datetime.now().date())
        
        # AddView 逻辑
        self.page_add.btn_cancel.clicked.connect(
            lambda: self.body_stack.setCurrentWidget(
                self.main_controller.resolve_add_return_target(
                    getattr(self, 'source_view_for_add', None),
                    self.page_dashboard,
                )
            )
        )
        self.page_add.saved.connect(self.on_schedule_saved)
        
        self.time_picker_mode = 'add'
        self.editing_schedule = None
        
        self.page_add.req_open_time_picker.connect(self.go_to_time_picker)
        self.page_time.back_requested.connect(self.back_from_time_picker) 
        self.page_time.confirm_requested.connect(self.on_time_confirmed)
        self.page_dashboard.req_edit_time.connect(self.go_to_time_picker_for_edit) # 🟢 监听面板传来的修改请求

        self.alarm_picker_mode = 'add'
        self.page_add.req_open_alarm_picker.connect(self.go_to_alarm_picker)
        self.page_alarm.back_requested.connect(self.back_from_alarm_picker) # 注意改名
        self.page_alarm.confirm_requested.connect(self.on_alarm_confirmed)
        self.page_dashboard.req_edit_alarm.connect(self.go_to_alarm_picker_for_edit) # 监听面板双击

        self.list_picker_mode = 'add'
        self.page_add.req_open_list_picker.connect(self.go_to_list_picker)
        self.page_list.back_requested.connect(self.back_from_list_picker) # 注意改名
        self.page_list.confirm_requested.connect(self.on_list_confirmed)
        self.page_dashboard.req_edit_list.connect(self.go_to_list_picker_for_edit) # 监听日程面板双击
        
        # 监听待办面板双击清单的请求
        self.page_todo.req_edit_list.connect(self.go_to_list_picker_for_edit)
        self.page_time.suspend_requested.connect(self.switch_to_suspend)
        self.page_alarm.suspend_requested.connect(self.switch_to_suspend)
        self.page_list.suspend_requested.connect(self.switch_to_suspend)
        self._register_refresh_targets()
        global_signals.axis_board_requested.connect(self.toggle_axis_board)
        global_signals.primary_window_pin_changed.connect(self._apply_primary_window_pin)
        current_style = self.styleSheet()
        self.setStyleSheet(current_style + StyleManager.get_tooltip_style())

        # 启动后台提醒监控
        self._init_scheduler()

    def _init_scheduler(self):
        self.reminder_service = ReminderService()
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(1000) 

    def _refresh_week_if_visible(self):
        if hasattr(self, 'week_window') and self.week_window.isVisible():
            self.week_window.refresh_week_data()

    def _register_refresh_targets(self):
        self.main_controller.register_refresh_target("dashboard", self.page_dashboard.refresh_data)
        self.main_controller.register_refresh_target("todo", self.page_todo.refresh_data)
        self.main_controller.register_refresh_target("week_if_visible", self._refresh_week_if_visible)
        self.main_controller.register_refresh_target("axis_if_visible", self._refresh_axis_if_visible)

    def _refresh_dashboard_todo_week(self):
        self.main_controller.request_refresh_many(
            ("dashboard", "todo", "week_if_visible", "axis_if_visible")
        )
        global_signals.refresh_requested.emit("dashboard_todo_week")

    def _refresh_axis_if_visible(self):
        if self.axis_board is not None and self.axis_board.isVisible():
            self.axis_board.refresh_data()

    def _restore_schedule_display_mode(self):
        mode_id = get_timetable_preferences().get("display_mode", "card")
        self.set_schedule_display_mode(mode_id, persist=False)

    def set_schedule_display_mode(self, mode_id, persist=True):
        if mode_id not in {"card", "timetable"}:
            return
        from .components import SharedMoreMenu

        SharedMoreMenu._schedule_display_mode = mode_id
        self.page_dashboard.set_schedule_display_mode(mode_id)
        if hasattr(self.week_window, "apply_schedule_display_mode"):
            self.week_window.apply_schedule_display_mode(mode_id)
        if hasattr(self.month_window, "apply_schedule_display_mode"):
            self.month_window.apply_schedule_display_mode(mode_id)
        if hasattr(self.header, "set_schedule_display_mode"):
            self.header.set_schedule_display_mode(mode_id)
        if persist:
            set_timetable_display_mode(mode_id)

    def reset_timetable_view_to_now(self):
        self.on_calendar_date_picked(datetime.now().date())
        self.page_dashboard.reset_timetable_to_current_time()

    def toggle_search_options_panel(self):
        current_widget = self.body_stack.currentWidget()
        if current_widget == self.page_dashboard:
            panel = self._ensure_day_query_panel("search")
            options = self.page_dashboard.search_options_for_panel()
            categories = db_manager.get_active_categories("schedule")
        elif current_widget == self.page_todo:
            panel = self._ensure_todo_query_panel("search")
            options = self.page_todo.search_options_for_panel()
            categories = db_manager.get_active_categories("todo")
        else:
            self.show_toast("搜索设置仅支持日界面和待办界面")
            return
        if panel.isVisible():
            panel.close()
            return
        self._hide_day_query_panels(except_panel=panel)
        panel.set_options(options, categories)
        self._show_day_query_panel(panel)

    def toggle_day_filter_panel(self):
        current_widget = self.body_stack.currentWidget()
        if current_widget == self.page_dashboard:
            panel = self._ensure_day_query_panel("filter")
            options = self.page_dashboard.filter_options()
            categories = db_manager.get_active_categories("schedule")
        elif current_widget == self.page_todo:
            panel = self._ensure_todo_query_panel("filter")
            options = self.page_todo.filter_options()
            categories = db_manager.get_active_categories("todo")
        else:
            self.show_toast("筛选仅支持日界面和待办界面")
            return
        if panel.isVisible():
            panel.close()
            return
        self._hide_day_query_panels(except_panel=panel)
        panel.set_options(options, categories)
        self._show_day_query_panel(panel)

    def _ensure_day_query_panel(self, panel_mode):
        from .popups.day_query_options_panel import DayQueryOptionsPanel

        attribute_name = (
            "search_options_panel"
            if panel_mode == "search"
            else "day_filter_panel"
        )
        panel = getattr(self, attribute_name)
        if panel is None:
            panel = DayQueryOptionsPanel(panel_mode, self)
            if panel_mode == "search":
                panel.options_changed.connect(self._handle_search_options_previewed)
                panel.applied.connect(self._handle_search_options_applied)
            else:
                panel.options_changed.connect(self._handle_filter_options_previewed)
                panel.applied.connect(self._handle_filter_options_applied)
            setattr(self, attribute_name, panel)
        return panel

    def _ensure_todo_query_panel(self, panel_mode):
        from .popups.day_query_options_panel import DayQueryOptionsPanel

        attribute_name = (
            "todo_search_options_panel"
            if panel_mode == "search"
            else "todo_filter_panel"
        )
        panel = getattr(self, attribute_name)
        if panel is None:
            panel = DayQueryOptionsPanel(
                panel_mode,
                self,
                view_scope="todo",
            )
            if panel_mode == "search":
                panel.options_changed.connect(
                    self._handle_todo_search_options_previewed
                )
                panel.applied.connect(
                    self._handle_todo_search_options_applied
                )
            else:
                panel.options_changed.connect(
                    self._handle_todo_filter_options_previewed
                )
                panel.applied.connect(
                    self._handle_todo_filter_options_applied
                )
            setattr(self, attribute_name, panel)
        return panel

    def _handle_search_options_applied(self, options):
        self.page_dashboard.apply_search_options(options)
        if self.search_options_panel is not None:
            self.search_options_panel.close()

    def _handle_search_options_previewed(self, options):
        self.page_dashboard.apply_search_options(options)

    def _handle_filter_options_applied(self, options):
        self.page_dashboard.apply_filter_options(options)
        self._sync_primary_filter_indicator()
        if self.day_filter_panel is not None:
            self.day_filter_panel.close()

    def _handle_filter_options_previewed(self, options):
        self.page_dashboard.apply_filter_options(options)
        self._sync_primary_filter_indicator()

    def _sync_day_filter_indicator(self):
        self._sync_primary_filter_indicator()

    def _handle_todo_search_options_applied(self, options):
        self.page_todo.apply_search_options(options)
        if self.todo_search_options_panel is not None:
            self.todo_search_options_panel.close()

    def _handle_todo_search_options_previewed(self, options):
        self.page_todo.apply_search_options(options)

    def _handle_todo_filter_options_applied(self, options):
        self.page_todo.apply_filter_options(options)
        self._sync_primary_filter_indicator()
        if self.todo_filter_panel is not None:
            self.todo_filter_panel.close()

    def _handle_todo_filter_options_previewed(self, options):
        self.page_todo.apply_filter_options(options)
        self._sync_primary_filter_indicator()

    def _sync_primary_filter_indicator(self):
        button = getattr(self.header, "toolbar_buttons", {}).get("filter")
        if button is None or not hasattr(button, "set_active"):
            return
        current_widget = self.body_stack.currentWidget()
        if current_widget == self.page_todo:
            active = self.page_todo.has_active_filter()
        elif current_widget == self.page_dashboard:
            active = self.page_dashboard.has_active_filter()
        else:
            active = False
        button.set_active(active)

    def _handle_search_text_changed(self, text):
        current_widget = self.body_stack.currentWidget()
        if current_widget == self.page_todo:
            self.page_todo.set_search_keyword(text)
        elif current_widget == self.page_dashboard:
            self.page_dashboard.set_search_keyword(text)

    def _hide_day_query_panels(self, except_panel=None):
        for panel in (
            self.search_options_panel,
            self.day_filter_panel,
            self.todo_search_options_panel,
            self.todo_filter_panel,
        ):
            if (
                panel is not None
                and panel is not except_panel
                and panel.isVisible()
            ):
                panel.close()

    def _sync_primary_query_header(self):
        current_widget = self.body_stack.currentWidget()
        if current_widget == self.page_todo:
            keyword = self.page_todo.search_keyword()
            placeholder = "搜索待办..."
        elif current_widget == self.page_dashboard:
            keyword = self.page_dashboard.search_keyword()
            placeholder = "搜索日程..."
        else:
            return

        search_box = self.header.search
        previous_block_state = search_box.blockSignals(True)
        search_box.setPlaceholderText(placeholder)
        search_box.setText(keyword)
        search_box.blockSignals(previous_block_state)
        self.header.search_clear_action.setVisible(bool(keyword))
        if hasattr(search_box, "_refresh_elided_text"):
            search_box._refresh_elided_text()
        self._sync_primary_filter_indicator()

    def _show_day_query_panel(self, panel):
        self._position_day_query_panel(panel)
        panel.show()
        panel.raise_()
        panel.activateWindow()

    def _position_day_query_panel(self, panel):
        window_geometry = self.frameGeometry()
        x = window_geometry.left() - panel.width() - 8
        y = window_geometry.top() + self.header.height() - 8

        screen = QApplication.screenAt(window_geometry.center()) or QApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            if x < available.left():
                x = window_geometry.left() + 8
            x = max(available.left(), min(x, available.right() - panel.width() + 1))
            y = max(available.top(), min(y, available.bottom() - panel.height() + 1))

        panel.move(x, y)

    def toggle_axis_board(self, anchor_window=None):
        from PyQt6.QtGui import QGuiApplication
        from .popups.schedule_axis_board import ScheduleAxisBoard

        if self.axis_board is None:
            self.axis_board = ScheduleAxisBoard()
            self.axis_board.set_detail_opener(self.open_schedule_detail_from_axis)

            anchor = anchor_window if anchor_window is not None else self
            anchor_geometry = anchor.frameGeometry()
            x = anchor_geometry.right() + 10
            y = anchor_geometry.top()
            screen = (
                QGuiApplication.screenAt(anchor_geometry.center())
                or QGuiApplication.primaryScreen()
            )
            if screen is not None:
                available = screen.availableGeometry()
                if x + self.axis_board.width() > available.right() + 1:
                    x = anchor_geometry.left() - self.axis_board.width() - 10
                x = max(
                    available.left(),
                    min(x, available.right() - self.axis_board.width() + 1),
                )
                y = max(
                    available.top(),
                    min(y, available.bottom() - self.axis_board.height() + 1),
                )
            self.axis_board.move(x, y)

        if self.axis_board.isVisible():
            self.axis_board.hide()
            return

        self.axis_board.set_pinned(get_primary_pin_preference())
        self.axis_board.refresh_data()
        self.axis_board.show()
        self.axis_board.raise_()
        self.axis_board.activateWindow()

    def toggle_weather_board(self, anchor_window=None):
        from PyQt6.QtGui import QGuiApplication
        from .popups.weather_board import WeatherBoard

        if self.weather_board is None:
            self.weather_board = WeatherBoard()

        if self.weather_board.isVisible():
            self.weather_board.hide()
            return

        self.weather_board.set_pinned(get_primary_pin_preference())
        anchor = anchor_window if anchor_window is not None else self
        anchor_geometry = anchor.frameGeometry()
        x = anchor_geometry.right() + 10
        y = anchor_geometry.top()
        screen = (
            QGuiApplication.screenAt(anchor_geometry.center())
            or QGuiApplication.primaryScreen()
        )
        if screen is not None:
            available = screen.availableGeometry()
            if x + self.weather_board.width() > available.right() + 1:
                x = anchor_geometry.left() - self.weather_board.width() - 10
            x = max(
                available.left(),
                min(x, available.right() - self.weather_board.width() + 1),
            )
            y = max(
                available.top(),
                min(y, available.bottom() - self.weather_board.height() + 1),
            )
        self.weather_board.move(x, y)
        self.weather_board.show()
        self.weather_board.raise_()
        self.weather_board.activateWindow()

    def show_calendar_popup(self):
        """在顶栏日期文字下方弹出日历"""
        # 找到 Header 里的日期标签
        lbl = self.header.lbl_date_info
        # 获取其在屏幕上的全局坐标
        pos = lbl.mapToGlobal(lbl.rect().bottomLeft())
        # 获取 Dashboard 当前停留的日期
        current = self.page_dashboard.current_date
        # 显示弹窗
        self.calendar_pop.show_at(pos, current)

    def on_calendar_date_picked(self, selected_date):
        """接收日历选中的日期并更新全局 UI"""
        # 1. 让看板跳转到这一天并刷新数据
        self.page_dashboard.current_date = selected_date
        self.page_dashboard.refresh_data()
        
        # 2. 同步更新 Header 上的文字（如果是今天显示"今天"，否则显示日期）
        today = datetime.now().date()
        if selected_date == today:
            self.header.lbl_date_info.setText(f"{selected_date.strftime('%m月%d日')} 今天") 
        else:
            week_str = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][selected_date.weekday()]
            self.header.lbl_date_info.setText(f"{selected_date.strftime('%m月%d日')} {week_str}")

    def eventFilter(self, obj, event):
        """事件过滤器：专门拦截顶部日期标签的滚轮事件"""
        if self._handle_vertical_resize_event(obj, event):
            return True

        if (
            hasattr(self, "header")
            and obj == self.header.lbl_date_info
            and event.type() == QEvent.Type.Wheel
        ):
            # 获取滚轮滚动的角度差
            delta = event.angleDelta().y()
            if delta != 0:
                current_date = self.page_dashboard.current_date
                
                # 滚轮向上滑 (delta > 0) -> 回到前一天
                if delta > 0:
                    new_date = current_date - timedelta(days=1)
                # 滚轮向下滑 (delta < 0) -> 去往后一天
                else:
                    new_date = current_date + timedelta(days=1)
                
                # 直接调用现成的方法，它会完美处理看板刷新和文字变化
                self.on_calendar_date_picked(new_date)
                
            # 返回 True 意味着“这个事件我处理完了，不需要再传给底层的滚动条”
            return True 
            
        # 其他无关事件交还给父类正常处理
        return super().eventFilter(obj, event)

    def handle_midnight_rollover(self):
        """接收到 00:00 跨天信号时，强制把看板重置为新的'今天'"""
        print("🌃 跨天啦！自动刷新整个看板到新的今天！")
        new_today = datetime.now().date()
        self.on_calendar_date_picked(new_today)

    def check_reminders(self):
        now = datetime.now()
        schedules = db_manager.get_all_schedules()

        due_schedules = self.reminder_service.collect_due_schedules(schedules, now)
        for s in due_schedules:
            self.show_reminder_popup(s)
            self.reminder_service.mark_triggered(s.id)
            diff = self.reminder_service.get_reminder_diff_seconds(s, now)
            if diff is not None:
                print(f"⏰️ 秒级触发提醒: {s.title} (延迟 {diff:.2f}s)")

    def show_reminder_popup(self, schedule_data):
        data_dict = self.reminder_service.build_reminder_popup_data(schedule_data)
        
        self.current_popup = ReminderPop(data_dict)
        self.current_popup.show()
        
        if schedule_data.is_alarm:
            print("🎵 播放系统闹钟声音...")
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_LOOP | winsound.SND_ASYNC)

    # --- 路由跳转逻辑 ---
    def jump_to_date(self, qdate):
        py_date = qdate.toPyDate()
        self.on_calendar_date_picked(py_date)
        self.switch_view("day")

    def jump_to_date_from_month(self, qdate):
        """从月视图点击具体日期，直接跳转到主面板的该日视图"""
        self.jump_to_date(qdate)

    def open_schedule_detail_from_month_panel(self, schedule_data, owner_panel=None):
        popup = None
        schedule_id = getattr(schedule_data, "id", None)

        if owner_panel is not None:
            child_popups = getattr(owner_panel, "child_detail_popups", [])
            for child_popup in list(child_popups):
                try:
                    child_schedule_id = getattr(getattr(child_popup, "data", None), "id", None)
                    if child_schedule_id == schedule_id:
                        popup = child_popup
                        break
                except RuntimeError:
                    continue

        if popup is not None:
            popup.show()
            popup.raise_()
            popup.activateWindow()
            return popup

        popup = ScheduleDetailPop(schedule_data, source_view="month")
        popup.req_edit_time.connect(lambda data: self.go_to_time_picker_for_edit(data, "month"))
        popup.req_edit_alarm.connect(lambda data: self.go_to_alarm_picker_for_edit(data, "month"))
        popup.req_edit_list.connect(lambda data: self.go_to_list_picker_for_edit(data, "month"))
        popup.schedule_updated.connect(
            lambda popup_ref=popup: self.month_window.refresh_after_schedule_change(
                getattr(popup_ref, "data", None)
            )
        )

        if owner_panel is not None and hasattr(owner_panel, "register_child_detail_popup"):
            owner_panel.register_child_detail_popup(popup)
            popup.owner_panel = owner_panel

        if owner_panel is not None:
            popup_pos = owner_panel.mapToGlobal(QPoint(owner_panel.width() + 10, 0))
            popup.move(popup_pos)
        elif hasattr(self, "month_window"):
            popup.move(self.month_window.mapToGlobal(QPoint(self.month_window.width() + 10, 0)))

        popup.show()
        return popup

    def open_schedule_detail_from_axis(self, schedule_data):
        """Open the shared detail popup for the global axis board."""
        popup = ScheduleDetailPop(schedule_data, source_view="axis")
        popup.set_pinned(bool(self.axis_board and self.axis_board.is_pinned))
        popup.req_edit_time.connect(
            lambda data: self.go_to_time_picker_for_edit(data, "axis")
        )
        popup.req_edit_alarm.connect(
            lambda data: self.go_to_alarm_picker_for_edit(data, "axis")
        )
        popup.req_edit_list.connect(
            lambda data: self.go_to_list_picker_for_edit(data, "axis")
        )
        popup.schedule_updated.connect(
            lambda popup_ref=popup: self._on_axis_detail_updated(
                getattr(popup_ref, "data", None)
            )
        )
        popup.show()
        return popup

    def _on_axis_detail_updated(self, updated_schedule):
        if updated_schedule is None:
            self._refresh_dashboard_todo_week()
            return
        self.month_window.refresh_after_schedule_change(updated_schedule)

    def go_to_time_picker(self, start, end):
        """模式1：从【添加界面】打开时间选择"""
        self.time_picker_mode = 'add'
        self.page_time.set_title("设置时间")
        
        # 如果是新建日程（没传时间），就把 Dashboard 停留的日期传给它！
        if not start and not end:
            dashboard_date = self.page_dashboard.current_date
            now = datetime.now()
            # 默认时间设为：看板当前选中的日期 + 现在的真实小时和分钟
            end = datetime(dashboard_date.year, dashboard_date.month, dashboard_date.day, now.hour, now.minute)
            
        self.page_time.set_initial_data(start, end)
        self.body_stack.setCurrentWidget(self.page_time)
        self.header.hide() 

    def go_to_time_picker_for_edit(self, schedule_data, source_view="dashboard"):
        """模式2：从【详情弹窗】打开时间修改"""
        edit_target = self._resolve_detail_edit_target(source_view)
        if edit_target == "week":
            self.week_window.go_to_time_picker_for_edit(schedule_data)
            return
        if edit_target == "month":
            self.month_window.go_to_time_picker_for_edit(schedule_data)
            return
        self.time_picker_mode = 'edit'
        self.edit_picker_return_view = edit_target
        self.editing_schedule = schedule_data
        
        # 智能截断标题防止 UI 撑爆
        display_title = schedule_data.title
        if len(display_title) > 8:
            display_title = display_title[:7] + "..."
            
        self.page_time.set_title(f"修改【{display_title}】日程时间")
        # 自动回填原有时间，防误触
        self.page_time.set_initial_data(schedule_data.start_time, schedule_data.end_time)
        self.body_stack.setCurrentWidget(self.page_time)
        self.header.hide()

    def back_from_time_picker(self):
        """统一的返回逻辑：从哪来的回哪去"""
        if self.time_picker_mode == 'add':
            self.body_stack.setCurrentWidget(self.page_add)
        else:
            self._return_from_main_edit_picker()
        self.header.show()

    def on_time_confirmed(self, start, end):
        if self.time_picker_mode == 'add':
            self.page_add.set_time_data(start, end)
            self.back_from_time_picker()
        elif self.time_picker_mode == 'edit' and self.editing_schedule:
            # 闭包接收 update_future 参数
            def _do_update(update_future):
                now = datetime.now() 
                new_data = {'start_time': start, 'end_time': end, 'created_at': now}
                db_manager.update_schedule_with_repeat(self.editing_schedule.id, new_data, update_future)
                
                self.editing_schedule.start_time = start
                self.editing_schedule.end_time = end
                self.editing_schedule.created_at = now
                if not update_future: self.editing_schedule.group_id = None # 同步脱离队伍
                
                self._refresh_dashboard_todo_week()
                for p in self.page_dashboard.open_popups:
                    if p.data.id == self.editing_schedule.id:
                        p.refresh_time_display()
                        p.refresh_created_display() 
                self.back_from_time_picker()
            self._check_repeat_and_execute(self.editing_schedule, _do_update)

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

    # === 提醒选择路由逻辑 (双模) ===
    def go_to_alarm_picker(self, target_time, is_alarm, duration):
        self.alarm_picker_mode = 'add'
        self.page_alarm.set_title("设置提醒")
        self.page_alarm.set_initial_data(target_time, is_alarm, duration) 
        self.body_stack.setCurrentWidget(self.page_alarm)
        self.header.hide()

    def go_to_alarm_picker_for_edit(self, schedule_data, source_view="dashboard"):
        edit_target = self._resolve_detail_edit_target(source_view)
        if edit_target == "week":
            self.week_window.go_to_alarm_picker_for_edit(schedule_data)
            return
        if edit_target == "month":
            self.month_window.go_to_alarm_picker_for_edit(schedule_data)
            return
        self.alarm_picker_mode = 'edit'
        self.edit_picker_return_view = edit_target
        self.editing_schedule = schedule_data
        display_title = schedule_data.title if len(schedule_data.title) <= 8 else schedule_data.title[:7] + "..."
        self.page_alarm.set_title(f"修改【{display_title}】提醒")
        
        target = schedule_data.start_time if schedule_data.start_time else schedule_data.end_time
        # 如果目标时间没设，默认给个现在的时间
        if not target: target = datetime.now()
        
        self.page_alarm.set_initial_data(target, schedule_data.is_alarm, schedule_data.alarm_duration)
        self.body_stack.setCurrentWidget(self.page_alarm)
        self.header.hide()

    def back_from_alarm_picker(self):
        if self.alarm_picker_mode == 'add':
            self.body_stack.setCurrentWidget(self.page_add)
        else:
            self._return_from_main_edit_picker()
        self.header.show()

    def on_alarm_confirmed(self, remind_dt, is_alarm, duration):
        if self.alarm_picker_mode == 'add':
            self.page_add.set_alarm_data(remind_dt, is_alarm, duration)
            self.back_from_alarm_picker()
        elif self.alarm_picker_mode == 'edit' and self.editing_schedule:
            def _do_update(update_future):
                now = datetime.now() 
                new_data = {'reminder_time': remind_dt, 'is_alarm': is_alarm, 'alarm_duration': duration, 'created_at': now}
                db_manager.update_schedule_with_repeat(self.editing_schedule.id, new_data, update_future)
                
                self.editing_schedule.reminder_time = remind_dt
                self.editing_schedule.is_alarm = is_alarm
                self.editing_schedule.alarm_duration = duration
                self.editing_schedule.created_at = now
                if not update_future: self.editing_schedule.group_id = None
                
                self._refresh_dashboard_todo_week()
                for p in self.page_dashboard.open_popups:
                    if p.data.id == self.editing_schedule.id: 
                        p.refresh_alarm_display()
                        p.refresh_created_display() 
                self.back_from_alarm_picker()
            self._check_repeat_and_execute(self.editing_schedule, _do_update)

    # === 清单选择路由逻辑 (双模) ===
    def go_to_list_picker(self, current_category_id, current_type):
        self.list_picker_mode = 'add'
        self.page_list.set_title("选择清单")
        # 把类型参数传给弹窗的 load_data
        self.page_list.load_data(current_category_id, list_type=current_type)
        self.body_stack.setCurrentWidget(self.page_list)
        self.header.hide()

    def go_to_list_picker_for_edit(self, schedule_data, source_view="dashboard"):
        edit_target = self._resolve_detail_edit_target(source_view)
        if edit_target == "week":
            self.week_window.go_to_list_picker_for_edit(schedule_data)
            return
        if edit_target == "month":
            self.month_window.go_to_list_picker_for_edit(schedule_data)
            return
        if edit_target == "todo_board":
            if hasattr(self, 'todo_board') and self.todo_board:
                self.todo_board.go_to_list_picker_for_edit(schedule_data)
            return
        self.list_picker_mode = 'edit'
        self.list_picker_source = "todo" if edit_target == "todo" else "dashboard"
        self.edit_picker_return_view = edit_target
        
        self.editing_schedule = schedule_data
        display_title = schedule_data.title if len(schedule_data.title) <= 8 else schedule_data.title[:7] + "..."
        self.page_list.set_title(f"修改【{display_title}】清单")
        
        self.page_list.load_data(schedule_data.category_id, list_type=schedule_data.item_type)
        self.body_stack.setCurrentWidget(self.page_list)
        self.header.hide()

    def back_from_list_picker(self):
        if self.list_picker_mode == 'add':
            self.body_stack.setCurrentWidget(self.page_add)
        else:
            self._return_from_main_edit_picker()
        self.header.show()

    def _resolve_detail_edit_target(self, source_view="dashboard"):
        """按当前可见视图决定详情弹窗的编辑承接窗口。"""
        if self.week_window.isVisible():
            return "week"
        if self.month_window.isVisible():
            return "month"
        if source_view == "todo_board":
            board = getattr(self, "todo_board", None)
            if board is not None and board.isVisible():
                return "todo_board"
        if self.body_stack.currentWidget() == self.page_todo:
            return "todo"
        if self.isVisible():
            return "day"
        return source_view if source_view in {"week", "month", "todo", "todo_board"} else "day"

    def _return_from_main_edit_picker(self):
        if getattr(self, "edit_picker_return_view", "day") == "todo":
            self.body_stack.setCurrentWidget(self.page_todo)
        else:
            self.body_stack.setCurrentWidget(self.page_dashboard)

    def on_list_confirmed(self, category_id):
        if self.list_picker_mode == 'add':
            self.page_add.set_list_data(category_id)
            self.back_from_list_picker()
        elif self.list_picker_mode == 'edit' and self.editing_schedule:
            def _do_update(update_future):
                now = datetime.now() 
                new_data = {'category_id': category_id, 'created_at': now}
                db_manager.update_schedule_with_repeat(self.editing_schedule.id, new_data, update_future)
                
                self.editing_schedule.category_id = category_id
                self.editing_schedule.created_at = now
                if not update_future: self.editing_schedule.group_id = None
                
                self._refresh_dashboard_todo_week() # 为保险起见，清单改变也同步刷新下周视图
                for p in self.page_dashboard.open_popups:
                    if p.data.id == self.editing_schedule.id: 
                        p.refresh_list_display()
                        p.refresh_created_display() 
                self.back_from_list_picker()
            self._check_repeat_and_execute(self.editing_schedule, _do_update)
    # --- 其他逻辑 ---

    def on_schedule_saved(self):
        self._refresh_dashboard_todo_week()
        self.body_stack.setCurrentIndex(0)
        return_target = self.main_controller.resolve_add_return_target(
            getattr(self, 'source_view_for_add', None),
            self.page_dashboard,
        )
        self.body_stack.setCurrentWidget(return_target)

    def handle_header_action(self, action_name):
        if action_name == "add":
            self.switch_to_add_page()
        elif action_name == "toggle_pin":
            self.toggle_pin_mode()
        elif action_name == "skin":
            print("这里以后写换肤逻辑")
        elif action_name == "view":
            # 动态判断当前在哪个页面，就弹哪个页面的视图选择器
            current_widget = self.body_stack.currentWidget()
            
            if current_widget == self.page_todo:
                self.page_todo.toggle_view_selector()
            elif current_widget == self.page_dashboard:
                self.page_dashboard.toggle_view_selector()
            else:
                # 如果在添加页或时间选择页等二级页面，先退回主面板，再弹菜单
                self.body_stack.setCurrentWidget(self.page_dashboard)
                self.page_dashboard.toggle_view_selector()
                
        elif action_name == "sort":
            if getattr(self.page_dashboard, "schedule_display_mode", "card") == "timetable":
                self.reset_timetable_view_to_now()
                return
            print("这里以后写排序逻辑")
        elif action_name == "filter":
            self.toggle_day_filter_panel()

    def _handle_dashboard_context_action(self, action_name):
        if action_name == "add":
            self.switch_to_add_page()

    def _handle_dashboard_context_view(self, view_name):
        self.switch_view(view_name)

    def toggle_pin_mode(self):
        next_pinned = not bool(
            self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
        )
        def _do_toggle():
            set_primary_pin_preference(next_pinned)
            global_signals.primary_window_pin_changed.emit(next_pinned)
            print(f"状态变更：{'开启' if next_pinned else '取消'}置顶")
            
            hwnd = int(self.winId())
            apply_24h2_border_fix(hwnd)
            QTimer.singleShot(10, self.header.reopen_menu)

        QTimer.singleShot(100, _do_toggle)

    def _apply_primary_window_pin(self, enabled):
        for window in (self, self.week_window, self.month_window):
            changed = set_window_pin_state(window, enabled)
            if changed and window.isVisible():
                apply_24h2_border_fix(int(window.winId()))
            
    def switch_to_add_page(self):
        self._hide_day_query_panels()
        current_widget = self.body_stack.currentWidget()
        
        # 只有在日视图（看板）且日期过期时，才禁止添加
        today = datetime.now().date()
        if current_widget == self.page_dashboard and self.page_dashboard.current_date < today:
            self.show_toast("该日期已过期，无法添加日程")
            return
            
        # 原本的切换逻辑
        if current_widget == self.page_add:
            # 如果当前在添加页，再点一次顶栏的 + 号，相当于取消，退回来源页
            return_target = self.main_controller.resolve_add_return_target(
                getattr(self, 'source_view_for_add', None),
                self.page_dashboard,
            )
            self.body_stack.setCurrentWidget(return_target)
        else:
            self.source_view_for_add = self.main_controller.resolve_add_source(
                current_widget,
                self.page_dashboard,
                self.page_todo,
                getattr(self, 'source_view_for_add', None),
            )
            
            default_to_schedule = self.main_controller.default_to_schedule_for_add(
                current_widget,
                self.page_todo,
            )
            self.page_add.reset(default_to_schedule=default_to_schedule)
            
            self.body_stack.setCurrentWidget(self.page_add)

    # 处理视图切换
    def switch_view(self, view_name):
        route_action = ViewRouter.classify_main_view(view_name)
        self._sync_view_selector_state(route_action)
        if route_action in {"day", "week", "month", "todo"}:
            self._hide_day_query_panels()

        # 切换前，先把可能处于打开状态的视图选择菜单隐藏掉
        if hasattr(self, 'page_dashboard'):
            self.page_dashboard.view_selector.hide()
        if hasattr(self, 'page_todo'):
            self.page_todo.view_selector.hide()

        # 从周视图切走时，让主窗口在周视图当前位置居中出现
        if route_action != "week" and hasattr(self, 'week_window') and self.week_window.isVisible():
            geom = self.week_window.geometry()
            self.move(geom.x() + (geom.width() - self.width()) // 2, geom.y() + (geom.height() - self.height()) // 2)
            self.week_window.hide()  # 关掉周界面
            self.show()

        # 从月视图切走时，让主窗口在月视图当前位置居中出现
        if route_action != "month" and hasattr(self, 'month_window') and self.month_window.isVisible():
            geom = self.month_window.geometry()
            self.move(geom.x() + (geom.width() - self.width()) // 2, geom.y() + (geom.height() - self.height()) // 2)
            self.month_window.hide()  # 关掉月界面
            self.show()
        
        if route_action == "week":
            # 切换到周视图 
            self.hide()
            self.week_window.refresh_week_data()
            if hasattr(self, 'header') and hasattr(self.header, 'current_weather_data'):
                if self.header.current_weather_data:
                    self.week_window.update_weather_ui(self.header.current_weather_data)
            
            # 获取主窗口坐标，计算周视图的相对中心位置
            main_geom = self.geometry()
            new_x = main_geom.x() + (main_geom.width() - self.week_window.width()) // 2
            new_y = main_geom.y() + (main_geom.height() - self.week_window.height()) // 2
            self.week_window.move(new_x, new_y)
            self.week_window.show()

        elif route_action == "month":
            # 月视图切换逻辑
            self.hide()
            if hasattr(self, 'header') and hasattr(self.header, 'current_weather_data'):
                if self.header.current_weather_data:
                    self.month_window.update_weather_ui(self.header.current_weather_data)
            # 获取主窗口坐标，计算月视图的相对中心位置
            main_geom = self.geometry()
            new_x = main_geom.x() + (main_geom.width() - self.month_window.width()) // 2
            new_y = main_geom.y() + (main_geom.height() - self.month_window.height()) // 2
            self.month_window.move(new_x, new_y)
            self.month_window.show()
            
        elif route_action == "todo":
            # 切换到待办视图
            self.body_stack.setCurrentWidget(self.page_todo)
            self.page_todo.refresh_data() # 切过去的时候刷新一下数据
            self._sync_primary_query_header()
            
        elif route_action == "day":
            # 切换回日视图 (主面板)
            self.body_stack.setCurrentWidget(self.page_dashboard)
            self.page_dashboard.refresh_data()
            self._sync_primary_query_header()
            
        elif route_action == "priority":

            self.show_toast("该视图入口已调整")
        else:
            self.show_toast(f"准备切换至：{view_name}")

        if route_action in {"day", "week", "month", "todo"}:
            QTimer.singleShot(0, self._restore_detail_popups)

    def _restore_detail_popups(self):
        self.page_dashboard.restore_detail_popups()
        self.page_todo.restore_detail_popups()
        self.month_window.restore_open_day_panels()

    def _sync_view_selector_state(self, view_name):
        if view_name not in {"day", "week", "month", "todo"}:
            return
        if hasattr(self, 'page_dashboard') and hasattr(self.page_dashboard, 'view_selector'):
            self.page_dashboard.view_selector.set_current_view(view_name)
        if hasattr(self, 'page_todo') and hasattr(self.page_todo, 'view_selector'):
            self.page_todo.view_selector.set_current_view(view_name)

    def restore_from_month_view(self):
        """从大屏月视图恢复到主视图窄屏"""
        # 计算相对位置，以月视图当前位置为中心，收缩回主窗口
        month_geom = self.month_window.geometry()
        new_x = month_geom.x() + (month_geom.width() - self.width()) // 2
        new_y = month_geom.y() + (month_geom.height() - self.height()) // 2
        self.move(new_x, new_y)

        self.month_window.hide()
        self.body_stack.setCurrentWidget(self.page_dashboard) # 确保路由回到看板
        self._sync_view_selector_state("day")
        self.page_dashboard.refresh_data()
        self._sync_primary_query_header()
        self.show()

    def restore_from_week_view(self):
        """从周视图宽屏恢复到主视图窄屏"""
        # 计算相对位置，以周视图当前位置为中心，收缩回主窗口
        week_geom = self.week_window.geometry()
        new_x = week_geom.x() + (week_geom.width() - self.width()) // 2
        new_y = week_geom.y() + (week_geom.height() - self.height()) // 2
        self.move(new_x, new_y)

        self.week_window.hide()
        self.body_stack.setCurrentWidget(self.page_dashboard) # 确保路由回到看板
        self._sync_view_selector_state("day")
        self.page_dashboard.refresh_data()
        self._sync_primary_query_header()
        self.show()

    def show_toast(self, message):
        self.toast_label = show_center_toast(self, message, attr_name="toast_label", duration_ms=500)

    def switch_to_suspend(self):
        pos = self.pos()
        self.suspend_window.set_source_gradient_height(self.height())
        self.suspend_window.move(pos)
        self.hide()
        self.suspend_window.show()

    def switch_to_normal(self):
        pos = self.suspend_window.pos()
        self.move(pos)
        self.suspend_window.hide()
        self.show()
        self.resize(AppConfig.DEFAULT_WIDTH, 600) 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path.addRoundedRect(rect, 5.0, 5.0)
        
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        painter.fillPath(path, QBrush(gradient))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(0, 0, 0, 26), 1))
        painter.drawPath(path)

    def _handle_vertical_resize_event(self, watched, event):
        if isinstance(watched, QWidget) and watched.window() is self:
            event_type = event.type()
            if event_type == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    edge = self._vertical_resize_edge_at(self._event_global_pos(event))
                    if edge:
                        self._vertical_resize_edge = edge
                        self._vertical_resize_start_pos = self._event_global_pos(event)
                        self._vertical_resize_start_geometry = self.geometry()
                        event.accept()
                        return True
            elif event_type == QEvent.Type.MouseMove:
                if self._vertical_resize_edge:
                    self._apply_vertical_resize(self._event_global_pos(event))
                    event.accept()
                    return True
                if self._vertical_resize_edge_at(self._event_global_pos(event)):
                    self.setCursor(Qt.CursorShape.SizeVerCursor)
                elif self.cursor().shape() == Qt.CursorShape.SizeVerCursor:
                    self.unsetCursor()
            elif event_type == QEvent.Type.MouseButtonRelease:
                if self._vertical_resize_edge:
                    self._vertical_resize_edge = None
                    self._vertical_resize_start_geometry = None
                    self.unsetCursor()
                    event.accept()
                    return True
            elif event_type == QEvent.Type.Leave:
                if not self._vertical_resize_edge and self.cursor().shape() == Qt.CursorShape.SizeVerCursor:
                    self.unsetCursor()

        return False

    def _event_global_pos(self, event):
        if hasattr(event, "globalPosition"):
            return event.globalPosition().toPoint()
        return event.globalPos()

    def _vertical_resize_edge_at(self, global_pos):
        local_pos = self.mapFromGlobal(global_pos)
        if local_pos.x() < 0 or local_pos.x() > self.width():
            return None
        if 0 <= local_pos.y() <= self._vertical_resize_margin:
            return "top"
        if self.height() - self._vertical_resize_margin <= local_pos.y() <= self.height():
            return "bottom"
        return None

    def _apply_vertical_resize(self, global_pos):
        if self._vertical_resize_start_geometry is None:
            return

        start_geometry = self._vertical_resize_start_geometry
        delta_y = global_pos.y() - self._vertical_resize_start_pos.y()
        minimum_height = self.minimumHeight()
        maximum_height = self.maximumHeight()
        if maximum_height <= 0:
            maximum_height = 16777215

        if self._vertical_resize_edge == "bottom":
            new_height = max(minimum_height, min(maximum_height, start_geometry.height() + delta_y))
            self.setGeometry(
                start_geometry.x(),
                start_geometry.y(),
                start_geometry.width(),
                new_height,
            )
        elif self._vertical_resize_edge == "top":
            new_height = max(minimum_height, min(maximum_height, start_geometry.height() - delta_y))
            bottom = start_geometry.y() + start_geometry.height()
            self.setGeometry(
                start_geometry.x(),
                bottom - new_height,
                start_geometry.width(),
                new_height,
            )

    def closeEvent(self, event):
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        if self.axis_board is not None:
            self.axis_board.close()
        if self.weather_board is not None:
            self.weather_board.close()
        self._hide_day_query_panels()
        super().closeEvent(event)

    def switch_week_to_suspend(self):
        """周视图 -> 宽版挂起条"""
        source_height = (
            self.week_window.height()
            if self.week_window.is_edit_mode
            else self.week_window.top_container.height()
        )
        self.suspend_window_week.set_source_gradient_height(source_height)
        self.week_window.hide()
        pos = self.week_window.pos()
        self.suspend_window_week.move(pos.x(), pos.y())
        self.suspend_window_week.show()

    def switch_suspend_to_week(self):
        """宽版挂起条 -> 周视图"""
        self.suspend_window_week.hide()
        pos = self.suspend_window_week.pos()
        self.week_window.move(pos.x(), pos.y())
        self.week_window.show()

    def switch_month_to_suspend(self):
        """月视图 -> 月视图专属挂起条"""
        self.suspend_window_month.set_source_gradient_height(self.month_window.height())
        self.month_window.hide()
        pos = self.month_window.pos()
        self.suspend_window_month.move(pos.x(), pos.y())
        self.suspend_window_month.show()

    def switch_suspend_to_month(self):
        """月视图专属挂起条 -> 月视图"""
        self.suspend_window_month.hide()
        pos = self.suspend_window_month.pos()
        self.month_window.move(pos.x(), pos.y())
        self.month_window.show()

    def _on_week_schedule_updated(self, updated_schedule):
        """当周视图完成修改时，顺便把弹窗里的文字刷新一下"""
        self._refresh_dashboard_todo_week()
        if not updated_schedule:
            return
        for p in self.page_dashboard.open_popups:
            if p.data.id == updated_schedule.id:
                p.refresh_time_display()
                p.refresh_alarm_display()  
                if hasattr(p, 'refresh_list_display'): 
                    p.refresh_list_display()
                p.refresh_created_display()
