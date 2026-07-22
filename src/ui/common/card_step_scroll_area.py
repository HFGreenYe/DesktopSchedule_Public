from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QScrollArea


class CardStepScrollArea(QScrollArea):
    def __init__(self, card_height, card_spacing, parent=None):
        super().__init__(parent)
        self._card_height = max(1, int(card_height))
        self._card_spacing = max(0, int(card_spacing))
        self._card_count = 0
        self._bottom_viewport_margin = 0
        self._snap_points = [0]
        self._sync_pending = False

    @property
    def row_pitch(self):
        return self._card_height + self._card_spacing

    def set_card_count(self, card_count):
        self._card_count = max(0, int(card_count))
        self._queue_scroll_geometry_sync()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._queue_scroll_geometry_sync()

    def wheelEvent(self, event):
        scroll_bar = self.verticalScrollBar()
        angle_delta = event.angleDelta().y()
        pixel_delta = event.pixelDelta().y()
        scroll_delta = angle_delta or pixel_delta
        if scroll_delta == 0 or len(self._snap_points) <= 1:
            super().wheelEvent(event)
            return

        current_index = min(
            range(len(self._snap_points)),
            key=lambda index: abs(
                self._snap_points[index] - scroll_bar.value()
            ),
        )
        notch_count = (
            max(1, abs(angle_delta) // 120)
            if angle_delta
            else 1
        )
        direction = -1 if scroll_delta > 0 else 1
        target_index = max(
            0,
            min(
                len(self._snap_points) - 1,
                current_index + direction * notch_count,
            ),
        )
        scroll_bar.setValue(self._snap_points[target_index])
        event.accept()

    def _queue_scroll_geometry_sync(self):
        if self._sync_pending:
            return
        self._sync_pending = True
        QTimer.singleShot(0, self._sync_scroll_geometry)

    def _sync_scroll_geometry(self):
        self._sync_pending = False
        content_widget = self.widget()
        if content_widget is None:
            return

        scroll_bar = self.verticalScrollBar()
        previous_row = round(scroll_bar.value() / self.row_pitch)

        # 无卡片时：不强制最小高度，让内容回归自然尺寸
        if self._card_count == 0:
            self._snap_points = [0]
            self._bottom_viewport_margin = 0
            self.setViewportMargins(0, 0, 0, 0)
            content_widget.setMinimumHeight(0)
            scroll_bar.setSingleStep(self.row_pitch)
            return

        available_height = max(
            1,
            self.viewport().height() + self._bottom_viewport_margin,
        )
        visible_rows = max(
            1,
            (available_height + self._card_spacing) // self.row_pitch,
        )

        if self._card_count > visible_rows:
            visible_span = (
                visible_rows * self._card_height
                + (visible_rows - 1) * self._card_spacing
            )
            bottom_margin = max(0, available_height - visible_span)
            hidden_rows = self._card_count - visible_rows
        else:
            bottom_margin = 0
            hidden_rows = 0

        if bottom_margin != self._bottom_viewport_margin:
            self._bottom_viewport_margin = bottom_margin
            self.setViewportMargins(0, 0, 0, bottom_margin)

        scroll_limit = hidden_rows * self.row_pitch
        self._snap_points = [
            row_index * self.row_pitch
            for row_index in range(hidden_rows + 1)
        ]
        scroll_bar.setSingleStep(self.row_pitch)
        content_widget.setMinimumHeight(
            max(1, self.viewport().height()) + scroll_limit
        )

        target_row = min(previous_row, hidden_rows)
        target_value = target_row * self.row_pitch
        QTimer.singleShot(
            0,
            lambda: scroll_bar.setValue(
                min(target_value, scroll_bar.maximum())
            ),
        )
