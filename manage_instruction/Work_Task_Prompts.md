请执行第六轮 6-6：EventBus 并行通知试点。本轮只做一个低风险 EventBus 并行通知，不替换旧刷新路径。

## 1. 本轮目标

基于 Work_Instruction.md 第六轮阶段合同，以及 Work_Log.md 中 6-0 ~ 6-5 的结论，在不移除旧直接刷新路径的前提下，选择一个低风险点增加 EventBus 并行通知。

本轮目标：

- 新增一个兼容式刷新通知信号。
- 在 MainWindow 已有刷新协调路径执行完成后，并行发出 EventBus 通知。
- 旧刷新路径仍然执行，且仍是实际 UI 刷新的主路径。
- 新 EventBus 信号只能作为未来架构的兼容增强，不得成为唯一刷新路径。
- 不新增数据库行为。
- 不改变 UI 行为。
- 不修改 WeekWindow / TodoView / TodoBoardWindow / MonthWindow。
- 不修改 Data / Repository / Service。
- 不修改旧信号签名。

推荐试点点位：

- MainWindow._refresh_dashboard_todo_week()
- 该方法当前已按旧顺序触发：
  - dashboard
  - todo
  - week_if_visible
- 本轮只允许在该旧刷新路径执行后，额外 emit 一个刷新域通知，例如：
  - global_signals.refresh_requested.emit("dashboard_todo_week")

注意：

- 不要用新 EventBus 通知替代 _refresh_dashboard_todo_week() 的实际刷新。
- 不要让任何旧 UI 依赖新信号才能刷新。
- 不要把 EventBus 接入 WeekWindow/TodoBoardWindow。
- 不要新增复杂 mediator。

## 2. 允许/禁止

本轮允许修改：

- src/utils/signals.py
- src/ui/main_window.py
- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在需要维护本轮复核锚点时）

本轮通常不需要修改，但如确有必要可修改：

- src/controllers/refresh_coordinator.py

本轮禁止修改：

- src/controllers/main_controller.py
- src/controllers/view_router.py
- src/controllers/__init__.py
- src/ui/week_window.py
- src/ui/month_window.py
- src/ui/todo.py
- src/ui/todo_board.py
- src/data/
- src/repositories/
- src/services/
- main.py
- requirements.txt
- schedule.db
- Work_Snapshot.md
- Work_Formulation.md

禁止事项：

- 不修改 global_signals 名称。
- 不修改 skin_changed 无参签名。
- 不修改 theme_changed / schedule_added / schedule_updated / schedule_deleted / category_changed 的既有签名。
- 不删除旧直接刷新路径。
- 不改变 _refresh_dashboard_todo_week 的刷新顺序。
- 不改变 _refresh_week_if_visible 的可见性判断。
- 不改变任何写库逻辑。
- 不改 db_manager API。
- 不修改 picker 返回逻辑。
- 不修改 switch_view。
- 不修改 UI 布局、文案、视觉和交互流程。
- 不提交 Git。

若开工前已有管理文档 diff，需要在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取阶段合同和 6-0 ~ 6-5 日志：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8

    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8

2. 读取当前 signals.py 和 MainWindow 刷新协调路径：

    Get-Content -Path src\utils\signals.py -Encoding UTF8

    rg -n "global_signals|_refresh_dashboard_todo_week|_refresh_week_if_visible|page_dashboard\\.refresh_data|page_todo\\.refresh_data|request_refresh_many|schedule_added|schedule_updated|category_changed" src/ui/main_window.py src/utils/signals.py

3. 在 src/utils/signals.py 中新增一个兼容式刷新通知信号。

建议新增：

- refresh_requested = pyqtSignal(str)

要求：

- 保留 global_signals 名称。
- 保留 skin_changed = pyqtSignal() 无参信号。
- 不修改任何既有信号签名。
- 新信号只表示“某刷新域被请求或已经执行相关刷新协调”，本轮不要求任何 UI 监听它。
- 不新增复杂 payload 对象。
- 不新增依赖。

4. 最小修改 src/ui/main_window.py。

建议方式：

- import global_signals。
- 在 _refresh_dashboard_todo_week() 内，保持现有旧刷新协调调用不变。
- 在旧刷新路径执行之后，追加：

    global_signals.refresh_requested.emit("dashboard_todo_week")

