# src/ui/month_window.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QToolButton, QLineEdit, 
                             QCalendarWidget, QApplication, QTableView, 
                             QStyledItemDelegate, QStyle, QStyleOptionViewItem,
                             QGridLayout, QTextEdit) 
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QTime, QTimer, QRectF, QSize
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QBrush, QLinearGradient, QIcon, QPen, QPalette, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from qframelesswindow import FramelessMainWindow
import datetime

from ..config import AppConfig
from ..data.database import db_manager
from ..utils.win_api import apply_24h2_border_fix
from ..utils.styles import StyleManager
from .header import ToolTipFilter
from .components import get_colored_icon, SharedMoreMenu


class CalendarCellDelegate(QStyledItemDelegate):
    def __init__(self, parent_window_height, grad_start_str, grad_end_str, table_view, parent=None):
        super().__init__(parent)
        self.p_height = parent_window_height
        self.grad_start = QColor(grad_start_str)
        self.grad_end = QColor(grad_end_str)
        self.table_view = table_view
        self.calendar_widget = parent
        self.visible_year = QDate.currentDate().year()
        self.visible_month = QDate.currentDate().month()
        self.today_date = QDate.currentDate()
        self.marker_cache = {}
        self.marker_count_cache = {}

    def set_calendar_state(self, visible_year, visible_month, today_date, marker_cache, marker_count_cache=None):
        self.visible_year = visible_year
        self.visible_month = visible_month
        self.today_date = today_date
        self.marker_cache = dict(marker_cache)
        self.marker_count_cache = dict(marker_count_cache or {})

    def _date_for_index(self, index):
        first_of_month = QDate(self.visible_year, self.visible_month, 1)
        first_day_of_week = self.calendar_widget.firstDayOfWeek().value
        offset = (first_of_month.dayOfWeek() - first_day_of_week) % 7
        if index.row() == 0:
            return QDate()

        if offset == 0:
            offset = 7

        first_visible_date = first_of_month.addDays(-offset)
        day_offset = (index.row() - 1) * 7 + index.column()
        return first_visible_date.addDays(day_offset)

    def _draw_label_marker(self, painter, rect, color, count):
        label_size = 22
        label_path = QPainterPath()
        label_path.moveTo(rect.left(), rect.top())
        label_path.lineTo(rect.left() + label_size, rect.top())
        label_path.lineTo(rect.left(), rect.top() + label_size)
        label_path.closeSubpath()

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawPath(label_path)

        count_text = "9+" if count > 9 else str(count)
        font = painter.font()
        font.setPointSize(6)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor("#FFFFFF"))
        text_rect = QRectF(rect.left(), rect.top(), 14, 14)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, count_text)
        painter.restore()


    # 计算全局 Y 坐标对应的颜色（线性插值）
    def get_color_for_y(self, y):
        ratio = y / self.p_height
        r = int(self.grad_start.red() * (1 - ratio) + self.grad_end.red() * ratio)
        g = int(self.grad_start.green() * (1 - ratio) + self.grad_end.green() * ratio)
        b = int(self.grad_start.blue() * (1 - ratio) + self.grad_end.blue() * ratio)
        return QColor(r, g, b)

    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. 绝对坐标计算 (分别求出格子的顶部和底部绝对 Y)
        cell_rect = option.rect
        table_y = self.table_view.y()
        global_offset_y = 32 
        
        abs_y_top = global_offset_y + table_y + cell_rect.top()
        abs_y_bottom = global_offset_y + table_y + cell_rect.bottom()
        
        abs_y_top = max(0, min(self.p_height, abs_y_top))
        abs_y_bottom = max(0, min(self.p_height, abs_y_bottom))

        color_top = self.get_color_for_y(abs_y_top)
        color_bottom = self.get_color_for_y(abs_y_bottom)
        
        cell_gradient = QLinearGradient(cell_rect.x(), cell_rect.top(), cell_rect.x(), cell_rect.bottom())
        cell_gradient.setColorAt(0.0, color_top)
        cell_gradient.setColorAt(1.0, color_bottom)
        
        painter.fillRect(cell_rect, QBrush(cell_gradient))

        # ==========================================
        # 计算一个向内收缩 3 像素的“内矩形”
        # ==========================================
        inner_rect = cell_rect.adjusted(3, 3, -3, -3)

        # 获取当前格子的文字
        date_str = str(index.data())
        cell_date = self._date_for_index(index)
        cell_py_date = cell_date.toPyDate() if cell_date.isValid() else None
        is_today = cell_date == self.today_date
        marker_color = self.marker_cache.get(cell_py_date)
        marker_count = self.marker_count_cache.get(cell_py_date, 0)
        
        # 核心逻辑：判断当前格子里是不是纯数字（表头"周一"不是，日期"27"是）
        is_date = date_str.isdigit() 

        # ==========================================
        # 5. 绘制卡片式空心白框 —— 【只给日期画，表头直接跳过】
        # ==========================================
        if is_date:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            
            # 1. 设置边框颜色和宽度 (保持原白色细边框)
            card_pen = QPen(QColor(255, 255, 255, 90))
            card_pen.setWidth(0)
            painter.setPen(card_pen)
            
            # 2. 设置内部填充颜色为纯白 (这就是把内部填满的关键！)
            painter.setBrush(QBrush(QColor(255, 255, 255, 10)))
            
            # 3. 绘制实心方框（边框+填充同时生效）
            painter.drawRect(inner_rect) 
            
            # 4. 顺手把画刷清空，保持良好的绘制习惯
            painter.setBrush(Qt.BrushStyle.NoBrush) 

        # 3. 画交互状态（悬停、选中遮罩）—— 【只给日期画】
        if is_date:
            if option.state & QStyle.StateFlag.State_Selected:
                if not is_today:
                    painter.fillRect(inner_rect, QColor(255, 255, 255, 40))
            elif option.state & QStyle.StateFlag.State_MouseOver:
                painter.fillRect(inner_rect, QColor(255, 255, 255, 10))

        # 4. 写字 —— 【不管是表头还是日期，都照常把字写出来】
        date_str = str(index.data()) 
        if date_str:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            # 判断当前内容是否是纯数字（日期），不是（表头）则跳过
            is_date = date_str.isdigit() 
            
            if is_date:
                is_current_month = (
                    cell_date.year() == self.visible_year and
                    cell_date.month() == self.visible_month
                )

                if is_today:
                    painter.setPen(QColor("#FFD700"))
                elif is_current_month:
                    if cell_date.dayOfWeek() in (6, 7):
                        painter.setPen(QColor(255, 60, 60))
                    else:
                        painter.setPen(QColor(255, 255, 255))
                else:
                    painter.setPen(QColor(128, 128, 128, 100))
            else:
                painter.setPen(QColor(255, 255, 255))

            # 居中写字
            painter.drawText(inner_rect, Qt.AlignmentFlag.AlignCenter, date_str)
            if marker_color is not None:
                self._draw_label_marker(painter, inner_rect, marker_color, marker_count)
        painter.restore()

