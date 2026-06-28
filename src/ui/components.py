# src/ui/components.py
from PyQt6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QScroller, QFrame, QLabel, QMenu, QWidgetAction, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty, QTimer,QPoint, QEvent, QObject, QRect
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QCursor
from datetime import datetime
from src.ui.todo_board import TodoBoardWindow

# =================================================================
class IOSSwitch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._checked = False
        self._thumb_x = 3.0
        
        self.anim = QPropertyAnimation(self, b"thumb_x")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    @pyqtProperty(float)
    def thumb_x(self): return self._thumb_x

    @thumb_x.setter
    def thumb_x(self, x):
        self._thumb_x = x
        self.update()

    def isChecked(self): return self._checked
    
    def setChecked(self, checked):
        self._checked = checked
        self._thumb_x = 25.0 if checked else 3.0
        self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._checked = not self._checked
            end_val = 25.0 if self._checked else 3.0
            self.anim.setStartValue(self._thumb_x)
            self.anim.setEndValue(end_val)
            self.anim.start()
            self.toggled.emit(self._checked)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 14, 14)
        if self._checked:
            bg_color = QColor("#0cc0df") 
        else:
            bg_color = QColor("#e0e0e0") 
        p.fillPath(path, bg_color)
        p.setBrush(Qt.GlobalColor.white)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(self._thumb_x), 3, 22, 22)

# =================================================================
# 循环滚轮 (修复：00与59无缝衔接)
# =================================================================
class NumberScroller(QListWidget):
    value_changed = pyqtSignal()

    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items_list = items
        self.real_count = len(items)
        self.item_height = 30  # 必须与下方 styleSheet 中的 height 一致
        
        self.setFixedWidth(50) 
        self.setFixedHeight(90) # 30px * 3行
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        QScroller.grabGesture(self.viewport(), QScroller.ScrollerGestureType.TouchGesture)
        self.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        
        # 填充 3 组数据 (上缓冲区 | 中间工作区 | 下缓冲区)
        # 这样无论往上滚还是往下滚，都有数据垫底
        loop_items = items * 3
        
        for i in loop_items:
            item = QListWidgetItem(i)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.addItem(item)
            
        self.setStyleSheet("""
            QListWidget { background: transparent; outline: none; }
            QListWidget::item {
                height: 30px; 
                color: rgba(255, 255, 255, 0.4);
                font-size: 14px; font-family: 'Microsoft YaHei'; border: none;
            }
            QListWidget::item:selected {
                background: transparent;
                color: #FFFFFF;
                font-size: 18px; font-weight: bold;
            }
        """)
        
        # 初始化时，定位到中间那一组的第0个
        QTimer.singleShot(0, lambda: self.set_value(items[0]))

    def _check_loop(self):
        """🟢 核心逻辑：检测边界并静默跳转"""
        current_val = self.verticalScrollBar().value()
        one_cycle_height = self.real_count * self.item_height
        
        # 如果滚到了第一组（太靠上），瞬移到第二组
        if current_val < one_cycle_height * 0.5:
            self.verticalScrollBar().setValue(int(current_val + one_cycle_height))
            
        # 如果滚到了第三组（太靠下），瞬移回第二组
        elif current_val > one_cycle_height * 1.5:
            self.verticalScrollBar().setValue(current_val - one_cycle_height)

    def set_value(self, value_str):
        try:
            index = self.items_list.index(value_str)
            # 始终定位到中间那一组 (第2组，索引偏移 real_count)
            target_row = self.real_count + index
            
            # 加上偏移量让它居中显示
            self.setCurrentRow(target_row)
            self.scrollToItem(self.item(target_row), QListWidget.ScrollHint.PositionAtCenter)
        except ValueError:
            pass

    def get_value(self):
        curr = self.currentItem()
        if curr and curr.text(): return curr.text()
        return self.items_list[0]

    def wheelEvent(self, e):
        # 在滚动时实时检测循环
        delta = e.angleDelta().y()
        step = self.item_height 
        
        current_val = self.verticalScrollBar().value()
        
        if delta > 0:
            new_val = current_val - step
        else:
            new_val = current_val + step
            
        self.verticalScrollBar().setValue(new_val)
        
        self._check_loop()    # 检查是否需要循环跳转
        self._snap_to_center() # 吸附对齐
        e.accept()
        
    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self._check_loop()     # 拖拽松手时也要检查
        self._snap_to_center()
        
    def _snap_to_center(self):
        center_y = self.height() // 2
        item = self.itemAt(10, center_y) 
        if item and item.text():
            if self.currentItem() != item:
                self.setCurrentItem(item)
                self.scrollToItem(item, QListWidget.ScrollHint.PositionAtCenter)
                self.value_changed.emit()

