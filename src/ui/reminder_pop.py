# src/ui/reminder_pop.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF, QPoint, QSize
from PyQt6.QtGui import QPainter, QPainterPath, QBrush, QLinearGradient, QColor, QIcon
from qframelesswindow import FramelessWindow
from ..utils.win_api import apply_24h2_border_fix
from ..config import AppConfig
from datetime import datetime
import winsound 
import traceback # 引入这个以便打印报错信息

class ReminderPop(FramelessWindow):
    """
    提醒弹窗：修复了倒计时卡死问题，关闭按钮改为绝对定位（贴死右上角）
    """
    def __init__(self, schedule_data, parent=None):
        super().__init__(parent=parent)
        self.data = schedule_data
        self.is_alarm_on = self.data.get('is_alarm', False)
        
        self.drag_pos = None 
        
        self.setFixedSize(320, 180) 
        
        self.titleBar.hide()
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.win_id = int(self.winId())
        apply_24h2_border_fix(self.win_id)
        
        self._init_ui()
        
        # 按钮放在 _init_ui 之后初始化，确保层级在最上
        self._init_close_btn()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_countdown)
        self.timer.start(1000)
        # 先手动调用一次，避免界面刚出来时显示 --:--:--
        self._update_countdown()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        # 顶部边距加大到 35，给右上角的关闭按钮腾出空间，防止文字被遮挡
        main_layout.setContentsMargins(15, 35, 15, 20)
        main_layout.setSpacing(5)
        
        # --- 移除了原本的 top_row 布局，改为绝对定位 ---
        
        # 标题
        self.lbl_title = QLabel(self.data.get('title', '日程提醒'))
        self.lbl_title.setStyleSheet("color: white; font-size: 22px; font-weight: bold; font-family: 'Microsoft YaHei';")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setWordWrap(True)
        main_layout.addWidget(self.lbl_title)
        
        # 倒计时
        self.lbl_countdown = QLabel("--:--:--")
        self.lbl_countdown.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 32px; font-weight: bold; font-family: 'Segoe UI';")
        self.lbl_countdown.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.lbl_countdown)
        
        main_layout.addStretch()
        
        # 底部按钮组
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        # 关闭闹钟按钮
        self.btn_stop_alarm = QPushButton("关闭闹钟")
        self.btn_stop_alarm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop_alarm.setFixedHeight(34)
        self.btn_stop_alarm.setStyleSheet("""
            QPushButton { background-color: rgba(255, 255, 255, 0.2); border-radius: 17px; color: white; border: 1px solid white; font-weight: bold;}
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.3); }
        """)
        self.btn_stop_alarm.clicked.connect(self._stop_alarm)
        
        if not self.is_alarm_on:
            self.btn_stop_alarm.hide()
            
        # 知道了按钮
        self.btn_close = QPushButton("知道了")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setFixedHeight(34)
        self.btn_close.setStyleSheet("""
            QPushButton { background-color: white; border-radius: 17px; color: #0cc0df; font-weight: bold;}
            QPushButton:hover { background-color: #f0f0f0; }
        """)
        self.btn_close.clicked.connect(self.close)
        
        btn_layout.addWidget(self.btn_stop_alarm)
        btn_layout.addWidget(self.btn_close)
        
        main_layout.addLayout(btn_layout)

    def _init_close_btn(self):
        # 关闭按钮不再放入布局，而是直接作为窗口子控件
        self.btn_top_close = QPushButton(self) # Parent 设为 self
        self.btn_top_close.setFixedSize(30, 30)
        self.btn_top_close.setIcon(QIcon("assets/icons/close.png"))
        self.btn_top_close.setIconSize(QSize(12, 12))
        self.btn_top_close.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 写死样式，确保背景透明，悬停变红
        self.btn_top_close.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none;
                border-radius: 0px; /* 贴角可以不用圆角，或者保留 */
                border-top-right-radius: 12px; /* 如果窗口是圆角，这里适配一下 */
            }
            QPushButton:hover {
                background-color: #ff4d4f;
                border-top-right-radius: 12px;
            }
            QPushButton:pressed {
                background-color: #d9363e;
            }
        """)
        self.btn_top_close.clicked.connect(self.close)
        # 初始位置设为右上角
        self.btn_top_close.move(self.width() - 30, 0)

    # 在窗口大小变化时，强制把按钮钉在右上角
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'btn_top_close'):
            self.btn_top_close.move(self.width() - 30, 0)
            self.btn_top_close.raise_() # 确保在最上层

    def mousePressEvent(self, event):
        # 只有按住非按钮区域才能拖动
        child = self.childAt(event.pos())
        if child == self.btn_top_close:
            return # 如果点的是关闭按钮，不触发拖动
            
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def _update_countdown(self):
        # 增加防卡死逻辑
        try:
            target = self.data.get('target_time')
            if not target:
                self.lbl_countdown.setText("00:00:00")
                return
                
            now = datetime.now()
            # 防止 naive 和 aware 时间相减报错
            if target.tzinfo is None and now.tzinfo is not None:
                now = now.replace(tzinfo=None)
            elif target.tzinfo is not None and now.tzinfo is None:
                target = target.replace(tzinfo=None)

            delta = target - now
            
            if delta.total_seconds() < 0:
                self.lbl_countdown.setText("已开始")
            else:
                total_seconds = int(delta.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                self.lbl_countdown.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        except Exception as e:
            print(f"倒计时逻辑错误: {e}")
            traceback.print_exc() 
            # 即使报错也不要卡死界面
            self.lbl_countdown.setText("Error")

    def _stop_alarm(self):
        print(">> 🔕 闹钟声音已停止")
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except:
            pass
        self.is_alarm_on = False
        self.btn_stop_alarm.hide() 

    def closeEvent(self, event):
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except:
            pass
        super().closeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path.addRoundedRect(rect, 12.0, 12.0)
        
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(12, 192, 223, 235)) 
        gradient.setColorAt(1.0, QColor(19, 194, 224, 245))
        
        painter.fillPath(path, QBrush(gradient))