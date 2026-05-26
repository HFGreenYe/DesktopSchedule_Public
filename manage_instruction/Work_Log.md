# Work Log

本文件只记录当前阶段/当前轮次的执行日志。

历史日志已归档到 `manage_instruction/History_Log.md`。

## 当前状态

第一轮：基建 + repository + db_manager 兼容委托，已完成并归档。

第二轮：Data 层整理与模型拆分，已完成并归档。

第三轮：纯业务查询与排序服务，已完成并归档。

第四轮：日程写入与重复规则服务，已完成并归档。

第五轮：提醒与运行期状态服务，已完成并归档。

第六轮：Controller / Router / EventBus 协调层，已完成并归档。

第七轮：Theme / QSS 接入与样式债务控制，已完成并归档。

第八轮：UI 拆分与样式债务整理，已完成 8-0（静态审查与职责地图），等待顾问窗口复核后进入 8-1。

## 当前轮次注意事项

- 第七轮归档内容见 `History_Instruction.md` 与 `History_Log.md`。
- 第八轮阶段合同已发布，当前已完成 8-0，只读基线已建立。
- 第八轮规划应保持小工单策略，避免一次性拆大 UI 文件。
- 第七轮遗留约束继续有效：基于 `default.qss / skin preset`，不建立 light/dark mode matrix。

## 2026-05-26 第八轮 8-0（UI 拆分静态审查与职责地图）

- 本轮任务名称：第八轮 8-0（UI 拆分静态审查与职责地图）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 21]`
  - 既有变更：`M manage_instruction/Work_Task_Prompts.md`
  - 说明：开工前已有管理文档 diff，本轮不视为源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`

- 读取的阶段合同结论：
  - 第八轮采用小工单渐进拆分，先做只读基线。
  - 第八轮继续基于 `default.qss / skin preset`，不建立 light/dark mode matrix。
  - 8-0 不允许改源码，不允许直接拆 `todo_board.py` / `week_window.py`。

- 静态搜索命令与关键结果：
  - `Get-ChildItem src\\ui -File | Sort-Object Length -Descending`：
    - `todo_board.py` 91505
    - `week_window.py` 61547
    - `main_window.py` 36655
    - `schedule_detail_pop.py` 36320
    - `month_window.py` 34545
    - `add_view.py` 29352
    - `add_view_week.py` 26190
    - `dashboard.py` 25332
    - `components.py` 25021
    - `todo.py` 21836
    - `list_picker.py` 18635
    - `header.py` 15469
  - `rg -n "^class " src/ui`：确认大文件多类集中分布，`todo_board.py` 与 `week_window.py` 为最高复杂度入口。
  - `rg -c "setStyleSheet\\(" src/ui/*.py` 热点：
    - `todo_board.py:58`
    - `week_window.py:42`
    - `schedule_detail_pop.py:25`
    - `month_window.py:24`
    - `add_view.py:24`
    - `add_view_week.py:20`
    - `list_picker.py:19`
    - `alarm_picker.py:17`
    - `dashboard.py:15`
    - 顾问窗口复核补充：上述 `rg -c ... src/ui/*.py` 在 PowerShell 下通配符传递会报路径错误；已用等价只读命令 `Get-ChildItem -Path src\\ui -Filter *.py | ForEach-Object { rg -n ... $_.FullName }` 复跑，热点数量与日志记录一致。
  - `rg -n "db_manager|...|RefreshCoordinator" src/ui`：
    - 直接写库/写状态调用集中于 `todo_board.py`、`week_window.py`、`todo.py`、`dashboard.py`、`schedule_detail_pop.py`、`main_window.py`。
    - `main_window.py` 已接第六轮 `MainController/ViewRouter/global_signals.refresh_requested`。
  - `Get-ChildItem src\\ui -Directory`：
    - 目前仅 `__pycache__`，无 `components/views/dialogs/popups/utils` 包骨架。

