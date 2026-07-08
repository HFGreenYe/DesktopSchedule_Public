# src/ui/time_picker_week.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QCalendarWidget, QGridLayout, QFrame, QPushButton, QToolButton)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer
from datetime import datetime, timedelta
from ..config import AppConfig
from ..utils.styles import StyleManager
from .components import IOSSwitch, NumberScroller

class TimePickerViewWeek(QWidget):
    back_requested = pyqtSignal()
    confirm_requested = pyqtSignal(object, object)
    timeChanged = pyqtSignal(QDate, bool, QTime, QTime)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_date = QDate.currentDate()
        self._init_ui()
        self._connect_signals()
        
        # 初始赋值
        now = QTime.currentTime()
        self.scroll_end_hour.set_value(f"{now.hour():02d}")
        self.scroll_end_min.set_value(f"{now.minute():02d}")

    def _get_colored_icon(self, icon_path, color_hex):
        renderer = QSvgRenderer(icon_path)
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), QColor(color_hex))
        painter.end()
        return QIcon(pixmap)

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
        header_row.addStretch()
        left_vbox.addLayout(header_row)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(False)
        self.calendar.setNavigationBarVisible(True)
        self.calendar.setStyleSheet(StyleManager.get_calendar_style())
        # 限制最小日期为今天，解决无法退回上个月和之前日子的限制 
        self.calendar.setMinimumDate(QDate.currentDate())
        
        # 替换日历切换图标
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
        self.time_picker_container.setStyleSheet("QFrame#TimeContainer { background-color: rgba(255, 255, 255, 0.1); border-radius: 12px; }")
        
        h_time_layout = QHBoxLayout(self.time_picker_container)
        self.start_group, self.scroll_start_hour, self.scroll_start_min = self._create_scroller_pair("开始时间")
        self.end_group, self.scroll_end_hour, self.scroll_end_min = self._create_scroller_pair("完成时间")
        
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
        self.btn_ok.setStyleSheet(f"QPushButton {{ background: white; border: none; border-radius: 16px; color: {AppConfig.COLOR_GRADIENT_START}; font-weight: bold; }}")
        
        btn_row.addStretch()
        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_ok)
        right_vbox.addLayout(btn_row)

        main_layout.addWidget(self.right_panel, 1)

    def _create_scroller_pair(self, label):
        grp = QWidget()
        lay = QVBoxLayout(grp)
        lay.setContentsMargins(0,0,0,0)
        lbl = QLabel(label)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 11px;")
        
        h = QHBoxLayout()
        sh = NumberScroller([f"{i:02d}" for i in range(24)])
        sm = NumberScroller([f"{i:02d}" for i in range(60)])
        
        # 修正冒号居中逻辑 
        lbl_colon = QLabel(":")
        lbl_colon.setFixedWidth(10)
        lbl_colon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_colon.setStyleSheet("color: white; font-size: 20px; font-weight: bold; padding-bottom: 5px;")
        
        h.addWidget(sh)
        h.addWidget(lbl_colon)
        h.addWidget(sm)
        
        lay.addWidget(lbl)
        lay.addLayout(h)
        return grp, sh, sm

    def set_title(self, text):
        self.lbl_title.setText(text)

    def set_initial_data(self, start_dt, end_dt):
        target = end_dt if end_dt else datetime.now()
        self.current_date = QDate(target.year, target.month, target.day)
        self.calendar.setSelectedDate(self.current_date)
        self.scroll_end_hour.set_value(f"{target.hour:02d}")
        self.scroll_end_min.set_value(f"{target.minute:02d}")
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

    def _connect_signals(self):
        self.calendar.clicked.connect(self._on_date_selected)
        self.chk_enable_start.toggled.connect(self._on_switch_toggled)
        self.btn_cancel.clicked.connect(self.back_requested.emit)
        self.btn_ok.clicked.connect(self._on_confirm)
        # 滚轮检测信号 [cite: 1388]
        for s in [self.scroll_start_hour, self.scroll_start_min, self.scroll_end_hour, self.scroll_end_min]:
            s.value_changed.connect(self._validate_scroll_time)

    def _on_date_selected(self, date):
        self.current_date = date

    def _on_switch_toggled(self, checked):
        self.start_group.setVisible(checked)
        self.duration_grid.setVisible(checked)

    def _on_quick_set(self, btn):
        mins = btn.property("minutes")
        eh, em = int(self.scroll_end_hour.get_value()), int(self.scroll_end_min.get_value())
        dt_end = datetime(2024,1,1, eh, em)
        dt_start = dt_end - timedelta(minutes=mins)
        self.scroll_start_hour.set_value(f"{dt_start.hour:02d}")
        self.scroll_start_min.set_value(f"{dt_start.minute:02d}")

    def _on_confirm(self):
        d = self.calendar.selectedDate()
        dt_end = datetime(d.year(), d.month(), d.day(), int(self.scroll_end_hour.get_value()), int(self.scroll_end_min.get_value()))
        dt_start = None
        if self.chk_enable_start.isChecked():
            dt_start = datetime(d.year(), d.month(), d.day(), int(self.scroll_start_hour.get_value()), int(self.scroll_start_min.get_value()))
        
        # 二次校验：确保不早于当前时间 [cite: 1394, 1395]
        now = datetime.now()
        if dt_end < now: return
            
        self.confirm_requested.emit(dt_start, dt_end)

    def _validate_scroll_time(self):
        now = datetime.now()
        if self.current_date == QDate.currentDate():
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
