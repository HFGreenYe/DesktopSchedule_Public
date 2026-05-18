请执行第四轮 4-7b：已有重复组 `update_future=True` 未来更新路径最小委托改造。本轮只做最小源码委托，不扩大到取消重复路径或 UI。

## 1. 本轮目标

基于第四轮合同和 4-7a 行为基线，将已有重复组 `update_future=True` 路径中“删除旧未来实例”的写入策略做最小 service 委托。

本轮只抽取一个明确边界：

- 从 `DatabaseManager.update_schedule_with_repeat(...)` 中，把“旧未来实例删除策略”委托到 `ScheduleService`。
- 保持 `DatabaseManager` 仍负责整体流程协调：
  - 判断 `update_future`
  - 判断新旧规则
  - 当前条 update
  - `group_id` 沿用或创建
  - 调用 `ScheduleRepeatService.build_repeat_insert_plan(..., include_base=False)`
  - `db.atomic`
  - `insert_many`
  - `True / False` 返回语义

本轮不抽取：

- 当前条更新逻辑。
- 新未来实例重建逻辑。
- 事务边界。
- `insert_many` 批量插入。
- 取消重复路径。
- UI 行为。

本轮完成后，4-7a 行为基线必须仍然通过：

- 当前之前旧实例保留。
- 当前条更新。
- 旧未来实例删除。
- 新未来实例重建。
- 同组最终总数保持 23。
- 清理后 `schedule.db` 无 tracked diff。

## 2. 允许/禁止

本轮允许修改：

- `src/services/schedule_service.py`
- `src/data/database.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- `src/services/schedule_repeat_service.py`
- `src/ui/`
- `src/data/models.py`
- `src/repositories/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不修改 `add_schedule`。
- 不修改 `update_future=False` 路径。
- 不修改非组转重复路径。
- 不处理取消重复路径。
- 不修改新未来实例重建逻辑。
- 不修改 `ScheduleRepeatService.build_repeat_insert_plan(...)`。
- 不修改 `db.atomic`、`insert_many`、`batch_size=100` 的职责归属。
- 不新增 `parent_id`。
- 不新增 `每年 / yearly / daily / weekly / monthly` 行为。
- 不修改 UI 的 `group_id` 内存态同步。
- 不修改数据库字段、迁移逻辑、表名、默认值。
- 不改变 `db_manager.update_schedule_with_repeat(...)` 方法名、参数、返回语义。
- 不保留临时数据。
- 不保留 `schedule.db` tracked diff。

若临时数据创建、更新、清理任一环节失败，立即停止后续验证，并在 `Work_Log.md` 记录临时标题前缀、`group_id`、失败位置和需要人工清理的信息。

## 3. 具体任务

1. 读取：
   - `manage_instruction/Work_Instruction.md`
   - `manage_instruction/Work_Log.md` 中 4-7a 结论

2. 阅读当前代码：
   - `src/data/database.py` 中 `update_schedule_with_repeat`
   - `src/services/schedule_service.py`

3. 在 `ScheduleService` 中新增一个最小方法，方法名可自定，建议边界如下：
   - `delete_future_schedules_for_group(schedule_model, old_group_id, schedule_id, current_schedule)`
   - 输入：
     - `schedule_model`
     - `old_group_id`
     - 当前 `schedule_id`
     - 当前 `current_schedule`
   - 行为必须完全保持旧逻辑：
     - 如果 `current_schedule.start_time` 存在：删除同组、非当前、`start_time > current_schedule.start_time` 的未来实例。
     - 否则如果 `current_schedule.end_time` 存在：删除同组、非当前、`end_time > current_schedule.end_time` 的未来实例。
     - 否则：删除同组、非当前、`id > schedule_id` 的未来实例。
   - 返回删除数量或 Peewee `execute()` 结果。
   - 不捕获异常，让 `DatabaseManager.update_schedule_with_repeat` 原有 `try/except` 处理。
   - 不导入 UI、db_manager、Repository。
   - 不修改模型字段。
   - 不处理新未来实例重建。

4. 修改 `DatabaseManager.update_schedule_with_repeat(...)`：
   - 仅把 `if old_group_id:` 下的旧未来删除块替换为调用 `ScheduleService`。
   - 保持调用位置不变：仍在当前条 `Schedule.update(...)` 之后、新未来重建之前。
   - 不改变 `update_future=False` 分支。
   - 不改变非组转重复路径。
   - 不改变取消重复路径。
   - 不改变 `ScheduleRepeatService.build_repeat_insert_plan(..., include_base=False)` 调用。
   - 不改变 `db.atomic`、`insert_many`、`batch_size=100`。
   - 不改变 `True / False` 返回语义。

