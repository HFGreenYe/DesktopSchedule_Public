# src/ui/widgets.py
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from..utils.styles import StyleManager
from..config import AppConfig

class DashboardSlot(QFrame):
    """
    对应设计图中下方的三个大横向槽位 
    """
    def __init__(self, title="", parent=None):
        # 必须显式传递 parent 给父类
        super().__init__(parent)
        self.setObjectName("DashboardPanel")
        self.setMinimumHeight(120)
        self.setStyleSheet(StyleManager.get_glass_style())
        
        # 添加外部阴影 
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.layout = QVBoxLayout(self)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {AppConfig.TEXT_COLOR_SECONDARY}; font-size: 14px; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        self.layout.addStretch()

class IconButton(QLabel):
    """
    对应搜索框右侧的那一排功能图标按钮 
    """
    def __init__(self, icon_text, parent=None):
        # 显式传递 parent 给父类，防止在布局中崩溃
        super().__init__(icon_text, parent)
        self.setFixedSize(30, 30)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 按钮样式定义
        self.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                background: transparent;
                border-radius: 5px;
            }
            QLabel:hover {
                background: rgba(255, 255, 255, 40);
            }
        """)