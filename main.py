# src/main.py
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from src.theme import ThemeManager
from src.ui.main_window import MainWindow
from src.ui.popups.commemoration_day_panel import show_commemoration_day_panel
from src.utils.commemoration_preferences import get_due_commemoration_dates


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Lankor Schedule")
    
    app.setStyle("Fusion")
    theme_manager = ThemeManager()
    theme_manager.apply_theme(app, ThemeManager.DEFAULT_PRESET)
    
    window = MainWindow()
    window.show()
    if get_due_commemoration_dates():
        QTimer.singleShot(
            0,
            lambda: show_commemoration_day_panel(window),
        )
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
