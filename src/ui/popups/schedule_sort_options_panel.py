from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.config import AppConfig
from src.services.schedule_sort_service import ScheduleSortOptions
from src.ui.components import IOSSwitch
from src.ui.popups.day_query_options_panel import DayQueryOptionsPanel


class SortSegmentGroup(QWidget):
    value_changed = pyqtSignal(str)

    def __init__(self, items, parent=None):
        super().__init__(parent)
        self._buttons = {}
        self._synchronizing = False
        self.setFixedHeight(30)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        for text, value in items:
            button = QPushButton(text)
            button.setCheckable(True)
            button.setFixedHeight(28)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda checked=False, selected_value=value: self.set_value(
                    selected_value,
                    emit=True,
                )
            )
            layout.addWidget(button, 1)
            self._buttons[value] = button
        self.set_value(items[0][1])

    def clear_selection(self):
        self._synchronizing = True
        try:
            for button in self._buttons.values():
                button.setChecked(False)
                button.setStyleSheet(self._button_style(False))
        finally:
            self._synchronizing = False

    def set_value(self, value, emit=False):
        normalized = value if value in self._buttons else next(iter(self._buttons))
        self._synchronizing = True
        try:
            for button_value, button in self._buttons.items():
                button.setChecked(button_value == normalized)
                button.setStyleSheet(self._button_style(button.isChecked()))
        finally:
            self._synchronizing = False
        if emit:
            self.value_changed.emit(normalized)

    def value(self):
        for value, button in self._buttons.items():
            if button.isChecked():
                return value
        return next(iter(self._buttons))

    @staticmethod
    def _button_style(checked):
        if checked:
            return (
                f"QPushButton {{ color: {AppConfig.COLOR_GRADIENT_START}; "
                "background: rgba(255,255,255,0.94); "
                "border: 1px solid white; border-radius: 5px; "
                "font-family: 'Microsoft YaHei'; font-size: 11px; font-weight: bold; }"
            )
        return (
            "QPushButton { color: white; background: rgba(255,255,255,0.15); "
            "border: 1px solid rgba(255,255,255,0.62); border-radius: 5px; "
            "font-family: 'Microsoft YaHei'; font-size: 11px; } "
            "QPushButton:hover { background: rgba(255,255,255,0.22); }"
        )


