from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMenu,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt, QRectF, QSize, pyqtSignal
from PyQt6.QtGui import QAction, QBrush, QColor, QIcon, QLinearGradient, QPainter, QPen

from ...config import AppConfig
from ..utils.icon_loader import load_colored_svg_pixmap


class _MonthScheduleItemFrame(QFrame):
    double_clicked = pyqtSignal(object)
    status_change_requested = pyqtSignal(object, int)

    def __init__(self, schedule, parent=None):
        super().__init__(parent)
        self.schedule = schedule

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.schedule)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        menu = self._build_context_menu()
        menu.exec(event.globalPos())
        event.accept()

    def _build_context_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(
            """
            QMenu {
                background-color: rgba(255, 255, 255, 0.96);
                border: 1px solid rgba(0, 0, 0, 0.10);
                border-radius: 6px;
                padding: 4px;
                color: #333333;
            }
            QMenu::item {
                padding: 6px 18px 6px 8px;
                border-radius: 4px;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
            }
            QMenu::item:selected {
                background-color: rgba(12, 192, 223, 0.14);
            }
            QMenu::item:disabled {
                color: #999999;
            }
            """
        )

        is_completed = int(getattr(self.schedule, "status", 0) or 0) == 1
        text = "未完成" if is_completed else "完成日程"
        target_status = 0 if is_completed else 1
        icon_name = "uncheck.svg" if is_completed else "check.svg"
        icon_pixmap = load_colored_svg_pixmap(
            f"assets/icons/{icon_name}",
            "#333333",
            16,
            16,
            self.devicePixelRatioF(),
        )
        action = QAction(QIcon(icon_pixmap), text, menu)
        action.triggered.connect(
            lambda: self.status_change_requested.emit(self.schedule, target_status)
        )
        menu.addAction(action)
        return menu


class _ElidedTitleLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._full_text = text
        self.setToolTip(text)
        self._update_elided_text()

    def setText(self, text):
        self._full_text = text or ""
        self.setToolTip(self._full_text)
        self._update_elided_text()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_elided_text()

    def sizeHint(self):
        hint = super().sizeHint()
        return QSize(0, hint.height())

    def minimumSizeHint(self):
        hint = super().minimumSizeHint()
        return QSize(0, hint.height())

    def _update_elided_text(self):
        available_width = max(self.contentsRect().width(), 0)
        display_text = self.fontMetrics().elidedText(
            self._full_text,
            Qt.TextElideMode.ElideRight,
            available_width,
        )
        if super().text() != display_text:
            super().setText(display_text)


