import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMenu

from src.utils.styles import StyleManager


class ActionContextMenu(QMenu):
    action_requested = pyqtSignal(str)
    view_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.actions_by_id = {}
        self.view_actions_by_id = {}
        self._apply_menu_style(self)
        self._build_menu()

    def _build_menu(self):
        skin_action = self._create_main_action(
            action_id="skin",
            text="换肤",
            icon_names=("Skin.svg", "theme.svg"),
            enabled=False,
        )
        self.actions_by_id["skin"] = skin_action

        self.view_menu = QMenu("视图", self)
        self._apply_menu_style(self.view_menu)
        self._create_view_action("day", "日视图", ("Calendar.svg",))
        self._create_view_action("week", "周视图", ("week_top_color.svg", "view.svg"))
        self._create_view_action("month", "月视图", ("Calendar.svg",))
        self._create_view_action("priority", "四象限视图", ("importance.svg",), enabled=False)
        self._create_view_action("todo", "待办", ("todo.svg",))

        view_action = self._create_main_action(
            action_id="view",
            text="视图",
            icon_names=("view.svg",),
            enabled=True,
        )
        view_action.setMenu(self.view_menu)
        self.actions_by_id["view"] = view_action

        add_action = self._create_main_action(
            action_id="add",
            text="添加",
            icon_names=("add.svg",),
            enabled=True,
        )
        add_action.triggered.connect(lambda: self.action_requested.emit("add"))
        self.actions_by_id["add"] = add_action

        sort_action = self._create_main_action(
            action_id="sort",
            text="排序",
            icon_names=("sort.svg",),
            enabled=False,
        )
        self.actions_by_id["sort"] = sort_action

        filter_action = self._create_main_action(
            action_id="filter",
            text="筛选",
            icon_names=("filter.svg",),
            enabled=False,
        )
        self.actions_by_id["filter"] = filter_action

    def _create_main_action(self, action_id, text, icon_names, enabled):
        action = QAction(self._load_icon(icon_names), text, self)
        action.setEnabled(enabled)
        self.addAction(action)
        return action

    def _create_view_action(self, view_id, text, icon_names, enabled=True):
        action = QAction(self._load_icon(icon_names), text, self.view_menu)
        action.setEnabled(enabled)
        if enabled:
            action.triggered.connect(lambda _checked=False, value=view_id: self.view_requested.emit(value))
        self.view_menu.addAction(action)
        self.view_actions_by_id[view_id] = action
        return action

    @staticmethod
    def _load_icon(icon_names):
        for name in icon_names:
            path = os.path.join("assets", "icons", name)
            if os.path.exists(path):
                return QIcon(path)
        return QIcon()

    @staticmethod
    def _apply_menu_style(menu):
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
