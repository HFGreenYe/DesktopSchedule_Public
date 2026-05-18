请执行第四轮 4-4：`add_schedule` 重复路径委托收口与写入验收。本轮只处理 `DatabaseManager.add_schedule(data)` 的重复路径，不处理 `update_schedule_with_repeat`。

## 1. 本轮目标

基于第四轮合同和 4-0 ~ 4-3 结论，确认并收口 `add_schedule` 的重复路径委托。

当前重复路径已通过 `ScheduleRepeatService.build_repeat_insert_plan(...)` 生成待插入计划。本轮重点是：

- 复核 `add_schedule` 重复路径是否已经正确委托生成计划。
- 如已满足边界，默认不改源码，只做重复写入验收并记录。
- 如发现重复路径仍有未委托或边界不符，只做最小修正。
- 验证 `每天 / 每周 / 每月` 三类重复新增行为。
- 验证生成数量不变：
  - `每天`：366 条。
  - `每周`：53 条。
  - `每月`：13 条。
- 验证同批生成项 `group_id` 一致。
- 验证后必须按 `group_id` 清理临时数据。
- 最终 `schedule.db` 无 tracked diff。

本轮不处理：

- `add_schedule` 非重复路径。
- `update_schedule_with_repeat`。
- UI。
- Repository。
- 模型字段。
- 迁移逻辑。

## 2. 允许/禁止

本轮允许修改：

- `src/data/database.py`（仅当重复路径委托边界不符合时，做最小修正）
- `src/services/schedule_repeat_service.py`（仅当生成计划边界不符合时，做最小修正）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮默认预期：

- 不改源码。
- 只更新 `Work_Log.md` 和必要的 `Work_Task_Prompts.md`。

本轮禁止修改：

- `src/services/schedule_service.py`
- `src/ui/`
- `src/data/models.py`
- `src/repositories/`
- `main.py`
- `requirements.txt`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不修改 `add_schedule` 非重复路径。
- 不修改 `update_schedule_with_repeat`。
- 不新增 `parent_id`。
- 不新增 `每年 / yearly / daily / weekly / monthly` 行为。
- 不改变 `每天 / 每周 / 每月` 生成数量。
- 不改变 `group_id` 语义。
- 不改变 `db.atomic`、`insert_many`、`batch_size=100` 的职责归属。
- 不改变 `DatabaseManager.add_schedule(data)` 成功 `True`、失败 `False` 的返回语义。
- 不让 service 依赖 UI / db_manager / Repository。
- 不保留临时数据。
- 不保留 `schedule.db` tracked diff；允许为了验收临时写入，但必须清理。

若任一临时重复组清理失败，立即停止后续验证，并在 `Work_Log.md` 记录失败规则、临时标题前缀、`group_id`、失败原因和需要人工清理的信息。

## 3. 具体任务

1. 读取：
   - `manage_instruction/Work_Instruction.md`
   - `manage_instruction/Work_Log.md` 中 4-0 ~ 4-3 结论

2. 复核当前代码：
   - `src/data/database.py` 中 `add_schedule`
   - `src/services/schedule_repeat_service.py`
   - 确认重复路径仍通过 `ScheduleRepeatService.build_repeat_insert_plan(data, rule, group_id, include_base=True)` 生成计划。
   - 确认 `DatabaseManager` 仍负责：
     - 创建 `group_id`
     - `db.atomic`
     - `insert_many`
     - `batch_size=100`
     - `True / False` 返回

3. 判断是否需要源码修改：
   - 若重复路径已符合上述边界：不改源码。
   - 若不符合：只做最小修正，且不得影响非重复路径和 `update_schedule_with_repeat`。

4. 执行三组临时重复写入验收：
   - 标题前缀固定为：`__tmp_4_4_repeat_`
   - 分别验证规则：
     - `每天`
     - `每周`
     - `每月`
   - 每组创建后立即确认数量、`group_id`，再按 `group_id` 清理。
   - 任一清理失败立即停止。

5. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

静态复核重复路径：

```cmd
rg -n "def add_schedule|build_repeat_insert_plan|uuid|group_id|with db\.atomic|batch_size|insert_many|return True|return False|create_single_schedule|update_schedule_with_repeat" src/data/database.py
```

人工复核该输出，确认：

- 非重复路径仍调用 `ScheduleService.create_single_schedule(...)`。
- 重复路径仍调用 `ScheduleRepeatService.build_repeat_insert_plan(..., include_base=True)`。
- `group_id` 仍在 `DatabaseManager.add_schedule` 中创建。
- `db.atomic`、`insert_many`、`batch_size=100` 仍在 `DatabaseManager.add_schedule` 中。
- `update_schedule_with_repeat` 未被本轮修改。

