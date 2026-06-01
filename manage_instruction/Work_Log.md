# Work Log

用途：记录当前阶段/当前小工单的执行过程、验证结果和风险。

历史日志归档见：

- `History_Log.md`

旧架构改写阶段日志已移入：

- `ReconstructionDolder/History_Log.md`

---

## 当前状态

架构改写主线已经结束。

当前进入功能补充阶段，优先完善月界面功能。暂不优先实现四象限视图。

---

## 2026-05-29 工作文档重建

- 背景：
  - 旧 `manage_instruction` 文档已由用户移入 `ReconstructionDolder/`。
  - 当前需要为后续三窗口联动重新建立轻量工作文档。

- 新建/重建文件：
  - `History_Instruction.md`
  - `History_Log.md`
  - `Workflow_Guide.md`
  - `Work_Formulation.md`
  - `Work_Instruction.md`
  - `Work_Log.md`
  - `Work_Task_Prompts.md`

- 不重建文件：
  - `code_pack.txt`
  - `Device_Sync_Guide.md`
  - `Work_Snapshot.md`
  - `Work_Discussion.md`

- 当前协作模式：
  - 主窗口：调度、审核、决策收口、最终提示词输出。
  - 决策窗口：提出方案供主窗口审核。
  - 执行窗口：按最终提示词执行具体任务。

- 当前阶段规划：
  - 先完善月界面。
  - 可穿插处理低风险交互增强，例如周界面日期双击跳转日视图。
  - 月界面稳定后，再制定后续功能补充规划。

- 未完成事项：
  - 尚未发布具体 M-0 / W-1 执行提示词。

- 风险或疑点：
  - 旧文档移入 `ReconstructionDolder/` 后，Git 当前可能显示旧文件删除和新文件重建，需要主窗口复核 diff 后再提交。

## 2026-05-29 功能补充 W-1（周界面日期双击跳转日视图）

- 本轮任务名称：功能补充 W-1（周界面日期双击跳转日视图）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 39]`
  - 既有变更：`M manage_instruction/Work_Task_Prompts.md`
  - 说明：开工前已有管理文档 diff，本轮不视为源码问题。
- 实际修改文件：
  - `src/ui/common/week_day_block.py`
  - `src/ui/week_window.py`
  - `src/ui/main_window.py`
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有 diff，本轮未新增修改）

- `DayBlock` 新增信号和事件说明：
  - 新增信号：`double_clicked = pyqtSignal(QDate)`。
  - 新增方法：`mouseDoubleClickEvent(self, event)`。
  - 左键双击时：`emit self.double_clicked(self.date)` 并 `event.accept()`。
  - 非左键双击时：调用 `super().mouseDoubleClickEvent(event)`。
  - 保持 `clicked = pyqtSignal(QDate)` 与 `mouseReleaseEvent(...)` 单击语义不变。

- `WeekWindow` 新增信号和转发说明：
  - 新增信号：`day_double_clicked = pyqtSignal(QDate)`。
  - `DayBlock` 连接：
    - 保留 `block.clicked.connect(self._on_day_clicked)`。
    - 新增 `block.double_clicked.connect(self._on_day_double_clicked)`。
  - 新增 `_on_day_double_clicked(self, qdate)`：
    - 先调用 `self._on_day_clicked(qdate)` 保持选中行为；
    - 再 `self.day_double_clicked.emit(qdate)` 转发给主窗口。

- `MainWindow` 日期跳转方法泛化说明：
  - 新增 `jump_to_date(self, qdate)`：
    - `py_date = qdate.toPyDate()`
    - `self.on_calendar_date_picked(py_date)`
    - `self.switch_view("day")`
  - 保留 `jump_to_date_from_month(self, qdate)` 方法名，改为调用 `self.jump_to_date(qdate)`。
  - 新增连接：`self.week_window.day_double_clicked.connect(self.jump_to_date)`。

- 单击行为是否保持不变：
  - 是。单击日期仍只更新周视图选中日期，不触发日视图跳转。

- 添加日程日期来源是否保持不变：
  - 是。`WeekWindow.switch_to_add_page(...)` 仍使用当前 `current_selected_date`，本轮未修改。

- 验证结果：
  - 链路定位命令通过：
    - `rg -n "double_clicked|day_double_clicked|mouseDoubleClickEvent|jump_to_date|jump_to_date_from_month|_on_day_double_clicked|_on_day_clicked" ...`
  - DayBlock import：
    - `day block import ok <class 'src.ui.common.week_day_block.DayBlock'>`
  - WeekWindow import：
    - `week import ok <class 'src.ui.week_window.WeekWindow'> <class 'src.ui.common.week_day_block.DayBlock'>`
  - MainWindow import：
    - `main window import ok <class 'src.ui.main_window.MainWindow'>`
  - DayBlock offscreen 信号验证：
    - 输出：`hits [('double', PyQt6.QtCore.QDate(2026, 5, 30))]`
    - 断言通过：双击仅触发 `double_clicked`，且日期正确。
  - WeekWindow offscreen 连接验证：
    - 输出：`selected 2026-05-31`，`hits ['2026-05-31']`
    - 断言通过：双击后选中日期与对外信号一致。
  - MainWindow offscreen 方法验证：
    - 输出：`dashboard date 2026-06-01`
    - 断言通过：跳转后日视图日期更新，并保留 `jump_to_date_from_month`。
  - 语法检查：
    - `python -m py_compile src/ui/common/week_day_block.py src/ui/week_window.py src/ui/main_window.py main.py`
    - 结果：通过。

- diff 范围检查结果：
  - 禁止范围均无 diff：
    - `src/ui/month_window.py`
    - `src/ui/dashboard.py`
    - `src/ui/add_view.py`
    - `src/ui/add_view_week.py`
    - `src/ui/todo_board.py`
    - `src/ui/common/toast.py`
    - `src/ui/utils/icon_loader.py`
    - `src/controllers`
    - `src/data`
    - `src/repositories`
    - `src/services`
    - `src/theme`
    - `src/utils/signals.py`
    - `src/utils/styles.py`
    - `assets`
    - `main.py`
    - `requirements.txt`
    - `schedule.db`
  - 允许范围：
    - `git diff --name-only -- src/ui` 仅：
      - `src/ui/common/week_day_block.py`
      - `src/ui/main_window.py`
      - `src/ui/week_window.py`
  - 总范围：
    - `git diff --name-only`：
      - `manage_instruction/Work_Log.md`
      - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
      - `src/ui/common/week_day_block.py`
      - `src/ui/main_window.py`
      - `src/ui/week_window.py`
    - `git status --short --branch`：
      - `## main...temp/main [ahead 39]`
      - `M manage_instruction/Work_Log.md`
      - `M manage_instruction/Work_Task_Prompts.md`
      - `M src/ui/common/week_day_block.py`
      - `M src/ui/main_window.py`
      - `M src/ui/week_window.py`