- UI 文件体量排序摘要（高风险文件）：
  - 超大文件：
    - `todo_board.py`（~89.4 KB）: 状态机 + 写库 + 视图栈 + 拖拽 + 详情弹窗借道 + toast。
    - `week_window.py`（~60.1 KB）: 周卡片/日期块/路由/编辑回流/拖拽重排/天气/toast。
  - 中高风险文件：
    - `main_window.py`、`schedule_detail_pop.py`、`month_window.py`、`add_view.py`、`add_view_week.py`。

- 大文件类分布与职责地图：
  - `todo_board.py`：
    - 数据卡片层：`StickyNoteCard`、`FolderCard`、`AddFolderCard`、`ManageCategoryCard`
    - 容器层：`StickViewContainer`、`FolderViewContainer`、`ManageListView`
    - 编辑层：`InlineAddTodoView`
    - 主状态机：`TodoBoardWindow`
    - 关键耦合：`db_manager` 写库、`view_stack` 路由、folder/stick 双态、`sort_order` 回写、详情弹窗借道 Dashboard。
  - `week_window.py`：
    - 展示类：`WeekScheduleCard`、`DayBlock`
    - 主窗口：`WeekWindow`
    - 关键耦合：内部 `body_stack` 路由、编辑 picker 三条回流、`update_schedule_with_repeat`、周内拖拽重排和 `sort_order` 回写。
  - `month_window.py`：
    - `CalendarCellDelegate`（渲染）
    - `InlineAddViewMonth`（内联新增）
    - `MonthWindow`（主视图 + view selector + calendar + weather + toast）
  - `main_window.py`：
    - 主视图路由容器与页面堆栈
    - 第六轮接入：`MainController` 添加页来源决策、`request_refresh_many` 三连刷新协调、`ViewRouter` 视图分类、`refresh_requested` 并行通知
    - 高耦合：编辑 picker 回流、周/月/待办桥接、详情弹窗回流中转。

- `components.py` / `widgets.py` 现有公共组件结论：
  - `components.py` 已有可复用组件：`IOSSwitch`、`NumberScroller`、`CountdownToolTip`/`CountdownToolTipFilter`、`SharedMoreMenu`、`ScheduleContextMenu`、`get_colored_icon`。
  - `widgets.py` 为旧小组件（`DashboardSlot`、`IconButton`），可作为后续轻量封装参考，但与主流程耦合弱。
  - 风险点：`components.py` 顶部直接 `from src.ui.todo_board import TodoBoardWindow`，已形成反向耦合，不宜在 8-0 直接动。

- tooltip/toast/icon loader/window control 重复逻辑分布：
  - `CustomToolTip/ToolTipFilter` 多处重复：`header.py`、`add_view.py`、`add_view_week.py`、`list_picker.py`、`alarm_picker*.py`。
  - 倒计时 tooltip 已有公共实现：`components.py::CountdownToolTip*`，但仍有局部实现并存。
  - icon loader 重复：
    - `components.py::get_colored_icon`
    - `todo_board.py::get_colored_icon` 与 `TodoBoardWindow._get_icon`
    - `schedule_detail_pop.py::_get_icon`
    - `time_picker.py/_week.py::_get_colored_icon`
  - toast 重复：
    - `main_window.py`、`week_window.py`、`month_window.py`、`todo_board.py` 均有 `show_toast`。
  - window control 创建/样式重复：
    - `header.py`、`week_window.py`、`month_window.py`、`list_picker.py`、`alarm_picker.py`、`time_picker.py`、`suspend_window*.py`。

- `setStyleSheet(...)` 热点与样式债务：
  - 热点集中在 `todo_board.py`、`week_window.py`、`schedule_detail_pop.py`、`month_window.py`、`add_view*.py`。
  - `StyleManager` 与内联样式并存，说明样式源不统一，迁移需按单点推进。

- 适合 `default.qss / role/state/variant` 的低风险样式候选：
  - 单点窗口控制按钮（延续 7-4 思路，限单控件）。
  - 单点 tooltip 容器（非业务逻辑型，仅视觉规则）。
  - 单点菜单项 hover（如 `SharedMoreMenu` 局部规则），前提是不改行为。
  - 不建议本轮处理全局按钮、卡片、输入框基础规则。

