请执行第四轮 4-2：重复规则待插入数据计划服务。本轮只抽取“根据 base data + repeat_rule + group_id 生成待插入数据计划”的纯逻辑，不写数据库。

## 1. 本轮目标

基于 `manage_instruction/Work_Instruction.md` 第四轮合同，以及 `Work_Log.md` 的 4-0 / 4-1 结论，继续完善 `ScheduleRepeatService`，把重复日程“待插入数据列表”的生成逻辑抽成纯函数。

本轮目标：

- 在 `src/services/schedule_repeat_service.py` 中实现重复计划生成纯逻辑。
- `add_schedule` 重复路径可委托 service 生成包含当前项的待插入数据计划。
- `update_schedule_with_repeat(update_future=True)` 未来重建路径可委托 service 生成未来项计划。
- `DatabaseManager` 仍负责：
  - 判断写入路径。
  - 创建或沿用 `group_id`。
  - 数据库事务。
  - `insert_many` 批量写入。
  - 返回 `True / False`。
- 不改变事务边界。
- 不改变批量插入流程。
- 不改变返回语义。
- 不写 `schedule.db`。

## 2. 允许/禁止

本轮允许修改：

- `src/services/schedule_repeat_service.py`
- `src/data/database.py`（仅用于委托生成待插入数据计划）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- `src/ui/`
- `src/data/models.py`
- `src/repositories/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不修改 UI。
- 不修改模型字段。
- 不新增数据库字段。
- 不新增 `parent_id`。
- 不改变 `add_schedule` 对外 API。
- 不改变 `update_schedule_with_repeat` 对外 API。
- 不改变 `add_schedule` / `update_schedule_with_repeat` 的事务边界。
- 不改变 `insert_many` 批量插入流程。
- 不改变返回语义。
- 不运行写入验证。
- 不调用 `add_schedule` 写库。
- 不调用 `update_schedule_with_repeat` 写库。
- 不新增 `每年 / yearly / daily / weekly / monthly` 行为。

若开工前已有管理文档 diff，需在 `Work_Log.md` 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取：
   - `manage_instruction/Work_Instruction.md`
   - `manage_instruction/Work_Log.md` 中 4-0 / 4-1 结论
2. 阅读当前：
   - `src/services/schedule_repeat_service.py`
   - `src/data/database.py` 中 `add_schedule`
   - `src/data/database.py` 中 `update_schedule_with_repeat`
3. 在 `ScheduleRepeatService` 中新增纯逻辑方法。方法名可自定，但建议边界如下：
   - `get_repeat_count(rule)`：返回旧规则未来生成数量。
     - `每天 -> 365`
     - `每周 -> 52`
     - `每月 -> 12`
     - 其他 -> 0
   - `is_non_repeat_rule(rule)`：识别 `none / 无 / 不重复 / ''`。
   - `build_repeat_insert_plan(base_data, rule, group_id, include_base=True)`：
     - 输入 base data、规则、group_id。
     - 输出待插入数据 list。
     - `include_base=True` 时用于 `add_schedule`，计划包含当前项。
     - `include_base=False` 时用于 `update_schedule_with_repeat` 的未来重建，只包含未来项。
     - 不修改传入的 `base_data` 原对象。
     - 不访问数据库。
     - 不导入 UI / db_manager / Repository。
4. 生成规则必须保持旧行为：
   - `add_schedule` 重复路径：
     - `每天` 计划 366 条，含当前项。
     - `每周` 计划 53 条，含当前项。
     - `每月` 计划 13 条，含当前项。
   - `update_schedule_with_repeat` 未来重建路径：
     - `每天` 计划 365 条未来项。
     - `每周` 计划 52 条未来项。
     - `每月` 计划 12 条未来项。
5. 生成计划必须保持旧字段处理：
   - 每条计划的 `group_id` 与传入 `group_id` 一致。
   - `start_time` 按规则偏移。
   - `end_time` 按规则偏移。
   - `reminder_time` 按规则偏移。
   - 其他字段从 base data copy。
6. 修改 `src/data/database.py`：
   - `add_schedule` 重复路径用 service 生成 `schedules_to_insert`。
   - `update_schedule_with_repeat` 未来重建路径用 service 生成 `schedules_to_insert`。
   - 保留原有事务块和 `insert_many` 分批写入位置。
   - 保留原有 `group_id` 创建/沿用逻辑。
   - 保留原有删除旧未来逻辑。
   - 保留原有 `True / False` 返回语义。
7. 不运行写库验证。
8. 更新 `Work_Log.md`。

## 4. 验收命令

读取合同与日志：

Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8

定位修改点：

rg -n "build_repeat|get_repeat_count|is_non_repeat|add_schedule|update_schedule_with_repeat|insert_many|db\.atomic|group_id|每天|每周|每月" src/services/schedule_repeat_service.py src/data/database.py

service import 验证：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.services.schedule_repeat_service import ScheduleRepeatService; print('repeat service import ok', ScheduleRepeatService)"

验证重复生成数量、group_id、输入不被原地修改：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import datetime as dt, copy; from src.services.schedule_repeat_service import ScheduleRepeatService as S; base={'title':'tmp','repeat_rule':'每天','start_time':dt.datetime(2026,1,1,9,0),'end_time':dt.datetime(2026,1,1,10,0),'reminder_time':dt.datetime(2026,1,1,8,30),'group_id':'gid-old'}; original=copy.deepcopy(base); expected={'每天':366,'每周':53,'每月':13}; future_expected={'每天':365,'每周':52,'每月':12}; rows=[]; future_rows=[];
for rule,count in expected.items():
    plan=S.build_repeat_insert_plan(base, rule, 'gid-test', include_base=True); rows.append((rule,len(plan),plan[0]['group_id'],plan[-1]['group_id'])); assert len(plan)==count; assert all(x.get('group_id')=='gid-test' for x in plan)
for rule,count in future_expected.items():
    plan=S.build_repeat_insert_plan(base, rule, 'gid-test', include_base=False); future_rows.append((rule,len(plan),plan[0]['group_id'] if plan else None)); assert len(plan)==count; assert all(x.get('group_id')=='gid-test' for x in plan)
print('rows', rows); print('future_rows', future_rows); print('base unchanged', base==original); assert base==original"

验证时间偏移与旧逻辑一致：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import datetime as dt; from src.services.schedule_repeat_service import ScheduleRepeatService as S; base={'title':'tmp','start_time':dt.datetime(2026,1,31,9,0),'end_time':dt.datetime(2026,1,31,10,0),'reminder_time':dt.datetime(2026,1,30,8,0)};
daily=S.build_repeat_insert_plan(base,'每天','gid',include_base=True); weekly=S.build_repeat_insert_plan(base,'每周','gid',include_base=True); monthly=S.build_repeat_insert_plan(base,'每月','gid',include_base=True);
print('daily first future', daily[1]['start_time'], daily[1]['end_time'], daily[1]['reminder_time']); print('weekly second future', weekly[2]['start_time'], weekly[2]['end_time'], weekly[2]['reminder_time']); print('monthly first future', monthly[1]['start_time'], monthly[1]['end_time'], monthly[1]['reminder_time']);
assert daily[1]['start_time']==dt.datetime(2026,2,1,9,0); assert weekly[2]['start_time']==dt.datetime(2026,2,14,9,0); assert monthly[1]['start_time']==dt.datetime(2026,2,28,9,0)"

验证非重复和未知规则不生成重复计划：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.services.schedule_repeat_service import ScheduleRepeatService as S; base={'title':'tmp'}; rules=['none','无','不重复','','每年','yearly','daily','weekly','monthly']; rows=[];
for rule in rules:
    plan=S.build_repeat_insert_plan(base, rule, 'gid', include_base=True); rows.append((rule,len(plan),S.is_non_repeat_rule(rule) if hasattr(S,'is_non_repeat_rule') else None))
print('non/unsupported rows', rows); assert all(len(plan:=S.build_repeat_insert_plan(base, r, 'gid', include_base=True)) in (0,1) for r in rules)"

静态依赖检查，确认 service 不依赖 UI / db_manager / Repository：

rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_repeat_service.py

预期：无输出，退出码 1 视为通过。

验证未新增不允许规则分支：

rg -n "每年|yearly|daily|weekly|monthly" src/services/schedule_repeat_service.py src/data/database.py

预期：不应出现新增实现分支；如只在日志、注释或验证文本中出现，需要说明不构成行为。

验证 `database.py` 写入边界仍保留：

rg -n "with db\.atomic|insert_many|batch_size|return True|return False|Schedule\.create|Schedule\.update|Schedule\.delete" src/data/database.py

人工复核该输出，确认：

- `add_schedule` 仍由 `DatabaseManager` 执行 `Schedule.create` 或 `insert_many`。
- `update_schedule_with_repeat` 仍由 `DatabaseManager` 执行 update/delete/insert_many。
- 事务块和批量插入仍在 `database.py`。
- 返回语义仍是 `True / False`。

语法检查：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src\services\schedule_repeat_service.py src\data\database.py

范围检查：

git diff --name-only -- src/ui
git diff --name-only -- src/data/models.py
git diff --name-only -- src/repositories
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch

预期：

- `src/ui` 无 diff。
- `src/data/models.py` 无 diff。
- `src/repositories` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- 最终只允许：
  - `src/services/schedule_repeat_service.py`
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. Work_Log.md 记录要求

至少记录：

- 本轮任务名称：第四轮 4-2（重复规则待插入数据计划服务）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 新增/修改的 service 方法清单
- `add_schedule` 委托生成计划的位置
- `update_schedule_with_repeat` 委托生成计划的位置
- 明确记录：未改事务边界
- 明确记录：未改批量插入流程
- 明确记录：未改返回语义
- 明确记录：未写数据库
- `每天 / 每周 / 每月` 计划数量验证结果
- `group_id` 一致性验证结果
- `start_time/end_time/reminder_time` 偏移验证结果
- 输入 base data 是否未被原地修改
- 未新增 `每年/yearly/daily/weekly/monthly` 行为说明
- service import 验证结果
- service 静态依赖检查结果
- `database.py` 写入边界复核结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
