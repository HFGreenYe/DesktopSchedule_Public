请执行第四轮 4-3：add_schedule 非重复路径委托。本轮只处理 `DatabaseManager.add_schedule(data)` 的非重复新增路径，不处理重复路径。

## 1. 本轮目标

基于第四轮合同和 4-0 ~ 4-2 结论，将 `add_schedule` 的非重复路径做最小 service 委托。

本轮只处理：

- `repeat_rule` 为 `none / 无 / 不重复 / ''` 的单次日程新增。
- `DatabaseManager.add_schedule(data)` 对外 API 不变。
- 成功返回 `True`，失败返回 `False` 的语义不变。
- 重复路径 `每天 / 每周 / 每月` 不改。
- `update_schedule_with_repeat` 不改。

推荐实现方向：

- 新增或完善 `src/services/schedule_service.py`。
- 在其中提供最小写入协调方法，例如 `create_single_schedule(schedule_model, data)`。
- service 可以通过注入的 `schedule_model` 执行创建，但不得导入 `db_manager`、UI 或 Repository。
- `DatabaseManager.add_schedule` 的非重复分支调用该 service。
- 异常处理和返回语义必须保持旧行为。

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
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不修改重复路径生成逻辑。
- 不修改 `update_schedule_with_repeat`。
- 不新增 `parent_id`。
- 不新增 `每年 / yearly / daily / weekly / monthly` 行为。
- 不修改数据库字段、迁移逻辑、表名、默认值。
- 不修改 UI 行为。
- 不改变 `db_manager.add_schedule(data)` 方法名、参数、返回语义。
- 不让 UI 直接调用 service。
- 不让 service 依赖 UI / `db_manager` / Repository。
- 不使用 `build_repeat_insert_plan` 接管非重复主路径。
- 不保留 `schedule.db` 变更；允许为了验收临时写入一个单次日程，但必须删除清理，并确认 `schedule.db` 无 tracked diff。

如临时写入、查询、删除或清理断言失败，立即停止并在 `Work_Log.md` 记录异常，不继续后续验证。

若开工前已有管理文档 diff，需在 `Work_Log.md` 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取：
   - `manage_instruction/Work_Instruction.md`
   - `manage_instruction/Work_Log.md` 中 4-0 ~ 4-2 结论
2. 阅读当前代码：
   - `src/data/database.py` 中 `add_schedule`
   - `src/services/schedule_repeat_service.py`
   - `src/services/` 当前文件结构
3. 新增或完善 `src/services/schedule_service.py`：
   - 只实现单次日程创建所需的最小方法。
   - 不实现重复规则。
   - 不处理 `update_schedule_with_repeat`。
   - 不导入 UI、`db_manager`、Repository。
   - 不修改传入 `data` 原对象，除非旧逻辑本来如此；推荐复制后写入。
4. 修改 `DatabaseManager.add_schedule(data)`：
   - 非重复路径调用 `ScheduleService`。
   - 保持旧判断范围：`none / 无 / 不重复 / ''`。
   - 保持成功 `True`、异常 `False`。
   - 保持原失败日志语义。
   - 重复路径继续使用当前 4-2 后的 `ScheduleRepeatService.build_repeat_insert_plan(...)`，不得改动其生成逻辑。
5. 不修改 `update_schedule_with_repeat`。
6. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

service import 验证：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.services.schedule_service import ScheduleService; print('schedule service import ok', ScheduleService)"

db import 验证：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('db import ok'); print('all schedules', len(db_manager.get_all_schedules()))"

非重复临时日程创建/删除验证：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='_tmp_4_3_single'+str(time.time_ns()); data={'title':name,'item_type':'schedule','priority':0,'repeat_rule':'none','description':'temporary 4-3 validation','category_id':None}; created=db_manager.add_schedule(data); print('created result', created); assert created is True; matches=[s for s in db_manager.get_all_schedules() if s.title==name]; print('matches', len(matches)); assert len(matches)==1; sid=matches[0].id; deleted=db_manager.delete_schedule(sid); print('deleted result', deleted); assert deleted is True; remaining=[s for s in db_manager.get_all_schedules() if s.id==sid]; print('remaining', len(remaining)); assert len(remaining)==0"

静态确认重复路径仍保留：

rg -n "build_repeat_insert_plan|每天|每周|每月|insert_many|db\.atomic|update_schedule_with_repeat" src/data/database.py

人工复核该输出，确认：

- `add_schedule` 重复路径仍调用 `ScheduleRepeatService.build_repeat_insert_plan(...)`。
- `每天 / 每周 / 每月` 规则没有新增或删除。
- `insert_many` 和 `db.atomic` 仍在重复路径。
- `update_schedule_with_repeat` 未被本轮修改。

service 静态依赖检查：

rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_service.py

预期：无输出，退出码 1 视为通过。

确认未新增不允许规则：

rg -n "每年|yearly|daily|weekly|monthly|parent_id" src/services/schedule_service.py src/data/database.py

预期：不应出现新增实现分支；如只在既有文本、注释或无关上下文中出现，需在日志说明。

语法检查：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src\services\schedule_service.py src\data\database.py

范围检查：

git diff --name-only -- src/services/schedule_repeat_service.py
git diff --name-only -- src/ui
git diff --name-only -- src/data/models.py
git diff --name-only -- src/repositories
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch

预期：

- `src/services/schedule_repeat_service.py` 无 diff。
- `src/ui` 无 diff。
- `src/data/models.py` 无 diff。
- `src/repositories` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- 最终只允许：
  - `src/services/schedule_service.py`
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第四轮 4-3（add_schedule 非重复路径委托）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 新增/修改的 service 方法
- `add_schedule` 非重复路径委托方式
- 明确记录：重复路径未改
- 明确记录：`update_schedule_with_repeat` 未改
- 明确记录：未新增 `parent_id`
- 明确记录：未新增 `每年/yearly/daily/weekly/monthly` 行为
- 非重复临时日程创建结果
- 临时日程删除清理结果
- `schedule.db` 是否无 tracked diff
- service import 验证结果
- db import 验证结果
- service 静态依赖检查结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
