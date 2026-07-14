# src/ui/header.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QToolButton, QMenu, QWidgetAction, 
                             QCheckBox, QSpacerItem, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt, QTimer, QTime, QDate, pyqtSignal, QSize, QRectF, QEvent, QObject, QPoint
from PyQt6.QtGui import QIcon, QImage, QPixmap, QPainter, QColor, QPen, QAction
from PyQt6.QtSvg import QSvgRenderer

from ..utils.styles import StyleManager
from ..config import AppConfig
from ..utils.win_api import apply_24h2_border_fix
from src.services.weather_service import WeatherWorker
from .utils.icon_loader import load_colored_svg_pixmap
from .common.weather_icon_label import WeatherIconLabel

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
        painter.setPen(QPen(QColor(AppConfig.COLOR_GRADIENT_START), 1))
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
        self._active = False
        self._hovered = False
        self._update_background()

    def set_active(self, active):
        self._active = bool(active)
        self._update_background()

    def _update_background(self):
        if self._active:
            background = (
                "rgba(255, 255, 255, 0.36)"
                if self._hovered
                else "rgba(255, 255, 255, 0.30)"
            )
        elif self._hovered:
            background = "rgba(255, 255, 255, 0.15)"
        else:
            background = "transparent"
        self.setStyleSheet(
            f"background-color: {background}; border-radius: 4px;"
        )
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            
    def enterEvent(self, event):
        self._hovered = True
        self._update_background()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._hovered = False
        self._update_background()
        super().leaveEvent(event)


class LeadingElideLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._base_style_sheet = ""
        self._elide_label = QLabel(self)
        self._elide_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )
        self._elide_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self._elide_label.setStyleSheet(
            "background: transparent; border: none; color: white; padding: 0px;"
        )
        self._elide_label.hide()
        self.textChanged.connect(self._refresh_elided_text)

    def set_elide_style_sheet(self, style_sheet):
        self._base_style_sheet = style_sheet
        QLineEdit.setStyleSheet(self, style_sheet)
        self._refresh_elided_text()

    def _refresh_elided_text(self):
        text = self.text()
        available_width = max(0, self.width() - 50)
        should_elide = bool(
            text
            and not self.hasFocus()
            and self.fontMetrics().horizontalAdvance(text) > available_width
        )
        if not should_elide:
            self._elide_label.hide()
            QLineEdit.setStyleSheet(self, self._base_style_sheet)
            return

        self._elide_label.setText(
            self.fontMetrics().elidedText(
                text,
                Qt.TextElideMode.ElideLeft,
                available_width,
            )
        )
        self._elide_label.setGeometry(25, 0, available_width, self.height())
        QLineEdit.setStyleSheet(
            self,
            self._base_style_sheet + " QLineEdit { color: transparent; }",
        )
        self._elide_label.show()
        self._elide_label.raise_()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self._refresh_elided_text()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._refresh_elided_text()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh_elided_text()

