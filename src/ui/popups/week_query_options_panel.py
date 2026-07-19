from PyQt6.QtCore import QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.config import AppConfig
from src.services.schedule_query_service import WeekScheduleQueryOptions
from src.ui.components import get_colored_icon
from src.ui.popups.day_query_options_panel import DayQueryOptionsPanel
from src.utils.window_preferences import (
    get_primary_pin_preference,
    set_window_pin_state,
)


class WeekdayPointSelector(QWidget):
    selection_changed = pyqtSignal(object)

    _LABELS = ("周一", "周二", "周三", "周四", "周五", "周六", "周日", "全部")
    _TOOLTIPS = (
        "周一",
        "周二",
        "周三",
        "周四",
        "周五",
        "周六",
        "周日",
        "全部",
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self._synchronizing = False
        self.setFixedHeight(42)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.buttons = []
        for index, (label, tooltip) in enumerate(zip(self._LABELS, self._TOOLTIPS)):
            item = QWidget()
            item.setFixedWidth(28)
            item_layout = QVBoxLayout(item)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(3)

            text_label = QLabel(label)
            text_label.setFixedHeight(17)
            text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_label.setStyleSheet(
                "color: white; background: transparent; border: none; "
                "font-family: 'Microsoft YaHei'; font-size: 10px;"
            )
            text_label.setToolTip(tooltip)

            button = QPushButton()
            button.setCheckable(True)
            button.setChecked(True)
            button.setFixedSize(10, 10)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setToolTip(tooltip)
            button.setStyleSheet(
                "QPushButton { background: transparent; "
                "border: 1px solid rgba(255,255,255,0.82); border-radius: 5px; "
                "padding: 0px; } "
                "QPushButton:hover { background: rgba(255,255,255,0.18); } "
                "QPushButton:checked { background: white; border: 1px solid white; }"
            )
            button.clicked.connect(
                lambda checked, selected_index=index: self._handle_click(
                    selected_index,
                    checked,
                )
            )
            self.buttons.append(button)
            item_layout.addWidget(text_label)
            item_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignHCenter)
            item_layout.addStretch()
            layout.addWidget(item)

        layout.addStretch()

    def selected_weekdays(self):
        return tuple(
            index
            for index, button in enumerate(self.buttons[:7])
            if button.isChecked()
        )

    def set_selected_weekdays(self, weekdays, emit=False):
        selected = {
            int(weekday)
            for weekday in weekdays
            if 0 <= int(weekday) <= 6
        }
        self._synchronizing = True
        try:
            for index, button in enumerate(self.buttons[:7]):
                button.setChecked(index in selected)
            self.buttons[7].setChecked(len(selected) == 7)
        finally:
            self._synchronizing = False
        if emit:
            self.selection_changed.emit(self.selected_weekdays())

    def _handle_click(self, index, checked):
        if self._synchronizing:
            return
        self._synchronizing = True
        try:
            if index == 7:
                for button in self.buttons[:7]:
                    button.setChecked(checked)
            else:
                self.buttons[7].setChecked(
                    all(button.isChecked() for button in self.buttons[:7])
                )
        finally:
            self._synchronizing = False
        self.selection_changed.emit(self.selected_weekdays())