class InlineAddViewMonth(QWidget):
    """月视图左侧专属的极简添加组件"""
    saved = pyqtSignal()
    canceled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_date = None
        self.is_schedule_mode = True
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 1. 标题输入
        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText("日程标题...")
        self.input_title.setFixedHeight(28)
        self.input_title.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255,255,255,0.3); 
                border-radius: 4px; color: white; font-size: 12px; padding: 0 5px; font-family: 'Microsoft YaHei';
            }
            QLineEdit:focus { border: 1px solid white; background: rgba(255, 255, 255, 0.2); }
        """)
        layout.addWidget(self.input_title)

        # 2. 详情输入
        self.input_desc = QTextEdit()
        self.input_desc.setPlaceholderText("详情描述...")
        self.input_desc.setFixedHeight(50)
        self.input_desc.setStyleSheet("""
            QTextEdit { 
                background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255,255,255,0.3); 
                border-radius: 4px; color: white; font-size: 11px; padding: 4px; font-family: 'Microsoft YaHei';
            }
            QTextEdit:focus { border: 1px solid white; background: rgba(255, 255, 255, 0.2); }
        """)
        layout.addWidget(self.input_desc)

        # 3. 浓缩版功能图标行 (时间、提醒、清单)
        icons_layout = QHBoxLayout()
        icons_layout.setContentsMargins(0, 0, 0, 0)
        icons_layout.setSpacing(4)
        
        for icon_name in ["time.svg", "alarm.svg", "list.svg"]:
            btn = QPushButton()
            btn.setFixedSize(22, 22)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            pixmap = get_colored_icon(icon_name, "#FFFFFF", 14)
            if not pixmap.isNull(): btn.setIcon(QIcon(pixmap))
            btn.setStyleSheet("QPushButton { background: transparent; border: none; } QPushButton:hover { background: rgba(255,255,255,0.2); border-radius: 3px; }")
            icons_layout.addWidget(btn)
        
        icons_layout.addStretch()
        layout.addLayout(icons_layout)

        # 4. 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_cancel = QPushButton("取消")
        self.btn_save = QPushButton("保存")
        for btn in [self.btn_cancel, self.btn_save]:
            btn.setFixedHeight(24)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
        self.btn_cancel.setStyleSheet("QPushButton { background: transparent; border: 1px solid rgba(255,255,255,0.5); border-radius: 12px; color: white; font-size: 11px; }")
        self.btn_save.setStyleSheet("QPushButton { background: white; border: none; border-radius: 12px; color: #0cc0df; font-weight: bold; font-size: 11px; }")
        
        self.btn_cancel.clicked.connect(self.canceled.emit)
        self.btn_save.clicked.connect(self._on_save)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def reset(self, target_date):
        self.selected_date = target_date
        self.input_title.clear()
        self.input_desc.clear()

    def _on_save(self):
        title = self.input_title.text().strip()
        if not title:
            if hasattr(self.window(), 'show_toast'):
                self.window().show_toast("⚠️ 标题不能为空")
            return

        from datetime import datetime
        # 默认保存为选中日期的 00:00
        py_date = self.selected_date.toPyDate()
        start_time = datetime(py_date.year, py_date.month, py_date.day, 0, 0)

        schedule_data = {
            'title': title,
            'item_type': 'schedule' if self.is_schedule_mode else 'todo',
            'priority': 0,
            'repeat_rule': 'none',
            'description': self.input_desc.toPlainText().strip(), 
            'start_time': start_time,
            'end_time': start_time, # 默认结束时间同上
            'category_id': None
        }

        from ..data.database import db_manager
        if db_manager.add_schedule(schedule_data):
            self.saved.emit()

class MonthWindow(FramelessMainWindow):
    """
    独立月视图窗口
    遵循主界面的青色渐变主题，左侧为信息控制栏，右侧为大日历网格
    """
    restore_requested = pyqtSignal()
    suspend_requested = pyqtSignal()
    view_selected = pyqtSignal(str)
    date_selected = pyqtSignal(QDate)

    def __init__(self):
        super().__init__()
        # 1. 窗口总尺寸缩小到 80%
        self.setFixedSize(720, 480) 
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.titleBar.hide()

        self.current_date = QDate.currentDate()
        self.schedule_marker_cache = {}
        self.schedule_marker_count_cache = {}
        self.drag_pos = None

        self._setup_ui()
        self._refresh_schedule_marker_cache()
        self._start_clock()
        
        # 挂载 24H2 边框与黑屏修复
        apply_24h2_border_fix(int(self.winId()))
        
        # 开启全局 ToolTip 样式
        self.setStyleSheet(self.styleSheet() + StyleManager.get_tooltip_style())

    def _setup_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==========================================
        # 1. 顶部栏 (高度缩小到 24px)
        # ==========================================
        self.top_bar = QWidget()
        self.top_bar.setFixedHeight(24)
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(2)

        # 顶栏左侧弹簧（把右侧的系统按钮推到最右边）
        top_layout.addStretch()

        # 居中的挂起按钮 (使用绝对定位)
        self.btn_suspend = QPushButton(self.top_bar) # 👈 重点：把 top_bar 作为父组件传进去
        self.btn_suspend.setFixedSize(24, 24)
        self.btn_suspend.move(348, 0)                # 👈 重点：(720 - 24) / 2 = 348
        
        self.btn_suspend.setIcon(QIcon("assets/icons/hang_up.png"))
        self.btn_suspend.setIconSize(QSize(14, 14))
        self.btn_suspend.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_suspend.setStyleSheet("QPushButton { background: transparent; border: none; } QPushButton:hover { background: rgba(255,255,255,0.2); border-radius: 12px; }")
        self.btn_suspend.clicked.connect(self.suspend_requested.emit)
        self.btn_suspend._tooltip = ToolTipFilter("挂起月视图", self.btn_suspend)
        self.btn_suspend.installEventFilter(self.btn_suspend._tooltip)

        # 顶栏右侧弹簧，将系统按钮推到最右边
        top_layout.addStretch()

        # 右上角功能键 (更多、最小化、关闭)
        self.btn_more = QToolButton()
        self.btn_more.setIcon(QIcon("assets/icons/more.png"))
        self.btn_more.setIconSize(QSize(12, 12))
        self.btn_more.setFixedSize(24, 24)
        self.btn_more.setStyleSheet(StyleManager.get_window_control_style(is_close=False))
        self.shared_more_menu = SharedMoreMenu(self, self.btn_more)
        self.btn_more.clicked.connect(self.shared_more_menu.show_menu)
        top_layout.addWidget(self.btn_more)

        self.btn_sync = QToolButton()
        self.btn_sync.setIcon(QIcon("assets/icons/sync.png"))
        self.btn_sync.setIconSize(QSize(12, 12))
        self.btn_sync.setFixedSize(24, 24)
        self.btn_sync.setStyleSheet(StyleManager.get_window_control_style(is_close=False))
        top_layout.addWidget(self.btn_sync)

        self.btn_close = QToolButton()
        self.btn_close.setIcon(QIcon("assets/icons/close.png"))
        self.btn_close.setIconSize(QSize(12, 12))
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.setStyleSheet(StyleManager.get_window_control_style(is_close=True))
        self.btn_close.clicked.connect(self.close)
        top_layout.addWidget(self.btn_close)

        main_layout.addWidget(self.top_bar)

        # ==========================================
        # 2. 主内容区 (左侧面板 + 分割线 + 右侧日历)
        # ==========================================
        content_area = QWidget()
        content_layout = QHBoxLayout(content_area)
        # 2. 内容区边距缩小
        content_layout.setContentsMargins(12, 8, 12, 12)
        content_layout.setSpacing(0)

        # --- 左侧面板 ---
        left_panel = QWidget()
        left_panel.setFixedWidth(144) 
        left_vbox = QVBoxLayout(left_panel)
        left_vbox.setContentsMargins(0, 0, 8, 0)
        left_vbox.setSpacing(0)

        # ==========================================
        # 1. 顶部信息区 (QGridLayout 网格完美对齐版)
        # ==========================================
        top_grid = QGridLayout()
        top_grid.setContentsMargins(0, 0, 0, 0)
        top_grid.setHorizontalSpacing(0)
        top_grid.setVerticalSpacing(4) # 控制上下两行的紧凑程度

        # --- 第0行，第0列：时间 ---
        self.lbl_time = QLabel("00:00")
        # 消除字体自带的 margin，方便对齐
        self.lbl_time.setStyleSheet('color: white; font-family: "Segoe UI Variable Display"; font-size: 34px; font-weight: 200; background: transparent; margin: 0; padding: 0;')
        top_grid.addWidget(self.lbl_time, 0, 0, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

        # --- 第0行，第1列：天气图标 ---
        self.lbl_weather_icon = QLabel("⌛")
        self.lbl_weather_icon.setFixedSize(30, 30) # 固定大小，确保居中不会乱跑
        self.lbl_weather_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_weather_icon.setStyleSheet('color: white; font-size: 16px; background: transparent;')
        top_grid.addWidget(self.lbl_weather_icon, 0, 1, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)

        # --- 第1行，第0列：月份切换器 ---
        month_row = QHBoxLayout()
        month_row.setContentsMargins(0, 0, 0, 0)
        
        self.btn_prev_month = QPushButton("〈")
        self.btn_prev_month.setStyleSheet("color: white; background: transparent; font-size: 13px; border: none;")
        self.btn_prev_month.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev_month.clicked.connect(self._prev_month)
        
        self.lbl_month = QLabel(f"{self.current_date.month()}月")
        self.lbl_month.setFixedHeight(18) # 固定高度
        self.lbl_month.setStyleSheet('color: white; font-size: 14px; font-family: "Microsoft YaHei"; font-weight: bold; margin: 0px 5px; background: transparent;')
        
        self.btn_next_month = QPushButton("〉")
        self.btn_next_month.setStyleSheet("color: white; background: transparent; font-size: 13px; border: none;")
        self.btn_next_month.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next_month.clicked.connect(self._next_month)

        month_row.addWidget(self.btn_prev_month)
        month_row.addWidget(self.lbl_month)
        month_row.addWidget(self.btn_next_month)
        month_row.addStretch() # 把月份往左挤
        
        # 把横向布局塞进网格
        top_grid.addLayout(month_row, 1, 0, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        # --- 第1行，第1列：温度标签 ---
        self.lbl_temp = QLabel("--°C")
        self.lbl_temp.setFixedHeight(18) # 高度与月份标签严格一致
        self.lbl_temp.setStyleSheet('color: white; font-size: 14px; font-family: "Microsoft YaHei"; font-weight: bold; background: transparent;')
        self.lbl_temp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_grid.addWidget(self.lbl_temp, 1, 1, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        top_grid.setColumnStretch(0, 1)
        top_grid.setColumnStretch(1, 0)

        left_vbox.addLayout(top_grid)
        left_vbox.addSpacing(0) 

        bottom_tools_vbox = QVBoxLayout()
        bottom_tools_vbox.setSpacing(4) 
        bottom_tools_vbox.setContentsMargins(0, 0, 0, 0)

        # --- 2.1 工具图标栏 ---
        icons_row = QHBoxLayout()
        icons_row.setSpacing(6)
        icons_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        icon_names = ["skin.svg", "view.svg", "add.svg", "sort.svg", "filter.svg"]
        for icon in icon_names:
            btn = QPushButton()
            pixmap = get_colored_icon(icon, "#FFFFFF", 16)
            if not pixmap.isNull(): btn.setIcon(QIcon(pixmap))
            btn.setIconSize(QSize(16, 16))
            btn.setFixedSize(24, 24)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("QPushButton { background: transparent; border: none; } QPushButton:hover { background: rgba(255,255,255,0.2); border-radius: 4px; }")
            
            # 绑定视图按钮事件
            if icon == "view.svg":
                self.btn_view_toggle = btn
                self.btn_view_toggle.clicked.connect(self.toggle_view_selector)
            elif icon == "add.svg":
                btn.clicked.connect(self._on_add_clicked)
                
            icons_row.addWidget(btn)
            
        bottom_tools_vbox.addLayout(icons_row)
        left_vbox.addSpacing(6)

        # 横向一排显示的视图选择器
        self.view_selector_container = QFrame()
        self.view_selector_container.setFixedHeight(20) 
        self.view_selector_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 4px;
            }
            QPushButton {
                background: transparent; color: white;
                font-family: 'Microsoft YaHei'; 
                font-size: 12px; /* 字体调小 */
                font-weight: bold;
                border-radius: 3px; 
                border: none; 
                padding: 0px 2px; /* 极限压缩内边距 */
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }
        """)
        
        vs_layout = QHBoxLayout(self.view_selector_container)
        vs_layout.setContentsMargins(2, 2, 2, 2)
        vs_layout.setSpacing(2)

        views = {"day": "日", "week": "周", "month": "月", "priority": "象限", "todo": "待办"}
        for vid, vname in views.items():
            v_btn = QPushButton(vname)
            v_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if vid == "month":
                v_btn.setStyleSheet("background-color: rgba(0, 0, 0, 0.2); color: white;")
            v_btn.clicked.connect(lambda _, v=vid: self._on_view_selected(v))
            vs_layout.addWidget(v_btn)

        self.view_selector_container.hide()
        bottom_tools_vbox.addWidget(self.view_selector_container)
        # --- 2.2 搜索框 ---
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索...")
        self.search_box.setFixedHeight(20)
        
        small_pixmap = get_colored_icon("search.svg", "#FFFFFF", 10)
        canvas = QPixmap(16, 16)
        canvas.fill(Qt.GlobalColor.transparent)
        painter = QPainter(canvas)
        painter.drawPixmap(3, 3, small_pixmap)
        painter.end()
        
        self.search_box.addAction(QIcon(canvas), QLineEdit.ActionPosition.LeadingPosition)
        self.search_box.setStyleSheet(StyleManager.get_search_input_style() + " QLineEdit { font-size: 11px; padding: 0px 3px; border-radius: 10px; }")
        
        bottom_tools_vbox.addWidget(self.search_box)

        self.inline_add_view = InlineAddViewMonth(self)
        self.inline_add_view.hide()
        self.inline_add_view.canceled.connect(self._close_add_view)
        self.inline_add_view.saved.connect(self._on_schedule_saved)
        bottom_tools_vbox.addWidget(self.inline_add_view)

        left_vbox.addLayout(bottom_tools_vbox)

        left_vbox.addStretch()
        content_layout.addWidget(left_panel)

        # --- 右侧面板 (大日历) ---
        right_panel = QWidget()
        right_vbox = QVBoxLayout(right_panel)
        right_vbox.setContentsMargins(12, 0, 0, 0)
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(False) 
        self.calendar.setNavigationBarVisible(False) 
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.currentPageChanged.connect(self._on_calendar_page_changed)
        self.calendar.clicked.connect(self.date_selected.emit)
        
        # ==========================================
        # 绘制挂载
        # ==========================================
        
        table_view = self.calendar.findChild(QTableView)
        
        self.cell_delegate = CalendarCellDelegate(
            self.height(), 
            AppConfig.COLOR_GRADIENT_START, 
            AppConfig.COLOR_GRADIENT_END,
            table_view,
            self.calendar
        )
        
        table_view.setItemDelegate(self.cell_delegate)
        
        self.calendar.setStyleSheet("""
            /* 1. 彻底剥离原生背景，砸碎 viewport 黑玻璃 */
            QCalendarWidget, QCalendarWidget > QWidget {
                background-color: transparent;
                border: none;
            }
            
            /* 2. 表格与表头全部透明，去除所有原生边框 */
            QCalendarWidget QTableView {
                background-color: transparent;
                alternate-background-color: transparent;
                border: none !important;
                border-top: 0px solid transparent !important; /* 🔪 强制斩杀表头下的那根幽灵线 */
                outline: none;
            }
            
            /* 3. 表头 (周一到周日)：完全透明，彻底抹除两边凸出来的原生分割线 */
            QCalendarWidget QHeaderView, QCalendarWidget QHeaderView::section {
                background-color: transparent;
                color: white; 
                border: 0px solid transparent !important;     
                border-left: 0px solid transparent !important; 
                border-right: 0px solid transparent !important; 
                border-top: 0px solid transparent !important;
                border-bottom: 0px solid transparent !important;
                
                font-size: 13px;
                font-weight: bold;
                padding-bottom: 6px;
                padding-top: 6px;
            }
        """)
        
        right_vbox.addWidget(self.calendar)
        content_layout.addWidget(right_panel, stretch=1)
        main_layout.addWidget(content_area, stretch=1)

    def _build_schedule_marker_cache(self):
        marker_cache = {}
        marker_count_cache = {}
        today = datetime.date.today()
        grouped = {}

        for schedule in db_manager.get_all_schedules():
            if getattr(schedule, "status", 0) == 2:
                continue
            if getattr(schedule, "item_type", None) != "schedule":
                continue

            target_date = (
                schedule.start_time.date()
                if schedule.start_time
                else (schedule.end_time.date() if schedule.end_time else None)
            )
            if target_date is None:
                continue

            info = grouped.setdefault(
                target_date,
                {"has_any": False, "all_completed": True, "max_priority": None, "count": 0},
            )
            info["has_any"] = True
            info["count"] += 1

            if getattr(schedule, "status", 0) != 1:
                info["all_completed"] = False
                priority = int(getattr(schedule, "priority", 0))
                if info["max_priority"] is None or priority > info["max_priority"]:
                    info["max_priority"] = priority

        for target_date, info in grouped.items():
            marker_count_cache[target_date] = info["count"]
            if target_date < today:
                marker_cache[target_date] = (
                    QColor("#FFFFFF") if info["all_completed"] else QColor("#999999")
                )
                continue

            if info["max_priority"] is None:
                continue

            marker_cache[target_date] = {
                2: QColor("#FF4D4F"),
                1: QColor("#FAAD14"),
                0: QColor("#52C41A"),
            }.get(info["max_priority"], QColor("#52C41A"))

        return marker_cache, marker_count_cache

    def _refresh_schedule_marker_cache(self):
        self.schedule_marker_cache, self.schedule_marker_count_cache = self._build_schedule_marker_cache()
        self.cell_delegate.set_calendar_state(
            self.current_date.year(),
            self.current_date.month(),
            QDate.currentDate(),
            self.schedule_marker_cache,
            self.schedule_marker_count_cache,
        )
        self.calendar.updateCells()

    def _start_clock(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)
        self._update_time()

    def _update_time(self):
        self.lbl_time.setText(QTime.currentTime().toString("HH:mm"))

    def _prev_month(self):
        self.current_date = self.current_date.addMonths(-1)
        self.lbl_month.setText(f"{self.current_date.month()}月")
        self.calendar.setCurrentPage(self.current_date.year(), self.current_date.month())

    def _next_month(self):
        self.current_date = self.current_date.addMonths(1)
        self.lbl_month.setText(f"{self.current_date.month()}月")
        self.calendar.setCurrentPage(self.current_date.year(), self.current_date.month())

    def _on_calendar_page_changed(self, year, month):
        """当右侧日历通过滚轮等原生方式翻页时，同步更新左侧UI和内部状态"""
        # 1. 更新内部维护的时间状态 (固定到该月1号防止日期溢出)
        self.current_date = QDate(year, month, 1)
        # 2. 同步更新左侧月份标签
        self.lbl_month.setText(f"{month}月")
        self._refresh_schedule_marker_cache()

    # 绘制青色渐变背景与T形切割线
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path.addRoundedRect(rect, 8.0, 8.0)
        
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START)) 
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))   
        painter.fillPath(path, QBrush(gradient))
        
        painter.save()
        line_color = QColor("#ffffff")
        painter.setPen(QPen(line_color, 1)) 
        
        # A. 水平线条：顶栏高度 24px
        painter.drawLine(2, 24, self.width() - 2, 24)
        
        # B. 垂直线条：左边距(12) + 左侧面板(144) = 156
        painter.drawLine(156, 24, 156, self.height() - 2)
        
        painter.restore()

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_schedule_marker_cache()

    # 窗口拖拽逻辑
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.pos().y() < 24:
            self.drag_pos = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def update_weather_ui(self, data):
        if not data: return
        icon_code = data['icon']
        svg_path = f"assets/weather/{icon_code}-fill.svg"
        colored_pixmap = self._load_colored_svg(svg_path, "#FFFFFF", 30, 30) 
        if not colored_pixmap.isNull():
            self.lbl_weather_icon.setPixmap(colored_pixmap)
            self.lbl_weather_icon.setText("") 
        else:
            self.lbl_weather_icon.setText("❓")
            
        self.lbl_temp.setText(f"{data['temp']}°C")
        tooltip = f"{data['city']}: {data['text']} {data['temp']}°C"
        
        # 清除旧的事件过滤器（防内存泄漏）
        if hasattr(self.lbl_weather_icon, '_tooltip_filter'):
            self.lbl_weather_icon.removeEventFilter(self.lbl_weather_icon._tooltip_filter)
            self.lbl_temp.removeEventFilter(self.lbl_temp._tooltip_filter)
            self.lbl_weather_icon._tooltip_filter.deleteLater()
            self.lbl_temp._tooltip_filter.deleteLater()

        # 重新绑定
        self.lbl_weather_icon._tooltip_filter = ToolTipFilter(tooltip, self.lbl_weather_icon)
        self.lbl_weather_icon.installEventFilter(self.lbl_weather_icon._tooltip_filter)
        
        self.lbl_temp._tooltip_filter = ToolTipFilter(tooltip, self.lbl_temp)
        self.lbl_temp.installEventFilter(self.lbl_temp._tooltip_filter)

    def _load_colored_svg(self, icon_path, color_hex, width, height):
        """专业的 SVG 着色器：读取源文件 -> 画在透明画布上 -> SourceIn 叠加纯色"""
        renderer = QSvgRenderer(icon_path)
        if not renderer.isValid(): return QPixmap()
        ratio = self.devicePixelRatio()
        pixel_width = int(width * ratio)
        pixel_height = int(height * ratio)
        pixmap = QPixmap(pixel_width, pixel_height)
        pixmap.fill(Qt.GlobalColor.transparent)
        pixmap.setDevicePixelRatio(ratio)
        painter = QPainter(pixmap)
        renderer.render(painter, QRectF(0, 0, width, height))
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(QRectF(0, 0, width, height), QColor(color_hex))
        painter.end()
        return pixmap
    
    def toggle_view_selector(self):
        if self.view_selector_container.isVisible():
            self.close_view_selector()
        else:
            self.open_view_selector()

    def open_view_selector(self):
        self.search_box.hide() # 展开时隐藏搜索框
        self.view_selector_container.show()
        if hasattr(self, 'btn_view_toggle'):
            self.btn_view_toggle.setStyleSheet("QPushButton { background: rgba(255,255,255,0.3); border-radius: 4px; }")

    def close_view_selector(self):
        self.view_selector_container.hide()
        self.search_box.show() # 收起时恢复搜索框
        if hasattr(self, 'btn_view_toggle'):
            self.btn_view_toggle.setStyleSheet("QPushButton { background: transparent; border: none; } QPushButton:hover { background: rgba(255,255,255,0.2); border-radius: 4px; }")

    def _on_view_selected(self, vid):
        self.close_view_selector()
        if vid == "month":
            pass # 已经在月视图，无操作
        else:
            self.view_selected.emit(vid)

    def _on_add_clicked(self):
        # 1. 验证日期是否过期
        today = QDate.currentDate()
        # 这里验证的是“右侧日历当前选中的日期”，而不是月历翻到的月份
        selected_date = self.calendar.selectedDate() 
        
        if selected_date < today:
            self.show_toast("🚫 该日期已过期，无法添加日程")
            return
            
        # 2. 切换 UI
        if self.inline_add_view.isVisible():
            self._close_add_view()
        else:
            self.search_box.hide()
            self.view_selector_container.hide()
            self.inline_add_view.reset(selected_date)
            self.inline_add_view.show()

    def _close_add_view(self):
        self.inline_add_view.hide()
        self.search_box.show()

    def _on_schedule_saved(self):
        self.show_toast("✅ 添加日程成功")
        self._close_add_view()
        self._refresh_schedule_marker_cache()

    def show_toast(self, message):
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtCore import Qt, QTimer
        
        if hasattr(self, 'toast_label') and self.toast_label.isVisible():
            self.toast_label.close()
            
        self.toast_label = QLabel(message, self)
        self.toast_label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.75); color: white;
            padding: 10px 20px; border-radius: 6px;
            font-family: 'Microsoft YaHei'; font-size: 13px; font-weight: bold;
        """)
        self.toast_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.toast_label.adjustSize()
        self.toast_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) 
        
        # 居中显示在整个月视图窗口
        x = (self.width() - self.toast_label.width()) // 2
        y = (self.height() - self.toast_label.height()) // 2
        self.toast_label.move(x, y)
        self.toast_label.show()
        
        QTimer.singleShot(1500, self.toast_label.close)
