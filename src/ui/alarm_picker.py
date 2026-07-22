# src/ui/alarm_picker.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGridLayout, QFrame, QScrollArea, 
                             QButtonGroup)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal, QTimer, QPoint
from PyQt6.QtGui import QColor, QPainter, QPen
from datetime import datetime, timedelta
from .components import NumberScroller, IOSSwitch 
from .components import get_colored_icon
from ..config import AppConfig
from ..utils.styles import StyleManager

# ... (CustomToolTip 类保持不变，无需修改) ...
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

class AlarmPickerView(QWidget):
    back_requested = pyqtSignal()
    suspend_requested = pyqtSignal()
    confirm_requested = pyqtSignal(object, bool, int) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.target_time = datetime.now() 
        self.drag_pos = None 
        
        self._setup_ui()
        self._connect_signals()



    def _setup_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # 标题
        header_container = QWidget()
        header_container.setFixedHeight(60)
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(30, 10, 30, 0)
        self.lbl_title = QLabel("设置提醒")
        self.lbl_title.setStyleSheet("color: white; font-size: 24px; font-weight: bold; font-family: 'Microsoft YaHei';")
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()
        outer_layout.addWidget(header_container)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) 
        self.scroll_area.setStyleSheet("QScrollArea { background: transparent; border: none; } QWidget { background: transparent; }")
        
        self.content_widget = QWidget()
        self.content = QVBoxLayout(self.content_widget)
        self.content.setContentsMargins(20, 10, 20, 30)
        self.content.setSpacing(20)
        self.scroll_area.setWidget(self.content_widget)
        outer_layout.addWidget(self.scroll_area)

        # 提示文字
        lbl_hint = QLabel("提醒时间")
        lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_hint.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px; margin-bottom: 5px;")
        self.content.addWidget(lbl_hint)
        
        # 开关逻辑
        self.day_select_container = QWidget()
        day_layout = QHBoxLayout(self.day_select_container)
        day_layout.setContentsMargins(20, 0, 20, 0) 
        
        lbl_prev_day = QLabel("设置为前一天")
        lbl_prev_day.setStyleSheet("color: white; font-size: 15px; font-weight: bold;")
        
        self.switch_prev_day = IOSSwitch()
        self.switch_prev_day.toggled.connect(self._validate_time)
        
        day_layout.addWidget(lbl_prev_day)
        day_layout.addStretch()
        day_layout.addWidget(self.switch_prev_day)
        
        self.content.addWidget(self.day_select_container)

        # 时间滚轮容器
        self.time_container = QWidget()
        self.time_container.setFixedHeight(130) 
        self.time_container.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
            }
        """)
        
        t_layout = QHBoxLayout(self.time_container)
        t_layout.setContentsMargins(40, 5, 40, 5)
        
        self.scroll_h = NumberScroller([f"{i:02d}" for i in range(24)])
        self.scroll_m = NumberScroller([f"{i:02d}" for i in range(60)])
        
        lbl_colon = QLabel(":")
        lbl_colon.setStyleSheet("color: white; font-size: 20px; font-weight: bold; background: transparent;")
        
        t_layout.addWidget(self.scroll_h)
        t_layout.addWidget(lbl_colon)
        t_layout.addWidget(self.scroll_m)
        
        self.content.addWidget(self.time_container)

        # 快捷提前选项
        self.quick_grid = QWidget()
        g_layout = QGridLayout(self.quick_grid)
        g_layout.setContentsMargins(0,0,0,0)
        g_layout.setSpacing(10)
        
        options = [
            (5, "5分钟前"), (10, "10分钟前"), (15, "15分钟前"),
            (30, "30分钟前"), (60, "1小时前"), (120, "2小时前")
        ]
        
        self.quick_btns = []
        for idx, (mins, text) in enumerate(options):
            btn = QPushButton(text)
            btn.setFixedHeight(32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("delta", mins)
            btn.clicked.connect(lambda _, b=btn: self._on_quick_set(b))
            btn.setStyleSheet(self._get_btn_style())
            g_layout.addWidget(btn, idx // 3, idx % 3)
            self.quick_btns.append(btn)
            
        self.content.addWidget(self.quick_grid)

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
        self.content.addLayout(alarm_row)

        # 闹钟时长选择
        self.alarm_opts_container = QWidget()
        v_alarm = QVBoxLayout(self.alarm_opts_container)
        v_alarm.setContentsMargins(0, 0, 0, 0)
        lbl_dur = QLabel("持续响铃时长")
        lbl_dur.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px;")
        v_alarm.addWidget(lbl_dur)
        
        h_alarm_btns = QHBoxLayout()
        h_alarm_btns.setSpacing(10)
        
        self.alarm_group = QButtonGroup(self)
        selected_alarm_color = AppConfig.COLOR_GRADIENT_START
        idle_alarm_color = StyleManager.color_to_rgba(
            AppConfig.COLOR_GRADIENT_START,
            0.35,
        )
        durations = [(0, "1分钟"), (1, "3分钟"), (2, "手动关闭")]
        for val, text in durations:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setFixedHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {idle_alarm_color}; border: 1px solid rgba(255,255,255,0.3);
                    border-radius: 15px; color: rgba(255,255,255,0.8); font-size: 12px;
                }}
                QPushButton:checked {{
                    background-color: {selected_alarm_color}; border: none; color: white; font-weight: bold;
                }}
            """)
            self.alarm_group.addButton(btn, val)
            h_alarm_btns.addWidget(btn)
            if val == 0: btn.setChecked(True)
            
        v_alarm.addLayout(h_alarm_btns)
        self.alarm_opts_container.hide()
        self.content.addWidget(self.alarm_opts_container)

        self.content.addStretch()

        # Footer
        footer = QWidget()
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(30, 10, 30, 20)
        f_layout.setSpacing(20)
        
        self.btn_cancel = QPushButton("取消")
        self.btn_ok = QPushButton("确定")
        
        for btn in [self.btn_cancel, self.btn_ok]:
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
        self.btn_cancel.setStyleSheet("""
            QPushButton { background: transparent; border: 1px solid rgba(255,255,255,0.6); border-radius: 20px; color: white; }
            QPushButton:hover { background: rgba(255,255,255,0.1); }
        """)
        self.btn_ok.setStyleSheet(f"""
            QPushButton {{ background: white; border: none; border-radius: 20px; color: {AppConfig.COLOR_GRADIENT_START}; font-weight: bold; }}
            QPushButton:hover {{ background: #f0f0f0; }}
        """)
        
        f_layout.addWidget(self.btn_cancel)
        f_layout.addWidget(self.btn_ok)
        outer_layout.addWidget(footer)
        self._setup_window_controls()

    def set_title(self, text="设置提醒"):
        self.lbl_title.setText(text)
        if len(text) > 4:
            self.lbl_title.setStyleSheet("color: white; font-size: 17px; font-weight: bold; font-family: 'Microsoft YaHei';")
        else:
            self.lbl_title.setStyleSheet("color: white; font-size: 24px; font-weight: bold; font-family: 'Microsoft YaHei';")

    def set_initial_data(self, dt, is_alarm=False, duration=0):
        self.target_time = dt if dt else datetime.now().replace(hour=23, minute=59)
        
        # 每次打开重置开关为 False (默认为当天)
        self.switch_prev_day.setChecked(False)
        
        # 初始化时间
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
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15); border-radius: 8px; color: white; 
                border: 1px solid rgba(255,255,255,0.2);
            }
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
        
        # 如果快捷计算结果早于当天 00:00，自动打开"前一天"开关
        day_start = self.target_time.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 先断开信号防止循环调用 _validate_time
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
        """
        实时校验逻辑：
        1. 下限：不能早于当前时间 (Now)
        2. 上限：不能晚于日程时间 (Target Time)
        """
        now = datetime.now()
        target = self.target_time
        
        try:
            h = int(self.scroll_h.get_value())
            m = int(self.scroll_m.get_value())
            
            # 计算当前滚轮代表的绝对时间
            target_date = self.target_time.date()
            if self.switch_prev_day.isChecked():
                target_date = target_date - timedelta(days=1)
            
            current_setting_dt = datetime(
                target_date.year, target_date.month, target_date.day,
                h, m
            )
            
            # --- 1. 下限检查：不能早于现在 ---
            if current_setting_dt.date() == now.date():
                if h < now.hour:
                    self.scroll_h.set_value(f"{now.hour:02d}")
                    if int(self.scroll_m.get_value()) < now.minute:
                        self.scroll_m.set_value(f"{now.minute:02d}")
                elif h == now.hour:
                    if m < now.minute:
                        self.scroll_m.set_value(f"{now.minute:02d}")

            # --- 2. 上限检查：不能晚于日程计划时间 ---
            # 只有在日期相同（即"前一天"未开启）的情况下，才需要严格限制小时和分钟
            # 如果开启了前一天，那么时间肯定早于 Target，无需检查上限
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
            
        remind_dt = datetime(
            base_date.year, base_date.month, base_date.day,
            h, m
        )
        
        def show_error(msg):
            print(f"❌ {msg}")
            tooltip = CustomToolTip(f"❌ {msg}", self)
            
            # 获取当前界面在屏幕上的绝对坐标
            window_pos = self.mapToGlobal(QPoint(0, 0))
            
            # 计算居中坐标
            # 屏幕X = 窗口左边 + (窗口宽 - 气泡宽) / 2
            center_x = window_pos.x() + (self.width() - tooltip.width()) // 2
            
            # 屏幕Y = 窗口顶边 + (窗口高 - 气泡高) / 2
            center_y = window_pos.y() + (self.height() - tooltip.height()) // 2
            
            tooltip.show_at(QPoint(int(center_x), int(center_y)))

        # 1. 检查是否早于当前
        if remind_dt < datetime.now():
            show_error("提醒时间不能早于当前时间")
            return
            
        # 2. 检查是否晚于日程时间
        if remind_dt > self.target_time:
            show_error("提醒时间不能晚于计划时间")
            return

        is_alarm = self.switch_alarm.isChecked()
        duration_mode = self.alarm_group.checkedId()
        self.confirm_requested.emit(remind_dt, is_alarm, duration_mode)

    def _setup_window_controls(self):
        """使用绝对定位在页面上方悬浮生成挂起和关闭按钮"""
        from PyQt6.QtWidgets import QPushButton, QToolButton
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        from ..utils.styles import StyleManager

        # 1. 挂起按钮 (绝对定位居中)
        self.btn_suspend = QPushButton(self)
        self.btn_suspend.setFixedSize(30, 30)
        self.btn_suspend.setIcon(QIcon("assets/icons/hang_up.png"))
        self.btn_suspend.setIconSize(QSize(20, 20))
        self.btn_suspend.setStyleSheet("QPushButton { background: transparent; border: none; }")
        self.btn_suspend.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_suspend.clicked.connect(self.suspend_requested.emit)

        # 2. 关闭按钮 (绝对定位右上角)
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