service import 验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.services.schedule_repeat_service import ScheduleRepeatService; from src.data.database import db_manager; print('imports ok', ScheduleRepeatService, len(db_manager.get_all_schedules()))"
```

三组重复临时写入/清理验证。

注意：使用 `-X utf8` 避免 `database.py` 中 `✅/❌` 日志在 GBK 控制台触发 `UnicodeEncodeError`；每条规则单独执行，避免 PowerShell 对多行 `python -c` 展开失败。

验证 `每天`：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -X utf8 -c "from src.data.database import db_manager; from src.data.models import Schedule; import datetime as dt,time,atexit; rule='每天'; expected=366; title='__tmp_4_4_repeat_'+str(time.time_ns())+'_'+rule; atexit.register(lambda: print('atexit cleanup by title', Schedule.delete().where(Schedule.title==title).execute())); data={'title':title,'item_type':'schedule','priority':0,'repeat_rule':rule,'description':'temporary 4-4 repeat validation','category_id':None,'start_time':dt.datetime(2026,1,31,9,0),'end_time':dt.datetime(2026,1,31,10,0),'reminder_time':dt.datetime(2026,1,31,8,30)}; ok=db_manager.add_schedule(data); print('created', rule, ok); assert ok is True; matches=list(Schedule.select().where(Schedule.title==title)); print('matches', len(matches)); assert len(matches)==expected; gids={m.group_id for m in matches}; print('group ids', gids); assert len(gids)==1; gid=next(iter(gids)); assert gid; deleted=Schedule.delete().where(Schedule.group_id==gid).execute(); print('deleted', deleted); assert deleted==expected; remaining=Schedule.select().where(Schedule.group_id==gid).count(); print('remaining', remaining); assert remaining==0"
```

验证 `每周`：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -X utf8 -c "from src.data.database import db_manager; from src.data.models import Schedule; import datetime as dt,time,atexit; rule='每周'; expected=53; title='__tmp_4_4_repeat_'+str(time.time_ns())+'_'+rule; atexit.register(lambda: print('atexit cleanup by title', Schedule.delete().where(Schedule.title==title).execute())); data={'title':title,'item_type':'schedule','priority':0,'repeat_rule':rule,'description':'temporary 4-4 repeat validation','category_id':None,'start_time':dt.datetime(2026,1,31,9,0),'end_time':dt.datetime(2026,1,31,10,0),'reminder_time':dt.datetime(2026,1,31,8,30)}; ok=db_manager.add_schedule(data); print('created', rule, ok); assert ok is True; matches=list(Schedule.select().where(Schedule.title==title)); print('matches', len(matches)); assert len(matches)==expected; gids={m.group_id for m in matches}; print('group ids', gids); assert len(gids)==1; gid=next(iter(gids)); assert gid; deleted=Schedule.delete().where(Schedule.group_id==gid).execute(); print('deleted', deleted); assert deleted==expected; remaining=Schedule.select().where(Schedule.group_id==gid).count(); print('remaining', remaining); assert remaining==0"
```

验证 `每月`：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -X utf8 -c "from src.data.database import db_manager; from src.data.models import Schedule; import datetime as dt,time,atexit; rule='每月'; expected=13; title='__tmp_4_4_repeat_'+str(time.time_ns())+'_'+rule; atexit.register(lambda: print('atexit cleanup by title', Schedule.delete().where(Schedule.title==title).execute())); data={'title':title,'item_type':'schedule','priority':0,'repeat_rule':rule,'description':'temporary 4-4 repeat validation','category_id':None,'start_time':dt.datetime(2026,1,31,9,0),'end_time':dt.datetime(2026,1,31,10,0),'reminder_time':dt.datetime(2026,1,31,8,30)}; ok=db_manager.add_schedule(data); print('created', rule, ok); assert ok is True; matches=list(Schedule.select().where(Schedule.title==title)); print('matches', len(matches)); assert len(matches)==expected; gids={m.group_id for m in matches}; print('group ids', gids); assert len(gids)==1; gid=next(iter(gids)); assert gid; deleted=Schedule.delete().where(Schedule.group_id==gid).execute(); print('deleted', deleted); assert deleted==expected; remaining=Schedule.select().where(Schedule.group_id==gid).count(); print('remaining', remaining); assert remaining==0"
```

确认临时数据前缀无残留：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.models import Schedule; prefix='__tmp_4_4_repeat_'; count=Schedule.select().where(Schedule.title.startswith(prefix)).count(); print('tmp repeat leftovers', count); assert count==0"
```

确认未新增不允许规则：

```cmd
rg -n "每年|yearly|daily|weekly|monthly|parent_id" src/data/database.py src/services/schedule_repeat_service.py
```

预期：不应出现新增实现分支；如只在既有文本、注释或无关上下文中出现，需在日志说明。

service 静态依赖检查：

```cmd
rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_repeat_service.py
```

预期：无输出，退出码 1 视为通过。

语法检查：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src\services\schedule_repeat_service.py src\data\database.py
```

范围检查：

```cmd
git diff --name-only -- src/services/schedule_service.py
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

- `src/services/schedule_service.py` 无 diff。
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
  - 或 `src/services/schedule_repeat_service.py`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第四轮 4-4（add_schedule 重复路径委托收口与写入验收）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 是否改源码；如未改，明确写“重复路径已符合 4-2 委托边界，本轮仅验收”
- `add_schedule` 重复路径委托复核结论
- `DatabaseManager` 是否仍负责 `group_id / db.atomic / insert_many / batch_size / True-False`
- 明确记录：非重复路径未改
- 明确记录：`update_schedule_with_repeat` 未改
- 明确记录：未新增 `parent_id`
- 明确记录：未新增 `每年/yearly/daily/weekly/monthly` 行为
- 临时数据标题前缀
- `每天` 创建数量、`group_id` 一致性、清理数量、残留检查结果
- `每周` 创建数量、`group_id` 一致性、清理数量、残留检查结果
- `每月` 创建数量、`group_id` 一致性、清理数量、残留检查结果
- `schedule.db` 是否无 tracked diff
- service import 验证结果
- service 静态依赖检查结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
