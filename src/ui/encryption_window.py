# src/ui/encryption_window.py
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QLinearGradient, QColor, QPen, QIcon, QImage, QPixmap
from PyQt6.QtSvg import QSvgRenderer

from ..config import AppConfig
from ..utils.window_preferences import set_window_pin_state


class EncryptionWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_pos = None
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(380, 300)

        # 置顶状态默认与主界面保持一致（主界面默认置顶）
        self.is_pinned = True
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

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
        bg_layout.addLayout(header_layout)

        # --- 内容区 ---
        content_layout = QVBoxLayout()
        content_layout.setSpacing(8)

        item_style = (
            "color: rgba(255, 255, 255, 0.85); font-size: 13px; "
            "padding: 12px 16px; "
            "border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 6px; "
            "background: rgba(255, 255, 255, 0.06); font-family: 'Microsoft YaHei';"
        )

        self.lbl_startup_lock = QLabel("🔐  启动密保")
        self.lbl_startup_lock.setStyleSheet(item_style)
        self.lbl_startup_lock.setCursor(Qt.CursorShape.PointingHandCursor)
        content_layout.addWidget(self.lbl_startup_lock)

        self.lbl_suspend_lock = QLabel("🔓  放下密保")
        self.lbl_suspend_lock.setStyleSheet(item_style)
        self.lbl_suspend_lock.setCursor(Qt.CursorShape.PointingHandCursor)
        content_layout.addWidget(self.lbl_suspend_lock)

        self.lbl_data_encrypt = QLabel("🗄️  数据加密")
        self.lbl_data_encrypt.setStyleSheet(item_style)
        self.lbl_data_encrypt.setCursor(Qt.CursorShape.PointingHandCursor)
        content_layout.addWidget(self.lbl_data_encrypt)

        self.lbl_auto_suspend = QLabel("⏸️  自动挂起")
        self.lbl_auto_suspend.setStyleSheet(item_style)
        self.lbl_auto_suspend.setCursor(Qt.CursorShape.PointingHandCursor)
        content_layout.addWidget(self.lbl_auto_suspend)

        content_layout.addStretch()
        bg_layout.addLayout(content_layout, 1)

        # --- 右上角绝对定位按钮 ---
        common_style = (
            "QPushButton { background: transparent; border: none; }"
            "QPushButton:hover { background: rgba(255, 255, 255, 0.2); border-radius: 4px; }"
        )

        self.btn_account = QPushButton(self)
        self.btn_account.setFixedSize(30, 30)
        self.btn_account.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_account.setToolTip("账户设置")
        self.btn_account.setStyleSheet(common_style)

        self.btn_pin = QPushButton(self)
        self.btn_pin.setFixedSize(30, 30)
        self.btn_pin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pin.setToolTip("窗口置顶")
        self.btn_pin.setStyleSheet(common_style)
        self.btn_pin.clicked.connect(self._toggle_pin)

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

        self._update_nav_icons()

    # ==========================================
    # 图标渲染
    # ==========================================

    def _get_icon(self, icon_name, color, target_size=16):
        path = f"assets/icons/{icon_name}"
        if not os.path.exists(path):
            return QPixmap()

        scale_ratio = 4.0
        high_res_size = int(target_size * scale_ratio)
        image = QImage(high_res_size, high_res_size, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        if icon_name.lower().endswith('.svg'):
            renderer = QSvgRenderer(path)
            if renderer.isValid():
                renderer.render(painter)
        else:
            src_img = QImage(path)
            if not src_img.isNull():
                src_img = src_img.scaled(
                    high_res_size, high_res_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                x = (high_res_size - src_img.width()) // 2
                y = (high_res_size - src_img.height()) // 2
                painter.drawImage(x, y, src_img)
        painter.end()

        painter = QPainter(image)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        if isinstance(color, str):
            color_obj = QColor(color)
        else:
            color_obj = color
        painter.fillRect(image.rect(), color_obj)
        painter.end()

        pixmap = QPixmap.fromImage(image)
        pixmap.setDevicePixelRatio(scale_ratio)
        return pixmap

    # ==========================================
    # 置顶 / 按钮
    # ==========================================

    def _toggle_pin(self):
        self.set_pinned(not self.is_pinned)

    def set_pinned(self, enabled):
        self.is_pinned = bool(enabled)
        set_window_pin_state(self, self.is_pinned)
        self._update_nav_icons()

    def _update_nav_icons(self):
        c_white = QColor(255, 255, 255, 255)
        c_grey = QColor(255, 255, 255, 150)

        close_icon = self._get_icon("close.png", c_white, 12)
        if not close_icon.isNull():
            self.btn_close.setIcon(QIcon(close_icon))
            self.btn_close.setText("")
        else:
            self.btn_close.setText("✕")

        pin_color = c_white if self.is_pinned else c_grey
        pm_pin = self._get_icon("pin.svg", pin_color, 16)
        if not pm_pin.isNull():
            self.btn_pin.setIcon(QIcon(pm_pin))
        else:
            self.btn_pin.setText("📌")

        pm_account = self._get_icon("admin.svg", c_white, 16)
        if not pm_account.isNull():
            self.btn_account.setIcon(QIcon(pm_account))
        else:
            self.btn_account.setText("👤")

        self._update_button_positions()

    def _update_button_positions(self):
        offset = 10
        if hasattr(self, 'btn_close'):
            self.btn_close.move(self.width() - offset - 30, 10)
            self.btn_close.raise_()
            offset += 32
        if hasattr(self, 'btn_pin'):
            self.btn_pin.move(self.width() - offset - 30, 10)
            self.btn_pin.raise_()
            offset += 32
        if hasattr(self, 'btn_account'):
            self.btn_account.move(self.width() - offset - 30, 10)
            self.btn_account.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_button_positions()

    def showEvent(self, event):
        super().showEvent(event)
        self._update_button_positions()

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
