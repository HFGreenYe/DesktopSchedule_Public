请执行第四轮 4-5：`update_schedule_with_repeat(update_future=False)` 路径委托准备与行为验收。本轮只处理“仅修改当前这一条”的路径，不处理影响未来路径。

## 1. 本轮目标

基于第四轮合同和 4-0 ~ 4-4 结论，验证并准备 `DatabaseManager.update_schedule_with_repeat(schedule_id, new_data, update_future=False)` 的旧行为边界。

本轮重点：

- 只关注 `update_future=False` 分支。
- 该分支旧语义必须保持：
  - 只更新当前选中的这一条。
  - 如果当前条原本属于重复组，则当前条更新后脱离原 `group_id`，即 `group_id=None`。
  - 同组其他日程不被修改。
  - 同组其他日程不被删除。
- 使用临时重复组验收。
- 选临时重复组的中间一条做修改。
- 验证完成后清理整组与脱组后的当前条。
- 最终 `schedule.db` 无 tracked diff。

本轮默认以行为验收和边界记录为主。若代码已符合边界，优先不改源码。若确需为后续委托做极小 service 方法，也必须只覆盖 `update_future=False` 分支，不得触碰未来更新路径。

## 2. 允许/禁止

本轮允许修改：

- `src/services/schedule_service.py`（仅当需要抽取 `update_future=False` 的最小写入协调时）
- `src/data/database.py`（仅限 `update_schedule_with_repeat` 的 `update_future=False` 分支）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮默认预期：

- 如果当前边界清楚且无需改造，可以不改源码，只做临时写库行为验收并记录。

本轮禁止修改：

- `src/services/schedule_repeat_service.py`
- `src/ui/`
- `src/data/models.py`
- `src/repositories/`
- `main.py`
- `requirements.txt`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不修改 `add_schedule`。
- 不修改 `update_future=True` 路径。
- 不修改旧未来实例删除逻辑。
- 不修改未来实例重建逻辑。
- 不新增 `parent_id`。
- 不新增 `每年 / yearly / daily / weekly / monthly` 行为。
- 不修改 UI 的 `group_id` 内存态同步。
- 不修改数据库字段、迁移逻辑、表名、默认值。
- 不改变 `db_manager.update_schedule_with_repeat(...)` 方法名、参数、返回语义。
- 不保留临时数据。
- 不保留 `schedule.db` tracked diff；允许为了验收临时写入，但必须清理。

若临时重复组创建、修改、清理任一环节失败，立即停止后续验证，并在 `Work_Log.md` 记录临时标题前缀、`group_id`、失败位置和需要人工清理的信息。

## 3. 具体任务

1. 读取：
   - `manage_instruction/Work_Instruction.md`
   - `manage_instruction/Work_Log.md` 中 4-0 ~ 4-4 结论

2. 复核当前代码：
   - `src/data/database.py` 中 `update_schedule_with_repeat`
   - `src/services/schedule_service.py`
   - 确认 `update_future=False` 分支当前行为：
     - 有旧 `group_id` 时写入 `new_data['group_id'] = None`
     - 只对当前 `schedule_id` 执行 `Schedule.update(...)`
     - 成功返回 `True`
     - 异常返回 `False`

3. 判断是否需要源码修改：
   - 若只是验收当前行为：不改源码。
   - 若做最小委托：只允许把 `update_future=False` 当前条更新逻辑抽到 `ScheduleService`，并保持 `DatabaseManager` 对外 API 与异常处理语义不变。
   - 不得改 `update_future=True` 后续分支。

4. 使用临时重复组进行行为验收：
   - 通过现有 `db_manager.add_schedule(...)` 创建一个 `每周` 临时重复组。
   - 标题前缀固定为：`__tmp_4_5_update_current_`
   - 预期生成 53 条。
   - 选中间一条，例如按 `start_time` 排序后的第 10 条。
   - 记录该条原 `id`、原 `group_id`、原 `title`、原 `description`。
   - 调用 `db_manager.update_schedule_with_repeat(target_id, new_data, update_future=False)`。
   - 验证：
     - 返回 `True`。
     - 当前条 title 或 description 已更新。
     - 当前条 `group_id is None`。
     - 原重复组剩余 52 条仍存在。
     - 原重复组其他条目的标题未被改成目标条的新标题。
     - 原重复组其他条目没有被删除。
   - 清理：
     - 删除脱组后的当前条。
     - 按原 `group_id` 删除剩余临时组。
     - 确认前缀无残留。

5. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

静态复核 `update_future=False` 分支：

```cmd
rg -n "def update_schedule_with_repeat|if not update_future|group_id.*None|Schedule\.update|Schedule\.delete|build_repeat_insert_plan|insert_many|return True|return False" src/data/database.py
```

人工复核该输出，确认：

- `update_future=False` 分支只更新当前条。
- `update_future=False` 分支中如有旧 `group_id`，当前条会脱组。
- `Schedule.delete(...)`、`build_repeat_insert_plan(...)`、`insert_many` 不属于 `update_future=False` 分支。
- `update_future=True` 分支未被本轮修改。

