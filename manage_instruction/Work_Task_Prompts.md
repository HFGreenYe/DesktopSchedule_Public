# Work Task Prompts

# 当前待执行提示词：MP-4

## MP-4：详情编辑请求按当前可见视图路由

请执行 `MP-4（详情编辑请求按当前可见视图路由）`。本轮优先验证现有动态路由是否已经满足要求；只有发现明确缺口时，才做最小源码修正。不得默认重写整套路由。

## 1. 本轮目标

基于 `MP-0 ~ MP-3` 当前结论，本轮只处理详情弹窗编辑请求的路由规则。

目标规则：

- `ScheduleDetailPop` 只发出编辑请求信号，不直接调用具体页面。
- 详情弹窗中的修改操作应按当前可见视图路由。
- 不应被弹窗创建时的固定 `source_view` 锁死。
- 当前可见周界面时，编辑请求走 `WeekWindow`。
- 当前可见月界面时，编辑请求走 `MonthWindow`。
- 当前可见主窗口日视图时，编辑请求走主窗口日视图编辑链路。
- 当前可见待办视图时，编辑请求走待办对应链路或主窗口已有待办返回链路。
- 当前可见待办看板且来源为 `todo_board` 时，允许继续走既有待办看板编辑链路。
- 若当前没有明确可见视图，可保留旧 `source_view` 作为兼容 fallback。
- 不改月日程 panel UI。
- 不改 MP-3 的 panel 生命周期。
- 不改保存后多视图刷新；该项留给 MP-5。

当前重点：

- `MainWindow._resolve_detail_edit_target(...)` 已存在，本轮必须先验证它是否已满足动态路由。
- `open_schedule_detail_from_month_panel(...)` 当前创建 `ScheduleDetailPop(source_view="month")`，并将编辑信号连接到 `go_to_*_picker_for_edit(data, "month")`。
- 如果 `_resolve_detail_edit_target(...)` 已能基于当前可见视图覆盖这个固定来源，本轮可不改源码，只记录“MP-4 无需源码修正”。
- 如果发现固定 `source_view` 仍会导致错误路由，只允许在 `MainWindow` 做最小修正。

## 2. 允许 / 禁止

允许修改：

- `src/ui/main_window.py`（仅在发现路由缺口时做最小修正）
- `src/ui/schedule_detail_pop.py`（仅限信号/参数兼容；原则上不改）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

禁止修改：

- `src/ui/popups/month_day_panel.py`
- `src/ui/month_window.py`
- `src/ui/dashboard.py`
- `src/ui/week_window.py`
- `src/ui/todo.py`
- `src/ui/todo_board.py`
- `src/controllers/`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/theme/`
- `src/utils/signals.py`
- `src/utils/styles.py`
- `assets/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `manage_instruction/Work_Instruction.md`
- `manage_instruction/Work_Formulation.md`
- `manage_instruction/Work_Snapshot.md`
- `manage_instruction/ReconstructionDolder/`

禁止事项：

- 不改数据库。
- 不写入 `schedule.db`。
- 不改保存逻辑。
- 不改 `ScheduleDetailPop` 的字段编辑业务逻辑。
- 不让 `ScheduleDetailPop` 直接调用 `MainWindow`、`MonthWindow`、`WeekWindow`、`DashboardView`、`TodoView` 或 `TodoBoardWindow`。
- 不把路由逻辑写进 `MonthDayPanel`。
- 不改 MP-3 的生命周期规则。
- 不新增协调器。
- 不提交 Git。

若开工前已有 diff，必须记录到 `Work_Log.md`，并区分是否为本轮产生。

## 3. 具体任务

### 3.1 开工前检查

运行：

~~~powershell
git status --short --branch
git diff --name-only
~~~

记录：

- 开工前 git 状态。
- 是否存在已有 diff。
- 已有 diff 是否与本轮有关。
- 不得回退或清理无关 diff。

### 3.2 读取基线

读取：

~~~powershell
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
Get-Content -Path src\ui\main_window.py -Encoding UTF8
Get-Content -Path src\ui\schedule_detail_pop.py -Encoding UTF8
Get-Content -Path src\ui\month_window.py -Encoding UTF8
Get-Content -Path src\ui\week_window.py -Encoding UTF8
Get-Content -Path src\ui\dashboard.py -Encoding UTF8
Get-Content -Path src\ui\todo.py -Encoding UTF8
Get-Content -Path src\ui\todo_board.py -Encoding UTF8
~~~

