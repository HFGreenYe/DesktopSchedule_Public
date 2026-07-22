# src/ui/time_picker_week.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCalendarWidget, QGridLayout, QFrame, QPushButton,
                             QToolButton, QTableView, QAbstractItemView, QToolTip)
from PyQt6.QtCore import (Qt, QDate, QTime, pyqtSignal, QSize, QPoint, QEvent,
                          QTimer, QRect)
from PyQt6.QtGui import (QIcon, QPixmap, QPainter, QColor, QTextCharFormat,
                         QCursor)
from PyQt6.QtSvg import QSvgRenderer
from datetime import datetime, timedelta
from ..config import AppConfig
from .calendar_pop import HighlightCalendarWidget
from .components import IOSSwitch, NumberScroller
from .time_picker import SelectionModeLabel

class TimePickerViewWeek(QWidget):
    back_requested = pyqtSignal()
    confirm_requested = pyqtSignal(object, object)
    multiple_confirm_requested = pyqtSignal(object)
    selection_mode_changed = pyqtSignal(str)
    timeChanged = pyqtSignal(QDate, bool, QTime, QTime)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_date = QDate.currentDate()
        self._end_day_offset = 0
        self._prev_end_hour = None
        self._selection_mode = "single"
        self._selected_dates = set()
        self._multi_drag_active = False
        self._multi_drag_last_date = None
        self._multi_press_date = None
        self._multi_drag_happened = False
        self._suppress_next_calendar_click = False
        self._calendar_view = None
        self._init_ui()
        self._update_time_group_layout(False)
        self._connect_signals()

        # 初始赋值
        now = QTime.currentTime()
        self.scroll_end_hour.set_value(f"{now.hour():02d}")
        self.scroll_end_min.set_value(f"{now.minute():02d}")
        self._prev_end_hour = int(self.scroll_end_hour.get_value())
        self._update_end_date_label()

    def _get_colored_icon(self, icon_path, color_hex, disabled_color="#b8b8b8"):
        def render_pixmap(color):
            renderer = QSvgRenderer(icon_path)
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            painter.fillRect(pixmap.rect(), QColor(color))
            painter.end()
            return pixmap

        icon = QIcon()
        icon.addPixmap(render_pixmap(color_hex), QIcon.Mode.Normal, QIcon.State.Off)
        icon.addPixmap(render_pixmap(disabled_color), QIcon.Mode.Disabled, QIcon.State.Off)
        return icon

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        # === 1. 左侧区域 (日历) ===
        self.left_panel = QFrame()
        left_vbox = QVBoxLayout(self.left_panel)
        
        header_row = QHBoxLayout()
        self.lbl_title = QLabel("设置时间")
        self.lbl_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        header_row.addWidget(self.lbl_title)
        self.btn_selection_mode = SelectionModeLabel(self.left_panel)
        self.btn_selection_mode.setTextFormat(Qt.TextFormat.RichText)
        self.btn_selection_mode.setText(self._selection_mode_text("单选"))
        self.btn_selection_mode.setFixedSize(48, 24)
        self.btn_selection_mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_selection_mode.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_selection_mode.setToolTip("点击切换单选/多选")
        self.btn_selection_mode.setStyleSheet("""
            background: transparent;
            border: none;
            color: rgba(255, 255, 255, 0.72);
            font-family: 'Microsoft YaHei';
            font-size: 12px;
            font-weight: bold;
            padding: 0px;
        """)
        header_row.addWidget(self.btn_selection_mode)
        header_row.addStretch()
        left_vbox.addLayout(header_row)

        self.calendar = HighlightCalendarWidget(
            self,
            export_theme=False,
            schedule_markers=False,
            dark_mode=True,
        )
        self.calendar.setGridVisible(False)
        self.calendar.setNavigationBarVisible(True)
        self.calendar.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        )
        self.calendar.setStyleSheet(f"""
            QCalendarWidget,
            QCalendarWidget QWidget {{
                background-color: transparent;
                alternate-background-color: transparent;
                border: none;
                color: white;
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background-color: transparent;
                border: none;
            }}
            QCalendarWidget QAbstractItemView:enabled {{
                background-color: transparent;
                alternate-background-color: transparent;
                selection-background-color: {AppConfig.COLOR_GRADIENT_START};
                selection-color: white;
                border: none;
                outline: 0;
            }}
            QCalendarWidget QHeaderView::section {{
                background-color: transparent;
                color: white;
                border: none;
                padding: 4px;
                font-weight: bold;
            }}
            QCalendarWidget QToolButton {{
                color: white;
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
                font-weight: bold;
                icon-size: 20px;
            }}
            QCalendarWidget QToolButton:disabled {{
                color: #b8b8b8;
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: rgba(255, 255, 255, 0.10);
            }}
            QCalendarWidget QToolButton::menu-indicator {{
                image: none;
            }}
            QCalendarWidget QSpinBox,
            QCalendarWidget QSpinBox QLineEdit {{
                color: white;
                background-color: transparent;
                border: none;
                font-weight: bold;
            }}
            QCalendarWidget QMenu {{
                background-color: rgba(35, 35, 35, 0.96);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.20);
            }}
        """)
        self.calendar.setAutoFillBackground(False)
        self._calendar_view = self.calendar.findChild(
            QTableView,
            "qt_calendar_calendarview",
        )
        if self._calendar_view is not None:
            self._calendar_view.viewport().setMouseTracking(True)
            self._calendar_view.viewport().installEventFilter(self)
        # 限制最小日期为今天，解决无法退回上个月和之前日子的限制 
        self.calendar.setMinimumDate(QDate.currentDate())

        weekday_format = QTextCharFormat()
        weekday_format.setForeground(QColor("#ffffff"))
        for weekday in (
            Qt.DayOfWeek.Monday,
            Qt.DayOfWeek.Tuesday,
            Qt.DayOfWeek.Wednesday,
            Qt.DayOfWeek.Thursday,
            Qt.DayOfWeek.Friday,
        ):
            self.calendar.setWeekdayTextFormat(weekday, weekday_format)

        weekend_format = QTextCharFormat()
        weekend_format.setForeground(QColor("#ff0000"))
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, weekend_format)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, weekend_format)
        
        # 替换日历切换图标
        arrow_color = "#ffffff"
        prev_btn = self.calendar.findChild(QToolButton, "qt_calendar_prevmonth")
        if prev_btn:
            prev_btn.setIcon(self._get_colored_icon("assets/icons/cal_left.svg", arrow_color))
            prev_btn.setIconSize(QSize(18, 18))

        next_btn = self.calendar.findChild(QToolButton, "qt_calendar_nextmonth")
        if next_btn:
            next_btn.setIcon(self._get_colored_icon("assets/icons/cal_right.svg", arrow_color))
            next_btn.setIconSize(QSize(18, 18))

        left_vbox.addWidget(self.calendar)

        # === 2. 分割线 ===
        line = QFrame()
        line.setFixedWidth(1)
        line.setStyleSheet("background-color: rgba(255, 255, 255, 60); margin: 20px 10px;")
        
        main_layout.addWidget(self.left_panel, 1)
        main_layout.addWidget(line)

        # === 3. 右侧区域 ===
        self.right_panel = QFrame()
        right_vbox = QVBoxLayout(self.right_panel)
        right_vbox.setSpacing(15)

        # 启用开关
        switch_row = QHBoxLayout()
        lbl_switch = QLabel("启用开始时间")
        lbl_switch.setStyleSheet("color: white; font-size: 15px; font-weight: bold;")
        self.chk_enable_start = IOSSwitch()
        switch_row.addWidget(lbl_switch)
        switch_row.addStretch()
        switch_row.addWidget(self.chk_enable_start)
        right_vbox.addLayout(switch_row)

        # 时间滚轮容器
        self.time_picker_container = QFrame()
        self.time_picker_container.setObjectName("TimeContainer")
        self.time_picker_container.setStyleSheet(
            "QFrame#TimeContainer { background-color: transparent; border: none; }"
        )
        
        h_time_layout = QHBoxLayout(self.time_picker_container)
        (
            self.start_group,
            self.lbl_start,
            self.scroll_start_hour,
            self.scroll_start_min,
        ) = self._create_scroller_pair("开始时间")
        (
            self.end_group,
            self.lbl_end,
            self.scroll_end_hour,
            self.scroll_end_min,
        ) = self._create_scroller_pair("完成时间", with_date_label=True)
        
        h_time_layout.addWidget(self.start_group)
        h_time_layout.addWidget(self.end_group)
        right_vbox.addWidget(self.time_picker_container)
        self.start_group.hide()

        # 快捷按钮组
        self.duration_grid = QWidget()
        grid = QGridLayout(self.duration_grid)
        grid.setContentsMargins(0, 0, 0, 0)
        durations = [(10, "10分钟"), (15, "15分钟"), (30, "30分钟"), (45, "45分钟"), (60, "1小时"), (90, "1.5小时")]
        for i, (mins, txt) in enumerate(durations):
            btn = QPushButton(txt)
            btn.setFixedHeight(28)
            btn.setProperty("minutes", mins)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("QPushButton { background: rgba(255,255,255,0.15); border-radius: 14px; color: white; font-size: 11px; } QPushButton:hover { background: rgba(255,255,255,0.3); }")
            btn.clicked.connect(lambda _, b=btn: self._on_quick_set(b))
            grid.addWidget(btn, i // 3, i % 3)
        
        self.duration_grid.hide()
        right_vbox.addWidget(self.duration_grid)

        # 确定/取消
        btn_row = QHBoxLayout()
        self.btn_cancel = QPushButton("取消")
        self.btn_ok = QPushButton("确定")
        for btn in [self.btn_cancel, self.btn_ok]:
            btn.setFixedSize(70, 32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet("QPushButton { background: transparent; border: 1px solid rgba(255,255,255,0.6); border-radius: 16px; color: white; }")
        self.btn_ok.setStyleSheet(f"""
            QPushButton {{
                background: #ffffff;
                border: none;
                border-radius: 16px;
                color: {AppConfig.COLOR_GRADIENT_START};
                font-weight: bold;
            }}
            QPushButton:hover {{ background: #f0f0f0; }}
        """)
        
        btn_row.addStretch()
        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_ok)
        right_vbox.addLayout(btn_row)

        main_layout.addWidget(self.right_panel, 1)

    def _create_scroller_pair(self, label, with_date_label=False):
        grp = QWidget()
        lay = QVBoxLayout(grp)
        lay.setContentsMargins(0,0,0,0)

        label_row = QHBoxLayout()
        label_row.setContentsMargins(0, 0, 0, 0)
        label_row.setSpacing(0)
        label_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl = QLabel(label)
        lbl.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 11px;")
        label_row.addStretch()

        if with_date_label:
            self.end_date_balance = QWidget()
            self.end_date_balance.setFixedWidth(0)
            label_row.addWidget(self.end_date_balance)

        label_row.addWidget(lbl)

        if with_date_label:
            self.lbl_end_date = QLabel("（今）")
            self.lbl_end_date.setStyleSheet(
                "color: rgba(255,255,255,0.85); font-size: 11px; font-weight: bold;"
            )
            self.lbl_end_date.setCursor(Qt.CursorShape.PointingHandCursor)
            self.lbl_end_date.setToolTip("双击切换完成日期")
            self.lbl_end_date.installEventFilter(self)
            label_row.addWidget(self.lbl_end_date)
        label_row.addStretch()
        lay.addLayout(label_row)

        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)
        sh = NumberScroller([f"{i:02d}" for i in range(24)])
        sm = NumberScroller([f"{i:02d}" for i in range(60)])
        single_line_style = """
            QListWidget { background: transparent; outline: none; }
            QListWidget::item {
                height: 30px;
                color: rgba(255, 255, 255, 0.4);
                font-size: 14px;
                font-family: 'Microsoft YaHei';
                border: none;
            }
            QListWidget::item:selected {
                background: transparent;
                color: #FFFFFF;
                font-size: 16px;
                font-weight: bold;
            }
        """
        for scroller in (sh, sm):
            scroller._week_multi_line_style = scroller.styleSheet()
            scroller._week_single_line_style = single_line_style

        lbl_colon = QLabel(":")
        lbl_colon.setFixedSize(10, 30)
        lbl_colon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_colon.setStyleSheet(
            "color: white; font-size: 16px; font-weight: bold; padding: 0px;"
        )
        grp._time_colon = lbl_colon

        h.addStretch()
        h.addWidget(sh)
        h.addWidget(lbl_colon)
        h.addWidget(sm)
        h.addStretch()

        lay.addLayout(h)
        return grp, lbl, sh, sm

    def _update_time_group_labels(self, start_enabled):
        self.lbl_start.setText("开始" if start_enabled else "开始时间")
        self.lbl_end.setText("完成" if start_enabled else "完成时间")

    def _sync_end_date_balance(self):
        if not hasattr(self, "end_date_balance"):
            return
        balance_width = (
            self.lbl_end_date.sizeHint().width()
            if not self.lbl_end_date.isHidden()
            else 0
        )
        self.end_date_balance.setFixedWidth(balance_width)

    def _update_time_group_layout(self, start_enabled):
        self._update_time_group_labels(start_enabled)
        self.lbl_end_date.setVisible(start_enabled)
        if not start_enabled and hasattr(self, "end_date_balance"):
            self.end_date_balance.setFixedWidth(0)
        elif start_enabled:
            self._sync_end_date_balance()

        for group, hour_scroller, minute_scroller in (
            (self.start_group, self.scroll_start_hour, self.scroll_start_min),
            (self.end_group, self.scroll_end_hour, self.scroll_end_min),
        ):
            colon = group._time_colon
            if start_enabled:
                colon.setFixedSize(10, 30)
                colon.setStyleSheet(
                    "color: white; font-size: 16px; font-weight: bold; padding: 0px;"
                )
            else:
                colon.setFixedSize(10, 90)
                colon.setStyleSheet(
                    "color: white; font-size: 20px; font-weight: bold; "
                    "padding-bottom: 5px;"
                )

            for scroller in (hour_scroller, minute_scroller):
                current_value = scroller.get_value()
                if start_enabled:
                    scroller.setFixedSize(42, 30)
                    scroller.setStyleSheet(scroller._week_single_line_style)
                else:
                    scroller.setFixedSize(50, 90)
                    scroller.setStyleSheet(scroller._week_multi_line_style)
                QTimer.singleShot(
                    0,
                    lambda target=scroller, value=current_value: target.set_value(value),
                )

    @staticmethod
    def _selection_mode_text(mode_text):
        return f'（<span style="color: #ffffff;">{mode_text}</span>）'

    def _toggle_selection_mode(self):
        mode = "multiple" if self._selection_mode == "single" else "single"
        self.set_selection_mode(mode)

    def set_selection_mode(self, mode, selected_dates=None):
        mode = "multiple" if mode == "multiple" else "single"
        previous_mode = self._selection_mode
        self._selection_mode = mode
        if selected_dates is not None:
            self._selected_dates = {
                value.toPyDate() if isinstance(value, QDate) else value
                for value in selected_dates
            }
        elif mode == "multiple" and previous_mode != "multiple":
            self._selected_dates = {self.current_date.toPyDate()}

        mode_text = "多选" if mode == "multiple" else "单选"
        self.btn_selection_mode.setText(self._selection_mode_text(mode_text))
        if mode == "single":
            self.calendar.setSelectedDate(self.current_date)
        if self._calendar_view is not None:
            selection_mode = (
                QAbstractItemView.SelectionMode.NoSelection
                if mode == "multiple"
                else QAbstractItemView.SelectionMode.SingleSelection
            )
            self._calendar_view.setSelectionMode(selection_mode)
            self._calendar_view.clearSelection()
        self.calendar.set_multi_selection(mode == "multiple", self._selected_dates)
        self.selection_mode_changed.emit(mode)

    def set_selection_mode_available(self, available):
        self.btn_selection_mode.setVisible(bool(available))
        if not available:
            self.set_selection_mode("single", [])

    def set_multiple_ranges(self, ranges):
        dates = []
        for start_time, end_time in ranges or []:
            target_time = start_time or end_time
            if target_time is not None:
                dates.append(target_time.date())
        if not dates:
            return
        first_date = min(dates)
        self.current_date = QDate(first_date.year, first_date.month, first_date.day)
        self.calendar.setSelectedDate(self.current_date)
        self._update_end_date_label()
        self.set_selection_mode("multiple", dates)

    def set_title(self, text):
        self.lbl_title.setText(text)

    def set_initial_data(self, start_dt, end_dt):
        target = end_dt if end_dt else datetime.now()
        self._end_day_offset = 0
        if start_dt and end_dt:
            start_date = start_dt.date()
            end_date = end_dt.date()
            offset_days = (end_date - start_date).days
            if offset_days > 0:
                self._end_day_offset = offset_days
                self.current_date = QDate(start_date.year, start_date.month, start_date.day)
            else:
                self.current_date = QDate(target.year, target.month, target.day)
        else:
            self.current_date = QDate(target.year, target.month, target.day)
        self._prev_end_hour = target.hour
        self.set_selection_mode("single", [])
        self.calendar.setSelectedDate(self.current_date)
        self.scroll_end_hour.set_value(f"{target.hour:02d}")
        self.scroll_end_min.set_value(f"{target.minute:02d}")
        self._update_end_date_label()
        if start_dt:
            self.chk_enable_start.setChecked(True)
            self.start_group.show()
            self.duration_grid.show()
            self.scroll_start_hour.set_value(f"{start_dt.hour:02d}")
            self.scroll_start_min.set_value(f"{start_dt.minute:02d}")
        else:
            self.chk_enable_start.setChecked(False)
            self.start_group.hide()
            self.duration_grid.hide()
        self._update_time_group_layout(bool(start_dt))

    def _connect_signals(self):
        self.btn_selection_mode.clicked.connect(self._toggle_selection_mode)
        self.calendar.clicked.connect(self._on_date_selected)
        self.chk_enable_start.toggled.connect(self._on_switch_toggled)
        self.btn_cancel.clicked.connect(self.back_requested.emit)
        self.btn_ok.clicked.connect(self._on_confirm)
        # 滚轮检测信号
        self.scroll_end_hour.value_changed.connect(self._on_end_hour_changed)
        for s in [self.scroll_start_hour, self.scroll_start_min, self.scroll_end_hour, self.scroll_end_min]:
            s.value_changed.connect(self._validate_scroll_time)

    def _on_date_selected(self, date):
        if self._selection_mode == "multiple":
            if self._suppress_next_calendar_click:
                self._suppress_next_calendar_click = False
                if self._calendar_view is not None:
                    self._calendar_view.clearSelection()
                return
            self._multi_drag_last_date = None
            self._toggle_multi_date(date)
            self._multi_drag_last_date = None
            if self._calendar_view is not None:
                self._calendar_view.clearSelection()
            return
        self.current_date = date
        self._update_end_date_label()

    def _on_switch_toggled(self, checked):
        self.start_group.setVisible(checked)
        self.duration_grid.setVisible(checked)
        self._update_time_group_layout(checked)

    def _on_quick_set(self, btn):
        mins = btn.property("minutes")
        eh, em = int(self.scroll_end_hour.get_value()), int(self.scroll_end_min.get_value())
        dt_end = datetime(2024,1,1, eh, em)
        dt_start = dt_end - timedelta(minutes=mins)
        self.scroll_start_hour.set_value(f"{dt_start.hour:02d}")
        self.scroll_start_min.set_value(f"{dt_start.minute:02d}")

    def _time_range_for_date(self, base_date):
        end_hour = int(self.scroll_end_hour.get_value())
        end_minute = int(self.scroll_end_min.get_value())
        day_offset = self._end_day_offset

        start_time = None
        if self.chk_enable_start.isChecked():
            start_time = datetime(
                base_date.year(),
                base_date.month(),
                base_date.day(),
                int(self.scroll_start_hour.get_value()),
                int(self.scroll_start_min.get_value()),
            )

        end_date = base_date.addDays(day_offset)
        end_time = datetime(
            end_date.year(),
            end_date.month(),
            end_date.day(),
            end_hour,
            end_minute,
        )
        if start_time is not None and end_time <= start_time:
            end_date = base_date.addDays(day_offset + 1)
            end_time = datetime(
                end_date.year(),
                end_date.month(),
                end_date.day(),
                end_hour,
                end_minute,
            )
        return start_time, end_time

    def _on_confirm(self):
        if self._selection_mode == "multiple":
            if not self._selected_dates:
                QToolTip.showText(
                    self.btn_ok.mapToGlobal(QPoint(0, -28)),
                    "选择日期不能为0",
                    self.btn_ok,
                    QRect(),
                    1800,
                )
                return

            ranges = []
            now = datetime.now()
            for py_date in sorted(self._selected_dates):
                base_date = QDate(py_date.year, py_date.month, py_date.day)
                start_time, end_time = self._time_range_for_date(base_date)
                if end_time < now:
                    return
                ranges.append((start_time, end_time))
            self.multiple_confirm_requested.emit(ranges)
            return

        d = self.calendar.selectedDate()
        end_date = d.addDays(self._end_day_offset)
        dt_end = datetime(end_date.year(), end_date.month(), end_date.day(), int(self.scroll_end_hour.get_value()), int(self.scroll_end_min.get_value()))
        dt_start = None
        if self.chk_enable_start.isChecked():
            dt_start = datetime(d.year(), d.month(), d.day(), int(self.scroll_start_hour.get_value()), int(self.scroll_start_min.get_value()))
            if dt_start is not None and dt_end <= dt_start:
                self._end_day_offset += 1
                end_date = d.addDays(self._end_day_offset)
                dt_end = datetime(end_date.year(), end_date.month(), end_date.day(), int(self.scroll_end_hour.get_value()), int(self.scroll_end_min.get_value()))

        # 二次校验：确保不早于当前时间
        now = datetime.now()
        if dt_end < now: return

        self.confirm_requested.emit(dt_start, dt_end)

    def _on_end_hour_changed(self):
        new_hour = int(self.scroll_end_hour.get_value())
        prev = self._prev_end_hour
        self._prev_end_hour = new_hour
        if prev is None:
            return
        if prev == 23 and new_hour == 0:
            self._end_day_offset += 1
        elif prev == 0 and new_hour == 23:
            self._end_day_offset = max(0, self._end_day_offset - 1)
        self._update_end_date_label()

    def _update_end_date_label(self):
        offset = self._end_day_offset
        if offset == 0:
            text = "（今）"
        elif 1 <= offset <= 9:
            text = f"（后{offset}天）"
        else:
            end_date = self.current_date.addDays(offset)
            text = f"（{end_date.toString('yy-MM-dd')}）"
        self.lbl_end_date.setText(text)
        if len(text) > 8:
            self.lbl_end_date.setStyleSheet(
                "color: rgba(255,255,255,0.85); font-size: 9px; font-weight: bold;"
            )
        else:
            self.lbl_end_date.setStyleSheet(
                "color: rgba(255,255,255,0.85); font-size: 11px; font-weight: bold;"
            )
        self._sync_end_date_balance()

    def _show_end_date_calendar(self):
        from .calendar_pop import CalendarPop

        cal_pop = CalendarPop(self, export_theme=False, schedule_markers=False, close_on_select=False)
        cal_pop.calendar.setMinimumDate(self.current_date)
        # 已过期日期铺浅灰底色（以真实今天为界，非 minimumDate）
        cal_pop.set_past_overlay_date(QDate.currentDate())
        # 开始日期用白色虚线框标记
        cal_pop.set_marker_date(self.current_date)
        target_date = self.current_date.addDays(self._end_day_offset)
        cal_pop.calendar.setSelectedDate(target_date)

        def on_date_selected(py_date):
            days_diff = self.current_date.daysTo(
                QDate(py_date.year, py_date.month, py_date.day)
            )
            self._end_day_offset = max(0, days_diff)
            self._update_end_date_label()

        cal_pop.date_selected.connect(on_date_selected)
        global_pos = self.lbl_end_date.mapToGlobal(QPoint(0, self.lbl_end_date.height()))
        cal_pop.show_at(global_pos)

    def eventFilter(self, watched, event):
        if (
            self._calendar_view is not None
            and watched is self._calendar_view.viewport()
            and self._selection_mode == "multiple"
        ):
            if (
                event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
            ):
                self._multi_drag_active = True
                self._multi_drag_happened = False
                self._multi_drag_last_date = None
                self._multi_press_date = self._calendar_date_at_cursor()
                return False
            if event.type() == QEvent.Type.MouseMove and self._multi_drag_active:
                if not self._multi_drag_happened:
                    self._multi_drag_happened = True
                    if self._multi_press_date is not None:
                        self._toggle_multi_date(self._multi_press_date)
                date = self._calendar_date_at_cursor()
                if date is not None:
                    self._toggle_multi_date(date)
                return False
            if (
                event.type() == QEvent.Type.MouseButtonRelease
                and event.button() == Qt.MouseButton.LeftButton
                and self._multi_drag_active
            ):
                self._suppress_next_calendar_click = self._multi_drag_happened
                self._multi_drag_active = False
                self._multi_drag_last_date = None
                self._multi_press_date = None
                return False
        if (
            hasattr(self, "lbl_end_date")
            and watched is self.lbl_end_date
            and event.type() == QEvent.Type.MouseButtonDblClick
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._show_end_date_calendar()
            return True
        return super().eventFilter(watched, event)

    def _calendar_date_at_cursor(self):
        viewport_position = self._calendar_view.viewport().mapFromGlobal(QCursor.pos())
        row = self._calendar_view.rowAt(viewport_position.y()) - 1
        column = self._calendar_view.columnAt(viewport_position.x())
        if row < 0 or column < 0:
            return None

        first_date = QDate(self.calendar.yearShown(), self.calendar.monthShown(), 1)
        first_weekday = int(self.calendar.firstDayOfWeek().value)
        leading_days = (first_date.dayOfWeek() - first_weekday) % 7
        date = first_date.addDays(row * 7 + column - leading_days)
        if date < self.calendar.minimumDate() or date > self.calendar.maximumDate():
            return None
        return date

    def _toggle_multi_date(self, date):
        py_date = date.toPyDate()
        if py_date == self._multi_drag_last_date:
            return
        self._multi_drag_last_date = py_date
        if py_date in self._selected_dates:
            self._selected_dates.remove(py_date)
        else:
            self._selected_dates.add(py_date)
        self.current_date = date
        self._update_end_date_label()
        self.calendar.set_multi_selection(True, self._selected_dates)

    def _validate_scroll_time(self):
        now = datetime.now()
        if self.current_date == QDate.currentDate() and self._end_day_offset == 0:
            curr_h, curr_m = now.hour, now.minute

            def check(sh, sm):
                try:
                    vh, vm = int(sh.get_value()), int(sm.get_value())
                    if vh < curr_h:
                        sh.set_value(f"{curr_h:02d}")
                        if int(sm.get_value()) < curr_m: sm.set_value(f"{curr_m:02d}")
                    elif vh == curr_h:
                        if vm < curr_m: sm.set_value(f"{curr_m:02d}")
                except: pass

            check(self.scroll_end_hour, self.scroll_end_min)
