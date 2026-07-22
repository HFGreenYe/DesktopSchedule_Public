# src/ui/todo.py
import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QTimer, QMimeData
from PyQt6.QtGui import QDrag
from ..data.database import db_manager
from ..services.schedule_query_service import (
    ScheduleQueryOptions,
    ScheduleQueryService,
)
from ..services.schedule_sort_service import ScheduleSortService
from ..utils.schedule_sort_preferences import (
    get_schedule_sort_options,
    set_schedule_sort_options,
)
from .schedule_detail_pop import ScheduleDetailPop

# 复用主界面的组件
from .dashboard import DraggableWidget, ViewSelectorCard, AdaptiveLabel
from .common.card_step_scroll_area import CardStepScrollArea


class TodoCard(QFrame):
    req_delete = pyqtSignal(int)
    req_refresh = pyqtSignal()
    req_status = pyqtSignal(int, int)
    req_show_detail = pyqtSignal(object) 

    def __init__(self, schedule_data, parent=None):
        super().__init__(parent)
        self.data = schedule_data
        self.setFixedHeight(60) 
        self.setCursor(Qt.CursorShape.PointingHandCursor) 
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        self.is_completed = (getattr(self.data, 'status', 0) == 1)

        self._setup_ui()
        self._apply_state_style() 

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._click_pos = event.pos()
            event.accept() 
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not hasattr(self, '_click_pos'):
            return
        if (event.pos() - self._click_pos).manhattanLength() > 10:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(str(self.data.id))
            drag.setMimeData(mime_data)
            
            # 实心抓取图片，不搞透明！
            pixmap = self.grab() 
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())
            
            
            container = self.parentWidget()
            if hasattr(container, 'current_drag_widget'):
                container.current_drag_widget = self
                
            # 把自己变成一个“空洞占位符”，留出缝隙
            original_style = self.styleSheet()
            self.setStyleSheet("background: transparent; border: 2px dashed rgba(255, 255, 255, 0.4); border-radius: 8px;")
            self.lbl_title.hide()
            self.priority_dot.hide()
            if hasattr(self, 'lbl_category_tag'): self.lbl_category_tag.hide()
            
            # 开始阻塞执行拖拽
            drag.exec(Qt.DropAction.MoveAction)
            
            # 拖拽结束
            self.setStyleSheet(original_style)
            self.lbl_title.show()
            self.priority_dot.show()
            if hasattr(self, 'lbl_category_tag'): self.lbl_category_tag.show()
                
            if hasattr(container, 'current_drag_widget'):
                container.current_drag_widget = None
                
            if hasattr(self, '_click_pos'): 
                del self._click_pos
            event.accept() 
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and hasattr(self, '_click_pos'):
            if (event.pos() - self._click_pos).manhattanLength() < 5:
                self.req_show_detail.emit(self.data)
            del self._click_pos 
            event.accept() 
        else:
            super().mouseReleaseEvent(event)

    def _apply_state_style(self):
        bg_color = "background-color: rgba(255, 255, 255, 0.10);"
        border_style = "border: 1px solid rgba(255, 255, 255, 0.4);"
        title_color = "white"
        strike_out = False
        dot_opacity = 1.0

        if self.is_completed:
            bg_color = "background-color: rgba(255, 255, 255, 0.10);"
            if getattr(self.data, 'is_pinned', False):
                border_style = "border: 1px solid white;" # 置顶且完成：保留白边
            else:
                border_style = "border: 1px solid rgba(255, 255, 255, 0.4);"
            title_color = "rgba(255, 255, 255, 0.5)"
            strike_out = True
            dot_opacity = 1.0 
        elif getattr(self.data, 'is_pinned', False):
            bg_color = "background-color: rgba(255, 255, 255, 0.2);"
            border_style = "border: 1px solid white;"

        self.setStyleSheet(f"""
            TodoCard {{
                {bg_color}
                border-radius: 8px;
                {border_style}
            }}
            TodoCard:hover {{
                background-color: rgba(255, 255, 255, 0.15);
            }}
            QLabel {{
                background-color: transparent;
                color: {title_color};
                font-family: 'Microsoft YaHei';
                border: none;
            }}
        """)
        
        self.lbl_title.setStrikeOut(strike_out)
        effect = self.priority_dot.graphicsEffect()
        if not effect: 
             from PyQt6.QtWidgets import QGraphicsOpacityEffect
             op = QGraphicsOpacityEffect(self.priority_dot)
             op.setOpacity(dot_opacity)
             self.priority_dot.setGraphicsEffect(op)
        else:
             effect.setOpacity(dot_opacity)

    def _show_context_menu(self, pos):
        from .components import ScheduleContextMenu
        menu = ScheduleContextMenu(self.data, self)
        menu.setup_actions(
            status_callback=lambda status: self.req_status.emit(self.data.id, status),
            pin_callback=lambda is_pinned: self._handle_pin_action(),
            delete_callback=self._handle_delete_action
        )
        menu.exec(self.mapToGlobal(pos))

    def _handle_pin_action(self):
        if db_manager.toggle_pin_status(self.data.id, getattr(self.data, 'is_pinned', False)):
            self.req_refresh.emit()

    def _handle_delete_action(self):
        if db_manager.delete_schedule(self.data.id):
            self.req_delete.emit(self.data.id)

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 0, 15, 0)
        main_layout.setSpacing(12) 

        self.priority_dot = QLabel()
        self.priority_dot.setFixedSize(10, 10)
        priority_val = getattr(self.data, 'priority', 0)
        p_color = {2: "#ff4d4f", 1: "#faad14", 0: "#52c41a"}.get(priority_val, "#52c41a")
        
        self.priority_dot.setStyleSheet(f"""
            background-color: {p_color};
            border-radius: 5px;
            border: 1px solid rgba(255,255,255,0.8);
        """)
        main_layout.addWidget(self.priority_dot)

        self.lbl_title = AdaptiveLabel(self.data.title, max_size=16, min_size=11)
        main_layout.addWidget(self.lbl_title, stretch=1)

        if getattr(self.data, 'category_id', None):
            category = db_manager.get_category(self.data.category_id)
            if category and not getattr(category, 'is_deleted', False):
                self.lbl_category_tag = QLabel(category.name)
                self.lbl_category_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.lbl_category_tag.setStyleSheet("""
                    background-color: transparent;
                    color: rgba(255, 255, 255, 0.6);
                    font-size: 11px;
                    font-family: 'Microsoft YaHei';
                    font-weight: bold;
                    padding-right: 5px;
                """)
                main_layout.addWidget(self.lbl_category_tag)

