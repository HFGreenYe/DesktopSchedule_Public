from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QLabel


def show_center_toast(parent, message, attr_name="toast_label", duration_ms=500):
    existing = getattr(parent, attr_name, None)
    if existing is not None and existing.isVisible():
        existing.close()

    label = QLabel(message, parent)
    label.setStyleSheet(
        """
            background-color: rgba(0, 0, 0, 0.75);
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            font-family: 'Microsoft YaHei';
            font-size: 14px;
            font-weight: bold;
        """
    )
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.adjustSize()
    label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    x = (parent.width() - label.width()) // 2
    y = (parent.height() - label.height()) // 2
    label.move(x, y)
    label.show()

    setattr(parent, attr_name, label)
    QTimer.singleShot(duration_ms, label.close)
    return label
