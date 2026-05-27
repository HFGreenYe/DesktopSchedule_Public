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

第八轮：UI 拆分与样式债务整理，已完成 8-6（TodoBoard AddFolderCard 单类提取试点），等待顾问窗口复核。

## 当前轮次注意事项

- 第七轮归档内容见 `History_Instruction.md` 与 `History_Log.md`。
- 第八轮阶段合同已发布，当前已完成 8-0、8-1、8-2a、8-2b、8-3a、8-3b、8-4a、8-4b、8-5、8-6，保持小工单推进。
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

## 2026-05-26 第八轮 8-1（UI 包目录骨架与导入边界准备）

- 本轮任务名称：第八轮 8-1（UI 包目录骨架与导入边界准备）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 23]`
  - 说明：开工前无源码 diff（仅分支 ahead 状态），符合目录骨架工单预期。
- 实际修改文件：
  - `src/ui/common/__init__.py`（新增）
  - `src/ui/views/__init__.py`（新增）
  - `src/ui/dialogs/__init__.py`（新增）
  - `src/ui/popups/__init__.py`（新增）
  - `src/ui/utils/__init__.py`（新增）
  - `manage_instruction/Work_Log.md`

- 新增目录与 `__init__.py` 清单：
  - `src/ui/common/`
  - `src/ui/views/`
  - `src/ui/dialogs/`
  - `src/ui/popups/`
  - `src/ui/utils/`
  - 每个目录均新增空 `__init__.py`，不含任何副作用代码。

- import 验证结果：
  - 命令：
    - `python -c "import src.ui.common, src.ui.views, src.ui.dialogs, src.ui.popups, src.ui.utils; from src.ui.components import SharedMoreMenu; print('ui package skeleton import ok')"`
  - 结果：
    - `ui package skeleton import ok`
  - 结论：
    - 新包可 import；
    - 未创建 `src/ui/components/`，未遮蔽既有 `src/ui/components.py` 导入链路。

- py_compile 结果：
  - 命令：
    - `python -m py_compile src/ui/common/__init__.py src/ui/views/__init__.py src/ui/dialogs/__init__.py src/ui/popups/__init__.py src/ui/utils/__init__.py`
  - 结果：通过。

- 无副作用说明：
  - 未触发 QApplication。
  - 未连接 signal。
  - 未迁移任何 UI 类。
  - 未替换任何调用方 import。

- diff 范围检查结果：
  - `git diff --name-only -- src/theme`：无输出。
  - `git diff --name-only -- src/data`：无输出。
  - `git diff --name-only -- src/repositories`：无输出。
  - `git diff --name-only -- src/services`：无输出。
  - `git diff --name-only -- src/controllers`：无输出。
  - `git diff --name-only -- src/utils/signals.py`：无输出。
  - `git diff --name-only -- src/utils/styles.py`：无输出。
  - `git diff --name-only -- main.py`：无输出。
  - `git diff --name-only -- requirements.txt`：无输出。
  - `git diff --name-only -- schedule.db`：无输出。
  - `git status --short --branch`：
    - `## main...temp/main [ahead 23]`
    - `?? src/ui/common/`
    - `?? src/ui/dialogs/`
    - `?? src/ui/popups/`
    - `?? src/ui/utils/`
    - `?? src/ui/views/`
  - 说明：
    - 本轮新增文件为未跟踪状态，`git diff --name-only` 对未跟踪文件不显示，最终以 `git status` 为准。

- 未完成事项：
  - 待顾问窗口复核后进入 8-2（建议先 8-2a 只读基线，再 8-2b 单点替换）。

- 风险或疑点：
  - 当前仅完成包骨架，尚未处理 `components.py` 与 `todo_board.py` 的导入耦合；后续拆分需继续单边界推进。

## 2026-05-26 第八轮 8-2a（公共 icon loader 静态定位与提取基线）

- 本轮任务名称：第八轮 8-2a（公共 icon loader 静态定位与提取基线）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 24]`
  - 既有变更：`M manage_instruction/Work_Task_Prompts.md`
  - 说明：开工前已有管理文档 diff，本轮不视为源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`

- 本轮执行约束落实：
  - 只读审查，不改源码。
  - 未创建 `src/ui/utils/icon_loader.py`。
  - 未替换任何调用方。
  - 未修改 `assets/`。

- 静态搜索命令与关键结果：
  - `rg -n "get_colored_icon|_get_icon|_load_colored_svg|QSvgRenderer|QPixmap|QIcon|setIcon|setPixmap|assets/icons|assets/weather" src/ui`
  - `rg -n "def get_colored_icon|def _get_icon|def _load_colored_svg" src/ui`
  - `rg -n "...(重点文件)..." src/ui/components.py src/ui/header.py src/ui/todo_board.py src/ui/schedule_detail_pop.py src/ui/time_picker.py src/ui/time_picker_week.py src/ui/week_window.py src/ui/month_window.py`
  - `Get-ChildItem -Path src\\ui\\utils -Force`
  - 结果摘要：
    - 明确命中函数 11 处：
      - `components.py::get_colored_icon`
      - `todo_board.py::get_colored_icon`
      - `todo_board.py::TodoBoardWindow._get_icon`
      - `schedule_detail_pop.py::_get_icon`
      - `header.py::_load_colored_svg`
      - `week_window.py::_load_colored_svg`
      - `month_window.py::_load_colored_svg`
      - `time_picker.py::_get_colored_icon`
      - `time_picker_week.py::_get_colored_icon`
      - `add_view.py::_load_colored_icon`
      - `add_view_week.py::_load_colored_icon`
    - `src/ui/utils` 当前仅 `__init__.py`，尚无 `icon_loader.py`（符合本轮约束）。

- icon loader 命中点职责地图（按可提取价值排序）：
  - `src/ui/components.py::get_colored_icon(icon_name, color, target_size=12)`
    - 输入：图标名（拼接 `assets/icons/`）、颜色、目标尺寸
    - 输出：`QPixmap`
    - 依赖：`QPainter + QSvgRenderer + QImage`
    - assets：`assets/icons/*`
    - fallback：文件不存在或 SVG 无效返回空 `QPixmap()`
    - QWidget/self 依赖：无（纯函数）
    - 抽取适配：高（最适合作为基础 pure helper）
    - 风险等级：低

  - `src/ui/todo_board.py::get_colored_icon(icon_name, color, target_size=12)`
    - 输入/输出/逻辑与 `components.py::get_colored_icon` 基本同构
    - fallback：同上（空 `QPixmap`)
    - QWidget/self 依赖：无（纯函数）
    - 抽取适配：高（重复实现，适合后续复用 helper）
    - 风险等级：中（文件本体为高耦合状态机，不宜本轮动）

  - `src/ui/todo_board.py::TodoBoardWindow._get_icon(icon_name, color, target_size=16)`
    - 输入：图标名、颜色、尺寸
    - 输出：`QPixmap`
    - 特点：同时支持 SVG 与位图（`QImage` 分支），并做居中缩放
    - fallback：路径不存在/无效图返回空 `QPixmap`
    - QWidget/self 依赖：有（成员方法，虽不直接用状态，但在高耦合主类内）
    - 抽取适配：中（能力更全，但迁移风险高）
    - 风险等级：高（暂缓）

  - `src/ui/schedule_detail_pop.py::_get_icon(icon_name, color, target_size=16)`
    - 输入：图标名、颜色、尺寸
    - 输出：`QPixmap`
    - 特点：与 `TodoBoardWindow._get_icon` 近似（SVG+位图双分支）
    - fallback：路径不存在/无效图返回空 `QPixmap`
    - QWidget/self 依赖：成员方法（位于复杂弹窗）
    - 抽取适配：中
    - 风险等级：高（涉及详情弹窗复杂行为，暂缓）

  - `src/ui/header.py::_load_colored_svg(icon_path, color_hex, width, height)`
    - 输入：完整 SVG 路径、颜色、宽高
    - 输出：`QPixmap`
    - 特点：使用 `self.devicePixelRatio()` 渲染高清图，适配 `assets/icons` 与 `assets/weather`
    - fallback：`renderer` 无效返回空 `QPixmap`
    - QWidget/self 依赖：有（DPR 读取依赖 widget）
    - 抽取适配：中（可转为 helper(path,color,w,h,dpr)）
    - 风险等级：中（可做单点替换候选）

  - `src/ui/week_window.py::_load_colored_svg(icon_path, color_hex, width, height)`
    - 与 `header.py` 基本同构
    - 用途：天气图标着色
    - QWidget/self 依赖：有（DPR）
    - 抽取适配：中
    - 风险等级：中高（`week_window.py` 主流程复杂，暂不作为首替换点）

  - `src/ui/month_window.py::_load_colored_svg(icon_path, color_hex, width, height)`
    - 与 `header.py`/`week_window.py` 同构
    - 用途：天气图标着色
    - QWidget/self 依赖：有（DPR）
    - 抽取适配：中
    - 风险等级：中高（`month_window.py` 视图逻辑较重，暂不首替换）

  - `src/ui/time_picker.py::_get_colored_icon(icon_path, color_hex)` 与 `src/ui/time_picker_week.py::_get_colored_icon(icon_path, color_hex)`
    - 输入：完整路径 + 颜色
    - 输出：`QIcon`（非 `QPixmap`）
    - 特点：固定 64x64 画布，主要服务日历上下月按钮
    - fallback：无显式文件/renderer 无效检查（依赖渲染结果）
    - QWidget/self 依赖：成员方法
    - 抽取适配：中低（返回类型不同，且存在两文件并行）
    - 风险等级：中高（建议暂缓）

  - `src/ui/add_view.py::_load_colored_icon(name, color_hex, target_size=18)` 与 `src/ui/add_view_week.py::_load_colored_icon(name, color_hex, target_size=18)`
    - 输入：图标名、颜色、目标尺寸
    - 输出：`QPixmap`
    - 特点：与 `components.py::get_colored_icon` 逻辑高度同构，使用 `assets/icons/{name}`、`QSvgRenderer`、4x 超采样和 `CompositionMode_SourceIn` 染色
    - fallback：renderer 无效返回空 `QPixmap()`；未显式先 `os.path.exists`
    - QWidget/self 依赖：成员方法，但逻辑本身不依赖实例状态
    - 抽取适配：中（重复度高，但处在添加页保存/校验 UI 文件内，首轮不建议替换）
    - 风险等级：中（建议在 add view 行为基线后再处理）

