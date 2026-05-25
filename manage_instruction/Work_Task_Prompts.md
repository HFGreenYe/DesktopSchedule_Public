请执行第六轮 6-7：详情弹窗与跨视图刷新回流复核。本轮只做静态审查、代码阅读、搜索和日志记录，不改源码。

## 1. 本轮目标

基于 Work_Instruction.md 第六轮阶段合同，以及 Work_Log.md 中 6-0 ~ 6-6 的结论，复核详情弹窗打开、编辑、删除、关闭后的刷新回流链路。

本轮目标：

- 记录 Dashboard 详情弹窗刷新行为。
- 记录 TodoView 详情弹窗刷新行为。
- 记录 WeekWindow 打开 Dashboard 详情弹窗的路径。
- 记录 TodoBoardWindow 借道 Dashboard 打开详情弹窗的路径。
- 记录 ScheduleDetailPop 内部 schedule_updated 发射点。
- 标记哪些回流适合后续接入 RefreshCoordinator。
- 标记哪些回流应推迟到第八轮 UI 拆分或另拆工单。
- 不做源码修改。
- 不做 EventBus 接入。
- 不改详情弹窗行为。

本轮是复核与决策基线，不是改造工单。

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

- 不修改 DashboardView。
- 不修改 TodoView。
- 不修改 TodoBoardWindow。
- 不修改 WeekWindow。
- 不修改 MainWindow。
- 不修改 ScheduleDetailPop。
- 不修改 controller。
- 不修改 signals.py。
- 不新增 EventBus 信号。
- 不连接 refresh_requested。
- 不改变任何弹窗打开、编辑、删除、刷新、关闭行为。
- 不写数据库。
- 不提交 Git。

若开工前已有管理文档 diff，需要在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取阶段合同和 6-0 ~ 6-6 日志：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8

    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8

2. 定位详情弹窗相关代码：

    rg -n "_show_detail_popup|request_schedule_detail|req_show_detail|schedule_updated|ScheduleDetailPop|source_view|req_edit_time|req_edit_alarm|req_edit_list|req_refresh_all|refresh_requested" src/ui/dashboard.py src/ui/todo.py src/ui/todo_board.py src/ui/week_window.py src/ui/main_window.py src/ui/schedule_detail_pop.py

3. 读取 Dashboard 详情弹窗打开与回流代码片段：

    Get-Content -Path src\ui\dashboard.py -Encoding UTF8 | Select-Object -Skip 500 -First 90

4. 读取 TodoView 详情弹窗打开与回流代码片段：

    Get-Content -Path src\ui\todo.py -Encoding UTF8 | Select-Object -Skip 440 -First 80

5. 读取 WeekWindow 到 MainWindow 到 Dashboard 详情弹窗路径：

    Get-Content -Path src\ui\week_window.py -Encoding UTF8 | Select-Object -Skip 280 -First 40

    Get-Content -Path src\ui\week_window.py -Encoding UTF8 | Select-Object -Skip 1020 -First 40

    Get-Content -Path src\ui\main_window.py -Encoding UTF8 | Select-Object -Skip 80 -First 30

6. 读取 TodoBoardWindow 借道 Dashboard 详情弹窗路径：

    Get-Content -Path src\ui\todo_board.py -Encoding UTF8 | Select-Object -Skip 1210 -First 50

    Get-Content -Path src\ui\todo_board.py -Encoding UTF8 | Select-Object -Skip 1840 -First 80

7. 读取 ScheduleDetailPop 的 source_view 与 schedule_updated 发射点：

    Get-Content -Path src\ui\schedule_detail_pop.py -Encoding UTF8 | Select-Object -Skip 90 -First 110

    rg -n "source_view|schedule_updated\\.emit|req_edit_time|req_edit_alarm|req_edit_list|delete|soft|hard|update|refresh" src/ui/schedule_detail_pop.py

8. 形成详情弹窗打开来源地图，至少记录：