class ScheduleSortOptionsPanel(QWidget):
    applied = pyqtSignal(object)
    options_changed = pyqtSignal(object)

    def __init__(self, view_scope, parent=None):
        super().__init__(parent, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.view_scope = view_scope if view_scope in {"day", "week", "month", "todo"} else "day"
        self._drag_offset = None
        self._synchronizing_options = False
        self._options_enabled = False
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(276, 330)
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(13, 11, 13, 13)
        outer.setSpacing(8)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        title_prefix = {
            "week": "周",
            "month": "月",
            "todo": "待办",
        }.get(self.view_scope, "")
        self.title_label = QLabel(f"{title_prefix}排序设置")
        self.title_label.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei'; "
            "font-size: 15px; font-weight: bold; background: transparent;"
        )
        header.addWidget(self.title_label, 1)

        self.btn_close = QPushButton("×")
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet(
            "QPushButton { background: transparent; border: none; color: white; "
            "font-size: 16px; font-weight: bold; } "
            "QPushButton:hover { background: rgba(255,255,255,0.18); border-radius: 12px; }"
        )
        self.btn_close.clicked.connect(self.exit_sort_mode)
        header.addWidget(self.btn_close)
        outer.addLayout(header)

        content = QFrame()
        content.setObjectName("scheduleSortOptionsContent")
        content.setStyleSheet(
            """
            QFrame#scheduleSortOptionsContent {
                background-color: rgba(255, 255, 255, 0.17);
                border: 1px solid rgba(255, 255, 255, 0.55);
                border-radius: 7px;
            }
            QLabel {
                color: rgba(255, 255, 255, 0.94);
                font-family: 'Microsoft YaHei';
                font-size: 12px;
                background: transparent;
                border: none;
            }
            """
        )
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(11, 10, 11, 11)
        content_layout.setSpacing(8)

        self.completed_switch = IOSSwitch()
        self.overdue_switch = IOSSwitch()
        self.completed_switch.toggled.connect(self._emit_options_changed)
        self.overdue_switch.toggled.connect(self._emit_options_changed)
        content_layout.addLayout(self._switch_row("包括已完成", self.completed_switch))
        content_layout.addLayout(self._switch_row("包括已过期", self.overdue_switch))

        content_layout.addWidget(self._section_label("排序范围"))
        self.scope_group = SortSegmentGroup(
            (("全部", "all"), ("仅DDL", "point"), ("时间段", "interval"))
        )
        self.scope_group.value_changed.connect(self._emit_options_changed)
        content_layout.addWidget(self.scope_group)

        content_layout.addWidget(self._section_label("排序方案"))
        self.scheme_group = SortSegmentGroup((("按时间", "time"), ("按重要性", "priority")))
        self.scheme_group.value_changed.connect(self._emit_options_changed)
        content_layout.addWidget(self.scheme_group)

        hint = QLabel("排序设置只作用于当前界面显示，不改写日程数据。")
        hint.setWordWrap(True)
        hint.setStyleSheet(
            "color: rgba(255,255,255,0.72); font-size: 10px; "
            "font-family: 'Microsoft YaHei'; background: transparent; border: none;"
        )
        content_layout.addWidget(hint)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(8)
        self.btn_reset = DayQueryOptionsPanel._create_button("重置")
        self.btn_apply = DayQueryOptionsPanel._create_button("退出")
        self.btn_reset.clicked.connect(self.reset_options)
        self.btn_apply.clicked.connect(self.exit_sort_mode)
        button_row.addWidget(self.btn_reset)
        button_row.addWidget(self.btn_apply)
        content_layout.addLayout(button_row)

        outer.addWidget(content, 1)

    @staticmethod
    def _section_label(text):
        label = QLabel(text)
        label.setFixedHeight(15)
        return label

    @staticmethod
    def _switch_row(text, switch):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        label = QLabel(text)
        label.setFixedHeight(28)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(label, 1)
        row.addWidget(switch, 0, Qt.AlignmentFlag.AlignRight)
        return row

    def set_options(self, options):
        self._synchronizing_options = True
        try:
            self._options_enabled = bool(getattr(options, "enabled", False))
            self.completed_switch.setChecked(bool(options.include_completed))
            self.overdue_switch.setChecked(bool(options.include_overdue))
            self.scope_group.set_value(options.item_scope)
            if (
                self.view_scope in {"day", "week"}
                and not self._options_enabled
            ):
                self.scheme_group.clear_selection()
            else:
                self.scheme_group.set_value(options.scheme)
        finally:
            self._synchronizing_options = False

    def current_options(self):
        return ScheduleSortOptions(
            include_completed=self.completed_switch.isChecked(),
            include_overdue=self.overdue_switch.isChecked(),
            item_scope=self.scope_group.value(),
            scheme=self.scheme_group.value(),
            enabled=self._options_enabled,
        )

    def reset_options(self):
        self.set_options(ScheduleSortOptions())
        self.options_changed.emit(self.current_options())

    def exit_sort_mode(self):
        self.set_options(ScheduleSortOptions())
        self.applied.emit(self.current_options())

    def _emit_options_changed(self, *_args):
        if not self._synchronizing_options:
            self._options_enabled = True
            self.options_changed.emit(self.current_options())

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
        painter.setPen(QPen(QColor(0, 0, 0, 30), 1))
        painter.drawPath(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())
            if self._is_interactive_child(child):
                super().mousePressEvent(event)
                return
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

    def _is_interactive_child(self, child):
        while child is not None and child is not self:
            if isinstance(child, (QPushButton, IOSSwitch, SortSegmentGroup)):
                return True
            child = child.parentWidget()
        return False
