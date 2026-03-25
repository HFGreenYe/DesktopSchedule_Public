# src/ui/list_picker.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QLineEdit, 
                             QMenu, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QTimer, QSize
from PyQt6.QtGui import QColor, QAction, QCursor, QPainter, QPen, QIcon
from ..data.database import db_manager
from ..utils.styles import StyleManager

# 复用气泡提示
class CustomToolTip(QLabel):
    def __init__(self, text, parent=None, border_color="#0cc0df"):
        super().__init__(parent, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setText(text)
        self.border_color = border_color
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setStyleSheet("""
            color: #333333;
            font-family: "Microsoft YaHei UI";
            font-size: 12px;
            padding: 6px 10px;
        """)
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
        self.move(pos)
        self.show()
        QTimer.singleShot(2500, self.close) # 稍微延长一点报错显示时间


class CategoryCard(QFrame):
    clicked = pyqtSignal(int)
    delete_requested = pyqtSignal(int, str) # 传递 id 和 名字

    def __init__(self, cat_id, name, is_selected=False, parent=None):
        super().__init__(parent)
        self.cat_id = cat_id
        self.cat_name = name
        self.is_selected = is_selected
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(50)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 0, 15, 0)
        
        self.dot = QLabel()
        self.dot.setFixedSize(8, 8)
        self.dot.setStyleSheet("background-color: #0cc0df; border-radius: 4px;")
        
        # UI 渲染：包括三位数编号
        display_text = f"#{self.cat_id:03d}  {self.cat_name}"
        self.lbl_name = QLabel(display_text)
        self.lbl_name.setStyleSheet("""
            color: white; 
            font-size: 14px; 
            font-weight: bold; 
            font-family: 'Microsoft YaHei';
        """)
        
        self.layout.addWidget(self.dot)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.lbl_name)
        self.layout.addStretch()
        
        self.lbl_check = QLabel("✔")
        self.lbl_check.setStyleSheet("color: #0cc0df; font-size: 16px; font-weight: bold;")
        self.lbl_check.hide()
        self.layout.addWidget(self.lbl_check)
        
        self.update_style()

    def update_style(self):
        if self.is_selected:
            self.setStyleSheet("""
                CategoryCard {
                    background-color: rgba(255, 255, 255, 0.2);
                    border: 1px solid #0cc0df;
                    border-radius: 8px;
                }
            """)
            self.lbl_check.show()
        else:
            self.setStyleSheet("""
                CategoryCard {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                }
                CategoryCard:hover {
                    background-color: rgba(255, 255, 255, 0.15);
                }
            """)
            self.lbl_check.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 点击时传递 ID
            self.clicked.emit(self.cat_id)
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(StyleManager.get_menu_style())
        
        icon_path = "assets/icons/delete.svg"
        del_action = QAction(QIcon(icon_path), "删除清单", self)
        
        # 删除时传递 ID 和 名称
        del_action.triggered.connect(lambda: self.delete_requested.emit(self.cat_id, self.cat_name))
        menu.addAction(del_action)
        
        menu.exec(pos)


