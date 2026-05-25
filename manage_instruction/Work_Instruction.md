# Work Instruction

用途：本文件用于“当前阶段”的执行指令发布。

- 仅保留正在执行或即将执行的任务。
- 已完成阶段请归档到 `History_Instruction.md`，避免本文件长期堆积。
- 当前主路线图见 `Work_Formulation.md` 的“架构改写轮次路线图”。
- 改写前行为和目录快照见 `Work_Snapshot.md`。
- 执行过程记录写入 `Work_Log.md`。

---

# 当前阶段：第六轮 - Controller / Router / EventBus 协调层

## 已完成并归档

- 第一轮：基建 + repository + db_manager 兼容委托。
- 第二轮：Data 层整理与模型拆分。
- 第三轮：纯业务查询与排序服务。
- 第四轮：日程写入与重复规则服务。
- 第五轮：提醒与运行期状态服务。
  - 第五轮 5-0 ~ 5-6 均已完成并归档。
  - 已完成 `ReminderService` 服务边界。
  - 已验证提醒扫描、提醒触发窗口、运行期去重、弹窗数据构造和 UI/声音边界保持。
  - 第五轮最终验收通过，`src`、`main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。

---

## 第六轮目标

第六轮目标是逐步降低 `MainWindow`、`WeekWindow`、`TodoBoardWindow`、`MonthWindow` 之间的互相引用、直接路由和直接刷新耦合。

本轮更准确的定位是“跨视图协调层接管”，不是 UI 大拆分。应先建立 controller/router/coordinator 边界，再用小工单把旧 UI 中最明确、最低风险的协调逻辑迁出或委托。

重点范围：

- 视图切换：日视图、周视图、月视图、待办视图之间的切换协调。
- 添加页来源记录：`source_view_for_add` 等返回目标状态。
- picker 返回流程：时间、提醒、清单 picker 的 add/edit 返回路径。
- 跨视图刷新：日程/清单变更后的 Dashboard、Todo、Week、Month 刷新。
- EventBus 使用边界：新协调层可使用 `global_signals` 的新增信号，但必须保留旧信号签名和旧 UI 信号兼容。

不追求一次清空 `MainWindow`。本轮每一步只迁移一个可验证闭环。

---

## 第六轮允许修改范围

第六轮整体允许修改：

- `src/controllers/__init__.py`
- `src/controllers/main_controller.py`
- `src/controllers/view_router.py`
- `src/controllers/refresh_coordinator.py`
- `src/utils/signals.py`（仅在小工单明确需要补充信号时；不得修改旧信号签名）
- `src/ui/main_window.py`（仅在小工单明确要求时做最小调用替换）
- `src/ui/week_window.py`（仅在小工单明确要求时做最小调用替换）
- `src/ui/month_window.py`（仅在小工单明确要求时做最小调用替换）
- `src/ui/todo.py`（仅在小工单明确要求时做最小调用替换）
- `src/ui/todo_board.py`（仅在小工单明确要求时做最小调用替换）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

第六轮默认不修改 UI。只有某个小工单明确列出 UI 文件时，才允许最小调用替换。

---

## 第六轮禁止事项

第六轮整体禁止：

- 不修改 `src/data/`。
- 不修改 `src/repositories/`。
- 不修改 `src/services/`，除非后续阶段合同明确把某个 service 纳入当前小工单。
- 不修改 `main.py`。
- 不修改 `requirements.txt`。
- 不修改 `schedule.db`，也不保留任何数据库变更。
- 不新增数据库字段。
- 不改数据库迁移逻辑。
- 不改 `db_manager` 对外 API。
- 不改 Repository / Service 方法名、参数、返回语义。
- 不改 UI 布局、视觉、文案和交互流程。
- 不批量拆分 UI 大文件；UI 大文件拆分留到第八轮。
- 不修改旧 signal 的名称、参数和触发语义。
- 不删除旧直连刷新路径，除非对应小工单已经完成行为基线、替代路径验证和回归验收。
- 不实现新功能。

---

## 行为保持原则

本轮所有改动必须满足：

- 日、周、月、待办之间切换行为不变。
- 添加日程/待办后的返回页面不变。
- picker add/edit 模式下的返回路径不变。
- 编辑时间、提醒、清单后的数据写入和页面刷新不变。
- 删除、置顶、状态变更后的相关视图刷新不变。
- 已打开详情弹窗的刷新行为不变。
- `global_signals.skin_changed` 仍为无参信号。
- `global_signals` 名称必须保留。
- 如引入新的 EventBus 信号，只能作为兼容增强，不得强迫旧 UI 一次性迁移。

---

## 第六轮小工单拆分

第六轮采用 `6-0`、`6-1` 等编号。执行时可根据 `6-0` 审查结果继续拆分更小工单，不得为了匹配编号一次迁移过多逻辑。

### 6-0：静态审查与跨视图耦合定位

目标：

- 只读定位当前跨视图协调逻辑，不改源码。
- 建立第六轮改造基线，确认哪些逻辑适合本轮迁移，哪些应留到第八轮 UI 拆分。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

审查重点：

- `MainWindow.switch_view(...)` 的视图切换路径。
- `source_view_for_add`、`list_picker_source`、`time_picker_mode`、`alarm_picker_mode`、`list_picker_mode` 等路由状态。
- time/alarm/list picker 的 add/edit 返回路径。
- `DashboardView.req_refresh_all`、`TodoView.req_refresh_all`、`WeekWindow.schedule_updated` 等跨视图刷新链路。
- `WeekWindow`、`MonthWindow`、`TodoBoardWindow` 对主窗口或其他窗口的直接调用。
- 详情弹窗打开和刷新回流路径。
- `global_signals` 当前信号是否已足够支撑本轮协调层。

验收重点：

- 输出耦合地图：按文件、函数、信号、刷新目标记录。
- 标记每个候选迁移点的风险等级。
- 明确哪些进入 `6-1` 后续小工单，哪些推迟。
- 确认 `src`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

Work_Log 记录：

- 本轮任务名称。
- 静态审查命令和结果。
- 跨视图耦合地图。
- 建议进入第六轮的小工单候选。
- 不适合本轮处理的内容及原因。
- diff 范围检查结果。
- 未完成事项和风险疑点。

### 6-1：Controller / Router / Coordinator 最小骨架

目标：

- 只创建第六轮确认会使用的最小协调层文件。
- 保证新增 controller 文件可 import，且不依赖数据库、不依赖具体 UI 创建过程。
- 不接入旧 UI，不替换旧路由和刷新逻辑。

允许修改：

- `src/controllers/__init__.py`
- `src/controllers/main_controller.py`
- `src/controllers/view_router.py`
- `src/controllers/refresh_coordinator.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/ui/`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/utils/signals.py`（本轮先不补信号）
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- `MainController`、`ViewRouter`、`RefreshCoordinator` 可 import。
- 新 controller 文件不 import `db_manager`、Repository、Service 写入对象或 QWidget 具体类。
- 旧应用入口和旧 UI 路径不变。
- diff 范围只包含允许文件。