service import / db import 验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; from src.services.schedule_service import ScheduleService; print('imports ok', ScheduleService, len(db_manager.get_all_schedules()))"
```

临时重复组 + 仅当前修改行为验收：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -X utf8 -c "from src.data.database import db_manager; from src.data.models import Schedule; import datetime as dt,time,atexit; prefix='__tmp_4_5_update_current_'+str(time.time_ns()); atexit.register(lambda: print('atexit cleanup by prefix', Schedule.delete().where(Schedule.title.startswith(prefix)).execute())); title=prefix+'_base'; print('prefix', prefix); data={'title':title,'item_type':'schedule','priority':0,'repeat_rule':'每周','description':'temporary 4-5 base','category_id':None,'start_time':dt.datetime(2026,1,7,9,0),'end_time':dt.datetime(2026,1,7,10,0),'reminder_time':dt.datetime(2026,1,7,8,30)}; ok=db_manager.add_schedule(data); print('created group', ok); assert ok is True; rows=list(Schedule.select().where(Schedule.title==title).order_by(Schedule.start_time, Schedule.id)); print('created rows', len(rows)); assert len(rows)==53; gids={r.group_id for r in rows}; print('group ids', gids); assert len(gids)==1; group_id=next(iter(gids)); assert group_id; target=rows[10]; target_id=target.id; old_group_count=Schedule.select().where(Schedule.group_id==group_id).count(); print('target id', target_id, 'group count before', old_group_count); assert old_group_count==53; new_title=prefix+'_updated_current_only'; new_data={'title':new_title,'description':'temporary 4-5 updated current only','repeat_rule':'每周'}; updated=db_manager.update_schedule_with_repeat(target_id,new_data,update_future=False); print('updated current only', updated); assert updated is True; refreshed=Schedule.get_by_id(target_id); print('refreshed', refreshed.id, refreshed.title, refreshed.group_id); assert refreshed.title==new_title; assert refreshed.group_id is None; remaining_group=list(Schedule.select().where(Schedule.group_id==group_id)); print('remaining group count', len(remaining_group)); assert len(remaining_group)==52; changed_others=[r.id for r in remaining_group if r.title==new_title]; print('changed others', changed_others); assert changed_others==[]; deleted_current=Schedule.delete().where(Schedule.id==target_id).execute(); print('deleted current', deleted_current); assert deleted_current==1; deleted_group=Schedule.delete().where(Schedule.group_id==group_id).execute(); print('deleted group', deleted_group); assert deleted_group==52; leftovers=Schedule.select().where(Schedule.title.startswith(prefix)).count(); print('leftovers', leftovers); assert leftovers==0"
```

确认临时前缀无残留：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.models import Schedule; prefix='__tmp_4_5_update_current_'; count=Schedule.select().where(Schedule.title.startswith(prefix)).count(); print('tmp 4-5 leftovers', count); assert count==0"
```

确认未新增不允许规则和字段：

```cmd
rg -n "每年|yearly|daily|weekly|monthly|parent_id" src/data/database.py src/services/schedule_service.py
```

预期：不应出现新增实现分支；如只在既有文本、注释或无关上下文中出现，需在日志说明。

service 静态依赖检查：

```cmd
rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_service.py
```

预期：无输出，退出码 1 视为通过。

语法检查：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src\services\schedule_service.py src\data\database.py
```

范围检查：

```cmd
git diff --name-only -- src/services/schedule_repeat_service.py
git diff --name-only -- src/ui
git diff --name-only -- src/data/models.py
git diff --name-only -- src/repositories
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch
```

预期：

- `src/services/schedule_repeat_service.py` 无 diff。
- `src/ui` 无 diff。
- `src/data/models.py` 无 diff。
- `src/repositories` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- 若无需源码修改，最终只允许：
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`
- 若确需最小源码修改，最终只允许额外包含：
  - `src/services/schedule_service.py`
  - `src/data/database.py`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第四轮 4-5（update_future=False 仅当前修改路径）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 是否改源码；如未改，明确写“本轮仅做行为基线验收”
- `update_future=False` 分支复核结论
- 是否保持：只更新当前条
- 是否保持：当前条脱离旧 `group_id`
- 是否保持：同组其他项不修改、不删除
- 明确记录：`add_schedule` 未改
- 明确记录：`update_future=True` 路径未改
- 明确记录：未新增 `parent_id`
- 明确记录：未新增 `每年/yearly/daily/weekly/monthly` 行为
- 临时数据标题前缀
- 临时重复组创建数量和 `group_id`
- 被选中的中间项 id
- `update_schedule_with_repeat(..., update_future=False)` 返回结果
- 当前条更新结果和脱组结果
- 原组剩余数量
- 其他组内条目是否未被修改
- 删除脱组当前条结果
- 删除剩余临时组结果
- 前缀残留检查结果
- `schedule.db` 是否无 tracked diff
- service import / db import 验证结果
- service 静态依赖检查结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
