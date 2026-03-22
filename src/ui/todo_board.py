# src/ui/todo_board.py
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QPushButton, QScrollArea, QGridLayout, QStackedWidget)
from PyQt6.QtCore import Qt, QRectF, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QPainter, QPainterPath, QBrush, QLinearGradient, QColor, QPixmap, QImage
from PyQt6.QtSvg import QSvgRenderer

from ..config import AppConfig
from ..data.database import db_manager # 引入真实数据库

# ==========================================
# 通用工具：SVG 高清渲染与染色 
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

        # 开启自定义右键菜单支持
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # 使用方法动态应用样式（区分置顶和普通状态）
        #self._apply_state_style()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 8) 
        main_layout.setSpacing(6)
        
        # 无边框贴纸样式
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.15);
                border: none;
                border-radius: 6px;
            }
            QFrame:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
        """)
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

        header_layout.addWidget(icon_label)

        self.title_label = QLabel(self.data.title)
        self.title_label.setStyleSheet("color: white; font-weight: bold; font-size: 13px; font-family: 'Microsoft YaHei'; border: none; background: transparent;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.title_label.setWordWrap(True)
        
        header_layout.addWidget(self.title_label, 1)
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
        
        # 如果置顶，背景更亮，边框发白光
        bg_color = "rgba(255, 255, 255, 0.25)" if is_pinned else "rgba(255, 255, 255, 0.15)"
        border = "1px solid rgba(255, 255, 255, 0.8)" if is_pinned else "none"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: {border};
                border-radius: 6px;
            }}
            QFrame:hover {{
                background-color: rgba(255, 255, 255, 0.3);
            }}
        """)
        if hasattr(self, 'title_label'):
            # 置顶使用金色(#FFD700)，未置顶保持纯白
            title_color = "#FFD700" if is_pinned else "white" 
            self.title_label.setStyleSheet(f"""
                color: {title_color}; 
                font-weight: bold; 
                font-size: 13px; 
                font-family: 'Microsoft YaHei'; 
                border: none; 
                background: transparent;
            """)

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
                
            self.setStyleSheet("background: transparent; border: 2px dashed rgba(255, 255, 255, 0.4);")
            
            drag.exec(Qt.DropAction.MoveAction)
            
            # 拖拽结束：恢复原样
            self.title_label.show()
            if hasattr(self, 'lbl_category'): 
                self.lbl_category.show() # 恢复右下角的清单文字
                
            self.setStyleSheet("background-color: rgba(255, 255, 255, 0.15); border: none;")
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

class StickViewContainer(QScrollArea):
    req_status = pyqtSignal(int, int)
    req_pin = pyqtSignal(int, bool)
    req_delete = pyqtSignal(int)
    req_show_detail = pyqtSignal(object)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
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
        self.grid_layout.setContentsMargins(0, 0, 5, 0)
        self.grid_layout.setSpacing(8) 
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setWidget(self.scroll_content)
        self.cards = []

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

        if item_count == 0: return

        # 3. 动态列数
        if item_count <= 3: cols = 1
        elif item_count <= 6: cols = 2
        else: cols = 3

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
        target_h = int((vh - 16) / 3)-1
        target_h = max(target_h, 50)
        for card in self.cards:
            card.setFixedHeight(target_h)

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
            parent_window._last_signature = "-".join([f"{t.id}_{getattr(t, 'sort_order', 0.0)}" for t in todos])
            parent_window.notify_main_window_refresh()
            
# ==========================================
# 文件夹卡片组件
# ==========================================
class FolderCard(QFrame):
    clicked = pyqtSignal(object) # 传出分类 ID（未分类传 None）

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
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8) # 稍微收紧一点图标和文字的间距

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(45, 45)
        
        icon_color = "#CCCCCC" if self.is_empty else "#FFFFFF"
        pixmap = get_colored_icon("card_folder.svg", icon_color, 45)
        
        if not pixmap.isNull():
            self.icon_label.setPixmap(pixmap)
        else:
            self.icon_label.setText("📁")
            self.icon_label.setStyleSheet("font-size: 40px; background: transparent; border: none;")

        self.name_label = QLabel(self.category_name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 字体变小两号 (14px -> 12px)
        text_color = "rgba(255, 255, 255, 0.6)" if self.is_empty else "white"
        self.name_label.setStyleSheet(f"color: {text_color}; font-weight: bold; font-size: 12px; font-family: 'Microsoft YaHei'; border: none; background: transparent;")

        layout.addWidget(self.icon_label, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.name_label, 0, Qt.AlignmentFlag.AlignHCenter)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.category_id)
            event.accept()

