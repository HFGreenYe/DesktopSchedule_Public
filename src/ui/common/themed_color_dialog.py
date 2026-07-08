from PyQt6.QtCore import QEvent, QPoint, QRect, QRectF, QSize, Qt, QTimer
from PyQt6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPalette, QPen
from PyQt6.QtWidgets import (
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpinBox,
)

from src.utils.color_preferences import (
    get_color_dialog_custom_colors,
    set_color_dialog_custom_colors,
)


class _ColorDialogHeader(QLabel):
    def __init__(self, title, accent, parent=None):
        super().__init__(parent)
        self._drag_offset = None
        self.setFixedHeight(32)
        self.setObjectName("ColorDialogHeader")
        self.setStyleSheet(
            "QLabel#ColorDialogHeader { "
            "background: transparent; border: none; }"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 0, 0)
        layout.setSpacing(6)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(
            "color: white; font-size: 13px; font-weight: bold; "
            "background: transparent; border: none;"
        )
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.close_button = QPushButton()
        self.close_button.setFixedSize(30, 30)
        self.close_button.setIconSize(QSize(12, 12))
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setToolTip("关闭")
        self.close_button.setStyleSheet(
            "QPushButton { color: white; background: transparent; border: none; "
            "border-top-right-radius: 12px; } "
            "QPushButton:hover { background-color: #ff4d4f; }"
        )
        close_icon = QIcon("assets/icons/close.png")
        if not close_icon.isNull():
            self.close_button.setIcon(close_icon)
        else:
            self.close_button.setText("×")
        self.close_button.clicked.connect(parent.reject)
        layout.addWidget(self.close_button)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.window().toggle_content_theme()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.window().pos()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self._drag_offset is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.window().move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_offset = None
        super().mouseReleaseEvent(event)