class MonthDayPanel(QWidget):
    closed = pyqtSignal(object)
    schedule_double_clicked = pyqtSignal(object, object)
    schedule_status_requested = pyqtSignal(object, int)

    def __init__(self, qdate, schedules, parent=None):
        super().__init__(parent, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.panel_date = qdate
        self._closed_emitted = False
        self._drag_offset = None
        self.child_detail_popups = []

        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedWidth(280)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(14, 12, 14, 12)
        self._layout.setSpacing(8)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        self.date_label = QLabel()
        self.date_label.setWordWrap(True)
        self.date_label.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei'; font-size: 14px; font-weight: bold;"
        )
        header_layout.addWidget(self.date_label, 1)

        self.btn_close = QPushButton("×")
        self.btn_close.setFixedSize(22, 22)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.92);
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.18);
                border-radius: 11px;
            }
            """
        )
        self.btn_close.clicked.connect(self.close)
        header_layout.addWidget(self.btn_close, 0, Qt.AlignmentFlag.AlignTop)
        self._layout.addLayout(header_layout)

        self.empty_label = QLabel("当日暂无日程")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setWordWrap(True)
        self.empty_label.setStyleSheet(
            "color: rgba(255, 255, 255, 0.86); font-family: 'Microsoft YaHei'; "
            "font-size: 12px; padding: 18px 8px;"
        )
        self._layout.addWidget(self.empty_label)

        self.body_scroll = QScrollArea()
        self.body_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.body_scroll.setWidgetResizable(True)
        self.body_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.body_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.body_scroll.setStyleSheet(
            """
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.35);
                border-radius: 2px;
                min-height: 18px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
                background: transparent;
            }
            """
        )

        self.body_container = QWidget()
        self.body_container.setStyleSheet("background: transparent;")
        self.body_layout = QVBoxLayout(self.body_container)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(4)
        self.body_layout.addStretch()
        self.body_scroll.setWidget(self.body_container)
        self._layout.addWidget(self.body_scroll)

        self.summary_label = QLabel()
        self.summary_label.setStyleSheet(
            "color: rgba(255, 255, 255, 0.78); font-family: 'Microsoft YaHei'; font-size: 11px;"
        )
        self._layout.addWidget(self.summary_label)

        self.set_panel_data(qdate, schedules)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))

        painter.setPen(QPen(QColor(255, 255, 255, 110), 1))
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(rect, 12, 12)

        # 内框：距边缘 4px，2px 白线，无填充
        inner_rect = rect.adjusted(4, 4, -4, -4)
        painter.setPen(QPen(QColor("#FFFFFF"), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(inner_rect, 8, 8)

        super().paintEvent(event)

    def set_panel_data(self, qdate, schedules):
        self.panel_date = qdate
        week_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        self.date_label.setText(
            f"{qdate.toString('yyyy-MM-dd')} {week_names[qdate.dayOfWeek() - 1]}"
        )

        self._clear_schedule_items()

        if not schedules:
            self.empty_label.show()
            self.body_scroll.hide()
            self.summary_label.hide()
            self.adjustSize()
            return

        self.empty_label.hide()
        self.body_scroll.show()

        visible_items = schedules[:8]
        insert_at = self.body_layout.count() - 1
        for schedule in visible_items:
            self.body_layout.insertWidget(insert_at, self._build_schedule_item(schedule))
            insert_at += 1

        item_height = 30
        item_spacing = 4
        visible_height = len(visible_items) * item_height + max(len(visible_items) - 1, 0) * item_spacing
        self.body_scroll.setFixedHeight(min(visible_height + 2, 220))

        if len(schedules) > len(visible_items):
            self.summary_label.setText(f"... 共 {len(schedules)} 条")
        else:
            self.summary_label.setText(f"共 {len(schedules)} 条")
        self.summary_label.show()

        self.adjustSize()

    def _clear_schedule_items(self):
        while self.body_layout.count() > 1:
            item = self.body_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _build_schedule_item(self, schedule):
        item_frame = _MonthScheduleItemFrame(schedule)
        item_frame.setObjectName("monthDayPanelItem")
        item_frame.setFixedHeight(30)
        item_frame.setStyleSheet(
            """
            QFrame#monthDayPanelItem {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.22);
                border-radius: 7px;
            }
            """
        )

        layout = QHBoxLayout(item_frame)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        time_label = QLabel(self._format_time_text(schedule))
        time_label.setFixedWidth(40)
        time_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        time_label.setStyleSheet(
            "background: transparent; border: none; color: white; "
            "font-family: 'Segoe UI'; font-size: 11px; font-weight: bold;"
        )
        layout.addWidget(time_label)

        title_label = _ElidedTitleLabel(self._format_title_text(schedule))
        title_label.setMinimumWidth(0)
        title_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        title_label.setWordWrap(False)
        title_label.setStyleSheet(
            "background: transparent; border: none; color: white; "
            "font-family: 'Microsoft YaHei'; font-size: 11px; font-weight: bold;"
        )
        layout.addWidget(title_label, 1)

        meta_label = QLabel(
            f"{self._format_priority_text(schedule)}/{self._format_status_text(schedule)}"
        )
        meta_label.setFixedWidth(66)
        meta_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        meta_label.setStyleSheet(
            "background: transparent; border: none; color: rgba(255, 255, 255, 0.84); "
            "font-family: 'Microsoft YaHei'; font-size: 10px;"
        )
        layout.addWidget(meta_label)

        item_frame.double_clicked.connect(self._emit_schedule_double_clicked)
        item_frame.status_change_requested.connect(self.schedule_status_requested.emit)
        return item_frame

    def _emit_schedule_double_clicked(self, schedule):
        self.schedule_double_clicked.emit(schedule, self)

    def _format_time_text(self, schedule):
        start_time = getattr(schedule, "start_time", None)
        end_time = getattr(schedule, "end_time", None)
        if start_time:
            return start_time.strftime("%H:%M")
        if end_time:
            return end_time.strftime("%H:%M")
        return "--:--"

    def _format_title_text(self, schedule):
        return getattr(schedule, "title", "") or "未命名日程"

    def _format_priority_text(self, schedule):
        priority = int(getattr(schedule, "priority", 0))
        return {2: "高", 1: "中", 0: "低"}.get(priority, "低")

    def _format_status_text(self, schedule):
        return "已完成" if getattr(schedule, "status", 0) == 1 else "未完成"

    def register_child_detail_popup(self, popup):
        if popup is None:
            return

        self._prune_child_detail_popups()
        if popup in self.child_detail_popups:
            return

        self.child_detail_popups.append(popup)

        if hasattr(popup, "popup_closed"):
            popup.popup_closed.connect(self._handle_child_popup_closed)
        popup.destroyed.connect(lambda *_: self._unregister_child_detail_popup(popup))

    def _handle_child_popup_closed(self, popup):
        self._unregister_child_detail_popup(popup)

    def _unregister_child_detail_popup(self, popup):
        self.child_detail_popups = [child for child in self.child_detail_popups if child is not popup]

    def _prune_child_detail_popups(self):
        valid_popups = []
        for popup in self.child_detail_popups:
            try:
                if popup is not None:
                    valid_popups.append(popup)
            except RuntimeError:
                continue
        self.child_detail_popups = valid_popups

    def closeEvent(self, event):
        self._close_child_detail_popups()
        if not self._closed_emitted:
            self._closed_emitted = True
            self.closed.emit(self)
        super().closeEvent(event)

    def _close_child_detail_popups(self):
        for popup in list(self.child_detail_popups):
            try:
                if popup is not None and hasattr(popup, "close"):
                    popup.close()
            except RuntimeError:
                pass
        self.child_detail_popups.clear()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = None
            event.accept()
            return
        super().mouseReleaseEvent(event)
