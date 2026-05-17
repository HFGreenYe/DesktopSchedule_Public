请执行第三轮 3-3a：day/week/todo 三处同构排序 key 抽取。本轮只抽取 `dashboard.py`、`week_window.py`、`todo.py` 中同构的 UI 排序逻辑，不处理 `todo_board.py`。

## 1. 本轮目标

基于 3-0 到 3-2b 结论，在 `ScheduleSortService` 中实现 day/week/todo 三处同构排序逻辑，并对三个 UI 文件做最小调用替换。

本轮目标：

- 实现 `ScheduleSortService.sort_for_day_view(items)`。
- 实现 `ScheduleSortService.sort_for_week_view(items)`。
- 实现 `ScheduleSortService.sort_for_todo_list(items)`。
- 三个方法必须保持当前 UI 中同构排序语义：
  - 置顶优先：`rank_pin = 0 if is_pinned else 1`
  - 已完成靠后：`rank_status = 3 if status == 1 else 1`
  - `sort_order` 越大越靠前：`sort_val = -sort_order`
  - sort key 为 `(rank_pin, rank_status, sort_val)`
- 最小替换以下文件中的内联排序：
  - `src/ui/dashboard.py`
  - `src/ui/week_window.py`
  - `src/ui/todo.py`
- 替换前后三个视图候选集合的 id 顺序必须一致。
- 不处理 `src/ui/todo_board.py`，它的排序规则和写回逻辑单独留给 3-3b。
- 不修改数据库，不写 `schedule.db`。

## 2. 允许/禁止

本轮允许修改：

- `src/services/schedule_sort_service.py`
- `src/ui/dashboard.py`
- `src/ui/week_window.py`
- `src/ui/todo.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- `src/ui/todo_board.py`
- `src/services/schedule_query_service.py`
- `src/services/category_policy_service.py`
- `src/services/weather_service.py`
- `src/services/matrix_classification_service.py`
- `src/repositories/`
- `src/data/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不处理 `todo_board.py`。
- 不迁移 `todo_board._sort_by_priority`。
- 不修改 Repository 日期过滤。
- 不修改 `ScheduleQueryService` 判定逻辑。
- 不处理分类策略。
- 不创建 matrix 服务。
- 不改 UI 布局。
- 不改 UI 视觉样式。
- 不改交互流程。
- 不改拖拽排序写库逻辑。
- 不改变 `db_manager` 对外 API。
- 不保留 `schedule.db` 变更。

若开工前已有管理文档 diff，需在 `Work_Log.md` 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取 `manage_instruction/Work_Instruction.md` 第三轮合同。
2. 读取 `manage_instruction/Work_Log.md` 中 3-0、3-1、3-2a、3-2b 结论。
3. 读取当前三处排序逻辑：
   - `src/ui/dashboard.py`
   - `src/ui/week_window.py`
   - `src/ui/todo.py`
4. 修改 `src/services/schedule_sort_service.py`：
   - 实现一个内部纯排序 key，或分别在三个方法中实现等价逻辑。
   - `sort_for_day_view(items)` 返回排序后的新 list。
   - `sort_for_week_view(items)` 返回排序后的新 list。
   - `sort_for_todo_list(items)` 返回排序后的新 list。
   - 不原地修改传入 iterable，除非输入本来就是 list 且调用方明确不依赖原对象顺序；建议统一 `return sorted(list(items), key=...)`。
   - 使用 `getattr` 读取 `is_pinned`、`status`、`sort_order`，保持 UI 旧逻辑默认值。
5. 修改 `src/ui/dashboard.py`：
   - 引入 `ScheduleSortService`。
   - 将 `dashboard_schedules.sort(key=sort_key)` 及本地 `sort_key` 替换为 `dashboard_schedules = ScheduleSortService.sort_for_day_view(dashboard_schedules)`。
   - 不改过滤逻辑、不改卡片渲染逻辑。
6. 修改 `src/ui/week_window.py`：
   - 引入 `ScheduleSortService`。
   - 将 `valid_schedules.sort(key=sort_key)` 及本地 `sort_key` 替换为 `valid_schedules = ScheduleSortService.sort_for_week_view(valid_schedules)`。
   - 不改日期循环、不改过滤逻辑、不改卡片渲染逻辑。
7. 修改 `src/ui/todo.py`：
   - 引入 `ScheduleSortService`。
   - 将 `dashboard_todos.sort(key=sort_key)` 及本地 `sort_key` 替换为 `dashboard_todos = ScheduleSortService.sort_for_todo_list(dashboard_todos)`。
   - 不改过滤逻辑、不改卡片渲染逻辑。
8. 不修改 `todo_board.py`。
9. 更新 `Work_Log.md`。

