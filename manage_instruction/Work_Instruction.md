# Work Instruction

用途：记录当前待执行的小工单阶段合同。执行窗口只能根据主窗口确认后的最终提示词行动。

---

# 当前阶段：月界面单击日程弹窗与详情编辑路由

本阶段代号：`MP`

本阶段只记录阶段合同与小工单拆分。执行窗口不得仅凭本文件直接开工；必须等待主窗口/决策窗口生成并确认后的单个小工单最终执行提示词。

## 阶段背景

月界面功能补齐阶段已归档。当前月界面已经具备：

- 日期状态标记。
- 单击选中日期。
- hover 只读预览。
- 日期持久 panel 壳。
- 月界面添加表单。
- 月界面右键菜单。

下一阶段目标是让“单击日期产生的月日程弹窗”从占位/简版 panel 演进为可承载日程列表的青色渐变 UI，并逐步接入共享 `ScheduleDetailPop` 与跨视图编辑路由。

本阶段不是一次性完成所有交互，必须按 `MP-0 ~ MP-5` 小工单推进。

## 阶段总体目标

- 月界面单击日期弹窗改为可承载日程列表的青色渐变 UI。
- 弹窗内日程项支持双击打开共享 `ScheduleDetailPop`。
- 月日程弹窗关闭时，关闭由它打开的子详情弹窗。
- 月日程弹窗不随月界面切换到日/周/待办等视图而自动关闭。
- 详情弹窗中的修改操作必须按当前可见视图路由，不绑定创建弹窗时的 `source_view`。
- 保存后刷新月格 marker、月日程弹窗、详情弹窗以及相关日/周/主界面数据。

## 阶段总体原则

- 不要一次性完成所有交互。
- 不要在 UI 改造工单里同时改跨视图编辑路由。
- 不要让月日程弹窗直接持有 `MainWindow` 的业务逻辑。
- 不要让 `ScheduleDetailPop` 直接调用具体页面。
- 编辑路由应由 `MainWindow` 或已有/新增的统一协调层承接。
- 共享详情弹窗应继续保持可复用，不绑定某一个页面。
- 普通视图切换导致的 `MonthWindow.hide()` 不应关闭月日程 panel；应用退出、窗口销毁、用户明确关闭月日程 panel，或产品规则确认的双击跳转清理，才允许关闭。
- 开工前若已有 diff，执行窗口必须记录到 `manage_instruction/Work_Log.md`，并区分是否属于本轮产生。

## 阶段总体禁止

- 不修改数据库字段。
- 不迁移数据库。
- 不改变 `db_manager` 对外 API。
- 不改变已有添加/删除/重复规则写入语义。
- 不伪实现四象限。
- 不接真实换肤 UI。
- 不把月日程弹窗做成 `MainWindow` 的业务代理。
- 不让 `ScheduleDetailPop` 直接调用 `MainWindow.page_dashboard`、`week_window`、`month_window` 等具体页面。
- 不把 MP 阶段和后续搜索/筛选/排序功能混做。

---

# 小工单拆分

## MP-0：现状审查与路由边界定位

### 目标

只读审查当前月界面持久 panel、详情弹窗、主/周/月视图刷新链路和编辑路由。明确后续 MP-1 到 MP-5 的真实代码边界。

重点定位：

- `src/ui/month_window.py`
  - `MonthWindow`
  - `MonthDayPanel` 打开/关闭链路
  - `open_day_panels`
  - `close_day_panels(...)`
  - marker / hover cache 刷新链路
  - 视图切换时是否隐藏/关闭月窗口
- `src/ui/popups/month_day_panel.py`
  - 当前 panel 壳结构
  - 是否已持有日程数据
  - 关闭信号和生命周期
- `src/ui/schedule_detail_pop.py`
  - `ScheduleDetailPop` 当前信号
  - 修改时间/提醒/清单/删除/状态变更请求如何发出
  - 当前是否依赖固定 `source_view`
- `src/ui/main_window.py`
  - 当前可见视图状态
  - day/week/month/todo 切换路由
  - 详情弹窗编辑请求如何分发
  - `_resolve_detail_edit_target(...)` 是否已满足“按当前可见视图动态路由”
  - 刷新 day/week/month/todo 的现有方法
- `src/ui/dashboard.py`
- `src/ui/week_window.py`
- `src/ui/todo.py`
- `src/ui/todo_board.py`
- `src/controllers/`
  - 是否已有可承接编辑路由的控制器/协调器。

### 允许修改文件

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

### 禁止事项

- 不修改 `src/`。
- 不修改 `main.py`。
- 不修改 `requirements.txt`。
- 不修改 `schedule.db`。
- 不写执行提示词之外的实现计划。
- 不提前创建新组件。