- 未完成事项：
  - 等待决策/顾问窗口复核本轮变更。

- 风险或疑点：
  - `DayBlock.mouseReleaseEvent(...)` 旧实现本就未调用 `super()`；本轮保持原样，未扩大修改范围。

### 主窗口复核补记

- 复核时间：2026-05-29。
- 对照 `Work_Task_Prompts.md`：
  - `DayBlock.double_clicked`、`mouseDoubleClickEvent(...)` 已按提示词实现。
  - `WeekWindow.day_double_clicked` 与 `_on_day_double_clicked(...)` 已按提示词实现。
  - `MainWindow.jump_to_date(...)` 已复用 `on_calendar_date_picked(py_date)`，`jump_to_date_from_month(...)` 保持兼容。
  - 单击链路仍为 `DayBlock.clicked -> WeekWindow._on_day_clicked(...)`。
  - 添加日程日期来源 `current_selected_date` 未被修改。
- 主窗口复跑验证：
  - 链路定位、DayBlock import、WeekWindow import、MainWindow import：通过。
  - DayBlock offscreen 双击信号验证：通过。
  - WeekWindow offscreen 转发验证：通过。
  - MainWindow offscreen 跳转验证：通过。
  - `py_compile`：通过。
  - 禁止范围检查：无越界 diff。
- 复核修正：
  - 原执行日志的总范围漏列 `manage_instruction/Work_Log.md`，已补正；源码未因复核发生额外修改。

## 2026-05-29 右键上下文菜单功能规划

- 本轮任务名称：主界面 / 周界面右键上下文菜单规划。
- 开工前 git 状态：
  - 原规划记录时为 `## main...temp/main [ahead 39]`，当时存在 W-1 未提交变更。
  - 提交前复核时 W-1 已提交：`792ab6c feat: jump to day view on week date double click`。
  - 当前状态为 `## main...temp/main [ahead 40]`，仅管理文档存在 diff。
  - 本轮只做管理文档规划，不新增源码修改。

- 读取的历史规划依据：
  - `manage_instruction/ReconstructionDolder/Work_Formulation.md`
  - `manage_instruction/ReconstructionDolder/History_Instruction.md`
  - `manage_instruction/ReconstructionDolder/Workflow_Guide.md`
  - 关键结论：
    - 新功能应沿用兼容式渐进路线，不一次性替换旧 UI 流程。
    - 视图切换和添加页来源应优先复用第六轮 `MainController` / `ViewRouter` 边界。
    - 新 UI 组件应沿用第七轮 `default.qss / skin preset` 和动态属性方向。
    - 新公共 UI 组件应沿用第八轮 `src/ui/common/` / `src/ui/utils/` 拆分方向。
    - 四象限、换肤 UI、排序、筛选等未实现功能不得伪实现。

- 实际修改文件：
  - `manage_instruction/Work_Formulation.md`
  - `manage_instruction/Work_Instruction.md`
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`

- 规划结果：
  - 当前阶段从“月界面优先”扩展为“月界面优先与上下文菜单增强”。
  - 右键菜单功能拆为：
    - `CM-0`：右键菜单现状审查与精确边界。
    - `CM-1`：公共 icon-text 上下文菜单组件试点。
    - `CM-2`：主界面日程区域右键菜单接入。
    - `CM-3`：周界面日期空白区域右键菜单接入。
    - `CM-4`：右键菜单整体验收。

- 主界面右键菜单规划：
  - 右键区域：主界面日程卡片区、空状态区或日程列表容器区，待 `CM-0` 精确定位。
  - 菜单项：
    - 换肤
    - 视图
    - 添加
    - 排序
    - 筛选
  - 本阶段先实装：
    - `视图`
    - `添加`
  - 其它项保留占位或禁用。

- 周界面右键菜单规划：
  - 右键区域：某日期对应的白色空白区域，待 `CM-0` 精确确认 `bottom_panels` 事件边界。
  - 添加行为：
    - 使用右键所在日期。
    - 过去日期不能添加日程。
  - 视图行为：
    - 使用与主界面一致的视图子菜单。
    - 四象限视图暂不实现。

- 菜单视觉规划：
  - 布局参考现有菜单：左侧图标，右侧文字。
  - 图标优先复用 `assets/icons/`：
    - `Skin.svg` / `theme.svg`
    - `view.svg`
    - `add.svg`
    - `sort.svg`
    - `filter.svg`
    - `Calendar.svg`
    - `todo.svg`
  - 不在本规划阶段新增 assets。

- 架构方向：
  - 不把完整右键菜单逻辑直接塞入 `MainWindow` 或 `WeekWindow`。
  - `CM-1` 应根据 `CM-0` 结论，新增或最小复用/扩展公共菜单组件。
  - 若现有 `SharedMoreMenu` / `ScheduleContextMenu` 不适合作为通用右键菜单，再新增 `src/ui/common/action_context_menu.py`。
  - 公共菜单组件只负责菜单 UI 和 action 信号，不直接访问数据库，不直接持有大窗口业务状态。
  - 主界面 / 周界面分别把菜单 action 接入已有动作入口。

- 当前未生成执行提示词：
  - `Work_Task_Prompts.md` 已重置为“暂无待执行提示词”。
  - 下一步应先由主窗口生成 `CM-0` 最终提示词。

- 未完成事项：
  - W-1 已完成并提交：`792ab6c`。
  - CM-0 提示词尚未生成。

- 风险或疑点：
  - 主界面右键区域需要防止与日程卡片现有右键菜单冲突。
  - 周界面白色区域右键需要防止破坏左键选中、双击跳转和拖拽排序。
  - 视图子菜单若做成紧邻弹窗，需要单独验证焦点、关闭和多菜单生命周期。

## 2026-05-29 CM-0（右键菜单现状审查与精确边界）

- 本轮任务名称：`CM-0（右键菜单现状审查与精确边界）`。
- 开工前 git 状态：
  - `## main...temp/main [ahead 42]`
  - 开工前未发现源码工作区 diff。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`（复核时修正 stale 锚点）

- 读取的规划文件清单：
  - `manage_instruction/Work_Formulation.md`
  - `manage_instruction/Work_Instruction.md`
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/ReconstructionDolder/Work_Formulation.md`
  - `manage_instruction/ReconstructionDolder/History_Instruction.md`

