# Work Instruction

用途：本文件用于“当前阶段”的执行指令发布。

- 仅保留正在执行或即将执行的任务。
- 已完成阶段请归档到 `History_Instruction.md`，避免本文件长期堆积。
- 当前主路线图见 `Work_Formulation.md` 的“架构改写轮次路线图”。
- 改写前行为和目录快照见 `Work_Snapshot.md`。
- 执行过程记录写入 `Work_Log.md`。

---

# 当前阶段：第八轮 - UI 拆分与样式债务整理

## 已完成并归档

- 第一轮：基建 + repository + db_manager 兼容委托。
- 第二轮：Data 层整理与模型拆分。
- 第三轮：纯业务查询与排序服务。
- 第四轮：日程写入与重复规则服务。
- 第五轮：提醒与运行期状态服务。
- 第六轮：Controller / Router / EventBus 协调层。
- 第七轮：Theme / QSS 接入与样式债务控制。

---

## 第八轮目标

第八轮目标是在数据层、业务服务、协调层、Theme/QSS 基础已经稳定后，开始整理 UI 大文件和公共组件，但仍采用兼容式渐进重构。

本轮重点不是“把 UI 一次性拆漂亮”，而是建立可持续拆分方式：

- 先定位 UI 大文件内部的职责边界。
- 优先沉淀低风险公共组件或工具。
- 每次只迁移一个小边界。
- 保持页面显示、交互、信号、刷新、拖拽、右键菜单、弹窗行为不变。
- 延续第七轮样式路线：基于 `default.qss / skin preset`，不建立 light/dark mode matrix。
- 新增或拆出的 UI 组件应优先使用 `role/state/variant` 动态属性规范，避免继续复制硬编码主题色。

第八轮应优先处理：

- `src/ui/todo_board.py` 的职责地图和安全拆分点。
- `src/ui/week_window.py` 的卡片、日期块、窗口控制、toast 等可拆边界。
- `src/ui/main_window.py` 中仍残留的 UI 协调与展示辅助。
- picker、tooltip、icon loader、toast、schedule card、folder card 等公共组件候选。

第八轮不以“文件体积立刻明显变小”为唯一目标。若某个小工单只完成边界定位、目录骨架或单个低风险组件提取，也算有效推进。

---

## 第八轮允许修改范围

第八轮整体允许修改：

- `src/ui/`
- `src/ui/common/`（可新增；用于后续拆出的共享 UI 小组件，避免与既有 `src/ui/components.py` 冲突）
- `src/ui/views/`（可新增）
- `src/ui/dialogs/`（可新增）
- `src/ui/popups/`（可新增）
- `src/ui/utils/`（可新增）
- `src/theme/default.qss`（仅在明确小工单中为新拆组件补充低风险动态属性规则）
- `src/theme/theme_manager.py`（默认不改；仅在明确小工单中为样式刷新做极小兼容修正）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

默认允许新增 UI 包目录和 `__init__.py`，但只有具体小工单明确要求时，才允许移动类或改调用方。

阶段级允许范围不等于每个小工单的实际可改范围。第八轮执行时必须以具体 `8-x` 提示词中的允许清单为准；未在该小工单中明确列出的 UI 文件、主题文件或工具文件不得顺手修改。

禁止创建与现有 `src/ui/*.py` 同名的包目录。例如当前已有 `src/ui/components.py`，因此不得创建 `src/ui/components/`，以免遮蔽既有 `from .components import ...` 导入。

`src/theme/theme_manager.py` 的兼容修正必须由具体小工单明确方法名、修改原因和验收命令；否则默认禁止修改。`src/utils/styles.py` 也必须由具体小工单明确唯一修改点和兼容验收；否则默认禁止修改。

---

## 第八轮禁止事项

第八轮整体禁止：

