# Work Task Prompts

用途：保存主窗口审核后的最终执行提示词或当前复核锚点。执行窗口只应执行本文件中的最终版本。

---

# 当前待执行提示词：M-1

## M-1：月格状态圆点与今天金色日期

请执行 `M-1：月格状态圆点与今天金色日期`。本轮只做月界面的视觉状态补齐：月格右下角状态圆点、今天日期数字金色。本轮不改变点击、双击、hover、右键、添加和跳转行为。

## 1. 本轮目标

基于 `M-0` 审查结论，在月界面实现两个视觉变化：

1. 月格右下角显示日程状态圆点。
2. 今天不再整格高亮，只将日期数字显示为金色。

本轮必须保持：

- 当前单击日期跳日视图行为不变。
- 当前添加按钮日期来源不变。
- 当前 `MonthWindow.date_selected` 信号语义不变。
- 当前 `MainWindow.jump_to_date_from_month(...)` 链路不变。
- 当前 `QCalendarWidget.selectedDate()` 业务使用方式不变。
- 不接 hover 预览。
- 不接持久浮窗。
- 不接右键菜单。
- 不修改数据库。

本轮是视觉试点，不处理 `M-2` 之后的交互重构。

## 2. 允许/禁止

允许修改：

- `src/ui/month_window.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/ui/main_window.py`
- `src/ui/calendar_pop.py`
- `src/ui/common/action_context_menu.py`
- `src/ui/popups/`
- `src/ui/common/`
- `src/controllers/`
- `src/services/`
- `src/data/`
- `src/repositories/`
- `src/theme/`
- `src/utils/signals.py`
- `src/utils/styles.py`
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

- 不改变单击日期跳日视图行为。
- 不新增双击跳转。
- 不新增 hover 预览。
- 不新增持久浮窗。
- 不新增右键菜单。
- 不改变添加按钮逻辑。
- 不改变 `date_selected` / `view_selected` 信号语义。
- 不引入 `user_selected_date` 或等价用户主动选中状态；该状态属于后续 `M-2/M-5`。
- 不调用 `setSelectedDate(...)`、不清空选择、不改 `selectedDate()` 业务语义。
- 不改数据库字段。
- 不写数据库。
- 不提交 Git。

若开工前已有 diff，必须在 `Work_Log.md` 中单独记录，并区分是否属于本轮产生。

## 3. 具体任务

### 3.1 读取当前上下文

读取：

```powershell
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
Get-Content -Path src\ui\month_window.py -Encoding UTF8
```

重点确认：

- M-0 对 M-1 的建议。
- 当前 `MonthWindow`、`CalendarCellDelegate`、`InlineAddViewMonth` 的结构。
- 当前 `calendar.clicked.connect(self.date_selected.emit)` 不能在本轮改变。
- 当前 `_on_add_clicked(...)` 不能在本轮改变。
- 当前 `QCalendarWidget.selectedDate()` 默认今天的风险只在绘制层规避，本轮不建立新的业务选中态。

### 3.2 实现月格状态圆点

在 `src/ui/month_window.py` 中实现月格状态圆点。

规则：

- 无日程日期：不显示圆点。
- 今天及未来：
  - 只统计未完成日程。
  - 未完成日程最高紧急性为高：红色圆点。
  - 未完成日程最高紧急性为中：黄色圆点。
  - 未完成日程最高紧急性为低：绿色圆点。
  - 没有未完成日程：不显示圆点。
- 过去日期：
  - 有日程且全部完成：白色圆点。
  - 有日程且存在未完成：灰色圆点。
  - 无日程：不显示圆点。

字段语义按 M-0 结论执行：

- `priority == 2`：高，红色。
- `priority == 1`：中，黄色。
- `priority == 0`：低，绿色。
- `status == 0`：未完成 / 活动。
- `status == 1`：已完成。
- `status == 2`：删除 / 历史，本轮圆点统计应排除。
- `item_type == "schedule"` 才参与月格圆点统计。
- `item_type == "todo"` 不参与月格圆点统计。
- 日期来源优先使用 `start_time.date()`，缺失时使用 `end_time.date()`。
- 重复日程实例作为独立记录参与统计，不按 `group_id` 合并。

实现原则：

- 本轮可以读取现有 `db_manager.get_all_schedules()` 并在月界面本地聚合 `date -> marker_color`。
- `db_manager.get_all_schedules()` 只能作为只读数据来源，不得写库。
- 不要为了 42 个格子反复调用 `get_schedules_for_date(...)`。
- 不新增 service/repository。
- 不修改 `calendar_pop.py`。
- 可以参考 `calendar_pop.py` 的圆点绘制思路，但不能直接套用其颜色规则。
- 不要继续扩大旧的“数字 + 行号阈值”启发式作为业务日期来源。
- 如果当前 `CalendarCellDelegate.paint(...)` 无法可靠拿到完整 `QDate`，应在 `MonthWindow` 或 delegate 中维护当前可见年月，并以当前页年月 + 格子 row/column 计算精确日期。
- 本轮只需覆盖当前可见月历格子的圆点绘制，不实现 hover/右键命中。

建议实现方向：

- 增加一个轻量的月格日程标记缓存，例如 `date -> marker_color`。
- 在 `MonthWindow` 初始化、翻月、保存日程后更新该缓存并刷新月历视图。
- 可以为 `CalendarCellDelegate` 增加最小 setter/helper，用于接收当前可见年月、今天日期和 marker 缓存。
- 若需要调整 `CalendarCellDelegate` 构造函数或内部 helper，只能服务于本轮绘制，不要顺手重构月界面。
- 在月格右下角绘制小圆点。
- 圆点尺寸和位置应稳定，不影响日期数字和现有布局。
- 如果外部窗口修改日程后本月圆点不能即时刷新，本轮只记录为风险；不要接入 `RefreshCoordinator` 或新增 signal。

