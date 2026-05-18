请执行第四轮 4-8b：取消重复路径条件收口复核。本轮优先复核，不默认改源码。

## 1. 本轮目标

基于第四轮合同、4-7b 和 4-8a 结论，复核 `update_schedule_with_repeat(update_future=True)` 的取消重复路径是否已经因 4-7b 的旧未来删除策略委托而满足当前架构边界。

本轮是条件执行/收口工单，不是强制源码改造。

本轮目标：

- 复核取消重复路径是否已复用 `ScheduleService.delete_future_schedules_for_group(...)`。
- 若已满足边界：不改源码，只记录“4-8b 无需额外源码改造”。
- 若发现取消重复路径仍有明显重复旧未来删除逻辑：只允许做最小修正，使其复用既有 `ScheduleService.delete_future_schedules_for_group(...)`。
- 跑一次取消重复路径回归。
- 跑一次 4-7b 保护回归。
- 最终 `schedule.db` 无 tracked diff。

本轮不迁移：

- 当前条 update。
- 事务边界。
- 新未来重建。
- `insert_many` / `batch_size=100`。
- UI。
- 模型字段。
- Repository。

## 2. 允许/禁止

本轮允许修改：

- `src/data/database.py`（仅当发现取消重复路径没有复用既有旧未来删除委托时）
- `src/services/schedule_service.py`（原则上不改；仅当既有方法极小签名/命名问题导致无法复用时）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮预期：

- 大概率不改源码。
- 只更新 `Work_Log.md` 和必要的 `Work_Task_Prompts.md`。

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
- 不修改已有重复组改重复路径的新未来重建逻辑。
- 不迁移当前条 update。
- 不迁移事务。
- 不迁移 `insert_many` / `batch_size=100`。
- 不修改 `ScheduleRepeatService.build_repeat_insert_plan(...)`。
- 不新增 `parent_id`。
- 不新增 `每年 / yearly / daily / weekly / monthly` 行为。
- 不修改 UI 的 `group_id` 内存态同步。
- 不修改数据库字段、迁移逻辑、表名、默认值。
- 不改变 `db_manager.update_schedule_with_repeat(...)` 方法名、参数、返回语义。
- 不保留临时数据。
- 不保留 `schedule.db` tracked diff。

若临时数据创建、更新、清理任一环节失败，立即停止后续验证，并在 `Work_Log.md` 记录临时标题前缀、原 `group_id`、失败位置和需要人工清理的信息。

## 3. 具体任务

1. 读取：
   - `manage_instruction/Work_Instruction.md`
   - `manage_instruction/Work_Log.md` 中 4-7b 和 4-8a 结论

2. 静态复核当前代码：
   - `src/data/database.py` 中 `update_schedule_with_repeat`
   - `src/services/schedule_service.py`
   - 确认 `if old_group_id:` 下旧未来删除已经调用 `ScheduleService.delete_future_schedules_for_group(...)`。
   - 确认取消重复路径走的是同一个旧未来删除委托。
   - 确认新规则为 `none / 无 / 不重复 / ''` 时：
     - 当前条 `group_id=None`
     - 当前条先 update
     - 执行旧未来删除委托
     - 不进入 `build_repeat_insert_plan(..., include_base=False)` 未来重建分支

3. 判断是否需要源码修改：
   - 若取消重复路径已复用 4-7b 的旧未来删除委托：不改源码。
   - 若仍存在重复内联删除逻辑：仅做最小修正，使其复用既有委托。
   - 不做任何额外抽象。

4. 执行取消重复路径回归：
   - 创建 `每周` 临时重复组。
   - 选中第 11 条 `rows[10]`。
   - 用 `update_future=True` 改为 `none`。
   - 验证当前条脱组、旧未来删除、不重建未来、旧保留实例仍存在。
   - 清理当前条和剩余旧组。

5. 执行 4-7b 保护回归：
   - 创建 `每周` 临时重复组。
   - 选中第 11 条 `rows[10]`。
   - 用 `update_future=True` 改为 `每月`。
   - 验证旧保留、新重建、旧未来删除、最终同组 23 条。
   - 清理整组。

6. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

静态复核取消重复路径是否已复用既有委托：

`rg -n "def update_schedule_with_repeat|new_rule|group_id.*None|delete_future_schedules_for_group|Schedule\.delete|build_repeat_insert_plan|include_base=False|insert_many|db\.atomic|return True|return False" src/data/database.py src/services/schedule_service.py`

人工复核该输出，确认：

- `ScheduleService.delete_future_schedules_for_group(...)` 存在。
- `DatabaseManager.update_schedule_with_repeat(...)` 的旧未来删除位置已调用该方法。
- 取消重复路径没有单独重复一套内联旧未来删除逻辑。
- 新规则为 `none / 无 / 不重复 / ''` 时不会进入未来重建分支。
- 当前条 update、事务、新未来重建、`insert_many` 均未被迁移或改动。

service / db import 验证：

`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; from src.services.schedule_service import ScheduleService; from src.services.schedule_repeat_service import ScheduleRepeatService; print('imports ok', ScheduleService, ScheduleRepeatService, len(db_manager.get_all_schedules()))"`

取消重复路径回归：

`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -X utf8 -c "from src.data.database import db_manager; from src.data.models import Schedule; import datetime as dt,time,atexit; prefix='__tmp_4_8b_cancel_repeat_'+str(time.time_ns()); atexit.register(lambda: print('atexit cleanup by prefix', Schedule.delete().where(Schedule.title.startswith(prefix)).execute())); base_title=prefix+'_weekly_base'; print('prefix', prefix); data={'title':base_title,'item_type':'schedule','priority':0,'repeat_rule':'每周','description':'temporary 4-8b weekly base','category_id':None,'start_time':dt.datetime(2026,1,7,9,0),'end_time':dt.datetime(2026,1,7,10,0),'reminder_time':dt.datetime(2026,1,7,8,30)}; created=db_manager.add_schedule(data); print('created weekly group', created); assert created is True; rows=list(Schedule.select().where(Schedule.title==base_title).order_by(Schedule.start_time, Schedule.id)); print('initial rows', len(rows)); assert len(rows)==53; gid=rows[0].group_id; assert gid; target=rows[10]; target_id=target.id; target_start=target.start_time; target_end=target.end_time; target_reminder=target.reminder_time; before_old=[r for r in rows if r.start_time < target_start]; after_old=[r for r in rows if r.start_time > target_start]; print('target', target_id, target_start, 'before', len(before_old), 'after', len(after_old)); assert len(before_old)==10; assert len(after_old)==42; new_title=prefix+'_cancelled_current'; new_data={'title':new_title,'description':'temporary 4-8b cancel repeat','repeat_rule':'none','start_time':target_start,'end_time':target_end,'reminder_time':target_reminder}; updated=db_manager.update_schedule_with_repeat(target_id,new_data,update_future=True); print('cancel repeat update', updated); assert updated is True; current=Schedule.get_by_id(target_id); print('current', current.id, current.title, current.repeat_rule, current.group_id, current.start_time); assert current.title==new_title; assert current.repeat_rule=='none'; assert current.group_id is None; remaining_group=list(Schedule.select().where(Schedule.group_id==gid).order_by(Schedule.start_time, Schedule.id)); print('remaining original group', len(remaining_group)); assert len(remaining_group)==10; assert all(r.start_time < target_start for r in remaining_group); assert all(r.title==base_title for r in remaining_group); old_future_left=[r.id for r in remaining_group if r.start_time > target_start]; print('old future left', old_future_left); assert old_future_left==[]; new_future_left=list(Schedule.select().where((Schedule.title==new_title) & (Schedule.id != target_id))); print('new future left', len(new_future_left)); assert len(new_future_left)==0; deleted_current=Schedule.delete().where(Schedule.id==target_id).execute(); print('deleted current', deleted_current); assert deleted_current==1; deleted_group=Schedule.delete().where(Schedule.group_id==gid).execute(); print('deleted remaining group', deleted_group); assert deleted_group==10; leftovers=Schedule.select().where(Schedule.title.startswith(prefix)).count(); print('leftovers', leftovers); assert leftovers==0"`