### 验收重点

- 输出当前月日程 panel、详情弹窗、编辑请求、刷新链路的耦合地图。
- 标记哪些改动适合 MP 阶段，哪些应推迟。
- 明确 `ScheduleDetailPop` 当前是否有固定 `source_view` 绑定风险。
- 明确 `MainWindow` 或协调层可以如何承接“当前可见视图路由”。
- 明确现有 `_resolve_detail_edit_target(...)` 是否已经满足 MP-4 的动态编辑路由要求；MP-4 应优先补缺口和验收，不默认重写整套路由。
- 确认 `src/`、`main.py`、`schedule.db` 无 diff。

### 风险点

- 若未先审查清楚 `ScheduleDetailPop` 信号，会在 MP-4 中误把编辑路由写进弹窗。
- 若未定位当前刷新链路，会在 MP-5 中漏刷新月 marker 或详情弹窗。

---

## MP-1：月日程弹窗青色渐变 UI 与列表承载

### 目标

只改造月日程弹窗自身 UI，使其能承载指定日期的日程列表。该工单只做 UI 与只读列表展示，不接详情弹窗，不改跨视图编辑路由。

目标行为：

- 单击月格日期仍打开/复用该日期的持久弹窗。
- 弹窗使用青色渐变风格，方向与现有主/月界面视觉一致。
- 弹窗显示日期标题和日程列表区域。
- 日程项至少显示标题、时间、紧急性/状态的基础信息。
- 无日程时显示空状态。
- 关闭按钮可关闭当前弹窗。
- 同一天重复单击仍复用已有弹窗，不重复创建。

### 允许修改文件

- `src/ui/popups/month_day_panel.py`
- `src/ui/month_window.py`（仅限传入日程列表、刷新/复用当前 panel 所需的最小改动）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

### 禁止事项

- 不打开 `ScheduleDetailPop`。
- 不改 `ScheduleDetailPop`。
- 不改 `MainWindow`。
- 不改 day/week/todo 视图。
- 不改数据层、服务层、控制层。
- 不写数据库。
- 不新增编辑能力。
- 不修改月界面添加表单。
- 不修改右键菜单。

### 验收重点

- `MonthDayPanel` 可 import、offscreen 构造。
- 单击日期弹窗能接收并展示该日程列表数据。
- 无日程日期有稳定空状态。
- 同一天重复单击复用同一个 panel。
- 关闭 panel 后从 `open_day_panels` 移除。
- 月界面切换到日/周/待办时，panel 不因普通视图切换自动关闭；不能把普通 `hide()` 一概视为清理信号。
- 用户明确关闭 panel、应用退出、窗口销毁，或产品规则确认的双击跳转清理，才允许关闭 panel。
- `src/ui/schedule_detail_pop.py` 无 diff。

### 风险点

- panel 如果直接查询数据库，会扩大职责；优先由 `MonthWindow` 传入已构建/已过滤的数据。
- panel 如果持有 `MainWindow`，会破坏后续路由边界。
- 视觉改造容易影响 M-4 生命周期，应保留关闭信号与 `open_day_panels` 维护方式。

---

## MP-2：月日程弹窗内日程项双击打开共享 ScheduleDetailPop

### 目标

在月日程弹窗内，为日程项增加双击打开共享 `ScheduleDetailPop` 的能力。该工单只接详情弹窗打开与生命周期，不处理跨视图编辑路由改造。

目标行为：

- 双击月日程弹窗内某条日程，打开共享 `ScheduleDetailPop`。
- 同一日程的详情弹窗重复打开时优先复用/置顶，避免重复多个相同详情。
- 月日程弹窗记录由自己打开的详情弹窗。
- 月日程弹窗关闭时，关闭它打开的子详情弹窗。
- 详情弹窗关闭后，应从月日程弹窗维护列表中移除。

### 允许修改文件

- `src/ui/popups/month_day_panel.py`
- `src/ui/month_window.py`（仅限连接 panel 信号、创建/管理详情弹窗的最小逻辑）
- `src/ui/main_window.py`（仅允许新增或复用统一详情弹窗打开入口/桥接，不处理编辑路由重构）
- `src/ui/schedule_detail_pop.py`（仅允许在必要时补充非业务侵入式信号或生命周期兼容；若无需修改则不改）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

### 禁止事项

- 不改编辑路由。
- 不改 `MainWindow` 的编辑路由决策。
- 不在 `MainWindow` 中处理 MP-4 范围的跨视图编辑路由重构。
- 不改 day/week/todo 具体页面。
- 不让 `MonthDayPanel` 调用 `MainWindow` 业务方法。
- 不让 `ScheduleDetailPop` 直接调用具体页面。
- 不改数据库。
- 不改保存逻辑。
- 不改月界面添加表单。

