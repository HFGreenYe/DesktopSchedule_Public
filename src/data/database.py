# src/data/database.py
from peewee import *
import datetime
import os
import uuid 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "schedule.db")

db = SqliteDatabase(DB_PATH)

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

class DatabaseManager:
    def __init__(self):
        self._connect()
        self._create_tables()
        self._migrate_db() # 检查并自动升级表结构
        from src.repositories import CategoryRepository, ScheduleRepository

        self.schedule_repository = ScheduleRepository()
        self.category_repository = CategoryRepository()

    def _connect(self):
        db.connect()

    def _create_tables(self):
        with db:
            db.create_tables([Schedule, Category])

    def _migrate_db(self):
        columns = [col.name for col in db.get_columns('schedules')]
        if 'group_id' not in columns:
            from playhouse.migrate import migrate, SqliteMigrator
            migrator = SqliteMigrator(db)
            group_id_field = CharField(null=True, index=True, verbose_name="循环组ID")
            try:
                migrate(migrator.add_column('schedules', 'group_id', group_id_field))
                print("✅ [DB] 成功迁移数据库，已添加 group_id 字段")
            except Exception as e:
                print(f"❌ [DB] 数据库迁移失败: {e}")

        if 'sort_order' not in columns:
            from playhouse.migrate import migrate, SqliteMigrator
            migrator = SqliteMigrator(db)
            sort_order_field = DoubleField(default=0.0, verbose_name="排序权重")
            try:
                # 1. 给数据库表增加新列
                migrate(migrator.add_column('schedules', 'sort_order', sort_order_field))
                
                # 2. 为老数据平滑赋初始权重（直接转换老创建时间为时间戳），不丢原顺序
                for s in Schedule.select():
                    s.sort_order = s.created_at.timestamp() if s.created_at else 0.0
                    s.save()
                    
                print("✅ [DB] 成功迁移数据库，已添加 sort_order 字段并平滑过渡老数据")
            except Exception as e:
                print(f"❌ [DB] 数据库迁移失败 (sort_order): {e}")
        
        columns_cat = [col.name for col in db.get_columns('categories')]
        if 'list_type' not in columns_cat:
            from playhouse.migrate import migrate, SqliteMigrator
            migrator = SqliteMigrator(db)
            list_type_field = CharField(default='schedule', verbose_name="清单类型")
            try:
                migrate(migrator.add_column('categories', 'list_type', list_type_field))
                print("✅ [DB] 成功迁移 categories，已添加 list_type 字段")
            except Exception as e:
                print(f"❌ [DB] categories 迁移失败: {e}")
        
        if 'sort_order' not in columns_cat:
            from playhouse.migrate import migrate, SqliteMigrator
            migrator = SqliteMigrator(db)
            cat_sort_order_field = DoubleField(default=0.0, verbose_name="排序权重")
            try:
                migrate(migrator.add_column('categories', 'sort_order', cat_sort_order_field))
                # 平滑赋初值
                for c in Category.select():
                    c.sort_order = c.created_at.timestamp() if c.created_at else 0.0
                    c.save()
                print("✅ [DB] 成功迁移 categories，已添加 sort_order 字段")
            except Exception as e:
                print(f"❌ [DB] categories 迁移失败(sort_order): {e}")

    # 辅助计算月份函数
    def _add_months(self, sourcedate, months):
        if not sourcedate: return None
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        # 获取目标月的最大天数，防止 1月31日 加一个月变成 2月31日 报错
        day = min(sourcedate.day, [31, 29 if year%4==0 and not year%100==0 or year%400==0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1])
        return sourcedate.replace(year=year, month=month, day=day)

    # ==========================================
    # 支持自动生成的日程添加法
    # ==========================================
    def add_schedule(self, data: dict):
        rule = data.get('repeat_rule', 'none').strip()
        
        # 1. 不重复，走原逻辑
        if rule in ('none', '无', '不重复', ''):
            try:
                Schedule.create(**data)
                return True
            except Exception as e:
                print(f"❌ [DB] 保存失败: {e}")
                return False
        
        # 2. 重复日程，执行批量生成逻辑
        group_id = str(uuid.uuid4())
        data['group_id'] = group_id
        schedules_to_insert = [data.copy()]
        
        base_start = data.get('start_time')
        base_end = data.get('end_time')
        base_reminder = data.get('reminder_time')
        
        # 设定循环上限 (天/周铺一年，月铺12个月)
        loop_count = 0
        if rule == '每天': loop_count = 365
        elif rule == '每周': loop_count = 52
        elif rule == '每月': loop_count = 12
        
        for i in range(1, loop_count + 1):
            new_data = data.copy()
            
            if rule == '每天':
                delta = datetime.timedelta(days=i)
                if base_start: new_data['start_time'] = base_start + delta
                if base_end: new_data['end_time'] = base_end + delta
                if base_reminder: new_data['reminder_time'] = base_reminder + delta
            elif rule == '每周':
                delta = datetime.timedelta(weeks=i)
                if base_start: new_data['start_time'] = base_start + delta
                if base_end: new_data['end_time'] = base_end + delta
                if base_reminder: new_data['reminder_time'] = base_reminder + delta
            elif rule == '每月':
                if base_start: new_data['start_time'] = self._add_months(base_start, i)
                if base_end: new_data['end_time'] = self._add_months(base_end, i)
                if base_reminder: new_data['reminder_time'] = self._add_months(base_reminder, i)
                
            schedules_to_insert.append(new_data)
            
        try:
            # 使用原子事务批量插入，性能最高 (分批插防上限)
            with db.atomic():
                batch_size = 100
                for i in range(0, len(schedules_to_insert), batch_size):
                    batch = schedules_to_insert[i:i+batch_size]
                    Schedule.insert_many(batch).execute()
            print(f"✅ [DB] 成功批量生成了 {len(schedules_to_insert)} 条重复日程")
            return True
        except Exception as e:
            print(f"❌ [DB] 批量保存失败: {e}")
            return False

    # ==========================================
    # 专用于修改/取消重复规则
    # ==========================================
    def update_schedule_with_repeat(self, schedule_id, new_data: dict, update_future: bool = False):
        try:
            current_schedule = Schedule.get_by_id(schedule_id)
            new_rule = new_data.get('repeat_rule', current_schedule.repeat_rule).strip()
            old_group_id = current_schedule.group_id
            
            # 场景 1：用户明确选择“仅修改当前这一条”
            if not update_future:
                if old_group_id:
                    new_data['group_id'] = None
                Schedule.update(**new_data).where(Schedule.id == schedule_id).execute()
                return True

            # 场景 2：修改并影响未来 (update_future == True)
            
            if not old_group_id and new_rule not in ('none', '无', '不重复', ''):
                import uuid # 确保能用
                group_id = str(uuid.uuid4())
            else:
                group_id = old_group_id # 沿用旧的
                
            # 2. 确定当前这条日程的最终归属（如果新规则是不重复，它就是个单次日程）
            if new_rule in ('none', '无', '不重复', ''):
                new_data['group_id'] = None
            else:
                new_data['group_id'] = group_id
                
            # 3. 更新当前日程本体
            Schedule.update(**new_data).where(Schedule.id == schedule_id).execute()
            
            # 4. 斩断旧的未来：如果原来属于某个循环组，把未来的同组日程全删了
            if old_group_id:
                if current_schedule.start_time:
                    Schedule.delete().where(
                        (Schedule.group_id == old_group_id) & 
                        (Schedule.id != schedule_id) & 
                        (Schedule.start_time > current_schedule.start_time)
                    ).execute()
                elif current_schedule.end_time:
                    Schedule.delete().where(
                        (Schedule.group_id == old_group_id) & 
                        (Schedule.id != schedule_id) & 
                        (Schedule.end_time > current_schedule.end_time)
                    ).execute()
                else:
                    Schedule.delete().where(
                        (Schedule.group_id == old_group_id) & 
                        (Schedule.id > schedule_id)
                    ).execute()

            # 5. 重建新的未来：如果新规则是循环，就重新生成
            if new_rule not in ('none', '无', '不重复', ''):
                updated_schedule = Schedule.get_by_id(schedule_id)
                
                # 利用 Peewee 特性一键获取所有字段，防漏防错
                base_data = updated_schedule.__data__.copy()
                base_data.pop('id', None)           
                base_data.pop('created_at', None)   
                base_data['group_id'] = group_id   
                
                schedules_to_insert = []
                base_start = updated_schedule.start_time
                base_end = updated_schedule.end_time
                base_reminder = updated_schedule.reminder_time
                
                loop_count = 0
                if new_rule == '每天': loop_count = 365
                elif new_rule == '每周': loop_count = 52
                elif new_rule == '每月': loop_count = 12
                
                for i in range(1, loop_count + 1):
                    new_item = base_data.copy()
                    if new_rule == '每天':
                        delta = datetime.timedelta(days=i)
                        if base_start: new_item['start_time'] = base_start + delta
                        if base_end: new_item['end_time'] = base_end + delta
                        if base_reminder: new_item['reminder_time'] = base_reminder + delta
                    elif new_rule == '每周':
                        delta = datetime.timedelta(weeks=i)
                        if base_start: new_item['start_time'] = base_start + delta
                        if base_end: new_item['end_time'] = base_end + delta
                        if base_reminder: new_item['reminder_time'] = base_reminder + delta
                    elif new_rule == '每月':
                        if base_start: new_item['start_time'] = self._add_months(base_start, i)
                        if base_end: new_item['end_time'] = self._add_months(base_end, i)
                        if base_reminder: new_item['reminder_time'] = self._add_months(base_reminder, i)
                        
                    schedules_to_insert.append(new_item)
                    
                if schedules_to_insert:
                    with db.atomic():
                        batch_size = 100
                        for i in range(0, len(schedules_to_insert), batch_size):
                            batch = schedules_to_insert[i:i+batch_size]
                            Schedule.insert_many(batch).execute()

            return True
        except Exception as e:
            print(f"❌ [DB] 更新未来日程失败: {e}")
            return False

    def delete_schedule(self, schedule_id):
        try:
            Schedule.delete().where(Schedule.id == schedule_id).execute()
            return True
        except Exception as e:
            return False

    def update_schedule_status(self, schedule_id, new_status):
        try:
            Schedule.update(status=new_status).where(Schedule.id == schedule_id).execute()
            return True
        except Exception as e:
            return False

    def update_schedule_fields(self, schedule_id, **kwargs):
        try:
            Schedule.update(**kwargs).where(Schedule.id == schedule_id).execute()
            return True
        except Exception as e:
            print(f"❌ [DB] 更新字段失败: {e}")
            return False
        
    def toggle_pin_status(self, schedule_id, current_pin_status):
        try:
            new_status = not current_pin_status
            Schedule.update(is_pinned=new_status).where(Schedule.id == schedule_id).execute()
            return True
        except Exception as e:
            return False

    def get_all_schedules(self):
        return self.schedule_repository.get_all_schedules()
    
    def get_schedules_for_date(self, target_date: datetime.date):
        return self.schedule_repository.get_schedules_for_date(target_date)

    def get_active_categories(self, list_type=None):
        return self.category_repository.get_active_categories(list_type)
    
    def update_category_fields(self, cat_id, **kwargs):
        try:
            Category.update(**kwargs).where(Category.id == cat_id).execute()
            return True
        except Exception as e:
            print(f"❌ [DB] 更新分类字段失败: {e}")
            return False

    def get_category_map(self):
        return self.category_repository.get_category_map()
        
    def get_category(self, cat_id):
        try:
            return Category.get_by_id(cat_id)
        except:
            return None

    def add_category(self, name, color="#0cc0df", list_type='schedule'):
        try:
            cat = Category.create(name=name, color=color, list_type=list_type)
            return cat.id  
        except Exception:
            return None
        
    def check_category_status(self, cat_id):
        schedules = list(Schedule.select().where(Schedule.category_id == cat_id))
        if not schedules:
            return 'empty'
            
        now = datetime.datetime.now()
        for s in schedules:
            is_completed = (s.status == 1)
            is_expired = (s.end_time and s.end_time < now and not is_completed)
            if not is_completed and not is_expired:
                return 'active'
        return 'historical'

    def soft_delete_category(self, cat_id):
        try:
            Category.update(is_deleted=True).where(Category.id == cat_id).execute()
            return True
        except:
            return False

    def hard_delete_category(self, cat_id):
        try:
            Category.delete().where(Category.id == cat_id).execute()
            return True
        except:
            return False

db_manager = DatabaseManager()
