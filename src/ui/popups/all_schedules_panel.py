import os
from bisect import bisect_right
from datetime import datetime

from PyQt6.QtCore import (
    QEvent,
    QPointF,
    QPropertyAnimation,
    QRect,
    QRectF,
    QSize,
    Qt,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QFont,
    QFontMetrics,
    QGuiApplication,
    QIcon,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.config import AppConfig
from src.services.schedule_query_service import ScheduleQueryOptions, ScheduleQueryService
from src.services.schedule_sort_service import ScheduleSortOptions, ScheduleSortService
from src.ui.popups.day_query_options_panel import DayQueryOptionsPanel
from src.utils.window_preferences import set_window_pin_state


class _DotOptionButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(22)
        font = self.font()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(7)
        self.setFont(font)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("background: transparent; border: none;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        font = painter.font()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(7)
        font.setBold(self.isChecked())
        painter.setFont(font)

        text_color = QColor(255, 255, 255, 255 if self.isChecked() else 220)
        painter.setPen(text_color)
        radius = 3.0
        dot_gap = 3.0
        edge_padding = 1.0
        text_left = edge_padding
        dot_size = radius * 2.0
        available_text_width = max(
            0,
            int(self.width() - edge_padding * 2.0 - dot_size - dot_gap),
        )
        display_text = painter.fontMetrics().elidedText(
            self.text(),
            Qt.TextElideMode.ElideRight,
            available_text_width,
        )
        text_width = min(
            painter.fontMetrics().horizontalAdvance(display_text),
            available_text_width,
        )
        text_rect = QRectF(text_left, 0, available_text_width, self.height())
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            display_text,
        )

        dot_x = min(
            text_left + text_width + dot_gap,
            self.width() - dot_size - edge_padding,
        )
        dot_rect = QRectF(
            dot_x,
            self.height() / 2.0 - radius,
            dot_size,
            dot_size,
        )
        painter.setPen(QPen(QColor(255, 255, 255, 230), 1))
        selected_color = QColor(255, 255, 255, 191)
        painter.setBrush(QBrush(selected_color) if self.isChecked() else Qt.BrushStyle.NoBrush)
        painter.drawEllipse(dot_rect)
        painter.end()


class _AllScheduleResultCard(QFrame):
    detail_requested = pyqtSignal(object)
    context_requested = pyqtSignal(object, object)

    def __init__(self, schedule, category_name, parent=None):
        super().__init__(parent)
        self.schedule = schedule
        self.setObjectName("allScheduleResultCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(
            """
            QFrame#allScheduleResultCard {
                background: transparent;
                border: none;
            }
            QLabel {
                background: transparent;
                border: none;
                font-family: "Microsoft YaHei UI";
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 3, 2, 8)
        layout.setSpacing(4)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(0)

        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(
            f"background-color: {self._priority_color(schedule)}; "
            "border-radius: 4px; border: none;"
        )
        dot.setVisible(False)
        top_row.addWidget(dot, alignment=Qt.AlignmentFlag.AlignVCenter)

        title_label = QLabel(str(getattr(schedule, "title", "") or "未命名日程"))
        title_label.setStyleSheet(
            f"color: {AppConfig.COLOR_GRADIENT_START}; "
            "font-size: 12px; font-weight: bold;"
        )
        title_label.setWordWrap(True)
        title_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        title_label.setCursor(Qt.CursorShape.PointingHandCursor)
        title_label.installEventFilter(self)
        self.title_label = title_label
        top_row.addWidget(title_label, 1)

        type_label = QLabel(self._type_text(schedule))
        type_label.setStyleSheet("color: rgba(45, 45, 45, 0.76); font-size: 10px;")
        type_label.setVisible(False)
        top_row.addWidget(type_label, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(top_row)

        description = str(getattr(schedule, "description", "") or "").strip()
        if description:
            description_label = QLabel(description)
            description_label.setWordWrap(True)
            description_label.setSizePolicy(
                QSizePolicy.Policy.Ignored,
                QSizePolicy.Policy.Preferred,
            )
            description_label.setStyleSheet(
                "color: rgba(35, 35, 35, 0.86); font-size: 10px;"
            )
            description_label.installEventFilter(self)
            layout.addWidget(description_label)

        time_label = QLabel(self._time_text(schedule))
        time_label.setWordWrap(True)
        time_label.setStyleSheet("color: rgba(45, 45, 45, 0.78); font-size: 10px;")
        time_label.installEventFilter(self)
        layout.addWidget(time_label)

        meta_label = QLabel(
            f"{category_name} · {self._priority_text(schedule)} · "
            f"{self._status_text(schedule)} · {self._repeat_text(schedule)}"
        )
        meta_label.setWordWrap(True)
        meta_label.setStyleSheet("color: rgba(45, 45, 45, 0.72); font-size: 10px;")
        meta_label.installEventFilter(self)
        layout.addWidget(meta_label)

    def eventFilter(self, obj, event):
        if (
            obj is getattr(self, "title_label", None)
            and event.type() == QEvent.Type.MouseButtonDblClick
        ):
            self.detail_requested.emit(self.schedule)
            return True
        if event.type() == QEvent.Type.ContextMenu and hasattr(event, "globalPos"):
            self.context_requested.emit(self.schedule, event.globalPos())
            return True
        return super().eventFilter(obj, event)

    def contextMenuEvent(self, event):
        self.context_requested.emit(self.schedule, event.globalPos())
        event.accept()

    @staticmethod
    def _priority_color(schedule):
        return {2: "#ff4d4f", 1: "#faad14", 0: "#52c41a"}.get(
            int(getattr(schedule, "priority", 0) or 0),
            "#52c41a",
        )

    @staticmethod
    def _priority_text(schedule):
        return {2: "高重要性", 1: "中重要性", 0: "低重要性"}.get(
            int(getattr(schedule, "priority", 0) or 0),
            "低重要性",
        )

    @staticmethod
    def _status_text(schedule):
        status = int(getattr(schedule, "status", 0) or 0)
        if status == 1:
            return "已完成"
        if status == 2:
            return "已隐藏"
        if _AllScheduleResultCard._is_overdue(schedule):
            return "已过期"
        return "未完成"

    @staticmethod
    def _repeat_text(schedule):
        rule = str(getattr(schedule, "repeat_rule", "") or "").strip()
        if not rule or rule in {"none", "无", "不重复"}:
            return "不重复"
        return rule

    @staticmethod
    def _type_text(schedule):
        if ScheduleQueryService.is_todo(schedule):
            return "待办"
        if _AllScheduleResultCard._is_interval(schedule):
            return "时间段"
        return "DDL"

    @staticmethod
    def _is_interval(schedule):
        start_time = getattr(schedule, "start_time", None)
        end_time = getattr(schedule, "end_time", None)
        return bool(start_time and end_time and start_time != end_time)

    @staticmethod
    def _effective_time(schedule):
        if _AllScheduleResultCard._is_interval(schedule):
            return getattr(schedule, "end_time", None)
        return (
            getattr(schedule, "end_time", None)
            or getattr(schedule, "start_time", None)
            or getattr(schedule, "created_at", None)
        )

    @staticmethod
    def _is_overdue(schedule):
        if int(getattr(schedule, "status", 0) or 0) == 1:
            return False
        effective_time = _AllScheduleResultCard._effective_time(schedule)
        return isinstance(effective_time, datetime) and effective_time < datetime.now()

    @staticmethod
    def _format_dt(value):
        return value.strftime("%Y-%m-%d %H:%M") if isinstance(value, datetime) else ""

    @classmethod
    def _time_text(cls, schedule):
        start_time = getattr(schedule, "start_time", None)
        end_time = getattr(schedule, "end_time", None)
        if start_time and end_time and start_time != end_time:
            return f"{cls._format_dt(start_time)} → {cls._format_dt(end_time)}"
        if end_time:
            return f"截止：{cls._format_dt(end_time)}"
        if start_time:
            return cls._format_dt(start_time)
        created_at = getattr(schedule, "created_at", None)
        return f"创建：{cls._format_dt(created_at)}" if created_at else "未设置时间"


class AllSchedulesPanel(QWidget):
    schedule_detail_requested = pyqtSignal(object)

    RESIZE_MARGIN = 14
    OPTION_TITLE_WIDTH = 52
    OPTION_ROW_SPACING = 2
    OPTION_GRID_COLUMNS = 5
    VIRTUAL_BUFFER_ITEMS = 4
    VIRTUAL_ROW_SPACING = 6

    def __init__(self, parent_window=None):
        super().__init__(
            parent_window,
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint,
        )
        self.parent_window = parent_window
        self._drag_offset = None
        self._resize_edge = None
        self._resize_start_pos = None
        self._resize_start_geometry = None
        self.is_pinned = False
        self._settings_visible = False
        self._search_options_visible = False
        self._settings_icon_angle = 0.0
        self._settings_icon_source = QPixmap()
        self._category_map = {}
        self._detail_signal_bound = False
        self._result_items = []
        self._result_records = []
        self._result_heights = []
        self._result_offsets = []
        self._virtual_total_height = 0
        self._virtual_render_range = (-1, -1)
        self._virtual_width = 0
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self._setup_ui()
        self.reset_geometry_for_parent()

    def reset_geometry_for_parent(self):
        parent = self.parent_window
        if parent is None:
            self.setFixedWidth(260)
            self.setMinimumHeight(384)
            self.resize(260, 384)
            return

        parent_rect = parent.frameGeometry()
        width = max(260, int(parent_rect.width() * 0.75))
        height = max(260, int(parent_rect.height() * 2 / 3))
        self.setFixedWidth(width)
        self.setMinimumHeight(height)
        self.resize(width, height)
        gap = 8
        preferred_x = parent_rect.x() + parent_rect.width() + gap
        fallback_x = parent_rect.x() - width - gap
        x = preferred_x
        y = parent_rect.y()

        screen = QGuiApplication.screenAt(parent_rect.center()) or QGuiApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            if preferred_x + width <= available.right() + 1:
                x = preferred_x
            elif fallback_x >= available.left():
                x = fallback_x
            else:
                x = max(
                    available.left(),
                    min(preferred_x, available.right() - width + 1),
                )
            y = max(
                available.top(),
                min(y, available.bottom() - height + 1),
            )

        self.move(x, y)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QVBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(2)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(3)

        self.title_label = QLabel("日程查看")
        self.title_label.setMinimumWidth(76)
        self.title_label.setFixedHeight(26)
        self.title_label.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei'; "
            "font-size: 16px; font-weight: bold; background: transparent; border: none;"
        )

        self.search_box = QLineEdit()
        self.search_box.setObjectName("allSchedulesSearchBox")
        self.search_box.setPlaceholderText("搜索日程...")
        self.search_box.setFixedHeight(24)
        self.search_box.setMinimumWidth(96)
        self.search_box.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.search_action = self.search_box.addAction(
            self._load_padded_svg_icon(
                "search.svg",
                "#FFFFFF",
                icon_size=12,
                canvas_size=16,
            ),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        self.search_box.setStyleSheet(
            """
            QLineEdit#allSchedulesSearchBox {
                background-color: rgba(255, 255, 255, 0.20);
                border: 2px solid #FFFFFF;
                border-radius: 6px;
                color: white;
                padding-left: 0px;
                padding-right: 4px;
                font-family: "Microsoft YaHei UI";
                font-size: 11px;
            }
            QLineEdit#allSchedulesSearchBox:hover,
            QLineEdit#allSchedulesSearchBox:focus {
                background-color: rgba(255, 255, 255, 0.24);
                border: 2px solid #FFFFFF;
            }
            QLineEdit#allSchedulesSearchBox::placeholder {
                color: rgba(255, 255, 255, 0.75);
            }
            """
        )

        button_style = (
            "QPushButton { background: transparent; border: none; border-radius: 4px; } "
            "QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }"
        )
        self.btn_settings = QPushButton()
        self.btn_settings.setFixedSize(30, 24)
        self.btn_settings.setIconSize(QSize(24, 24))
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.setToolTip("显示设置")
        self.btn_settings.setStyleSheet(button_style)
        self.btn_settings.clicked.connect(self._toggle_settings_area)
        self._settings_rotation_animation = QPropertyAnimation(
            self,
            b"settingsIconAngle",
            self,
        )
        self._settings_rotation_animation.setDuration(180)

        self.btn_pin = QPushButton(self)
        self.btn_pin.setFixedSize(30, 30)
        self.btn_pin.setIconSize(QSize(16, 16))
        self.btn_pin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pin.setToolTip("窗口置顶")
        self.btn_pin.setStyleSheet(button_style)
        self.btn_pin.clicked.connect(self._toggle_pin)

        self.btn_close = QPushButton(self)
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setIconSize(QSize(12, 12))
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setToolTip("关闭")
        self.btn_close.setStyleSheet(
            "QPushButton { background: transparent; border: none; "
            "border-top-right-radius: 12px; } "
            "QPushButton:hover { background: #ff4d4f; }"
        )
        self.btn_close.clicked.connect(self.close)

        title_row.addWidget(self.title_label)
        title_row.addStretch(1)
        header.addLayout(title_row)

        search_row = QHBoxLayout()
        search_row.setContentsMargins(0, 0, 0, 0)
        search_row.setSpacing(6)
        search_row.addWidget(self.search_box)
        search_row.addWidget(self.btn_settings)
        header.addLayout(search_row)
        layout.addLayout(header)

        self.display_frame = QFrame()
        self.display_frame.setObjectName("allSchedulesDisplayFrame")
        self.display_frame.setStyleSheet(
            """
            QFrame#allSchedulesDisplayFrame {
                background-color: rgba(255, 255, 255, 0.75);
                border: 2px solid white;
                border-radius: 8px;
            }
            """
        )
        display_layout = QVBoxLayout(self.display_frame)
        display_layout.setContentsMargins(8, 8, 8, 8)
        display_layout.setSpacing(6)

        self.settings_area = QFrame()
        self.settings_area.setObjectName("allSchedulesSettingsArea")
        self.settings_area.setStyleSheet(
            "QFrame#allSchedulesSettingsArea { background: transparent; border: none; }"
        )
        settings_layout = QGridLayout(self.settings_area)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        self._prepare_option_grid(settings_layout)
        self.completion_buttons = self._add_compact_option_row(
            settings_layout,
            "完成情况",
            ["已完成", "已过期", "未完成", "全部"],
            checked_index=3,
            values=["completed", "overdue", "active", "all"],
        )
        self.type_buttons = self._add_option_row(
            settings_layout,
            "日程类型",
            ["日程", "DDL", "时间段", "待办", "全部"],
            checked_index=4,
            values=["schedule", "point", "interval", "todo", "all"],
        )
        self.priority_buttons = self._add_compact_option_row(
            settings_layout,
            "重要性",
            ["低", "中", "高", "全部"],
            checked_index=3,
            values=[0, 1, 2, None],
        )
        self.reminder_buttons = self._add_compact_option_row(
            settings_layout,
            "提醒",
            ["提醒", "无提醒", "全部"],
            checked_index=2,
            values=["with", "without", "all"],
        )
        self.repeat_buttons = self._add_compact_option_row(
            settings_layout,
            "重复",
            ["重复", "不重复", "全部"],
            checked_index=2,
            values=["repeated", "none", "all"],
        )
        self.category_combo = self._create_category_combo()
        self._add_combo_row(settings_layout, "清单", self.category_combo)
        self.sort_buttons = self._add_compact_option_row(
            settings_layout,
            "排序方式",
            ["重要性", "时间", "创建时间"],
            checked_index=1,
            values=["priority", "time", "created"],
        )
        self.settings_area.hide()

        self.search_options_area = QFrame()
        self.search_options_area.setObjectName("allSchedulesSearchOptionsArea")
        self.search_options_area.setStyleSheet(
            "QFrame#allSchedulesSearchOptionsArea { background: transparent; border: none; }"
        )
        search_options_layout = QGridLayout(self.search_options_area)
        search_options_layout.setContentsMargins(0, 0, 0, 0)
        self._prepare_option_grid(search_options_layout)
        self.search_scope_buttons = self._add_option_row(
            search_options_layout,
            "搜索范围",
            ["标题", "标题+详情"],
            checked_index=0,
            values=["title", "title_description"],
        )
        self.search_match_buttons = self._add_option_row(
            search_options_layout,
            "搜索设置",
            ["模糊搜索", "精准搜索"],
            checked_index=0,
            values=["fuzzy", "exact"],
        )
        self.search_options_area.hide()

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("allSchedulesScrollArea")
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet(
            """
            QScrollArea#allSchedulesScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea#allSchedulesScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 0px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: transparent;
                border: none;
                border-radius: 0px;
                min-height: 24px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }
            """
        )
        self.results_container = QWidget()
        self.results_container.setStyleSheet("background: transparent;")
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(0)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.empty_label = QLabel("暂无日程数据")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(
            "color: rgba(0, 102, 204, 0.72); font-size: 12px; "
            "font-family: 'Microsoft YaHei UI'; background: transparent; border: none;"
        )
        self.scroll_area.setWidget(self.results_container)
        self.scroll_area.verticalScrollBar().valueChanged.connect(
            self._render_virtual_results
        )

        display_layout.addWidget(self.scroll_area, 1)
        layout.addWidget(self.search_options_area, 0)
        layout.addWidget(self.settings_area, 0)
        layout.addWidget(self.display_frame, 1)
        self.search_box.installEventFilter(self)
        self.search_box.textChanged.connect(self.refresh_results)
        self.category_combo.currentIndexChanged.connect(self.refresh_results)
        self._install_resize_event_filters()
        self._update_header_icons()
        self._update_header_button_positions()
        self.refresh_results()

    def _prepare_option_grid(self, grid):
        grid.setHorizontalSpacing(self.OPTION_ROW_SPACING)
        grid.setVerticalSpacing(3)
        grid.setColumnMinimumWidth(0, self.OPTION_TITLE_WIDTH)
        grid.setColumnStretch(0, 0)
        for column in range(1, self.OPTION_GRID_COLUMNS + 1):
            grid.setColumnStretch(column, 1)

    def _next_grid_row(self, grid):
        if grid.count() == 0:
            return 0
        return grid.rowCount()

    def _option_grid_positions(self, option_count):
        if option_count >= 5:
            return [(index + 1, 1) for index in range(option_count)]
        if option_count == 4:
            return [(1, 1), (2, 1), (3, 1), (5, 1)]
        if option_count == 3:
            return [(1, 1), (3, 1), (5, 1)]
        if option_count == 2:
            return [(2, 2), (4, 2)]
        return [(1, self.OPTION_GRID_COLUMNS)]

    def _add_option_row(self, parent_layout, title, options, checked_index=0, values=None):
        row = self._next_grid_row(parent_layout)
        title_label = QLabel(title)
        title_label.setFixedWidth(self.OPTION_TITLE_WIDTH)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_label.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei UI'; font-size: 10px; "
            "background: transparent; border: none;"
        )
        parent_layout.addWidget(title_label, row, 0)

        buttons = []
        positions = self._option_grid_positions(len(options))
        for index, text in enumerate(options):
            button = _DotOptionButton(text)
            button.setToolTip(text)
            option_values = values if values is not None else options
            button.setProperty("option_value", option_values[index])
            button.setChecked(index == checked_index)
            column, span = positions[index]
            parent_layout.addWidget(button, row, column, 1, span)
            buttons.append(button)

        for button in buttons:
            button.clicked.connect(
                lambda checked=False, current=button, group=buttons: self._select_option_button(
                    group,
                    current,
                )
            )
        return buttons

    def _add_compact_option_row(self, parent_layout, title, options, checked_index=0, values=None):
        row = self._next_grid_row(parent_layout)
        title_label = QLabel(title)
        title_label.setFixedWidth(self.OPTION_TITLE_WIDTH)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_label.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei UI'; font-size: 10px; "
            "background: transparent; border: none;"
        )
        parent_layout.addWidget(title_label, row, 0)

        option_widget = QWidget()
        option_widget.setStyleSheet("background: transparent; border: none;")
        option_layout = QHBoxLayout(option_widget)
        option_layout.setContentsMargins(0, 0, 0, 0)
        option_layout.setSpacing(2)

        buttons = []
        option_values = values if values is not None else options
        for index, text in enumerate(options):
            button = _DotOptionButton(text)
            button.setToolTip(text)
            button.setProperty("option_value", option_values[index])
            button.setChecked(index == checked_index)
            option_layout.addWidget(button, 1)
            buttons.append(button)

        parent_layout.addWidget(option_widget, row, 1, 1, self.OPTION_GRID_COLUMNS)

        for button in buttons:
            button.clicked.connect(
                lambda checked=False, current=button, group=buttons: self._select_option_button(
                    group,
                    current,
                )
            )
        return buttons

    def _add_combo_row(self, parent_layout, title, combo):
        row = self._next_grid_row(parent_layout)
        title_label = QLabel(title)
        title_label.setFixedWidth(self.OPTION_TITLE_WIDTH)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_label.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei UI'; font-size: 10px; "
            "background: transparent; border: none;"
        )
        parent_layout.addWidget(title_label, row, 0)
        parent_layout.addWidget(combo, row, 1, 1, self.OPTION_GRID_COLUMNS)

    def _create_category_combo(self):
        combo = QComboBox()
        combo.setFixedHeight(22)
        combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self._populate_category_combo(combo)
        combo.setStyleSheet(
            """
            QComboBox {
                color: white;
                background-color: rgba(255, 255, 255, 0.16);
                border: 1px solid rgba(255, 255, 255, 0.70);
                border-radius: 4px;
                padding: 1px 6px;
                font-family: 'Microsoft YaHei UI';
                font-size: 10px;
            }
            QComboBox:hover, QComboBox:focus {
                background-color: rgba(255, 255, 255, 0.22);
                border: 1px solid white;
            }
            QComboBox::drop-down {
                border: none;
                width: 18px;
            }
            QComboBox::down-arrow {
                image: url(assets/icons/combo_down_white.svg);
                width: 9px;
                height: 6px;
            }
            QComboBox QAbstractItemView {
                background: white;
                color: #0066cc;
                selection-background-color: #0066cc;
                selection-color: white;
                outline: none;
            }
            """
        )
        DayQueryOptionsPanel._apply_combo_popup_style(combo)
        combo.setFixedHeight(22)
        return combo

    def _populate_category_combo(self, combo, selected_value=None):
        combo.blockSignals(True)
        try:
            combo.clear()
            combo.addItem("全部清单", ScheduleQueryOptions.ALL_CATEGORIES)
            combo.addItem("未分类", ScheduleQueryOptions.UNCATEGORIZED)
            try:
                from src.data.database import db_manager

                for category in db_manager.get_active_categories():
                    combo.addItem(
                        getattr(category, "name", "未命名清单"),
                        getattr(category, "id", None),
                    )
            except Exception:
                pass

            if selected_value is not None:
                index = combo.findData(selected_value)
                if index >= 0:
                    combo.setCurrentIndex(index)
        finally:
            combo.blockSignals(False)

    def _reload_category_options(self):
        if hasattr(self, "category_combo"):
            self._populate_category_combo(
                self.category_combo,
                self.category_combo.currentData(),
            )

    def _select_option_button(self, buttons, selected_button):
        for button in buttons:
            button.setChecked(button is selected_button)
        self.refresh_results()

    def _selected_value(self, buttons, fallback=None):
        for button in buttons:
            if button.isChecked():
                return button.property("option_value")
        return fallback

    def _current_query_options(self):
        return ScheduleQueryOptions(
            category_id=self.category_combo.currentData(),
            priority=self._selected_value(self.priority_buttons),
            reminder_state=self._selected_value(self.reminder_buttons, "all") or "all",
            repeat_kind=self._selected_value(self.repeat_buttons, "all") or "all",
            search_scope=self._selected_value(self.search_scope_buttons, "title") or "title",
            match_mode=self._selected_value(self.search_match_buttons, "fuzzy") or "fuzzy",
        )

    def _current_sort_options(self):
        return ScheduleSortOptions(
            include_completed=True,
            include_overdue=True,
            item_scope="all",
            scheme=self._selected_value(self.sort_buttons, "time") or "time",
            enabled=True,
        )

    def _load_all_schedules(self):
        try:
            from src.data.database import db_manager

            self._category_map = db_manager.get_category_map()
            return db_manager.get_all_schedules()
        except Exception as exc:
            print(f"[AllSchedulesPanel] load schedules failed: {exc}")
            self._category_map = {}
            return []

    def _apply_completion_filter(self, items):
        completion = self._selected_value(self.completion_buttons, "all") or "all"
        if completion == "all":
            return list(items)

        filtered = []
        for item in items:
            status = int(getattr(item, "status", 0) or 0)
            if status == 2:
                continue
            is_completed = status == 1
            is_overdue = _AllScheduleResultCard._is_overdue(item)
            if completion == "completed" and is_completed:
                filtered.append(item)
            elif completion == "overdue" and is_overdue:
                filtered.append(item)
            elif completion == "active" and not is_completed and not is_overdue:
                filtered.append(item)
        return filtered

    def _apply_type_filter(self, items):
        selected_type = self._selected_value(self.type_buttons, "all") or "all"
        if selected_type == "all":
            return list(items)

        filtered = []
        for item in items:
            is_todo = ScheduleQueryService.is_todo(item)
            is_interval = _AllScheduleResultCard._is_interval(item)
            if selected_type == "todo" and is_todo:
                filtered.append(item)
            elif selected_type == "schedule" and not is_todo:
                filtered.append(item)
            elif selected_type == "interval" and not is_todo and is_interval:
                filtered.append(item)
            elif selected_type == "point" and not is_todo and not is_interval:
                filtered.append(item)
        return filtered

    def _filtered_results(self):
        items = self._load_all_schedules()
        items = self._apply_completion_filter(items)
        items = self._apply_type_filter(items)
        items = ScheduleQueryService.apply_options(
            items,
            self._current_query_options(),
            self.search_box.text(),
        )
        return ScheduleSortService.sort_for_all_schedules(
            items,
            self._current_sort_options(),
        )

    def _clear_results_layout(self):
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget is not None and widget is not self.empty_label:
                widget.deleteLater()

    def _show_empty_result(self):
        self.empty_label.setText("暂无符合条件的日程数据")
        self.empty_label.show()
        self.results_layout.addStretch(1)
        self.results_layout.addWidget(self.empty_label)
        self.results_layout.addStretch(1)

    def _add_todo_separator(self):
        line = QFrame(self.results_container)
        line.setObjectName("allSchedulesTodoSeparator")
        line.setFixedHeight(1)
        line.setStyleSheet(
            """
            QFrame#allSchedulesTodoSeparator {
                background-color: rgba(45, 45, 45, 0.32);
                border: none;
            }
            """
        )
        self.results_layout.addWidget(line)

    def _add_virtual_spacer(self, height):
        spacer = QWidget(self.results_container)
        spacer.setObjectName("allSchedulesVirtualSpacer")
        spacer.setFixedHeight(max(0, int(height)))
        spacer.setStyleSheet("background: transparent; border: none;")
        self.results_layout.addWidget(spacer)

    def _result_text_width(self):
        viewport_width = 0
        if hasattr(self, "scroll_area"):
            viewport_width = self.scroll_area.viewport().width()
        return max(80, int(viewport_width) - 8)

    @staticmethod
    def _wrapped_text_height(text, width, point_size, bold=False):
        text = str(text or "")
        if not text:
            return 0
        font = QFont("Microsoft YaHei UI")
        font.setPointSize(point_size)
        font.setBold(bold)
        metrics = QFontMetrics(font)
        rect = metrics.boundingRect(
            QRect(0, 0, max(1, int(width)), 10000),
            Qt.TextFlag.TextWordWrap.value,
            text,
        )
        return max(metrics.height(), rect.height())

    def _estimate_record_height(self, record, width):
        kind, schedule = record
        if kind == "separator":
            return 1 + self.VIRTUAL_ROW_SPACING

        title_height = self._wrapped_text_height(
            getattr(schedule, "title", "") or "未命名日程",
            width,
            12,
            bold=True,
        )
        description = str(getattr(schedule, "description", "") or "").strip()
        description_height = self._wrapped_text_height(description, width, 10)
        time_height = self._wrapped_text_height(
            _AllScheduleResultCard._time_text(schedule),
            width,
            10,
        )
        meta_height = self._wrapped_text_height(
            f"{self._category_name_for(schedule)} · "
            f"{_AllScheduleResultCard._priority_text(schedule)} · "
            f"{_AllScheduleResultCard._status_text(schedule)} · "
            f"{_AllScheduleResultCard._repeat_text(schedule)}",
            width,
            10,
        )
        text_count = 3 + (1 if description else 0)
        return (
            11
            + title_height
            + description_height
            + time_height
            + meta_height
            + max(0, text_count - 1) * 4
            + self.VIRTUAL_ROW_SPACING
        )

    def _build_result_records(self, results):
        has_schedule = any(not ScheduleQueryService.is_todo(item) for item in results)
        has_todo = any(ScheduleQueryService.is_todo(item) for item in results)
        separator_added = False
        records = []
        for schedule in results:
            if (
                has_schedule
                and has_todo
                and not separator_added
                and ScheduleQueryService.is_todo(schedule)
            ):
                records.append(("separator", None))
                separator_added = True
            records.append(("schedule", schedule))
        return records

    def _rebuild_virtual_metrics(self):
        width = self._result_text_width()
        self._virtual_width = width
        self._result_heights = [
            self._estimate_record_height(record, width)
            for record in self._result_records
        ]
        offsets = []
        current = 0
        for height in self._result_heights:
            offsets.append(current)
            current += int(height)
        self._result_offsets = offsets
        self._virtual_total_height = max(0, int(current))
        self.results_container.setFixedSize(
            max(1, self.scroll_area.viewport().width()),
            max(self.scroll_area.viewport().height(), self._virtual_total_height),
        )
        self._virtual_render_range = (-1, -1)

    def _render_virtual_results(self, *_args):
        if not hasattr(self, "results_layout"):
            return
        if not self._result_records:
            return

        current_width = self._result_text_width()
        if current_width != self._virtual_width:
            self._rebuild_virtual_metrics()

        viewport_height = max(1, self.scroll_area.viewport().height())
        scroll_value = self.scroll_area.verticalScrollBar().value()
        start = max(
            0,
            bisect_right(self._result_offsets, scroll_value)
            - 1
            - self.VIRTUAL_BUFFER_ITEMS,
        )
        end = min(
            len(self._result_records),
            bisect_right(
                self._result_offsets,
                scroll_value + viewport_height,
            )
            + 1
            + self.VIRTUAL_BUFFER_ITEMS,
        )

        if (start, end) == self._virtual_render_range:
            return
        self._virtual_render_range = (start, end)
        self._clear_results_layout()

        top_height = self._result_offsets[start] if start < len(self._result_offsets) else 0
        self._add_virtual_spacer(top_height)

        for index in range(start, end):
            kind, schedule = self._result_records[index]
            if kind == "separator":
                self._add_todo_separator()
                continue
            card = _AllScheduleResultCard(
                schedule,
                self._category_name_for(schedule),
                self.results_container,
            )
            card.detail_requested.connect(self.schedule_detail_requested.emit)
            card.context_requested.connect(self._show_result_context_menu)
            card.setFixedHeight(max(1, int(self._result_heights[index])))
            self.results_layout.addWidget(card)

        bottom_height = self._virtual_total_height
        if end > 0 and end <= len(self._result_offsets):
            bottom_height -= self._result_offsets[end - 1] + self._result_heights[end - 1]
        self._add_virtual_spacer(bottom_height)

    def _category_name_for(self, schedule):
        category = self._category_map.get(getattr(schedule, "category_id", None))
        return getattr(category, "name", None) or "未分类"

    def _show_result_context_menu(self, schedule, global_pos):
        menu = QMenu(self)
        menu.setStyleSheet(
            """
            QMenu {
                background-color: rgba(255, 255, 255, 0.96);
                border: 1px solid rgba(0, 0, 0, 0.12);
                border-radius: 6px;
                padding: 5px;
                color: #333333;
                font-family: "Microsoft YaHei UI";
                font-size: 12px;
            }
            QMenu::item {
                background: transparent;
                padding: 5px 18px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: rgba(0, 102, 204, 0.10);
                color: #0066cc;
            }
            """
        )

        open_action = QAction("打开详情", menu)
        open_action.triggered.connect(lambda: self.schedule_detail_requested.emit(schedule))
        menu.addAction(open_action)
        menu.addSeparator()

        is_completed = int(getattr(schedule, "status", 0) or 0) == 1
        status_action = QAction("撤销完成" if is_completed else "完成日程", menu)
        status_action.triggered.connect(
            lambda: self._handle_status_change(schedule, 0 if is_completed else 1)
        )
        menu.addAction(status_action)

        delete_action = QAction("删除日程", menu)
        delete_action.triggered.connect(lambda: self._handle_delete_schedule(schedule))
        menu.addAction(delete_action)

        menu.exec(global_pos)

    def _handle_status_change(self, schedule, new_status):
        schedule_id = getattr(schedule, "id", None)
        if schedule_id is None:
            return
        try:
            from src.data.database import db_manager

            if db_manager.update_schedule_status(schedule_id, new_status):
                try:
                    schedule.status = new_status
                except Exception:
                    pass
                self.refresh_results()
                self._notify_schedule_changed(schedule)
        except Exception as exc:
            print(f"[AllSchedulesPanel] update status failed: {exc}")

    def _handle_delete_schedule(self, schedule):
        schedule_id = getattr(schedule, "id", None)
        if schedule_id is None:
            return
        title = str(getattr(schedule, "title", "") or "未命名日程")
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定删除“{title}”吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            from src.data.database import db_manager

            if db_manager.delete_schedule(schedule_id):
                self.refresh_results()
                self._notify_schedule_changed(None)
        except Exception as exc:
            print(f"[AllSchedulesPanel] delete schedule failed: {exc}")

    def _notify_schedule_changed(self, schedule):
        parent = self.parent_window
        if parent is None:
            return
        if hasattr(parent, "_refresh_dashboard_todo_week"):
            parent._refresh_dashboard_todo_week()
            return
        signal = getattr(parent, "schedule_updated", None)
        if signal is not None and hasattr(signal, "emit"):
            signal.emit(schedule)

    def refresh_results(self, *_args):
        if not hasattr(self, "results_layout"):
            return

        self._clear_results_layout()
        results = self._filtered_results()
        self._result_items = list(results)
        self._result_records = self._build_result_records(self._result_items)
        if not results:
            self._result_records = []
            self._result_heights = []
            self._result_offsets = []
            self._virtual_total_height = 0
            self.results_container.setFixedSize(
                max(1, self.scroll_area.viewport().width()),
                max(1, self.scroll_area.viewport().height()),
            )
            self._show_empty_result()
            return

        self.empty_label.hide()
        self._rebuild_virtual_metrics()
        self.scroll_area.verticalScrollBar().setValue(0)
        self._render_virtual_results()

    def _load_tinted_pixmap(self, icon_name, color, target_size=16):
        path = f"assets/icons/{icon_name}"
        if not os.path.exists(path):
            return QPixmap()

        scale_ratio = 4.0
        high_res_size = int(target_size * scale_ratio)
        image = QImage(high_res_size, high_res_size, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        if icon_name.lower().endswith(".svg"):
            renderer = QSvgRenderer(path)
            if renderer.isValid():
                renderer.render(painter)
        else:
            source_image = QImage(path)
            if not source_image.isNull():
                source_image = source_image.scaled(
                    high_res_size,
                    high_res_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                x = (high_res_size - source_image.width()) // 2
                y = (high_res_size - source_image.height()) // 2
                painter.drawImage(x, y, source_image)
        painter.end()

        painter = QPainter(image)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        color_object = QColor(color) if isinstance(color, str) else color
        painter.fillRect(image.rect(), color_object)
        painter.end()

        pixmap = QPixmap.fromImage(image)
        pixmap.setDevicePixelRatio(scale_ratio)
        return pixmap

    def _load_tinted_icon(self, icon_name, color, target_size=16):
        pixmap = self._load_tinted_pixmap(icon_name, color, target_size)
        return QIcon(pixmap)

    def _load_padded_svg_icon(self, icon_name, color, icon_size=10, canvas_size=16):
        renderer = QSvgRenderer(f"assets/icons/{icon_name}")
        if not renderer.isValid():
            return QIcon()

        scale_ratio = 4.0
        high_res_canvas = int(canvas_size * scale_ratio)
        high_res_icon = int(icon_size * scale_ratio)
        offset = (high_res_canvas - high_res_icon) / 2

        image = QImage(high_res_canvas, high_res_canvas, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        renderer.render(painter, QRectF(offset, offset, high_res_icon, high_res_icon))
        painter.end()

        painter = QPainter(image)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(image.rect(), QColor(color))
        painter.end()

        pixmap = QPixmap.fromImage(image)
        pixmap.setDevicePixelRatio(scale_ratio)
        return QIcon(pixmap)

    def _update_header_icons(self):
        self._settings_icon_source = self._load_tinted_pixmap(
            "set.svg",
            "#FFFFFF",
            18,
        )
        self._set_settings_icon_angle(self._settings_icon_angle)
        pin_color = "#FFFFFF" if self.is_pinned else "#96FFFFFF"
        self.btn_pin.setIcon(self._load_tinted_icon("pin.svg", pin_color, 16))
        self.btn_close.setIcon(self._load_tinted_icon("close.png", "#FFFFFF", 12))

    def _get_settings_icon_angle(self):
        return self._settings_icon_angle

    def _set_settings_icon_angle(self, angle):
        self._settings_icon_angle = float(angle)
        if self._settings_icon_source.isNull():
            return

        canvas_size = 24.0
        icon_size = 18.0
        ratio = max(self._settings_icon_source.devicePixelRatio(), 1.0)
        pixmap = QPixmap(round(canvas_size * ratio), round(canvas_size * ratio))
        pixmap.setDevicePixelRatio(ratio)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.translate(canvas_size / 2.0, canvas_size / 2.0)
        painter.rotate(self._settings_icon_angle)
        painter.drawPixmap(
            QPointF(-icon_size / 2.0, -icon_size / 2.0),
            self._settings_icon_source,
        )
        painter.end()
        self.btn_settings.setIcon(QIcon(pixmap))

    settingsIconAngle = pyqtProperty(
        float,
        fget=_get_settings_icon_angle,
        fset=_set_settings_icon_angle,
    )

    def _update_header_button_positions(self):
        top_margin = 0
        right_margin = 0
        gap = 0

        close_x = self.width() - self.btn_close.width() - right_margin
        self.btn_close.move(close_x, top_margin)
        self.btn_close.raise_()

        pin_x = close_x - self.btn_pin.width() - gap
        self.btn_pin.move(pin_x, top_margin)
        self.btn_pin.raise_()

    def _toggle_settings_area(self):
        self._settings_visible = not self._settings_visible
        self.settings_area.setVisible(self._settings_visible)
        self._settings_rotation_animation.stop()
        self._settings_rotation_animation.setStartValue(self._settings_icon_angle)
        self._settings_rotation_animation.setEndValue(
            180.0 if self._settings_visible else 0.0
        )
        self._settings_rotation_animation.start()

    def _toggle_search_options_area(self):
        self._search_options_visible = not self._search_options_visible
        self.search_options_area.setVisible(self._search_options_visible)

    def _toggle_pin(self):
        self.set_pinned(not self.is_pinned)

    def set_pinned(self, enabled):
        self.is_pinned = bool(enabled)
        set_window_pin_state(self, self.is_pinned)
        self._update_header_icons()

    def showEvent(self, event):
        super().showEvent(event)
        self._reload_category_options()
        self.refresh_results()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_header_button_positions()
        if getattr(self, "_result_records", None):
            self._rebuild_virtual_metrics()
            self._render_virtual_results()

    def _install_resize_event_filters(self):
        for widget in (
            self.display_frame,
            self.scroll_area,
            self.scroll_area.viewport(),
            self.results_container,
            self.settings_area,
            self.search_options_area,
        ):
            widget.setMouseTracking(True)
            widget.installEventFilter(self)

    def eventFilter(self, watched, event):
        if (
            watched is self.search_box
            and event.type() == QEvent.Type.MouseButtonPress
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._toggle_search_options_area()
            return False

        if watched in {
            self.display_frame,
            self.scroll_area,
            self.scroll_area.viewport(),
            self.results_container,
            self.settings_area,
            self.search_options_area,
        }:
            if event.type() == QEvent.Type.Leave:
                watched.unsetCursor()
            elif event.type() == QEvent.Type.MouseMove and not event.buttons():
                edge = self._hit_resize_edge(watched.mapTo(self, event.position().toPoint()).y())
                watched.setCursor(
                    Qt.CursorShape.SizeVerCursor
                    if edge
                    else Qt.CursorShape.ArrowCursor
                )
            elif (
                event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
            ):
                edge = self._hit_resize_edge(watched.mapTo(self, event.position().toPoint()).y())
                if edge:
                    self._start_resize(edge, event.globalPosition().toPoint())
                    event.accept()
                    return True
            elif (
                event.type() == QEvent.Type.MouseMove
                and self._resize_edge
                and event.buttons() & Qt.MouseButton.LeftButton
            ):
                self._perform_resize(event.globalPosition().toPoint())
                event.accept()
                return True
            elif (
                event.type() == QEvent.Type.MouseButtonRelease
                and event.button() == Qt.MouseButton.LeftButton
                and self._resize_edge
            ):
                self._finish_resize()
                event.accept()
                return True
        return super().eventFilter(watched, event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        painter.fillPath(path, QBrush(gradient))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(0, 0, 0, 28), 1))
        painter.drawPath(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._hit_resize_edge(event.position().y())
            if edge:
                self._start_resize(edge, event.globalPosition().toPoint())
                event.accept()
                return
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resize_edge and self._resize_start_pos and self._resize_start_geometry:
            self._perform_resize(event.globalPosition().toPoint())
            event.accept()
            return

        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return

        edge = self._hit_resize_edge(event.position().y())
        self.setCursor(
            Qt.CursorShape.SizeVerCursor
            if edge
            else Qt.CursorShape.ArrowCursor
        )
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = None
            self._finish_resize()
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        if self._resize_edge is None:
            self.unsetCursor()
        super().leaveEvent(event)

    def _hit_resize_edge(self, y):
        if y <= self.RESIZE_MARGIN:
            return "top"
        if y >= self.height() - self.RESIZE_MARGIN:
            return "bottom"
        return None

    def _start_resize(self, edge, global_pos):
        self._resize_edge = edge
        self._resize_start_pos = global_pos
        self._resize_start_geometry = self.geometry()
        self.setCursor(Qt.CursorShape.SizeVerCursor)

    def _perform_resize(self, global_pos):
        if not self._resize_edge or not self._resize_start_pos or not self._resize_start_geometry:
            return
        delta_y = global_pos.y() - self._resize_start_pos.y()
        geometry = self._resize_start_geometry
        if self._resize_edge == "bottom":
            new_height = max(self.minimumHeight(), geometry.height() + delta_y)
            self.resize(self.width(), new_height)
        elif self._resize_edge == "top":
            new_height = max(self.minimumHeight(), geometry.height() - delta_y)
            consumed_delta = geometry.height() - new_height
            self.setGeometry(
                geometry.x(),
                geometry.y() + consumed_delta,
                geometry.width(),
                new_height,
            )

    def _finish_resize(self):
        self._resize_edge = None
        self._resize_start_pos = None
        self._resize_start_geometry = None