- 重复逻辑对比（输入/输出/颜色/尺寸/fallback/依赖）：
  - 输入形态：
    - A 类（icon_name）：`components.py`、`todo_board.py`、`schedule_detail_pop.py`
    - B 类（icon_path）：`header/week/month/time_picker/time_picker_week`
    - C 类（name + member helper）：`add_view/add_view_week::_load_colored_icon`
  - 输出类型：
    - `QPixmap`：A 类 + `header/week/month`
    - `QIcon`：`time_picker*::_get_colored_icon`
  - 颜色处理：
    - 全部使用 `CompositionMode_SourceIn + fillRect` 染色
    - 颜色入参有 `str` 与 `QColor` 双态
  - 尺寸处理：
    - `components.py` 与 `todo_board/schedule_detail` 使用 `scale_ratio=4.0` 超采样
    - `header/week/month` 用 widget DPR 计算 pixel size
    - `time_picker*` 固定 64x64
  - fallback 行为：
    - `components.py`、`todo_board*`、`schedule_detail_pop`、`header/week/month`、`add_view/add_view_week`：存在空 `QPixmap` fallback
    - `time_picker*`：缺少显式 fallback（相对风险更高）
  - QWidget/self 依赖：
    - 纯函数：`components.py::get_colored_icon`、`todo_board.py::get_colored_icon`
    - 成员方法：其余均依赖类上下文（至少绑定在类中）

- 低风险提取候选：
  - 候选 1（推荐）：以 `components.py::get_colored_icon` 作为首个抽取基线（纯函数、低耦合、fallback 清晰）。
  - 候选 2（可选）：`header.py::_load_colored_svg` 单点替换（但需 helper 支持 path+dpr 参数）。

- 中风险候选：
  - `week_window.py::_load_colored_svg`
  - `month_window.py::_load_colored_svg`
  - `add_view.py::_load_colored_icon`
  - `add_view_week.py::_load_colored_icon`
  - 原因：代码同构但宿主窗口较重，回归面大于 header 单点。

- 高风险暂缓项：
  - `todo_board.py::_get_icon`
  - `schedule_detail_pop.py::_get_icon`
  - `time_picker.py/_week.py::_get_colored_icon`
  - 原因：分别位于高耦合状态机/复杂弹窗/返回类型差异路径。

- 是否建议执行 8-2b：
  - 建议执行，但必须遵守“只提取一个 helper + 只替换一个调用点”。

- 8-2b 建议的唯一替换调用点：
  - 建议：`header.py::_load_colored_svg`（单文件、无写库、无状态机、回归面最小）。
  - 抽取来源建议：以 `components.py::get_colored_icon` 的染色流程为核心，扩展为 path 版 helper。
  - 暂不建议首轮替换 `todo_board.py` / `schedule_detail_pop.py` / `time_picker*`。

- diff 范围检查结果：
  - `git diff --name-only -- src`：无输出。
  - `git diff --name-only -- assets`：无输出。
  - `git diff --name-only -- main.py`：无输出。
  - `git diff --name-only -- requirements.txt`：无输出。
  - `git diff --name-only -- schedule.db`：无输出。
  - 当前总 diff：
    - `manage_instruction/Work_Log.md`（本轮）
    - `manage_instruction/Work_Task_Prompts.md`（开工前既有）

- 未完成事项：
  - 8-2b 具体工单需锁定 helper 签名与唯一替换点（建议 `header.py::_load_colored_svg`）。

- 风险或疑点：
  - icon helper 若同时兼容 `QPixmap/QIcon` 两种输出，容易扩张边界；8-2b 建议先只输出 `QPixmap`，避免首轮过度抽象。
  - `components.py` 当前仍直接 import `todo_board.py`，后续若扩大提取范围需同步评估导入边界。

- 特别记录：
  - 本轮只读审查，不改源码。
  - 不创建 `src/ui/utils/icon_loader.py`。
  - 不替换任何调用方。
  - 不修改 `assets`。
  - 后续若进入 8-2b，必须只提取一个 helper 并只替换一个低风险调用点。

## 2026-05-26 第八轮 8-2b（公共 icon loader 最小提取与 Header 单点替换）

- 本轮任务名称：第八轮 8-2b（公共 icon loader 最小提取与 Header 单点替换）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 25]`
  - 既有变更：`M manage_instruction/Work_Task_Prompts.md`
  - 说明：开工前已有管理文档 diff，本轮不视为源码改动。
- 实际修改文件：
  - `src/ui/utils/icon_loader.py`（新增）
  - `src/ui/header.py`
  - `manage_instruction/Work_Log.md`

- 新增 helper 文件与函数名：
  - 文件：`src/ui/utils/icon_loader.py`
  - 函数：`load_colored_svg_pixmap(icon_path, color_hex, width, height, device_pixel_ratio=1.0)`

- helper 签名与职责：
  - 输入：
    - `icon_path`：完整 SVG 路径
    - `color_hex`：颜色字符串
    - `width/height`：逻辑尺寸
    - `device_pixel_ratio`：DPR（默认 1.0）
  - 输出：
    - `QPixmap`
  - 行为：
    - `QSvgRenderer` 渲染 SVG
    - 按 DPR 生成像素尺寸并 `setDevicePixelRatio`
    - `CompositionMode_SourceIn` 染色

- helper fallback 行为：
  - `renderer.isValid()` 为 `False` 时返回空 `QPixmap()`。
  - 缺失文件路径在 `QSvgRenderer` 无效分支同样返回空 `QPixmap()`。

- 是否依赖 QWidget/self：
  - 否。helper 为纯 UI 工具函数，不依赖 widget 实例，不读取全局状态，不连接信号。

- `header.py::_load_colored_svg(...)` 兼容性说明：
  - 方法名、参数、返回语义保持不变。
  - 仍在 `HeaderBar` 内部通过 `self.devicePixelRatio()` 取 DPR。
  - 方法体改为单行委托 helper，不改变调用方。

- 确认未修改 `_load_colored_svg(...)` 调用方：
  - `header.py` 内部调用位置保持不变（按钮图标与天气图标路径未改）。

- 确认未修改 `btn_sync` 试点：
  - `btn_sync` 的 `role/variant/state` 属性保持：
    - `windowControl` / `toolbar` / `normal`
  - `btn_sync` 相关行为与连接未改。

- 验证结果：
  - helper 定位与替换检查：
    - `rg -n "load_colored_svg_pixmap|_load_colored_svg|QSvgRenderer|CompositionMode_SourceIn|devicePixelRatio" ...` 命中符合预期。
  - helper import 验证：
    - 输出：`icon loader import ok <function load_colored_svg_pixmap ...>`
  - helper offscreen 渲染验证：
    - 输出：`pixmap null False size 24 24 dpr 1.0`
    - 输出：`missing null True`
    - 结论：有效 SVG 可渲染，缺失路径回空图。
  - Header import 验证：
    - 输出：`header import ok <class 'src.ui.header.HeaderBar'>`
  - Header offscreen 回归：
    - 输出：`header pixmap null False size 24 24`
    - 输出：`sync role windowControl`
    - 输出：`sync variant toolbar`
    - 输出：`sync state normal`
  - 旧 `src.ui.components` 导入回归：
    - 输出：`components import ok <class 'src.ui.components.SharedMoreMenu'> <function get_colored_icon ...>`
  - 默认启动接入回归：
    - 输出：`main import ok`
  - py_compile：
    - 命令：`python -m py_compile src/ui/utils/icon_loader.py src/ui/header.py main.py`
    - 结果：通过。

- diff 范围检查结果：
  - 禁止范围：
    - `assets`、`src/ui/components.py`、`src/ui/todo_board.py`、`src/ui/schedule_detail_pop.py`、`src/ui/time_picker.py`、`src/ui/time_picker_week.py`、`src/ui/week_window.py`、`src/ui/month_window.py`、`src/theme`、`src/data`、`src/repositories`、`src/services`、`src/controllers`、`src/utils/signals.py`、`src/utils/styles.py`、`main.py`、`requirements.txt`、`schedule.db` 均无 diff。
  - 允许范围：
    - `src/ui` 仅命中：
      - `src/ui/header.py`
      - `src/ui/utils/icon_loader.py`
  - 当前总 diff：
    - `src/ui/header.py`
    - `src/ui/utils/icon_loader.py`
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`（开工前既有）

