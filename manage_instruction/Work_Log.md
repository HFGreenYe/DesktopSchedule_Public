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

当前已完成 6-4（添加页来源与 picker 返回状态最小接管），等待顾问窗口复核与后续 6-5 小工单发布。

## 当前轮次注意事项

- 6-4 仅接管 MainWindow `source_view_for_add` 闭环纯决策，不迁移任何 picker 逻辑。
- 后续第六轮改造需按小工单逐步迁移，不得一次性重构 `MainWindow`/`WeekWindow`/`TodoBoardWindow`。
- 在未收到后续正式提示词前，不得自行开始 6-5 及之后的实现改造。

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

## 2026-05-25 第六轮 6-1（Controller / Router / Coordinator 最小骨架）

- 本轮任务名称：第六轮 6-1（Controller / Router / Coordinator 最小骨架）。
- 开工前 git 状态：
  - `git status --short --branch` -> `## main...temp/main [ahead 1]`，`M manage_instruction/Work_Task_Prompts.md`。
  - 结论：开工前已有管理文档 diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/controllers/__init__.py`
  - `src/controllers/main_controller.py`
  - `src/controllers/view_router.py`
  - `src/controllers/refresh_coordinator.py`
  - `manage_instruction/Work_Log.md`
- 新增或完善的 controller 文件：
  - `src/controllers/main_controller.py`
  - `src/controllers/view_router.py`
  - `src/controllers/refresh_coordinator.py`
- MainController 当前职责边界：
  - 只组合 `ViewRouter` 与 `RefreshCoordinator`。
  - 仅提供视图名归一化/判断与刷新回调触发代理方法。
  - 不持有具体 UI 实例，不执行 Qt 路由操作，不写数据库。
- ViewRouter 当前职责边界：
  - 只做视图名纯判断与归一化（`day/week/month/todo`）。
  - 提供 `normalize_view_name / is_known_view / resolve_or_default`。
  - 不涉及 `show/hide/setCurrentWidget` 或任何 QWidget 行为。
- RefreshCoordinator 当前职责边界：
  - 只做刷新回调注册、移除和显式触发。
  - 不自动连接 UI，不连接信号总线，不写数据库。
- `__init__.py` 导出说明：
  - 仅轻量导出 `MainController`、`ViewRouter`、`RefreshCoordinator`。
  - 无 UI 创建、无数据库连接、无信号连接副作用。

### 验证结果

- import 验证命令和结果：
  - 命令：
    - `python -c "from src.controllers.main_controller import MainController; from src.controllers.view_router import ViewRouter; from src.controllers.refresh_coordinator import RefreshCoordinator; import src.controllers as controllers; ..."`
  - 结果：
    - 输出 `controller imports ok`
    - `True True True True`
- py_compile 验证命令和结果：
  - 命令：
    - `python -m py_compile src/controllers/main_controller.py src/controllers/view_router.py src/controllers/refresh_coordinator.py src/controllers/__init__.py`
  - 结果：通过（无输出）。
- 静态依赖检查结果：
  - 命令：
    - `rg -n "QWidget|QStackedWidget|PyQt|PySide|MainWindow|WeekWindow|MonthWindow|TodoView|TodoBoard|db_manager|Repository|ScheduleRepository|CategoryRepository|add_schedule|update_schedule|delete_schedule|soft_delete|hard_delete" src/controllers`
  - 结果：无输出（退出码 1，视为通过）。

### 禁止范围检查

- `src/ui` 是否无 diff：
  - 是，`git diff --name-only -- src/ui` 无输出。
- `src/data` 是否无 diff：
  - 是，`git diff --name-only -- src/data` 无输出。
- `src/repositories` 是否无 diff：
  - 是，`git diff --name-only -- src/repositories` 无输出。
- `src/services` 是否无 diff：
  - 是，`git diff --name-only -- src/services` 无输出。
- `src/utils/signals.py` 是否无 diff：
  - 是，`git diff --name-only -- src/utils/signals.py` 无输出。
- `main.py`、`requirements.txt`、`schedule.db` 是否无 diff：
  - 是，三者 `git diff --name-only -- ...` 均无输出。

### 最终 diff 范围检查结果

- `git diff --name-only`（仅 tracked diff）：
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
  - `src/controllers/__init__.py`
  - 写入本日志后另含 `manage_instruction/Work_Log.md`
  - 注：`src/controllers/main_controller.py`、`src/controllers/refresh_coordinator.py`、`src/controllers/view_router.py` 为本轮新增未跟踪文件，需以 `git status --short --branch` 复核。
- `git status --short --branch`：
  - `## main...temp/main [ahead 1]`
  - `M manage_instruction/Work_Task_Prompts.md`
  - `M src/controllers/__init__.py`
  - `?? src/controllers/main_controller.py`
  - `?? src/controllers/refresh_coordinator.py`
  - `?? src/controllers/view_router.py`
  - 写入本日志后另含 `M manage_instruction/Work_Log.md`