- 确认的架构原则：
  - 新功能优先兼容式旁路，不一次性替换旧 UI 流程。
  - 新公共 UI 组件优先放入 `src/ui/common/` 或 `src/ui/utils/`。
  - 右键菜单不得直接大段塞入 `MainWindow` / `WeekWindow`。
  - 不伪实现四象限、换肤、排序、筛选。
  - 视图切换和添加来源优先复用既有路由与添加入口。

- 静态搜索命令和关键结果摘要：
  - `rg -n "class DashboardView|class ScheduleCard|...|contextMenu" src/ui/dashboard.py src/ui/main_window.py`
    - 命中 `ScheduleCard` 已有 `CustomContextMenu + _show_context_menu`（`dashboard.py:154-155,297`）。
    - `DashboardView` 容器结构命中：`lbl_empty`、`scroll_area`、`scroll_content(TodoListContainer)`、`list_layout`（`dashboard.py:460-486`）。
  - `rg -n "bottom_panels|eventFilter|MouseButtonPress|..." src/ui/week_window.py src/ui/common/week_day_block.py`
    - `bottom_panels` 创建与索引关系命中（`week_window.py:497,539`）。
    - 空白区域左键选日命中 `eventFilter`（`week_window.py:1045-1058`）。
    - 周卡片右键菜单命中 `WeekScheduleCard._show_context_menu`（`week_window.py:190-192`）。
    - W-1 双击链路命中：`DayBlock.double_clicked` -> `_on_day_double_clicked` -> `day_double_clicked.emit`（`week_window.py:452,1028-1030`；`week_day_block.py:102`）。
  - `rg -n "class SharedMoreMenu|class ScheduleContextMenu|get_colored_icon|..." src/ui/components.py src/ui/header.py`
    - `SharedMoreMenu`（`components.py:272`）和 `ScheduleContextMenu`（`components.py:474`）均存在且职责明确。
    - `get_colored_icon` 命中（`components.py:585`）。
  - `rg -n "handle_header_action|switch_to_add_page|switch_view|..." src/ui/main_window.py src/ui/week_window.py src/controllers`
    - 主界面动作入口命中：`handle_header_action`、`switch_to_add_page`、`switch_view`（`main_window.py:505,547,581`）。
    - 周界面动作入口命中：`switch_to_add_page`、`view_selected.emit`（`week_window.py:676,1124`）。
    - 第六轮路由/控制器命中：`MainController`、`ViewRouter`（`main_window.py:29-30,582`；`controllers/*`）。

- 主界面可右键区域地图（DashboardView）：
  - 卡片区域：`ScheduleCard`（`dashboard.py:141+`），每张卡片已自带右键菜单。
  - 空状态区域：`lbl_empty`（`dashboard.py:460-467`）。
  - 滚动区域：`scroll_area`（`dashboard.py:469-473`）。
  - 列表容器区域：`scroll_content = TodoListContainer(self)`（`dashboard.py:475-486`）。
  - 建议可接入区域：
    - 空状态区域（`lbl_empty`）
    - 列表容器空白区（`scroll_content` 中非卡片命中区）
  - 建议暂不直接挂接区域：
    - `ScheduleCard` 本体（避免覆盖既有卡片右键）
    - 整个 `DashboardView` 根窗口（若无命中判断易吞掉卡片右键）。

- 主界面 `ScheduleCard` 既有右键菜单冲突风险：
  - 现状：`ScheduleCard` 通过 `setContextMenuPolicy(CustomContextMenu)` + `_show_context_menu` 打开 `ScheduleContextMenu`。
  - 风险：若主界面右键菜单接入在父容器且不做命中排除，可能与卡片右键竞争，导致卡片菜单失效或双菜单冲突。
  - 约束建议：
    - 主界面区域右键仅在“非 `ScheduleCard` 命中”时触发。
    - 卡片命中时保持走原 `ScheduleCard._show_context_menu`。

- 周界面 `bottom_panels` 日期映射结论：
  - `bottom_panels` 在周看板页按 0..6 顺序创建并 append（`week_window.py:497-539`）。
  - 每列日期映射统一使用 `target_date = current_monday.addDays(index)`（`week_window.py:1057`）。
  - 左键空白区域选中日期由 `eventFilter` 处理（仅 `LeftButton`，`week_window.py:1046`）。

