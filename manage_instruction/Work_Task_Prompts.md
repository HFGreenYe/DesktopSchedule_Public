请执行第三轮 3-2b：ScheduleQueryService 日程/待办区分纯逻辑抽取。本轮只抽取 UI 中重复的日程/待办判断逻辑，不处理排序，不修改日期过滤，不写数据库。

## 1. 本轮目标

基于 3-0/3-1/3-2a 结论，在 `ScheduleQueryService` 中实现日程/待办区分相关的纯判断，并对 3-0 定位到的 UI 重复判断做最小调用替换。

本轮目标：

- 实现 `ScheduleQueryService.is_todo(item)`。
- 实现 `ScheduleQueryService.is_schedule(item)`，语义必须对齐当前周视图使用的 `item_type == 'schedule'` 判断。
- 实现或补全 `ScheduleQueryService.split_schedule_and_todo(items)`。
- 最小替换以下文件中 3-0 定位到的重复判断：
  - `src/ui/dashboard.py`
  - `src/ui/week_window.py`
  - `src/ui/todo.py`
  - `src/ui/todo_board.py`
- 替换前后各视图候选集合 id 必须一致。
- 不处理排序，排序逻辑留给 3-3。
- 不修改 Repository 日期过滤，3-2a 已完成。
- 不写 `schedule.db`。

## 2. 允许/禁止

本轮允许修改：

