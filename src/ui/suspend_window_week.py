# src/ui/suspend_window_week.py
from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QRectF
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QLinearGradient, QColor, QIcon
from qframelesswindow import FramelessWindow

from ..config import AppConfig
from ..utils.win_api import apply_24h2_border_fix
from ..utils.signals import global_signals
from ..utils.styles import StyleManager

class SuspendWindowWeek(FramelessWindow):
    restore_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        # 高度定为 30px，宽度和周界面保持一致 680px
        self.setFixedSize(680, 30)
        self._source_gradient_height = 125
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
        # === 中间：还原按钮 (保持绝对居中定位) ===
        self.btn_restore = QPushButton(self)
        self.btn_restore.setFixedSize(30, 30)
        self.btn_restore.setIconSize(QSize(20, 20))
        self.btn_restore.setIcon(QIcon(AppConfig.ICON_RESTORE))
        self.btn_restore.setStyleSheet("""
            QPushButton { background: transparent; border: none; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); border-radius: 15px; }
        """)
        self.btn_restore.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restore.setToolTip("还原周视图")
        self.btn_restore.clicked.connect(self.restore_requested.emit)
        
        # === 右侧：工具按钮组 ===
        self.top_layout = QHBoxLayout(self)
        self.top_layout.setContentsMargins(15, 0, 0, 0)
        self.top_layout.setSpacing(2)  # 将原本的 10 改为 2，让图标排列更紧凑，与主界面对齐
        
        self.top_layout.addStretch()   # 把后面的按钮全部推到最右侧

        self.btn_more = QPushButton()
        self.btn_more.setFixedSize(30, 30)
        self.btn_more.setIcon(QIcon("assets/icons/more.png"))
        self.btn_more.setIconSize(QSize(16, 16))
        self.btn_more.setToolTip("更多")
        self.btn_more.setStyleSheet(StyleManager.get_button_style())
        from .components import SharedMoreMenu
        self.shared_more_menu = SharedMoreMenu(self, self.btn_more, show_festival_option=True)
        self.btn_more.clicked.connect(self.shared_more_menu.show_menu)
        self.top_layout.addWidget(self.btn_more)
        
        # 同步按钮
        self.btn_sync = QPushButton()
        self.btn_sync.setFixedSize(30, 30)
        self.btn_sync.setIcon(QIcon("assets/icons/sync.png"))
        self.btn_sync.setIconSize(QSize(16, 16))
        self.btn_sync.setToolTip("云同步")
        self.btn_sync.setStyleSheet(StyleManager.get_button_style())
        self.top_layout.addWidget(self.btn_sync)
        
        # 关闭按钮
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
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path.addRoundedRect(rect, 5.0, 5.0)
        gradient = QLinearGradient(0, 0, 0, self._source_gradient_height)
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        painter.fillPath(path, QBrush(gradient))

    # 拖拽逻辑
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

