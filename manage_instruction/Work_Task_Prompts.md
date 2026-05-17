请执行第三轮 3-3b：todo_board 主看板渲染排序抽取。本轮只处理 `src/ui/todo_board.py` 主渲染路径中的看板排序，不处理“一键按重要性排序”。

## 1. 本轮目标

基于 3-0 到 3-3a 结论，在 `ScheduleSortService` 中实现 `sort_for_todo_board(items)`，并对 `todo_board.py` 主看板渲染路径做最小调用替换。

本轮只处理当前主看板渲染排序：

- 旧逻辑位置：`src/ui/todo_board.py` 中生成 `todos` 后的本地 `sort_key`。
- 旧排序语义：
  - 置顶优先：`rank_pin = 0 if is_pinned else 1`
  - `sort_order` 越大越靠前：`sort_val = -sort_order`
  - sort key 为 `(rank_pin, sort_val)`

本轮不处理：

- `_sort_by_priority`
- priority 排序
- priority 排序后的 `sort_order` 写回
- 拖拽排序写库逻辑
- dashboard/week/todo 三处排序
- 查询/过滤/分类策略

## 2. 允许/禁止

本轮允许修改：

- `src/services/schedule_sort_service.py`
- `src/ui/todo_board.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- `src/ui/dashboard.py`
- `src/ui/week_window.py`
- `src/ui/todo.py`
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

- 不修改 `_sort_by_priority`。
- 不修改 priority 排序规则。
- 不修改任何 `sort_order` 写回逻辑。
- 不修改拖拽排序写库逻辑。
- 不修改 dashboard/week/todo。
- 不修改 `ScheduleQueryService`。
- 不修改 Repository 或 Data 层。
- 不处理分类策略。
- 不创建 matrix 服务。
- 不改 UI 布局、视觉样式、交互流程。
- 不改变 `db_manager` 对外 API。
- 不保留 `schedule.db` 变更。

若开工前已有管理文档 diff，需在 `Work_Log.md` 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取 `manage_instruction/Work_Instruction.md` 第三轮合同。
2. 读取 `manage_instruction/Work_Log.md` 中 3-0 到 3-3a 结论。
3. 读取 `src/ui/todo_board.py` 当前主看板渲染排序位置。
4. 在 `src/services/schedule_sort_service.py` 中实现：
   - `ScheduleSortService.sort_for_todo_board(items)`
   - 返回排序后的新 list。
   - 不原地修改传入 list。
   - 使用 `sorted(list(items), key=...)`。
   - 使用 `getattr` 读取 `is_pinned`、`sort_order`，保持旧默认值。
5. 在 `src/ui/todo_board.py` 中：
   - 引入 `ScheduleSortService`。
   - 只把主渲染路径中的本地 `sort_key` 和 `todos.sort(key=sort_key)` 替换为 `todos = ScheduleSortService.sort_for_todo_board(todos)`。
   - 不修改 `all_active_todos` 生成逻辑。
   - 不修改文件夹过滤逻辑。
   - 不修改 `self.current_todos = todos` 之后的逻辑。
6. 不修改 `_sort_by_priority` 方法。
7. 不修改任何数据库写入逻辑。
8. 更新 `Work_Log.md`。

## 4. 验收命令

开工前基线命令，修改代码前先执行并记录输出：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; from src.services.schedule_query_service import ScheduleQueryService; all_items=db_manager.get_all_schedules(); all_active=[s for s in all_items if getattr(s,'status',0)!=2 and ScheduleQueryService.is_todo(s) and getattr(s,'status',0)==0]; old_sorted=sorted(list(all_active), key=lambda item: (0 if getattr(item,'is_pinned',False) else 1, -getattr(item,'sort_order',0.0))); print('baseline todo_board', [s.id for s in old_sorted])"

修改后使用 `ScheduleSortService.sort_for_todo_board` 复跑，并确认 id 顺序与基线一致：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; from src.services.schedule_query_service import ScheduleQueryService; from src.services.schedule_sort_service import ScheduleSortService; all_items=db_manager.get_all_schedules(); all_active=[s for s in all_items if getattr(s,'status',0)!=2 and ScheduleQueryService.is_todo(s) and getattr(s,'status',0)==0]; sorted_items=ScheduleSortService.sort_for_todo_board(all_active); print('after todo_board', [s.id for s in sorted_items])"

验证 `sort_for_todo_board` 返回新 list，且不原地修改输入：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; from src.services.schedule_sort_service import ScheduleSortService; items=list(db_manager.get_all_schedules()[:8]); original=[s.id for s in items]; result=ScheduleSortService.sort_for_todo_board(items); print('returns list', isinstance(result, list)); print('new object', result is not items); print('input unchanged', [s.id for s in items] == original); print('result ids', [s.id for s in result]); assert isinstance(result, list); assert result is not items; assert [s.id for s in items] == original"

验证 service 可 import 且 day/week/todo 旧方法仍可用：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; from src.services.schedule_sort_service import ScheduleSortService; items=db_manager.get_all_schedules()[:5]; print('day', isinstance(ScheduleSortService.sort_for_day_view(items), list)); print('week', isinstance(ScheduleSortService.sort_for_week_view(items), list)); print('todo', isinstance(ScheduleSortService.sort_for_todo_list(items), list)); print('board', isinstance(ScheduleSortService.sort_for_todo_board(items), list))"

验证旧 `db_manager.get_schedules_for_date` 仍可用：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; schedules=db_manager.get_schedules_for_date(date.today()); print('db_manager path ok', isinstance(schedules, list), len(schedules))"

静态依赖检查，确认 `schedule_sort_service.py` 不依赖 UI / db_manager / Repository / QWidget：

rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_sort_service.py

检查 `todo_board.py` 引用范围：

rg -n "ScheduleSortService|schedule_sort_service|CategoryPolicyService|src\.repositories" src/ui/todo_board.py

预期：

- `todo_board.py` 允许命中 `ScheduleSortService` / `schedule_sort_service`。
- 不应命中 `CategoryPolicyService`。
- 不应命中 `src.repositories`。

确认 `_sort_by_priority` 未被修改或替换：

rg -n "def _sort_by_priority|priority|sort_order|update_schedule_fields" src/ui/todo_board.py

注意：该命令会命中既有逻辑。日志中需说明 `_sort_by_priority` 未参与本轮改动，priority 排序和写回逻辑保持原样。

检查本轮未误动其他 UI / service：

git diff --name-only -- src/ui/dashboard.py
git diff --name-only -- src/ui/week_window.py
git diff --name-only -- src/ui/todo.py
git diff --name-only -- src/services/schedule_query_service.py
git diff --name-only -- src/services/category_policy_service.py
git diff --name-only -- src/services/weather_service.py

语法检查：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src\services\schedule_sort_service.py src\ui\todo_board.py

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
- `dashboard.py` 无 diff。
- `week_window.py` 无 diff。
- `todo.py` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- `schedule_query_service.py` 无 diff。
- `category_policy_service.py` 无 diff。
- `weather_service.py` 无 diff。
- 最终只允许：
  - `src/services/schedule_sort_service.py`
  - `src/ui/todo_board.py`
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第三轮 3-3b（todo_board 主看板渲染排序抽取）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 开工前 todo_board 主排序 id 基线输出摘要
- 实现的 `ScheduleSortService.sort_for_todo_board` 方法
- `todo_board.py` 替换了哪一处排序
- 明确记录：未修改 `_sort_by_priority`
- 明确记录：未修改 priority 排序和 `sort_order` 写回逻辑
- 明确记录：未修改 dashboard/week/todo
- 明确记录：未修改 `ScheduleQueryService`
- 修改后 todo_board 主排序 id 是否与基线一致
- `sort_for_todo_board` 是否返回新 list 且不原地修改输入
- service import / direct call 验证结果
- 旧 `db_manager.get_schedules_for_date` 验证结果
- 静态依赖检查结果
- `todo_board.py` 引用检查结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