class ThemedColorDialog(QColorDialog):
    CORNER_RADIUS = 12
    RIGHT_PANEL_WIDTH = 340
    _custom_colors_loaded = False

    _TEXT_TRANSLATIONS = {
        "Basic colors": "基本颜色",
        "Pick Screen Color": "拾取屏幕颜色",
        "Custom colors": "自定义颜色",
        "Add to Custom Colors": "添加到自定义颜色",
        "Hue:": "色相：",
        "Sat:": "饱和度：",
        "Val:": "明度：",
        "Red:": "R：",
        "Green:": "G：",
        "Blue:": "B：",
        "Alpha channel:": "透明度：",
        "HTML:": "HTML：",
        "OK": "确定",
        "Cancel": "取消",
    }

    def __init__(self, initial_color, title, accent, parent=None):
        ThemedColorDialog._restore_custom_colors()
        super().__init__(initial_color, parent)
        accent_color = QColor(accent)
        if not accent_color.isValid():
            accent_color = QColor("#0cc0df")
        self._accent = accent_color
        self._dark_content = False
        self._spin_buttons = []
        self._hue_picker = None
        self._luminance_picker = None
        self._left_layout = None
        self._basic_colors_label = None
        self._basic_colors_widget = None
        self._screen_pick_button = None
        self._custom_colors_label = None
        self._custom_colors_widget = None
        self._add_custom_color_button = None
        self._hue_label = None
        self._alignment_widgets_detached = False
        self._alignment_rects = {}
        self._values_widget = None
        self._html_line_edit = None
        self._button_box = None
        self._content_background = QColor("#ffffff")

        self.setObjectName("themedColorDialog")
        self.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(False)
        self.setWindowTitle(title)

        self._translate_qt_controls()
        self._compact_qt_layout()
        self._install_spin_controls()
        self._apply_content_theme()

        self._header = _ColorDialogHeader(title, self._accent.name(), self)
        dialog_layout = self.layout()
        dialog_layout.setContentsMargins(0, 0, 0, 8)
        dialog_layout.setSpacing(4)
        dialog_layout.insertWidget(0, self._header)
        self.adjustSize()
        self.setFixedSize(self.sizeHint())
        self._position_spin_buttons()
        self._update_window_mask()

    @classmethod
    def _restore_custom_colors(cls):
        if cls._custom_colors_loaded:
            return

        for index, color_name in enumerate(get_color_dialog_custom_colors()):
            if index >= QColorDialog.customCount():
                break
            color = QColor(color_name)
            if color.isValid():
                QColorDialog.setCustomColor(index, color)
        cls._custom_colors_loaded = True

    @staticmethod
    def _save_custom_colors():
        color_names = [
            QColorDialog.customColor(index).name(QColor.NameFormat.HexArgb)
            for index in range(QColorDialog.customCount())
        ]
        set_color_dialog_custom_colors(color_names)

    @staticmethod
    def _normalized_text(text):
        return str(text).replace("&", "").strip()

    def _translate_qt_controls(self):
        for label in self.findChildren(QLabel):
            normalized = self._normalized_text(label.text())
            translated = self._TEXT_TRANSLATIONS.get(normalized)
            if translated is not None:
                label.setText(translated)

        for button in self.findChildren(QPushButton):
            normalized = self._normalized_text(button.text())
            translated = self._TEXT_TRANSLATIONS.get(normalized)
            if translated is not None:
                button.setText(translated)

    def _compact_qt_layout(self):
        root_layout = self.layout()
        body_layout = root_layout.itemAt(0).layout()
        if body_layout is None or body_layout.count() < 2:
            return

        body_layout.setContentsMargins(10, 4, 10, 0)
        body_layout.setSpacing(8)
        left_layout = body_layout.itemAt(0).layout()
        right_layout = body_layout.itemAt(1).layout()
        if left_layout is not None:
            self._left_layout = left_layout
            left_layout.setSpacing(0)
            basic_colors_label = left_layout.itemAt(0)
            if basic_colors_label is not None and basic_colors_label.widget() is not None:
                label = basic_colors_label.widget()
                label.setFixedHeight(label.fontMetrics().height())
                self._basic_colors_label = label
            basic_colors_item = left_layout.itemAt(1)
            if basic_colors_item is not None:
                self._basic_colors_widget = basic_colors_item.widget()
            screen_pick_item = left_layout.itemAt(2)
            if screen_pick_item is not None:
                self._screen_pick_button = screen_pick_item.widget()
                if self._screen_pick_button is not None:
                    self._screen_pick_button.setObjectName("ColorDialogActionButton")
            custom_colors_item = left_layout.itemAt(5)
            if custom_colors_item is not None:
                self._custom_colors_label = custom_colors_item.widget()
            custom_palette_item = left_layout.itemAt(6)
            if custom_palette_item is not None:
                self._custom_colors_widget = custom_palette_item.widget()
            add_custom_color_item = left_layout.itemAt(7)
            if add_custom_color_item is not None:
                self._add_custom_color_button = add_custom_color_item.widget()
                if self._add_custom_color_button is not None:
                    self._add_custom_color_button.setObjectName("ColorDialogActionButton")
            for index in (2, 7):
                item = left_layout.itemAt(index)
                if item is not None and item.widget() is not None:
                    item.widget().setFixedHeight(20)
            screen_pick_status = left_layout.itemAt(3)
            if screen_pick_status is not None and screen_pick_status.widget() is not None:
                # Qt writes live cursor coordinates here while screen picking.
                # The compressed dialog does not have a stable row for it, so keep
                # the picker behavior but hide this optional status text.
                screen_pick_status.widget().hide()
                screen_pick_status.widget().setFixedHeight(0)
            for index in (4, 8):
                item = left_layout.itemAt(index)
                if item is not None and item.spacerItem() is not None:
                    item.spacerItem().changeSize(
                        0,
                        0,
                        QSizePolicy.Policy.Minimum,
                        QSizePolicy.Policy.Minimum,
                    )

        if right_layout is None:
            return
        right_layout.setSpacing(4)
        top_layout = right_layout.itemAt(0).layout()
        if top_layout is not None and top_layout.count() >= 3:
            picker_layout = top_layout.itemAt(0).layout()
            if picker_layout is not None and picker_layout.count() >= 2:
                self._hue_picker = picker_layout.itemAt(1).widget()
                if self._hue_picker is not None:
                    self._hue_picker.setFixedSize(260, 190)
            self._luminance_picker = top_layout.itemAt(2).widget()
            if self._luminance_picker is not None:
                self._luminance_picker.setFixedSize(18, 195)
            top_layout.setSpacing(4)

        self._values_widget = right_layout.itemAt(2).widget()
        if self._values_widget is None:
            return
        values_layout = self._values_widget.layout()
        if values_layout is not None:
            values_layout.setContentsMargins(0, 0, 0, 0)
            values_layout.setHorizontalSpacing(6)
            values_layout.setVerticalSpacing(3)
            values_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self._values_widget.setFixedWidth(self.RIGHT_PANEL_WIDTH)
        self._values_widget.setMinimumHeight(150)

        for label in self._values_widget.findChildren(QLabel):
            if self._normalized_text(label.text()) == "色相：":
                self._hue_label = label
                break

        for spin in self._values_widget.findChildren(
            QSpinBox,
            options=Qt.FindChildOption.FindDirectChildrenOnly,
        ):
            spin.setFixedWidth(66)
            spin.setMinimumHeight(22)
        for line_edit in self._values_widget.findChildren(
            QLineEdit,
            options=Qt.FindChildOption.FindDirectChildrenOnly,
        ):
            self._html_line_edit = line_edit
            line_edit.setMinimumHeight(22)
            line_edit.setMinimumWidth(72)

        self._button_box = self.findChild(QDialogButtonBox)
        if self._button_box is not None:
            root_layout.removeWidget(self._button_box)
            self._button_box.setParent(self._values_widget)
            self._button_box.setFixedSize(128, 24)
            for button in self._button_box.buttons():
                button.setObjectName("ColorDialogActionButton")
                button.setFixedHeight(22)
            self._button_box.show()

    def _install_spin_controls(self):
        for spin in self.findChildren(QSpinBox):
            spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
            spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
            spin.installEventFilter(self)

            up_button = QPushButton("▴", spin)
            down_button = QPushButton("▾", spin)
            for button in (up_button, down_button):
                button.setCursor(Qt.CursorShape.PointingHandCursor)
                button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                button.setFixedSize(14, 11)
            up_button.clicked.connect(spin.stepUp)
            down_button.clicked.connect(spin.stepDown)
            self._spin_buttons.append((spin, up_button, down_button))

    def _position_spin_buttons(self):
        for spin, up_button, down_button in self._spin_buttons:
            button_x = max(spin.width() - 14, 0)
            up_button.move(button_x, 0)
            down_button.move(button_x, max(spin.height() - 11, 0))
            up_button.raise_()
            down_button.raise_()

    def _align_right_edges(self):
        if not self._spin_buttons:
            return

        self.layout().activate()
        target_right = max(
            spin.mapTo(self, QPoint(spin.width(), 0)).x()
            for spin, _up_button, _down_button in self._spin_buttons
        )

        if self._html_line_edit is not None:
            spin_positions = [
                (
                    spin.mapTo(self, QPoint(0, 0)).x(),
                    spin.mapTo(self, QPoint(spin.width(), 0)).x(),
                )
                for spin, _up_button, _down_button in self._spin_buttons
            ]
            left_column_x = min(left for left, _right in spin_positions)
            left_column_right = max(
                right
                for left, right in spin_positions
                if abs(left - left_column_x) <= 4
            )
            html_left = self._html_line_edit.mapTo(self, QPoint(0, 0)).x()
            self._html_line_edit.setFixedWidth(
                max(72, left_column_right - html_left)
            )
            self.layout().activate()

        if self._hue_picker is not None and self._luminance_picker is not None:
            luminance_right = self._luminance_picker.mapTo(
                self,
                QPoint(self._luminance_picker.width(), 0),
            ).x()
            width_delta = target_right - luminance_right
            if abs(width_delta) > 1:
                self._hue_picker.setFixedWidth(
                    max(190, self._hue_picker.width() + width_delta)
                )
                self.layout().activate()

        if (
            self._button_box is not None
            and self._values_widget is not None
            and self._html_line_edit is not None
        ):
            values_origin = self._values_widget.mapTo(self, QPoint(0, 0))
            html_origin = self._html_line_edit.mapTo(self, QPoint(0, 0))
            button_x = target_right - values_origin.x() - self._button_box.width()
            button_y = (
                html_origin.y()
                - values_origin.y()
                + (self._html_line_edit.height() - self._button_box.height()) // 2
            )
            self._button_box.move(max(0, button_x), max(0, button_y))
            self._button_box.raise_()

    def _detach_alignment_widgets(self):
        if self._alignment_widgets_detached or self._left_layout is None:
            return

        widgets = tuple(
            widget
            for widget in (
                self._basic_colors_label,
                self._basic_colors_widget,
                self._screen_pick_button,
                self._custom_colors_label,
                self._add_custom_color_button,
            )
            if widget is not None
        )
        if len(widgets) != 5:
            return

        self.layout().activate()
        self._alignment_rects = {
            widget: QRect(widget.mapTo(self, QPoint(0, 0)), widget.size())
            for widget in widgets
        }

        indexed_widgets = sorted(
            (
                (self._left_layout.indexOf(widget), widget)
                for widget in widgets
            ),
            reverse=True,
        )
        for index, widget in indexed_widgets:
            if index < 0:
                continue
            self._left_layout.takeAt(index)
            self._left_layout.insertSpacing(
                index,
                max(widget.height(), widget.sizeHint().height(), 1),
            )
            widget.raise_()

        self._alignment_widgets_detached = True
        self._left_layout.activate()

    def _move_widget_in_dialog(self, widget, x, y):
        parent = widget.parentWidget()
        if parent is None:
            return
        widget.move(parent.mapFrom(self, QPoint(round(x), round(y))))
        widget.raise_()

    def _align_control_rows(self):
        if (
            self._basic_colors_label is None
            or self._basic_colors_widget is None
            or self._screen_pick_button is None
            or self._hue_picker is None
            or self._custom_colors_label is None
            or self._hue_label is None
            or self._add_custom_color_button is None
            or self._button_box is None
        ):
            return

        self._detach_alignment_widgets()
        if not self._alignment_widgets_detached:
            return

        basic_label_rect = self._alignment_rects[self._basic_colors_label]
        basic_palette_rect = self._alignment_rects[self._basic_colors_widget]
        screen_pick_rect = self._alignment_rects[self._screen_pick_button]
        custom_label_rect = self._alignment_rects[self._custom_colors_label]
        add_button_rect = self._alignment_rects[self._add_custom_color_button]

        hue_picker_rect = QRect(
            self._hue_picker.mapTo(self, QPoint(0, 0)),
            self._hue_picker.size(),
        )
        hue_label_rect = QRect(
            self._hue_label.mapTo(self, QPoint(0, 0)),
            self._hue_label.size(),
        )
        button_box_rect = QRect(
            self._button_box.mapTo(self, QPoint(0, 0)),
            self._button_box.size(),
        )

        palette_shift = hue_picker_rect.bottom() - screen_pick_rect.bottom()
        self._move_widget_in_dialog(
            self._basic_colors_label,
            basic_label_rect.x(),
            hue_picker_rect.y(),
        )
        self._move_widget_in_dialog(
            self._basic_colors_widget,
            basic_palette_rect.x(),
            basic_palette_rect.y() + palette_shift,
        )
        self._move_widget_in_dialog(
            self._screen_pick_button,
            screen_pick_rect.x(),
            screen_pick_rect.y() + palette_shift,
        )
        self._custom_colors_label.setFixedHeight(hue_label_rect.height())
        self._move_widget_in_dialog(
            self._custom_colors_label,
            custom_label_rect.x(),
            hue_label_rect.y(),
        )
        self._move_widget_in_dialog(
            self._add_custom_color_button,
            add_button_rect.x(),
            button_box_rect.bottom() - add_button_rect.height() + 1,
        )

    def _schedule_control_alignment(self):
        QTimer.singleShot(0, self._align_control_rows)

    def _apply_content_theme(self):
        dark = self._dark_content
        background = "#242424" if dark else "#ffffff"
        secondary = "#303030" if dark else "#f5f5f5"
        text = "#ffffff" if dark else "#333333"
        border = "#555555" if dark else "#cfcfcf"
        arrow = "#ffffff" if dark else self._accent.name()
        self._content_background = QColor(background)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(background))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(text))
        palette.setColor(QPalette.ColorRole.Base, QColor(background))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(secondary))
        palette.setColor(QPalette.ColorRole.Text, QColor(text))
        palette.setColor(QPalette.ColorRole.Button, QColor(secondary))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(text))
        palette.setColor(QPalette.ColorRole.Highlight, self._accent)
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        self.setPalette(palette)
        self.setStyleSheet(
            "QColorDialog#themedColorDialog { "
            f"background: transparent; color: {text}; }}"
            "QColorDialog#themedColorDialog QLabel { "
            f"color: {text}; background: transparent; }}"
            "QColorDialog#themedColorDialog QLineEdit { "
            f"background-color: {background}; color: {text}; "
            f"border: 1px solid {border}; border-radius: 3px; "
            f"padding: 2px 4px; selection-background-color: {self._accent.name()}; }}"
            "QColorDialog#themedColorDialog QSpinBox { "
            f"background: transparent; color: {arrow}; border: none; padding-right: 14px; }}"
            "QColorDialog#themedColorDialog QSpinBox QLineEdit { "
            f"background: transparent; color: {arrow}; border: none; padding: 0px 14px 0px 0px; }}"
            "QColorDialog#themedColorDialog QPushButton#ColorDialogActionButton { "
            f"background-color: {secondary}; color: {text}; "
            f"border: 1px solid {border}; border-radius: 4px; padding: 3px 10px; }}"
            "QColorDialog#themedColorDialog QPushButton#ColorDialogActionButton:hover { "
            f"background-color: {'#3a3a3a' if dark else '#e9e9e9'}; }}"
        )
        for widget in (
            self._basic_colors_widget,
            self._custom_colors_widget,
            self._hue_picker,
            self._luminance_picker,
        ):
            if widget is not None:
                widget.setStyleSheet("border: none; background: transparent;")
        for _spin, up_button, down_button in self._spin_buttons:
            arrow_style = (
                "QPushButton { background: transparent; border: none; padding: 0px; "
                f"color: {arrow}; font-size: 8px; }}"
                "QPushButton:hover { background: transparent; }"
            )
            up_button.setStyleSheet(arrow_style)
            down_button.setStyleSheet(arrow_style)
        self._position_spin_buttons()

    def toggle_content_theme(self):
        self._dark_content = not self._dark_content
        self._apply_content_theme()

    def eventFilter(self, watched, event):
        if isinstance(watched, QSpinBox) and event.type() == QEvent.Type.Resize:
            self._position_spin_buttons()
        return super().eventFilter(watched, event)

    def _update_window_mask(self):
        # Rounded corners are painted with antialiasing instead of an integer
        # QRegion mask. This matches the main windows and avoids white pixels at
        # the corners under Windows fractional DPI scaling.
        self.clearMask()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, self.CORNER_RADIUS, self.CORNER_RADIUS)
        painter.fillPath(path, self._content_background)

        header_height = self._header.height() if hasattr(self, "_header") else 32
        painter.save()
        painter.setClipPath(path)
        painter.fillRect(QRectF(0, 0, self.width(), header_height), self._accent)
        painter.restore()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(0, 0, 0, 26), 1))
        painter.drawPath(path)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_spin_buttons()
        self._align_right_edges()
        self._schedule_control_alignment()

    def showEvent(self, event):
        super().showEvent(event)
        self._position_spin_buttons()
        self._align_right_edges()
        self._schedule_control_alignment()

    def done(self, result):
        self._save_custom_colors()
        super().done(result)

    @classmethod
    def get_color(cls, initial_color, title, accent, parent=None):
        dialog = cls(initial_color, title, accent, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.currentColor()
        return QColor()
