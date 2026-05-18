请执行第四轮 4-6：`update_schedule_with_repeat(update_future=True)` 非组转重复路径行为验收。本轮只处理“原本非重复日程，修改为重复并影响未来”的路径。

## 1. 本轮目标

基于第四轮合同和 4-0 ~ 4-5 结论，验证 `DatabaseManager.update_schedule_with_repeat(schedule_id, new_data, update_future=True)` 在“原本无 `group_id` 的单次日程改为重复日程”时的旧行为边界。

本轮重点：

- 只关注：旧日程无 `group_id`，新规则为 `每天 / 每周 / 每月` 之一，且 `update_future=True`。
- 默认偏行为验收，不急于改源码。
- 验证旧行为：
  - 当前条获得新的 `group_id`。
  - 当前条本体被更新。
  - 未来实例被生成。
  - 同组生成项 `group_id` 一致。
  - 生成数量保持旧语义。
  - 时间偏移保持旧语义。
- 使用临时单次日程验收。
- 验证完成后按 `group_id` 清理整组。
- 最终 `schedule.db` 无 tracked diff。

本轮默认不改源码；如果发现当前行为不符合第四轮合同，只记录风险，不直接扩大改造范围。

## 2. 允许/禁止

本轮允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮默认禁止源码修改。

如确实发现 4-6 路径已有明显边界问题，需要先在 `Work_Log.md` 记录问题，不得直接大改源码；等待顾问窗口和决策窗口重新下发修正工单。

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

- 不修改 `add_schedule`。
- 不修改 `update_future=False` 路径。
- 不处理已有重复组的未来更新路径。
- 不处理取消重复路径。
- 不修改旧未来实例删除逻辑。
- 不修改未来实例重建逻辑。
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
   - `manage_instruction/Work_Log.md` 中 4-0 ~ 4-5 结论

2. 复核当前代码：
   - `src/data/database.py` 中 `update_schedule_with_repeat`
   - 确认 `update_future=True` 且旧条无 `group_id`、新规则为重复时：
     - 创建新 `group_id`
     - 当前条写入该 `group_id`
     - 当前条先更新
     - 使用 `ScheduleRepeatService.build_repeat_insert_plan(..., include_base=False)` 生成未来项
     - 未来项通过 `insert_many` 写入
     - 成功返回 `True`

3. 使用临时单次日程进行行为验收：
   - 标题前缀固定为：`__tmp_4_6_single_to_repeat_`
   - 先创建一个 `repeat_rule='none'` 的单次日程。
   - 确认初始 `group_id is None`。
   - 调用 `db_manager.update_schedule_with_repeat(single_id, new_data, update_future=True)`，把它改为 `每周`。
   - 验证：
     - 返回 `True`。
     - 当前条获得非空 `group_id`。
     - 当前条标题/描述/规则已更新。
     - 同组总数为 `53`：当前条 + 52 个未来项。
     - 同组所有项 `group_id` 一致。
     - 第一个未来项时间比当前条晚 1 周。
     - 第二个未来项时间比当前条晚 2 周。
   - 清理：
     - 按 `group_id` 删除整组。
     - 确认前缀无残留。

4. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

静态复核 `update_future=True` 非组转重复路径：

`rg -n "def update_schedule_with_repeat|old_group_id|not old_group_id|uuid|group_id|new_rule|Schedule\.update|Schedule\.delete|build_repeat_insert_plan|include_base=False|insert_many|return True|return False" src/data/database.py`

人工复核该输出，确认：

- `not old_group_id and new_rule not in ('none', '无', '不重复', '')` 时会创建新 `group_id`。
- 当前条会写入新 `group_id`。
- 当前条先执行 `Schedule.update(...)`。
- 非组转重复路径不会删除旧未来实例，因为旧条无 `group_id`。
- 未来项使用 `build_repeat_insert_plan(..., include_base=False)` 生成。
- 本轮不修改源码。

