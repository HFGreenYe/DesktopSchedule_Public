from datetime import date, timedelta
from html import escape
from pathlib import Path

from PyQt6.QtCore import (
    QEvent,
    QPoint,
    QPointF,
    QRect,
    QRectF,
    QSize,
    Qt,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QColor,
    QGuiApplication,
    QIcon,
    QImage,
    QIntValidator,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPixmap,
)
from PyQt6.QtPdf import QPdfDocument, QPdfPageRenderer
from PyQt6.QtPdfWidgets import QPdfView
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
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.config import AppConfig
from src.services.export_background_presets import (
    DEFAULT_EXPORT_BACKGROUND_PRESETS,
    get_export_background_image_path,
    get_export_background_preset,
)


def _theme_preview_bg_rgba():
    """白色，用于 PDF/PNG 预览框背景（stylesheet）。"""
    return "#FFFFFF"


def _theme_preview_bg_qcolor():
    """白色 QColor，用于 QPainter 绘制。"""
    return QColor("#FFFFFF")
from src.services.schedule_export_service import (
    ExportOptions,
    PdfExportStyle,
    PdfTextStyle,
    PngCanvasSpec,
    ScheduleExportService,
)
from src.services.schedule_png_exporter import SchedulePngExporter
from src.services.schedule_pdf_preview_service import SchedulePdfPreviewController
from src.ui.calendar_pop import CalendarPop
from src.ui.common.toast import show_center_toast
from src.ui.common.themed_color_dialog import ThemedColorDialog
from src.ui.components import get_colored_icon
from src.ui.popups.export_range_picker import ExportPeriodPickerPopup
from src.utils.export_style_preferences import (
    get_export_style_preferences,
    set_export_style_preferences,
)
from src.ui.popups.export_default_background_popup import (
    ExportDefaultBackgroundPopup,
    paint_default_background_pattern,
)
from src.ui.popups.export_background_crop_popup import (
    ExportBackgroundCropPopup,
)
from src.utils.window_preferences import set_window_pin_state


PNG_SIZE_PRESETS = {
    "2:3": PngCanvasSpec(1200, 1800),
    "16:9": PngCanvasSpec(1920, 1080),
    "3:4": PngCanvasSpec(1200, 1600),
    "1:1": PngCanvasSpec(1600, 1600),
    "9:16": PngCanvasSpec(1080, 1920),
}


class _PdfThumbnailSurface(QWidget):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._image = QImage()
        self._page_count = 0
        self._page_unit = "页"
        self._status_text = "正在生成 PDF 预览…"
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_loading(self, text="正在生成 PDF 预览…", page_unit="页"):
        self._image = QImage()
        self._page_count = 0
        self._page_unit = page_unit
        self._status_text = text
        self.update()

    def set_preview(self, image, page_count, page_unit="页"):
        self._image = QImage(image)
        self._page_count = max(0, int(page_count))
        self._page_unit = page_unit
        self._status_text = ""
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.fillRect(self.rect(), _theme_preview_bg_qcolor())
        if self._image.isNull():
            painter.setPen(QColor("#555555"))
            painter.drawText(
                self.rect().adjusted(12, 12, -12, -12),
                Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
                self._status_text,
            )
            return

        footer_height = 24
        available = QSize(
            max(1, self.width() - 12),
            max(1, self.height() - footer_height - 12),
        )
        scaled = self._image.scaled(
            available,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        left = (self.width() - scaled.width()) / 2
        top = 6 + max(0, (available.height() - scaled.height()) / 2)
        page_rect = QRectF(left, top, scaled.width(), scaled.height())
        shadow_rect = page_rect.translated(2, 2)
        painter.fillRect(shadow_rect, QColor(0, 0, 0, 48))
        painter.drawImage(page_rect, scaled)
        painter.setPen(QColor("#8A8A8A"))
        painter.drawRect(page_rect)

        page_text = f"共 {self._page_count} {self._page_unit}"
        badge_width = max(52, painter.fontMetrics().horizontalAdvance(page_text) + 16)
        badge_rect = QRectF(
            (self.width() - badge_width) / 2,
            self.height() - footer_height + 2,
            badge_width,
            18,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 224))
        painter.drawRoundedRect(badge_rect, 9, 9)
        painter.setPen(QColor("#4A4A4A"))
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, page_text)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            event.accept()
            return
        super().mousePressEvent(event)