class ListPickerView(QWidget):
    back_requested = pyqtSignal()
    suspend_requested = pyqtSignal()
    confirm_requested = pyqtSignal(object) # 发送 cat_id 或 None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_cat_id = None
        self.drag_pos = None 
        self.current_list_type = 'schedule'
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. 标题栏
        self.header_container = QWidget() 
        self.header_container.setFixedHeight(60)
        header_layout = QHBoxLayout(self.header_container)
        header_layout.setContentsMargins(30, 10, 30, 0)
        self.lbl_title = QLabel("选择清单")
        self.lbl_title.setStyleSheet("""
            color: white; 
            font-size: 24px; 
            font-weight: bold; 
            font-family: 'Microsoft YaHei';
        """)
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()
        layout.addWidget(self.header_container)

        # 2. 内容区
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 10, 20, 20)
        self.content_layout.setSpacing(15)
        
        # --- 动态输入框 (默认隐藏) ---
        self.input_container = QWidget()
        self.input_container.setFixedHeight(50)
        self.input_container.hide() 
        input_layout = QHBoxLayout(self.input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)
        
        self.input_new = QLineEdit()
        self.input_new.setPlaceholderText("输入清单名称，回车确认...")
        self.input_new.setFixedHeight(40)
        self.input_new.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid #0cc0df;
                border-radius: 8px;
                color: white;
                padding-left: 10px;
                font-family: 'Microsoft YaHei';
                font-weight: bold;
            }
        """)
        
        self.btn_confirm_add = QPushButton("✔")
        self.btn_confirm_add.setFixedSize(40, 40)
        self.btn_confirm_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirm_add.setStyleSheet("""
            QPushButton {
                background-color: #0cc0df; 
                border: 1px solid white; 
                border-radius: 20px; 
                color: white; 
                font-size: 16px; 
            }
            QPushButton:hover { background-color: #0bb0cf; }
        """)
        
        input_layout.addWidget(self.input_new)
        input_layout.addWidget(self.btn_confirm_add)
        self.content_layout.addWidget(self.input_container)
        
        # 清单列表
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        self.content_layout.addWidget(self.cards_container)
        
        self.content_layout.addStretch()
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

        # 3. 底部按钮组
        self.footer_container = QWidget()
        f_layout = QHBoxLayout(self.footer_container)
        f_layout.setContentsMargins(25, 10, 25, 20)
        f_layout.setSpacing(15) 
        
        btn_size = QSize(85, 40)
        
        common_style = """
            QPushButton { 
                background: transparent; 
                border: 1px solid rgba(255,255,255,0.6); 
                border-radius: 20px; 
                color: white; 
                font-weight: bold; 
                font-family: 'Microsoft YaHei';
                font-size: 13px;
            }
            QPushButton:hover { 
                background: rgba(255,255,255,0.15); 
                border-color: white; 
            }
        """
        
        primary_style = """
            QPushButton { 
                background: white; 
                border: none; 
                border-radius: 20px; 
                color: #0cc0df; 
                font-weight: bold; 
                font-family: 'Microsoft YaHei';
                font-size: 13px;
            }
            QPushButton:hover { background: #f0f0f0; }
        """
        
        self.btn_add_new = QPushButton("+ 新建")
        self.btn_add_new.setFixedSize(btn_size)
        self.btn_add_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_new.setStyleSheet(common_style)
        
        self.btn_cancel = QPushButton("退出")
        self.btn_cancel.setFixedSize(btn_size)
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet(common_style)
        
        self.btn_ok = QPushButton("确定")
        self.btn_ok.setFixedSize(btn_size)
        self.btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ok.setStyleSheet(primary_style) 
        
        f_layout.addWidget(self.btn_add_new)
        f_layout.addStretch() 
        f_layout.addWidget(self.btn_cancel)
        f_layout.addWidget(self.btn_ok)
        
        layout.addWidget(self.footer_container)
        self._setup_window_controls()

    def set_title(self, text="选择清单"):
        self.lbl_title.setText(text)
        if len(text) > 4:
            self.lbl_title.setStyleSheet("color: white; font-size: 17px; font-weight: bold; font-family: 'Microsoft YaHei';")
        else:
            self.lbl_title.setStyleSheet("color: white; font-size: 24px; font-weight: bold; font-family: 'Microsoft YaHei';")

    def _connect_signals(self):
        self.btn_add_new.clicked.connect(self._toggle_input_box)
        self.btn_confirm_add.clicked.connect(self._add_category)
        self.input_new.returnPressed.connect(self._add_category)
        
        self.btn_cancel.clicked.connect(self.back_requested.emit)
        self.btn_ok.clicked.connect(self._on_confirm)

    def load_data(self, current_selected_id=None, list_type=None):
        self.selected_cat_id = current_selected_id
        
        # 如果主界面传了新的类型过来，就更新弹窗自己的状态
        if list_type:
            self.current_list_type = list_type
            
        self.input_container.hide() 
        
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 查询时把 current_list_type 传给数据库进行过滤！
        categories = db_manager.get_active_categories(list_type=self.current_list_type)
        
        if not categories:
            lbl = QLabel("还没有清单，点击下方新建")
            lbl.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 14px; margin-top: 20px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cards_layout.addWidget(lbl)
        
        for cat in categories:
            is_active = (cat.id == self.selected_cat_id)
            card = CategoryCard(cat.id, cat.name, is_active)
            card.clicked.connect(self._on_card_clicked)
            card.delete_requested.connect(self._delete_category_logic)
            self.cards_layout.addWidget(card)

    def _toggle_input_box(self):
        if self.input_container.isVisible():
            self.input_container.hide()
        else:
            self.input_container.show()
            self.input_new.setFocus()

    def _add_category(self):
        name = self.input_new.text().strip()
        if not name: return
        
        # 接收新创建的清单 ID
        new_id = db_manager.add_category(name, list_type=self.current_list_type)
        
        if new_id is not None:
            self.input_new.clear()
            self.input_container.hide() 
            
            # 将当前选中的 ID 强制设为刚刚新建的清单 ID
            self.selected_cat_id = new_id
            
            # 重新加载列表
            self.load_data(self.selected_cat_id) 
        else:
            self._show_tooltip("⚠️ 添加清单失败", is_error=True)

    # 删除状态拦截逻辑
    def _delete_category_logic(self, cat_id, cat_name):
        status = db_manager.check_category_status(cat_id)
        
        if status == 'active':
            # 存在有效日程，报错拦截
            self._show_tooltip("🚫 该清单存在有效日程，无法删除！", is_error=True)
            
        elif status == 'historical':
            # 存在历史日程，二次确认
            reply = QMessageBox.question(
                self, '确认删除', 
                f"清单【#{cat_id:03d} {cat_name}】包含历史日程。\n删除后这些日程将标记为已删除状态。\n是否继续？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                if db_manager.soft_delete_category(cat_id):
                    # 如果删除的是当前选中的，重置选中状态
                    if self.selected_cat_id == cat_id:
                        self.selected_cat_id = None
                    self.load_data(self.selected_cat_id)
                else:
                    self._show_tooltip("❌ 删除失败", is_error=True)
                
        else: # empty
            # 空清单，直接物理删除，不留垃圾数据
            if db_manager.hard_delete_category(cat_id):
                if self.selected_cat_id == cat_id:
                    self.selected_cat_id = None
                self.load_data(self.selected_cat_id)
            else:
                self._show_tooltip("❌ 删除失败", is_error=True)

    def _on_card_clicked(self, cat_id):
        if self.selected_cat_id == cat_id:
            self.selected_cat_id = None
        else:
            self.selected_cat_id = cat_id
        self.load_data(self.selected_cat_id)

    def _on_confirm(self):
        # 将最终选定的清单 ID 传回给上一级
        self.confirm_requested.emit(self.selected_cat_id)

    def _show_tooltip(self, text, is_error=False):
        color = "#ff4d4f" if is_error else "#0cc0df"
        tooltip = CustomToolTip(text, self, border_color=color)
        global_pos = self.mapToGlobal(QPoint(0, 0))
        x = global_pos.x() + (self.width() - tooltip.sizeHint().width()) // 2
        y = global_pos.y() + (self.height() - tooltip.sizeHint().height()) // 2
        tooltip.show_at(QPoint(x, y))

    def _setup_window_controls(self):
        """使用绝对定位在页面上方悬浮生成挂起和关闭按钮"""
        from PyQt6.QtWidgets import QPushButton, QToolButton
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        from ..utils.styles import StyleManager

        # 1. 挂起按钮 (绝对定位居中)
        self.btn_suspend = QPushButton(self)
        self.btn_suspend.setFixedSize(30, 30)
        self.btn_suspend.setIcon(QIcon("assets/icons/hang_up.png"))
        self.btn_suspend.setIconSize(QSize(20, 20))
        self.btn_suspend.setStyleSheet("QPushButton { background: transparent; border: none; }")
        self.btn_suspend.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_suspend.clicked.connect(self.suspend_requested.emit)

        # 2. 关闭按钮 (绝对定位右上角)
        self.btn_close = QToolButton(self)
        self.btn_close.setIcon(QIcon("assets/icons/close.png"))
        self.btn_close.setIconSize(QSize(16, 16))
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.setStyleSheet(StyleManager.get_window_control_style(is_close=True))
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        # 直接调用最顶层窗口的关闭事件
        self.btn_close.clicked.connect(lambda: self.window().close())

    def resizeEvent(self, event):
        """当窗口大小变化时，自动吸附按钮到顶部边缘"""
        super().resizeEvent(event)
        if hasattr(self, 'btn_suspend'):
            self.btn_suspend.move((self.width() - 30) // 2, 0)
            self.btn_suspend.raise_() # 确保在最上层，防止被遮挡
        if hasattr(self, 'btn_close'):
            self.btn_close.move(self.width() - 30, 0)
            self.btn_close.raise_()

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