class HeaderBar(QWidget):
    suspend_requested = pyqtSignal(bool)
    action_requested = pyqtSignal(str)
    search_requested = pyqtSignal()
    search_text_changed = pyqtSignal(str)
    req_open_calendar = pyqtSignal()
    midnight_rollover = pyqtSignal()
    weather_updated = pyqtSignal(dict)
    view_requested = pyqtSignal(str)
    mode_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.drag_pos = None
        self.current_weather_data = {}
        self.setFixedHeight(160)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_header_context_menu)

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
        ratio = self.devicePixelRatio()
        return load_colored_svg_pixmap(icon_path, color_hex, width, height, ratio)

    @staticmethod
    def _load_padded_svg_icon(
        icon_path,
        color_hex="#FFFFFF",
        glyph_size=9,
        canvas_size=16,
    ):
        renderer = QSvgRenderer(icon_path)
        if not renderer.isValid():
            return QIcon(icon_path)

        scale_ratio = 4.0
        canvas_pixels = int(canvas_size * scale_ratio)
        glyph_pixels = glyph_size * scale_ratio
        offset = (canvas_pixels - glyph_pixels) / 2
        image = QImage(
            canvas_pixels,
            canvas_pixels,
            QImage.Format.Format_ARGB32,
        )
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        renderer.render(
            painter,
            QRectF(offset, offset, glyph_pixels, glyph_pixels),
        )
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(image.rect(), QColor(color_hex))
        painter.end()

        pixmap = QPixmap.fromImage(image)
        pixmap.setDevicePixelRatio(scale_ratio)
        return QIcon(pixmap)

    def _set_toolbar_button_icon(self, btn, icon_name, tooltip):
        svg_path = f"assets/icons/{icon_name}"
        pixmap = self._load_colored_svg(svg_path, "#FFFFFF", 24, 24)
        if not pixmap.isNull():
            btn.setPixmap(pixmap)
            btn.setText("")
        else:
            btn.clear()
            btn.setText("?")
        btn.icon_path = svg_path
        if hasattr(btn, "_tooltip_filter"):
            btn._tooltip_filter.text = tooltip

    def set_schedule_display_mode(self, mode_id):
        sort_button = getattr(self, "toolbar_buttons", {}).get("sort")
        if sort_button is None:
            return

        if mode_id == "timetable":
            self._set_toolbar_button_icon(sort_button, "refresh.svg", "刷新课表")
        else:
            self._set_toolbar_button_icon(sort_button, "sort.svg", "排序")

    def _init_weather_service(self):
        self.weather_worker = WeatherWorker(self.my_api_key, self.my_api_host)
        self.weather_worker.data_received.connect(self.update_weather_ui)
        self._start_weather_fetch()
        self.weather_timer = QTimer(self)
        self.weather_timer.timeout.connect(self._start_weather_fetch)
        self.weather_timer.start(1800 * 1000)

    def _start_weather_fetch(self):
        if not self.current_weather_data and hasattr(self, "lbl_weather_icon"):
            self.lbl_weather_icon.start_loading()
        self.weather_worker.start()

    def _setup_search_ui(self):
        self.search = LeadingElideLineEdit()
        self.search.setFixedHeight(26)
        self.search.setPlaceholderText("搜索日程...")
        icon_path = "assets/icons/search.svg"
        self.search_action = self.search.addAction(
            QIcon(icon_path),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        self.search_action.setToolTip("搜索设置")
        self.search_action.triggered.connect(
            lambda _checked=False: self.search_requested.emit()
        )
        self.search_clear_action = self.search.addAction(
            self._load_padded_svg_icon(
                "assets/icons/search_clear.svg",
                glyph_size=10,
                canvas_size=16,
            ),
            QLineEdit.ActionPosition.TrailingPosition,
        )
        self.search_clear_action.setToolTip("清空搜索")
        self.search_clear_action.setVisible(False)
        self.search_clear_action.triggered.connect(self.search.clear)
        self.search.textChanged.connect(self._on_search_text_changed)
        self.search.set_elide_style_sheet(StyleManager.get_search_input_style())

    def _on_search_text_changed(self, text):
        self.search_clear_action.setVisible(bool(text))
        self.search_text_changed.emit(text)

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
        self.lbl_weather_icon = WeatherIconLabel(50, self)
        self.lbl_weather_icon.setFixedHeight(70)
        self.lbl_weather_icon.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.lbl_weather_icon.start_loading()
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
        self.toolbar_buttons = {}
        
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
            self.toolbar_buttons[action_key] = btn
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
        self.lbl_weather_icon.set_weather_icon(svg_path)
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

    def _show_header_context_menu(self, pos):
        from .common.action_context_menu import ActionContextMenu

        menu = ActionContextMenu(self)
        menu.action_requested.connect(self.action_requested.emit)
        menu.view_requested.connect(self.view_requested.emit)
        menu.mode_requested.connect(self.mode_requested.emit)
        menu.exec(self.mapToGlobal(pos))
