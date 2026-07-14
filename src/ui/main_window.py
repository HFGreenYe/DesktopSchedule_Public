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
from ..services.schedule_sort_service import ScheduleSortOptions

class MainWindow(FramelessMainWindow):
    def __init__(self):
        super().__init__()
        self.main_controller = MainController()
        self.axis_board = None
        self.weather_board = None
        self.search_options_panel = None
        self.day_filter_panel = None
        self.day_sort_panel = None
        self.todo_search_options_panel = None
        self.todo_filter_panel = None
        self.todo_sort_panel = None
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
        
        # --- 椤甸潰鍫嗘爤 ---
        self.body_stack = QStackedWidget()
        self.main_layout.addWidget(self.body_stack)

        # Page 0: 鐪嬫澘
        self.page_dashboard = DashboardView() 
        self.body_stack.addWidget(self.page_dashboard)

        # Page 1: 娣诲姞椤?
        self.page_add = AddScheduleView()
        self.body_stack.addWidget(self.page_add)
        
        # Page 2: 鏃堕棿閫夋嫨椤?
        self.page_time = TimePickerView()
        self.body_stack.addWidget(self.page_time)

        # Page 3: 鎻愰啋閫夋嫨椤?
        self.page_alarm = AlarmPickerView()
        self.body_stack.addWidget(self.page_alarm)

        # Page 4: 娓呭崟閫夋嫨椤?
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

        # --- 淇″彿杩炴帴 ---
        self.header.suspend_requested.connect(self.switch_to_suspend)
        self.suspend_window.restore_requested.connect(self.switch_to_normal)
        self.header.action_requested.connect(self.handle_header_action)
        self.header.search_requested.connect(self.toggle_search_options_panel)
        self.header.search_text_changed.connect(self._handle_search_text_changed)
        self.header.view_requested.connect(self.switch_view)
        self.header.mode_requested.connect(self.set_schedule_display_mode)
        # 瀹炰緥鍖栨棩鍘嗗脊绐?
        self.calendar_pop = CalendarPop(self)
        # 鐩戝惉鏃ュ巻閫変腑鐨勬棩鏈?
        self.calendar_pop.date_selected.connect(self.on_calendar_date_picked)
        # 鐩戝惉 Header 鍙戝嚭鐨勬墦寮€鏃ュ巻璇锋眰
        self.header.req_open_calendar.connect(self.show_calendar_popup)
        # 鐩戝惉 Header 鍙戝嚭鐨勮法澶╀俊鍙?
        self.header.midnight_rollover.connect(self.handle_midnight_rollover)
        # 涓洪《閮ㄦ棩鏈熸枃鏈畨瑁呬簨浠惰繃婊ゅ櫒
        self.header.lbl_date_info.installEventFilter(self)
        self._restore_schedule_display_mode()
        # 杞欢鍒氭墦寮€鏃讹紝寮哄埗鎵ц涓€娆♀€滈€変腑浠婂ぉ鈥濈殑閫昏緫锛岀‘淇濇墍鏈塙I鍚屾鍒颁粖澶?
        self.on_calendar_date_picked(datetime.now().date())
        
        # AddView 閫昏緫
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
        self.page_dashboard.req_edit_time.connect(self.go_to_time_picker_for_edit) # 馃煝 鐩戝惉闈㈡澘浼犳潵鐨勪慨鏀硅姹?

        self.alarm_picker_mode = 'add'
        self.page_add.req_open_alarm_picker.connect(self.go_to_alarm_picker)
        self.page_alarm.back_requested.connect(self.back_from_alarm_picker) # 娉ㄦ剰鏀瑰悕
        self.page_alarm.confirm_requested.connect(self.on_alarm_confirmed)
        self.page_dashboard.req_edit_alarm.connect(self.go_to_alarm_picker_for_edit) # 鐩戝惉闈㈡澘鍙屽嚮

        self.list_picker_mode = 'add'
        self.page_add.req_open_list_picker.connect(self.go_to_list_picker)
        self.page_list.back_requested.connect(self.back_from_list_picker) # 娉ㄦ剰鏀瑰悕
        self.page_list.confirm_requested.connect(self.on_list_confirmed)
        self.page_dashboard.req_edit_list.connect(self.go_to_list_picker_for_edit) # 鐩戝惉鏃ョ▼闈㈡澘鍙屽嚮
        
        # 鐩戝惉寰呭姙闈㈡澘鍙屽嚮娓呭崟鐨勮姹?
        self.page_todo.req_edit_list.connect(self.go_to_list_picker_for_edit)
        self.page_time.suspend_requested.connect(self.switch_to_suspend)
        self.page_alarm.suspend_requested.connect(self.switch_to_suspend)
        self.page_list.suspend_requested.connect(self.switch_to_suspend)
        self._register_refresh_targets()
        global_signals.axis_board_requested.connect(self.toggle_axis_board)
        global_signals.primary_window_pin_changed.connect(self._apply_primary_window_pin)
        current_style = self.styleSheet()
        self.setStyleSheet(current_style + StyleManager.get_tooltip_style())

        # 鍚姩鍚庡彴鎻愰啋鐩戞帶
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
        current_mode = getattr(self.page_dashboard, "schedule_display_mode", "card")
        if current_mode != mode_id:
            self._exit_sort_state_for_mode_switch()
        from .components import SharedMoreMenu

        SharedMoreMenu._schedule_display_mode = mode_id
        self.page_dashboard.set_schedule_display_mode(mode_id)
        if hasattr(self.week_window, "apply_schedule_display_mode"):
            self.week_window.apply_schedule_display_mode(mode_id)
        if hasattr(self.month_window, "apply_schedule_display_mode"):
            self.month_window.apply_schedule_display_mode(mode_id)
        if hasattr(self.header, "set_schedule_display_mode"):
            self.header.set_schedule_display_mode(mode_id)
        self._sync_primary_sort_indicator()
        if persist:
            set_timetable_display_mode(mode_id)

    def _exit_sort_state_for_mode_switch(self):
        current_widget = self.body_stack.currentWidget()
        if (
            current_widget == self.page_dashboard
            and self.page_dashboard.has_active_sort()
        ):
            self.page_dashboard.freeze_current_card_order()
            self.page_dashboard.apply_sort_options(ScheduleSortOptions())

        if hasattr(self, "week_window") and self.week_window.isVisible():
            self.week_window._exit_sort_state_for_close()

        if hasattr(self, "month_window") and self.month_window.isVisible():
            self.month_window._exit_sort_state_for_close()

        self._hide_day_query_panels()
        if hasattr(self, "week_window"):
            self.week_window._hide_week_query_panels()
        if hasattr(self, "month_window"):
            self.month_window._hide_month_query_panels()
        self._sync_primary_sort_indicator()

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
            self.show_toast("\u7b5b\u9009\u4ec5\u652f\u6301\u65e5\u754c\u9762\u548c\u5f85\u529e\u754c\u9762")
            return
        if panel.isVisible():
            panel.close()
            return
        self._hide_day_query_panels(except_panel=panel)
        panel.set_options(options, categories)
        self._show_day_query_panel(panel)

    def toggle_day_sort_panel(self):
        current_widget = self.body_stack.currentWidget()
        if current_widget == self.page_dashboard:
            panel = self._ensure_day_sort_panel("day")
            options = self.page_dashboard.sort_options()
        elif current_widget == self.page_todo:
            panel = self._ensure_day_sort_panel("todo")
            options = self.page_todo.sort_options()
        else:
            self.show_toast("排序仅支持日界面和待办界面")
            return
        if panel.isVisible():
            panel.close()
            return
        self._hide_day_query_panels(except_panel=panel)
        panel.set_options(options)
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

    def _ensure_day_sort_panel(self, view_scope):
        from .popups.schedule_sort_options_panel import ScheduleSortOptionsPanel

        attribute_name = "todo_sort_panel" if view_scope == "todo" else "day_sort_panel"
        panel = getattr(self, attribute_name)
        if panel is None:
            panel = ScheduleSortOptionsPanel(view_scope, self)
            if view_scope == "todo":
                panel.options_changed.connect(self._handle_todo_sort_options_previewed)
                panel.applied.connect(self._handle_todo_sort_options_applied)
            else:
                panel.options_changed.connect(self._handle_sort_options_previewed)
                panel.applied.connect(self._handle_sort_options_applied)
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

    def _handle_sort_options_applied(self, options):
        if options.is_default() and self.page_dashboard.has_active_sort():
            self.page_dashboard.freeze_current_card_order()
        self.page_dashboard.apply_sort_options(options)
        self._sync_primary_sort_indicator()
        if self.day_sort_panel is not None:
            self.day_sort_panel.close()

    def _handle_sort_options_previewed(self, options):
        self.page_dashboard.apply_sort_options(options)
        self._sync_primary_sort_indicator()

    def _handle_todo_sort_options_applied(self, options):
        if options.is_default() and self.page_todo.has_active_sort():
            self.page_todo.freeze_current_card_order()
        self.page_todo.apply_sort_options(options)
        self._sync_primary_sort_indicator()
        if self.todo_sort_panel is not None:
            self.todo_sort_panel.close()

    def _handle_todo_sort_options_previewed(self, options):
        self.page_todo.apply_sort_options(options)
        self._sync_primary_sort_indicator()

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

    def _sync_primary_sort_indicator(self):
        button = getattr(self.header, "toolbar_buttons", {}).get("sort")
        if button is None or not hasattr(button, "set_active"):
            return
        current_widget = self.body_stack.currentWidget()
        if current_widget == self.page_todo:
            active = self.page_todo.has_active_sort()
        elif current_widget == self.page_dashboard:
            active = (
                self.page_dashboard.has_active_sort()
                and getattr(self.page_dashboard, "schedule_display_mode", "card") == "card"
            )
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
            self.day_sort_panel,
            self.todo_search_options_panel,
            self.todo_filter_panel,
            self.todo_sort_panel,
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
            placeholder = "鎼滅储寰呭姙..."
        elif current_widget == self.page_dashboard:
            keyword = self.page_dashboard.search_keyword()
            placeholder = "鎼滅储鏃ョ▼..."
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
        self._sync_primary_sort_indicator()

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
        """Show calendar popup under header date text."""
        # 鎵惧埌 Header 閲岀殑鏃ユ湡鏍囩
        lbl = self.header.lbl_date_info
        # 鑾峰彇鍏跺湪灞忓箷涓婄殑鍏ㄥ眬鍧愭爣
        pos = lbl.mapToGlobal(lbl.rect().bottomLeft())
        # 鑾峰彇 Dashboard 褰撳墠鍋滅暀鐨勬棩鏈?
        current = self.page_dashboard.current_date
        # 鏄剧ず寮圭獥
        self.calendar_pop.show_at(pos, current)

    def on_calendar_date_picked(self, selected_date):
        """Receive selected calendar date and update UI."""
        # 1. 璁╃湅鏉胯烦杞埌杩欎竴澶╁苟鍒锋柊鏁版嵁
        self.page_dashboard.current_date = selected_date
        self.page_dashboard.refresh_data()
        
        # 2. 鍚屾鏇存柊 Header 涓婄殑鏂囧瓧锛堝鏋滄槸浠婂ぉ鏄剧ず"浠婂ぉ"锛屽惁鍒欐樉绀烘棩鏈燂級
        today = datetime.now().date()
        if selected_date == today:
            self.header.lbl_date_info.setText(f"{selected_date.month:02d}\u6708{selected_date.day:02d}\u65e5 \u4eca\u5929")
        else:
            week_str = ["\u5468\u4e00", "\u5468\u4e8c", "\u5468\u4e09", "\u5468\u56db", "\u5468\u4e94", "\u5468\u516d", "\u5468\u65e5"][selected_date.weekday()]
            self.header.lbl_date_info.setText(f"{selected_date.month:02d}\u6708{selected_date.day:02d}\u65e5 {week_str}")

    def eventFilter(self, obj, event):
        """Event filter for vertical resize and header date wheel."""
        if self._handle_vertical_resize_event(obj, event):
            return True

        if (
            hasattr(self, "header")
            and obj == self.header.lbl_date_info
            and event.type() == QEvent.Type.Wheel
        ):
            # 鑾峰彇婊氳疆婊氬姩鐨勮搴﹀樊
            delta = event.angleDelta().y()
            if delta != 0:
                current_date = self.page_dashboard.current_date
                
                # 婊氳疆鍚戜笂婊?(delta > 0) -> 鍥炲埌鍓嶄竴澶?
                if delta > 0:
                    new_date = current_date - timedelta(days=1)
                # 婊氳疆鍚戜笅婊?(delta < 0) -> 鍘诲線鍚庝竴澶?
                else:
                    new_date = current_date + timedelta(days=1)
                
                # 鐩存帴璋冪敤鐜版垚鐨勬柟娉曪紝瀹冧細瀹岀編澶勭悊鐪嬫澘鍒锋柊鍜屾枃瀛楀彉鍖?
                self.on_calendar_date_picked(new_date)
                
            # 杩斿洖 True 鎰忓懗鐫€鈥滆繖涓簨浠舵垜澶勭悊瀹屼簡锛屼笉闇€瑕佸啀浼犵粰搴曞眰鐨勬粴鍔ㄦ潯鈥?
            return True 
            
        # 鍏朵粬鏃犲叧浜嬩欢浜よ繕缁欑埗绫绘甯稿鐞?
        return super().eventFilter(obj, event)

    def handle_midnight_rollover(self):
        """Reset dashboard to the new today after midnight rollover."""
        print("馃寖 璺ㄥぉ鍟︼紒鑷姩鍒锋柊鏁翠釜鐪嬫澘鍒版柊鐨勪粖澶╋紒")
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
                print(f"鈴帮笍 绉掔骇瑙﹀彂鎻愰啋: {s.title} (寤惰繜 {diff:.2f}s)")

    def show_reminder_popup(self, schedule_data):
        data_dict = self.reminder_service.build_reminder_popup_data(schedule_data)
        
        self.current_popup = ReminderPop(data_dict)
        self.current_popup.show()
        
        if schedule_data.is_alarm:
            print("馃幍 鎾斁绯荤粺闂归挓澹伴煶...")
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_LOOP | winsound.SND_ASYNC)

    # --- 璺敱璺宠浆閫昏緫 ---
    def jump_to_date(self, qdate):
        py_date = qdate.toPyDate()
        self.on_calendar_date_picked(py_date)
        self.switch_view("day")

    def jump_to_date_from_month(self, qdate):
        """Open day view from a selected month date."""
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
        """Open time picker from add view."""
        self.time_picker_mode = 'add'
        self.page_time.set_title("\u8bbe\u7f6e\u65f6\u95f4")
        
        # 濡傛灉鏄柊寤烘棩绋嬶紙娌′紶鏃堕棿锛夛紝灏辨妸 Dashboard 鍋滅暀鐨勬棩鏈熶紶缁欏畠锛?
        if not start and not end:
            dashboard_date = self.page_dashboard.current_date
            now = datetime.now()
            # 榛樿鏃堕棿璁句负锛氱湅鏉垮綋鍓嶉€変腑鐨勬棩鏈?+ 鐜板湪鐨勭湡瀹炲皬鏃跺拰鍒嗛挓
            end = datetime(dashboard_date.year, dashboard_date.month, dashboard_date.day, now.hour, now.minute)
            
        self.page_time.set_initial_data(start, end)
        self.body_stack.setCurrentWidget(self.page_time)
        self.header.hide() 

    def go_to_time_picker_for_edit(self, schedule_data, source_view="dashboard"):
        """Open time picker from detail popup."""
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
        
        # 鏅鸿兘鎴柇鏍囬闃叉 UI 鎾戠垎
        display_title = schedule_data.title
        if len(display_title) > 8:
            display_title = display_title[:7] + "..."
            
        self.page_time.set_title(f"修改「{display_title}」日程时间")
        # 鑷姩鍥炲～鍘熸湁鏃堕棿锛岄槻璇Е
        self.page_time.set_initial_data(schedule_data.start_time, schedule_data.end_time)
        self.body_stack.setCurrentWidget(self.page_time)
        self.header.hide()

    def back_from_time_picker(self):
        """Return from picker to the originating view."""
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
            # 闂寘鎺ユ敹 update_future 鍙傛暟
            def _do_update(update_future):
                now = datetime.now() 
                new_data = {'start_time': start, 'end_time': end, 'created_at': now}
                db_manager.update_schedule_with_repeat(self.editing_schedule.id, new_data, update_future)
                
                self.editing_schedule.start_time = start
                self.editing_schedule.end_time = end
                self.editing_schedule.created_at = now
                if not update_future: self.editing_schedule.group_id = None # 鍚屾鑴辩闃熶紞
                
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
            msg.setWindowTitle("重复规则确认")
            msg.setText(f"当前日程包含「{rule}」的重复规则。\n您的修改将会应用到该系列的所有日程。")
            
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
                update_callback(True)   # 浼?True: 淇敼鏈潵鐨勬墍鏈夋棩绋?
            elif msg.clickedButton() == btn_single:
                update_callback(False)  # 浼?False: 鑴辩闃熶紞锛屼粎淇敼褰撳墠杩欐潯
            else:
                pass 
        else:
            update_callback(False)

    # === 鎻愰啋閫夋嫨璺敱閫昏緫 (鍙屾ā) ===
    def go_to_alarm_picker(self, target_time, is_alarm, duration):
        self.alarm_picker_mode = 'add'
        self.page_alarm.set_title("\u8bbe\u7f6e\u63d0\u9192")
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
        self.page_alarm.set_title(f"修改「{display_title}」提醒")
        
        target = schedule_data.start_time if schedule_data.start_time else schedule_data.end_time
        # 濡傛灉鐩爣鏃堕棿娌¤锛岄粯璁ょ粰涓幇鍦ㄧ殑鏃堕棿
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

    # === 娓呭崟閫夋嫨璺敱閫昏緫 (鍙屾ā) ===
    def go_to_list_picker(self, current_category_id, current_type):
        self.list_picker_mode = 'add'
        self.page_list.set_title("\u9009\u62e9\u6e05\u5355")
        # 鎶婄被鍨嬪弬鏁颁紶缁欏脊绐楃殑 load_data
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
        self.page_list.set_title(f"修改「{display_title}」清单")
        
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
        """Resolve which visible view should handle detail editing."""
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
                
                self._refresh_dashboard_todo_week() # 涓轰繚闄╄捣瑙侊紝娓呭崟鏀瑰彉涔熷悓姝ュ埛鏂颁笅鍛ㄨ鍥?
                for p in self.page_dashboard.open_popups:
                    if p.data.id == self.editing_schedule.id: 
                        p.refresh_list_display()
                        p.refresh_created_display() 
                self.back_from_list_picker()
            self._check_repeat_and_execute(self.editing_schedule, _do_update)
    # --- 鍏朵粬閫昏緫 ---

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
            print("杩欓噷浠ュ悗鍐欐崲鑲ら€昏緫")
        elif action_name == "view":
            # 鍔ㄦ€佸垽鏂綋鍓嶅湪鍝釜椤甸潰锛屽氨寮瑰摢涓〉闈㈢殑瑙嗗浘閫夋嫨鍣?
            current_widget = self.body_stack.currentWidget()
            
            if current_widget == self.page_todo:
                self.page_todo.toggle_view_selector()
            elif current_widget == self.page_dashboard:
                self.page_dashboard.toggle_view_selector()
            else:
                # 濡傛灉鍦ㄦ坊鍔犻〉鎴栨椂闂撮€夋嫨椤电瓑浜岀骇椤甸潰锛屽厛閫€鍥炰富闈㈡澘锛屽啀寮硅彍鍗?
                self.body_stack.setCurrentWidget(self.page_dashboard)
                self.page_dashboard.toggle_view_selector()
                
        elif action_name == "sort":
            current_widget = self.body_stack.currentWidget()
            if current_widget == self.page_todo:
                self.toggle_day_sort_panel()
            elif current_widget == self.page_dashboard:
                if getattr(self.page_dashboard, "schedule_display_mode", "card") == "timetable":
                    self.reset_timetable_view_to_now()
                    return
                self.toggle_day_sort_panel()
            else:
                self.show_toast("排序仅支持日界面和待办界面")
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
            print(f"primary pin changed: {'on' if next_pinned else 'off'}")
            
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
        
        # 鍙湁鍦ㄦ棩瑙嗗浘锛堢湅鏉匡級涓旀棩鏈熻繃鏈熸椂锛屾墠绂佹娣诲姞
        today = datetime.now().date()
        if current_widget == self.page_dashboard and self.page_dashboard.current_date < today:
            self.show_toast("该日期已过期，无法添加日程")
            return
            
        # 鍘熸湰鐨勫垏鎹㈤€昏緫
        if current_widget == self.page_add:
            # 濡傛灉褰撳墠鍦ㄦ坊鍔犻〉锛屽啀鐐逛竴娆￠《鏍忕殑 + 鍙凤紝鐩稿綋浜庡彇娑堬紝閫€鍥炴潵婧愰〉
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

    # 澶勭悊瑙嗗浘鍒囨崲
    def switch_view(self, view_name):
        route_action = ViewRouter.classify_main_view(view_name)
        self._exit_sort_state_for_view_switch(route_action)
        self._sync_view_selector_state(route_action)
        if route_action in {"day", "week", "month", "todo"}:
            self._hide_day_query_panels()

        # 鍒囨崲鍓嶏紝鍏堟妸鍙兘澶勪簬鎵撳紑鐘舵€佺殑瑙嗗浘閫夋嫨鑿滃崟闅愯棌鎺?        if hasattr(self, 'page_dashboard'):
            self.page_dashboard.view_selector.hide()
        if hasattr(self, 'page_todo'):
            self.page_todo.view_selector.hide()

        # 浠庡懆瑙嗗浘鍒囪蛋鏃讹紝璁╀富绐楀彛鍦ㄥ懆瑙嗗浘褰撳墠浣嶇疆灞呬腑鍑虹幇
        if route_action != "week" and hasattr(self, 'week_window') and self.week_window.isVisible():
            geom = self.week_window.geometry()
            self.move(geom.x() + (geom.width() - self.width()) // 2, geom.y() + (geom.height() - self.height()) // 2)
            self.week_window.hide()  # 鍏虫帀鍛ㄧ晫闈?
            self.show()

        # 浠庢湀瑙嗗浘鍒囪蛋鏃讹紝璁╀富绐楀彛鍦ㄦ湀瑙嗗浘褰撳墠浣嶇疆灞呬腑鍑虹幇
        if route_action != "month" and hasattr(self, 'month_window') and self.month_window.isVisible():
            geom = self.month_window.geometry()
            self.move(geom.x() + (geom.width() - self.width()) // 2, geom.y() + (geom.height() - self.height()) // 2)
            self.month_window.hide()  # 鍏虫帀鏈堢晫闈?
            self.show()
        
        if route_action == "week":
            # 鍒囨崲鍒板懆瑙嗗浘 
            self.hide()
            self.week_window.refresh_week_data()
            if hasattr(self, 'header') and hasattr(self.header, 'current_weather_data'):
                if self.header.current_weather_data:
                    self.week_window.update_weather_ui(self.header.current_weather_data)
            
            # 鑾峰彇涓荤獥鍙ｅ潗鏍囷紝璁＄畻鍛ㄨ鍥剧殑鐩稿涓績浣嶇疆
            main_geom = self.geometry()
            new_x = main_geom.x() + (main_geom.width() - self.week_window.width()) // 2
            new_y = main_geom.y() + (main_geom.height() - self.week_window.height()) // 2
            self.week_window.move(new_x, new_y)
            self.week_window.show()

        elif route_action == "month":
            # 鏈堣鍥惧垏鎹㈤€昏緫
            self.hide()
            if hasattr(self, 'header') and hasattr(self.header, 'current_weather_data'):
                if self.header.current_weather_data:
                    self.month_window.update_weather_ui(self.header.current_weather_data)
            # 鑾峰彇涓荤獥鍙ｅ潗鏍囷紝璁＄畻鏈堣鍥剧殑鐩稿涓績浣嶇疆
            main_geom = self.geometry()
            new_x = main_geom.x() + (main_geom.width() - self.month_window.width()) // 2
            new_y = main_geom.y() + (main_geom.height() - self.month_window.height()) // 2
            self.month_window.move(new_x, new_y)
            self.month_window.show()
            
        elif route_action == "todo":
            # 鍒囨崲鍒板緟鍔炶鍥?            self.body_stack.setCurrentWidget(self.page_todo)
            self.page_todo.refresh_data() # 鍒囪繃鍘荤殑鏃跺€欏埛鏂颁竴涓嬫暟鎹?            self._sync_primary_query_header()
            
        elif route_action == "day":
            # 鍒囨崲鍥炴棩瑙嗗浘 (涓婚潰鏉?
            self.body_stack.setCurrentWidget(self.page_dashboard)
            self.page_dashboard.refresh_data()
            self._sync_primary_query_header()
            
        elif route_action == "priority":

            self.show_toast("\u8be5\u89c6\u56fe\u5165\u53e3\u5df2\u8c03\u6574")
        else:
            self.show_toast(f"\u51c6\u5907\u5207\u6362\u81f3\uff1a{view_name}")

        if route_action in {"day", "week", "month", "todo"}:
            QTimer.singleShot(0, self._restore_detail_popups)

    def _exit_sort_state_for_view_switch(self, route_action):
        if route_action not in {"day", "week", "month", "todo"}:
            return

        current_widget = self.body_stack.currentWidget()
        if (
            route_action != "day"
            and current_widget == self.page_dashboard
            and self.page_dashboard.has_active_sort()
        ):
            self.page_dashboard.freeze_current_card_order()
            self.page_dashboard.apply_sort_options(ScheduleSortOptions())

        if (
            route_action != "todo"
            and current_widget == self.page_todo
            and self.page_todo.has_active_sort()
        ):
            self.page_todo.freeze_current_card_order()
            self.page_todo.apply_sort_options(ScheduleSortOptions())

        if (
            route_action != "week"
            and hasattr(self, "week_window")
            and self.week_window.isVisible()
        ):
            self.week_window._exit_sort_state_for_close()

        if (
            route_action != "month"
            and hasattr(self, "month_window")
            and self.month_window.isVisible()
        ):
            self.month_window._exit_sort_state_for_close()

        self._sync_primary_sort_indicator()

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
        """Restore main window from month view."""
        # 璁＄畻鐩稿浣嶇疆锛屼互鏈堣鍥惧綋鍓嶄綅缃负涓績锛屾敹缂╁洖涓荤獥鍙?
        month_geom = self.month_window.geometry()
        new_x = month_geom.x() + (month_geom.width() - self.width()) // 2
        new_y = month_geom.y() + (month_geom.height() - self.height()) // 2
        self.move(new_x, new_y)

        self.month_window.hide()
        self.body_stack.setCurrentWidget(self.page_dashboard) # 纭繚璺敱鍥炲埌鐪嬫澘
        self._sync_view_selector_state("day")
        self.page_dashboard.refresh_data()
        self._sync_primary_query_header()
        self.show()

    def restore_from_week_view(self):
        """Restore main window from week view."""
        # 璁＄畻鐩稿浣嶇疆锛屼互鍛ㄨ鍥惧綋鍓嶄綅缃负涓績锛屾敹缂╁洖涓荤獥鍙?
        week_geom = self.week_window.geometry()
        new_x = week_geom.x() + (week_geom.width() - self.width()) // 2
        new_y = week_geom.y() + (week_geom.height() - self.height()) // 2
        self.move(new_x, new_y)

        self.week_window.hide()
        self.body_stack.setCurrentWidget(self.page_dashboard) # 纭繚璺敱鍥炲埌鐪嬫澘
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
        painter.setPen(QPen(QColor(120, 120, 120, 140), 1))
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
        self._exit_sort_states_for_close()
        if self.axis_board is not None:
            self.axis_board.close()
        if self.weather_board is not None:
            self.weather_board.close()
        self._hide_day_query_panels()
        super().closeEvent(event)

    def _exit_sort_states_for_close(self):
        if self.page_dashboard.has_active_sort():
            self.page_dashboard.freeze_current_card_order()
            self.page_dashboard.apply_sort_options(ScheduleSortOptions())
        if self.page_todo.has_active_sort():
            self.page_todo.freeze_current_card_order()
            self.page_todo.apply_sort_options(ScheduleSortOptions())
        if hasattr(self, "week_window"):
            self.week_window._exit_sort_state_for_close()
        if hasattr(self, "month_window"):
            self.month_window._exit_sort_state_for_close()
        self._sync_primary_sort_indicator()

    def switch_week_to_suspend(self):
        """Switch week view to suspend bar."""
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
        """Restore week view from suspend bar."""
        self.suspend_window_week.hide()
        pos = self.suspend_window_week.pos()
        self.week_window.move(pos.x(), pos.y())
        self.week_window.show()

    def switch_month_to_suspend(self):
        """Switch month view to suspend bar."""
        self.suspend_window_month.set_source_gradient_height(self.month_window.height())
        self.month_window.hide()
        pos = self.month_window.pos()
        self.suspend_window_month.move(pos.x(), pos.y())
        self.suspend_window_month.show()

    def switch_suspend_to_month(self):
        """Restore month view from suspend bar."""
        self.suspend_window_month.hide()
        pos = self.suspend_window_month.pos()
        self.month_window.move(pos.x(), pos.y())
        self.month_window.show()

    def _on_week_schedule_updated(self, updated_schedule):
        """Refresh detail popups after week schedule updates."""
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
