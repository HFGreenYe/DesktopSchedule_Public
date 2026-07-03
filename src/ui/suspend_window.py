# src/ui/suspend_window.py
from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QRectF
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QLinearGradient, QColor, QIcon
from qframelesswindow import FramelessWindow

from ..config import AppConfig
from ..utils.win_api import apply_24h2_border_fix
from ..utils.signals import global_signals
from ..utils.styles import StyleManager

class SuspendWindow(FramelessWindow):
    restore_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedSize(AppConfig.DEFAULT_WIDTH, 30)
        self._source_gradient_height = 600
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        if hasattr(self, 'titleBar'):
            self.titleBar.hide()
        
        self._init_ui()
        
        self.win_id = int(self.winId())
        apply_24h2_border_fix(self.win_id)
        
        global_signals.skin_changed.connect(self.update)

    def set_source_gradient_height(self, height):
        self._source_gradient_height = max(self.height(), int(height))
        self.update()

    def _init_ui(self):
        # === A. 中间：还原按钮 (Absolute Center) ===
        self.btn_restore = QPushButton(self)
        # 强制尺寸为 30x30，与主界面一致
        self.btn_restore.setFixedSize(30, 30)
        # 图标大小设为 16x16 
        self.btn_restore.setIconSize(QSize(20, 20))
        self.btn_restore.setIcon(QIcon(AppConfig.ICON_RESTORE))
        self.btn_restore.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restore.setStyleSheet("QPushButton { background: transparent; border: none; } QPushButton:hover { background: rgba(255, 255, 255, 40); border-radius: 15px; }")
        self.btn_restore.clicked.connect(self.restore_requested.emit)

        # === B. 右侧：系统按钮 ===
        self.top_layout = QHBoxLayout(self)
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(0)
        self.top_layout.addStretch()

        # 更多
        self.btn_more = QPushButton()
        self.btn_more.setFixedSize(30, 30)
        self.btn_more.setIcon(QIcon("assets/icons/more.png"))
        self.btn_more.setIconSize(QSize(16, 16)) 
        self.btn_more.setToolTip("更多")
        self.btn_more.setStyleSheet(StyleManager.get_button_style(is_close=False)) 
        from .components import SharedMoreMenu
        self.shared_more_menu = SharedMoreMenu(self, self.btn_more)
        self.btn_more.clicked.connect(self.shared_more_menu.show_menu)
        self.top_layout.addWidget(self.btn_more)

        # 最小化
        self.btn_sync = QPushButton()
        self.btn_sync.setFixedSize(30, 30)
        self.btn_sync.setIcon(QIcon("assets/icons/sync.png"))
        self.btn_sync.setIconSize(QSize(16, 16)) 
        self.btn_sync.setToolTip("最小化")
        self.btn_sync.setStyleSheet(StyleManager.get_button_style(is_close=False))
        self.top_layout.addWidget(self.btn_sync)

        # 关闭
        self.btn_close = QPushButton()
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setIcon(QIcon("assets/icons/close.png"))
        self.btn_close.setIconSize(QSize(16, 16))
        self.btn_close.setToolTip("关闭程序")
        self.btn_close.setStyleSheet(StyleManager.get_button_style(is_close=True))
        self.btn_close.clicked.connect(QApplication.instance().quit) 
        self.top_layout.addWidget(self.btn_close)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'btn_restore'):
            center_x = (self.width() - self.btn_restore.width()) // 2
            self.btn_restore.move(center_x, 0)
            self.btn_restore.raise_()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        # 0.5偏移防止锯齿
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path.addRoundedRect(rect, 5.0, 5.0)

        gradient = QLinearGradient(0, 0, 0, self._source_gradient_height)
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        painter.fillPath(path, QBrush(gradient))

    # 拖拽逻辑保持不变
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'drag_pos') and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
