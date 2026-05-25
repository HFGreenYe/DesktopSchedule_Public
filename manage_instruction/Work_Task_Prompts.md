请执行第六轮 6-5：RefreshCoordinator 跨视图刷新边界建立。本轮只建立 MainWindow 内 Dashboard / Todo / Week 刷新协调边界，不接 EventBus，不改刷新触发时机。

## 1. 本轮目标

基于 Work_Instruction.md 第六轮阶段合同，以及 Work_Log.md 中 6-0 ~ 6-4 的结论，本轮建立最小跨视图刷新协调边界。

本轮目标：

- 使用 RefreshCoordinator 封装 MainWindow 中“刷新哪些视图”的协调动作。
- 优先处理 MainWindow 内已有的 Dashboard / Todo / Week 刷新组合。
- 保持旧刷新顺序不变：
  - page_dashboard.refresh_data()
  - page_todo.refresh_data()
  - _refresh_week_if_visible()
- 保持 _refresh_week_if_visible() 的可见性判断不变。
- 不改变触发时机。
- 不删除旧 UI 信号。
- 不新增 EventBus 信号。
- 不接 global_signals。
- 不写数据库。
- 不修改 WeekWindow / TodoView / TodoBoardWindow / MonthWindow。

本轮只建立刷新协调边界，不做事件总线替代。EventBus 并行通知留给 6-6。

## 2. 允许/禁止

本轮允许修改：

- src/controllers/refresh_coordinator.py
- src/ui/main_window.py
- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在需要维护本轮复核锚点时）

本轮通常不需要修改，但如确有必要可修改：

- src/controllers/main_controller.py

本轮禁止修改：

- src/controllers/view_router.py
- src/controllers/__init__.py
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

- 不新增或修改 global_signals。
- 不新增 EventBus 信号。
- 不连接 global_signals。
- 不改变 page_dashboard/page_todo/week_window 的刷新顺序。
- 不改变 _refresh_week_if_visible 的内部逻辑和可见性判断。
- 不改变任何写库逻辑。
- 不改 db_manager API。
- 不修改 picker 返回逻辑。
- 不修改 switch_view。
- 不修改 UI 布局、文案、视觉和交互流程。
- 不修改 WeekWindow / TodoBoardWindow / TodoView。
- 不提交 Git。

若开工前已有管理文档 diff，需要在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取阶段合同和 6-0 ~ 6-4 日志：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8

    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8

2. 读取 RefreshCoordinator、MainController、MainWindow 当前代码：

    Get-Content -Path src\controllers\refresh_coordinator.py -Encoding UTF8

    Get-Content -Path src\controllers\main_controller.py -Encoding UTF8

    rg -n "RefreshCoordinator|MainController|refresh_coordinator|main_controller|page_dashboard\\.refresh_data|page_todo\\.refresh_data|_refresh_week_if_visible|req_refresh_all|schedule_updated|on_schedule_saved|on_time_confirmed|on_alarm_confirmed|on_list_confirmed" src/ui/main_window.py

3. 先记录 MainWindow 旧刷新基线。

至少记录这些位置是否存在刷新组合：

- on_schedule_saved
- on_time_confirmed edit 分支
- on_alarm_confirmed edit 分支
- on_list_confirmed edit 分支
- _on_week_schedule_updated
- Dashboard / Todo 的 req_refresh_all 连接
- WeekWindow.schedule_updated 连接

4. 检查 src/controllers/refresh_coordinator.py 当前能力。

如果已有 register / unregister / trigger / trigger_many 能满足本轮需要，不要做复杂扩展。

如需新增方法，只允许新增纯协调方法，例如：

- trigger_registered(names)
- trigger_dashboard_todo_week()
- trigger_many(names)

要求：

- 不 import Qt。
- 不 import UI。
- 不 import db_manager。
- 不 import Repository。
- 不写数据库。
- 不自动连接信号。
- 只保存 callable 或显式触发 callable。
- 不吞异常，除非现有代码已有该策略；不得隐藏刷新失败。

5. 最小修改 src/ui/main_window.py。

建议方式：

- 如果 6-4 已在 MainWindow 中创建 MainController，则复用现有 MainController，不要重复创建。
- 如果 MainController 已有 refresh_coordinator，则通过它注册刷新目标。
- 如果没有合适入口，可以在 MainWindow 中直接持有 RefreshCoordinator，但必须说明原因。
- 注册三个刷新目标：
  - dashboard -> self.page_dashboard.refresh_data
  - todo -> self.page_todo.refresh_data
  - week_if_visible -> self._refresh_week_if_visible
- 增加一个 MainWindow 私有辅助方法，例如：

    _refresh_dashboard_todo_week()

  该方法内部按旧顺序触发：
  - dashboard
  - todo
  - week_if_visible

- 用该辅助方法替换 MainWindow 内完全同构的三连刷新代码。

优先替换这些位置的三连刷新：

- on_schedule_saved
- on_time_confirmed edit 成功后
- on_alarm_confirmed edit 成功后
- on_list_confirmed edit 成功后

