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
    QFrame,
    QScrollBar,
)
from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
    QDate,
    QRect,
    QRectF,
    QSize,
    QEvent,
    QPoint,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPalette,
    QPen,
    QPixmap,
    QRegion,
    QTextCharFormat,
)
from PyQt6.QtSvg import QSvgRenderer
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


def _make_arrow_icon(svg_path, enabled_color="#ffffff", disabled_color="#bbbbbb"):
    """从 SVG 创建带正常/禁用双模式的 QIcon，禁用时自动变灰。"""
    renderer = QSvgRenderer(svg_path)
    icon = QIcon()
    for mode, color in [(QIcon.Mode.Normal, enabled_color),
                        (QIcon.Mode.Disabled, disabled_color)]:
        pm = QPixmap(64, 64)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        renderer.render(p)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        p.fillRect(pm.rect(), QColor(color))
        p.end()
        icon.addPixmap(pm, mode)
    return icon


class HighlightCalendarWidget(QCalendarWidget):
    """自定义日历控件：负责在有日程的日期下方画三色小圆点"""
    def __init__(
        self,
        parent=None,
        export_theme=False,
        schedule_markers=True,
    ):
        super().__init__(parent)
        self._export_theme = bool(export_theme)
        self._schedule_markers = bool(schedule_markers)
        self.date_status = {} # 字典，记录具体状态颜色
        self.update_schedule_dates()

    def update_schedule_dates(self):
        """扫描数据库，计算每天的综合状态：全完成(白) / 逾期(灰) / 待办(青)"""
        if not self._schedule_markers:
            self.updateCells()
            return
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

    def set_date_markers(self, date_status):
        self.date_status = dict(date_status or {})
        self.updateCells()

    def paintCell(self, painter, rect, date):
        """重写底层绘制：自己控制所有绘制，不依赖 super() 的不可控背景"""
        if self._export_theme:
            self._paint_export_cell(painter, rect, date)
        else:
            self._paint_normal_cell(painter, rect, date)

        # 日程小圆点（两种模式共用）
        py_date = date.toPyDate()
        if py_date in self.date_status:
            status = self.date_status[py_date]

            if status == "white":
                color = QColor("#05e92a")
            elif status == "grey":
                color = QColor("#999999")
            elif status == "commemoration":
                color = QColor(AppConfig.COLOR_GRADIENT_START)
            else:
                color = QColor(_calendar_accent_color())

            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)

            dot_size = 4
            x = int(rect.center().x() - dot_size / 2)
            y = int(rect.bottom() - 1)

            painter.drawEllipse(x, y, dot_size, dot_size)
            painter.restore()

    def _paint_normal_cell(self, painter, rect, date):
        """非导出模式：不填充格子背景（透明→外层 paintEvent 提供背景）。
        支持 past_overlay（已过期日期浅灰底）和 marker（实线框标记日期）。
        颜色规则：今日=金，周末=红，工作日=灰黑，非本月=浅灰。"""
        painter.save()

        selected = date == self.selectedDate()
        in_current_month = (
            date.year() == self.yearShown() and date.month() == self.monthShown()
        )
        is_today = date == QDate.currentDate()
        dow = date.dayOfWeek()  # 1=Mon … 7=Sun

        past_overlay_date = getattr(self, '_past_overlay_date', None)
        marker_date = getattr(self, '_marker_date', None)

        # ── 图层 1：已过期 / 上月日期的浅灰底色 ──
        has_past_overlay = (
            past_overlay_date is not None
            and date < past_overlay_date
        )
        if has_past_overlay:
            painter.fillRect(rect, QColor("#e0e0e0"))

        # ── 图层 2：高亮（选中日期=主题色，开始日期=文字变色） ──
        is_marker = marker_date is not None and date == marker_date
        # 选中日期：主题色高亮
        if selected:
            highlight = QColor(_calendar_accent_color())
            highlight.setAlpha(120)
            painter.fillRect(rect.adjusted(5, 5, -5, -5), highlight)

        # ── 图层 3：文字颜色 ──
        if selected:
            text_color = QColor("white")
        elif is_marker:
            # 开始日期：文字用背景渐变色上沿（主题色）
            text_color = QColor(AppConfig.COLOR_GRADIENT_START)
        elif has_past_overlay:
            # 浅灰底上保持周末红 / 工作日灰黑，整体稍暗以区分
            if not in_current_month:
                text_color = QColor("#aaaaaa")
            elif dow in (6, 7):
                text_color = QColor("#cc3333")
            else:
                text_color = QColor("#555555")
        elif not in_current_month:
            text_color = QColor("#999999")
        elif dow in (6, 7):  # 周六 / 周日
            text_color = QColor("#ff3333")
        else:
            text_color = QColor("#333333")

        if is_today and not selected and not has_past_overlay and not is_marker:
            text_color = QColor("#FFD700")

        font = painter.font()
        font.setBold(is_today)
        painter.setFont(font)
        painter.setPen(text_color)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(date.day()))

        painter.restore()

    def _paint_export_cell(self, painter, rect, date):
        overlay_start = QColor(
            StyleManager.mix_colors(
                AppConfig.COLOR_GRADIENT_START,
                "#ffffff",
                0.30,
            )
        )
        overlay_end = QColor(
            StyleManager.mix_colors(
                AppConfig.COLOR_GRADIENT_END,
                "#ffffff",
                0.30,
            )
        )
        progress = max(0.0, min(1.0, rect.center().y() / max(1, self.height())))
        background = QColor(
            round(overlay_start.red() + (overlay_end.red() - overlay_start.red()) * progress),
            round(overlay_start.green() + (overlay_end.green() - overlay_start.green()) * progress),
            round(overlay_start.blue() + (overlay_end.blue() - overlay_start.blue()) * progress),
        )
        selected = date == self.selectedDate()
        painter.save()
        painter.fillRect(
            rect,
            QColor(_calendar_accent_color()) if selected else background,
        )

        in_current_month = (
            date.year() == self.yearShown() and date.month() == self.monthShown()
        )
        if selected:
            text_color = QColor("white")
        elif not in_current_month:
            text_color = QColor("#999999")
        elif date.dayOfWeek() in (Qt.DayOfWeek.Saturday, Qt.DayOfWeek.Sunday):
            text_color = QColor("red")
        else:
            text_color = QColor("#333333")
        is_today = date == QDate.currentDate()
        if is_today and not selected:
            text_color = QColor("#FAAD14")
        font = painter.font()
        font.setBold(is_today)
        painter.setFont(font)
        painter.setPen(text_color)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(date.day()))
        painter.restore()