- 未完成事项：
  - 后续若继续 icon 统一，需另开工单，且每次只替换一个调用点。

- 风险或疑点：
  - `header.py` 仍保留 `QSvgRenderer` 相关 import（当前未影响行为）；后续可在单独清理工单处理，不在本轮扩大范围。

- 特别记录：
  - 本轮只新增一个 helper。
  - 本轮只替换 `header.py::_load_colored_svg(...)` 这一个低风险调用边界。
  - 本轮不统一所有 icon loader。
  - 本轮不修改 `assets`。
  - 本轮不处理 `QIcon` 返回路径。
  - 本轮不处理 `todo_board.py` / `schedule_detail_pop.py` / `time_picker*.py`。

## 2026-05-26 第八轮 8-3a（公共 tooltip / toast 边界静态定位）

- 本轮任务名称：第八轮 8-3a（公共 tooltip / toast 边界静态定位）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 26]`
  - 既有变更：`M manage_instruction/Work_Task_Prompts.md`
  - 说明：开工前已有管理文档 diff，本轮不视为源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`

- 本轮执行约束落实：
  - 本轮只读审查，不改源码。
  - 未创建 `src/ui/common/tooltip.py`。
  - 未创建 `src/ui/common/toast.py`。
  - 未替换任何调用方。
  - 未修改 QSS、icon loader、assets。
  - 未清理 `header.py` import 残留（按工单要求保留）。

- tooltip 搜索命令与结果摘要：
  - 命令：
    - `rg -n "CustomToolTip|ToolTipFilter|CountdownToolTip|CountdownToolTipFilter|QToolTip|tooltip|toolTip|setToolTip|eventFilter|Enter|Leave|Hover" src/ui`
  - 结果摘要：
    - `CustomToolTip` 定义分布在：
      - `src/ui/header.py`
      - `src/ui/add_view.py`
      - `src/ui/add_view_week.py`
      - `src/ui/list_picker.py`
      - `src/ui/alarm_picker.py`
      - `src/ui/alarm_picker_week.py`
    - `ToolTipFilter` 定义分布在：
      - `src/ui/header.py`
      - `src/ui/add_view.py`
      - `src/ui/add_view_week.py`
    - `CountdownToolTip` / `CountdownToolTipFilter` 定义在：
      - `src/ui/components.py`
    - `ToolTipFilter` 调用分布在：
      - `header.py`（窗口控制/天气）
      - `week_window.py`（天气、按钮、日期）
      - `month_window.py`（天气、挂起按钮）
      - `todo_board.py::_apply_custom_tooltip(...)`（借用 header 的 ToolTipFilter）
    - Qt 原生 `setToolTip(...)` 分布在：
      - `schedule_detail_pop.py`（字段说明）
      - `suspend_window*.py`
      - `header.py`（日期、天气）
  - 备注：
    - `src/ui/hanging_widget.py` 不存在（`Get-ChildItem src/ui` 未发现该文件），本轮按实际文件集审查。

- toast 搜索命令与结果摘要：
  - 命令：
    - `rg -n "show_toast|toast|Toast|toast_label|toast_widget|QTimer|singleShot|hide\(|close\(|临时|提示|成功|失败" src/ui`
  - 结果摘要：
    - 明确 `show_toast` 定义分布在：
      - `src/ui/main_window.py`
      - `src/ui/week_window.py`
      - `src/ui/month_window.py`
      - `src/ui/todo_board.py`
    - 临时提示（非 `show_toast`）分布在：
      - `src/ui/list_picker.py::_show_tooltip(...)`
      - `src/ui/add_view.py` / `src/ui/add_view_week.py`（校验失败气泡）
      - `src/ui/alarm_picker.py` / `src/ui/alarm_picker_week.py`（参数校验气泡）
    - `dashboard.py`、`todo.py` 未定义本地 `show_toast`，主要依赖主窗口或其它视图回流。

- tooltip 职责地图：
  - `src/ui/header.py::CustomToolTip + ToolTipFilter`
    - 类型：自定义 tooltip widget + eventFilter。
    - 输入：`text`。
    - parent 依赖：有（filter 安装到目标 widget）。
    - timer：`QTimer(singleShot, 400ms)` 控制悬停触发。
    - 显示位置：`QCursor.pos()`。
    - 关闭行为：`Leave/MousePress/Hide/FocusOut` 时 `_close_tooltip()`。
    - 复用情况：被 `todo_board.py` 间接复用，被 `week/month` 直接引用 `ToolTipFilter`。
    - 风险等级：中（跨文件引用已存在，变更会影响多个窗口）。

  - `src/ui/components.py::CountdownToolTip + CountdownToolTipFilter`
    - 类型：倒计时 tooltip + eventFilter。
    - 输入：`schedule_data`，内部解析 `start_time/end_time`。
    - parent 依赖：中（绑定到卡片 widget）。
    - timer：
      - filter 悬停延迟 400ms；
      - tooltip 内部每秒更新倒计时。
    - 显示位置：`QCursor.pos() + QPoint(15, 15)`。
    - 关闭行为：离开/点击/隐藏/失焦 -> stop + close + deleteLater。
    - 复用情况：`dashboard.py`、`week_window.py` schedule card 复用。
    - 风险等级：高（涉及倒计时逻辑与生命周期，不宜首轮抽取）。

  - `src/ui/add_view.py` / `src/ui/add_view_week.py::CustomToolTip + ToolTipFilter`
    - 类型：局部重复实现。
    - 输入：`text`，`CustomToolTip` 支持 `border_color`。
    - parent 依赖：有。
    - timer：
      - filter 悬停 400ms；
      - tooltip 自动关闭 500ms。
    - 显示位置：`QCursor.pos() + QPoint(10, 10)`；校验场景还会指定按钮附近偏移。
    - 关闭行为：同 header 版本。
    - 复用情况：仅文件内使用，和 header 版本重复度高。
    - 风险等级：中（与添加页编辑流程耦合，宜单点替换）。

  - `src/ui/list_picker.py::CustomToolTip + _show_tooltip(...)`
    - 类型：局部错误提示气泡（非 eventFilter 模式）。
    - 输入：`text` + `is_error` 控制边框颜色。
    - parent 依赖：有（以当前 picker 为 parent）。
    - timer：tooltip 内部 `singleShot(2500ms)` 自动关闭。
    - 显示位置：基于窗口几何中心计算。
    - 关闭行为：到时 close。
    - 复用情况：仅 list picker 删除/新增失败提示。
    - 风险等级：低（边界独立，适合后续单点提取）。

  - `src/ui/alarm_picker.py` / `src/ui/alarm_picker_week.py::CustomToolTip`
    - 类型：局部校验提示气泡。
    - 输入：`text`（固定红色边框）。
    - parent 依赖：有。
    - timer：`singleShot(2000ms)`。
    - 显示位置：窗口中心。
    - 关闭行为：到时 close。
    - 复用情况：两文件重复实现。
    - 风险等级：低到中（纯提示，但涉及两个 picker 文件）。

  - `schedule_detail_pop.py` / `suspend_window*.py` / `header.py` 的 `setToolTip`
    - 类型：Qt 原生 tooltip 文案。
    - 依赖：无自定义 timer、无 eventFilter。
    - 风险等级：低（本身不需要抽取，属于静态说明文案）。

