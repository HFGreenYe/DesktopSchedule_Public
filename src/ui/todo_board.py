# src/ui/todo_board.py
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QPushButton, QScrollArea, QGridLayout, QStackedWidget,QLineEdit, QTextEdit, QMenu, QSizePolicy)
from PyQt6.QtCore import Qt, QRect, QRectF, QTimer, pyqtSignal, QPoint, QMimeData
from PyQt6.QtGui import QAction, QIcon, QPainter, QPainterPath, QBrush, QLinearGradient, QColor, QPixmap, QImage, QDrag, QFontMetrics, QPen
from PyQt6.QtSvg import QSvgRenderer

from ..config import AppConfig
from ..data.database import db_manager 
from ..services.category_policy_service import CategoryDeleteAction, CategoryPolicyService
from ..services.schedule_query_service import ScheduleQueryService
from ..services.schedule_sort_service import ScheduleSortService
from ..utils.styles import StyleManager
from ..utils.window_preferences import set_window_pin_state
from .list_picker import ListPickerView
from .common.todo_board_add_folder_card import AddFolderCard
# ==========================================
# SVG 高清渲染与染色 
# ==========================================
def get_colored_icon(icon_name, color, target_size=12):

    path = f"assets/icons/{icon_name}"
    if not os.path.exists(path): return QPixmap()
    renderer = QSvgRenderer(path)
    if not renderer.isValid(): return QPixmap()
    
    scale_ratio = 4.0 # 提高分辨率解决锯齿问题
    high_res_size = int(target_size * scale_ratio)
    image = QImage(high_res_size, high_res_size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    
    painter = QPainter(image)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    color_obj = QColor(color) if isinstance(color, str) else color
    painter.fillRect(image.rect(), color_obj)
    painter.end()
    
    pixmap = QPixmap.fromImage(image)
    pixmap.setDevicePixelRatio(scale_ratio)
    return pixmap


def get_todo_card_color():
    return QColor(StyleManager.mix_colors(
        AppConfig.COLOR_GRADIENT_START,
        AppConfig.COLOR_GRADIENT_END,
        0.5,
    ))

# ==========================================
# 贴纸风格便签卡片组件 
# ==========================================
class StickyNoteCard(QFrame):
    req_status = pyqtSignal(int, int)
    req_pin = pyqtSignal(int, bool)
    req_delete = pyqtSignal(int)
    req_show_detail = pyqtSignal(object)
    def __init__(self, schedule_data, parent=None):
        super().__init__(parent)
        self.data = schedule_data
        self.setObjectName("stickyNoteCard")

        # 开启自定义右键菜单支持
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # 使用方法动态应用样式（区分置顶和普通状态）
        #self._apply_state_style()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 8) 
        main_layout.setSpacing(6)
        
        #main_layout = QVBoxLayout(self)
        #main_layout.setContentsMargins(10, 10, 10, 8) # 底部边距稍微缩小一点留给文字
        #main_layout.setSpacing(6)

        # --- 1. 顶部：图标 + 标题 ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        icon_label = QLabel()
        icon_label.setFixedSize(16, 16)
        icon_label.setStyleSheet("background: transparent; border: none;")
        
        # 确定颜色
        priority = getattr(self.data, 'priority', 0)
        if priority == 2: color = QColor(255, 77, 79) # 🔴 红
        elif priority == 1: color = QColor(250, 173, 20) # 🟡 黄
        else: color = QColor(82, 196, 26) # 🟢 绿
            
        pin_icon = get_colored_icon("pin_board.svg", color, 16)
        if not pin_icon.isNull():
            icon_label.setPixmap(pin_icon)
        else:
            icon_label.setText("📌")

        header_layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignTop)

        self._title_text = str(getattr(self.data, "title", ""))
        self._title_color = "white"
        self.title_label = QLabel(self._title_text)
        self.title_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px; font-family: 'Microsoft YaHei'; border: none; background: transparent;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.title_label.setWordWrap(True)
        self.title_label.setFixedHeight(38)
        self.title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        header_layout.addWidget(self.title_label, 1, Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(header_layout)

        # --- 底部：清单标签 (右下角) ---
        main_layout.addStretch() # 加个弹簧把标题顶在上面，把清单标签压在最下面
        
        if getattr(self.data, 'category_id', None):
            category = db_manager.get_category(self.data.category_id)
            if category and not getattr(category, 'is_deleted', False):
                bottom_layout = QHBoxLayout()
                bottom_layout.setContentsMargins(0, 0, 0, 0)
                bottom_layout.addStretch() # 左侧加弹簧，把文字挤到右边
                
                # 统一风格，带上 #编号
                self.lbl_category = QLabel(f"#{category.id:03d} {category.name}")
                self.lbl_category.setStyleSheet("""
                    color: rgba(255, 255, 255, 0.6); 
                    font-size: 10px; 
                    font-family: 'Microsoft YaHei'; 
                    font-weight: bold; 
                    background: transparent; 
                    border: none;
                """)
                bottom_layout.addWidget(self.lbl_category)
                main_layout.addLayout(bottom_layout)

        self._apply_state_style()

    # 应用状态样式（解决置顶的视觉表现）
    def _apply_state_style(self):
        is_pinned = getattr(self.data, 'is_pinned', False)
        base_color = get_todo_card_color()
        bg_color = base_color.name()
        hover_color = base_color.lighter(108).name()
        border = (
            "1px solid rgba(255, 255, 255, 0.8)"
            if is_pinned
            else "none"
        )
        
        self.setStyleSheet(f"""
            QFrame#stickyNoteCard {{
                background-color: {bg_color};
                border: {border};
                border-radius: 6px;
            }}
            QFrame#stickyNoteCard:hover {{
                background-color: {hover_color};
            }}
        """)
        if hasattr(self, 'title_label'):
            self._title_color = "white"
            self._fit_title_label()

    def _set_title_style(self, font_size):
            self.title_label.setStyleSheet(f"""
                color: {self._title_color}; 
                font-weight: bold; 
                font-size: {font_size}px; 
                font-family: 'Microsoft YaHei'; 
                border: none; 
                background: transparent;
            """)

    def _fit_title_label(self):
        if not hasattr(self, 'title_label'):
            return

        width = max(40, self.title_label.width())
        height = self.title_label.height()
        flags = Qt.TextFlag.TextWordWrap.value | Qt.AlignmentFlag.AlignLeft.value

        for font_size in (13, 12, 11, 10):
            font = self.title_label.font()
            font.setPixelSize(font_size)
            metrics = QFontMetrics(font)
            rect = metrics.boundingRect(QRect(0, 0, width, 1000), flags, self._title_text)
            if rect.height() <= height:
                self._set_title_style(font_size)
                return

        self._set_title_style(10)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'title_label'):
            self._fit_title_label()

    # 右键菜单呼出逻辑
    def _show_context_menu(self, pos):
        from .components import ScheduleContextMenu
        menu = ScheduleContextMenu(self.data, self)
        menu.setup_actions(
            status_callback=lambda status: self.req_status.emit(self.data.id, status),
            pin_callback=lambda is_pinned: self.req_pin.emit(self.data.id, is_pinned),
            delete_callback=lambda: self.req_delete.emit(self.data.id)
        )
        menu.exec(self.mapToGlobal(pos))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._click_pos = event.pos()
            event.accept() 

    def mouseMoveEvent(self, event):
        if not hasattr(self, '_click_pos'): return
        if (event.pos() - self._click_pos).manhattanLength() > 10:
            from PyQt6.QtGui import QDrag
            from PyQt6.QtCore import QMimeData
            
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(str(self.data.id)) 
            drag.setMimeData(mime_data)
            
            drag.setPixmap(self.grab())
            drag.setHotSpot(event.pos())
            
            container = self.parentWidget()
            if hasattr(container, 'current_drag_widget'):
                container.current_drag_widget = self
            
            # 把原卡片变虚线占位，隐藏所有文字
            self.title_label.hide()
            if hasattr(self, 'lbl_category'): 
                self.lbl_category.hide() # 隐藏右下角的清单文字
                
            self.setStyleSheet(
                "QFrame#stickyNoteCard { background: transparent; "
                "border: 2px dashed rgba(255, 255, 255, 0.4); }"
            )
            
            drag.exec(Qt.DropAction.MoveAction)
            
            # 拖拽结束：恢复原样
            self.title_label.show()
            if hasattr(self, 'lbl_category'): 
                self.lbl_category.show() # 恢复右下角的清单文字
                
            self._apply_state_style()
            if hasattr(container, 'current_drag_widget'):
                container.current_drag_widget = None

    def mouseReleaseEvent(self, event):
        if hasattr(self, '_click_pos') and event.button() == Qt.MouseButton.LeftButton:
            if (event.pos() - self._click_pos).manhattanLength() < 5:
                self.req_show_detail.emit(self.data)
            del self._click_pos
            event.accept()
        else:
            super().mouseReleaseEvent(event)

# ==========================================
# 动态响应式便签网格容器
# ==========================================
class DropWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 把最初传入的父对象（StickViewContainer）存为 container
        self.container = parent 
        self.setAcceptDrops(True)
        self.current_drag_widget = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasText(): event.accept()

    def dragMoveEvent(self, event):
        if self.container:
            self.container._handle_drag_move(event)

    def dropEvent(self, event):
        if self.container:
            self.container._save_new_order()
        event.accept()


class SnapPointScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scroll_snap_points = [0]

    def _configure_snap_points(self, content_widget, snap_points, preferred_value=None):
        current_value = self.verticalScrollBar().value()
        normalized_points = sorted({max(0, int(point)) for point in snap_points}) or [0]
        scroll_limit = normalized_points[-1]
        self._scroll_snap_points = normalized_points
        content_widget.setMinimumHeight(max(1, self.viewport().height()) + scroll_limit)

        if preferred_value is None:
            target_value = min(
                normalized_points,
                key=lambda point: abs(point - current_value),
            )
        else:
            target_value = min(
                normalized_points,
                key=lambda point: abs(point - preferred_value),
            )
        QTimer.singleShot(
            0,
            lambda: self.verticalScrollBar().setValue(
                min(target_value, self.verticalScrollBar().maximum())
            ),
        )

    def wheelEvent(self, event):
        scroll_bar = self.verticalScrollBar()
        angle_delta = event.angleDelta().y()
        if angle_delta == 0 or len(self._scroll_snap_points) <= 1 or scroll_bar.maximum() <= 0:
            super().wheelEvent(event)
            return

        current_index = min(
            range(len(self._scroll_snap_points)),
            key=lambda index: abs(self._scroll_snap_points[index] - scroll_bar.value()),
        )
        notch_count = max(1, abs(angle_delta) // 120)
        direction = -1 if angle_delta > 0 else 1
        target_index = max(
            0,
            min(len(self._scroll_snap_points) - 1, current_index + direction * notch_count),
        )
        scroll_bar.setValue(self._scroll_snap_points[target_index])
        event.accept()


class RowSnapScrollArea(SnapPointScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._row_scroll_step = 0
        self._row_scroll_limit = 0

    def _configure_row_scrolling(self, row_count, card_height, spacing, top_margin, bottom_margin):
        viewport_height = max(1, self.viewport().height())
        previous_step = self._row_scroll_step
        previous_value = self.verticalScrollBar().value()
        previous_row = round(previous_value / previous_step) if previous_step else 0

        if row_count <= 0 or card_height <= 0:
            self._row_scroll_step = 0
            self._row_scroll_limit = 0
            self._configure_snap_points(self.scroll_content, [0], 0)
            return

        row_pitch = card_height + spacing
        usable_height = max(1, viewport_height - top_margin - bottom_margin)
        visible_rows = max(1, (usable_height + spacing) // row_pitch)
        hidden_rows = max(0, row_count - visible_rows)
        scroll_limit = hidden_rows * row_pitch

        self._row_scroll_step = row_pitch
        self._row_scroll_limit = scroll_limit
        snap_points = [row_index * row_pitch for row_index in range(hidden_rows + 1)]
        self._configure_snap_points(
            self.scroll_content,
            snap_points,
            min(previous_row * row_pitch, self._row_scroll_limit),
        )


class StickViewContainer(RowSnapScrollArea):
    req_status = pyqtSignal(int, int)
    req_pin = pyqtSignal(int, bool)
    req_delete = pyqtSignal(int)
    req_show_detail = pyqtSignal(object)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { width: 6px; background: transparent; margin: 0px; }
            QScrollBar::handle:vertical { background: rgba(255, 255, 255, 0.3); border-radius: 3px; }
            QScrollBar::handle:vertical:hover { background: rgba(255, 255, 255, 0.5); }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        self.scroll_content = DropWidget(self)
        self.scroll_content.setStyleSheet("background: transparent;")
        self.setViewportMargins(0, 0, 0, 0)
        if self.viewport():
            self.viewport().setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setContentsMargins(5, 6, 5, 0)
        self.grid_layout.setSpacing(8) 
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setWidget(self.scroll_content)
        self.cards = []
        self._column_count = 1

    def load_data(self, schedules_list):
        """接收真实列表渲染"""
        item_count = len(schedules_list)
        
        # 1. 清空旧卡片
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                self.grid_layout.removeWidget(widget)
                widget.deleteLater()
        self.cards.clear()

        # 2. 清除旧比例
        for c in range(self.grid_layout.columnCount()):
            self.grid_layout.setColumnStretch(c, 0)

        if item_count == 0:
            self._column_count = 1
            margins = self.grid_layout.contentsMargins()
            self._configure_row_scrolling(
                0,
                0,
                self.grid_layout.verticalSpacing(),
                margins.top(),
                margins.bottom(),
            )
            return

        # 3. 动态列数
        if item_count <= 3: cols = 1
        elif item_count <= 6: cols = 2
        else: cols = 3
        self._column_count = cols

        for c in range(cols):
            self.grid_layout.setColumnStretch(c, 1)

        # 4. 生成真实卡片
        for i, sched in enumerate(schedules_list):
            card = StickyNoteCard(sched)
            
            # 连接卡片信号到容器，继续向上传递
            card.req_status.connect(self.req_status.emit)
            card.req_pin.connect(self.req_pin.emit)
            card.req_delete.connect(self.req_delete.emit)
            card.req_show_detail.connect(self.req_show_detail.emit)
            
            self.cards.append(card)
            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(card, row, col)

        self.update_card_heights()

    def update_card_heights(self):
        if not self.cards: return
        vh = self.viewport().height()
        target_h = int((vh - 26) / 3)-1
        target_h = max(target_h, 50)
        for card in self.cards:
            card.setFixedHeight(target_h)
        row_count = (len(self.cards) + self._column_count - 1) // self._column_count
        margins = self.grid_layout.contentsMargins()
        self._configure_row_scrolling(
            row_count,
            target_h,
            self.grid_layout.verticalSpacing(),
            margins.top(),
            margins.bottom(),
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_card_heights()

    def _handle_drag_move(self, event):
        target = self.scroll_content.current_drag_widget
        if not target: return

        pos = event.position()
        old_idx = self.cards.index(target)

        # 使用“最近中心点距离法”
        closest_idx = old_idx
        min_dist = float('inf')

        for i, card in enumerate(self.cards):
            # 获取卡片的中心坐标
            center = card.geometry().center()
            # 计算鼠标当前位置与各个卡片中心点的距离平方
            dist = (pos.x() - center.x())**2 + (pos.y() - center.y())**2
            
            if dist < min_dist:
                min_dist = dist
                closest_idx = i

        target_pin = getattr(target.data, 'is_pinned', False)
        temp_min, temp_max = 0, len(self.cards) - 1
        found_group = False
        
        for i, c in enumerate(self.cards):
            if getattr(c.data, 'is_pinned', False) == target_pin:
                if not found_group:
                    temp_min = i
                    found_group = True
                temp_max = i
        
        if found_group:
            closest_idx = max(temp_min, min(closest_idx, temp_max))

        new_idx = closest_idx

        if new_idx != old_idx:
            # 改变列表顺序
            self.cards.insert(new_idx, self.cards.pop(old_idx))
            # 立即刷新网格显示
            self._reorder_layout()
            
        event.accept()

    def _reorder_layout(self):
        """物理性地重新排布 QGridLayout 中的卡片顺序"""
        #暂时冻结容器的刷新，等卡片位置挪好了再统一画出来
        self.scroll_content.setUpdatesEnabled(False)
        
        item_count = len(self.cards)
        cols = 1 if item_count <= 3 else (2 if item_count <= 6 else 3)
        
        for i, card in enumerate(self.cards):
            target_row, target_col = i // cols, i % cols
            
            idx = self.grid_layout.indexOf(card)
            if idx != -1:
                r, c, _, _ = self.grid_layout.getItemPosition(idx)
                if r == target_row and c == target_col:
                    continue
            
            # 只有当 i 对应的行列变了，才执行这个搬家动作
            self.grid_layout.addWidget(card, target_row, target_col)
            
        #恢复刷新，并强制系统立即重绘一次，不留残影
        self.scroll_content.setUpdatesEnabled(True)
        self.scroll_content.update()

    def _save_new_order(self):
        """保存新顺序到数据库，并更新签名防止回滚"""
        for i, card in enumerate(self.cards):
            # 权重计算：越靠前的值越大
            new_order = float((len(self.cards) - i) * 100.0)
            if getattr(card.data, 'sort_order', 0.0) != new_order:
                card.data.sort_order = new_order # 同步内存数据
                db_manager.update_schedule_fields(card.data.id, sort_order=new_order)
        
        parent_window = self.window()
        if isinstance(parent_window, TodoBoardWindow):
            # 更新签名，并仅触发全局刷新（不要自身再刷新一次）
            todos = [c.data for c in self.cards]
            todo_categories = db_manager.get_active_categories()
            parent_window._last_signature = parent_window._generate_signature(todos, todo_categories)
            parent_window.notify_main_window_refresh()
            
# ==========================================
# 文件夹卡片组件
# ==========================================
class FolderCard(QFrame):
    clicked = pyqtSignal(object) # 传出分类 ID（未分类传 None）
    doubleClicked = pyqtSignal(object, str)
    delete_requested = pyqtSignal(int, str) 

    def __init__(self, category_id, category_name, is_empty, parent=None):
        super().__init__(parent)
        self.category_id = category_id
        self.category_name = category_name
        self.is_empty = is_empty

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 将卡片容器设置为完全透明且无边框
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
            QFrame:hover {
                /* 悬停时给一点极淡的背景光晕作为交互反馈 */
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8) # 稍微收紧一点图标和文字的间距

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(45, 45)
        
        icon_color = QColor("#999999") if self.is_empty else QColor("#FFFFFF")
        pixmap = get_colored_icon("card_folder.svg", icon_color, 45)
        
        if not pixmap.isNull():
            self.icon_label.setPixmap(pixmap)
        else:
            self.icon_label.setText("📁")
            self.icon_label.setStyleSheet("font-size: 40px; background: transparent; border: none;")

        self._name_text = str(self.category_name)
        self._name_color = "rgba(255, 255, 255, 0.6)" if self.is_empty else "white"
        self.name_label = QLabel(self._name_text)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setMaximumWidth(82)
        self.name_label.setFixedHeight(18)
        self.name_label.setMinimumWidth(1)
        self.name_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.name_label.setToolTip(self._name_text)
        
        # 字体变小两号 (14px -> 12px)
        self._fit_name_label()

        layout.addWidget(self.icon_label, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.name_label, 0, Qt.AlignmentFlag.AlignHCenter)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _set_name_style(self, font_size):
        self.name_label.setStyleSheet(f"color: {self._name_color}; font-weight: bold; font-size: {font_size}px; font-family: 'Microsoft YaHei'; border: none; background: transparent;")

    def _fit_name_label(self):
        if not hasattr(self, 'name_label'):
            return

        width = max(45, min(82, self.name_label.width() or 82))
        for font_size in (12, 11, 10, 9):
            font = self.name_label.font()
            font.setPixelSize(font_size)
            metrics = QFontMetrics(font)
            if metrics.horizontalAdvance(self._name_text) <= width:
                self.name_label.setText(self._name_text)
                self._set_name_style(font_size)
                return

        font = self.name_label.font()
        font.setPixelSize(9)
        metrics = QFontMetrics(font)
        self._set_name_style(9)
        self.name_label.setText(metrics.elidedText(self._name_text, Qt.TextElideMode.ElideRight, width))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'name_label'):
            label_width = max(45, min(82, self.width() - 18))
            self.name_label.setMaximumWidth(label_width)
            self._fit_name_label()

    def _show_context_menu(self, pos):
        # 拦截：系统默认的“未分类待办”不允许删除
        if self.category_id is None:
            return 
            
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: rgba(255, 255, 255, 0.95); border: 1px solid rgba(0, 0, 0, 0.1); border-radius: 5px; padding: 6px; color: #333333; }
            QMenu::item { background-color: transparent; padding: 6px 20px; border-radius: 4px; font-family: "Microsoft YaHei UI"; font-size: 12px; }
            /* 悬停时稍微泛红，提示是危险操作 */
            QMenu::item:selected { background-color: rgba(255, 77, 79, 0.1); color: #ff4d4f; }
        """)
        
        # 创建删除动作
        del_action = QAction("🗑️ 删除文件夹", self)
        del_action.triggered.connect(lambda: self.delete_requested.emit(self.category_id, self.category_name))
        menu.addAction(del_action)
        
        menu.exec(self.mapToGlobal(pos))

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.doubleClicked.emit(self.category_id, self.category_name)
            event.accept()

    # 对鼠标按下的拦截
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 限制：“未分类待办”这种特殊的固定占位文件夹不允许拖动
            if self.category_id is None:
                super().mousePressEvent(event)
                return
            self._click_pos = event.pos()
            event.accept()
        else:
            super().mousePressEvent(event)

    # 触发 QDrag 的能力与隐身效果
    def mouseMoveEvent(self, event):
        if not hasattr(self, '_click_pos'): return
        if (event.pos() - self._click_pos).manhattanLength() > 10:
            from PyQt6.QtGui import QDrag
            from PyQt6.QtCore import QMimeData
            
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(f"folder_{self.category_id}")
            drag.setMimeData(mime_data)
            
            drag.setPixmap(self.grab())
            drag.setHotSpot(event.pos())
            
            container = self.parentWidget()
            if hasattr(container, 'current_drag_widget'):
                container.current_drag_widget = self
            
            # 隐身特效：变虚线并隐藏里面文字
            original_style = self.styleSheet()
            self.setStyleSheet("QFrame { background: transparent; border: 2px dashed rgba(255, 255, 255, 0.4); border-radius: 12px; }")
            self.icon_label.hide()
            self.name_label.hide()
            
            drag.exec(Qt.DropAction.MoveAction)
            
            # 还原状态
            self.icon_label.show()
            self.name_label.show()
            self.setStyleSheet(original_style)
            
            if hasattr(container, 'current_drag_widget'):
                container.current_drag_widget = None
            if hasattr(self, '_click_pos'):
                del self._click_pos
            event.accept()
        else:
            super().mouseMoveEvent(event)

    # 将点击事件转移至弹起时校验，以避免与拖拽冲突
    def mouseReleaseEvent(self, event):
        if hasattr(self, '_click_pos') and event.button() == Qt.MouseButton.LeftButton:
            if (event.pos() - self._click_pos).manhattanLength() < 5:
                self.clicked.emit(self.category_id)
            del self._click_pos
            event.accept()
        else:
            super().mouseReleaseEvent(event)

# ==========================================
# 文件夹视图 3x3 网格容器
# ==========================================
class FolderViewContainer(RowSnapScrollArea):
    folder_opened = pyqtSignal(object, str)
    add_folder_requested = pyqtSignal()
    delete_folder_requested = pyqtSignal(int, str) 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { width: 6px; background: transparent; margin: 0px; }
            QScrollBar::handle:vertical { background: rgba(255, 255, 255, 0.3); border-radius: 3px; }
            QScrollBar::handle:vertical:hover { background: rgba(255, 255, 255, 0.5); }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        self.scroll_content = DropWidget(self)
        self.scroll_content.setStyleSheet("background: transparent;")
        self.setViewportMargins(0, 0, 0, 0)
        
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setContentsMargins(8, 17, 14, 0)
        #self.grid_layout.setSpacing(12) 

        self.grid_layout.setHorizontalSpacing(12) 
        self.grid_layout.setVerticalSpacing(20)

        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setWidget(self.scroll_content)
        self.cards =[]
        self._column_count = 3

    def load_data(self, folder_data_list, uncategorized_count):
        # 1. 清空旧卡片
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                self.grid_layout.removeWidget(widget)
                widget.deleteLater()
        self.cards.clear()

        # 2. 强制设为 3 列，保证 3x3 网格的基础结构
        cols = 3
        for c in range(cols):
            self.grid_layout.setColumnStretch(c, 1)

        current_index = 0
        
        # 3. 如果有未分类待办
        if uncategorized_count > 0:
            card = FolderCard(category_id=None, category_name="未分类待办", is_empty=False)
            card.doubleClicked.connect(self.folder_opened.emit) # 连接双击信号
            self.grid_layout.addWidget(card, current_index // cols, current_index % cols, Qt.AlignmentFlag.AlignCenter)
            self.cards.append(card)
            current_index += 1

        # 4. 生成数据库里所有的清单文件夹
        for data in folder_data_list:
            card = FolderCard(category_id=data['id'], category_name=data['name'], is_empty=data['is_empty'])
            card.doubleClicked.connect(self.folder_opened.emit) # 连接双击信号
            card.delete_requested.connect(self.delete_folder_requested.emit)
            self.grid_layout.addWidget(card, current_index // cols, current_index % cols, Qt.AlignmentFlag.AlignCenter)
            self.cards.append(card)
            current_index += 1
        
        add_card = AddFolderCard()
        add_card.clicked.connect(self.add_folder_requested.emit)
        self.grid_layout.addWidget(add_card, current_index // cols, current_index % cols, Qt.AlignmentFlag.AlignCenter)
        self.cards.append(add_card)

        self.update_card_heights()

    def update_card_heights(self):
        if not self.cards: return
        vh = self.viewport().height()
        # 计算高度，确保一屏刚好显示 3 行
        target_h = int((vh - 24) / 3) 
        target_h = max(target_h, 80)
        available_w = max(240, self.viewport().width() - 14)
        target_w = int((available_w - self.grid_layout.horizontalSpacing() * 2) / 3)
        target_w = max(76, min(112, target_w))
        for card in self.cards:
            card.setFixedHeight(target_h)
            card.setFixedWidth(target_w)
        row_count = (len(self.cards) + self._column_count - 1) // self._column_count
        margins = self.grid_layout.contentsMargins()
        self._configure_row_scrolling(
            row_count,
            target_h,
            self.grid_layout.verticalSpacing(),
            margins.top(),
            margins.bottom(),
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_card_heights()

    def _handle_drag_move(self, event):
        target = self.scroll_content.current_drag_widget
        if not target or not isinstance(target, FolderCard): return

        pos = event.position()
        if target not in self.cards: return
        old_idx = self.cards.index(target)

        # 同样使用“中心点距离推挤算法”
        closest_idx = old_idx
        min_dist = float('inf')

        for i, card in enumerate(self.cards):
            center = card.geometry().center()
            dist = (pos.x() - center.x())**2 + (pos.y() - center.y())**2
            if dist < min_dist:
                min_dist = dist
                closest_idx = i

        # 核心拦截逻辑：绝对禁止取代头尾的特殊占位符
        min_idx = 0
        # 如果存在"未分类"（判断特征为 category_id=None），最低插入下限退至 1
        if self.cards and isinstance(self.cards[0], FolderCard) and self.cards[0].category_id is None:
            min_idx = 1
            
        # 最后一个永远是 AddFolderCard 按钮
        max_idx = len(self.cards) - 2 
        
        if min_idx > max_idx: return
        
        # 将被选中的 index 限定在合法边界内
        closest_idx = max(min_idx, min(closest_idx, max_idx))

        new_idx = closest_idx

        if new_idx != old_idx:
            # 把这个卡片在列表中平移
            self.cards.insert(new_idx, self.cards.pop(old_idx))
            # 呼叫立即重绘
            self._reorder_layout()
            
        event.accept()

    def _reorder_layout(self):
        """实时响应矩阵排列"""
        self.scroll_content.setUpdatesEnabled(False)
        cols = 3
        for i, card in enumerate(self.cards):
            target_row, target_col = i // cols, i % cols
            idx = self.grid_layout.indexOf(card)
            if idx != -1:
                r, c, _, _ = self.grid_layout.getItemPosition(idx)
                if r == target_row and c == target_col:
                    continue
            self.grid_layout.addWidget(card, target_row, target_col)
        self.scroll_content.setUpdatesEnabled(True)
        self.scroll_content.update()

    def _save_new_order(self):
        """手松开时，将重排结果更新至数据库"""
        # 从当前网格中过滤掉不可拖拽的卡片（去除添加按钮、去除未分类），提取干净的清单序列
        draggable_folders =[c for c in self.cards if isinstance(c, FolderCard) and c.category_id is not None]
        
        for i, card in enumerate(draggable_folders):
            # 将视觉排序结果转换为 倒序权重浮点数
            new_order = float((len(draggable_folders) - i) * 100.0)
            db_manager.update_category_fields(card.category_id, sort_order=new_order)
            
        parent_window = self.window()
        if hasattr(parent_window, '_last_signature'):
            parent_window._last_signature = None
        if hasattr(parent_window, 'notify_main_window_refresh'):
            parent_window.notify_main_window_refresh()
        if hasattr(parent_window, 'refresh_data'):
            parent_window.refresh_data()


# ==========================================
# 专属清单管理视图 (纯管理，不包含选择功能)
# ==========================================
class ManageCategoryCard(QFrame):
    delete_requested = pyqtSignal(int, str)
    
    def __init__(self, category_id, category_name, parent=None):
        super().__init__(parent)
        self.cat_id = category_id
        self.cat_name = category_name
        self.setFixedHeight(45) # 卡片高度
        self.setStyleSheet("""
            QFrame { background-color: rgba(255, 255, 255, 0.1); border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); }
            QFrame:hover { background-color: rgba(255, 255, 255, 0.2); }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(
            f"background-color: {AppConfig.COLOR_GRADIENT_START}; "
            "border: 1px solid white; border-radius: 4px;"
        )
        
        lbl_name = QLabel(f"#{self.cat_id:03d}  {self.cat_name}")
        lbl_name.setStyleSheet("color: white; font-size: 13px; font-weight: bold; font-family: 'Microsoft YaHei'; background: transparent; border: none;")
        
        layout.addWidget(dot)
        layout.addSpacing(10)
        layout.addWidget(lbl_name)
        layout.addStretch()
        
        # 绑定右键菜单
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)
        
    def _show_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background-color: rgba(255, 255, 255, 0.95); border: 1px solid rgba(0, 0, 0, 0.1); border-radius: 5px; padding: 6px; color: #333333; }}
            QMenu::item {{ background-color: transparent; padding: 6px 20px; border-radius: 4px; font-family: "Microsoft YaHei UI"; font-size: 12px; }}
            QMenu::item:selected {{ background-color: {StyleManager.theme_overlay_rgba(0.10)}; color: {StyleManager.theme_accent_color()}; }}
        """)
        del_action = QAction("删除清单", self)
        del_action.triggered.connect(lambda: self.delete_requested.emit(self.cat_id, self.cat_name))
        menu.addAction(del_action)
        menu.exec(self.mapToGlobal(pos))

class ManageListView(QWidget):
    back_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 滚动区域
        self.scroll_area = SnapPointScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { width: 4px; background: transparent; margin: 0px; }
            QScrollBar::handle:vertical { background: rgba(255, 255, 255, 0.3); border-radius: 2px; }
        """)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 10, 20, 10) 
        self.content_layout.setSpacing(10)
        
        # 输入框容器 
        self.input_container = QWidget()
        self.input_container.setFixedHeight(50) # 调高容器以适应更大的控件
        self.input_container.hide()
        i_layout = QHBoxLayout(self.input_container)
        i_layout.setContentsMargins(0, 0, 0, 0)
        i_layout.setSpacing(12) # 增加输入框和确认按钮之间的间距
        
        self.input_new = QLineEdit()
        self.input_new.setPlaceholderText("输入清单名称，回车确认...")
        self.input_new.setFixedHeight(36) 
        self.input_new.setStyleSheet("""
            QLineEdit {
                background-color: #7092BE; 
                border: 2px solid #FFFFFF; 
                border-radius: 10px; 
                color: white;
                padding-left: 15px;
                font-family: 'Microsoft YaHei';
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.7);
                font-weight: normal;
            }
        """)
        
        self.btn_confirm_add = QPushButton("✔")
        self.btn_confirm_add.setFixedSize(36, 36) 
        self.btn_confirm_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirm_add.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF; /* 纯白实心背景 */
                border: none;
                border-radius: 18px; /* 完美正圆 (44的一半) */
                color: """ + AppConfig.COLOR_GRADIENT_START + """; /* 主题色对勾 */
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)
        
        self.btn_confirm_add.clicked.connect(self._add_category)
        self.input_new.returnPressed.connect(self._add_category)
        
        i_layout.addWidget(self.input_new)
        i_layout.addWidget(self.btn_confirm_add)
        self.content_layout.addWidget(self.input_container)
        
        # 卡片列表容器
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(8)
        self.content_layout.addWidget(self.cards_container)
        self.content_layout.addStretch()
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area, stretch=1)
        
        # 底部只有两个按钮：新建 和 退出
        self.footer = QWidget()
        self.footer.setStyleSheet("background: transparent;")
        f_layout = QHBoxLayout(self.footer)
        f_layout.setContentsMargins(25, 5, 25, 5)
        
        self.btn_add_new = QPushButton("+ 新建")
        self.btn_cancel = QPushButton("退出")
        
        btn_style = "QPushButton { background: transparent; border: 1px solid rgba(255,255,255,0.6); border-radius: 15px; color: white; font-weight: bold; font-family: 'Microsoft YaHei'; font-size: 13px; } QPushButton:hover { background: rgba(255,255,255,0.15); border-color: white; }"
        self.btn_add_new.setStyleSheet(btn_style)
        self.btn_cancel.setStyleSheet(btn_style)
        self.btn_add_new.setFixedSize(85, 30)
        self.btn_cancel.setFixedSize(85, 30)
        self.btn_add_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_add_new.clicked.connect(self._toggle_input)
        self.btn_cancel.clicked.connect(self.back_requested.emit)
        
        f_layout.addWidget(self.btn_add_new)
        f_layout.addStretch()
        f_layout.addWidget(self.btn_cancel)
        layout.addWidget(self.footer, stretch=0)

    def _toggle_input(self):
        self.input_container.setVisible(not self.input_container.isVisible())
        if self.input_container.isVisible():
            self.input_new.setFocus()
            self._schedule_scroll_geometry(reset_to_top=True)
        else:
            self._schedule_scroll_geometry()

    def _schedule_scroll_geometry(self, reset_to_top=False):
        QTimer.singleShot(0, lambda: self._update_scroll_geometry(reset_to_top))

    def _update_scroll_geometry(self, reset_to_top=False):
        card_count = self.cards_layout.count()
        card_height = 45
        card_spacing = self.cards_layout.spacing()
        card_pitch = card_height + card_spacing
        margins = self.content_layout.contentsMargins()
        usable_height = max(1, self.scroll_area.viewport().height() - margins.top() - margins.bottom())
        visible_cards = max(1, (usable_height + card_spacing) // card_pitch)
        hidden_cards = max(0, card_count - visible_cards)
        input_offset = (
            self.input_container.height() + self.content_layout.spacing()
            if self.input_container.isVisible()
            else 0
        )

        snap_points = [0]
        if input_offset:
            snap_points.append(input_offset)
        first_card_hide_offset = input_offset + margins.top() + card_height
        snap_points.extend(
            first_card_hide_offset + (hidden_index - 1) * card_pitch
            for hidden_index in range(1, hidden_cards + 1)
        )
        preferred_value = 0 if reset_to_top else None
        self.scroll_area._configure_snap_points(
            self.content_widget,
            snap_points,
            preferred_value,
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._schedule_scroll_geometry()
            
    def load_data(self):
        self.input_new.clear()
        self.input_container.hide()
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        categories = db_manager.get_active_categories(list_type='todo')
        for cat in categories:
            card = ManageCategoryCard(cat.id, cat.name)
            card.delete_requested.connect(self._delete_category)
            self.cards_layout.addWidget(card)
        self._schedule_scroll_geometry(reset_to_top=True)
            
    def _add_category(self):
        name = self.input_new.text().strip()
        if not name: return
        new_id = db_manager.add_category(name, list_type='todo')
        if new_id:
            self.load_data()
            if hasattr(self.window(), 'refresh_data'):
                self.window()._last_signature = None
                self.window().refresh_data()
                if hasattr(self.window(), 'notify_main_window_refresh'):
                    self.window().notify_main_window_refresh()
                
    def _delete_category(self, cat_id, cat_name):
        from PyQt6.QtWidgets import QMessageBox
        status = db_manager.check_category_status(cat_id)
        action = CategoryPolicyService.choose_delete_action(status)
        if action == CategoryDeleteAction.BLOCK:
            if hasattr(self.window(), 'show_toast'): self.window().show_toast("🚫 该清单存在有效待办，无法删除！")
        elif action == CategoryDeleteAction.SOFT_DELETE:
            reply = QMessageBox.question(self, '确认删除', f"清单【{cat_name}】包含历史待办。\n是否继续？", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                db_manager.soft_delete_category(cat_id)
                self.load_data()
                if hasattr(self.window(), 'refresh_data'):
                    self.window()._last_signature = None
                    self.window().refresh_data()
                    if hasattr(self.window(), 'notify_main_window_refresh'):
                        self.window().notify_main_window_refresh()
        else:
            db_manager.hard_delete_category(cat_id)
            self.load_data()
            if hasattr(self.window(), 'refresh_data'):
                self.window()._last_signature = None
                self.window().refresh_data()
                if hasattr(self.window(), 'notify_main_window_refresh'):
                    self.window().notify_main_window_refresh()


# ==========================================
# 轻量级内联添加待办视图
# ==========================================
class InlineAddTodoView(QWidget):
    saved = pyqtSignal()
    canceled = pyqtSignal()
    req_open_list_picker = pyqtSignal(object, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_priority = 0
        self.selected_category_id = None
        self._setup_ui()

    def _setup_ui(self):
        # 主布局：取消边距，让底部按钮能贴底，中间滚动
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 滚动区域 ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        # 定制极简滚动条
        self.scroll_area.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { width: 4px; background: transparent; margin: 0px; }
            QScrollBar::handle:vertical { background: rgba(255, 255, 255, 0.3); border-radius: 2px; }
            QScrollBar::handle:vertical:hover { background: rgba(255, 255, 255, 0.5); }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # 滚动内容容器
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)

        # 1. 标题输入框
        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText("请输入待办标题...")
        self.input_title.setFixedHeight(40)
        self.input_title.setStyleSheet("""
            QLineEdit {
                background: transparent; border: none; border-bottom: 1px solid rgba(255, 255, 255, 0.5); 
                color: white; font-size: 18px; padding: 0 5px; font-family: 'Microsoft YaHei'; font-weight: bold;
            }
            QLineEdit::placeholder { color: rgba(255, 255, 255, 0.6); font-weight: normal; }
            QLineEdit:focus { border-bottom: 2px solid white; }
        """)
        layout.addWidget(self.input_title)

        # 2. 详情折叠按钮
        self.icon_plus = QIcon(get_colored_icon("todo_plus.svg", QColor(255, 255, 255, 178), 14))
        self.icon_minus = QIcon(get_colored_icon("todo_minus.svg", QColor(255, 255, 255, 178), 14))

        self.btn_detail_toggle = QPushButton("添加描述详情")
        self.btn_detail_toggle.setIcon(self.icon_plus)
        self.btn_detail_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_detail_toggle.setStyleSheet("""
            QPushButton { background: transparent; color: rgba(255,255,255,0.7); text-align: left; border: none; font-family: 'Microsoft YaHei'; font-size: 13px; padding-left: 5px; }
            QPushButton:hover { color: white; }
        """)
        self.btn_detail_toggle.clicked.connect(self._toggle_details)
        layout.addWidget(self.btn_detail_toggle)

        # 3. 详情输入框 (默认隐藏)
        self.txt_details = QTextEdit()
        self.txt_details.setPlaceholderText("添加描述 (150字以内)...")
        self.txt_details.setFixedHeight(70)
        self.txt_details.setStyleSheet("""
            QTextEdit { 
                background-color: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.3); 
                border-radius: 8px; color: white; font-size: 13px; font-family: 'Microsoft YaHei'; padding: 8px; 
            }
            QTextEdit:focus { border: 1px solid rgba(255, 255, 255, 0.6); background-color: rgba(255, 255, 255, 0.15); }
        """)
        self.txt_details.hide()
        layout.addWidget(self.txt_details)

        # 4. 属性卡片 (紧急性 & 清单)
        self.info_card = QFrame()
        self.info_card.setStyleSheet("QFrame { background-color: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 8px; }")
        info_layout = QVBoxLayout(self.info_card)
        info_layout.setSpacing(12)
        info_layout.setContentsMargins(15, 12, 15, 12)

        self.lbl_info_priority = self._create_info_row("importance.svg", "低重要性")
        self.lbl_info_priority.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_info_priority.mousePressEvent = self._on_priority_click
        info_layout.addWidget(self.lbl_info_priority.row_container)

        self.lbl_info_list = self._create_info_row("list.svg", "未选择清单")
        self.lbl_info_list.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_info_list.mousePressEvent = self._on_list_click
        info_layout.addWidget(self.lbl_info_list.row_container)

        layout.addWidget(self.info_card)
        layout.addStretch()

        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)

        # --- 5. 底部按钮容器 (独立于滚动条，永远贴底) ---
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(20, 5, 20, 5)
        
        self.btn_cancel = QPushButton("取消")
        self.btn_confirm = QPushButton("保存")
        for btn in [self.btn_cancel, self.btn_confirm]:
            btn.setFixedSize(70, 30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet("QPushButton { background: transparent; border: 1px solid rgba(255,255,255,0.6); border-radius: 15px; color: white; font-family: 'Microsoft YaHei'; font-weight: bold;} QPushButton:hover { background: rgba(255,255,255,0.1); border: 1px solid white; }")
        self.btn_confirm.setStyleSheet(
            f"QPushButton {{ background: white; border: none; border-radius: 15px; "
            f"color: {AppConfig.COLOR_GRADIENT_START}; font-family: 'Microsoft YaHei'; "
            "font-weight: bold;} QPushButton:hover { background: #f0f0f0; }"
        )
        self.btn_cancel.clicked.connect(self.canceled.emit)
        self.btn_confirm.clicked.connect(self._on_save)
        
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_cancel)
        bottom_layout.addSpacing(15)
        bottom_layout.addWidget(self.btn_confirm)
        
        main_layout.addWidget(bottom_container)

    def _create_info_row(self, icon_name, text):
        row_widget = QWidget()
        row_widget.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(row_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(18, 18)
        icon_lbl.setPixmap(get_colored_icon(icon_name, "#FFFFFF", 18))
        
        text_lbl = QLabel(text)
        text_lbl.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 13px; font-family: 'Microsoft YaHei';")
        
        layout.addWidget(icon_lbl)
        layout.addWidget(text_lbl)
        layout.addStretch()
        
        text_lbl.row_container = row_widget 
        return text_lbl

    def _toggle_details(self):
        if self.txt_details.isVisible():
            self.txt_details.hide()
            self.btn_detail_toggle.setText("添加描述详情")
            self.btn_detail_toggle.setIcon(self.icon_plus)
        else:
            self.txt_details.show()
            self.btn_detail_toggle.setText("收起描述详情")
            self.btn_detail_toggle.setIcon(self.icon_minus)

    def _on_priority_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected_priority = (self.selected_priority + 1) % 3
            p_map = {0: "低重要性", 1: "中重要性", 2: "高重要性"}
            self.lbl_info_priority.setText(p_map[self.selected_priority])

    def _on_list_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.req_open_list_picker.emit(self.selected_category_id, 'todo')

    def _set_category(self, cat_id, cat_name):
        self.selected_category_id = cat_id
        if cat_id is None:
            self.lbl_info_list.setText("未选择清单")
            self.lbl_info_list.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 13px; font-family: 'Microsoft YaHei';")
        else:
            self.lbl_info_list.setText(f"#{cat_id:03d} {cat_name}")
            self.lbl_info_list.setStyleSheet("color: #FFFFFF; font-size: 13px; font-family: 'Microsoft YaHei'; font-weight: bold;")

    def reset(self):
        self.input_title.clear()
        self.txt_details.clear()
        self.txt_details.hide()
        self.btn_detail_toggle.setText("添加描述详情")
        self.btn_detail_toggle.setIcon(self.icon_plus)
        self.selected_priority = 0
        self.lbl_info_priority.setText("低重要性")
        self._set_category(None, "未选择清单")

    def _on_save(self):
        title = self.input_title.text().strip()
        if not title:
            # 复用看板已经写好的 show_toast 方法来提醒
            if hasattr(self.window(), 'show_toast'):
                self.window().show_toast("⚠️ 标题不能为空")
            return

        description = self.txt_details.toPlainText().strip()
        schedule_data = {
            'title': title,
            'item_type': 'todo',
            'priority': self.selected_priority,
            'repeat_rule': 'none',
            'description': description, 
            'category_id': self.selected_category_id
        }

        if db_manager.add_schedule(schedule_data):
            self.saved.emit()

# ==========================================
# 主看板窗口
# ==========================================
class TodoBoardWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_pinned = False
        self.view_mode = 'stick' 
        self._drag_pos = None
        self._last_signature = None # 用于记录数据是否改变，防止无意义闪烁
        self.current_folder_id = "NOT_IN_FOLDER" 
        self.current_folder_name = ""
        self._setup_ui()
        
        self.stick_view.req_status.connect(self._handle_status_change)
        self.stick_view.req_pin.connect(self._handle_pin_change)
        self.stick_view.req_delete.connect(self._handle_delete)
        self.stick_view.req_show_detail.connect(self._show_detail_popup)

        # ==========================================
        # 信号驱动
        # ==========================================
        if parent:
            # 1. 监听添加界面的保存动作 
            if hasattr(parent, 'page_add'):
                parent.page_add.saved.connect(self.refresh_data)
            
            # 2. 监听日程面板的全局刷新信号 
            if hasattr(parent, 'page_dashboard'):
                parent.page_dashboard.req_refresh_all.connect(self.refresh_data)
            
            # 3. 监听待办面板的全局刷新信号
            if hasattr(parent, 'page_todo'):
                parent.page_todo.req_refresh_all.connect(self.refresh_data)

        # 保留定时器作为兜底机制（应对比如凌晨 00:00 跨天这种非人为点击的更新），并提速到 1 秒
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(1000) 
        
        self.refresh_data() # 立即加载一次

    def _generate_signature(self, todos, categories):
        """统一生成防闪烁签名，将所有影响卡片外观的字段纳入监控"""
        current_signature = "-".join([
            f"{t.id}_{getattr(t, 'sort_order', 0)}_{getattr(t, 'category_id', '')}_{getattr(t, 'priority', 0)}_{getattr(t, 'title', '')}_{getattr(t, 'is_pinned', False)}_{getattr(t, 'status', 0)}" 
            for t in todos
        ])
        cat_signature = "-".join([f"{c.id}_{getattr(c, 'sort_order', 0.0)}" for c in categories])
        return f"{current_signature}|{cat_signature}|{self.view_mode}"

    def refresh_data(self):
        if hasattr(self.stick_view, 'scroll_content'):
            if self.stick_view.scroll_content.current_drag_widget is not None:
                return
        if hasattr(self, 'folder_view') and hasattr(self.folder_view, 'scroll_content'):
            if self.folder_view.scroll_content.current_drag_widget is not None:
                return
        all_schedules = db_manager.get_all_schedules()
        # ==========================================
        # 同步更新弹窗数据的代码
        # ==========================================
        parent_win = self.window()
        popups = parent_win.page_dashboard.open_popups if hasattr(parent_win, 'page_dashboard') else []
        for pop in popups:
            if pop.isVisible():
                for s in all_schedules:
                    if s.id == pop.data.id:
                        pop.data = s  
                        
                        # 增加兼容所有可能的方法名，彻底解决静默失效不更新的问题
                        for method_name in ['refresh_list_display', 'refresh_category_display', 'update_category_display']:
                            if hasattr(pop, method_name): getattr(pop, method_name)()
                            
                        if hasattr(pop, 'refresh_time_display'): pop.refresh_time_display()
                        if hasattr(pop, 'refresh_alarm_display'): pop.refresh_alarm_display()
                        if hasattr(pop, 'refresh_priority_display'): pop.refresh_priority_display()
                        if hasattr(pop, 'refresh_repeat_display'): pop.refresh_repeat_display()
                        break

        all_active_todos = []  
        active_cat_ids = set()
        uncategorized_count = 0

        # 第一步：先统计全局状态（保证底层文件夹空状态判定准确）
        for s in all_schedules:
            if getattr(s, 'status', 0) == 2:
                continue
                
            is_todo = ScheduleQueryService.is_todo(s)
            is_active = (getattr(s, 'status', 0) == 0) 
            
            if is_todo and is_active:
                all_active_todos.append(s) # 存入全局列表
                if getattr(s, 'category_id', None):
                    active_cat_ids.add(s.category_id)
                else:
                    uncategorized_count += 1

        # 第二步：提取出要在界面上渲染的卡片（如果是文件夹内，则实施过滤）
        todos = [] # 重新定义 todos 给后续的渲染使用
        for s in all_active_todos:
            if getattr(self, 'current_folder_id', "NOT_IN_FOLDER") != "NOT_IN_FOLDER":
                if getattr(s, 'category_id', None) != self.current_folder_id:
                    continue # 过滤掉非当前文件夹的待办
            todos.append(s)
                
        todos = ScheduleSortService.sort_for_todo_board(todos)
        self.current_todos = todos

        # 处理所有“清单(文件夹)”数据
        todo_categories = db_manager.get_active_categories(list_type='todo')
        folder_data =[]
        for cat in todo_categories:
            folder_data.append({
                'id': cat.id,
                'name': cat.name,
                'is_empty': cat.id not in active_cat_ids 
            })


        full_signature = self._generate_signature(todos, todo_categories)

        if self._last_signature == full_signature:
            return
        self._last_signature = full_signature

        # 给两个视图同时下发数据渲染指令
        self.stick_view.load_data(todos)
        self.folder_view.load_data(folder_data, uncategorized_count)
        
        current_widget = self.view_stack.currentWidget()
        if current_widget in [self.inline_add_view, self.page_list, self.manage_list_view]:
            # 如果用户正处于“添加待办”或“选择清单”界面，只在后台静默刷新数据，绝对不跳转界面
            pass
        else:
            if getattr(self, 'current_folder_id', "NOT_IN_FOLDER") != "NOT_IN_FOLDER":
                self.empty_placeholder.setText(f"【{self.current_folder_name}】\n\n当前分类没有任何未完成的待办！")
                # 在文件夹内部
                if not todos:
                    self.view_stack.setCurrentWidget(self.empty_placeholder)
                else:
                    self.view_stack.setCurrentWidget(self.stick_view)
            else:
                self.empty_placeholder.setText("当前视图：待办看板\n\n当前没有任何未完成的待办事项！")
                # 在外部主看板
                if not todos and not folder_data:
                    self.view_stack.setCurrentWidget(self.empty_placeholder)
                else:
                    if self.view_mode == 'stick':
                        if not todos:
                            self.view_stack.setCurrentWidget(self.empty_placeholder)
                        else:
                            self.view_stack.setCurrentWidget(self.stick_view)
                    elif self.view_mode == 'folder':
                        self.view_stack.setCurrentWidget(self.folder_view)

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

    def _apply_custom_tooltip(self, widget, text):
        from .header import ToolTipFilter
        t_filter = ToolTipFilter(text, widget)
        widget.installEventFilter(t_filter)
        widget._tooltip_filter = t_filter 

    def _setup_ui(self):
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(380, 300) 

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.bg_frame = QFrame(self)
        self.bg_frame.setStyleSheet("background: transparent;")
        bg_layout = QVBoxLayout(self.bg_frame)
        bg_layout.setContentsMargins(16, 16, 16, 6)
        main_layout.addWidget(self.bg_frame)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 70, 10) 

        self.title_label = QLabel("待办看板")
        self.title_label.setFixedHeight(26)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; border: none; background: transparent; font-family: 'Microsoft YaHei';")
        header_layout.addWidget(self.title_label)

        self.views_frame = QFrame(self)
        self.views_frame.setStyleSheet("background: transparent; border: none;")
        self.views_layout = QHBoxLayout(self.views_frame)
        self.views_layout.setContentsMargins(5, 0, 0, 0)
        self.views_layout.setSpacing(0)

        common_style = """
            QPushButton { background: transparent; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }
        """

        self.btn_stick = QPushButton()
        self.btn_stick.setFixedSize(26, 26)
        self.btn_stick.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_custom_tooltip(self.btn_stick, "便签视图")
        self.btn_stick.setStyleSheet(common_style)
        self.btn_stick.clicked.connect(lambda: self._switch_view('stick'))
        self.views_layout.addWidget(self.btn_stick)

        self.btn_folder = QPushButton()
        self.btn_folder.setFixedSize(26, 26)
        self.btn_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_custom_tooltip(self.btn_folder, "文件夹视图") 
        self.btn_folder.setStyleSheet(common_style)
        self.btn_folder.clicked.connect(lambda: self._switch_view('folder'))
        self.views_layout.addWidget(self.btn_folder)

        header_layout.addWidget(self.views_frame)
        self.btn_folder_back = QPushButton()
        self.btn_folder_back.setFixedSize(26, 26)
        self.btn_folder_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_custom_tooltip(self.btn_folder_back, "返回文件夹视图")
        self.btn_folder_back.setStyleSheet(common_style)
        pm_back = self._get_icon("folder_back.svg", QColor(255, 255, 255, 255), 16)
        if not pm_back.isNull(): 
            self.btn_folder_back.setIcon(QIcon(pm_back))
        else: 
            self.btn_folder_back.setText("←")
        self.btn_folder_back.clicked.connect(self._back_to_folder_view)
        self.btn_folder_back.hide()
        header_layout.addWidget(self.btn_folder_back)
        header_layout.addStretch()
        bg_layout.addLayout(header_layout)

        self.btn_pin = QPushButton(self) 
        self.btn_pin.setFixedSize(30, 30)
        self.btn_pin.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_custom_tooltip(self.btn_pin, "窗口置顶") 
        self.btn_pin.setStyleSheet(common_style)
        self.btn_pin.clicked.connect(self._toggle_pin)

        self.btn_sort = QPushButton(self) 
        self.btn_sort.setFixedSize(30, 30)
        self.btn_sort.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_custom_tooltip(self.btn_sort, "按重要性排序") 
        self.btn_sort.setStyleSheet(common_style)
        self.btn_sort.clicked.connect(self._sort_by_priority)

        self.btn_add = QPushButton(self) 
        self.btn_add.setFixedSize(30, 30)
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_custom_tooltip(self.btn_add, "添加待办") 
        self.btn_add.setStyleSheet(common_style)
        self.btn_add.clicked.connect(self._on_add_clicked)

        self.btn_close = QPushButton(self) 
        self.btn_close.setFixedSize(30, 30) 
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_custom_tooltip(self.btn_close, "关闭看板") 
        self.btn_close.setStyleSheet("QPushButton { background: transparent; border: none; border-top-right-radius: 12px; } QPushButton:hover { background: #ff4d4f; }")
        self.btn_close.clicked.connect(self.close)
        
        self._update_nav_icons()

        # ==========================================
        # 堆栈管理器：负责在空状态、便签、文件夹之间切换
        # ==========================================
        self.view_stack = QStackedWidget()
        self.view_stack.setStyleSheet("background: transparent; border: none;")

        self.manage_list_view = ManageListView(self)
        self.manage_list_view.back_requested.connect(self.back_from_manage_list)
        self.view_stack.addWidget(self.manage_list_view)
        
        self.stick_view = StickViewContainer(self)
        self.view_stack.addWidget(self.stick_view)
        
        self.folder_view = FolderViewContainer(self)
        self.folder_view.folder_opened.connect(self._open_folder_view)
        self.folder_view.add_folder_requested.connect(self._on_add_folder_card_clicked)
        self.folder_view.delete_folder_requested.connect(self._handle_folder_delete)
        self.view_stack.addWidget(self.folder_view)
    
        # 空状态占位
        self.empty_placeholder = QLabel("当前视图：待办看板\n\n当前没有任何未完成的待办事项！")
        self.empty_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_placeholder.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 13px; border: 2px dashed rgba(255, 255, 255, 0.2); border-radius: 8px; background: rgba(255, 255, 255, 0.05); font-family: 'Microsoft YaHei';")
        self.view_stack.addWidget(self.empty_placeholder)

        self.inline_add_view = InlineAddTodoView(self)
        self.view_stack.addWidget(self.inline_add_view)
        self.inline_add_view.saved.connect(self._on_inline_add_saved)
        self.inline_add_view.canceled.connect(self._on_inline_add_canceled)

        self.page_list = ListPickerView()
        if hasattr(self.page_list, 'btn_close'): self.page_list.btn_close.hide()
        if hasattr(self.page_list, 'btn_suspend'): self.page_list.btn_suspend.hide()

        if hasattr(self.page_list, 'header_container'): self.page_list.header_container.hide()
        if hasattr(self.page_list, 'footer_container'): self.page_list.footer_container.layout().setContentsMargins(25, 0, 25, 5)
        if hasattr(self.page_list, 'scroll_area'): self.page_list.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.view_stack.addWidget(self.page_list)
        
        self.inline_add_view.req_open_list_picker.connect(self.go_to_list_picker)
        self.page_list.back_requested.connect(self.back_from_list_picker)
        self.page_list.confirm_requested.connect(self.on_list_confirmed)
        self.view_stack.currentChanged.connect(self._schedule_body_repaint)
        self.view_stack.setCurrentWidget(self.stick_view)
        bg_layout.addWidget(self.view_stack, 1)

    def go_to_list_picker(self, current_category_id, current_type):
        """进入添加模式的清单选择"""
        self.list_picker_mode = 'add'
        self.title_label.setText("选择清单")
        self.page_list.load_data(current_category_id, list_type=current_type)
        self.view_stack.setCurrentWidget(self.page_list)
        
        # 隐藏顶部可能引起歧义的工具栏按钮
        self.views_frame.hide()
        if hasattr(self, 'btn_folder_back'): self.btn_folder_back.hide()
        self.btn_add.hide()
        if hasattr(self, 'btn_sort'): self.btn_sort.hide()
        self._update_button_positions()

    def go_to_list_picker_for_edit(self, schedule_data):
        self.list_picker_mode = 'edit'
        self.editing_schedule = schedule_data
        
        display_title = schedule_data.title if len(schedule_data.title) <= 8 else schedule_data.title[:7] + "..."
        self.title_label.setText(f"修改【{display_title}】清单") 
        
        self.page_list.load_data(schedule_data.category_id, list_type=schedule_data.item_type)
        
        self.view_stack.setCurrentWidget(self.page_list)
        self.views_frame.hide()
        if hasattr(self, 'btn_folder_back'): self.btn_folder_back.hide()
        self.btn_add.hide()
        if hasattr(self, 'btn_sort'): self.btn_sort.hide()
        self._update_button_positions()

    def back_from_list_picker(self):
        """通用返回逻辑"""
        in_folder = getattr(self, 'current_folder_id', "NOT_IN_FOLDER") != "NOT_IN_FOLDER"
        
        # 1. 动态恢复标题
        self.title_label.setText(self.current_folder_name if in_folder else "待办看板")
        
        picker_mode = getattr(self, 'list_picker_mode', 'add')
        if picker_mode in ['edit', 'manage']:
            # 2. 动态恢复顶部按钮状态
            if in_folder:
                if hasattr(self, 'btn_folder_back'): self.btn_folder_back.show()
                self.views_frame.hide()
            else:
                if hasattr(self, 'btn_folder_back'): self.btn_folder_back.hide()
                self.views_frame.show()
                
            self.btn_add.show()
            if (self.view_mode == 'stick' or in_folder) and hasattr(self, 'btn_sort'):
                self.btn_sort.show()

            # 3. 动态恢复下方的堆栈视图
            if in_folder or self.view_mode == 'stick':
                if not self.current_todos:
                    self.view_stack.setCurrentWidget(self.empty_placeholder)
                else:
                    self.view_stack.setCurrentWidget(self.stick_view)
            elif self.view_mode == 'folder':
                self.view_stack.setCurrentWidget(self.folder_view)
            else:
                self.view_stack.setCurrentWidget(self.empty_placeholder)
                
        else:
            # 如果是添加模式，退回内联添加界面（此时不恢复顶部工具按钮）
            self.view_stack.setCurrentWidget(self.inline_add_view)
        
        self._update_button_positions()

    def on_list_confirmed(self, category_id):
        # 提取当前模式
        mode = getattr(self, 'list_picker_mode', 'add')
        
        # 1. 修改模式逻辑
        if mode == 'edit' and hasattr(self, 'editing_schedule') and self.editing_schedule:
            def _do_update(update_future):
                from datetime import datetime
                now = datetime.now()
                new_data = {'category_id': category_id, 'created_at': now}
                db_manager.update_schedule_with_repeat(self.editing_schedule.id, new_data, update_future)
                
                self.editing_schedule.category_id = category_id
                self.editing_schedule.created_at = now
                if not update_future: self.editing_schedule.group_id = None
                
                self._last_signature = None
                self.refresh_data()
                self.notify_main_window_refresh()
                
                parent_win = self.parent()  
                if parent_win and hasattr(parent_win, 'page_dashboard'):
                    for p in parent_win.page_dashboard.open_popups:
                        if p.data.id == self.editing_schedule.id:
                            p.data.category_id = category_id 
                            p.data.created_at = now
                            if not update_future: p.data.group_id = None
                            
                            if hasattr(p, 'refresh_list_display'): p.refresh_list_display()
                            if hasattr(p, 'refresh_created_display'): p.refresh_created_display()
                            
                self.back_from_list_picker()
                
            self._check_repeat_and_execute(self.editing_schedule, _do_update)

        # 2. 添加模式逻辑
        else:
            cat_name = "未选择清单"
            if category_id is not None:
                cat = db_manager.get_category(category_id)
                cat_name = cat.name if cat else "未知"
            self.inline_add_view._set_category(category_id, cat_name)
            self.back_from_list_picker()


    def _check_repeat_and_execute(self, schedule_data, update_callback):
        """复用的系列修改拦截器"""
        from PyQt6.QtWidgets import QMessageBox
        rule = getattr(schedule_data, 'repeat_rule', '')
        if rule and str(rule).strip() not in ["", "无", "none", "不重复"]:
            msg = QMessageBox(self)
            msg.setWindowTitle("修改重复日程")
            msg.setText(f"当前日程包含【{rule}】的重复规则。\n您的修改将会应用到该系列的所有日程。")
            msg.setStyleSheet("""
                QMessageBox { background-color: white; }
                QPushButton { padding: 6px 15px; border-radius: 4px; background-color: #f0f0f0; font-family: 'Microsoft YaHei'; }
                QPushButton:hover { background-color: #e0e0e0; }
            """)
            btn_all = msg.addButton("修改所有", QMessageBox.ButtonRole.AcceptRole)
            btn_single = msg.addButton("仅修改本次", QMessageBox.ButtonRole.ActionRole)
            btn_cancel = msg.addButton("取消", QMessageBox.ButtonRole.RejectRole)
            msg.exec()
            
            if msg.clickedButton() == btn_all:
                update_callback(True)
            elif msg.clickedButton() == btn_single:
                update_callback(False)
            else:
                pass 
        else:
            update_callback(False)

    # 双击进入文件夹视图
    def _open_folder_view(self, category_id, category_name):
        self.current_folder_id = category_id
        self.current_folder_name = category_name

        self.title_label.setText(category_name)
        self.views_frame.hide()
        self.btn_folder_back.show()

        self.btn_add.show()

        self._update_nav_icons()
        self._last_signature = None 
        self.refresh_data()

    # 返回上一级
    def _back_to_folder_view(self):
        self.current_folder_id = "NOT_IN_FOLDER"
        self.current_folder_name = ""

        self.title_label.setText("待办看板")
        self.btn_folder_back.hide()
        self.views_frame.show()

        self.view_mode = 'folder'
        self._update_nav_icons()
        self._last_signature = None
        self.refresh_data()

    def _update_nav_icons(self):
        c_white = QColor(255, 255, 255, 255)
        c_grey = QColor(255, 255, 255, 150)

        close_icon = self._get_icon("close.png", c_white, 12)
        if not close_icon.isNull(): 
            self.btn_close.setIcon(QIcon(close_icon))
            self.btn_close.setText("") 
        else: 
            self.btn_close.setText("✕")

        pin_color = c_white if self.is_pinned else c_grey
        pm_pin = self._get_icon("pin.svg", pin_color, 16)
        if not pm_pin.isNull(): self.btn_pin.setIcon(QIcon(pm_pin))

        pm_sort = self._get_icon("sort.svg", c_white, 16)
        if not pm_sort.isNull(): self.btn_sort.setIcon(QIcon(pm_sort))
        show_sort = (self.view_mode == 'stick') or (getattr(self, 'current_folder_id', "NOT_IN_FOLDER") != "NOT_IN_FOLDER")
        self.btn_sort.setVisible(show_sort)

        pm_add = self._get_icon("add.svg", c_white, 16)
        if not pm_add.isNull(): self.btn_add.setIcon(QIcon(pm_add))

        stick_color = c_white if self.view_mode == 'stick' else c_grey
        folder_color = c_white if self.view_mode == 'folder' else c_grey
        
        pm_stick = self._get_icon("stick_view.svg", stick_color, 16)
        if not pm_stick.isNull(): self.btn_stick.setIcon(QIcon(pm_stick))
        
        pm_folder = self._get_icon("folder_view.svg", folder_color, 16)
        if not pm_folder.isNull(): self.btn_folder.setIcon(QIcon(pm_folder))

        self._update_button_positions()

    def _switch_view(self, mode):
        self.view_mode = mode
        self._update_nav_icons()
        self.refresh_data()

    def _toggle_pin(self):
        self.set_pinned(not self.is_pinned)

    def set_pinned(self, enabled):
        self.is_pinned = bool(enabled)
        set_window_pin_state(self, self.is_pinned)
        self._update_nav_icons()

    def _sort_by_priority(self):
        """一键按重要性(高->低)及创建时间(早->晚)重新排序"""
        import datetime
        in_folder = getattr(self, 'current_folder_id', "NOT_IN_FOLDER") != "NOT_IN_FOLDER"
        if (self.view_mode != 'stick' and not in_folder) or not hasattr(self.stick_view, 'cards'):
            return

        # 1. 提取当前所有显示的便签数据
        todos = [card.data for card in self.stick_view.cards]
        if not todos:
            return

        def get_created_timestamp(item):
            val = getattr(item, 'created_at', None)
            if isinstance(val, datetime.datetime):
                return val.timestamp()
            return 0.0

        # 2. 排序逻辑：
        # priority (2:高, 1:中, 0:低)。从高到低排，所以用 -priority (升序变降序)
        # created_at 由早到晚排，直接用时间戳升序
        todos.sort(key=lambda x: (-int(getattr(x, 'priority', 0)), get_created_timestamp(x)))

        # 3. 重新分配 sort_order（因为看板渲染是按 sort_order 值越大越靠前显示的）
        total = len(todos)
        for i, t in enumerate(todos):
            new_order = float((total - i) * 100.0)
            t.sort_order = new_order
            # 更新到数据库
            db_manager.update_schedule_fields(t.id, sort_order=new_order)

        # 4. 清除签名缓存，强制刷新本地看板
        self._last_signature = None
        self.refresh_data()

        self.notify_main_window_refresh()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_button_positions()

    def _schedule_body_repaint(self, *_):
        QTimer.singleShot(0, self.update)

    def _update_button_positions(self):
        """动态计算右上角按钮位置，跳过隐藏的按钮防止留空隙"""
        offset = 40  # 初始右边距
        
        if hasattr(self, 'btn_close'):
            self.btn_close.move(self.width() - offset, 10)
            self.btn_close.raise_()
            offset += 30
            
        if hasattr(self, 'btn_pin'):
            self.btn_pin.move(self.width() - offset, 10)
            self.btn_pin.raise_()
            offset += 30
            
        # 只有排序键处于显示状态，才分配空间
        if hasattr(self, 'btn_sort') and not self.btn_sort.isHidden():
            self.btn_sort.move(self.width() - offset, 10)
            self.btn_sort.raise_()
            offset += 30
            
        if hasattr(self, 'btn_add'):
            self.btn_add.move(self.width() - offset, 10)
            self.btn_add.raise_()
            offset += 30

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        rect = QRectF(10, 10, self.width() - 20, self.height() - 20)
        path.addRoundedRect(rect, 12.0, 12.0)
        
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(AppConfig.COLOR_GRADIENT_START))
        gradient.setColorAt(1.0, QColor(AppConfig.COLOR_GRADIENT_END))
        
        painter.fillPath(path, QBrush(gradient))

        if hasattr(self, 'view_stack'):
            body_top = self.view_stack.mapTo(self, QPoint(0, 0)).y()
            body_top = max(rect.top(), min(float(body_top), rect.bottom()))
            body_rect = QRectF(
                rect.left(),
                body_top,
                rect.width(),
                rect.bottom() - body_top + 1,
            )
            painter.save()
            painter.setClipPath(path)
            painter.fillRect(body_rect, QColor(255, 255, 255, 179))
            painter.restore()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(0, 0, 0, 26), 1))
        painter.drawPath(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()

    def _show_detail_popup(self, schedule_data):
        # 使用 self.parent() 获取当初创建它时传入的 MainWindow
        main_win = self.parent()
        
        if main_win and hasattr(main_win, 'page_dashboard'):
            # 计算出“待办看板”自身的右侧屏幕绝对坐标
            board_pos = self.mapToGlobal(QPoint(self.width() + 10, 0))
            
            # 呼叫主面板的弹窗机制 
            main_win.page_dashboard._show_detail_popup(schedule_data, source_view="todo_board")
            
            # 遍历打开的弹窗，把对应这个日程的弹窗强行拽到看板旁边
            for p in main_win.page_dashboard.open_popups:
                if p.data.id == schedule_data.id and p.isVisible():
                    p.move(board_pos)
                    p.raise_()
                    p.activateWindow()
                    break

    def _handle_status_change(self, schedule_id, new_status):
        if db_manager.update_schedule_status(schedule_id, new_status):
            self._last_signature = None
            self.refresh_data()
            self.notify_main_window_refresh()

    def _handle_pin_change(self, schedule_id, current_pin_status):
        if db_manager.toggle_pin_status(schedule_id, current_pin_status):
            self._last_signature = None
            self.refresh_data()
            self.notify_main_window_refresh()

    def _handle_delete(self, schedule_id):
        if db_manager.delete_schedule(schedule_id):
            self._last_signature = None
            self.refresh_data()
            self.notify_main_window_refresh()

    def notify_main_window_refresh(self):
        parent = self.parent()
        if parent:
            # 1. 强制要求主窗口的“待办视图”立刻刷新
            if hasattr(parent, 'page_todo'): 
                parent.page_todo.refresh_data()
            # 2. 触发全局刷新信号，让“主面板”和“周视图”也同步
            if hasattr(parent, 'page_dashboard'): 
                parent.page_dashboard.req_refresh_all.emit()

    def _on_add_clicked(self):
        """待办看板的添加入口"""
        self.inline_add_view.reset()
        if getattr(self, 'current_folder_id', "NOT_IN_FOLDER") != "NOT_IN_FOLDER":
            self.inline_add_view._set_category(self.current_folder_id, self.current_folder_name)
        self.view_stack.setCurrentWidget(self.inline_add_view)
        
        # 进入添加模式时，隐藏顶栏容易引起误触的按钮
        self.views_frame.hide()
        if hasattr(self, 'btn_folder_back'): self.btn_folder_back.hide()
        self.btn_add.hide()
        if hasattr(self, 'btn_sort'):
            self.btn_sort.hide()
        self._update_button_positions()

    def _on_inline_add_canceled(self):
        # 恢复顶栏添加按钮显示
        self.btn_add.show()
        
        # 动态恢复状态：判断当前是否在文件夹内
        if getattr(self, 'current_folder_id', "NOT_IN_FOLDER") != "NOT_IN_FOLDER":
            # 如果在文件夹内：显示返回键，隐藏视图切换键
            if hasattr(self, 'btn_folder_back'): self.btn_folder_back.show()
            self.views_frame.hide()
            if hasattr(self, 'btn_sort'): self.btn_sort.show()
            
            # 文件夹内固定使用便签视图来展示内容
            if not self.current_todos:
                self.view_stack.setCurrentWidget(self.empty_placeholder)
            else:
                self.view_stack.setCurrentWidget(self.stick_view)
        else:
            # 如果在外部主看板：显示视图切换键，隐藏返回键
            self.views_frame.show()
            if hasattr(self, 'btn_folder_back'): self.btn_folder_back.hide()
            if self.view_mode == 'stick' and hasattr(self, 'btn_sort'):
                self.btn_sort.show()
            
            # 原本的堆栈恢复逻辑
            if self.view_mode == 'stick':
                if not self.current_todos:
                    self.view_stack.setCurrentWidget(self.empty_placeholder)
                else:
                    self.view_stack.setCurrentWidget(self.stick_view)
            elif self.view_mode == 'folder':
                self.view_stack.setCurrentWidget(self.folder_view)
                
        # 清除签名，触发一次数据对齐
        self._last_signature = None
        self.refresh_data()
        self._update_button_positions()

    def _on_inline_add_saved(self):
        self.show_toast("✅ 添加待办成功")
        self._on_inline_add_canceled() # 恢复 UI 显示并回到看板
        self.notify_main_window_refresh() # 通知主窗口同步刷新

    def show_toast(self, message):
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtCore import Qt, QTimer
        
        # 如果已经有提示在显示，先关掉
        if hasattr(self, 'toast_label') and self.toast_label.isVisible():
            self.toast_label.close()
            
        self.toast_label = QLabel(message, self)
        self.toast_label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.75);
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            font-family: 'Microsoft YaHei';
            font-size: 14px;
            font-weight: bold;
        """)
        self.toast_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.toast_label.adjustSize()
        self.toast_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) 
        
        # 让弹窗完美居中在看板窗口
        x = (self.width() - self.toast_label.width()) // 2
        y = (self.height() - self.toast_label.height()) // 2
        self.toast_label.move(x, y)
        self.toast_label.show()
        
        # 定时 1.5 秒后自动销毁关闭
        QTimer.singleShot(1500, self.toast_label.close)

    def _on_add_folder_card_clicked(self):
        """进入纯粹的清单管理界面"""
        self.title_label.setText("管理清单")
        
        # 使用全新的管理视图加载数据并切换
        self.manage_list_view.load_data()
        self.view_stack.setCurrentWidget(self.manage_list_view)
        
        # 隐藏顶部不需要的按钮
        self.views_frame.hide()
        if hasattr(self, 'btn_folder_back'): self.btn_folder_back.hide()
        self.btn_add.hide()
        if hasattr(self, 'btn_sort'): self.btn_sort.hide()
        self._update_button_positions()
        
        # 自动展开输入框体验更好
        if not self.manage_list_view.input_container.isVisible():
            self.manage_list_view._toggle_input()

    def back_from_manage_list(self):
        """从管理界面退回文件夹视图"""
        self.title_label.setText("待办看板")
        self.view_stack.setCurrentWidget(self.folder_view)
        
        self.views_frame.show()
        self.btn_add.show()
        if hasattr(self, 'btn_folder_back'): self.btn_folder_back.hide()
        
        self._update_button_positions()

    def _handle_folder_delete(self, cat_id, cat_name):
        from PyQt6.QtWidgets import QMessageBox
        
        # 查询该文件夹的状态 (active=有未完成待办, historical=有已完成/过期待办, empty=完全空)
        status = db_manager.check_category_status(cat_id)
        action = CategoryPolicyService.choose_delete_action(status)
        
        if action == CategoryDeleteAction.BLOCK:
            # 非灰色（有待办）拦截
            self.show_toast("🚫 该文件夹存在有效待办，无法直接删除！")
        elif action == CategoryDeleteAction.SOFT_DELETE:
            # 包含历史记录
            reply = QMessageBox.question(
                self, '确认删除', 
                f"文件夹【{cat_name}】包含历史待办记录。\n是否继续删除？", 
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                db_manager.soft_delete_category(cat_id)
                self.show_toast(f"✅ 已删除文件夹【{cat_name}】")
                self._last_signature = None
                self.refresh_data()
                self.notify_main_window_refresh()
        else:
            # 完全空的灰色文件夹，直接物理抹除
            db_manager.hard_delete_category(cat_id)
            self.show_toast(f"✅ 已删除空文件夹【{cat_name}】")
            self._last_signature = None
            self.refresh_data()
            self.notify_main_window_refresh()