- 周界面右键冲突风险分析：
  - 与左键选中冲突：当前 `eventFilter` 仅拦截 `LeftButton`，新增右键分支可旁路实现，不会天然覆盖左键。
  - 与双击跳转冲突：W-1 双击发生在顶部 `DayBlock`（`nav_container`），与底部 `bottom_panels` 空白区分离；主要风险低。
  - 与拖拽排序冲突：拖拽起点在 `WeekScheduleCard`，落点由 `panel.card_dropped` 处理；右键空白区菜单若仅在非拖拽、非卡片命中触发，风险可控。
  - 与卡片右键菜单冲突：`WeekScheduleCard` 已有 `ScheduleContextMenu`；周界面空白区右键必须排除卡片命中，避免覆盖。

- 周界面白色空白区域右键接入建议：
  - 建议接入位置：`WeekWindow.eventFilter` 内针对 `obj in bottom_panels` 增加 `RightButton` 分支。
  - 日期传递建议：复用 `index = bottom_panels.index(obj)` 与 `current_monday.addDays(index)`，得到右键日期后：
    - 先更新 `current_selected_date`（复用 `_on_day_clicked` 或等价选中逻辑）。
    - 再触发“添加”入口。
  - 过去日期限制：复用 `WeekWindow.switch_to_add_page` 的既有判断（`current_selected_date.toPyDate() < today`，`week_window.py:682`）。

- `SharedMoreMenu` / `ScheduleContextMenu` 复用评估：
  - `SharedMoreMenu`：
    - 当前职责是顶栏“更多”动作窗口菜单，强耦合 `parent_window`、置顶切换、待办窗显示、按钮锚点等。
    - 不适合作为主/周右键区域菜单直接复用。
  - `ScheduleContextMenu`：
    - 当前职责是“单个日程/待办卡片”状态菜单（完成、置顶、删除）。
    - 强依赖 `schedule_obj`，不适合作为“页面级动作菜单”。
  - 结论：建议 `CM-1` 新增 `src/ui/common/action_context_menu.py`，而非硬复用以上两者。

- 可复用 icon 清单（基于 `assets/icons` 现有资源）：
  - 换肤：`Skin.svg` / `theme.svg`
  - 视图：`view.svg`
  - 添加：`add.svg`
  - 排序：`sort.svg`
  - 筛选：`filter.svg`
  - 日视图：`Calendar.svg`（或 `cal_up/down/left/right.svg` 作为备选）
  - 周视图：`week_top_color.svg`（或沿用 `view.svg`）
  - 月视图：`Calendar.svg`
  - 待办：`todo.svg`
  - 四象限占位：`importance.svg`（仅占位，禁用或提示“未实现”）
  - 图标着色复用：`components.get_colored_icon(...)`。

- 主界面和周界面的动作入口清单：
  - 主界面添加：`MainWindow.switch_to_add_page()`。
  - 主界面视图：`MainWindow.switch_view(view_name)`。
  - 主界面动作分发：`MainWindow.handle_header_action(...)`（`add/view` 已接入）。
  - 周界面添加：`WeekWindow.switch_to_add_page()`。
  - 周界面视图：`WeekWindow._on_view_selected(...) -> view_selected.emit(vid)`，由 `MainWindow.switch_view` 接管。
  - 周界面日期选中：`WeekWindow._on_day_clicked(qdate)`。
  - 禁止放进右键菜单组件的逻辑：
    - `db_manager` 写入
    - 路由状态机
    - picker 返回链路
    - 详情弹窗回流
    - 刷新协调时序。

- CM-1 建议（组件策略）：
  - 建议新增 `src/ui/common/action_context_menu.py`。
  - 组件仅做：
    - icon-text 菜单渲染
    - action 回调/信号发射
    - 右侧视图子菜单（日/周/月/待办 + 四象限占位）
  - 不直接依赖 `MainWindow`/`WeekWindow` 业务状态，不直接写库。

- CM-2 建议（主界面接入）：
  - 建议接入点：`DashboardView` 的 `lbl_empty` 与 `scroll_content` 空白区。
  - 允许修改范围建议最小化：`src/ui/dashboard.py` + 必要的新公共菜单文件。
  - 验收重点：
    - 卡片右键菜单保持原行为。
    - 右键“添加”复用 `MainWindow.switch_to_add_page()`。
    - 右键“视图”复用 `MainWindow.switch_view(...)`。
    - 四象限仅占位，不伪实现。

- CM-3 建议（周界面接入）：
  - 建议接入点：`WeekWindow.eventFilter` 的 `bottom_panels` 分支新增 `RightButton` 处理。
  - 允许修改范围建议最小化：`src/ui/week_window.py` + 必要的新公共菜单文件。
  - 验收重点：
    - 左键选中日期不变。
    - W-1 双击跳日视图不变。
    - 卡片拖拽排序不变。
    - 卡片右键菜单不变。
    - 右键“添加”使用命中列日期并复用过去日期限制。

- 是否建议继续拆分 `CM-1 / CM-2 / CM-3`：
  - 建议继续拆分并按当前顺序执行。
  - 原因：
    - `CM-1` 先落菜单组件边界，可降低 `CM-2/CM-3` 接入复杂度。
    - 主界面与周界面接入风险不同，分开验收更稳。

- diff 范围检查结果：
  - 本轮执行后应满足：
    - `git diff --name-only -- src` 无输出。
    - `git diff --name-only -- assets` 无输出。
    - `git diff --name-only -- main.py` 无输出。
    - `git diff --name-only -- requirements.txt` 无输出。
    - `git diff --name-only -- schedule.db` 无输出。
  - 最终仅允许管理文档 diff。

- 未完成事项：
  - 等待决策/顾问窗口复核 `CM-0` 结论。
  - 复核通过后再下发 `CM-1` 最终执行提示词。

- 风险或疑点：
  - `DashboardView` 右键接入若命中判断不精确，最容易破坏卡片既有右键菜单。
  - `WeekWindow` 右键接入若不区分卡片命中与面板空白，可能干扰卡片右键与拖拽。
  - `SharedMoreMenu` 带窗口行为耦合，直接复用会引入与上下文菜单无关的副作用。

## 2026-05-29 CM-1（公共 icon-text 上下文菜单组件试点）