- 写库、刷新、picker、详情弹窗、拖拽、右键菜单、sort_order、folder/stick 状态机风险点：
  - 写库热点：
    - `todo_board.py`（22 处 `db_manager` 相关命中）
    - `week_window.py`（10 处）
    - `todo.py`（7 处）
    - `dashboard.py`（6 处）
    - `schedule_detail_pop.py`（6 处）
  - picker 返回链路：
    - `main_window.py` 与 `week_window.py` 各自持有 `time/alarm/list` add/edit 模式机与回流。
    - `todo_board.py` 另有 `list_picker_mode + view_stack` 独立状态机。
  - 详情弹窗回流：
    - `week -> main -> dashboard._show_detail_popup`
    - `todo_board -> main.page_dashboard._show_detail_popup`
  - 拖拽与排序写回：
    - `week_window.py`、`todo.py`、`todo_board.py` 都包含 `sort_order` 重排回写。
  - folder/stick 状态机：
    - `TodoBoardWindow` 同时管理 `view_mode/current_folder_id/current_folder_name/view_stack`，耦合高。
  - toast/timer/tooltip 生命周期：
    - 多窗口各自维护，若集中抽取容易引发父子窗口生命周期回归风险。

- 低风险拆分候选：
  - 仅建 UI 包目录骨架（`components/views/dialogs/popups/utils` + `__init__.py`），不移动类。
  - icon loader 先做只读统一映射，后续仅替换一个调用点（单文件）。
  - tooltip/toast 先做分布基线，再单点提取一个工具或组件。

- 中风险拆分候选：
  - `week_window.py` 中单类提取试点（`WeekScheduleCard` 或 `DayBlock` 二选一）。
  - `main_window.py` 局部展示辅助提取（不含路由/写库）。
  - `month_window.py` 内联新增视图或视图选择器局部提取（仅在行为基线稳定后）。

- 高风险暂缓项：
  - 直接拆 `todo_board.py` 主状态机。
  - 直接拆 `week_window.py` 主窗口流程。
  - `schedule_detail_pop.py` source_view 分支和编辑回流迁移。
  - 跨文件统一 toast/tooltip 生命周期改造。
  - 批量 `setStyleSheet` 迁移或全局控件风格重写。

- 建议下一步小工单：
  - 建议 `8-1` 仅建 UI 包目录骨架，不迁移类、不改调用方。
  - 建议 `8-2`、`8-3` 拆成 `8-2a/8-2b`、`8-3a/8-3b`：
    - `a`：只读基线
    - `b`：唯一调用点最小替换
  - 建议 `8-4` 在 `WeekScheduleCard` 与 `DayBlock` 中只选一个类做提取试点。
  - 建议 `8-5` 维持 TodoBoard 只读地图，不直接代码拆分。

- 是否建议 `8-1` 只建 UI 包目录骨架：
  - 建议。当前目录下仅 `__pycache__` 子目录，先建立包骨架可降低后续迁移冲突和 import 风险。

- diff 范围检查结果：
  - `git diff --name-only -- src`：无输出。
  - `git diff --name-only -- main.py`：无输出。
  - `git diff --name-only -- requirements.txt`：无输出。
  - `git diff --name-only -- schedule.db`：无输出。
  - 当前总 diff：
    - `manage_instruction/Work_Log.md`（本轮）
    - `manage_instruction/Work_Task_Prompts.md`（开工前既有）

- 未完成事项：
  - 8-1 目录骨架工单待执行。
  - 8-2/8-3 是否拆 a/b 待顾问窗口确认。

- 风险或疑点：
  - `components.py` 对 `todo_board.py` 的直接导入已构成潜在循环依赖风险，后续拆分需先做导入边界校正策略。
  - `todo_board.py` 与 `week_window.py` 都包含“写库 + 状态机 + UI 生命周期”三重耦合，必须继续单边界推进。

- 特别记录：
  - 本轮只读审查，不改源码。
  - 第八轮继续基于 `default.qss / skin preset`。
  - 不建立 light/dark mode matrix。
  - 不把真实换肤 UI、`theme_color/设置字体` 功能闭环并入本轮。
  - 不直接拆 `todo_board.py` 或 `week_window.py`。
