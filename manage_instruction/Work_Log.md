# Work Log

用途：记录当前阶段/当前小工单的执行过程、验证结果和风险。

历史日志归档见：

- `History_Log.md`

旧架构改写阶段日志已移入：

- `ReconstructionDolder/History_Log.md`

---

## 当前状态

右键上下文菜单阶段已完成并归档。

当前无待执行小工单。

下一步建议：

- 等待决策窗口复核“月界面功能补齐阶段”规划。
- 复核通过后生成 `M-0：月界面现状审查与交互边界定位` 最终提示词。

---

## 2026-06-02 月界面功能补齐阶段规划写入

- 任务目标：
  - 将用户提出的月界面功能补齐构想整理为阶段规划和小工单边界。
  - 本轮只改管理文档，不改源码。
- 实际修改文件：
  - `manage_instruction/Work_Formulation.md`
  - `manage_instruction/Work_Instruction.md`
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`
- 写入内容：
  - 阶段名：`功能补充 - 月界面功能补齐`。
  - 明确下一步先做 `M-0` 只读审查，不直接修改 `month_window.py`。
  - 记录月格状态圆点规则：
    - 无日程不显示圆点。
    - 今天及未来只统计未完成日程，按最高紧急性显示红/黄/绿。
    - 过去日期有日程且全部完成为白点，有未完成为灰点，无日程不显示圆点。
  - 记录今天/选中态规则：
    - 今天只将日期数字改金色。
    - 整格高亮留给选中日期。
  - 记录交互规则：
    - 单击选中日期。
    - 双击跳转日界面并关闭所有月界面持久浮窗。
    - hover 显示只读预览，移走立即隐藏。
    - 单击显示月界面外侧持久浮窗，可多个并存。
  - 记录添加与右键菜单规则：
    - 添加按钮优先使用选中日期，过去日期不可添加。
    - 月界面右键菜单复用 `ActionContextMenu`，实装视图和添加，其余禁用。
    - 右键日期作为菜单上下文，建议不改变当前选中日期。
  - 记录 `M-0` 到 `M-7` 小工单路线。
- 特别补强的执行边界：
  - `M-0` 必须读取 `manage_instruction/ReconstructionDolder/Work_Formulation.md`、`History_Instruction.md`、`Workflow_Guide.md`，确认新增月界面功能不违背旧架构规划中的分层、公共组件、刷新协调和渐进式改造原则。
  - `M-0` 必须确认 `QCalendarWidget` / `QTableView` 鼠标位置到日期的映射方式。
  - `M-0` 必须确认 `QCalendarWidget.selectedDate()` 默认选中今天与后续“用户主动选中日期”状态如何区分，避免今天默认 selected 状态继续造成整格高亮。
  - `M-0` 必须确认 `priority`、完成状态、软删除/历史/todo/重复日程等字段语义。
  - `M-2` 允许最小修改 `MainWindow` 月界面信号连接。
  - 持久浮窗必须由 `MonthWindow` 管理生命周期，避免孤儿窗口。
  - `month` 当前项和周视图日期上下文如何处理，留给 `M-0` 结合现有路由确认。
- 验证：
  - 本轮未修改 `src/`、`assets/`、`main.py`、`requirements.txt`、`schedule.db`。
- 未完成事项：
  - 尚未生成 `M-0` 最终执行提示词。
  - 等待决策窗口复核本阶段规划。
- 风险或疑点：
  - 月界面当前基于 `QCalendarWidget` 原生表格与 delegate 绘制，后续日期映射和 hover/右键事件边界需要先读代码确认。

---

## 2026-06-02 M-0 最终提示词写入

- 任务目标：
  - 将决策窗口拟定并经主窗口修正的 `M-0（月界面现状审查与交互边界定位）` 提示词写入 `Work_Task_Prompts.md`。
- 实际修改文件：
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`
- 修正点：
  - 保留 M-0 只读审查边界，不允许修改源码、不写数据库。
  - 明确读取 `ReconstructionDolder` 旧规划，确认月界面功能补齐符合分层、公共组件、刷新协调和渐进式改造原则。
  - 明确审查 `QCalendarWidget.selectedDate()` 默认选中今天与“用户主动选中日期”的区分风险。
  - 明确当前已存在的月界面规划文档 diff 应作为开工前既有 diff 记录，避免执行窗口误判为 M-0 新增改动。
- 当前状态：
  - `M-0` 最终提示词已写入。
  - 等待执行窗口执行，完成后等待决策/顾问窗口复核。