- toast 职责地图：
  - `src/ui/main_window.py::show_toast(message)`
    - 创建：`toast_label = QLabel(message, self)`。
    - 显示位置：主窗口居中。
    - 持续时间：500ms（最短）。
    - timer 生命周期：`QTimer.singleShot(500, self.toast_label.close)`。
    - parent 依赖：`self`（MainWindow）。
    - 文案来源：视图切换提示、日期限制提示等。
    - 业务影响：弱（仅展示层）。
    - 风险等级：低（候选单点提取）。

  - `src/ui/month_window.py::show_toast(message)`
    - 创建：`toast_label = QLabel(message, self)`。
    - 显示位置：MonthWindow 居中。
    - 持续时间：1500ms。
    - timer 生命周期：`singleShot(1500)`。
    - parent 依赖：`self`。
    - 文案来源：添加成功/日期限制等。
    - 业务影响：弱。
    - 风险等级：低（候选单点提取）。

  - `src/ui/todo_board.py::show_toast(message)`
    - 创建：`toast_label = QLabel(message, self)`。
    - 显示位置：看板窗口居中。
    - 持续时间：1500ms。
    - timer 生命周期：`singleShot(1500)`。
    - parent 依赖：`self`（复杂状态机窗口）。
    - 文案来源：新增成功、删除反馈、拦截提醒。
    - 业务影响：中（和 folder/stick 状态流频繁联动）。
    - 风险等级：中高（不建议首轮抽取）。

  - `src/ui/week_window.py::show_toast(message)`
    - 创建：`toast_widget(QWidget)` + icon + text 组合。
    - 显示位置：周视图窗口居中。
    - 持续时间：1500ms。
    - timer 生命周期：`singleShot(1500)`。
    - parent 依赖：`self`。
    - 文案来源：拖拽拦截、新增/校验提示。
    - 业务影响：中（含图标与编辑模式背景耦合）。
    - 风险等级：中高（不建议首轮抽取）。

  - `src/ui/list_picker.py::_show_tooltip(...)`（提示条替代）
    - 虽名称不是 toast，但承担局部错误反馈。
    - 风险等级：低（边界独立）。

- parent / timer / eventFilter / 显示位置 / 关闭行为分析：
  - parent 归属：
    - tooltip/toast 基本都绑定当前窗口/控件，跨窗口抽取时需保留 parent 语义。
  - timer 行为：
    - tooltip 悬停延迟主流为 400ms；
    - tooltip 自动关闭时长分裂为 500ms / 2000ms / 2500ms；
    - toast 自动关闭分裂为 500ms（main）与 1500ms（week/month/todo_board）。
  - eventFilter 行为：
    - `header/add_view/add_view_week` 的 `ToolTipFilter` 返回值策略相似，但实现分散。
    - `CountdownToolTipFilter` 明确不吞事件（return False），属于特殊行为，不能与普通 tooltip filter 混抽。
  - 显示位置：
    - cursor 附近（header/add_view*）
    - 窗口中心（list_picker、alarm_picker*、toast）
    - cursor 偏移 + 动态倒计时（components）
  - 关闭行为：
    - `close` + 有些路径 `deleteLater`（components）
    - 一般 tooltip 仅 `close`，无 deleteLater。

- 低风险候选：
  - 候选 A：`list_picker.py::_show_tooltip` 相关 `CustomToolTip` 单点提取（局部、无状态机、无写库耦合）。
  - 候选 B：`main_window.py::show_toast` 单点 helper 化（最短路径、影响面可控）。
  - 候选 C：`alarm_picker.py` 与 `alarm_picker_week.py` 的 `CustomToolTip`（二选一先单点，不要双替换）。

- 中风险候选：
  - `add_view.py` / `add_view_week.py` 的 `ToolTipFilter` 统一（需确保编辑流程与校验提示位置不变）。
  - `month_window.py::show_toast`（可抽，但与 inline add 回流关联，建议先基线）。

- 高风险暂缓项：
  - `components.py::CountdownToolTipFilter`（倒计时 + 生命周期 + 事件吞吐策略）。
  - `week_window.py::show_toast`（图标注入 + 模式背景联动）。
  - `todo_board.py::show_toast`（复杂状态机窗口，联动点多）。
  - 跨文件统一所有 `ToolTipFilter` / `CustomToolTip`（一次性改动面过大）。

- 是否建议进入 8-3b：
  - 建议进入，但必须维持“单点提取、单调用方替换”策略。

- 8-3b 建议的唯一单点提取目标：
  - 建议优先：`src/ui/main_window.py::show_toast` 提取为一个最小 toast helper（只替换 MainWindow 一处）。
  - 原因：业务耦合最低、无 eventFilter、无倒计时业务语义、回归成本最低。
  - 明确暂缓：`week_window.py` 与 `todo_board.py` toast，`components.py` 倒计时 tooltip。

- 验证结果：
  - `Test-Path src\ui\common\tooltip.py`：`False`
  - `Test-Path src\ui\common\toast.py`：`False`
  - UI 包骨架 import：
    - `ui package skeleton import ok`
  - icon loader import 回归：
    - `icon loader import ok <function load_colored_svg_pixmap ...>`

- diff 范围检查结果：
  - `git diff --name-only -- src`：无输出。
  - `git diff --name-only -- assets`：无输出。
  - `git diff --name-only -- main.py`：无输出。
  - `git diff --name-only -- requirements.txt`：无输出。
  - `git diff --name-only -- schedule.db`：无输出。
  - 当前总 diff：
    - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
    - `manage_instruction/Work_Log.md`（本轮）

- 未完成事项：
  - 8-3b 工单需锁定单点目标和替换边界（建议只碰 `main_window.py::show_toast`）。

- 风险或疑点：
  - `hanging_widget.py` 在当前仓库不存在，若后续提示词继续包含该文件，应先确认是否为历史文件名。
  - `ToolTipFilter` 在 `header/add_view/add_view_week` 三处存在细节差异，8-3b 不建议同时统一三处。

- 特别记录：
  - 本轮只读审查，不改源码。
  - 本轮不创建 `tooltip.py` / `toast.py`。
  - 本轮不替换任何调用方。
  - 本轮不修改 QSS。
  - 本轮不处理 icon loader 后续统一。
  - 本轮不清理 8-2b 遗留的 `header.py` unused import，若需处理必须另开小工单。

## 2026-05-27 第八轮 8-3b（MainWindow toast 单点提取）

- 本轮任务名称：第八轮 8-3b（MainWindow toast 单点提取）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 27]`
  - 既有变更：`M manage_instruction/Work_Task_Prompts.md`
  - 说明：开工前已有管理文档 diff，本轮不视为源码问题。
- 实际修改文件：
  - `src/ui/common/toast.py`（新增）
  - `src/ui/main_window.py`
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有管理文档 diff，本轮随复核锚点保留）

- 新增 helper 文件和函数名：
  - 文件：`src/ui/common/toast.py`
  - 函数：`show_center_toast(parent, message, attr_name="toast_label", duration_ms=500)`

- helper 签名与职责：
  - 输入：
    - `parent`：承载 toast 的 QWidget
    - `message`：显示文本
    - `attr_name`：保存标签属性名（默认 `toast_label`）
    - `duration_ms`：自动关闭时长（默认 `500`）
  - 输出：`QLabel`
  - 行为：
    - 若 `parent` 上已有同名 toast 且可见，先 `close()`
    - 创建 `QLabel(message, parent)` 并回写到 `parent.toast_label`
    - 使用与 MainWindow 原实现一致的样式字符串
    - 居中定位规则保持不变
    - `WA_TransparentForMouseEvents` 保持
    - `QTimer.singleShot(duration_ms, label.close)`

- helper 是否依赖 MainWindow：
  - 否。仅依赖传入 `parent` 的 QWidget 基础能力，不引用 MainWindow 类型。

- helper 是否访问 db_manager / Repository / Service：
  - 否。无数据层、仓储层、服务层依赖。

- `MainWindow.show_toast(message)` 兼容性说明：
  - 方法名、参数保持不变：`show_toast(self, message)`。
  - 对外调用方保持不变。
  - 内部改为单行委托：
    - `self.toast_label = show_center_toast(self, message, attr_name="toast_label", duration_ms=500)`
  - 语义保持：
    - parent 仍为 `self`
    - 属性仍为 `self.toast_label`
    - 先关旧 toast
    - 样式、居中、透明鼠标、500ms 自动关闭保持一致

- 确认未修改 `show_toast` 调用方：
  - `main_window.py` 其他方法未改，仅 `show_toast` 方法体替换为 helper 委托。

- 确认未修改 week/month/todo_board toast：
  - `git diff --name-only -- src/ui/week_window.py`：无输出。
  - `git diff --name-only -- src/ui/month_window.py`：无输出。
  - `git diff --name-only -- src/ui/todo_board.py`：无输出。

- 确认未创建 tooltip 文件：
  - `Test-Path src\ui\common\tooltip.py`：`False`。

- helper import 验证结果：
  - 命令：
    - `python -c "from src.ui.common.toast import show_center_toast; print(...)" `
  - 输出：`toast helper import ok <function show_center_toast ...>`

- helper offscreen 行为验证结果：
  - 先执行了提示词原命令，失败原因：
    - 原命令使用 `label.WidgetAttribute.WA_TransparentForMouseEvents`，在 PyQt6 中 `QLabel` 不提供该枚举属性，触发 `AttributeError`。
  - 执行等价修正版（使用 `Qt.WidgetAttribute.WA_TransparentForMouseEvents`）后通过：
    - `label text hello`
    - `same attr True`
    - `transparent True`
    - `new label text world`
    - `old closed or hidden True`
  - 注：offscreen 且 parent 未 show 时 `label.isVisible()` 为 `False`，不影响属性/语义验证。

- MainWindow import 验证结果：
  - 输出：`main window import ok <class 'src.ui.main_window.MainWindow'>`

- MainWindow offscreen show_toast 回归结果：
  - 先执行了提示词原命令，失败原因同上（`w.toast_label.WidgetAttribute` 不存在）。
  - 执行等价修正版（`Qt.WidgetAttribute...`）后通过：
    - `toast attr True`
    - `toast text toast check`
    - `transparent True`
  - 注：offscreen 且窗口未 show 时 `toast visible False` 属预期环境现象。

- py_compile 结果：
  - 命令：
    - `python -m py_compile src/ui/common/toast.py src/ui/main_window.py main.py`
  - 结果：通过。

- main import 回归结果：
  - 命令：
    - `python -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; import main; print('main import ok')"`
  - 结果：`main import ok`

