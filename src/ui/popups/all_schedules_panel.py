import os

from PyQt6.QtCore import QEvent, QPointF, QPropertyAnimation, QRectF, QSize, Qt, pyqtProperty
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QIcon,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.config import AppConfig
from src.ui.popups.day_query_options_panel import DayQueryOptionsPanel
from src.utils.window_preferences import set_window_pin_state


class _DotOptionButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(22)
        font = self.font()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(7)
        self.setFont(font)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("background: transparent; border: none;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        font = painter.font()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(7)
        font.setBold(self.isChecked())
        painter.setFont(font)

        text_color = QColor(255, 255, 255, 255 if self.isChecked() else 220)
        painter.setPen(text_color)
        radius = 3.0
        dot_gap = 3.0
        edge_padding = 1.0
        text_width = painter.fontMetrics().horizontalAdvance(self.text())
        text_left = edge_padding
        text_rect = QRectF(text_left, 0, text_width, self.height())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.text())

        dot_x = min(
            text_rect.right() + dot_gap,
            self.width() - radius * 2.0 - edge_padding,
        )
        dot_rect = QRectF(
            dot_x,
            self.height() / 2.0 - radius,
            radius * 2.0,
            radius * 2.0,
        )
        painter.setPen(QPen(QColor(255, 255, 255, 230), 1))
        selected_color = QColor(255, 255, 255, 191)
        painter.setBrush(QBrush(selected_color) if self.isChecked() else Qt.BrushStyle.NoBrush)
        painter.drawEllipse(dot_rect)
        painter.end()


