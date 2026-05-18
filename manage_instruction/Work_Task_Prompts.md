请执行第四轮 4-7a：已有重复组 `update_future=True` 未来更新路径行为基线验收。本轮只做行为基线验收，不做源码委托改造。

## 1. 本轮目标

基于第四轮合同和 4-0 ~ 4-6 结论，验证 `DatabaseManager.update_schedule_with_repeat(schedule_id, new_data, update_future=True)` 在“已有重复组中选中一条，并选择影响未来”时的旧行为边界。

这是第四轮风险最高路径之一。本轮只做 4-7a 行为基线，不做 4-7b 委托改造。

本轮重点验证：

- 创建一个临时重复组。
- 选中该重复组中间一条。
- 使用 `update_future=True` 修改当前条及未来。
- 验证当前之前的旧实例保留。
- 验证当前条本体更新。
- 验证旧未来实例被删除。
- 验证新未来实例被重建。
- 验证 `group_id` 沿用旧组。
- 验证新未来实例数量与新规则一致。
- 验证清理覆盖：
  - 当前之前保留的旧实例。
  - 当前条。
  - 新重建的未来实例。
- 最终 `schedule.db` 无 tracked diff。

本轮默认不改源码。若发现行为与合同不符，只记录风险，不直接修改源码。

## 2. 允许/禁止

本轮允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- `src/data/database.py`
- `src/services/schedule_service.py`
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

- 不修改源码。
- 不做 4-7b 委托改造。
- 不修改 `add_schedule`。
- 不修改 `update_future=False` 路径。
- 不处理取消重复路径。
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
   - `manage_instruction/Work_Log.md` 中 4-0 ~ 4-6 结论

2. 复核当前代码：
   - `src/data/database.py` 中 `update_schedule_with_repeat`
   - 确认已有 `old_group_id` 且 `update_future=True` 时：
     - 沿用旧 `group_id`
     - 当前条先执行 `Schedule.update(...)`
     - 删除旧未来实例
     - 使用 `ScheduleRepeatService.build_repeat_insert_plan(..., include_base=False)` 重建新未来项
     - 未来项通过 `insert_many` 写入
     - 成功返回 `True`

3. 使用临时重复组进行行为基线验收：
   - 标题前缀固定为：`__tmp_4_7a_existing_group_`
   - 先创建一个 `repeat_rule='每周'` 的临时重复组。
   - 预期初始同组 53 条。
   - 按 `start_time, id` 排序后选中第 11 条，即 `rows[10]`。
   - 记录：
     - 原 `group_id`
     - 目标条 `id`
     - 目标条原 `start_time`
     - 目标条之前旧实例数量
     - 目标条之后旧未来实例数量
   - 调用 `db_manager.update_schedule_with_repeat(target_id, new_data, update_future=True)`。
   - 将规则从 `每周` 改为 `每月`，并更新标题/描述。
   - 验证：
     - 返回 `True`。
     - 当前条仍使用原 `group_id`。
     - 当前条标题/描述/规则已更新。
     - 当前之前的旧实例保留，数量为 10。
     - 当前之后的原每周未来实例已删除。
     - 新每月未来实例生成 12 条。
     - 同组最终总数为 23：旧保留 10 + 当前 1 + 新未来 12。
     - 新未来实例标题/规则为新值。
     - 第一个新未来项时间比当前条晚 1 个月。
     - 第二个新未来项时间比当前条晚 2 个月。
   - 清理：
     - 按 `group_id` 删除整组。
     - 确认前缀无残留。

4. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

静态复核已有重复组 `update_future=True` 路径：

`rg -n "def update_schedule_with_repeat|old_group_id|group_id|update_future|Schedule\.update|Schedule\.delete|start_time >|end_time >|id >|build_repeat_insert_plan|include_base=False|insert_many|return True|return False" src/data/database.py`

人工复核该输出，确认：

- `old_group_id` 存在时沿用旧 `group_id`。
- 当前条先执行 `Schedule.update(...)`。
- 删除旧未来实例的分支存在。
- 删除旧未来实例按 `start_time` / `end_time` / `id` 回退策略执行。
- 新未来项使用 `build_repeat_insert_plan(..., include_base=False)` 生成。
- 本轮不修改源码。

service / db import 验证：

`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; from src.services.schedule_repeat_service import ScheduleRepeatService; print('imports ok', ScheduleRepeatService, len(db_manager.get_all_schedules()))"`

已有重复组中间项 `update_future=True` 行为验收：