5. 执行 4-7a 同等行为回归验收：
   - 创建 `每周` 临时重复组。
   - 选中第 11 条 `rows[10]`。
   - 用 `update_future=True` 改为 `每月`。
   - 验证旧保留、新重建、旧未来删除、最终数量、清理结果。

6. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

静态定位修改点：

`rg -n "delete_future|delete.*future|def update_schedule_with_repeat|old_group_id|Schedule\.delete|start_time >|end_time >|id >|build_repeat_insert_plan|include_base=False|insert_many|db\.atomic|return True|return False" src/data/database.py src/services/schedule_service.py`

人工复核该输出，确认：

- 旧未来删除策略已委托到 `ScheduleService`。
- `ScheduleService` 中保留 `start_time / end_time / id` 三段回退删除策略。
- `DatabaseManager.update_schedule_with_repeat` 中调用位置仍在当前条 update 之后、新未来重建之前。
- `ScheduleRepeatService.build_repeat_insert_plan(..., include_base=False)` 未改。
- `insert_many` / `db.atomic` / `batch_size=100` 未移动出 `database.py`。
- `update_future=False` 分支未改。
- `add_schedule` 未改。

service / db import 验证：

`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; from src.services.schedule_service import ScheduleService; from src.services.schedule_repeat_service import ScheduleRepeatService; print('imports ok', ScheduleService, ScheduleRepeatService, len(db_manager.get_all_schedules()))"`

已有重复组中间项 `update_future=True` 行为回归验收：

`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -X utf8 -c "from src.data.database import db_manager; from src.data.models import Schedule; import datetime as dt,time,atexit; prefix='__tmp_4_7b_existing_group_'+str(time.time_ns()); atexit.register(lambda: print('atexit cleanup by prefix', Schedule.delete().where(Schedule.title.startswith(prefix)).execute())); base_title=prefix+'_weekly_base'; print('prefix', prefix); data={'title':base_title,'item_type':'schedule','priority':0,'repeat_rule':'每周','description':'temporary 4-7b weekly base','category_id':None,'start_time':dt.datetime(2026,1,7,9,0),'end_time':dt.datetime(2026,1,7,10,0),'reminder_time':dt.datetime(2026,1,7,8,30)}; created=db_manager.add_schedule(data); print('created weekly group', created); assert created is True; rows=list(Schedule.select().where(Schedule.title==base_title).order_by(Schedule.start_time, Schedule.id)); print('initial rows', len(rows)); assert len(rows)==53; gids={r.group_id for r in rows}; print('initial gids', gids); assert len(gids)==1; gid=next(iter(gids)); assert gid; target=rows[10]; target_id=target.id; target_start=target.start_time; target_end=target.end_time; target_reminder=target.reminder_time; before_old=[r for r in rows if r.start_time < target_start]; after_old=[r for r in rows if r.start_time > target_start]; print('target', target_id, target_start, 'before', len(before_old), 'after', len(after_old)); assert len(before_old)==10; assert len(after_old)==42; new_title=prefix+'_monthly_updated'; new_data={'title':new_title,'description':'temporary 4-7b monthly updated','repeat_rule':'每月','start_time':target_start,'end_time':target_end,'reminder_time':target_reminder}; updated=db_manager.update_schedule_with_repeat(target_id,new_data,update_future=True); print('updated existing group future', updated); assert updated is True; current=Schedule.get_by_id(target_id); print('current', current.id, current.title, current.repeat_rule, current.group_id, current.start_time); assert current.group_id==gid; assert current.title==new_title; assert current.repeat_rule=='每月'; group_rows=list(Schedule.select().where(Schedule.group_id==gid).order_by(Schedule.start_time, Schedule.id)); print('group rows after', len(group_rows)); assert len(group_rows)==23; preserved=[r for r in group_rows if r.start_time < target_start]; rebuilt=[r for r in group_rows if r.start_time > target_start]; print('preserved', len(preserved), 'rebuilt', len(rebuilt)); assert len(preserved)==10; assert all(r.title==base_title for r in preserved); assert len(rebuilt)==12; assert all(r.title==new_title for r in rebuilt); assert all(r.repeat_rule=='每月' for r in rebuilt); print('first rebuilt starts', [r.start_time for r in rebuilt[:2]]); assert rebuilt[0].start_time==dt.datetime(2026,4,18,9,0); assert rebuilt[1].start_time==dt.datetime(2026,5,18,9,0); old_future_left=[r.id for r in group_rows if r.title==base_title and r.start_time > target_start]; print('old future left', old_future_left); assert old_future_left==[]; deleted=Schedule.delete().where(Schedule.group_id==gid).execute(); print('deleted group', deleted); assert deleted==23; leftovers=Schedule.select().where(Schedule.title.startswith(prefix)).count(); print('leftovers', leftovers); assert leftovers==0"`

