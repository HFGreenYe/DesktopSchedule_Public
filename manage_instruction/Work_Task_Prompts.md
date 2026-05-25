请执行第六轮 6-8：第六轮整体验收与归档准备。本轮只做总体验收、日志汇总和归档准备，不改源码。

## 1. 本轮目标

基于 Work_Instruction.md 第六轮阶段合同，以及 Work_Log.md 中 6-0 ~ 6-7 的结论，对第六轮 Controller / Router / EventBus 协调层改造做整体验收。

本轮目标：

- 汇总第六轮所有小工单结果。
- 验证新增/修改的 controller 可 import。
- 验证 global_signals 兼容性和 refresh_requested 新信号。
- 验证 MainWindow import 可用。
- 验证 ViewRouter 精确路由决策行为。
- 验证 MainController 添加页来源决策行为。
- 验证 RefreshCoordinator 刷新回调行为。
- 验证 MainWindow 中关键协调入口仍存在。
- 验证禁止范围无 diff。
- 明确第六轮是否可归档。
- 明确第七轮 Theme/QSS 接入前需要保留的风险点。

本轮只做验收和日志，不新增功能，不继续接管详情弹窗，不修改任何 src 源码。

## 2. 允许/禁止

本轮允许修改：

- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- src/
- main.py
- requirements.txt
- schedule.db
- Work_Snapshot.md
- Work_Formulation.md

禁止事项：

- 不修改 controller。
- 不修改 MainWindow。
- 不修改 signals.py。
- 不修改任何 UI 文件。
- 不新增 EventBus 信号。
- 不连接 refresh_requested。
- 不改数据库。
- 不写 schedule.db。
- 不改 requirements.txt。
- 不做第七轮 Theme/QSS 接入。
- 不做归档提交。
- 不提交 Git。

若开工前已有管理文档 diff，需要在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体验收任务

1. 读取第六轮阶段合同和当前日志：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8

    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8

2. 汇总 6-0 ~ 6-7 完成情况，至少包括：

- 6-0：静态审查与跨视图耦合定位。
- 6-1：Controller / Router / Coordinator 最小骨架。
- 6-2：ViewRouter 接管 MainWindow.switch_view 纯路由决策。
- 6-3：添加页来源与 picker 返回状态基线。
- 6-4：MainController 接管 source_view_for_add 最小闭环。
- 6-5：RefreshCoordinator 建立 Dashboard/Todo/Week 三连刷新协调边界。
- 6-6：新增 refresh_requested 并行 EventBus 通知试点。
- 6-7：详情弹窗与跨视图刷新回流复核。

3. 验证 controller import：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.controllers.main_controller import MainController; from src.controllers.view_router import ViewRouter; from src.controllers.refresh_coordinator import RefreshCoordinator; import src.controllers as controllers; print('controller imports ok'); print(MainController is not None, ViewRouter is not None, RefreshCoordinator is not None, controllers is not None)"

4. 验证 py_compile：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/controllers/main_controller.py src/controllers/view_router.py src/controllers/refresh_coordinator.py src/controllers/__init__.py src/utils/signals.py src/ui/main_window.py

5. 验证 ViewRouter 精确路由决策：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.controllers.view_router import ViewRouter; assert ViewRouter.classify_main_view('day') == 'day'; assert ViewRouter.classify_main_view('week') == 'week'; assert ViewRouter.classify_main_view('month') == 'month'; assert ViewRouter.classify_main_view('todo') == 'todo'; assert ViewRouter.classify_main_view('priority') == 'priority'; assert ViewRouter.classify_main_view('bad') is None; assert ViewRouter.classify_main_view(' WEEK ') is None; assert ViewRouter.classify_main_view('Week') is None; print('view router exact behavior ok')"

6. 验证 MainController 添加页来源决策：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.controllers.main_controller import MainController; c=MainController(); dashboard=object(); todo=object(); other=object(); old=object(); assert c.resolve_add_source(dashboard, dashboard, todo, old) is dashboard; assert c.resolve_add_source(todo, dashboard, todo, old) is todo; assert c.resolve_add_source(other, dashboard, todo, old) is old; assert c.resolve_add_source(other, dashboard, todo, None) is None; assert c.resolve_add_return_target(todo, dashboard) is todo; assert c.resolve_add_return_target(None, dashboard) is dashboard; assert c.default_to_schedule_for_add(dashboard, todo) is True; assert c.default_to_schedule_for_add(todo, todo) is False; assert c.default_to_schedule_for_add(other, todo) is True; print('main controller add source behavior ok')"

7. 验证 RefreshCoordinator 行为：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.controllers.refresh_coordinator import RefreshCoordinator; c=RefreshCoordinator(); calls=[]; c.register('dashboard', lambda: calls.append('dashboard')); c.register('todo', lambda: calls.append('todo')); c.register('week_if_visible', lambda: calls.append('week_if_visible')); assert c.trigger('dashboard') is True; assert c.trigger('missing') is False; assert c.trigger_many(['todo','week_if_visible']) == 2; assert calls == ['dashboard','todo','week_if_visible']; c.unregister('todo'); assert c.trigger('todo') is False; print('refresh coordinator behavior ok')"