- 本轮任务名称：`CM-1（公共 icon-text 上下文菜单组件试点）`。
- 开工前 git 状态：
  - `## main...temp/main [ahead 43]`
  - 开工前无源码 diff，存在未跟踪文件：无。
- 实际修改文件：
  - `src/ui/common/action_context_menu.py`
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`（复核时修正 stale 锚点）

- 是否新增 `src/ui/common/action_context_menu.py`：
  - 是，已新增。

- 菜单类名和信号名：
  - 类名：`ActionContextMenu`
  - 信号：`action_requested(str)`、`view_requested(str)`

- 主菜单 action id 清单：
  - `skin`
  - `view`
  - `add`
  - `sort`
  - `filter`

- 视图子菜单 view id 清单：
  - `day`
  - `week`
  - `month`
  - `priority`
  - `todo`

- `view` 主项行为：
  - 仅作为子菜单入口（`QAction.setMenu(...)`），不会发出 `action_requested("view")`。

- 禁用项策略：
  - 主菜单禁用：`skin`、`sort`、`filter`
  - 视图子菜单禁用：`priority`
  - 禁用项无业务信号连接，`trigger()` 后不会新增有效动作信号。

- 禁用项 trigger 后信号检查：
  - 先触发已启用项得到：
    - `actions == ['add']`
    - `views == ['day', 'week', 'month', 'todo']`
  - 再触发禁用项（`skin/view/sort/filter/priority`）后：
    - `actions`、`views` 均无新增。
  - 断言通过：`'view' not in actions`，`'priority' not in views`。

- 图标复用清单：
  - `skin`: `Skin.svg` -> `theme.svg` 兜底
  - `view`: `view.svg`
  - `add`: `add.svg`
  - `sort`: `sort.svg`
  - `filter`: `filter.svg`
  - `day`: `Calendar.svg`
  - `week`: `week_top_color.svg` -> `view.svg` 兜底
  - `month`: `Calendar.svg`
  - `priority`: `importance.svg`
  - `todo`: `todo.svg`

- 是否使用 `QIcon("assets/icons/xxx.svg")`：
  - 是，组件内部通过 `QIcon(path)` 加载，若文件不存在降级为空图标并保持可构造。

- 是否未导入 `src.ui.components.get_colored_icon`：
  - 是，未导入。

- 是否导入或依赖 `MainWindow` / `WeekWindow` / `DashboardView` / `TodoBoardWindow`：
  - 否。

- 是否导入或依赖 `db_manager` / Repository / Service：
  - 否。

- 静态依赖检查结果：
  - 命令：
    - `rg -n "MainWindow|WeekWindow|DashboardView|TodoBoardWindow|db_manager|Repository|Service|ScheduleRepository|CategoryRepository|global_signals|switch_view|switch_to_add_page|get_colored_icon|src\.ui\.components" src/ui/common/action_context_menu.py`
  - 结果：无输出（`rg` 退出码 1，符合预期）。

- 静态定位结果：
  - 命令：
    - `rg -n "class ActionContextMenu|action_requested|view_requested|actions_by_id|view_actions_by_id|skin|view|add|sort|filter|priority|todo" src/ui/common/action_context_menu.py`
  - 结果：命中类、信号、动作字典、主菜单与视图子菜单项，结构完整。

- import 验证结果：
  - 命令：
    - `python -c "from src.ui.common.action_context_menu import ActionContextMenu; print(...)" `
  - 结果：`ActionContextMenu import ok`。

- offscreen 构造验证结果：
  - 命令：
    - `python -c "... ActionContextMenu(); print(actions/views) ..."`
  - 结果：
    - `actions ['skin', 'view', 'add', 'sort', 'filter']`
    - `views ['day', 'week', 'month', 'priority', 'todo']`

- 信号验证结果：
  - 命令：按提示词触发 `add/day/week/month/todo` 及禁用项 trigger 校验。
  - 结果：
    - `actions ['add']`
    - `views ['day', 'week', 'month', 'todo']`
    - 所有断言通过。

- `py_compile` 结果：
  - 命令：
    - `python -m py_compile src/ui/common/action_context_menu.py`
  - 结果：通过。

- diff 范围检查结果：
  - 禁止范围检查：
    - `src/ui/main_window.py`、`src/ui/week_window.py`、`src/ui/dashboard.py`、`src/ui/components.py`、`src/ui/header.py`、`src/controllers`、`src/data`、`src/repositories`、`src/services`、`src/theme`、`src/utils/signals.py`、`src/utils/styles.py`、`assets`、`main.py`、`requirements.txt`、`schedule.db` 均无 diff。
  - 总范围：
    - `git status --short --branch` 显示：
      - `## main...temp/main [ahead 43]`
      - `?? src/ui/common/action_context_menu.py`
      - `M manage_instruction/Work_Log.md`
      - 复核修正后另有 `M manage_instruction/Work_Task_Prompts.md`
  - 说明：本轮未修改 `src/ui/common/__init__.py`，符合“默认不导出 ActionContextMenu”的限制。

- 复核修正：
  - 发现 `Work_Task_Prompts.md` 仍显示“当前待执行提示词：CM-0”，与实际 CM-1 执行状态不一致。
  - 已将其收口为 CM-1 已执行、等待决策/顾问窗口复核，下一步候选 CM-2；未写入 CM-2 执行提示词。

- 未完成事项：
  - 等待决策/顾问窗口复核 `CM-1`。

- 风险或疑点：
  - 当前组件仅完成通用菜单壳与信号出口，尚未接入主界面/周界面，后续 `CM-2/CM-3` 需要额外验证命中区域与事件冲突。

## 2026-06-01 CM-2（主界面日程区域右键菜单接入）

- 本轮任务名称：`CM-2（主界面日程区域右键菜单接入）`
- 开工前 git 状态：
  - `## main...temp/main [ahead 44]`
  - 开工前已有管理文档 diff：`manage_instruction/Work_Task_Prompts.md`（既有状态，非本轮产生）。
