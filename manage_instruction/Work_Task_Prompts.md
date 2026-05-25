请执行第六轮 6-2：ViewRouter 视图切换基线与低风险接管。本轮只处理 MainWindow.switch_view 的低风险路由决策边界，不迁移 Qt 实际 show/hide/setCurrentWidget 操作。

## 1. 本轮目标

基于 Work_Instruction.md 第六轮阶段合同，以及 Work_Log.md 中 6-0/6-1 的结论，尝试让 ViewRouter 承担 MainWindow.switch_view 中“view_name 属于哪类路由”的纯决策。

本轮目标：

- 先记录 MainWindow.switch_view 当前行为基线。
- 在 ViewRouter 中增加用于 MainWindow.switch_view 的精确路由判断方法。
- 最小修改 src/ui/main_window.py，让 switch_view 使用 ViewRouter 的纯决策结果。
- Qt 实际操作仍留在 MainWindow：
  - hide/show
  - move
  - setCurrentWidget
  - refresh_data
  - refresh_week_data
  - update_weather_ui
  - show_toast
- 保持旧行为不变，尤其是 day/week/month/todo/priority/未知 view_name 的行为不变。

重要边界：

- 当前 ViewRouter.normalize_view_name 会 strip/lower，并可能改变旧 switch_view 对大小写或空格输入的处理。
- 因此本轮不要直接用 normalize_view_name 改写 switch_view。
- 若需要新增方法，应使用“精确匹配旧字符串”的方式，例如只把完全等于 "day"、"week"、"month"、"todo"、"priority" 的值识别为对应动作。
- 对未知 view_name，必须保持旧逻辑：走最终 toast 分支，不默认回 day。
- 对 "priority"，必须保持旧逻辑：显示“准备切换至：四象限视图”，不实现四象限功能。

## 2. 允许/禁止

本轮允许修改：

- src/controllers/view_router.py
- src/ui/main_window.py
- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- src/controllers/main_controller.py
- src/controllers/refresh_coordinator.py
- src/controllers/__init__.py（除非 view_router 新增导出确有必要；通常不需要）
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

- 不迁移 switch_view 的 Qt 操作。
- 不改变 MainWindow.switch_view 的外部方法名、参数和调用方式。
- 不修改 UI 布局、文案、视觉和交互流程。
- 不修改 WeekWindow/MonthWindow 生命周期逻辑。
- 不修改刷新触发时机。
- 不新增 EventBus 信号。
- 不接 global_signals。
- 不写数据库。
- 不实现四象限视图。
- 不把未知 view_name 默认切回 day。

若开工前已有管理文档 diff，需要在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取阶段合同和 6-0/6-1 日志：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8

    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8

2. 读取当前 ViewRouter 与 MainWindow.switch_view：

    Get-Content -Path src\controllers\view_router.py -Encoding UTF8

    rg -n "def switch_view|view_name ==|view_name !=|show_toast|setCurrentWidget|refresh_data|refresh_week_data|month_window|week_window" src/ui/main_window.py

3. 记录 switch_view 当前行为基线，至少包括：

- view_name == "week"：
  - 隐藏主窗口
  - 刷新 week_window
  - 同步天气
  - 移动并显示 week_window
- view_name == "month"：
  - 隐藏主窗口
  - 同步天气
  - 移动并显示 month_window
- view_name == "todo"：
  - body_stack 切到 page_todo
  - page_todo.refresh_data()
- view_name == "day"：
  - body_stack 切到 page_dashboard
  - page_dashboard.refresh_data()
- view_name == "priority"：
  - show_toast("准备切换至：四象限视图")
- 其他未知 view_name：
  - show_toast(f"准备切换至：{view_name}")
- 从可见 week_window 切到非 week 时：
  - 按旧逻辑移动主窗口、隐藏 week_window、显示主窗口
- 从可见 month_window 切到非 month 时：
  - 按旧逻辑移动主窗口、隐藏 month_window、显示主窗口

4. 在 src/controllers/view_router.py 中新增或完善一个专用于旧 switch_view 的精确判断方法。

建议形态可以是以下之一，但由你按现有代码风格决定：

