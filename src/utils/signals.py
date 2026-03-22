# src/utils/signals.py
from PyQt6.QtCore import QObject, pyqtSignal

class AppSignals(QObject):
    # 定义一个信号：当皮肤改变时触发
    skin_changed = pyqtSignal()

# 创建全局单例实例
global_signals = AppSignals()