`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -X utf8 -c "from src.data.database import db_manager; from src.data.models import Schedule; import datetime as dt,time,atexit; prefix='__tmp_4_7a_existing_group_'+str(time.time_ns()); atexit.register(lambda: print('atexit cleanup by prefix', Schedule.delete().where(Schedule.title.startswith(prefix)).execute())); base_title=prefix+'_weekly_base'; print('prefix', prefix); data={'title':base_title,'item_type':'schedule','priority':0,'repeat_rule':'每周','description':'temporary 4-7a weekly base','category_id':None,'start_time':dt.datetime(2026,1,7,9,0),'end_time':dt.datetime(2026,1,7,10,0),'reminder_time':dt.datetime(2026,1,7,8,30)}; created=db_manager.add_schedule(data); print('created weekly group', created); assert created is True; rows=list(Schedule.select().where(Schedule.title==base_title).order_by(Schedule.start_time, Schedule.id)); print('initial rows', len(rows)); assert len(rows)==53; gids={r.group_id for r in rows}; print('initial gids', gids); assert len(gids)==1; gid=next(iter(gids)); assert gid; target=rows[10]; target_id=target.id; target_start=target.start_time; target_end=target.end_time; target_reminder=target.reminder_time; before_old=[r for r in rows if r.start_time < target_start]; after_old=[r for r in rows if r.start_time > target_start]; print('target', target_id, target_start, 'before', len(before_old), 'after', len(after_old)); assert len(before_old)==10; assert len(after_old)==42; new_title=prefix+'_monthly_updated'; new_data={'title':new_title,'description':'temporary 4-7a monthly updated','repeat_rule':'每月','start_time':target_start,'end_time':target_end,'reminder_time':target_reminder}; updated=db_manager.update_schedule_with_repeat(target_id,new_data,update_future=True); print('updated existing group future', updated); assert updated is True; current=Schedule.get_by_id(target_id); print('current', current.id, current.title, current.repeat_rule, current.group_id, current.start_time); assert current.group_id==gid; assert current.title==new_title; assert current.repeat_rule=='每月'; group_rows=list(Schedule.select().where(Schedule.group_id==gid).order_by(Schedule.start_time, Schedule.id)); print('group rows after', len(group_rows)); assert len(group_rows)==23; preserved=[r for r in group_rows if r.start_time < target_start]; rebuilt=[r for r in group_rows if r.start_time > target_start]; print('preserved', len(preserved), 'rebuilt', len(rebuilt)); assert len(preserved)==10; assert all(r.title==base_title for r in preserved); assert len(rebuilt)==12; assert all(r.title==new_title for r in rebuilt); assert all(r.repeat_rule=='每月' for r in rebuilt); print('first rebuilt starts', [r.start_time for r in rebuilt[:2]]); assert rebuilt[0].start_time==dt.datetime(2026,4,18,9,0); assert rebuilt[1].start_time==dt.datetime(2026,5,18,9,0); old_future_left=[r.id for r in group_rows if r.title==base_title and r.start_time > target_start]; print('old future left', old_future_left); assert old_future_left==[]; deleted=Schedule.delete().where(Schedule.group_id==gid).execute(); print('deleted group', deleted); assert deleted==23; leftovers=Schedule.select().where(Schedule.title.startswith(prefix)).count(); print('leftovers', leftovers); assert leftovers==0"`

确认临时前缀无残留：

`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.models import Schedule; prefix='__tmp_4_7a_existing_group_'; count=Schedule.select().where(Schedule.title.startswith(prefix)).count(); print('tmp 4-7a leftovers', count); assert count==0"`

确认未新增不允许规则和字段：

`rg -n "每年|yearly|daily|weekly|monthly|parent_id" src/data/database.py src/services/schedule_repeat_service.py src/services/schedule_service.py`

预期：不应出现新增实现分支；如只在既有文本、注释或无关上下文中出现，需在日志说明。

service 静态依赖检查：

`rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_repeat_service.py src/services/schedule_service.py`

预期：无输出，退出码 1 视为通过。

语法检查：

`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src\services\schedule_repeat_service.py src\services\schedule_service.py src\data\database.py`

范围检查：

`git diff --name-only -- src/data/database.py`

`git diff --name-only -- src/services/schedule_service.py`

`git diff --name-only -- src/services/schedule_repeat_service.py`

`git diff --name-only -- src/ui`

`git diff --name-only -- src/data/models.py`

`git diff --name-only -- src/repositories`

`git diff --name-only -- main.py`

`git diff --name-only -- requirements.txt`

`git diff --name-only -- schedule.db`

`git diff --name-only`

`git status --short --branch`

预期：

- `src/data/database.py` 无 diff。
- `src/services/schedule_service.py` 无 diff。
- `src/services/schedule_repeat_service.py` 无 diff。
- `src/ui` 无 diff。
- `src/data/models.py` 无 diff。
- `src/repositories` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- 最终只允许：
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第四轮 4-7a（已有重复组 update_future=True 未来更新路径行为基线）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 是否改源码；预期为“否，本轮仅做行为基线验收”
- 已有重复组 `update_future=True` 路径静态复核结论
- 是否保持：沿用旧 `group_id`
- 是否保持：当前条本体先更新
- 是否保持：当前之前旧实例保留
- 是否保持：旧未来实例删除
- 是否保持：新未来实例重建
- 是否保持：同组最终总数为 23
- 是否保持：新未来项时间偏移正确
- 明确记录：`add_schedule` 未改
- 明确记录：`update_future=False` 路径未改
- 明确记录：非组转重复路径未改
- 明确记录：取消重复路径未处理
- 明确记录：未新增 `parent_id`
- 明确记录：未新增 `每年/yearly/daily/weekly/monthly` 行为
- 临时数据标题前缀
- 原 `group_id`
- 被选中的中间项 id
- 被选中的中间项原 `start_time`
- 更新前当前之前旧实例数量
- 更新前当前之后旧未来实例数量
- 更新后当前条标题/规则/`group_id`
- 更新后保留旧实例数量
- 更新后新未来实例数量
- 更新后旧未来实例残留检查结果
- 第一个和第二个新未来项时间
- 删除整组结果
- 前缀残留检查结果
- `schedule.db` 是否无 tracked diff
- service import / db import 验证结果
- service 静态依赖检查结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点
- 是否建议进入 4-7b；如果行为基线仍有疑点，应记录“不建议进入 4-7b”

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
