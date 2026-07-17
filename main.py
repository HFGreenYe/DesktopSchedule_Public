# src/main.py
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.theme import ThemeManager
from src.ui.main_window import MainWindow


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
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