确认：

- 本轮只执行 MP-4，不执行 MP-5。
- `ScheduleDetailPop` 是否仍只发 `req_edit_time` / `req_edit_alarm` / `req_edit_list` 信号。
- `ScheduleDetailPop` 是否直接调用具体页面。
- `MainWindow._resolve_detail_edit_target(...)` 当前判断顺序。
- `MainWindow.go_to_time_picker_for_edit(...)`、`go_to_alarm_picker_for_edit(...)`、`go_to_list_picker_for_edit(...)` 当前是否都调用 `_resolve_detail_edit_target(...)`。
- `MonthWindow` 是否已有 `go_to_time_picker_for_edit(...)` / `go_to_alarm_picker_for_edit(...)` / `go_to_list_picker_for_edit(...)`。
- `WeekWindow` 是否已有对应 edit picker 入口。
- `TodoBoardWindow` 是否仍有既有待办看板 list picker edit 入口。
- 月 panel 详情桥接是否仍在 `MainWindow.open_schedule_detail_from_month_panel(...)`。

### 3.3 优先做无代码验证

先不改源码，验证现有动态路由是否满足 MP-4。

重点判断：

- 当 `month_window.isVisible()` 为 True 时，编辑请求是否路由到 month。
- 当 `week_window.isVisible()` 为 True 时，编辑请求是否路由到 week。
- 当主窗口可见且当前是日视图时，编辑请求是否路由到 day。
- 当主窗口可见且当前是待办视图时，编辑请求是否路由到 todo 或既有待办返回链路。
- 当来源为 `todo_board` 且待办看板可见时，是否保留既有 `todo_board` 路由。
- 从月 panel 打开的详情弹窗，即使连接时传入 `source_view="month"`，在月界面隐藏、主窗口日视图可见后，是否会路由到 day。
- 从月 panel 打开的详情弹窗，在周界面可见后，是否会路由到 week。

如果全部通过：

- 不修改源码。
- 在 `Work_Log.md` 记录“MP-4 无需源码修正，现有 `_resolve_detail_edit_target(...)` 已满足当前动态路由要求”。

如果发现缺口：

- 只允许最小修改 `src/ui/main_window.py`。
- 优先修正 `_resolve_detail_edit_target(...)` 或月 panel 详情桥接传参方式。
- 不新建协调器。
- 不改 `ScheduleDetailPop`，除非确实必须补信号参数兼容。
- 不改具体页面业务逻辑。
- 不改 MP-5 范围的保存后刷新。

### 3.4 如需源码修正的边界

若必须改 `src/ui/main_window.py`，要求：

- 保持 `_resolve_detail_edit_target(...)` 为唯一主要路由决策点。
- 保持 `source_view` 只作为 fallback，不作为当前可见视图的优先决策。
- 不改变 `go_to_*_picker_for_edit(...)` 对外方法名和参数兼容。
- 不改 `open_schedule_detail_from_month_panel(...)` 的弹窗创建和 owner panel 生命周期逻辑，除非其传参导致路由错误。
- 不改 Dashboard / Week / Month / Todo / TodoBoard 具体页面。
- 不改 MP-5 范围的保存后刷新。

### 3.5 更新 Work_Log.md

在 `manage_instruction/Work_Log.md` 追加记录，至少包含：

- 本轮任务名称：`MP-4（详情编辑请求按当前可见视图路由）`
- 开工前 git 状态
- 开工前是否已有 diff
- 实际修改文件
- 是否修改源码；如果未改，明确记录“无需源码修正”
- `ScheduleDetailPop` 信号边界检查结果
- `_resolve_detail_edit_target(...)` 判断顺序检查结果
- time/alarm/list 三类编辑请求路由验证结果
- 月 panel 详情弹窗固定 `source_view="month"` 是否会锁死路由
- day/week/month/todo/todo_board 路由验证结果
- 是否未改 MP-3 生命周期
- 验证命令和结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

## 4. 验收命令

### 4.1 静态定位

