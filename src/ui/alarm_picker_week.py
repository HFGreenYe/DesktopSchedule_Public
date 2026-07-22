# src/ui/alarm_picker_week.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGridLayout, QFrame, 
                             QButtonGroup)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPoint
from PyQt6.QtGui import QColor, QPainter, QPen
from datetime import datetime, timedelta
from ..config import AppConfig
from ..utils.styles import StyleManager
from .components import NumberScroller, IOSSwitch 
from .components import get_colored_icon

class CustomToolTip(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(parent, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setText(text)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setStyleSheet("""
            color: #333333;
            font-family: "Microsoft YaHei";
            font-size: 12px;
            padding: 6px 10px;
        """)
        self.adjustSize()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#ffffff"))
        painter.setPen(QPen(QColor("#ff4d4f"), 1)) 
        rect = self.rect().adjusted(0, 0, -1, -1)
        painter.drawRoundedRect(rect, 4, 4)
        super().paintEvent(event)

    def show_at(self, pos):
        self.move(pos)
        self.show()
        QTimer.singleShot(2000, self.close)


class AlarmPickerViewWeek(QWidget):
    back_requested = pyqtSignal()
    confirm_requested = pyqtSignal(object, bool, int) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.target_time = datetime.now() 
        
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(0)

        # ==========================================
        # 1. 左侧区域
        # ==========================================
        self.left_panel = QFrame()
        left_vbox = QVBoxLayout(self.left_panel)
        left_vbox.setContentsMargins(10, 0, 10, 0)
        
        # 标题
        header_row = QHBoxLayout()
        self.lbl_title = QLabel("设置提醒")
        self.lbl_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; font-family: 'Microsoft YaHei';")
        header_row.addWidget(self.lbl_title)
        header_row.addStretch()
        left_vbox.addLayout(header_row)
        
        left_vbox.addSpacing(15)

        # 提示文字
        lbl_hint = QLabel("提醒时间")
        lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_hint.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px; margin-bottom: 5px;")
        left_vbox.addWidget(lbl_hint)
        
        # 开关逻辑 (前一天)
        self.day_select_container = QWidget()
        day_layout = QHBoxLayout(self.day_select_container)
        day_layout.setContentsMargins(15, 0, 15, 0) 
        
        lbl_prev_day = QLabel("设置为前一天")
        lbl_prev_day.setStyleSheet("color: white; font-size: 15px; font-weight: bold;")
        
        self.switch_prev_day = IOSSwitch()
        self.switch_prev_day.toggled.connect(self._validate_time)
        
        day_layout.addWidget(lbl_prev_day)
        day_layout.addStretch()
        day_layout.addWidget(self.switch_prev_day)
        left_vbox.addWidget(self.day_select_container)

        # 时间滚轮容器
        self.time_container = QWidget()
        self.time_container.setFixedHeight(130) 
        self.time_container.setStyleSheet("QWidget { background-color: rgba(255, 255, 255, 0.05); border-radius: 10px; }")
        
        t_layout = QHBoxLayout(self.time_container)
        t_layout.setContentsMargins(30, 5, 30, 5)
        
        self.scroll_h = NumberScroller([f"{i:02d}" for i in range(24)])
        self.scroll_m = NumberScroller([f"{i:02d}" for i in range(60)])
        
        lbl_colon = QLabel(":")
        lbl_colon.setStyleSheet("color: white; font-size: 20px; font-weight: bold; background: transparent;")
        
        t_layout.addWidget(self.scroll_h)
        t_layout.addWidget(lbl_colon)
        t_layout.addWidget(self.scroll_m)
        left_vbox.addWidget(self.time_container)
        
        left_vbox.addStretch()

        # ==========================================
        # 2. 中间分割线
        # ==========================================
        line = QFrame()
        line.setFixedWidth(1)
        line.setStyleSheet("background-color: rgba(255, 255, 255, 60); margin: 20px 15px;")

        main_layout.addWidget(self.left_panel, 1)
        main_layout.addWidget(line)

        # ==========================================
        # 3. 右侧区域
        # ==========================================
        self.right_panel = QFrame()
        right_vbox = QVBoxLayout(self.right_panel)
        right_vbox.setContentsMargins(10, 10, 10, 0)
        right_vbox.setSpacing(15)

        # 快捷提前选项
        self.quick_grid = QWidget()
        g_layout = QGridLayout(self.quick_grid)
        g_layout.setContentsMargins(0,0,0,0)
        g_layout.setSpacing(10)
        
        options = [(5, "5分钟前"), (10, "10分钟前"), (15, "15分钟前"), (30, "30分钟前"), (60, "1小时前"), (120, "2小时前")]
        
        self.quick_btns = []
        for idx, (mins, text) in enumerate(options):
            btn = QPushButton(text)
            btn.setFixedHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("delta", mins)
            btn.clicked.connect(lambda _, b=btn: self._on_quick_set(b))
            btn.setStyleSheet(self._get_btn_style())
            g_layout.addWidget(btn, idx // 3, idx % 3)
            self.quick_btns.append(btn)
            
        right_vbox.addWidget(self.quick_grid)

        # 强提醒/闹钟开关
        alarm_row = QHBoxLayout()
        alarm_row.setSpacing(3)
        icon_bell = QLabel()
        icon_bell.setFixedSize(18, 18)
        icon_bell.setPixmap(get_colored_icon("bell.svg", "#FFFFFF", 18))
        lbl_alarm = QLabel("强提醒 (有声模式)")
        lbl_alarm.setStyleSheet("color: white; font-size: 15px; font-weight: bold;")
        self.switch_alarm = IOSSwitch()
        self.switch_alarm.toggled.connect(self._toggle_alarm_options)
        alarm_row.addWidget(icon_bell)
        alarm_row.addWidget(lbl_alarm)
        alarm_row.addStretch()
        alarm_row.addWidget(self.switch_alarm)
        right_vbox.addLayout(alarm_row)

        # 闹钟时长选择
        self.alarm_opts_container = QWidget()
        v_alarm = QVBoxLayout(self.alarm_opts_container)
        v_alarm.setContentsMargins(0, 0, 0, 0)
        
        lbl_dur = QLabel("持续响铃时长")
        lbl_dur.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px;")
        v_alarm.addWidget(lbl_dur)
        
        h_alarm_btns = QHBoxLayout()
        h_alarm_btns.setSpacing(8)
        
        self.alarm_group = QButtonGroup(self)
        idle_alarm_color = StyleManager.color_to_rgba(
            AppConfig.COLOR_GRADIENT_START,
            0.35,
        )
        durations = [(0, "1分钟"), (1, "3分钟"), (2, "手动关闭")]
        for val, text in durations:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setFixedHeight(28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{ background-color: {idle_alarm_color}; border: 1px solid rgba(255,255,255,0.3); border-radius: 14px; color: rgba(255,255,255,0.8); font-size: 11px; }}
                QPushButton:checked {{ background-color: {AppConfig.COLOR_GRADIENT_START}; border: none; color: white; font-weight: bold; }}
            """)
            self.alarm_group.addButton(btn, val)
            h_alarm_btns.addWidget(btn)
            if val == 0: btn.setChecked(True)
            
        v_alarm.addLayout(h_alarm_btns)
        self.alarm_opts_container.hide()
        right_vbox.addWidget(self.alarm_opts_container)
        
        right_vbox.addStretch()

        # 底部确定/取消按钮
        footer = QWidget()
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(0, 0, 0, 10)
        
        self.btn_cancel = QPushButton("取消")
        self.btn_ok = QPushButton("确定")
        
        for btn in [self.btn_cancel, self.btn_ok]:
            btn.setFixedSize(70, 32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
        self.btn_cancel.setStyleSheet("QPushButton { background: transparent; border: 1px solid rgba(255,255,255,0.6); border-radius: 16px; color: white; } QPushButton:hover { background: rgba(255,255,255,0.1); }")
        self.btn_ok.setStyleSheet(self.btn_cancel.styleSheet())
        
        f_layout.addStretch()
        f_layout.addWidget(self.btn_cancel)
        f_layout.addSpacing(15)
        f_layout.addWidget(self.btn_ok)
        right_vbox.addWidget(footer)

        main_layout.addWidget(self.right_panel, 1)


    def set_title(self, text="设置提醒"):
        self.lbl_title.setText(text)
        if len(text) > 4:
            self.lbl_title.setStyleSheet("color: white; font-size: 17px; font-weight: bold; font-family: 'Microsoft YaHei';")
        else:
            self.lbl_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; font-family: 'Microsoft YaHei';")

    def set_initial_data(self, dt, is_alarm=False, duration=0):
        self.target_time = dt if dt else datetime.now().replace(hour=23, minute=59)
        self.switch_prev_day.setChecked(False)
        self._update_scrollers(self.target_time)
        self.switch_alarm.setChecked(is_alarm)
        if is_alarm:
            self.alarm_opts_container.show()
        else:
            self.alarm_opts_container.hide()
        btn = self.alarm_group.button(duration)
        if btn: btn.setChecked(True)

    def _get_btn_style(self):
        return """
            QPushButton { background-color: rgba(255, 255, 255, 0.15); border-radius: 8px; color: white; border: 1px solid rgba(255,255,255,0.2); }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.3); }
        """

    def _connect_signals(self):
        self.btn_cancel.clicked.connect(self.back_requested.emit)
        self.btn_ok.clicked.connect(self._on_confirm)
        self.scroll_h.value_changed.connect(self._validate_time)
        self.scroll_m.value_changed.connect(self._validate_time)

    def _on_quick_set(self, btn):
        delta_min = btn.property("delta")
        remind_dt = self.target_time - timedelta(minutes=delta_min)
        day_start = self.target_time.replace(hour=0, minute=0, second=0, microsecond=0)
        
        self.switch_prev_day.blockSignals(True)
        if remind_dt < day_start:
            self.switch_prev_day.setChecked(True) 
        else:
            self.switch_prev_day.setChecked(False) 
        self.switch_prev_day.blockSignals(False)
        self._update_scrollers(remind_dt)

    def _update_scrollers(self, dt):
        self.scroll_h.set_value(f"{dt.hour:02d}")
        self.scroll_m.set_value(f"{dt.minute:02d}")

    def _validate_time(self):
        now = datetime.now()
        target = self.target_time
        try:
            h = int(self.scroll_h.get_value())
            m = int(self.scroll_m.get_value())
            target_date = self.target_time.date()
            if self.switch_prev_day.isChecked():
                target_date = target_date - timedelta(days=1)
            current_setting_dt = datetime(target_date.year, target_date.month, target_date.day, h, m)
            
            if current_setting_dt.date() == now.date():
                if h < now.hour:
                    self.scroll_h.set_value(f"{now.hour:02d}")
                    if int(self.scroll_m.get_value()) < now.minute:
                        self.scroll_m.set_value(f"{now.minute:02d}")
                elif h == now.hour:
                    if m < now.minute:
                        self.scroll_m.set_value(f"{now.minute:02d}")

            if not self.switch_prev_day.isChecked():
                target_h = target.hour
                target_m = target.minute
                if h > target_h:
                    self.scroll_h.set_value(f"{target_h:02d}")
                    if int(self.scroll_m.get_value()) > target_m:
                        self.scroll_m.set_value(f"{target_m:02d}")
                elif h == target_h:
                    if m > target_m:
                        self.scroll_m.set_value(f"{target_m:02d}")
        except Exception as e:
            pass

    def _toggle_alarm_options(self, checked):
        if checked:
            self.alarm_opts_container.show()
        else:
            self.alarm_opts_container.hide()

    def _on_confirm(self):
        h = int(self.scroll_h.get_value())
        m = int(self.scroll_m.get_value())
        base_date = self.target_time.date()
        if self.switch_prev_day.isChecked():
            base_date = base_date - timedelta(days=1)
            
        remind_dt = datetime(base_date.year, base_date.month, base_date.day, h, m)
        
        def show_error(msg):
            print(f"❌ {msg}")
            tooltip = CustomToolTip(f"❌ {msg}", self)
            window_pos = self.mapToGlobal(QPoint(0, 0))
            center_x = window_pos.x() + (self.width() - tooltip.width()) // 2
            center_y = window_pos.y() + (self.height() - tooltip.height()) // 2
            tooltip.show_at(QPoint(int(center_x), int(center_y)))

        if remind_dt < datetime.now():
            show_error("提醒时间不能早于当前时间")
            return
            
        if remind_dt > self.target_time:
            show_error("提醒时间不能晚于计划时间")
            return

        is_alarm = self.switch_alarm.isChecked()
        duration_mode = self.alarm_group.checkedId()
        self.confirm_requested.emit(remind_dt, is_alarm, duration_mode)
