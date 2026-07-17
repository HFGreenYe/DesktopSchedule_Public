"""Debounced background generation for temporary schedule PDF previews."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, QTimer, pyqtSignal

from src.services.schedule_export_service import (
    ExportOptions,
    ExportPayload,
    PdfExportStyle,
)
from src.services.schedule_pdf_exporter import SchedulePdfExporter


class _PdfPreviewWorkerSignals(QObject):
    completed = pyqtSignal(int, str, str)


class _PdfPreviewWorker(QRunnable):
    def __init__(
        self,
        request_id: int,
        target: Path,
        payload: ExportPayload,
        style: PdfExportStyle,
        page_size=None,
    ):
        super().__init__()
        self.request_id = request_id
        self.target = target
        self.payload = payload
        self.style = style
        self.page_size = page_size
        self.signals = _PdfPreviewWorkerSignals()

    def run(self):
        error = ""
        try:
            if self.page_size is None:
                SchedulePdfExporter.write(self.target, self.payload, self.style)
            else:
                SchedulePdfExporter.write(
                    self.target,
                    self.payload,
                    self.style,
                    page_size=self.page_size,
                )
        except Exception as exc:
            error = str(exc) or type(exc).__name__
        self.signals.completed.emit(self.request_id, str(self.target), error)


class SchedulePdfPreviewController(QObject):
    preview_ready = pyqtSignal(str)
    preview_failed = pyqtSignal(str)

    def __init__(
        self,
        payload_builder: Callable[[ExportOptions], ExportPayload],
        parent=None,
        debounce_ms: int = 300,
    ):
        super().__init__(parent)
        self._payload_builder = payload_builder
        self._request_id = 0
        self._pending_request = None
        self._workers = {}
        self._temporary_directory = TemporaryDirectory(
            prefix="desktop_schedule_pdf_preview_"
        )
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(max(0, debounce_ms))
        self._timer.timeout.connect(self._start_latest_request)
        self._thread_pool = QThreadPool(self)
        self._thread_pool.setMaxThreadCount(1)
        self._shutting_down = False

    @property
    def debounce_ms(self) -> int:
        return self._timer.interval()

    def schedule(
        self,
        options: ExportOptions,
        style: PdfExportStyle,
        page_size=None,
    ) -> int:
        if self._shutting_down:
            return self._request_id
        self._request_id += 1
        self._pending_request = (
            self._request_id,
            options,
            style,
            page_size,
        )
        self._timer.start()
        return self._request_id

    def cancel(self):
        self._request_id += 1
        self._pending_request = None
        self._timer.stop()

    def discard(self, file_path, retries=20):
        if not file_path:
            return
        try:
            Path(file_path).unlink(missing_ok=True)
        except OSError:
            if retries > 0 and not self._shutting_down:
                QTimer.singleShot(
                    100,
                    lambda path=file_path, remaining=retries - 1: self.discard(
                        path,
                        remaining,
                    ),
                )

    def shutdown(self):
        if self._shutting_down:
            return
        self._shutting_down = True
        self.cancel()
        self._thread_pool.waitForDone(-1)
        try:
            self._temporary_directory.cleanup()
        except OSError:
            pass

    def _start_latest_request(self):
        if self._pending_request is None or self._shutting_down:
            return
        request_id, options, style, page_size = self._pending_request
        self._pending_request = None
        if request_id != self._request_id:
            return
        try:
            payload = self._payload_builder(options)
        except Exception as exc:
            self.preview_failed.emit(str(exc) or type(exc).__name__)
            return

        target = (
            Path(self._temporary_directory.name)
            / f"preview_{request_id:08d}.pdf"
        )
        worker = _PdfPreviewWorker(
            request_id,
            target,
            payload,
            style,
            page_size,
        )
        worker.signals.completed.connect(self._handle_worker_completed)
        self._workers[request_id] = worker
        self._thread_pool.start(worker)

    def _handle_worker_completed(self, request_id: int, file_path: str, error: str):
        self._workers.pop(request_id, None)
        if self._shutting_down or request_id != self._request_id:
            self.discard(file_path)
            return
        if error:
            self.discard(file_path)
            self.preview_failed.emit(error)
            return
        self.preview_ready.emit(file_path)