- diff 范围检查结果：
  - 禁止范围：
    - `src/theme` / `src/data` / `src/repositories` / `src/services` / `src/controllers` / `src/utils/signals.py` / `src/utils/styles.py` / `assets` / `main.py` / `requirements.txt` / `schedule.db`：均无 diff。
    - `src/ui/header.py`、`src/ui/components.py`、`src/ui/list_picker.py`、`src/ui/add_view.py`、`src/ui/add_view_week.py`、`src/ui/alarm_picker.py`、`src/ui/alarm_picker_week.py`：均无 diff。
  - `git diff --name-only -- src/ui`：
    - 输出仅 `src/ui/main_window.py`
    - 说明：`src/ui/common/toast.py` 为未跟踪新文件，`git diff` 不显示，已由 `git status` 确认。
  - `git status --short --branch`：
    - `M manage_instruction/Work_Log.md`
    - `M src/ui/main_window.py`
    - `?? src/ui/common/toast.py`
    - `M manage_instruction/Work_Task_Prompts.md`（开工前既有）
  - 当前总变更：
    - `src/ui/common/toast.py`
    - `src/ui/main_window.py`
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`（开工前既有）

- 未完成事项：
  - 8-3b 顾问窗口复核待完成。

- 风险或疑点：
  - 提示词中的两条 offscreen 验证命令存在 PyQt6 枚举访问写法问题（`label.WidgetAttribute`），执行窗口已保留失败记录并用等价修正版验证通过。
  - 未对 1500ms toast 路径做任何改动，符合本轮收口边界。

- 特别记录：
  - 本轮只提取 MainWindow toast。
  - 本轮不统一全部 toast。
  - 本轮不处理 tooltip。
  - 本轮不修改 QSS。
  - 本轮不修改 1500ms toast 路径。
  - 本轮不清理 8-2b 遗留的 `header.py` unused import。

## 2026-05-27 第八轮 8-4a（WeekWindow 低风险类提取候选只读复核）

- 本轮任务名称：第八轮 8-4a（WeekWindow 低风险类提取候选只读复核）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 28]`
  - 既有变更：`M manage_instruction/Work_Task_Prompts.md`
  - 说明：开工前已有管理文档 diff，本轮不视为源码问题。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有管理文档 diff，本轮未新增修改）

- 关键静态搜索命令与结果：
  - `rg -n "^class WeekScheduleCard|^class DayBlock|^class WeekWindow" src/ui/week_window.py`
    - `WeekScheduleCard`：L28
    - `DayBlock`：L198
    - `WeekWindow`：L290
  - `rg -n "^\\s*\\w+\\s*=\\s*pyqtSignal|clicked = pyqtSignal|scheduleDropped|card_dropped" ...`
    - `WeekScheduleCard`：`clicked/req_status/req_pin/req_delete`
    - `DayBlock`：`clicked(QDate)`
    - `WeekWindow`：`restore_requested/suspend_requested/request_schedule_detail/view_selected/schedule_updated`
    - `panel.card_dropped.connect(...)`：L605
  - `rg -n "db_manager|...|show_toast|...|pyqtSignal" src/ui/week_window.py`
    - 明确 `db_manager` 写库、`show_toast`、拖拽排序写回在 `WeekWindow` 中。
  - `rg -n "^from |^import " src/ui/week_window.py`
    - 依赖含 Qt、`db_manager`、`ScheduleQueryService`、`ScheduleSortService`、`ToolTipFilter`、`CountdownToolTipFilter`、`AdaptiveLabel`、`get_colored_icon`、`TodoListContainer`。

- `WeekScheduleCard` 定义范围与职责：
  - 定义范围：约 L28-L197（下一个类 `DayBlock` 起于 L198）。
  - 构造参数：`__init__(self, schedule_obj, parent=None)`。
  - 核心职责：
    - 渲染单条周日程卡片（标题、时间、优先级圆点、置顶图标）。
    - 发出详情点击与右键菜单动作信号。
    - 承担卡片拖拽源行为（`mousePressEvent/mouseMoveEvent/mouseReleaseEvent`）。
  - signal：
    - `clicked(object)`
    - `req_status(int, int)`
    - `req_pin(int, bool)`
    - `req_delete(int)`
  - event handler：
    - `mousePressEvent`
    - `mouseMoveEvent`（`QDrag/QMimeData` + 样式临时切换）
    - `mouseReleaseEvent`
    - `resizeEvent`（置顶图标定位）
    - `_show_context_menu`（`ScheduleContextMenu`）
  - tooltip / style / paint：
    - 使用 `CountdownToolTipFilter`，`installEventFilter`。
    - 含内联 `setStyleSheet`；无 `paintEvent`。
  - 外部依赖：
    - `AdaptiveLabel`
    - `CountdownToolTipFilter`
    - `get_colored_icon`
    - `ScheduleContextMenu`（函数内延迟 import）
  - 与 WeekWindow 反向访问点：
    - `WeekWindow` 在加载卡片时连接 `clicked/req_status/req_pin/req_delete`（L1044-L1047）。
    - 拖拽流程依赖父容器的 `current_drag_widget` 约定字段。
  - 生命周期管理点：
    - `WeekWindow.load_week_schedules_from_db` 中旧卡片 `deleteLater`（L1028）。
    - 本类未显式清理 `CountdownToolTipFilter`。
  - 与拖拽/排序/详情/toast/刷新链路关系：
    - 与拖拽强耦合（拖拽源）。
    - 间接触发详情弹窗（通过 `clicked -> request_schedule_detail`）。
    - 右键菜单动作落到 WeekWindow 写库和刷新。
  - 是否直接访问 db_manager / Repository / Service：
    - 否（无直接 `db_manager` 调用）。
  - 提取风险等级：中高。
    - 原因：拖拽源行为 + 右键菜单信号 + tooltip filter + 父容器约定字段，多边界联动。

- `DayBlock` 定义范围与职责：
  - 定义范围：约 L198-L289（下一个类 `WeekWindow` 起于 L290）。
  - 构造参数：`__init__(self, parent=None)`。
  - 核心职责：
    - 渲染顶部日期格（阳历日、农历简写）。
    - 处理选中态/今日态样式。
    - 维护日期 tooltip（阳历+农历完整文案）。
    - 点击后发出选日信号。
  - signal：
    - `clicked(QDate)`
  - event handler：
    - `mouseReleaseEvent`（发出 clicked）。
    - 无拖拽 `dragEnter/dragMove/drop`。
  - tooltip / style / paint：
    - 使用 `ToolTipFilter`，在 `set_data` 中替换旧 filter（`removeEventFilter + deleteLater + installEventFilter`）。
    - 仅内联 `setStyleSheet`；无 `paintEvent`。
  - 外部依赖：
    - `ZhDate`、`datetime/timedelta`（农历计算）
    - `ToolTipFilter`
    - `QDate/QLabel/QFrame`
  - 与 WeekWindow 反向访问点：
    - `WeekWindow` 创建 `self.day_blocks`，连接 `block.clicked -> _on_day_clicked`（L538-L540）。
    - `WeekWindow` 在刷新日期条时调用 `set_data/set_selected`（L997-L1001）。
  - 生命周期管理点：
    - 自身 tooltip filter 生命周期在 `set_data` 内部自清理并重绑。
  - 与拖拽/排序/详情/toast/刷新链路关系：
    - 不参与卡片拖拽排序。
    - 不直接触发详情弹窗。
    - 仅通过选日触发周视图刷新链路。
  - 是否直接访问 db_manager / Repository / Service：
    - 否。
  - 是否管理 `WeekScheduleCard` 实例：
    - 否（仅管理日期展示，不持有卡片容器）。
  - 提取风险等级：低到中。
    - 原因：职责单一、无写库、无拖拽排序、信号单一。

- 二者风险对比结论：
  - `DayBlock` 明显低于 `WeekScheduleCard`。
  - `WeekScheduleCard` 当前仍耦合拖拽源行为与右键菜单动作信号，不适合作为首个提取试点。

