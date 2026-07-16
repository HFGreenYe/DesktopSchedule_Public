"""ReportLab-backed PDF rendering for schedule export payloads."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from threading import RLock

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Flowable, Frame, PageTemplate, Spacer

from src.services.export_background_presets import (
    get_export_background_image_path,
    get_export_background_preset,
)
from src.services.schedule_export_service import (
    ExportItem,
    ExportPayload,
    PdfExportStyle,
    PdfTextStyle,
    ScheduleMarkdownExporter,
)


_UNIT_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[._:/+\-][A-Za-z0-9]+)*|[ \t]+|.", re.S)
_PDF_WRITE_LOCK = RLock()


@dataclass(frozen=True)
class _FontDefinition:
    key: str
    regular: str
    bold: str | None = None
    inherently_bold: bool = False


@dataclass(frozen=True)
class _FontUse:
    alias: str
    synthetic_bold: bool


@dataclass(frozen=True)
class _TextRun:
    text: str
    font_alias: str
    width: float
    synthetic_bold: bool


@dataclass(frozen=True)
class _TextLine:
    runs: tuple[_TextRun, ...]
    width: float


@dataclass(frozen=True)
class _RenderLine:
    text_line: _TextLine
    font_size: float
    leading: float
    color: colors.Color
    italic: bool
    gap_before: float = 0.0


class _FontRegistry:
    _definitions = {
        "微软雅黑": _FontDefinition("yahei", "msyh.ttc", "msyhbd.ttc"),
        "宋体": _FontDefinition("simsun", "simsun.ttc"),
        "黑体": _FontDefinition("simhei", "simhei.ttf", "simhei.ttf", True),
        "仿宋": _FontDefinition("simfang", "simfang.ttf"),
        "Times New Roman": _FontDefinition("times", "times.ttf", "timesbd.ttf"),
        "Arial": _FontDefinition("arial", "arial.ttf", "arialbd.ttf"),
        "Calibri": _FontDefinition("calibri", "calibri.ttf", "calibrib.ttf"),
        "Georgia": _FontDefinition("georgia", "georgia.ttf", "georgiab.ttf"),
    }
    _english_families = {"Times New Roman", "Arial", "Calibri", "Georgia"}

    def __init__(self):
        windows_dir = Path(os.environ.get("WINDIR", "C:/Windows"))
        self.font_dir = windows_dir / "Fonts"
        self._uses: dict[tuple[str, bool], _FontUse] = {}

    def resolve(self, family: str, character: str, bold: bool) -> _FontUse:
        effective_family = family
        if family in self._english_families and not character.isascii():
            effective_family = "微软雅黑"
        definition = self._available_definition(effective_family)
        cache_key = (definition.key, bold)
        if cache_key in self._uses:
            return self._uses[cache_key]

        bold_path = self.font_dir / definition.bold if definition.bold else None
        regular_path = self.font_dir / definition.regular
        use_bold_file = bool(bold and bold_path is not None and bold_path.exists())
        font_path = bold_path if use_bold_file else regular_path
        alias = f"DesktopSchedule_{definition.key}_{'bold' if bold else 'regular'}"
        if alias not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(alias, str(font_path), subfontIndex=0))
        font_use = _FontUse(
            alias=alias,
            synthetic_bold=bool(
                bold and not use_bold_file and not definition.inherently_bold
            ),
        )
        self._uses[cache_key] = font_use
        return font_use

    def _available_definition(self, family: str) -> _FontDefinition:
        candidates = (
            self._definitions.get(family),
            self._definitions["微软雅黑"],
            self._definitions["黑体"],
        )
        for definition in candidates:
            if definition is not None and (self.font_dir / definition.regular).exists():
                return definition
        raise RuntimeError("未找到可用于 PDF 导出的中文字体")


class _PdfLayoutEngine:
    def __init__(self, style: PdfExportStyle):
        self.style = style
        self.fonts = _FontRegistry()

    def build_lines(
        self,
        text: str,
        text_style: PdfTextStyle,
        width: float,
        font_size: float,
        leading: float,
        gap_before: float = 0.0,
    ) -> list[_RenderLine]:
        usable_width = max(
            1.0,
            width - (font_size * 0.24 if text_style.italic else 0.0),
        )
        wrapped = self._wrap_text(
            str(text or ""),
            text_style.font_family,
            usable_width,
            font_size,
            text_style.bold,
        )
        color = self._color(text_style.color, "#253746")
        return [
            _RenderLine(
                text_line=line,
                font_size=font_size,
                leading=leading,
                color=color,
                italic=text_style.italic,
                gap_before=gap_before if index == 0 else 0.0,
            )
            for index, line in enumerate(wrapped)
        ]

    def draw_line(self, canvas, line: _RenderLine, left: float, baseline: float):
        current_x = left
        for run in line.text_line.runs:
            canvas.saveState()
            canvas.setFillColor(line.color)
            canvas.setStrokeColor(line.color)
            shear = 0.18 if line.italic else 0.0
            canvas.transform(1, 0, shear, 1, current_x, baseline)
            text_object = canvas.beginText()
            text_object.setTextOrigin(0, 0)
            text_object.setFont(run.font_alias, line.font_size)
            if run.synthetic_bold:
                canvas.setLineWidth(max(0.12, line.font_size * 0.018))
                text_object.setTextRenderMode(2)
            text_object.textOut(run.text)
            canvas.drawText(text_object)
            canvas.restoreState()
            current_x += run.width

    def draw_lines_from_top(
        self,
        canvas,
        lines: list[_RenderLine] | tuple[_RenderLine, ...],
        left: float,
        top: float,
        align_width: float | None = None,
        centered: bool = False,
    ):
        current_top = top
        for line in lines:
            current_top -= line.gap_before
            baseline = current_top - line.font_size
            line_x = left
            if centered and align_width is not None:
                line_x += max(0.0, (align_width - line.text_line.width) / 2)
            self.draw_line(canvas, line, line_x, baseline)
            current_top -= line.leading

    @staticmethod
    def lines_height(lines: list[_RenderLine] | tuple[_RenderLine, ...]) -> float:
        return sum(line.gap_before + line.leading for line in lines)

    def _wrap_text(
        self,
        text: str,
        family: str,
        width: float,
        font_size: float,
        bold: bool,
    ) -> list[_TextLine]:
        lines: list[_TextLine] = []
        paragraphs = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        for paragraph in paragraphs:
            if not paragraph:
                lines.append(_TextLine((), 0.0))
                continue
            current: list[_TextRun] = []
            current_width = 0.0
            for unit in _UNIT_PATTERN.findall(paragraph):
                unit_runs = self._runs_for_text(unit, family, font_size, bold)
                unit_width = sum(run.width for run in unit_runs)
                if current and current_width + unit_width > width:
                    current, current_width = self._flush_line(lines, current)
                    if unit.isspace():
                        continue
                if unit_width <= width:
                    current = self._merge_runs(current, unit_runs)
                    current_width += unit_width
                    continue
                for character in unit:
                    character_runs = self._runs_for_text(character, family, font_size, bold)
                    character_width = sum(run.width for run in character_runs)
                    if current and current_width + character_width > width:
                        current, current_width = self._flush_line(lines, current)
                    current = self._merge_runs(current, character_runs)
                    current_width += character_width
            if current:
                self._flush_line(lines, current)
        return lines or [_TextLine((), 0.0)]

    def _runs_for_text(
        self,
        text: str,
        family: str,
        font_size: float,
        bold: bool,
    ) -> list[_TextRun]:
        grouped: list[tuple[str, _FontUse]] = []
        for character in text:
            font_use = self.fonts.resolve(family, character, bold)
            if grouped and grouped[-1][1] == font_use:
                grouped[-1] = (grouped[-1][0] + character, font_use)
            else:
                grouped.append((character, font_use))
        return [
            _TextRun(
                text=value,
                font_alias=font_use.alias,
                width=pdfmetrics.stringWidth(value, font_use.alias, font_size),
                synthetic_bold=font_use.synthetic_bold,
            )
            for value, font_use in grouped
        ]

    @staticmethod
    def _merge_runs(base: list[_TextRun], additions: list[_TextRun]) -> list[_TextRun]:
        merged = list(base)
        for addition in additions:
            if (
                merged
                and merged[-1].font_alias == addition.font_alias
                and merged[-1].synthetic_bold == addition.synthetic_bold
            ):
                previous = merged[-1]
                merged[-1] = _TextRun(
                    text=previous.text + addition.text,
                    font_alias=previous.font_alias,
                    width=previous.width + addition.width,
                    synthetic_bold=previous.synthetic_bold,
                )
            else:
                merged.append(addition)
        return merged

    @staticmethod
    def _flush_line(lines: list[_TextLine], runs: list[_TextRun]):
        width = sum(run.width for run in runs)
        lines.append(_TextLine(tuple(runs), width))
        return [], 0.0

    @staticmethod
    def _color(value: str, fallback: str) -> colors.Color:
        try:
            return colors.HexColor(str(value or fallback))
        except (TypeError, ValueError):
            return colors.HexColor(fallback)


class _ScheduleCard(Flowable):
    padding = 4.5 * mm

    def __init__(
        self,
        renderer: "SchedulePdfExporter",
        item: ExportItem,
        source_lines: tuple[_RenderLine, ...] | None = None,
        source_width: float | None = None,
        continued: bool = False,
    ):
        super().__init__()
        self.renderer = renderer
        self.item = item
        self.source_lines = source_lines
        self.source_width = source_width
        self.continued = continued
        self._prefix_lines: tuple[_RenderLine, ...] = ()
        self._combined_lines: tuple[_RenderLine, ...] = ()

    def wrap(self, avail_width: float, avail_height: float):
        content_width = avail_width - 2 * self.padding
        if self.source_lines is None:
            self.source_lines = tuple(self.renderer.card_lines(self.item, content_width))
            self.source_width = content_width
        elif self.source_width is not None and abs(self.source_width - content_width) > 0.5:
            raise RuntimeError("PDF 卡片续页宽度发生变化")
        if self.continued:
            self._prefix_lines = tuple(
                self.renderer.engine.build_lines(
                    f"{self.item.title or '未命名项目'}（续）",
                    self.renderer.style.title,
                    content_width,
                    10.5,
                    13.0,
                )
            )
        else:
            self._prefix_lines = ()
        self._combined_lines = self._prefix_lines + tuple(self.source_lines)
        self.width = avail_width
        self.height = self._height_for(self._combined_lines)
        return self.width, self.height

    def split(self, avail_width: float, avail_height: float):
        self.wrap(avail_width, avail_height)
        if self.height <= avail_height:
            return []
        if self.height <= self.renderer.frame_height:
            return []
        if avail_height < self.renderer.frame_height * 0.72:
            return []
        used = 2 * self.padding
        fit_count = 0
        for line in self._combined_lines:
            required = line.gap_before + line.leading
            if fit_count and used + required > avail_height:
                break
            if not fit_count and used + required > avail_height:
                return []
            used += required
            fit_count += 1
        consumed_source = fit_count - len(self._prefix_lines)
        if consumed_source <= 0:
            return []
        remaining = tuple(self.source_lines[consumed_source:])
        if not remaining:
            return []
        first = _FixedScheduleCard(
            self.renderer,
            avail_width,
            self._combined_lines[:fit_count],
        )
        continuation = _ScheduleCard(
            self.renderer,
            self.item,
            source_lines=remaining,
            source_width=self.source_width,
            continued=True,
        )
        return [first, continuation]

    def draw(self):
        self.renderer.draw_card(self.canv, self.width, self.height, self._combined_lines)

    def _height_for(self, lines: tuple[_RenderLine, ...]) -> float:
        return 2 * self.padding + self.renderer.engine.lines_height(lines)


class _FixedScheduleCard(Flowable):
    def __init__(
        self,
        renderer: "SchedulePdfExporter",
        width: float,
        lines: tuple[_RenderLine, ...],
    ):
        super().__init__()
        self.renderer = renderer
        self.width = width
        self.lines = lines
        self.height = 2 * _ScheduleCard.padding + renderer.engine.lines_height(lines)

    def wrap(self, avail_width: float, avail_height: float):
        return self.width, self.height

    def draw(self):
        self.renderer.draw_card(self.canv, self.width, self.height, self.lines)


class _GroupHeader(Flowable):
    def __init__(self, renderer: "SchedulePdfExporter", text: str):
        super().__init__()
        self.renderer = renderer
        self.text = text
        self.keepWithNext = 1
        self.lines: list[_RenderLine] = []

    def wrap(self, avail_width: float, avail_height: float):
        self.width = avail_width
        content_width = avail_width - 6 * mm
        self.lines = self.renderer.engine.build_lines(
            self.text,
            self.renderer.style.title,
            content_width,
            11.5,
            15.0,
        )
        self.height = self.renderer.engine.lines_height(self.lines) + 2.5 * mm
        return self.width, self.height

    def draw(self):
        self.renderer.engine.draw_lines_from_top(
            self.canv,
            self.lines,
            3 * mm,
            self.height,
        )
        self.canv.saveState()
        self.canv.setStrokeColor(
            self.renderer.engine._color(self.renderer.style.title.color, "#0066CC")
        )
        self.canv.setLineWidth(0.6)
        self.canv.line(3 * mm, 1.4 * mm, self.width - 3 * mm, 1.4 * mm)
        self.canv.restoreState()


class _EmptyState(Flowable):
    def __init__(self, renderer: "SchedulePdfExporter"):
        super().__init__()
        self.renderer = renderer
        self.lines: list[_RenderLine] = []

    def wrap(self, avail_width: float, avail_height: float):
        self.width = avail_width
        content_width = avail_width - 10 * mm
        self.lines = self.renderer.engine.build_lines(
            "暂无符合当前内容类型和日期范围的日程或待办。",
            self.renderer.style.note,
            content_width,
            10.0,
            14.0,
        )
        self.height = self.renderer.engine.lines_height(self.lines) + 10 * mm
        return self.width, self.height

    def draw(self):
        self.canv.saveState()
        if hasattr(self.canv, "setStrokeAlpha"):
            self.canv.setStrokeAlpha(0.35)
        self.canv.setStrokeColor(
            self.renderer.engine._color(self.renderer.style.title.color, "#0066CC")
        )
        self.canv.setLineWidth(0.55)
        self.canv.roundRect(0, 0, self.width, self.height, 3 * mm, fill=0, stroke=1)
        self.canv.restoreState()
        self.renderer.engine.draw_lines_from_top(
            self.canv,
            self.lines,
            5 * mm,
            self.height - 5 * mm,
        )


class SchedulePdfExporter:
    def __init__(self, payload: ExportPayload, style: PdfExportStyle):
        self.payload = payload
        self.style = style
        self.engine = _PdfLayoutEngine(style)
        self.frame_height = A4[1] - 58 * mm

    @classmethod
    def write(
        cls,
        target: Path,
        payload: ExportPayload,
        style: PdfExportStyle,
    ) -> Path:
        with _PDF_WRITE_LOCK:
            exporter = cls(payload, style)
            exporter._write(target)
        return target

    def _write(self, target: Path):
        document = BaseDocTemplate(
            str(target),
            pagesize=A4,
            title="桌面日程导出",
            author="DesktopSchedule",
            subject=self._header_summary(),
        )
        frame = Frame(
            18 * mm,
            20 * mm,
            A4[0] - 36 * mm,
            self.frame_height,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        document.addPageTemplates(
            PageTemplate("schedule_export", frames=(frame,), onPage=self._draw_page)
        )
        story: list[Flowable] = []
        groups = self._group_items()
        if not groups:
            story.append(_EmptyState(self))
        for group_name, items in groups:
            story.append(_GroupHeader(self, group_name))
            for item in items:
                story.append(_ScheduleCard(self, item))
                story.append(Spacer(1, 2.2 * mm))
        document.build(story)

    def card_lines(self, item: ExportItem, width: float) -> list[_RenderLine]:
        status_text = ScheduleMarkdownExporter._status_text(
            item,
            self.payload.generated_at,
        )
        lines = self.engine.build_lines(
            item.title or "未命名项目",
            self.style.title,
            width,
            12.0,
            15.0,
        )
        note_lines = "\n".join(
            (
                f"时间：{ScheduleMarkdownExporter._time_text(item)}",
                (
                    f"类型：{ScheduleMarkdownExporter._item_type_text(item)} · "
                    f"状态：{status_text} · "
                    f"重要性：{ScheduleMarkdownExporter._priority_text(item.priority)}"
                ),
                (
                    f"清单：{item.category_name or '未分类'} · "
                    f"提醒：{ScheduleMarkdownExporter._reminder_text(item)} · "
                    f"重复：{ScheduleMarkdownExporter._repeat_text(item.repeat_rule)}"
                ),
                f"创建时间：{ScheduleMarkdownExporter._format_datetime(item.created_at)}",
            )
        )
        lines.extend(
            self.engine.build_lines(
                note_lines,
                self.style.note,
                width,
                9.2,
                12.0,
                gap_before=2.0,
            )
        )
        if item.description.strip():
            lines.extend(
                self.engine.build_lines(
                    f"详情：{item.description.strip()}",
                    self.style.detail,
                    width,
                    9.8,
                    13.0,
                    gap_before=3.0,
                )
            )
        return lines

    def draw_card(
        self,
        canvas,
        width: float,
        height: float,
        lines: tuple[_RenderLine, ...],
    ):
        self.engine.draw_lines_from_top(
            canvas,
            lines,
            _ScheduleCard.padding,
            height - _ScheduleCard.padding,
        )

    def _draw_page(self, canvas, document):
        page_width, page_height = A4
        canvas.saveState()
        if self.style.background_mode == "default":
            preset = get_export_background_preset(
                self.style.default_background_index
            )
            image_path = get_export_background_image_path(preset)
            if image_path is not None:
                image = ImageReader(str(image_path))
                image_width, image_height = image.getSize()
                scale = max(
                    page_width / image_width,
                    page_height / image_height,
                )
                draw_width = image_width * scale
                draw_height = image_height * scale
                canvas.drawImage(
                    image,
                    (page_width - draw_width) / 2,
                    (page_height - draw_height) / 2,
                    width=draw_width,
                    height=draw_height,
                    preserveAspectRatio=False,
                    mask="auto",
                )
            else:
                canvas.linearGradient(
                    0,
                    page_height,
                    0,
                    0,
                    (
                        self.engine._color(preset.top_color, "#EAF6FF"),
                        self.engine._color(preset.bottom_color, "#9CCFFF"),
                    ),
                    (0, 1),
                )
                if hasattr(canvas, "setFillAlpha"):
                    canvas.setFillAlpha(0.26)
                canvas.setFillColor(colors.white)
                canvas.circle(
                    -page_width * 0.08,
                    page_height * 0.80,
                    page_width * 0.34,
                    fill=1,
                    stroke=0,
                )
                if hasattr(canvas, "setFillAlpha"):
                    canvas.setFillAlpha(0.34)
                canvas.circle(
                    page_width * 0.88,
                    page_height * 0.58,
                    page_width * 0.29,
                    fill=1,
                    stroke=0,
                )
        elif self.style.background_mode == "gradient":
            canvas.linearGradient(
                0,
                page_height,
                0,
                0,
                (
                    self.engine._color(self.style.gradient_start, "#0066CC"),
                    self.engine._color(self.style.gradient_end, "#0099CC"),
                ),
                (0, 1),
            )
        else:
            canvas.setFillColor(
                self.engine._color(self.style.solid_color, "#ffffff")
            )
            canvas.rect(0, 0, page_width, page_height, fill=1, stroke=0)
        canvas.restoreState()

        title_lines = self.engine.build_lines(
            "日程导出",
            self.style.title,
            page_width - 36 * mm,
            19.0,
            23.0,
        )
        self.engine.draw_lines_from_top(
            canvas,
            title_lines,
            18 * mm,
            page_height - 14 * mm,
        )
        summary_lines = self.engine.build_lines(
            self._header_summary(),
            self.style.note,
            page_width - 36 * mm,
            9.5,
            13.0,
        )
        self.engine.draw_lines_from_top(
            canvas,
            summary_lines,
            18 * mm,
            page_height - 27 * mm,
        )
        footer_lines = self.engine.build_lines(
            (
                f"生成于 {ScheduleMarkdownExporter._format_datetime(self.payload.generated_at)}"
                f" · 第 {document.page} 页"
            ),
            self.style.note,
            page_width - 36 * mm,
            8.5,
            11.0,
        )
        self.engine.draw_lines_from_top(
            canvas,
            footer_lines,
            18 * mm,
            14 * mm,
            align_width=page_width - 36 * mm,
            centered=True,
        )

    def _header_summary(self) -> str:
        return (
            f"{ScheduleMarkdownExporter._content_type_text(self.payload.options.content_type)}"
            f" · {ScheduleMarkdownExporter._range_text(self.payload.options)}"
            f" · 共 {len(self.payload.items)} 条"
        )

    def _group_items(self):
        groups: dict[str, list[ExportItem]] = {}
        for item in self.payload.items:
            if self.payload.options.group_by == "category":
                group_name = item.category_name or "未分类"
            else:
                group_name = item.group_date.isoformat() if item.group_date else "未设置日期"
            groups.setdefault(group_name, []).append(item)
        return list(groups.items())