~~~powershell
rg -n "def _resolve_detail_edit_target|go_to_time_picker_for_edit|go_to_alarm_picker_for_edit|go_to_list_picker_for_edit|open_schedule_detail_from_month_panel|source_view|ScheduleDetailPop|req_edit_time|req_edit_alarm|req_edit_list" src/ui/main_window.py src/ui/schedule_detail_pop.py
rg -n "go_to_time_picker_for_edit|go_to_alarm_picker_for_edit|go_to_list_picker_for_edit" src/ui/month_window.py src/ui/week_window.py src/ui/todo_board.py
rg -n "req_edit_time|req_edit_alarm|req_edit_list|_show_detail_popup|ScheduleDetailPop" src/ui/dashboard.py src/ui/todo.py
~~~

预期：

- `ScheduleDetailPop` 只发信号，不直接调用具体页面。
- `MainWindow.go_to_time_picker_for_edit(...)` 调用 `_resolve_detail_edit_target(...)`。
- `MainWindow.go_to_alarm_picker_for_edit(...)` 调用 `_resolve_detail_edit_target(...)`。
- `MainWindow.go_to_list_picker_for_edit(...)` 调用 `_resolve_detail_edit_target(...)`。
- `MonthWindow` 和 `WeekWindow` 仍有对应 edit picker 入口。
- `todo_board` 相关既有入口若被定位到，只记录现状，不在本轮扩展。

### 4.2 import 验证

~~~powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.main_window import MainWindow; from src.ui.schedule_detail_pop import ScheduleDetailPop; from src.ui.month_window import MonthWindow; from src.ui.week_window import WeekWindow; print('mp4 imports ok', MainWindow, ScheduleDetailPop, MonthWindow, WeekWindow)"
~~~

### 4.3 直接验证 _resolve_detail_edit_target 判断

~~~powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); w.show(); app.processEvents(); print('day target', w._resolve_detail_edit_target('month')); assert w._resolve_detail_edit_target('month') == 'day'; w.month_window.show(); app.processEvents(); print('month target', w._resolve_detail_edit_target('dashboard')); assert w._resolve_detail_edit_target('dashboard') == 'month'; w.month_window.hide(); w.week_window.show(); app.processEvents(); print('week target', w._resolve_detail_edit_target('month')); assert w._resolve_detail_edit_target('month') == 'week'; w.week_window.hide(); w.body_stack.setCurrentWidget(w.page_todo); w.show(); app.processEvents(); print('todo target', w._resolve_detail_edit_target('dashboard')); assert w._resolve_detail_edit_target('dashboard') == 'todo'"
~~~

### 4.4 time 编辑请求路由 smoke

使用 monkeypatch，不写数据库，不打开真实 picker：

~~~powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from types import SimpleNamespace; from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); s=SimpleNamespace(id=1, title='mp4', start_time=None, end_time=None); hits=[]; w.week_window.go_to_time_picker_for_edit=lambda data: hits.append(('week', data)); w.month_window.go_to_time_picker_for_edit=lambda data: hits.append(('month', data)); w.month_window.show(); app.processEvents(); w.go_to_time_picker_for_edit(s, 'dashboard'); assert hits[-1][0]=='month'; w.month_window.hide(); w.week_window.show(); app.processEvents(); w.go_to_time_picker_for_edit(s, 'month'); assert hits[-1][0]=='week'; w.week_window.hide(); w.show(); app.processEvents(); w.go_to_time_picker_for_edit(s, 'month'); assert w.time_picker_mode == 'edit'; print('time route ok', hits)"
~~~

### 4.5 alarm 编辑请求路由 smoke

~~~powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from types import SimpleNamespace; from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); s=SimpleNamespace(id=1, title='mp4', start_time=None, end_time=None, is_alarm=False, alarm_duration=0); hits=[]; w.week_window.go_to_alarm_picker_for_edit=lambda data: hits.append(('week', data)); w.month_window.go_to_alarm_picker_for_edit=lambda data: hits.append(('month', data)); w.month_window.show(); app.processEvents(); w.go_to_alarm_picker_for_edit(s, 'dashboard'); assert hits[-1][0]=='month'; w.month_window.hide(); w.week_window.show(); app.processEvents(); w.go_to_alarm_picker_for_edit(s, 'month'); assert hits[-1][0]=='week'; w.week_window.hide(); w.show(); app.processEvents(); w.go_to_alarm_picker_for_edit(s, 'month'); assert w.alarm_picker_mode == 'edit'; print('alarm route ok', hits)"
~~~