- 8-4b 建议的唯一候选类：
  - 建议：`DayBlock`（唯一候选）。
  - 8-4b 范围建议：仅提取 `DayBlock` 到新文件并保持 WeekWindow 调用/行为不变，不触碰 `WeekScheduleCard`。

- 若不建议直接提取的说明：
  - 对 `WeekScheduleCard` 不建议在 8-4b 同步提取。
  - 建议后续先补一轮 `WeekScheduleCard` 拖拽/右键菜单/tooltip 生命周期基线后，再评估单独拆分。

- 验证回归结果：
  - `Test-Path src\ui\common\week_cards.py`：`False`
  - `Test-Path src\ui\views\week_window.py`：`False`
  - `Test-Path src\ui\views\week_cards.py`：`False`
  - WeekWindow import 回归：
    - `week imports ok <class 'src.ui.week_window.WeekWindow'> <class 'src.ui.week_window.WeekScheduleCard'> <class 'src.ui.week_window.DayBlock'>`
  - 8-3b toast helper 回归：
    - `toast helper import ok <function show_center_toast ...>`
  - 8-2b icon loader 回归：
    - `icon loader import ok <function load_colored_svg_pixmap ...>`

- diff 范围检查结果：
  - `git diff --name-only -- src`：无输出。
  - `git diff --name-only -- assets`：无输出。
  - `git diff --name-only -- main.py`：无输出。
  - `git diff --name-only -- requirements.txt`：无输出。
  - `git diff --name-only -- schedule.db`：无输出。
  - `git diff --name-only`：`manage_instruction/Work_Task_Prompts.md`（开工前既有）+ `manage_instruction/Work_Log.md`（本轮）。
  - `git status --short --branch`：
    - `## main...temp/main [ahead 28]`
    - `M manage_instruction/Work_Task_Prompts.md`
    - `M manage_instruction/Work_Log.md`

- 未完成事项：
  - 等待顾问窗口确认 8-4b 是否按 `DayBlock` 单类提取推进。

- 风险或疑点：
  - `DayBlock.set_data` 包含农历异常兜底 `except Exception`，虽不影响本轮只读判断，但 8-4b 抽取时需保持原异常策略不变。
  - `WeekScheduleCard` 与父容器 `current_drag_widget` 的隐式契约较脆弱，后续拆分若处理不当易引入拖拽回归。

- 特别记录：
  - 本轮只读审查，不改源码。
  - 本轮不拆 `week_window.py`。
  - 本轮不新增任何 WeekWindow 组件文件。
  - 本轮不修改 tooltip/toast/icon loader。
  - 本轮仅用于为 8-4b 锁定唯一候选类。

## 2026-05-27 第八轮 8-4b（WeekWindow DayBlock 单类提取试点）

- 本轮任务名称：第八轮 8-4b（WeekWindow DayBlock 单类提取试点）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 29]`
  - 既有变更：`M manage_instruction/Work_Task_Prompts.md`
  - 说明：开工前已有管理文档 diff，本轮不视为源码问题。
- 实际修改文件：
  - `src/ui/common/week_day_block.py`（新增）
  - `src/ui/week_window.py`
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有管理文档 diff，本轮未新增修改）

- `DayBlock` 新文件路径：
  - `src/ui/common/week_day_block.py`

- `DayBlock` 保持兼容内容确认：
  - 类名：`DayBlock`
  - signal：`clicked = pyqtSignal(QDate)`
  - 构造函数：`__init__(self, parent=None)`
  - 方法保留：`set_data`、`set_selected`、`update_style`、`mouseReleaseEvent`
  - tooltip 逻辑保留：
    - `removeEventFilter` / `deleteLater` / `installEventFilter`
    - `ToolTipFilter` 文案格式保持 `阳历：...\n农历：...`
  - 农历异常兜底保留：
    - `except Exception: pass` 原样保留
  - 样式字符串与控件结构保持不变。

- `week_window.py` import 替换说明：
  - 新增导入：`from .common.week_day_block import DayBlock`
  - 删除原文件内联 `DayBlock` 类定义（仅此一段迁移）
  - `WeekWindow` 对 `DayBlock` 的使用方式未改（`self.day_blocks`、`block.clicked.connect(...)`、`set_data(...)`、`set_selected(...)` 保持原样）。

- 确认边界：
  - 未修改 `WeekScheduleCard`。
  - 未修改 `WeekWindow` 拖拽/排序/写库逻辑。
  - 未修改 `WeekWindow.show_toast`。
  - 未修改 tooltip 公共实现。
  - 未修改 icon loader / toast helper。

- 验收命令结果：
  - 定位新旧位置：
    - `rg -n "^class DayBlock|from .*week_day_block import DayBlock|DayBlock" ...`
    - 结果：`DayBlock` 类仅在 `src/ui/common/week_day_block.py`，`week_window.py` 为导入和使用点。
  - `WeekScheduleCard` 未迁移检查：
    - `rg -n "^class WeekScheduleCard|CountdownToolTipFilter|current_drag_widget|req_status|req_pin|req_delete" src/ui/week_window.py`
    - 结果：命中均在 `week_window.py`，符合“只提取 DayBlock”。
  - 未新增禁止文件：
    - `Test-Path src\ui\common\week_cards.py`：`False`
    - `Test-Path src\ui\views\week_window.py`：`False`
    - `Test-Path src\ui\views\week_cards.py`：`False`
  - DayBlock import 验证：
    - `day block import ok <class 'src.ui.common.week_day_block.DayBlock'>`
  - WeekWindow import 回归：
    - `week imports ok <class 'src.ui.week_window.WeekWindow'> <class 'src.ui.week_window.WeekScheduleCard'> <class 'src.ui.common.week_day_block.DayBlock'>`
  - DayBlock offscreen 基础实例化验证：
    - 提示词原命令失败（命令与现有接口不一致）：
      - `set_data(QDate.currentDate(), False)` 将 `bool` 传给 `QLabel.setText`，触发 `TypeError`
      - 并且命令读取 `b.date_obj`，而类原有字段为 `b.date`
    - 等价兼容回归命令通过（保持类语义不改）：
      - `set_data(QDate.currentDate(), '初一')`
      - 校验 `b.date == QDate.currentDate()`
      - 输出：`day block created True`、`selected true ok`、`selected false ok`
  - WeekWindow offscreen 基础实例化验证：
    - 输出：`week window created True`、`day blocks 7`
  - 8-3b toast helper 回归：
    - `toast helper import ok <function show_center_toast ...>`
  - 8-2b icon loader 回归：
    - `icon loader import ok <function load_colored_svg_pixmap ...>`
  - main import 回归：
    - `main import ok`
  - py_compile：
    - `python -m py_compile src/ui/common/week_day_block.py src/ui/week_window.py main.py`
    - 结果：通过。

- diff 范围检查结果：
  - 禁止范围均无 diff：
    - `src/ui/components.py`、`src/ui/header.py`、`src/ui/common/toast.py`、`src/ui/utils/icon_loader.py`
    - `src/ui/todo_board.py`、`src/ui/month_window.py`、`src/ui/main_window.py`、`src/ui/dashboard.py`
    - `src/ui/add_view.py`、`src/ui/add_view_week.py`
    - `src/theme`、`src/data`、`src/repositories`、`src/services`、`src/controllers`
    - `src/utils/signals.py`、`src/utils/styles.py`
    - `assets`、`main.py`、`requirements.txt`、`schedule.db`
  - `git diff --name-only -- src/ui`：
    - 仅显示 `src/ui/week_window.py`（新增文件在 `git diff` 中不显示）
  - `git status --short --branch`：
    - `M src/ui/week_window.py`
    - `?? src/ui/common/week_day_block.py`
    - `M manage_instruction/Work_Log.md`
    - `M manage_instruction/Work_Task_Prompts.md`（开工前既有）
  - 当前总变更符合本轮允许范围：
    - `src/ui/common/week_day_block.py`
    - `src/ui/week_window.py`
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`（开工前既有）

- 未完成事项：
  - 等待顾问窗口复核 8-4b 结果。

- 风险或疑点：
  - 提示词中的 DayBlock offscreen 命令与既有接口不一致（`bool` 文案参数、`date_obj` 字段名）；执行窗口已保留失败记录并使用等价命令完成行为回归，不对类语义做额外“适配性改造”。

- 特别记录：
  - 本轮只提取 `DayBlock`。
  - 本轮不提取 `WeekScheduleCard`。
  - 本轮不拆 `WeekWindow` 主流程。
  - 本轮不修改周视图业务行为。
  - 本轮不修改 tooltip/toast/icon loader。
  - 本轮不修改数据库或服务层。

## 2026-05-27 第八轮 8-5（TodoBoard 只读基线与低风险拆分候选确认）

