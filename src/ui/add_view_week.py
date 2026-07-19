# src/ui/add_view_week.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QListView, 
                             QFrame, QTextEdit, QStackedWidget, QStyle,
                             QStyleOptionComboBox, QStylePainter)
from PyQt6.QtCore import Qt, QSize, QEvent, QObject, pyqtSignal, QTimer, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QImage, QPen
from PyQt6.QtSvg import QSvgRenderer
from ..config import AppConfig
from ..data.database import db_manager


class CenteredComboBox(QComboBox):
    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionComboBox()
        self.initStyleOption(option)
        current_text = self.currentText().strip()
        option.currentText = ""
        painter.drawComplexControl(QStyle.ComplexControl.CC_ComboBox, option)
        text_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_ComboBox,
            option,
            QStyle.SubControl.SC_ComboBoxEditField,
            self,
        )
        painter.setPen(QColor("#ffffff"))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, current_text)

class CustomToolTip(QLabel):
    def __init__(self, text, parent=None, border_color=None):
        super().__init__(parent, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setText(text)
        self.border_color = border_color or AppConfig.COLOR_GRADIENT_START
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setStyleSheet("""
            color: #333333;
            font-family: "Microsoft YaHei UI";
            font-size: 12px;
            padding: 6px 10px;
        """)

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
        QTimer.singleShot(500, self.close)

class ToolTipFilter(QObject):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.tooltip = None
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.show_tooltip)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Enter:
            self.timer.start(400)
            return True
        elif event.type() == QEvent.Type.Leave:
            self.timer.stop()
            self._close_tooltip()
            return True
        elif event.type() == QEvent.Type.MouseButtonPress:
            self.timer.stop()
            self._close_tooltip()
            return False
        elif event.type() == QEvent.Type.Hide or event.type() == QEvent.Type.FocusOut:
            self.timer.stop()
            self._close_tooltip()
            return False
        return False

    def show_tooltip(self):
        from PyQt6.QtGui import QCursor
        if not self.tooltip:
            self.tooltip = CustomToolTip(self.text)
        self.tooltip.show_at(QCursor.pos() + QPoint(10, 10))

    def _close_tooltip(self):
        if self.tooltip:
            self.tooltip.close()
            self.tooltip = None

