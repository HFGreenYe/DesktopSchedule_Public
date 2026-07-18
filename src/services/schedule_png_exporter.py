"""PNG page rendering through the shared ReportLab layout pipeline."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from PyQt6.QtCore import QEventLoop, QSize, QTimer
from PyQt6.QtPdf import QPdfDocument
from reportlab.lib.pagesizes import A4

from src.services.schedule_export_service import (
    ExportPayload,
    PdfExportStyle,
    PngCanvasSpec,
)
from src.services.schedule_pdf_exporter import SchedulePdfExporter


class SchedulePngExporter:
    load_timeout_ms = 15_000

    @staticmethod
    def logical_page_size(canvas_spec: PngCanvasSpec) -> tuple[float, float]:
        short_edge = float(A4[0])
        ratio = canvas_spec.width / canvas_spec.height
        if ratio >= 1:
            return short_edge * ratio, short_edge
        return short_edge, short_edge / ratio

    @staticmethod
    def output_paths(target: Path, page_count: int) -> tuple[Path, ...]:
        target = Path(target).with_suffix(".png")
        page_count = max(1, int(page_count))
        if page_count == 1:
            return (target,)
        output_directory = target.parent / target.stem
        digits = max(3, len(str(page_count)))
        return tuple(
            output_directory
            / f"{target.stem}_{page_number:0{digits}d}.png"
            for page_number in range(1, page_count + 1)
        )

    @staticmethod
    def output_directory(target: Path, page_count: int) -> Path:
        target = Path(target).with_suffix(".png")
        if max(1, int(page_count)) == 1:
            return target.parent
        return target.parent / target.stem

    @classmethod
    def output_folder_name(cls, target: Path, page_count: int) -> str:
        return cls.output_directory(target, page_count).name

    @classmethod
    def output_display_paths(
        cls,
        target: Path,
        page_count: int,
    ) -> tuple[str, ...]:
        target = Path(target).with_suffix(".png")
        return tuple(
            str(path.relative_to(target.parent))
            for path in cls.output_paths(target, page_count)
        )

    @classmethod
    def conflict_paths(cls, target: Path, page_count: int) -> tuple[Path, ...]:
        target = Path(target).with_suffix(".png")
        return tuple(
            path
            for path in cls.output_paths(target, page_count)
            if path.exists()
        )

    @classmethod
    def write(
        cls,
        target: Path,
        payload: ExportPayload,
        style: PdfExportStyle,
        canvas_spec: PngCanvasSpec,
        overwrite=False,
    ) -> tuple[Path, ...]:
        target = Path(target).with_suffix(".png")
        target.parent.mkdir(parents=True, exist_ok=True)
        page_size = cls.logical_page_size(canvas_spec)
        with TemporaryDirectory(
            prefix="desktop_schedule_png_",
            dir=target.parent,
        ) as temporary_directory:
            temporary_root = Path(temporary_directory)
            pdf_path = temporary_root / "layout.pdf"
            SchedulePdfExporter.write(
                pdf_path,
                payload,
                style,
                page_size=page_size,
            )
            document = cls._load_document(pdf_path)
            try:
                page_count = document.pageCount()
                if page_count <= 0:
                    raise RuntimeError("PNG 排版未生成有效页面")
                output_paths = cls.output_paths(target, page_count)
                output_directory = cls.output_directory(target, page_count)
                if output_directory.exists() and not output_directory.is_dir():
                    raise FileExistsError(
                        f"目标文件夹路径被同名文件占用：{output_directory.name}"
                    )
                conflicts = cls.conflict_paths(target, page_count)
                if conflicts and not overwrite:
                    names = "、".join(path.name for path in conflicts[:5])
                    raise FileExistsError(f"目标文件已存在：{names}")

                temporary_images = []
                render_size = QSize(canvas_spec.width, canvas_spec.height)
                for page_index, output_path in enumerate(output_paths):
                    image = document.render(page_index, render_size)
                    if image.isNull():
                        raise RuntimeError(
                            f"PNG 第 {page_index + 1} 页渲染失败"
                        )
                    temporary_image = (
                        temporary_root / f"page_{page_index + 1:05d}.png"
                    )
                    if not image.save(str(temporary_image), "PNG"):
                        raise RuntimeError(
                            f"PNG 第 {page_index + 1} 页写入失败"
                        )
                    temporary_images.append((temporary_image, output_path))
            finally:
                document.close()
                del document

            if overwrite:
                for conflict in conflicts:
                    conflict.unlink(missing_ok=True)
            output_directory.mkdir(parents=True, exist_ok=True)
            for temporary_image, output_path in temporary_images:
                temporary_image.replace(output_path)
            return output_paths

    @classmethod
    def _load_document(cls, pdf_path: Path) -> QPdfDocument:
        document = QPdfDocument(None)
        load_error = document.load(str(pdf_path))
        if load_error != QPdfDocument.Error.None_:
            document.close()
            raise RuntimeError(f"PNG 临时排版加载失败：{load_error}")
        if document.status() == QPdfDocument.Status.Loading:
            loop = QEventLoop()
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(loop.quit)
            document.statusChanged.connect(
                lambda status: (
                    loop.quit()
                    if status != QPdfDocument.Status.Loading
                    else None
                )
            )
            timer.start(cls.load_timeout_ms)
            loop.exec()
            timer.stop()
        if document.status() != QPdfDocument.Status.Ready:
            status = document.status()
            document.close()
            raise RuntimeError(f"PNG 临时排版未就绪：{status}")
        return document
