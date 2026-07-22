# src/ui/time_picker.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QApplication, QPushButton, QCalendarWidget, QGridLayout,
                             QListWidget, QListWidgetItem, QScroller,
                             QFrame, QScrollArea, QSizePolicy, QTableView, QToolButton,
                             QStyle, QStyleOptionButton, QStyledItemDelegate, QToolTip,
                             QAbstractItemView)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, QRectF, QPoint, pyqtProperty, QSize, QEvent, QTimer
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QBrush, QPen, QIcon, QPalette, QPixmap, QTextCharFormat, QCursor
from PyQt6.QtSvg import QSvgRenderer
from datetime import datetime, timedelta
from ..config import AppConfig
from ..utils.styles import StyleManager
from .components import IOSSwitch, NumberScroller


EMBEDDED_CALENDAR_STYLE = "theme_80"


def _embedded_calendar_style_values(style_name):
    if style_name == "white_65":
        return 0.65, "#ffffff"
    return 0.80, AppConfig.COLOR_GRADIENT_START


class WeekdayHeaderDelegate(QStyledItemDelegate):
    def __init__(self, base_delegate, background, vertical_offset, parent=None):
        super().__init__(parent)
        self._base_delegate = base_delegate
        self._background = QColor(background)
        self._vertical_offset = int(vertical_offset)

    def paint(self, painter, option, index):
        if index.row() == 0:
            painter.save()
            painter.fillRect(
                option.rect.translated(0, self._vertical_offset),
                self._background,
            )
            painter.restore()
        self._base_delegate.paint(painter, option, index)

    def sizeHint(self, option, index):
        return self._base_delegate.sizeHint(option, index)