- 实际修改文件：
  - `src/ui/dashboard.py`
  - `src/ui/main_window.py`
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有 diff；复核时修正 stale 锚点）

- 主界面右键接入区域：
  - `DashboardView.lbl_empty`
  - `DashboardView.scroll_content`

- 是否排除 `ScheduleCard` 本体：
  - 是。
  - `scroll_content` 右键通过 `childAt(pos)` + 父链遍历判定，命中 `ScheduleCard` 时直接返回，不弹页面级菜单。

- 是否保持 `ScheduleCard._show_context_menu(...)` 未改：
  - 是，未修改 `ScheduleCard` 右键链路与 `ScheduleContextMenu`。

- `DashboardView` 新增信号名称：
  - `context_action_requested(str)`
  - `context_view_requested(str)`

- `DashboardView -> MainWindow` 信号链路：
  - `DashboardView` 右键创建 `ActionContextMenu`，仅转发：
    - `menu.action_requested -> self.context_action_requested.emit`
    - `menu.view_requested -> self.context_view_requested.emit`
  - `MainWindow` 连接：
    - `page_dashboard.context_action_requested -> _handle_dashboard_context_action`
    - `page_dashboard.context_view_requested -> _handle_dashboard_context_view`

- `添加` 是否复用 `MainWindow.switch_to_add_page()`：
  - 是，`_handle_dashboard_context_action` 中仅处理 `add`，调用 `switch_to_add_page()`。

- `视图` 是否复用 `MainWindow.switch_view(...)`：
  - 是，`_handle_dashboard_context_view` 直接调用 `switch_view(view_name)`。

- `skin/sort/filter/priority` 是否仍未实现：
  - 是。仍由 `ActionContextMenu` 禁用策略控制，不在本轮启用。

- 是否修改数据库：
  - 否。未新增任何写库路径。

- import 验证结果：
  - 命令：
    - `python -c "from src.ui.dashboard import DashboardView, ScheduleCard; from src.ui.main_window import MainWindow; from src.ui.common.action_context_menu import ActionContextMenu; print('imports ok', ...)"`
  - 结果：通过（`imports ok`）。

- offscreen 验证结果：
  - Dashboard 信号存在性验证：
    - `dashboard context signals ok`，通过。
  - MainWindow 桥接验证：
    - `main window dashboard context bridge ok`，通过。

- `ActionContextMenu` 回归验证结果：
  - 触发输出：
    - `actions ['add']`
    - `views ['day', 'week', 'month', 'todo']`
  - `priority` 保持禁用，断言通过。

- 静态定位检查结果：
  - 命令：
    - `rg -n "context_action_requested|context_view_requested|ActionContextMenu|customContextMenuRequested|setContextMenuPolicy|_show_dashboard_context|_handle_dashboard_context|ScheduleCard|_show_context_menu|switch_to_add_page|switch_view" ...`
  - 结果：
    - `DashboardView` 页面级信号、接入点、菜单弹出方法命中。
    - `MainWindow` 处理方法与桥接连接命中。
    - `ScheduleCard._show_context_menu` 仍存在。

- `py_compile` 结果：
  - 命令：
    - `python -m py_compile src/ui/dashboard.py src/ui/main_window.py src/ui/common/action_context_menu.py`
  - 结果：通过。

- diff 范围检查结果：
  - 禁止范围均无 diff：
    - `src/ui/week_window.py`
    - `src/ui/components.py`
    - `src/ui/header.py`
    - `src/ui/todo.py`
    - `src/ui/todo_board.py`
    - `src/ui/month_window.py`
    - `src/controllers`
    - `src/data`
    - `src/repositories`
    - `src/services`
    - `src/theme`
    - `src/utils/signals.py`
    - `src/utils/styles.py`
    - `assets`
    - `main.py`
    - `requirements.txt`
    - `schedule.db`
  - 总范围：
    - `git diff --name-only`：
      - `manage_instruction/Work_Task_Prompts.md`（开工前既有；复核时修正 stale 锚点）
      - `src/ui/dashboard.py`
      - `src/ui/main_window.py`
    - `git status --short --branch`：
      - `## main...temp/main [ahead 44]`
      - `M manage_instruction/Work_Task_Prompts.md`
      - `M src/ui/dashboard.py`
      - `M src/ui/main_window.py`

- 复核修正：
  - 发现 `Work_Task_Prompts.md` 仍显示“当前待执行提示词：CM-2”，与实际 CM-2 执行状态不一致。
  - 已将其收口为 CM-2 已执行、等待决策/顾问窗口复核，下一步候选 CM-3；未写入 CM-3 执行提示词。

- 未完成事项：
  - 等待决策/顾问窗口复核 `CM-2` 接入。

- 风险或疑点：
  - 当前仅接入 `lbl_empty` 与 `scroll_content`。后续 `CM-3` 在周界面接入时需单独复核右键与拖拽/卡片右键冲突。

## 2026-06-01 CM-3（周界面日期空白区域右键菜单接入）

- 本轮任务名称：`CM-3（周界面日期空白区域右键菜单接入）`
- 开工前 git 状态：
  - `## main...temp/main [ahead 45]`
  - 开工前已有管理文档 diff：`manage_instruction/Work_Task_Prompts.md`（既有状态，非本轮产生）。
- 实际修改文件：
  - `src/ui/week_window.py`
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有 diff；复核时修正 stale 锚点）

- 周界面右键接入区域：
  - `bottom_panels` 白色空白区域（`WeekWindow.eventFilter` 中 `obj in bottom_panels` 分支）。

- 日期映射方式：
  - `index = self.bottom_panels.index(obj)`
  - `target_date = self.current_monday.addDays(index)`

- 是否排除 `WeekScheduleCard` 本体：
  - 是。
  - 右键分支通过 `obj.childAt(event.pos())` + 父链 `isinstance(..., WeekScheduleCard)` 过滤；
  - 命中卡片则 `return False`，保持卡片右键菜单链路。

