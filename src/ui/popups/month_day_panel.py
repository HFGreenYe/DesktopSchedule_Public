from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush


class MonthDayPanel(QWidget):
    closed = pyqtSignal(object)

    def __init__(self, qdate, schedules, parent=None):
        super().__init__(parent, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.panel_date = qdate
        self._closed_emitted = False

        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(12, 10, 12, 10)
        self._layout.setSpacing(6)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        self.date_label = QLabel()
        self.date_label.setStyleSheet(
            "color: #0cc0df; font-family: 'Microsoft YaHei'; font-size: 12px; font-weight: bold;"
        )
        header_layout.addWidget(self.date_label)
        header_layout.addStretch()

        self.btn_close = QPushButton("×")
        self.btn_close.setFixedSize(20, 20)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #666666;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.06);
                border-radius: 10px;
            }
        """)
        self.btn_close.clicked.connect(self.close)
        header_layout.addWidget(self.btn_close)
        self._layout.addLayout(header_layout)

        self.body_label = QLabel()
        self.body_label.setStyleSheet(
            "color: #333333; font-family: 'Microsoft YaHei'; font-size: 11px; background: transparent;"
        )
        self.body_label.setWordWrap(True)
        self._layout.addWidget(self.body_label)

        self.set_panel_data(qdate, schedules)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        painter.setPen(QPen(QColor(0, 0, 0, 26), 1))
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawRoundedRect(rect, 10, 10)
        super().paintEvent(event)

    def set_panel_data(self, qdate, schedules):
        self.panel_date = qdate
        week_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        self.date_label.setText(
            f"{qdate.toString('yyyy-MM-dd')} {week_names[qdate.dayOfWeek() - 1]}"
        )

        if not schedules:
            self.body_label.setText("无日程")
            self.adjustSize()
            return

        lines = []
        for schedule in schedules[:8]:
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

        if len(schedules) > 8:
            lines.append(f"... 共 {len(schedules)} 条")

        self.body_label.setText("\n".join(lines))
        self.adjustSize()

    def closeEvent(self, event):
        if not self._closed_emitted:
            self._closed_emitted = True
            self.closed.emit(self)
        super().closeEvent(event)
