# src/ui/schedule_detail_pop.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGridLayout, QSizePolicy,
                             QLineEdit, QTextEdit, QDialog, QMenu) # 🟢 新增了输入框组件
from PyQt6.QtCore import Qt, QRectF, QPoint, QSize, pyqtSignal, QEvent, QTimer
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QBrush, QLinearGradient, QIcon, QPen, QPixmap, QImage
from PyQt6.QtSvg import QSvgRenderer
from ..data.database import db_manager, Schedule
from ..utils.win_api import apply_24h2_border_fix
from ..utils.styles import StyleManager
from ..utils.window_preferences import set_window_pin_state
from ..config import AppConfig 
from .common.themed_color_dialog import ThemedColorDialog
import os
from datetime import datetime

class RepeatConfirmDialog(QDialog):
    def __init__(self, new_rule, parent=None):
        super().__init__(parent)
        self.result_mode = 0  # 0: 取消, 1: 仅此条, 2: 修改未来
        self.setFixedSize(300, 150)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        lbl_title = QLabel("修改循环规则")
        lbl_title.setStyleSheet("color: white; font-size: 16px; font-weight: bold; font-family: 'Microsoft YaHei';")
        layout.addWidget(lbl_title)
        
        lbl_msg = QLabel(f"您将重复规则修改为了【{new_rule}】。\n请选择修改范围：")
        lbl_msg.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 13px; font-family: 'Microsoft YaHei';")
        lbl_msg.setWordWrap(True)
        layout.addWidget(lbl_msg)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1); color: white; 
                border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 5px; 
                padding: 6px 0px; font-family: 'Microsoft YaHei'; font-size: 12px;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }
        """
        highlight_color = AppConfig.COLOR_GRADIENT_START
        highlight_hover = StyleManager.mix_colors(
            highlight_color,
            "#ffffff",
            0.85,
        )
        btn_style_highlight = f"""
            QPushButton {{
                background-color: {highlight_color}; color: white; border: none;
                border-radius: 5px; padding: 6px 0px; font-family: 'Microsoft YaHei'; font-size: 12px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {highlight_hover}; }}
        """
        
        btn_cancel = QPushButton("取消")
        btn_cancel.setStyleSheet(btn_style)
        btn_cancel.clicked.connect(self._on_cancel)
        
        btn_only_this = QPushButton("仅此条")
        btn_only_this.setStyleSheet(btn_style)
        btn_only_this.clicked.connect(self._on_only_this)
        
        btn_future = QPushButton("修改未来")
        btn_future.setStyleSheet(btn_style_highlight)
        btn_future.clicked.connect(self._on_future)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_only_this)
        btn_layout.addWidget(btn_future)
        layout.addLayout(btn_layout)

    def _on_cancel(self):
        self.result_mode = 0
        self.reject()
        
    def _on_only_this(self):
        self.result_mode = 1
        self.accept()
        
    def _on_future(self):
        self.result_mode = 2
        self.accept()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path.addRoundedRect(rect, 10.0, 10.0)
        # 绘制高级深灰磨砂背景
        painter.fillPath(path, QBrush(QColor(40, 44, 52, 245)))
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.drawPath(path)


class ScheduleDetailPop(QWidget):
    schedule_updated = pyqtSignal()
    req_edit_time = pyqtSignal(object)
    req_edit_alarm = pyqtSignal(object) 
    req_edit_list = pyqtSignal(object)  
    popup_closed = pyqtSignal(object)
    timetable_color_changed = pyqtSignal(object, object)

    def __init__(
        self,
        schedule_data,
        source_view="dashboard",
        dark_mode=False,
        parent=None,
        pin_icon_size=16,
    ):
        super().__init__(parent)
        self.data = schedule_data
        self.source_view = source_view
        self._popup_dark_mode = dark_mode
        self.is_pinned = False
        self.drag_pos = None
        self.timetable_color = None
        self._pin_icon_size = max(8, int(pin_icon_size))

        # 弹窗其他地方的字和图标，必须永远保持白色！
        self.c_text_main = "white"
        self.c_text_sub = "rgba(255,255,255,0.9)"
        self.c_icon = "#FFFFFF"
        self.c_combo_bg = "rgba(255, 255, 255, 0.2)"
        self.c_combo_border = "rgba(255, 255, 255, 0.5)"
        self.c_icon_pin = QColor(255, 255, 255, 255)
        self.c_icon_pin_off = QColor(255, 255, 255, 150)

        self._compute_theme_colors()

        self.setFixedWidth(320)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.win_id = int(self.winId())
        apply_24h2_border_fix(self.win_id)
        
        self._setup_ui()

    def _compute_theme_colors(self):
        """根据 _popup_dark_mode 和 source_view 计算所有动态颜色"""
        if self.source_view == "week":
            if self._popup_dark_mode:
                self.c_desc_bg = "#2b2b2b"
                self.c_desc_border = "rgba(255,255,255,0.1)"
                self._grid_text_color = "rgba(255,255,255,0.85)"
                # QColor 不支持 rgba() 字符串，必须用对象
                self._grid_icon_color = QColor(255, 255, 255, 217)
            else:
                self.c_desc_bg = "#FFFFFF"
                self.c_desc_border = "#FFFFFF"
                grid_end = AppConfig.COLOR_GRADIENT_END
                self._grid_text_color = grid_end
                self._grid_icon_color = grid_end
        else:
            self.c_desc_bg = StyleManager.derive_surface_rgba(
                AppConfig.COLOR_GRADIENT_START,
                dark_factor=115,
                alpha=0.9,
            )
            self.c_desc_border = "rgba(255, 255, 255, 0.6)"
            self._grid_text_color = "rgba(255,255,255,0.9)"
            self._grid_icon_color = "#FFFFFF"

    def _apply_popup_theme(self):
        """动态重设所有颜色相关 widget 的样式（用于切换暗色模式）"""
        # 描述框
        if hasattr(self, "desc_frame"):
            self.desc_frame.setStyleSheet(f"""
                QFrame {{ border: 1px solid {self.c_desc_border}; border-radius: 8px; background-color: {self.c_desc_bg}; }}
            """)
        # 描述文字
        if hasattr(self, "lbl_desc"):
            desc_color = self._get_desc_color(bool(self.data.description))
            self.lbl_desc.setStyleSheet(
                f"color: {desc_color}; border: none; background: transparent; font-size: 13px; font-family: 'Microsoft YaHei'; line-height: 1.5;"
            )
        if hasattr(self, "edit_desc"):
            self.edit_desc.setStyleSheet(f"""
                QTextEdit {{
                    background: transparent; color: {self._get_desc_color(True)};
                    border: none;
                    font-size: 13px; font-family: 'Microsoft YaHei'; padding: 0px;
                }}
            """)
        # 网格文字标签
        for attr in ("lbl_time_info", "lbl_alarm_info", "lbl_list_info",
                     "lbl_created_info", "lbl_priority", "lbl_repeat"):
            widget = getattr(self, attr, None)
            if widget is None:
                continue
            widget.setStyleSheet(
                f"color: {self._grid_text_color}; background: transparent; "
                "border: none; padding: 0px; font-size: 12px; "
                "font-family: 'Microsoft YaHei';"
            )
        # 网格图标（重新着色）
        for icon_lbl, icon_name in getattr(self, "_grid_icon_labels", []):
            if icon_name is None:
                continue
            pix = self._get_icon(icon_name, self._grid_icon_color, 16)
            if not pix.isNull():
                icon_lbl.setPixmap(pix)
        # 重复图标单独处理（它是 QLabel 对象，icon_name=None）
        if hasattr(self, "icon_repeat"):
            pix = self._get_icon("repeat.svg", self._grid_icon_color, 16)
            if not pix.isNull():
                self.icon_repeat.setPixmap(pix)
        # 强制重绘
        self.update()

    def _get_desc_color(self, has_text):
        """动态获取详情框里文字的颜色"""
        if self.source_view == "week":
            if self._popup_dark_mode:
                return "rgba(255,255,255,0.85)" if has_text else "rgba(255,255,255,0.45)"
            return "#666666" if has_text else "#999999"
        return "rgba(255, 255, 255, 0.9)" if has_text else "rgba(255, 255, 255, 0.6)"

    def set_timetable_color(self, color):
        if color is None:
            self.timetable_color = None
            if hasattr(self, "timetable_color_holder"):
                self.timetable_color_holder.hide()
            self._refresh_title_layout()
            return
        color_obj = QColor(color)
        if not color_obj.isValid():
            self.timetable_color = None
            if hasattr(self, "timetable_color_holder"):
                self.timetable_color_holder.hide()
            self._refresh_title_layout()
            return

        self.timetable_color = color_obj
        if hasattr(self, "lbl_timetable_color"):
            self.lbl_timetable_color.setStyleSheet(
                "QLabel { "
                "background-color: "
                f"rgba({color_obj.red()}, {color_obj.green()}, "
                f"{color_obj.blue()}, {color_obj.alpha()}); "
                "border: 2px solid white; "
                "border-radius: 2px; "
                "}"
            )
            self.lbl_timetable_color.show()
        if hasattr(self, "timetable_color_holder"):
            self.timetable_color_holder.show()
        self._refresh_title_layout()

    def _available_title_width(self):
        if not hasattr(self, "_main_layout") or not hasattr(self, "_title_row"):
            return 180

        main_margins = self._main_layout.contentsMargins()
        row_margins = self._title_row.contentsMargins()
        width = (
            self.width()
            - main_margins.left()
            - main_margins.right()
            - row_margins.left()
            - row_margins.right()
        )
        spacing = self._title_row.spacing()

        if hasattr(self, "lbl_source_icon") and self.lbl_source_icon.isVisible():
            width -= self.lbl_source_icon.width() + spacing
        if hasattr(self, "timetable_color_holder") and self.timetable_color_holder.isVisible():
            width -= self.timetable_color_holder.width() + spacing

        return max(80, width)

    def _refresh_title_layout(self):
        if not hasattr(self, "lbl_title"):
            return

        title_width = self._available_title_width()
        self.lbl_title.setFixedWidth(title_width)
        title_height = self.lbl_title.heightForWidth(title_width)
        if title_height <= 0:
            title_height = self.lbl_title.sizeHint().height()
        self.lbl_title.setFixedHeight(max(1, title_height))

        if hasattr(self, "edit_title"):
            self.edit_title.setFixedWidth(title_width)

        self.updateGeometry()
        self.adjustSize()

    def _handle_timetable_color_chip_clicked(self):
        if self.timetable_color is None:
            return
        selected = ThemedColorDialog.get_color(
            QColor(self.timetable_color),
            f"选择{getattr(self.data, 'title', '') or '日程'}日程颜色",
            AppConfig.COLOR_GRADIENT_START,
            self,
        )
        if not selected.isValid():
            return

        selected.setAlpha(self.timetable_color.alpha())
        self.set_timetable_color(selected)
        self.timetable_color_changed.emit(self.data, selected)

    def _handle_timetable_color_label_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._handle_timetable_color_chip_clicked()
            event.accept()
            return
        QLabel.mousePressEvent(self.lbl_timetable_color, event)

    def _get_icon(self, icon_name, color, target_size=16):
        path = f"assets/icons/{icon_name}"
        if not os.path.exists(path): return QPixmap()
        
        scale_ratio = 4.0
        high_res_size = int(target_size * scale_ratio)
        image = QImage(high_res_size, high_res_size, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(image)
        if icon_name.lower().endswith('.svg'):
            renderer = QSvgRenderer(path)
            if renderer.isValid(): renderer.render(painter)
        else:
            src_img = QImage(path)
            if not src_img.isNull():
                src_img = src_img.scaled(high_res_size, high_res_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                x = (high_res_size - src_img.width()) // 2
                y = (high_res_size - src_img.height()) // 2
                painter.drawImage(x, y, src_img)
        painter.end()

        painter = QPainter(image)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        if isinstance(color, str): color_obj = QColor(color)
        else: color_obj = color
            
        painter.fillRect(image.rect(), color_obj)
        painter.end()
        
        pixmap = QPixmap.fromImage(image)
        pixmap.setDevicePixelRatio(scale_ratio)
        return pixmap

    def _setup_ui(self):
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(20, 20, 20, 20)
        self._main_layout.setSpacing(15)

        # === 顶部控制栏 (标题 + 输入框切换) ===
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 60, 0)
        top_row.setSpacing(5)
        top_row.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._title_row = top_row

        # 如果是从“待办看板”打开的弹窗，加一个便签图标以示区分
        if self.source_view == "todo_board":
            self.lbl_source_icon = QLabel()
            self.lbl_source_icon.setFixedSize(24, 24)
            pix = self._get_icon("stick_view.svg", "#FFFFFF", 20)
            if not pix.isNull():
                self.lbl_source_icon.setPixmap(pix)
            self.lbl_source_icon.setStyleSheet("margin-top: 5px; background: transparent;")
            self.lbl_source_icon.setToolTip("待办看板 - 便签模式")
            top_row.addWidget(self.lbl_source_icon, 0, Qt.AlignmentFlag.AlignTop)

        # 标题显示标签
        self.timetable_color_holder = QWidget()
        self.timetable_color_holder.setFixedSize(18, 22)
        self.timetable_color_holder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.timetable_color_holder.mousePressEvent = self._handle_timetable_color_label_press
        self.timetable_color_holder.hide()
        self.lbl_timetable_color = QLabel(self.timetable_color_holder)
        self.lbl_timetable_color.setFixedSize(18, 18)
        self.lbl_timetable_color.move(0, 4)
        self.lbl_timetable_color.setToolTip("课表颜色")
        self.lbl_timetable_color.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_timetable_color.mousePressEvent = self._handle_timetable_color_label_press

        self.lbl_title = QLabel(self.data.title)
        self.lbl_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; font-family: 'Microsoft YaHei';")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.lbl_title.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.lbl_title.setWordWrap(True)
        self.lbl_title.installEventFilter(self) # 监听双击

        # 标题编辑框 (默认隐藏)
        self.edit_title = QLineEdit(self.data.title)
        self.edit_title.setStyleSheet("""
            QLineEdit {
                background: transparent; color: white;
                border: none;
                font-size: 20px; font-weight: bold; font-family: 'Microsoft YaHei'; padding: 0px;
            }
        """)
        self.edit_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.edit_title.hide()
        self.edit_title.installEventFilter(self)

        top_row.addWidget(self.timetable_color_holder, 0, Qt.AlignmentFlag.AlignTop)
        top_row.addWidget(self.lbl_title, stretch=1)
        top_row.addWidget(self.edit_title, 1, Qt.AlignmentFlag.AlignTop)
        self._main_layout.addLayout(top_row)

        # 固钉按钮
        # 固钉按钮
        self.btn_pin = QPushButton(self) 
        self.btn_pin.setFixedSize(30, 30) 
        self.btn_pin.setIconSize(
            QSize(self._pin_icon_size, self._pin_icon_size)
        )
        self.btn_pin.setCursor(Qt.CursorShape.PointingHandCursor)
        pin_icon = self._get_icon(
            "pin.svg",
            QColor(255, 255, 255, 150),
            self._pin_icon_size,
        )
        if not pin_icon.isNull(): self.btn_pin.setIcon(QIcon(pin_icon))
        else: self.btn_pin.setText("📌")
        
        # 加上 hover 态的背景变色逻辑
        self.btn_pin.setStyleSheet("""
            QPushButton { background: transparent; border: none; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); border-radius: 4px; }
        """)
        
        self.btn_pin.clicked.connect(self._toggle_pin)
        self.btn_pin.move(self.width() - 60, 0)

        # 关闭按钮
        self.btn_close = QPushButton(self) 
        self.btn_close.setFixedSize(30, 30) 
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        close_icon = self._get_icon("close.png", "#FFFFFF", 12)
        if not close_icon.isNull(): self.btn_close.setIcon(QIcon(close_icon))
        else: self.btn_close.setText("✕")
        self.btn_close.setStyleSheet("QPushButton { background: transparent; border: none; border-top-right-radius: 10px; } QPushButton:hover { background: #ff4d4f; }")
        self.btn_close.clicked.connect(self.close)
        self.btn_close.move(self.width() - 30, 0)

        # === 详情内容框 (强制存在，无内容时提示添加) ===
        self.desc_frame = QFrame()
        self.desc_frame.setStyleSheet(f"""
            QFrame {{ border: 1px solid {self.c_desc_border}; border-radius: 8px; background-color: {self.c_desc_bg}; }}
        """)
        desc_layout = QVBoxLayout(self.desc_frame)
        desc_layout.setContentsMargins(12, 12, 12, 12)
        
        # 详情显示标签
        desc_text = self.data.description if self.data.description else "暂无详情，双击添加..."
        desc_color = self._get_desc_color(bool(self.data.description))
        self.lbl_desc = QLabel(desc_text)
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet(f"color: {desc_color}; border: none; background: transparent; font-size: 13px; font-family: 'Microsoft YaHei'; line-height: 1.5;")
        self.lbl_desc.installEventFilter(self) # 监听双击
        
        # 详情编辑框 (默认隐藏)
        self.edit_desc = QTextEdit(self.data.description or "")
        self.edit_desc.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # 隐藏垂直滚动条
        self.edit_desc.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # 彻底隐藏水平滚动条！
        self.edit_desc.document().setDocumentMargin(0) # 消除内部边距，和标签文本完全对齐
        self.edit_desc.setStyleSheet(f"""
            QTextEdit {{
                background: transparent; color: {self._get_desc_color(True)};
                border: none;
                font-size: 13px; font-family: 'Microsoft YaHei'; padding: 0px;
            }}
        """)
        self.edit_desc.hide()
        self.edit_desc.installEventFilter(self)
        self.edit_desc.textChanged.connect(self._adjust_desc_height) # 文字变动时自动撑开弹窗高度
        
        desc_layout.addWidget(self.lbl_desc)
        desc_layout.addWidget(self.edit_desc)
        self._main_layout.addWidget(self.desc_frame)

        # === 3. 底部信息网格 ===
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setContentsMargins(0, 8, 0, 0)

        self._grid_icon_labels = []  # 存储 (icon_label, icon_name) 用于主题切换

        def create_info_item(icon_source, content):
            # 加上 self，防止我们后面隐藏它时，它变成游离的幽灵窗口
            w = QWidget(self)
            l = QHBoxLayout(w)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(6)

            # 图标支持传入字符串(生成静态图标) 或 QLabel(生成动态图标)
            if isinstance(icon_source, str):
                icon_lbl = QLabel()
                icon_lbl.setFixedSize(16, 16)
                pix = self._get_icon(icon_source, self._grid_icon_color, 16)
                if not pix.isNull(): icon_lbl.setPixmap(pix)
                l.addWidget(icon_lbl)
                self._grid_icon_labels.append((icon_lbl, icon_source))
            else:
                l.addWidget(icon_source)
                self._grid_icon_labels.append((icon_source, None))

            if isinstance(content, str):
                text_lbl = QLabel(content)
                text_lbl.setStyleSheet(
                    f"color: {self._grid_text_color}; font-size: 12px; "
                    "font-family: 'Microsoft YaHei';"
                )
                l.addWidget(text_lbl)
            else:
                l.addWidget(content)
                
            l.addStretch()
            return w

        # 数据准备
        # (1) 将时间做成独立 Label 并监听双击
        self.lbl_time_info = QLabel()
        self.lbl_time_info.setStyleSheet(
            f"color: {self._grid_text_color}; font-size: 12px; "
            "font-family: 'Microsoft YaHei';"
        )
        self.lbl_time_info.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_time_info.setToolTip("双击修改时间")
        self.lbl_time_info.installEventFilter(self)
        self.refresh_time_display() # 调用刷新方法填充文字

        # (2) 将提醒做成独立 Label 并监听双击
        self.lbl_alarm_info = QLabel()
        self.lbl_alarm_info.setStyleSheet(
            f"color: {self._grid_text_color}; font-size: 12px; "
            "font-family: 'Microsoft YaHei';"
        )
        self.lbl_alarm_info.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_alarm_info.setToolTip("双击修改提醒")
        self.lbl_alarm_info.installEventFilter(self)
        self.refresh_alarm_display()

        # (3) 将清单做成独立 Label 并监听双击
        self.lbl_list_info = QLabel()
        self.lbl_list_info.setStyleSheet(
            f"color: {self._grid_text_color}; font-size: 12px; "
            "font-family: 'Microsoft YaHei';"
        )
        self.lbl_list_info.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_list_info.setToolTip("双击修改所属清单")
        self.lbl_list_info.installEventFilter(self)
        self.refresh_list_display()

        self.lbl_created_info = QLabel()
        self.lbl_created_info.setStyleSheet(
            f"color: {self._grid_text_color}; font-size: 12px; "
            "font-family: 'Microsoft YaHei';"
        )
        self.lbl_created_info.setToolTip("最后修改时间")
        self.refresh_created_display()

        # --- (4) 重要性标签；编辑时使用独立菜单，避免内嵌下拉框重排窗口 ---
        self.lbl_priority = QLabel()
        self.lbl_priority.setStyleSheet(
            f"color: {self._grid_text_color}; background: transparent; "
            "border: none; padding: 0px; font-size: 12px; "
            "font-family: 'Microsoft YaHei';"
        )
        self.lbl_priority.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_priority.setToolTip("双击修改紧急性")
        self.lbl_priority.installEventFilter(self)

        self.priority_options = ("低重要性", "中重要性", "高重要性")

        self.priority_editor_container = QWidget()
        self.priority_editor_container.setStyleSheet(
            "background: transparent; border: none; padding: 0px;"
        )
        self.priority_editor_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.priority_editor_container.setToolTip("双击修改重要性")
        self.priority_editor_container.installEventFilter(self)
        pri_layout = QHBoxLayout(self.priority_editor_container)
        pri_layout.setContentsMargins(0, 0, 0, 0)
        pri_layout.addWidget(self.lbl_priority)

        # --- (5) 重复标签；编辑时使用独立菜单 ---
        self.lbl_repeat = QLabel()
        self.lbl_repeat.setStyleSheet(
            f"color: {self._grid_text_color}; background: transparent; "
            "border: none; padding: 0px; font-size: 12px; "
            "font-family: 'Microsoft YaHei';"
        )
        self.lbl_repeat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_repeat.setToolTip("双击修改重复规则")
        self.lbl_repeat.installEventFilter(self)

        self.repeat_options = ("不重复", "每天", "每周", "每月")

        self.icon_repeat = QLabel() 
        self.icon_repeat.setFixedSize(16, 16)

        self.repeat_editor_container = QWidget()
        self.repeat_editor_container.setStyleSheet(
            "background: transparent; border: none; padding: 0px;"
        )
        self.repeat_editor_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.repeat_editor_container.setToolTip("双击修改重复规则")
        self.repeat_editor_container.installEventFilter(self)
        rep_layout = QHBoxLayout(self.repeat_editor_container)
        rep_layout.setContentsMargins(0, 0, 0, 0)
        rep_layout.addWidget(self.lbl_repeat)

        self.refresh_priority_display()
        self.refresh_repeat_display()

        # 先把所有信息的容器对象拿到手里
        w_time = create_info_item("time.svg", self.lbl_time_info)
        w_alarm = create_info_item("alarm.svg", self.lbl_alarm_info)
        w_list = create_info_item("list.svg", self.lbl_list_info)
        w_created = create_info_item("edit_time.svg", self.lbl_created_info)
        w_priority = create_info_item("importance.svg", self.priority_editor_container)
        w_repeat = create_info_item(self.icon_repeat, self.repeat_editor_container)

        is_todo = getattr(self.data, 'item_type', 'schedule') == 'todo'

        if is_todo:
            # 待办模式：将不需要的【整个容器】隐藏
            w_time.hide()
            w_alarm.hide()
            w_repeat.hide()
            
            # 将剩下的排进网格，只有两行
            grid.addWidget(w_priority, 0, 0)
            grid.addWidget(w_list, 0, 1)
            grid.addWidget(w_created, 1, 0)
        else:
            # 日程模式：全量显示的六宫格
            grid.addWidget(w_time, 0, 0)
            grid.addWidget(w_alarm, 0, 1)
            grid.addWidget(w_list, 1, 0)
            grid.addWidget(w_created, 1, 1)
            grid.addWidget(w_priority, 2, 0)
            grid.addWidget(w_repeat, 2, 1)

        self._main_layout.addLayout(grid)
        
        # 1. 将原本单一的文本标签替换为 图标+文字 的组合容器
        self._refresh_title_layout()

    def _adjust_desc_height(self):
        """终极精准高度计算：抛弃不稳定的测算，使用绝对宽度"""
        if self.edit_desc.isVisible():
            # 弹窗固定宽 320 - 主边距 40 - 内边距 24 = 绝对内容宽度 256
            self.edit_desc.document().setTextWidth(256)
            doc_height = self.edit_desc.document().size().height()
            
            # 紧凑贴合，只给光标留 2px 呼吸空间
            self.edit_desc.setFixedHeight(int(doc_height) + 2)
            self.adjustSize()

    def refresh_time_display(self):
        """根据最新数据重新生成时间文字"""
        st, et = self.data.start_time, self.data.end_time
        if st and et:
            if st.date() == et.date(): time_str = f"{st.strftime('%m-%d %H:%M')} - {et.strftime('%H:%M')}"
            else: time_str = f"{st.strftime('%m-%d %H:%M')} - {et.strftime('%m-%d %H:%M')}"
        elif et: time_str = f"{et.strftime('%m-%d')} 截止: {et.strftime('%H:%M')}"
        else: time_str = "全天"
        self.lbl_time_info.setText(time_str)

    def refresh_alarm_display(self):
        """根据最新数据重新生成提醒文字"""
        reminder_str = self.data.reminder_time.strftime("%m-%d %H:%M") if self.data.reminder_time else "无提醒"
        self.lbl_alarm_info.setText(reminder_str)
        
    def refresh_list_display(self):
        """根据最新数据重新生成清单文字"""
        list_str = "未选择"
        if self.data.category_id:
            cat = db_manager.get_category(self.data.category_id)
            if cat:
                suffix = " (已删除)" if cat.is_deleted else ""
                list_str = f"#{cat.id:03d} {cat.name}{suffix}"
        self.lbl_list_info.setText(list_str)

    def refresh_priority_display(self):
        """刷新优先级展示"""
        p_map = {0: "低重要性", 1: "中重要性", 2: "高重要性"}
        self.lbl_priority.setText(p_map.get(self.data.priority, "低重要性"))

    def refresh_repeat_display(self):
        """刷新重复规则展示及图标"""
        rep = self.data.repeat_rule.strip()
        if not rep or rep in ("none", "无"):
            self.lbl_repeat.setText("不重复")
            pix = self._get_icon("repeat_off.svg", self._grid_icon_color, 16)
        else:
            self.lbl_repeat.setText(rep)
            pix = self._get_icon("repeat.svg", self._grid_icon_color, 16)
        
        if hasattr(self, 'icon_repeat'):
            self.icon_repeat.setPixmap(pix)

    def refresh_created_display(self):
        """刷新最后修改时间显示"""
        created_str = self.data.created_at.strftime("%m-%d %H:%M")
        self.lbl_created_info.setText(created_str)

    def _finish_edit_priority(self, index):
        """菜单选中后自动保存。"""
        changed = False
        if self.data.priority != index:
            self.data.priority = index
            self.data.created_at = datetime.now() # 更新修改时间
            db_manager.update_schedule_fields(self.data.id, priority=index, created_at=self.data.created_at)
            self.refresh_created_display() # 刷新时间UI
            changed = True
        self.refresh_priority_display()
        if changed:
            self.schedule_updated.emit()

    def _finish_edit_repeat(self, index):
        text = self.repeat_options[index]
        val = "无" if text == "不重复" else text
        changed = False

        if (self.data.repeat_rule or "").strip() == "自定义":
            changed = db_manager.convert_custom_instance_repeat(
                self.data.id,
                val,
                datetime.now(),
            )
            if changed:
                self.data = Schedule.get_by_id(self.data.id)
                self.refresh_repeat_display()
                self.refresh_created_display()
                self.schedule_updated.emit()
            return
        
        if self.data.repeat_rule != val:
            update_future = False
            has_group = bool(getattr(self.data, 'group_id', None))
            
            # 弹窗询问
            if has_group:
                dialog = RepeatConfirmDialog(val, self)
                dialog.exec()
                
                if dialog.result_mode == 0:  # 选择了 取消
                    self.refresh_repeat_display()
                    return
                elif dialog.result_mode == 2:  # 选择了 修改未来
                    update_future = True
                elif dialog.result_mode == 1:  # 选择了 仅此条
                    update_future = False
            else:
                if val != "无": update_future = True

            self.data.repeat_rule = val
            self.data.created_at = datetime.now()

            db_manager.update_schedule_with_repeat(
                self.data.id, 
                {'repeat_rule': val, 'created_at': self.data.created_at}, 
                update_future
            )
            self.data = Schedule.get_by_id(self.data.id)
            self.refresh_repeat_display()
            self.refresh_created_display() 
            changed = True

        self.refresh_repeat_display()
        if changed:
            self.schedule_updated.emit()

    @staticmethod
    def _style_choice_menu(menu):
        accent_color = StyleManager.theme_accent_color()
        selected_background = StyleManager.theme_overlay_rgba(0.12)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                padding: 4px;
                font-family: 'Microsoft YaHei';
                font-size: 12px;
            }}
            QMenu::item {{
                min-width: 64px;
                padding: 5px 12px;
                border-radius: 3px;
            }}
            QMenu::item:selected {{
                background-color: {selected_background};
                color: {accent_color};
            }}
        """)

    def _show_priority_menu(self):
        menu = QMenu(self)
        self._style_choice_menu(menu)
        for index, text in enumerate(self.priority_options):
            action = menu.addAction(text)
            action.setData(index)
        pos = self.priority_editor_container.mapToGlobal(
            QPoint(0, self.priority_editor_container.height())
        )
        selected = menu.exec(pos)
        if selected is not None:
            self._finish_edit_priority(int(selected.data()))

    def _show_repeat_menu(self):
        menu = QMenu(self)
        self._style_choice_menu(menu)
        menu.setToolTipsVisible(True)
        tooltip_map = {
            "不重复": "设为单次独立日程；循环组日程会在确认后按所选范围更新。",
            "每天": "按天重复；保存时沿用现有重复日程更新规则。",
            "每周": "按周重复；保存时沿用现有重复日程更新规则。",
            "每月": "按月重复；保存时沿用现有重复日程更新规则。",
        }
        for index, text in enumerate(self.repeat_options):
            action = menu.addAction(text)
            action.setData(index)
            action.setToolTip(tooltip_map[text])
        pos = self.repeat_editor_container.mapToGlobal(
            QPoint(0, self.repeat_editor_container.height())
        )
        selected = menu.exec(pos)
        if selected is not None:
            self._finish_edit_repeat(int(selected.data()))

    # 事件过滤器 (捕获双击、焦点丢失、回车)
    def eventFilter(self, obj, event):
        # 1. 拦截双击事件，进入编辑模式
        if event.type() == QEvent.Type.MouseButtonDblClick:
            if obj == getattr(self, 'lbl_time_info', None):
                self.req_edit_time.emit(self.data) # 发出修改时间信号
                return True
            elif obj == getattr(self, 'lbl_alarm_info', None):
                self.req_edit_alarm.emit(self.data) 
                return True
            elif obj == getattr(self, 'lbl_list_info', None):
                self.req_edit_list.emit(self.data) 
                return True
            # 拦截优先级双击
            elif obj in (
                getattr(self, 'lbl_priority', None),
                getattr(self, 'priority_editor_container', None),
            ):
                self._show_priority_menu()
                return True
            # 拦截重复规则双击
            elif obj in (
                getattr(self, 'lbl_repeat', None),
                getattr(self, 'repeat_editor_container', None),
            ):
                self._show_repeat_menu()
                return True
            elif obj == self.lbl_title:
                self.lbl_title.hide()
                self.edit_title.setText(self.lbl_title.text())
                self.edit_title.show()
                self.edit_title.setFocus()
                self.edit_title.selectAll()
                return True
            elif obj == getattr(self, 'lbl_desc', None):
                # 1. 记住当前文本标签的完美高度
                base_height = self.lbl_desc.height()
                self.lbl_desc.hide()
                
                # 2. 阻断信号！防止它在 0 宽度时去瞎算高度
                self.edit_desc.blockSignals(True)
                self.edit_desc.setPlainText(self.data.description or "")
                self.edit_desc.blockSignals(False)
                
                # 3. 先借用标签的高度撑住场面，防止瞬间闪烁
                self.edit_desc.setFixedHeight(base_height + 2)
                
                self.edit_desc.show()
                self.edit_desc.setFocus()
                cursor = self.edit_desc.textCursor()
                cursor.movePosition(cursor.MoveOperation.End) 
                self.edit_desc.setTextCursor(cursor)
                
                QTimer.singleShot(50, self._adjust_desc_height)
                return True
                
        # 2. 拦截回车按键 (仅限单行文本框 title)
        elif event.type() == QEvent.Type.KeyPress:
            if obj == self.edit_title and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self._finish_edit_title()
                return True
                
        # 3. 拦截焦点丢失 (点击其他区域)，完成编辑
        elif event.type() == QEvent.Type.FocusOut:
            if obj == self.edit_title and self.edit_title.isVisible():
                self._finish_edit_title()
                return True
            elif obj == self.edit_desc and self.edit_desc.isVisible():
                self._finish_edit_desc()
                return True

        return super().eventFilter(obj, event)

    # 结束标题编辑并保存
    def _finish_edit_title(self):
        new_title = self.edit_title.text().strip()
        if new_title and new_title != self.data.title:
            self.data.title = new_title
            self.data.created_at = datetime.now() # 更新修改时间
            self.lbl_title.setText(new_title)
            db_manager.update_schedule_fields(self.data.id, title=new_title, created_at=self.data.created_at)
            self.refresh_created_display() # 刷新时间UI
            self.schedule_updated.emit()
        elif not new_title:
            self.edit_title.setText(self.data.title)

        self.edit_title.hide()
        self.lbl_title.show()
        QTimer.singleShot(0, self._refresh_title_layout)

    # 结束详情编辑并保存
    def _finish_edit_desc(self):
        new_desc = self.edit_desc.toPlainText().strip()
        if new_desc != (self.data.description or ""):
            self.data.description = new_desc
            self.data.created_at = datetime.now() # 更新修改时间
            self.lbl_desc.setText(new_desc if new_desc else "暂无详情，双击添加...")
            desc_color = self._get_desc_color(bool(new_desc))
            self.lbl_desc.setStyleSheet(f"color: {desc_color}; border: none; background: transparent; font-size: 13px; font-family: 'Microsoft YaHei'; line-height: 1.5;")
            db_manager.update_schedule_fields(self.data.id, description=new_desc, created_at=self.data.created_at)
            self.refresh_created_display() # 刷新时间UI
            self.schedule_updated.emit()

        self.edit_desc.hide()
        self.lbl_desc.show()
        QTimer.singleShot(0, lambda: self.adjustSize())

    def _toggle_pin(self):
        self.set_pinned(not self.is_pinned)

    def set_pinned(self, enabled):
        self.is_pinned = bool(enabled)
        set_window_pin_state(self, self.is_pinned)
        self._refresh_pin_icon()

        if self.isVisible():
            self.raise_()
        apply_24h2_border_fix(int(self.winId()))

    def set_pin_icon_size(self, size):
        self._pin_icon_size = max(8, int(size))
        self.btn_pin.setIconSize(
            QSize(self._pin_icon_size, self._pin_icon_size)
        )
        self._refresh_pin_icon()

    def _refresh_pin_icon(self):
        pin_color = (
            QColor(255, 255, 255, 255)
            if self.is_pinned
            else QColor(255, 255, 255, 150)
        )
        pin_icon = self._get_icon(
            "pin.svg",
            pin_color,
            self._pin_icon_size,
        )
        if not pin_icon.isNull():
            self.btn_pin.setIcon(QIcon(pin_icon))

    def closeEvent(self, event):
        self.popup_closed.emit(self)
        super().closeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path.addRoundedRect(rect, 10.0, 10.0)

        if self.source_view == "week":
            if self._popup_dark_mode:
                bg_color = QColor("#2b2b2b")
                border_color = QColor(255, 255, 255, 25)
            else:
                bg_color = QColor("#FFFFFF")
                border_color = QColor(0, 0, 0, 30)
            painter.fillPath(path, QBrush(bg_color))

            # 渐变头部区：裁剪到与上方间距等距处
            if hasattr(self, "desc_frame"):
                gap = getattr(self, "_main_layout", None)
                gap = gap.spacing() if gap else 15
                header_bottom = self.desc_frame.geometry().bottom() + gap
            else:
                header_bottom = self.height() // 2
            painter.save()
            painter.setClipRect(
                QRectF(0, 0, float(self.width()), float(header_bottom))
            )
            gradient = QLinearGradient(0, 0, 0, header_bottom)
            gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
            gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
            painter.fillPath(path, QBrush(gradient))
            painter.restore()

            # 边线
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(border_color, 1.0))
            painter.drawPath(path)
        else:
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
            gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
            painter.fillPath(path, QBrush(gradient))
        
    def mousePressEvent(self, event):
        if hasattr(self, 'edit_title') and self.edit_title.isVisible():
            self.edit_title.clearFocus()
        if hasattr(self, 'edit_desc') and self.edit_desc.isVisible():
            self.edit_desc.clearFocus()
            
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        """双击分界线以下空白区切换弹窗暗色模式（仅周界面）"""
        if self.source_view != "week":
            super().mouseDoubleClickEvent(event)
            return

        # 计算渐变头部底边（与 paintEvent 一致）
        if hasattr(self, "desc_frame"):
            gap = getattr(self, "_main_layout", None)
            gap = gap.spacing() if gap else 15
            header_bottom = self.desc_frame.geometry().bottom() + gap
        else:
            header_bottom = self.height() // 2

        if event.position().y() > header_bottom:
            self._popup_dark_mode = not self._popup_dark_mode
            self._compute_theme_colors()
            self._apply_popup_theme()
            event.accept()
            return

        super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
