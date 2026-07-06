from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient

from ...config import AppConfig


class MonthDayHoverPreview(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setObjectName("MonthDayHoverPreview")
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMinimumWidth(150)
        self.setMaximumWidth(260)

        self.setStyleSheet("""
            QFrame#MonthDayHoverPreview {
                background-color: transparent;
                border: none;
            }
            QLabel {
                color: #FFFFFF;
                background: transparent;
                font-family: 'Microsoft YaHei';
            }
        """)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(11, 9, 11, 9)
        self._layout.setSpacing(4)

        self.date_label = QLabel()
        self.date_label.setStyleSheet(
            "font-size: 12px; font-weight: bold;"
        )
        self._layout.addWidget(self.date_label)

        self.body_label = QLabel()
        self.body_label.setStyleSheet("font-size: 11px;")
        self.body_label.setWordWrap(True)
        self.body_label.setMaximumWidth(238)
        self._layout.addWidget(self.body_label)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)

        gradient = QLinearGradient(0, 0, 0, self.height())
        start_color = QColor(AppConfig.COLOR_GRADIENT_START)
        end_color = QColor(AppConfig.COLOR_GRADIENT_END)
        start_color.setAlpha(153)
        end_color.setAlpha(153)
        gradient.setColorAt(0.0, start_color)
        gradient.setColorAt(1.0, end_color)

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor("#FFFFFF"), 2))
        painter.drawRoundedRect(rect, 8, 8)
        super().paintEvent(event)

    def set_preview_data(self, qdate, schedules):
        week_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        self.date_label.setText(
            f"{qdate.toString('yyyy-MM-dd')} {week_names[qdate.dayOfWeek() - 1]}"
        )

        if not schedules:
            self.body_label.setText("无日程")
            self.adjustSize()
            return

        lines = []
        for schedule in schedules[:6]:
            time_text = "--:--"
            start_time = getattr(schedule, "start_time", None)
            end_time = getattr(schedule, "end_time", None)
            if start_time:
                time_text = start_time.strftime("%H:%M")
            elif end_time:
                time_text = end_time.strftime("%H:%M")

            priority = int(getattr(schedule, "priority", 0))
            priority_text = {2: "高", 1: "中", 0: "低"}.get(priority, "低")
            status_text = "已完成" if getattr(schedule, "status", 0) == 1 else "未完成"
            title = getattr(schedule, "title", "") or "未命名日程"
            lines.append(f"{time_text}  {title}  [{priority_text}/{status_text}]")

        if len(schedules) > 6:
            lines.append(f"... 共 {len(schedules)} 条")

        self.body_label.setText("\n".join(lines))
        self.adjustSize()
