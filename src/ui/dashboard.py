# src/ui/dashboard.py
import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QFrame, QSizePolicy,
                             QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QTimer
from PyQt6.QtGui import (QColor,QFont, QFontMetrics)

from ..data.database import db_manager
from ..services.schedule_query_service import ScheduleQueryService
from ..services.schedule_sort_service import ScheduleSortService
from .schedule_detail_pop import ScheduleDetailPop
from .common.action_context_menu import ActionContextMenu

class DraggableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            window = self.window()
            self.drag_pos = event.globalPosition().toPoint() - window.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos:
            window = self.window()
            window.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None


class ViewSelectorCard(QFrame):
    """
    视图切换按键组：伪装成一个普通的日程卡片
    """
    view_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60) # 改成 60，和日程卡片的高度完全一致
        
        self.setStyleSheet("""
            ViewSelectorCard {
                background-color: rgba(255, 255, 255, 0.10);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.4);
            }
            QPushButton {
                background: transparent;
                color: white;
                font-family: 'Microsoft YaHei';
                font-size: 13px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(5)

        # 定义四个视图按钮
        self.views = {
            "day": "日视图",
            "week": "周视图",
            "month": "月视图",
            "todo": "待办"
        }

        for view_id, view_name in self.views.items():
            btn = QPushButton(view_name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor) # 加个手型光标
            btn.clicked.connect(lambda checked, v=view_id: self.view_selected.emit(v))
            layout.addWidget(btn)
        
class AdaptiveLabel(QLabel):
    def __init__(self, text="", parent=None, max_size=16, min_size=11):
        super().__init__(text, parent)
        self._original_text = text # 保存原始完整文本
        self.max_font_size = max_size
        self.min_font_size = min_size
        self.base_font = QFont('Microsoft YaHei', self.max_font_size)
        self.base_font.setBold(True)
        self.setFont(self.base_font)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.is_strike = False

    def setText(self, text):
        # 确保被外部更新文字时，记录下原本的内容
        self._original_text = text 
        super().setText(text)
        self.adjust_font_to_fit()

    def setStrikeOut(self, strike):
        self.is_strike = strike
        font = self.font()
        font.setStrikeOut(strike)
        self.setFont(font)

    def adjust_font_to_fit(self):
        available_width = self.width()
        if available_width <= 0: return
        
        # 始终根据原始文本去计算，而不是已经被截断成省略号的文本
        text = self._original_text 
        font = self.font()
        font.setStrikeOut(self.is_strike)
        
        # 尝试缩小字号以适应宽度
        for size in range(self.max_font_size, self.min_font_size - 1, -1):
            font.setPixelSize(size)
            fm = QFontMetrics(font)
            text_width = fm.horizontalAdvance(text)
            if text_width <= available_width:
                self.setFont(font)
                super().setText(text)
                return
                
        # 如果缩小到最小字号 (min_size) 还是超出宽度，则截取文字并添加三点省略号
        font.setPixelSize(self.min_font_size)
        self.setFont(font)
        fm = QFontMetrics(font)
        elided_text = fm.elidedText(text, Qt.TextElideMode.ElideRight, available_width)
        super().setText(elided_text)

    def resizeEvent(self, event):
        self.adjust_font_to_fit()
        super().resizeEvent(event)


class ScheduleCard(QFrame):
    """单个日程卡片"""
    req_delete = pyqtSignal(int)
    req_refresh = pyqtSignal()
    req_status = pyqtSignal(int, int)
    req_show_detail = pyqtSignal(object) # 请求显示详情弹窗的信号

    def __init__(self, schedule_data, parent=None):
        super().__init__(parent)
        self.data = schedule_data
        self.setFixedHeight(60) 
        self.setCursor(Qt.CursorShape.PointingHandCursor) # 增加鼠标手型
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        self.is_completed = (self.data.status == 1)
        self.is_expired = False
        
        now = datetime.datetime.now()
        if self.data.end_time and self.data.end_time < now and not self.is_completed:
            self.is_expired = True

        self._setup_ui()
        self._apply_state_style() 

        from .components import CountdownToolTipFilter
        self._tooltip_filter = CountdownToolTipFilter(self.data, self)
        self.installEventFilter(self._tooltip_filter)

    # 拦截左键点击，打开弹窗
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
                
            original_style = self.styleSheet()
            # 加上 "ScheduleCard" 类名，严格限制虚线只画在最外层，不感染内部容器
            self.setStyleSheet("ScheduleCard { background: transparent; border: 2px dashed rgba(255, 255, 255, 0.4); border-radius: 8px; }")
            
            # 遍历布局，暴力隐藏里面的所有东西（包括左容器、竖线、右容器）
            for i in range(self.layout().count()):
                if self.layout().itemAt(i).widget():
                    self.layout().itemAt(i).widget().hide()
            
            # 开始执行拖拽
            drag.exec(Qt.DropAction.MoveAction)
            
            # 拖拽结束，恢复样式，并把里面的东西全部显示回来
            self.setStyleSheet(original_style)
            for i in range(self.layout().count()):
                if self.layout().itemAt(i).widget():
                    self.layout().itemAt(i).widget().show()
                
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
        time_color = "white"
        strike_out = False
        dot_opacity = 1.0

        if self.is_completed:
            bg_color = "background-color: rgba(255, 255, 255, 0.10);"
            if self.data.is_pinned:
                # 如果置顶了，保留实心白色边框
                border_style = "border: 1px solid white;"
            else:
                # 如果没置顶，沿用半透明边框
                border_style = "border: 1px solid rgba(255, 255, 255, 0.4);"
            title_color = "rgba(255, 255, 255, 0.5)"
            time_color = "rgba(255, 255, 255, 0.5)"
            strike_out = True
            dot_opacity = 1.0 

        elif self.is_expired:
            if self.data.is_pinned:
                border_style = "border: 1px solid white;"
            else:
                border_style = "border: 1px solid rgba(255, 255, 255, 0.4);"
            bg_color = "background-color: #bebebe;" 
            border_style = "border: 1px solid rgba(255, 255, 255, 0.4);"
            title_color = "rgba(255, 255, 255, 0.9)" 
            time_color = "#ff4d4f" 
            strike_out = False
            
        elif self.data.is_pinned:
            bg_color = "background-color: rgba(255, 255, 255, 0.2);"
            border_style = "border: 1px solid white;"

        self.setStyleSheet(f"""
            ScheduleCard {{
                {bg_color}
                border-radius: 8px;
                {border_style}
            }}
            ScheduleCard:hover {{
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
        self.lbl_time.setStyleSheet(f"font-size: 10px; color: {time_color};")
        
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
            pin_callback=lambda is_pinned: self._handle_pin_action(), # 沿用原有的置顶处理函数
            delete_callback=self._handle_delete_action
        )
        menu.exec(self.mapToGlobal(pos))

    def _handle_pin_action(self):
        if db_manager.toggle_pin_status(self.data.id, self.data.is_pinned):
            self.req_refresh.emit()

    def _handle_delete_action(self):
        if db_manager.delete_schedule(self.data.id):
            self.req_delete.emit(self.data.id)

    def _setup_ui(self):
        from .components import get_colored_icon
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 0, 15, 0)
        main_layout.setSpacing(10)

        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self.priority_dot = QLabel()
        self.priority_dot.setFixedSize(10, 10)
        p_color = {2: "#ff4d4f", 1: "#faad14", 0: "#52c41a"}.get(self.data.priority, "#52c41a")
        self.priority_dot.setStyleSheet(f"""
            background-color: {p_color};
            border-radius: 5px;
            border: 1px solid rgba(255,255,255,0.8);
        """)
        left_layout.addWidget(self.priority_dot)

        self.lbl_title = AdaptiveLabel(self.data.title, max_size=16, min_size=11)
        left_layout.addWidget(self.lbl_title, stretch=1)
        
        reminder_widget = QWidget()
        reminder_layout = QHBoxLayout(reminder_widget)
        reminder_layout.setContentsMargins(4, 0, 0, 0)
        reminder_layout.setSpacing(4)
        
        self.icon_bell = QLabel()
        self.icon_bell.setFixedSize(12, 12) 
        self.lbl_reminder = QLabel()

        icon_color = QColor(255, 255, 255, 127) if self.is_completed else QColor(255, 255, 255, 255)

        if self.data.reminder_time:
            self.icon_bell.setPixmap(get_colored_icon("alarm.svg", icon_color, 12))
            r_time = self.data.reminder_time
            base_dt = self.data.start_time if self.data.start_time else self.data.end_time
            time_str = r_time.strftime("%H:%M")
            
            if base_dt and r_time.date() < base_dt.date():
                self.lbl_reminder.setText(f"前一天\n{time_str}")
                self.lbl_reminder.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.lbl_reminder.setStyleSheet(f"font-size: 10px; color: {icon_color.name()}; font-weight: bold;")
            else:
                self.lbl_reminder.setText(time_str)
                self.lbl_reminder.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.lbl_reminder.setStyleSheet(f"font-size: 11px; color: {icon_color.name()}; font-weight: bold;")
        else:
            self.icon_bell.setPixmap(get_colored_icon("alarm_off.svg", icon_color, 12))
            self.lbl_reminder.setText("不提醒")
            self.lbl_reminder.setStyleSheet(f"font-size: 11px; color: {icon_color.name()};") 

        reminder_layout.addWidget(self.icon_bell)
        reminder_layout.addWidget(self.lbl_reminder)
        reminder_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        left_layout.addWidget(reminder_widget)

        line = QFrame()
        line.setFixedWidth(1)   
        line.setFixedHeight(40) 
        line.setStyleSheet(f"background-color: {icon_color.name()}; opacity: 0.6;")

        right_container = QWidget()
        right_container.setFixedWidth(60) 
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(2) 
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_time = QLabel()
        self.lbl_time.setStyleSheet(f"font-size: 10px; color: {icon_color.name()};") 
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.data.start_time and self.data.end_time:
            t_str = f"{self.data.start_time.strftime('%H:%M')}-{self.data.end_time.strftime('%H:%M')}"
        elif self.data.end_time:
            t_str = self.data.end_time.strftime('%H:%M')
        else:
            t_str = "全天"
        self.lbl_time.setText(t_str)
        
        repeat_container = QWidget()
        repeat_layout = QHBoxLayout(repeat_container)
        repeat_layout.setContentsMargins(0, 0, 0, 0)
        repeat_layout.setSpacing(4)
        repeat_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_repeat = QLabel()
        self.icon_repeat.setFixedSize(12, 12)
        self.lbl_repeat = QLabel()
        self.lbl_repeat.setStyleSheet(f"font-size: 11px; color: {icon_color.name()};padding-bottom: 2px;")

        rule = self.data.repeat_rule.strip()
        if rule and rule != "无" and rule != "none":
            self.icon_repeat.setPixmap(get_colored_icon("repeat.svg", icon_color, 12))
            self.lbl_repeat.setText(rule)
        else:
            self.icon_repeat.setPixmap(get_colored_icon("repeat_off.svg", icon_color, 12))
            self.lbl_repeat.setText("不重复")
            
        repeat_layout.addWidget(self.icon_repeat, 0, Qt.AlignmentFlag.AlignVCenter)
        repeat_layout.addWidget(self.lbl_repeat, 0, Qt.AlignmentFlag.AlignVCenter)

        right_layout.addWidget(self.lbl_time)
        right_layout.addWidget(repeat_container)

        main_layout.addWidget(left_container)
        main_layout.addWidget(line)
        main_layout.addWidget(right_container)

from .todo import TodoListContainer
class DashboardView(QWidget):
    req_edit_time = pyqtSignal(object, str)
    req_edit_alarm = pyqtSignal(object, str) 
    req_edit_list = pyqtSignal(object, str)
    req_refresh_all = pyqtSignal()
    context_action_requested = pyqtSignal(str)
    context_view_requested = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_pos = None 
        self.open_popups = []
        
        self.current_date = datetime.date.today()
        
        self._setup_ui()
        
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000) 
        
        self.refresh_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 20)
        layout.setSpacing(8)

        # 实例化视图选择器，并放置在主布局的最上方，默认隐藏
        self.view_selector = ViewSelectorCard(self)
        self.view_selector.hide()
        layout.addWidget(self.view_selector)

        self.lbl_empty = QLabel("您还没有日程记录，请点击添加")
        self.lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            font-size: 16px;
            font-family: 'Microsoft YaHei';
        """)
        layout.addWidget(self.lbl_empty)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        
        self.scroll_content = TodoListContainer(self) 
        self.scroll_content.card_dropped.connect(self._handle_card_drop)
        self.scroll_content.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.scroll_content.setStyleSheet("background: transparent;")
        
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8) 
        self.list_layout.addStretch()
        
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        self.lbl_empty.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.lbl_empty.customContextMenuRequested.connect(self._show_context_menu_for_empty)

        self.scroll_content.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.scroll_content.customContextMenuRequested.connect(self._show_context_menu_for_scroll_content)

    # 增加一个供外部调用的切换方法
    def toggle_view_selector(self):
        if self.view_selector.isVisible():
            self.view_selector.hide()
        else:
            self.view_selector.show()

    def _show_context_menu_for_empty(self, pos):
        global_pos = self.lbl_empty.mapToGlobal(pos)
        self._show_dashboard_context_menu(global_pos)

    def _show_context_menu_for_scroll_content(self, pos):
        child = self.scroll_content.childAt(pos)
        if self._is_schedule_card_hit(child):
            return
        global_pos = self.scroll_content.mapToGlobal(pos)
        self._show_dashboard_context_menu(global_pos)

    def _is_schedule_card_hit(self, widget):
        current = widget
        while current is not None:
            if isinstance(current, ScheduleCard):
                return True
            current = current.parentWidget()
        return False

    def _show_dashboard_context_menu(self, global_pos):
        menu = ActionContextMenu(self)
        menu.action_requested.connect(self.context_action_requested.emit)
        menu.view_requested.connect(self.context_view_requested.emit)
        menu.exec(global_pos)

    def refresh_data(self):
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        schedules = db_manager.get_schedules_for_date(self.current_date)
        
        dashboard_schedules = []
        for s in schedules:
            if getattr(s, 'status', 0) == 2:
                continue
                
            if not ScheduleQueryService.is_todo(s):
                dashboard_schedules.append(s)

        dashboard_schedules = ScheduleSortService.sort_for_day_view(dashboard_schedules)

        if not dashboard_schedules:
            self.lbl_empty.show()
            self.scroll_area.hide()
        else:
            self.lbl_empty.hide()
            self.scroll_area.show()
            for index, item in enumerate(dashboard_schedules):
                card = ScheduleCard(item)
                card.req_delete.connect(self._remove_card_from_view)
                card.req_refresh.connect(self.refresh_data)
                
                # 卡片自身操作后，发射全局刷新信号
                card.req_refresh.connect(self.req_refresh_all.emit) 
                
                card.req_status.connect(self._handle_status_change)
                # 连接弹窗信号
                card.req_show_detail.connect(self._show_detail_popup)
                self.list_layout.insertWidget(index, card)

    # 弹出并管理详情面板
    def _show_detail_popup(self, schedule_data, source_view="dashboard"):
        for p in self.open_popups:
            if p.data.id == schedule_data.id and p.isVisible():
                p.activateWindow()
                return
                
        self.open_popups = [p for p in self.open_popups if p.isVisible()]
        
        # 把参数传给弹窗实例
        pop = ScheduleDetailPop(schedule_data, source_view=source_view)
        pop.schedule_updated.connect(self.refresh_data)
        pop.schedule_updated.connect(self.req_refresh_all.emit) 
        
        pop.req_edit_time.connect(lambda data, sv=source_view: self.req_edit_time.emit(data, sv))
        pop.req_edit_alarm.connect(lambda data, sv=source_view: self.req_edit_alarm.emit(data, sv)) 
        pop.req_edit_list.connect(lambda data, sv=source_view: self.req_edit_list.emit(data, sv))
        self.open_popups.append(pop)
        
        pos = self.mapToGlobal(QPoint(self.width() + 10, 0))
        pop.move(pos)
        pop.show()

    def _remove_card_from_view(self, schedule_id):
        sender_card = self.sender()
        if sender_card:
            self.list_layout.removeWidget(sender_card)
            sender_card.deleteLater()
            if self.list_layout.count() <= 1:
                self.lbl_empty.show()
                self.scroll_area.hide()
                
            # 删除日程后，发射全局刷新信号
            self.req_refresh_all.emit() 

    def _handle_status_change(self, schedule_id, new_status):
        if db_manager.update_schedule_status(schedule_id, new_status):
            self.refresh_data()
            
            # 勾选/取消完成状态后，发射全局刷新信号
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

    def _handle_card_drop(self, dragged_id, target_index):
        # 从已被底层物理排序好的 layout 中直接提取最新顺序
        schedules = []
        for i in range(self.list_layout.count() - 1):
            widget = self.list_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'data'):
                schedules.append(widget.data)
                
        dragged_item = next((s for s in schedules if s.id == dragged_id), None)
        if not dragged_item: return

        # 身份识别，防止越界排序
        target_pin = getattr(dragged_item, 'is_pinned', False)
        target_status = getattr(dragged_item, 'status', 0)

        group_items = [s for s in schedules if getattr(s, 'is_pinned', False) == target_pin and getattr(s, 'status', 0) == target_status]

        if len(group_items) <= 1: return
        idx = group_items.index(dragged_item)

        # 计算最新的浮点排序权重
        if idx == 0:
            new_order = getattr(group_items[1], 'sort_order', 0.0) + 100.0
        elif idx == len(group_items) - 1:
            new_order = getattr(group_items[-2], 'sort_order', 0.0) - 100.0
        else:
            new_order = (getattr(group_items[idx-1], 'sort_order', 0.0) + getattr(group_items[idx+1], 'sort_order', 0.0)) / 2.0

        # 更新数据库并刷新
        db_manager.update_schedule_fields(dragged_item.id, sort_order=new_order)
        self.refresh_data()
        self.req_refresh_all.emit()