class ThemePerforationSeparator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(10)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

    def _background_color(self):
        window = self.window()
        gradient_height = max(1, window.height())
        if getattr(window, "_day_collapsed", False):
            gradient_height = max(
                gradient_height,
                int(getattr(window, "_day_expanded_height", gradient_height)),
            )
        center_y = self.mapTo(window, QPoint(0, self.height() // 2)).y()
        ratio = max(0.0, min(center_y / gradient_height, 1.0))
        start = QColor(AppConfig.COLOR_GRADIENT_START)
        end = QColor(AppConfig.COLOR_GRADIENT_END)
        inverse = 1.0 - ratio
        return QColor(
            round(start.red() * inverse + end.red() * ratio),
            round(start.green() * inverse + end.green() * ratio),
            round(start.blue() * inverse + end.blue() * ratio),
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._background_color())

        diameter = 5.0
        radius = diameter / 2.0
        span = max(1.0, float(self.width() - 1))
        count = max(2, round(span / 8.0) + 1)
        step = span / (count - 1)
        center_y = self.height() / 2.0
        for index in range(count):
            center_x = index * step
            painter.drawEllipse(QRectF(
                center_x - radius,
                center_y - radius,
                diameter,
                diameter,
            ))


class SelectionModeLabel(QLabel):
    clicked = pyqtSignal()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)


#  主视图 (TimePickerView)
# =================================================================
class TimePickerView(QWidget):
    back_requested = pyqtSignal() 
    suspend_requested = pyqtSignal()
    confirm_requested = pyqtSignal(object, object) 
    multiple_confirm_requested = pyqtSignal(object)
    selection_mode_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_date = QDate.currentDate()
        self.drag_pos = None
        self._end_day_offset = 0
        self._prev_end_hour = None
        self._embedded_calendar_style = EMBEDDED_CALENDAR_STYLE
        self._selection_mode = "single"
        self._selected_dates = set()
        self._multi_drag_active = False
        self._multi_drag_last_date = None
        self._multi_press_date = None
        self._multi_drag_happened = False
        self._suppress_next_calendar_click = False
        self._calendar_view = None
        self._calendar_style_switch_enabled = self.__class__ is TimePickerView
        self._date_icon_double_click_active = False
        self._date_icon_single_click_timer = QTimer(self)
        self._date_icon_single_click_timer.setSingleShot(True)
        self._date_icon_single_click_timer.timeout.connect(self._toggle_calendar)

        self._setup_ui()
        self._connect_signals()
        QTimer.singleShot(0, self._position_selection_mode_button)

        self._update_date_label()
        now = QTime.currentTime()
        self.scroll_end_hour.set_value(f"{now.hour():02d}")
        self.scroll_end_min.set_value(f"{now.minute():02d}")
        self._prev_end_hour = int(self.scroll_end_hour.get_value())
        self._update_end_date_label()

    def _get_colored_icon(self, icon_path, color_hex):
        """工具方法：将 SVG 动态渲染为指定颜色"""
        renderer = QSvgRenderer(icon_path)
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), QColor(color_hex))
        painter.end()
        return QIcon(pixmap)

    def _setup_ui(self):
        (
            self._calendar_surface_alpha,
            self._calendar_foreground_color,
        ) = _embedded_calendar_style_values(self._embedded_calendar_style)

        # 1. 主布局
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # 2. 标题栏
        header_container = QWidget()
        self.header_container = header_container
        header_container.setFixedHeight(70)
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(30, 10, 30, 0)
        header_layout.setSpacing(0)
        self.lbl_title = QLabel("设置时间")
        self.lbl_title.setStyleSheet("color: white; font-size: 24px; font-weight: bold; font-family: 'Microsoft YaHei';")
        header_layout.addWidget(self.lbl_title)
        self.btn_selection_mode = SelectionModeLabel(header_container)
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
        self.btn_selection_mode.setVisible(self.__class__ is TimePickerView)
        header_layout.addStretch()
        outer_layout.addWidget(header_container)

        # 3. 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("QScrollArea { background: transparent; border: none; } QWidget { background: transparent; }")
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 10, 20, 30)
        self.content_layout.setSpacing(20)

        self.scroll_area.setWidget(self.content_widget)
        outer_layout.addWidget(self.scroll_area)

        # --- 内容 ---

        # 4. 日期按钮
        self.date_calendar_container = QFrame()
        self.date_calendar_container.setObjectName("DateCalendarContainer")
        self.date_calendar_container.setStyleSheet("""
            QFrame#DateCalendarContainer {
                background-color: transparent;
                border: none;
            }
        """)
        self.date_calendar_layout = QVBoxLayout(self.date_calendar_container)
        self.date_calendar_layout.setContentsMargins(0, 0, 0, 0)
        self.date_calendar_layout.setSpacing(0)

        self.btn_date = QPushButton()
        self.btn_date.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_date.setFixedHeight(45)
        # 在这里设置日历 SVG 图标
        self.btn_date.setIcon(self._get_colored_icon(
            "assets/icons/calendar.svg",
            self._calendar_foreground_color,
        ))
        self.btn_date.setIconSize(QSize(20, 20))
        self.date_calendar_layout.addWidget(self.btn_date)

        # 5. 日历控件（暗色模式：深色背景 + 白色工作日 + 红色周末）
        from .calendar_pop import HighlightCalendarWidget, _make_arrow_icon
        self.calendar = HighlightCalendarWidget(
            self, export_theme=False, schedule_markers=False,
            dark_mode=True, embedded_calendar=True,
            embedded_foreground_color=self._calendar_foreground_color,
        )
        self.calendar.setGridVisible(False)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.setNavigationBarVisible(True)
        self.calendar.setMinimumDate(QDate.currentDate())

        weekday_format = QTextCharFormat()
        weekday_format.setForeground(QColor(self._calendar_foreground_color))
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
        weekday_header_color = QColor(StyleManager.mix_colors(
            AppConfig.COLOR_GRADIENT_START,
            "#ffffff",
            0.40,
        ))
        self.calendar.setStyleSheet(f"""
            QCalendarWidget {{
                background-color: transparent;
                border: none;
            }}
            QCalendarWidget QWidget {{
                background-color: transparent;
                alternate-background-color: transparent;
                color: white;
            }}
            QCalendarWidget QAbstractItemView {{
                background-color: transparent;
                alternate-background-color: transparent;
                border: none;
                outline: 0;
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background-color: transparent;
            }}
            QCalendarWidget QToolButton {{
                color: #333333; background-color: transparent; border: none;
                border-radius: 4px; padding: 4px; font-weight: bold;
            }}
            QCalendarWidget QToolButton#qt_calendar_monthbutton,
            QCalendarWidget QToolButton#qt_calendar_yearbutton {{
                color: {self._calendar_foreground_color};
            }}
            QCalendarWidget QToolButton:disabled {{
                color: #cccccc;
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: rgba(0, 0, 0, 0.06);
            }}
            QCalendarWidget QToolButton::menu-indicator {{ image: none; }}
            QCalendarWidget QSpinBox {{
                background-color: transparent; color: white; border: none;
                font-weight: bold; padding-right: 10px;
            }}
            QCalendarWidget QSpinBox QLineEdit {{
                color: white; background: transparent; border: none;
            }}
            QCalendarWidget QHeaderView::section {{
                background-color: transparent;
                color: {self._calendar_foreground_color};
                border: none; padding: 4px; font-weight: bold;
            }}
            QCalendarWidget QMenu {{
                background-color: #2b2b2b; color: white;
                border: 1px solid rgba(255,255,255,0.15);
            }}
        """)
        if self.__class__ is TimePickerView:
            calendar_view = self.calendar.findChild(
                QTableView,
                "qt_calendar_calendarview",
            )
            if calendar_view is not None:
                self._calendar_view = calendar_view
                calendar_view.viewport().setMouseTracking(True)
                calendar_view.viewport().installEventFilter(self)
                self._weekday_header_delegate = WeekdayHeaderDelegate(
                    calendar_view.itemDelegate(),
                    weekday_header_color,
                    -3,
                    calendar_view,
                )
                calendar_view.setItemDelegate(self._weekday_header_delegate)
        self.calendar.setAutoFillBackground(False)

        self.calendar_background = QFrame()
        self.calendar_background.setObjectName("CalendarBackground")
        self.calendar_background.setStyleSheet(f"""
            QFrame#CalendarBackground {{
                background-color: rgba(255, 255, 255, {self._calendar_surface_alpha:.2f});
                border-top: none;
                border-left: 1px solid rgba(255, 255, 255, 0.5);
                border-right: 1px solid rgba(255, 255, 255, 0.5);
                border-bottom: 1px solid rgba(255, 255, 255, 0.5);
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
        """)
        calendar_layout = QVBoxLayout(self.calendar_background)
        calendar_layout.setContentsMargins(0, 5, 0, 7)
        calendar_layout.setSpacing(0)
        calendar_layout.addWidget(self.calendar)
        self.date_calendar_layout.addWidget(self.calendar_background)
        self.content_layout.addWidget(self.date_calendar_container)
        self._apply_date_button_style(expanded=True)

        self.calendar_perforation = ThemePerforationSeparator(self.date_calendar_container)
        self.date_calendar_container.installEventFilter(self)
        self._position_calendar_perforation()

        prev_btn = self.calendar.findChild(QToolButton, "qt_calendar_prevmonth")
        if prev_btn:
            prev_btn.setIcon(_make_arrow_icon(
                "assets/icons/cal_left.svg",
                enabled_color=self._calendar_foreground_color,
                disabled_color="#bbbbbb",
            ))
            prev_btn.setIconSize(QSize(18, 18))

        next_btn = self.calendar.findChild(QToolButton, "qt_calendar_nextmonth")
        if next_btn:
            next_btn.setIcon(_make_arrow_icon(
                "assets/icons/cal_right.svg",
                enabled_color=self._calendar_foreground_color,
                disabled_color="#bbbbbb",
            ))
            next_btn.setIconSize(QSize(18, 18))

        # 6. 开关行
        switch_row = QHBoxLayout()
        lbl_switch = QLabel("启用开始时间")
        lbl_switch.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 15px; font-weight: bold;")
        self.chk_enable_start = IOSSwitch()
        switch_row.addWidget(lbl_switch)
        switch_row.addStretch()
        switch_row.addWidget(self.chk_enable_start)
        self.content_layout.addLayout(switch_row)

        # 7. 时间选择区域
        self.time_picker_container = QWidget()
        self.time_picker_container.setStyleSheet("""
            QWidget#TimeContainer {
                background-color: transparent;
                border-radius: 8px;
            }
        """)
        self.time_picker_container.setObjectName("TimeContainer")
        
        h_layout = QHBoxLayout(self.time_picker_container)
        h_layout.setContentsMargins(5, 15, 5, 15)
        h_layout.setSpacing(2)

        # --> 左侧：开始时间
        self.start_group = QWidget()
        v_start = QVBoxLayout(self.start_group)
        v_start.setContentsMargins(0,0,0,0)
        self.lbl_start = QLabel("开始")
        self.lbl_start.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_start.setStyleSheet("color: rgba(255,255,255,0.75); font-size: 12px; font-weight: bold; margin-bottom: 5px;")
        
        self.start_scroller_widget, self.scroll_start_hour, self.scroll_start_min = self._create_single_time_scroller()
        v_start.addWidget(self.lbl_start)
        v_start.addWidget(self.start_scroller_widget)
        
        # --> 右侧：完成时间
        self.end_group = QWidget()
        v_end = QVBoxLayout(self.end_group)
        v_end.setContentsMargins(0,0,0,0)

        end_label_row = QHBoxLayout()
        end_label_row.setContentsMargins(0, 0, 0, 0)
        end_label_row.setSpacing(0)
        end_label_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_end = QLabel("完成时间")
        self.lbl_end.setStyleSheet("color: rgba(255,255,255,0.75); font-size: 12px; font-weight: bold; margin-bottom: 5px; margin-left: 6px;")
        self.lbl_end_date = QLabel("（今）")
        self.lbl_end_date.setStyleSheet(
            "color: rgba(255,255,255,0.85); font-size: 12px; margin-bottom: 5px; "
            "font-weight: bold;"
        )
        self.lbl_end_date.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_end_date.setToolTip("双击切换完成日期")
        self.lbl_end_date.installEventFilter(self)
        end_label_row.addStretch()
        end_label_row.addWidget(self.lbl_end)
        end_label_row.addWidget(self.lbl_end_date)
        end_label_row.addStretch()
        v_end.addLayout(end_label_row)

        self.end_scroller_widget, self.scroll_end_hour, self.scroll_end_min = self._create_single_time_scroller()
        v_end.addWidget(self.end_scroller_widget)

        h_layout.addWidget(self.start_group)
        h_layout.addWidget(self.end_group)
        
        h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.start_group.hide()
        self.lbl_end_date.hide()  # DDL 模式默认不需要日期偏移标签

        self.content_layout.addWidget(self.time_picker_container)

        # 8. 时长快捷按钮
        self.duration_grid = QWidget()
        grid = QGridLayout(self.duration_grid)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(10)
        
        durations = [
            (10, "10分钟"), (15, "15分钟"), (30, "30分钟"), (45, "45分钟"),
            (60, "1小时"), (90, "1.5小时"), (120, "2小时"), (180, "3小时")
        ]
        
        row, col = 0, 0
        for mins, text in durations:
            btn = QPushButton(text)
            btn.setFixedHeight(32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("minutes", mins)
            btn.clicked.connect(lambda _, b=btn: self._on_quick_set(b))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.15); 
                    border-radius: 8px;
                    color: white; 
                    border: 1px solid rgba(255,255,255,0.2);
                    font-size: 12px;
                }
                QPushButton:hover { background-color: rgba(255, 255, 255, 0.3); border-color: white;}
            """)
            grid.addWidget(btn, row, col)
            
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        self.duration_grid.hide() 
        self.content_layout.addWidget(self.duration_grid)

        self.content_layout.addStretch()

        # 9. 底部按钮
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(30, 10, 30, 20)
        btn_layout.setSpacing(20)

        self.btn_cancel = QPushButton("取消")
        self.btn_ok = QPushButton("确定")
        
        for btn in [self.btn_cancel, self.btn_ok]:
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: transparent; border: 1px solid rgba(255,255,255,0.6);
                border-radius: 20px; color: white; font-size: 14px;
            }
            QPushButton:hover { background-color: rgba(255,255,255,0.1); }
        """)
        
        self.btn_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: white; border: none;
                border-radius: 20px; color: {AppConfig.COLOR_GRADIENT_START}; font-weight: bold; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: #f0f0f0; }}
        """)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_ok)
        outer_layout.addWidget(btn_container)
        self._setup_window_controls()

    def set_title(self, text="设置时间"):
        """动态修改时间页面的标题，并根据字数自动调整字体大小"""
        self.lbl_title.setText(text)
        
        # 智能判断字数：超过4个字说明是“修改XX时间”模式，缩小字号
        if len(text) > 4:
            self.lbl_title.setStyleSheet("color: white; font-size: 17px; font-weight: bold; font-family: 'Microsoft YaHei';")
        else:
            self.lbl_title.setStyleSheet("color: white; font-size: 24px; font-weight: bold; font-family: 'Microsoft YaHei';")
        QTimer.singleShot(0, self._position_selection_mode_button)

    def _position_selection_mode_button(self):
        if (
            not hasattr(self, "btn_selection_mode")
            or self.btn_selection_mode.isHidden()
        ):
            return

        title_rect = self.lbl_title.geometry()
        title_metrics = self.lbl_title.fontMetrics()
        button_metrics = self.btn_selection_mode.fontMetrics()
        title_baseline = (
            title_rect.y()
            + (title_rect.height() - title_metrics.height()) // 2
            + title_metrics.ascent()
        )
        button_baseline_offset = (
            (self.btn_selection_mode.height() - button_metrics.height()) // 2
            + button_metrics.ascent()
        )
        button_x = (
            title_rect.x()
            + title_metrics.horizontalAdvance(self.lbl_title.text())
            + 4
        )
        button_y = title_baseline - button_baseline_offset
        self.btn_selection_mode.move(button_x, button_y)
        self.btn_selection_mode.raise_()

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

        mode_text = "多选" if self._selection_mode == "multiple" else "单选"
        self.btn_selection_mode.setText(self._selection_mode_text(mode_text))
        if self._selection_mode == "single":
            self.calendar.setSelectedDate(self.current_date)
        if self._calendar_view is not None:
            if self._selection_mode == "multiple":
                self._calendar_view.setSelectionMode(
                    QAbstractItemView.SelectionMode.NoSelection
                )
                self._calendar_view.clearSelection()
            else:
                self._calendar_view.setSelectionMode(
                    QAbstractItemView.SelectionMode.SingleSelection
                )
        self.calendar.set_multi_selection(
            self._selection_mode == "multiple",
            self._selected_dates,
        )
        self.selection_mode_changed.emit(self._selection_mode)

    def set_selection_mode_available(self, available):
        available = bool(available) and self.__class__ is TimePickerView
        if not available:
            self.set_selection_mode("single", [])
        self.btn_selection_mode.setVisible(available)
        QTimer.singleShot(0, self._position_selection_mode_button)

    def set_multiple_ranges(self, ranges):
        dates = []
        for start, end in ranges or []:
            target = start or end
            if target is not None:
                dates.append(target.date())
        if dates:
            first = min(dates)
            self.current_date = QDate(first.year, first.month, first.day)
            self.calendar.setSelectedDate(self.current_date)
            self._update_date_label()
            self._update_end_date_label()
            self.set_selection_mode("multiple", dates)

    @staticmethod
    def _selection_mode_text(mode_text):
        return f'（<span style="color: #ffffff;">{mode_text}</span>）'

    def _create_single_time_scroller(self):
        """创建一个单独的 [时 : 分] 滚轮组"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2) 
        
        hours = [f"{i:02d}" for i in range(24)]
        scroll_h = NumberScroller(hours)
        
        mins = [f"{i:02d}" for i in range(60)]
        scroll_m = NumberScroller(mins)
        
        lbl_colon = QLabel(":")
        lbl_colon.setFixedWidth(10) # 限制冒号宽度
        lbl_colon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_colon.setStyleSheet("color: white; font-size: 20px; font-weight: bold; padding-bottom: 5px;")
        
        layout.addWidget(scroll_h)
        layout.addWidget(lbl_colon)
        layout.addWidget(scroll_m)
        
        return widget, scroll_h, scroll_m

    # --- 逻辑处理 ---

    def set_initial_data(self, start_dt, end_dt):
        """显式控制界面显隐，防止状态残留"""
        target_dt = end_dt if end_dt else datetime.now()
        self._end_day_offset = 0
        if start_dt and end_dt:
            start_date = start_dt.date()
            end_date = end_dt.date()
            offset_days = (end_date - start_date).days
            if offset_days > 0:
                self._end_day_offset = offset_days
                self.current_date = QDate(start_date.year, start_date.month, start_date.day)
            else:
                self.current_date = QDate(target_dt.year, target_dt.month, target_dt.day)
        else:
            self.current_date = QDate(target_dt.year, target_dt.month, target_dt.day)
        self._prev_end_hour = target_dt.hour
        self.set_selection_mode("single", [])
        self._update_date_label()
        self._update_end_date_label()
        self.calendar.setSelectedDate(self.current_date)

        self.scroll_end_hour.set_value(f"{target_dt.hour:02d}")
        self.scroll_end_min.set_value(f"{target_dt.minute:02d}")

        if start_dt:
            self.chk_enable_start.setChecked(True)
            self.scroll_start_hour.set_value(f"{start_dt.hour:02d}")
            self.scroll_start_min.set_value(f"{start_dt.minute:02d}")
            self._set_dual_time_group_layout(True)

            # 显式显示 (因为 setChecked 不发信号)
            self.start_group.show()
            self.duration_grid.show()
            self.lbl_end_date.show()
            self.lbl_start.setText("开始")
            self.lbl_end.setText("完成")
        else:
            self.chk_enable_start.setChecked(False)
            self._set_dual_time_group_layout(False)

            # 显式隐藏 (这是修复 Bug 的核心)
            self.start_group.hide()
            self.duration_grid.hide()
            self.lbl_end_date.hide()
            self.lbl_start.setText("开始时间")
            self.lbl_end.setText("完成时间")

    def _connect_signals(self):
        if self._calendar_style_switch_enabled:
            self.btn_date.installEventFilter(self)
        self.btn_selection_mode.clicked.connect(self._toggle_selection_mode)
        self.btn_date.clicked.connect(self._toggle_calendar)
        self.calendar.clicked.connect(self._on_date_selected)
        # 结束时间转轮
        self.scroll_end_hour.value_changed.connect(self._on_end_hour_changed)
        self.scroll_end_hour.value_changed.connect(self._validate_scroll_time)
        self.scroll_end_min.value_changed.connect(self._validate_scroll_time)
        # 开始时间转轮
        self.scroll_start_hour.value_changed.connect(self._validate_scroll_time)
        self.scroll_start_min.value_changed.connect(self._validate_scroll_time)
        # --- 结束 ---
        self.chk_enable_start.toggled.connect(self._on_switch_toggled)
        self.btn_cancel.clicked.connect(self.back_requested.emit)
        self.btn_ok.clicked.connect(self._on_confirm)

    def _toggle_calendar(self):
        expanded = self.calendar_background.isHidden()
        self.calendar_background.setVisible(expanded)
        self.calendar_perforation.setVisible(expanded)
        self._apply_date_button_style(expanded=expanded)
        self.date_calendar_container.updateGeometry()
        self.content_widget.updateGeometry()
        self._position_calendar_perforation()

    def _position_calendar_perforation(self):
        if not hasattr(self, "calendar_perforation"):
            return
        separator_height = self.calendar_perforation.height()
        seam_y = self.btn_date.geometry().bottom() + 1
        self.calendar_perforation.setGeometry(
            0,
            seam_y - separator_height // 2,
            self.date_calendar_container.width(),
            separator_height,
        )
        self.calendar_perforation.raise_()
        self.calendar_perforation.update()

    def _date_button_icon_rect(self):
        option = QStyleOptionButton()
        self.btn_date.initStyleOption(option)
        contents = self.btn_date.style().subElementRect(
            QStyle.SubElement.SE_PushButtonContents,
            option,
            self.btn_date,
        )
        icon_size = option.iconSize
        text_width = option.fontMetrics.horizontalAdvance(option.text)
        spacing = 4 if option.text else 0
        content_width = icon_size.width() + spacing + text_width
        icon_x = contents.x() + max(0, (contents.width() - content_width) // 2)
        icon_y = contents.y() + (contents.height() - icon_size.height()) // 2
        return QRect(icon_x, icon_y, icon_size.width(), icon_size.height()).adjusted(
            -3, -3, 3, 3
        )

    def _switch_embedded_calendar_style(self):
        style_name = (
            "white_65"
            if self._embedded_calendar_style == "theme_80"
            else "theme_80"
        )
        self._apply_embedded_calendar_style(style_name)

    def _apply_embedded_calendar_style(self, style_name):
        from .calendar_pop import _make_arrow_icon

        previous_foreground = self._calendar_foreground_color
        self._embedded_calendar_style = style_name
        (
            self._calendar_surface_alpha,
            self._calendar_foreground_color,
        ) = _embedded_calendar_style_values(style_name)

        self.btn_date.setIcon(self._get_colored_icon(
            "assets/icons/calendar.svg",
            self._calendar_foreground_color,
        ))
        self.calendar._embedded_foreground_color = QColor(
            self._calendar_foreground_color
        )

        weekday_format = QTextCharFormat()
        weekday_format.setForeground(QColor(self._calendar_foreground_color))
        for weekday in (
            Qt.DayOfWeek.Monday,
            Qt.DayOfWeek.Tuesday,
            Qt.DayOfWeek.Wednesday,
            Qt.DayOfWeek.Thursday,
            Qt.DayOfWeek.Friday,
        ):
            self.calendar.setWeekdayTextFormat(weekday, weekday_format)

        calendar_style = self.calendar.styleSheet().replace(
            previous_foreground,
            self._calendar_foreground_color,
        )
        self.calendar.setStyleSheet(calendar_style)
        self.calendar_background.setStyleSheet(f"""
            QFrame#CalendarBackground {{
                background-color: rgba(255, 255, 255, {self._calendar_surface_alpha:.2f});
                border-top: none;
                border-left: 1px solid rgba(255, 255, 255, 0.5);
                border-right: 1px solid rgba(255, 255, 255, 0.5);
                border-bottom: 1px solid rgba(255, 255, 255, 0.5);
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
        """)

        prev_btn = self.calendar.findChild(QToolButton, "qt_calendar_prevmonth")
        if prev_btn:
            prev_btn.setIcon(_make_arrow_icon(
                "assets/icons/cal_left.svg",
                enabled_color=self._calendar_foreground_color,
                disabled_color="#bbbbbb",
            ))
        next_btn = self.calendar.findChild(QToolButton, "qt_calendar_nextmonth")
        if next_btn:
            next_btn.setIcon(_make_arrow_icon(
                "assets/icons/cal_right.svg",
                enabled_color=self._calendar_foreground_color,
                disabled_color="#bbbbbb",
            ))

        self._apply_date_button_style(
            expanded=not self.calendar_background.isHidden()
        )
        self.calendar.updateCells()

    def _apply_date_button_style(self, expanded):
        bottom_radius = 0 if expanded else 8
        bottom_border = "none" if expanded else "1px solid rgba(255, 255, 255, 0.5)"
        hover_alpha = min(1.0, self._calendar_surface_alpha + 0.08)
        self.btn_date.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, {self._calendar_surface_alpha:.2f});
                border-top: 1px solid rgba(255, 255, 255, 0.5);
                border-left: 1px solid rgba(255, 255, 255, 0.5);
                border-right: 1px solid rgba(255, 255, 255, 0.5);
                border-bottom: {bottom_border};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom-left-radius: {bottom_radius}px;
                border-bottom-right-radius: {bottom_radius}px;
                color: {self._calendar_foreground_color};
                font-size: 16px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, {hover_alpha:.2f});
            }}
        """)

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
        self._update_date_label()
        self._update_end_date_label()

    def _update_date_label(self):
        text = self.current_date.toString("yyyy年MM月dd日")
        self.btn_date.setText("    " + text)

    def _set_dual_time_group_layout(self, enabled):
        maximum_width = 124 if enabled else 16777215
        self.start_group.setMaximumWidth(maximum_width)
        self.end_group.setMaximumWidth(maximum_width)
        self.time_picker_container.layout().invalidate()
        self.time_picker_container.updateGeometry()

    def _on_switch_toggled(self, checked):
        self._set_dual_time_group_layout(checked)
        if checked:
            self.start_group.show()
            self.duration_grid.show()
            self.lbl_end_date.show()
            self.lbl_start.setText("开始")
            self.lbl_end.setText("完成")
            end_h = int(self.scroll_end_hour.get_value())
            end_m = int(self.scroll_end_min.get_value())
            dt_end = datetime(2024, 1, 1, end_h, end_m)
            dt_start = dt_end - timedelta(hours=1)
            self.scroll_start_hour.set_value(f"{dt_start.hour:02d}")
            self.scroll_start_min.set_value(f"{dt_start.minute:02d}")
            # 滚回顶部避免日历头部被裁
            self.scroll_area.verticalScrollBar().setValue(0)
        else:
            self.start_group.hide()
            self.duration_grid.hide()
            self.lbl_end_date.hide()
            self.lbl_start.setText("开始时间")
            self.lbl_end.setText("完成时间")

    def _on_quick_set(self, btn):
        mins = btn.property("minutes")
        end_h = int(self.scroll_end_hour.get_value())
        end_m = int(self.scroll_end_min.get_value())
        dt_end = datetime(2024,1,1, end_h, end_m)
        dt_start = dt_end - timedelta(minutes=mins)
        self.scroll_start_hour.set_value(f"{dt_start.hour:02d}")
        self.scroll_start_min.set_value(f"{dt_start.minute:02d}")

    def _on_end_hour_changed(self):
        """检测小时滚轮 00↔23 跨越，推断跨天方向。"""
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
        # 自适应字号：超过 8 个字时缩小
        if len(text) > 8:
            self.lbl_end_date.setStyleSheet(
                "color: rgba(255,255,255,0.85); font-size: 10px; margin-bottom: 5px; "
                "font-weight: bold;"
            )
        else:
            self.lbl_end_date.setStyleSheet(
                "color: rgba(255,255,255,0.85); font-size: 12px; margin-bottom: 5px; "
                "font-weight: bold;"
            )

    def _show_end_date_calendar(self):
        """双击日期标签弹出暗色日历选择完成日期。"""
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
            elif event.type() == QEvent.Type.MouseMove and self._multi_drag_active:
                if not self._multi_drag_happened:
                    self._multi_drag_happened = True
                    if self._multi_press_date is not None:
                        self._toggle_multi_date(self._multi_press_date)
                date = self._calendar_date_at_cursor()
                if date is not None:
                    self._toggle_multi_date(date)
                return False
            elif (
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
            watched is self.btn_date
            and self._calendar_style_switch_enabled
            and event.type() in (
                QEvent.Type.MouseButtonPress,
                QEvent.Type.MouseButtonRelease,
                QEvent.Type.MouseButtonDblClick,
            )
            and event.button() == Qt.MouseButton.LeftButton
        ):
            icon_hit = self._date_button_icon_rect().contains(
                event.position().toPoint()
            )
            if event.type() == QEvent.Type.MouseButtonDblClick and icon_hit:
                self._date_icon_single_click_timer.stop()
                self._date_icon_double_click_active = True
                self._switch_embedded_calendar_style()
                return True
            if event.type() == QEvent.Type.MouseButtonPress and icon_hit:
                return True
            if (
                event.type() == QEvent.Type.MouseButtonRelease
                and (icon_hit or self._date_icon_double_click_active)
            ):
                if self._date_icon_double_click_active:
                    self._date_icon_double_click_active = False
                else:
                    app = QApplication.instance()
                    interval = (
                        app.styleHints().mouseDoubleClickInterval()
                        if app is not None
                        else 400
                    )
                    self._date_icon_single_click_timer.start(interval)
                return True
        if (
            watched is self.date_calendar_container
            and event.type() == QEvent.Type.Resize
        ):
            self._position_calendar_perforation()
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
        self._update_date_label()
        self._update_end_date_label()
        self.calendar.set_multi_selection(True, self._selected_dates)

    def _time_range_for_date(self, base_date):
        end_h = int(self.scroll_end_hour.get_value())
        end_m = int(self.scroll_end_min.get_value())
        day_offset = self._end_day_offset

        dt_start = None
        if self.chk_enable_start.isChecked():
            start_h = int(self.scroll_start_hour.get_value())
            start_m = int(self.scroll_start_min.get_value())
            dt_start = datetime(
                base_date.year(), base_date.month(), base_date.day(), start_h, start_m
            )

        end_date = base_date.addDays(day_offset)
        dt_end = datetime(end_date.year(), end_date.month(), end_date.day(), end_h, end_m)
        if dt_start is not None and dt_end <= dt_start:
            end_date = base_date.addDays(day_offset + 1)
            dt_end = datetime(end_date.year(), end_date.month(), end_date.day(), end_h, end_m)
        return dt_start, dt_end

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
                dt_start, dt_end = self._time_range_for_date(base_date)
                if dt_end < now:
                    print("❌ 结束时间不能早于当前时间")
                    return
                ranges.append((dt_start, dt_end))
            self.multiple_confirm_requested.emit(ranges)
            return

        end_h = int(self.scroll_end_hour.get_value())
        end_m = int(self.scroll_end_min.get_value())
        end_date = self.current_date.addDays(self._end_day_offset)
        dt_end = datetime(end_date.year(), end_date.month(), end_date.day(), end_h, end_m)

        dt_start = None
        if self.chk_enable_start.isChecked():
            start_h = int(self.scroll_start_hour.get_value())
            start_m = int(self.scroll_start_min.get_value())
            dt_start = datetime(self.current_date.year(), self.current_date.month(), self.current_date.day(), start_h, start_m)
            # 修正：若开始时间晚于完成时间（如 23:00→01:00 次日），
            # 且未通过 day_offset 处理，则将完成推到下一天
            if dt_start is not None and dt_end <= dt_start:
                self._end_day_offset += 1
                end_date = self.current_date.addDays(self._end_day_offset)
                dt_end = datetime(end_date.year(), end_date.month(), end_date.day(), end_h, end_m)

        now = datetime.now()
        if dt_end < now:
            print("❌ 结束时间不能早于当前时间")
            return
        self.confirm_requested.emit(dt_start, dt_end)

    def _setup_window_controls(self):
        """使用绝对定位在页面上方悬浮生成挂起和关闭按钮"""
        from PyQt6.QtWidgets import QPushButton, QToolButton
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        from ..utils.styles import StyleManager

        # 1. 挂起按钮 绝对定位居中
        self.btn_suspend = QPushButton(self)
        self.btn_suspend.setFixedSize(30, 30)
        self.btn_suspend.setIcon(QIcon("assets/icons/hang_up.png"))
        self.btn_suspend.setIconSize(QSize(20, 20))
        self.btn_suspend.setStyleSheet("QPushButton { background: transparent; border: none; }")
        self.btn_suspend.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_suspend.clicked.connect(self.suspend_requested.emit)

        # 2. 关闭按钮 绝对定位右上角
        self.btn_close = QToolButton(self)
        self.btn_close.setIcon(QIcon("assets/icons/close.png"))
        self.btn_close.setIconSize(QSize(16, 16))
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setStyleSheet(StyleManager.get_window_control_style(is_close=True))
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        # 直接调用最顶层窗口的关闭事件
        self.btn_close.clicked.connect(lambda: self.window().close())

    def resizeEvent(self, event):
        """当窗口大小变化时，自动吸附按钮到顶部边缘"""
        super().resizeEvent(event)
        if hasattr(self, 'btn_suspend'):
            self.btn_suspend.move((self.width() - 30) // 2, 0)
            self.btn_suspend.raise_() # 确保在最上层，防止被遮挡
        if hasattr(self, 'btn_close'):
            self.btn_close.move(self.width() - 30, 0)
            self.btn_close.raise_()
        self._position_selection_mode_button()
        self._position_calendar_perforation()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.window().pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos:
            self.window().move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def _validate_scroll_time(self):
        now = datetime.now()
        selected_qdate = self.current_date
        today_qdate = QDate.currentDate()

        # 完成时间在将来某天（offset>0），不受”今天”限制
        end_qdate = selected_qdate.addDays(self._end_day_offset)

        # 只有完成日期是”今天”时才需要限制
        if selected_qdate == today_qdate and self._end_day_offset == 0:
            curr_h = now.hour
            curr_m = now.minute

            # 定义一个内部函数来处理单组转轮
            def check_scroller(scroll_h, scroll_m):
                try:
                    val_h = int(scroll_h.get_value())
                    val_m = int(scroll_m.get_value())
                    
                    # 1. 检查小时
                    if val_h < curr_h:
                        # 强制回弹到当前小时
                        scroll_h.set_value(f"{curr_h:02d}")
                        # 此时分钟也必须检查，防止回弹后分钟依然非法
                        if val_m < curr_m:
                            scroll_m.set_value(f"{curr_m:02d}")
                            
                    # 2. 如果小时也是当前小时，检查分钟
                    elif val_h == curr_h:
                        if val_m < curr_m:
                            # 强制回弹到当前分钟
                            scroll_m.set_value(f"{curr_m:02d}")
                except:
                    pass

            check_scroller(self.scroll_end_hour, self.scroll_end_min)