### 4.6 list 编辑请求路由 smoke

~~~powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from types import SimpleNamespace; from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); s=SimpleNamespace(id=1, title='mp4', category_id=None, item_type='schedule'); hits=[]; w.week_window.go_to_list_picker_for_edit=lambda data: hits.append(('week', data)); w.month_window.go_to_list_picker_for_edit=lambda data: hits.append(('month', data)); w.month_window.show(); app.processEvents(); w.go_to_list_picker_for_edit(s, 'dashboard'); assert hits[-1][0]=='month'; w.month_window.hide(); w.week_window.show(); app.processEvents(); w.go_to_list_picker_for_edit(s, 'month'); assert hits[-1][0]=='week'; w.week_window.hide(); w.body_stack.setCurrentWidget(w.page_todo); w.show(); app.processEvents(); w.go_to_list_picker_for_edit(s, 'month'); assert getattr(w, 'list_picker_source', None) == 'todo'; print('list route ok', hits, getattr(w, 'list_picker_source', None))"
~~~

### 4.7 月 panel 详情弹窗固定 source_view 不锁死路由验证

验证从月 panel 打开的 popup 在切换到 day/week 后仍按当前可见视图路由。

~~~powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from datetime import datetime; from types import SimpleNamespace; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.main_window import MainWindow; from src.ui.popups.month_day_panel import MonthDayPanel; app=QApplication([]); w=MainWindow(); panel=MonthDayPanel(QDate.currentDate(), []); s=SimpleNamespace(id=77, title='mp4 month popup', description='', start_time=None, end_time=None, priority=0, status=0, item_type='schedule', category_id=None, is_alarm=False, alarm_duration=0, reminder_time=None, repeat_rule='无', created_at=datetime.now()); pop=w.open_schedule_detail_from_month_panel(s, panel); assert pop.source_view == 'month'; hits=[]; w.week_window.go_to_time_picker_for_edit=lambda data: hits.append(('week', data)); w.month_window.hide(); w.week_window.hide(); w.show(); app.processEvents(); pop.req_edit_time.emit(s); assert w.time_picker_mode == 'edit'; w.week_window.show(); app.processEvents(); pop.req_edit_time.emit(s); assert hits[-1][0] == 'week'; print('month popup dynamic route ok', hits); panel.close()"
~~~

### 4.8 禁止范围检查

~~~powershell
git diff --name-only -- src/ui/popups/month_day_panel.py
git diff --name-only -- src/ui/month_window.py
git diff --name-only -- src/ui/dashboard.py
git diff --name-only -- src/ui/week_window.py
git diff --name-only -- src/ui/todo.py
git diff --name-only -- src/ui/todo_board.py
git diff --name-only -- src/controllers
git diff --name-only -- src/data
git diff --name-only -- src/repositories
git diff --name-only -- src/services
git diff --name-only -- src/theme
git diff --name-only -- src/utils/signals.py
git diff --name-only -- src/utils/styles.py
git diff --name-only -- assets
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
~~~

预期：

- 如果现有路由已满足，本轮源码应无 diff。
- 如果确需修正，原则上只允许 `src/ui/main_window.py` 出现 diff。
- `schedule.db` 必须无 diff。

### 4.9 语法检查

~~~powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/main_window.py src/ui/schedule_detail_pop.py src/ui/month_window.py src/ui/week_window.py main.py
~~~

### 4.10 总范围检查

~~~powershell
git diff --check
git diff --name-only
git status --short --branch
~~~

预期：

- `git diff --check` 无 whitespace error；LF/CRLF warning 可记录。
- 如无需源码修正，最终只允许：
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`
- 如需要源码修正，最终只允许：
  - `src/ui/main_window.py`
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. Work_Task_Prompts.md 处理要求

如需要维护复核锚点，可将当前状态更新为：

~~~text
MP-4 已执行，等待决策/顾问窗口复核。
下一步候选：MP-5。
~~~

不得在本轮自行写入 `MP-5` 的执行提示词。

## 6. 完成后要求

完成后不要提交 Git，等待决策/顾问窗口复核。
