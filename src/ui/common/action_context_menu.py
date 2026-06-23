import os

from PyQt6.QtCore import QPoint, QRect, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QCursor, QIcon
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMenu, QWidgetAction

from src.ui.utils.icon_loader import load_colored_svg_pixmap
from src.utils.styles import StyleManager


class _MenuRow(QFrame):
    ICON_COLOR = "#333333"
    TEXT_COLOR = "#333333"
    DISABLED_TEXT_COLOR = "#777777"
    HOVER_BG = "rgba(12, 192, 223, 0.1)"
    ICON_SIZE = 18
    ICON_DPR = 2.0

    def __init__(
        self,
        text,
        icon_path,
        action,
        width,
        enabled=True,
        arrow=False,
        on_enter=None,
        on_leave=None,
        on_click=None,
        parent=None,
    ):
        super().__init__(parent)
        self._action = action
        self._enabled = enabled
        self._hovered = False
        self._forced_hovered = False
        self._on_enter = on_enter
        self._on_leave = on_leave
        self._on_click = on_click

        self.setFixedSize(width, 38)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor if enabled else Qt.CursorShape.ArrowCursor)
        self._refresh_hover_style()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(12)

        icon_label = QLabel()
        icon_label.setFixedSize(self.ICON_SIZE, self.ICON_SIZE)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setScaledContents(True)
        icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        if icon_path:
            icon_label.setPixmap(self._load_menu_icon_pixmap(icon_path))
        layout.addWidget(icon_label)

        text_label = QLabel(text)
        text_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        text_color = self.TEXT_COLOR if enabled else self.DISABLED_TEXT_COLOR
        text_label.setStyleSheet(
            f"color: {text_color}; font-family: 'Microsoft YaHei UI'; "
            "font-size: 13px; background: transparent; border: none;"
        )
        layout.addWidget(text_label)
        layout.addStretch()

        if arrow:
            arrow_label = QLabel("›")
            arrow_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            arrow_label.setStyleSheet(
                "color: #0cc0df; font-family: 'Microsoft YaHei UI'; "
                "font-size: 18px; font-weight: bold; background: transparent; border: none;"
            )
            layout.addWidget(arrow_label)

    def enterEvent(self, event):
        if self._enabled:
            self.set_hovered(True)
        if self._on_enter:
            self._on_enter()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.set_hovered(False)
        if self._on_leave:
            self._on_leave()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._enabled and event.button() == Qt.MouseButton.LeftButton:
            self._action.trigger()
            if self._on_click:
                self._on_click()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def set_hovered(self, hovered):
        self._hovered = hovered
        self._refresh_hover_style()

    def set_forced_hovered(self, hovered):
        self._forced_hovered = hovered
        self._refresh_hover_style()

    def _refresh_hover_style(self):
        bg = self.HOVER_BG if (self._hovered or self._forced_hovered) else "transparent"
        self.setStyleSheet(f"background-color: {bg}; border-radius: 8px;")

    @classmethod
    def _load_menu_icon_pixmap(cls, icon_path):
        return load_colored_svg_pixmap(
            icon_path,
            cls.ICON_COLOR,
            cls.ICON_SIZE,
            cls.ICON_SIZE,
            cls.ICON_DPR,
        )


