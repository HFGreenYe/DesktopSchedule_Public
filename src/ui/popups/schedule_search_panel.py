from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QIcon, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.config import AppConfig


class ScheduleSearchPanel(QWidget):
    apply_requested = pyqtSignal(dict)
    cleared = pyqtSignal()
    closed = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(268, 372)
        self._drag_offset = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 12, 14, 14)
        outer.setSpacing(8)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        self.title_label = QLabel("搜索 / 筛选")
        self.title_label.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei'; "
            "font-size: 15px; font-weight: bold; background: transparent;"
        )
        header.addWidget(self.title_label, 1)

        self.btn_close = QPushButton("×")
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.92);
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.18);
                border-radius: 12px;
            }
            """
        )
        self.btn_close.clicked.connect(self.close)
        header.addWidget(self.btn_close)
        outer.addLayout(header)

        content = QFrame()
        content.setObjectName("scheduleSearchPanelContent")
        content.setStyleSheet(
            """
            QFrame#scheduleSearchPanelContent {
                background-color: rgba(255, 255, 255, 0.17);
                border: 1px solid rgba(255, 255, 255, 0.55);
                border-radius: 7px;
            }
            QLabel {
                color: rgba(255, 255, 255, 0.92);
                font-family: 'Microsoft YaHei';
                font-size: 12px;
                background: transparent;
                border: none;
            }
            QLineEdit, QComboBox {
                min-height: 24px;
                color: white;
                background-color: rgba(255, 255, 255, 0.16);
                border: 1px solid rgba(255, 255, 255, 0.72);
                border-radius: 4px;
                padding: 2px 6px;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid white;
                background-color: rgba(255, 255, 255, 0.22);
            }
            QCheckBox {
                color: rgba(255, 255, 255, 0.9);
                font-family: 'Microsoft YaHei';
                font-size: 12px;
                spacing: 5px;
                background: transparent;
            }
            """
        )
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(12, 11, 12, 12)
        content_layout.setSpacing(9)

        keyword_label = QLabel("关键词")
        content_layout.addWidget(keyword_label)
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("标题 / 描述 / 清单")
        self.keyword_input.addAction(
            QIcon("assets/icons/search.svg"),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        content_layout.addWidget(self.keyword_input)

        option_grid = QGridLayout()
        option_grid.setContentsMargins(0, 2, 0, 0)
        option_grid.setHorizontalSpacing(8)
        option_grid.setVerticalSpacing(8)

        self.range_combo = self._create_combo(["当前日期", "前后 7 天", "全部日期"])
        self.list_combo = self._create_combo(["全部清单", "未分类", "当前清单"])
        self.status_combo = self._create_combo(["全部状态", "未完成", "已完成"])
        self.priority_combo = self._create_combo(["全部重要性", "低重要性", "中重要性", "高重要性"])

        self._add_option_row(option_grid, 0, "范围", self.range_combo)
        self._add_option_row(option_grid, 1, "清单", self.list_combo)
        self._add_option_row(option_grid, 2, "状态", self.status_combo)
        self._add_option_row(option_grid, 3, "重要性", self.priority_combo)
        content_layout.addLayout(option_grid)

        type_label = QLabel("日程类型")
        content_layout.addWidget(type_label)

        type_row = QHBoxLayout()
        type_row.setContentsMargins(0, 0, 0, 0)
        type_row.setSpacing(8)
        self.include_interval_check = QCheckBox("时间段")
        self.include_point_check = QCheckBox("DDL / 单时间")
        self.include_interval_check.setChecked(True)
        self.include_point_check.setChecked(True)
        type_row.addWidget(self.include_interval_check)
        type_row.addWidget(self.include_point_check)
        content_layout.addLayout(type_row)

        hint = QLabel("当前仅完成面板入口，筛选生效逻辑下一步接入。")
        hint.setWordWrap(True)
        hint.setStyleSheet(
            "color: rgba(255, 255, 255, 0.72); font-size: 11px; "
            "font-family: 'Microsoft YaHei'; background: transparent; border: none;"
        )
        content_layout.addWidget(hint)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 2, 0, 0)
        button_row.setSpacing(8)
        self.btn_clear = self._create_action_button("清空")
        self.btn_apply = self._create_action_button("应用")
        self.btn_clear.clicked.connect(self.reset_options)
        self.btn_apply.clicked.connect(lambda: self.apply_requested.emit(self.current_options()))
        button_row.addWidget(self.btn_clear)
        button_row.addWidget(self.btn_apply)
        content_layout.addLayout(button_row)

        outer.addWidget(content, 1)

    @staticmethod
    def _create_combo(items):
        combo = QComboBox()
        combo.addItems(items)
        combo.setCursor(Qt.CursorShape.PointingHandCursor)
        return combo

    @staticmethod
    def _add_option_row(grid, row, label_text, widget):
        label = QLabel(label_text)
        label.setFixedWidth(42)
        grid.addWidget(label, row, 0, Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(widget, row, 1)

    @staticmethod
    def _create_action_button(text):
        button = QPushButton(text)
        button.setFixedHeight(26)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(
            """
            QPushButton {
                color: __ACCENT__;
                background: rgba(255, 255, 255, 0.92);
                border: 1px solid rgba(255, 255, 255, 0.95);
                border-radius: 5px;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
            }
            QPushButton:hover {
                background: white;
            }
            QPushButton:pressed {
                background: rgba(235, 245, 255, 0.95);
            }
            """
            .replace("__ACCENT__", AppConfig.COLOR_GRADIENT_START)
        )
        return button

    def current_options(self):
        return {
            "keyword": self.keyword_input.text().strip(),
            "range": self.range_combo.currentText(),
            "list": self.list_combo.currentText(),
            "status": self.status_combo.currentText(),
            "priority": self.priority_combo.currentText(),
            "include_interval": self.include_interval_check.isChecked(),
            "include_point": self.include_point_check.isChecked(),
        }

    def reset_options(self):
        self.keyword_input.clear()
        self.range_combo.setCurrentIndex(0)
        self.list_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.priority_combo.setCurrentIndex(0)
        self.include_interval_check.setChecked(True)
        self.include_point_check.setChecked(True)
        self.cleared.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)

        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        painter.fillPath(path, QBrush(gradient))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(0, 0, 0, 30), 1))
        painter.drawPath(path)

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
        super().mouseReleaseEvent(event)

    def closeEvent(self, event):
        self.closed.emit(self)
        super().closeEvent(event)