---

## 2026-06-01 右键菜单子菜单与 hover 细节修正

- 任务目标：
  - 修正 `ActionContextMenu` 视图子菜单显示/隐藏、位置、宽度、图标颜色和选中背景覆盖范围。
- 实际修改：
  - `src/ui/common/action_context_menu.py`
    - 将菜单项改为 `QWidgetAction` 自绘行，扩大 hover 青色背景覆盖范围，使背景覆盖图标与文字整行。
    - 主菜单图标与视图子菜单图标统一通过 `load_colored_svg_pixmap(..., "#333333", ...)` 染色，避免白色图标融入浅色背景。
    - `视图` 项不再依赖 Qt 原生 `setMenu(...)` 子菜单延迟，改为 hover 时手动 `popup(...)`。
    - 视图子菜单显示位置改为主菜单右边界贴合子菜单左边界，减少原生子菜单重叠。
    - 视图子菜单固定宽度缩窄为 `150px`，主菜单固定宽度为 `160px`。
    - 鼠标离开主菜单/子菜单区域后通过零延迟检查关闭视图子菜单，避免原生子菜单长时间残留。
- 保持不变：
  - 未修改 Dashboard / WeekWindow 接入逻辑。
  - 未修改 `action_requested("add")` 与 `view_requested(day/week/month/todo)` 的信号语义。
  - 未启用换肤、排序、筛选、四象限。
  - 未修改数据库、服务层、控制层、assets。
- 验证：
  - `ActionContextMenu` import 通过。
  - offscreen 构造通过。
  - 信号回归通过：`add`、`day/week/month/todo` 仍按原语义发出，禁用项不触发动作。
  - `DashboardView` / `WeekWindow` import 回归通过。
  - `py_compile` 通过。
- 未完成事项：
  - 未做真实 GUI 截图自动验收；本轮需要用户本地目视确认菜单贴边、宽度和 hover 体验。
- 风险或疑点：
  - 子菜单显示改为手动 `popup(...)`，如果后续发现边缘屏幕位置溢出，需要另开小修正处理屏幕边界回退。

---

## 2026-06-01 右键菜单圆角样式微调

- 任务目标：
  - 将主界面和周界面共用的右键上下文菜单外观对齐到“更多”弹窗样式。
  - 仅调整菜单组件样式，不改变右键菜单功能、动作信号、接入位置和业务流程。
- 开工前状态：
  - 已存在归档管理文档 diff。
  - 本轮源码改动仅限 `src/ui/common/action_context_menu.py`。
- 实际修改：
  - `src/ui/common/action_context_menu.py`
    - 引入 `StyleManager.get_menu_style()`。
    - `ActionContextMenu` 主菜单复用“更多”弹窗同款 QMenu 样式。
    - `view_menu` 子菜单同步复用同款样式。
    - 为菜单设置 `WA_TranslucentBackground`、`Popup`、`FramelessWindowHint`、`NoDropShadowWindowHint`，对齐 `SharedMoreMenu` 的圆角显示方式。
- 保持不变：
  - 未修改 Dashboard / WeekWindow 的右键菜单接入逻辑。
  - 未修改 `action_requested` / `view_requested` 信号。
  - 未修改换肤、排序、筛选、四象限禁用策略。
  - 未修改数据库、服务层、控制层、QSS、assets。
- 验证：
  - `ActionContextMenu` import 通过。
  - offscreen 构造通过，主菜单和视图子菜单均可创建。
  - 信号回归通过：`add`、`day/week/month/todo` 行为保持一致，禁用项不触发新增动作。
  - `py_compile` 通过。
  - diff 范围符合预期：源码仅 `src/ui/common/action_context_menu.py` 有改动，另有归档管理文档既有 diff。
- 未完成事项：
  - 未做真实 GUI 截图验收；本轮为低风险样式对齐，运行期仍建议用户本地目视确认圆角效果。
- 风险或疑点：
  - Qt 原生菜单在不同 Windows 主题/合成器下对圆角和阴影的渲染可能略有差异，但样式来源已与“更多”弹窗统一。

---

## 2026-06-01 右键上下文菜单阶段归档

- 已归档到：
  - `History_Instruction.md`
  - `History_Log.md`
- 阶段结论：
  - `CM-0` 到 `CM-4` 已完成。
  - 右键上下文菜单阶段可归档。
  - 本阶段未实现换肤、排序、筛选、四象限。
  - 后续建议回到月界面功能补齐规划。
