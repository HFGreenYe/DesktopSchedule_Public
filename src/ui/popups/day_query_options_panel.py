from PyQt6.QtCore import QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPalette,
    QPen,
)
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListView,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QVBoxLayout,
    QWidget,
)

from src.config import AppConfig
from src.services.schedule_query_service import ScheduleQueryOptions
from src.ui.components import get_colored_icon
from src.utils.window_preferences import (
    get_primary_pin_preference,
    set_window_pin_state,
)


class ComboPopupItemDelegate(QStyledItemDelegate):
    def __init__(self, accent_color, parent=None):
        super().__init__(parent)
        self._accent_color = QColor(accent_color)

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        text_color = QColor("white") if selected else self._accent_color
        for color_group in (
            QPalette.ColorGroup.Active,
            QPalette.ColorGroup.Inactive,
            QPalette.ColorGroup.Disabled,
        ):
            option.palette.setColor(color_group, QPalette.ColorRole.Base, QColor("white"))
            option.palette.setColor(color_group, QPalette.ColorRole.Text, text_color)
            option.palette.setColor(color_group, QPalette.ColorRole.WindowText, text_color)
            option.palette.setColor(
                color_group,
                QPalette.ColorRole.Highlight,
                self._accent_color,
            )
            option.palette.setColor(
                color_group,
                QPalette.ColorRole.HighlightedText,
                QColor("white"),
            )

    def paint(self, painter, option, index):
        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        painter.save()
        painter.fillRect(
            option.rect,
            self._accent_color if selected else QColor("white"),
        )
        painter.setPen(QColor("white") if selected else self._accent_color)
        painter.setFont(option.font)
        painter.drawText(
            option.rect.adjusted(7, 0, -5, 0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            str(index.data(Qt.ItemDataRole.DisplayRole) or ""),
        )
        painter.restore()

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(max(26, size.height()))
        return size


class DayQueryOptionsPanel(QWidget):
    applied = pyqtSignal(object)
    options_changed = pyqtSignal(object)

    def __init__(self, panel_mode, parent=None, view_scope="day"):
        super().__init__(parent, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        if panel_mode not in {"search", "filter"}:
            raise ValueError(f"unsupported panel mode: {panel_mode}")
        self.panel_mode = panel_mode
        self.view_scope = (
            view_scope
            if view_scope in {"day", "month", "todo"}
            else "day"
        )
        self.is_pinned = bool(get_primary_pin_preference())
        self._drag_offset = None
        self._synchronizing_options = False
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        if self.view_scope == "todo":
            panel_height = 270 if panel_mode == "search" else 212
        elif self.view_scope == "day":
            panel_height = 410 if panel_mode == "search" else 334
        else:
            panel_height = 346 if panel_mode == "search" else 270
        self.setFixedSize(252, panel_height)
        self._setup_ui()
        self._update_pin_button()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(13, 11, 13, 13)
        outer.setSpacing(8)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        title_prefix = {
            "month": "月",
            "todo": "待办",
        }.get(self.view_scope, "")
        self.title_label = QLabel(
            f"{title_prefix}搜索设置"
            if self.panel_mode == "search"
            else f"{title_prefix}筛选"
        )
        self.title_label.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei'; "
            "font-size: 15px; font-weight: bold; background: transparent;"
        )
        header.addWidget(self.title_label, 1)

        self.btn_pin = QPushButton()
        self.btn_pin.setFixedSize(24, 24)
        self.btn_pin.setIconSize(QSize(14, 14))
        self.btn_pin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pin.setStyleSheet(
            "QPushButton { background: transparent; border: none; } "
            "QPushButton:hover { background: rgba(255,255,255,0.18); border-radius: 12px; }"
        )
        self.btn_pin.clicked.connect(self._toggle_pin)
        header.addWidget(self.btn_pin)

        self.btn_close = QPushButton("×")
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet(
            "QPushButton { background: transparent; border: none; color: white; "
            "font-size: 16px; font-weight: bold; } "
            "QPushButton:hover { background: rgba(255,255,255,0.18); border-radius: 12px; }"
        )
        self.btn_close.clicked.connect(self.close)
        header.addWidget(self.btn_close)
        outer.addLayout(header)

        content = QFrame()
        content.setObjectName("dayQueryOptionsContent")
        accent_color = AppConfig.COLOR_GRADIENT_START
        content.setStyleSheet(
            """
            QFrame#dayQueryOptionsContent {
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
            QComboBox {
                min-height: 25px;
                color: white;
                background-color: rgba(255, 255, 255, 0.16);
                border: 1px solid rgba(255, 255, 255, 0.72);
                border-radius: 4px;
                padding: 1px 6px;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
            }
            QComboBox:focus {
                border: 1px solid white;
                background-color: rgba(255, 255, 255, 0.22);
            }
            QComboBox::down-arrow {
                image: url(assets/icons/combo_down_white.svg);
                width: 11px;
                height: 7px;
            }
            """.replace("__ACCENT__", accent_color)
        )
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(11, 10, 11, 11)
        content_layout.setSpacing(8)

        options_container = QWidget()
        option_grid = QGridLayout(options_container)
        option_grid.setContentsMargins(0, 0, 0, 0)
        option_grid.setHorizontalSpacing(8)
        option_grid.setVerticalSpacing(3)

        self.category_combo = QComboBox()
        self._apply_combo_popup_style(self.category_combo)
        self.priority_combo = self._create_combo(
            (("不限", None), ("低重要性", 0), ("中重要性", 1), ("高重要性", 2))
        )
        self.status_combo = None
        self.time_kind_combo = None
        self.reminder_combo = None
        self.repeat_combo = None
        if self.view_scope != "todo":
            self.status_combo = self._create_combo(
                (("不限", None), ("未完成", 0), ("已完成", 1))
            )
            self.time_kind_combo = self._create_combo(
                (("不限", "all"), ("时间段", "interval"), ("DDL / 单时间", "point"))
            )
        if self.view_scope == "day":
            self.reminder_combo = self._create_combo(
                (("不限", "all"), ("提醒", "with"), ("无提醒", "without"))
            )
            self.repeat_combo = self._create_combo(
                (
                    ("不限", "all"),
                    ("重复", "repeated"),
                    ("日重复", "daily"),
                    ("周重复", "weekly"),
                    ("月重复", "monthly"),
                )
            )

        row = 0
        self._add_option_row(option_grid, row, "清单", self.category_combo)
        row += 1
        self._add_option_row(option_grid, row, "重要性", self.priority_combo)
        row += 1
        if self.status_combo is not None:
            self._add_option_row(option_grid, row, "状态", self.status_combo)
            row += 1
        if self.time_kind_combo is not None:
            self._add_option_row(option_grid, row, "时间形式", self.time_kind_combo)
            row += 1
        if self.reminder_combo is not None:
            self._add_option_row(option_grid, row, "提醒", self.reminder_combo)
            row += 1
        if self.repeat_combo is not None:
            self._add_option_row(option_grid, row, "重复", self.repeat_combo)
            row += 1

        self.scope_combo = None
        self.match_combo = None
        if self.panel_mode == "search":
            self.scope_combo = self._create_combo(
                (("标题", "title"), ("标题 + 详情", "title_description"))
            )
            self.match_combo = self._create_combo(
                (("模糊搜索", "fuzzy"), ("精准搜索", "exact"))
            )
            self._add_option_row(option_grid, row, "搜索范围", self.scope_combo)
            row += 1
            self._add_option_row(option_grid, row, "搜索设置", self.match_combo)

        for combo in self._option_combos():
            combo.currentIndexChanged.connect(self._emit_options_changed)

        option_count = len(self._option_combos())
        options_container.setFixedHeight(option_count * 29 + (option_count - 1) * 3)
        content_layout.addWidget(options_container)
        if self.panel_mode == "search":
            content_layout.addSpacing(4)

        if self.panel_mode == "search":
            hint_text = {
                "month": "搜索条件会即时作用于本月关键词；清空关键词后恢复原筛选结果。",
                "todo": "搜索条件会即时作用于待办关键词；清空关键词后恢复原筛选结果。",
            }.get(
                self.view_scope,
                "搜索条件会即时作用于当前关键词；清空关键词后恢复原筛选结果。",
            )
        else:
            hint_text = {
                "month": "筛选条件会即时作用于当前月；搜索清空后会回到这里。",
                "todo": "筛选条件会即时作用于待办列表；搜索清空后会回到这里。",
            }.get(
                self.view_scope,
                "筛选条件会即时作用于日界面，搜索清空后会回到这里。",
            )
        hint = QLabel(hint_text)
        hint.setWordWrap(True)
        hint.setStyleSheet(
            "color: rgba(255,255,255,0.72); font-size: 10px; "
            "font-family: 'Microsoft YaHei'; background: transparent; border: none;"
        )
        content_layout.addWidget(hint)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(8)
        self.btn_reset = self._create_button("重置")
        self.btn_apply = self._create_button("应用")
        self.btn_reset.clicked.connect(self.reset_options)
        self.btn_apply.clicked.connect(lambda: self.applied.emit(self.current_options()))
        button_row.addWidget(self.btn_reset)
        button_row.addWidget(self.btn_apply)
        content_layout.addLayout(button_row)

        outer.addWidget(content, 1)

    @staticmethod
    def _create_combo(items):
        combo = QComboBox()
        combo.setCursor(Qt.CursorShape.PointingHandCursor)
        for text, data in items:
            combo.addItem(text, data)
        DayQueryOptionsPanel._apply_combo_popup_style(combo)
        return combo

    @staticmethod
    def _apply_combo_popup_style(combo):
        accent_color = QColor(AppConfig.COLOR_GRADIENT_START)
        combo.setFixedHeight(29)
        view = QListView()
        combo.setView(view)
        view.setAlternatingRowColors(False)
        view.setUniformItemSizes(True)
        view.setItemDelegate(ComboPopupItemDelegate(accent_color, view))
        palette = view.palette()
        for color_group in (
            QPalette.ColorGroup.Active,
            QPalette.ColorGroup.Inactive,
            QPalette.ColorGroup.Disabled,
        ):
            palette.setColor(color_group, QPalette.ColorRole.Base, QColor("white"))
            palette.setColor(color_group, QPalette.ColorRole.Window, QColor("white"))
            palette.setColor(color_group, QPalette.ColorRole.Text, accent_color)
            palette.setColor(color_group, QPalette.ColorRole.WindowText, accent_color)
            palette.setColor(color_group, QPalette.ColorRole.Highlight, accent_color)
            palette.setColor(
                color_group,
                QPalette.ColorRole.HighlightedText,
                QColor("white"),
            )
        view.setPalette(palette)
        view.viewport().setPalette(palette)
        view.viewport().setAutoFillBackground(True)
        view.setStyleSheet(
            "color: __ACCENT__; background-color: white; "
            "border: 1px solid __ACCENT__; outline: none; "
            "selection-color: white; selection-background-color: __ACCENT__; "
            "font-family: 'Microsoft YaHei'; font-size: 12px;"
            .replace("__ACCENT__", accent_color.name())
        )

    @staticmethod
    def _add_option_row(grid, row, text, widget):
        label = QLabel(text)
        label.setFixedWidth(52)
        label.setFixedHeight(29)
        label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        grid.addWidget(label, row, 0)
        grid.addWidget(widget, row, 1)

    @staticmethod
    def _create_button(text):
        button = QPushButton(text)
        button.setFixedHeight(26)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(
            f"QPushButton {{ color: {AppConfig.COLOR_GRADIENT_START}; "
            "background: rgba(255,255,255,0.92); "
            "border: 1px solid white; border-radius: 5px; font-family: 'Microsoft YaHei'; "
            "font-size: 12px; } QPushButton:hover { background: white; }"
        )
        return button

    def set_options(self, options, categories):
        self._synchronizing_options = True
        try:
            self.category_combo.clear()
            self.category_combo.addItem("不限", ScheduleQueryOptions.ALL_CATEGORIES)
            self.category_combo.addItem("未分类", ScheduleQueryOptions.UNCATEGORIZED)
            for category in categories:
                self.category_combo.addItem(category.name, category.id)

            self._set_combo_data(self.category_combo, options.category_id)
            self._set_combo_data(self.priority_combo, options.priority)
            if self.status_combo is not None:
                self._set_combo_data(self.status_combo, options.status)
            if self.time_kind_combo is not None:
                self._set_combo_data(self.time_kind_combo, options.time_kind)
            if self.reminder_combo is not None:
                self._set_combo_data(
                    self.reminder_combo,
                    getattr(options, "reminder_state", "all"),
                )
            if self.repeat_combo is not None:
                self._set_combo_data(
                    self.repeat_combo,
                    getattr(options, "repeat_kind", "all"),
                )
            if self.scope_combo is not None:
                self._set_combo_data(self.scope_combo, options.search_scope)
            if self.match_combo is not None:
                self._set_combo_data(self.match_combo, options.match_mode)
        finally:
            self._synchronizing_options = False

    def current_options(self):
        return ScheduleQueryOptions(
            category_id=self.category_combo.currentData(),
            priority=self.priority_combo.currentData(),
            status=(
                self.status_combo.currentData()
                if self.status_combo is not None
                else None
            ),
            time_kind=(
                self.time_kind_combo.currentData() or "all"
                if self.time_kind_combo is not None
                else "all"
            ),
            reminder_state=(
                self.reminder_combo.currentData() or "all"
                if self.reminder_combo is not None
                else "all"
            ),
            repeat_kind=(
                self.repeat_combo.currentData() or "all"
                if self.repeat_combo is not None
                else "all"
            ),
            search_scope=(
                self.scope_combo.currentData()
                if self.scope_combo is not None
                else "title"
            ),
            match_mode=(
                self.match_combo.currentData()
                if self.match_combo is not None
                else "fuzzy"
            ),
        )

    def reset_options(self):
        self._synchronizing_options = True
        try:
            for combo in self._option_combos():
                combo.setCurrentIndex(0)
        finally:
            self._synchronizing_options = False
        self.options_changed.emit(self.current_options())

    def _option_combos(self):
        return tuple(
            combo
            for combo in (
                self.category_combo,
                self.priority_combo,
                self.status_combo,
                self.time_kind_combo,
                self.reminder_combo,
                self.repeat_combo,
                self.scope_combo,
                self.match_combo,
            )
            if combo is not None
        )

    def _emit_options_changed(self):
        if not self._synchronizing_options:
            self.options_changed.emit(self.current_options())

    @staticmethod
    def _set_combo_data(combo, value):
        for index in range(combo.count()):
            if combo.itemData(index) == value:
                combo.setCurrentIndex(index)
                return
        combo.setCurrentIndex(0)

    def _toggle_pin(self):
        self.set_pinned(not self.is_pinned)

    def set_pinned(self, enabled):
        self.is_pinned = bool(enabled)
        position = self.pos()
        set_window_pin_state(self, self.is_pinned)
        self.move(position)
        self._update_pin_button()

    def _update_pin_button(self):
        pin_color = "#FFFFFF" if self.is_pinned else "rgba(255,255,255,0.59)"
        pixmap = get_colored_icon("pin.svg", pin_color, 14)
        self.btn_pin.setIcon(
            QIcon(pixmap)
            if not pixmap.isNull()
            else QIcon("assets/icons/pin.svg")
        )
        self.btn_pin.setToolTip(
            "取消窗口置顶" if self.is_pinned else "窗口置顶"
        )

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
