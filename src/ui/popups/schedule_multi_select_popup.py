from PyQt6.QtCore import QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...config import AppConfig
from ...utils.styles import StyleManager
from ...utils.window_preferences import (
    get_primary_pin_preference,
    set_window_pin_state,
)
from ..components import get_colored_icon
from ..header import ToolTipFilter


class ScheduleMultiSelectPopup(QWidget):
    action_requested = pyqtSignal(str)
    day_scope_toggled = pyqtSignal(int)
    closed = pyqtSignal(object)

    HEADER_HEIGHT = 42
    CORNER_RADIUS = 10
    ACTION_BUTTON_SIZE = 36
    ACTION_ICON_SIZE = 18
    WEEK_DAY_BUTTON_SIZE = 34
    ACTIONS = (
        ("select_all", "Multiplechoice.svg", "全选 / 全不选"),
        ("complete", "finished.svg", "完成"),
        ("undo", "withdraw.svg", "撤销"),
        ("delete", "delete.svg", "删除"),
        ("exit", "exit.svg", "退出"),
    )
    WEEK_DAY_LABELS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "All")

    def __init__(self, mode, parent=None, initial_pinned=None):
        if mode not in {"day", "week"}:
            raise ValueError(f"Unsupported multi-select popup mode: {mode}")
        if initial_pinned is None:
            initial_pinned = get_primary_pin_preference()

        window_flags = Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
        if initial_pinned:
            window_flags |= Qt.WindowType.WindowStaysOnTopHint
        super().__init__(parent, window_flags)

        self.mode = mode
        self.is_pinned = bool(initial_pinned)
        self._closed_emitted = False
        self._drag_offset = None
        self.day_buttons = []
        self.action_buttons = {}

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setFixedSize(294 if mode == "day" else 354, 106 if mode == "day" else 150)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget(self)
        header.setFixedHeight(self.HEADER_HEIGHT)
        header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(14, 0, 0, 0)
        header_layout.setSpacing(0)

        title = QLabel("日程多选" if mode == "day" else "周日程多选")
        title.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei'; "
            "font-size: 14px; font-weight: bold; background: transparent;"
        )
        header_layout.addWidget(title, 1)

        header_button_style = """
            QPushButton {
                background: transparent;
                border: none;
                padding: 0;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.18);
            }
        """

        self.btn_pin = QPushButton()
        self.btn_pin.setFixedSize(30, 30)
        self.btn_pin.setIconSize(QSize(14, 14))
        self.btn_pin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pin.setStyleSheet(header_button_style)
        self.btn_pin.clicked.connect(self._toggle_pin)
        header_layout.addWidget(
            self.btn_pin,
            0,
            Qt.AlignmentFlag.AlignTop,
        )

        self.btn_close = QPushButton()
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setIconSize(QSize(12, 12))
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet(header_button_style)
        self.btn_close.setIcon(
            QIcon(self._tinted_raster_icon("assets/icons/close.png", "#FFFFFF", 12))
        )
        self.btn_close.clicked.connect(self.close)
        header_layout.addWidget(
            self.btn_close,
            0,
            Qt.AlignmentFlag.AlignTop,
        )
        layout.addWidget(header)

        body = QWidget(self)
        body.setStyleSheet("background: transparent;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(14, 10, 14, 10)
        body_layout.setSpacing(10)

        if mode == "week":
            body_layout.addLayout(self._create_week_scope_row())
        body_layout.addLayout(self._create_action_row())
        layout.addWidget(body, 1)

        self._update_pin_button()
        if mode == "week":
            self.set_scope_state(set(range(7)))
        self.set_action_state(
            has_scope_cards=False,
            all_scope_selected=False,
            can_complete=False,
            can_undo=False,
            can_delete=False,
        )

    def _create_week_scope_row(self):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        for day_index, text in enumerate(self.WEEK_DAY_LABELS):
            button = QPushButton(text)
            button.setFixedSize(
                self.WEEK_DAY_BUTTON_SIZE,
                self.WEEK_DAY_BUTTON_SIZE,
            )
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda _checked=False, value=day_index: (
                    self.day_scope_toggled.emit(value)
                )
            )
            self.day_buttons.append(button)
            row.addWidget(button)
            if day_index < len(self.WEEK_DAY_LABELS) - 1:
                row.addStretch(1)
        return row

    def _create_action_row(self):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        for action_index, (action_id, icon_name, tooltip) in enumerate(self.ACTIONS):
            button = QPushButton()
            button.setFixedSize(
                self.ACTION_BUTTON_SIZE,
                self.ACTION_BUTTON_SIZE,
            )
            button.setIconSize(
                QSize(self.ACTION_ICON_SIZE, self.ACTION_ICON_SIZE)
            )
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda _checked=False, value=action_id: (
                    self.action_requested.emit(value)
                )
            )
            button._tooltip_filter = ToolTipFilter(tooltip, button)
            button.installEventFilter(button._tooltip_filter)
            self.action_buttons[action_id] = button
            row.addWidget(button)
            if action_index < len(self.ACTIONS) - 1:
                row.addStretch(1)
            self._set_action_button(button, icon_name, enabled=True)
        return row

    @staticmethod
    def _midpoint_color():
        return StyleManager.mix_colors(
            AppConfig.COLOR_GRADIENT_START,
            AppConfig.COLOR_GRADIENT_END,
            0.5,
        )

    @staticmethod
    def _tinted_raster_icon(path, color, size):
        source = QPixmap(path)
        if source.isNull():
            return QPixmap()
        pixmap = source.scaled(
            size,
            size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter = QPainter(pixmap)
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_SourceIn
        )
        painter.fillRect(pixmap.rect(), QColor(color))
        painter.end()
        return pixmap

    def _set_action_button(self, button, icon_name, *, enabled):
        icon_color = "#FFFFFF" if enabled else "#8A8A8A"
        pixmap = get_colored_icon(icon_name, icon_color, self.ACTION_ICON_SIZE)
        button.setIcon(
            QIcon(pixmap)
            if not pixmap.isNull()
            else QIcon(f"assets/icons/{icon_name}")
        )
        button.setEnabled(enabled)
        button.setStyleSheet(
            "QPushButton {"
            f"background: {self._midpoint_color()};"
            "border: none; border-radius: 5px; padding: 0;"
            "}"
            "QPushButton:hover { background: rgba(255, 255, 255, 0.24); }"
            "QPushButton:pressed { background: rgba(0, 0, 0, 0.12); }"
            "QPushButton:disabled {"
            f"background: {self._midpoint_color()};"
            "}"
        )
        button._current_icon_name = icon_name

    def set_scope_state(self, selected_days):
        if self.mode != "week":
            return
        selected_days = set(selected_days)
        all_days_selected = len(selected_days) == 7
        for day_index, button in enumerate(self.day_buttons):
            selected = (
                all_days_selected
                if day_index == 7
                else day_index in selected_days
            )
            border = (
                f"2px solid {AppConfig.COLOR_GRADIENT_START}"
                if selected
                else "none"
            )
            button.setStyleSheet(
                "QPushButton {"
                "background: transparent; color: #7A7A7A;"
                f"border: {border}; border-radius: 17px;"
                "font-family: 'Segoe UI'; font-size: 9px; font-weight: 600;"
                "padding: 0;"
                "}"
                "QPushButton:hover { background: rgba(255, 255, 255, 0.22); }"
            )

    def set_action_state(
        self,
        *,
        has_scope_cards,
        all_scope_selected,
        can_complete,
        can_undo,
        can_delete,
    ):
        self._set_action_button(
            self.action_buttons["select_all"],
            "all_no.svg" if all_scope_selected else "Multiplechoice.svg",
            enabled=has_scope_cards,
        )
        self._set_action_button(
            self.action_buttons["complete"],
            "finished.svg",
            enabled=can_complete,
        )
        self._set_action_button(
            self.action_buttons["undo"],
            "withdraw.svg",
            enabled=can_undo,
        )
        self._set_action_button(
            self.action_buttons["delete"],
            "delete.svg",
            enabled=can_delete,
        )
        self._set_action_button(
            self.action_buttons["exit"],
            "exit.svg",
            enabled=True,
        )

    def _toggle_pin(self):
        self.set_pinned(not self.is_pinned)

    def set_pinned(self, enabled):
        self.is_pinned = bool(enabled)
        position = self.pos()
        set_window_pin_state(self, self.is_pinned)
        self.move(position)
        self._update_pin_button()

    def _update_pin_button(self):
        pin_color = "#FFFFFF" if self.is_pinned else "#96FFFFFF"
        pixmap = get_colored_icon("pin.svg", pin_color, 14)
        self.btn_pin.setIcon(
            QIcon(pixmap)
            if not pixmap.isNull()
            else QIcon("assets/icons/pin.svg")
        )
        self.btn_pin.setToolTip(
            "取消窗口置顶" if self.is_pinned else "窗口置顶"
        )

    def show_near(self, anchor_window):
        self.adjustSize()
        anchor_geometry = anchor_window.frameGeometry()
        screen = (
            QApplication.screenAt(anchor_geometry.center())
            or QApplication.primaryScreen()
        )
        x = anchor_geometry.right() + 8
        y = anchor_geometry.top() + 36
        if screen is not None:
            available = screen.availableGeometry()
            if x + self.width() > available.right() + 1:
                x = anchor_geometry.left() - self.width() - 8
            x = max(
                available.left(),
                min(x, available.right() - self.width() + 1),
            )
            y = max(
                available.top(),
                min(y, available.bottom() - self.height() + 1),
            )
        self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))

        outer_path = QPainterPath()
        outer_path.addRoundedRect(
            rect,
            self.CORNER_RADIUS,
            self.CORNER_RADIUS,
        )
        painter.setPen(QPen(QColor(255, 255, 255, 110), 1))
        painter.setBrush(QBrush(gradient))
        painter.drawPath(outer_path)

        painter.save()
        painter.setClipPath(outer_path)
        painter.fillRect(
            0,
            self.HEADER_HEIGHT,
            self.width(),
            self.height() - self.HEADER_HEIGHT,
            QColor(255, 255, 255, 179),
        )
        painter.restore()
        super().paintEvent(event)

    def closeEvent(self, event):
        if not self._closed_emitted:
            self._closed_emitted = True
            self.closed.emit(self)
        super().closeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self._drag_offset is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = None
            event.accept()
            return
        super().mouseReleaseEvent(event)
