# Work Formulation

用途：记录当前阶段的总体规划、目标边界和小工单路线。由主窗口在审核决策窗口方案后维护。

---

# 当前阶段：功能补充 - 月界面功能补齐

## 1. 当前背景

架构改写主线已结束。

右键上下文菜单阶段已完成并归档：

- 主界面日程区域右键菜单。
- 周界面日期空白区域右键菜单。
- 公共 `ActionContextMenu` 组件。
- 添加与视图切换已接入既有入口。
- 换肤、排序、筛选、四象限保持未实现。

归档位置：

- `History_Instruction.md`
- `History_Log.md`

旧架构规划参考：

- `manage_instruction/ReconstructionDolder/Work_Formulation.md`
- `manage_instruction/ReconstructionDolder/History_Instruction.md`
- `manage_instruction/ReconstructionDolder/Workflow_Guide.md`

---

## 2. 阶段目标

本阶段目标是补齐月界面交互，不直接启动四象限视图，也不做真实换肤、排序、筛选或云同步。

月界面应从当前“静态月历 + 单击日期跳日视图”的行为，逐步调整为：

- 月格只显示日程状态摘要圆点，不塞完整日程文本。
- 今天只让日期数字变金色，不再整格高亮。
- 单击日期表示选中，选中态才使用整格高亮。
- 双击日期才跳转对应日界面，并关闭所有月界面持久浮窗。
- hover 日期显示只读预览，鼠标移走立即隐藏。
- 单击日期显示月界面外侧的持久浮窗，可多个并存，先做壳。
- 添加按钮优先使用选中日期，过去日期不可添加。
- 在进入月界面右键菜单前，先补齐月界面左侧添加表单能力，使其逐步对齐主界面添加页的字段语义。
- 月界面右键菜单复用 `ActionContextMenu`，只实装“视图”和“添加”，其他占位禁用。

---

## 3. 日程圆点规则

无日程日期不显示圆点。

今天及未来：

- 只统计未完成日程。
- 最高紧急性为高：红色圆点。
- 最高紧急性为中：黄色圆点。
- 最高紧急性为低：绿色圆点。
- 没有未完成日程：不显示圆点。

过去日期：

- 有日程且全部完成：白色圆点。
- 有日程且存在未完成：灰色圆点。
- 无日程：不显示圆点。

`M-0` 必须先确认当前数据字段真实语义：

- `priority` 的高/中/低映射。
- 完成状态字段。
- 是否需要排除软删除、历史、todo 类型、重复日程展开结果。
- 月界面当前能否获得整月 `date -> schedules` 映射。

---

## 4. 交互规则

日期格：

- 今天：日期数字为金色，不代表选中。
- 单击：选中该日期，整格高亮。
- 双击：跳转该日期的日界面，关闭月界面，并关闭所有月界面持久浮窗。
- hover：显示只读预览，鼠标移走立即隐藏。

持久浮窗：

- 由单击日期触发。
- 显示在月界面外侧，类比待办面板，不挤压月历，不被父窗口裁剪。
- 可多个并存。
- 至少有关闭按钮。
- 后续关闭单个浮窗时，应从 `MonthWindow` 管理列表移除。
- 月界面关闭、隐藏、双击跳日界面时，必须关闭全部持久浮窗，避免孤儿窗口。

添加：

- 左侧添加按钮优先使用当前选中日期。
- 没有选中日期时沿用当前默认逻辑。
- 过去日期不可添加。
- 右键菜单的添加使用右键日期作为上下文，不必改变当前选中日期。
- 月界面左侧按键组和搜索框下方区域，类比主界面按键组下方的添加区域。
- 月界面添加表单可做竖向压缩适配，不必完全复制主界面 UI。
- 详情输入框可默认显示，不必保留主界面“详情”展开按钮。
- 时间、提醒、清单、紧急性、重复规则应逐步对齐主界面添加页的数据字段语义。
- `M-5b` 必须先审查 picker 承接方式，不能默认照搬 `MainWindow` 页面栈。
- `M-5b` 必须确认 `repeat_rule` 的真实入库值、显示值和 `ScheduleRepeatService` 归一化规则；后续不新增新规则，只沿用现有真实值体系。
- 保存后必须刷新月格 marker cache、hover 预览数据和已打开的同日期持久 panel；如暂时不能刷新全部 panel，至少关闭或重载目标日期 panel，避免脏数据。

右键菜单：

- 复用 `ActionContextMenu`。
- 右键日期格空白区域弹出菜单。
- 右键日期作为菜单上下文。
- 建议右键不改变当前选中日期，避免影响对比浮窗。
- 实装“视图”和“添加”。
- 换肤、排序、筛选、四象限保持禁用或占位。
- `month` 当前项如何处理、周视图是否携带日期上下文，需由 `M-0` 结合现有 `switch_view` 能力确认。
- `M-6` 应推迟到 M-5 后续添加表单能力补齐之后；右键菜单的“添加”复用补齐后的同一入口。