class AllSchedulesPanel(QWidget):
    RESIZE_MARGIN = 14
    OPTION_TITLE_WIDTH = 52
    OPTION_ROW_SPACING = 2
    OPTION_GRID_COLUMNS = 5

    def __init__(self, parent_window=None):
        super().__init__(
            parent_window,
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint,
        )
        self.parent_window = parent_window
        self._drag_offset = None
        self._resize_edge = None
        self._resize_start_pos = None
        self._resize_start_geometry = None
        self.is_pinned = False
        self._settings_visible = False
        self._search_options_visible = False
        self._settings_icon_angle = 0.0
        self._settings_icon_source = QPixmap()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self._setup_ui()
        self.reset_geometry_for_parent()

    def reset_geometry_for_parent(self):
        parent = self.parent_window
        if parent is None:
            self.setFixedWidth(260)
            self.setMinimumHeight(384)
            self.resize(260, 384)
            return

        parent_rect = parent.frameGeometry()
        width = max(260, int(parent_rect.width() * 0.75))
        height = max(260, int(parent_rect.height() * 2 / 3))
        self.setFixedWidth(width)
        self.setMinimumHeight(height)
        self.resize(width, height)
        self.move(
            parent_rect.left() + (parent_rect.width() - width) // 2,
            parent_rect.top() + (parent_rect.height() - height) // 2,
        )

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QVBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(2)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(3)

        self.title_label = QLabel("日程查看")
        self.title_label.setMinimumWidth(76)
        self.title_label.setFixedHeight(26)
        self.title_label.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei'; "
            "font-size: 16px; font-weight: bold; background: transparent; border: none;"
        )

        self.search_box = QLineEdit()
        self.search_box.setObjectName("allSchedulesSearchBox")
        self.search_box.setPlaceholderText("搜索日程...")
        self.search_box.setFixedHeight(24)
        self.search_box.setMinimumWidth(96)
        self.search_box.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.search_action = self.search_box.addAction(
            self._load_padded_svg_icon(
                "search.svg",
                "#FFFFFF",
                icon_size=12,
                canvas_size=16,
            ),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        self.search_box.setStyleSheet(
            """
            QLineEdit#allSchedulesSearchBox {
                background-color: rgba(255, 255, 255, 0.20);
                border: 2px solid #FFFFFF;
                border-radius: 6px;
                color: white;
                padding-left: 0px;
                padding-right: 4px;
                font-family: "Microsoft YaHei UI";
                font-size: 11px;
            }
            QLineEdit#allSchedulesSearchBox:hover,
            QLineEdit#allSchedulesSearchBox:focus {
                background-color: rgba(255, 255, 255, 0.24);
                border: 2px solid #FFFFFF;
            }
            QLineEdit#allSchedulesSearchBox::placeholder {
                color: rgba(255, 255, 255, 0.75);
            }
            """
        )

        button_style = (
            "QPushButton { background: transparent; border: none; border-radius: 4px; } "
            "QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }"
        )
        self.btn_settings = QPushButton()
        self.btn_settings.setFixedSize(30, 24)
        self.btn_settings.setIconSize(QSize(24, 24))
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.setToolTip("显示设置")
        self.btn_settings.setStyleSheet(button_style)
        self.btn_settings.clicked.connect(self._toggle_settings_area)
        self._settings_rotation_animation = QPropertyAnimation(
            self,
            b"settingsIconAngle",
            self,
        )
        self._settings_rotation_animation.setDuration(180)

        self.btn_pin = QPushButton(self)
        self.btn_pin.setFixedSize(30, 30)
        self.btn_pin.setIconSize(QSize(16, 16))
        self.btn_pin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pin.setToolTip("窗口置顶")
        self.btn_pin.setStyleSheet(button_style)
        self.btn_pin.clicked.connect(self._toggle_pin)

        self.btn_close = QPushButton(self)
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setIconSize(QSize(12, 12))
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setToolTip("关闭")
        self.btn_close.setStyleSheet(
            "QPushButton { background: transparent; border: none; "
            "border-top-right-radius: 12px; } "
            "QPushButton:hover { background: #ff4d4f; }"
        )
        self.btn_close.clicked.connect(self.close)

        title_row.addWidget(self.title_label)
        title_row.addStretch(1)
        header.addLayout(title_row)

        search_row = QHBoxLayout()
        search_row.setContentsMargins(0, 0, 0, 0)
        search_row.setSpacing(6)
        search_row.addWidget(self.search_box)
        search_row.addWidget(self.btn_settings)
        header.addLayout(search_row)
        layout.addLayout(header)

        self.display_frame = QFrame()
        self.display_frame.setObjectName("allSchedulesDisplayFrame")
        self.display_frame.setStyleSheet(
            """
            QFrame#allSchedulesDisplayFrame {
                background-color: rgba(255, 255, 255, 0.75);
                border: 2px solid white;
                border-radius: 8px;
            }
            """
        )
        display_layout = QVBoxLayout(self.display_frame)
        display_layout.setContentsMargins(8, 8, 8, 8)
        display_layout.setSpacing(6)

        self.settings_area = QFrame()
        self.settings_area.setObjectName("allSchedulesSettingsArea")
        self.settings_area.setStyleSheet(
            "QFrame#allSchedulesSettingsArea { background: transparent; border: none; }"
        )
        settings_layout = QGridLayout(self.settings_area)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        self._prepare_option_grid(settings_layout)
        self._add_option_row(
            settings_layout,
            "完成情况",
            ["已完成", "已过期", "未完成", "全部"],
            checked_index=3,
        )
        self._add_option_row(
            settings_layout,
            "日程类型",
            ["日程", "DDL", "时间段", "待办", "全部"],
            checked_index=4,
        )
        self._add_option_row(
            settings_layout,
            "重要性",
            ["低", "中", "高", "全部"],
            checked_index=3,
        )
        self._add_option_row(
            settings_layout,
            "提醒",
            ["提醒", "无提醒", "全部"],
            checked_index=2,
        )
        self._add_option_row(
            settings_layout,
            "重复",
            ["重复", "不重复", "全部"],
            checked_index=2,
        )
        self.category_combo = self._create_category_combo()
        self._add_combo_row(settings_layout, "清单", self.category_combo)
        self._add_option_row(
            settings_layout,
            "排序方式",
            ["按重要性", "按时间"],
            checked_index=1,
        )
        self.settings_area.hide()

        self.search_options_area = QFrame()
        self.search_options_area.setObjectName("allSchedulesSearchOptionsArea")
        self.search_options_area.setStyleSheet(
            "QFrame#allSchedulesSearchOptionsArea { background: transparent; border: none; }"
        )
        search_options_layout = QGridLayout(self.search_options_area)
        search_options_layout.setContentsMargins(0, 0, 0, 0)
        self._prepare_option_grid(search_options_layout)
        self._add_option_row(
            search_options_layout,
            "搜索范围",
            ["标题", "标题+详情"],
            checked_index=0,
        )
        self._add_option_row(
            search_options_layout,
            "搜索设置",
            ["模糊搜索", "精准搜索"],
            checked_index=0,
        )
        self.search_options_area.hide()

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("allSchedulesScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet(
            """
            QScrollArea#allSchedulesScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea#allSchedulesScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.55);
                border-radius: 3px;
                min-height: 24px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }
            """
        )
        self.results_container = QWidget()
        self.results_container.setStyleSheet("background: transparent;")
        results_layout = QVBoxLayout(self.results_container)
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(6)
        self.empty_label = QLabel("暂无日程数据")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(
            "color: rgba(0, 102, 204, 0.72); font-size: 12px; "
            "font-family: 'Microsoft YaHei UI'; background: transparent; border: none;"
        )
        results_layout.addStretch(1)
        results_layout.addWidget(self.empty_label)
        results_layout.addStretch(1)
        self.scroll_area.setWidget(self.results_container)

        display_layout.addWidget(self.scroll_area, 1)
        layout.addWidget(self.search_options_area, 0)
        layout.addWidget(self.settings_area, 0)
        layout.addWidget(self.display_frame, 1)
        self.search_box.installEventFilter(self)
        self._install_resize_event_filters()
        self._update_header_icons()
        self._update_header_button_positions()

    def _prepare_option_grid(self, grid):
        grid.setHorizontalSpacing(self.OPTION_ROW_SPACING)
        grid.setVerticalSpacing(3)
        grid.setColumnMinimumWidth(0, self.OPTION_TITLE_WIDTH)
        grid.setColumnStretch(0, 0)
        for column in range(1, self.OPTION_GRID_COLUMNS + 1):
            grid.setColumnStretch(column, 1)

    def _next_grid_row(self, grid):
        if grid.count() == 0:
            return 0
        return grid.rowCount()

    def _option_grid_positions(self, option_count):
        if option_count >= 5:
            return [(index + 1, 1) for index in range(option_count)]
        if option_count == 4:
            return [(1, 1), (2, 1), (3, 1), (5, 1)]
        if option_count == 3:
            return [(1, 1), (3, 1), (5, 1)]
        if option_count == 2:
            return [(2, 2), (4, 2)]
        return [(1, self.OPTION_GRID_COLUMNS)]

    def _add_option_row(self, parent_layout, title, options, checked_index=0):
        row = self._next_grid_row(parent_layout)
        title_label = QLabel(title)
        title_label.setFixedWidth(self.OPTION_TITLE_WIDTH)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_label.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei UI'; font-size: 10px; "
            "background: transparent; border: none;"
        )
        parent_layout.addWidget(title_label, row, 0)

        buttons = []
        positions = self._option_grid_positions(len(options))
        for index, text in enumerate(options):
            button = _DotOptionButton(text)
            button.setChecked(index == checked_index)
            column, span = positions[index]
            parent_layout.addWidget(button, row, column, 1, span)
            buttons.append(button)

        for button in buttons:
            button.clicked.connect(
                lambda checked=False, current=button, group=buttons: self._select_option_button(
                    group,
                    current,
                )
            )

    def _add_combo_row(self, parent_layout, title, combo):
        row = self._next_grid_row(parent_layout)
        title_label = QLabel(title)
        title_label.setFixedWidth(self.OPTION_TITLE_WIDTH)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_label.setStyleSheet(
            "color: white; font-family: 'Microsoft YaHei UI'; font-size: 10px; "
            "background: transparent; border: none;"
        )
        parent_layout.addWidget(title_label, row, 0)
        parent_layout.addWidget(combo, row, 1, 1, self.OPTION_GRID_COLUMNS)

    def _create_category_combo(self):
        combo = QComboBox()
        combo.setFixedHeight(22)
        combo.setCursor(Qt.CursorShape.PointingHandCursor)
        combo.addItem("全部清单", None)
        combo.addItem("未分类", "__uncategorized__")
        try:
            from src.data.database import db_manager

            for category in db_manager.get_active_categories():
                combo.addItem(getattr(category, "name", "未命名清单"), getattr(category, "id", None))
        except Exception:
            pass
        combo.setStyleSheet(
            """
            QComboBox {
                color: white;
                background-color: rgba(255, 255, 255, 0.16);
                border: 1px solid rgba(255, 255, 255, 0.70);
                border-radius: 4px;
                padding: 1px 6px;
                font-family: 'Microsoft YaHei UI';
                font-size: 10px;
            }
            QComboBox:hover, QComboBox:focus {
                background-color: rgba(255, 255, 255, 0.22);
                border: 1px solid white;
            }
            QComboBox::drop-down {
                border: none;
                width: 18px;
            }
            QComboBox::down-arrow {
                image: url(assets/icons/combo_down_white.svg);
                width: 9px;
                height: 6px;
            }
            QComboBox QAbstractItemView {
                background: white;
                color: #0066cc;
                selection-background-color: #0066cc;
                selection-color: white;
                outline: none;
            }
            """
        )
        DayQueryOptionsPanel._apply_combo_popup_style(combo)
        combo.setFixedHeight(22)
        return combo

    def _select_option_button(self, buttons, selected_button):
        for button in buttons:
            button.setChecked(button is selected_button)

    def _load_tinted_pixmap(self, icon_name, color, target_size=16):
        path = f"assets/icons/{icon_name}"
        if not os.path.exists(path):
            return QPixmap()

        scale_ratio = 4.0
        high_res_size = int(target_size * scale_ratio)
        image = QImage(high_res_size, high_res_size, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        if icon_name.lower().endswith(".svg"):
            renderer = QSvgRenderer(path)
            if renderer.isValid():
                renderer.render(painter)
        else:
            source_image = QImage(path)
            if not source_image.isNull():
                source_image = source_image.scaled(
                    high_res_size,
                    high_res_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                x = (high_res_size - source_image.width()) // 2
                y = (high_res_size - source_image.height()) // 2
                painter.drawImage(x, y, source_image)
        painter.end()

        painter = QPainter(image)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        color_object = QColor(color) if isinstance(color, str) else color
        painter.fillRect(image.rect(), color_object)
        painter.end()

        pixmap = QPixmap.fromImage(image)
        pixmap.setDevicePixelRatio(scale_ratio)
        return pixmap

    def _load_tinted_icon(self, icon_name, color, target_size=16):
        pixmap = self._load_tinted_pixmap(icon_name, color, target_size)
        return QIcon(pixmap)

    def _load_padded_svg_icon(self, icon_name, color, icon_size=10, canvas_size=16):
        renderer = QSvgRenderer(f"assets/icons/{icon_name}")
        if not renderer.isValid():
            return QIcon()

        scale_ratio = 4.0
        high_res_canvas = int(canvas_size * scale_ratio)
        high_res_icon = int(icon_size * scale_ratio)
        offset = (high_res_canvas - high_res_icon) / 2

        image = QImage(high_res_canvas, high_res_canvas, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        renderer.render(painter, QRectF(offset, offset, high_res_icon, high_res_icon))
        painter.end()

        painter = QPainter(image)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(image.rect(), QColor(color))
        painter.end()

        pixmap = QPixmap.fromImage(image)
        pixmap.setDevicePixelRatio(scale_ratio)
        return QIcon(pixmap)

    def _update_header_icons(self):
        self._settings_icon_source = self._load_tinted_pixmap(
            "set.svg",
            "#FFFFFF",
            18,
        )
        self._set_settings_icon_angle(self._settings_icon_angle)
        pin_color = "#FFFFFF" if self.is_pinned else "#96FFFFFF"
        self.btn_pin.setIcon(self._load_tinted_icon("pin.svg", pin_color, 16))
        self.btn_close.setIcon(self._load_tinted_icon("close.png", "#FFFFFF", 12))

    def _get_settings_icon_angle(self):
        return self._settings_icon_angle

    def _set_settings_icon_angle(self, angle):
        self._settings_icon_angle = float(angle)
        if self._settings_icon_source.isNull():
            return

        canvas_size = 24.0
        icon_size = 18.0
        ratio = max(self._settings_icon_source.devicePixelRatio(), 1.0)
        pixmap = QPixmap(round(canvas_size * ratio), round(canvas_size * ratio))
        pixmap.setDevicePixelRatio(ratio)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.translate(canvas_size / 2.0, canvas_size / 2.0)
        painter.rotate(self._settings_icon_angle)
        painter.drawPixmap(
            QPointF(-icon_size / 2.0, -icon_size / 2.0),
            self._settings_icon_source,
        )
        painter.end()
        self.btn_settings.setIcon(QIcon(pixmap))

    settingsIconAngle = pyqtProperty(
        float,
        fget=_get_settings_icon_angle,
        fset=_set_settings_icon_angle,
    )

    def _update_header_button_positions(self):
        top_margin = 0
        right_margin = 0
        gap = 0

        close_x = self.width() - self.btn_close.width() - right_margin
        self.btn_close.move(close_x, top_margin)
        self.btn_close.raise_()

        pin_x = close_x - self.btn_pin.width() - gap
        self.btn_pin.move(pin_x, top_margin)
        self.btn_pin.raise_()

    def _toggle_settings_area(self):
        self._settings_visible = not self._settings_visible
        self.settings_area.setVisible(self._settings_visible)
        self._settings_rotation_animation.stop()
        self._settings_rotation_animation.setStartValue(self._settings_icon_angle)
        self._settings_rotation_animation.setEndValue(
            180.0 if self._settings_visible else 0.0
        )
        self._settings_rotation_animation.start()

    def _toggle_search_options_area(self):
        self._search_options_visible = not self._search_options_visible
        self.search_options_area.setVisible(self._search_options_visible)

    def _toggle_pin(self):
        self.set_pinned(not self.is_pinned)

    def set_pinned(self, enabled):
        self.is_pinned = bool(enabled)
        set_window_pin_state(self, self.is_pinned)
        self._update_header_icons()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_header_button_positions()

    def _install_resize_event_filters(self):
        for widget in (
            self.display_frame,
            self.scroll_area,
            self.scroll_area.viewport(),
            self.results_container,
            self.settings_area,
            self.search_options_area,
        ):
            widget.setMouseTracking(True)
            widget.installEventFilter(self)

    def eventFilter(self, watched, event):
        if (
            watched is self.search_box
            and event.type() == QEvent.Type.MouseButtonPress
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._toggle_search_options_area()
            return False

        if watched in {
            self.display_frame,
            self.scroll_area,
            self.scroll_area.viewport(),
            self.results_container,
            self.settings_area,
            self.search_options_area,
        }:
            if event.type() == QEvent.Type.Leave:
                watched.unsetCursor()
            elif event.type() == QEvent.Type.MouseMove and not event.buttons():
                edge = self._hit_resize_edge(watched.mapTo(self, event.position().toPoint()).y())
                watched.setCursor(
                    Qt.CursorShape.SizeVerCursor
                    if edge
                    else Qt.CursorShape.ArrowCursor
                )
            elif (
                event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
            ):
                edge = self._hit_resize_edge(watched.mapTo(self, event.position().toPoint()).y())
                if edge:
                    self._start_resize(edge, event.globalPosition().toPoint())
                    event.accept()
                    return True
            elif (
                event.type() == QEvent.Type.MouseMove
                and self._resize_edge
                and event.buttons() & Qt.MouseButton.LeftButton
            ):
                self._perform_resize(event.globalPosition().toPoint())
                event.accept()
                return True
            elif (
                event.type() == QEvent.Type.MouseButtonRelease
                and event.button() == Qt.MouseButton.LeftButton
                and self._resize_edge
            ):
                self._finish_resize()
                event.accept()
                return True
        return super().eventFilter(watched, event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        painter.fillPath(path, QBrush(gradient))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(0, 0, 0, 28), 1))
        painter.drawPath(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._hit_resize_edge(event.position().y())
            if edge:
                self._start_resize(edge, event.globalPosition().toPoint())
                event.accept()
                return
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resize_edge and self._resize_start_pos and self._resize_start_geometry:
            self._perform_resize(event.globalPosition().toPoint())
            event.accept()
            return

        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return

        edge = self._hit_resize_edge(event.position().y())
        self.setCursor(
            Qt.CursorShape.SizeVerCursor
            if edge
            else Qt.CursorShape.ArrowCursor
        )
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = None
            self._finish_resize()
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        if self._resize_edge is None:
            self.unsetCursor()
        super().leaveEvent(event)

    def _hit_resize_edge(self, y):
        if y <= self.RESIZE_MARGIN:
            return "top"
        if y >= self.height() - self.RESIZE_MARGIN:
            return "bottom"
        return None

    def _start_resize(self, edge, global_pos):
        self._resize_edge = edge
        self._resize_start_pos = global_pos
        self._resize_start_geometry = self.geometry()
        self.setCursor(Qt.CursorShape.SizeVerCursor)

    def _perform_resize(self, global_pos):
        if not self._resize_edge or not self._resize_start_pos or not self._resize_start_geometry:
            return
        delta_y = global_pos.y() - self._resize_start_pos.y()
        geometry = self._resize_start_geometry
        if self._resize_edge == "bottom":
            new_height = max(self.minimumHeight(), geometry.height() + delta_y)
            self.resize(self.width(), new_height)
        elif self._resize_edge == "top":
            new_height = max(self.minimumHeight(), geometry.height() - delta_y)
            consumed_delta = geometry.height() - new_height
            self.setGeometry(
                geometry.x(),
                geometry.y() + consumed_delta,
                geometry.width(),
                new_height,
            )

    def _finish_resize(self):
        self._resize_edge = None
        self._resize_start_pos = None
        self._resize_start_geometry = None