Work_Log 记录：

- 新增/修改文件。
- 每个 controller 文件的当前职责边界。
- import 验证结果。
- 静态依赖检查结果。
- diff 范围检查结果。
- 未完成事项和风险疑点。

### 6-2：ViewRouter 视图切换基线与低风险接管

目标：

- 基于 `6-0` 结论，先处理最清晰的主视图切换映射。
- 如基线不清楚，本轮只记录“不改源码”；不得强行接管。
- 如接管，优先让 `ViewRouter` 承担 view_name 到目标视图/窗口动作的轻量映射或决策，`MainWindow` 继续执行实际 Qt 操作。

允许修改：

- `src/controllers/view_router.py`
- `src/ui/main_window.py`（仅最小调用替换）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/ui/week_window.py`
- `src/ui/month_window.py`
- `src/ui/todo.py`
- `src/ui/todo_board.py`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- `switch_view("day" / "week" / "month" / "todo")` 的旧行为不变。
- `ViewRouter` 不创建 QWidget，不直接 show/hide 窗口，不写数据库。
- 如果改 `main_window.py`，只能替换路由决策调用，不能改布局和交互流程。
- GUI smoke 或 import 兜底通过。
- diff 范围只包含允许文件。

Work_Log 记录：

- 是否接管源码；如未接管，记录原因。
- 接管的 view_name 范围。
- 替换前后行为基线。
- 验证命令和结果。
- 风险疑点。

### 6-3：添加页来源与 picker 返回状态基线

目标：

- 先审查并记录 add/picker 返回状态，不默认改源码。
- 重点确认 `source_view_for_add`、`list_picker_source`、`time_picker_mode`、`alarm_picker_mode`、`list_picker_mode` 的旧语义。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- 记录 add 页从 dashboard/todo 返回的路径。
- 记录 time/alarm/list picker 的 add/edit 返回路径。
- 记录 week/todo_board 内部 picker 是否存在独立路径。
- 判断是否需要拆出 `MainController` 状态辅助；若需要，必须进入后续小工单，不在本轮直接修改。
- diff 范围只包含管理文档。

Work_Log 记录：

- 状态字段清单。
- 每个字段的写入点、读取点、返回目标。
- 后续是否建议接管及拆分方式。
- diff 范围检查结果。

### 6-4：添加页来源与 picker 返回状态最小接管（条件执行）

目标：

- 仅在 `6-3` 结论明确、风险可控时执行。
- 把一个最小状态决策迁入 `MainController` 或 `ViewRouter`，不一次迁移所有 picker。
- 如 `6-3` 判断不适合，本轮不改源码，只记录“无需/暂不接管”。

允许修改：

- `src/controllers/main_controller.py`
- `src/controllers/view_router.py`
- `src/ui/main_window.py`（仅最小调用替换）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/ui/week_window.py`
- `src/ui/todo_board.py`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/utils/signals.py`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- 被接管的返回路径行为不变。
- 未接管的 picker 路径行为不变。
- 不改变 add/edit 保存逻辑。
- 不改变 UI 布局、文案、交互。
- diff 范围只包含允许文件。

Work_Log 记录：

- 是否进入源码修改分支。
- 接管的具体字段/路径。
- 未接管路径及原因。
- 行为验证结果。
- 风险疑点。

### 6-5：RefreshCoordinator 跨视图刷新边界建立

目标：

- 建立跨视图刷新协调边界。
- 优先封装“调用哪些 refresh 方法”的协调动作，不改变触发时机。
- 本轮不删除旧信号，不改变旧 UI 信号签名。

允许修改：

- `src/controllers/refresh_coordinator.py`
- `src/ui/main_window.py`（仅最小调用替换或注册刷新目标）
- `src/utils/signals.py`（仅当 `6-0` 证明缺少必要兼容信号时）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/ui/week_window.py`（除非后续提示词明确纳入）
- `src/ui/todo_board.py`（除非后续提示词明确纳入）
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- Dashboard、Todo、Week 的刷新调用顺序和可见性判断保持。
- `global_signals` 旧信号保持兼容。
- `RefreshCoordinator` 不写数据库，不创建窗口，不修改业务对象。
- add/edit/delete 后的旧刷新路径仍可用。
- diff 范围只包含允许文件。

