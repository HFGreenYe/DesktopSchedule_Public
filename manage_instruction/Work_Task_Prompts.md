请执行第三轮 3-2a：ScheduleQueryService 日期过滤纯逻辑抽取。本轮只处理 Repository 侧 `get_schedules_for_date(target_date)` 中与日期过滤直接相关的纯逻辑，不处理 UI，不处理排序服务，不处理分类策略。

## 1. 本轮目标

将 `src/repositories/schedule_repository.py` 中 `get_schedules_for_date(target_date)` 的日期过滤规则抽到 `src/services/schedule_query_service.py`。

目标边界：

- 实现 `ScheduleQueryService.filter_for_date(items, target_date)`。
- 让 `ScheduleRepository.get_schedules_for_date(target_date)` 使用该 service 完成过滤。
- 保留 `ScheduleRepository.get_schedules_for_date` 原有对外方法名、参数、返回类型和排序结果语义。
- 保留 Repository 内现有排序逻辑，本轮不迁移排序。
- 不修改 UI。
- 不写 `schedule.db`。

本轮不实现 `split_schedule_and_todo`，不处理 UI 侧日程/待办区分，这部分留给后续 3-2b。

## 2. 允许/禁止

本轮允许修改：

- `src/services/schedule_query_service.py`
- `src/repositories/schedule_repository.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- `src/services/schedule_sort_service.py`
- `src/services/category_policy_service.py`
- `src/services/weather_service.py`
- `src/services/matrix_classification_service.py`
- `src/data/`
- `src/ui/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不修改 UI。
- 不接四象限 UI。
- 不创建 matrix 服务。
- 不迁移排序逻辑到 `schedule_sort_service.py`。
- 不处理分类策略。
- 不修改数据库字段、迁移逻辑或写入逻辑。
- 不改变 `db_manager.get_schedules_for_date(target_date)` 对外语义。
- 不改变 Repository 公开方法名、参数、返回语义。
- 不改变现有排序顺序。
- 不保留 `schedule.db` 变更。

若开工前已有管理文档 diff，需在 `Work_Log.md` 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 先读取 `manage_instruction/Work_Instruction.md` 第三轮合同。
2. 读取 `manage_instruction/Work_Log.md` 中 3-0 和 3-1 结论。
3. 读取 `src/repositories/schedule_repository.py` 当前 `get_schedules_for_date(target_date)` 实现。
4. 开工前先记录旧路径基线输出，至少覆盖：
   - 今天
   - 昨天
   - 明天
5. 在 `ScheduleQueryService.filter_for_date(items, target_date)` 中实现旧 Repository 中的日期过滤规则：
   - 输入为 schedule/todo 对象 iterable。
   - 输出为 list。
   - 保持原过滤语义：
     - `item_type == "todo"` 且没有 `end_time` 时保留。
     - 有 `start_time` 和 `end_time` 时，`start_date <= target_date <= end_date` 保留。
     - 只有 `end_time` 时，`end_date == target_date` 保留。
     - 没有 `end_time` 且不满足前面特殊分支时保留。
   - 不在 service 中访问数据库。
   - 不在 service 中导入 Repository、db_manager、UI、QWidget。
6. 修改 `ScheduleRepository.get_schedules_for_date(target_date)`：
   - 仍由 Repository 查询 `self._schedule_model.select()`。
   - 调用 `ScheduleQueryService.filter_for_date(all_data, target_date)` 得到 filtered。
   - 保留原方法里的排序逻辑和排序顺序。
7. 不实现 `split_schedule_and_todo`；该方法可继续保持 3-1 的未实现状态。
8. 不修改任何 UI 文件。
9. 更新 `Work_Log.md`。

## 4. 验收命令

开工前基线命令，修改代码前先执行并记录输出：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date, timedelta; from src.data.database import db_manager; days=[date.today()+timedelta(days=i) for i in (-1,0,1)]; print('baseline'); [print(d.isoformat(), [s.id for s in db_manager.get_schedules_for_date(d)]) for d in days]"

修改后运行同一命令，确认同一日期下 id 顺序与基线一致：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date, timedelta; from src.data.database import db_manager; days=[date.today()+timedelta(days=i) for i in (-1,0,1)]; print('after'); [print(d.isoformat(), [s.id for s in db_manager.get_schedules_for_date(d)]) for d in days]"

验证 service 可 import 且可直接调用：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.services.schedule_query_service import ScheduleQueryService; from src.data.database import db_manager; items=db_manager.get_all_schedules(); result=ScheduleQueryService.filter_for_date(items, date.today()); print('service filter ok', isinstance(result, list), len(result))"

验证旧 `db_manager` 路径仍可用：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; schedules=db_manager.get_schedules_for_date(date.today()); print('db_manager path ok', isinstance(schedules, list), len(schedules))"

静态依赖检查，确认 `schedule_query_service.py` 不依赖 UI / db_manager / Repository / QWidget：

rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_query_service.py

检查本轮未误动其他 service：

git diff --name-only -- src/services/schedule_sort_service.py
git diff --name-only -- src/services/category_policy_service.py
git diff --name-only -- src/services/weather_service.py

范围检查：

git diff --name-only -- src/data
git diff --name-only -- src/ui
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch

预期：

- `src/data` 无 diff。
- `src/ui` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- `schedule_sort_service.py` 无 diff。
- `category_policy_service.py` 无 diff。
- `weather_service.py` 无 diff。
- 最终只允许：
  - `src/services/schedule_query_service.py`
  - `src/repositories/schedule_repository.py`
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第三轮 3-2a（ScheduleQueryService 日期过滤纯逻辑抽取）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 开工前基线命令和输出摘要
- 实现的 service 方法
- Repository 委托方式
- 明确记录：排序逻辑未迁移，仍保留在 Repository
- 明确记录：`split_schedule_and_todo` 未实现，留给后续 3-2b
- 修改后同一日期 id 顺序是否与基线一致
- service import / direct call 验证结果
- 旧 `db_manager.get_schedules_for_date` 验证结果
- 静态依赖检查结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