- 不修改 `src/data/`。
- 不修改 `src/repositories/`。
- 不修改 `src/services/`，除非后续小工单明确只读验证已有 service 行为；默认不碰。
- 不修改 `src/controllers/`，除非后续小工单明确只读验证第六轮协调层；默认不碰。
- 不修改 `src/utils/signals.py`。
- 不修改 `src/utils/styles.py`，除非后续小工单明确做极小兼容整理；默认不碰。
- 不修改 `main.py`，除非小工单明确只做 import smoke 或极小入口兼容；默认不碰。
- 不修改 `requirements.txt`。
- 不修改 `schedule.db`。
- 不新增数据库字段。
- 不改数据库迁移逻辑。
- 不改 `db_manager` 对外 API。
- 不改业务服务语义。
- 不改第六轮 `ViewRouter`、`MainController`、`RefreshCoordinator`、`refresh_requested` 行为。
- 不实现新功能。
- 不实现真实换肤 UI。
- 不实现 `theme_color/设置字体` 功能闭环。
- 不实现四象限 UI。
- 不实现搜索、筛选、导出、同步等占位功能。
- 不一次性拆分 `todo_board.py` / `week_window.py` / `month_window.py` / `add_view.py` 等大文件。
- 不批量迁移所有 `setStyleSheet(...)`。
- 不删除旧 UI 类或旧导入路径，除非具体小工单已完成兼容验证。

---

## 行为保持原则

第八轮所有改动必须满足：

- 应用可 import / smoke。
- 日、周、月、待办切换行为不变。
- 添加、编辑、删除、提醒、详情弹窗行为不变。
- picker 返回行为不变。
- 拖拽、右键菜单、置顶、排序、文件夹/便签视图切换行为不变。
- 第六轮跨视图刷新链路不变。
- 第七轮 `default.qss / skin preset` 路线不变。
- 已试点的 `header.btn_sync` 动态属性样式不被破坏。
- 旧 UI 仍可继续使用既有 `setStyleSheet(...)`。
- 新拆出的组件必须保留旧类的公开行为、信号、参数和返回语义。

---

## 第八轮小工单拆分

第八轮采用 `8-0`、`8-1` 等编号。执行时可根据 `8-0` 审查结果继续拆成 `8-2a`、`8-2b` 这种更小工单，不得为了匹配编号一次迁移过多 UI。

### 8-0：UI 拆分静态审查与职责地图

目标：

- 只读审查当前 UI 大文件、公共组件、样式债务和可拆边界。
- 不改源码。
- 为第八轮后续小工单建立行为基线和风险分级。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

审查重点：

- UI 文件体量和类分布。
- `todo_board.py` 内部类、状态机、写库调用、toast、icon loader、list picker、folder/stick 视图边界。
- `week_window.py` 内部 `WeekScheduleCard`、`DayBlock`、window controls、toast、weather、view selector、周视图刷新边界。
- `month_window.py` 内部 inline add、window controls、calendar、toast、weather、view selector 边界。
- `main_window.py` 中仍承担的 UI 展示辅助、toast、详情弹窗回流、跨视图协调调用。
- `components.py`、`widgets.py`、`header.py` 中已有公共组件可复用性。
- 重复的 `CustomToolTip` / `ToolTipFilter` / icon loader / toast / window control 逻辑。
- `setStyleSheet(...)` 热点与适合使用 `default.qss` 动态属性的低风险位置。
- 哪些拆分适合第八轮，哪些应推迟到后续功能轮。

验收重点：

- 输出 UI 职责地图。
- 输出拆分候选清单和风险等级。
- 输出建议优先级。
- 确认 `src`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

Work_Log 记录：

- 静态审查命令和结果。
- UI 大文件体量。
- 高风险区域。
- 低风险拆分候选。
- 建议的下一步小工单。

### 8-1：UI 包目录骨架与导入边界准备

目标：

- 只建立第八轮后续拆分需要的 UI 包目录骨架。
- 不移动旧类。
- 不替换旧调用。
- 不改变运行行为。

允许修改：

