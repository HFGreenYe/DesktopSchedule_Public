from datetime import date, timedelta
from html import escape
from pathlib import Path

from PyQt6.QtCore import QEvent, QPoint, QPointF, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QGuiApplication,
    QIcon,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPixmap,
)
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QFileDialog,
    QLabel,
    QButtonGroup,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QStyle,
    QStyleOptionComboBox,
    QStylePainter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.config import AppConfig
from src.services.schedule_export_service import (
    ExportOptions,
    PdfExportStyle,
    PdfTextStyle,
    ScheduleExportService,
)
from src.ui.calendar_pop import CalendarPop
from src.ui.common.toast import show_center_toast
from src.ui.common.themed_color_dialog import ThemedColorDialog
from src.ui.popups.export_range_picker import ExportPeriodPickerPopup
from src.utils.window_preferences import set_window_pin_state


class _ExportPreviewBox(QTextEdit):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class _ElidedComboBox(QComboBox):
    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionComboBox()
        self.initStyleOption(option)
        text_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_ComboBox,
            option,
            QStyle.SubControl.SC_ComboBoxEditField,
            self,
        )
        option.currentText = self.fontMetrics().elidedText(
            self.currentText(),
            Qt.TextElideMode.ElideRight,
            max(0, text_rect.width()),
        )
        painter.drawComplexControl(QStyle.ComplexControl.CC_ComboBox, option)
        painter.drawControl(QStyle.ControlElement.CE_ComboBoxLabel, option)


class _ExportClickableColorPreview(QLabel):
    clicked = pyqtSignal(str)

    def __init__(self, mode, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            area = "solid"
            if self.mode == "gradient":
                area = "top" if event.position().y() < self.height() / 2 else "bottom"
            self.clicked.emit(area)
            event.accept()
            return
        super().mousePressEvent(event)


class _ExportPreviewPopup(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._source_preview_size = QSize(168, 296)
        self._drag_offset = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header_holder = QWidget()
        self.header_holder.setFixedHeight(42)
        header = QHBoxLayout(self.header_holder)
        header.setContentsMargins(14, 8, 14, 2)
        header.setSpacing(0)
        self.title = QLabel("导出预览")
        self.title.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei UI'; "
            "font-size: 16px; font-weight: bold; background: transparent; border: none;"
        )
        self.close_btn = QPushButton("×", self)
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet(
            "QPushButton { color: white; background: transparent; border: none; "
            "font-size: 20px; } QPushButton:hover { background: #ff4d4f; "
            "border-top-right-radius: 8px; border-bottom-left-radius: 4px; }"
        )
        self.close_btn.clicked.connect(self.close)
        header.addWidget(self.title)
        header.addStretch(1)
        layout.addWidget(self.header_holder)

        self.content_frame = QFrame()
        self.content_frame.setObjectName("exportPreviewContentFrame")
        self.set_preview_background("background-color: rgba(255, 255, 255, 0.70)")
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(14, 10, 14, 14)
        content_layout.setSpacing(0)

        self.preview_editor = QTextEdit()
        self.preview_editor.setReadOnly(True)
        self.preview_editor.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.preview_editor.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.preview_editor.setPlainText(text)
        self.preview_editor.setStyleSheet(
            f"""
            QTextEdit {{
                background: transparent;
                border: none;
                color: {AppConfig.COLOR_GRADIENT_START};
                font-family: "Microsoft YaHei UI";
                font-size: 12px;
                padding: 0px;
            }}
            """
        )
        content_layout.addWidget(self.preview_editor)
        layout.addWidget(self.content_frame, 1)
        self.header_holder.installEventFilter(self)
        self.title.installEventFilter(self)
        self.content_frame.installEventFilter(self)
        self.preview_editor.viewport().installEventFilter(self)
        self.set_preview_size(self._source_preview_size)
        self._update_close_button_position()

    def set_preview_html(self, html):
        self.preview_editor.setHtml(html)

    def set_preview_background(self, background_style):
        self.content_frame.setStyleSheet(
            "QFrame#exportPreviewContentFrame { "
            f"{background_style}; border: none; "
            "border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; }"
        )

    def set_preview_size(self, size):
        self._source_preview_size = QSize(max(1, size.width()), max(1, size.height()))
        scale = 1.45
        content_width = max(220, round(self._source_preview_size.width() * scale))
        content_height = max(320, round(self._source_preview_size.height() * scale))
        self.setFixedSize(content_width + 28, content_height + 56)
        self._update_close_button_position()

    def _update_close_button_position(self):
        self.close_btn.move(self.width() - self.close_btn.width(), 0)
        self.close_btn.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_close_button_position()

    def show_near(self, anchor):
        if anchor is not None:
            anchor_rect = anchor.frameGeometry()
            x = anchor_rect.x() + anchor_rect.width() + 8
            y = anchor_rect.y()
            screen = (
                QGuiApplication.screenAt(anchor_rect.center())
                or QGuiApplication.primaryScreen()
            )
            if screen is not None:
                available = screen.availableGeometry()
                if x + self.width() > available.right() + 1:
                    x = anchor_rect.x() - self.width() - 8
                x = max(available.left(), min(x, available.right() - self.width() + 1))
                y = max(available.top(), min(y, available.bottom() - self.height() + 1))
            self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()

    def eventFilter(self, watched, event):
        header_drag = watched in (self.header_holder, self.title)
        content_drag = watched is self.content_frame
        preview_drag = watched is self.preview_editor.viewport()
        if header_drag or content_drag or preview_drag:
            if (
                event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
                and (
                    header_drag
                    or content_drag
                    or self._is_preview_blank_position(event.position())
                )
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
        return super().eventFilter(watched, event)

    def _is_preview_blank_position(self, position):
        document_position = QPointF(position)
        document_position += QPointF(
            self.preview_editor.horizontalScrollBar().value(),
            self.preview_editor.verticalScrollBar().value(),
        )
        hit_position = self.preview_editor.document().documentLayout().hitTest(
            document_position,
            Qt.HitTestAccuracy.ExactHit,
        )
        return hit_position < 0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 8, 8)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        painter.fillPath(path, gradient)


class _ExportBackgroundStylePopup(QWidget):
    def __init__(self, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(330, 150)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        frame = QFrame()
        frame.setObjectName("backgroundStyleFrame")
        frame.setStyleSheet(
            """
            QFrame#backgroundStyleFrame {
                background-color: rgba(255, 255, 255, 0.70);
                border: 2px solid #FFFFFF;
                border-radius: 8px;
            }
            """
        )
        frame_layout = QHBoxLayout(frame)
        frame_layout.setContentsMargins(14, 12, 14, 12)
        frame_layout.setSpacing(14)

        frame_layout.addWidget(
            self._create_background_option(
                "纯色背景",
                "background-color: rgba(255, 255, 255, 0.92);",
            )
        )
        frame_layout.addWidget(
            self._create_background_option(
                "渐变背景",
                "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
                f"stop:0 {AppConfig.COLOR_GRADIENT_START}, "
                f"stop:1 {AppConfig.COLOR_GRADIENT_END});",
            )
        )
        frame_layout.addWidget(
            self._create_background_option(
                "默认图片",
                "background-color: rgba(255, 255, 255, 0.76);",
                "待施工",
            )
        )
        frame_layout.addWidget(
            self._create_background_option(
                "自定义",
                "background-color: rgba(255, 255, 255, 0.76);",
                "+",
                18,
            )
        )

        layout.addWidget(frame)

        self.btn_close = QPushButton(self)
        self.btn_close.setFixedSize(22, 22)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setText("×")
        self.btn_close.setStyleSheet(
            """
            QPushButton {
                color: white;
                background: transparent;
                border: none;
                font-family: "Microsoft YaHei UI";
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4d4f;
                border-radius: 4px;
            }
            """
        )
        self.btn_close.clicked.connect(self.close)
        self._update_close_position()

    def _create_background_option(
        self,
        title,
        preview_style,
        preview_text="",
        preview_font_size=12,
    ):
        container = QWidget()
        container.setFixedWidth(62)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setFixedHeight(18)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            "color: #222222; font-family: 'Microsoft YaHei UI'; "
            "font-size: 11px; font-weight: bold; background: transparent; border: none;"
        )
        layout.addWidget(title_label)

        preview = QLabel(preview_text)
        preview.setFixedSize(46, 78)
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview.setWordWrap(True)
        preview.setStyleSheet(
            f"""
            QLabel {{
                {preview_style}
                border: 1px solid rgba(120, 120, 120, 0.65);
                border-radius: 4px;
                color: #777777;
                font-family: "Microsoft YaHei UI";
                font-size: {preview_font_size}px;
                font-weight: bold;
            }}
            """
        )
        layout.addWidget(preview, 0, Qt.AlignmentFlag.AlignHCenter)
        return container

    def show_near(self, anchor):
        if anchor is not None:
            anchor_rect = QRectF(anchor.rect())
            anchor_top_left = anchor.mapToGlobal(anchor_rect.topLeft().toPoint())
            x = anchor_top_left.x() + anchor.width() + 8
            y = anchor_top_left.y()
            screen = QGuiApplication.screenAt(anchor_top_left) or QGuiApplication.primaryScreen()
            if screen is not None:
                available = screen.availableGeometry()
                if x + self.width() > available.right() + 1:
                    x = anchor_top_left.x() - self.width() - 8
                x = max(available.left(), min(x, available.right() - self.width() + 1))
                y = max(available.top(), min(y, available.bottom() - self.height() + 1))
            self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()

    def _update_close_position(self):
        self.btn_close.move(self.width() - self.btn_close.width() - 14, 14)
        self.btn_close.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_close_position()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 10, 10)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        painter.fillPath(path, gradient)


