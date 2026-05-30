from PyQt6.QtCore import QObject, pyqtSignal


class AppSignals(QObject):
    # Legacy signal must remain no-arg for compatibility.
    skin_changed = pyqtSignal()

    # Event bus channels for new architecture layers.
    theme_changed = pyqtSignal(str)
    schedule_added = pyqtSignal(object)
    schedule_updated = pyqtSignal(object)
    schedule_deleted = pyqtSignal(int)
    category_changed = pyqtSignal()
    refresh_requested = pyqtSignal(str)


global_signals = AppSignals()
