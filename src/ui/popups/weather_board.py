from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QBrush, QColor, QIcon, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.config import AppConfig
from src.utils.window_preferences import set_window_pin_state


class WeatherBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(380, 280)
        self._drag_offset = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 14, 18, 18)
        outer.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        self.title_label = QLabel("天气看板")
        self.title_label.setStyleSheet(
            "color: white; font-size: 17px; font-weight: bold; "
            "font-family: 'Microsoft YaHei'; background: transparent;"
        )
        header.addWidget(self.title_label)
        header.addStretch()

        self.btn_close = QPushButton()
        self.btn_close.setFixedSize(28, 28)
        self.btn_close.setIconSize(QSize(12, 12))
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setToolTip("关闭天气看板")
        self.btn_close.setStyleSheet(
            "QPushButton { background: transparent; border: none; border-radius: 4px; } "
            "QPushButton:hover { background: #ff4d4f; }"
        )
        self.btn_close.setIcon(QIcon("assets/icons/close.png"))
        self.btn_close.clicked.connect(self.close)
        header.addWidget(self.btn_close)
        outer.addLayout(header)

        content = QFrame()
        content.setStyleSheet(
            "QFrame { background-color: rgba(255,255,255,0.16); "
            "border: 1px solid rgba(255,255,255,0.45); border-radius: 6px; }"
        )
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 14, 16, 14)
        content_layout.setSpacing(8)

        status = QLabel("天气展示规则（待接入预测 API）")
        status.setStyleSheet(
            "color: white; font-size: 13px; font-weight: bold; "
            "font-family: 'Microsoft YaHei'; background: transparent; border: none;"
        )
        content_layout.addWidget(status)

        rules = QLabel(
            "过去日期：统一显示问号天气图标，温度显示 --°C。\n"
            "今天：显示当前实时天气和当前温度。\n"
            "明天及以后：在 API 实际提供的预报天数内显示预报天气；"
            "超出预报上限后显示问号天气图标。\n"
            "非今天日期：温度统一显示 --°C。\n"
            "看板可展示的天数以后以 API 实际返回范围为准。"
        )
        rules.setWordWrap(True)
        rules.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        rules.setStyleSheet(
            "color: rgba(255,255,255,0.86); font-size: 12px; "
            "line-height: 1.5; font-family: 'Microsoft YaHei'; "
            "background: transparent; border: none;"
        )
        content_layout.addWidget(rules, 1)
        outer.addWidget(content, 1)

    def set_pinned(self, enabled):
        set_window_pin_state(self, enabled)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        painter.fillPath(path, QBrush(gradient))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(0, 0, 0, 28), 1))
        painter.drawPath(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = None
        super().mouseReleaseEvent(event)