class TodoListContainer(QWidget):
    card_dropped = pyqtSignal(int, int) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True) 
        self.drag_pos = None
        self.current_drag_widget = None # 记录当前在天上飞的是谁

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.window().pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos:
            self.window().move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasText(): 
            event.accept()
            # 跨列认领逻辑
            # 只要是从别的地方（如其他天数的列）拖进来的卡片，当前列直接接收控制权
            source = event.source()
            if source and hasattr(source, 'data'):
                self.current_drag_widget = source
        else: 
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText() and self.current_drag_widget:
            # ==========================================
            # 边缘雷达，靠近顶部/底部自动滚动 ScrollArea
            # ==========================================
            viewport = self.parentWidget()
            if viewport:
                scroll_area = viewport.parentWidget()
                if hasattr(scroll_area, 'verticalScrollBar'):
                    v_bar = scroll_area.verticalScrollBar()
                    viewport_y = self.mapTo(viewport, event.position().toPoint()).y()
                    margin = 40 # 边缘 40 像素触发
                    if viewport_y < margin:
                        v_bar.setValue(v_bar.value() - 15) # 向上滑
                    elif viewport_y > viewport.height() - margin:
                        v_bar.setValue(v_bar.value() + 15) # 向下滑

            # ==========================================
            # 实时推挤补位，让占位虚线框在布局里实时穿梭
            # ==========================================
            pos_y = event.position().y()
            layout = self.layout()
            target_index = layout.count() - 1 
            
            for i in range(layout.count() - 1):
                item = layout.itemAt(i)
                if item.widget() and pos_y < item.widget().geometry().center().y():
                    target_index = i
                    break
                    
            # 严格保证虚线框不会飞出自己的分类区域（置顶、普通、已完成）
            dragged_pin = getattr(self.current_drag_widget.data, 'is_pinned', False)
            dragged_status = getattr(self.current_drag_widget.data, 'status', 0)
            
            found_group = False
            temp_min = 0
            temp_max = layout.count() - 2
            
            for i in range(layout.count() - 1):
                w = layout.itemAt(i).widget()
                if w and hasattr(w, 'data'):
                    w_pin = getattr(w.data, 'is_pinned', False)
                    w_status = getattr(w.data, 'status', 0)
                    if w_pin == dragged_pin and w_status == dragged_status:
                        if not found_group:
                            temp_min = i
                            found_group = True
                        temp_max = i
                        
            if found_group:
                target_index = max(temp_min, min(target_index, temp_max))
            else:
                # 如果被拖到了空列，或者跨列过来的新数据
                current_idx = layout.indexOf(self.current_drag_widget)
                if current_idx == -1: 
                    # 它是跨列来的，在当前列找不到它，把它插在最底部弹簧的前面
                    target_index = layout.count() - 1
                else:
                    # 保持原位
                    target_index = current_idx
                
            # 物理移动这个虚线框，其他卡片会自动挤开！
            if layout.indexOf(self.current_drag_widget) != target_index:
                layout.insertWidget(target_index, self.current_drag_widget)

            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText() and self.current_drag_widget:
            dragged_id = int(event.mimeData().text())
            target_index = self.layout().indexOf(self.current_drag_widget)
            
            # ==========================================
            # 致命崩溃的终极修复！
            # 延时 0 毫秒发送信号，等 QDrag 彻底死透了再去刷新整个界面
            # ==========================================
            QTimer.singleShot(50, lambda: self.card_dropped.emit(dragged_id, target_index))
            event.accept()

