from PyQt6.QtWidgets import QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal


class AddFolderCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
            QFrame:hover {
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(45, 45)

        # 延迟导入以避免与 src.ui.todo_board 的模块级相互导入触发循环。
        from ..todo_board import get_colored_icon
        pixmap = get_colored_icon("folder_add.svg", "#FFFFFF", 45)
        if not pixmap.isNull():
            self.icon_label.setPixmap(pixmap)
        else:
            self.icon_label.setText("➕")
            self.icon_label.setStyleSheet("font-size: 40px; color: white; background: transparent; border: none;")

        self.name_label = QLabel("新建清单")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px; font-family: 'Microsoft YaHei'; border: none; background: transparent;")

        layout.addWidget(self.icon_label, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.name_label, 0, Qt.AlignmentFlag.AlignHCenter)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            event.accept()
