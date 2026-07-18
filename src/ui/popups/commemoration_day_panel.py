import unicodedata
from datetime import date

from PyQt6.QtCore import QEvent, QPoint, QRectF, QSize, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QGuiApplication,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ...config import AppConfig
from ...utils.commemoration_preferences import (
    create_commemoration_item,
    load_commemoration_dates,
    save_commemoration_dates,
)
from ...utils.window_preferences import set_window_pin_state
from ...utils.styles import StyleManager
from ..utils.icon_loader import load_colored_svg_pixmap


class _MiniSwitch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._checked = False
        self.setFixedSize(36, 20)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def isChecked(self):
        return self._checked

    def setChecked(self, checked):
        checked = bool(checked)
        if checked == self._checked:
            return
        self._checked = checked
        self.update()
        self.toggled.emit(self._checked)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self._checked)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        track_color = (
            QColor(AppConfig.COLOR_GRADIENT_START)
            if self._checked
            else QColor("#c8cdd1")
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(QRectF(self.rect()), 10, 10)
        thumb_x = 18 if self._checked else 2
        painter.setBrush(QColor("white"))
        painter.drawEllipse(QRectF(thumb_x, 2, 16, 16))


class _ReminderDayButton(QPushButton):
    def __init__(self, text, days, parent=None):
        super().__init__(parent)
        self.option_text = text
        self.setProperty("reminder_days", days)
        self.setCheckable(True)
        self.setFixedSize(37 if text == "当天" else 31, 22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("background: transparent; border: none;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        font = painter.font()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(8)
        painter.setFont(font)
        painter.setPen(QColor("#455a64"))
        painter.drawText(
            QRectF(0, 0, self.width() - 10, self.height()),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            self.option_text,
        )

        circle_rect = QRectF(self.width() - 9, 7, 8, 8)
        painter.setPen(QPen(QColor("#8a9297"), 1))
        painter.setBrush(
            QColor(AppConfig.COLOR_GRADIENT_START)
            if self.isChecked()
            else Qt.BrushStyle.NoBrush
        )
        painter.drawEllipse(circle_rect)


class CommemorationDayPanel(QWidget):
    HEADER_HEIGHT = 54
    BODY_OVERLAY_ALPHA = 179
    CORNER_RADIUS = 12
    PIN_ICON_SIZE = 14
    NAME_WIDTH_UNITS_LIMIT = 36
    ADD_PANEL_BASE_HEIGHT = 166

    def __init__(self, parent=None, initial_pinned=True, settings=None):
        window_flags = Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
        if initial_pinned:
            window_flags |= Qt.WindowType.WindowStaysOnTopHint
        super().__init__(parent, window_flags)

        self.is_pinned = bool(initial_pinned)
        self._settings = settings
        self._items = load_commemoration_dates(self._settings)
        self._drag_offset = None
        self._calendar_popup = None
        self._selected_date = date.today()

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(312, 470)
        self._setup_ui()
        self._render_items()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.header = QWidget()
        self.header.setFixedHeight(self.HEADER_HEIGHT)
        self.header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(16, 7, 7, 5)
        header_layout.setSpacing(2)

        title_label = QLabel("纪念日期")
        title_label.setStyleSheet(
            "color: white; background: transparent; border: none; "
            "font-family: 'Microsoft YaHei UI'; font-size: 16px; font-weight: bold;"
        )
        header_layout.addWidget(title_label, 1)

        button_style = """
            QPushButton {
                background: transparent;
                border: none;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.18);
                border-radius: 15px;
            }
            QPushButton:checked {
                background: rgba(255, 255, 255, 0.18);
                border-radius: 15px;
            }
        """

        self.btn_add_toggle = QPushButton()
        self.btn_add_toggle.setFixedSize(30, 30)
        self.btn_add_toggle.setIconSize(QSize(16, 16))
        self.btn_add_toggle.setCheckable(True)
        self.btn_add_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_toggle.setToolTip("添加纪念日")
        self.btn_add_toggle.setStyleSheet(button_style)
        add_pixmap = load_colored_svg_pixmap(
            "assets/icons/add.svg",
            QColor(255, 255, 255),
            16,
            16,
            self.devicePixelRatioF(),
        )
        self.btn_add_toggle.setIcon(QIcon(add_pixmap))
        self.btn_add_toggle.toggled.connect(self._toggle_add_panel)
        header_layout.addWidget(self.btn_add_toggle)

        self.btn_pin = QPushButton()
        self.btn_pin.setFixedSize(30, 30)
        self.btn_pin.setIconSize(QSize(self.PIN_ICON_SIZE, self.PIN_ICON_SIZE))
        self.btn_pin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pin.setStyleSheet(button_style)
        self.btn_pin.clicked.connect(self._toggle_pin)
        header_layout.addWidget(self.btn_pin)

        self.btn_close = QPushButton()
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setIcon(QIcon("assets/icons/close.png"))
        self.btn_close.setIconSize(QSize(12, 12))
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setToolTip("关闭")
        self.btn_close.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                color: white;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.18);
                border-radius: 15px;
            }
            """
        )
        self.btn_close.clicked.connect(self.close)
        header_layout.addWidget(self.btn_close)
        root_layout.addWidget(self.header)

        self.add_panel_holder = QWidget()
        self.add_panel_holder.setFixedHeight(self.ADD_PANEL_BASE_HEIGHT)
        self.add_panel_holder.setStyleSheet("background: transparent;")
        add_holder_layout = QVBoxLayout(self.add_panel_holder)
        add_holder_layout.setContentsMargins(12, 0, 12, 0)
        add_holder_layout.setSpacing(0)

        self.add_form_container = QWidget()
        self.add_form_container.setStyleSheet(
            "background: transparent; border: none;"
        )
        add_form_layout = QVBoxLayout(self.add_form_container)
        add_form_layout.setContentsMargins(0, 5, 0, 7)
        add_form_layout.setSpacing(10)

        add_title_layout = QHBoxLayout()
        add_title_layout.setContentsMargins(0, 0, 0, 0)
        add_title_layout.setSpacing(6)
        add_title = QLabel("添加纪念日")
        add_title.setStyleSheet(
            f"color: {AppConfig.COLOR_GRADIENT_START}; background: transparent; "
            "border: none; font-family: 'Microsoft YaHei UI'; "
            "font-size: 13px; font-weight: bold;"
        )
        add_title_layout.addWidget(add_title)
        add_title_layout.addStretch()

        self.btn_calendar = QPushButton()
        self.btn_calendar.setFixedSize(26, 26)
        self.btn_calendar.setIconSize(QSize(15, 15))
        self.btn_calendar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_calendar.setToolTip("选择日期")
        self.btn_calendar.setStyleSheet(
            f"QPushButton {{ background: {AppConfig.COLOR_GRADIENT_START}; "
            "border: none; border-radius: 13px; } "
            f"QPushButton:hover {{ background: {AppConfig.COLOR_GRADIENT_END}; }}"
        )
        calendar_pixmap = load_colored_svg_pixmap(
            "assets/icons/commemoryday_cal.svg",
            QColor("white"),
            15,
            15,
            self.devicePixelRatioF(),
        )
        self.selected_date_label = QLabel(self._selected_date.isoformat())
        self.selected_date_label.setFixedSize(96, 26)
        self.selected_date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_date_label.setStyleSheet(
            "color: #455a64; background: transparent; border: none; "
            "font-family: 'Microsoft YaHei UI'; font-size: 11px;"
        )
        add_title_layout.addWidget(self.selected_date_label)

        self.btn_calendar.setIcon(QIcon(calendar_pixmap))
        self.btn_calendar.clicked.connect(self._show_calendar)
        add_title_layout.addWidget(self.btn_calendar)
        add_form_layout.addLayout(add_title_layout)

        input_style = f"""
            QLineEdit {{
                color: #263238;
                background: rgba(255, 255, 255, 0.72);
                border: 1px solid {AppConfig.COLOR_GRADIENT_END};
                border-radius: 6px;
                padding: 0 8px;
                font-family: 'Microsoft YaHei UI';
                font-size: 12px;
                selection-background-color: {AppConfig.COLOR_GRADIENT_START};
            }}
            QLineEdit:focus {{
                border: 1px solid {AppConfig.COLOR_GRADIENT_START};
                background: rgba(255, 255, 255, 0.88);
            }}
        """

        self.name_edit = QLineEdit()
        self.name_edit.setFixedHeight(34)
        self.name_edit.setMaxLength(self.NAME_WIDTH_UNITS_LIMIT)
        self.name_edit.setPlaceholderText("纪念日名称（18个中文 / 36个英文）")
        self.name_edit.setStyleSheet(input_style)
        self.name_edit.textChanged.connect(self._enforce_name_limit)
        self.name_edit.returnPressed.connect(self._add_item)
        add_form_layout.addWidget(self.name_edit)

        self.reminder_row = QWidget()
        self.reminder_row.setFixedHeight(22)
        self.reminder_row.setStyleSheet("background: transparent; border: none;")
        reminder_layout = QHBoxLayout(self.reminder_row)
        reminder_layout.setContentsMargins(0, 0, 0, 0)
        reminder_layout.setSpacing(7)

        reminder_label = QLabel("启用提醒")
        reminder_label.setStyleSheet(
            "color: #455a64; background: transparent; border: none; "
            "font-family: 'Microsoft YaHei UI'; font-size: 11px;"
        )
        reminder_layout.addWidget(reminder_label)

        self.reminder_switch = _MiniSwitch()
        self.reminder_switch.toggled.connect(self._on_reminder_toggled)
        reminder_layout.addWidget(self.reminder_switch)

        self.reminder_options_container = QWidget()
        self.reminder_options_container.setStyleSheet(
            "background: transparent; border: none;"
        )
        reminder_options_layout = QHBoxLayout(self.reminder_options_container)
        reminder_options_layout.setContentsMargins(0, 0, 0, 0)
        reminder_options_layout.setSpacing(0)

        self.reminder_days_group = QButtonGroup(self)
        self.reminder_days_group.setExclusive(True)
        for option_text, days in (
            ("7天", 7),
            ("5天", 5),
            ("3天", 3),
            ("1天", 1),
            ("当天", 0),
        ):
            option_button = _ReminderDayButton(option_text, days)
            if days == 0:
                option_button.setChecked(True)
            self.reminder_days_group.addButton(option_button)
            reminder_options_layout.addWidget(option_button)
        reminder_layout.addStretch()
        reminder_layout.addWidget(self.reminder_options_container)
        add_form_layout.addWidget(self.reminder_row)
        self.reminder_options_container.hide()

        add_action_layout = QHBoxLayout()
        add_action_layout.setContentsMargins(0, 0, 0, 0)
        add_action_layout.setSpacing(7)
        self.message_label = QLabel()
        self.message_label.setStyleSheet(
            "color: #c62828; background: transparent; border: none; "
            "font-family: 'Microsoft YaHei UI'; font-size: 9px;"
        )
        add_action_layout.addWidget(self.message_label)
        add_action_layout.addStretch()

        self.btn_add = QPushButton("添加")
        self.btn_add.setFixedSize(58, 30)
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet(
            f"""
            QPushButton {{
                color: white;
                background: {AppConfig.COLOR_GRADIENT_START};
                border: none;
                border-radius: 6px;
                font-family: 'Microsoft YaHei UI';
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {AppConfig.COLOR_GRADIENT_END};
            }}
            QPushButton:pressed {{
                padding-top: 1px;
            }}
            """
        )
        self.btn_add.clicked.connect(self._add_item)
        add_action_layout.addWidget(self.btn_add)
        add_form_layout.addLayout(add_action_layout)

        add_holder_layout.addWidget(self.add_form_container, 1)
        self.add_separator = QFrame()
        self.add_separator.setFixedHeight(1)
        self.add_separator.setStyleSheet(
            "background: rgba(255, 255, 255, 0.95); border: none;"
        )
        add_holder_layout.addWidget(self.add_separator)
        root_layout.addWidget(self.add_panel_holder)
        self.add_panel_holder.hide()

        self.body = QWidget()
        self.body.setStyleSheet("background: transparent;")
        body_layout = QVBoxLayout(self.body)
        body_layout.setContentsMargins(14, 12, 14, 14)
        body_layout.setSpacing(9)

        list_header_layout = QHBoxLayout()
        list_header_layout.setContentsMargins(0, 1, 0, 0)
        list_header_layout.setSpacing(6)
        list_title = QLabel("我的纪念日")
        list_title.setStyleSheet(
            f"color: {AppConfig.COLOR_GRADIENT_START}; background: transparent; "
            "border: none; font-family: 'Microsoft YaHei UI'; "
            "font-size: 13px; font-weight: bold;"
        )
        list_title.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )
        list_header_layout.addWidget(list_title)
        list_header_layout.addStretch()
        self.count_label = QLabel()
        self.count_label.setStyleSheet(
            "color: #607d8b; background: transparent; border: none; "
            "font-family: 'Microsoft YaHei UI'; font-size: 10px;"
        )
        self.count_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )
        list_header_layout.addWidget(self.count_label)
        body_layout.addLayout(list_header_layout)

        self.list_scroll = QScrollArea()
        self.list_scroll.setWidgetResizable(True)
        self.list_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.list_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.list_scroll.setStyleSheet(
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
                background: rgba(0, 102, 204, 0.35);
                border-radius: 2px;
                min-height: 18px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
            """
        )
        self.list_scroll.viewport().setStyleSheet("background: transparent;")

        self.list_container = QWidget()
        self.list_container.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(7)
        self.list_scroll.setWidget(self.list_container)
        body_layout.addWidget(self.list_scroll, 1)
        root_layout.addWidget(self.body, 1)

        self._drag_surfaces = {
            self.body,
            self.list_scroll.viewport(),
            self.list_container,
        }
        for surface in self._drag_surfaces:
            surface.installEventFilter(self)
            surface.setContextMenuPolicy(
                Qt.ContextMenuPolicy.CustomContextMenu
            )
            surface.customContextMenuRequested.connect(
                lambda position, source=surface: self._show_blank_context_menu(
                    source,
                    position,
                )
            )

        self._update_pin_button()

    def _show_blank_context_menu(self, source, position):
        if self._surface_hits_card(source, position):
            return
        from ..common.action_context_menu import ActionContextMenu

        menu = ActionContextMenu(
            self,
            show_multiple_choice=True,
            multiple_choice_only=True,
        )
        menu.exec(source.mapToGlobal(position))

    def _surface_hits_card(self, source, position):
        global_position = source.mapToGlobal(position)
        list_position = self.list_container.mapFromGlobal(global_position)
        current = self.list_container.childAt(list_position)
        while current is not None and current is not self.list_container:
            if current.property("commemoration_id"):
                return True
            current = current.parentWidget()
        return False

    def _toggle_add_panel(self, expanded):
        self.add_panel_holder.setVisible(bool(expanded))
        if expanded:
            self.name_edit.setFocus()

    def _show_calendar(self):
        if self._calendar_popup is None:
            from ..calendar_pop import CalendarPop

            self._calendar_popup = CalendarPop(
                self,
                export_theme=True,
                schedule_markers=False,
            )
            self._calendar_popup.date_selected.connect(
                self._apply_calendar_date
            )
            self._calendar_popup.calendar.currentPageChanged.connect(
                self._refresh_calendar_markers
            )

        anchor = self.btn_calendar.mapToGlobal(
            QPoint(self.btn_calendar.width() // 2, self.btn_calendar.height())
        )
        self._calendar_popup.show_at(anchor, self._selected_date)
        self._refresh_calendar_markers(
            self._calendar_popup.calendar.yearShown(),
            self._calendar_popup.calendar.monthShown(),
        )
        screen = (
            QGuiApplication.screenAt(anchor)
            or QGuiApplication.primaryScreen()
        )
        if screen is None:
            return
        available = screen.availableGeometry()
        position = self._calendar_popup.pos()
        position.setX(
            max(
                available.left(),
                min(
                    position.x(),
                    available.right() - self._calendar_popup.width() + 1,
                ),
            )
        )
        position.setY(
            max(
                available.top(),
                min(
                    position.y(),
                    available.bottom() - self._calendar_popup.height() + 1,
                ),
            )
        )
        self._calendar_popup.move(position)
        self._calendar_popup.raise_()

    def _refresh_calendar_markers(self, visible_year=None, visible_month=None):
        if self._calendar_popup is None:
            return
        marker_status = {}
        today = date.today()
        target_year = int(visible_year or self._selected_date.year)
        for item in self._items:
            source_date = date.fromisoformat(item["date"])
            marker_date = (
                self._annual_date(source_date, target_year)
                if item["annual"]
                else source_date
            )
            marker_status[marker_date] = (
                "grey" if marker_date < today else "commemoration"
            )
        self._calendar_popup.calendar.set_date_markers(marker_status)

    def _apply_calendar_date(self, selected_date):
        self._selected_date = selected_date
        self.selected_date_label.setText(selected_date.isoformat())

    def _enforce_name_limit(self, text):
        used_units = 0
        accepted_characters = []
        for character in text:
            character_units = (
                2
                if unicodedata.east_asian_width(character) in {"W", "F"}
                else 1
            )
            if used_units + character_units > self.NAME_WIDTH_UNITS_LIMIT:
                break
            accepted_characters.append(character)
            used_units += character_units

        accepted_text = "".join(accepted_characters)
        if accepted_text == text:
            return
        self.name_edit.blockSignals(True)
        self.name_edit.setText(accepted_text)
        self.name_edit.setCursorPosition(len(accepted_text))
        self.name_edit.blockSignals(False)
        self._show_message("名称已达上限", error=True)

    def _on_reminder_toggled(self, enabled):
        self.reminder_options_container.setVisible(bool(enabled))

    def _selected_reminder_days(self):
        checked_button = self.reminder_days_group.checkedButton()
        if checked_button is None:
            return 0
        return int(checked_button.property("reminder_days"))

    def _add_item(self):
        item = create_commemoration_item(
            self.name_edit.text(),
            self._selected_date,
            annual=False,
            reminder_enabled=self.reminder_switch.isChecked(),
            reminder_days=self._selected_reminder_days(),
        )
        if item is None:
            self._show_message("请输入纪念日名称", error=True)
            self.name_edit.setFocus()
            return

        self._items.append(item)
        self._save_items()
        self.name_edit.clear()
        self._show_message("已添加", error=False)
        self._render_items()

    def _delete_item(self, item_id):
        self._items = [item for item in self._items if item["id"] != item_id]
        self._save_items()
        self._render_items()

    def _save_items(self):
        self._items = save_commemoration_dates(self._items, self._settings)

    def _show_message(self, text, error=False):
        color = "#c62828" if error else AppConfig.COLOR_GRADIENT_START
        self.message_label.setStyleSheet(
            f"color: {color}; background: transparent; border: none; "
            "font-family: 'Microsoft YaHei UI'; font-size: 10px;"
        )
        self.message_label.setText(text)
        QTimer.singleShot(1800, self.message_label.clear)

    def _render_items(self):
        while self.list_layout.count():
            layout_item = self.list_layout.takeAt(0)
            widget = layout_item.widget()
            if widget is not None:
                widget.deleteLater()

        sorted_items = sorted(self._items, key=self._item_sort_key)
        self.count_label.setText(f"共 {len(sorted_items)} 个")
        if not sorted_items:
            empty_label = QLabel("还没有纪念日\n从上方添加一个吧")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet(
                "color: #78909c; background: transparent; border: none; "
                "font-family: 'Microsoft YaHei UI'; font-size: 12px; padding: 30px 8px;"
            )
            empty_label.setAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents,
                True,
            )
            self.list_layout.addStretch()
            self.list_layout.addWidget(empty_label)
            self.list_layout.addStretch()
            return

        for item in sorted_items:
            self.list_layout.addWidget(self._create_item_card(item))
        self.list_layout.addStretch()

    def _create_item_card(self, item):
        card = QFrame()
        card.setObjectName("commemorationCard")
        card.setFixedHeight(68)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setProperty("commemoration_id", item["id"])

        days = self._days_from_today(item)
        is_today = days == 0
        is_expired = days < 0
        card.setProperty("is_today", is_today)
        card.setProperty("is_expired", is_expired)

        midpoint_color = StyleManager.mix_colors(
            AppConfig.COLOR_GRADIENT_START,
            AppConfig.COLOR_GRADIENT_END,
            0.5,
        )
        background_color = "#ffffff" if is_expired else midpoint_color
        if is_expired:
            border_style = "1px solid rgba(80, 90, 95, 0.25)"
        else:
            border_style = "1px solid rgba(255, 255, 255, 0.70)"
        card.setStyleSheet(
            f"""
            QFrame#commemorationCard {{
                background: {background_color};
                border: {border_style};
                border-radius: 8px;
            }}
            """
        )
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(12, 7, 12, 7)
        card_layout.setSpacing(0)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(3)

        primary_text_color = (
            "#FFD700"
            if is_today
            else "#455a64" if is_expired else "white"
        )
        secondary_text_color = "#78909c" if is_expired else "rgba(255, 255, 255, 0.82)"

        name_label = QLabel(item["name"])
        name_label.setStyleSheet(
            f"color: {primary_text_color}; background: transparent; border: none; "
            "font-family: 'Microsoft YaHei UI'; font-size: 13px; font-weight: bold;"
        )
        text_layout.addWidget(name_label)

        details_layout = QHBoxLayout()
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(8)
        target_date = date.fromisoformat(item["date"])
        if item["annual"]:
            date_text = f"每年 · {target_date.month:02d}月{target_date.day:02d}日"
        else:
            date_text = target_date.strftime("%Y年%m月%d日")

        date_label = QLabel(date_text)
        date_label.setStyleSheet(
            f"color: {secondary_text_color}; background: transparent; border: none; "
            "font-family: 'Microsoft YaHei UI'; font-size: 10px;"
        )
        details_layout.addWidget(date_label)
        details_layout.addStretch()

        if item["reminder_enabled"]:
            reminder_days = item["reminder_days"]
            reminder_text = (
                "当天提醒"
                if reminder_days == 0
                else f"提前{reminder_days}天提醒"
            )
        else:
            reminder_text = "不提醒"
        reminder_label = QLabel(reminder_text)
        reminder_label.setStyleSheet(
            f"color: {secondary_text_color}; background: transparent; border: none; "
            "font-family: 'Microsoft YaHei UI'; font-size: 10px;"
        )
        details_layout.addWidget(reminder_label)
        text_layout.addLayout(details_layout)
        card_layout.addLayout(text_layout, 1)

        card.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        card.customContextMenuRequested.connect(
            lambda position, card_item=item, card_widget=card: self._show_item_context_menu(
                card_item,
                card_widget,
                position,
            )
        )
        return card

    def _show_item_context_menu(self, item, card, position):
        menu = QMenu(card)
        menu.setStyleSheet(StyleManager.get_menu_style())
        delete_pixmap = load_colored_svg_pixmap(
            "assets/icons/delete.svg",
            QColor("#333333"),
            14,
            14,
            self.devicePixelRatioF(),
        )
        delete_action = QAction(
            QIcon(delete_pixmap),
            "删除纪念日便签",
            menu,
        )
        delete_action.triggered.connect(
            lambda checked=False, item_id=item["id"]: self._delete_item(item_id)
        )
        menu.addAction(delete_action)
        menu.exec(card.mapToGlobal(position))

    def _item_sort_key(self, item):
        days = self._days_from_today(item)
        if days >= 0:
            return 0, days, item["name"]
        return 1, abs(days), item["name"]

    def _days_from_today(self, item):
        today = date.today()
        source_date = date.fromisoformat(item["date"])
        target_date = source_date
        if item["annual"]:
            target_date = self._annual_date(source_date, today.year)
            if target_date < today:
                target_date = self._annual_date(source_date, today.year + 1)
        return (target_date - today).days

    @staticmethod
    def _annual_date(source_date, year):
        try:
            return date(year, source_date.month, source_date.day)
        except ValueError:
            return date(year, 2, 28)

    def _toggle_pin(self):
        self.set_pinned(not self.is_pinned)

    def set_pinned(self, enabled):
        self.is_pinned = bool(enabled)
        position = self.pos()
        set_window_pin_state(self, self.is_pinned)
        self.move(position)
        self._update_pin_button()

    def _update_pin_button(self):
        pin_color = (
            QColor(255, 255, 255, 255)
            if self.is_pinned
            else QColor(255, 255, 255, 150)
        )
        pin_pixmap = load_colored_svg_pixmap(
            "assets/icons/pin.svg",
            pin_color,
            self.PIN_ICON_SIZE,
            self.PIN_ICON_SIZE,
            self.devicePixelRatioF(),
        )
        self.btn_pin.setIcon(QIcon(pin_pixmap))
        self.btn_pin.setToolTip(
            "取消窗口置顶" if self.is_pinned else "窗口置顶"
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, self.CORNER_RADIUS, self.CORNER_RADIUS)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        painter.fillPath(path, QBrush(gradient))

        painter.save()
        painter.setClipPath(path)
        painter.fillRect(
            QRectF(
                0,
                self.HEADER_HEIGHT,
                self.width(),
                self.height() - self.HEADER_HEIGHT,
            ),
            QColor(255, 255, 255, self.BODY_OVERLAY_ALPHA),
        )
        painter.restore()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255, 110), 1))
        painter.drawPath(path)
        super().paintEvent(event)

    def eventFilter(self, watched, event):
        if watched in getattr(self, "_drag_surfaces", set()):
            if (
                event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
            ):
                position = event.position().toPoint()
                if self._surface_hits_card(watched, position):
                    return False
                self._drag_offset = (
                    event.globalPosition().toPoint()
                    - self.frameGeometry().topLeft()
                )
                event.accept()
                return True
            if (
                event.type() == QEvent.Type.MouseMove
                and self._drag_offset is not None
                and event.buttons() & Qt.MouseButton.LeftButton
            ):
                self.move(
                    event.globalPosition().toPoint() - self._drag_offset
                )
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

    def mousePressEvent(self, event):
        if (
            event.button() == Qt.MouseButton.LeftButton
            and event.position().y() <= self.HEADER_HEIGHT
        ):
            self._drag_offset = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            event.buttons() & Qt.MouseButton.LeftButton
            and self._drag_offset is not None
        ):
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_offset = None
        super().mouseReleaseEvent(event)

    def hideEvent(self, event):
        if self._calendar_popup is not None:
            self._calendar_popup.close()
        super().hideEvent(event)


def show_commemoration_day_panel(parent_window, toggle=False):
    panel = getattr(parent_window, "commemoration_day_panel", None)
    if panel is None:
        initial_pinned = bool(
            parent_window.windowFlags()
            & Qt.WindowType.WindowStaysOnTopHint
        )
        panel = CommemorationDayPanel(
            parent_window,
            initial_pinned=initial_pinned,
        )
        parent_window.commemoration_day_panel = panel

        anchor_geometry = parent_window.frameGeometry()
        x = anchor_geometry.right() + 10
        y = anchor_geometry.top()
        screen = (
            QGuiApplication.screenAt(anchor_geometry.center())
            or QGuiApplication.primaryScreen()
        )
        if screen is not None:
            available = screen.availableGeometry()
            if x + panel.width() > available.right() + 1:
                x = anchor_geometry.left() - panel.width() - 10
            x = max(
                available.left(),
                min(x, available.right() - panel.width() + 1),
            )
            y = max(
                available.top(),
                min(y, available.bottom() - panel.height() + 1),
            )
        panel.move(x, y)

    if toggle and panel.isVisible():
        panel.hide()
        return panel

    panel.btn_add_toggle.setChecked(False)
    panel.show()
    panel.raise_()
    panel.activateWindow()
    return panel
