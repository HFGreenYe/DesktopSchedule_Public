# src/ui/header.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QToolButton, QMenu, QWidgetAction, 
                             QCheckBox, QSpacerItem, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt, QTimer, QTime, QDate, pyqtSignal, QSize, QRectF, QEvent, QObject, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QAction
from PyQt6.QtSvg import QSvgRenderer

from ..utils.styles import StyleManager
from ..config import AppConfig
from ..utils.win_api import apply_24h2_border_fix
from src.services.weather_service import WeatherWorker

import os
from dotenv import load_dotenv

class CustomToolTip(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(parent, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setText(text)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setStyleSheet("""
            color: #333333;
            font-family: "Microsoft YaHei UI";
            font-size: 12px;
            padding: 5px 8px;
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) 
        painter.setBrush(QColor("#ffffff"))       
        painter.setPen(QPen(QColor("#0cc0df"), 1)) 
        rect = self.rect().adjusted(0, 0, -1, -1)
        painter.drawRoundedRect(rect, 4, 4) 
        super().paintEvent(event)

    def show_at(self, pos):
        self.adjustSize()
        self.move(pos.x() + 10, pos.y() + 10)
        self.show()

# 气泡过滤器
class ToolTipFilter(QObject):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.tooltip = None
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.show_tooltip)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Enter:
            self.timer.start(400)
            return True
        elif event.type() == QEvent.Type.Leave:
            self.timer.stop()
            self._close_tooltip()
            return True
        elif event.type() == QEvent.Type.MouseButtonPress:
            self.timer.stop()
            self._close_tooltip()
            return False
        # 修复残留
        elif event.type() == QEvent.Type.Hide or event.type() == QEvent.Type.FocusOut:
            self.timer.stop()
            self._close_tooltip()
            return False
        return False

    def show_tooltip(self):
        from PyQt6.QtGui import QCursor
        if not self.tooltip:
            self.tooltip = CustomToolTip(self.text)
        self.tooltip.show_at(QCursor.pos())

    def _close_tooltip(self):
        if self.tooltip:
            self.tooltip.close()
            self.tooltip = None

class ClickableIcon(QLabel):
    clicked = pyqtSignal()

    def __init__(self, icon_path, size, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_path = icon_path
        self.icon_size = size
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            
    def enterEvent(self, event):
        self.setStyleSheet("background-color: rgba(255, 255, 255, 0.15); border-radius: 4px;")
        
    def leaveEvent(self, event):
        self.setStyleSheet("background-color: transparent;")

class HeaderBar(QWidget):
    suspend_requested = pyqtSignal(bool)
    action_requested = pyqtSignal(str)
    req_open_calendar = pyqtSignal()
    midnight_rollover = pyqtSignal() 
    weather_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.drag_pos = None
        self.current_weather_data = {}
        self.setFixedHeight(160)
        
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("header_container") 
        self.setStyleSheet(StyleManager.get_header_container_style())
        
        self._setup_hud_ui()
        self._start_clock()
        
        # 加载 .env 文件中的环境变量
        load_dotenv()
        
        # 安全读取 API 密钥和 Host
        self.my_api_key = os.getenv("QWEATHER_API_KEY")
        self.my_api_host = os.getenv("QWEATHER_API_HOST")
        
        if not self.my_api_key or not self.my_api_host:
            print("⚠️ 警告：未能在 .env 文件中读取到天气 API 配置！") 
        self._init_weather_service()

    def _load_colored_svg(self, icon_path, color_hex, width, height):
        renderer = QSvgRenderer(icon_path)
        if not renderer.isValid():
            return QPixmap()
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

    def _init_weather_service(self):
        self.weather_worker = WeatherWorker(self.my_api_key, self.my_api_host)
        self.weather_worker.data_received.connect(self.update_weather_ui)
        self.weather_worker.start()
        self.weather_timer = QTimer(self)
        self.weather_timer.timeout.connect(self.weather_worker.start)
        self.weather_timer.start(1800 * 1000)

    def _setup_search_ui(self):
        self.search = QLineEdit()
        self.search.setFixedHeight(26)
        self.search.setPlaceholderText("搜索日程...")
        icon_path = "assets/icons/search.svg"
        self.search.addAction(QIcon(icon_path), QLineEdit.ActionPosition.LeadingPosition)
        self.search.setStyleSheet(StyleManager.get_search_input_style())

    def _setup_hud_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- 顶部行 ---
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.addStretch()

        self.btn_suspend = QPushButton(self)
        self.btn_suspend.setFixedSize(30, 30)
        self.btn_suspend.setIcon(QIcon(AppConfig.ICON_HANG_UP))
        self.btn_suspend.setIconSize(QSize(20, 20))
        self.btn_suspend.setStyleSheet("QPushButton { background: transparent; border: none; }")
        self.btn_suspend.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_suspend.clicked.connect(self._on_suspend_clicked)
        self.btn_suspend.raise_()

        self.btn_more = self._create_control_btn("assets/icons/more.png", "更多")
        self.btn_more.setIconSize(QSize(16, 16))
        from .components import SharedMoreMenu
        self.shared_more_menu = SharedMoreMenu(self.parent_window, self.btn_more)
        self.btn_more.clicked.connect(self.shared_more_menu.show_menu)
        
        self.btn_sync = self._create_control_btn("assets/icons/sync.png", "云同步")
        self.btn_sync.setIconSize(QSize(16, 16))
        self.btn_sync.setProperty("role", "windowControl")
        self.btn_sync.setProperty("variant", "toolbar")
        self.btn_sync.setProperty("state", "normal")
        # Clear local stylesheet for this single trial control so app-level QSS can apply.
        self.btn_sync.setStyleSheet("")
        
        self.btn_close = self._create_control_btn("assets/icons/close.png", "关闭", True)
        self.btn_close.setIconSize(QSize(16, 16))
        self.btn_close.clicked.connect(self.parent_window.close)

        top_row.addWidget(self.btn_more)
        top_row.addWidget(self.btn_sync)
        top_row.addWidget(self.btn_close)
        self.main_layout.addLayout(top_row)

        # --- 内容容器 ---
        self.content_container = QWidget()
        self.content_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.content_container.setFixedHeight(155)
        self.container_layout = QVBoxLayout(self.content_container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)

        # --- 时间与天气 ---
        hud_row = QHBoxLayout()
        hud_row.setContentsMargins(30, 0, 40, 5)
        
        left_container = QVBoxLayout()
        left_container.setSpacing(-5)
        self.lbl_time = QLabel("00:00")
        self.lbl_time.setFixedHeight(70)
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.lbl_time.setStyleSheet('font-family: "Segoe UI Variable Display"; font-size: 64px; font-weight: 200;')
        self.lbl_date_info = QLabel("Loading...")
        self.lbl_date_info.setStyleSheet('font-size: 18px; padding-bottom: 0px;')
        self.lbl_date_info.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        left_container.addWidget(self.lbl_time)
        left_container.addWidget(self.lbl_date_info)

        # 赋予日期文字交互能力
        self.lbl_date_info.setCursor(Qt.CursorShape.PointingHandCursor) 
        self.lbl_date_info.setToolTip("点击切换日期") 
        self.lbl_date_info.installEventFilter(self)

        hud_row.addLayout(left_container)

        hud_row.addStretch()

        right_container = QVBoxLayout()
        right_container.setSpacing(0)
        spacer = QSpacerItem(0, 8)
        right_container.addSpacerItem(spacer)
        self.lbl_weather_icon = QLabel(" ⛅ ")
        self.lbl_weather_icon.setFixedHeight(70)
        self.lbl_weather_icon.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.lbl_temp = QLabel("--°C")
        self.lbl_temp.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.lbl_temp.setStyleSheet('font-size: 18px; padding-bottom: 0px;')
        right_container.addWidget(self.lbl_weather_icon)
        right_container.addWidget(self.lbl_temp)
        hud_row.addLayout(right_container)

        self.container_layout.addLayout(hud_row)
        self.container_layout.addSpacing(5)

        # --- 底部：搜索框 + 按钮组 ---
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(15, 0, 15, 25)
        
        self._setup_search_ui()
        
        self.icon_group = QHBoxLayout()
        self.icon_group.setSpacing(3)
        
        buttons_config = [
            ("skin.svg", "换肤"),
            ("view.svg", "视图"),
            ("add.svg", "添加"),
            ("sort.svg", "排序"),
            ("filter.svg", "筛选")
        ]
        
        for icon_name, tooltip in buttons_config:
            btn = ClickableIcon(f"assets/icons/{icon_name}", 24, self)
            bg_filter = ToolTipFilter(tooltip, btn) 
            btn.installEventFilter(bg_filter)
            btn._tooltip_filter = bg_filter
            svg_path = f"assets/icons/{icon_name}"
            pixmap = self._load_colored_svg(svg_path, "#FFFFFF", 24, 24)
            if not pixmap.isNull():
                btn.setPixmap(pixmap)
            else:
                btn.setText("?")
            action_key = icon_name.split('.')[0]
            btn.clicked.connect(lambda name=action_key: self.action_requested.emit(name))
            self.icon_group.addWidget(btn)

        bottom_row.addWidget(self.search, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)
        bottom_row.addLayout(self.icon_group, stretch=0)
        bottom_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.container_layout.addLayout(bottom_row)
        self.main_layout.addWidget(self.content_container)

    def update_weather_ui(self, data):
        if not data: return
        self.current_weather_data = data      
        self.weather_updated.emit(data)
        icon_code = data['icon']
        svg_path = f"assets/weather/{icon_code}-fill.svg"
        colored_pixmap = self._load_colored_svg(svg_path, "#FFFFFF", 50, 50)
        if not colored_pixmap.isNull():
            self.lbl_weather_icon.setPixmap(colored_pixmap)
            self.lbl_weather_icon.setText("") 
        else:
            self.lbl_weather_icon.setText("❓")
        self.lbl_temp.setText(f"{data['temp']}°C")
        tooltip = f"{data['city']}: {data['text']} {data['temp']}°C"
        self.lbl_weather_icon.setToolTip(tooltip)
        self.lbl_temp.setToolTip(tooltip)

    def _create_control_btn(self, icon_path, tip, is_close=False):
        btn = QToolButton() 
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(16, 16))
        if tip:
            btn._tooltip_filter = ToolTipFilter(tip, btn)
            btn.installEventFilter(btn._tooltip_filter)
        btn.setFixedSize(30, 30)
        btn.setStyleSheet(StyleManager.get_window_control_style(is_close=is_close))
        return btn

    def _start_clock(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)
        
        # 记录程序启动时的“真实物理日期”
        self.last_real_date = QDate.currentDate()
        self._update_time()

    def _update_time(self):
        # 1. 正常更新分钟和小时
        now = QTime.currentTime()
        self.lbl_time.setText(now.toString("HH:mm"))
        
        # 2. 跨天侦测
        curr_date = QDate.currentDate()
        if curr_date != self.last_real_date:
            self.last_real_date = curr_date # 更新记录
            self.midnight_rollover.emit()   # 通知主窗口

    def _on_suspend_clicked(self):
        self.suspend_requested.emit(True) 

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.parent_window.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos:
            self.parent_window.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'btn_suspend'):
            center_x = (self.width() - 30) // 2 
            self.btn_suspend.move(center_x, 0)

    def eventFilter(self, obj, event):
        # 拦截交互事件
        from PyQt6.QtCore import QEvent 
        if obj == getattr(self, 'lbl_date_info', None) and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self.req_open_calendar.emit()
                return True
                
        return super().eventFilter(obj, event)