service / db import 验证：

`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; from src.services.schedule_repeat_service import ScheduleRepeatService; print('imports ok', ScheduleRepeatService, len(db_manager.get_all_schedules()))"`

临时单次日程改为重复日程验收：

`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -X utf8 -c "from src.data.database import db_manager; from src.data.models import Schedule; import datetime as dt,time,atexit; prefix='__tmp_4_6_single_to_repeat_'+str(time.time_ns()); atexit.register(lambda: print('atexit cleanup by prefix', Schedule.delete().where(Schedule.title.startswith(prefix)).execute())); title=prefix+'_single'; print('prefix', prefix); data={'title':title,'item_type':'schedule','priority':0,'repeat_rule':'none','description':'temporary 4-6 single base','category_id':None,'start_time':dt.datetime(2026,1,7,9,0),'end_time':dt.datetime(2026,1,7,10,0),'reminder_time':dt.datetime(2026,1,7,8,30)}; created=db_manager.add_schedule(data); print('created single', created); assert created is True; singles=list(Schedule.select().where(Schedule.title==title)); print('single matches', len(singles)); assert len(singles)==1; single=singles[0]; assert single.group_id is None; new_title=prefix+'_repeat_weekly'; new_data={'title':new_title,'description':'temporary 4-6 converted to weekly repeat','repeat_rule':'每周','start_time':dt.datetime(2026,1,7,9,0),'end_time':dt.datetime(2026,1,7,10,0),'reminder_time':dt.datetime(2026,1,7,8,30)}; updated=db_manager.update_schedule_with_repeat(single.id,new_data,update_future=True); print('updated to repeat', updated); assert updated is True; current=Schedule.get_by_id(single.id); print('current', current.id, current.title, current.repeat_rule, current.group_id); assert current.title==new_title; assert current.repeat_rule=='每周'; assert current.group_id; gid=current.group_id; rows=list(Schedule.select().where(Schedule.group_id==gid).order_by(Schedule.start_time, Schedule.id)); print('group rows', len(rows)); assert len(rows)==53; assert all(r.group_id==gid for r in rows); assert rows[0].id==current.id; print('first three starts', [r.start_time for r in rows[:3]]); assert rows[1].start_time==dt.datetime(2026,1,14,9,0); assert rows[2].start_time==dt.datetime(2026,1,21,9,0); deleted=Schedule.delete().where(Schedule.group_id==gid).execute(); print('deleted group', deleted); assert deleted==53; leftovers=Schedule.select().where(Schedule.title.startswith(prefix)).count(); print('leftovers', leftovers); assert leftovers==0"`

确认临时前缀无残留：

`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.models import Schedule; prefix='__tmp_4_6_single_to_repeat_'; count=Schedule.select().where(Schedule.title.startswith(prefix)).count(); print('tmp 4-6 leftovers', count); assert count==0"`

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

- 本轮任务名称：第四轮 4-6（update_future=True 非组转重复路径行为验收）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 是否改源码；预期为“否，本轮仅做行为基线验收”
- `update_future=True` 非组转重复路径静态复核结论
- 是否保持：旧条无 `group_id` 时创建新 `group_id`
- 是否保持：当前条获得新 `group_id`
- 是否保持：当前条本体先更新
- 是否保持：未来实例生成数量为 52 个，加当前条同组共 53 条
- 是否保持：同组所有项 `group_id` 一致
- 是否保持：未来项时间偏移正确
- 明确记录：`add_schedule` 未改
- 明确记录：`update_future=False` 路径未改
- 明确记录：既有重复组未来更新路径未处理
- 明确记录：取消重复路径未处理
- 明确记录：未新增 `parent_id`
- 明确记录：未新增 `每年/yearly/daily/weekly/monthly` 行为
- 临时数据标题前缀
- 临时单次日程 id
- 更新后 `group_id`
- 同组总数
- 第一个和第二个未来项时间
- 删除整组结果
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