- 本轮任务名称：第八轮 8-5（TodoBoard 只读基线与低风险拆分候选确认）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 30]`
  - 既有变更：`M manage_instruction/Work_Task_Prompts.md`
  - 说明：开工前已有管理文档 diff，本轮不视为源码问题。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有管理文档 diff，本轮未新增修改）

- `todo_board.py` 类/函数结构地图：
  - 顶层 helper：
    - `get_colored_icon(...)`（L18）
  - 卡片/容器类：
    - `StickyNoteCard`（L47）
    - `DropWidget`（L233）
    - `StickViewContainer`（L253）
    - `FolderCard`（L429）
    - `AddFolderCard`（L571）
    - `FolderViewContainer`（L617）
    - `ManageCategoryCard`（L784）
    - `ManageListView`（L827）
    - `InlineAddTodoView`（L1006）
  - 主状态机窗口：
    - `TodoBoardWindow`（L1216）

- 主状态机字段与职责地图（`TodoBoardWindow`）：
  - 核心状态字段：
    - `view_mode`（`stick/folder`）
    - `current_folder_id`、`current_folder_name`
    - `view_stack`（`manage_list_view/stick_view/folder_view/empty_placeholder/inline_add_view/page_list`）
    - `_last_signature`（防闪烁签名）
    - `list_picker_mode`、`editing_schedule`（编辑清单回流）
    - `is_pinned`、`_drag_pos`
  - 核心职责：
    - 数据刷新与签名短路（`refresh_data`）
    - 视图模式切换与导航图标状态（`_switch_view/_update_nav_icons`）
    - 文件夹内外路由（`_open_folder_view/_back_to_folder_view`）
    - 编辑清单回流（`go_to_list_picker* / on_list_confirmed / back_from_list_picker`）
    - 详情弹窗借道主面板（`_show_detail_popup`）
    - 全局刷新通知（`notify_main_window_refresh`）
    - 一键排序与写回（`_sort_by_priority`）

- 写库调用地图：
  - 日程写入/更新：
    - `db_manager.add_schedule`（InlineAddTodoView 保存）
    - `db_manager.update_schedule_with_repeat`（编辑清单）
    - `db_manager.update_schedule_status` / `toggle_pin_status` / `delete_schedule`
    - `db_manager.update_schedule_fields(..., sort_order=...)`（便签排序写回）
  - 清单写入/删除：
    - `db_manager.add_category`
    - `db_manager.check_category_status`
    - `db_manager.soft_delete_category` / `hard_delete_category`
    - `db_manager.update_category_fields(..., sort_order=...)`（文件夹排序写回）
  - 读取：
    - `db_manager.get_all_schedules`、`get_active_categories`、`get_category`

- 拖拽/排序/写回链路地图：
  - 便签拖拽：
    - `StickyNoteCard.mouseMoveEvent` -> `DropWidget.dragMoveEvent/dropEvent` -> `StickViewContainer._handle_drag_move/_reorder_layout/_save_new_order`
    - 写回：`update_schedule_fields(sort_order=...)`
  - 文件夹拖拽：
    - `FolderCard.mouseMoveEvent` -> `FolderViewContainer._handle_drag_move/_reorder_layout/_save_new_order`
    - 写回：`update_category_fields(sort_order=...)`
  - 主窗口排序按钮：
    - `TodoBoardWindow._sort_by_priority` -> 批量 `update_schedule_fields(sort_order=...)`

- toast / tooltip / icon loader 地图：
  - toast：
    - `TodoBoardWindow.show_toast`（1500ms，居中，`toast_label`）
    - `InlineAddTodoView._on_save` 与 `ManageListView` 删除分支借用 `window().show_toast(...)`
  - tooltip：
    - `TodoBoardWindow._apply_custom_tooltip` 通过 `header.ToolTipFilter` 绑定顶部按钮
  - icon loader：
    - 顶层 `get_colored_icon`（大量卡片/内联视图复用）
    - `TodoBoardWindow._get_icon`（SVG/位图双分支，导航按钮专用）

- 跨视图与详情弹窗回流地图：
  - 详情弹窗借道：
    - `TodoBoardWindow._show_detail_popup` -> `main_win.page_dashboard._show_detail_popup(..., source_view='todo_board')`
    - 后续遍历 `open_popups` 调整位置
  - 跨视图刷新：
    - `notify_main_window_refresh` 直接调用 `parent.page_todo.refresh_data()`
    - 同时 `parent.page_dashboard.req_refresh_all.emit()`
  - 初始化连接：
    - 监听 `parent.page_add.saved`、`parent.page_dashboard.req_refresh_all`、`parent.page_todo.req_refresh_all`
  - 弹窗数据同步：
    - `refresh_data` 内遍历 `page_dashboard.open_popups` 并刷新弹窗字段显示

- `FolderCard` 定义范围、职责、依赖、风险等级：
  - 定义范围：L429-L570
  - 构造签名：`__init__(self, category_id, category_name, is_empty, parent=None)`
  - signal：
    - `clicked(object)`
    - `doubleClicked(object, str)`
    - `delete_requested(int, str)`
  - public 属性：`category_id/category_name/is_empty/icon_label/name_label`
  - event handler：
    - `_show_context_menu`
    - `mouseDoubleClickEvent`
    - `mousePressEvent/mouseMoveEvent/mouseReleaseEvent`（含 QDrag）
  - 依赖：
    - `get_colored_icon`
    - `QMenu/QAction`
    - 父容器 `current_drag_widget` 隐式契约
  - db_manager：无直接调用
  - 是否直接调用 TodoBoardWindow：无直接调用，但通过父容器拖拽契约和信号与主状态机强耦合
  - 是否依赖 `view_mode/current_folder_id/view_stack`：不直接依赖
  - 是否参与拖拽/排序写回：是（文件夹拖拽入口）
  - 是否依赖 toast / tooltip / icon loader：依赖 icon loader
  - 提取所需 import：`QFrame/QVBoxLayout/QLabel/QMenu/QAction/QDrag/QMimeData/Qt/pyqtSignal/get_colored_icon`
  - 提取后调用方改动：`FolderViewContainer` 创建与 `isinstance(FolderCard)` 判断、拖拽类型判断
  - 风险等级：中（交互较多，拖拽链路敏感）

- `AddFolderCard` 定义范围、职责、依赖、风险等级：
  - 定义范围：L571-L616
  - 构造签名：`__init__(self, parent=None)`
  - signal：`clicked()`
  - public 属性：`icon_label/name_label`
  - event handler：`mouseReleaseEvent`（只发 `clicked`）
  - 依赖：`get_colored_icon`、基础 Qt 组件
  - db_manager：无
  - 是否直接调用 TodoBoardWindow：无（仅 signal）
  - 是否依赖 `view_mode/current_folder_id/view_stack`：无
  - 是否参与拖拽/排序写回：否
  - 是否依赖 toast / tooltip / icon loader：仅 icon loader
  - 提取所需 import：`QFrame/QVBoxLayout/QLabel/Qt/pyqtSignal/get_colored_icon`
  - 提取后调用方改动：`FolderViewContainer` 中实例化与 `clicked` 连接
  - 风险等级：低（纯展示+单击信号）

- 其它候选类或 helper 风险等级：
  - `ManageCategoryCard`：中（右键删除动作链路）
  - `FolderViewContainer`：中高（拖拽排序写回 + 卡片类型判断）
  - `StickViewContainer`：高（便签拖拽/排序写回 + 主窗口刷新回流）
  - `InlineAddTodoView`：高（写库、校验、清单 picker 入口）
  - `TodoBoardWindow`：高（主状态机，跨视图桥接，弹窗借道，刷新定时器）
  - 顶层 `get_colored_icon`：中（复用面广，改动需联动验证）

- 高风险暂缓项：
  - `TodoBoardWindow` 主状态机整体迁移
  - `view_mode/current_folder_id/view_stack` 状态流迁移
  - sort_order 写回链路（便签/文件夹）
  - `go_to_list_picker* / on_list_confirmed / back_from_list_picker`
  - 详情弹窗借道 `page_dashboard._show_detail_popup`
  - `notify_main_window_refresh` 跨视图刷新链路

- 8-6 建议的唯一候选类：
  - 建议唯一候选：`AddFolderCard`
  - 原因：依赖最少、无拖拽、无写库、无状态机字段、回归成本最低。
  - 不建议 8-6 直接提取 `FolderCard`（拖拽与上下文菜单交互较多，风险更高）。

- 若不建议直接提取的补充：
  - 若顾问窗口认为仍需更保守，建议 8-6 先做 `todo_board.py` 局部 import 边界清理（只读/微调）再提取 `AddFolderCard`。

- 验证回归结果：
  - 未新增 TodoBoard 拆分文件：
    - `Test-Path src\ui\common\todo_board_cards.py`：`False`
    - `Test-Path src\ui\views\todo_board.py`：`False`
    - `Test-Path src\ui\views\todo_board_cards.py`：`False`
  - TodoBoard import 回归：
    - `todo board import ok <class 'src.ui.todo_board.TodoBoardWindow'>`
  - 8-4b DayBlock 回归：
    - `day block import ok <class 'src.ui.common.week_day_block.DayBlock'>`
  - 8-3b toast helper 回归：
    - `toast helper import ok <function show_center_toast ...>`
  - 8-2b icon loader 回归：
    - `icon loader import ok <function load_colored_svg_pixmap ...>`

- diff 范围检查结果：
  - `git diff --name-only -- src`：无输出。
  - `git diff --name-only -- assets`：无输出。
  - `git diff --name-only -- main.py`：无输出。
  - `git diff --name-only -- requirements.txt`：无输出。
  - `git diff --name-only -- schedule.db`：无输出。
  - 当前总 diff：
    - `manage_instruction/Work_Log.md`（本轮）
    - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
  - `git status --short --branch`：
    - `## main...temp/main [ahead 30]`
    - `M manage_instruction/Work_Task_Prompts.md`
    - `M manage_instruction/Work_Log.md`

