# Work Log

本文件只记录当前阶段/当前轮次的执行日志。

历史日志已归档到 `manage_instruction/History_Log.md`。

## 当前状态

第一轮：基建 + repository + db_manager 兼容委托，已完成并归档。

第二轮：Data 层整理与模型拆分，已完成并归档。

第三轮：纯业务查询与排序服务，已完成并归档。

第四轮：日程写入与重复规则服务，已完成并归档。

第五轮：提醒与运行期状态服务，已完成并归档。

第六轮：Controller / Router / EventBus 协调层，已启动。

当前已完成 6-0（静态审查与跨视图耦合定位），等待顾问窗口复核与后续 6-1 小工单发布。

## 当前轮次注意事项

- 6-0 只做静态审查和耦合定位，不做源码改造。
- 后续第六轮改造需按小工单逐步迁移，不得一次性重构 `MainWindow`/`WeekWindow`/`TodoBoardWindow`。
- 在未收到后续正式提示词前，不得自行开始 6-1 及之后的实现改造。

## 2026-05-25 第六轮 6-0（静态审查与跨视图耦合定位）

- 本轮任务名称：第六轮 6-0（静态审查与跨视图耦合定位）。
- 开工前 git 状态：
  - `git status --short --branch` -> `## main...temp/main`，`M manage_instruction/Work_Task_Prompts.md`。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`。
  - 结论：开工前已有管理文档 diff（`Work_Task_Prompts.md`），不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`

### 读取的阶段合同结论

- 第六轮目标是“跨视图协调层接管”，不是 UI 大拆分。
- 第六轮首工单 `6-0` 仅做静态审查与耦合定位。
- 默认不改 UI，不改数据层，不改 `db_manager` API。
- 重点是为后续 `MainController` / `ViewRouter` / `RefreshCoordinator` 建立迁移基线。

### 静态搜索命令与关键结果

- `Get-Content manage_instruction/Work_Instruction.md`：确认第六轮合同与小工单拆分。
- `Get-Content src/utils/signals.py`：确认 `global_signals` 当前信号集。
- `rg ... src/ui/main_window.py`：命中 `switch_view`、`source_view_for_add`、picker 模式状态、跨视图刷新直连、周/月窗口 show/hide。
- `rg ... src/ui/week_window.py`：命中内部 `body_stack` 路由、picker 返回链、`schedule_updated/request_schedule_detail/view_selected/restore/suspend` 信号。
- `rg ... src/ui/month_window.py`：命中 `view_selected/date_selected/restore/suspend`。
- `rg ... src/ui/todo.py`：命中 `req_refresh_all`、详情弹窗回流、跨视图刷新发射。
- `rg ... src/ui/todo_board.py`：命中 `view_stack` 内部路由、picker 返回、`window()/parent` 直接调用主窗口子页面、详情弹窗借道 dashboard、清单删除策略分支。
- `rg ... src/ui`：确认跨文件强耦合主要集中在 `main_window.py` 与 `todo_board.py`。
- `Get-ChildItem src/controllers` + `Get-Content src/controllers/__init__.py`：当前 controller 目录只有空 `__init__.py`，无协调层实现。

### global_signals 当前信号清单与缺口

- 当前信号：
  - `skin_changed()`（无参，兼容约束）
  - `theme_changed(str)`
  - `schedule_added(object)`
  - `schedule_updated(object)`
  - `schedule_deleted(int)`
  - `category_changed()`
- 缺口判断（面向第六轮协调）：
  - 缺少显式“视图路由请求”信号（如 view intent）。
  - 缺少“刷新域”信号（如 dashboard/todo/week/month 精确刷新域）。
  - 缺少“picker 返回结果”统一总线信号。
  - 缺少“详情弹窗回流完成”统一信号。
  - 结论：当前信号足够做兼容并行接入试点，但不足以完全替代跨窗口直连调用。

### 跨视图耦合地图

- 主视图切换链路：
  - `MainWindow.switch_view` 直接控制 `body_stack` 与 `WeekWindow`/`MonthWindow` show/hide/position。
  - 同时处理 dashboard/todo/week/month/suspend 路由状态。
- 添加页来源与返回链路：
  - `source_view_for_add` 存于 `MainWindow`，由当前页决定 add 返回目标。
  - `WeekWindow`、`TodoBoardWindow`存在各自内部 add/picker 逻辑，未统一。
- time/alarm/list picker add/edit 返回链路：
  - `MainWindow`：`time_picker_mode/alarm_picker_mode/list_picker_mode/list_picker_source` 决定返回页与写回目标。
  - `WeekWindow`：独立 `go_to_* / back_from_* / on_list_confirmed`。
  - `TodoBoardWindow`：独立 `view_stack` + list picker 返回。
- 日程/待办保存后的刷新链路：
  - `MainWindow`内多处直接 `page_dashboard.refresh_data()`、`page_todo.refresh_data()`、`_refresh_week_if_visible()`。
  - `WeekWindow.schedule_updated` 回传 `MainWindow` 后再触发 dashboard refresh。
