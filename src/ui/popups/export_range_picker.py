from datetime import date

from PyQt6.QtCore import QEvent, QPoint, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QGuiApplication,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
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


class _PeriodBodyFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent; border: none;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        radius = 8.0
        path = QPainterPath()
        path.moveTo(rect.left(), rect.top())
        path.lineTo(rect.right(), rect.top())
        path.lineTo(rect.right(), rect.bottom() - radius)
        path.quadTo(
            rect.right(),
            rect.bottom(),
            rect.right() - radius,
            rect.bottom(),
        )
        path.lineTo(rect.left() + radius, rect.bottom())
        path.quadTo(
            rect.left(),
            rect.bottom(),
            rect.left(),
            rect.bottom() - radius,
        )
        path.closeSubpath()
        painter.fillPath(path, QColor(255, 255, 255, 179))
        painter.setPen(QPen(QColor("white"), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)


class ExportPeriodPickerPopup(QWidget):
    period_selected = pyqtSignal(int, int)

    def __init__(self, mode, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint,
        )
        if mode not in {"week", "month"}:
            raise ValueError(f"不支持的周期选择模式：{mode}")
        self.mode = mode
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(258, 146)
        self._drag_offset = None
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.header_holder = QWidget()
        self.header_holder.setFixedHeight(40)
        header = QHBoxLayout(self.header_holder)
        header.setContentsMargins(14, 6, 8, 4)
        self.title = QLabel("选择周" if self.mode == "week" else "选择月份")
        self.title.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei UI'; "
            "font-size: 14px; font-weight: bold; background: transparent;"
        )
        self.close_button = QPushButton("×", self)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setStyleSheet(
            "QPushButton { color: white; background: transparent; border: none; "
            "font-size: 18px; } QPushButton:hover { background: #ff4d4f; "
            "border-top-right-radius: 8px; border-bottom-left-radius: 4px; }"
        )
        self.close_button.clicked.connect(self.close)
        header.addWidget(self.title)
        header.addStretch(1)
        root.addWidget(self.header_holder)

        self.body_frame = _PeriodBodyFrame()
        self.body_frame.setObjectName("exportPeriodPickerFrame")
        frame_layout = QVBoxLayout(self.body_frame)
        frame_layout.setContentsMargins(14, 10, 14, 10)
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
        root.addWidget(self.body_frame, 1)

        self._drag_surfaces = (
            self.header_holder,
            self.title,
            self.body_frame,
        )
        for surface in self._drag_surfaces:
            surface.installEventFilter(self)
        self._update_close_button_position()

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

    def eventFilter(self, watched, event):
        if watched in self._drag_surfaces and self._handle_drag_event(event):
            return True
        return super().eventFilter(watched, event)

    def mousePressEvent(self, event):
        if self._handle_drag_event(event):
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._handle_drag_event(event):
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._handle_drag_event(event):
            return
        super().mouseReleaseEvent(event)

    def _handle_drag_event(self, event):
        if (
            event.type() == QEvent.Type.MouseButtonPress
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._drag_offset = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()
            return True
        if (
            event.type() == QEvent.Type.MouseMove
            and self._drag_offset is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return True
        if (
            event.type() == QEvent.Type.MouseButtonRelease
            and self._drag_offset is not None
        ):
            self._drag_offset = None
            event.accept()
            return True
        return False

    def _update_close_button_position(self):
        self.close_button.move(self.width() - self.close_button.width(), 0)
        self.close_button.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_close_button_position()

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