要求：

- 替换前后刷新顺序必须一致。
- 替换前后触发时机必须一致。
- _refresh_week_if_visible 内部逻辑不变。
- 不替换 DashboardView.req_refresh_all / TodoView.req_refresh_all 的信号连接。
- 不替换 WeekWindow.schedule_updated 的连接。
- 不接 global_signals。
- 不修改其他 UI 文件。

如果发现某处刷新组合不是完全同构，不要强行替换；只记录保留原因。

6. 不修改 src/utils/signals.py。

7. 不修改 WeekWindow / TodoView / TodoBoardWindow / MonthWindow。

## 4. 验收命令

1. py_compile 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/controllers/refresh_coordinator.py src/controllers/main_controller.py src/ui/main_window.py

2. RefreshCoordinator 纯行为验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.controllers.refresh_coordinator import RefreshCoordinator; c=RefreshCoordinator(); calls=[]; c.register('dashboard', lambda: calls.append('dashboard')); c.register('todo', lambda: calls.append('todo')); c.register('week_if_visible', lambda: calls.append('week_if_visible')); assert c.trigger('dashboard') is True; assert c.trigger('missing') is False; count=c.trigger_many(['todo','week_if_visible']); assert count == 2; assert calls == ['dashboard','todo','week_if_visible']; c.unregister('todo'); assert c.trigger('todo') is False; print('refresh coordinator behavior ok')"

3. controller import 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.controllers.main_controller import MainController; from src.controllers.view_router import ViewRouter; from src.controllers.refresh_coordinator import RefreshCoordinator; print('controller imports ok')"

4. MainWindow import 级验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.main_window import MainWindow; print('main window import ok', MainWindow is not None)"

5. 静态确认 MainWindow 刷新顺序和接管点：

    rg -n "_refresh_dashboard_todo_week|register_refresh|register_refresh_target|request_refresh|trigger_many|page_dashboard\\.refresh_data|page_todo\\.refresh_data|_refresh_week_if_visible|on_schedule_saved|on_time_confirmed|on_alarm_confirmed|on_list_confirmed" src/ui/main_window.py

6. 静态依赖检查，确认 RefreshCoordinator 不依赖 UI/db/Repository/Qt：

    rg -n "QWidget|QStackedWidget|PyQt|PySide|MainWindow|WeekWindow|MonthWindow|TodoView|TodoBoard|db_manager|Repository|ScheduleRepository|CategoryRepository|add_schedule|update_schedule|delete_schedule|soft_delete|hard_delete|setCurrentWidget|refresh_data" src/controllers/refresh_coordinator.py

   预期无输出。
   如果命中来自注释或文档字符串，需要确认不会造成运行依赖，并在 Work_Log.md 说明。

7. 确认 signals.py 无改动：

    git diff --name-only -- src/utils/signals.py

8. 禁止范围检查：

    git diff --name-only -- src/controllers/view_router.py

    git diff --name-only -- src/controllers/__init__.py

    git diff --name-only -- src/ui/week_window.py

    git diff --name-only -- src/ui/month_window.py

    git diff --name-only -- src/ui/todo.py

    git diff --name-only -- src/ui/todo_board.py

    git diff --name-only -- src/data

    git diff --name-only -- src/repositories

    git diff --name-only -- src/services

    git diff --name-only -- main.py

    git diff --name-only -- requirements.txt

    git diff --name-only -- schedule.db

9. 最终 diff 范围检查：

    git diff --name-only

    git status --short --branch

预期最终只允许包含：

- src/controllers/refresh_coordinator.py
- src/ui/main_window.py
- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在需要维护本轮复核锚点时）

如果你确实修改了 src/controllers/main_controller.py，必须在 Work_Log.md 解释原因；否则不应出现。

如果 MainWindow import 因本地 GUI/Qt 环境问题失败，但 py_compile 通过，需要记录失败原因，并至少完成静态验证。

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

## 5. 日志要求

更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第六轮 6-5（RefreshCoordinator 跨视图刷新边界建立）
- 开工前 git 状态
- 实际修改文件
- MainWindow 旧刷新基线：
  - on_schedule_saved
  - on_time_confirmed edit 分支
  - on_alarm_confirmed edit 分支
  - on_list_confirmed edit 分支
  - req_refresh_all / schedule_updated 旧信号连接
- RefreshCoordinator 当前能力或新增方法说明
- 刷新目标注册方式：
  - dashboard
  - todo
  - week_if_visible
- 接管的刷新链路
- 保留的旧直连路径及原因
- 是否保持旧刷新顺序
- 是否保持旧触发时机
- 是否未接 global_signals
- py_compile 验证结果
- RefreshCoordinator 纯行为验证结果
- controller import 回归结果
- MainWindow import 或兜底验证结果
- RefreshCoordinator 静态依赖检查结果
- signals.py 是否无 diff
- 禁止范围 diff 检查结果
- 最终 diff 范围检查结果
- 未完成事项
- 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