### 未完成事项

- 待顾问窗口下发 `6-2` 正式提示词，决定是否接管 `switch_view` 的低风险路由决策映射。

### 风险或疑点

- 当前 controller 仅是边界骨架，尚未接入 UI，实际价值依赖后续小步接管工单。
- 后续接入时必须先保持旧路径并行，再逐步替换，避免跨窗口刷新顺序回归。

## 2026-05-25 第六轮 6-2（ViewRouter 视图切换基线与低风险接管）

- 本轮任务名称：第六轮 6-2（ViewRouter 视图切换基线与低风险接管）。
- 开工前 git 状态：
  - `git status --short --branch` 延续 6-1 收尾状态：`## main...temp/main [ahead 2]`，仅有 `M manage_instruction/Work_Task_Prompts.md` 作为开工前既有管理文档 diff。
  - 结论：开工前已有管理文档 diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/controllers/view_router.py`
  - `src/ui/main_window.py`
  - `manage_instruction/Work_Log.md`

### switch_view 旧行为基线

- `view_name == "week"`：
  - 主窗口 `hide()`
  - `week_window.refresh_week_data()`
  - 若有天气数据则 `week_window.update_weather_ui(...)`
  - 按主窗口中心计算位置后 `week_window.move(...); week_window.show()`
- `view_name == "month"`：
  - 主窗口 `hide()`
  - 若有天气数据则 `month_window.update_weather_ui(...)`
  - 按主窗口中心计算位置后 `month_window.move(...); month_window.show()`
- `view_name == "todo"`：
  - `body_stack.setCurrentWidget(self.page_todo)`
  - `page_todo.refresh_data()`
- `view_name == "day"`：
  - `body_stack.setCurrentWidget(self.page_dashboard)`
  - `page_dashboard.refresh_data()`
- `view_name == "priority"`：
  - `show_toast("准备切换至：四象限视图")`
- 未知 `view_name`：
  - `show_toast(f"准备切换至：{view_name}")`
- 从可见 `week_window` 切到非 week：
  - 主窗口移动到周视图中心后 `week_window.hide(); self.show()`
- 从可见 `month_window` 切到非 month：
  - 主窗口移动到月视图中心后 `month_window.hide(); self.show()`

### 本轮实现

- ViewRouter 新增方法名：
  - `classify_main_view(view_name)`
- 方法语义：
  - 仅精确匹配 `day/week/month/todo/priority`
  - 未知返回 `None`
  - 不做 `strip()`/`lower()`，保持 `switch_view` 旧分支匹配语义
- 为什么不直接使用 `normalize_view_name`：
  - `normalize_view_name` 会 `strip/lower`，会把 `" WEEK "`/`"Week"` 归一化，改变旧 `switch_view` 对未知输入的 toast 行为。
- MainWindow.switch_view 最小替换说明：
  - 新增 `route_action = ViewRouter.classify_main_view(view_name)`
  - 分支判断从 `view_name == ...` / `view_name != ...` 改为 `route_action == ...` / `route_action != ...`
  - Qt 操作代码（`hide/show/move/setCurrentWidget/refresh_data/refresh_week_data/update_weather_ui/show_toast`）全部保留在 `MainWindow`
  - 除 `switch_view` 处新增 `ViewRouter` import 外，无其他流程变更
- `priority` 分支是否保持原行为：
  - 是，仍为 `show_toast("准备切换至：四象限视图")`
- 未知 `view_name` 是否保持原 toast 行为：
  - 是，仍为 `show_toast(f"准备切换至：{view_name}")`

### 验证结果

- `py_compile` 验证结果：
  - 命令：`python -m py_compile src/controllers/view_router.py src/ui/main_window.py`
  - 结果：通过（无输出）
- ViewRouter 纯行为验证结果：
  - `day/week/month/todo/priority` 正确识别
  - `bad` 返回 `None`
  - `" WEEK "`、`"Week"` 返回 `None`
  - 结果：通过（输出 `view router exact switch behavior ok`）
- controller import 回归结果：
  - 命令通过，输出 `controller imports ok`
- MainWindow import 或兜底验证结果：
  - `from src.ui.main_window import MainWindow` 通过，输出 `main window import ok True`
- ViewRouter 静态依赖检查结果：
  - 命令：`rg -n "QWidget|QStackedWidget|PyQt|PySide|MainWindow|WeekWindow|MonthWindow|TodoView|TodoBoard|db_manager|Repository|ScheduleRepository|CategoryRepository" src/controllers/view_router.py`
  - 结果：无输出（退出码 1，视为通过）

### 禁止范围 diff 检查结果

- `src/ui/week_window.py`：无 diff
- `src/ui/month_window.py`：无 diff
- `src/ui/todo.py`：无 diff
- `src/ui/todo_board.py`：无 diff
- `src/data`：无 diff
- `src/repositories`：无 diff
- `src/services`：无 diff
- `src/utils/signals.py`：无 diff
- `main.py`：无 diff
- `requirements.txt`：无 diff
- `schedule.db`：无 tracked diff

### 最终 diff 范围检查结果

- `git diff --name-only`：
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
  - `src/controllers/view_router.py`
  - `src/ui/main_window.py`
  - 写入本日志后另含 `manage_instruction/Work_Log.md`
- `git status --short --branch`：
  - `## main...temp/main [ahead 2]`
  - `M manage_instruction/Work_Task_Prompts.md`
  - `M src/controllers/view_router.py`
  - `M src/ui/main_window.py`
  - 写入本日志后另含 `M manage_instruction/Work_Log.md`

