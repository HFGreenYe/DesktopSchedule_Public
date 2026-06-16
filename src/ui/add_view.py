# src/ui/add_view.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QListView, 
                             QFrame, QTextEdit, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, QEvent, QObject, pyqtSignal, QTimer, QRectF, QPoint
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QImage, QPen
from PyQt6.QtSvg import QSvgRenderer
from ..data.database import db_manager


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

class AddScheduleView(QWidget):
    saved = pyqtSignal() 
    req_open_time_picker = pyqtSignal(object, object) 
    req_open_alarm_picker = pyqtSignal(object, bool, int)
    req_open_list_picker = pyqtSignal(object, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_schedule_mode = True 
        self.drag_pos = None 
        
        self.selected_start_time = None
        self.selected_end_time = None
        
        # 保存清单的 ID，而不是名字
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
        # Header
        self.lbl_title = QLabel("添加新日程")
        self.lbl_title.setStyleSheet("color: white; font-size: 24px; font-weight: bold; font-family: 'Microsoft YaHei';")
        
        self.btn_type_toggle = QPushButton("日程")
        self.btn_type_toggle.setFixedSize(60, 28)
        self.btn_type_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_type_toggle.setStyleSheet("""
            QPushButton {
                background-color: transparent; border: 1px solid white; border-radius: 14px;
                color: white; font-size: 13px; font-weight: bold; font-family: 'Microsoft YaHei';
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }
        """)

        # Input
        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText("请输入标题")
        self.input_title.setFixedHeight(50)
        self.input_title.setStyleSheet("""
            QLineEdit {
                background: transparent; border: none; border-bottom: 1px solid rgba(255, 255, 255, 0.5); 
                color: white; font-size: 18px; padding: 0 5px; font-family: 'Microsoft YaHei';
            }
            QLineEdit::placeholder { color: rgba(255, 255, 255, 0.6); }
            QLineEdit:focus { border-bottom: 2px solid white; }
        """)

        # Icons
        self.btn_detail = self._create_icon_btn("edit.svg", "填写详情")
        self.btn_time = self._create_icon_btn("time.svg", "设置时间")
        self.btn_alarm = self._create_icon_btn("alarm.svg", "设置提醒")
        self.btn_list = self._create_icon_btn("list.svg", "添加到清单")
        self.btn_font = self._create_icon_btn("theme.svg", "设置字体")

        self.btn_alarm.setGraphicsEffect(self._get_opacity_effect(0.5))

        # Details
        self.details_container = QWidget()
        self.details_container.hide() 
        
        self.txt_details = QTextEdit()
        self.txt_details.setPlaceholderText("添加描述 (150字以内)...")
        self.txt_details.setFixedHeight(80) 
        self.txt_details.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.txt_details.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.txt_details.setStyleSheet("""
            QTextEdit { background-color: rgba(0, 0, 0, 0.08); border: 1px solid rgba(255, 255, 255, 0.35); border-radius: 8px; color: white; font-size: 14px; font-family: 'Microsoft YaHei'; padding: 8px; }
            QTextEdit:focus { border: 1px solid rgba(255, 255, 255, 0.6); background-color: rgba(0, 0, 0, 0.12); }
        """)
        
        self.details_bottom_widget = QWidget()
        details_btn_layout = QHBoxLayout(self.details_bottom_widget)
        details_btn_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_char_count = QLabel("0/150")
        self.lbl_char_count.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 12px;")
        
        self.btn_collapse_details = QPushButton("收起")
        self.btn_collapse_details.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_collapse_details.setFixedSize(50, 24)
        self.btn_collapse_details.setStyleSheet("""
            QPushButton { background: transparent; color: rgba(255,255,255,0.8); border: 1px solid rgba(255,255,255,0.3); border-radius: 12px; font-size: 12px; }
            QPushButton:hover { background: rgba(255,255,255,0.1); color: white; }
        """)
        
        details_btn_layout.addWidget(self.lbl_char_count)
        details_btn_layout.addStretch()
        details_btn_layout.addWidget(self.btn_collapse_details)

        # Properties
        self.priority_container, self.combo_priority = self._create_property_group("重要性：", ["   低", "   中", "   高"])
        self.repeat_container, self.combo_repeat = self._create_property_group("重复：", ["   无", "  每天", "  每周", "  每月"])

        # Info Card
        self.info_card = QFrame()
        self.info_card.setObjectName("InfoCard")
        self.info_card.setStyleSheet("#InfoCard { background-color: transparent; }")
        
        self.lbl_info_time = self._create_info_row("time.svg", "时间未设置")
        self.lbl_info_alarm = self._create_info_row("alarm.svg", "无提醒")
        self.lbl_info_list = self._create_info_row("list.svg", "未选择") 

        # 重要性显示行 
        self.lbl_info_priority = self._create_info_row("importance.svg", "低重要性") 

        self.lbl_info_priority.setCursor(Qt.CursorShape.PointingHandCursor)

        self.lbl_info_priority.mousePressEvent = self._toggle_priority_inline

        # Footer
        self.btn_cancel = self._create_footer_btn("取消", is_primary=False)
        self.btn_confirm = self._create_footer_btn("保存", is_primary=True)

    def _create_info_row(self, icon_name, text):
        row_widget = QWidget()
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
        text_lbl.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 14px; font-family: 'Microsoft YaHei';")
        
        layout.addWidget(icon_lbl)
        layout.addWidget(text_lbl)
        layout.addStretch()
        
        text_lbl.row_container = row_widget 
        return text_lbl

    def _setup_layout_structure(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 40, 30, 30)
        self.main_layout.setSpacing(10)

        # Header
        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.lbl_title)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.btn_type_toggle)
        self.main_layout.addLayout(self.header_layout)

        self.main_layout.addSpacing(10)

        # Scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(20) 

        self.scroll_layout.addWidget(self.input_title)
        
        self.icons_layout = QHBoxLayout()
        self.icons_layout.setContentsMargins(0, 0, 0, 0)
        self.icons_layout.setSpacing(0)
        self.scroll_layout.addLayout(self.icons_layout)

        d_layout = QVBoxLayout(self.details_container)
        d_layout.setContentsMargins(0, 0, 0, 0)
        d_layout.setSpacing(5)
        d_layout.addWidget(self.txt_details)
        d_layout.addWidget(self.details_bottom_widget)
        self.scroll_layout.addWidget(self.details_container)

        self.status_wrapper = QWidget()
        self.status_layout = QHBoxLayout(self.status_wrapper)
        self.status_layout.setContentsMargins(0, 0, 0, 0)
        self.status_layout.setSpacing(0) 
        self.status_layout.addWidget(self.priority_container) 
        self.status_layout.addStretch()                       
        self.status_layout.addWidget(self.repeat_container)   
        self.scroll_layout.addWidget(self.status_wrapper)

        info_layout = QVBoxLayout(self.info_card)
        info_layout.setContentsMargins(3, 12, 15, 12)
        info_layout.setSpacing(8)
        info_layout.addWidget(self.lbl_info_time.row_container)
        info_layout.addWidget(self.lbl_info_alarm.row_container)
        info_layout.addWidget(self.lbl_info_priority.row_container)
        info_layout.addWidget(self.lbl_info_list.row_container)
        self.scroll_layout.addWidget(self.info_card)

        self.scroll_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        # Footer
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)
        bottom_layout.setContentsMargins(0, 10, 0, 0)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_cancel)
        bottom_layout.addWidget(self.btn_confirm)
        self.main_layout.addLayout(bottom_layout)

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
        lbl.setStyleSheet("color: rgba(255, 255, 255, 0.9); font-size: 13px; font-family: 'Microsoft YaHei'; font-weight: bold;")
        
        combo = QComboBox()
        combo.addItems(items)
        combo.setFixedSize(60, 26)
        combo.setCursor(Qt.CursorShape.PointingHandCursor)
        combo.setView(QListView())
        combo.setStyleSheet("""
            QComboBox { background-color: transparent; border: 1px solid rgba(255, 255, 255, 0.7); color: #ffffff; border-radius: 4px; padding-left: 10px; font-family: 'Microsoft YaHei'; font-size: 12px; }
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
        btn.setFixedSize(32, 32)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn._tooltip_filter = ToolTipFilter(tooltip_text, btn)
        btn.installEventFilter(btn._tooltip_filter)
        
        btn.setIcon(QIcon(f"assets/icons/{icon_name}"))
        btn.setIconSize(QSize(24, 24))
        btn.setStyleSheet("""
            QPushButton { background-color: transparent; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }
        """)
        return btn

    def _create_footer_btn(self, text, is_primary=False):
        btn = QPushButton(text)
        btn.setFixedSize(72, 30)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if is_primary:
            btn.setStyleSheet("QPushButton { background-color: white; border: none; border-radius: 15px; color: #0cc0df; font-size: 13px; font-weight: bold; font-family: 'Microsoft YaHei'; } QPushButton:hover { background-color: #f2f2f2; }")
        else:
            btn.setStyleSheet("QPushButton { background-color: transparent; border: 1px solid rgba(255, 255, 255, 0.7); border-radius: 15px; color: white;font-weight: bold; font-size: 13px; font-family: 'Microsoft YaHei'; } QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); border: 1px solid white; }")
        return btn

    def _connect_signals(self):
        self.btn_type_toggle.clicked.connect(self._toggle_mode)
        self.btn_confirm.clicked.connect(self._on_save)
        self.btn_cancel.clicked.connect(self.reset)
        self.btn_time.clicked.connect(self._emit_time_request)
        self.btn_detail.clicked.connect(self._toggle_details)
        self.btn_collapse_details.clicked.connect(self._hide_details)
        self.txt_details.textChanged.connect(self._on_text_changed)
        self.btn_alarm.clicked.connect(self._emit_alarm_request)
        
        self.btn_list.clicked.connect(self._emit_list_request)

    # 发射请求打开清单页的信号
    def _emit_list_request(self):
        current_type = 'schedule' if self.is_schedule_mode else 'todo'
        self.req_open_list_picker.emit(self.selected_list_id, current_type)

    # 接收从 Picker 返回的数据 (接收 ID)
    def set_list_data(self, category_id):
        self.selected_list_id = category_id
        self._update_info_card()

    def _toggle_details(self):
        if not self.details_container.isHidden():
            self._hide_details()
        else:
            self._show_details()

    def _show_details(self):
        self.details_container.show()
        self._update_detail_btn_state()

    def _hide_details(self):
        self.details_container.hide()
        self._update_detail_btn_state()

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
        self._update_detail_btn_state()

    def _update_detail_btn_state(self):
        is_expanded = not self.details_container.isHidden()
        
        if is_expanded:
            self.btn_detail.setStyleSheet("background-color: rgba(255, 255, 255, 0.3); border-radius: 4px;")
        else:
            self.btn_detail.setStyleSheet("background-color: transparent; border: none; border-radius: 4px;")

    def _emit_time_request(self):
        self.req_open_time_picker.emit(self.selected_start_time, self.selected_end_time)

    def _emit_alarm_request(self):
        if not self.selected_start_time and not self.selected_end_time:
            tooltip = CustomToolTip("⚠️ 请先设置计划时间", self, border_color="#ff4d4f")
            global_pos = self.btn_alarm.mapToGlobal(QPoint(0, 0))
            local_pos = self.mapFromGlobal(global_pos)
            tooltip.show_at(local_pos + QPoint(-10, -35)) 
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

    def _update_info_card(self):
        # 1. 更新时间文本
        if self.selected_end_time:
            date_str = self.selected_end_time.strftime("%m-%d")
            end_str = self.selected_end_time.strftime("%H:%M")
            if self.selected_start_time:
                start_str = self.selected_start_time.strftime("%H:%M")
                text = f"{date_str} {start_str} - {end_str}"
            else:
                text = f"{date_str} 截止: {end_str}"
            self.lbl_info_time.setText(text)
            self.lbl_info_time.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 15px;") 
        else:
            self.lbl_info_time.setText("时间未设置")
            self.lbl_info_time.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 14px;") 

        # 2. 更新提醒文本
        if self.selected_reminder:
            remind_str = self.selected_reminder.strftime("%m-%d %H:%M")
            icon_prefix = "" if self.is_alarm_mode else "🔔 "
            self.lbl_info_alarm.setText(f"{icon_prefix}{remind_str}")
            self.lbl_info_alarm.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 15px;") 
        else:
            self.lbl_info_alarm.setText("无提醒")
            self.lbl_info_alarm.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 14px;")

        # 3. 更新重要性显示 (针对待办模式)
        p_map = {0: "低重要性", 1: "中重要性", 2: "高重要性"}
        current_p = p_map.get(self.combo_priority.currentIndex(), "低重要性")
        self.lbl_info_priority.setText(f"{current_p}")

        # 4. 逻辑控制：哪些行该显示
        if self.is_schedule_mode:
             # 日程模式：显示时间、提醒、清单
             self.lbl_info_time.row_container.show()
             self.lbl_info_alarm.row_container.show()
             self.lbl_info_list.row_container.show()
             self.lbl_info_priority.row_container.hide()
             self.info_card.layout().setSpacing(8)
        else:
             # 待办模式：隐藏时间、提醒；显示重要性（点击切换）、清单（纯显示）
             self.lbl_info_time.row_container.hide()
             self.lbl_info_alarm.row_container.hide()
             self.lbl_info_priority.row_container.show()
             self.lbl_info_list.row_container.show()
             self.info_card.layout().setSpacing(20)
            
        # 5. 更新清单显示 
        list_text = "未选择"
        text_color = "rgba(255, 255, 255, 0.5)"
        font_weight = "normal"
        
        if self.selected_list_id:
            cat = db_manager.get_category(self.selected_list_id)
            if cat:
                list_text = f"#{cat.id:03d} {cat.name}"
                text_color = "#FFFFFF"
                font_weight = "bold"

        self.lbl_info_list.setText(list_text)
        self.lbl_info_list.setStyleSheet(f"""
            color: {text_color}; 
            font-weight: {font_weight}; 
            font-size: 14px; 
            font-family: 'Microsoft YaHei';
        """)
        
        

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
            self.info_card.show() 
            #self.info_card.hide() 

        self._clear_layout(self.icons_layout)
        
        self.btn_detail.show()
        self.btn_list.show()
        self.btn_font.show()
        
        if self.is_schedule_mode:
            self.btn_time.show()
            self.btn_alarm.show()

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
            # 待办模式：隐藏时间相关
            self.btn_time.hide()
            self.btn_alarm.hide()
            fixed_gap = 25
            # 待办模式布局：详情 - 弹簧 - 清单 - 弹簧 - 字体 - 结尾弹簧
            self.icons_layout.addWidget(self.btn_detail)
            self.icons_layout.addSpacing(fixed_gap)
            self.icons_layout.addWidget(self.btn_list)  # 插入清单键
            self.icons_layout.addSpacing(fixed_gap)
            self.icons_layout.addWidget(self.btn_font)
            self.icons_layout.addStretch() 

    def _clear_layout(self, layout):
        while layout.count():
            layout.takeAt(0)

    def _toggle_mode(self):
        self.is_schedule_mode = not self.is_schedule_mode
        self._update_mode_ui()
        self._update_info_card()

    def reset(self, default_to_schedule=True):
        self.input_title.clear()            
        self.combo_priority.setCurrentIndex(0) 
        self.combo_repeat.setCurrentIndex(0)   
        self.txt_details.clear()
        self.details_container.hide()
        
        self.selected_start_time = None
        self.selected_end_time = None
        
        # 重置时清空清单 ID
        self.selected_list_id = None
        
        self.selected_reminder = None 
        self.is_alarm_mode = False
        self.alarm_duration = 0
        
        self.btn_time.setStyleSheet("background-color: transparent; border: none; border-radius: 4px;")
        self.btn_alarm.setGraphicsEffect(self._get_opacity_effect(0.5))
        
        self._update_detail_btn_state()
        
        # 不再硬编码为 True，而是使用传入的参数
        self.is_schedule_mode = default_to_schedule
        self._update_mode_ui()
        self._update_info_card() 
        print(">> 界面状态已重置")

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
            print(f"✅ [DB] 写入成功 ...")
            self.saved.emit() 
            self.reset()
        else:
            print("❌ [DB] 保存失败")

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

    def _toggle_priority_inline(self, event):
        """点击信息框中的重要性，直接 0->1->2 循环切换"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 获取当前索引 (0:低, 1:中, 2:高)
            current_idx = self.combo_priority.currentIndex()
            next_idx = (current_idx + 1) % 3
        
            # 同步更新原始的下拉框
            self.combo_priority.setCurrentIndex(next_idx)
        
             # 刷新信息卡片显示
            self._update_info_card()