class ActionContextMenu(QMenu):
    action_requested = pyqtSignal(str)
    view_requested = pyqtSignal(str)

    MAIN_MENU_WIDTH = 160
    VIEW_MENU_WIDTH = 150

    def __init__(self, parent=None):
        super().__init__(parent)
        self.actions_by_id = {}
        self.widget_actions_by_id = {}
        self.rows_by_id = {}
        self.view_actions_by_id = {}
        self.view_action = None
        self.view_menu = QMenu("视图", self)
        self._view_hover_timer = QTimer(self)
        self._view_hover_timer.setInterval(30)
        self._view_hover_timer.timeout.connect(self._close_view_menu_if_cursor_outside)
        self._apply_menu_style(self, self.MAIN_MENU_WIDTH)
        self._apply_menu_style(self.view_menu, self.VIEW_MENU_WIDTH)
        self.aboutToHide.connect(self.view_menu.close)
        self.view_menu.aboutToHide.connect(self._clear_view_row_hover)
        self._build_menu()

    def _build_menu(self):
        self._create_main_action(
            action_id="skin",
            text="换肤",
            icon_names=("Skin.svg", "theme.svg"),
            enabled=False,
        )

        self._create_view_action("day", "日视图", ("interface-day.svg", "calendar.svg"))
        self._create_view_action("week", "周视图", ("interface-week.svg", "week_top_color.svg", "view.svg"))
        self._create_view_action("month", "月视图", ("interface-month.svg", "calendar.svg"))
        self._create_view_action("todo", "待办", ("todo.svg",))

        self.view_action = self._create_main_action(
            action_id="view",
            text="视图",
            icon_names=("view.svg",),
            enabled=True,
            arrow=True,
            on_enter=self._show_view_menu,
            on_leave=self._hide_view_menu_if_cursor_left,
            on_click=self._show_view_menu,
        )

        self._create_main_action(
            action_id="add",
            text="添加",
            icon_names=("add.svg",),
            enabled=True,
            on_enter=self._hide_view_menu,
            on_click=self.close,
        ).triggered.connect(lambda: self.action_requested.emit("add"))

        self._create_main_action(
            action_id="sort",
            text="排序",
            icon_names=("sort.svg",),
            enabled=False,
            on_enter=self._hide_view_menu,
        )

        self._create_main_action(
            action_id="filter",
            text="筛选",
            icon_names=("filter.svg",),
            enabled=False,
            on_enter=self._hide_view_menu,
        )

    def _create_main_action(
        self,
        action_id,
        text,
        icon_names,
        enabled,
        arrow=False,
        on_enter=None,
        on_leave=None,
        on_click=None,
    ):
        action = QAction(text, self)
        action.setIcon(self._load_icon(icon_names))
        action.setEnabled(enabled)
        row = _MenuRow(
            text=text,
            icon_path=self._first_existing_icon_path(icon_names),
            action=action,
            width=self.MAIN_MENU_WIDTH - 12,
            enabled=enabled,
            arrow=arrow,
            on_enter=on_enter,
            on_leave=on_leave,
            on_click=on_click,
        )
        widget_action = QWidgetAction(self)
        widget_action.setDefaultWidget(row)
        self.addAction(widget_action)
        self.actions_by_id[action_id] = action
        self.widget_actions_by_id[action_id] = widget_action
        self.rows_by_id[action_id] = row
        return action

    def _create_view_action(self, view_id, text, icon_names, enabled=True):
        action = QAction(text, self.view_menu)
        action.setIcon(self._load_icon(icon_names))
        action.setEnabled(enabled)
        if enabled:
            action.triggered.connect(lambda _checked=False, value=view_id: self._emit_view_requested(value))

        row = _MenuRow(
            text=text,
            icon_path=self._first_existing_icon_path(icon_names),
            action=action,
            width=self.VIEW_MENU_WIDTH - 12,
            enabled=enabled,
            on_enter=lambda: None,
            on_leave=self._hide_view_menu_if_cursor_left,
            on_click=lambda: (self.view_menu.close(), self.close()),
        )
        widget_action = QWidgetAction(self.view_menu)
        widget_action.setDefaultWidget(row)
        self.view_menu.addAction(widget_action)
        self.view_actions_by_id[view_id] = action
        return action

    def _emit_view_requested(self, view_id):
        self.view_requested.emit(view_id)

    def _show_view_menu(self):
        view_widget_action = self.widget_actions_by_id.get("view")
        if not view_widget_action:
            return
        view_row = self.rows_by_id.get("view")
        if view_row:
            view_row.set_forced_hovered(True)
        action_rect = self.actionGeometry(view_widget_action)
        popup_pos = self.mapToGlobal(QPoint(self.width(), action_rect.top()))
        self.view_menu.popup(popup_pos)
        if not self._view_hover_timer.isActive():
            self._view_hover_timer.start()

    def _hide_view_menu(self):
        self._view_hover_timer.stop()
        self._clear_view_row_hover()
        self.view_menu.close()

    def _clear_view_row_hover(self):
        view_row = self.rows_by_id.get("view")
        if view_row:
            view_row.set_hovered(False)
            view_row.set_forced_hovered(False)

    def _hide_view_menu_if_cursor_left(self):
        QTimer.singleShot(0, self._close_view_menu_if_cursor_outside)

    def _close_view_menu_if_cursor_outside(self):
        if not self.view_menu.isVisible():
            self._view_hover_timer.stop()
            self._clear_view_row_hover()
            return
        cursor_pos = QCursor.pos()
        view_row = self.rows_by_id.get("view")
        view_row_rect = QRect()
        if view_row:
            view_row_rect = QRect(view_row.mapToGlobal(QPoint(0, 0)), view_row.size())
        view_rect = QRect(self.view_menu.mapToGlobal(QPoint(0, 0)), self.view_menu.size())
        if not view_row_rect.contains(cursor_pos) and not view_rect.contains(cursor_pos):
            self._hide_view_menu()

    @staticmethod
    def _load_icon(icon_names):
        path = ActionContextMenu._first_existing_icon_path(icon_names)
        if path:
            return QIcon(_MenuRow._load_menu_icon_pixmap(path))
        return QIcon()

    @staticmethod
    def _first_existing_icon_path(icon_names):
        for name in icon_names:
            path = os.path.join("assets", "icons", name)
            if os.path.exists(path):
                return path
        return None

    @staticmethod
    def _apply_menu_style(menu, width):
        menu.setFixedWidth(width)
        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        menu.setWindowFlags(
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        menu.setStyleSheet(StyleManager.get_menu_style())

    def get_action(self, action_id):
        return self.actions_by_id.get(action_id)

    def get_view_action(self, view_id):
        return self.view_actions_by_id.get(view_id)