# ==========================================
# 文件夹视图 3x3 网格容器
# ==========================================
class FolderViewContainer(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { width: 6px; background: transparent; margin: 0px; }
            QScrollBar::handle:vertical { background: rgba(255, 255, 255, 0.3); border-radius: 3px; }
            QScrollBar::handle:vertical:hover { background: rgba(255, 255, 255, 0.5); }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.setViewportMargins(0, 0, 0, 0)
        
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setContentsMargins(0, 0, 5, 0)
        self.grid_layout.setSpacing(12) 
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setWidget(self.scroll_content)
        self.cards =[]

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
        
        # 3. 如果有未分类待办，首先生成“未分类待办”文件夹
        if uncategorized_count > 0:
            card = FolderCard(category_id=None, category_name="未分类待办", is_empty=False)
            self.grid_layout.addWidget(card, current_index // cols, current_index % cols)
            self.cards.append(card)
            current_index += 1

        # 4. 生成数据库里所有的清单文件夹
        for data in folder_data_list:
            card = FolderCard(category_id=data['id'], category_name=data['name'], is_empty=data['is_empty'])
            self.grid_layout.addWidget(card, current_index // cols, current_index % cols)
            self.cards.append(card)
            current_index += 1

        self.update_card_heights()

    def update_card_heights(self):
        if not self.cards: return
        vh = self.viewport().height()
        # 计算高度，确保一屏刚好显示 3 行
        target_h = int((vh - 24) / 3) 
        target_h = max(target_h, 80)
        for card in self.cards:
            card.setFixedHeight(target_h)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_card_heights()

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
        self._setup_ui()
        
        self.stick_view.req_status.connect(self._handle_status_change)
        self.stick_view.req_pin.connect(self._handle_pin_change)
        self.stick_view.req_delete.connect(self._handle_delete)
        self.stick_view.req_show_detail.connect(self._show_detail_popup)

        # ==========================================
        # 零延迟信号驱动机制
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

    def refresh_data(self):
        if hasattr(self.stick_view, 'scroll_content'):
            if self.stick_view.scroll_content.current_drag_widget is not None:
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
                        if hasattr(pop, 'refresh_list_display'): pop.refresh_list_display()
                        if hasattr(pop, 'refresh_time_display'): pop.refresh_time_display()
                        if hasattr(pop, 'refresh_alarm_display'): pop.refresh_alarm_display()
                        if hasattr(pop, 'refresh_priority_display'): pop.refresh_priority_display()
                        if hasattr(pop, 'refresh_repeat_display'): pop.refresh_repeat_display()
                        break

        # 处理所有“活跃”的待办数据
        todos =[]
        active_cat_ids = set()
        uncategorized_count = 0

        for s in all_schedules:
            # 确保加上刚才的过滤隐藏逻辑
            if getattr(s, 'status', 0) == 2:
                continue
                
            is_todo = (getattr(s, 'item_type', '') == 'todo' or getattr(s, 'type', 0) == 1)
            is_active = (getattr(s, 'status', 0) == 0) 
            
            if is_todo and is_active:
                todos.append(s)
                # 记录所有含有待办的清单ID，并统计未分类的数量
                if getattr(s, 'category_id', None):
                    active_cat_ids.add(s.category_id)
                else:
                    uncategorized_count += 1
                
        def sort_key(item):
            rank_pin = 0 if getattr(item, 'is_pinned', False) else 1
            sort_val = -getattr(item, 'sort_order', 0.0) 
            return (rank_pin, sort_val)

        todos.sort(key=sort_key)
        self.current_todos = todos

        # 处理所有“清单(文件夹)”数据
        # 移除 list_type='todo' 的限制，获取所有清单，防止因为历史遗留导致读取不到
        todo_categories = db_manager.get_active_categories()
        folder_data =[]
        for cat in todo_categories:
            folder_data.append({
                'id': cat.id,
                'name': cat.name,
                'is_empty': cat.id not in active_cat_ids 
            })

        # 防闪烁：生成签名
        # 把 self.view_mode 加进签名里，这样切视图就一定会触发渲染
        current_signature = "-".join([f"{t.id}_{getattr(t, 'sort_order', 0)}" for t in todos])
        cat_signature = "-".join([str(c.id) for c in todo_categories])
        full_signature = f"{current_signature}|{cat_signature}|{self.view_mode}"

        if self._last_signature == full_signature:
            return
        self._last_signature = full_signature

        # 给两个视图同时下发数据渲染指令
        self.stick_view.load_data(todos)
        self.folder_view.load_data(folder_data, uncategorized_count)
        
        # 智能显示堆栈判断
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
        bg_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.addWidget(self.bg_frame)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 70, 10) 

        title_label = QLabel("待办看板")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; border: none; background: transparent; font-family: 'Microsoft YaHei';")
        header_layout.addWidget(title_label)

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
        
        self.stick_view = StickViewContainer(self)
        self.view_stack.addWidget(self.stick_view)
        
        self.folder_view = FolderViewContainer(self)
        self.view_stack.addWidget(self.folder_view)
    
        # 空状态占位
        self.empty_placeholder = QLabel("当前视图：待办看板\n\n当前没有任何未完成的待办事项！")
        self.empty_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_placeholder.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 13px; border: 2px dashed rgba(255, 255, 255, 0.2); border-radius: 8px; background: rgba(255, 255, 255, 0.05); font-family: 'Microsoft YaHei';")
        self.view_stack.addWidget(self.empty_placeholder)

        bg_layout.addWidget(self.view_stack, 1)

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
        self.btn_sort.setVisible(self.view_mode == 'stick')

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
        self.is_pinned = not self.is_pinned
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, self.is_pinned)
        self._update_nav_icons()
        self.show() 

    def _sort_by_priority(self):
        """一键按重要性(高->低)及创建时间(早->晚)重新排序"""
        import datetime
        if self.view_mode != 'stick' or not hasattr(self.stick_view, 'cards'):
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

        # 5. 🟢 替换原来的 parent 通知逻辑
        self.notify_main_window_refresh()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_button_positions()

    def _update_button_positions(self):
        """🟢 动态计算右上角按钮位置，跳过隐藏的按钮防止留空隙"""
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
        if hasattr(self, 'btn_sort') and self.view_mode == 'stick':
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
        """待办看板的智能添加入口 (预留给后续内联添加)"""
        if self.view_mode == 'stick':
            print(">> 准备在看板内联添加：新建待办便签")
            # TODO: 实现生成一个空白虚线便签框，直接输入文字
            
        elif self.view_mode == 'folder':
            print(">> 准备在看板内联添加：新建清单文件夹")
            # TODO: 实现生成一个带输入框的空白文件夹图标