- 是否保持 `WeekScheduleCard._show_context_menu(...)` 未改：
  - 是，未修改卡片右键菜单实现。

- 是否保持卡片拖拽排序未改：
  - 是，未修改 `_handle_card_drop(...)` 与 `card_dropped` 相关逻辑。

- 是否保持 `DayBlock.clicked` / `double_clicked` / `_on_day_clicked` / `_on_day_double_clicked` 未改：
  - `DayBlock.clicked`、`DayBlock.double_clicked` 未改。
  - `_on_day_clicked(...)`、`_on_day_double_clicked(...)` 方法体未改。

- `ActionContextMenu -> WeekWindow` 信号链路：
  - 右键空白区创建 `ActionContextMenu(self)`（每次新建实例）。
  - `menu.action_requested -> _handle_week_context_action`
  - `menu.view_requested -> _handle_week_context_view`
  - `menu.exec(obj.mapToGlobal(event.pos()))` 后 `return True`。

- `添加` 是否复用 `WeekWindow.switch_to_add_page()`：
  - 是，`_handle_week_context_action` 仅处理 `add`，调用 `switch_to_add_page()`。

- 过去日期禁止添加是否仍由 `switch_to_add_page()` 处理：
  - 是，沿用 `switch_to_add_page()` 现有 `current_selected_date < today` 判断。

- `视图` 是否复用 `_on_view_selected(...)` 或 `view_selected.emit(...)`：
  - 是，`_handle_week_context_view` 直接复用 `_on_view_selected(view_name)`。
  - `week` 仍走 `_on_view_selected('week')` 的 no-op 语义。

- `skin/sort/filter/priority` 是否仍未实现：
  - 是，仍由 `ActionContextMenu` 禁用项策略控制，本轮未启用。

- 是否修改数据库：
  - 否。未新增任何写库逻辑。

- 静态定位结果：
  - 命令：
    - `rg -n "ActionContextMenu|RightButton|bottom_panels|eventFilter|_handle_week_context|_show_week_context|WeekScheduleCard|_show_context_menu|_on_day_clicked|_on_day_double_clicked|switch_to_add_page|_on_view_selected|view_selected" src/ui/week_window.py src/ui/common/action_context_menu.py`
  - 结果：
    - `WeekWindow` 引用 `ActionContextMenu` 命中；
    - `eventFilter` 的 `RightButton` 分支命中；
    - 日期映射、卡片过滤、`return True` 命中；
    - `WeekScheduleCard._show_context_menu`、`_on_day_clicked`、`_on_day_double_clicked`、`switch_to_add_page`、`_on_view_selected` 均存在。

- import 验证结果：
  - 命令：
    - `python -c "from src.ui.week_window import WeekWindow, WeekScheduleCard; from src.ui.common.action_context_menu import ActionContextMenu; print('imports ok', ...)" `
  - 结果：通过（`imports ok`）。

- offscreen 验证结果：
  - 桥接存在性：
    - `week context bridge exists ok`，通过。
  - 日期映射：
    - 输出 `mapped dates` 共 7 项，`dates[0] == current_monday`，通过。
  - 添加路径日期选择：
    - 输出 `selected date for add path 2026-06-04`（示例），`current_selected_date` 断言通过。

- `ActionContextMenu` 回归验证结果：
  - 输出：
    - `actions ['add']`
    - `views ['day', 'week', 'month', 'todo']`
  - `priority` 保持禁用，断言通过。

- `py_compile` 结果：
  - 命令：
    - `python -m py_compile src/ui/week_window.py src/ui/common/action_context_menu.py`
  - 结果：通过。

- diff 范围检查结果：
  - 禁止范围检查：
    - `src/ui/main_window.py`、`src/ui/dashboard.py`、`src/ui/components.py`、`src/ui/header.py`、`src/ui/todo.py`、`src/ui/todo_board.py`、`src/ui/month_window.py`、`src/controllers`、`src/data`、`src/repositories`、`src/services`、`src/theme`、`src/utils/signals.py`、`src/utils/styles.py`、`assets`、`main.py`、`requirements.txt`、`schedule.db` 均无 diff。
  - 命令拼写兜底：
    - 提示词中的 `git diff --name-name-only -- schedule.db` 失败（无此参数），已按要求改用 `git diff --name-only -- schedule.db`，结果无输出。
  - 总范围：
    - `git diff --name-only`：
      - `manage_instruction/Work_Log.md`
      - `manage_instruction/Work_Task_Prompts.md`（开工前既有；复核时修正 stale 锚点）
      - `src/ui/week_window.py`
    - `git status --short --branch`：
      - `## main...temp/main [ahead 45]`
      - `M manage_instruction/Work_Log.md`
      - `M manage_instruction/Work_Task_Prompts.md`
      - `M src/ui/week_window.py`

- 复核修正：
  - 发现 `Work_Task_Prompts.md` 仍显示“当前待执行提示词：CM-3”，与实际 CM-3 执行状态不一致。
  - 已将其收口为 CM-3 已执行、等待决策/顾问窗口复核，下一步候选 CM-4；未写入 CM-4 执行提示词。

- 未完成事项：
  - 等待决策/顾问窗口复核 `CM-3` 接入。

- 风险或疑点：
  - 本轮仅覆盖周界面空白区右键。后续 `CM-4` 需整体验证与 `CM-2` 并行存在时的交互一致性。

## 2026-06-01 CM-4（右键上下文菜单整体验收与归档准备）

