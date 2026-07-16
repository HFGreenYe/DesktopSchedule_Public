"""Read-only export payload construction and file rendering."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, Mapping

from src.services.schedule_query_service import ScheduleQueryService


@dataclass(frozen=True)
class ExportOptions:
    content_type: str = "all"
    range_kind: str = "day"
    target_date: date = field(default_factory=date.today)
    group_by: str = "date"


@dataclass(frozen=True)
class PdfTextStyle:
    font_family: str = "微软雅黑"
    color: str = "#0066CC"
    bold: bool = False
    italic: bool = False


@dataclass(frozen=True)
class PdfExportStyle:
    background_mode: str = "solid"
    solid_color: str = "#ffffff"
    gradient_start: str = "#0066CC"
    gradient_end: str = "#0099CC"
    default_background_index: int = 0
    title: PdfTextStyle = field(
        default_factory=lambda: PdfTextStyle(bold=True)
    )
    detail: PdfTextStyle = field(default_factory=PdfTextStyle)
    note: PdfTextStyle = field(default_factory=PdfTextStyle)


@dataclass(frozen=True)
class ExportItem:
    item_id: int | None
    item_type: str
    title: str
    description: str
    start_time: datetime | None
    end_time: datetime | None
    reminder_time: datetime | None
    is_alarm: bool
    priority: int
    repeat_rule: str
    category_name: str
    status: int
    created_at: datetime | None

    @property
    def is_todo(self) -> bool:
        return self.item_type == "todo"

    @property
    def is_interval(self) -> bool:
        return bool(
            self.start_time is not None
            and self.end_time is not None
            and self.start_time != self.end_time
        )

    @property
    def effective_time(self) -> datetime | None:
        if self.is_interval:
            return self.end_time
        return self.end_time or self.start_time or self.created_at

    @property
    def group_date(self) -> date | None:
        value = self.start_time or self.end_time or self.created_at
        return value.date() if isinstance(value, datetime) else None


@dataclass(frozen=True)
class ExportPayload:
    options: ExportOptions
    generated_at: datetime
    items: tuple[ExportItem, ...]


class ScheduleMarkdownExporter:
    @classmethod
    def render(cls, payload: ExportPayload) -> str:
        lines = [
            "# 日程导出",
            "",
            f"- 导出时间：{cls._format_datetime(payload.generated_at)}",
            f"- 内容类型：{cls._content_type_text(payload.options.content_type)}",
            f"- 日程范围：{cls._range_text(payload.options)}",
            f"- 共计：{len(payload.items)} 条",
            "",
        ]
        if not payload.items:
            lines.append("暂无符合条件的日程或待办。")
            return "\n".join(lines).rstrip() + "\n"

        grouped = cls._group_items(payload)
        for group_name, items in grouped:
            lines.extend([f"## {cls._escape(group_name)}", ""])
            for item in items:
                lines.extend(cls._render_item(item, payload.generated_at))
        return "\n".join(lines).rstrip() + "\n"

    @classmethod
    def _group_items(cls, payload: ExportPayload):
        groups: dict[str, list[ExportItem]] = {}
        for item in payload.items:
            if payload.options.group_by == "category":
                key = item.category_name or "未分类"
            else:
                key = item.group_date.isoformat() if item.group_date else "未设置日期"
            groups.setdefault(key, []).append(item)
        return list(groups.items())

    @classmethod
    def _render_item(cls, item: ExportItem, generated_at: datetime) -> list[str]:
        lines = [
            f"### {cls._escape(item.title or '未命名项目')}",
            "",
            f"- 类型：{cls._item_type_text(item)}",
            f"- 时间：{cls._time_text(item)}",
            f"- 状态：{cls._status_text(item, generated_at)}",
            f"- 重要性：{cls._priority_text(item.priority)}",
            f"- 清单：{cls._escape(item.category_name or '未分类')}",
            f"- 提醒：{cls._reminder_text(item)}",
            f"- 重复：{cls._repeat_text(item.repeat_rule)}",
            f"- 创建时间：{cls._format_datetime(item.created_at)}",
        ]
        if item.description.strip():
            lines.extend(["", "详情：", ""])
            lines.extend(
                f"> {line}" if line else ">"
                for line in item.description.strip().splitlines()
            )
        lines.append("")
        return lines

    @staticmethod
    def _content_type_text(value):
        return {"schedule": "仅日程", "todo": "仅待办", "all": "日程 + 待办"}.get(
            value,
            "日程 + 待办",
        )

    @staticmethod
    def _range_text(options):
        target = options.target_date
        if options.range_kind == "day":
            return target.isoformat()
        if options.range_kind == "week":
            iso_year, iso_week, _ = target.isocalendar()
            return f"{iso_year:04d} 年第 {iso_week:02d} 周"
        if options.range_kind == "month":
            return f"{target.year:04d}-{target.month:02d}"
        return "全部"

    @staticmethod
    def _item_type_text(item):
        if item.is_todo:
            return "待办"
        return "时间段" if item.is_interval else "DDL / 单时间"

    @classmethod
    def _time_text(cls, item):
        if item.is_interval:
            return (
                f"{cls._format_datetime(item.start_time)} → "
                f"{cls._format_datetime(item.end_time)}"
            )
        if item.end_time:
            return f"截止：{cls._format_datetime(item.end_time)}"
        if item.start_time:
            return cls._format_datetime(item.start_time)
        return "未设置时间"

    @classmethod
    def _status_text(cls, item, generated_at):
        if item.status == 1:
            return "已完成"
        if item.status == 2:
            return "已隐藏"
        effective_time = item.effective_time
        if isinstance(effective_time, datetime) and effective_time < generated_at:
            return "已过期"
        return "未完成"

    @staticmethod
    def _priority_text(priority):
        return {0: "低重要性", 1: "中重要性", 2: "高重要性"}.get(
            int(priority or 0),
            "低重要性",
        )

    @classmethod
    def _reminder_text(cls, item):
        if item.reminder_time is None:
            return "无提醒"
        suffix = "（强提醒）" if item.is_alarm else ""
        return f"{cls._format_datetime(item.reminder_time)}{suffix}"

    @staticmethod
    def _repeat_text(value):
        rule = str(value or "").strip()
        return {
            "": "不重复",
            "none": "不重复",
            "无": "不重复",
            "不重复": "不重复",
            "daily": "每日重复",
            "每天": "每日重复",
            "weekly": "每周重复",
            "每周": "每周重复",
            "monthly": "每月重复",
            "每月": "每月重复",
        }.get(rule, rule)

    @staticmethod
    def _format_datetime(value):
        return value.strftime("%Y-%m-%d %H:%M") if isinstance(value, datetime) else "未设置"

    @staticmethod
    def _escape(value):
        text = str(value or "")
        for token in ("\\", "`", "*", "_", "{", "}", "[", "]", "<", ">", "#"):
            text = text.replace(token, f"\\{token}")
        return text


class ScheduleExportService:
    def __init__(self, schedule_repository=None, category_repository=None):
        if schedule_repository is None or category_repository is None:
            from src.repositories.category_repository import CategoryRepository
            from src.repositories.schedule_repository import ScheduleRepository

            schedule_repository = schedule_repository or ScheduleRepository()
            category_repository = category_repository or CategoryRepository()
        self.schedule_repository = schedule_repository
        self.category_repository = category_repository

    def build_payload(self, options: ExportOptions) -> ExportPayload:
        items = self.schedule_repository.get_all_schedules()
        category_map = self.category_repository.get_category_map()
        return self.build_payload_from_items(items, category_map, options)

    @classmethod
    def build_payload_from_items(
        cls,
        items: Iterable,
        category_map: Mapping[int, object],
        options: ExportOptions,
        generated_at: datetime | None = None,
    ) -> ExportPayload:
        now = generated_at or datetime.now()
        filtered = [
            item
            for item in items
            if cls._matches_content_type(item, options.content_type)
            and cls._matches_range(item, options)
        ]
        export_items = tuple(
            cls._to_export_item(item, category_map)
            for item in sorted(filtered, key=cls._sort_key)
        )
        return ExportPayload(options=options, generated_at=now, items=export_items)

    def render_markdown(self, options: ExportOptions) -> str:
        return ScheduleMarkdownExporter.render(self.build_payload(options))

    def write_markdown(self, file_path, options: ExportOptions) -> Path:
        target = Path(file_path)
        target.write_text(self.render_markdown(options), encoding="utf-8")
        return target

    def write_pdf(
        self,
        file_path,
        options: ExportOptions,
        style: PdfExportStyle,
    ) -> Path:
        from src.services.schedule_pdf_exporter import SchedulePdfExporter

        target = Path(file_path)
        SchedulePdfExporter.write(target, self.build_payload(options), style)
        return target

    @staticmethod
    def _matches_content_type(item, content_type):
        is_todo = ScheduleQueryService.is_todo(item)
        if content_type == "schedule":
            return not is_todo
        if content_type == "todo":
            return is_todo
        return True

    @classmethod
    def _matches_range(cls, item, options):
        if options.range_kind == "all":
            return True
        range_start, range_end = cls._range_bounds(options)
        start_time = getattr(item, "start_time", None)
        end_time = getattr(item, "end_time", None)
        if start_time and end_time and start_time != end_time:
            low, high = sorted((start_time, end_time))
            return low < range_end and high >= range_start
        value = end_time or start_time or getattr(item, "created_at", None)
        return isinstance(value, datetime) and range_start <= value < range_end

    @staticmethod
    def _range_bounds(options):
        target = options.target_date
        start = datetime(target.year, target.month, target.day)
        if options.range_kind == "day":
            end = start + timedelta(days=1)
        elif options.range_kind == "week":
            start -= timedelta(days=start.weekday())
            end = start + timedelta(days=7)
        elif options.range_kind == "month":
            end = (
                datetime(target.year + 1, 1, 1)
                if target.month == 12
                else datetime(target.year, target.month + 1, 1)
            )
            start = datetime(target.year, target.month, 1)
        else:
            raise ValueError(f"不支持的导出范围：{options.range_kind}")
        return start, end

    @staticmethod
    def _to_export_item(item, category_map):
        category = category_map.get(getattr(item, "category_id", None))
        return ExportItem(
            item_id=getattr(item, "id", None),
            item_type="todo" if ScheduleQueryService.is_todo(item) else "schedule",
            title=str(getattr(item, "title", "") or ""),
            description=str(getattr(item, "description", "") or ""),
            start_time=getattr(item, "start_time", None),
            end_time=getattr(item, "end_time", None),
            reminder_time=getattr(item, "reminder_time", None),
            is_alarm=bool(getattr(item, "is_alarm", False)),
            priority=int(getattr(item, "priority", 0) or 0),
            repeat_rule=str(getattr(item, "repeat_rule", "") or ""),
            category_name=str(getattr(category, "name", "") or "未分类"),
            status=int(getattr(item, "status", 0) or 0),
            created_at=getattr(item, "created_at", None),
        )

    @staticmethod
    def _sort_key(item):
        start_time = getattr(item, "start_time", None)
        end_time = getattr(item, "end_time", None)
        created_at = getattr(item, "created_at", None)
        value = start_time or end_time or created_at or datetime.max
        return (value, int(getattr(item, "id", 0) or 0))
