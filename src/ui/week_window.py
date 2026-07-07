# src/ui/week_window.py
#import requests
import time

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QToolButton, QLineEdit, QSizePolicy, QStackedWidget, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QTime, QTimer, QRectF, QSize
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QBrush, QLinearGradient, QIcon, QPixmap, QCursor
from PyQt6.QtSvg import QSvgRenderer
from qframelesswindow import FramelessMainWindow
from zhdate import ZhDate
from datetime import datetime, timedelta

from ..config import AppConfig
from ..utils.win_api import apply_24h2_border_fix
from ..utils.styles import StyleManager

# 引入主界面的添加与选择组件
from .add_view_week import AddScheduleViewWeek
from .time_picker_week import TimePickerViewWeek
from .alarm_picker_week import AlarmPickerViewWeek
from .list_picker import ListPickerView
from ..data.database import db_manager
from ..services.schedule_query_service import ScheduleQueryService
from ..services.schedule_sort_service import ScheduleSortService
from .header import ToolTipFilter
from .dashboard import AdaptiveLabel 
from .components import CountdownToolTipFilter, get_colored_icon
from .common.week_day_block import DayBlock
from .common.action_context_menu import ActionContextMenu
from .common.weather_icon_label import WeatherIconLabel
from .utils.window_drag_controller import WindowDragController

class WeekScheduleCard(QFrame):
    """周视图中的单条日程小卡片"""
    clicked = pyqtSignal(object)
    # 右键菜单需要的三个信号
    req_status = pyqtSignal(int, int) # id, status
    req_pin = pyqtSignal(int, bool)   # id, is_pinned
    req_delete = pyqtSignal(int)      # id
    drag_started = pyqtSignal(object)
    drag_finished = pyqtSignal(object, object)

    def __init__(self, schedule_obj, parent=None):
        super().__init__(parent)
        self.setProperty("windowDragDisabled", True)
        self.data = schedule_obj
        self.schedule_obj = schedule_obj
        
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
        self.setFixedHeight(46) 
        
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
        
        # 根据是否已完成动态调整标题和圆点样式
        self.lbl_title = AdaptiveLabel(schedule_obj.title, max_size=11, min_size=10)

        # 2. 设置状态样式
        is_completed = getattr(self.schedule_obj, 'status', 0) == 1
        if is_completed:
            self.dot.setStyleSheet("background-color: #cccccc; border-radius: 4px;")
            self.lbl_title.setStyleSheet("color: rgba(51, 51, 51, 0.5); font-weight: bold; border: none; background: transparent;")
            self.lbl_title.setStrikeOut(True)
        else:
            p_color = {2: "#FF4D4F", 1: "#FAAD14", 0: "#52C41A"}.get(schedule_obj.priority, "#52C41A")
            self.dot.setStyleSheet(f"background-color: {p_color}; border-radius: 4px;")
            self.lbl_title.setStyleSheet("color: #333333; font-weight: bold; border: none; background: transparent;")
            
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
        self.lbl_time.setStyleSheet("color: #888888;padding-left: 10px; font-size: 9px; border: none; background: transparent;")
        
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
            pixmap = get_colored_icon("week_top_color.svg", "#0cc0df", 16)
            self.icon_pin.setPixmap(pixmap)
            #self.icon_pin.setScaledContents(True)
            self.icon_pin.setStyleSheet("background: transparent;")

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
            if (event.pos() - self._click_pos).manhattanLength() < 5:
                self.clicked.emit(self.schedule_obj)
            del self._click_pos
            event.accept()
        else:
            super().mouseReleaseEvent(event)

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