- 本轮任务名称：`CM-4（右键上下文菜单整体验收与归档准备）`。
- 开工前 git 状态：
  - `## main...temp/main [ahead 46]`
  - 开工前既有 diff：`manage_instruction/Work_Task_Prompts.md`（管理文档既有变更，非本轮源码问题）。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`

- 最近相关提交摘要（`git log --oneline -8`）：
  - `76f2f94 feat: add week empty area context menu`（CM-3）
  - `3481655 feat: add dashboard context menu bridge`（CM-2）
  - `6fb847f refactor: add reusable action context menu`（CM-1）
  - `8a6c551 docs: record cm-0 context menu boundary review`（CM-0 记录）

- CM-0~CM-3 汇总结论：
  - CM-0：完成主界面/周界面右键接入边界审查，明确新增公共菜单组件路径。
  - CM-1：完成 `ActionContextMenu` 公共组件试点，信号与禁用项策略建立。
  - CM-2：主界面空状态与列表空白区完成页面级右键菜单接入，桥接到主窗口既有入口。
  - CM-3：周界面 `bottom_panels` 空白区完成页面级右键菜单接入，右键列日期映射与视图/添加动作链路接入。

- ActionContextMenu 整体验收结果：
  - 静态定位通过：`class ActionContextMenu`、`action_requested`、`view_requested`、`actions_by_id`、`view_actions_by_id` 均存在。
  - 回归验证通过（offscreen）：
    - `add` 触发后 `actions == ['add']`。
    - `day/week/month/todo` 触发后 `views == ['day','week','month','todo']`。
    - `skin/sort/filter/priority` 禁用，trigger 后不新增信号。
    - `view` 主项不发出 `action_requested('view')`。

- 主界面右键菜单链路验收结果：
  - `DashboardView` 保留并提供 `context_action_requested` / `context_view_requested`。
  - `MainWindow` 保留桥接：`_handle_dashboard_context_action` / `_handle_dashboard_context_view`。
  - `添加` 复用 `switch_to_add_page()`；`日/周/月/待办` 复用 `switch_view(...)`。

- 主界面 `ScheduleCard` 既有右键菜单：
  - `ScheduleCard._show_context_menu(...)` 仍存在（静态命中），未被覆盖。

- 周界面右键菜单链路验收结果：
  - `WeekWindow` 保留桥接：`_handle_week_context_action` / `_handle_week_context_view`。
  - `eventFilter` 中右键空白区链路存在，菜单动作接入既有入口。
  - `添加` 复用 `switch_to_add_page()`，过去日期限制仍由该入口原逻辑处理。
  - `日/周/月/待办` 复用 `_on_view_selected(...)` / `view_selected`。
  - `week` 仍走 `_on_view_selected('week')` 的 no-op 分支。

- 周界面日期映射验收结果：
  - offscreen 输出：`mapped dates ['2026-06-01','2026-06-02','2026-06-03','2026-06-04','2026-06-05','2026-06-06','2026-06-07']`。
  - 断言通过：`len(bottom_panels)==7`，首列等于 `current_monday`。

- 周界面 `WeekScheduleCard` 既有右键菜单：
  - `WeekScheduleCard._show_context_menu(...)` 仍存在（静态命中），未被破坏。

- 周界面左键/双击/拖拽保持性：
  - `_on_day_clicked(...)` / `_on_day_double_clicked(...)` 均存在。
  - 添加日期路径验证通过：`_on_day_clicked(q)` 后 `current_selected_date == q`。
  - 拖拽排序相关方法链路未改动（静态检查无异常变更）。

- `skin/sort/filter/priority` 未实现项状态：
  - 保持禁用；本轮未启用实现。

- 是否修改数据库：
  - 否。本轮未写库。
  - `schedule.db` 无 tracked diff。

- 静态依赖检查结果：
  - 命令：
    - `rg -n "MainWindow|WeekWindow|DashboardView|TodoBoardWindow|db_manager|Repository|Service|ScheduleRepository|CategoryRepository|global_signals|switch_view|switch_to_add_page|get_colored_icon|src\.ui\.components" src/ui/common/action_context_menu.py`
  - 结果：无输出（exit code 1），符合预期。

- import 验证结果：
  - 通过：`ActionContextMenu`、`DashboardView`、`ScheduleCard`、`MainWindow`、`WeekWindow`、`WeekScheduleCard` 可 import。

- offscreen 验证结果：
  - 通过：`ActionContextMenu` 行为回归。
  - 通过：`DashboardView` context 信号存在。
  - 通过：`MainWindow` dashboard context bridge 存在。
  - 通过：`WeekWindow` context bridge 存在。
  - 通过：周界面日期映射与添加日期路径验证。

- `py_compile` 结果：
  - 通过：`src/ui/common/action_context_menu.py`、`src/ui/dashboard.py`、`src/ui/main_window.py`、`src/ui/week_window.py`。

- diff 范围检查结果：
  - `git diff --name-only -- src`：无输出。
  - `git diff --name-only -- assets`：无输出。
  - `git diff --name-only -- main.py`：无输出。
  - `git diff --name-only -- requirements.txt`：无输出。
  - `git diff --name-only -- schedule.db`：无输出。
  - `git diff --name-only`：`manage_instruction/Work_Log.md`（本轮）+ `manage_instruction/Work_Task_Prompts.md`（开工前既有）。

- 复核修正：
  - 发现 `Work_Task_Prompts.md` 仍显示“当前待执行提示词：CM-4”，与实际 CM-4 执行状态不一致。
  - 已将其收口为 CM-4 已执行、等待决策/顾问窗口复核；右键上下文菜单阶段等待归档；未写入后续功能执行提示词。

- 是否建议右键菜单阶段归档：
  - 建议可归档（CM-0~CM-4 验收链路通过，且本轮无源码改动）。

- 下一步建议：
  - 进入后续功能补充阶段；如继续扩展右键菜单，仅新增小工单处理未实现项（换肤/排序/筛选/四象限），保持渐进接入。

- 未完成事项：
  - 等待决策/顾问窗口复核并决定是否执行正式归档文档迁移。

- 风险或疑点：
  - 本轮 offscreen 验证覆盖静态与基础交互链路；真实桌面环境下菜单焦点与复杂鼠标轨迹仍建议人工点测一次后再做最终归档操作。
