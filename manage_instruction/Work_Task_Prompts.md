请执行第六轮 6-4：添加页来源与 picker 返回状态最小接管（条件执行）。本轮只接管 MainWindow 添加页来源返回的最低风险闭环，不迁移 picker，不碰 WeekWindow/TodoBoardWindow。

## 1. 本轮目标

基于 Work_Instruction.md 第六轮阶段合同，以及 Work_Log.md 中 6-3 的基线结论，本轮只做一个最低风险闭环：

- MainWindow 添加页来源记录与返回目标决策。
- 涉及 source_view_for_add 的写入和读取。
- 不迁移 time/alarm/list picker。
- 不迁移 WeekWindow。
- 不迁移 TodoBoardWindow。
- 不改变 add/edit 保存逻辑。
- 不改变 UI 布局、文案、视觉和交互流程。

6-3 建议的最低风险候选项是：

- MainWindow source_view_for_add 闭环：
  - 从 dashboard/todo 进入添加页时记录来源。
  - 添加页取消时返回来源页，默认 dashboard。
  - 添加页保存后返回来源页，默认 dashboard。
  - 在添加页再次点 add 时返回来源页。
  - 从 todo 进入添加页时 default_to_schedule=False，否则 True。

本轮目标是把这些“返回目标/来源判断”的纯决策迁入 MainController，但 Qt 实际 setCurrentWidget、page_add.reset、refresh_data 等操作仍留在 MainWindow。

## 2. 允许/禁止

本轮允许修改：

- src/controllers/main_controller.py
- src/ui/main_window.py
- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在需要维护本轮复核锚点时）

本轮通常不需要修改，但如确有必要可修改：

- src/controllers/view_router.py

本轮禁止修改：

- src/controllers/refresh_coordinator.py
- src/controllers/__init__.py（除非 MainController 导出已坏；通常不需要）
- src/ui/week_window.py
- src/ui/month_window.py
- src/ui/todo.py
- src/ui/todo_board.py
- src/data/
- src/repositories/
- src/services/
- src/utils/signals.py
- main.py
- requirements.txt
- schedule.db
- Work_Snapshot.md
- Work_Formulation.md

禁止事项：

- 不迁移 time_picker_mode。
- 不迁移 alarm_picker_mode。
- 不迁移 list_picker_mode。
- 不迁移 list_picker_source。
- 不迁移 editing_schedule。
- 不迁移任何 picker confirm/edit 写库逻辑。
- 不修改 WeekWindow picker 返回路径。
- 不修改 TodoBoardWindow picker/view_stack 状态机。
- 不新增 EventBus 信号。
- 不接 global_signals。
- 不写数据库。
- 不改 db_manager API。
- 不改变 MainWindow 对外方法名和信号连接。
- 不改变 UI 行为。
- 不提交 Git。

若开工前已有管理文档 diff，需要在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取阶段合同和 6-3 基线结论：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8

    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8

2. 读取 MainController 和 MainWindow 相关代码：

    Get-Content -Path src\controllers\main_controller.py -Encoding UTF8

    rg -n "source_view_for_add|page_add\\.btn_cancel|on_schedule_saved|switch_to_add_page|return_target|page_add\\.reset|default_to_schedule|body_stack\\.currentWidget" src/ui/main_window.py

3. 在 src/controllers/main_controller.py 中新增最小纯决策方法。

建议方法名固定为以下三个，便于验收：

- resolve_add_source(current_widget, dashboard_widget, todo_widget, existing_source=None)
- resolve_add_return_target(source_view, dashboard_widget)
- default_to_schedule_for_add(current_widget, todo_widget)

建议语义：

- resolve_add_source:
  - 如果 current_widget 是 dashboard_widget 或 todo_widget，返回 current_widget。
  - 否则返回 existing_source。
  - 不创建 UI，不调用 UI 方法，不持有 UI 引用，只返回传入对象。
- resolve_add_return_target:
  - 如果 source_view 不为 None，返回 source_view。
  - 否则返回 dashboard_widget。
- default_to_schedule_for_add:
  - 如果 current_widget 是 todo_widget，返回 False。
  - 否则返回 True。

要求：

- 这些方法必须是纯决策方法。
- 不 import QWidget。
- 不 import MainWindow。
- 不 import db_manager。
- 不 import Repository。
- 不调用 setCurrentWidget。
- 不调用 refresh_data。
- 不写数据库。
- 不保存 UI 对象为 MainController 成员属性。

4. 最小修改 src/ui/main_window.py。

允许修改点：

- 引入 MainController。
- 在 source_view_for_add 相关位置调用 MainController 的纯决策方法。
- 保留实际 Qt 操作在 MainWindow 内。

建议替换范围：

- page_add.btn_cancel 的返回目标：
  - 原行为：getattr(self, 'source_view_for_add', self.page_dashboard)
  - 新行为：通过 MainController.resolve_add_return_target(...) 得到目标，再 setCurrentWidget。
- on_schedule_saved 的 return_target：
  - 使用 MainController.resolve_add_return_target(...)。
