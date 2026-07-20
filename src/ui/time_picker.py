# src/ui/time_picker.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QCalendarWidget, QGridLayout, 
                             QListWidget, QListWidgetItem, QScroller, 
                             QFrame, QScrollArea, QSizePolicy, QToolButton)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, QPoint, pyqtProperty, QSize, QEvent
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QBrush, QPen, QIcon, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from datetime import datetime, timedelta
from ..config import AppConfig
from ..utils.styles import StyleManager
from .components import IOSSwitch, NumberScroller


#  主视图 (TimePickerView)
# =================================================================
class TimePickerView(QWidget):
    back_requested = pyqtSignal() 
    suspend_requested = pyqtSignal()
    confirm_requested = pyqtSignal(object, object) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_date = QDate.currentDate()
        self.drag_pos = None
        self._end_day_offset = 0
        self._prev_end_hour = None

        self._setup_ui()
        self._connect_signals()

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
        # 1. 主布局
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # 2. 标题栏
        header_container = QWidget()
        header_container.setFixedHeight(70)
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(30, 10, 30, 0)
        self.lbl_title = QLabel("设置时间")
        self.lbl_title.setStyleSheet("color: white; font-size: 24px; font-weight: bold; font-family: 'Microsoft YaHei';")
        header_layout.addWidget(self.lbl_title)
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
        self.content_layout.setContentsMargins(20, 8, 20, 20)
        self.content_layout.setSpacing(12)

        self.scroll_area.setWidget(self.content_widget)
        outer_layout.addWidget(self.scroll_area)

        # --- 内容 ---

        # 4. 日期按钮
        self.btn_date = QPushButton()
        self.btn_date.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_date.setFixedHeight(45)
        # 在这里设置日历 SVG 图标
        self.btn_date.setIcon(self._get_colored_icon("assets/icons/calendar.svg", "#FFFFFF"))
        self.btn_date.setIconSize(QSize(20, 20))
        self.btn_date.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.18);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.28); }
        """)
        self.content_layout.addWidget(self.btn_date)

        # 5. 日历控件
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(False)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.setNavigationBarVisible(True)
        self.calendar.setStyleSheet(StyleManager.get_calendar_style())
        self.calendar.setMinimumDate(QDate.currentDate())
        self.content_layout.addWidget(self.calendar)

        # 箭头接近主题主色，混入少量白色保持原有轻微提亮效果。
        arrow_color = StyleManager.mix_colors(
            AppConfig.COLOR_GRADIENT_START,
            "#ffffff",
            primary_ratio=0.98,
        )
        prev_btn = self.calendar.findChild(QToolButton, "qt_calendar_prevmonth")
        if prev_btn:
            prev_btn.setIcon(self._get_colored_icon("assets/icons/cal_left.svg", arrow_color))
            prev_btn.setIconSize(QSize(18, 18))

        next_btn = self.calendar.findChild(QToolButton, "qt_calendar_nextmonth")
        if next_btn:
            next_btn.setIcon(self._get_colored_icon("assets/icons/cal_right.svg", arrow_color))
            next_btn.setIconSize(QSize(18, 18))

        # 6. 开关行
        switch_row = QHBoxLayout()
        lbl_switch = QLabel("启用开始时间")
        lbl_switch.setStyleSheet("color: white; font-size: 15px; font-weight: bold;")
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
        h_layout.setContentsMargins(5, 13, 5, 13)
        h_layout.setSpacing(10) 

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
        self._update_date_label()
        self._update_end_date_label()
        self.calendar.setSelectedDate(self.current_date)

        self.scroll_end_hour.set_value(f"{target_dt.hour:02d}")
        self.scroll_end_min.set_value(f"{target_dt.minute:02d}")

        if start_dt:
            self.chk_enable_start.setChecked(True)
            self.scroll_start_hour.set_value(f"{start_dt.hour:02d}")
            self.scroll_start_min.set_value(f"{start_dt.minute:02d}")

            # 显式显示 (因为 setChecked 不发信号)
            self.start_group.show()
            self.duration_grid.show()
            self.lbl_end_date.show()
            self.lbl_start.setText("开始")
            self.lbl_end.setText("完成")
        else:
            self.chk_enable_start.setChecked(False)

            # 显式隐藏 (这是修复 Bug 的核心)
            self.start_group.hide()
            self.duration_grid.hide()
            self.lbl_end_date.hide()
            self.lbl_start.setText("开始时间")
            self.lbl_end.setText("完成时间")

    def _connect_signals(self):
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
        if self.calendar.isVisible():
            self.calendar.hide()
        else:
            self.calendar.show()

    def _on_date_selected(self, date):
        self.current_date = date
        self._update_date_label()
        self._update_end_date_label()

    def _update_date_label(self):
        text = self.current_date.toString("yyyy年MM月dd日")
        self.btn_date.setText("    " + text)

    def _on_switch_toggled(self, checked):
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
            watched is self.lbl_end_date
            and event.type() == QEvent.Type.MouseButtonDblClick
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._show_end_date_calendar()
            return True
        return super().eventFilter(watched, event)

    def _on_confirm(self):
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