4-7b 保护回归：

`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -X utf8 -c "from src.data.database import db_manager; from src.data.models import Schedule; import datetime as dt,time,atexit; prefix='__tmp_4_8b_existing_group_guard_'+str(time.time_ns()); atexit.register(lambda: print('atexit cleanup by prefix', Schedule.delete().where(Schedule.title.startswith(prefix)).execute())); base_title=prefix+'_weekly_base'; data={'title':base_title,'item_type':'schedule','priority':0,'repeat_rule':'每周','description':'guard 4-7b path','category_id':None,'start_time':dt.datetime(2026,1,7,9,0),'end_time':dt.datetime(2026,1,7,10,0),'reminder_time':dt.datetime(2026,1,7,8,30)}; assert db_manager.add_schedule(data) is True; rows=list(Schedule.select().where(Schedule.title==base_title).order_by(Schedule.start_time, Schedule.id)); assert len(rows)==53; gid=rows[0].group_id; target=rows[10]; target_start=target.start_time; new_title=prefix+'_monthly_updated'; ok=db_manager.update_schedule_with_repeat(target.id,{'title':new_title,'repeat_rule':'每月','start_time':target.start_time,'end_time':target.end_time,'reminder_time':target.reminder_time},update_future=True); print('existing group monthly ok', ok); assert ok is True; group_rows=list(Schedule.select().where(Schedule.group_id==gid).order_by(Schedule.start_time, Schedule.id)); print('group rows', len(group_rows)); assert len(group_rows)==23; preserved=[r for r in group_rows if r.start_time < target_start]; rebuilt=[r for r in group_rows if r.start_time > target_start]; assert len(preserved)==10; assert len(rebuilt)==12; deleted=Schedule.delete().where(Schedule.group_id==gid).execute(); print('deleted', deleted); assert deleted==23; leftovers=Schedule.select().where(Schedule.title.startswith(prefix)).count(); print('leftovers', leftovers); assert leftovers==0"`

确认临时前缀无残留：

`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.models import Schedule; prefixes=['__tmp_4_8b_cancel_repeat_','__tmp_4_8b_existing_group_guard_']; rows=[(p, Schedule.select().where(Schedule.title.startswith(p)).count()) for p in prefixes]; print(rows); assert all(c==0 for _, c in rows)"`

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
- 若无需源码修正，最终只允许：
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`
- 若确需最小源码修正，最终只允许额外包含：
  - `src/data/database.py`
  - `src/services/schedule_service.py`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第四轮 4-8b（取消重复路径条件收口复核）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 是否改源码；若未改，明确写“4-8b 无需额外源码改造”
- 静态复核结论：取消重复路径是否已复用 `ScheduleService.delete_future_schedules_for_group(...)`
- 明确记录：未迁移当前条 update
- 明确记录：未迁移事务边界
- 明确记录：未迁移新未来重建
- 明确记录：未修改 `insert_many` / `batch_size=100`
- 明确记录：未修改 `add_schedule`
- 明确记录：未修改 `update_future=False` 路径
- 明确记录：未修改非组转重复路径
- 明确记录：未修改已有重复组改重复路径的新未来重建逻辑
- 明确记录：未新增 `parent_id`
- 明确记录：未新增 `每年/yearly/daily/weekly/monthly` 行为
- 取消重复路径回归结果：
  - 临时数据标题前缀
  - 原 `group_id`
  - 被选中的中间项 id
  - 更新后当前条 `group_id`
  - 更新后保留旧实例数量
  - 更新后旧未来实例残留检查结果
  - 更新后新未来实例残留检查结果
  - 删除脱组当前条结果
  - 删除剩余旧实例结果
  - 前缀残留检查结果
- 4-7b 保护回归结果
- `schedule.db` 是否无 tracked diff
- service import / db import 验证结果
- service 静态依赖检查结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
