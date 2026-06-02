# Work Task Prompts

用途：保存主窗口审核后的最终执行提示词或当前复核锚点。执行窗口只应执行本文件中的最终版本。

---

# 当前待执行提示词：M-0

## M-0：月界面现状审查与交互边界定位

请执行 `M-0：月界面现状审查与交互边界定位`。本轮只做静态审查、代码阅读、搜索和日志记录，不修改源码，不写数据库，不实现任何功能。

## 1. 本轮目标

基于当前项目代码、`manage_instruction/Work_Instruction.md` 的月界面功能补齐阶段合同，以及 `manage_instruction/ReconstructionDolder/` 内旧规划，审查月界面现状并输出后续 `M-1` 到 `M-7` 的真实代码边界。

重点定位：

- 月界面当前 `QCalendarWidget` / `QTableView` / `CalendarCellDelegate` 绘制方式。
- 当前日期格单击跳日视图链路。
- 当前添加入口和 `calendar.selectedDate()` 使用方式。
- `QCalendarWidget.selectedDate()` 默认选中今天与后续“用户主动选中日期”的区分风险。
- 鼠标位置到日期的映射能力。
- 上月/下月补位日期判断方式。
- 日程圆点所需数据来源、字段语义和整月 `date -> schedules` 映射可行性。
- hover 只读预览弹窗和单击持久浮窗的组件归属。
- 月界面右键菜单复用 `ActionContextMenu` 的接入边界。
- 后续每个小工单适合修改哪些文件、风险等级和验收重点。

本轮只输出审查结论，不直接修改 `src/`。