class WeekQueryOptionsPanel(QWidget):
    applied = pyqtSignal(object)
    options_changed = pyqtSignal(object)

    def __init__(self, panel_mode, parent=None):
        super().__init__(parent, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        if panel_mode not in {"search", "filter"}:
            raise ValueError(f"unsupported panel mode: {panel_mode}")
        self.panel_mode = panel_mode
        self.is_pinned = bool(get_primary_pin_preference())
        self._drag_offset = None
        self._synchronizing_options = False
        self._categories = []
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(292, 486 if panel_mode == "search" else 410)
        self._setup_ui()
        self._update_pin_button()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(13, 11, 13, 13)
        outer.setSpacing(8)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        self.title_label = QLabel(
            "周搜索设置" if self.panel_mode == "search" else "周筛选"
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
        content.setObjectName("weekQueryOptionsContent")
        content.setStyleSheet(
            """
            QFrame#weekQueryOptionsContent {
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
            """
        )
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(11, 10, 11, 11)
        content_layout.setSpacing(8)

        option_grid = QGridLayout()
        option_grid.setContentsMargins(0, 0, 0, 0)
        option_grid.setHorizontalSpacing(8)
        option_grid.setVerticalSpacing(3)

        self.category_combo = QComboBox()
        DayQueryOptionsPanel._apply_combo_popup_style(self.category_combo)
        self.priority_combo = self._create_combo(
            (("不限", None), ("低重要性", 0), ("中重要性", 1), ("高重要性", 2))
        )
        self.status_combo = self._create_combo(
            (("不限", None), ("未完成", 0), ("已完成", 1))
        )
        self.time_kind_combo = self._create_combo(
            (("不限", "all"), ("时间段", "interval"), ("DDL / 单时间", "point"))
        )
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
        self._add_option_row(option_grid, row, "状态", self.status_combo)
        row += 1
        self._add_option_row(option_grid, row, "时间形式", self.time_kind_combo)
        row += 1
        self._add_option_row(option_grid, row, "提醒", self.reminder_combo)
        row += 1
        self._add_option_row(option_grid, row, "重复", self.repeat_combo)
        content_layout.addLayout(option_grid)

        range_label = QLabel("时间范围")
        range_label.setFixedHeight(16)
        content_layout.addWidget(range_label)
        self.weekday_selector = WeekdayPointSelector()
        self.weekday_selector.selection_changed.connect(self._emit_options_changed)
        content_layout.addWidget(self.weekday_selector)

        self.scope_combo = None
        self.match_combo = None
        if self.panel_mode == "search":
            search_grid = QGridLayout()
            search_grid.setContentsMargins(0, 0, 0, 0)
            search_grid.setHorizontalSpacing(8)
            search_grid.setVerticalSpacing(3)
            self.scope_combo = self._create_combo(
                (("标题", "title"), ("标题 + 详情", "title_description"))
            )
            self.match_combo = self._create_combo(
                (("模糊搜索", "fuzzy"), ("精准搜索", "exact"))
            )
            self._add_option_row(search_grid, 0, "搜索范围", self.scope_combo)
            self._add_option_row(search_grid, 1, "搜索设置", self.match_combo)
            content_layout.addLayout(search_grid)

        for combo in self._option_combos():
            combo.currentIndexChanged.connect(self._emit_options_changed)

        hint_text = (
            "搜索条件会即时作用于本周关键词；清空关键词后恢复原筛选结果。"
            if self.panel_mode == "search"
            else "筛选条件会即时作用于当前周；搜索清空后会回到这里。"
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
        self.btn_reset = DayQueryOptionsPanel._create_button("重置")
        self.btn_apply = DayQueryOptionsPanel._create_button("应用")
        self.btn_reset.clicked.connect(self.reset_options)
        self.btn_apply.clicked.connect(
            lambda: self.applied.emit(self.current_options())
        )
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
    def _add_option_row(grid, row, text, widget):
        label = QLabel(text)
        label.setFixedWidth(64)
        label.setFixedHeight(29)
        label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        grid.addWidget(label, row, 0)
        grid.addWidget(widget, row, 1)

    def set_options(self, options, categories):
        self._categories = list(categories)
        self._synchronizing_options = True
        try:
            self.category_combo.clear()
            self.category_combo.addItem(
                "不限",
                WeekScheduleQueryOptions.ALL_CATEGORIES,
            )
            self.category_combo.addItem(
                "未分类",
                WeekScheduleQueryOptions.UNCATEGORIZED,
            )
            for category in self._categories:
                self.category_combo.addItem(category.name, category.id)

            DayQueryOptionsPanel._set_combo_data(
                self.category_combo,
                options.category_id,
            )
            DayQueryOptionsPanel._set_combo_data(
                self.priority_combo,
                options.priority,
            )
            DayQueryOptionsPanel._set_combo_data(
                self.status_combo,
                options.status,
            )
            DayQueryOptionsPanel._set_combo_data(
                self.time_kind_combo,
                options.time_kind,
            )
            DayQueryOptionsPanel._set_combo_data(
                self.reminder_combo,
                getattr(options, "reminder_state", "all"),
            )
            DayQueryOptionsPanel._set_combo_data(
                self.repeat_combo,
                getattr(options, "repeat_kind", "all"),
            )
            self.weekday_selector.set_selected_weekdays(options.weekdays)
            if self.scope_combo is not None:
                DayQueryOptionsPanel._set_combo_data(
                    self.scope_combo,
                    options.search_scope,
                )
            if self.match_combo is not None:
                DayQueryOptionsPanel._set_combo_data(
                    self.match_combo,
                    options.match_mode,
                )
        finally:
            self._synchronizing_options = False

    def current_options(self):
        return WeekScheduleQueryOptions(
            category_id=self.category_combo.currentData(),
            priority=self.priority_combo.currentData(),
            status=self.status_combo.currentData(),
            time_kind=self.time_kind_combo.currentData() or "all",
            reminder_state=self.reminder_combo.currentData() or "all",
            repeat_kind=self.repeat_combo.currentData() or "all",
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
            weekdays=self.weekday_selector.selected_weekdays(),
        )

    def reset_options(self):
        self.set_options(
            WeekScheduleQueryOptions(),
            self._categories,
        )
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

    def _emit_options_changed(self, *_args):
        if not self._synchronizing_options:
            self.options_changed.emit(self.current_options())

    def _toggle_pin(self):
        self.set_pinned(not self.is_pinned)

    def set_pinned(self, enabled):
        self.is_pinned = bool(enabled)
        position = self.pos()
        set_window_pin_state(self, self.is_pinned)
        self.move(position)
        self._update_pin_button()

    def _update_pin_button(self):
        pin_color = "#FFFFFF" if self.is_pinned else "#A0A0A0"
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
            self._drag_offset = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
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
