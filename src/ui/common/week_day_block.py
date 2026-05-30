from PyQt6.QtWidgets import QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from zhdate import ZhDate
from datetime import datetime, timedelta

from ..header import ToolTipFilter


class DayBlock(QFrame):
    """单独的日期方格"""
    clicked = pyqtSignal(QDate)
    double_clicked = pyqtSignal(QDate)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.date = QDate.currentDate()
        self.is_today = False
        self.is_selected = False

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(44)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 4, 2, 4)
        layout.setSpacing(2)

        self.lbl_day = QLabel("1")
        self.lbl_day.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_lunar = QLabel("初一")
        self.lbl_lunar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.lbl_day)
        layout.addWidget(self.lbl_lunar)

    def set_data(self, qdate, lunar_str):
        self.date = qdate
        self.is_today = (qdate == QDate.currentDate())

        day_text = f"今 {qdate.day()}" if self.is_today else str(qdate.day())
        self.lbl_day.setText(day_text)
        self.lbl_lunar.setText(lunar_str)
        self.update_style()

        # 计算完整的农历日期 (月份 + 日期)
        full_lunar_str = lunar_str
        try:
            py_date = qdate.toPyDate()
            lunar_date = ZhDate.from_datetime(datetime(py_date.year, py_date.month, py_date.day))
            month_names = ["正月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "冬月", "腊月"]
            day_names = ["", "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
                         "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
                         "廿一", "廿二", "廿三", "廿四", "廿5", "廿六", "廿七", "廿八", "廿九", "三十"]

            m_name = month_names[lunar_date.lunar_month - 1]
            d_name = day_names[lunar_date.lunar_day]
            full_lunar_str = f"{m_name}{d_name}"

            # 判断是否为除夕
            next_date = py_date + timedelta(days=1)
            next_lunar = ZhDate.from_datetime(datetime(next_date.year, next_date.month, next_date.day))
            if next_lunar.lunar_month == 1 and next_lunar.lunar_day == 1:
                full_lunar_str = f"{m_name}除夕"

        except Exception:
            pass  # 发生异常时，兜底使用原来的简写

        # 清除旧的悬浮事件
        if hasattr(self, '_tooltip_filter') and self._tooltip_filter:
            self.removeEventFilter(self._tooltip_filter)
            self._tooltip_filter.deleteLater()

        # 获取阳历字符串 (格式：X月X日)
        gregorian_str = f"{qdate.month()}月{qdate.day()}日"

        # 拼接最终的弹窗文本，使用 \n 换行
        tooltip_text = f"阳历：{gregorian_str}\n农历：{full_lunar_str}"

        # 绑定包含【阳历+农历】的悬浮气泡
        self._tooltip_filter = ToolTipFilter(tooltip_text, self)
        self.installEventFilter(self._tooltip_filter)

    def set_selected(self, selected):
        self.is_selected = selected
        self.update_style()

    def update_style(self):
        text_color = "#FFD700" if self.is_today else "#FFFFFF"
        self.lbl_day.setStyleSheet(f"color: {text_color}; font-size: 12px; font-weight: bold; font-family: 'Microsoft YaHei'; background: transparent;")
        self.lbl_lunar.setStyleSheet(f"color: {text_color}; font-size: 9px; font-family: 'Microsoft YaHei'; background: transparent;")

        if self.is_selected:
            self.setStyleSheet("DayBlock { background-color: rgba(0, 100, 100, 0.4); border-radius: 4px; }")
        else:
            self.setStyleSheet("DayBlock { background-color: transparent; border-radius: 4px; } DayBlock:hover { background-color: rgba(255, 255, 255, 0.15); }")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.date)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.date)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)