Work_Log 记录：

- 刷新目标注册方式。
- 接管的刷新链路。
- 保留的旧直连路径。
- 验证命令和结果。
- 风险疑点。

### 6-6：EventBus 并行通知试点

目标：

- 在不移除旧直接刷新路径的前提下，选择一个低风险变更点增加 EventBus 并行通知。
- 该通知只能作为兼容增强，不得成为唯一刷新路径。

允许修改：

- `src/controllers/refresh_coordinator.py`
- `src/ui/main_window.py`（仅低风险变更点）
- `src/utils/signals.py`（仅补充必要信号，且不改旧签名）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/ui/week_window.py`（除非后续提示词明确纳入）
- `src/ui/todo_board.py`（除非后续提示词明确纳入）
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- 旧刷新路径仍执行。
- 新 EventBus 信号可连接、可触发。
- 不出现重复写库。
- 不改变 UI 行为。
- diff 范围只包含允许文件。

Work_Log 记录：

- 选择的低风险通知点。
- 旧路径与新路径是否并存。
- 信号触发验证结果。
- 风险疑点。

### 6-7：详情弹窗与跨视图刷新回流复核

目标：

- 复核详情弹窗打开、编辑、关闭后的刷新回流。
- 默认只做行为验收和耦合记录；如需接管，必须另拆小工单。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- Dashboard 详情弹窗刷新行为不变。
- Week 打开 Dashboard 详情弹窗的路径不变。
- Todo/TodoBoard 打开详情弹窗的路径不变。
- 标记哪些回流适合后续接入 `RefreshCoordinator`。
- diff 范围只包含管理文档。

Work_Log 记录：

- 弹窗打开来源。
- 弹窗更新后的刷新目标。
- 直接耦合点。
- 是否建议后续迁移。

### 6-8：第六轮整体验收与归档准备

目标：

- 汇总第六轮所有 controller/router/coordinator 改动和未迁移债务。
- 确认可进入第七轮 Theme/QSS 接入。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- `MainController`、`ViewRouter`、`RefreshCoordinator` 可 import。
- `global_signals` 兼容性通过。
- 日/周/月/待办切换行为通过 GUI smoke 或 import 级兜底。
- add/edit/delete 后刷新链路按第六轮日志保持。
- picker 返回路径按第六轮日志保持。
- 详情弹窗刷新回流按第六轮日志保持。
- `src/data`、`src/repositories`、`src/services`、`main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。
- 明确第六轮是否可归档。

Work_Log 记录：

- 6-0 到 6-7 完成摘要。
- 实际迁移到 controller/router/coordinator 的职责。
- 保留在 UI 中的职责及原因。
- 整体验收命令和结果。
- 可归档性结论。

---

## 当前执行要求

当前只完成第六轮阶段合同与小工单拆分。

执行窗口在收到 `6-0` 正式提示词前，不得自行开始源码改造、数据库改造或管理文档大范围改写。