### 未完成事项

- 待顾问窗口下发 `6-3` 正式提示词，进入 add/picker 返回状态基线审查。

### 风险或疑点

- `switch_view` 仍是多职责方法，本轮仅接管低风险字符串决策；后续若继续迁移需保持行为基线与回归用例。

## 2026-05-25 第六轮 6-3（添加页来源与 picker 返回状态基线）

- 本轮任务名称：第六轮 6-3（添加页来源与 picker 返回状态基线）。
- 开工前 git 状态：
  - `git status --short --branch` -> `## main...temp/main [ahead 3]`
  - 开工前既有 diff：`M manage_instruction/Work_Task_Prompts.md`
  - 结论：开工前已有管理文档 diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`

### 读取的阶段合同和 6-0/6-1/6-2 结论

- `6-3` 仅允许静态审查和日志记录，不改 `src`。
- 本轮需输出添加页来源与 picker 返回链路地图、状态字段写入/读取/返回目标表、风险等级和 6-4 建议。
- 延续 6-0/6-1/6-2 约束：不做跨窗口大迁移，不在 6-4 同时触碰 MainWindow/WeekWindow/TodoBoardWindow 全量链路。

### 静态搜索命令和关键结果

- MainWindow 添加页来源与返回：
  - `rg -n "source_view_for_add|page_add\\.btn_cancel|on_schedule_saved|handle_header_action|setCurrentWidget\\(self\\.page_add|return_target|page_add\\.reset|default_to_schedule|body_stack\\.currentWidget" src/ui/main_window.py`
  - 关键命中：`126-127, 491-497, 499-565`。
- MainWindow time picker：
  - `rg -n "time_picker_mode|...|editing_schedule|setCurrentWidget\\(self\\.page_time|..." src/ui/main_window.py`
  - 关键命中：`131-137, 268-336`。
- MainWindow alarm picker：
  - 命中：`139-143, 369-424`。
- MainWindow list picker：
  - 命中：`145-152, 427-488, 455-463`。
- WeekWindow 添加页与 picker：
  - `rg -n "page_add\\.btn_cancel|on_schedule_saved|switch_to_main_board|time_picker_mode|alarm_picker_mode|list_picker_mode|..." src/ui/week_window.py`
  - 关键命中：`748-761, 774-927`。
- TodoBoardWindow list picker / inline add：
  - `rg -n "inline_add_view|page_list|list_picker_mode|current_folder_id|current_folder_name|..." src/ui/todo_board.py`
  - 关键命中：`1223-1224, 1529-1660, 1692-1708, 1905-1957`。
- 代码片段阅读：
  - `main_window.py`：`Select-Object -Skip 110 -First 390` + `-Skip 500 -First 80`
  - `week_window.py`：`-Skip 730 -First 260`
  - `todo_board.py`：`-Skip 1510 -First 260` + `-Skip 1888 -First 95`

### MainWindow 添加页来源与返回链路地图

- 添加页取消：
  - `page_add.btn_cancel` -> `setCurrentWidget(getattr(source_view_for_add, page_dashboard))`（`main_window.py:126-127`）。
- 添加页保存：
  - `on_schedule_saved()` 内 `return_target = getattr(source_view_for_add, page_dashboard)` 后返回（`491-497`）。
  - 保存后还会 `page_dashboard.refresh_data()`、`page_todo.refresh_data()`、`_refresh_week_if_visible()`（`491-494`）。
- 进入添加页：
  - `switch_to_add_page()` 在当前页为 dashboard/todo 时写入 `source_view_for_add = current_widget`（`558-559`）。
  - 来源是 todo 时 `default_to_schedule=False`，否则 `True`（`562-563`）。
  - 若当前已在添加页，再点 add 会按 `source_view_for_add` 返回（`552-554`）。
- Header 触发：
  - `handle_header_action('add')` -> `switch_to_add_page()`（`499-501`）。

### MainWindow time/alarm/list picker add/edit 返回链路地图

- Time picker：
  - add 模式：`time_picker_mode='add'`（`270`）-> `back_from_time_picker()` 返回 `page_add`（`304-307`）。
  - edit 模式：`time_picker_mode='edit'` + `editing_schedule`（`290-291`）-> 返回 `page_dashboard`（`304-309`）。
  - edit 确认后触发：写库更新 + `page_dashboard/page_todo/_refresh_week_if_visible` + popup 刷新后返回（`316-336`）。
- Alarm picker：
  - add 模式：返回 `page_add`（`394-395`）。
  - edit 模式：返回 `page_dashboard`（`396-397`）。
  - edit 确认后触发：写库更新 + `page_dashboard/page_todo/_refresh_week_if_visible` + popup 刷新后返回（`404-424`）。
- List picker：
  - add 模式：返回 `page_add`（`456-457`）。
  - edit 模式：先写 `list_picker_source`（`445`），返回时按来源：
    - `todo` -> `page_todo`（`460-461`）
    - 否则 -> `page_dashboard`（`463`）
  - edit 确认后触发：写库更新 + `page_dashboard/page_todo/_refresh_week_if_visible` + popup 刷新后返回（`470-488`）。

### WeekWindow 添加页与 picker 返回链路地图

- 添加页取消：
  - `page_add.btn_cancel` -> `switch_to_main_board()`（`748, 777-778`）。
- 添加页保存：
  - `on_schedule_saved()` -> `switch_to_main_board()` + `refresh_week_data()`（`782-784`）。
- picker add/edit 返回：
  - time：edit 返回 `switch_to_main_board()`；add 返回 `page_add`（`810-815`）。
  - alarm：edit 返回 `switch_to_main_board()`；add 返回 `page_add`（`859-863`）。
  - list：edit 返回 `switch_to_main_board()`；add 返回 `page_add`（`904-908`）。
- edit 确认后刷新回流：
  - 三个 picker 在 edit 确认后均 `refresh_week_data()` + `schedule_updated.emit(editing_schedule)`（`827-833, 876-882, 919-925`）。

### TodoBoardWindow list picker 与 inline add 返回链路地图

- inline add 进入 list picker：
  - `inline_add_view.req_open_list_picker` -> `go_to_list_picker()`（`1544, 1550-1555`）。
  - 进入 picker 后 `view_stack` 切到 `page_list`，并临时隐藏顶部按钮（`1555-1561`）。
- edit 进入 list picker：
  - `go_to_list_picker_for_edit()` 设置 `list_picker_mode='edit'` + `editing_schedule`，切到 `page_list`（`1564-1573`）。
- picker 返回：
  - `back_from_list_picker()` 先根据 `current_folder_id/current_folder_name` 恢复标题与按钮（`1582-1599`）。
  - edit/manage 模式根据 `in_folder + view_mode + current_todos` 回到 `empty/stick/folder`（`1602-1610`）。
  - add 模式固定回 `inline_add_view`（`1613-1614`）。
- picker 确认：
  - edit：写库更新后 `refresh_data()` + `notify_main_window_refresh()` + popup 回流，再 `back_from_list_picker()`（`1620-1649`）。
  - add：给 `inline_add_view` 设分类后返回 `back_from_list_picker()`（`1659-1660`）。
- `current_folder_id/current_folder_name` 影响：
  - 文件夹进入写入（`1692-1693`），返回主看板重置（`1707-1708`）。
  - add 入口会把当前 folder 分类预填到 inline_add（`1907-1910`）。

### 状态字段清单（写入点 / 读取点 / 返回目标）

- `source_view_for_add`（MainWindow）：
  - 写入：`switch_to_add_page()`（`558-559`）
  - 读取：`btn_cancel`、`on_schedule_saved`、二次点击 add（`126-127, 496, 553`）
  - 返回目标：`page_dashboard` 或 `page_todo`
- `list_picker_source`（MainWindow）：
  - 写入：`go_to_list_picker_for_edit(..., source_view)`（`445`）
  - 读取：`back_from_list_picker()`（`460-463`）
  - 返回目标：edit 返回 `todo` 或 `dashboard`
- `time_picker_mode`（MainWindow/WeekWindow）：
  - 写入：`go_to_time_picker`/`go_to_time_picker_for_edit`（Main `270/290`，Week `788/799`）
  - 读取：`back_from_time_picker`、`on_time_confirmed`
  - 返回目标：Main add->`page_add`，edit->`page_dashboard`；Week add->`page_add`，edit->`page_week_board`
- `alarm_picker_mode`（MainWindow/WeekWindow）：
  - 写入：`go_to_alarm_picker`/`go_to_alarm_picker_for_edit`
  - 读取：`back_from_alarm_picker`、`on_alarm_confirmed`
  - 返回目标：Main add->`page_add`，edit->`page_dashboard`；Week add->`page_add`，edit->`page_week_board`
- `list_picker_mode`（MainWindow/WeekWindow/TodoBoardWindow）：
  - 写入：`go_to_list_picker`/`go_to_list_picker_for_edit`
  - 读取：`back_from_list_picker`、`on_list_confirmed`
  - 返回目标：
    - Main：add->`page_add`，edit->`page_todo`/`page_dashboard`
    - Week：add->`page_add`，edit->`page_week_board`
    - TodoBoard：add->`inline_add_view`，edit/manage->`stick/folder/empty` 动态
- `editing_schedule`（MainWindow/WeekWindow/TodoBoardWindow）：
  - 写入：各 picker `go_to_*_for_edit`
  - 读取：各 picker `on_*_confirmed` edit 分支
  - 返回目标：通过 `back_from_*` 返回到对应上级页面，同时驱动 popup/refresh 回流
- `current_folder_id/current_folder_name`（TodoBoardWindow）：
  - 写入：`_open_folder_view`（`1692-1693`），`_back_to_folder_view` 重置（`1707-1708`）
  - 读取：`back_from_list_picker`、`_on_add_clicked`、`_on_inline_add_canceled`、`refresh_data` 过滤
  - 返回目标：决定 `view_stack` 退回 `folder/stick/empty/inline_add`，并影响标题/按钮状态

### 风险等级

- 低风险：
  - MainWindow `source_view_for_add` 的来源记录与返回目标决策（纯状态+路由，不直接触写库）。
  - MainWindow `list_picker_source` 的 edit 返回目标决策（`todo/dashboard` 二选一）。
- 中风险：
  - WeekWindow 内部 picker add/edit 返回决策（单文件内，但联动 `schedule_updated.emit` 与 `refresh_week_data`）。
- 高风险：
  - MainWindow 三类 picker edit 分支（涉及写库、重复规则弹窗、跨视图刷新顺序）。
  - TodoBoardWindow `list_picker_mode + current_folder_id/current_folder_name + view_mode + view_stack` 组合状态机。
  - TodoBoard edit 路径对主窗口 dashboard popup 的回流联动。

### 适合 6-4 最小接管的候选项

- 建议仅接管一个最低风险闭环：
  - **MainWindow 添加页来源返回决策闭环**（`source_view_for_add` 写入 + cancel/save 返回目标读取）
  - 理由：单文件、纯路由状态、不涉及写库和跨窗口生命周期，回归面最小。

### 不适合 6-4 接管、应推迟或继续拆分的项

- 不建议在 6-4 一次性迁移 MainWindow 全部 picker 状态（time/alarm/list）。
- 不建议在 6-4 同时碰 WeekWindow 与 TodoBoardWindow。
- TodoBoard 的 list picker + inline add + folder/stick 状态机建议推迟到第八轮 UI 拆分前后，或至少另拆独立基线工单再做。

### diff 范围检查结果

- `git diff --name-only -- src` -> 无输出。
- `git diff --name-only -- main.py` -> 无输出。
- `git diff --name-only -- requirements.txt` -> 无输出。
- `git diff --name-only -- schedule.db` -> 无输出。
- `git diff --name-only` -> `manage_instruction/Work_Log.md`、`manage_instruction/Work_Task_Prompts.md`（后者为开工前既有）。
- `git status --short --branch` -> `## main...temp/main [ahead 3]`，`M manage_instruction/Work_Log.md`，`M manage_instruction/Work_Task_Prompts.md`。