要求：

- 旧刷新路径必须先执行。
- EventBus 通知必须后执行。
- 不改变 request_refresh_many(("dashboard", "todo", "week_if_visible")) 的顺序。
- 不改变 _refresh_week_if_visible。
- 不新增任何 signal connect。
- 不让 UI 刷新依赖 refresh_requested。
- 不修改其他方法，除非是必要 import。

5. 如果发现 refresh_requested 已存在：

- 不重复定义。
- 只复用现有信号。
- 在 Work_Log.md 记录“信号已存在，未重复新增”。

6. 不修改 RefreshCoordinator，除非发现必须由它统一发出通知。

如果修改 RefreshCoordinator，必须满足：

- 不 import Qt。
- 不 import global_signals。
- 不 import UI。
- 不写数据库。
- 必须在 Work_Log.md 解释为什么 MainWindow 直接 emit 不适合。

优先方案仍是：signals.py 新增信号，MainWindow 在旧刷新后直接 emit。

## 4. 验收命令

1. py_compile 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/utils/signals.py src/ui/main_window.py

2. global_signals 兼容性和新信号验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.utils.signals import global_signals; hits=[]; global_signals.skin_changed.connect(lambda: hits.append('skin')); global_signals.skin_changed.emit(); assert hits == ['skin']; assert hasattr(global_signals, 'refresh_requested'); global_signals.refresh_requested.connect(lambda domain: hits.append(domain)); global_signals.refresh_requested.emit('dashboard_todo_week'); assert hits == ['skin', 'dashboard_todo_week']; print('global signals compatibility ok')"

3. MainWindow import 级验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.main_window import MainWindow; print('main window import ok', MainWindow is not None)"

4. 静态确认旧刷新路径仍在，并且 EventBus 通知只是追加：

    rg -n "_refresh_dashboard_todo_week|request_refresh_many|refresh_requested|global_signals|page_dashboard\\.refresh_data|page_todo\\.refresh_data|_refresh_week_if_visible" src/ui/main_window.py src/utils/signals.py

5. 静态确认 signals.py 旧信号签名未改：

    rg -n "skin_changed|theme_changed|schedule_added|schedule_updated|schedule_deleted|category_changed|refresh_requested|global_signals" src/utils/signals.py

预期：

- skin_changed 仍是 pyqtSignal()
- theme_changed 仍是 pyqtSignal(str)
- schedule_added 仍是 pyqtSignal(object)
- schedule_updated 仍是 pyqtSignal(object)
- schedule_deleted 仍是 pyqtSignal(int)
- category_changed 仍是 pyqtSignal()
- refresh_requested 是新增 pyqtSignal(str)
- global_signals 名称保留

6. 禁止范围检查：

    git diff --name-only -- src/controllers/main_controller.py

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

7. 最终 diff 范围检查：

    git diff --name-only

    git status --short --branch

预期最终只允许包含：

- src/utils/signals.py
- src/ui/main_window.py
- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在需要维护本轮复核锚点时）

如果你确实修改了 src/controllers/refresh_coordinator.py，必须在 Work_Log.md 解释原因；否则不应出现。

如果 MainWindow import 因本地 GUI/Qt 环境问题失败，但 py_compile 通过，需要记录失败原因，并至少完成静态验证。

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

## 5. 日志要求

更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第六轮 6-6（EventBus 并行通知试点）
- 开工前 git 状态
- 实际修改文件
- 选择的低风险通知点
- 新增或复用的 EventBus 信号
- 旧刷新路径是否仍执行
- 新 EventBus 通知是否只作为并行增强
- refresh_requested 的 payload 语义
- 是否保持 skin_changed 无参签名
- 是否保持其他旧信号签名
- 是否未连接任何 UI 监听新信号
- 是否未修改 WeekWindow / TodoView / TodoBoardWindow / MonthWindow
- py_compile 验证结果
- global_signals 兼容性和新信号验证结果
- MainWindow import 或兜底验证结果
- 静态检查结果
- 禁止范围 diff 检查结果
- 最终 diff 范围检查结果
- 未完成事项
- 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