class AddScheduleViewWeek(QWidget):
    saved = pyqtSignal() 
    req_open_time_picker = pyqtSignal(object, object) 
    req_open_alarm_picker = pyqtSignal(object, bool, int)
    req_open_list_picker = pyqtSignal(object) 
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_schedule_mode = True 
        
        self.selected_start_time = None
        self.selected_end_time = None
        self.selected_list_id = None 
        self.selected_reminder = None   
        self.is_alarm_mode = False      
        self.alarm_duration = 0         
        
        self._init_widgets()
        self._setup_layout_structure()
        self._connect_signals()
        self._update_mode_ui()
        self._update_info_card() 

    def _init_widgets(self):
        # 1. 标题与切换按钮
        self.lbl_title = QLabel("添加新日程")
        self.lbl_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; font-family: 'Microsoft YaHei';")
        
        self.btn_type_toggle = QPushButton("日程")
        self.btn_type_toggle.setFixedSize(60, 26)
        self.btn_type_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_type_toggle.setStyleSheet("""
            QPushButton {
                background-color: transparent; border: 1px solid white; border-radius: 13px;
                color: white; font-size: 12px; font-weight: bold; font-family: 'Microsoft YaHei';
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }
        """)

        # 2. 标题输入框
        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText("请输入标题")
        self.input_title.setFixedHeight(45)
        self.input_title.setStyleSheet("""
            QLineEdit {
                background: transparent; border: none; border-bottom: 1px solid rgba(255, 255, 255, 0.5); 
                color: white; font-size: 16px; padding: 0 5px; font-family: 'Microsoft YaHei';
            }
            QLineEdit::placeholder { color: rgba(255, 255, 255, 0.6); }
            QLineEdit:focus { border-bottom: 2px solid white; }
        """)

        # 3. 功能图标
        self.btn_detail = self._create_icon_btn("edit.svg", "添加/隐藏详情")
        self.btn_time = self._create_icon_btn("time.svg", "设置时间")
        self.btn_alarm = self._create_icon_btn("alarm.svg", "设置提醒")
        self.btn_list = self._create_icon_btn("list.svg", "添加到清单")
        self.btn_font = self._create_icon_btn("theme.svg", "设置字体")
        self.btn_alarm.setGraphicsEffect(self._get_opacity_effect(0.5))

        # 4. 详情输入区
        self.txt_details = QTextEdit()
        self.txt_details.setPlaceholderText("添加描述 (150字以内)...")
        self.txt_details.setStyleSheet("""
            QTextEdit { 
                background-color: rgba(255, 255, 255, 0.05); 
                border: 1px solid rgba(255, 255, 255, 0.3); 
                border-radius: 8px; color: white; font-size: 13px; 
                font-family: 'Microsoft YaHei'; padding: 10px; 
            }
            QTextEdit:focus { border: 1px solid rgba(255, 255, 255, 0.6); background-color: rgba(255, 255, 255, 0.1); }
        """)
        self.lbl_char_count = QLabel("0/150")
        self.lbl_char_count.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 12px;")

        # 5. 重要性与重复 
        self.priority_container, self.combo_priority = self._create_property_group("重要性：", ["   低", "   中", "   高"])
        self.repeat_container, self.combo_repeat = self._create_property_group("重复：", ["   无", "  每天", "  每周", "  每月"])

        # 6. 信息结果卡片 
        self.info_card = QFrame()
        self.info_card.setObjectName("InfoCard") 
        self.info_card.setStyleSheet("""
            #InfoCard { 
                background-color: rgba(255, 255, 255, 0.05); 
                border: 1px solid rgba(255, 255, 255, 0.3); 
                border-radius: 8px; color: white; font-size: 13px; 
                padding: 10px; 
            }
        """)
        self.lbl_info_time = self._create_info_row("time.svg", "时间未设置")
        self.lbl_info_alarm = self._create_info_row("alarm.svg", "无提醒")
        self.lbl_info_list = self._create_info_row("list.svg", "未选择") 

        # 7. 底部保存与取消按键
        self.btn_cancel = self._create_footer_btn("取消", is_primary=False)
        self.btn_confirm = self._create_footer_btn("保存", is_primary=True)

    def _setup_layout_structure(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 30, 40, 30)

        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(40) 

        # --- 左侧布局 ---
        self.left_panel = QVBoxLayout()
        # 设置为0，取消全局固定间距，全靠弹簧来等分空间
        self.left_panel.setSpacing(0) 
        
        # 第一行：顶部栏
        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.lbl_title)
        self.header_layout.addStretch() 
        self.header_layout.addWidget(self.btn_type_toggle)
        self.left_panel.addLayout(self.header_layout)

        self.left_panel.addStretch(1) # 等量分割区域 1

        # 第二行：标题输入框
        self.left_panel.addWidget(self.input_title)
        
        self.left_panel.addStretch(1) # 等量分割区域 2
        
        # 第三行：图标工具栏
        self.icons_layout = QHBoxLayout()
        self.icons_layout.setContentsMargins(0, 5, 0, 5)
        self.icons_layout.addWidget(self.btn_detail)
        self.icons_layout.addStretch()
        self.icons_layout.addWidget(self.btn_time)
        self.icons_layout.addStretch()
        self.icons_layout.addWidget(self.btn_alarm)
        self.icons_layout.addStretch()
        self.icons_layout.addWidget(self.btn_list)
        self.icons_layout.addStretch()
        self.icons_layout.addWidget(self.btn_font)
        self.left_panel.addLayout(self.icons_layout)
        
        self.left_panel.addStretch(1) # 等量分割区域 3

        # 第四行：重要性与重复属性
        self.status_wrapper = QWidget()
        self.status_layout = QHBoxLayout(self.status_wrapper)
        self.status_layout.setContentsMargins(0, 0, 0, 0)
        self.status_layout.addWidget(self.priority_container) 
        self.status_layout.addStretch()                       
        self.status_layout.addWidget(self.repeat_container)   
        self.left_panel.addWidget(self.status_wrapper)

        # --- 右侧布局 ---
        self.right_panel = QVBoxLayout()
        self.right_panel.setSpacing(15) 
        
        self.right_stack = QStackedWidget()
        
        # 第0页：预览卡片
        self.page_info = QWidget()
        page_info_layout = QVBoxLayout(self.page_info)
        page_info_layout.setContentsMargins(0, 0, 0, 0)
        
        # 让卡片内部的信息均匀分布
        info_layout = QVBoxLayout(self.info_card)
        info_layout.setContentsMargins(20, 20, 20, 20) # 稍微加大内边距会更好看
        info_layout.setSpacing(10)
        info_layout.addStretch()
        info_layout.addWidget(self.lbl_info_time.row_container)
        info_layout.addWidget(self.lbl_info_alarm.row_container)
        info_layout.addWidget(self.lbl_info_list.row_container)
        info_layout.addStretch()
        
        page_info_layout.addWidget(self.info_card, stretch=1)


        placeholder_layout = QHBoxLayout()
        placeholder_lbl = QLabel("0/150") # 放同样的文本保证高度完全一样
        placeholder_lbl.setStyleSheet("color: transparent; font-size: 12px;") # 设置为全透明，肉眼看不见
        placeholder_layout.addStretch()
        placeholder_layout.addWidget(placeholder_lbl)
        
        page_info_layout.addLayout(placeholder_layout)
        
        # 第1页：详情输入框
        self.page_details = QWidget()
        page_details_layout = QVBoxLayout(self.page_details)
        page_details_layout.setContentsMargins(0, 0, 0, 0)
        page_details_layout.setSpacing(5)
        page_details_layout.addWidget(self.txt_details)
        
        count_layout = QHBoxLayout()
        count_layout.addStretch()
        count_layout.addWidget(self.lbl_char_count)
        page_details_layout.addLayout(count_layout)
        
        self.right_stack.addWidget(self.page_info)
        self.right_stack.addWidget(self.page_details)
        
        self.right_panel.addWidget(self.right_stack, stretch=1)

        # 底部按键组 (与左侧第四行处于同一水平基准)
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_cancel)
        bottom_layout.addSpacing(120)
        bottom_layout.addWidget(self.btn_confirm)
        self.right_panel.addLayout(bottom_layout)

        # --- 组装左右分栏 ---
        self.content_layout.addLayout(self.left_panel, stretch=10) 
        self.content_layout.addLayout(self.right_panel, stretch=11)
        self.main_layout.addLayout(self.content_layout, stretch=1)

    def _create_info_row(self, icon_name, text):
        row_widget = QWidget()
        row_widget.setStyleSheet("background-color: transparent;")
        layout = QHBoxLayout(row_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        icon_size = 18
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(icon_size, icon_size)
        icon_lbl.setScaledContents(True)
        pm = self._load_colored_icon(icon_name, "#FFFFFF", target_size=icon_size)
        icon_lbl.setPixmap(pm)
        
        text_lbl = QLabel(text)
        text_lbl.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 13px; font-family: 'Microsoft YaHei';")
        
        layout.addWidget(icon_lbl)
        layout.addWidget(text_lbl)
        layout.addStretch()
        
        text_lbl.row_container = row_widget 
        return text_lbl

    def _load_colored_icon(self, name, color_hex, target_size=18):
        path = f"assets/icons/{name}"
        if not QSvgRenderer(path).isValid(): return QPixmap()
        renderer = QSvgRenderer(path)
        scale_ratio = 4.0
        high_res_size = int(target_size * scale_ratio)
        image = QImage(high_res_size, high_res_size, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()
        painter = QPainter(image)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(image.rect(), QColor(color_hex))
        painter.end()
        pm = QPixmap.fromImage(image)
        pm.setDevicePixelRatio(scale_ratio)
        return pm

    def _create_property_group(self, label_text, items):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: rgba(255, 255, 255, 0.9); font-size: 12px; font-family: 'Microsoft YaHei'; font-weight: bold;")
        
        combo = CenteredComboBox()
        combo.addItems([item.strip() for item in items])
        for index in range(combo.count()):
            combo.setItemData(
                index,
                Qt.AlignmentFlag.AlignCenter,
                Qt.ItemDataRole.TextAlignmentRole,
            )
        combo.setFixedSize(65, 26)
        combo.setCursor(Qt.CursorShape.PointingHandCursor)
        combo.setView(QListView())
        combo.setStyleSheet("""
            QComboBox { background-color: transparent; border: 1px solid rgba(255, 255, 255, 0.7); color: #ffffff; border-radius: 4px; padding-left: 0px; font-family: 'Microsoft YaHei'; font-size: 12px; }
            QComboBox:hover { background-color: rgba(255, 255, 255, 0.1); border: 1px solid #ffffff; }
            QComboBox::drop-down { border: none; width: 0px; }
            QListView { background-color: #ffffff; color: #333333; border: 1px solid #dddddd; outline: 0px; }
            QListView::item { background-color: #ffffff; color: #333333; padding: 4px 8px; }
            QListView::item:selected { background-color: #0cc0df; color: #ffffff; }
            QListView::item:hover { background-color: #f0f0f0; color: #333333; }
        """)
        layout.addWidget(lbl)
        layout.addWidget(combo)
        return container, combo

    def _create_icon_btn(self, icon_name, tooltip_text):
        btn = QPushButton()
        btn.setFixedSize(30, 30)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn._tooltip_filter = ToolTipFilter(tooltip_text, btn)
        btn.installEventFilter(btn._tooltip_filter)
        btn.setIcon(QIcon(f"assets/icons/{icon_name}"))
        btn.setIconSize(QSize(22, 22))
        btn.setStyleSheet("""
            QPushButton { background-color: transparent; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }
        """)
        return btn

    def _create_footer_btn(self, text, is_primary=False):
        btn = QPushButton(text)
        btn.setFixedSize(80, 32)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if is_primary:
            btn.setStyleSheet(f"QPushButton {{ background-color: white; border: none; border-radius: 16px; color: {AppConfig.COLOR_GRADIENT_START}; font-size: 13px; font-weight: bold; font-family: 'Microsoft YaHei'; }} QPushButton:hover {{ background-color: #f2f2f2; }}")
        else:
            btn.setStyleSheet("QPushButton { background-color: transparent; border: 1px solid rgba(255, 255, 255, 0.7); border-radius: 16px; color: white;font-weight: bold; font-size: 13px; font-family: 'Microsoft YaHei'; } QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); border: 1px solid white; }")
        return btn

    def _connect_signals(self):
        self.btn_type_toggle.clicked.connect(self._toggle_mode)
        self.btn_confirm.clicked.connect(self._on_save)
        self.btn_cancel.clicked.connect(self.reset)
        
        self.btn_time.clicked.connect(self._emit_time_request)
        self.btn_alarm.clicked.connect(self._emit_alarm_request)
        self.btn_list.clicked.connect(self._emit_list_request)
        
        # 绑定详情按钮点击事件，切换右侧显示区域
        self.btn_detail.clicked.connect(self._toggle_details_view)
        self.txt_details.textChanged.connect(self._on_text_changed)

    def _toggle_details_view(self):
        # 如果当前是预览（0），切换到详情（1）
        current_idx = self.right_stack.currentIndex()
        if current_idx == 0:
            self.right_stack.setCurrentIndex(1)
            self.txt_details.setFocus()
        else:
            self.right_stack.setCurrentIndex(0)

    def _emit_list_request(self):
        self.req_open_list_picker.emit(self.selected_list_id)

    def set_list_data(self, category_id):
        self.selected_list_id = category_id
        self._update_info_card()

    def _on_text_changed(self):
        text = self.txt_details.toPlainText()
        length = len(text)
        if length > 150:
            text = text[:150]
            self.txt_details.setPlainText(text)
            cursor = self.txt_details.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.txt_details.setTextCursor(cursor)
            length = 150
        self.lbl_char_count.setText(f"{length}/150")

    def _emit_time_request(self):
        self.req_open_time_picker.emit(self.selected_start_time, self.selected_end_time)

    def _emit_alarm_request(self):
        if not self.selected_start_time and not self.selected_end_time:
            tooltip = CustomToolTip("⚠️ 请先设置计划时间", self, border_color="#ff4d4f")
            global_pos = self.btn_alarm.mapToGlobal(QPoint(0, 0))
            #local_pos = self.mapFromGlobal(global_pos)
            tooltip.show_at(global_pos + QPoint(-10, -35)) 
            return

        target_time = self.selected_start_time if self.selected_start_time else self.selected_end_time
        self.req_open_alarm_picker.emit(target_time, self.is_alarm_mode, self.alarm_duration)

    def set_alarm_data(self, remind_dt, is_alarm, duration_mode):
        self.selected_reminder = remind_dt
        self.is_alarm_mode = is_alarm
        self.alarm_duration = duration_mode
        self._update_info_card()

    def set_time_data(self, start, end):
        self.selected_start_time = start
        self.selected_end_time = end
        
        if start or end:
            self.btn_alarm.setGraphicsEffect(self._get_opacity_effect(1.0))
        else:
            self.btn_alarm.setGraphicsEffect(self._get_opacity_effect(0.5))
            
        self._update_info_card()

    def _format_time_range(self, start, end):
        """格式化时间范围显示。同天：MM-DD S - E；跨天同年：MM-DD S - MM-DD E；跨年：YY-MM-DD S - YY-MM-DD E"""
        if not end:
            return None
        start = start or end
        if start.date() == end.date():
            return f"{start:%m-%d %H:%M} - {end:%H:%M}"
        if start.year == end.year:
            return f"{start:%m-%d %H:%M} - {end:%m-%d %H:%M}"
        return f"{start:%y-%m-%d %H:%M} - {end:%y-%m-%d %H:%M}"

    def _update_info_card(self):
        if self.selected_end_time:
            if self.selected_start_time:
                text = self._format_time_range(self.selected_start_time, self.selected_end_time)
            else:
                text = f"{self.selected_end_time:%m-%d} 截止: {self.selected_end_time:%H:%M}"
            self.lbl_info_time.setText(text)
            if len(text) > 18:
                fs = "10px"
            elif len(text) > 14:
                fs = "12px"
            else:
                fs = "14px"
            self.lbl_info_time.setStyleSheet(
                f"color: #FFFFFF; font-weight: bold; font-size: {fs};"
            ) 
        else:
            self.lbl_info_time.setText("时间未设置")
            self.lbl_info_time.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 13px;") 

        if self.selected_reminder:
            remind_str = self.selected_reminder.strftime("%m-%d %H:%M")
            icon_prefix = "" if self.is_alarm_mode else ""
            self.lbl_info_alarm.setText(f"{icon_prefix}{remind_str}")
            self.lbl_info_alarm.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 14px;") 
        else:
            self.lbl_info_alarm.setText("无提醒")
            self.lbl_info_alarm.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 13px;")
            
        if self.selected_list_id:
            cat = db_manager.get_category(self.selected_list_id)
            if cat:
                list_text = f"#{cat.id:03d} {cat.name}"
            else:
                list_text = "未选择"
        else:
            list_text = "未选择"
        
        self.lbl_info_list.setText(list_text)

    def _get_opacity_effect(self, opacity):
        from PyQt6.QtWidgets import QGraphicsOpacityEffect
        eff = QGraphicsOpacityEffect(self)
        eff.setOpacity(opacity)
        return eff

    def _update_mode_ui(self):
        if self.is_schedule_mode:
            self.lbl_title.setText("添加新日程")
            self.btn_type_toggle.setText("日程")
            self.status_wrapper.show()
            self.info_card.show()
        else:
            self.lbl_title.setText("添加新待办")
            self.btn_type_toggle.setText("待办")
            self.status_wrapper.hide()
            self.info_card.hide()

        self._clear_layout(self.icons_layout)
        self.btn_detail.show()
        self.btn_font.show()
        
        if self.is_schedule_mode:
            self.btn_time.show()
            self.btn_alarm.show()
            self.btn_list.show()
            self.icons_layout.addWidget(self.btn_detail)
            self.icons_layout.addStretch()
            self.icons_layout.addWidget(self.btn_time)
            self.icons_layout.addStretch()
            self.icons_layout.addWidget(self.btn_alarm)
            self.icons_layout.addStretch()
            self.icons_layout.addWidget(self.btn_list)
            self.icons_layout.addStretch()
            self.icons_layout.addWidget(self.btn_font)
        else:
            self.btn_time.hide()
            self.btn_alarm.hide()
            self.btn_list.hide()
            self.icons_layout.addWidget(self.btn_detail)
            self.icons_layout.addSpacing(20)
            self.icons_layout.addWidget(self.btn_font)
            self.icons_layout.addStretch()

    def _clear_layout(self, layout):
        while layout.count():
            layout.takeAt(0)

    def _toggle_mode(self):
        self.is_schedule_mode = not self.is_schedule_mode
        self._update_mode_ui()

    def reset(self):
        self.input_title.clear()           
        self.combo_priority.setCurrentIndex(0) 
        self.combo_repeat.setCurrentIndex(0)   
        self.txt_details.clear()
        
        self.selected_start_time = None
        self.selected_end_time = None
        self.selected_list_id = None
        self.selected_reminder = None 
        self.is_alarm_mode = False
        self.alarm_duration = 0
        
        self.btn_time.setStyleSheet("background-color: transparent; border: none; border-radius: 4px;")
        self.btn_alarm.setGraphicsEffect(self._get_opacity_effect(0.5))
        
        self.is_schedule_mode = True
        self.right_stack.setCurrentIndex(0) # 重置时确保右侧切回预览卡片状态
        self._update_mode_ui()
        self._update_info_card() 

    def _on_save(self):
        title = self.input_title.text().strip()
        if not title:
            print("❌ 标题不能为空")
            tooltip = CustomToolTip("⚠️ 标题不能为空", self, border_color="#ff4d4f")
            global_pos = self.input_title.mapToGlobal(QPoint(0, 0))
            tooltip.show_at(global_pos + QPoint(70, -35))
            return
        if self.is_schedule_mode and not self.selected_start_time and not self.selected_end_time:
            print("❌ 日程必须设置时间")
            tooltip = CustomToolTip("⚠️ 请先设置计划时间\n如果不设时间请切换到待办", self, border_color="#ff4d4f")
            
            # 定位到时间按钮上方弹出提示
            global_pos = self.btn_time.mapToGlobal(QPoint(0, 0))
            tooltip.show_at(global_pos + QPoint(-10, -45))
            return

        item_type = 'schedule' if self.is_schedule_mode else 'todo'
        priority = self.combo_priority.currentIndex()
        repeat_text = self.combo_repeat.currentText().strip()
        description = self.txt_details.toPlainText().strip()
        
        schedule_data = {
            'title': title,
            'item_type': item_type,
            'priority': priority,
            'repeat_rule': repeat_text,
            'description': description, 
            'start_time': self.selected_start_time,
            'end_time': self.selected_end_time,
            'reminder_time': self.selected_reminder,
            'is_alarm': self.is_alarm_mode,
            'alarm_duration': self.alarm_duration,
            'category_id': self.selected_list_id
        }

        if db_manager.add_schedule(schedule_data):
            self.saved.emit() 
            self.reset()
        else:
            print("❌ [DB] 保存失败")