# =================================================================
# 动态倒计时气泡提示 (不阻挡右键及点击)
# =================================================================
class CountdownToolTip(QLabel):
    def __init__(self, target_time, parent=None, border_color="#0cc0df"):
        super().__init__(parent, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.target_time = target_time
        self.border_color = border_color
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) 
        self.setStyleSheet("""
            color: #333333;
            font-family: "Microsoft YaHei UI";
            font-size: 12px;
            padding: 6px 10px;
        """)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_text)

    def update_text(self):
        if not self.target_time or not isinstance(self.target_time, datetime):
            self.setText("全天日程 / 无时间限制")
            self.adjustSize()
            return
            
        now = datetime.now()
        if now > self.target_time:
            self.setText("日程已结束 / 已过期")
            self.timer.stop()
        else:
            diff = self.target_time - now
            days = diff.days
            secs = diff.seconds
            hours = secs // 3600
            minutes = (secs % 3600) // 60
            seconds = secs % 60
            
            if days > 0:
                self.setText(f"距离倒计时: {days}天 {hours}小时 {minutes}分")
            else:
                self.setText(f"距离倒计时: {hours:02d}:{minutes:02d}:{seconds:02d}")
        self.adjustSize()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#ffffff"))
        painter.setPen(QPen(QColor(self.border_color), 1)) 
        rect = self.rect().adjusted(0, 0, -1, -1)
        painter.drawRoundedRect(rect, 4, 4)
        super().paintEvent(event)

    def show_at(self, pos):
        self.update_text()
        self.move(pos)
        self.show()
        if self.target_time and self.target_time > datetime.now():
            self.timer.start(1000)

class CountdownToolTipFilter(QObject):
    def __init__(self, schedule_data, parent=None):
        super().__init__(parent)
        self.data = schedule_data
        self.tooltip = None
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.show_tooltip)

    def eventFilter(self, obj, event):
        # 监听事件，但一律返回 False，绝不拦截吞噬事件
        if event.type() == QEvent.Type.Enter:
            self.timer.start(400) # 悬停 400ms 后显示
        elif event.type() in (QEvent.Type.Leave, QEvent.Type.MouseButtonPress, QEvent.Type.Hide, QEvent.Type.FocusOut):
            self.timer.stop()
            self._close_tooltip()
        return False

    def show_tooltip(self):
        if not self.tooltip:
            # 如果已经过了开始时间，就倒计时到结束时间
            now = datetime.now()
            target_time = getattr(self.data, 'start_time', None)
            end_time = getattr(self.data, 'end_time', None)
            
            if target_time and now > target_time and end_time and now < end_time:
                target_time = end_time
            elif not target_time:
                target_time = end_time
                
            self.tooltip = CountdownToolTip(target_time)
        self.tooltip.show_at(QCursor.pos() + QPoint(15, 15))

    def _close_tooltip(self):
        if self.tooltip:
            self.tooltip.timer.stop()
            self.tooltip.close()
            self.tooltip.deleteLater()
            self.tooltip = None