class ExportSchedulePanel(QWidget):
    export_requested = pyqtSignal()

    def __init__(self, parent_window=None):
        super().__init__(
            parent_window,
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint,
        )
        self.parent_window = parent_window
        self.is_pinned = False
        self._drag_offset = None
        self._preview_popup = None
        self._background_popup = None
        self._day_range_popup = None
        self._period_range_popup = None
        self._export_service = None
        today = date.today()
        self._selected_range_dates = {
            "day": today,
            "week": today - timedelta(days=today.weekday()),
            "month": today.replace(day=1),
        }
        self.default_preview_height = 298
        self.default_preview_width = round(
            self.default_preview_height * 210 / 297
        )
        self.preview_width = self.default_preview_width
        self._selected_preview_size = "9:16"
        self.export_background_mode = "solid"
        self.export_solid_color = "#ffffff"
        self.export_gradient_start = AppConfig.COLOR_GRADIENT_START
        self.export_gradient_end = AppConfig.COLOR_GRADIENT_END
        self.export_font_colors = {
            label: AppConfig.COLOR_GRADIENT_START
            for label in ("标题", "详情", "备注")
        }
        self.font_languages = {label: "中" for label in ("标题", "详情", "备注")}
        self.font_choices = {
            label: {"中": "微软雅黑", "英": "Times New Roman"}
            for label in ("标题", "详情", "备注")
        }
        self.option_groups = {}
        self._radio_groups = []
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.export_requested.connect(self._handle_export_requested)
        self._setup_ui()
        self.reset_geometry_for_parent()

    def reset_geometry_for_parent(self):
        parent = self.parent_window
        width = self._panel_width()
        height = 360
        self.setFixedSize(width, height)
        if hasattr(self, "preview_box"):
            self._refresh_export_preview()

        if parent is None:
            return

        parent_rect = parent.frameGeometry()
        gap = 8
        preferred_x = parent_rect.x() + parent_rect.width() + gap
        fallback_x = parent_rect.x() - width - gap
        x = preferred_x
        y = parent_rect.y()
        screen = (
            QGuiApplication.screenAt(parent_rect.center())
            or QGuiApplication.primaryScreen()
        )
        if screen is not None:
            available = screen.availableGeometry()
            if preferred_x + width <= available.right() + 1:
                x = preferred_x
            elif fallback_x >= available.left():
                x = fallback_x
            else:
                x = max(available.left(), min(preferred_x, available.right() - width + 1))
            y = max(available.top(), min(y, available.bottom() - height + 1))
        self.move(x, y)

    def _panel_width(self):
        return 320 + self.preview_width

    def set_preview_width(self, width):
        self.preview_width = max(120, int(width))
        if hasattr(self, "preview_box"):
            self.preview_box.setFixedWidth(self.preview_width)
        self.setFixedWidth(self._panel_width())
        if self._preview_popup is not None and hasattr(self, "preview_box"):
            self._preview_popup.set_preview_size(self.preview_box.size())

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header_holder = QWidget()
        header_holder.setFixedHeight(42)
        header_layout = QHBoxLayout(header_holder)
        header_layout.setContentsMargins(14, 8, 104, 2)
        header_layout.setSpacing(0)
        title = QLabel("导出日程")
        title.setFixedHeight(28)
        title.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei UI'; "
            "font-size: 17px; font-weight: bold; background: transparent; border: none;"
        )
        header_layout.addWidget(title)
        header_layout.addStretch(1)
        root.addWidget(header_holder)

        self.btn_print = QPushButton(self)
        self.btn_print.setFixedSize(30, 30)
        self.btn_print.setIconSize(QSize(16, 16))
        self.btn_print.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_print.setToolTip("导出日程")

        self.btn_pin = QPushButton(self)
        self.btn_pin.setFixedSize(30, 30)
        self.btn_pin.setIconSize(QSize(16, 16))
        self.btn_pin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pin.setToolTip("窗口置顶")

        self.btn_close = QPushButton(self)
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setIconSize(QSize(12, 12))
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setToolTip("关闭")

        button_style = (
            "QPushButton { background: transparent; border: none; border-radius: 4px; } "
            "QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }"
        )
        self.btn_print.setStyleSheet(button_style)
        self.btn_pin.setStyleSheet(button_style)
        self.btn_close.setStyleSheet(
            "QPushButton { background: transparent; border: none; "
            "border-top-right-radius: 12px; } "
            "QPushButton:hover { background: #ff4d4f; }"
        )
        self.btn_print.clicked.connect(self.export_requested.emit)
        self.btn_pin.clicked.connect(self._toggle_pin)
        self.btn_close.clicked.connect(self.close)

        self.settings_frame = QFrame()
        self.settings_frame.setObjectName("exportSettingsFrame")
        self.settings_frame.setStyleSheet(
            """
            QFrame#exportSettingsFrame {
                background-color: rgba(255, 255, 255, 0.70);
                border: none;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
            """
        )
        frame_layout = QHBoxLayout(self.settings_frame)
        frame_layout.setContentsMargins(14, 10, 14, 10)
        frame_layout.setSpacing(12)

        controls_layout = QVBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(6)
        self.settings_title = QLabel("导出设置")
        self.settings_title.setFixedHeight(22)
        self.settings_title.setStyleSheet(
            "color: #111111; font-family: 'Microsoft YaHei UI'; "
            "font-size: 14px; font-weight: bold; background: transparent; border: none;"
        )
        controls_layout.addWidget(self.settings_title)
        self.aligned_controls = self._create_aligned_controls()
        controls_layout.addWidget(self.aligned_controls)
        controls_layout.addStretch(1)
        frame_layout.addLayout(controls_layout)

        self.preview_box = _ExportPreviewBox()
        self.preview_box.setReadOnly(True)
        self.preview_box.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.preview_box.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.preview_box.setPlainText(
            "导出预览\n\n"
            "当前为 UI 骨架阶段，后续会在这里显示按选项生成的导出内容预览。\n\n"
            "- 内容类型：日程 + 待办\n"
            "- 日程范围：某日\n"
            "- 导出格式：Markdown"
        )
        self.preview_box.clicked.connect(self._show_preview_popup)
        self.preview_box.setFixedSize(
            self.preview_width,
            self.default_preview_height,
        )
        self._apply_preview_surface_styles()
        frame_layout.addWidget(
            self.preview_box,
            0,
            Qt.AlignmentFlag.AlignTop,
        )
        frame_layout.addSpacing(4)

        root.addWidget(self.settings_frame, 1)
        self._sync_size_button_state()
        self._refresh_export_preview()
        self._update_header_icons()

    def _create_aligned_controls(self):
        area = QWidget()
        area.setFixedSize(264, 270)
        grid = QGridLayout(area)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(0)
        grid.setVerticalSpacing(2)
        grid.setColumnMinimumWidth(0, 2)
        grid.setColumnMinimumWidth(1, 82)
        grid.setColumnMinimumWidth(2, 10)
        grid.setColumnMinimumWidth(3, 170)

        for row in tuple(range(4)) + tuple(range(5, 10)) + tuple(range(11, 15)):
            grid.setRowMinimumHeight(row, 18)
        grid.setRowMinimumHeight(4, 4)
        grid.setRowMinimumHeight(10, 4)

        self._add_option_group_to_grid(
            grid,
            0,
            "内容类型",
            "content_type",
            ["仅日程", "仅待办", "日程 + 待办"],
            "日程 + 待办",
        )
        self.background_section = self._create_background_settings()
        grid.addWidget(
            self.background_section,
            0,
            3,
            4,
            1,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
        )

        self._add_option_group_to_grid(
            grid,
            5,
            "日程范围",
            "schedule_range",
            ["某日", "某周", "某月", "全部"],
            "某日",
        )
        self.font_section = self._create_font_settings()
        grid.addWidget(self.font_section, 5, 3, 5, 1)

        self._add_option_group_to_grid(
            grid,
            11,
            "导出格式",
            "export_format",
            ["Markdown", "PDF", "PNG"],
            "Markdown",
        )
        self.size_section = self._create_size_settings()
        grid.addWidget(
            self.size_section,
            11,
            3,
            4,
            1,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
        )
        return area

    def _add_option_group_to_grid(
        self,
        grid,
        title_row,
        title,
        group_key,
        labels,
        default_label,
    ):
        title_label = self._create_section_title(title)
        grid.addWidget(title_label, title_row, 0, 1, 2)

        line = QFrame()
        line.setFixedWidth(2)
        line.setStyleSheet(
            f"background-color: {AppConfig.COLOR_GRADIENT_START}; "
            "border: none; border-radius: 1px;"
        )
        grid.addWidget(line, title_row + 1, 0, len(labels), 1)

        radio_group = QButtonGroup(self)
        radio_group.setExclusive(True)
        self._radio_groups.append(radio_group)
        radio_style = f"""
            QRadioButton {{
                color: #333333;
                background: transparent;
                font-family: "Microsoft YaHei UI";
                font-size: 10px;
                spacing: 5px;
            }}
            QRadioButton::indicator {{
                width: 9px;
                height: 9px;
                border: 1px solid #777777;
                border-radius: 5px;
                background: transparent;
            }}
            QRadioButton::indicator:checked {{
                border: 1px solid {AppConfig.COLOR_GRADIENT_START};
                background-color: {AppConfig.COLOR_GRADIENT_START};
            }}
            QRadioButton::indicator:disabled {{
                border: 1px solid rgba(120, 120, 120, 0.45);
                background: transparent;
            }}
        """
        buttons = []
        for label in labels:
            button = QRadioButton(label)
            button.setProperty("option_value", label)
            button.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            button.setFixedHeight(18)
            button.setFixedWidth(76)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(radio_style)
            button.clicked.connect(
                lambda checked=False, key=group_key, value=label: self._handle_option_clicked(
                    key,
                    value,
                )
            )
            radio_group.addButton(button)
            grid.addWidget(
                button,
                title_row + 1 + len(buttons),
                1,
                alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            )
            buttons.append(button)
        self.option_groups[group_key] = buttons
        self._select_option(group_key, default_label)

    def _create_section_title(self, text):
        label = QLabel(text)
        label.setFixedHeight(18)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        label.setStyleSheet(
            "color: #222222; font-family: 'Microsoft YaHei UI'; "
            "font-size: 11px; font-weight: bold; background: transparent; border: none;"
        )
        return label

    def _create_background_settings(self):
        section = QWidget()
        section.setFixedSize(156, 78)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(self._create_section_title("背景设置"))

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)
        self.solid_background_preview = self._create_background_preview_item(
            "纯色",
            "solid",
        )
        self.gradient_background_preview = self._create_background_preview_item(
            "渐变",
            "gradient",
        )
        row.addWidget(self.solid_background_preview)
        row.addWidget(self.gradient_background_preview)
        row.addWidget(self._create_background_preview_item("默认", "disabled", "待"))
        row.addWidget(self._create_background_preview_item("自定义", "disabled", "+", 16))
        layout.addLayout(row)
        self._apply_background_preview_styles()
        return section

    def _create_background_preview_item(
        self,
        title,
        mode,
        preview_text="",
        preview_font_size=8,
    ):
        container = QWidget()
        container.setFixedWidth(36)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setFixedHeight(13)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            "color: #222222; font-family: 'Microsoft YaHei UI'; "
            "font-size: 8px; font-weight: bold; background: transparent; border: none;"
        )
        layout.addWidget(title_label)

        preview = _ExportClickableColorPreview(mode)
        preview.setFixedSize(36, 42)
        preview.setText(preview_text)
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if mode != "disabled":
            preview.clicked.connect(self._handle_background_preview_clicked)
        else:
            preview.setCursor(Qt.CursorShape.ArrowCursor)
        preview.setProperty("previewFontSize", preview_font_size)
        if mode == "solid":
            self.solid_background_chip = preview
        elif mode == "gradient":
            self.gradient_background_chip = preview
        elif mode == "disabled":
            preview.setStyleSheet(
                self._preview_chip_style(
                    "background-color: rgba(255, 255, 255, 0.76);",
                    preview_font_size,
                )
            )
        layout.addWidget(preview, 0, Qt.AlignmentFlag.AlignHCenter)
        return container

    def _create_font_settings(self):
        section = QWidget()
        section.setFixedSize(170, 98)
        grid = QGridLayout(section)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(3)
        grid.setVerticalSpacing(2)
        for row in range(5):
            grid.setRowMinimumHeight(row, 18)
        for column, width in enumerate((28, 20, 50, 14, 20, 20)):
            grid.setColumnMinimumWidth(column, width)

        grid.addWidget(self._create_section_title("字体"), 0, 0, 1, 6)

        self.font_labels = {}
        self.font_combos = {}
        self.font_language_buttons = {}
        self.font_color_chips = {}
        self.emphasis_labels = {}
        self.emphasis_buttons = {}
        for column, emphasis in ((4, "加粗"), (5, "斜体")):
            header = QLabel(emphasis)
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.setStyleSheet(
                "color: #333333; font-family: 'Microsoft YaHei UI'; "
                "font-size: 9px; background: transparent; border: none;"
            )
            grid.addWidget(header, 1, column)
            self.emphasis_labels[emphasis] = header

        for row_index, label in enumerate(("标题", "详情", "备注"), start=2):
            text_label = QLabel(label)
            text_label.setFixedSize(28, 18)
            text_label.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            text_label.setStyleSheet(
                "color: #333333; font-family: 'Microsoft YaHei UI'; "
                "font-size: 10px; background: transparent; border: none;"
            )

            language_button = QPushButton("中")
            language_button.setFixedSize(20, 18)
            language_button.setCursor(Qt.CursorShape.PointingHandCursor)
            language_button.setToolTip("点击切换为英文字体")
            language_button.setStyleSheet(self._font_language_button_style())
            language_button.clicked.connect(
                lambda checked=False, field=label: self._toggle_font_language(field)
            )

            combo = _ElidedComboBox()
            combo.setFixedSize(50, 18)
            combo.view().setTextElideMode(Qt.TextElideMode.ElideRight)
            combo.setStyleSheet(self._compact_combo_style())
            combo.currentTextChanged.connect(
                lambda value, field=label: self._remember_font_choice(field, value)
            )

            color_chip = _ExportClickableColorPreview("solid")
            color_chip.setFixedSize(14, 14)
            color_chip.setToolTip(f"选择{label}字体颜色")
            color_chip.clicked.connect(
                lambda _area, field=label: self._handle_font_color_clicked(field)
            )

            grid.addWidget(text_label, row_index, 0)
            grid.addWidget(language_button, row_index, 1)
            grid.addWidget(combo, row_index, 2)
            grid.addWidget(
                color_chip,
                row_index,
                3,
                alignment=Qt.AlignmentFlag.AlignCenter,
            )
            self.font_labels[label] = text_label
            self.font_combos[label] = combo
            self.font_language_buttons[label] = language_button
            self.font_color_chips[label] = color_chip
            self.emphasis_buttons[label] = {}
            for column, emphasis in ((4, "加粗"), (5, "斜体")):
                button = QRadioButton()
                button.setAutoExclusive(False)
                button.setFixedSize(14, 18)
                button.setToolTip(f"{label}{emphasis}")
                button.setStyleSheet(self._mini_radio_style())
                button.setChecked(label == "标题" and emphasis == "加粗")
                button.clicked.connect(self._refresh_export_preview)
                grid.addWidget(
                    button,
                    row_index,
                    column,
                    alignment=Qt.AlignmentFlag.AlignCenter,
                )
                self.emphasis_buttons[label][emphasis] = button
            self._populate_font_combo(label)
        self._apply_font_color_chip_styles()
        return section

    def _create_size_settings(self):
        section = QWidget()
        section.setFixedSize(156, 78)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.size_title = self._create_section_title("尺寸")
        layout.addWidget(self.size_title)

        self.size_widgets = []
        self.size_buttons = {}
        self._size_group = QButtonGroup(self)
        self._size_group.setExclusive(True)
        self._radio_groups.append(self._size_group)
        size_labels = ("3:2", "16:9", "4:3", "1:1", "9:16")
        for row_index in range(3):
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(12)
            for column_index in range(2):
                option_index = row_index * 2 + column_index
                if option_index < len(size_labels):
                    button = QRadioButton(size_labels[option_index])
                    button.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
                    button.setFixedSize(72, 18)
                    button.setStyleSheet(self._mini_radio_style())
                    button.clicked.connect(
                        lambda checked=False, value=size_labels[option_index]:
                        self._select_preview_size(value)
                    )
                    self._size_group.addButton(button)
                    row.addWidget(button)
                    self.size_widgets.append(button)
                    self.size_buttons[size_labels[option_index]] = button
                else:
                    custom_holder = QWidget()
                    custom_holder.setFixedSize(72, 18)
                    custom_layout = QHBoxLayout(custom_holder)
                    custom_layout.setContentsMargins(0, 0, 0, 0)
                    custom_layout.setSpacing(2)
                    width_edit = self._create_size_line_edit()
                    height_edit = self._create_size_line_edit()
                    self.custom_width_edit = width_edit
                    self.custom_height_edit = height_edit
                    separator = QLabel("*")
                    separator.setStyleSheet(
                        "color: #333333; background: transparent; border: none;"
                    )
                    custom_layout.addWidget(width_edit)
                    custom_layout.addWidget(separator)
                    custom_layout.addWidget(height_edit)
                    row.addWidget(custom_holder)
                    self.size_widgets.extend([custom_holder, width_edit, height_edit, separator])
            layout.addLayout(row)
        self.size_buttons[self._selected_preview_size].setChecked(True)
        self.custom_width_edit.textChanged.connect(self._apply_custom_preview_size)
        self.custom_height_edit.textChanged.connect(self._apply_custom_preview_size)
        return section

    def _create_size_line_edit(self):
        edit = QLineEdit()
        edit.setFixedSize(28, 18)
        edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        edit.setPlaceholderText("__")
        edit.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: rgba(255, 255, 255, 0.78);
                border: 1px solid rgba(255, 255, 255, 0.95);
                border-radius: 4px;
                color: {AppConfig.COLOR_GRADIENT_START};
                font-family: "Microsoft YaHei UI";
                font-size: 9px;
            }}
            QLineEdit:disabled {{
                color: rgba(105, 105, 105, 0.78);
                background-color: rgba(255, 255, 255, 0.16);
            }}
            """
        )
        return edit

    def _compact_combo_style(self):
        return f"""
            QComboBox {{
                background-color: rgba(255, 255, 255, 0.78);
                border: 1px solid rgba(255, 255, 255, 0.95);
                border-radius: 4px;
                color: {AppConfig.COLOR_GRADIENT_START};
                font-family: "Microsoft YaHei UI";
                font-size: 9px;
                padding-left: 4px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 14px;
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                color: {AppConfig.COLOR_GRADIENT_START};
                selection-background-color: rgba(0, 102, 204, 0.14);
            }}
        """

    def _font_language_button_style(self):
        return f"""
            QPushButton {{
                color: {AppConfig.COLOR_GRADIENT_START};
                background-color: rgba(255, 255, 255, 0.54);
                border: 1px solid rgba(255, 255, 255, 0.92);
                border-radius: 4px;
                font-family: "Microsoft YaHei UI";
                font-size: 9px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.78);
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.38);
            }}
        """

    def _toggle_font_language(self, field):
        self.font_languages[field] = "英" if self.font_languages[field] == "中" else "中"
        button = self.font_language_buttons[field]
        button.setText(self.font_languages[field])
        button.setToolTip(
            "点击切换为中文字体"
            if self.font_languages[field] == "英"
            else "点击切换为英文字体"
        )
        self._populate_font_combo(field)
        if hasattr(self, "preview_box"):
            self._refresh_export_preview()

    def _populate_font_combo(self, field):
        language = self.font_languages[field]
        fonts = (
            ["微软雅黑", "宋体", "黑体", "仿宋"]
            if language == "中"
            else ["Times New Roman", "Arial", "Calibri", "Georgia"]
        )
        combo = self.font_combos[field]
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(fonts)
        selected = self.font_choices[field][language]
        combo.setCurrentText(selected if selected in fonts else fonts[0])
        combo.blockSignals(False)

    def _remember_font_choice(self, field, value):
        if value:
            self.font_choices[field][self.font_languages[field]] = value
            if hasattr(self, "preview_box"):
                self._refresh_export_preview()

    def _mini_radio_style(self):
        return f"""
            QRadioButton {{
                color: #333333;
                background: transparent;
                font-family: "Microsoft YaHei UI";
                font-size: 10px;
                spacing: 5px;
            }}
            QRadioButton::indicator {{
                width: 9px;
                height: 9px;
                border: 1px solid #777777;
                border-radius: 5px;
                background: transparent;
            }}
            QRadioButton::indicator:checked {{
                border: 1px solid {AppConfig.COLOR_GRADIENT_START};
                background-color: {AppConfig.COLOR_GRADIENT_START};
            }}
            QRadioButton:disabled {{
                color: rgba(105, 105, 105, 0.78);
                font-family: "Microsoft YaHei UI";
                font-size: 10px;
            }}
            QRadioButton::indicator:disabled {{
                width: 9px;
                height: 9px;
                border: 1px solid rgba(105, 105, 105, 0.62);
                border-radius: 5px;
                background: transparent;
            }}
        """

    def _apply_background_preview_styles(self):
        if hasattr(self, "solid_background_chip"):
            self.solid_background_chip.setStyleSheet(
                self._preview_chip_style(
                    f"background-color: {self.export_solid_color};",
                    8,
                )
            )
        if hasattr(self, "gradient_background_chip"):
            self.gradient_background_chip.setStyleSheet(
                self._preview_chip_style(
                    "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
                    f"stop:0 {self.export_gradient_start}, "
                    f"stop:0.5 {self.export_gradient_start}, "
                    f"stop:0.5 {self.export_gradient_end}, "
                    f"stop:1 {self.export_gradient_end});",
                    8,
                )
            )
        if hasattr(self, "preview_box"):
            self._apply_preview_surface_styles()

    def _apply_preview_surface_styles(self):
        embedded_background, popup_background = self._preview_background_styles()
        self.preview_box.setStyleSheet(
            f"""
            QTextEdit {{
                {embedded_background};
                border: 1px solid rgba(255, 255, 255, 0.98);
                border-radius: 7px;
                color: {AppConfig.COLOR_GRADIENT_START};
                font-family: "Microsoft YaHei UI";
                font-size: 12px;
                padding: 10px;
            }}
            """
        )
        if self._preview_popup is not None:
            self._preview_popup.set_preview_background(popup_background)

    def _preview_background_styles(self):
        export_format = self._selected_option("export_format") or "Markdown"
        if export_format == "Markdown":
            return (
                "background-color: rgba(255, 255, 255, 0.96)",
                "background-color: rgba(255, 255, 255, 0.70)",
            )
        if self.export_background_mode == "gradient":
            embedded = (
                "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
                f"stop:0 {self.export_gradient_start}, "
                f"stop:1 {self.export_gradient_end})"
            )
            popup = (
                "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
                f"stop:0 {self.export_gradient_start}, "
                f"stop:1 {self.export_gradient_end})"
            )
            return embedded, popup
        return (
            f"background-color: {self.export_solid_color}",
            f"background-color: {self.export_solid_color}",
        )

    def _apply_font_color_chip_styles(self):
        if not hasattr(self, "font_color_chips"):
            return
        for field, chip in self.font_color_chips.items():
            chip.setStyleSheet(
                self._preview_chip_style(
                    f"background-color: {self.export_font_colors[field]};",
                    8,
                    border_radius=3,
                )
            )

    def _preview_chip_style(self, background_style, font_size, border_radius=4):
        return f"""
            QLabel {{
                {background_style}
                border: 1px solid rgba(120, 120, 120, 0.65);
                border-radius: {border_radius}px;
                color: #777777;
                font-family: "Microsoft YaHei UI";
                font-size: {font_size}px;
                font-weight: bold;
            }}
        """

    def _handle_background_preview_clicked(self, area):
        sender = self.sender()
        mode = getattr(sender, "mode", "")
        changed = False
        if mode == "solid":
            selected = self._choose_export_color(
                self.export_solid_color,
                "选择导出纯色背景颜色",
            )
            if selected:
                self.export_solid_color = selected
                self.export_background_mode = "solid"
                changed = True
        elif mode == "gradient":
            if area == "top":
                selected = self._choose_export_color(
                    self.export_gradient_start,
                    "选择导出背景上沿颜色",
                )
                if selected:
                    self.export_gradient_start = selected
                    self.export_background_mode = "gradient"
                    changed = True
            else:
                selected = self._choose_export_color(
                    self.export_gradient_end,
                    "选择导出背景下沿颜色",
                )
                if selected:
                    self.export_gradient_end = selected
                    self.export_background_mode = "gradient"
                    changed = True
        if changed:
            self._apply_background_preview_styles()

    def _handle_font_color_clicked(self, field):
        selected = self._choose_export_color(
            self.export_font_colors[field],
            f"选择导出{field}字体颜色",
        )
        if not selected:
            return
        self.export_font_colors[field] = selected
        self._apply_font_color_chip_styles()
        self._refresh_export_preview()

    def _choose_export_color(self, initial_color, title):
        selected = ThemedColorDialog.get_color(
            QColor(initial_color),
            title,
            AppConfig.COLOR_GRADIENT_START,
            self,
        )
        if not selected.isValid():
            return ""
        return selected.name()

    def _select_option(self, group_key, value):
        for button in self.option_groups.get(group_key, []):
            button.setChecked(button.property("option_value") == value)
            button.update()
        if group_key == "export_format":
            self._sync_size_button_state()
        if hasattr(self, "preview_box"):
            self._refresh_export_preview()

    def _selected_option(self, group_key):
        for button in self.option_groups.get(group_key, []):
            if button.isChecked():
                return button.property("option_value")
        return None

    def _handle_option_clicked(self, group_key, value):
        self._select_option(group_key, value)
        if group_key == "schedule_range" and value != "全部":
            self._show_range_picker(value)

    def _show_range_picker(self, range_label):
        range_kind = {
            "某日": "day",
            "某周": "week",
            "某月": "month",
        }.get(range_label)
        if range_kind is None:
            return
        button = self._option_button("schedule_range", range_label)
        if button is None:
            return

        if self._day_range_popup is not None:
            self._day_range_popup.close()
        if self._period_range_popup is not None:
            self._period_range_popup.close()

        selected_date = self._selected_range_dates[range_kind]
        if range_kind == "day":
            if self._day_range_popup is None:
                self._day_range_popup = CalendarPop(self, export_theme=True)
                self._day_range_popup.date_selected.connect(
                    self._apply_day_range_selection
                )
            anchor = button.mapToGlobal(QPoint(button.width() // 2, button.height()))
            self._day_range_popup.show_at(anchor, selected_date)
            screen = (
                QGuiApplication.screenAt(anchor)
                or QGuiApplication.primaryScreen()
            )
            if screen is not None:
                available = screen.availableGeometry()
                position = self._day_range_popup.pos()
                position.setX(
                    max(
                        available.left(),
                        min(
                            position.x(),
                            available.right() - self._day_range_popup.width() + 1,
                        ),
                    )
                )
                position.setY(
                    max(
                        available.top(),
                        min(
                            position.y(),
                            available.bottom() - self._day_range_popup.height() + 1,
                        ),
                    )
                )
                self._day_range_popup.move(position)
            return

        popup = ExportPeriodPickerPopup(range_kind, self)
        popup.period_selected.connect(
            lambda year, period, kind=range_kind: self._apply_period_range_selection(
                kind,
                year,
                period,
            )
        )
        if range_kind == "week":
            iso_year, iso_week, _ = selected_date.isocalendar()
            popup.set_selection(iso_year, iso_week)
        else:
            popup.set_selection(selected_date.year, selected_date.month)
        self._period_range_popup = popup
        popup.show_near(button)

    def _apply_day_range_selection(self, selected_date):
        self._selected_range_dates["day"] = selected_date
        self._update_range_button_text("day")
        self._select_option("schedule_range", "某日")

    def _apply_period_range_selection(self, range_kind, year, period):
        if range_kind == "week":
            selected_date = date.fromisocalendar(year, period, 1)
        else:
            selected_date = date(year, period, 1)
        self._selected_range_dates[range_kind] = selected_date
        self._update_range_button_text(range_kind)
        self._select_option(
            "schedule_range",
            "某周" if range_kind == "week" else "某月",
        )

    def _update_range_button_text(self, range_kind):
        range_label = {"day": "某日", "week": "某周", "month": "某月"}[range_kind]
        button = self._option_button("schedule_range", range_label)
        if button is None:
            return
        selected_date = self._selected_range_dates[range_kind]
        short_year = selected_date.year % 100
        if range_kind == "day":
            text = (
                f"{short_year:02d}年{selected_date.month:02d}月"
                f"{selected_date.day:02d}日"
            )
        elif range_kind == "week":
            iso_year, iso_week, _ = selected_date.isocalendar()
            text = f"{iso_year % 100:02d}年第{iso_week:02d}周"
        else:
            text = f"{short_year:02d}年{selected_date.month:02d}月"
        button.setText(text)
        button.setToolTip(text)

    def _option_button(self, group_key, value):
        for button in self.option_groups.get(group_key, []):
            if button.property("option_value") == value:
                return button
        return None

    def _current_export_options(self):
        content_type = {
            "仅日程": "schedule",
            "仅待办": "todo",
            "日程 + 待办": "all",
        }.get(self._selected_option("content_type"), "all")
        range_label = self._selected_option("schedule_range")
        range_kind = {
            "某日": "day",
            "某周": "week",
            "某月": "month",
            "全部": "all",
        }.get(range_label, "day")
        target_date = self._selected_range_dates.get(range_kind, date.today())
        return ExportOptions(
            content_type=content_type,
            range_kind=range_kind,
            target_date=target_date,
            group_by="date",
        )

    def _current_pdf_style(self):
        def text_style(field):
            emphasis = self.emphasis_buttons[field]
            return PdfTextStyle(
                font_family=self.font_combos[field].currentText() or "微软雅黑",
                color=self.export_font_colors[field],
                bold=emphasis["加粗"].isChecked(),
                italic=emphasis["斜体"].isChecked(),
            )

        return PdfExportStyle(
            background_mode=self.export_background_mode,
            solid_color=self.export_solid_color,
            gradient_start=self.export_gradient_start,
            gradient_end=self.export_gradient_end,
            title=text_style("标题"),
            detail=text_style("详情"),
            note=text_style("备注"),
        )

    def _handle_export_requested(self):
        export_format = self._selected_option("export_format") or "Markdown"
        if export_format not in {"Markdown", "PDF"}:
            show_center_toast(
                self,
                f"{export_format} 导出尚未接入",
                attr_name="_export_result_toast",
                duration_ms=1400,
            )
            return

        options = self._current_export_options()
        extension = ".md" if export_format == "Markdown" else ".pdf"
        file_filter = (
            "Markdown 文件 (*.md)"
            if export_format == "Markdown"
            else "PDF 文件 (*.pdf)"
        )
        file_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            f"导出 {export_format}",
            self._default_export_filename(options, extension),
            file_filter,
        )
        if not file_path:
            return

        target = Path(file_path)
        if target.suffix.lower() != extension:
            target = target.with_suffix(extension)

        try:
            if self._export_service is None:
                self._export_service = ScheduleExportService()
            if export_format == "Markdown":
                exported_path = self._export_service.write_markdown(target, options)
            else:
                exported_path = self._export_service.write_pdf(
                    target,
                    options,
                    self._current_pdf_style(),
                )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "导出失败",
                f"{export_format} 文件保存失败：\n{exc}",
            )
            return

        show_center_toast(
            self,
            f"已导出：{exported_path.name}",
            attr_name="_export_result_toast",
            duration_ms=1800,
        )

    @staticmethod
    def _default_export_filename(options, extension):
        content_text = {
            "schedule": "日程",
            "todo": "待办",
            "all": "日程与待办",
        }.get(options.content_type, "日程与待办")
        target = options.target_date
        if options.range_kind == "day":
            range_text = target.isoformat()
        elif options.range_kind == "week":
            iso_year, iso_week, _weekday = target.isocalendar()
            range_text = f"{iso_year}年第{iso_week:02d}周"
        elif options.range_kind == "month":
            range_text = f"{target.year}-{target.month:02d}"
        else:
            range_text = "全部"
        return f"{content_text}_{range_text}{extension}"

    @staticmethod
    def _default_markdown_filename(options):
        return ExportSchedulePanel._default_export_filename(options, ".md")

    def _refresh_export_preview(self):
        if not hasattr(self, "preview_box"):
            return
        try:
            if self._export_service is None:
                self._export_service = ScheduleExportService()
            markdown = self._export_service.render_markdown(
                self._current_export_options()
            )
            export_format = self._selected_option("export_format") or "Markdown"
            if export_format == "Markdown":
                preview_text = markdown
            elif export_format == "PDF":
                preview_text = (
                    "# PDF 导出预览\n\n"
                    "当前背景、字体、字体颜色、加粗和斜体设置会应用到 PDF 文件。\n\n"
                    f"{markdown}"
                )
            else:
                preview_text = (
                    f"{export_format} 导出尚未接入，当前先显示同一份导出数据的 "
                    "Markdown 结构预览。\n\n"
                    f"{markdown}"
                )
        except Exception as exc:
            preview_text = f"导出预览生成失败：{exc}"
        preview_html = self._build_preview_html(preview_text)
        self._preview_plain_text = preview_text
        self._preview_html = preview_html
        self.preview_box.setHtml(preview_html)
        if self._preview_popup is not None:
            self._preview_popup.set_preview_html(preview_html)

    def _build_preview_html(self, preview_text):
        lines = []
        for line in preview_text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                field = "标题"
            elif stripped == "详情：" or stripped.startswith(">"):
                field = "详情"
            else:
                field = "备注"
            style = self._preview_text_style(field)
            content = escape(line) if line else "&nbsp;"
            lines.append(
                f'<div style="{style}; white-space: pre-wrap; margin: 0 0 4px 0;">'
                f"{content}</div>"
            )
        return (
            '<html><body style="margin:0; padding:0; background:transparent;">'
            + "".join(lines)
            + "</body></html>"
        )

    def _preview_text_style(self, field):
        export_format = self._selected_option("export_format") or "Markdown"
        if export_format == "Markdown":
            color = AppConfig.COLOR_GRADIENT_START
            font_family = "Microsoft YaHei UI"
            font_weight = "600" if field == "标题" else "400"
            font_style = "normal"
        else:
            color = self.export_font_colors[field]
            font_family = self.font_combos[field].currentText() or "Microsoft YaHei UI"
            emphasis = self.emphasis_buttons[field]
            font_weight = "700" if emphasis["加粗"].isChecked() else "400"
            font_style = (
                "italic" if emphasis["斜体"].isChecked() else "normal"
            )
        return (
            f"color:{color}; font-family:'{escape(font_family, quote=True)}'; "
            f"font-size:12px; font-weight:{font_weight}; font-style:{font_style}"
        )

    def _sync_size_button_state(self):
        if not hasattr(self, "size_section"):
            return
        export_format = self._selected_option("export_format")
        visual_style_enabled = export_format in {"PDF", "PNG"}
        size_enabled = export_format == "PNG"
        self._set_section_enabled(self.background_section, visual_style_enabled)
        self._set_section_enabled(self.font_section, visual_style_enabled)
        self._set_section_enabled(self.size_section, size_enabled)
        self.size_title.setStyleSheet(
            "color: #222222; font-family: 'Microsoft YaHei UI'; "
            "font-size: 11px; font-weight: bold; background: transparent; border: none;"
            if size_enabled
            else "color: rgba(105, 105, 105, 0.78); font-family: 'Microsoft YaHei UI'; "
            "font-size: 11px; font-weight: bold; background: transparent; border: none;"
        )
        for widget in getattr(self, "size_widgets", []):
            widget.setEnabled(size_enabled)
            if isinstance(widget, QLabel):
                widget.setStyleSheet(
                    "color: #333333; background: transparent; border: none;"
                    if size_enabled
                    else "color: rgba(105, 105, 105, 0.78); "
                    "background: transparent; border: none;"
                )
        if hasattr(self, "preview_box"):
            if size_enabled:
                self._apply_selected_preview_size()
            else:
                self.set_preview_width(self.default_preview_width)
            self._apply_preview_surface_styles()
        self.updateGeometry()

    def _set_section_enabled(self, section, enabled):
        section.setEnabled(enabled)
        effect = section.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(section)
            section.setGraphicsEffect(effect)
        effect.setOpacity(1.0 if enabled else 0.42)

    def _select_preview_size(self, label):
        self._selected_preview_size = label
        for edit in (
            getattr(self, "custom_width_edit", None),
            getattr(self, "custom_height_edit", None),
        ):
            if edit is not None:
                edit.blockSignals(True)
                edit.clear()
                edit.blockSignals(False)
        if self._selected_option("export_format") == "PNG":
            self._apply_selected_preview_size()

    def _apply_selected_preview_size(self):
        ratio_map = {
            "3:2": (3, 2),
            "16:9": (16, 9),
            "4:3": (4, 3),
            "1:1": (1, 1),
            "9:16": (9, 16),
        }
        ratio = ratio_map.get(self._selected_preview_size)
        if ratio is not None:
            self._apply_preview_ratio(*ratio)

    def _apply_custom_preview_size(self):
        if self._selected_option("export_format") != "PNG":
            return
        try:
            width = int(self.custom_width_edit.text())
            height = int(self.custom_height_edit.text())
        except ValueError:
            return
        if width <= 0 or height <= 0:
            return
        self._size_group.setExclusive(False)
        for button in self.size_buttons.values():
            button.setChecked(False)
        self._size_group.setExclusive(True)
        self._selected_preview_size = None
        self._apply_preview_ratio(width, height)

    def _apply_preview_ratio(self, width, height):
        if not hasattr(self, "preview_box") or height <= 0:
            return
        preview_height = self.preview_box.height()
        if preview_height <= 0:
            return
        self.set_preview_width(round(preview_height * width / height))

    def _show_preview_popup(self):
        text = getattr(self, "_preview_plain_text", self.preview_box.toPlainText())
        if self._preview_popup is None:
            self._preview_popup = _ExportPreviewPopup(text, self)
        self._preview_popup.set_preview_html(
            getattr(self, "_preview_html", self._build_preview_html(text))
        )
        self._apply_preview_surface_styles()
        self._preview_popup.set_preview_size(self.preview_box.size())
        self._preview_popup.show_near(self)

    def _toggle_background_popup(self):
        return

    def _toggle_pin(self):
        self.set_pinned(not self.is_pinned)

    def set_pinned(self, enabled):
        self.is_pinned = bool(enabled)
        set_window_pin_state(self, self.is_pinned)
        self._update_header_icons()

    def _load_tinted_icon(self, icon_name, color, target_size):
        path = f"assets/icons/{icon_name}"
        if not path.lower().endswith(".svg"):
            pixmap = QPixmap(path)
            if pixmap.isNull():
                return QIcon()
            image = pixmap.toImage().convertToFormat(QImage.Format.Format_ARGB32)
            painter = QPainter(image)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            painter.fillRect(image.rect(), QColor(color))
            painter.end()
            return QIcon(QPixmap.fromImage(image))

        renderer = QSvgRenderer(path)
        if not renderer.isValid():
            return QIcon()
        ratio = max(self.devicePixelRatioF(), 1.0)
        pixmap = QPixmap(round(target_size * ratio), round(target_size * ratio))
        pixmap.setDevicePixelRatio(ratio)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter, QRectF(0, 0, target_size, target_size))
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(QRectF(0, 0, target_size, target_size), QColor(color))
        painter.end()
        return QIcon(pixmap)

    def _update_header_icons(self):
        self.btn_print.setIcon(self._load_tinted_icon("printer.svg", "#FFFFFF", 16))
        pin_color = "#FFFFFF" if self.is_pinned else "#96FFFFFF"
        self.btn_pin.setIcon(self._load_tinted_icon("pin.svg", pin_color, 16))
        self.btn_close.setIcon(self._load_tinted_icon("close.png", "#FFFFFF", 12))

    def _update_header_button_positions(self):
        close_x = self.width() - self.btn_close.width()
        self.btn_close.move(close_x, 0)
        self.btn_close.raise_()
        self.btn_pin.move(close_x - self.btn_pin.width(), 0)
        self.btn_pin.raise_()
        self.btn_print.move(
            close_x - self.btn_pin.width() - self.btn_print.width(),
            0,
        )
        self.btn_print.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_header_button_positions()

    def closeEvent(self, event):
        if self._preview_popup is not None:
            self._preview_popup.close()
        if self._background_popup is not None:
            self._background_popup.close()
        if self._day_range_popup is not None:
            self._day_range_popup.close()
        if self._period_range_popup is not None:
            self._period_range_popup.close()
        super().closeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())
            if child not in (self.btn_close, self.btn_pin, self.btn_print):
                self._drag_offset = event.globalPosition().toPoint() - self.pos()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self._drag_offset is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_offset = None
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 12, 12)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        painter.fillPath(path, gradient)