- switch_to_add_page 中记录 source_view_for_add：
  - 使用 MainController.resolve_add_source(...) 判断是否更新来源。
- switch_to_add_page 中 default_to_schedule：
  - 使用 MainController.default_to_schedule_for_add(...)。
- 在添加页再次点 add 时返回来源页：
  - 使用 MainController.resolve_add_return_target(...)。

要求：

- 不改保存后的刷新顺序：
  - page_dashboard.refresh_data()
  - page_todo.refresh_data()
  - _refresh_week_if_visible()
- 不改 page_add.reset(...) 的调用时机。
- 不改 body_stack.setCurrentWidget(...) 的目标行为。
- 不改 handle_header_action。
- 不改 time/alarm/list picker 任何逻辑。
- 不改 WeekWindow/TodoBoardWindow。

5. 不修改任何其他 src/ui 文件。

6. 不修改 signals.py。

## 4. 验收命令

1. py_compile 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/controllers/main_controller.py src/ui/main_window.py

2. MainController 纯决策行为验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.controllers.main_controller import MainController; c=MainController(); dashboard=object(); todo=object(); other=object(); old=object(); assert c.resolve_add_source(dashboard, dashboard, todo, old) is dashboard; assert c.resolve_add_source(todo, dashboard, todo, old) is todo; assert c.resolve_add_source(other, dashboard, todo, old) is old; assert c.resolve_add_source(other, dashboard, todo, None) is None; assert c.resolve_add_return_target(todo, dashboard) is todo; assert c.resolve_add_return_target(None, dashboard) is dashboard; assert c.default_to_schedule_for_add(dashboard, todo) is True; assert c.default_to_schedule_for_add(todo, todo) is False; assert c.default_to_schedule_for_add(other, todo) is True; print('main controller add source behavior ok')"

3. controller import 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.controllers.main_controller import MainController; from src.controllers.view_router import ViewRouter; from src.controllers.refresh_coordinator import RefreshCoordinator; print('controller imports ok')"

4. MainWindow import 级验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.main_window import MainWindow; print('main window import ok', MainWindow is not None)"

5. 静态确认 MainWindow 只改 source_view_for_add 闭环，不动 picker：

    rg -n "source_view_for_add|resolve_add_source|resolve_add_return_target|default_to_schedule_for_add|page_add\\.btn_cancel|on_schedule_saved|switch_to_add_page|time_picker_mode|alarm_picker_mode|list_picker_mode|list_picker_source" src/ui/main_window.py

6. 静态依赖检查，确认 MainController 不依赖 UI/db/Repository/Qt：

    rg -n "QWidget|QStackedWidget|PyQt|PySide|MainWindow|WeekWindow|MonthWindow|TodoView|TodoBoard|db_manager|Repository|ScheduleRepository|CategoryRepository|add_schedule|update_schedule|delete_schedule|soft_delete|hard_delete|setCurrentWidget|refresh_data" src/controllers/main_controller.py

   预期无输出。
   如果命中来自注释或文档字符串，需要确认不会造成运行依赖，并在 Work_Log.md 说明。

7. 禁止范围检查：

    git diff --name-only -- src/controllers/refresh_coordinator.py

    git diff --name-only -- src/controllers/__init__.py

    git diff --name-only -- src/ui/week_window.py

    git diff --name-only -- src/ui/month_window.py

    git diff --name-only -- src/ui/todo.py

    git diff --name-only -- src/ui/todo_board.py

    git diff --name-only -- src/data

    git diff --name-only -- src/repositories

    git diff --name-only -- src/services

    git diff --name-only -- src/utils/signals.py

    git diff --name-only -- main.py

    git diff --name-only -- requirements.txt

    git diff --name-only -- schedule.db

8. 最终 diff 范围检查：

    git diff --name-only

    git status --short --branch

预期最终只允许包含：

- src/controllers/main_controller.py
- src/ui/main_window.py
- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在需要维护本轮复核锚点时）

如果你确实修改了 src/controllers/view_router.py，必须在 Work_Log.md 解释原因；否则不应出现。

如果 MainWindow import 因本地 GUI/Qt 环境问题失败，但 py_compile 通过，需要记录失败原因，并至少完成静态验证。

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

## 5. 日志要求

更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第六轮 6-4（添加页来源与 picker 返回状态最小接管）
- 开工前 git 状态
- 实际修改文件
- 是否进入源码修改分支
- 接管的具体字段/路径：
  - source_view_for_add 写入决策
  - 添加页取消返回目标
  - 添加页保存后返回目标
  - 添加页再次点击 add 的返回目标
  - default_to_schedule 判断
- MainController 新增方法名和语义
- MainWindow 最小替换说明
- 未接管路径及原因：
  - time picker
  - alarm picker
  - list picker
  - WeekWindow
  - TodoBoardWindow
- py_compile 验证结果
- MainController 纯决策行为验证结果
- controller import 回归结果
- MainWindow import 或兜底验证结果
- MainController 静态依赖检查结果
- 禁止范围 diff 检查结果
- 最终 diff 范围检查结果
- 未完成事项
- 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
