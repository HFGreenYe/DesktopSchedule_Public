请执行第三轮 3-6：第三轮整体验收与归档准备。本轮只做整体验收和日志记录，不修改源码，不写数据库。

## 1. 本轮目标

汇总并验证第三轮 3-0 到 3-5 的全部结果，确认第三轮“纯业务查询与排序服务”可以归档。

本轮验收范围：

- `ScheduleQueryService`
- `ScheduleSortService`
- `CategoryPolicyService`
- 旧 `db_manager` 调用路径
- 已替换的 UI import 路径
- 查询、过滤、排序、分类状态、删除动作映射关键结果
- 四象限评估结论
- diff 范围

本轮不实现新功能，不修改源码，不写 `schedule.db`。

## 2. 允许/禁止

本轮允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不修改任何 Python 源码。
- 不修改 UI。
- 不修改 Data / Repository / Service 代码。
- 不创建 `matrix_classification_service.py`。
- 不接四象限 UI。
- 不写数据库。
- 不提交 Git。
- 不改变任何业务行为。

若开工前已有管理文档 diff，需在 `Work_Log.md` 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取 `manage_instruction/Work_Instruction.md` 第三轮合同。
2. 读取 `manage_instruction/Work_Log.md` 中 3-0 到 3-5 结论。
3. 汇总第三轮实际完成内容：
   - 3-0 静态审查与旧逻辑定位。
   - 3-1 service 边界建立。
   - 3-2a 日期过滤抽取。
   - 3-2b 日程/待办判定抽取。
   - 3-3a day/week/todo 排序抽取。
   - 3-3b todo_board 主排序抽取。
   - 3-4a 分类状态判断抽取。
   - 3-4b 分类删除动作决策抽取。
   - 3-5 四象限规则评估，暂不创建 matrix service。
4. 验证新增/修改 service 可 import。
5. 验证 service 不依赖 UI / db_manager / Repository。
6. 验证旧 `db_manager` 路径仍可用。
7. 验证 UI import 可通过。
8. 验证关键过滤、排序、分类状态、删除动作映射结果符合第三轮日志。
9. 确认 `matrix_classification_service.py` 未创建。
10. 确认 `src`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。
11. 在 `Work_Log.md` 记录第三轮是否可归档。

## 4. 验收命令

读取合同和日志：

Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8

验证 service import：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.services.schedule_query_service import ScheduleQueryService; from src.services.schedule_sort_service import ScheduleSortService; from src.services.category_policy_service import CategoryPolicyService, CategoryStatus, CategoryDeleteAction; print('service imports ok')"

验证 service 不依赖 UI / db_manager / Repository：

rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_query_service.py src/services/schedule_sort_service.py src/services/category_policy_service.py

预期：无输出。若 `rg` 返回退出码 1 但无输出，视为通过。

验证旧 `db_manager` 路径仍可用：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; print('all schedules', len(db_manager.get_all_schedules())); print('today schedules', len(db_manager.get_schedules_for_date(date.today()))); print('active categories', len(db_manager.get_active_categories())); print('missing category status', db_manager.check_category_status(-999999)); assert isinstance(db_manager.get_all_schedules(), list); assert isinstance(db_manager.get_schedules_for_date(date.today()), list); assert isinstance(db_manager.get_active_categories(), list); assert db_manager.check_category_status(-999999) in {'empty','active','historical'}"

验证 UI import 可通过：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import importlib; mods=['src.ui.dashboard','src.ui.week_window','src.ui.todo','src.ui.todo_board','src.ui.list_picker']; [importlib.import_module(m) for m in mods]; print('ui imports ok', mods)"

如果 UI import 因 Qt/GUI 环境限制失败，记录完整错误摘要，并继续执行后续 `py_compile` 作为语法兜底；不要修改源码规避环境问题。

验证日期过滤路径仍可用：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date, timedelta; from src.data.database import db_manager; days=[date.today()+timedelta(days=i) for i in (-1,0,1)]; rows=[(d.isoformat(), [s.id for s in db_manager.get_schedules_for_date(d)]) for d in days]; print('date filter rows', rows); assert all(isinstance(ids, list) for _, ids in rows)"

验证日程/待办判定与 split：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; from src.services.schedule_query_service import ScheduleQueryService; items=db_manager.get_all_schedules(); schedules,todos=ScheduleQueryService.split_schedule_and_todo(items); print('split', len(schedules), len(todos)); print('sample', [(s.id, ScheduleQueryService.is_todo(s), ScheduleQueryService.is_schedule(s)) for s in items[:5]]); assert isinstance(schedules, list); assert isinstance(todos, list)"