8. 验证 global_signals 兼容性：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.utils.signals import global_signals; hits=[]; global_signals.skin_changed.connect(lambda: hits.append('skin')); global_signals.skin_changed.emit(); assert hits == ['skin']; assert hasattr(global_signals, 'refresh_requested'); global_signals.refresh_requested.connect(lambda domain: hits.append(domain)); global_signals.refresh_requested.emit('dashboard_todo_week'); assert hits == ['skin', 'dashboard_todo_week']; print('global signals compatibility ok')"

9. 验证 MainWindow import：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.main_window import MainWindow; print('main window import ok', MainWindow is not None)"

10. 静态确认 MainWindow 第六轮关键接入点：

    rg -n "MainController|ViewRouter|global_signals|_register_refresh_targets|_refresh_dashboard_todo_week|request_refresh_many|refresh_requested|resolve_add_source|resolve_add_return_target|default_to_schedule_for_add|classify_main_view" src/ui/main_window.py

11. 静态确认 signals.py 旧信号签名和新信号：

    rg -n "skin_changed|theme_changed|schedule_added|schedule_updated|schedule_deleted|category_changed|refresh_requested|global_signals" src/utils/signals.py

预期：

- skin_changed 仍为 pyqtSignal()
- theme_changed 仍为 pyqtSignal(str)
- schedule_added 仍为 pyqtSignal(object)
- schedule_updated 仍为 pyqtSignal(object)
- schedule_deleted 仍为 pyqtSignal(int)
- category_changed 仍为 pyqtSignal()
- refresh_requested 为 pyqtSignal(str)
- global_signals 名称保留

12. 静态依赖检查 controller 不依赖 UI/db/Repository：

    rg -n "QWidget|QStackedWidget|PyQt|PySide|MainWindow|WeekWindow|MonthWindow|TodoView|TodoBoard|db_manager|Repository|ScheduleRepository|CategoryRepository|add_schedule|update_schedule|delete_schedule|soft_delete|hard_delete|setCurrentWidget|refresh_data" src/controllers

预期无输出。
如果命中来自注释或文档字符串，需要确认不会造成运行依赖，并在 Work_Log.md 说明。

13. 检查第六轮未迁移债务，至少记录：

- MainWindow 仍保留 Qt 实际路由操作。
- picker time/alarm/list edit 写库和返回路径仍在 UI。
- WeekWindow 内部 picker 路径仍独立。
- TodoBoardWindow view_stack/list picker 状态机仍未迁移。
- 详情弹窗打开和 source_view 分支仍未迁移。
- refresh_requested 当前仍无 UI 监听者，只是并行通知试点。
- 第八轮 UI 拆分时应重点处理 TodoBoardWindow / MainWindow / WeekWindow 大文件结构。

14. diff 范围检查：

    git diff --name-only -- src

    git diff --name-only -- main.py

    git diff --name-only -- requirements.txt

    git diff --name-only -- schedule.db

    git diff --name-only

    git status --short --branch

预期：

- src 无 diff。
- main.py 无 diff。
- requirements.txt 无 diff。
- schedule.db 无 diff。
- 最终只允许 manage_instruction/Work_Log.md，以及必要时的 manage_instruction/Work_Task_Prompts.md。
- 如果开工前已有管理文档 diff，需要在日志中明确说明它是开工前既有状态，不属于 6-8 执行改动。

## 4. Work_Log.md 记录要求

更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第六轮 6-8（第六轮整体验收与归档准备）
- 开工前 git 状态
- 实际修改文件
- 6-0 ~ 6-7 完成摘要
- 第六轮实际迁移到 controller/router/coordinator 的职责：
  - ViewRouter
  - MainController
  - RefreshCoordinator
  - global_signals.refresh_requested
- 保留在 UI 中的职责及原因
- controller import 验证结果
- py_compile 验证结果
- ViewRouter 行为验证结果
- MainController 行为验证结果
- RefreshCoordinator 行为验证结果
- global_signals 兼容性验证结果
- MainWindow import 或兜底验证结果
- MainWindow 关键接入点静态检查结果
- signals.py 旧信号签名检查结果
- controller 静态依赖检查结果
- diff 范围检查结果
- 第六轮未迁移债务
- 第七轮 Theme/QSS 接入前注意事项
- 是否建议第六轮归档
- 未完成事项
- 风险或疑点

## 5. 完成后要求

完成后不要提交 Git，等待顾问窗口复核。

如果验收全部通过，请在 Work_Log.md 明确写：

- 第六轮可归档。
- 可进入第七轮 Theme/QSS 接入阶段合同/规划。

如果任一验证失败：

- 不要修源码。
- 记录失败命令、失败原因和建议处理方式。
- 等待顾问窗口/决策窗口复核后再决定是否补修。