---

## 5. 小工单路线

### M-0：月界面现状审查与交互边界定位

只读审查，不改源码。

重点确认：

- 读取 `manage_instruction/ReconstructionDolder/Work_Formulation.md`、`History_Instruction.md`、`Workflow_Guide.md`，确认月界面功能补齐不违背旧架构规划中的分层、公共组件、刷新协调和渐进式改造原则。
- `QCalendarWidget` / `QTableView` / `CalendarCellDelegate` 当前绘制方式。
- 鼠标位置到日期的映射能力：`indexAt(...)`、`visualRect(...)`、当前页年月、上月/下月补位日期判断。
- 当前单击跳日视图链路：`MonthWindow.date_selected` -> `MainWindow.jump_to_date_from_month`。
- 当前添加入口：`calendar.selectedDate()` 与 `InlineAddViewMonth`。
- `QCalendarWidget.selectedDate()` 默认选中今天与后续“用户主动选中日期”状态如何区分，避免今天默认 selected 状态继续造成整格高亮。
- 日程数据来源、字段语义和整月数据映射能力。
- 外侧持久浮窗应放入 `src/ui/popups/` 还是 `src/ui/common/`。
- `ActionContextMenu` 在月界面的接入边界。

### M-1：月格状态圆点与今天金色日期

只做视觉状态：

- 绘制状态圆点。
- 今天日期数字改为金色。
- 无日程不显示圆点。
- 不改点击跳转。
- 不改添加。
- 不接 hover / popup / right-click。

### M-2：月格单击选中与双击跳日视图

调整交互语义：

- 单击只选中日期。
- 双击跳日视图。
- 双击跳转时关闭所有月界面持久浮窗。
- 允许最小修改 `MainWindow` 的月界面信号连接。
- 不做 hover 预览。
- 不做持久浮窗内容。

### M-3：hover 只读预览弹窗

实现鼠标悬停预览：

- 日期格 hover 显示只读列表。
- 鼠标移走立即隐藏。
- 弹窗在日期格右下角。
- 不可编辑。
- 不影响单击选中态。

### M-4：单击日期持久浮窗壳

实现外侧持久浮窗：

- 类比待办面板，使用独立浮窗。
- 显示在月界面外侧，不挤压月历，不被父窗口裁剪。
- 可多个并存。
- 至少有关闭按钮。
- 内容先做空白或简版列表壳。
- `MonthWindow` 负责浮窗列表和生命周期清理。

### M-5：添加按钮日期来源联动

调整月界面添加入口：

- 有选中日期时，添加默认该日期。
- 无选中日期时，沿用当前默认逻辑。
- 过去日期不可添加。
- 不改数据库写入逻辑。

### M-5b：月界面添加表单能力只读审查与 picker 承接方案确认

只读审查，不改源码。

重点审查：

- `src/ui/month_window.py::InlineAddViewMonth`
- `src/ui/month_window.py::MonthWindow`
- `src/ui/add_view.py::AddScheduleView`
- `src/ui/add_view_week.py::AddScheduleViewWeek`
- `src/ui/time_picker.py`
- `src/ui/time_picker_week.py`
- `src/ui/alarm_picker.py`
- `src/ui/alarm_picker_week.py`
- `src/ui/list_picker.py`
- `src/ui/main_window.py` 中主界面 picker 承接链路
- `src/ui/week_window.py` 中周界面 picker 承接链路

必须输出：

- 月添加表单与主/周添加页字段差异。
- 当前 `InlineAddViewMonth` 缺失能力清单。
- 可复用 picker、信号和回填链路。
- picker 承接方案：新增月界面内部页面栈、复用主窗口 picker、或月界面左侧局部切换 picker。
- picker 返回后如何回填 `InlineAddViewMonth`。
- picker 打开期间 hover 预览 / 持久 panel 是否需要隐藏。
- 时间语义：默认日期、是否允许跨天、未选时间时继续 `00:00` 兼容还是提示必须选择时间。
- 提醒依赖时间规则：未设置 start/end 时不能设置提醒，target_time 使用 start 优先还是 end 优先。
- 清单 picker 的 `list_type` 建议，确认月界面是否只支持添加日程。
- `repeat_rule` 的真实入库值、显示值和 `ScheduleRepeatService` 归一化规则。
- M-5c 到 M-5g 的精确边界。

### M-5c：月界面添加表单 UI 壳补齐

只做 UI 壳，不接 picker，不改保存逻辑。