### 验收重点

- 日程项双击能发出明确的详情请求信号。
- `MainWindow` 或统一桥接入口负责创建/复用共享 `ScheduleDetailPop`；`MonthWindow`/`MonthDayPanel` 只发起详情打开请求并维护必要生命周期引用。
- `MonthDayPanel` 关闭时能关闭其打开的详情弹窗。
- 详情弹窗自身关闭时能从 panel 维护列表移除。
- 切换月界面到日/周/待办时，月日程弹窗和它打开的详情弹窗不因视图切换被自动关闭。
- 不修改跨视图编辑路由。

### 风险点

- 如果在 MP-2 中处理编辑路由，工单会过大且难以验收。
- 如果详情弹窗生命周期只由 `MonthWindow.open_popups` 管理，可能无法做到“panel 关闭时关闭子详情”。
- 如果 panel 直接创建 `ScheduleDetailPop`，需确保它不承接主窗口业务路由。

---

## MP-3：月日程弹窗生命周期与跨视图保留规则

### 目标

专门收口月日程弹窗及其子详情弹窗的生命周期，确保它们不会因月界面切换到日/周/待办等视图而被错误关闭，同时保留真正需要清理的场景。

目标行为：

- 月日程弹窗不随月界面切换到日/周/待办等视图而关闭。
- 普通视图切换导致的 `MonthWindow.hide()` 不应清理 panel 与子详情。
- 应用退出、窗口销毁、用户明确关闭 panel，或产品规则确认的双击跳转清理，才允许清理 panel 与子详情。
- 双击月格跳日视图时，是否关闭月日程弹窗应按最新产品规则复核：
  - 若延续此前规则：双击跳日关闭所有月界面持久 panel。
  - 若本阶段要求“视图切换不关闭”：应记录冲突并由主窗口确认，不在执行中自行改规则。
- panel 手动关闭时，必须关闭其子详情弹窗。
- 子详情弹窗手动关闭时，不应关闭父 panel。

### 允许修改文件

- `src/ui/month_window.py`
- `src/ui/popups/month_day_panel.py`
- `src/ui/schedule_detail_pop.py`（仅限生命周期信号兼容，若无需修改则不改）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

### 禁止事项

- 不改编辑路由。
- 不改 `MainWindow` 视图路由。
- 不改 day/week/todo 页面。
- 不改数据层、服务层、控制层。
- 不写数据库。
- 不改详情弹窗业务操作。

### 验收重点

- 视图切换动作不会误触 `close_day_panels()`。
- 普通 `hide()` 不会清理 panel。
- 应用退出/窗口销毁路径仍有明确清理策略。
- panel 手动关闭会清理子详情。
- 子详情手动关闭不会关闭父 panel。
- 若发现“双击跳日关闭 panel”和“切换日视图不关闭 panel”存在产品规则冲突，必须记录并暂停该分支，等待确认。

### 风险点

- 此工单涉及旧规则冲突：早期需求要求“双击跳日关闭所有持久弹窗”，本阶段又要求“月日程弹窗不随切换到日/周界面而关闭”。执行前必须在 MP-0 或本工单内明确二者优先级。
- 如果简单删除 `close_day_panels()`，可能破坏窗口 hide/close 清理。

---

## MP-4：详情编辑请求按当前可见视图路由

### 目标

改造详情弹窗中的编辑请求路由，使修改操作按当前可见视图分发，而不是绑定创建弹窗时的 `source_view`。该工单只处理路由，不改月日程弹窗 UI。

目标行为：

- `ScheduleDetailPop` 发出编辑请求信号，不直接调用具体页面。
- `MainWindow` 或已有/新增统一协调层根据当前可见视图分发：
  - 当前可见日视图：走日视图编辑链路。
  - 当前可见周视图：走周视图编辑链路。
  - 当前可见月视图：优先走 `MonthWindow` 已有的编辑 picker 链路，例如时间/提醒/清单编辑入口；只有 MP-0 证明某个编辑类型存在明确缺口时，才允许记录并暂停，不得临时回退到其他页面。
  - 当前可见待办视图：走待办相关链路。
- 详情弹窗创建时的旧 `source_view` 不再作为最终路由依据；如需保留，只能作为兼容字段或日志来源，不作为决策核心。
- 不让 `ScheduleDetailPop` 直接调用 `page_dashboard/week_window/month_window/todo_board`。

### 允许修改文件