class TodoView(QWidget):
    req_refresh_all = pyqtSignal()
    req_change_view = pyqtSignal(str)
    req_edit_list = pyqtSignal(object, str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_pos = None 
        self.open_popups = []
        self.current_todos = []
        self._todo_source = []
        self._filter_options = ScheduleQueryOptions()
        self._search_options = None
        self._search_keyword = ""
        self._last_search_scope = "title"
        self._last_match_mode = "fuzzy"
        self._sort_options = get_schedule_sort_options("todo")
        
        self._setup_ui()
        
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000) 
        
        self.refresh_data()

    def _setup_ui(self):
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 20)
        layout.setSpacing(8)

        # 实例化视图选择器 
        self.view_selector = ViewSelectorCard(self)
        self.view_selector.set_current_view("todo")
        self.view_selector.hide()
        self.view_selector.view_selected.connect(self.req_change_view.emit)
        layout.addWidget(self.view_selector)

        self.lbl_empty = QLabel("您还没有待办记录，请点击添加")
        self.lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            font-size: 16px;
            font-family: 'Microsoft YaHei';
        """)
        layout.addWidget(self.lbl_empty)

        self.scroll_area = CardStepScrollArea(60, 8)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        
        self.scroll_content = TodoListContainer()
        self.scroll_content.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.scroll_content.setStyleSheet("background: transparent;")
        self.scroll_content.card_dropped.connect(self._handle_card_drop)
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8) 
        self.list_layout.addStretch() # 底部的弹簧，让少于满屏的卡片依然靠上对齐
        
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

    def toggle_view_selector(self):
        if self.view_selector.isVisible():
            self.view_selector.hide()
        else:
            self.view_selector.show()

    def _handle_card_drop(self, dragged_id, target_index):
        dragged_item = next((item for item in self.current_todos if item.id == dragged_id), None)
        if not dragged_item: return

        # 1. 假装它在这个大列表里被移到了新位置
        self.current_todos.remove(dragged_item)
        target_index = max(0, min(target_index, len(self.current_todos)))
        self.current_todos.insert(target_index, dragged_item)

        # 2. 身份识别：只抓取跟它完全同级（同置顶/同完成状态）的兄弟们
        target_pin = getattr(dragged_item, 'is_pinned', False)
        target_status = getattr(dragged_item, 'status', 0)

        group_items = [
            item for item in self.current_todos 
            if getattr(item, 'is_pinned', False) == target_pin and getattr(item, 'status', 0) == target_status
        ]

        if len(group_items) <= 1: return 

        # 3. 找到它在同类里真正落下的位置
        idx = group_items.index(dragged_item)

        # 4. 浮点权重计算 (越靠上权重越高)
        if idx == 0:
            next_order = getattr(group_items[1], 'sort_order', 0.0)
            new_order = next_order + 100.0 
        elif idx == len(group_items) - 1:
            prev_order = getattr(group_items[-2], 'sort_order', 0.0)
            new_order = prev_order - 100.0 
        else:
            prev_order = getattr(group_items[idx-1], 'sort_order', 0.0)
            next_order = getattr(group_items[idx+1], 'sort_order', 0.0)
            new_order = (prev_order + next_order) / 2.0 

        # 5. 更新本地和数据库
        dragged_item.sort_order = new_order
        db_manager.update_schedule_fields(dragged_item.id, sort_order=new_order)
        
        self.refresh_data()
        self.req_refresh_all.emit()

    def filter_options(self):
        return self._filter_options

    def search_options_for_panel(self):
        if self._search_options is not None:
            return self._search_options
        return self._filter_options.with_search_preferences(
            self._last_search_scope,
            self._last_match_mode,
        )

    def apply_filter_options(self, options):
        self._filter_options = options
        self._render_query_results()

    def apply_search_options(self, options):
        self._search_options = options
        self._last_search_scope = options.search_scope
        self._last_match_mode = options.match_mode
        if self._search_keyword:
            self._render_query_results()

    def set_search_keyword(self, keyword):
        normalized_keyword = str(keyword or "").strip()
        if normalized_keyword:
            if self._search_options is None:
                self._search_options = self.search_options_for_panel()
            self._search_keyword = normalized_keyword
        else:
            self._search_keyword = ""
            self._search_options = None
        self._render_query_results()

    def search_keyword(self):
        return self._search_keyword

    def has_active_filter(self):
        return self._filter_options.has_filter_constraints()

    def has_active_query(self):
        return bool(self._search_keyword) or self.has_active_filter()

    def sort_options(self):
        return self._sort_options

    def apply_sort_options(self, options):
        self._sort_options = options
        set_schedule_sort_options("todo", options)
        self._render_query_results()

    def has_active_sort(self):
        return not self._sort_options.is_default()

    def freeze_current_card_order(self):
        schedules = []
        for index in range(self.list_layout.count() - 1):
            item = self.list_layout.itemAt(index)
            widget = item.widget() if item is not None else None
            if isinstance(widget, TodoCard):
                schedules.append(widget.data)
        self._write_manual_sort_order(schedules)

    @staticmethod
    def _write_manual_sort_order(schedules):
        base_order = datetime.datetime.now().timestamp()
        for index, schedule in enumerate(schedules):
            schedule_id = getattr(schedule, "id", None)
            if schedule_id is None:
                continue
            new_order = base_order - index * 100.0
            schedule.sort_order = new_order
            db_manager.update_schedule_fields(schedule_id, sort_order=new_order)

    def _active_query_options(self):
        if self._search_keyword:
            return self._search_options or self.search_options_for_panel()
        return self._filter_options

    def _filtered_todos(self):
        return ScheduleQueryService.apply_options(
            self._todo_source,
            self._active_query_options(),
            self._search_keyword,
        )

    def _clear_todo_cards(self):
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _render_query_results(self):
        self._clear_todo_cards()
        visible_todos = ScheduleSortService.sort_for_todo_list(
            self._filtered_todos(),
            self._sort_options,
        )
        self.current_todos = visible_todos

        if not visible_todos:
            self.lbl_empty.setText(
                "没有符合条件的待办"
                if self.has_active_query()
                else "您还没有待办记录，请点击添加"
            )
            self.lbl_empty.show()
            self.scroll_area.hide()
            self.scroll_area.set_card_count(0)
            return

        self.lbl_empty.hide()
        self.scroll_area.show()
        for index, item in enumerate(visible_todos):
            card = TodoCard(item)
            card.req_delete.connect(self._remove_card_from_view)
            card.req_refresh.connect(self.refresh_data)
            card.req_refresh.connect(self.req_refresh_all.emit)
            card.req_status.connect(self._handle_status_change)
            card.req_show_detail.connect(self._show_detail_popup)
            self.list_layout.insertWidget(index, card)
        self.scroll_area.set_card_count(len(visible_todos))

    def contextMenuEvent(self, event):
        """待办页面空白区域右键菜单：收起/展开切换。"""
        # DefaultContextMenu 策略下，卡片上右键由卡片自己的菜单处理，
        # 这里只处理空白区域的右键。
        owner = self.window()
        if not hasattr(owner, 'is_day_view_active'):
            return
        from .common.action_context_menu import ActionContextMenu
        day_collapsed = (
            hasattr(owner, 'is_day_collapsed') and owner.is_day_collapsed()
        )
        menu = ActionContextMenu(
            self, show_day_collapse=True, day_collapsed=day_collapsed,
        )
        menu.action_requested.connect(
            lambda action: (
                owner.toggle_day_collapsed()
                if action == "toggle_day_collapse" else None
            )
        )
        menu.popup(event.globalPos())

    def refresh_data(self):
        if hasattr(self, 'scroll_content') and getattr(self.scroll_content, 'current_drag_widget', None) is not None:
            return

        # 获取所有数据并仅过滤出待办事项
        all_schedules = db_manager.get_all_schedules()

        # ==========================================
        # 将最新数据同步给所有正在悬浮显示的详情弹窗
        # ==========================================
        for pop in self.open_popups:
            if pop.isVisible():
                for s in all_schedules:
                    if s.id == pop.data.id:
                        pop.data = s  # 偷偷把弹窗里的老数据替换成最新数据库数据
                        # 强制呼叫弹窗的内置刷新方法更新 UI
                        if hasattr(pop, 'refresh_list_display'): pop.refresh_list_display()
                        if hasattr(pop, 'refresh_time_display'): pop.refresh_time_display()
                        if hasattr(pop, 'refresh_alarm_display'): pop.refresh_alarm_display()
                        if hasattr(pop, 'refresh_priority_display'): pop.refresh_priority_display()
                        if hasattr(pop, 'refresh_repeat_display'): pop.refresh_repeat_display()
                        break
        # ==========================================

        self._todo_source = [
            schedule
            for schedule in all_schedules
            if getattr(schedule, 'status', 0) != 2
            and ScheduleQueryService.is_todo(schedule)
        ]
        self._render_query_results()

    def _show_detail_popup(self, schedule_data, source_view="todo"):
        for p in self.open_popups:
            if p.data.id == schedule_data.id:
                p.show()
                p.raise_()
                p.activateWindow()
                return
        
        pop = ScheduleDetailPop(schedule_data, source_view=source_view)
        pop.schedule_updated.connect(self.refresh_data)
        pop.schedule_updated.connect(self.req_refresh_all.emit) 
        pop.req_edit_list.connect(lambda data, sv=source_view: self.req_edit_list.emit(data, sv))
        pop.popup_closed.connect(self._remove_detail_popup)
        self.open_popups.append(pop)
        
        pos = self.mapToGlobal(QPoint(self.width() + 10, 0))
        pop.move(pos)
        pop.show()

    def _remove_detail_popup(self, popup):
        self.open_popups = [p for p in self.open_popups if p is not popup]

    def restore_detail_popups(self):
        for popup in tuple(self.open_popups):
            popup_pos = popup.pos()
            popup.hide()
            popup.show()
            popup.move(popup_pos)
            popup.raise_()

    def _remove_card_from_view(self, schedule_id):
        sender_card = self.sender()
        if sender_card:
            self.list_layout.removeWidget(sender_card)
            sender_card.deleteLater()
            remaining = sum(
                1 for i in range(self.list_layout.count())
                if isinstance(self.list_layout.itemAt(i).widget(), TodoCard)
            )
            self.scroll_area.set_card_count(remaining)
            if self.list_layout.count() <= 1:
                self.lbl_empty.show()
                self.scroll_area.hide()
            self.req_refresh_all.emit()

    def _handle_status_change(self, schedule_id, new_status):
        if db_manager.update_schedule_status(schedule_id, new_status):
            self.refresh_data()
            self.req_refresh_all.emit()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.window().pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos:
            self.window().move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