### 3.3 实现今天日期数字金色

将“今天”的视觉表达改为：

- 今天只把日期数字绘制为金色。
- 今天不应因为 `QCalendarWidget.selectedDate()` 默认值而整格高亮。
- 整格高亮仍保留给后续 `M-2` 用户主动选中态；本轮不要实现新的选中态。

注意：

- 当前 `QCalendarWidget.selectedDate()` 默认可能是今天。
- 本轮需要避免“今天默认 selected”导致整格高亮。
- 只在绘制层处理今天视觉，不改变 `selectedDate()`、不清空选择、不修改单击信号。
- 如果本轮仍保留 Qt selected 绘制，必须确保今天默认 selected 不造成整格高亮；如果无法严格区分，应在日志记录限制，不要扩大交互重构。

### 3.4 保持现有行为不变

必须保持以下链路：

- `MonthWindow.calendar.clicked.connect(self.date_selected.emit)` 仍存在或行为等价。
- 单击日期仍触发 `date_selected`。
- `MainWindow.jump_to_date_from_month(...)` 不被修改。
- `_on_add_clicked(...)` 仍按当前逻辑使用 `calendar.selectedDate()`。
- `InlineAddViewMonth` 写入逻辑不变。
- `view_selected` 逻辑不变。
- 天气 tooltip、toast、skin/view/add/sort/filter 按钮行为不变。

不得新增或修改以下行为：

- `mouseDoubleClickEvent`
- `contextMenuEvent`
- `eventFilter` 的鼠标命中交互
- hover popup
- persistent popup
- `ActionContextMenu`

### 3.5 更新日志

更新 `manage_instruction/Work_Log.md`，记录本轮修改、验证和风险。

## 4. 验收命令

开工状态：

```powershell
git status --short --branch
git diff --name-only
```

定位本轮改动：

```powershell
rg -n "marker|dot|schedule_dates|date_map|cell_date|paint|CalendarCellDelegate|selectedDate|date_selected|calendar\.clicked|_on_add_clicked|priority|status|item_type|get_all_schedules" src/ui/month_window.py
```

确认未新增后续交互：

```powershell
rg -n "mouseDoubleClickEvent|contextMenuEvent|ActionContextMenu|customContextMenuRequested|setContextMenuPolicy|hover|persistent|open_day_panels|user_selected_date|setSelectedDate|clearSelection" src/ui/month_window.py
```

若命中来自既有代码或注释，必须在 `Work_Log.md` 中说明；不得新增 `M-2` 之后的交互逻辑。

import 验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.month_window import MonthWindow, CalendarCellDelegate, InlineAddViewMonth; print('month import ok', MonthWindow, CalendarCellDelegate, InlineAddViewMonth)"
```

offscreen 构造验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); print('month window construct ok'); print('selected', w.calendar.selectedDate().toString('yyyy-MM-dd'))"
```

只读数据路径验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; schedules=db_manager.get_all_schedules(); print('schedules', len(schedules)); print('sample fields ok', all(hasattr(s, 'priority') and hasattr(s, 'status') and hasattr(s, 'item_type') for s in schedules[:5]))"
```

语法检查：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/month_window.py main.py
```

行为链路静态检查：

```powershell
rg -n "calendar\.clicked\.connect\(self\.date_selected\.emit\)|date_selected|jump_to_date_from_month|_on_add_clicked|selectedDate|InlineAddViewMonth|view_selected" src/ui/month_window.py src/ui/main_window.py
```

禁止范围检查：

```powershell
git diff --name-only -- src/ui/main_window.py
git diff --name-only -- src/ui/calendar_pop.py
git diff --name-only -- src/ui/common/action_context_menu.py
git diff --name-only -- src/ui/popups
git diff --name-only -- src/ui/common
git diff --name-only -- src/controllers
git diff --name-only -- src/services
git diff --name-only -- src/data
git diff --name-only -- src/repositories
git diff --name-only -- src/theme
git diff --name-only -- src/utils/signals.py
git diff --name-only -- src/utils/styles.py
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
```

允许范围检查：

```powershell
git diff --name-only -- src/ui/month_window.py
git diff --name-only
git status --short --branch
```

预期：

- `src/ui/month_window.py` 有 diff。
- `manage_instruction/Work_Log.md` 有 diff。
- 必要时 `manage_instruction/Work_Task_Prompts.md` 有 diff。
- 禁止范围均无 diff。
- `schedule.db` 无 diff。
- 不出现 `src/ui/main_window.py` diff。
- 不出现 `src/data`、`src/services`、`src/repositories` diff。

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：`M-1（月格状态圆点与今天金色日期）`
- 开工前 git 状态。
- 开工前既有 diff。
- 实际修改文件。
- 月格圆点实现位置。
- 月格圆点数据来源。
- 圆点过滤规则：
  - 是否排除 `status == 2`。
  - 是否排除 `item_type == "todo"`。
  - 日期来源是否为 `start_time` 优先、`end_time` 兜底。
- 未来/今天未完成日程红黄绿规则实现说明。
- 过去日期白/灰规则实现说明。
- 今天日期数字金色实现说明。
- 如何处理 `selectedDate()` 默认今天导致整格高亮的风险。
- 是否保持单击跳日视图链路不变。
- 是否保持添加按钮日期来源不变。
- 是否未新增双击/hover/右键/持久浮窗逻辑。
- 验证命令和结果。
- diff 范围检查结果。
- 未完成事项。
- 风险或疑点。

完成后不要提交 Git，等待决策/顾问窗口复核。
