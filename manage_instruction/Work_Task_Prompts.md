请执行第六轮 6-1：Controller / Router / Coordinator 最小骨架。本轮只创建/完善最小 controller 文件，不接入旧 UI，不替换旧路由和刷新逻辑。

## 1. 本轮目标

基于 manage_instruction/Work_Instruction.md 第六轮阶段合同，以及 Work_Log.md 中 6-0 的静态审查结论，建立第六轮后续会使用的最小协调层骨架。

本轮目标只包括：

- 创建或完善 src/controllers/main_controller.py。
- 创建或完善 src/controllers/view_router.py。
- 创建或完善 src/controllers/refresh_coordinator.py。
- 更新 src/controllers/__init__.py 做轻量导出。
- 保证 MainController、ViewRouter、RefreshCoordinator 可 import。
- 保证 controller 文件不依赖 QWidget、db_manager、Repository、Service 写入对象。
- 不接入 MainWindow、WeekWindow、MonthWindow、TodoView、TodoBoardWindow。
- 不改变任何旧 UI 行为。

本轮只是建立边界，不迁移业务逻辑、不迁移 UI 路由、不迁移刷新链路。

## 2. 允许/禁止

本轮允许修改：

- src/controllers/__init__.py
- src/controllers/main_controller.py
- src/controllers/view_router.py
- src/controllers/refresh_coordinator.py
- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- src/ui/
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

- 不接 UI。
- 不修改 MainWindow。
- 不修改 WeekWindow。
- 不修改 MonthWindow。
- 不修改 TodoView。
- 不修改 TodoBoardWindow。
- 不修改 global_signals。
- 不新增或修改 signal。
- 不写数据库。
- 不改 db_manager API。
- 不迁移 switch_view。
- 不迁移 picker 返回逻辑。
- 不迁移刷新逻辑。
- 不创建空泛复杂抽象。
- 不实现新功能。

若开工前已有管理文档 diff，需要在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取第六轮阶段合同和 6-0 结论：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8

    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8

2. 检查 controller 目录当前状态：

    Get-ChildItem -Path src\controllers -Force

    Get-Content -Path src\controllers\__init__.py -Encoding UTF8

3. 新增或完善 src/controllers/view_router.py。

   要求：

   - 只放最小路由决策边界。
   - 可以定义 ViewRouter 类。
   - 可以定义轻量的 route/view name 常量或集合。
   - 可以提供不触碰 Qt 的纯判断/归一化方法，例如 normalize_view_name(view_name) 或 is_known_view(view_name)。
   - 不直接 import QWidget、QStackedWidget、MainWindow、WeekWindow、MonthWindow、TodoView、TodoBoardWindow。
   - 不调用 show/hide/setCurrentWidget。
   - 不改变旧 switch_view 行为。

4. 新增或完善 src/controllers/refresh_coordinator.py。

   要求：

   - 只放刷新协调边界。
   - 可以定义 RefreshCoordinator 类。
   - 可以预留注册刷新回调的轻量结构，但不得接入旧 UI。
   - 如果实现回调注册，也只能保存 callable 并提供显式调用方法；不得自动连接 UI 或 global_signals。
   - 不 import db_manager。
   - 不 import Repository。
   - 不 import QWidget。
   - 不写数据库。
   - 不改变旧刷新触发时机。

5. 新增或完善 src/controllers/main_controller.py。

   要求：

   - 只放主协调器边界。
   - 可以定义 MainController 类。
   - 可以组合 ViewRouter 和 RefreshCoordinator。
   - 不持有具体 UI 窗口实例。
   - 不 import MainWindow。
   - 不 import QWidget。
   - 不 import db_manager。
   - 不 import Repository。
   - 不调用旧 UI 方法。
   - 不执行实际路由、刷新或写库。

6. 更新 src/controllers/__init__.py。

   要求：

   - 只做轻量导出。
   - 可以导出 MainController、ViewRouter、RefreshCoordinator。
   - 不触发 UI 创建。
   - 不触发数据库连接。
   - 不触发信号连接副作用。

7. 不修改任何 src/ui 文件。

8. 不修改 src/utils/signals.py。

9. 不修改 src/services、src/data、src/repositories。

## 4. 验收命令

1. controller import 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.controllers.main_controller import MainController; from src.controllers.view_router import ViewRouter; from src.controllers.refresh_coordinator import RefreshCoordinator; import src.controllers as controllers; print('controller imports ok'); print(MainController is not None, ViewRouter is not None, RefreshCoordinator is not None, controllers is not None)"

2. py_compile 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/controllers/main_controller.py src/controllers/view_router.py src/controllers/refresh_coordinator.py src/controllers/__init__.py

3. 静态依赖检查，确认 controller 不依赖 UI、db_manager、Repository、Service 写入对象：

    rg -n "QWidget|QStackedWidget|PyQt|PySide|MainWindow|WeekWindow|MonthWindow|TodoView|TodoBoard|db_manager|Repository|ScheduleRepository|CategoryRepository|add_schedule|update_schedule|delete_schedule|soft_delete|hard_delete" src/controllers

   预期：
   - 不应命中 QWidget/QStackedWidget/PyQt/PySide。
   - 不应命中 MainWindow/WeekWindow/MonthWindow/TodoView/TodoBoard。
   - 不应命中 db_manager/Repository/ScheduleRepository/CategoryRepository。
   - 不应命中写入方法名。
   - 如果命中类名来自注释或文档字符串，需要确认不会造成运行依赖，并在 Work_Log.md 说明。

4. 检查 src/ui 无改动：

    git diff --name-only -- src/ui

5. 检查 src/data 无改动：

    git diff --name-only -- src/data

6. 检查 src/repositories 无改动：

    git diff --name-only -- src/repositories

7. 检查 src/services 无改动：

    git diff --name-only -- src/services

8. 检查 src/utils/signals.py 无改动：

    git diff --name-only -- src/utils/signals.py

9. 检查 main.py、requirements.txt、schedule.db 无改动：

    git diff --name-only -- main.py

    git diff --name-only -- requirements.txt

    git diff --name-only -- schedule.db

10. 检查本轮最终 diff 范围：

    git diff --name-only

    git status --short --branch

预期最终只允许包含：

- src/controllers/__init__.py
- src/controllers/main_controller.py
- src/controllers/view_router.py
- src/controllers/refresh_coordinator.py
- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在需要维护本轮复核锚点时）

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

## 5. 日志要求

更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第六轮 6-1（Controller / Router / Coordinator 最小骨架）
- 开工前 git 状态
- 实际修改文件
- 新增或完善的 controller 文件
- MainController 当前职责边界
- ViewRouter 当前职责边界
- RefreshCoordinator 当前职责边界
- __init__.py 导出说明
- import 验证命令和结果
- py_compile 验证命令和结果
- 静态依赖检查结果
- src/ui 是否无 diff
- src/data 是否无 diff
- src/repositories 是否无 diff
- src/services 是否无 diff
- src/utils/signals.py 是否无 diff
- main.py、requirements.txt、schedule.db 是否无 diff
- 最终 diff 范围检查结果
- 未完成事项
- 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