- `src/ui/main_window.py`
- `src/ui/schedule_detail_pop.py`（仅限信号/参数兼容，不直接调用具体页面）
- `src/controllers/`（若已有协调器适合承接，可最小修改；若需新增轻量协调器，必须在提示词中明确）
- `src/ui/month_window.py`（仅限接收刷新/编辑请求信号的最小连接）
- `src/ui/dashboard.py`、`src/ui/week_window.py`、`src/ui/todo.py`、`src/ui/todo_board.py`（仅当现有编辑信号接入缺口明确，且必须最小修改）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

### 禁止事项

- 不改月日程弹窗 UI。
- 不改数据库字段。
- 不改 `db_manager` API。
- 不让 `ScheduleDetailPop` 直接调用具体页面。
- 不把 `MainWindow` 业务逻辑塞进 `MonthDayPanel`。
- 不一次性重构全部视图路由。
- 不改添加表单。

### 验收重点

- `ScheduleDetailPop` 仍可由日/周/月等入口打开。
- 编辑时间/提醒/清单等请求由 `MainWindow` 或协调层按当前可见视图分发。
- 切换视图后，旧详情弹窗再触发编辑请求，路由按当前可见视图走，而不是创建时 `source_view`。
- 如果现有 `_resolve_detail_edit_target(...)` 已满足动态路由，本工单优先补缺口和验收，不重写已有可用机制。
- 主界面、周界面既有详情编辑不回归。
- 月界面打开的详情弹窗不要求直接持有 `MainWindow`。
- 相关 import / offscreen smoke / py_compile 通过。

### 风险点

- 这是本阶段风险最高的路由工单，必须独立执行。
- 若把路由决策留在 `ScheduleDetailPop`，后续所有视图都会继续耦合。
- 若一次改所有编辑类型，容易破坏日/周现有编辑链路；必要时可再拆 MP-4a/MP-4b。

---

## MP-5：保存后多视图刷新与阶段整体验收

### 目标

收口保存后的刷新链路，并对 MP 阶段进行整体验收。确保详情编辑保存后，月格 marker、月日程弹窗、详情弹窗以及相关日/周/主界面数据刷新一致。

目标行为：

- 详情编辑保存后：
  - 月格 marker 刷新。
  - hover cache 刷新。
  - 已打开月日程弹窗的对应日期列表刷新。
  - 已打开详情弹窗显示最新数据，或在保存后安全关闭/重开，必须有明确策略。
  - 当前可见日/周/待办/主界面数据按现有刷新入口刷新。
- 删除、状态修改、时间/提醒/清单修改后也应触发一致刷新。
- 不新增数据库字段。
- 不改变保存接口语义。

### 允许修改文件

- `src/ui/main_window.py`
- `src/ui/month_window.py`
- `src/ui/popups/month_day_panel.py`
- `src/ui/schedule_detail_pop.py`（仅限刷新信号兼容）
- `src/controllers/`（若 MP-4 已引入协调层，则允许最小补齐刷新协调）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

可选允许：

- `src/ui/dashboard.py`
- `src/ui/week_window.py`
- `src/ui/todo.py`
- `src/ui/todo_board.py`

仅当刷新入口缺失且 MP-5 提示词明确授权时才可改。

### 禁止事项

- 不新增功能入口。
- 不改数据库字段。
- 不改重复规则写入语义。
- 不重构全局事件总线。
- 不把刷新逻辑分散到 `ScheduleDetailPop` 直接调用具体页面。
- 不修改无关 UI 布局。

### 验收重点

- 月日程 panel 列表刷新后数据一致。
- 月 marker / hover cache 刷新后状态一致。
- 详情弹窗保存后，刷新策略明确且可验证。
- 当前可见视图刷新按统一入口触发。
- 日/周/月/待办既有详情编辑和刷新不回归。
- `schedule.db` 如需临时写入验证，必须使用临时数据并清理；最终无 tracked diff。
- MP 阶段完成结论写入 `Work_Log.md`。

### 风险点

- 刷新链路容易重复调用，导致闪烁或性能问题；应优先复用已有刷新入口。
- 如果不同视图各自刷新，后续会继续扩大耦合；应优先通过 `MainWindow` 或协调层聚合。
- 真实写库验收必须谨慎，避免污染本地数据。

---

## 当前禁止

- 不直接修改 `src/`。
- 不直接写入新的功能实现提示词。
- 不继续在已归档的月界面阶段追加任务。
- 不修改 `manage_instruction/ReconstructionDolder/`。

---

## 下一步入口

下一步入口：`MP-0：现状审查与路由边界定位`。

等待决策/顾问窗口基于本阶段合同生成 `MP-0` 最终执行提示词。