- 调整 `InlineAddViewMonth` 左侧表单布局。
- 标题输入框保留。
- 详情输入框默认显示。
- 增加紧凑图标行：时间、提醒、清单。
- 增加紧急性和重复规则的紧凑控件。
- 保留取消 / 保存按钮。
- 不改变 `_on_save(...)` 写库结构。
- 不打开 picker。
- 如果需要避免误触，时间 / 提醒 / 清单按钮可禁用或显示轻量 toast；不得写入状态，不得打开 picker。
- 紧急性 / 重复控件即使可操作，本轮也不得影响 `_on_save(...)`。
- 验收重点是布局，不是功能。

### M-5d：月界面时间选择接入

只接时间选择。

- 点击时间按钮后打开 M-5b 确认的时间选择入口。
- 时间选择完成后回填 `selected_start_time` / `selected_end_time`。
- 打开时间选择时默认日期基于 M-5 的添加目标日期。
- 用户选择的 start/end 是否必须落在该日期，按 M-5b 结论执行。
- 未选择时间时行为按 M-5b 结论执行。
- 保存时使用用户选择时间，不再固定为 `00:00`，除非 M-5b 明确保留阶段性兼容。
- 不接提醒、清单、重复规则。

### M-5e：月界面提醒与清单接入

只接提醒和清单。

- 复用现有提醒 picker 和清单 picker。
- 回填 `selected_reminder`、`is_alarm_mode`、`alarm_duration`、`selected_list_id`。
- 保存时写入现有字段：`reminder_time`、`is_alarm`、`alarm_duration`、`category_id`。
- 未设置 start/end 时不能设置提醒。
- 提醒 target_time 使用 start 优先还是 end 优先，按 M-5b 结论执行。
- 清单 picker 的 `list_type` 按 M-5b 结论执行。
- 不新增数据库字段，不改 picker 内部逻辑。

### M-5f：月界面紧急性 / 重复规则 / 保存结构对齐

- 月添加表单支持紧急性选择。
- 月添加表单支持重复规则选择。
- `_on_save(...)` 与主界面添加页字段语义对齐。
- 保存字段至少覆盖：`title`、`item_type`、`priority`、`repeat_rule`、`description`、`start_time`、`end_time`、`reminder_time`、`is_alarm`、`alarm_duration`、`category_id`。
- 重复规则不新增新类型；沿用 M-5b 确认后的现有真实值体系。
- 不改变重复日程生成逻辑。
- 保存后刷新月格 marker cache、hover 预览数据和已打开的同日期持久 panel；如暂时不能刷新全部 panel，至少关闭或重载目标日期 panel。

### M-5g：月界面添加能力整体验收

复跑：

- 有选中日期时添加到选中日期。
- 无选中日期时 fallback 正常。
- 过去日期不可添加。
- 时间选择可回填并保存。
- 未选择时间时行为符合 M-5b 结论。
- 未设置时间时提醒不可设置。
- 提醒可回填并保存。
- 清单可回填并保存。
- 紧急性和重复规则可保存。
- 重复规则未新增新类型。
- 保存后月格状态标记刷新。
- hover 预览刷新。
- 持久日期 panel 刷新、重载或关闭，不显示脏数据。
- 主界面 / 周界面添加能力不回归。
- 月界面单击、双击、hover、持久 panel 不回归。

### M-6：月界面右键菜单接入

复用 `ActionContextMenu`：

- 右键日期格空白区域弹出菜单。
- 右键日期作为菜单上下文。
- 右键不改变当前选中日期，除非 `M-0` 另有结论。
- 实装视图切换和添加。
- 四象限、换肤、排序、筛选禁用。
- 过去日期添加禁用。

### M-7：月界面功能补齐整体验收

复跑：

- 圆点规则。
- 今天/选中态规则。
- 单击/双击行为。
- hover 预览生命周期。
- 持久浮窗生命周期。
- 添加日期来源。
- 月界面添加表单能力。
- 右键菜单行为。
- `schedule.db` 无 tracked diff。
- `main.py`、数据层、服务层非必要无 diff。

---

## 6. 当前不做

- 不直接启动四象限视图。
- 不做完整云同步。
- 不做真实换肤 UI 闭环。
- 不做排序和筛选完整功能。
- 不做大范围 UI 重构。
- 不做大范围 QSS 迁移。
- 不重写 `MainWindow` / `WeekWindow` / `TodoBoardWindow`。
- 不改变现有数据库字段。
- 不修改 `manage_instruction/ReconstructionDolder/`。

---

## 7. 当前等待事项

当前 M-5 已完成并提交。下一步应先执行 `M-5b：月界面添加表单能力只读审查与 picker 承接方案确认`，暂不进入 M-6。
