from datetime import date

from PyQt6.QtCore import QPoint, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QGuiApplication, QLinearGradient, QPainter, QPainterPath
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.config import AppConfig


class ExportPeriodPickerPopup(QWidget):
    period_selected = pyqtSignal(int, int)

    def __init__(self, mode, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint,
        )
        if mode not in {"week", "month"}:
            raise ValueError(f"不支持的周期选择模式：{mode}")
        self.mode = mode
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(258, 146)
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 8, 10, 10)
        root.setSpacing(0)

        header = QHBoxLayout()
        header.setContentsMargins(4, 0, 0, 0)
        title = QLabel("选择周" if self.mode == "week" else "选择月份")
        title.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei UI'; "
            "font-size: 14px; font-weight: bold; background: transparent;"
        )
        close_button = QPushButton("×")
        close_button.setFixedSize(24, 24)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setStyleSheet(
            "QPushButton { color: white; background: transparent; border: none; "
            "font-size: 18px; } QPushButton:hover { background: #ff4d4f; "
            "border-radius: 4px; }"
        )
        close_button.clicked.connect(self.close)
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(close_button)
        root.addLayout(header)

        frame = QFrame()
        frame.setObjectName("exportPeriodPickerFrame")
        frame.setStyleSheet(
            "QFrame#exportPeriodPickerFrame { background-color: rgba(255,255,255,0.76); "
            "border: 2px solid white; border-radius: 7px; }"
        )
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(12, 10, 12, 10)
        frame_layout.setSpacing(10)

        combo_row = QHBoxLayout()
        combo_row.setContentsMargins(0, 0, 0, 0)
        combo_row.setSpacing(8)
        self.year_combo = self._create_combo()
        self.period_combo = self._create_combo()
        combo_row.addWidget(self.year_combo, 1)
        combo_row.addWidget(self.period_combo, 1)
        frame_layout.addLayout(combo_row)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.addStretch(1)
        confirm_button = QPushButton("确定")
        confirm_button.setFixedSize(68, 26)
        confirm_button.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_button.setStyleSheet(
            f"QPushButton {{ color: {AppConfig.COLOR_GRADIENT_START}; "
            "background: rgba(255,255,255,0.92); border: 1px solid white; "
            "border-radius: 5px; font-family: 'Microsoft YaHei UI'; }} "
            "QPushButton:hover { background: white; }"
        )
        confirm_button.clicked.connect(self._confirm_selection)
        button_row.addWidget(confirm_button)
        frame_layout.addLayout(button_row)
        root.addWidget(frame)

        current_year = date.today().year
        for year in range(current_year - 50, current_year + 51):
            self.year_combo.addItem(f"{year} 年", year)
        self.year_combo.currentIndexChanged.connect(self._update_periods)
        self._update_periods()

    def _create_combo(self):
        combo = QComboBox()
        combo.setFixedHeight(28)
        combo.setCursor(Qt.CursorShape.PointingHandCursor)
        combo.setStyleSheet(
            f"""
            QComboBox {{
                color: {AppConfig.COLOR_GRADIENT_START};
                background: white;
                border: 1px solid rgba(255,255,255,0.95);
                border-radius: 5px;
                padding-left: 8px;
                font-family: "Microsoft YaHei UI";
                font-size: 11px;
            }}
            QComboBox::drop-down {{ border: none; width: 22px; }}
            QComboBox QAbstractItemView {{
                color: {AppConfig.COLOR_GRADIENT_START};
                background: white;
                selection-color: white;
                selection-background-color: {AppConfig.COLOR_GRADIENT_START};
                outline: none;
            }}
            """
        )
        return combo

    def _update_periods(self):
        selected = self.period_combo.currentData()
        self.period_combo.blockSignals(True)
        self.period_combo.clear()
        if self.mode == "week":
            year = self.year_combo.currentData() or date.today().year
            week_count = date(int(year), 12, 28).isocalendar().week
            for week in range(1, week_count + 1):
                self.period_combo.addItem(f"第 {week:02d} 周", week)
        else:
            for month in range(1, 13):
                self.period_combo.addItem(f"{month:02d} 月", month)
        index = self.period_combo.findData(selected)
        self.period_combo.setCurrentIndex(max(0, index))
        self.period_combo.blockSignals(False)

    def set_selection(self, year, period):
        year_index = self.year_combo.findData(int(year))
        if year_index >= 0:
            self.year_combo.setCurrentIndex(year_index)
        self._update_periods()
        period_index = self.period_combo.findData(int(period))
        if period_index >= 0:
            self.period_combo.setCurrentIndex(period_index)

    def show_near(self, anchor):
        position = anchor.mapToGlobal(QPoint(anchor.width() + 8, 0))
        screen = QGuiApplication.screenAt(position) or QGuiApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            if position.x() + self.width() > available.right() + 1:
                position.setX(anchor.mapToGlobal(QPoint(-self.width() - 8, 0)).x())
            position.setX(
                max(available.left(), min(position.x(), available.right() - self.width() + 1))
            )
            position.setY(
                max(available.top(), min(position.y(), available.bottom() - self.height() + 1))
            )
        self.move(position)
        self.show()
        self.raise_()

    def _confirm_selection(self):
        year = self.year_combo.currentData()
        period = self.period_combo.currentData()
        if year is None or period is None:
            return
        self.period_selected.emit(int(year), int(period))
        self.close()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 8, 8)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        painter.fillPath(path, gradient)