确认临时前缀无残留：

`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.models import Schedule; prefix='__tmp_4_7b_existing_group_'; count=Schedule.select().where(Schedule.title.startswith(prefix)).count(); print('tmp 4-7b leftovers', count); assert count==0"`

确认 4-5 路径未被破坏，执行一个轻量行为回归：

`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -X utf8 -c "from src.data.database import db_manager; from src.data.models import Schedule; import datetime as dt,time,atexit; prefix='__tmp_4_7b_current_only_guard_'+str(time.time_ns()); atexit.register(lambda: print('atexit cleanup by prefix', Schedule.delete().where(Schedule.title.startswith(prefix)).execute())); title=prefix+'_base'; data={'title':title,'item_type':'schedule','priority':0,'repeat_rule':'每周','description':'guard 4-5 path','category_id':None,'start_time':dt.datetime(2026,1,7,9,0),'end_time':dt.datetime(2026,1,7,10,0),'reminder_time':dt.datetime(2026,1,7,8,30)}; assert db_manager.add_schedule(data) is True; rows=list(Schedule.select().where(Schedule.title==title).order_by(Schedule.start_time, Schedule.id)); assert len(rows)==53; gid=rows[0].group_id; target=rows[10]; new_title=prefix+'_current_only'; ok=db_manager.update_schedule_with_repeat(target.id,{'title':new_title,'repeat_rule':'每周'},update_future=False); print('current only ok', ok); assert ok is True; refreshed=Schedule.get_by_id(target.id); assert refreshed.group_id is None; assert refreshed.title==new_title; remaining=Schedule.select().where(Schedule.group_id==gid).count(); print('remaining old group', remaining); assert remaining==52; deleted_current=Schedule.delete().where(Schedule.id==target.id).execute(); deleted_group=Schedule.delete().where(Schedule.group_id==gid).execute(); print('deleted', deleted_current, deleted_group); assert deleted_current==1; assert deleted_group==52; leftovers=Schedule.select().where(Schedule.title.startswith(prefix)).count(); print('leftovers', leftovers); assert leftovers==0"`

确认未新增不允许规则和字段：

`rg -n "每年|yearly|daily|weekly|monthly|parent_id" src/data/database.py src/services/schedule_repeat_service.py src/services/schedule_service.py`

预期：不应出现新增实现分支；如只在既有文本、注释或无关上下文中出现，需在日志说明。

service 静态依赖检查：

`rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_repeat_service.py src/services/schedule_service.py`

预期：无输出，退出码 1 视为通过。

语法检查：

`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src\services\schedule_repeat_service.py src\services\schedule_service.py src\data\database.py`

范围检查：

`git diff --name-only -- src/ui`

`git diff --name-only -- src/data/models.py`

`git diff --name-only -- src/repositories`

`git diff --name-only -- main.py`

`git diff --name-only -- requirements.txt`

`git diff --name-only -- schedule.db`

`git diff --name-only`

`git status --short --branch`

预期：

- `src/ui` 无 diff。
- `src/data/models.py` 无 diff。
- `src/repositories` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- 最终只允许：
  - `src/data/database.py`
  - `src/services/schedule_service.py`
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第四轮 4-7b（已有重复组 update_future=True 旧未来删除策略最小委托）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 新增/修改的 `ScheduleService` 方法名
- 委托前后边界说明
- 明确记录：只委托旧未来删除策略
- 明确记录：当前条 update 未迁移
- 明确记录：新未来重建未迁移
- 明确记录：事务边界未改
- 明确记录：`insert_many` / `batch_size=100` 未改
- 明确记录：`add_schedule` 未改
- 明确记录：`update_future=False` 路径未改
- 明确记录：非组转重复路径未改
- 明确记录：取消重复路径未处理
- 明确记录：未新增 `parent_id`
- 明确记录：未新增 `每年/yearly/daily/weekly/monthly` 行为
- 4-7a 等价行为回归结果：
  - 临时数据标题前缀
  - 原 `group_id`
  - 被选中的中间项 id
  - 更新前当前之前旧实例数量
  - 更新前当前之后旧未来实例数量
  - 更新后保留旧实例数量
  - 更新后新未来实例数量
  - 更新后旧未来实例残留检查结果
  - 同组最终总数
  - 删除整组结果
  - 前缀残留检查结果
- 4-5 轻量回归结果
- `schedule.db` 是否无 tracked diff
- service import / db import 验证结果
- service 静态依赖检查结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