class CalendarPop(QWidget):
    """悬浮日历弹窗容器"""
    date_selected = pyqtSignal(object) 

    def __init__(
        self,
        parent=None,
        export_theme=False,
        schedule_markers=True,
        close_on_select=True,
    ):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(225, 195)

        self._corner_radius = 8
        self._export_theme = bool(export_theme)
        self._schedule_markers = bool(schedule_markers)
        self._close_on_select = close_on_select
        self.drag_pos = None
        self.last_today = QDate.currentDate()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # 内边距防止日历尖角透出

        self.calendar = HighlightCalendarWidget(
            self,
            self._export_theme,
            self._schedule_markers,
        )
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
            # 显式禁用原生 QFrame 边框 + 滚动条，消除右下角直角
            calendar_view.setFrameStyle(QFrame.Shape.NoFrame)
            calendar_view.setLineWidth(0)
            calendar_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            calendar_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            # 隐藏所有 scrollbar 子控件
            for sb in calendar_view.findChildren(QScrollBar):
                sb.hide()
            # 替换 corner widget 为零尺寸透明占位
            corner = QWidget()
            corner.setFixedSize(0, 0)
            corner.setStyleSheet("background: transparent;")
            corner.setAutoFillBackground(False)
            calendar_view.setCornerWidget(corner)

        # 缩进日历内部布局，防止子控件越界到外层圆角区域
        cal_layout = self.calendar.layout()
        if cal_layout:
            cal_layout.setContentsMargins(2, 2, 2, 2)

        # 防止 Qt 用系统 palette 填充不透明背景，破坏圆角
        self.calendar.setAutoFillBackground(False)

        # 应用初始主题
        self._apply_theme()

        # --- 替换左右月份箭头（带禁用态自动变灰） ---
        prev_btn = self.calendar.findChild(QToolButton, "qt_calendar_prevmonth")
        if prev_btn:
            prev_btn.setIcon(_make_arrow_icon("assets/icons/cal_left.svg"))
            prev_btn.setIconSize(QSize(16, 16))

        next_btn = self.calendar.findChild(QToolButton, "qt_calendar_nextmonth")
        if next_btn:
            next_btn.setIcon(_make_arrow_icon("assets/icons/cal_right.svg"))
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
        self._nav_bar = nav_bar
        if nav_bar:
            nav_bar.installEventFilter(self)

    def _apply_theme(self):
        if self._export_theme:
            text_color = "#333333"
            disable_color = "#999999"
            nav_bg = "transparent"
            view_bg = f"background-color: {StyleManager.mix_colors(AppConfig.COLOR_GRADIENT_START, '#ffffff', 0.30)};"
            view_alt = StyleManager.mix_colors(AppConfig.COLOR_GRADIENT_START, "#ffffff", 0.30)
            menu_bg = "rgba(255, 255, 255, 0.96)"
        else:
            # 渐变色背景 + paintEvent 画白遮罩；QAbstractItemView 保持透明让遮罩透出
            text_color = "#333333"
            disable_color = "#999999"
            nav_bg = "transparent"
            view_bg = "background-color: transparent;"
            view_alt = "transparent"
            menu_bg = "rgba(255, 255, 255, 0.96)"

        calendar_accent = _calendar_accent_color()

        # 跟月界面一样：全部设透明，让 paintEvent 负责背景
        self.calendar.setStyleSheet(f"""
            QCalendarWidget, QCalendarWidget > QWidget {{
                background-color: transparent;
                border: none;
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background-color: {nav_bg};
            }}
            QCalendarWidget QTableView {{
                background-color: transparent;
                alternate-background-color: transparent;
                border: none !important;
                outline: none;
                frame-width: 0px;
            }}
            QAbstractScrollArea::corner {{
                background-color: transparent;
                border: none;
            }}
            QCalendarWidget QHeaderView, QCalendarWidget QHeaderView::section {{
                background-color: transparent;
                color: white;
                border: 0px solid transparent !important;
                font-size: 10px;
                font-weight: bold;
                padding-bottom: 4px;
                padding-top: 4px;
            }}
            QCalendarWidget QToolButton {{
                color: white; background-color: transparent; border: none;
                border-radius: 4px; padding: 4px; font-weight: bold;
                font-family: 'Microsoft YaHei'; font-size: 12px;
            }}
            QCalendarWidget QToolButton:disabled {{
                color: #555555;
            }}
            QCalendarWidget QToolButton::menu-indicator {{ image: none; }}
            QCalendarWidget QToolButton:hover {{ background-color: rgba(0, 0, 0, 0.15); }}
            QCalendarWidget QToolButton:pressed {{ background-color: rgba(0, 0, 0, 0.3); }}
            QCalendarWidget QMenu {{ background-color: {menu_bg}; color: {text_color}; border: 1px solid {calendar_accent}; }}
            QCalendarWidget QSpinBox {{
                background-color: transparent; color: white; border: none;
                font-weight: bold; font-family: 'Microsoft YaHei'; font-size: 12px;
                max-width: 42px; padding-right: 10px;
            }}
            QCalendarWidget QSpinBox::up-button {{
                subcontrol-origin: border; subcontrol-position: top right;
                width: 10px; height: 8px; margin-top: 4px; right: 2px;
            }}
            QCalendarWidget QSpinBox::down-button {{
                subcontrol-origin: border; subcontrol-position: bottom right;
                width: 10px; height: 8px; margin-bottom: 4px; right: 2px;
            }}
            QCalendarWidget QSpinBox::up-button:hover, QCalendarWidget QSpinBox::down-button:hover {{
                background-color: rgba(0, 0, 0, 0.2); border-radius: 2px;
            }}
            QCalendarWidget QAbstractItemView {{
                {view_bg}
                alternate-background-color: {view_alt};
                selection-background-color: {calendar_accent}; selection-color: white;
                font-family: 'Microsoft YaHei'; font-size: 11px; outline: 0px;
            }}
            QCalendarWidget QAbstractItemView:disabled {{
                color: {disable_color}; background-color: transparent;
            }}
        """)
        if self._export_theme:
            calendar_view = self.calendar.findChild(QTableView, "qt_calendar_calendarview")
            if calendar_view is not None:
                calendar_view.viewport().setStyleSheet(view_bg)
                view_palette = calendar_view.palette()
                view_palette.setColor(QPalette.ColorRole.Base, QColor(view_alt))
                view_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(view_alt))
                calendar_view.setPalette(view_palette)
                calendar_view.viewport().setPalette(view_palette)

        # ── 圆角修复：递归透明化日历控件及其所有子控件 ──
        # stylesheet 设了 transparent，但 Qt 内部 delegate / corner widget /
        # scrollbar 等控件可能从 palette 取色画不透明背景，必须逐层清零。
        transparent = QColor(0, 0, 0, 0)
        window_roles = (
            QPalette.ColorRole.Window,
            QPalette.ColorRole.Base,
            QPalette.ColorRole.AlternateBase,
            QPalette.ColorRole.Button,
        )

        def _make_transparent(widget):
            """递归将 widget 及其所有子控件的背景 palette 色值清零"""
            w_pal = widget.palette()
            for role in window_roles:
                w_pal.setColor(role, transparent)
            widget.setPalette(w_pal)
            widget.setAutoFillBackground(False)
            for child in widget.findChildren(QWidget):
                c_pal = child.palette()
                for role in window_roles:
                    c_pal.setColor(role, transparent)
                child.setPalette(c_pal)
                child.setAutoFillBackground(False)

        _make_transparent(self.calendar)
        # ────────────────────────────────────────────────────────────

        self._update_today_highlight()

    def _update_today_highlight(self):
        """标黄今天的日期，并处理跨天刷新逻辑"""
        today = QDate.currentDate()
        today_color = "#FAAD14" if self._export_theme else "#FFD700"
        
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
        """仅保留顶栏拖拽事件"""
        nav_bar = self.calendar.findChild(QWidget, "qt_calendar_navigationbar")
        if obj == nav_bar:
            if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
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

        outer_path = QPainterPath()
        outer_path.addRoundedRect(QRectF(self.rect()), self._corner_radius, self._corner_radius)

        # 背景：主界面渐变色
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        painter.fillPath(outer_path, gradient)

        # 头部以下：70% 白色不透明遮罩
        header_bottom = 32
        if self._nav_bar is not None:
            header_bottom = self.calendar.mapTo(self, QPoint(0, self._nav_bar.geometry().bottom())).y() + 1
        overlay_alpha = 179 if self._export_theme else 178  # ~70%
        painter.save()
        painter.setClipPath(outer_path)
        painter.fillRect(
            QRectF(0, header_bottom, self.width(), self.height() - header_bottom),
            QColor(255, 255, 255, overlay_alpha),
        )
        # 灰色圆角边缘
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
        painter.drawRoundedRect(
            QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5),
            self._corner_radius,
            self._corner_radius,
        )

        painter.restore()

    def show_at(self, pos, current_date=None):
        self._apply_theme()
        self.calendar.update_schedule_dates()
        if current_date:
            self.calendar.setSelectedDate(QDate(current_date.year, current_date.month, current_date.day))
        self.move(pos.x() - 112, pos.y() + 4)
        self.show()

    def set_past_overlay_date(self, qdate):
        """设置在日历中显示浅灰底色的「已过期」日期分界线。
        qdate 之前的日期格子会被铺上不透明浅灰底色。"""
        self.calendar._past_overlay_date = qdate
        self.calendar.updateCells()

    def set_marker_date(self, qdate):
        """设置虚线框标记的日期（用于完成时间日历中的开始日期标注）。
        qdate 为 None 则清除标记。"""
        self.calendar._marker_date = qdate
        self.calendar.updateCells()

    def _on_date_clicked(self, qdate):
        py_date = qdate.toPyDate()
        self.date_selected.emit(py_date)
        if self._close_on_select:
            self.close()