- classify_main_view(view_name)
- resolve_switch_action(view_name)
- get_switch_target(view_name)

要求：

- 只做纯字符串精确匹配。
- 识别 "day"、"week"、"month"、"todo"、"priority"。
- 未知值返回 None 或 "unknown"。
- 不 strip。
- 不 lower。
- 不把未知值默认到 day。
- 不 import Qt。
- 不 import UI。
- 不 import db_manager。
- 不 import Repository。
- 不触发任何副作用。

5. 最小修改 src/ui/main_window.py。

要求：

- 引入 ViewRouter 或通过已有 controller 边界使用 ViewRouter，但不要创建复杂控制器接入。
- switch_view 开头可以计算 route_action = ViewRouter 的精确判断结果。
- 保留原 Qt 操作代码在 MainWindow。
- 保留“切换前隐藏 view_selector”的逻辑。
- 保留“从 week/month 切走时恢复主窗口位置”的逻辑。
- 用 route_action 替代后续分支判断可以，但必须保证旧行为一致。
- 对未知 view_name，仍使用原始 view_name 进入 toast。
- 对 priority，仍显示原文案，不实现新页面。
- 不修改 switch_view 之外的其他流程，除非是必要 import。

6. 不修改任何其他 UI 文件。

7. 不修改 signals.py。

## 4. 验收命令

1. py_compile 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/controllers/view_router.py src/ui/main_window.py

2. ViewRouter 纯行为验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.controllers.view_router import ViewRouter; r=ViewRouter(); method=getattr(r, 'classify_main_view', None) or getattr(r, 'resolve_switch_action', None) or getattr(r, 'get_switch_target', None); assert method is not None, 'missing switch classification method'; print('day', method('day')); print('week', method('week')); print('month', method('month')); print('todo', method('todo')); print('priority', method('priority')); print('unknown', method('bad')); assert method('day') in ('day', 'dashboard'); assert method('week') == 'week'; assert method('month') == 'month'; assert method('todo') == 'todo'; assert method('priority') == 'priority'; assert method('bad') in (None, 'unknown'); assert method(' WEEK ') in (None, 'unknown'); assert method('Week') in (None, 'unknown'); print('view router exact switch behavior ok')"

3. controller import 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.controllers.main_controller import MainController; from src.controllers.view_router import ViewRouter; from src.controllers.refresh_coordinator import RefreshCoordinator; print('controller imports ok')"

4. MainWindow import 级验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.main_window import MainWindow; print('main window import ok', MainWindow is not None)"

5. 静态确认 switch_view 仍保留 Qt 操作在 MainWindow：

    rg -n "def switch_view|setCurrentWidget|refresh_data|refresh_week_data|show_toast|week_window\\.show|week_window\\.hide|month_window\\.show|month_window\\.hide" src/ui/main_window.py

6. 静态依赖检查，确认 ViewRouter 不依赖 UI/db/Repository/Qt：

    rg -n "QWidget|QStackedWidget|PyQt|PySide|MainWindow|WeekWindow|MonthWindow|TodoView|TodoBoard|db_manager|Repository|ScheduleRepository|CategoryRepository" src/controllers/view_router.py

   预期无输出。

7. 禁止范围检查：

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

- src/controllers/view_router.py
- src/ui/main_window.py
- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在需要维护本轮复核锚点时）

如果 MainWindow import 因本地 GUI/Qt 环境问题失败，但 py_compile 通过，需要记录失败原因，并至少完成静态验证。

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

## 5. 日志要求

更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第六轮 6-2（ViewRouter 视图切换基线与低风险接管）
- 开工前 git 状态
- 实际修改文件
- switch_view 旧行为基线
- ViewRouter 新增/完善的方法名
- 为什么该方法使用精确匹配而不是 normalize_view_name
- MainWindow.switch_view 的最小替换说明
- priority 分支是否保持原行为
- 未知 view_name 是否保持原 toast 行为
- py_compile 验证结果
- ViewRouter 纯行为验证结果
- controller import 回归结果
- MainWindow import 或兜底验证结果
- ViewRouter 静态依赖检查结果
- 禁止范围 diff 检查结果
- 最终 diff 范围检查结果
- 未完成事项
- 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