- 清单新增/删除/修改后的刷新链路：
  - `TodoBoardWindow` 直接 `window().refresh_data()` + `notify_main_window_refresh()` + parent 页面直刷。
  - 删除策略逻辑与刷新调用在同文件聚合。
- 周/月/待办窗口与主窗口信号链路：
  - `WeekWindow`: `restore_requested/suspend_requested/view_selected/request_schedule_detail/schedule_updated`。
  - `MonthWindow`: `restore_requested/suspend_requested/view_selected/date_selected`。
  - `TodoView`: `req_change_view/req_refresh_all/req_edit_list`。
- 详情弹窗打开与更新后的刷新回流：
  - `WeekWindow.request_schedule_detail -> MainWindow -> Dashboard._show_detail_popup`。
  - `TodoBoardWindow._show_detail_popup` 直接借道 `main_win.page_dashboard._show_detail_popup(...)`。
  - `TodoView`、`DashboardView` 弹窗更新后分别直连本视图 refresh + `req_refresh_all`。
- 跨文件直接调用热点：
  - `todo_board.py` 中大量 `self.window()/parent/page_dashboard/page_todo` 直接操作。
  - `main_window.py` 承担路由、picker 状态、跨视图刷新和弹窗回流，职责过重。

### 耦合点风险等级

- 高风险：
  - `MainWindow.switch_view`（多窗口生命周期 + 位置控制 + 视图状态联动）。
  - `TodoBoardWindow` 对 `page_dashboard/page_todo` 的直接调用链。
  - 详情弹窗跨视图回流（week/todo_board -> dashboard popup -> 多视图刷新）。
  - picker add/edit 状态分散在 `MainWindow/WeekWindow/TodoBoardWindow`。
- 中风险：
  - `req_refresh_all` 广播式刷新（可能重复刷新但行为可回归）。
  - `WeekWindow.schedule_updated` 与 `MainWindow._on_week_schedule_updated` 联动。
  - 月视图 `date_selected` 跳转到 dashboard 的路径。
- 低风险：
  - 纯路由映射（view_name -> target view decision）本身。
  - refresh 目标注册表（不改触发时机，仅聚合调用）。
  - controller 空骨架与轻量 import 接入。

### 第六轮迁移建议分类

- 适合第六轮迁移：
  - `6-1` 先建 `MainController/ViewRouter/RefreshCoordinator` 最小骨架并保证可 import。
  - `6-2` 仅接管 `switch_view` 的“路由决策映射”，Qt 实际 show/hide 仍在 `MainWindow`。
  - `6-5` 建立 `RefreshCoordinator`，先聚合 refresh 目标，不改触发时机。
  - `6-6` 做单点 EventBus 并行通知试点，保留旧直连刷新链路。
- 需要先做行为基线再决定：
  - picker add/edit 返回状态接管（`source_view_for_add` + 三种 picker mode/source）。
  - 详情弹窗回流链路接管（week/todo_board 来源保持）。
  - TodoBoard 的清单操作后跨视图刷新顺序。
- 应推迟到第八轮 UI 拆分：
  - `TodoBoardWindow` 大文件结构拆分。
  - `MainWindow` 超长流程分段重排与方法分仓。
  - Week/Month/Todo 的大规模页面组织重构。
- 不应迁移或暂不迁移：
  - 旧 `global_signals.skin_changed` 签名与触发语义。
  - Data/Repository/Service 写入行为与 API 语义。
  - UI 布局、文案、交互流程。

### 是否需要后续补充 EventBus 信号

- 需要，但应分阶段补充：
  - 建议新增“路由请求”“刷新域请求”“picker 结果回流”“详情回流完成”四类兼容增强信号。
  - 仅并行接入，不替换旧信号签名和旧直连路径，避免一次性风险。

### diff 范围检查结果

- `git diff --name-only -- src` -> 无输出。
- `git diff --name-only -- main.py` -> 无输出。
- `git diff --name-only -- requirements.txt` -> 无输出。
- `git diff --name-only -- schedule.db` -> 无输出。
- `git diff --name-only` -> 写入本日志前仅 `manage_instruction/Work_Task_Prompts.md`；写入本日志后为 `manage_instruction/Work_Log.md`、`manage_instruction/Work_Task_Prompts.md`。
- `git status --short --branch` -> 写入本日志前仅 `M manage_instruction/Work_Task_Prompts.md`；写入本日志后另含 `M manage_instruction/Work_Log.md`。

### 未完成事项

- 待顾问窗口下发 `6-1` 正式提示词，确认 controller 骨架文件命名与最小职责边界。

### 风险或疑点

- `TodoBoardWindow` 当前对主窗口子页面的直接访问较多，迁移时必须保持刷新顺序与弹窗回流行为。
- `MainWindow` 同时处理路由、picker 状态和刷新协调，任何接管都需要小步验证并保留兜底旧路径。