- Dashboard 卡片 -> DashboardView._show_detail_popup(source_view="dashboard")
- TodoView 卡片 -> TodoView._show_detail_popup(source_view="todo")
- WeekWindow 卡片 -> request_schedule_detail -> MainWindow lambda -> DashboardView._show_detail_popup(source_view="week")
- TodoBoardWindow 卡片 -> TodoBoardWindow._show_detail_popup -> main_win.page_dashboard._show_detail_popup(source_view="todo_board")

9. 形成详情弹窗更新回流地图，至少记录：

- Dashboard 弹窗 schedule_updated 后触发：
  - DashboardView.refresh_data
  - DashboardView.req_refresh_all.emit
- TodoView 弹窗 schedule_updated 后触发：
  - TodoView.refresh_data
  - TodoView.req_refresh_all.emit
- Week 来源弹窗更新后是否借助 Dashboard 的 req_refresh_all 回流到主窗口/周视图。
- TodoBoard 来源弹窗更新后是否借助 Dashboard 的 req_refresh_all 及 TodoBoard 既有父级连接回流。
- ScheduleDetailPop 中不同操作触发 schedule_updated.emit 的位置和语义。

10. 形成 edit picker 回流地图，至少记录：

- ScheduleDetailPop.req_edit_time -> DashboardView.req_edit_time -> MainWindow.go_to_time_picker_for_edit(source_view)
- ScheduleDetailPop.req_edit_alarm -> DashboardView.req_edit_alarm -> MainWindow.go_to_alarm_picker_for_edit(source_view)
- ScheduleDetailPop.req_edit_list -> DashboardView/TodoView req_edit_list -> MainWindow.go_to_list_picker_for_edit(source_view)
- source_view 为 week/todo_board 时 MainWindow 当前分支如何处理。

11. 标记直接耦合点：

- WeekWindow 通过 MainWindow lambda 借 Dashboard 打开弹窗。
- TodoBoardWindow 直接调用 main_win.page_dashboard._show_detail_popup。
- Dashboard/Todo 的弹窗回流直接连接本视图 refresh 与 req_refresh_all。
- ScheduleDetailPop 内部通过 source_view 改变 UI/行为。
- req_refresh_all 和 refresh_requested 当前是否有重复或并行风险。

12. 标记风险等级：

- 低风险：
  - 纯记录弹窗来源与 source_view 字符串映射。
  - 只把“弹窗更新后刷新目标”注册到 RefreshCoordinator 的未来候选。
- 中风险：
  - Dashboard/Todo 的 schedule_updated 回流改为 RefreshCoordinator 协调。
  - Week 来源弹窗更新后统一走 MainWindow 刷新协调。
- 高风险：
  - TodoBoardWindow 详情弹窗借道 Dashboard 的路径迁移。
  - ScheduleDetailPop source_view 行为重构。
  - 弹窗编辑 picker 回流迁移。
  - 弹窗删除/恢复/重复日程相关更新路径迁移。

13. 输出后续建议：

- 是否建议在第六轮继续做详情弹窗源码接管。
- 如果建议继续，必须说明最小候选项。
- 如果不建议继续，说明应留到第八轮 UI 拆分或单独工单。
- 明确 6-8 整体验收前需要保留哪些回归重点。

## 4. 验收命令

完成审查和日志记录后执行范围检查：

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
- 如果开工前已有管理文档 diff，需要在日志中明确说明它是开工前既有状态，不属于 6-7 执行改动。

## 5. 日志要求

更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第六轮 6-7（详情弹窗与跨视图刷新回流复核）
- 开工前 git 状态
- 实际修改文件
- 读取的阶段合同和 6-0 ~ 6-6 结论
- 静态搜索命令和关键结果
- 详情弹窗打开来源地图
- 详情弹窗更新回流地图
- edit picker 回流地图
- ScheduleDetailPop 中 schedule_updated.emit 发射点
- source_view 当前语义
- 直接耦合点
- 风险等级
- 适合后续接入 RefreshCoordinator 的候选项
- 应推迟到第八轮 UI 拆分或另拆工单的项
- 是否建议第六轮继续做详情弹窗源码接管
- 6-8 整体验收前需要重点回归的弹窗行为
- diff 范围检查结果
- 未完成事项
- 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
