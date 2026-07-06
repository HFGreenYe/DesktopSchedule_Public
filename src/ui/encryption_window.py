# src/ui/encryption_window.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QLinearGradient, QColor, QPen

from ..config import AppConfig


class EncryptionWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_pos = None
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(380, 300)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.bg_frame = QFrame(self)
        self.bg_frame.setStyleSheet("background: transparent;")
        bg_layout = QVBoxLayout(self.bg_frame)
        bg_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.addWidget(self.bg_frame)

        # --- 标题行 ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 10)

        self.title_label = QLabel("安全加密")
        self.title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: white; "
            "border: none; background: transparent; font-family: 'Microsoft YaHei';"
        )
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        self.btn_close = QPushButton(self)
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setToolTip("关闭")
        self.btn_close.setStyleSheet(
            "QPushButton { background: transparent; border: none; "
            "border-top-right-radius: 12px; } "
            "QPushButton:hover { background: #ff4d4f; }"
        )
        self.btn_close.clicked.connect(self.close)
        header_layout.addWidget(
            self.btn_close,
            0,
            Qt.AlignmentFlag.AlignTop,
        )
        bg_layout.addLayout(header_layout)

        # --- 内容区（占位） ---
        self.content_label = QLabel("安全加密设置\n\n功能待实现")
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_label.setStyleSheet(
            "color: rgba(255, 255, 255, 0.7); font-size: 13px; "
            "border: 2px dashed rgba(255, 255, 255, 0.2); border-radius: 8px; "
            "background: rgba(255, 255, 255, 0.05); font-family: 'Microsoft YaHei';"
        )
        bg_layout.addWidget(self.content_label, 1)

    # ==========================================
    # 外观 & 拖拽
    # ==========================================

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        rect = QRectF(10, 10, self.width() - 20, self.height() - 20)
        path.addRoundedRect(rect, 12.0, 12.0)

        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))

        painter.fillPath(path, QBrush(gradient))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(0, 0, 0, 26), 1))
        painter.drawPath(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()