验证排序关键结果：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; from src.services.schedule_query_service import ScheduleQueryService; from src.services.schedule_sort_service import ScheduleSortService; today=db_manager.get_schedules_for_date(date.today()); all_items=db_manager.get_all_schedules(); dashboard=[s for s in today if getattr(s,'status',0)!=2 and not ScheduleQueryService.is_todo(s)]; week=[s for s in today if ScheduleQueryService.is_schedule(s) and getattr(s,'status',0)!=2]; todo=[s for s in all_items if getattr(s,'status',0)!=2 and ScheduleQueryService.is_todo(s)]; board=[s for s in all_items if getattr(s,'status',0)!=2 and ScheduleQueryService.is_todo(s) and getattr(s,'status',0)==0]; print('dashboard sorted', [s.id for s in ScheduleSortService.sort_for_day_view(dashboard)]); print('week sorted', [s.id for s in ScheduleSortService.sort_for_week_view(week)]); print('todo sorted', [s.id for s in ScheduleSortService.sort_for_todo_list(todo)]); print('board sorted', [s.id for s in ScheduleSortService.sort_for_todo_board(board)])"

验证排序方法返回新 list，不原地修改输入：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; from src.services.schedule_sort_service import ScheduleSortService; items=list(db_manager.get_all_schedules()[:8]); original=[s.id for s in items]; funcs=[ScheduleSortService.sort_for_day_view, ScheduleSortService.sort_for_week_view, ScheduleSortService.sort_for_todo_list, ScheduleSortService.sort_for_todo_board]; results=[]; [results.append((f.__name__, isinstance(f(items), list), f(items) is not items, [s.id for s in items]==original)) for f in funcs]; print('sort list behavior', results); assert all(a and b and c for _,a,b,c in results)"

验证分类状态和删除动作映射：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; from src.services.category_policy_service import CategoryPolicyService, CategoryDeleteAction; cats=db_manager.get_active_categories(); rows=[(c.id,c.name,db_manager.check_category_status(c.id),CategoryPolicyService.choose_delete_action(db_manager.check_category_status(c.id)).value) for c in cats]; rows.append((-999999,'missing',db_manager.check_category_status(-999999),CategoryPolicyService.choose_delete_action(db_manager.check_category_status(-999999)).value)); print('category rows', rows); expected={'active':'block','historical':'soft_delete','empty':'hard_delete'}; assert all(status in expected for _,_,status,_ in rows); assert all(action==expected[status] for _,_,status,action in rows)"

验证 `db_manager.check_category_status` 仍返回字符串：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; cats=db_manager.get_active_categories(); ids=[c.id for c in cats[:5]]+[-999999]; vals=[db_manager.check_category_status(i) for i in ids]; print('category status values', vals); assert all(isinstance(v, str) for v in vals); assert all(v in {'empty','active','historical'} for v in vals)"

确认 matrix service 未创建：

Test-Path src\services\matrix_classification_service.py
rg -n "matrix_classification_service|MatrixClassificationService" src manage_instruction

预期：

- `Test-Path` 输出 `False`。
- `rg` 只能在管理文档/日志中命中“未创建/暂不实现”等记录，不应在 `src/` 中命中实际 service。

语法检查：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src\services\schedule_query_service.py src\services\schedule_sort_service.py src\services\category_policy_service.py src\repositories\schedule_repository.py src\repositories\category_repository.py src\ui\dashboard.py src\ui\week_window.py src\ui\todo.py src\ui\todo_board.py src\ui\list_picker.py

范围检查：

git diff --name-only -- src
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch

预期：

- `src` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- 最终只允许：
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第三轮 3-6（第三轮整体验收与归档准备）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 第三轮完成项汇总
- service import 验证结果
- service 静态依赖检查结果
- 旧 `db_manager` 路径验证结果
- UI import 验证结果
- 日期过滤验证结果
- 日程/待办判定验证结果
- 排序关键结果验证
- 排序方法是否返回新 list 且不原地修改输入
- 分类状态和删除动作映射验证结果
- `db_manager.check_category_status` 返回字符串验证结果
- `matrix_classification_service.py` 是否未创建
- 四象限规则缺口是否已记录
- py_compile 结果
- diff 范围检查结果
- 第三轮是否可归档
- 未完成事项
- 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
