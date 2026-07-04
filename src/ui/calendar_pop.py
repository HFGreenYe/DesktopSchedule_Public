# src/ui/calendar_pop.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QCalendarWidget,
    QToolButton,
    QSpinBox,
    QLabel,
    QLineEdit,
    QTableView,
)
from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
    QDate,
    QRect,
    QSize,
    QEvent,
    QPoint,
)
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QIcon, QTextCharFormat
import datetime
from ..data.database import db_manager
from ..config import AppConfig
from ..utils.styles import StyleManager


def _calendar_accent_color():
    return StyleManager.mix_colors(
        AppConfig.COLOR_GRADIENT_START,
        "#ffffff",
        0.98,
    )


class HighlightCalendarWidget(QCalendarWidget):
    """自定义日历控件：负责在有日程的日期下方画三色小圆点"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.date_status = {} # 字典，记录具体状态颜色
        self.update_schedule_dates()

    def update_schedule_dates(self):
        """扫描数据库，计算每天的综合状态：全完成(白) / 逾期(灰) / 待办(青)"""
        schedules = db_manager.get_all_schedules()
        
        # 1. 先把日程按日期分组
        date_map = {}
        for s in schedules:
            target = s.start_time.date() if s.start_time else (s.end_time.date() if s.end_time else None)
            if target:
                if target not in date_map:
                    date_map[target] = []
                date_map[target].append(s)

        self.date_status.clear()
        today = datetime.date.today()

        # 2. 评判每天的颜色
        for d, scheds in date_map.items():
            # 判断这天是否所有日程都已完成 (status == 1)
            all_completed = all(getattr(s, 'status', 0) == 1 for s in scheds)
            
            if all_completed:
                self.date_status[d] = "white" # 全部完成显示白色
            else:
                if d < today:
                    self.date_status[d] = "grey"  # 过去有未完成的，逾期灰色
                else:
                    self.date_status[d] = "cyan"  # 今天及未来有未完成的，青色

        self.updateCells()

    def paintCell(self, painter, rect, date):
        """重写底层绘制：根据不同颜色画点"""
        super().paintCell(painter, rect, date)
        
        py_date = date.toPyDate()
        if py_date in self.date_status:
            status = self.date_status[py_date]
            
            # 定义三种颜色的具体色值
            if status == "white":
                color = QColor("#05e92a") 
            elif status == "grey":
                color = QColor("#999999")          
            else:
                color = QColor(_calendar_accent_color())
                
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            
            dot_size = 4
            x = int(rect.center().x() - dot_size / 2)
            y = int(rect.bottom() - 6)
            
            painter.drawEllipse(x, y, dot_size, dot_size)
            painter.restore()


class CalendarPop(QWidget):
    """悬浮日历弹窗容器"""
    date_selected = pyqtSignal(object) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(300, 260)
        
        self.drag_pos = None 
        self.current_theme = "dark" 
        self.last_today = QDate.currentDate()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.calendar = HighlightCalendarWidget(self)
        self.calendar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.calendar.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        self.calendar.setGridVisible(False) 
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        layout.addWidget(self.calendar)
        self.calendar.clicked.connect(self._on_date_clicked)

        calendar_view = self.calendar.findChild(
            QTableView,
            "qt_calendar_calendarview",
        )
        if calendar_view is not None:
            calendar_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # 应用初始主题
        self._apply_theme()

        # --- 替换左右月份箭头 ---
        prev_btn = self.calendar.findChild(QToolButton, "qt_calendar_prevmonth")
        if prev_btn:
            prev_btn.setIcon(QIcon("assets/icons/cal_left.svg")) 
            prev_btn.setIconSize(QSize(16, 16)) 

        next_btn = self.calendar.findChild(QToolButton, "qt_calendar_nextmonth")
        if next_btn:
            next_btn.setIcon(QIcon("assets/icons/cal_right.svg")) 
            next_btn.setIconSize(QSize(16, 16)) 

        # --- 改造年份框：禁用输入，仅使用上下箭头 ---
        year_spin = self.calendar.findChild(QSpinBox)
        if year_spin:
            # 找到数字框里的文本输入框，将其变成纯只读，屏蔽键盘
            line_edit = year_spin.findChild(QLineEdit)
            if line_edit:
                line_edit.setReadOnly(True)
                line_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            year_spin.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # --- 允许拖拽 ---
        nav_bar = self.calendar.findChild(QWidget, "qt_calendar_navigationbar")
        if nav_bar:
            nav_bar.installEventFilter(self)
            
        # --- 双击空白处切换主题 ---
        #self.theme_toggle_area = QLabel(self)
        #self.theme_toggle_area.setGeometry(0, 32, 45, 25) 
        #self.theme_toggle_area.setStyleSheet("background: transparent;")
        #self.theme_toggle_area.setCursor(Qt.CursorShape.PointingHandCursor)
        #self.theme_toggle_area.setToolTip("双击切换深浅色")
        #self.theme_toggle_area.mouseDoubleClickEvent = self._toggle_theme 

    def _toggle_theme(self, event=None):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self._apply_theme()
        self.update() 

    def _apply_theme(self):
        if self.current_theme == "dark":
            bg_color, text_color, disable_color = "#2b2b2b", "white", "#666666"
        else:
            bg_color, text_color, disable_color = "#ffffff", "#333333", "#cccccc"

        calendar_accent = _calendar_accent_color()

        self.calendar.setStyleSheet(f"""
            QCalendarWidget QWidget {{ alternate-background-color: {bg_color};color: {text_color}; }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{ background-color: {calendar_accent}; }}
            
            QCalendarWidget QToolButton {{
                color: white; background-color: transparent; border: none; 
                border-radius: 4px; padding: 4px; font-weight: bold; font-family: 'Microsoft YaHei'; font-size: 14px;
            }}
            QCalendarWidget QToolButton::menu-indicator {{ image: none; }}
            QCalendarWidget QToolButton:hover {{ background-color: rgba(0, 0, 0, 0.15); }}
            QCalendarWidget QToolButton:pressed {{ background-color: rgba(0, 0, 0, 0.3); }}
            
            QCalendarWidget QMenu {{ background-color: {bg_color}; color: {text_color}; border: 1px solid {calendar_accent}; }}
            
            /* 让箭头与文字紧凑聚拢 */
            QCalendarWidget QSpinBox {{ 
                background-color: transparent; color: white; border: none; 
                font-weight: bold; font-family: 'Microsoft YaHei'; font-size: 14px;
                max-width: 48px; /* 限制最大宽度，强行把右边的箭头向左拉近 */
                padding-right: 12px; 
            }}
            QCalendarWidget QSpinBox::up-button {{
                subcontrol-origin: border; subcontrol-position: top right;
                width: 12px; height: 10px; 
                margin-top: 6px; /* 把上箭头往下推，靠近中间 */
                right: 2px;
                image: url(assets/icons/cal_up.svg);
            }}
            QCalendarWidget QSpinBox::down-button {{
                subcontrol-origin: border; subcontrol-position: bottom right;
                width: 12px; height: 10px; 
                margin-bottom: 6px; /* 把下箭头往上推，靠近中间 */
                right: 2px;
                image: url(assets/icons/cal_down.svg);
            }}
            QCalendarWidget QSpinBox::up-button:hover, QCalendarWidget QSpinBox::down-button:hover {{
                background-color: rgba(0, 0, 0, 0.2); border-radius: 2px;
            }}
            
            QCalendarWidget QAbstractItemView:enabled {{
                background-color: {bg_color}; 
                selection-background-color: {calendar_accent}; selection-color: white;
                font-family: 'Microsoft YaHei'; font-size: 13px; outline: 0px;
            }}
            QCalendarWidget QAbstractItemView:disabled {{ color: {disable_color}; }}
        """)
        self._update_today_highlight()

    def _update_today_highlight(self):
        """标黄今天的日期，并处理跨天刷新逻辑"""
        today = QDate.currentDate()
        today_color = "#FFD700" if self.current_theme == "dark" else "#FAAD14"
        
        if self.last_today != today:
            # 如果跨天了，清除昨天的黄色格式
            self.calendar.setDateTextFormat(self.last_today, QTextCharFormat())
        self.last_today = today
        
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(today_color))
        font = fmt.font()
        font.setBold(True) 
        fmt.setFont(font)
        
        self.calendar.setDateTextFormat(today, fmt)

    def eventFilter(self, obj, event):
        """仅保留顶栏拖拽事件，清除了之前的滚轮拦截逻辑"""
        nav_bar = self.calendar.findChild(QWidget, "qt_calendar_navigationbar")
        if obj == nav_bar:
            if event.type() == QEvent.Type.MouseButtonDblClick and event.button() == Qt.MouseButton.LeftButton:
                self._toggle_theme()  # 触发主题切换
                return True
            elif event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self.drag_pos = event.globalPosition().toPoint() - self.pos()
                return True
            elif event.type() == QEvent.Type.MouseMove and self.drag_pos is not None:
                self.move(event.globalPosition().toPoint() - self.drag_pos)
                return True
            elif event.type() == QEvent.Type.MouseButtonRelease:
                self.drag_pos = None
                return True
        return super().eventFilter(obj, event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg = QColor("#2b2b2b") if self.current_theme == "dark" else QColor("#ffffff")
        painter.setBrush(QBrush(bg))
        painter.setPen(QPen(QColor("rgba(255, 255, 255, 0.2)"), 1))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)

    def show_at(self, pos, current_date=None):
        self._apply_theme()
        self.calendar.update_schedule_dates() 
        if current_date:
            self.calendar.setSelectedDate(QDate(current_date.year, current_date.month, current_date.day))
        self.move(pos.x() - 150, pos.y() + 10) 
        self.show()

    def _on_date_clicked(self, qdate):
        py_date = qdate.toPyDate()
        self.date_selected.emit(py_date)
        self.close()