- 未完成事项：
  - 等待顾问窗口确认 8-6 是否按 `AddFolderCard` 单类提取推进。

- 风险或疑点：
  - `todo_board.py` 同时存在顶层 `get_colored_icon` 和成员 `_get_icon` 两套图标路径，后续若要统一需要单独小工单，不能与 8-6 类提取并行。
  - `FolderViewContainer._save_new_order` 依赖 `isinstance(FolderCard)` 与“最后一个 AddFolderCard 保留位”，若后续提取 `FolderCard` 风险高于 `AddFolderCard`。

- 特别记录：
  - 本轮只读审查，不改源码。
  - 本轮不拆 `todo_board.py`。
  - 本轮不新增任何 TodoBoard 组件文件。
  - 本轮不修改 tooltip/toast/icon loader。
  - 本轮不修改数据库或服务层。
  - 本轮仅用于为 8-6 判断唯一低风险候选类。

## 2026-05-27 第八轮 8-6（TodoBoard AddFolderCard 单类提取试点）

- 本轮任务名称：第八轮 8-6（TodoBoard AddFolderCard 单类提取试点）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 31]`
  - 既有变更：`M manage_instruction/Work_Task_Prompts.md`
  - 说明：开工前已有管理文档 diff，本轮不视为源码问题。
- 实际修改文件：
  - `src/ui/common/todo_board_add_folder_card.py`（新增）
  - `src/ui/todo_board.py`
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有管理文档 diff，本轮未新增修改）

- `AddFolderCard` 新文件路径：
  - `src/ui/common/todo_board_add_folder_card.py`

- `AddFolderCard` 保持兼容内容：
  - 类名：`AddFolderCard`
  - signal：`clicked = pyqtSignal()`
  - 构造函数：`__init__(self, parent=None)`
  - 方法保留：`mouseReleaseEvent(...)`
  - 图标加载语义：
    - 保持调用 `get_colored_icon(...)` 进行 SVG 染色加载
    - 保持原有参数：`("folder_add.svg", "#FFFFFF", 45)`（与现有代码一致）
  - 样式字符串保留（透明背景 + hover 轻微高亮）
  - 点击发射逻辑保留（左键 emit `clicked`）
  - 鼠标指针设置保留（`PointingHandCursor`）

- `todo_board.py` import 替换说明：
  - 新增导入：`from .common.todo_board_add_folder_card import AddFolderCard`
  - 删除原内联 `AddFolderCard` 类定义
  - `FolderViewContainer` 中 `AddFolderCard` 实例化与 `clicked.connect(...)` 逻辑未改

- 循环导入风险及判断依据：
  - 新文件未在模块顶层导入 `src.ui.todo_board.get_colored_icon`，而是在 `AddFolderCard.__init__` 内做延迟导入：
    - `from ..todo_board import get_colored_icon`
  - 判断依据：
    - `todo_board.py` 模块导入阶段先定义顶层 `get_colored_icon`，再导入 `AddFolderCard` 文件；
    - `AddFolderCard` 类本身在导入阶段不触发 `__init__`，不会立即反向导入；
    - 运行时创建 `AddFolderCard()` 时，`todo_board` 模块已加载完成，导入可解析。
  - 实际回归结果（见下）验证当前无循环导入异常。

- 确认边界未越界：
  - 未修改 `FolderCard`
  - 未修改 `FolderViewContainer` 拖拽/排序/写回逻辑
  - 未修改 `TodoBoardWindow` 主状态机
  - 未修改 `TodoBoardWindow.show_toast`
  - 未修改 `get_colored_icon` 实现
  - 未修改 `_get_icon` 实现
  - 未新增 `src/ui/common/todo_board_cards.py` / `src/ui/views/todo_board.py`

- 验收命令结果：
  - 定位新旧位置：
    - `rg -n "^class AddFolderCard|from .*todo_board_add_folder_card import AddFolderCard|AddFolderCard" ...`
    - 结果：`AddFolderCard` 类仅在新文件；`todo_board.py` 保留导入与使用点。
  - `FolderCard` 未迁移检查：
    - `rg -n "^class FolderCard|doubleClicked|delete_requested|current_drag_widget|QDrag|QMimeData" src/ui/todo_board.py`
    - 结果：命中均在 `todo_board.py`，符合“只提取 AddFolderCard”。
  - 未新增禁止文件：
    - `Test-Path src\ui\common\todo_board_cards.py`：`False`
    - `Test-Path src\ui\views\todo_board.py`：`False`
    - `Test-Path src\ui\views\todo_board_cards.py`：`False`
  - AddFolderCard import 验证：
    - `add folder card import ok <class 'src.ui.common.todo_board_add_folder_card.AddFolderCard'>`
  - TodoBoard import 回归：
    - `todo board imports ok <class 'src.ui.todo_board.TodoBoardWindow'> <class 'src.ui.todo_board.FolderCard'> <class 'src.ui.common.todo_board_add_folder_card.AddFolderCard'>`
  - AddFolderCard offscreen 基础实例化验证：
    - `add folder card created True`
    - `cursor PointingHandCursor`
    - `has icon label True`
    - `has name label True`
  - TodoBoardWindow offscreen 基础实例化验证：
    - `todo board created True`
    - `view mode stick`
  - 8-4b DayBlock 回归：
    - `day block import ok <class 'src.ui.common.week_day_block.DayBlock'>`
  - 8-3b toast helper 回归：
    - `toast helper import ok <function show_center_toast ...>`
  - 8-2b icon loader 回归：
    - `icon loader import ok <function load_colored_svg_pixmap ...>`
  - 默认入口 import 回归：
    - `main import ok`
  - 语法检查：
    - `python -m py_compile src/ui/common/todo_board_add_folder_card.py src/ui/todo_board.py main.py`
    - 结果：通过。

- diff 范围检查结果：
  - 禁止范围均无 diff：
    - `src/ui/common/todo_board_cards.py`
    - `src/ui/common/toast.py`
    - `src/ui/common/week_day_block.py`
    - `src/ui/utils/icon_loader.py`
    - `src/ui/components.py`
    - `src/ui/header.py`
    - `src/ui/week_window.py`
    - `src/ui/month_window.py`
    - `src/ui/main_window.py`
    - `src/ui/dashboard.py`
    - `src/ui/add_view.py`
    - `src/ui/add_view_week.py`
    - `src/theme` / `src/data` / `src/repositories` / `src/services` / `src/controllers`
    - `src/utils/signals.py` / `src/utils/styles.py`
    - `assets` / `main.py` / `requirements.txt` / `schedule.db`
  - `git diff --name-only -- src/ui`：
    - 显示：`src/ui/todo_board.py`
    - 说明：新增文件 `src/ui/common/todo_board_add_folder_card.py` 为未跟踪，`git diff` 不显示，已由 `git status` 确认。
  - `git status --short --branch`：
    - `M src/ui/todo_board.py`
    - `?? src/ui/common/todo_board_add_folder_card.py`
    - `M manage_instruction/Work_Log.md`
    - `M manage_instruction/Work_Task_Prompts.md`（开工前既有）
  - 当前总变更符合本轮允许范围：
    - `src/ui/common/todo_board_add_folder_card.py`
    - `src/ui/todo_board.py`
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`（开工前既有）

- 未完成事项：
  - 等待顾问窗口复核 8-6 结果。

- 风险或疑点：
  - `AddFolderCard` 在新文件内通过延迟导入复用 `todo_board.get_colored_icon`，当前回归通过，但后续若移动/重命名 `todo_board.py` 需要同步调整该导入路径。

- 特别记录：
  - 本轮只提取 `AddFolderCard`。
  - 本轮不提取 `FolderCard`。
  - 本轮不拆 `TodoBoardWindow` 主状态机。
  - 本轮不修改待办看板业务行为。
  - 本轮不修改 tooltip/toast/icon loader。
  - 本轮不修改数据库或服务层。