class SharedMoreMenu(QMenu):
    """
    通用型更多菜单管理类
    支持跨窗口实例调用，可自动处理置顶、悬浮、边框修复及菜单项渲染
    """
    _schedule_display_mode = "card"

    def __init__(self, parent_window, anchor_button, show_festival_option=False):
        # parent_window 必须是顶级窗口 
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.anchor_button = anchor_button
        self.show_festival_option = show_festival_option
        self._ignore_next_click = False
        
        self._setup_ui()
        self.aboutToHide.connect(self._on_menu_closing)

    def _setup_ui(self):
        from PyQt6.QtWidgets import QWidgetAction, QCheckBox, QFrame, QHBoxLayout, QWidget, QLabel
        from PyQt6.QtGui import QPixmap, QIcon
        from PyQt6.QtCore import QSize, Qt
        from ..utils.styles import StyleManager
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setStyleSheet(StyleManager.get_menu_style())

        text_color = "#333333" 
        hover_bg = "rgba(12, 192, 223, 0.1)" 
        self._more_hover_bg = hover_bg
        self._mode_row = None
        self._mode_widget_action = None
        self._mode_menu_locked = False
        self._mode_option_rows = {}
        self.mode_menu = QMenu("模式切换", self)
        self.mode_menu.setFixedWidth(150)
        self.mode_menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.mode_menu.setWindowFlags(
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.mode_menu.setStyleSheet(StyleManager.get_menu_style())
        self.mode_menu.aboutToHide.connect(self._clear_mode_row_hover)
        self._mode_hover_timer = QTimer(self)
        self._mode_hover_timer.setInterval(30)
        self._mode_hover_timer.timeout.connect(self._close_mode_menu_if_cursor_outside)

        self._help_row = None
        self._help_widget_action = None
        self._help_menu_locked = False
        self.help_menu = QMenu("使用帮助", self)
        self.help_menu.setFixedWidth(150)
        self.help_menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.help_menu.setWindowFlags(
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.help_menu.setStyleSheet(StyleManager.get_menu_style())
        self.help_menu.aboutToHide.connect(self._clear_help_row_hover)
        self.aboutToHide.connect(self.mode_menu.close)
        self.aboutToHide.connect(self.help_menu.close)
        self._help_hover_timer = QTimer(self)
        self._help_hover_timer.setInterval(30)
        self._help_hover_timer.timeout.connect(self._close_help_menu_if_cursor_outside)

        def add_centered_btn(text, icon_name, callback, menu=None, arrow=False, close_on_click=True, on_enter=None, on_leave=None, icon_color=None, icon_inset=0):
            target_menu = menu or self
            action = QWidgetAction(target_menu)
            btn_frame = QFrame()
            btn_frame.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            
            layout = QHBoxLayout(btn_frame)
            layout.setContentsMargins(0, 6, 0, 6) 
            layout.setSpacing(8)                  
            layout.addStretch() 
            
            icon_label = QLabel()
            icon_label.setFixedSize(18, 18)
            if icon_color:
                icon_pixmap = get_colored_icon(
                    f"{icon_name}.svg",
                    icon_color,
                    18 - icon_inset * 2,
                )
            else:
                icon_pixmap = QPixmap(f"assets/icons/{icon_name}.svg")
                if icon_inset:
                    icon_pixmap = icon_pixmap.scaled(
                        18 - icon_inset * 2,
                        18 - icon_inset * 2,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
            icon_label.setScaledContents(not icon_inset)
            if icon_inset:
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setPixmap(icon_pixmap)
            icon_label.setStyleSheet("background: transparent; border: none;")
            icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            layout.addWidget(icon_label)
            
            text_label = QLabel(text)
            text_label.setStyleSheet(f"color: {text_color}; font-family: 'Microsoft YaHei UI'; font-size: 13px; background: transparent; border: none;")
            text_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            layout.addWidget(text_label)
            layout.addStretch() 

            if arrow:
                arrow_label = QLabel("›")
                arrow_label.setStyleSheet(
                    "color: #0cc0df; font-family: 'Microsoft YaHei UI'; "
                    "font-size: 18px; font-weight: bold; background: transparent; border: none;"
                )
                arrow_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                layout.addWidget(arrow_label)
            
            def enter_event(event):
                btn_frame.setStyleSheet(f"background-color: {hover_bg}; border-radius: 4px;")
                if on_enter:
                    on_enter()
            def leave_event(event):
                if (
                    btn_frame is self._mode_row
                    and self.mode_menu.isVisible()
                ) or (
                    btn_frame is self._help_row
                    and self.help_menu.isVisible()
                ):
                    btn_frame.setStyleSheet(f"background-color: {hover_bg}; border-radius: 4px;")
                else:
                    btn_frame.setStyleSheet("background-color: transparent;")
                if on_leave:
                    on_leave()
            def mouse_release(event):
                if event.button() == Qt.MouseButton.LeftButton:
                    if close_on_click:
                        self.help_menu.close()
                        self.mode_menu.close()
                        self.close()
                    callback()

            btn_frame.enterEvent = enter_event
            btn_frame.leaveEvent = leave_event
            btn_frame.mouseReleaseEvent = mouse_release
            
            action.setDefaultWidget(btn_frame)
            target_menu.addAction(action)
            return action, btn_frame

        def add_mode_option(text, icon_name, mode_id, icon_inset=0):
            action = QWidgetAction(self.mode_menu)
            btn_frame = QFrame()
            btn_frame.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

            layout = QHBoxLayout(btn_frame)
            layout.setContentsMargins(0, 6, 0, 6)
            layout.setSpacing(8)
            layout.addStretch()

            icon_label = QLabel()
            icon_label.setFixedSize(18, 18)
            icon_pixmap = QPixmap(f"assets/icons/{icon_name}.svg")
            if icon_inset:
                icon_pixmap = icon_pixmap.scaled(
                    18 - icon_inset * 2,
                    18 - icon_inset * 2,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            icon_label.setScaledContents(not icon_inset)
            if icon_inset:
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setPixmap(icon_pixmap)
            icon_label.setStyleSheet("background: transparent; border: none;")
            icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            layout.addWidget(icon_label)

            text_label = QLabel(text)
            text_label.setStyleSheet(
                f"color: {text_color}; font-family: 'Microsoft YaHei UI'; font-size: 13px; "
                "background: transparent; border: none;"
            )
            text_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            layout.addWidget(text_label)
            layout.addStretch()

            def enter_event(event):
                self._set_mode_option_style(mode_id, hovered=True)

            def leave_event(event):
                self._set_mode_option_style(mode_id, hovered=False)

            def mouse_release(event):
                if event.button() == Qt.MouseButton.LeftButton:
                    self._on_schedule_mode_selected(mode_id)
                    self._mode_menu_locked = False
                    self.mode_menu.close()
                    self.close()

            btn_frame.enterEvent = enter_event
            btn_frame.leaveEvent = leave_event
            btn_frame.mouseReleaseEvent = mouse_release

            action.setDefaultWidget(btn_frame)
            self.mode_menu.addAction(action)
            self._mode_option_rows[mode_id] = btn_frame
            return action, btn_frame

        def add_menu_separator():
            action = QWidgetAction(self)
            container = QWidget()
            container.setObjectName("more_menu_separator_container")
            layout = QHBoxLayout(container)
            layout.setContentsMargins(10, 4, 10, 4)
            layout.setSpacing(0)

            line = QFrame()
            line.setObjectName("more_menu_separator_line")
            line.setFixedHeight(1)
            line.setStyleSheet("background-color: #dcdcdc; border: none;")
            layout.addWidget(line)

            action.setDefaultWidget(container)
            self.addAction(action)
            return action

        def add_checkable_option(text, is_checked, callback, icon_path=None):
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(8, 4, 15, 4)
            checkbox = QCheckBox(text)
            if icon_path:
                checkbox.setIcon(QIcon(icon_path))
            checkbox.setIconSize(QSize(18, 18))
            checkbox.setChecked(is_checked)
            checkbox.toggled.connect(callback)
            layout.addWidget(checkbox)
            action = QWidgetAction(self)
            action.setDefaultWidget(container)
            self.addAction(action)
            return checkbox

        pin_icon_path = f"assets/icons/pin.svg"
        self.chk_pin = add_checkable_option(
            " 窗口置顶",
            False,
            lambda checked: self.toggle_pin_mode(),
            icon_path=pin_icon_path
        )

        add_menu_separator()
        self.chk_festival = None
        if self.show_festival_option:
            self.chk_festival = add_checkable_option(
                " 显示节日",
                True,
                lambda checked: None,
                icon_path="assets/icons/festival.svg",
            )
            add_menu_separator()
        add_centered_btn("坐标显示", "axis", self._on_show_axis)
        add_centered_btn("待办显示", "todo", self._on_show_todo)
        add_centered_btn("修改字体", "theme", self._on_modify_font, icon_color="#333333")
        add_centered_btn("导出日程", "export", self._on_export_schedule)
        add_centered_btn("全部日程", "history", self._on_show_history)
        add_menu_separator()
        self._mode_widget_action, self._mode_row = add_centered_btn(
            "模式切换",
            "model_switch",
            self._toggle_mode_menu_lock,
            arrow=True,
            close_on_click=False,
            on_enter=self._show_mode_menu,
            on_leave=self._schedule_mode_menu_hide,
            icon_inset=1,
        )
        add_mode_option("卡片模式", "schedule_card", "card")
        add_mode_option("课表模式", "timetable", "timetable", icon_inset=1)
        self._refresh_mode_option_styles()
        self._help_widget_action, self._help_row = add_centered_btn(
            "使用帮助",
            "help",
            self._toggle_help_menu_lock,
            arrow=True,
            close_on_click=False,
            on_enter=self._show_help_menu,
            on_leave=self._schedule_help_menu_hide,
        )
        add_centered_btn("使用手册", "user_manual", self._on_show_help_manual, menu=self.help_menu)
        add_centered_btn("帮助助手", "assistant", self._on_show_help_assistant, menu=self.help_menu)

    def _set_mode_row_hover(self, hovered):
        if not self._mode_row:
            return
        if hovered:
            self._mode_row.setStyleSheet(
                f"background-color: {getattr(self, '_more_hover_bg', 'rgba(12, 192, 223, 0.1)')}; border-radius: 4px;"
            )
        else:
            self._mode_row.setStyleSheet("background-color: transparent;")

    def _set_mode_option_style(self, mode_id, hovered=False):
        row = self._mode_option_rows.get(mode_id)
        if not row:
            return
        is_current = self.__class__._schedule_display_mode == mode_id
        if is_current:
            row.setStyleSheet("background-color: rgba(12, 192, 223, 0.16); border-radius: 4px;")
        elif hovered:
            row.setStyleSheet("background-color: rgba(12, 192, 223, 0.1); border-radius: 4px;")
        else:
            row.setStyleSheet("background-color: transparent;")

    def _refresh_mode_option_styles(self):
        for mode_id in self._mode_option_rows:
            self._set_mode_option_style(mode_id, hovered=False)

    def _show_mode_menu(self):
        if not self._mode_widget_action:
            return
        self._help_menu_locked = False
        self.help_menu.close()
        self._set_mode_row_hover(True)
        self._refresh_mode_option_styles()
        action_rect = self.actionGeometry(self._mode_widget_action)
        popup_pos = self.mapToGlobal(QPoint(self.width(), action_rect.top()))
        self.mode_menu.popup(popup_pos)
        if not self._mode_hover_timer.isActive():
            self._mode_hover_timer.start()

    def _toggle_mode_menu_lock(self):
        if self._mode_menu_locked:
            self._mode_menu_locked = False
            self._close_mode_menu_if_cursor_outside()
            return
        self._mode_menu_locked = True
        self._show_mode_menu()
        self._mode_hover_timer.stop()

    def _schedule_mode_menu_hide(self):
        if self._mode_menu_locked:
            return
        QTimer.singleShot(0, self._close_mode_menu_if_cursor_outside)

    def _hide_mode_menu(self):
        self._mode_hover_timer.stop()
        self._mode_menu_locked = False
        self._clear_mode_row_hover()
        self.mode_menu.close()

    def _clear_mode_row_hover(self):
        self._set_mode_row_hover(False)

    def _close_mode_menu_if_cursor_outside(self):
        if self._mode_menu_locked:
            self._mode_hover_timer.stop()
            return
        if not hasattr(self, "mode_menu") or not self.mode_menu.isVisible():
            self._mode_hover_timer.stop()
            self._clear_mode_row_hover()
            return
        cursor_pos = QCursor.pos()
        mode_row_rect = QRect()
        if self._mode_row:
            mode_row_rect = QRect(self._mode_row.mapToGlobal(QPoint(0, 0)), self._mode_row.size())
        mode_menu_rect = QRect(self.mode_menu.mapToGlobal(QPoint(0, 0)), self.mode_menu.size())
        if not mode_row_rect.contains(cursor_pos) and not mode_menu_rect.contains(cursor_pos):
            self._hide_mode_menu()

    def _on_schedule_mode_selected(self, mode_id):
        if mode_id not in {"card", "timetable"}:
            return
        self.__class__._schedule_display_mode = mode_id
        self._refresh_mode_option_styles()
        mode_label = {"card": "卡片模式", "timetable": "课表模式"}[mode_id]
        print(f"[{self.parent_window.__class__.__name__}] 选择日程显示模式：{mode_label}（功能待接入）")

    def _set_help_row_hover(self, hovered):
        if not self._help_row:
            return
        if hovered:
            self._help_row.setStyleSheet(
                f"background-color: {getattr(self, '_more_hover_bg', 'rgba(12, 192, 223, 0.1)')}; border-radius: 4px;"
            )
        else:
            self._help_row.setStyleSheet("background-color: transparent;")

    def _show_help_menu(self):
        if not self._help_widget_action:
            return
        self._mode_menu_locked = False
        self.mode_menu.close()
        self._set_help_row_hover(True)
        action_rect = self.actionGeometry(self._help_widget_action)
        popup_pos = self.mapToGlobal(QPoint(self.width(), action_rect.top()))
        self.help_menu.popup(popup_pos)
        if not self._help_hover_timer.isActive():
            self._help_hover_timer.start()

    def _toggle_help_menu_lock(self):
        if self._help_menu_locked:
            self._help_menu_locked = False
            self._close_help_menu_if_cursor_outside()
            return
        self._help_menu_locked = True
        self._show_help_menu()
        self._help_hover_timer.stop()

    def _schedule_help_menu_hide(self):
        if self._help_menu_locked:
            return
        QTimer.singleShot(0, self._close_help_menu_if_cursor_outside)

    def _hide_help_menu(self):
        self._help_hover_timer.stop()
        self._help_menu_locked = False
        self._clear_help_row_hover()
        self.help_menu.close()

    def _clear_help_row_hover(self):
        self._set_help_row_hover(False)

    def _close_help_menu_if_cursor_outside(self):
        if self._help_menu_locked:
            self._help_hover_timer.stop()
            return
        if not hasattr(self, "help_menu") or not self.help_menu.isVisible():
            self._help_hover_timer.stop()
            self._clear_help_row_hover()
            return
        cursor_pos = QCursor.pos()
        help_row_rect = QRect()
        if self._help_row:
            help_row_rect = QRect(self._help_row.mapToGlobal(QPoint(0, 0)), self._help_row.size())
        help_menu_rect = QRect(self.help_menu.mapToGlobal(QPoint(0, 0)), self.help_menu.size())
        if not help_row_rect.contains(cursor_pos) and not help_menu_rect.contains(cursor_pos):
            self._hide_help_menu()

    def show_menu(self):
        from PyQt6.QtCore import Qt
        from ..utils.win_api import apply_24h2_border_fix
        if self._ignore_next_click: return
        
        # 智能识别当前调用窗口的置顶状态并同步 UI
        current_flags = self.parent_window.windowFlags()
        is_pinned = bool(current_flags & Qt.WindowType.WindowStaysOnTopHint)
        self.chk_pin.blockSignals(True)
        self.chk_pin.setChecked(is_pinned)
        self.chk_pin.blockSignals(False)

        # 锚定按钮左下角弹出
        pos = self.anchor_button.mapToGlobal(self.anchor_button.rect().bottomLeft())
        pos.setY(pos.y() + 6)
        
        self.ensurePolished()
        hwnd = int(self.winId())
        apply_24h2_border_fix(hwnd)
        self.exec(pos)
        
        self.anchor_button.setDown(False)      
        self.anchor_button.clearFocus()         
        self.anchor_button.setAttribute(Qt.WidgetAttribute.WA_UnderMouse, False) 
        self.anchor_button.update()             

    def _on_menu_closing(self):
        from PyQt6.QtCore import QTimer
        self._mode_menu_locked = False
        self._help_menu_locked = False
        self._mode_hover_timer.stop()
        self._help_hover_timer.stop()
        self._clear_mode_row_hover()
        self._clear_help_row_hover()
        self._ignore_next_click = True
        QTimer.singleShot(300, lambda: setattr(self, '_ignore_next_click', False))

    def reopen_menu(self):
        self._ignore_next_click = False
        self.show_menu()

    def toggle_pin_mode(self):
        """等主窗口闪烁完毕后，再瞬间弹出菜单，绝对不丢！"""
        from PyQt6.QtCore import Qt, QTimer
        from ..utils.win_api import apply_24h2_border_fix
        
        # 立即获取当前的置顶状态
        current_flags = self.parent_window.windowFlags()
        
        # 为了安全，先主动关闭当前菜单，释放系统的控制权
        self.close()
        
        def _do_toggle():

            if current_flags & Qt.WindowType.WindowStaysOnTopHint:
                new_flags = current_flags ^ Qt.WindowType.WindowStaysOnTopHint
                print("状态变更：取消置顶")
            else:
                new_flags = current_flags | Qt.WindowType.WindowStaysOnTopHint
                print("状态变更：开启置顶")
            
            # 执行变更
            self.parent_window.setWindowFlags(new_flags)
            self.parent_window.show()
            
            # 补上 24H2 的防黑边
            hwnd = int(self.parent_window.winId())
            apply_24h2_border_fix(hwnd)

            # 等主窗口彻底闪烁完毕、稳定之后，再把菜单瞬间弹出来！
            QTimer.singleShot(50, self.reopen_menu)

        # 稍微延迟 10ms 执行窗口重建，确保前面的 self.close() 已经彻底生效
        QTimer.singleShot(10, _do_toggle)
        
    def _on_export_schedule(self):
        print(f"[{self.parent_window.__class__.__name__}] 点击了导出日程")

    def _on_show_history(self):
        print(f"[{self.parent_window.__class__.__name__}] 点击了全部日程")

    def _on_show_axis(self):
        from PyQt6.QtGui import QGuiApplication
        from PyQt6.QtWidgets import QApplication
        from src.ui.popups.schedule_axis_board import ScheduleAxisBoard

        if not hasattr(self.parent_window, "axis_board") or self.parent_window.axis_board is None:
            self.parent_window.axis_board = ScheduleAxisBoard(self.parent_window)
            detail_owner = self.parent_window
            if not hasattr(detail_owner, "open_schedule_detail_from_month_panel"):
                detail_owner = next(
                    (
                        widget
                        for widget in QApplication.topLevelWidgets()
                        if hasattr(widget, "open_schedule_detail_from_month_panel")
                    ),
                    None,
                )
            if detail_owner is not None:
                self.parent_window.axis_board.set_detail_opener(
                    detail_owner.open_schedule_detail_from_month_panel
                )
            parent_geometry = self.parent_window.frameGeometry()
            board = self.parent_window.axis_board
            x = parent_geometry.right() + 10
            y = parent_geometry.top()
            screen = QGuiApplication.screenAt(parent_geometry.center()) or QGuiApplication.primaryScreen()
            if screen is not None:
                available = screen.availableGeometry()
                if x + board.width() > available.right() + 1:
                    x = parent_geometry.left() - board.width() - 10
                x = max(available.left(), min(x, available.right() - board.width() + 1))
                y = max(available.top(), min(y, available.bottom() - board.height() + 1))
            board.move(x, y)

        board = self.parent_window.axis_board
        if board.isVisible():
            board.hide()
            return
        board.refresh_data()
        board.show()
        board.raise_()
        board.activateWindow()

    def _on_modify_font(self):
        print(f"[{self.parent_window.__class__.__name__}] 点击了修改字体")

    def _on_show_help_manual(self):
        print(f"[{self.parent_window.__class__.__name__}] 点击了使用手册")

    def _on_show_help_assistant(self):
        print(f"[{self.parent_window.__class__.__name__}] 点击了帮助助手")

    def _on_show_todo(self):
        # 检查主窗口是否已经实例化了看板，没有则新建
        if not hasattr(self.parent_window, 'todo_board') or self.parent_window.todo_board is None:
            self.parent_window.todo_board = TodoBoardWindow(self.parent_window)
            
            # 默认弹在主窗口右侧一点的位置
            main_geom = self.parent_window.geometry()
            self.parent_window.todo_board.move(main_geom.x() + main_geom.width() + 10, main_geom.y())
            
        board = self.parent_window.todo_board
        
        # 切换显示/隐藏状态
        if board.isVisible():
            board.hide()
        else:
            board.show()
            board.raise_()
            board.activateWindow()

# =================================================================
# 日程卡片通用右键菜单
# =================================================================
from PyQt6.QtWidgets import QMenu

class ScheduleContextMenu(QMenu):
    def __init__(self, schedule_obj, parent=None):
        super().__init__(parent)
        self.schedule_obj = schedule_obj
        
        from PyQt6.QtCore import Qt
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setStyleSheet("""
            QMenu {
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 6px;
                padding: 4px;
                min-width: 110px;
            }
            QMenu::separator {
                height: 1px;
                background: rgba(0,0,0,0.1);
                margin: 4px 10px;
            }
        """)

    def setup_actions(self, status_callback, pin_callback, delete_callback):
        """配置菜单项，接收三个核心功能的回调函数"""
        menu_icon_color = "#333333" 
        
        # 1. 智能判断是日程还是待办
        is_todo = False
        if hasattr(self.schedule_obj, 'item_type') and self.schedule_obj.item_type == 'todo':
            is_todo = True
        elif hasattr(self.schedule_obj, 'type') and getattr(self.schedule_obj, 'type', 0) == 1:
            is_todo = True
            
        suffix = "待办" if is_todo else "日程"
        
        # 2. 获取当前状态 (0:未完成, 1:已完成, 2:已隐藏)
        status = getattr(self.schedule_obj, 'status', 0)
        is_completed = (status == 1 or status == 2)
        
        # 3. 完成/撤销完成
        if is_completed:
            text, icon_name, target_status = "撤销完成", "undo.svg", 0
        else:
            text, icon_name, target_status = f"完成{suffix}", "check.svg", 1
            
        self._add_centered_action(text, icon_name, menu_icon_color, lambda: status_callback(target_status))
        
        # 如果当前是“已完成”状态(status==1)，显示“隐藏”按钮
        if status == 1:
            hide_text = f"隐藏{suffix}"
            self._add_centered_action(hide_text, "hide.svg", menu_icon_color, lambda: status_callback(2))
        
        self.addSeparator()

        # 置顶/取消置顶
        is_pinned = getattr(self.schedule_obj, 'is_pinned', False)
        text, icon_name = ("取消置顶", "untop.svg") if is_pinned else (f"置顶{suffix}", "top.svg")
        self._add_centered_action(text, icon_name, menu_icon_color, lambda: pin_callback(is_pinned))
        
        self.addSeparator()

        # 删除
        self._add_centered_action(f"删除{suffix}", "delete.svg", menu_icon_color, delete_callback)

    def _add_centered_action(self, text, icon_name, icon_color, callback):
        
        action = QWidgetAction(self)
        btn_frame = QFrame()
        btn_frame.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_frame.setStyleSheet("background-color: transparent;")
        
        layout = QHBoxLayout(btn_frame)
        layout.setContentsMargins(0, 6, 0, 6) 
        layout.setSpacing(6)                  
        layout.addStretch() 
        
        icon_label = QLabel()
        icon_label.setFixedSize(14, 14)
        pixmap = get_colored_icon(icon_name, icon_color, 14)
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap)
            layout.addWidget(icon_label)
        else:
            if "check" in icon_name: text = "✅ " + text
            elif "undo" in icon_name: text = "↩️ " + text
            icon_label.hide()
        
        text_label = QLabel(text)
        text_label.setStyleSheet("color: #333333; font-size: 13px; background: transparent; border: none;")
        layout.addWidget(text_label)
        layout.addStretch()
        
        def mouseReleaseEvent(e):
            if e.button() == Qt.MouseButton.LeftButton:
                self.close()
                callback()
        def enterEvent(e):
            btn_frame.setStyleSheet("background-color: rgba(0, 0, 0, 0.05); border-radius: 4px;")
        def leaveEvent(e):
            btn_frame.setStyleSheet("background-color: transparent;")

        btn_frame.mouseReleaseEvent = mouseReleaseEvent
        btn_frame.enterEvent = enterEvent
        btn_frame.leaveEvent = leaveEvent
        action.setDefaultWidget(btn_frame)
        self.addAction(action)

# =================================================================
# SVG 高清渲染与染色
# =================================================================
def get_colored_icon(icon_name, color, target_size=12):

    import os
    from PyQt6.QtGui import QPixmap, QImage, QColor, QPainter
    from PyQt6.QtCore import Qt
    from PyQt6.QtSvg import QSvgRenderer

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