## 4. 验收命令

开工前基线命令，修改代码前先执行并记录输出：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; from src.services.schedule_query_service import ScheduleQueryService; today=db_manager.get_schedules_for_date(date.today()); all_items=db_manager.get_all_schedules(); old_sort=lambda items: sorted(list(items), key=lambda item: (0 if getattr(item,'is_pinned',False) else 1, 3 if getattr(item,'status',0)==1 else 1, -getattr(item,'sort_order',0.0))); dashboard=[s for s in today if getattr(s,'status',0)!=2 and not ScheduleQueryService.is_todo(s)]; week=[s for s in today if ScheduleQueryService.is_schedule(s) and getattr(s,'status',0)!=2]; todo=[s for s in all_items if getattr(s,'status',0)!=2 and ScheduleQueryService.is_todo(s)]; print('baseline dashboard', [s.id for s in old_sort(dashboard)]); print('baseline week', [s.id for s in old_sort(week)]); print('baseline todo', [s.id for s in old_sort(todo)])"

修改后使用 `ScheduleSortService` 复跑，并确认三组 id 顺序与基线一致：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; from src.services.schedule_query_service import ScheduleQueryService; from src.services.schedule_sort_service import ScheduleSortService; today=db_manager.get_schedules_for_date(date.today()); all_items=db_manager.get_all_schedules(); dashboard=[s for s in today if getattr(s,'status',0)!=2 and not ScheduleQueryService.is_todo(s)]; week=[s for s in today if ScheduleQueryService.is_schedule(s) and getattr(s,'status',0)!=2]; todo=[s for s in all_items if getattr(s,'status',0)!=2 and ScheduleQueryService.is_todo(s)]; print('after dashboard', [s.id for s in ScheduleSortService.sort_for_day_view(dashboard)]); print('after week', [s.id for s in ScheduleSortService.sort_for_week_view(week)]); print('after todo', [s.id for s in ScheduleSortService.sort_for_todo_list(todo)])"

验证 service 可 import 且直接调用：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; from src.services.schedule_sort_service import ScheduleSortService; items=db_manager.get_all_schedules()[:5]; print('sort day ok', isinstance(ScheduleSortService.sort_for_day_view(items), list)); print('sort week ok', isinstance(ScheduleSortService.sort_for_week_view(items), list)); print('sort todo ok', isinstance(ScheduleSortService.sort_for_todo_list(items), list))"

验证旧 `db_manager.get_schedules_for_date` 仍可用：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; schedules=db_manager.get_schedules_for_date(date.today()); print('db_manager path ok', isinstance(schedules, list), len(schedules))"

静态依赖检查，确认 `schedule_sort_service.py` 不依赖 UI / db_manager / Repository / QWidget：

rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_sort_service.py

检查 UI 引用范围：

rg -n "ScheduleSortService|schedule_sort_service|ScheduleQueryService|CategoryPolicyService|src\.repositories" src/ui/dashboard.py src/ui/week_window.py src/ui/todo.py src/ui/todo_board.py

注意：

- `dashboard.py`、`week_window.py`、`todo.py` 允许命中 `ScheduleSortService` 和既有 `ScheduleQueryService`。
- `todo_board.py` 不应新增 `ScheduleSortService`。
- 不应命中 `CategoryPolicyService` 或 `src.repositories`。

确认 `todo_board.py` 未改：

git diff --name-only -- src/ui/todo_board.py

检查本轮未误动其他 service：

git diff --name-only -- src/services/schedule_query_service.py
git diff --name-only -- src/services/category_policy_service.py
git diff --name-only -- src/services/weather_service.py

语法检查：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src\services\schedule_sort_service.py src\ui\dashboard.py src\ui\week_window.py src\ui\todo.py

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
- `src/ui/todo_board.py` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- `schedule_query_service.py` 无 diff。
- `category_policy_service.py` 无 diff。
- `weather_service.py` 无 diff。
- 最终只允许：
  - `src/services/schedule_sort_service.py`
  - `src/ui/dashboard.py`
  - `src/ui/week_window.py`
  - `src/ui/todo.py`
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第三轮 3-3a（day/week/todo 三处同构排序 key 抽取）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 开工前三组排序 id 基线输出摘要
- 实现的 `ScheduleSortService` 方法
- 每个 UI 文件替换了哪一处排序
- 明确记录：未修改 `todo_board.py`
- 明确记录：未修改 `ScheduleQueryService`
- 明确记录：未修改 Repository 日期过滤
- 修改后三组排序 id 是否与基线一致
- service import / direct call 验证结果
- 旧 `db_manager.get_schedules_for_date` 验证结果
- 静态依赖检查结果
- UI 引用检查结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
