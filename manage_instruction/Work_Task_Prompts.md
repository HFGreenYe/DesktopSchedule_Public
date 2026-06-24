# Work Task Prompts

# 当前待执行提示词：MP-0

## MP-0：现状审查与路由边界定位

请执行 `MP-0：现状审查与路由边界定位`。本轮只做只读审查、代码搜索、边界分析和日志记录，不修改源码，不实现功能。

## 1. 本轮目标

基于当前项目状态、`manage_instruction/Final_Formulation.md` 和 `manage_instruction/Work_Instruction.md` 中的 MP 阶段合同，审查“月界面单击日程弹窗与详情编辑路由”相关代码边界，为后续 MP-1 ~ MP-5 提供准确依据。

重点输出：

- 月日程 panel 当前结构与生命周期。
- `ScheduleDetailPop` 当前打开、信号、编辑请求机制。
- `MainWindow` 当前详情编辑动态路由能力。
- `MonthWindow` 当前编辑 picker 链路能力。
- 保存后刷新链路。
- 普通视图切换、`hide/close`、双击跳日对 panel 生命周期的影响。
- MP-1 ~ MP-5 是否需要进一步拆分或收紧边界。

## 2. 允许 / 禁止

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

禁止修改：

- `src/`
- `assets/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `.env`
- `.gitignore`
- `manage_instruction/Work_Instruction.md`
- `manage_instruction/Work_Formulation.md`
- `manage_instruction/Work_Snapshot.md`
- `manage_instruction/ReconstructionDolder/`

禁止事项：

- 不改源码。
- 不新增 UI。
- 不创建新组件。
- 不接 `ScheduleDetailPop`。
- 不改编辑路由。
- 不改刷新链路。
- 不写数据库。
- 不提交 Git。

若开工前已有 diff，必须在 `Work_Log.md` 中记录，并区分是否属于本轮产生。

## 3. 具体任务

### 3.1 开工前状态检查

先运行：

```powershell
git status --short --branch
git diff --name-only
```

要求：

- 记录开工前 git 状态。
- 若已有 diff，记录具体文件，并说明这些 diff 不视为本轮源码问题。
- 本轮不得清理、回退或改动开工前已有源码 diff。

### 3.2 读取阶段合同与当前日志

读取：

```powershell
Get-Content -Path manage_instruction\Final_Formulation.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
```

确认：

- 当前阶段为 `MP：月界面单击日程弹窗与详情编辑路由`。
- 本轮只执行 `MP-0`。
- 不执行 `MP-1 ~ MP-5`。
- 不修改 `src/`。

### 3.3 审查月界面 panel 生命周期

重点审查：

- `src/ui/month_window.py`
- `src/ui/popups/month_day_panel.py`

定位：

- `MonthDayPanel` 当前 UI 结构。
- `MonthDayPanel` 是否已持有日程列表。
- panel 打开方法：
  - `_open_day_panel(...)`
  - `_find_open_day_panel(...)`
  - `_get_day_panel_position(...)`
- panel 关闭方法：
  - `close_day_panels(...)`
  - `_remove_day_panel(...)`
- `open_day_panels` 如何维护。
- 同一天重复单击是否复用 panel。
- `hideEvent(...) / closeEvent(...)` 是否清理 panel。
- 普通视图切换是否会触发 `MonthWindow.hide()`。
- 双击/activated 跳日是否调用 `close_day_panels()`。

必须特别判断：

- 当前代码中“视图切换不关闭 panel”和“hide/close 清理 panel”是否存在实现冲突。
- 后续 MP-3 是否需要先确认产品规则再改代码。

### 3.4 审查 ScheduleDetailPop 当前机制

重点审查：

- `src/ui/schedule_detail_pop.py`
- `src/ui/dashboard.py`
- `src/ui/week_window.py`
- `src/ui/todo.py`
- `src/ui/todo_board.py`
- `src/ui/main_window.py`

定位：

- `ScheduleDetailPop` 构造参数。
- 是否存在 `source_view`。
- 当前详情弹窗有哪些信号：
  - 修改时间
  - 修改提醒
  - 修改清单
  - 删除
  - 状态变更
  - 刷新
- `ScheduleDetailPop` 是否直接调用具体页面。
- 日视图 / 周视图 / 待办视图当前如何打开详情弹窗。
- 是否已有复用 / 防重复打开逻辑。
- 详情弹窗关闭时是否有生命周期信号可供父 panel 解绑。

### 3.5 审查 MainWindow 动态编辑路由

重点审查：

- `src/ui/main_window.py`
- `src/controllers/`

必须定位：

- `_resolve_detail_edit_target(...)` 是否存在。
- 该方法是否按当前可见视图动态判断。
- 当前可见视图的判断来源是什么。
- 当前详情编辑请求是否已由 `MainWindow` 统一承接。
- `go_to_time_picker_for_edit(...)`
- `go_to_alarm_picker_for_edit(...)`
- `go_to_list_picker_for_edit(...)`
- 删除 / 状态修改 / 刷新请求当前如何分发。

必须判断：

- 现有 `_resolve_detail_edit_target(...)` 是否已满足 MP-4 的动态编辑路由要求。
- MP-4 应该是“补缺口 + 验收”，还是确实需要重构。
- 是否存在 `source_view` 固定绑定仍会影响编辑路由。

### 3.6 审查 MonthWindow 编辑承接能力

重点审查：

- `src/ui/month_window.py`

定位：

- 是否已有：
  - `go_to_time_picker_for_edit(...)`
  - `go_to_alarm_picker_for_edit(...)`
  - `go_to_list_picker_for_edit(...)`
- 月界面是否能承接详情弹窗的编辑请求。
- 月界面 time/alarm/list picker 当前是否只服务添加，还是也支持编辑。
- 如果缺少编辑承接能力，记录缺口，不要修改。

必须判断：

- 当前可见月界面时，MP-4 是否应优先走 `MonthWindow` 编辑 picker 链路。
- 哪些编辑类型已具备基础能力。
- 哪些编辑类型需要后续新增或暂停确认。

### 3.7 审查保存后刷新链路

重点审查：

- `src/ui/main_window.py`
- `src/ui/month_window.py`
- `src/ui/dashboard.py`
- `src/ui/week_window.py`
- `src/ui/todo.py`
- `src/ui/todo_board.py`

定位：

- 月界面 marker 刷新方法：
  - `_build_schedule_marker_cache(...)`
  - `_build_hover_schedule_cache(...)`
  - `_refresh_schedule_marker_cache(...)`
- 月日程 panel 列表后续如何刷新。
- hover cache 如何刷新。
- 日视图刷新入口。
- 周视图刷新入口。
- 待办刷新入口。
- 主窗口是否已有统一 refresh / refresh_all / signal 链路。
- 保存后详情弹窗是否需要刷新自身数据，或关闭/重开。

### 3.8 输出 MP-1 ~ MP-5 执行建议

基于审查结果，输出建议：

- MP-1 是否可以只做 panel UI 和列表展示。
- MP-2 是否需要最小改 `MainWindow` 做详情弹窗桥接。
- MP-3 生命周期规则是否存在产品冲突。
- MP-4 动态编辑路由是否已有基础，是否只需补缺口。
- MP-5 刷新链路应复用哪些入口。
- 哪些任务需要继续拆成 `MP-4a / MP-4b` 等更小工单。

### 3.9 更新 Work_Log.md

在 `manage_instruction/Work_Log.md` 追加记录，至少包含：

- 本轮任务名称：`MP-0（现状审查与路由边界定位）`
- 开工前 git 状态。
- 实际修改文件。
- 是否存在开工前 diff。
- 月日程 panel 生命周期审查结论。
- `ScheduleDetailPop` 信号与 `source_view` 审查结论。
- `MainWindow._resolve_detail_edit_target(...)` 审查结论。
- `MonthWindow` 编辑承接能力审查结论。
- 保存后刷新链路审查结论。
- 普通视图切换 / hide / close / 双击跳日生命周期冲突判断。
- MP-1 ~ MP-5 建议。
- 不适合本阶段处理的事项。
- diff 范围检查结果。
- 未完成事项。
- 风险或疑点。

## 4. 建议搜索命令

### 4.1 月 panel 生命周期

```powershell
rg -n "MonthDayPanel|open_day_panels|_open_day_panel|_find_open_day_panel|_remove_day_panel|close_day_panels|hideEvent|closeEvent|_on_calendar_date_clicked|_on_calendar_date_activated|date_selected.emit|view_selected.emit|context_menu_date|_handle_context_view" src/ui/month_window.py src/ui/popups/month_day_panel.py
```

### 4.2 ScheduleDetailPop 机制

```powershell
rg -n "class ScheduleDetailPop|source_view|pyqtSignal|req_|emit|closeEvent|delete|status|time|alarm|list|refresh|ScheduleDetailPop\(" src/ui/schedule_detail_pop.py src/ui/dashboard.py src/ui/week_window.py src/ui/todo.py src/ui/todo_board.py src/ui/main_window.py
```

### 4.3 MainWindow 动态路由

```powershell
rg -n "_resolve_detail_edit_target|current_view|switch_view|go_to_time_picker_for_edit|go_to_alarm_picker_for_edit|go_to_list_picker_for_edit|req_edit_time|req_edit_alarm|req_edit_list|source_view|page_dashboard|week_window|month_window|todo_board" src/ui/main_window.py src/ui/schedule_detail_pop.py src/ui/dashboard.py src/ui/week_window.py src/ui/month_window.py src/ui/todo.py src/ui/todo_board.py src/controllers
```

### 4.4 MonthWindow 编辑承接

```powershell
rg -n "go_to_time_picker_for_edit|go_to_alarm_picker_for_edit|go_to_list_picker_for_edit|editing_schedule|update_schedule_with_repeat|on_time_confirmed|on_alarm_confirmed|on_list_confirmed|page_time|page_alarm|page_list" src/ui/month_window.py
```

### 4.5 刷新链路

```powershell
rg -n "_refresh_schedule_marker_cache|_build_schedule_marker_cache|_build_hover_schedule_cache|refresh_data|refresh|req_refresh|req_refresh_all|global_signals|schedule_updated|schedule_deleted|_on_schedule_saved|on_time_confirmed|on_alarm_confirmed|on_list_confirmed" src/ui/main_window.py src/ui/month_window.py src/ui/dashboard.py src/ui/week_window.py src/ui/todo.py src/ui/todo_board.py src/utils/signals.py src/controllers
```

## 5. 验收命令

### 5.1 import / 静态 smoke

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.month_window import MonthWindow; from src.ui.popups.month_day_panel import MonthDayPanel; from src.ui.schedule_detail_pop import ScheduleDetailPop; from src.ui.main_window import MainWindow; print('mp0 imports ok', MonthWindow, MonthDayPanel, ScheduleDetailPop, MainWindow)"
```

如果 `.venv` Python 因本地解释器路径失效、沙箱或环境问题无法运行，不要改源码；必须在 `Work_Log.md` 记录失败命令、失败原因和“需用户本地 CMD/PowerShell 复跑”的说明。

### 5.2 禁止范围检查

```powershell
git diff --name-only -- src
git diff --name-only -- assets
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
```

预期无输出。若开工前已有源码 diff，必须记录为开工前 diff，不得误报为本轮产生。

### 5.3 总范围检查

```powershell
git diff --check
git diff --name-only
git status --short --branch
```

预期最终只允许：

```text
manage_instruction/Work_Log.md
manage_instruction/Work_Task_Prompts.md
```

其中 `Work_Task_Prompts.md` 仅在维护复核锚点时允许修改。

## 6. Work_Task_Prompts.md 处理要求

如需要维护复核锚点，可将当前状态更新为：

```text
MP-0 已执行，等待决策/顾问窗口复核。
下一步候选：MP-1。
```

不得在本轮自行写入 `MP-1` 的执行提示词。

## 7. 完成后要求

完成后不要提交 Git，等待决策/顾问窗口复核。
