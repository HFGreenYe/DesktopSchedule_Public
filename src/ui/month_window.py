# src/ui/month_window.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QToolButton, QLineEdit, 
                             QCalendarWidget, QApplication, QTableView, 
                             QStyledItemDelegate, QStyle, QStyleOptionViewItem,
                             QGridLayout, QTextEdit, QComboBox, QListView,
                             QStyleOptionComboBox, QStylePainter, QMessageBox,
                             QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QTime, QTimer, QRectF, QSize, QEvent
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QBrush, QLinearGradient, QIcon, QPen, QPalette, QPixmap, QGuiApplication
from PyQt6.QtSvg import QSvgRenderer
from qframelesswindow import FramelessMainWindow
import datetime

from ..config import AppConfig
from ..data.database import db_manager
from ..utils.win_api import apply_24h2_border_fix
from ..utils.styles import StyleManager
from .header import ToolTipFilter
from .components import IOSSwitch, get_colored_icon, SharedMoreMenu
from .common.action_context_menu import ActionContextMenu
from .common.weather_icon_label import WeatherIconLabel
from .time_picker import TimePickerView
from .alarm_picker import AlarmPickerView
from .list_picker import CategoryCard, ListPickerView
from .popups.month_day_hover_preview import MonthDayHoverPreview
from .popups.month_day_panel import MonthDayPanel


class CenteredComboBox(QComboBox):
    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionComboBox()
        self.initStyleOption(option)
        current_text = self.currentText().strip()
        option.currentText = ""
        painter.drawComplexControl(QStyle.ComplexControl.CC_ComboBox, option)
        text_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_ComboBox,
            option,
            QStyle.SubControl.SC_ComboBoxEditField,
            self,
        )
        painter.setPen(QColor("#ffffff"))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, current_text)


class MonthListPickerView(ListPickerView):
    """月界面左栏专用的紧凑清单选择器。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._apply_compact_layout()

    def _apply_compact_layout(self):
        self.header_container.setFixedHeight(28)
        self.header_container.layout().setContentsMargins(4, 0, 30, 0)
        self.set_title(self.lbl_title.text())

        self.btn_suspend.hide()
        self.btn_close.show()
        self.btn_close.setIconSize(QSize(12, 12))
        self.btn_close.setFixedSize(24, 24)
        try:
            self.btn_close.clicked.disconnect()
        except TypeError:
            pass
        self.btn_close.clicked.connect(self.back_requested.emit)
        self.btn_close.raise_()

        self.content_layout.setContentsMargins(0, 4, 0, 4)
        self.content_layout.setSpacing(6)
        self.cards_layout.setSpacing(6)

        self.input_container.setFixedHeight(30)
        self.input_container.layout().setSpacing(4)
        self.input_new.setFixedHeight(28)
        self.btn_confirm_add.setFixedSize(28, 28)
        self.btn_confirm_add.setStyleSheet("""
            QPushButton {
                background-color: #0cc0df;
                border: 1px solid white;
                border-radius: 14px;
                color: white;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #0bb0cf; }
        """)

        footer_layout = self.footer_container.layout()
        footer_layout.setContentsMargins(0, 8, 0, 0)
        footer_layout.setSpacing(4)
        self.footer_container.setFixedHeight(32)
        for button in (self.btn_add_new, self.btn_cancel, self.btn_ok):
            button.setFixedSize(38, 24)
        self.btn_cancel.setText("取消")
        self.btn_add_new.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255,255,255,0.6);
                border-radius: 12px;
                color: white;
                font-size: 10px;
                font-family: 'Microsoft YaHei';
            }
            QPushButton:hover { background: rgba(255,255,255,0.15); }
        """)
        self.btn_cancel.setStyleSheet(self.btn_add_new.styleSheet())
        self.btn_ok.setStyleSheet("""
            QPushButton {
                background: white;
                border: none;
                border-radius: 12px;
                color: #0cc0df;
                font-size: 10px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
            }
            QPushButton:hover { background: #f0f0f0; }
        """)

    def set_title(self, text="选择清单"):
        compact_text = "修改清单" if text.startswith("修改") else text
        self.lbl_title.setText(compact_text)
        self.lbl_title.setStyleSheet(
            "color: white; font-size: 12px; font-weight: bold; "
            "font-family: 'Microsoft YaHei';"
        )

    def load_data(self, current_selected_id=None, list_type=None):
        super().load_data(current_selected_id, list_type)
        for card in self.cards_container.findChildren(CategoryCard):
            card.setFixedHeight(28)
            card.layout.setContentsMargins(8, 0, 6, 0)
            card.layout.setSpacing(4)
            spacer = card.layout.itemAt(1).spacerItem()
            if spacer is not None:
                spacer.changeSize(4, 0)
            card.dot.setFixedSize(6, 6)
            card.dot.setStyleSheet("background-color: #0cc0df; border-radius: 3px;")
            card.lbl_name.setStyleSheet(
                "color: white; font-size: 11px; font-weight: bold; "
                "font-family: 'Microsoft YaHei';"
            )
            card.lbl_check.setStyleSheet(
                "color: #0cc0df; font-size: 12px; font-weight: bold;"
            )