- `src/ui/common/__init__.py`
- `src/ui/views/__init__.py`
- `src/ui/dialogs/__init__.py`
- `src/ui/popups/__init__.py`
- `src/ui/utils/__init__.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- 现有 `src/ui/*.py` 文件。
- `src/theme/`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `src/utils/signals.py`
- `src/utils/styles.py`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- 新目录可作为 Python package import。
- 不触发 QApplication。
- 不触发 UI 实例化。
- 不引入循环导入。
- 总 diff 只包含允许文件和日志。

Work_Log 记录：

- 新增目录和 `__init__.py`。
- import 验证。
- diff 范围检查。

### 8-2：公共 icon loader 静态定位与最小提取

目标：

- 先定位重复 icon loader 逻辑，再只提取一个低风险纯工具。
- 不改图标资源。
- 不改业务 UI 行为。

建议拆分保护：

- 若 `8-0` 发现 icon loader 逻辑差异较大，先执行 `8-2a` 只读基线，不改源码。
- 只有差异清楚后，执行 `8-2b` 最小提取。

允许修改：

- `src/ui/utils/icon_loader.py`（可新增）
- 一个明确列出的调用方文件（执行提示词必须写死具体文件，例如 `src/ui/header.py` 或 `src/ui/todo_board.py` 中的单个函数）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- 未在提示词列出的 UI 文件。
- `assets/`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `src/theme/`（除非只读验证）
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- 提取后的 helper 可 import。
- 旧图标加载结果不抛异常。
- 被替换调用方行为不变。
- 只替换一个低风险调用点。
- diff 范围严格受控。

Work_Log 记录：

- 旧逻辑位置。
- 提取后的函数职责。
- 替换的唯一调用点。
- import / py_compile / smoke 结果。

### 8-3：公共 tooltip / toast 边界定位与单点提取

目标：

- 整理重复的 tooltip/toast 候选，但只做一个小边界。
- 不改变提示文案、显示位置、持续时间、关闭行为。

建议拆分保护：

- 优先 `8-3a`：只读定位 `CustomToolTip`、`ToolTipFilter`、`show_toast` 分布。
- 如边界清楚，再 `8-3b`：只提取一个低风险组件或工具。

允许修改：

- `src/ui/common/tooltip.py` 或 `src/ui/common/toast.py`（具体文件由执行提示词写死）
- 一个明确列出的调用方文件
- `src/theme/default.qss`（仅在明确需要动态属性规则时）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- 未在提示词列出的 UI 文件。
- `src/utils/styles.py`（默认不碰）
- `src/utils/signals.py`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- tooltip/toast 显示语义不变。
- 不改变已有计时器、关闭、鼠标事件行为。
- 不改变 parent 归属、生命周期、eventFilter 安装/移除、focus 行为、hide/show 时机。
- `default.qss` 只新增动态属性选择器，不新增全局规则。
- 被替换调用方 import / py_compile 通过。

Work_Log 记录：

- 旧重复位置。
- 本轮只处理的唯一边界。
- 未处理的重复项和推迟原因。

### 8-4：WeekWindow 低风险类提取试点

目标：

- 从 `week_window.py` 中选择一个低风险 UI 类做文件级提取试点。
- 优先候选：`WeekScheduleCard` 或 `DayBlock`。
- 不改周视图业务流程。

执行前置条件：

- 必须基于 `8-0` 的静态审查结论锁定唯一最低风险候选类。
- 若 `8-0` 未明确建议 `WeekScheduleCard` 或 `DayBlock` 中的唯一候选，不得直接执行源码提取，应先补充只读复核或继续拆分为 `8-4a` / `8-4b`。
- 执行提示词必须写死被提取类名、新文件名和唯一替换范围，不允许执行窗口自行扩大到多个类。

允许修改：

- `src/ui/week_window.py`
- `src/ui/common/week_schedule_card.py` 或 `src/ui/common/day_block.py`（具体文件由执行提示词写死）
- `src/ui/common/__init__.py`（仅轻量导出，且不触发副作用）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/ui/todo_board.py`
- `src/ui/month_window.py`
- `src/ui/main_window.py`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `src/theme/`（除非只读验证）
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- 类公开构造参数、信号、属性访问保持兼容。
- `week_window.py` import 新类后行为不变。
- 周视图 import / offscreen smoke 通过。
- 不改变卡片排序、点击、拖拽、tooltip、详情弹窗行为。

Work_Log 记录：

- 提取的类。
- 原位置和新位置。
- 兼容性说明。
- import / py_compile / smoke 结果。

### 8-5：TodoBoard 只读基线与低风险拆分候选确认

目标：

- 只读审查 `todo_board.py`，不拆代码。
- 明确哪些类可以后续拆，哪些状态机必须暂缓。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

审查重点：

- `StickyNoteCard`
- `StickViewContainer`
- `FolderCard`
- `AddFolderCard`
- `FolderViewContainer`
- `ManageCategoryCard`
- `ManageListView`
- `InlineAddTodoView`
- `TodoBoardWindow`
- `_get_icon`
- `_apply_custom_tooltip`
- `show_toast`
- folder/stick 状态机。
- sort_order 写回路径。
- list picker / inline add / refresh 通知链路。

验收重点：

- 输出 TodoBoard 职责地图。
- 输出后续可拆小工单建议。
- 明确高风险状态机暂缓项。
- 确认无源码 diff。

Work_Log 记录：

- 类与职责地图。
- 写库/刷新/状态机风险点。
- 建议下一步是否可拆某个卡片类。

### 8-6：TodoBoard 单个卡片类提取试点

目标：

- 在 `8-5` 基线清楚后，只提取一个低风险卡片类。
- 优先候选：`FolderCard` 或 `AddFolderCard`。
- 不迁移 `TodoBoardWindow` 状态机。

允许修改：

- `src/ui/todo_board.py`
- `src/ui/common/todo_board_cards.py` 或明确的单类文件
- `src/ui/common/__init__.py`（仅轻量导出）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `src/theme/`（除非只读验证）
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- 提取类构造参数、信号、右键菜单、拖拽相关行为不变。
- `TodoBoardWindow` 仍按旧方式使用该类。
- 不改变 folder/stick 状态机。
- 不改变 sort_order 写回。
- 不改变新增/删除/刷新行为。

Work_Log 记录：

- 提取的唯一类。
- 旧行为保持说明。
- import / py_compile / offscreen smoke 结果。
- 未拆项和风险。

### 8-7：MainWindow / MonthWindow / AddView 拆分候选复核

目标：

- 只读或极小范围复核剩余 UI 大文件的拆分候选。
- 不默认改源码。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

审查重点：

- `main_window.py` 的 toast、详情弹窗回流、视图容器、刷新入口是否已由第六轮稳定承接。
- `month_window.py` 的 inline add、calendar、window controls、toast、view selector 是否适合后续拆。
- `add_view.py` / `add_view_week.py` 重复结构是否适合后续合并，但本轮不合并。
- `schedule_detail_pop.py` 复杂分支是否应继续推迟。

验收重点：

- 输出候选清单。
- 输出建议顺序。
- 明确不在第八轮处理或需另开功能轮的项。
- 确认无源码 diff。

Work_Log 记录：

- 文件级拆分建议。
- 高风险项。
- 下一轮或后续功能轮建议。

### 8-8：第八轮整体验收与归档准备

目标：

- 汇总第八轮已完成的小工单。
- 验证 UI 拆分没有破坏已有功能边界。
- 判断是否可归档第八轮。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- 新增 UI 包可 import。
- 被提取的组件可 import。
- 原调用方可 import / py_compile。
- 默认启动接入仍可 import smoke。
- 第七轮 `btn_sync` 试点仍可回归。
- 第六轮协调层行为不变。
- `src/data`、`src/repositories`、`src/services`、`src/controllers`、`main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。
- 明确第八轮是否可归档。

Work_Log 记录：

- 8-0 到已完成小工单摘要。
- 实际拆出的组件和目录。
- 未拆 UI 债务。
- 第九轮或后续功能轮建议。
- 可归档性结论。

---

## 当前执行要求

- 当前只完成第八轮阶段合同与小工单拆分。
- 执行窗口在收到 `8-0` 正式提示词前，不得自行开始源码改造、UI 拆分、样式迁移、数据库改造或管理文档大范围改写。
- 第八轮应优先执行 `8-0` 静态审查与职责地图，不应直接拆 `todo_board.py` 或 `week_window.py`。
- 若后续顾问窗口复核认为某个小工单仍过大，应继续拆成 `8-xa` / `8-xb`。