## 2. 允许/禁止

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `assets/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `manage_instruction/Work_Formulation.md`
- `manage_instruction/Work_Instruction.md`
- `manage_instruction/Work_Snapshot.md`
- `manage_instruction/History_Instruction.md`
- `manage_instruction/History_Log.md`
- `manage_instruction/ReconstructionDolder/`

禁止事项：

- 不改源码。
- 不新增 UI 组件。
- 不修改数据库。
- 不运行写库验证。
- 不调整现有月界面行为。
- 不生成 `M-1` / `M-2` 等源码实现。
- 不提交 Git。

若开工前已有 diff，必须在 `Work_Log.md` 中单独记录，并区分是否属于本轮产生。

特别说明：

- 如果开工前已有 `manage_instruction/Work_Formulation.md` / `manage_instruction/Work_Instruction.md` / `manage_instruction/Work_Log.md` / `manage_instruction/Work_Task_Prompts.md` 的月界面规划相关 diff，应记录为“开工前既有规划文档 diff”。
- `M-0` 本轮不得继续修改 `Work_Formulation.md` 或 `Work_Instruction.md`。
- 最终范围检查中若仍存在开工前既有规划文档 diff，必须在日志中说明它们不是 `M-0` 执行新增改动。

## 3. 具体任务

### 3.1 读取阶段合同和旧规划

读取：

```powershell
Get-Content -Path manage_instruction\Work_Formulation.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
Get-Content -Path manage_instruction\ReconstructionDolder\Work_Formulation.md -Encoding UTF8
Get-Content -Path manage_instruction\ReconstructionDolder\History_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\ReconstructionDolder\Workflow_Guide.md -Encoding UTF8
```

审查重点：

- 月界面功能补齐是否符合旧规划中的渐进式改造原则。
- 新 UI 组件应优先放入 `src/ui/common/` 还是 `src/ui/popups/`。
- 是否需要复用现有 controller / router / coordinator 边界。
- 是否继续遵守 `ActionContextMenu`、skin preset、QSS 动态属性方向。

### 3.2 读取月界面相关源码

读取：

```powershell
Get-Content -Path src\ui\month_window.py -Encoding UTF8
Get-Content -Path src\ui\main_window.py -Encoding UTF8
Get-Content -Path src\ui\calendar_pop.py -Encoding UTF8
Get-Content -Path src\ui\common\action_context_menu.py -Encoding UTF8
```

如发现月界面依赖其他文件，再只读追加读取相关文件，并在日志中记录追加读取原因。

### 3.3 静态搜索月界面链路

执行搜索：

```powershell
rg -n "MonthWindow|CalendarCellDelegate|QCalendarWidget|QTableView|selectedDate|date_selected|clicked|doubleClicked|mouse|hover|paint|paintCell|visualRect|indexAt|calendar\.clicked|jump_to_date_from_month|jump_to_date|InlineAddViewMonth|_on_add_clicked|ActionContextMenu|switch_view|view_selected|date\(" src manage_instruction
```

重点确认：

- `MonthWindow.date_selected` 当前如何发出。
- `MainWindow.jump_to_date_from_month` 当前如何接收。
- 当前单击日期是否直接跳日界面。
- 当前月界面添加是否依赖 `calendar.selectedDate()`。
- 是否已有双击、hover、右键事件链路。
- 是否已有月格自绘或类似日程圆点绘制逻辑。

### 3.4 审查日期映射可行性

只读判断：

- 当前 `CalendarCellDelegate.paint(...)` 是否能准确获得日期。
- 当前 `QCalendarWidget` 内部 `QTableView` 是否可通过 `indexAt(...)`、`visualRect(...)` 获取鼠标所在格子。
- 当前页年月和上月/下月补位日期如何判断。
- 是否需要维护 `visible_month`、`cell_date_map` 或类似映射。
- `QCalendarWidget.selectedDate()` 默认今天是否会和“用户主动选中日期”混淆。
- 后续是否需要新增 `user_selected_date` 或类似状态，而不是直接复用 `calendar.selectedDate()`。

### 3.5 审查日程圆点数据规则

只读判断：

- 月界面当前是否已经加载整月日程。
- 是否可通过现有 `db_manager` / repository / service 获取整月数据。
- 当前 `Schedule` 字段中：
  - `priority` 高/中/低映射是什么。
  - `status` 完成/未完成/删除/历史语义是什么。
  - `item_type` 中 schedule/todo 是否需要区分。
  - 重复日程实例是否已经以独立记录存在。
  - `start_time`、`end_time`、`reminder_time` 哪个应作为月格日期来源。
- `calendar_pop.py` 中已有日程圆点绘制逻辑是否可作为参考，是否适合直接复用。

不要在本轮实现圆点逻辑，只记录建议。

### 3.6 审查浮窗组件归属

只读判断：

- hover 只读预览弹窗应放在 `src/ui/common/`、`src/ui/popups/` 还是 `month_window.py` 内部临时类。
- 单击持久浮窗壳应放在 `src/ui/popups/` 还是 `src/ui/common/`。
- 持久浮窗是否应使用独立顶层窗口，避免被 `MonthWindow` 裁剪。
- 是否需要由 `MonthWindow` 维护 `open_day_panels` 或类似列表。
- 月界面关闭、隐藏、双击跳日视图时，应在哪个方法里统一关闭全部持久浮窗。
- 多个持久浮窗并存时，如何避免完全重叠。

### 3.7 审查右键菜单接入边界

只读判断：

- `ActionContextMenu` 当前支持哪些 action。
- 月界面是否可复用已实现的视图子菜单。
- 月界面右键日期如何作为菜单上下文。
- 右键不改变当前选中日期是否可实现。
- 添加 action 如何使用右键日期。
- 过去日期添加如何禁用。
- `month` 当前项是否禁用、无动作或保持可点。
- 周视图跳转是否能携带日期上下文；如果现有路由不支持，本阶段先记录限制，不强行实现。

### 3.8 输出后续小工单建议

在 `Work_Log.md` 中输出：

- `M-1` 建议修改文件、风险等级、验收重点。
- `M-2` 建议修改文件、风险等级、验收重点。
- `M-3` 建议修改文件、风险等级、验收重点。
- `M-4` 建议修改文件、风险等级、验收重点。
- `M-5` 建议修改文件、风险等级、验收重点。
- `M-6` 建议修改文件、风险等级、验收重点。
- `M-7` 整体验收重点。

如果发现当前规划中某个小工单边界不合理，只记录调整建议，不直接修改 `Work_Instruction.md`。

## 4. 验收命令

开工状态：

```powershell
git status --short --branch
git diff --name-only
```

静态搜索：

```powershell
rg -n "MonthWindow|CalendarCellDelegate|QCalendarWidget|QTableView|selectedDate|date_selected|clicked|doubleClicked|mouse|hover|paint|paintCell|visualRect|indexAt|calendar\.clicked|jump_to_date_from_month|jump_to_date|InlineAddViewMonth|_on_add_clicked|ActionContextMenu|switch_view|view_selected|date\(" src manage_instruction
```

月界面源码定位：

```powershell
rg -n "class MonthWindow|class CalendarCellDelegate|class InlineAddViewMonth|date_selected|calendar\.clicked|selectedDate|_on_add_clicked|jump_to_date_from_month|ActionContextMenu|mousePressEvent|mouseMoveEvent|mouseDoubleClickEvent|contextMenuEvent|paint\(" src/ui/month_window.py src/ui/main_window.py src/ui/calendar_pop.py src/ui/common/action_context_menu.py
```

禁止范围检查：

```powershell
git diff --name-only -- src
git diff --name-only -- assets
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
git diff --name-only -- manage_instruction/Work_Formulation.md
git diff --name-only -- manage_instruction/Work_Instruction.md
git diff --name-only -- manage_instruction/Work_Snapshot.md
git diff --name-only -- manage_instruction/History_Instruction.md
git diff --name-only -- manage_instruction/History_Log.md
git diff --name-only -- manage_instruction/ReconstructionDolder
git diff --name-only
git status --short --branch
```

预期：

- `src` 无 diff。
- `assets` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 diff。
- `Work_Formulation.md`、`Work_Instruction.md`、`Work_Snapshot.md` 无 `M-0` 新增 diff。
- `History_Instruction.md`、`History_Log.md` 无 diff。
- `manage_instruction/ReconstructionDolder/` 无 diff。
- 最终只允许 `M-0` 新增：
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`
- 如果 `Work_Formulation.md` / `Work_Instruction.md` 存在开工前既有规划 diff，必须在 `Work_Log.md` 中标记为既有，不得视为 `M-0` 新增改动。

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：`M-0（月界面现状审查与交互边界定位）`
- 开工前 git 状态。
- 开工前既有 diff，尤其是月界面规划文档 diff。
- 实际修改文件。
- 读取的规划文件和源码文件。
- 当前月界面点击跳转链路。
- 当前月界面添加入口和日期来源。
- `QCalendarWidget.selectedDate()` 默认今天与用户主动选中日期的区分风险。
- 当前绘制方式和月格日期映射可行性。
- 日程圆点所需字段语义审查结论。
- hover 只读预览组件建议。
- 持久浮窗组件建议和生命周期管理建议。
- 月界面右键菜单接入建议。
- `M-1` 到 `M-7` 的建议修改文件、风险等级、验收重点。
- diff 范围检查结果。
- 未完成事项。
- 风险或疑点。

完成后不要提交 Git，等待决策/顾问窗口复核。
