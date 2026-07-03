from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtWidgets import (
    QAbstractSlider,
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QLineEdit,
    QListWidget,
    QPlainTextEdit,
    QTextEdit,
    QWidget,
)


class WindowDragController(QObject):
    """Turns non-input child surfaces into drag handles for a frameless window."""

    def __init__(self, window, *, drag_started=None):
        super().__init__(window)
        self._window = window
        self._drag_started = drag_started
        self._press_global = None
        self._window_origin = None
        self._pending = False
        self._dragging = False

        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

    @property
    def is_dragging(self):
        return self._dragging

    def eventFilter(self, obj, event):
        if not self._belongs_to_window(obj):
            return False

        event_type = event.type()
        if event_type == QEvent.Type.MouseButtonPress:
            if (
                event.button() == Qt.MouseButton.LeftButton
                and not self._is_excluded(obj)
            ):
                self._press_global = self._event_global(obj, event)
                self._window_origin = self._window.pos()
                self._pending = True
                self._dragging = False
            return False

        if event_type == QEvent.Type.MouseMove and self._pending:
            if not (event.buttons() & Qt.MouseButton.LeftButton):
                self._clear_state()
                return False

            current_global = self._event_global(obj, event)
            delta = current_global - self._press_global
            if not self._dragging:
                if delta.manhattanLength() < QApplication.startDragDistance():
                    return False
                self._dragging = True
                if self._drag_started is not None:
                    self._drag_started()

            self._window.move(self._window_origin + delta)
            event.accept()
            return True

        if event_type == QEvent.Type.MouseButtonRelease and self._pending:
            was_dragging = self._dragging
            self._clear_state()
            if was_dragging and event.button() == Qt.MouseButton.LeftButton:
                event.accept()
                return True
            return False

        if obj is self._window and event_type in (
            QEvent.Type.Hide,
            QEvent.Type.WindowDeactivate,
        ):
            self._clear_state()

        return False

    def _belongs_to_window(self, obj):
        return isinstance(obj, QWidget) and obj.window() is self._window

    @staticmethod
    def _event_global(widget, event):
        return widget.mapToGlobal(event.position().toPoint())

    def _is_excluded(self, widget):
        current = widget
        excluded_types = (
            QLineEdit,
            QTextEdit,
            QPlainTextEdit,
            QComboBox,
            QAbstractSpinBox,
            QAbstractSlider,
            QListWidget,
        )
        while current is not None:
            if bool(current.property("windowDragDisabled")):
                return True
            if isinstance(current, excluded_types):
                return True
            if current is self._window:
                break
            current = current.parentWidget()
        return False

    def _clear_state(self):
        self._press_global = None
        self._window_origin = None
        self._pending = False
        self._dragging = False