- `src/services/schedule_query_service.py`
- `src/ui/dashboard.py`
- `src/ui/week_window.py`
- `src/ui/todo.py`
- `src/ui/todo_board.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- `src/repositories/`
- `src/data/`
- `src/services/schedule_sort_service.py`
- `src/services/category_policy_service.py`
- `src/services/weather_service.py`
- `src/services/matrix_classification_service.py`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不修改 Repository 日期过滤。
- 不迁移排序逻辑。
- 不修改分类策略。
- 不创建 matrix 服务。
- 不改 UI 布局。
- 不改 UI 视觉样式。
- 不改交互流程。
- 不改数据库字段、迁移逻辑或写入逻辑。
- 不改变 `db_manager` 对外 API。
- 不保留 `schedule.db` 变更。

若开工前已有管理文档 diff，需在 `Work_Log.md` 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取 `manage_instruction/Work_Instruction.md` 第三轮合同。
2. 读取 `manage_instruction/Work_Log.md` 中 3-0、3-1、3-2a 结论。
3. 开工前记录旧逻辑基线，至少覆盖四类候选集合：
   - dashboard 日视图候选日程集合。
   - week_window 单日候选日程集合。
   - todo 待办列表候选集合。
   - todo_board 活跃待办候选集合。
4. 在 `src/services/schedule_query_service.py` 中实现：
   - `is_todo(item)`：
     - `item_type == 'todo'` 返回 True。
     - 或旧字段 `type == 1` 返回 True。
     - 使用 `getattr`，避免对象缺字段时报错。
   - `is_schedule(item)`：
     - 必须匹配当前周视图语义：`item_type == 'schedule'`。
     - 不要简单写成 `not is_todo(item)`，避免改变旧周视图行为。
   - `split_schedule_and_todo(items)`：
     - 返回 `(schedules, todos)`。
     - `todos` 使用 `is_todo(item)`。
     - `schedules` 使用 `not is_todo(item)`，用于通用拆分，不替代周视图的 `is_schedule` 判断。
5. 在 `src/ui/dashboard.py` 中最小替换原有 `is_todo` 内联判断：
   - 保留 `status == 2` 过滤。
   - 保留后续排序逻辑不变。
6. 在 `src/ui/week_window.py` 中最小替换 `s.item_type == 'schedule'`：
   - 使用 `ScheduleQueryService.is_schedule(s)`。
   - 保留 `status != 2` 过滤。
   - 保留后续排序逻辑不变。
7. 在 `src/ui/todo.py` 中最小替换原有 `is_todo` 内联判断：
   - 保留 `status == 2` 过滤。
   - 保留后续排序逻辑不变。
8. 在 `src/ui/todo_board.py` 中最小替换原有 `is_todo` 内联判断：
   - 保留 `status == 2` 过滤。
   - 保留 `status == 0` 活跃判断。
   - 保留文件夹过滤、统计和排序逻辑不变。
9. 不替换其他无关 `item_type` 使用点，例如创建数据、传参、详情加载等。
10. 更新 `Work_Log.md`。

## 4. 验收命令

开工前基线命令，修改代码前先执行并记录输出：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; today=db_manager.get_schedules_for_date(date.today()); all_items=db_manager.get_all_schedules(); old_is_todo=lambda s: ((hasattr(s,'item_type') and s.item_type=='todo') or (hasattr(s,'type') and getattr(s,'type',0)==1)); dashboard=[s.id for s in today if getattr(s,'status',0)!=2 and not old_is_todo(s)]; week=[s.id for s in today if getattr(s,'item_type',None)=='schedule' and getattr(s,'status',0)!=2]; todo=[s.id for s in all_items if getattr(s,'status',0)!=2 and old_is_todo(s)]; board=[s.id for s in all_items if getattr(s,'status',0)!=2 and old_is_todo(s) and getattr(s,'status',0)==0]; print('baseline dashboard', dashboard); print('baseline week', week); print('baseline todo', todo); print('baseline board', board)"

修改后使用 service 逻辑复跑，并确认四组 id 与基线一致：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; from src.services.schedule_query_service import ScheduleQueryService; today=db_manager.get_schedules_for_date(date.today()); all_items=db_manager.get_all_schedules(); dashboard=[s.id for s in today if getattr(s,'status',0)!=2 and not ScheduleQueryService.is_todo(s)]; week=[s.id for s in today if ScheduleQueryService.is_schedule(s) and getattr(s,'status',0)!=2]; todo=[s.id for s in all_items if getattr(s,'status',0)!=2 and ScheduleQueryService.is_todo(s)]; board=[s.id for s in all_items if getattr(s,'status',0)!=2 and ScheduleQueryService.is_todo(s) and getattr(s,'status',0)==0]; print('after dashboard', dashboard); print('after week', week); print('after todo', todo); print('after board', board)"

验证 service 方法可直接调用：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; from src.services.schedule_query_service import ScheduleQueryService; items=db_manager.get_all_schedules(); schedules,todos=ScheduleQueryService.split_schedule_and_todo(items); print('split ok', isinstance(schedules,list), isinstance(todos,list), len(schedules), len(todos)); print('sample flags', [(s.id, ScheduleQueryService.is_todo(s), ScheduleQueryService.is_schedule(s)) for s in items[:5]])"

验证旧 `db_manager.get_schedules_for_date` 仍可用：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; schedules=db_manager.get_schedules_for_date(date.today()); print('db_manager path ok', isinstance(schedules, list), len(schedules))"

静态依赖检查，确认 `schedule_query_service.py` 不依赖 UI / db_manager / Repository / QWidget：

rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_query_service.py

检查 UI 只引入 query service，不引入其他 service 或 repository：

rg -n "ScheduleQueryService|schedule_query_service|ScheduleSortService|CategoryPolicyService|src\.repositories|db_manager" src/ui/dashboard.py src/ui/week_window.py src/ui/todo.py src/ui/todo_board.py

注意：上述命令中既有 `db_manager` 命中是允许的，因为这些 UI 原本就通过 `db_manager` 取数；日志需说明是否只是既有取数路径。

检查本轮未误动其他 service：

git diff --name-only -- src/services/schedule_sort_service.py
git diff --name-only -- src/services/category_policy_service.py
git diff --name-only -- src/services/weather_service.py

范围检查：

git diff --name-only -- src/repositories
git diff --name-only -- src/data
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch

预期：

- `src/repositories` 无 diff。
- `src/data` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- `schedule_sort_service.py` 无 diff。
- `category_policy_service.py` 无 diff。
- `weather_service.py` 无 diff。
- 最终只允许：
  - `src/services/schedule_query_service.py`
  - `src/ui/dashboard.py`
  - `src/ui/week_window.py`
  - `src/ui/todo.py`
  - `src/ui/todo_board.py`
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第三轮 3-2b（日程/待办区分纯逻辑抽取）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 开工前四组候选集合基线输出摘要
- 实现的 service 方法
- 每个 UI 文件替换了哪一处判断
- 明确记录：未修改排序逻辑
- 明确记录：未修改 Repository 日期过滤
- 修改后四组候选集合 id 是否与基线一致
- `split_schedule_and_todo` 验证结果
- 旧 `db_manager.get_schedules_for_date` 验证结果
- 静态依赖检查结果
- UI 引用检查结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