from .todo import TodoListContainer
from ..utils.window_preferences import get_primary_pin_preference
class WeekWindow(FramelessMainWindow):
    """
    680x400 独立周视图窗口 (去线极简版)
    """
    restore_requested = pyqtSignal()
    suspend_requested = pyqtSignal()
    request_schedule_detail = pyqtSignal(object)
    view_selected = pyqtSignal(str)
    schedule_updated = pyqtSignal(object)
    day_double_clicked = pyqtSignal(QDate)
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
        self._drag_edge_entered_at = 0.0
        self._drag_last_turn_at = 0.0
        self._drag_edge_timer = QTimer(self)
        self._drag_edge_timer.setInterval(60)
        self._drag_edge_timer.timeout.connect(self._check_drag_week_edge)
        # 编辑模式状态位，控制背景渲染！
        self.is_edit_mode = False 

        self._setup_ui()
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
        self.top_container.setStyleSheet("""
            QWidget#week_top_surface {
                background: transparent;
                border-top: 1px solid rgba(0, 0, 0, 0.1);
                border-left: 1px solid rgba(0, 0, 0, 0.1);
                border-right: 1px solid rgba(0, 0, 0, 0.1);
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
            
            if icon_name == "view.svg":
                self.btn_view_toggle = btn 
                self.btn_view_toggle.clicked.connect(self.toggle_view_selector)
            elif icon_name == "add.svg":
                btn.clicked.connect(self.switch_to_add_page)
                
            icons_row.addWidget(btn)
        icons_row.addStretch()
        tools_layout.addLayout(icons_row)

        # 1. 搜索框 
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索日程...")
        self.search_box.setFixedSize(123, 18) 
        self.search_box.setStyleSheet(StyleManager.get_search_input_style() + " QLineEdit { font-size: 10px; padding: 0px 4px; }")
        
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
        
        views = {"day": "日", "week": "周", "month": "月", "todo": "待办"}
        for vid, vname in views.items():
            v_btn = QPushButton(vname)
            v_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            if vid == "week":
                v_btn.setStyleSheet("background-color: rgba(0, 0, 0, 0.15); color: white;")
                
            v_btn.clicked.connect(lambda _, v=vid: self._on_view_selected(v))
            vs_layout.addWidget(v_btn, 1)
            
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
        status_row.addStretch() # 顶满左侧区域

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
        
        for i in range(7):
            col_widget = QWidget()
            col_widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
            
            col_layout = QVBoxLayout(col_widget)
            col_layout.setContentsMargins(2, 0, 2, 0)
            col_layout.setSpacing(4)
            
            lbl_week = QLabel(week_names[i])
            lbl_week.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_week.setStyleSheet("color: white; font-size: 10px; font-weight: bold; font-family: 'Microsoft YaHei';")
            
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
        self.content_area = QWidget()
        self.content_area.setObjectName("week_content_surface")
        # 初始为纯白背景
        self.content_area.setStyleSheet("""
            QWidget#week_content_surface {
                background-color: #FFFFFF;
                border-left: 1px solid rgba(0, 0, 0, 0.1);
                border-right: 1px solid rgba(0, 0, 0, 0.1);
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """)
        
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建堆栈容器
        self.body_stack = QStackedWidget()
        content_layout.addWidget(self.body_stack)
        
        # --- 第0页：周日程展示板 ---
        self.page_week_board = QWidget()
        week_board_layout = QHBoxLayout(self.page_week_board)
        week_board_layout.setContentsMargins(0, 0, 0, 0)
        week_board_layout.setSpacing(0)
        
        self.bottom_panels = []
        self.placeholder_labels = [] 
        
        # 给每一列配置专属的“文字”和“对齐方式”
        placeholder_config = {
            2: ("  ", Qt.AlignmentFlag.AlignRight),   # 周三：靠右
            3: ("点击添加日程", Qt.AlignmentFlag.AlignHCenter), # 周四：居中
            4: ("  ", Qt.AlignmentFlag.AlignLeft)     # 周五：靠左
        }
        
        for i in range(7):
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True) 
            scroll_area.setFrameShape(QFrame.Shape.NoFrame) 
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) 
            scroll_area.setStyleSheet("background: transparent; border: none;")

            panel = TodoListContainer(self)
            panel.setStyleSheet("background-color: #FFFFFF;")
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
            week_board_layout.addWidget(scroll_area, stretch=1)
            
        self.body_stack.addWidget(self.page_week_board)
        
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
        main_layout.addWidget(self.content_area, stretch=1)
        
        self._setup_routing_signals()


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

    def _set_edit_mode_bg(self, is_edit):
        """动态切换下半部分盒子的颜色，并命令窗口重绘自己"""
        self.is_edit_mode = is_edit
        if is_edit:
            self.content_area.setStyleSheet("""
                QWidget#week_content_surface {
                    background-color: transparent;
                    border-left: 1px solid rgba(0, 0, 0, 0.1);
                    border-right: 1px solid rgba(0, 0, 0, 0.1);
                    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
                    border-bottom-left-radius: 8px;
                    border-bottom-right-radius: 8px;
                }
            """)
        else:
            self.content_area.setStyleSheet("""
                QWidget#week_content_surface {
                    background-color: #FFFFFF;
                    border-left: 1px solid rgba(0, 0, 0, 0.1);
                    border-right: 1px solid rgba(0, 0, 0, 0.1);
                    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
                    border-bottom-left-radius: 8px;
                    border-bottom-right-radius: 8px;
                }
            """)
        
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
        if self.body_stack.currentWidget() == self.page_add:
            self.switch_to_main_board()
            return
        
        today = datetime.now().date()
        if self.current_selected_date.toPyDate() < today:
            print("该日期已过期，无法添加日程") 
            return
            
        self.page_add.reset()
        self.body_stack.setCurrentWidget(self.page_add)
        self._set_edit_mode_bg(True)

    def switch_to_main_board(self):
        self.body_stack.setCurrentWidget(self.page_week_board)
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

    def refresh_week_data(self):
        for i in range(7):
            iter_date = self.current_monday.addDays(i)
            block = self.day_blocks[i]
            block.set_data(iter_date, self.get_lunar_str(iter_date))
            block.set_selected(iter_date == self.current_selected_date)
            is_selected = (iter_date == self.current_selected_date)
            block.set_selected(is_selected)
            
            if hasattr(self, 'bottom_panels') and i < len(self.bottom_panels):
                if is_selected:
                    # 选中时变非常浅的灰色
                    self.bottom_panels[i].setStyleSheet("background-color: #F5F5F5;") 
                else:
                    # 未选中恢复纯白
                    self.bottom_panels[i].setStyleSheet("background-color: #FFFFFF;")

        month = self.current_monday.month()    
        week_num = self.current_monday.weekNumber()[0]
        self.lbl_week_num.setText(f"{month}月 第{week_num}周")
        self.load_week_schedules_from_db()

    def load_week_schedules_from_db(self):
        """直接从数据库读取本周所有数据，并渲染到 7 个面板"""
        has_any_schedule = False
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

        # 2. 遍历本周 7 天，向数据库查询
        for day_index in range(7):
            target_date = self.current_monday.addDays(day_index).toPyDate()
            daily_schedules = db_manager.get_schedules_for_date(target_date)
            valid_schedules =[s for s in daily_schedules if ScheduleQueryService.is_schedule(s) and getattr(s, 'status', 0) != 2]

            if valid_schedules:
                has_any_schedule = True
                panel_layout = self.bottom_panels[day_index].layout()

                valid_schedules = ScheduleSortService.sort_for_week_view(valid_schedules)
                
                for sched_obj in valid_schedules:
                    if active_drag_id is not None and sched_obj.id == active_drag_id:
                        continue
                    card = WeekScheduleCard(sched_obj)
                    card.clicked.connect(self.request_schedule_detail.emit)
                    card.req_status.connect(self._handle_schedule_status_change)
                    card.req_pin.connect(self._handle_schedule_pin_change)
                    card.req_delete.connect(self._handle_schedule_delete)
                    card.drag_started.connect(self._begin_card_drag)
                    card.drag_finished.connect(self._finish_card_drag)
                    panel_layout.insertWidget(panel_layout.count() - 1, card)

        self.update_placeholder_visibility(has_any_schedule)
        self._sync_panel_scroll_heights()

    def update_placeholder_visibility(self, has_any_schedule: bool):
        """
        核心控制：根据本周是否含有任何日程，统一显示或隐藏跨列提示字
        """
        for lbl in self.placeholder_labels:
            lbl.setVisible(not has_any_schedule)

    def _sync_panel_scroll_heights(self):
        for panel in self.bottom_panels:
            layout = panel.layout()
            if layout is not None:
                panel.setMinimumHeight(layout.sizeHint().height())

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
        self.refresh_week_data()

    def _on_day_double_clicked(self, qdate):
        self._on_day_clicked(qdate)
        self.day_double_clicked.emit(qdate)

    def _handle_week_context_action(self, action_name):
        if action_name == "add":
            self.switch_to_add_page()

    def _handle_week_context_view(self, view_name):
        self._on_view_selected(view_name)

    def mousePressEvent(self, event):
        # 如果视图选择器正开着，点窗口上半部分任何空白处都会关掉它
        if hasattr(self, 'view_selector_container') and self.view_selector_container.isVisible():
            self.close_view_selector()
        super().mousePressEvent(event)

    def _on_window_drag_started(self):
        self.close_view_selector()

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent 
        
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

                menu = ActionContextMenu(self)
                menu.action_requested.connect(self._handle_week_context_action)
                menu.view_requested.connect(self._handle_week_context_view)
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
        if self.is_edit_mode or self.body_stack.currentWidget() != self.page_week_board:
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

    def toggle_view_selector(self):
        """点击视图图标时，自动判断是展开还是收起"""
        if self.view_selector_container.isVisible():
            self.close_view_selector()
        else:
            self.open_view_selector()

    def open_view_selector(self):
        """隐藏搜索框，显示视图选择器，并高亮顶部视图图标"""
        self.search_box.hide()
        self.view_selector_container.show()
        if hasattr(self, 'btn_view_toggle'):
            self.btn_view_toggle.setStyleSheet("QPushButton { background: rgba(255,255,255,0.3); border-radius: 3px; }")

    def close_view_selector(self):
        """隐藏视图选择器，恢复搜索框，并取消图标高亮"""
        self.view_selector_container.hide()
        self.search_box.show()
        if hasattr(self, 'btn_view_toggle'):
            self.btn_view_toggle.setStyleSheet("QPushButton { background: transparent; border: none; } QPushButton:hover { background: rgba(255,255,255,0.2); border-radius: 3px; }")

    def _on_view_selected(self, vid):
        """处理视图点击事件"""
        self.close_view_selector()
        if vid == "week":
            pass # 当前已经在周视图，无操作
        else:
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