class _ExportPreviewBox(QTextEdit):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdf_surface = _PdfThumbnailSurface(self.viewport())
        self.pdf_surface.clicked.connect(self.clicked)
        self.pdf_surface.hide()

    def show_text_preview(self):
        self.pdf_surface.hide()

    def show_pdf_loading(self, text="正在生成 PDF 预览…", page_unit="页"):
        self.clear()
        self.pdf_surface.setGeometry(self.viewport().rect())
        self.pdf_surface.set_loading(text, page_unit)
        self.pdf_surface.show()
        self.pdf_surface.raise_()

    def show_pdf_preview(self, image, page_count, page_unit="页"):
        self.clear()
        self.pdf_surface.setGeometry(self.viewport().rect())
        self.pdf_surface.set_preview(image, page_count, page_unit)
        self.pdf_surface.show()
        self.pdf_surface.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.pdf_surface.setGeometry(self.viewport().rect())

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
        self._background_selected = False
        self._default_background_index = 0
        self._custom_background_path = ""
        self._custom_background_crop = None
        self._custom_background_image = QImage()
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_background_selected(self, selected):
        self._background_selected = bool(selected)
        self.update()

    def set_default_background_index(self, index):
        self._default_background_index = int(index)
        self.update()

    def set_custom_background(self, image_path, crop=None):
        normalized_path = str(image_path or "")
        if normalized_path != self._custom_background_path:
            self._custom_background_path = normalized_path
            self._custom_background_image = QImage(normalized_path)
        self._custom_background_crop = crop
        self.setToolTip(
            f"自定义背景：{Path(normalized_path).name}"
            if normalized_path
            else "选择自定义导出背景"
        )
        self.update()

    def paintEvent(self, event):
        if self.mode not in {"default", "custom"}:
            super().paintEvent(event)
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, 4, 4)
        painter.save()
        painter.setClipPath(path)
        if self.mode == "default":
            paint_default_background_pattern(
                painter,
                rect,
                self._default_background_index,
            )
        elif not self._custom_background_image.isNull():
            image_rect = QRectF(self._custom_background_image.rect())
            crop = self._custom_background_crop
            if crop and len(crop) == 4:
                crop_x, crop_y, crop_width, crop_height = crop
                image_rect = QRectF(
                    crop_x * self._custom_background_image.width(),
                    crop_y * self._custom_background_image.height(),
                    crop_width * self._custom_background_image.width(),
                    crop_height * self._custom_background_image.height(),
                )
            painter.drawImage(rect, self._custom_background_image, image_rect)
        else:
            painter.fillPath(path, QColor(255, 255, 255, 194))
            painter.setPen(QColor(105, 105, 105))
            font = painter.font()
            font.setPixelSize(16)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "+")
        painter.restore()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(
            QColor("#FFFFFF")
            if self._background_selected
            else QColor(120, 120, 120, 166)
        )
        painter.drawRoundedRect(rect, 4, 4)

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
    print_requested = pyqtSignal()

    _ZOOM_STEP_FACTOR = 1.12
    _MIN_ZOOM_RATIO = 0.25
    _MAX_ZOOM_RATIO = 4.0
    _MIN_TEXT_ZOOM_STEPS = -6
    _MAX_TEXT_ZOOM_STEPS = 18

    def __init__(self, text, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._source_preview_size = QSize(168, 296)
        self._drag_offset = None
        self._document_format = "PDF"
        self._page_unit = "页"
        self._text_zoom_steps = 0
        self._pdf_zoom_expected_page = -1
        self._pdf_zoom_expected_width = 0

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
        printer_pixmap = get_colored_icon("printer.svg", "#FFFFFF", 16)
        self.printer_icon = QLabel(self)
        self.printer_icon.setFixedSize(30, 30)
        self.printer_icon.setPixmap(printer_pixmap)
        self.printer_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.printer_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.printer_icon.setToolTip("导出日程")
        self.printer_icon.setStyleSheet("background: transparent; border: none;")
        self.printer_icon.installEventFilter(self)
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

        self.preview_stack = QStackedWidget(self.content_frame)
        self.preview_editor = QTextEdit()
        self.preview_editor.setReadOnly(True)
        self.preview_editor.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.preview_editor.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.preview_editor.setPlainText(text)
        self.preview_editor.setToolTip("按住 Ctrl 并滚动鼠标滚轮可缩放预览")
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
        pdf_bg = _theme_preview_bg_rgba()
        self.pdf_status = QLabel("正在生成 PDF 预览…")
        self.pdf_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pdf_status.setWordWrap(True)
        self.pdf_status.setStyleSheet(
            f"color: #555555; background: {pdf_bg}; border: none; "
            "font-family: 'Microsoft YaHei UI'; font-size: 12px; padding: 16px;"
        )
        self.pdf_view = QPdfView(self.preview_stack)
        self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        self.pdf_view.setPageSpacing(12)
        self.pdf_view.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.pdf_view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.pdf_view.setStyleSheet(
            f"QPdfView {{ background: {pdf_bg}; border: none; }}"
        )
        self.pdf_view.setToolTip("按住 Ctrl 并滚动鼠标滚轮可缩放预览")
        self._pdf_zoom_overlay = QLabel(self.pdf_view.viewport())
        self._pdf_zoom_overlay.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )
        self._pdf_zoom_overlay.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self._pdf_zoom_overlay.setStyleSheet(
            f"background: {pdf_bg}; border: none;"
        )
        self._pdf_zoom_overlay.hide()
        self._pdf_zoom_overlay_timeout = QTimer(self)
        self._pdf_zoom_overlay_timeout.setSingleShot(True)
        self._pdf_zoom_overlay_timeout.setInterval(1500)
        self._pdf_zoom_overlay_timeout.timeout.connect(
            self._finish_pdf_zoom_transition
        )
        self._pdf_page_renderer = self.pdf_view.findChild(QPdfPageRenderer)
        if self._pdf_page_renderer is not None:
            self._pdf_page_renderer.pageRendered.connect(
                self._handle_pdf_page_rendered
            )
        self.pdf_view.pageNavigator().currentPageChanged.connect(
            self._update_pdf_title
        )
        self._pdf_page_count = 0
        self.preview_stack.addWidget(self.preview_editor)
        self.preview_stack.addWidget(self.pdf_status)
        self.preview_stack.addWidget(self.pdf_view)
        content_layout.addWidget(self.preview_stack)
        layout.addWidget(self.content_frame, 1)
        self.header_holder.installEventFilter(self)
        self.title.installEventFilter(self)
        self.content_frame.installEventFilter(self)
        self.preview_editor.viewport().installEventFilter(self)
        self.pdf_view.viewport().installEventFilter(self)
        self.set_preview_size(self._source_preview_size)
        self._update_close_button_position()

    def set_preview_html(self, html):
        if self._text_zoom_steps > 0:
            self.preview_editor.zoomOut(self._text_zoom_steps)
        elif self._text_zoom_steps < 0:
            self.preview_editor.zoomIn(-self._text_zoom_steps)
        self._text_zoom_steps = 0
        self.preview_editor.setHtml(html)
        self.title.setText("导出预览")
        self.preview_stack.setCurrentWidget(self.preview_editor)
        self.set_preview_size(self._source_preview_size)

    def set_pdf_loading(self, text="正在生成 PDF 预览…", format_name="PDF"):
        self._document_format = format_name
        self._page_unit = "张" if format_name == "PNG" else "页"
        self.pdf_status.setText(text)
        self.title.setText(f"导出预览 · {format_name}")
        self.preview_stack.setCurrentWidget(self.pdf_status)
        self.set_preview_size(self._source_preview_size)

    def set_pdf_document(self, document, format_name="PDF"):
        self._finish_pdf_zoom_transition()
        self._document_format = format_name
        self._page_unit = "张" if format_name == "PNG" else "页"
        self.pdf_view.setDocument(document)
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        self._pdf_page_count = document.pageCount()
        self.preview_stack.setCurrentWidget(self.pdf_view)
        self.set_preview_size(self._source_preview_size)
        self._update_pdf_title(self.pdf_view.pageNavigator().currentPage())

    def clear_pdf_document(self):
        self._finish_pdf_zoom_transition()
        self.pdf_view.setDocument(None)
        self._pdf_page_count = 0

    def _update_pdf_title(self, page=0):
        if self._pdf_page_count <= 0:
            self.title.setText(f"导出预览 · {self._document_format}")
            return
        current_page = max(0, int(page)) + 1
        self.title.setText(
            f"导出预览 · {self._document_format} "
            f"{current_page}/{self._pdf_page_count}"
        )

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
        pdf_height_padding = (
            max(0, self.pdf_view.pageSpacing() - 4)
            if hasattr(self, "pdf_view")
            and self.preview_stack.currentWidget() in (self.pdf_status, self.pdf_view)
            else 0
        )
        self.setFixedSize(
            content_width + 28,
            content_height + 56 + pdf_height_padding,
        )
        self._update_close_button_position()

    def _update_close_button_position(self):
        self.close_btn.move(self.width() - self.close_btn.width(), 0)
        self.close_btn.raise_()
        if hasattr(self, "printer_icon"):
            self.printer_icon.move(
                self.width() - self.close_btn.width() - self.printer_icon.width(), 0
            )
            self.printer_icon.raise_()
        self.title.setMaximumWidth(
            max(1, self.width() - self.close_btn.width() - self.printer_icon.width() - 28)
        )

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
        if (
            watched is self.printer_icon
            and event.type() == QEvent.Type.MouseButtonRelease
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self.print_requested.emit()
            event.accept()
            return True
        if (
            watched in (self.preview_editor.viewport(), self.pdf_view.viewport())
            and event.type() == QEvent.Type.Wheel
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            wheel_steps = self._wheel_zoom_steps(event)
            if wheel_steps:
                if watched is self.pdf_view.viewport():
                    self._zoom_pdf_preview(wheel_steps, event.position())
                else:
                    self._zoom_text_preview(wheel_steps)
            event.accept()
            return True
        if (
            watched is self.pdf_view.viewport()
            and event.type() == QEvent.Type.Resize
        ):
            self._pdf_zoom_overlay.setGeometry(self.pdf_view.viewport().rect())
        header_drag = watched in (self.header_holder, self.title)
        content_drag = watched is self.content_frame
        preview_drag = watched is self.preview_editor.viewport()
        pdf_drag = watched is self.pdf_view.viewport()
        if header_drag or content_drag or preview_drag or pdf_drag:
            if (
                event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
                and (
                    header_drag
                    or content_drag
                    or pdf_drag
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

    @staticmethod
    def _wheel_zoom_steps(event):
        delta = event.angleDelta().y()
        threshold = 120
        if not delta:
            delta = event.pixelDelta().y()
            threshold = 40
        if not delta:
            return 0
        steps = int(delta / threshold)
        if not steps:
            steps = 1 if delta > 0 else -1
        return max(-4, min(4, steps))

    def _zoom_text_preview(self, wheel_steps):
        target_steps = max(
            self._MIN_TEXT_ZOOM_STEPS,
            min(self._MAX_TEXT_ZOOM_STEPS, self._text_zoom_steps + wheel_steps),
        )
        applied_steps = target_steps - self._text_zoom_steps
        if applied_steps > 0:
            self.preview_editor.zoomIn(applied_steps)
        elif applied_steps < 0:
            self.preview_editor.zoomOut(-applied_steps)
        self._text_zoom_steps = target_steps

    def _zoom_pdf_preview(self, wheel_steps, anchor_position):
        fit_factor = self._pdf_fit_width_factor()
        if fit_factor <= 0:
            return
        if self.pdf_view.zoomMode() == QPdfView.ZoomMode.Custom:
            current_factor = self.pdf_view.zoomFactor()
        else:
            current_factor = fit_factor
        minimum_factor = fit_factor * self._MIN_ZOOM_RATIO
        maximum_factor = fit_factor * self._MAX_ZOOM_RATIO
        target_factor = max(
            minimum_factor,
            min(
                maximum_factor,
                current_factor * (self._ZOOM_STEP_FACTOR**wheel_steps),
            ),
        )
        if abs(target_factor - current_factor) < 0.0001:
            return

        horizontal_bar = self.pdf_view.horizontalScrollBar()
        vertical_bar = self.pdf_view.verticalScrollBar()
        old_horizontal = horizontal_bar.value()
        old_vertical = vertical_bar.value()
        scale_ratio = target_factor / current_factor
        anchor_x = anchor_position.x()
        anchor_y = anchor_position.y()

        self._show_pdf_zoom_transition(scale_ratio, anchor_position)
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.Custom)
        self.pdf_view.setZoomFactor(target_factor)
        self._set_expected_pdf_render(target_factor)

        def restore_anchor():
            horizontal_bar.setValue(
                round((old_horizontal + anchor_x) * scale_ratio - anchor_x)
            )
            vertical_bar.setValue(
                round((old_vertical + anchor_y) * scale_ratio - anchor_y)
            )

        QTimer.singleShot(0, restore_anchor)

    def _show_pdf_zoom_transition(self, scale_ratio, anchor_position):
        viewport = self.pdf_view.viewport()
        if self._pdf_zoom_overlay.isVisible():
            snapshot = self._pdf_zoom_overlay.pixmap()
        else:
            snapshot = viewport.grab()
        if snapshot is None or snapshot.isNull():
            return

        if scale_ratio < 1.0:
            transition = QPixmap(snapshot)
        else:
            transition = QPixmap(snapshot.size())
            transition.setDevicePixelRatio(snapshot.devicePixelRatio())
            transition.fill(_theme_preview_bg_qcolor())
            painter = QPainter(transition)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            painter.translate(anchor_position)
            painter.scale(scale_ratio, scale_ratio)
            painter.translate(-anchor_position)
            painter.drawPixmap(0, 0, snapshot)
            painter.end()

        self._pdf_zoom_overlay.setGeometry(viewport.rect())
        self._pdf_zoom_overlay.setPixmap(transition)
        self._pdf_zoom_overlay.show()
        self._pdf_zoom_overlay.raise_()
        self._pdf_zoom_overlay_timeout.start()

    def _set_expected_pdf_render(self, target_factor):
        document = self.pdf_view.document()
        if document is None or document.pageCount() <= 0:
            self._pdf_zoom_expected_page = -1
            self._pdf_zoom_expected_width = 0
            return
        current_page = self.pdf_view.pageNavigator().currentPage()
        page_index = max(0, min(int(current_page), document.pageCount() - 1))
        page_width = document.pagePointSize(page_index).width()
        logical_width = page_width * self.pdf_view.logicalDpiX() / 72.0
        self._pdf_zoom_expected_page = page_index
        self._pdf_zoom_expected_width = round(
            logical_width * target_factor * self.pdf_view.devicePixelRatioF()
        )

    def _handle_pdf_page_rendered(self, page_number, image_size, *_args):
        if not self._pdf_zoom_overlay.isVisible():
            return
        if int(page_number) != self._pdf_zoom_expected_page:
            return
        width_tolerance = max(3, round(self._pdf_zoom_expected_width * 0.02))
        if abs(image_size.width() - self._pdf_zoom_expected_width) > width_tolerance:
            return
        self.pdf_view.viewport().repaint()
        self._finish_pdf_zoom_transition()

    def _finish_pdf_zoom_transition(self):
        if hasattr(self, "_pdf_zoom_overlay_timeout"):
            self._pdf_zoom_overlay_timeout.stop()
        if hasattr(self, "_pdf_zoom_overlay"):
            self._pdf_zoom_overlay.hide()
            self._pdf_zoom_overlay.clear()
        self._pdf_zoom_expected_page = -1
        self._pdf_zoom_expected_width = 0

    def _pdf_fit_width_factor(self):
        document = self.pdf_view.document()
        if document is None or document.pageCount() <= 0:
            return 0.0
        current_page = self.pdf_view.pageNavigator().currentPage()
        page_index = max(0, min(int(current_page), document.pageCount() - 1))
        page_size = document.pagePointSize(page_index)
        if page_size.width() <= 0:
            return 0.0
        margins = self.pdf_view.documentMargins()
        available_width = max(
            1,
            self.pdf_view.viewport().width() - margins.left() - margins.right(),
        )
        page_pixel_width = page_size.width() * self.pdf_view.logicalDpiX() / 72.0
        return available_width / page_pixel_width

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
        self._background_crop_popup = None
        self._background_crop_cache = {}
        self._background_crop_request = None
        self._export_style_preferences = get_export_style_preferences()
        self._active_style_format = "Markdown"
        self._restoring_export_style = False
        self._export_ui_ready = False
        self._day_range_popup = None
        self._period_range_popup = None
        self._export_service = None
        self._pdf_document = None
        self._pdf_document_path = ""
        self._loaded_preview_format = ""
        self._pending_pdf_document = None
        self._pending_pdf_document_path = ""
        self._pdf_preview_controller = SchedulePdfPreviewController(
            self._build_pdf_preview_payload,
            self,
            debounce_ms=300,
        )
        self._pdf_preview_controller.preview_ready.connect(
            self._handle_pdf_preview_ready
        )
        self._pdf_preview_controller.preview_failed.connect(
            self._handle_pdf_preview_failed
        )
        application = QGuiApplication.instance()
        if application is not None:
            application.aboutToQuit.connect(self._shutdown_pdf_preview)
            application.aboutToQuit.connect(self._persist_active_export_style)
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
        self.export_default_background_index = 0
        self.export_default_background_crop = None
        self.export_custom_background_path = ""
        self.export_custom_background_crop = None
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
        self._export_ui_ready = True
        self._restore_format_style(self._active_style_format)
        self._sync_size_button_state()
        self._apply_background_preview_styles()
        self._apply_font_color_chip_styles()
        self._refresh_export_preview()
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
        self.default_background_preview = self._create_background_preview_item(
            "默认",
            "default",
            "图",
        )
        row.addWidget(self.default_background_preview)
        self.custom_background_preview = self._create_background_preview_item(
            "自定义",
            "custom",
            "+",
            16,
        )
        row.addWidget(self.custom_background_preview)
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
        if mode == "default":
            preview.clicked.connect(lambda _area: self._toggle_background_popup())
        elif mode == "custom":
            preview.clicked.connect(lambda _area: self._choose_custom_background())
        else:
            preview.clicked.connect(self._handle_background_preview_clicked)
        preview.setProperty("previewFontSize", preview_font_size)
        if mode == "solid":
            self.solid_background_chip = preview
        elif mode == "gradient":
            self.gradient_background_chip = preview
        elif mode == "default":
            self.default_background_chip = preview
            preview.setText("")
            preview.setToolTip("选择默认导出背景")
            preview.setStyleSheet(
                "QLabel { background: transparent; border: none; }"
            )
        elif mode == "custom":
            self.custom_background_chip = preview
            preview.setText("")
            preview.setToolTip("选择自定义导出背景")
            preview.setStyleSheet(
                "QLabel { background: transparent; border: none; }"
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
                button.clicked.connect(
                    lambda checked=False, selected_field=label:
                    self._handle_font_emphasis_changed(selected_field)
                )
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
        size_labels = tuple(PNG_SIZE_PRESETS)
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
                    preset = PNG_SIZE_PRESETS[size_labels[option_index]]
                    button.setToolTip(
                        f"{preset.width} × {preset.height} 像素"
                    )
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
        self.custom_width_edit.editingFinished.connect(
            self._handle_custom_size_editing_finished
        )
        self.custom_height_edit.editingFinished.connect(
            self._handle_custom_size_editing_finished
        )
        return section

    def _create_size_line_edit(self):
        edit = QLineEdit()
        edit.setFixedSize(28, 18)
        edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        edit.setPlaceholderText("__")
        edit.setMaxLength(4)
        edit.setValidator(QIntValidator(320, 8192, edit))
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
        self._persist_active_export_style()
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
            self._persist_active_export_style()
            if hasattr(self, "preview_box"):
                self._refresh_export_preview()

    def _handle_font_emphasis_changed(self, field):
        self._persist_active_export_style()
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
        export_format = self._selected_option("export_format") or "Markdown"
        selected_mode = (
            self.export_background_mode
            if export_format in {"PDF", "PNG"}
            else ""
        )

        def border_for(mode):
            return (
                "#FFFFFF"
                if selected_mode == mode
                else "rgba(120, 120, 120, 0.65)"
            )

        if hasattr(self, "solid_background_chip"):
            self.solid_background_chip.setStyleSheet(
                self._preview_chip_style(
                    f"background-color: {self.export_solid_color};",
                    8,
                    border_color=border_for("solid"),
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
                    border_color=border_for("gradient"),
                )
            )
        if hasattr(self, "default_background_chip"):
            self.default_background_chip.set_default_background_index(
                self.export_default_background_index
            )
            self.default_background_chip.set_background_selected(
                selected_mode == "default"
            )
        if hasattr(self, "custom_background_chip"):
            self.custom_background_chip.set_custom_background(
                self.export_custom_background_path,
                self.export_custom_background_crop,
            )
            self.custom_background_chip.set_background_selected(
                selected_mode == "custom"
            )
        if hasattr(self, "preview_box"):
            self._apply_preview_surface_styles()

    def _apply_preview_surface_styles(self):
        embedded_background, popup_background = self._preview_background_styles()
        self.preview_box.setStyleSheet(
            f"""
            QTextEdit {{
                {embedded_background};
                border: 10px solid rgba(255, 255, 255, 0.98);
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
        if export_format == "PDF":
            bg_rgba = _theme_preview_bg_rgba()
            return (
                f"background-color: {bg_rgba}",
                "background-color: rgba(255, 255, 255, 0.70)",
            )
        if self.export_background_mode == "gradient":
            popup = (
                "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
                f"stop:0 {self.export_gradient_start}, "
                f"stop:1 {self.export_gradient_end})"
            )
            return "background-color: #FFFFFF", popup
        if self.export_background_mode == "default":
            preset = get_export_background_preset(
                self.export_default_background_index
            )
            background = (
                "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
                f"stop:0 {preset.top_color}, stop:1 {preset.bottom_color})"
            )
            return "background-color: #FFFFFF", background
        if self.export_background_mode == "custom":
            return (
                "background-color: #FFFFFF",
                "background-color: rgba(255, 255, 255, 0.70)",
            )
        return (
            "background-color: #FFFFFF",
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

    def _preview_chip_style(
        self,
        background_style,
        font_size,
        border_radius=4,
        border_color="rgba(120, 120, 120, 0.65)",
    ):
        return f"""
            QLabel {{
                {background_style}
                border: 1px solid {border_color};
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
        changed = mode in {"solid", "gradient"}
        if mode == "solid":
            self.export_background_mode = "solid"
            selected = self._choose_export_color(
                self.export_solid_color,
                "选择导出纯色背景颜色",
            )
            if selected:
                self.export_solid_color = selected
        elif mode == "gradient":
            self.export_background_mode = "gradient"
            if area == "top":
                selected = self._choose_export_color(
                    self.export_gradient_start,
                    "选择导出背景上沿颜色",
                )
                if selected:
                    self.export_gradient_start = selected
            else:
                selected = self._choose_export_color(
                    self.export_gradient_end,
                    "选择导出背景下沿颜色",
                )
                if selected:
                    self.export_gradient_end = selected
        if changed:
            self._apply_background_preview_styles()
            self._persist_active_export_style()
            self._refresh_export_preview()

    def _background_crop_target(self):
        export_format = self._selected_option("export_format") or "Markdown"
        if export_format == "PDF":
            return 210, 297, "PDF · A4（210 × 297）"
        if export_format == "PNG":
            try:
                canvas_spec = self._current_png_canvas_spec()
            except ValueError:
                return None
            return (
                canvas_spec.width,
                canvas_spec.height,
                f"PNG · {canvas_spec.width} × {canvas_spec.height}",
            )
        return None

    def _background_crop_key(self, source_id, target=None):
        if not source_id or source_id[0] not in {"default", "custom"}:
            return None
        target = target or self._background_crop_target()
        if target is None:
            return None
        width, height, _target_text = target
        source_key = source_id[2] if source_id[0] == "default" else source_id[1]
        export_format = (
            self._selected_option("export_format")
            or self._active_style_format
        )
        return (
            export_format,
            source_id[0],
            str(source_key).casefold(),
            round(float(width) / float(height), 8),
        )

    def _default_background_source(self, preset_index):
        preset = get_export_background_preset(preset_index)
        image_path = get_export_background_image_path(preset)
        if image_path is None:
            return None
        source_id = ("default", int(preset_index), preset.image_file)
        return source_id, Path(image_path), preset.name

    def _custom_background_source(self, image_path=None):
        path_text = str(image_path or self.export_custom_background_path).strip()
        if not path_text:
            return None
        path = Path(path_text).expanduser().resolve()
        if not path.is_file():
            return None
        source_id = ("custom", str(path))
        return source_id, path, path.name

    def _current_background_source(self):
        if self.export_background_mode == "default":
            return self._default_background_source(
                self.export_default_background_index
            )
        if self.export_background_mode == "custom":
            return self._custom_background_source()
        return None

    def _background_source_from_id(self, source_id):
        if not source_id:
            return None
        if source_id[0] == "default":
            return self._default_background_source(source_id[1])
        if source_id[0] == "custom":
            return self._custom_background_source(source_id[1])
        return None

    def _restore_current_background_crop(self):
        if self.export_background_mode not in {"default", "custom"}:
            return True
        if self.export_background_mode == "default":
            preset = get_export_background_preset(
                self.export_default_background_index
            )
            if get_export_background_image_path(preset) is None:
                self.export_default_background_crop = None
                return True
        source = self._current_background_source()
        if source is None:
            return False
        source_id, _image_path, _display_name = source
        key = self._background_crop_key(source_id)
        if key is None:
            return False
        crop = self._background_crop_cache.get(key)
        if self.export_background_mode == "default":
            self.export_default_background_crop = crop
        else:
            self.export_custom_background_crop = crop
        return crop is not None

    def _show_background_crop_required(self, message=None):
        self._pdf_preview_controller.cancel()
        self._clear_pdf_document()
        export_format = self._selected_option("export_format") or "PDF"
        page_unit = "页" if export_format == "PDF" else "张"
        message = message or "请确认背景裁剪后生成真实预览"
        self._preview_plain_text = message
        self._preview_html = ""
        self.preview_box.show_pdf_loading(message, page_unit)
        if self._preview_popup is not None:
            self._preview_popup.set_pdf_loading(message, export_format)
        self._apply_preview_surface_styles()

    def _ensure_current_background_crop(self, open_popup):
        if self.export_background_mode not in {"default", "custom"}:
            return True
        if self.export_background_mode == "default":
            preset = get_export_background_preset(
                self.export_default_background_index
            )
            if get_export_background_image_path(preset) is None:
                self.export_default_background_crop = None
                return True
        source = self._current_background_source()
        if source is None:
            self._show_background_crop_required("请重新选择自定义背景图片")
            return False
        if self._restore_current_background_crop():
            return True
        self._show_background_crop_required()
        if open_popup:
            self._show_background_crop_popup_for_source(*source)
        return False

    def _show_background_crop_popup_for_source(
        self,
        source_id,
        image_path,
        display_name,
    ):
        target = self._background_crop_target()
        if target is None:
            return False
        crop_key = self._background_crop_key(source_id, target)
        if crop_key is None:
            return False
        if self._background_crop_popup is None:
            self._background_crop_popup = ExportBackgroundCropPopup(self)
            self._background_crop_popup.crop_confirmed.connect(
                self._handle_background_crop_confirmed
            )
        self._background_crop_request = (source_id, crop_key)
        width, height, target_text = target
        self._background_crop_popup.configure(
            source_id,
            image_path,
            display_name,
            width,
            height,
            target_text,
            self._background_crop_cache.get(crop_key),
        )
        if self._background_popup is not None:
            self._background_popup.close()
        self._background_crop_popup.show_near(self)
        return True

    def _show_default_background_crop_popup(self, preset_index):
        source = self._default_background_source(preset_index)
        return (
            self._show_background_crop_popup_for_source(*source)
            if source is not None
            else False
        )

    def _show_custom_background_crop_popup(self, image_path=None):
        source = self._custom_background_source(image_path)
        return (
            self._show_background_crop_popup_for_source(*source)
            if source is not None
            else False
        )

    def _show_current_background_crop_popup(self):
        source = self._current_background_source()
        return (
            self._show_background_crop_popup_for_source(*source)
            if source is not None
            else False
        )

    def _handle_background_crop_confirmed(self, source_id, crop):
        request = self._background_crop_request
        current_key = self._background_crop_key(source_id)
        if request is None or request[0] != source_id or request[1] != current_key:
            source = self._background_source_from_id(source_id)
            if source is not None:
                QTimer.singleShot(
                    0,
                    lambda selected_source=source: (
                        self._show_background_crop_popup_for_source(
                            *selected_source
                        )
                    ),
                )
            return
        normalized_crop = tuple(float(value) for value in crop)
        self._background_crop_cache[current_key] = normalized_crop
        if source_id[0] == "default":
            self.export_default_background_index = int(source_id[1])
            self.export_default_background_crop = normalized_crop
            self.export_background_mode = "default"
        else:
            self.export_custom_background_path = str(source_id[1])
            self.export_custom_background_crop = normalized_crop
            self.export_background_mode = "custom"
        self._background_crop_request = None
        self._apply_background_preview_styles()
        self._persist_active_export_style()
        self._refresh_export_preview()

    def _choose_custom_background(self):
        initial_path = self.export_custom_background_path
        initial_location = ""
        if initial_path:
            current_path = Path(initial_path)
            initial_location = str(
                current_path.parent if current_path.parent.exists() else current_path
            )
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "选择自定义导出背景",
            initial_location,
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.webp);;所有文件 (*)",
        )
        if not file_path:
            return
        image_path = Path(file_path).resolve()
        if QImage(str(image_path)).isNull():
            QMessageBox.warning(self, "背景图片无效", "无法读取所选背景图片。")
            return
        if not self._show_custom_background_crop_popup(image_path):
            QMessageBox.warning(self, "背景图片无效", "无法打开所选背景图片进行裁剪。")

    def _handle_font_color_clicked(self, field):
        selected = self._choose_export_color(
            self.export_font_colors[field],
            f"选择导出{field}字体颜色",
        )
        if not selected:
            return
        self.export_font_colors[field] = selected
        self._apply_font_color_chip_styles()
        self._persist_active_export_style()
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

    @staticmethod
    def _default_background_identifier(index):
        preset = get_export_background_preset(index)
        if preset.image_file:
            return f"file:{preset.image_file}"
        return f"name:{preset.name}"

    @staticmethod
    def _default_background_index_from_identifier(identifier):
        identifier = str(identifier or "").strip()
        if identifier.startswith("file:"):
            image_file = identifier[5:].casefold()
            for index, preset in enumerate(DEFAULT_EXPORT_BACKGROUND_PRESETS):
                if preset.image_file.casefold() == image_file:
                    return index
        elif identifier.startswith("name:"):
            preset_name = identifier[5:]
            for index, preset in enumerate(DEFAULT_EXPORT_BACKGROUND_PRESETS):
                if preset.name == preset_name:
                    return index
        return 0

    def _capture_current_format_style(self):
        size_preset = self._selected_preview_size
        if size_preset in PNG_SIZE_PRESETS:
            size_spec = PNG_SIZE_PRESETS[size_preset]
        else:
            try:
                size_spec = self._current_png_canvas_spec()
            except ValueError:
                size_preset = "9:16"
                size_spec = PNG_SIZE_PRESETS[size_preset]

        font_states = {}
        for field in ("标题", "详情", "备注"):
            language = self.font_languages[field]
            choices = dict(self.font_choices[field])
            current_family = self.font_combos[field].currentText().strip()
            if current_family:
                choices[language] = current_family
            emphasis = self.emphasis_buttons[field]
            font_states[field] = {
                "language": language,
                "choices": choices,
                "color": self.export_font_colors[field],
                "bold": emphasis["加粗"].isChecked(),
                "italic": emphasis["斜体"].isChecked(),
            }

        return {
            "background": {
                "mode": self.export_background_mode,
                "solid_color": self.export_solid_color,
                "gradient_start": self.export_gradient_start,
                "gradient_end": self.export_gradient_end,
                "default_identifier": self._default_background_identifier(
                    self.export_default_background_index
                ),
                "crop": (
                    list(self.export_default_background_crop)
                    if self.export_default_background_crop is not None
                    else None
                ),
                "custom_path": self.export_custom_background_path,
                "custom_crop": (
                    list(self.export_custom_background_crop)
                    if self.export_custom_background_crop is not None
                    else None
                ),
            },
            "fonts": font_states,
            "size": {
                "preset": size_preset or "custom",
                "width": size_spec.width,
                "height": size_spec.height,
            },
        }

    def _persist_format_style(self, export_format):
        if (
            not self._export_ui_ready
            or self._restoring_export_style
            or export_format not in {"Markdown", "PDF", "PNG"}
        ):
            return
        self._export_style_preferences["formats"][export_format] = (
            self._capture_current_format_style()
        )
        set_export_style_preferences(self._export_style_preferences)

    def _persist_active_export_style(self):
        self._persist_format_style(self._active_style_format)

    def _restore_format_style(self, export_format):
        state = self._export_style_preferences["formats"].get(export_format)
        if not isinstance(state, dict):
            return
        self._restoring_export_style = True
        try:
            background = state["background"]
            self.export_background_mode = background["mode"]
            self.export_solid_color = background["solid_color"]
            self.export_gradient_start = background["gradient_start"]
            self.export_gradient_end = background["gradient_end"]
            self.export_default_background_index = (
                self._default_background_index_from_identifier(
                    background["default_identifier"]
                )
            )
            crop = background.get("crop")
            self.export_default_background_crop = (
                tuple(float(value) for value in crop)
                if crop is not None
                else None
            )
            self.export_custom_background_path = background.get(
                "custom_path",
                "",
            )
            custom_crop = background.get("custom_crop")
            self.export_custom_background_crop = (
                tuple(float(value) for value in custom_crop)
                if custom_crop is not None
                else None
            )

            for field in ("标题", "详情", "备注"):
                font_state = state["fonts"][field]
                language = font_state["language"]
                self.font_languages[field] = language
                self.font_choices[field] = dict(font_state["choices"])
                self.export_font_colors[field] = font_state["color"]
                language_button = self.font_language_buttons[field]
                language_button.setText(language)
                language_button.setToolTip(
                    "点击切换为中文字体"
                    if language == "英"
                    else "点击切换为英文字体"
                )
                self._populate_font_combo(field)
                emphasis = self.emphasis_buttons[field]
                emphasis["加粗"].setChecked(bool(font_state["bold"]))
                emphasis["斜体"].setChecked(bool(font_state["italic"]))

            size_state = state["size"]
            size_preset = size_state["preset"]
            self._size_group.setExclusive(False)
            for label, button in self.size_buttons.items():
                button.setChecked(label == size_preset)
            self._size_group.setExclusive(True)
            for edit in (self.custom_width_edit, self.custom_height_edit):
                edit.blockSignals(True)
            if size_preset in PNG_SIZE_PRESETS:
                self._selected_preview_size = size_preset
                self.custom_width_edit.clear()
                self.custom_height_edit.clear()
            else:
                self._selected_preview_size = None
                self.custom_width_edit.setText(str(size_state["width"]))
                self.custom_height_edit.setText(str(size_state["height"]))
            for edit in (self.custom_width_edit, self.custom_height_edit):
                edit.blockSignals(False)

            if self.export_default_background_crop is not None:
                source = self._default_background_source(
                    self.export_default_background_index
                )
                crop_key = (
                    self._background_crop_key(source[0])
                    if source is not None
                    else None
                )
                if crop_key is not None:
                    self._background_crop_cache[crop_key] = (
                        self.export_default_background_crop
                    )
            if self.export_custom_background_crop is not None:
                source = self._custom_background_source(
                    self.export_custom_background_path
                )
                crop_key = (
                    self._background_crop_key(source[0])
                    if source is not None
                    else None
                )
                if crop_key is not None:
                    self._background_crop_cache[crop_key] = (
                        self.export_custom_background_crop
                    )
        finally:
            self._restoring_export_style = False

    def _select_option(self, group_key, value):
        previous_format = self._active_style_format
        if (
            group_key == "export_format"
            and self._export_ui_ready
            and previous_format != value
        ):
            self._persist_format_style(previous_format)
        for button in self.option_groups.get(group_key, []):
            button.setChecked(button.property("option_value") == value)
            button.update()
        should_refresh = True
        if group_key == "export_format":
            self._active_style_format = value
            if self._export_ui_ready and previous_format != value:
                self._restore_format_style(value)
            self._sync_size_button_state()
            if hasattr(self, "solid_background_chip"):
                self._apply_background_preview_styles()
            if value in {"PDF", "PNG"} and hasattr(self, "preview_box"):
                should_refresh = self._ensure_current_background_crop(
                    open_popup=True
                )
        if hasattr(self, "preview_box") and should_refresh:
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
            default_background_index=self.export_default_background_index,
            default_background_crop=self.export_default_background_crop,
            custom_background_path=self.export_custom_background_path,
            custom_background_crop=self.export_custom_background_crop,
            title=text_style("标题"),
            detail=text_style("详情"),
            note=text_style("备注"),
        )

    def _handle_export_requested(self):
        export_format = self._selected_option("export_format") or "Markdown"
        if (
            export_format in {"PDF", "PNG"}
            and not self._ensure_current_background_crop(open_popup=True)
        ):
            show_center_toast(
                self,
                "请先确认当前尺寸的背景裁剪",
                attr_name="_export_result_toast",
                duration_ms=1600,
            )
            return
        options = self._current_export_options()
        extension = {
            "Markdown": ".md",
            "PDF": ".pdf",
            "PNG": ".png",
        }[export_format]
        file_filter = {
            "Markdown": "Markdown 文件 (*.md)",
            "PDF": "PDF 文件 (*.pdf)",
            "PNG": "PNG 图片 (*.png)",
        }[export_format]
        canvas_spec = None
        page_count = 0
        if export_format == "PNG":
            try:
                canvas_spec = self._current_png_canvas_spec()
            except ValueError as exc:
                QMessageBox.warning(self, "PNG 尺寸无效", str(exc))
                return
            if (
                self._pdf_document is None
                or self._loaded_preview_format != "PNG"
            ):
                show_center_toast(
                    self,
                    "PNG 真实预览正在生成，请稍后再导出",
                    attr_name="_export_result_toast",
                    duration_ms=1600,
                )
                return
            page_count = self._pdf_document.pageCount()
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

        overwrite_png = False
        if export_format == "PNG":
            if page_count > 1:
                output_folder_name = SchedulePngExporter.output_folder_name(
                    target,
                    page_count,
                )
                response = QMessageBox.question(
                    self,
                    "确认 PNG 分页导出",
                    (
                        f"当前设置将生成 {page_count} 张 "
                        f"{canvas_spec.width}×{canvas_spec.height} PNG 图片。\n"
                        f"图片将保存到文件夹“{output_folder_name}”，"
                        "并按 _001、_002… 编号，是否继续？"
                    ),
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes,
                )
                if response != QMessageBox.StandardButton.Yes:
                    return
            conflicts = SchedulePngExporter.conflict_paths(target, page_count)
            if conflicts:
                display_paths = SchedulePngExporter.output_display_paths(
                    target,
                    page_count,
                )
                existing_paths = {
                    str(path.relative_to(target.parent))
                    for path in conflicts[:5]
                }
                names = "、".join(
                    path for path in display_paths if path in existing_paths
                )
                if len(conflicts) > 5:
                    names += " 等"
                response = QMessageBox.question(
                    self,
                    "覆盖 PNG 文件",
                    f"以下文件已存在：{names}\n是否覆盖？",
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if response != QMessageBox.StandardButton.Yes:
                    return
                overwrite_png = True

        try:
            if self._export_service is None:
                self._export_service = ScheduleExportService()
            if export_format == "Markdown":
                exported_path = self._export_service.write_markdown(target, options)
                exported_paths = (exported_path,)
            elif export_format == "PDF":
                exported_path = self._export_service.write_pdf(
                    target,
                    options,
                    self._current_pdf_style(),
                )
                exported_paths = (exported_path,)
            else:
                exported_paths = self._export_service.write_png_pages(
                    target,
                    options,
                    self._current_pdf_style(),
                    canvas_spec,
                    overwrite=overwrite_png,
                )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "导出失败",
                f"{export_format} 文件保存失败：\n{exc}",
            )
            return

        if export_format == "PNG" and len(exported_paths) > 1:
            success_text = (
                f"已导出 {len(exported_paths)} 张 PNG 至文件夹："
                f"{exported_paths[0].parent.name}"
            )
        else:
            success_text = f"已导出：{exported_paths[0].name}"
        show_center_toast(
            self,
            success_text,
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

    def _build_pdf_preview_payload(self, options):
        if self._export_service is None:
            self._export_service = ScheduleExportService()
        return self._export_service.build_payload(options)

    def _refresh_export_preview(self):
        if not hasattr(self, "preview_box"):
            return
        export_format = self._selected_option("export_format") or "Markdown"
        if export_format in {"PDF", "PNG"}:
            page_size = None
            page_unit = "页" if export_format == "PDF" else "张"
            if export_format == "PNG":
                try:
                    canvas_spec = self._current_png_canvas_spec()
                except ValueError as exc:
                    self._pdf_preview_controller.cancel()
                    self._clear_pdf_document()
                    preview_text = f"PNG 预览尺寸无效：{exc}"
                    self._preview_plain_text = preview_text
                    self.preview_box.show_pdf_loading(preview_text, page_unit)
                    if self._preview_popup is not None:
                        self._preview_popup.set_pdf_loading(
                            preview_text,
                            export_format,
                        )
                    return
                page_size = SchedulePngExporter.logical_page_size(canvas_spec)
            self._clear_pdf_document()
            self._preview_plain_text = f"正在生成 {export_format} 真实预览…"
            self._preview_html = ""
            self.preview_box.show_pdf_loading(
                self._preview_plain_text,
                page_unit,
            )
            if self._preview_popup is not None:
                self._preview_popup.set_pdf_loading(
                    self._preview_plain_text,
                    export_format,
                )
            self._apply_preview_surface_styles()
            self._pdf_preview_controller.schedule(
                self._current_export_options(),
                self._current_pdf_style(),
                page_size=page_size,
            )
            return

        self._pdf_preview_controller.cancel()
        self._clear_pdf_document()
        try:
            if self._export_service is None:
                self._export_service = ScheduleExportService()
            markdown = self._export_service.render_markdown(
                self._current_export_options()
            )
            preview_text = markdown
        except Exception as exc:
            preview_text = f"导出预览生成失败：{exc}"
        preview_html = self._build_preview_html(preview_text)
        self._preview_plain_text = preview_text
        self._preview_html = preview_html
        self.preview_box.show_text_preview()
        self.preview_box.setHtml(preview_html)
        if self._preview_popup is not None:
            self._preview_popup.set_preview_html(preview_html)

    def _handle_pdf_preview_ready(self, file_path):
        if self._selected_option("export_format") not in {"PDF", "PNG"}:
            self._pdf_preview_controller.discard(file_path)
            return
        document = QPdfDocument(self)
        self._pending_pdf_document = document
        self._pending_pdf_document_path = file_path
        document.statusChanged.connect(
            lambda status, current=document, path=file_path: self._handle_pdf_document_status(
                current,
                path,
                status,
            )
        )
        load_error = document.load(file_path)
        if (
            load_error != QPdfDocument.Error.None_
            and self._pending_pdf_document is document
        ):
            self._fail_pending_pdf_document(document, file_path, str(load_error))
            return
        if self._pending_pdf_document is document:
            self._handle_pdf_document_status(document, file_path, document.status())

    def _handle_pdf_document_status(self, document, file_path, status):
        if self._pending_pdf_document is not document:
            return
        if status == QPdfDocument.Status.Loading:
            return
        if status != QPdfDocument.Status.Ready:
            self._fail_pending_pdf_document(
                document,
                file_path,
                "Qt PDF 文档加载失败",
            )
            return
        export_format = self._selected_option("export_format")
        if export_format not in {"PDF", "PNG"}:
            self._fail_pending_pdf_document(document, file_path, "")
            return

        self._pending_pdf_document = None
        self._pending_pdf_document_path = ""
        self._pdf_document = document
        self._pdf_document_path = file_path
        self._loaded_preview_format = export_format
        page_count = document.pageCount()
        thumbnail = document.render(
            0,
            self._preview_thumbnail_render_size(export_format),
        )
        if thumbnail.isNull() or page_count <= 0:
            self._clear_pdf_document()
            self._handle_pdf_preview_failed(
                f"{export_format} 第一页渲染失败"
            )
            return
        page_unit = "页" if export_format == "PDF" else "张"
        self._preview_plain_text = (
            f"{export_format} 真实预览 · 共 {page_count} {page_unit}"
        )
        self.preview_box.show_pdf_preview(
            thumbnail,
            page_count,
            page_unit,
        )
        if self._preview_popup is not None:
            self._preview_popup.set_pdf_document(document, export_format)

    def _preview_thumbnail_render_size(self, export_format):
        if export_format != "PNG":
            return QSize(420, 594)
        canvas_spec = self._current_png_canvas_spec()
        ratio = canvas_spec.width / canvas_spec.height
        longest_edge = 594
        if ratio >= 1:
            return QSize(longest_edge, max(1, round(longest_edge / ratio)))
        return QSize(max(1, round(longest_edge * ratio)), longest_edge)

    def _fail_pending_pdf_document(self, document, file_path, message):
        if self._pending_pdf_document is document:
            self._pending_pdf_document = None
            self._pending_pdf_document_path = ""
        document.close()
        document.deleteLater()
        self._pdf_preview_controller.discard(file_path)
        if message:
            self._handle_pdf_preview_failed(message)

    def _handle_pdf_preview_failed(self, message):
        export_format = self._selected_option("export_format")
        if export_format not in {"PDF", "PNG"}:
            return
        page_unit = "页" if export_format == "PDF" else "张"
        preview_text = f"{export_format} 预览生成失败：{message}"
        self._preview_plain_text = preview_text
        self.preview_box.show_pdf_loading(preview_text, page_unit)
        if self._preview_popup is not None:
            self._preview_popup.set_pdf_loading(preview_text, export_format)

    def _clear_pdf_document(self):
        self._loaded_preview_format = ""
        if self._preview_popup is not None:
            self._preview_popup.clear_pdf_document()
        if self._pending_pdf_document is not None:
            pending_document = self._pending_pdf_document
            pending_path = self._pending_pdf_document_path
            self._pending_pdf_document = None
            self._pending_pdf_document_path = ""
            pending_document.close()
            pending_document.deleteLater()
            self._pdf_preview_controller.discard(pending_path)
        if self._pdf_document is not None:
            document = self._pdf_document
            file_path = self._pdf_document_path
            self._pdf_document = None
            self._pdf_document_path = ""
            document.close()
            document.deleteLater()
            self._pdf_preview_controller.discard(file_path)

    def _shutdown_pdf_preview(self):
        self._clear_pdf_document()
        self._pdf_preview_controller.shutdown()

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
            crop_ready = self._ensure_current_background_crop(open_popup=True)
            self._persist_active_export_style()
            if not crop_ready:
                return
            self._refresh_export_preview()

    def _apply_selected_preview_size(self):
        canvas_spec = PNG_SIZE_PRESETS.get(self._selected_preview_size)
        if canvas_spec is None:
            try:
                canvas_spec = self._current_png_canvas_spec()
            except ValueError:
                return
        self._apply_preview_ratio(canvas_spec.width, canvas_spec.height)

    def _apply_custom_preview_size(self):
        if self._selected_option("export_format") != "PNG":
            return
        try:
            width = int(self.custom_width_edit.text())
            height = int(self.custom_height_edit.text())
        except ValueError:
            return
        try:
            canvas_spec = PngCanvasSpec(width, height)
        except ValueError:
            return
        self._size_group.setExclusive(False)
        for button in self.size_buttons.values():
            button.setChecked(False)
        self._size_group.setExclusive(True)
        self._selected_preview_size = None
        self._apply_preview_ratio(canvas_spec.width, canvas_spec.height)
        crop_ready = self._ensure_current_background_crop(open_popup=False)
        self._persist_active_export_style()
        if not crop_ready:
            return
        self._refresh_export_preview()

    def _handle_custom_size_editing_finished(self):
        if self._selected_option("export_format") != "PNG":
            return
        try:
            self._current_png_canvas_spec()
        except ValueError:
            return
        if self._ensure_current_background_crop(open_popup=False):
            return
        if (
            self._background_crop_popup is not None
            and self._background_crop_popup.isVisible()
        ):
            return
        self._show_current_background_crop_popup()

    def _current_png_canvas_spec(self):
        if self._selected_preview_size in PNG_SIZE_PRESETS:
            return PNG_SIZE_PRESETS[self._selected_preview_size]
        try:
            width = int(self.custom_width_edit.text())
            height = int(self.custom_height_edit.text())
        except ValueError as exc:
            raise ValueError("请输入完整的 PNG 自定义宽度和高度") from exc
        return PngCanvasSpec(width, height)

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
            self._preview_popup.print_requested.connect(
                self._handle_preview_print_requested
            )
        export_format = self._selected_option("export_format") or "Markdown"
        if export_format in {"PDF", "PNG"}:
            if self._pdf_document is not None:
                self._preview_popup.set_pdf_document(
                    self._pdf_document,
                    export_format,
                )
            else:
                self._preview_popup.set_pdf_loading(text, export_format)
        else:
            self._preview_popup.set_preview_html(
                getattr(self, "_preview_html", self._build_preview_html(text))
            )
        self._apply_preview_surface_styles()
        self._preview_popup.set_preview_size(self.preview_box.size())
        self._preview_popup.show_near(self)

    def _handle_preview_print_requested(self):
        self.export_requested.emit()

    def _toggle_background_popup(self):
        if self._background_popup is None:
            self._background_popup = ExportDefaultBackgroundPopup(self)
            self._background_popup.background_selected.connect(
                self._handle_default_background_selected
            )
        self._background_popup.set_selected_index(
            self.export_default_background_index
        )
        if self._background_popup.isVisible():
            self._background_popup.close()
            return
        self._background_popup.show_near(self)

    def _handle_default_background_selected(self, index):
        preset = get_export_background_preset(index)
        if get_export_background_image_path(preset) is not None:
            self._show_default_background_crop_popup(index)
            return
        self.export_default_background_index = int(index)
        self.export_default_background_crop = None
        self.export_background_mode = "default"
        self._apply_background_preview_styles()
        self._persist_active_export_style()
        self._refresh_export_preview()

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
        self._persist_active_export_style()
        self._pdf_preview_controller.cancel()
        self._clear_pdf_document()
        if self._preview_popup is not None:
            self._preview_popup.close()
        if self._background_popup is not None:
            self._background_popup.close()
        if self._background_crop_popup is not None:
            self._background_crop_popup.close()
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