### 未完成事项

- 待顾问窗口下发 `6-4` 正式提示词，确认是否仅接管 MainWindow `source_view_for_add` 最小闭环。

### 风险或疑点

- MainWindow picker edit 分支与写库/刷新顺序耦合较重，若进入接管需先做单路径行为回归脚本。
- TodoBoard 当前状态机依赖 `current_folder_id + view_mode + current_todos` 多条件组合，提前迁移会引入高回归风险。

## 2026-05-25 第六轮 6-4（添加页来源与 picker 返回状态最小接管）

- 本轮任务名称：第六轮 6-4（添加页来源与 picker 返回状态最小接管）。
- 开工前 git 状态：
  - `git status --short --branch` -> `## main...temp/main [ahead 4]`
  - 开工前既有 diff：`M manage_instruction/Work_Task_Prompts.md`
  - 结论：开工前已有管理文档 diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/controllers/main_controller.py`
  - `src/ui/main_window.py`
  - `manage_instruction/Work_Log.md`
- 是否进入源码修改分支：是（按 6-4 条件执行，仅接管最低风险闭环）。

### 接管的具体字段/路径

- `source_view_for_add` 写入决策：
  - `MainWindow.switch_to_add_page` 中改为调用 `MainController.resolve_add_source(...)`。
- 添加页取消返回目标：
  - `page_add.btn_cancel` 回调改为调用 `MainController.resolve_add_return_target(...)`。
- 添加页保存后返回目标：
  - `MainWindow.on_schedule_saved` 的 `return_target` 改为调用 `MainController.resolve_add_return_target(...)`。
- 添加页再次点击 add 的返回目标：
  - `switch_to_add_page` 中“当前已在 page_add”分支改为调用 `MainController.resolve_add_return_target(...)`。
- `default_to_schedule` 判断：
  - `switch_to_add_page` 中改为调用 `MainController.default_to_schedule_for_add(...)`。

### MainController 新增方法名和语义

- 新增方法：
  - `resolve_add_source(current_widget, dashboard_widget, todo_widget, existing_source=None)`
  - `resolve_add_return_target(source_view, dashboard_widget)`
  - `default_to_schedule_for_add(current_widget, todo_widget)`
- 语义：
  - 仅做对象比较和返回目标选择，不执行任何 UI 操作，不写数据库，不依赖 Qt/UI/db/Repository。

### MainWindow 最小替换说明

- 仅替换 `source_view_for_add` 闭环中的纯决策部分，Qt 实际操作仍在 MainWindow：
  - `setCurrentWidget(...)` 仍在 MainWindow。
  - `page_add.reset(...)` 仍在 MainWindow。
  - 保存后刷新顺序保持原样：
    - `page_dashboard.refresh_data()`
    - `page_todo.refresh_data()`
    - `_refresh_week_if_visible()`
- `handle_header_action` 未修改。
- `switch_view` 逻辑未修改。

### 未接管路径及原因

- `time picker`：未接管。原因：涉及 edit 写库、重复规则确认、跨视图刷新回流，风险高于本轮边界。
- `alarm picker`：未接管。原因同上。
- `list picker`：未接管。原因：除写库外还涉及 `list_picker_source` 和 todo/dashboard 返回分支，不属于本轮最小闭环。
- `WeekWindow`：未接管。原因：本轮明确禁止触碰。
- `TodoBoardWindow`：未接管。原因：本轮明确禁止触碰，且状态机复杂度高。

### 验证结果

- `py_compile` 验证结果：
  - 命令：`python -m py_compile src/controllers/main_controller.py src/ui/main_window.py`
  - 结果：通过（无输出）。
- MainController 纯决策行为验证结果：
  - 命令按提示词断言 `resolve_add_source/resolve_add_return_target/default_to_schedule_for_add`。
  - 结果：通过，输出 `main controller add source behavior ok`。
- controller import 回归结果：
  - 通过，输出 `controller imports ok`。
- MainWindow import 或兜底验证结果：
  - 通过，输出 `main window import ok True`。
- MainController 静态依赖检查结果：
  - 命令：`rg -n "QWidget|QStackedWidget|PyQt|PySide|MainWindow|WeekWindow|MonthWindow|TodoView|TodoBoard|db_manager|Repository|ScheduleRepository|CategoryRepository|add_schedule|update_schedule|delete_schedule|soft_delete|hard_delete|setCurrentWidget|refresh_data" src/controllers/main_controller.py`
  - 结果：无输出（退出码 1，视为通过）。

### 禁止范围 diff 检查结果

- `src/controllers/refresh_coordinator.py`：无 diff。
- `src/controllers/__init__.py`：无 diff。
- `src/ui/week_window.py`：无 diff。
- `src/ui/month_window.py`：无 diff。
- `src/ui/todo.py`：无 diff。
- `src/ui/todo_board.py`：无 diff。
- `src/data`：无 diff。
- `src/repositories`：无 diff。
- `src/services`：无 diff。
- `src/utils/signals.py`：无 diff。
- `main.py`：无 diff。
- `requirements.txt`：无 diff。
- `schedule.db`：无 tracked diff。

### 最终 diff 范围检查结果

- `git diff --name-only`：
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
  - `src/controllers/main_controller.py`
  - `src/ui/main_window.py`
  - 写入本日志后另含 `manage_instruction/Work_Log.md`
- `git status --short --branch`：
  - `## main...temp/main [ahead 4]`
  - `M manage_instruction/Work_Task_Prompts.md`
  - `M src/controllers/main_controller.py`
  - `M src/ui/main_window.py`
  - 写入本日志后另含 `M manage_instruction/Work_Log.md`

### 未完成事项

- 待顾问窗口下发 `6-5` 正式提示词，评估是否进入刷新协调边界建立。

### 风险或疑点

- `source_view_for_add` 闭环已迁入 controller 纯决策，但 MainWindow 内仍存在多个 picker 状态分支，后续若继续迁移需要保持“单闭环、可回归”节奏。
