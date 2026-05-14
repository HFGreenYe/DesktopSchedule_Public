# src/data/models.py
from peewee import *
import datetime
from src.data.connection import db


class BaseModel(Model):
    class Meta:
        database = db


class Category(BaseModel):
    name = CharField(verbose_name="清单名称")
    color = CharField(default="#0cc0df", verbose_name="主题色")
    list_type = CharField(default='schedule', verbose_name="清单类型")
    is_deleted = BooleanField(default=False, verbose_name="是否已删除")
    created_at = DateTimeField(default=datetime.datetime.now, verbose_name="创建时间")
    sort_order = DoubleField(default=lambda: datetime.datetime.now().timestamp(), verbose_name="排序权重")

    class Meta:
        table_name = 'categories'


class Schedule(BaseModel):
    title = CharField(verbose_name="标题")
    description = TextField(null=True, verbose_name="详情描述")
    item_type = CharField(default='schedule', verbose_name="类型")
    start_time = DateTimeField(null=True, verbose_name="开始时间")
    end_time = DateTimeField(null=True, verbose_name="结束时间/截止时间")
    reminder_time = DateTimeField(null=True, verbose_name="提醒时间")
    is_alarm = BooleanField(default=False, verbose_name="是否强提醒/闹钟")
    alarm_duration = IntegerField(default=0, verbose_name="闹钟时长模式")
    priority = IntegerField(default=0, verbose_name="紧急性")
    repeat_rule = CharField(default='none', verbose_name="重复规则")
    category_id = IntegerField(null=True, default=None, verbose_name="所属清单ID")
    theme_color = CharField(default='#FFFFFF', verbose_name="字体颜色")
    status = IntegerField(default=0, verbose_name="状态")
    is_pinned = BooleanField(default=False, verbose_name="是否置顶")
    created_at = DateTimeField(default=datetime.datetime.now, verbose_name="创建时间")
    group_id = CharField(null=True, index=True, verbose_name="循环组ID")

    sort_order = DoubleField(default=lambda: datetime.datetime.now().timestamp(), verbose_name="排序权重")

    class Meta:
        table_name = 'schedules'
