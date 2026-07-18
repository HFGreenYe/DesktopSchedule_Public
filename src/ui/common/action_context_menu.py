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
    ICON_SIZE = 18
    ICON_DPR = 2.0

    @staticmethod
    def hover_bg():
        return StyleManager.theme_overlay_rgba(0.10)

    @staticmethod
    def active_bg():
        return StyleManager.theme_overlay_rgba(0.16)

    @staticmethod
    def accent_color():
        return StyleManager.theme_accent_color()

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
                f"color: {self.accent_color()}; font-family: 'Microsoft YaHei UI'; "
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
        bg = self.hover_bg() if (self._hovered or self._forced_hovered) else "transparent"
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
    mode_requested = pyqtSignal(str)
    drag_snap_requested = pyqtSignal(int)

    MAIN_MENU_WIDTH = 160
    VIEW_MENU_WIDTH = 150

    def __init__(
        self,
        parent=None,
        show_drag_options=False,
        drag_snap_minutes=1,
        show_day_collapse=False,
        day_collapsed=False,
    ):
        super().__init__(parent)
        self.show_drag_options = show_drag_options
        self.drag_snap_minutes = self._normalize_drag_snap_minutes(drag_snap_minutes)
        self.show_day_collapse = bool(show_day_collapse)
        self.day_collapsed = bool(day_collapsed)
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

        # --- 模式 子菜单 ---
        self.mode_menu = QMenu("模式", self)
        self._mode_hover_timer = QTimer(self)
        self._mode_hover_timer.setInterval(30)
        self._mode_hover_timer.timeout.connect(
            self._close_mode_menu_if_cursor_outside
        )
        self._mode_rows = {}
        self._mode_widget_actions = {}
        self._mode_row = None
        self._mode_widget_action = None
        self._apply_menu_style(self.mode_menu, self.VIEW_MENU_WIDTH)
        self.aboutToHide.connect(self.mode_menu.close)
        self.mode_menu.aboutToHide.connect(self._clear_mode_row_hover)

        # --- 拖拉 子菜单（仅日课表模式使用） ---
        self.drag_menu = QMenu("拖拉", self)
        self._drag_hover_timer = QTimer(self)
        self._drag_hover_timer.setInterval(30)
        self._drag_hover_timer.timeout.connect(
            self._close_drag_menu_if_cursor_outside
        )
        self._drag_rows = {}
        self._drag_widget_actions = {}
        self._apply_menu_style(self.drag_menu, self.VIEW_MENU_WIDTH)
        self.aboutToHide.connect(self.drag_menu.close)
        self.drag_menu.aboutToHide.connect(self._clear_drag_row_hover)

        self._build_menu()

    @staticmethod
    def _normalize_drag_snap_minutes(value):
        try:
            minutes = int(value)
        except (TypeError, ValueError):
            return 1
        return minutes if minutes in {1, 5} else 1

    def _build_menu(self):
        # --- 模式（仿"视图"子菜单结构） ---
        self._create_mode_action("card", "卡片模式", ("schedule_card.svg",))
        self._create_mode_action(
            "timetable",
            "课表模式",
            ("timetable.svg",),
            icon_inset=1,
        )

        self._create_main_action(
            action_id="mode",
            text="模式",
            icon_names=("model_switch.svg",),
            enabled=True,
            arrow=True,
            on_enter=self._show_mode_menu,
            on_leave=self._hide_mode_menu_if_cursor_left,
            on_click=self._show_mode_menu,
        )

        if self.show_drag_options:
            self._create_drag_action(1, "1分钟刻度", ("1.svg",))
            self._create_drag_action(5, "5分钟刻度", ("5.svg",))
            self._create_main_action(
                action_id="drag",
                text="拖拉",
                icon_names=("drag.svg",),
                enabled=True,
                arrow=True,
                on_enter=self._show_drag_menu,
                on_leave=self._hide_drag_menu_if_cursor_left,
                on_click=self._show_drag_menu,
            )

        self._create_main_action(
            action_id="skin",
            text="换肤",
            icon_names=("Skin.svg", "theme.svg"),
            enabled=False,
        )

        if self.show_day_collapse:
            collapse_text = "放下" if self.day_collapsed else "收起"
            collapse_icon = "setdown.svg" if self.day_collapsed else "setup.svg"
            self._create_main_action(
                action_id="day_collapse",
                text=collapse_text,
                icon_names=(collapse_icon,),
                enabled=True,
                on_enter=self._hide_secondary_menus,
                on_click=self.close,
            ).triggered.connect(
                lambda: self.action_requested.emit("toggle_day_collapse")
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

    def _hide_secondary_menus(self):
        self._hide_mode_menu()
        self._hide_drag_menu()
        self._hide_view_menu()

    @staticmethod
    def _global_widget_rect(widget):
        return QRect(widget.mapToGlobal(QPoint(0, 0)), widget.size())

    @classmethod
    def _cursor_inside_submenu_path(cls, cursor_pos, row, submenu):
        if row is None or not submenu.isVisible():
            return False

        row_rect = cls._global_widget_rect(row)
        submenu_rect = cls._global_widget_rect(submenu)
        if row_rect.contains(cursor_pos) or submenu_rect.contains(cursor_pos):
            return True

        if row_rect.right() < submenu_rect.left():
            bridge_left = row_rect.right() + 1
            bridge_right = submenu_rect.left() - 1
        elif submenu_rect.right() < row_rect.left():
            bridge_left = submenu_rect.right() + 1
            bridge_right = row_rect.left() - 1
        else:
            return False

        bridge_rect = QRect(
            QPoint(bridge_left, min(row_rect.top(), submenu_rect.top())),
            QPoint(bridge_right, max(row_rect.bottom(), submenu_rect.bottom())),
        )
        return bridge_rect.contains(cursor_pos)

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

    # ── 模式子菜单（镜像视图） ──────────────────────────

    def _create_mode_action(self, mode_id, text, icon_names, icon_inset=0):
        action = QAction(text, self.mode_menu)
        if icon_names:
            path = self._first_existing_icon_path(icon_names)
            if path:
                pixmap = _MenuRow._load_menu_icon_pixmap(path)
                if icon_inset and not pixmap.isNull():
                    pixmap = pixmap.scaled(
                        pixmap.width() - icon_inset * 2,
                        pixmap.height() - icon_inset * 2,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                action.setIcon(QIcon(pixmap))
        action.setEnabled(True)
        action.triggered.connect(
            lambda _checked=False, mid=mode_id: self._emit_mode_requested(mid)
        )

        row = _MenuRow(
            text=text,
            icon_path=(
                self._first_existing_icon_path(icon_names) if icon_names else None
            ),
            action=action,
            width=self.VIEW_MENU_WIDTH - 12,
            enabled=True,
            on_click=lambda: (
                self.mode_menu.close(),
                self.close(),
            ),
        )
        widget_action = QWidgetAction(self.mode_menu)
        widget_action.setDefaultWidget(row)
        self.mode_menu.addAction(widget_action)
        self._mode_rows[mode_id] = row
        self._mode_widget_actions[mode_id] = widget_action
        return action

    def _emit_mode_requested(self, mode_id):
        self.mode_requested.emit(mode_id)

    # ── 拖拉子菜单 ──────────────────────────

    def _create_drag_action(self, snap_minutes, text, icon_names):
        snap_minutes = self._normalize_drag_snap_minutes(snap_minutes)
        action = QAction(text, self.drag_menu)
        action.setIcon(self._load_icon(icon_names))
        action.setEnabled(True)
        action.triggered.connect(
            lambda _checked=False, minutes=snap_minutes: self._emit_drag_snap_requested(minutes)
        )

        row = _MenuRow(
            text=text,
            icon_path=self._first_existing_icon_path(icon_names),
            action=action,
            width=self.VIEW_MENU_WIDTH - 12,
            enabled=True,
            on_enter=lambda minutes=snap_minutes: self._set_drag_option_style(
                minutes,
                hovered=True,
            ),
            on_leave=lambda minutes=snap_minutes: self._set_drag_option_style(
                minutes,
                hovered=False,
            ),
            on_click=lambda: (
                self.drag_menu.close(),
                self.close(),
            ),
        )
        widget_action = QWidgetAction(self.drag_menu)
        widget_action.setDefaultWidget(row)
        self.drag_menu.addAction(widget_action)
        self._drag_rows[snap_minutes] = row
        self._drag_widget_actions[snap_minutes] = widget_action
        self._set_drag_option_style(snap_minutes, hovered=False)
        return action

    def _emit_drag_snap_requested(self, minutes):
        self.drag_snap_requested.emit(self._normalize_drag_snap_minutes(minutes))

    def _set_drag_option_style(self, minutes, hovered=False):
        row = self._drag_rows.get(self._normalize_drag_snap_minutes(minutes))
        if not row:
            return
        is_current = self.drag_snap_minutes == self._normalize_drag_snap_minutes(minutes)
        if is_current:
            row.setStyleSheet(
                f"background-color: {_MenuRow.active_bg()}; border-radius: 8px;"
            )
        elif hovered:
            row.setStyleSheet(
                f"background-color: {_MenuRow.hover_bg()}; border-radius: 8px;"
            )
        else:
            row.setStyleSheet("background-color: transparent; border-radius: 8px;")

    def _show_drag_menu(self):
        wa = self.widget_actions_by_id.get("drag")
        if not wa:
            return
        self.mode_menu.close()
        self.view_menu.close()
        row = self.rows_by_id.get("drag")
        if row:
            row.set_forced_hovered(True)
        action_rect = self.actionGeometry(wa)
        popup_pos = self.mapToGlobal(QPoint(self.width(), action_rect.top()))
        self.drag_menu.popup(popup_pos)
        if not self._drag_hover_timer.isActive():
            self._drag_hover_timer.start()

    def _hide_drag_menu(self):
        self._drag_hover_timer.stop()
        self._clear_drag_row_hover()
        self.drag_menu.close()

    def _clear_drag_row_hover(self):
        row = self.rows_by_id.get("drag")
        if row:
            row.set_hovered(False)
            row.set_forced_hovered(False)

    def _hide_drag_menu_if_cursor_left(self):
        QTimer.singleShot(0, self._close_drag_menu_if_cursor_outside)

    def _close_drag_menu_if_cursor_outside(self):
        if not self.drag_menu.isVisible():
            self._drag_hover_timer.stop()
            self._clear_drag_row_hover()
            return
        cursor_pos = QCursor.pos()
        drag_row = self.rows_by_id.get("drag")
        if not self._cursor_inside_submenu_path(
            cursor_pos,
            drag_row,
            self.drag_menu,
        ):
            self._hide_drag_menu()

    def _show_mode_menu(self):
        wa = self.widget_actions_by_id.get("mode")
        if not wa:
            return
        self.drag_menu.close()
        self.view_menu.close()
        row = self.rows_by_id.get("mode")
        if row:
            row.set_forced_hovered(True)
        action_rect = self.actionGeometry(wa)
        popup_pos = self.mapToGlobal(QPoint(self.width(), action_rect.top()))
        self.mode_menu.popup(popup_pos)
        if not self._mode_hover_timer.isActive():
            self._mode_hover_timer.start()

    def _hide_mode_menu(self):
        self._mode_hover_timer.stop()
        self._clear_mode_row_hover()
        self.mode_menu.close()

    def _clear_mode_row_hover(self):
        row = self.rows_by_id.get("mode")
        if row:
            row.set_hovered(False)
            row.set_forced_hovered(False)

    def _hide_mode_menu_if_cursor_left(self):
        QTimer.singleShot(0, self._close_mode_menu_if_cursor_outside)

    def _close_mode_menu_if_cursor_outside(self):
        if not self.mode_menu.isVisible():
            self._mode_hover_timer.stop()
            self._clear_mode_row_hover()
            return
        cursor_pos = QCursor.pos()
        mode_row = self.rows_by_id.get("mode")
        if not self._cursor_inside_submenu_path(
            cursor_pos,
            mode_row,
            self.mode_menu,
        ):
            self._hide_mode_menu()

    def _show_view_menu(self):
        view_widget_action = self.widget_actions_by_id.get("view")
        if not view_widget_action:
            return
        self.mode_menu.close()
        self.drag_menu.close()
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
        if not self._cursor_inside_submenu_path(
            cursor_pos,
            view_row,
            self.view_menu,
        ):
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