class MonthCompactSwitch(IOSSwitch):
    """月界面窄栏专用开关，不改变共享 IOSSwitch 的尺寸。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(19, 12)
        self._thumb_diameter = 9.0
        self._thumb_inset = 1.5
        self.setChecked(self.isChecked())

    def _checked_thumb_x(self):
        return float(self.width() - self._thumb_inset - self._thumb_diameter)

    def setChecked(self, checked):
        self.anim.stop()
        self._checked = bool(checked)
        self._thumb_x = (
            self._checked_thumb_x() if self._checked else float(self._thumb_inset)
        )
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            super().mouseReleaseEvent(event)
            return
        self._checked = not self._checked
        self.anim.setStartValue(self._thumb_x)
        self.anim.setEndValue(
            self._checked_thumb_x() if self._checked else float(self._thumb_inset)
        )
        self.anim.start()
        self.toggled.emit(self._checked)
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 6, 6)
        painter.fillPath(path, QColor("#0cc0df" if self._checked else "#e0e0e0"))
        painter.setBrush(Qt.GlobalColor.white)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            QRectF(
                self._thumb_x,
                self._thumb_inset,
                self._thumb_diameter,
                self._thumb_diameter,
            )
        )


class MonthTimePickerView(TimePickerView):
    """月界面左栏专用的紧凑时间选择器。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._apply_compact_layout()

    def _apply_compact_layout(self):
        header_container = self.lbl_title.parentWidget()
        header_container.setFixedHeight(28)
        header_container.layout().setContentsMargins(4, 0, 30, 0)
        self.set_title(self.lbl_title.text())
        self.btn_suspend.hide()
        self.btn_close.show()
        self.btn_close.setIconSize(QSize(12, 12))
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.raise_()

        self.content_layout.setContentsMargins(0, 4, 0, 4)
        self.content_layout.setSpacing(6)

        self.btn_date.setFixedSize(136, 28)
        self.btn_date.setIcon(self._get_colored_icon("assets/icons/calendar.svg", "#FFFFFF"))
        self.btn_date.setIconSize(QSize(14, 14))
        self.btn_date.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.18);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                color: white;
                font-size: 11px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
                text-align: left;
                padding-left: 8px;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.28); }
        """)

        self.calendar.setFixedSize(136, 122)
        self.calendar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.calendar.setStyleSheet(StyleManager.get_calendar_style() + """
            QCalendarWidget QToolButton {
                font-size: 8px;
                icon-size: 10px;
                min-width: 14px;
                min-height: 16px;
            }
            QCalendarWidget QAbstractItemView:enabled { font-size: 8px; }
            QCalendarWidget QTableHeaderView::section {
                font-size: 8px;
                padding: 0px;
            }
        """)
        for object_name in ("qt_calendar_prevmonth", "qt_calendar_nextmonth"):
            button = self.calendar.findChild(QToolButton, object_name)
            if button is not None:
                button.setIconSize(QSize(10, 10))

        self._replace_enable_switch()
        for label in self.content_widget.findChildren(QLabel):
            if label.text() == "启用开始时间":
                label.setAlignment(
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                )
                label.setStyleSheet("color: white; font-size: 10px; font-weight: bold;")
            elif label.text() in {"开始时间", "完成时间"}:
                label.setStyleSheet(
                    "color: rgba(255,255,255,0.7); font-size: 9px; margin-bottom: 2px;"
                )

        self.time_picker_container.setFixedWidth(136)
        self.time_picker_container.setStyleSheet("""
            QWidget#TimeContainer {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
        """)
        time_layout = self.time_picker_container.layout()
        time_layout.setContentsMargins(2, 4, 2, 4)
        time_layout.setSpacing(2)
        self.start_group.setFixedWidth(65)
        self.end_group.setFixedWidth(65)
        for scroller in (
            self.scroll_start_hour,
            self.scroll_start_min,
            self.scroll_end_hour,
            self.scroll_end_min,
        ):
            self._compact_scroller(scroller)
        for group in (self.start_scroller_widget, self.end_scroller_widget):
            for colon in group.findChildren(QLabel):
                colon.setFixedWidth(6)
                colon.setStyleSheet(
                    "color: white; font-size: 12px; font-weight: bold; padding-bottom: 2px;"
                )

        self.duration_grid.setFixedWidth(136)
        duration_layout = self.duration_grid.layout()
        duration_layout.setSpacing(2)
        for button in self.duration_grid.findChildren(QPushButton):
            button.setFixedHeight(20)
            button.setMinimumWidth(0)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.15);
                    border-radius: 4px;
                    color: white;
                    border: 1px solid rgba(255,255,255,0.2);
                    font-size: 8px;
                }
                QPushButton:hover { background-color: rgba(255, 255, 255, 0.3); }
            """)

        footer_container = self.btn_cancel.parentWidget()
        footer_layout = footer_container.layout()
        footer_layout.setContentsMargins(0, 8, 0, 0)
        footer_layout.setSpacing(8)
        footer_container.setFixedHeight(32)
        for button in (self.btn_cancel, self.btn_ok):
            button.setFixedHeight(24)
            button.setMinimumWidth(0)
            button.setMaximumWidth(16777215)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255,255,255,0.5);
                border-radius: 12px;
                color: white;
                font-size: 11px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.1); }
        """)
        self.btn_ok.setStyleSheet("""
            QPushButton {
                background: white;
                border: none;
                border-radius: 12px;
                color: #0cc0df;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover { background: #f0f0f0; }
        """)

    def _replace_enable_switch(self):
        old_switch = self.chk_enable_start
        switch_layout = None
        switch_item_index = -1
        for index in range(self.content_layout.count()):
            candidate = self.content_layout.itemAt(index).layout()
            if candidate is not None and candidate.indexOf(old_switch) >= 0:
                switch_layout = candidate
                switch_item_index = index
                break
        if switch_layout is None:
            return

        label = None
        for index in range(switch_layout.count()):
            widget = switch_layout.itemAt(index).widget()
            if isinstance(widget, QLabel) and widget.text() == "启用开始时间":
                label = widget
                break
        if label is None:
            label = QLabel("启用开始时间", self.content_widget)

        checked = old_switch.isChecked()
        switch_layout.removeWidget(label)
        switch_layout.removeWidget(old_switch)
        old_switch.hide()
        old_switch.deleteLater()

        row_widget = QWidget(self.content_widget)
        row_widget.setFixedWidth(136)
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(4)

        label.setParent(row_widget)
        row_layout.addWidget(label, 0, Qt.AlignmentFlag.AlignVCenter)
        row_layout.addStretch()

        compact_switch = MonthCompactSwitch(row_widget)
        compact_switch.setChecked(checked)
        compact_switch.toggled.connect(self._on_switch_toggled)
        row_layout.addWidget(compact_switch, 0, Qt.AlignmentFlag.AlignVCenter)

        if switch_item_index >= 0:
            self.content_layout.takeAt(switch_item_index)
            self.content_layout.insertWidget(switch_item_index, row_widget)
        self.chk_enable_start = compact_switch

    def _compact_scroller(self, scroller):
        scroller.item_height = 20
        scroller.setFixedSize(26, 60)
        scroller.setStyleSheet("""
            QListWidget { background: transparent; outline: none; }
            QListWidget::item {
                height: 20px;
                color: rgba(255, 255, 255, 0.4);
                font-size: 9px;
                font-family: 'Microsoft YaHei';
                border: none;
            }
            QListWidget::item:selected {
                background: transparent;
                color: #FFFFFF;
                font-size: 11px;
                font-weight: bold;
            }
        """)

    def set_title(self, text="设置时间"):
        compact_text = "修改时间" if text.startswith("修改") else "设置时间"
        self.lbl_title.setText(compact_text)
        self.lbl_title.setStyleSheet(
            "color: white; font-size: 12px; font-weight: bold; "
            "font-family: 'Microsoft YaHei';"
        )


class MonthAlarmPickerView(AlarmPickerView):
    """月界面左栏专用的紧凑提醒选择器。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._apply_compact_layout()

    def _apply_compact_layout(self):
        header_container = self.lbl_title.parentWidget()
        header_container.setFixedHeight(28)
        header_container.layout().setContentsMargins(4, 0, 30, 0)
        self.set_title(self.lbl_title.text())
        self.btn_suspend.hide()
        self.btn_close.show()
        self.btn_close.setIconSize(QSize(12, 12))
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.raise_()

        self.content.setContentsMargins(0, 4, 0, 4)
        self.content.setSpacing(6)

        for label in self.content_widget.findChildren(QLabel):
            text = label.text()
            if text == "提醒时间":
                label.setAlignment(
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                )
                label.setFixedWidth(136)
                label.setStyleSheet(
                    "color: rgba(255,255,255,0.75); font-size: 9px; "
                    "font-weight: bold;"
                )
            elif text == "设置为前一天":
                label.setAlignment(
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                )
                label.setStyleSheet("color: white; font-size: 10px; font-weight: bold;")
            elif text == "强提醒 (有声模式)":
                label.setText("强提醒")
                label.setStyleSheet("color: white; font-size: 10px; font-weight: bold;")
            elif text == "持续响铃时长":
                label.setStyleSheet(
                    "color: rgba(255,255,255,0.75); font-size: 9px; "
                    "font-weight: bold;"
                )

        self._replace_switch_row(
            self.switch_prev_day,
            self._validate_time,
            row_width=136,
        )
        self._replace_switch_row(
            self.switch_alarm,
            self._toggle_alarm_options,
            row_width=136,
        )

        self.day_select_container.setFixedWidth(136)
        day_layout = self.day_select_container.layout()
        day_layout.setContentsMargins(0, 0, 0, 0)
        day_layout.setSpacing(4)

        self.time_container.setFixedSize(136, 80)
        self.time_container.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
        """)
        time_layout = self.time_container.layout()
        time_layout.setContentsMargins(20, 4, 20, 4)
        time_layout.setSpacing(6)
        for scroller in (self.scroll_h, self.scroll_m):
            self._compact_scroller(scroller)
        for colon in self.time_container.findChildren(QLabel):
            if colon.text() == ":":
                colon.setFixedWidth(8)
                colon.setStyleSheet(
                    "color: white; font-size: 12px; font-weight: bold; "
                    "background: transparent;"
                )

        self.quick_grid.setFixedWidth(136)
        quick_layout = self.quick_grid.layout()
        quick_layout.setSpacing(2)
        for button in self.quick_btns:
            button.setFixedHeight(20)
            button.setMinimumWidth(0)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setStyleSheet(self._get_btn_style())

        self.alarm_opts_container.setFixedWidth(136)
        alarm_opts_layout = self.alarm_opts_container.layout()
        alarm_opts_layout.setSpacing(4)
        alarm_btn_layout = alarm_opts_layout.itemAt(1).layout()
        if alarm_btn_layout is not None:
            alarm_btn_layout.setSpacing(2)
        for button in self.alarm_group.buttons():
            button.setFixedHeight(20)
            button.setMinimumWidth(0)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.15);
                    border-radius: 4px;
                    color: white;
                    border: 1px solid rgba(255,255,255,0.2);
                    font-size: 8px;
                }
                QPushButton:checked {
                    background-color: #0cc0df;
                    border-color: white;
                    color: white;
                    font-weight: bold;
                }
            """)

        footer_container = self.btn_cancel.parentWidget()
        footer_layout = footer_container.layout()
        footer_layout.setContentsMargins(0, 8, 0, 0)
        footer_layout.setSpacing(8)
        footer_container.setFixedHeight(32)
        for button in (self.btn_cancel, self.btn_ok):
            button.setFixedHeight(24)
            button.setMinimumWidth(0)
            button.setMaximumWidth(16777215)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255,255,255,0.5);
                border-radius: 12px;
                color: white;
                font-size: 11px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.1); }
        """)
        self.btn_ok.setStyleSheet("""
            QPushButton {
                background: white;
                border: none;
                border-radius: 12px;
                color: #0cc0df;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover { background: #f0f0f0; }
        """)

    def _replace_switch_row(self, old_switch, callback, row_width):
        parent_layout = None
        item_index = -1
        for index in range(self.content.count()):
            item = self.content.itemAt(index)
            candidate = item.layout()
            if candidate is not None and candidate.indexOf(old_switch) >= 0:
                parent_layout = candidate
                item_index = index
                break
            widget = item.widget()
            if widget is not None and widget.layout() is not None:
                candidate = widget.layout()
                if candidate.indexOf(old_switch) >= 0:
                    parent_layout = candidate
                    item_index = index
                    break
        if parent_layout is None:
            return

        checked = old_switch.isChecked()
        parent_layout.removeWidget(old_switch)
        old_switch.setParent(None)
        old_switch.deleteLater()

        compact_switch = MonthCompactSwitch(self.content_widget)
        compact_switch.setChecked(checked)
        compact_switch.toggled.connect(callback)

        switch_index = parent_layout.count()
        parent_layout.insertWidget(
            switch_index,
            compact_switch,
            0,
            Qt.AlignmentFlag.AlignVCenter,
        )
        if old_switch is self.switch_prev_day:
            self.switch_prev_day = compact_switch
        elif old_switch is self.switch_alarm:
            self.switch_alarm = compact_switch

        if item_index >= 0:
            item = self.content.itemAt(item_index)
            widget = item.widget()
            if widget is not None:
                widget.setFixedWidth(row_width)

    def _compact_scroller(self, scroller):
        scroller.item_height = 20
        scroller.setFixedSize(34, 60)
        scroller.setStyleSheet("""
            QListWidget { background: transparent; outline: none; }
            QListWidget::item {
                height: 20px;
                color: rgba(255, 255, 255, 0.4);
                font-size: 9px;
                font-family: 'Microsoft YaHei';
                border: none;
            }
            QListWidget::item:selected {
                background: transparent;
                color: #FFFFFF;
                font-size: 11px;
                font-weight: bold;
            }
        """)

    def _get_btn_style(self):
        return """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 4px;
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
                font-size: 8px;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.3); }
        """

    def set_title(self, text="设置提醒"):
        compact_text = "修改提醒" if text.startswith("修改") else "设置提醒"
        self.lbl_title.setText(compact_text)
        self.lbl_title.setStyleSheet(
            "color: white; font-size: 12px; font-weight: bold; "
            "font-family: 'Microsoft YaHei';"
        )


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
        self.user_selected_date = None

    def set_calendar_state(self, visible_year, visible_month, today_date, marker_cache, marker_count_cache=None, user_selected_date=None):
        self.visible_year = visible_year
        self.visible_month = visible_month
        self.today_date = today_date
        self.marker_cache = dict(marker_cache)
        self.marker_count_cache = dict(marker_count_cache or {})
        self.user_selected_date = user_selected_date

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
            if self.user_selected_date is not None and cell_date == self.user_selected_date:
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
    req_open_time_picker = pyqtSignal(object, object)
    req_open_alarm_picker = pyqtSignal(object, bool, int)
    req_open_list_picker = pyqtSignal(object, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_date = None
        self.is_schedule_mode = True
        self.selected_start_time = None
        self.selected_end_time = None
        self.selected_reminder = None
        self.selected_alarm_duration = 0
        self.selected_list_id = None
        self.selected_list_name = None
        self.selected_is_alarm_mode = False
        self._setup_ui()
        self._update_summary_labels()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 3, 0, 0)
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
        self.input_desc.setFixedHeight(75)
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

        self.btn_time = self._create_icon_btn("time.svg", "时间设置待接入")
        self.btn_alarm = self._create_icon_btn("alarm.svg", "提醒设置待接入")
        self.btn_list = self._create_icon_btn("list.svg", "清单选择待接入")
        self.btn_font = self._create_icon_btn("theme.svg", "字体设置待接入")

        self.btn_time.clicked.connect(
            lambda: self.req_open_time_picker.emit(self.selected_start_time, self.selected_end_time)
        )
        self.btn_alarm.clicked.connect(self._emit_alarm_request)
        self.btn_list.clicked.connect(
            lambda: self.req_open_list_picker.emit(self.selected_list_id, "schedule")
        )

        for button in (self.btn_time, self.btn_alarm, self.btn_list, self.btn_font):
            icons_layout.addWidget(button, 1, Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(icons_layout)

        # 4. 轻量状态壳：重要性 / 重复
        shell_row = QHBoxLayout()
        shell_row.setContentsMargins(0, 0, 0, 0)
        shell_row.setSpacing(3)

        self.repeat_value_map = {
            "无": "无",
            "日": "每天",
            "周": "每周",
            "月": "每月",
        }

        self.lbl_priority = QLabel("重要性")
        self.lbl_priority.setStyleSheet("color: rgba(255,255,255,0.85); font-size: 11px; font-family: 'Microsoft YaHei';")
        self.lbl_priority.setFixedWidth(36)
        self.combo_priority = CenteredComboBox()
        self.combo_priority.setView(QListView())
        self.combo_priority.addItems(["高", "中", "低"])
        self.combo_priority.setCurrentIndex(2)
        self.combo_priority.setFixedHeight(22)
        self.combo_priority.setFixedWidth(30)
        self._center_combo_text(self.combo_priority)
        self.combo_priority.setStyleSheet(self._combo_style())

        self.lbl_repeat = QLabel("重复")
        self.lbl_repeat.setStyleSheet("color: rgba(255,255,255,0.85); font-size: 11px; font-family: 'Microsoft YaHei';")
        self.lbl_repeat.setFixedWidth(24)
        self.combo_repeat = CenteredComboBox()
        self.combo_repeat.setView(QListView())
        self.combo_repeat.addItems(["无", "日", "周", "月"])
        self.combo_repeat.setFixedHeight(22)
        self.combo_repeat.setFixedWidth(30)
        self._center_combo_text(self.combo_repeat)
        self.combo_repeat.setStyleSheet(self._combo_style())

        shell_row.addWidget(self.lbl_priority)
        shell_row.addWidget(self.combo_priority)
        shell_row.addWidget(self.lbl_repeat)
        shell_row.addWidget(self.combo_repeat)
        shell_row.addStretch()
        layout.addLayout(shell_row)

        # 5. 当前状态摘要
        self.info_card = QFrame()
        self.info_card.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 6px;
            }
        """)
        info_layout = QVBoxLayout(self.info_card)
        info_layout.setContentsMargins(8, 8, 8, 8)
        info_layout.setSpacing(4)

        self.lbl_info_time = QLabel("时间未设置")
        self.lbl_info_alarm = QLabel("无提醒")
        self.lbl_info_list = QLabel("清单未选择")
        for label in (self.lbl_info_time, self.lbl_info_alarm, self.lbl_info_list):
            label.setStyleSheet(
                "color: rgba(255,255,255,0.88); font-size: 11px; "
                "font-family: 'Microsoft YaHei'; background: transparent; "
                "border: none; padding: 0px;"
            )
            info_layout.addWidget(label)

        layout.addWidget(self.info_card)

        # 6. 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 21, 0, 0)
        
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

    def _create_icon_btn(self, icon_name, tooltip_text):
        btn = QPushButton()
        btn.setFixedSize(22, 22)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pixmap = get_colored_icon(icon_name, "#FFFFFF", 14)
        if not pixmap.isNull():
            btn.setIcon(QIcon(pixmap))
        btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; } "
            "QPushButton:hover { background: rgba(255,255,255,0.2); border-radius: 3px; }"
        )
        btn._tooltip = ToolTipFilter(tooltip_text, btn)
        btn.installEventFilter(btn._tooltip)
        return btn

    def _center_combo_text(self, combo):
        for index in range(combo.count()):
            combo.setItemData(
                index,
                Qt.AlignmentFlag.AlignCenter,
                Qt.ItemDataRole.TextAlignmentRole,
            )

    def _combo_style(self):
        return """
            QComboBox {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255,255,255,0.25);
                border-radius: 4px;
                color: white;
                font-size: 11px;
                padding-left: 0px;
                font-family: 'Microsoft YaHei';
            }
            QComboBox::drop-down { border: none; width: 0px; }
            QComboBox::down-arrow { image: none; width: 0px; height: 0px; }
            QComboBox QAbstractItemView {
                background: white;
                color: #333333;
                border: 1px solid #dddddd;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                background: white;
                color: #333333;
                padding: 4px 6px;
            }
            QComboBox QAbstractItemView::item:selected {
                background: #0cc0df;
                color: white;
            }
        """

    def _show_pending_toast(self, message):
        if hasattr(self.window(), "show_toast"):
            self.window().show_toast(message)

    def _emit_alarm_request(self):
        target_time = self.selected_start_time if self.selected_start_time else self.selected_end_time
        if not target_time:
            self._show_pending_toast("⚠️ 请先设置计划时间")
            return
        self.req_open_alarm_picker.emit(
            target_time,
            self.selected_is_alarm_mode,
            self.selected_alarm_duration,
        )

    def _format_state_value(self, value):
        if value is None:
            return ""
        return str(value)

    def _update_summary_labels(self):
        start_text = self._format_state_value(self.selected_start_time)
        end_text = self._format_state_value(self.selected_end_time)
        reminder_text = self._format_state_value(self.selected_reminder)

        if start_text and end_text:
            self.lbl_info_time.setText(f"时间：{start_text} - {end_text}")
        elif end_text:
            self.lbl_info_time.setText(f"时间：{end_text}")
        elif start_text:
            self.lbl_info_time.setText(f"时间：{start_text}")
        else:
            self.lbl_info_time.setText("时间未设置")

        if reminder_text:
            alarm_prefix = "强提醒 " if self.selected_is_alarm_mode else ""
            self.lbl_info_alarm.setText(f"提醒：{alarm_prefix}{reminder_text}")
        else:
            self.lbl_info_alarm.setText("无提醒")

        if self.selected_list_name:
            self.lbl_info_list.setText(f"清单：{self.selected_list_name}")
        elif self.selected_list_id is not None:
            self.lbl_info_list.setText(f"清单：#{self.selected_list_id}")
        else:
            self.lbl_info_list.setText("清单未选择")

    def set_time_data(self, start_time, end_time):
        self.selected_start_time = start_time
        self.selected_end_time = end_time
        self._update_summary_labels()

    def set_alarm_data(self, reminder_time, is_alarm_mode=False, alarm_duration=0):
        self.selected_reminder = reminder_time
        self.selected_is_alarm_mode = is_alarm_mode
        self.selected_alarm_duration = alarm_duration
        self._update_summary_labels()

    def set_list_data(self, category_id, category_name):
        self.selected_list_id = category_id
        self.selected_list_name = category_name
        self._update_summary_labels()

    def reset_form(self, target_date=None):
        if target_date is not None:
            self.selected_date = target_date

        self.input_title.clear()
        self.input_desc.clear()
        self.selected_start_time = None
        self.selected_end_time = None
        self.selected_reminder = None
        self.selected_alarm_duration = 0
        self.selected_list_id = None
        self.selected_list_name = None
        self.selected_is_alarm_mode = False
        self.combo_priority.setCurrentIndex(2)
        self.combo_repeat.setCurrentIndex(0)
        self._update_summary_labels()

    def reset(self, target_date):
        self.reset_form(target_date)

    def _on_save(self):
        title = self.input_title.text().strip()
        if not title:
            if hasattr(self.window(), 'show_toast'):
                self.window().show_toast("⚠️ 标题不能为空")
            return

        if not self.selected_start_time and not self.selected_end_time:
            if hasattr(self.window(), 'show_toast'):
                self.window().show_toast("⚠️ 请先设置计划时间")
            return

        schedule_data = {
            'title': title,
            'item_type': 'schedule',
            'priority': 2 - self.combo_priority.currentIndex(),
            'repeat_rule': self.repeat_value_map.get(self.combo_repeat.currentText().strip(), "无"),
            'description': self.input_desc.toPlainText().strip(), 
            'start_time': self.selected_start_time,
            'end_time': self.selected_end_time,
            'reminder_time': self.selected_reminder,
            'is_alarm': self.selected_is_alarm_mode,
            'alarm_duration': self.selected_alarm_duration,
            'category_id': self.selected_list_id
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
    schedule_updated = pyqtSignal(object)
    schedule_detail_requested = pyqtSignal(object, object)

    def __init__(self):
        super().__init__()
        # 1. 窗口总尺寸缩小到 80%
        self.setFixedSize(720, 480) 
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.titleBar.hide()

        self.current_date = QDate.currentDate()
        self.user_selected_date = None
        self.schedule_marker_cache = {}
        self.schedule_marker_count_cache = {}
        self.hover_schedule_cache = {}
        self.open_day_panels = []
        self.hovered_date = None
        self.hover_preview_popup = None
        self.drag_pos = None
        self.context_menu_date = None
        self.time_picker_mode = "add"
        self.alarm_picker_mode = "add"
        self.list_picker_mode = "add"
        self.editing_schedule = None

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
        self.shared_more_menu = SharedMoreMenu(self, self.btn_more, show_festival_option=True)
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
        self.lbl_weather_icon = WeatherIconLabel(30, self)
        self.lbl_weather_icon.setFixedSize(30, 30) # 固定大小，确保居中不会乱跑
        self.lbl_weather_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_weather_icon.setStyleSheet('color: white; font-size: 16px; background: transparent;')
        self.lbl_weather_icon.start_loading()
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

        views = {"day": "日", "week": "周", "month": "月", "todo": "待办"}
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
        self.inline_add_view.req_open_time_picker.connect(self.go_to_time_picker)
        self.inline_add_view.req_open_alarm_picker.connect(self.go_to_alarm_picker)
        self.inline_add_view.req_open_list_picker.connect(self.go_to_list_picker)
        bottom_tools_vbox.addWidget(self.inline_add_view)

        self.page_time = MonthTimePickerView(self)
        self.page_time.hide()
        self.page_time.set_title("设置时间")
        self.page_time.setFixedHeight(self.inline_add_view.sizeHint().height())
        if hasattr(self.page_time, "btn_suspend"):
            self.page_time.btn_suspend.hide()
        if hasattr(self.page_time, "btn_close"):
            try:
                self.page_time.btn_close.clicked.disconnect()
            except TypeError:
                pass
            self.page_time.btn_close.clicked.connect(self.back_from_time_picker)
        self.page_time.back_requested.connect(self.back_from_time_picker)
        self.page_time.confirm_requested.connect(self.on_time_confirmed)
        bottom_tools_vbox.addWidget(self.page_time)

        self.page_alarm = MonthAlarmPickerView(self)
        self.page_alarm.hide()
        self.page_alarm.set_title("设置提醒")
        self.page_alarm.setFixedHeight(self.inline_add_view.sizeHint().height())
        if hasattr(self.page_alarm, "btn_suspend"):
            self.page_alarm.btn_suspend.hide()
        if hasattr(self.page_alarm, "btn_close"):
            try:
                self.page_alarm.btn_close.clicked.disconnect()
            except TypeError:
                pass
            self.page_alarm.btn_close.clicked.connect(self.back_from_alarm_picker)
        self.page_alarm.back_requested.connect(self.back_from_alarm_picker)
        self.page_alarm.confirm_requested.connect(self.on_alarm_confirmed)
        bottom_tools_vbox.addWidget(self.page_alarm)

        self.page_list = MonthListPickerView(self)
        self.page_list.hide()
        self.page_list.set_title("选择清单")
        self.page_list.setFixedHeight(self.inline_add_view.sizeHint().height())
        self.page_list.back_requested.connect(self.back_from_list_picker)
        self.page_list.confirm_requested.connect(self.on_list_confirmed)
        bottom_tools_vbox.addWidget(self.page_list)

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
        self.calendar.clicked.connect(self._on_calendar_date_clicked)
        self.calendar.activated.connect(self._on_calendar_date_activated)
        
        # ==========================================
        # 绘制挂载
        # ==========================================
        
        table_view = self.calendar.findChild(QTableView)
        self.calendar_table_view = table_view
        self.calendar_viewport = table_view.viewport()
        self.calendar_table_view.setMouseTracking(True)
        self.calendar_viewport.setMouseTracking(True)
        self.calendar_viewport.installEventFilter(self)
        
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

    def _build_hover_schedule_cache(self):
        hover_schedule_cache = {}

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

            hover_schedule_cache.setdefault(target_date, []).append(schedule)

        fallback_time = datetime.datetime.max
        for schedules in hover_schedule_cache.values():
            schedules.sort(
                key=lambda schedule: (
                    getattr(schedule, "start_time", None)
                    or getattr(schedule, "end_time", None)
                    or fallback_time,
                    -int(getattr(schedule, "priority", 0)),
                    getattr(schedule, "title", "") or "",
                )
            )

        return hover_schedule_cache

    def _refresh_schedule_marker_cache(self):
        self.schedule_marker_cache, self.schedule_marker_count_cache = self._build_schedule_marker_cache()
        self.hover_schedule_cache = self._build_hover_schedule_cache()
        self.cell_delegate.set_calendar_state(
            self.current_date.year(),
            self.current_date.month(),
            QDate.currentDate(),
            self.schedule_marker_cache,
            self.schedule_marker_count_cache,
            self.user_selected_date,
        )
        self._hide_hover_preview()
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

    def _on_calendar_date_clicked(self, qdate):
        self.user_selected_date = qdate
        self._refresh_schedule_marker_cache()
        self._hide_hover_preview()
        existing_panel = self._find_open_day_panel(qdate)
        if existing_panel is not None:
            existing_panel.close()
            return

        self._open_day_panel(qdate)

    def _on_calendar_date_activated(self, qdate):
        self.user_selected_date = qdate
        self._refresh_schedule_marker_cache()
        self._hide_hover_preview()
        self.close_day_panels()
        self.date_selected.emit(qdate)

    def _remove_day_panel(self, panel):
        if panel in self.open_day_panels:
            self.open_day_panels.remove(panel)

    def _find_open_day_panel(self, qdate):
        self.open_day_panels = [panel for panel in self.open_day_panels if panel is not None]
        for panel in self.open_day_panels:
            if getattr(panel, "panel_date", None) == qdate:
                return panel
        return None

    def _get_day_panel_position(self, index, panel=None):
        month_rect = self.frameGeometry()
        gap = 16
        y_offset = 24 + index * 36
        panel_size = panel.sizeHint() if panel is not None else QSize(220, 120)
        panel_width = max(panel_size.width(), 120)
        panel_height = max(panel_size.height(), 80)

        x = month_rect.topRight().x() + gap
        y = month_rect.topRight().y() + y_offset

        screen = QGuiApplication.screenAt(month_rect.center()) or QGuiApplication.primaryScreen()
        if screen is None:
            return x, y

        available_rect = screen.availableGeometry()
        if x + panel_width > available_rect.right():
            x = month_rect.left() - gap - panel_width

        x = max(available_rect.left(), min(x, available_rect.right() - panel_width))
        y = max(available_rect.top(), min(y, available_rect.bottom() - panel_height))
        return x, y

    def _open_day_panel(self, qdate):
        existing_panel = self._find_open_day_panel(qdate)
        if existing_panel is not None:
            existing_panel.show()
            existing_panel.raise_()
            existing_panel.activateWindow()
            return existing_panel

        schedules = self.hover_schedule_cache.get(qdate.toPyDate(), [])
        panel = MonthDayPanel(qdate, schedules)
        panel.closed.connect(self._remove_day_panel)
        panel.schedule_double_clicked.connect(self.schedule_detail_requested.emit)
        panel.move(*self._get_day_panel_position(len(self.open_day_panels), panel))
        panel.show()
        self.open_day_panels.append(panel)
        return panel

    def close_day_panels(self):
        for panel in list(self.open_day_panels):
            try:
                if panel is not None and hasattr(panel, "close"):
                    panel.close()
            finally:
                pass
        self.open_day_panels.clear()

    def _ensure_hover_preview_popup(self):
        if self.hover_preview_popup is None:
            self.hover_preview_popup = MonthDayHoverPreview()
        return self.hover_preview_popup

    def _hide_hover_preview(self):
        self.hovered_date = None
        if self.hover_preview_popup is not None:
            self.hover_preview_popup.hide()

    def _show_hover_preview(self, qdate, index):
        popup = self._ensure_hover_preview_popup()
        self.hovered_date = qdate
        schedules = self.hover_schedule_cache.get(qdate.toPyDate(), [])
        popup.set_preview_data(qdate, schedules)

        cell_rect = self.calendar_table_view.visualRect(index)
        global_anchor = self.calendar_viewport.mapToGlobal(cell_rect.bottomRight())
        popup.move(global_anchor.x() + 8, global_anchor.y() + 8)
        popup.show()

    def eventFilter(self, obj, event):
        if obj == getattr(self, "calendar_viewport", None):
            if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.RightButton:
                index = self.calendar_table_view.indexAt(event.pos())
                if not index.isValid():
                    return False

                qdate = self.cell_delegate._date_for_index(index)
                if not qdate.isValid():
                    return False

                self._hide_hover_preview()
                self._show_context_menu_for_date(qdate, self.calendar_viewport.mapToGlobal(event.pos()))
                return True

            if event.type() == QEvent.Type.MouseMove:
                index = self.calendar_table_view.indexAt(event.pos())
                if not index.isValid():
                    self._hide_hover_preview()
                    return False

                qdate = self.cell_delegate._date_for_index(index)
                if not qdate.isValid():
                    self._hide_hover_preview()
                    return False

                if self.hovered_date != qdate:
                    self.hovered_date = qdate
                self._show_hover_preview(qdate, index)
                return False

            if event.type() == QEvent.Type.Leave:
                self._hide_hover_preview()
                return False

        return super().eventFilter(obj, event)

    def _show_context_menu_for_date(self, qdate, global_pos):
        self.context_menu_date = qdate
        menu = ActionContextMenu(self)
        menu.action_requested.connect(self._handle_context_action)
        menu.view_requested.connect(self._handle_context_view)
        menu.exec(global_pos)

    def _handle_context_action(self, action_name):
        if action_name != "add":
            return

        target_date = self.context_menu_date
        if target_date is None or not target_date.isValid():
            return

        if target_date < QDate.currentDate():
            self.show_toast("🚫 该日期已过期，无法添加日程")
            return

        self.search_box.show()
        self.view_selector_container.hide()
        self.page_time.hide()
        self.page_alarm.hide()
        self.page_list.hide()
        self.inline_add_view.reset(target_date)
        self.inline_add_view.show()

    def _handle_context_view(self, view_name):
        if view_name == "day":
            target_date = self.context_menu_date
            if target_date is None or not target_date.isValid():
                return
            self._hide_hover_preview()
            self.close_day_panels()
            self.date_selected.emit(target_date)
            return

        if view_name == "week":
            self._on_view_selected("week")
            return

        if view_name == "month":
            return

        if view_name == "todo":
            self._on_view_selected("todo")
            return

        if view_name == "priority":
            return

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
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(0, 0, 0, 26), 1))
        painter.drawPath(path)
        
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

    def hideEvent(self, event):
        self._hide_hover_preview()
        super().hideEvent(event)

    def closeEvent(self, event):
        self.close_day_panels()
        self._hide_hover_preview()
        super().closeEvent(event)

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
        self.lbl_weather_icon.set_weather_icon(svg_path)
            
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

    def _get_add_target_date(self):
        if self.user_selected_date is not None and self.user_selected_date.isValid():
            return self.user_selected_date
        return self.calendar.selectedDate()

    def _on_add_clicked(self):
        # 1. 验证日期是否过期
        today = QDate.currentDate()
        target_date = self._get_add_target_date()

        if not target_date.isValid():
            return
        
        if target_date < today:
            self.show_toast("🚫 该日期已过期，无法添加日程")
            return
            
        # 2. 切换 UI
        if self.inline_add_view.isVisible():
            self._close_add_view()
        else:
            self.search_box.show()
            self.view_selector_container.hide()
            self.inline_add_view.reset(target_date)
            self.page_time.hide()
            self.page_alarm.hide()
            self.page_list.hide()
            self.inline_add_view.show()

    def _close_add_view(self):
        self.page_time.hide()
        self.page_alarm.hide()
        self.page_list.hide()
        self.inline_add_view.hide()
        self.search_box.show()

    def go_to_time_picker(self, start, end):
        self.time_picker_mode = "add"
        self._hide_hover_preview()
        self.close_day_panels()

        target_qdate = self.inline_add_view.selected_date or self._get_add_target_date()
        if target_qdate is None or not target_qdate.isValid():
            target_qdate = QDate.currentDate()

        target_pydate = target_qdate.toPyDate()
        now = datetime.datetime.now()
        default_end = datetime.datetime(
            target_pydate.year,
            target_pydate.month,
            target_pydate.day,
            now.hour,
            now.minute,
        )

        self.page_time.set_title("设置时间")
        self.page_time.set_initial_data(start, end or default_end)
        if not self.isVisible():
            self.show()
        self.page_alarm.hide()
        self.page_list.hide()
        self.inline_add_view.hide()
        self.page_time.show()

    def go_to_time_picker_for_edit(self, schedule_data):
        self.time_picker_mode = "edit"
        self.editing_schedule = schedule_data
        self.page_time.set_title("修改时间")
        self.page_time.set_initial_data(schedule_data.start_time, schedule_data.end_time)
        self._show_edit_picker(self.page_time)

    def back_from_time_picker(self):
        self.page_time.hide()
        if self.time_picker_mode == "edit":
            self._finish_edit_picker("time_picker_mode")
        else:
            self.inline_add_view.show()

    def on_time_confirmed(self, start, end):
        if self.time_picker_mode == "edit" and self.editing_schedule:
            schedule = self.editing_schedule

            def _do_update(update_future):
                now = datetime.datetime.now()
                db_manager.update_schedule_with_repeat(
                    schedule.id,
                    {"start_time": start, "end_time": end, "created_at": now},
                    update_future,
                )
                schedule.start_time = start
                schedule.end_time = end
                schedule.created_at = now
                if not update_future:
                    schedule.group_id = None
                self._complete_schedule_edit(schedule)
                self.back_from_time_picker()

            self._check_repeat_and_execute(schedule, _do_update)
            return
        self.inline_add_view.set_time_data(start, end)
        self.back_from_time_picker()

    def go_to_alarm_picker(self, target_time, is_alarm, duration):
        self.alarm_picker_mode = "add"
        self._hide_hover_preview()
        self.close_day_panels()
        self.page_alarm.set_title("设置提醒")
        self.page_alarm.set_initial_data(target_time, is_alarm, duration)
        if not self.isVisible():
            self.show()
        self.page_time.hide()
        self.page_list.hide()
        self.inline_add_view.hide()
        self.page_alarm.show()

    def go_to_alarm_picker_for_edit(self, schedule_data):
        self.alarm_picker_mode = "edit"
        self.editing_schedule = schedule_data
        target = schedule_data.start_time or schedule_data.end_time or datetime.datetime.now()
        self.page_alarm.set_title("修改提醒")
        self.page_alarm.set_initial_data(
            target,
            schedule_data.is_alarm,
            schedule_data.alarm_duration,
        )
        self._show_edit_picker(self.page_alarm)

    def back_from_alarm_picker(self):
        self.page_alarm.hide()
        if self.alarm_picker_mode == "edit":
            self._finish_edit_picker("alarm_picker_mode")
        else:
            self.inline_add_view.show()

    def on_alarm_confirmed(self, remind_dt, is_alarm, duration):
        if self.alarm_picker_mode == "edit" and self.editing_schedule:
            schedule = self.editing_schedule

            def _do_update(update_future):
                now = datetime.datetime.now()
                db_manager.update_schedule_with_repeat(
                    schedule.id,
                    {
                        "reminder_time": remind_dt,
                        "is_alarm": is_alarm,
                        "alarm_duration": duration,
                        "created_at": now,
                    },
                    update_future,
                )
                schedule.reminder_time = remind_dt
                schedule.is_alarm = is_alarm
                schedule.alarm_duration = duration
                schedule.created_at = now
                if not update_future:
                    schedule.group_id = None
                self._complete_schedule_edit(schedule)
                self.back_from_alarm_picker()

            self._check_repeat_and_execute(schedule, _do_update)
            return
        self.inline_add_view.set_alarm_data(remind_dt, is_alarm, duration)
        self.back_from_alarm_picker()

    def go_to_list_picker(self, current_category_id, list_type="schedule"):
        self.list_picker_mode = "add"
        self._hide_hover_preview()
        self.close_day_panels()
        self.page_list.set_title("选择清单")
        self.page_list.load_data(current_category_id, list_type="schedule")
        if not self.isVisible():
            self.show()
        self.page_time.hide()
        self.page_alarm.hide()
        self.inline_add_view.hide()
        self.page_list.show()

    def go_to_list_picker_for_edit(self, schedule_data):
        self.list_picker_mode = "edit"
        self.editing_schedule = schedule_data
        self.page_list.set_title("修改清单")
        self.page_list.load_data(
            schedule_data.category_id,
            list_type=getattr(schedule_data, "item_type", "schedule"),
        )
        self._show_edit_picker(self.page_list)

    def back_from_list_picker(self):
        self.page_list.hide()
        if self.list_picker_mode == "edit":
            self._finish_edit_picker("list_picker_mode")
        else:
            self.inline_add_view.show()

    def on_list_confirmed(self, category_id):
        if self.list_picker_mode == "edit" and self.editing_schedule:
            schedule = self.editing_schedule

            def _do_update(update_future):
                now = datetime.datetime.now()
                db_manager.update_schedule_with_repeat(
                    schedule.id,
                    {"category_id": category_id, "created_at": now},
                    update_future,
                )
                schedule.category_id = category_id
                schedule.created_at = now
                if not update_future:
                    schedule.group_id = None
                self._complete_schedule_edit(schedule)
                self.back_from_list_picker()

            self._check_repeat_and_execute(schedule, _do_update)
            return
        category_name = None
        if category_id is not None:
            category = db_manager.get_category(category_id)
            category_name = category.name if category else None
        self.inline_add_view.set_list_data(category_id, category_name)
        self.back_from_list_picker()

    def _show_edit_picker(self, active_picker):
        self._hide_hover_preview()
        self.close_day_panels()
        if not self.isVisible():
            self.show()
        self.search_box.show()
        self.view_selector_container.hide()
        self.inline_add_view.hide()
        for picker in (self.page_time, self.page_alarm, self.page_list):
            picker.setVisible(picker is active_picker)

    def _finish_edit_picker(self, mode_attribute):
        setattr(self, mode_attribute, "add")
        self.editing_schedule = None
        self.inline_add_view.hide()
        self.search_box.show()

    def _complete_schedule_edit(self, schedule):
        self._refresh_schedule_marker_cache()
        self.schedule_updated.emit(schedule)

    def _check_repeat_and_execute(self, schedule_data, update_callback):
        rule = getattr(schedule_data, "repeat_rule", "")
        if rule and str(rule).strip() not in {"", "无", "none", "不重复"}:
            message = QMessageBox(self)
            message.setWindowTitle("修改重复日程")
            message.setText(
                f"当前日程包含【{rule}】的重复规则。\n"
                "请选择修改当前日程，或修改该系列的所有日程。"
            )
            all_button = message.addButton("修改所有", QMessageBox.ButtonRole.AcceptRole)
            single_button = message.addButton("仅修改本次", QMessageBox.ButtonRole.ActionRole)
            message.addButton("取消", QMessageBox.ButtonRole.RejectRole)
            message.exec()
            if message.clickedButton() == all_button:
                update_callback(True)
            elif message.clickedButton() == single_button:
                update_callback(False)
            return
        update_callback(False)

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
