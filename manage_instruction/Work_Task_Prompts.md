# Work Task Prompts

用途：保存主窗口审核后的最终执行提示词或当前复核锚点。执行窗口只应执行本文件中的最终版本。

---

# 当前待执行提示词：M-2

## M-2：月格单击选中与双击跳日视图

请执行 `M-2：月格单击选中与双击跳日视图`。本轮只调整月界面日期格点击语义：单击只选中日期并高亮，双击才跳转日视图。

本轮不修改 M-1 已完成的月格状态三角数量角标，不修改添加按钮日期来源，不实现 hover 预览，不实现持久浮窗，不接入月界面右键菜单。

## 1. 本轮目标

基于 M-0 / M-1 结论，调整 `src/ui/month_window.py` 的日期格交互：

- 单击日期格：
  - 只更新“用户主动选中日期”状态。
  - 只更新月格选中高亮。
  - 不跳转日视图。
- 双击日期格：
  - 跳转对应日期的日视图。
  - 跳转前调用关闭月界面持久浮窗的安全接口。
  - 当前即使还没有持久浮窗，也要预留安全空实现，供后续 M-4 接入。
- 保持 M-1 月格状态三角数量角标逻辑不变。
- 保持今天日期数字金色逻辑不变。
- 保持添加按钮日期来源不变，添加日期来源联动留到 M-5。
- 不修改数据库、服务层、数据层、Repository、Controller 或路由主流程。

## 2. 允许/禁止

允许修改：

- `src/ui/month_window.py`
- `src/ui/main_window.py`（仅当双击跳转信号连接确有必要时允许最小修改；优先不改）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/ui/calendar_pop.py`
- `src/ui/common/action_context_menu.py`
- `src/ui/popups/`
- `src/ui/common/`
- `src/ui/dashboard.py`
- `src/ui/week_window.py`
- `src/ui/todo.py`
- `src/ui/todo_board.py`
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

- 不改变 M-1 的状态角标颜色、数量、过滤规则。
- 不改变今天金色日期逻辑。
- 不重写 `_on_add_clicked(...)` 为使用 `user_selected_date`。
- 不修改 `InlineAddViewMonth` 写库逻辑。
- 不实现 hover 只读预览。
- 不实现单击持久浮窗。
- 不接入右键菜单。
- 不新增数据库字段。
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
Get-Content -Path src\ui\main_window.py -Encoding UTF8
```

重点确认：

- M-0 对 M-2 的建议。
- M-1 已实现的月格状态三角数量角标与今天金色日期逻辑。
- 当前 `MonthWindow.date_selected` / `MainWindow.jump_to_date_from_month(...)` 链路。
- 当前 `self.calendar.clicked.connect(self.date_selected.emit)` 是单击直接跳转来源，本轮需要解除该直接跳转链路。
- 当前 `_on_add_clicked(...)` 使用 `self.calendar.selectedDate()`，本轮不能重写添加日期来源。

### 3.2 新增用户主动选中日期状态

在 `src/ui/month_window.py` 中新增或完善“用户主动选中日期”状态，例如：

```python
self.user_selected_date = None
```

要求：

- 该状态只由用户单击日期格更新。
- 不能把 `QCalendarWidget.selectedDate()` 默认今天直接当作用户主动选中日期。
- 单击日期后，月格应出现选中高亮。
- 今天仍只用日期数字金色表示；今天是否整格高亮，必须由 `user_selected_date` 决定。
- 如果用户主动单击今天，今天可以整格高亮；未主动单击今天时，今天不能因默认 selected 状态整格高亮。
- 不改变 M-1 的三角数量角标逻辑。

如果需要扩展 `CalendarCellDelegate.set_calendar_state(...)`，只能增加用户选中日期状态传入，不要重构 M-1 的 marker 计算。

### 3.3 将单击日期改为只选中

调整月界面日期格单击行为：

- 将 `calendar.clicked.connect(self.date_selected.emit)` 改为连接内部处理方法，例如 `_on_calendar_date_clicked(qdate)`。
- 单击日期格后，只更新 `user_selected_date` 或等价状态。
- 单击日期格后刷新月格视觉。
- 单击日期格不得发出跳转日视图信号。
- 单击日期格不得调用 `MainWindow.jump_to_date_from_month(...)`。
- 单击日期格不得打开添加页。
- 单击日期格不得写数据库。

选中态绘制要求：

- 月格整格高亮应基于 `user_selected_date`。
- 不应继续直接依赖 Qt 默认 `State_Selected` 作为用户主动选中判断。
- 如果 `QCalendarWidget` 原生 selected 状态仍存在，应在 delegate 绘制中规避它对默认今天的整格高亮影响。

### 3.4 新增双击跳日视图链路

实现日期格双击行为：

- 双击日期格时，获取被双击的准确 `QDate`。
- 双击日期格时，先调用 `close_day_panels()` 或等价安全接口。
- 然后发出跳转信号，复用现有 `MainWindow.jump_to_date_from_month(...)` 链路进入日视图。
- 不修改 `MainWindow.switch_view(...)` 主流程。
- 不新增 Controller / Router 行为。
- 不改变其他视图跳转逻辑。

建议实现：

- 优先使用 `QCalendarWidget.activated(QDate)` 作为双击/激活入口。
- 推荐保留现有 `MonthWindow.date_selected = pyqtSignal(QDate)` 信号，但只在双击/activated 跳转路径中 emit。
- 由于 `MainWindow` 当前已经连接 `self.month_window.date_selected.connect(self.jump_to_date_from_month)`，优先不修改 `src/ui/main_window.py`。
- 如确需新增 `date_double_clicked = pyqtSignal(QDate)` 并调整 `MainWindow` 连接，必须在日志说明理由和最小 diff。

### 3.5 预留关闭持久浮窗安全接口

在 `MonthWindow` 中预留关闭持久浮窗接口，例如：

```python
def close_day_panels(self):
    ...
```

要求：

- 当前没有持久浮窗时，该方法安全无副作用。
- 允许新增 `self.open_day_panels = []`。
- 当前只用于后续 M-4 生命周期接入。
- 双击跳转日视图前必须调用该接口。
- 不实现 M-4 的持久浮窗。
- 不新增真实 popup 文件。
- 不新增 UI 内容。

### 3.6 保持 M-1 和添加逻辑不变

必须确认并保持：

- 月格三角数量角标颜色规则不变。
- 月格三角数量角标计数规则不变。
- 月格三角数量角标显示条件不变。
- 今天金色日期逻辑不变。
- `_on_add_clicked(...)` 不重写为使用 `user_selected_date`。
- `InlineAddViewMonth` 不改。
- `db_manager.add_schedule(...)` 调用不改。
- `schedule.db` 无 tracked diff。

说明：

- 本轮不正式解决“添加按钮使用用户选中日期”的产品需求，该需求留到 M-5。
- 如果 `QCalendarWidget.selectedDate()` 因原生单击行为继续变化，应在日志记录为现状；本轮不得扩大为添加逻辑重构。

### 3.7 更新日志

更新 `manage_instruction/Work_Log.md`，记录本轮修改、验证和风险。

## 4. 验收命令

开工状态：

```powershell
git status --short --branch
git diff --name-only
```

定位本轮链路：

```powershell
rg -n "user_selected_date|selected_date|date_selected|date_double_clicked|activated|mouseDoubleClickEvent|clicked|calendar\.clicked|jump_to_date_from_month|close_day_panels|open_day_panels|_on_add_clicked|InlineAddViewMonth|marker|schedule_marker|marker_count" src/ui/month_window.py src/ui/main_window.py
```

import 验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.month_window import MonthWindow, CalendarCellDelegate, InlineAddViewMonth; from src.ui.main_window import MainWindow; print('month/main import ok', MonthWindow, CalendarCellDelegate, InlineAddViewMonth, MainWindow)"
```

offscreen 构造验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); print('month construct ok'); print('has close_day_panels', hasattr(w, 'close_day_panels')); print('has calendar', hasattr(w, 'calendar')); print('user selected', getattr(w, 'user_selected_date', None)); assert hasattr(w, 'close_day_panels'); assert getattr(w, 'user_selected_date', None) is None"
```

单击不跳转静态验证：

```powershell
rg -n "calendar\.clicked\.connect\(self\.date_selected\.emit\)|calendar\.clicked\.connect|calendar\.activated\.connect|date_selected\.emit|jump_to_date_from_month" src/ui/month_window.py src/ui/main_window.py
```

要求：

- 不应再存在 `calendar.clicked.connect(self.date_selected.emit)`。
- `calendar.clicked.connect(...)` 应连接到月界面内部单击处理方法。
- `date_selected.emit(...)` 必须只出现在双击/activated 跳转路径或等价跳转路径中。
- `MainWindow.jump_to_date_from_month(...)` 可保留。

添加逻辑静态验证：

```powershell
rg -n "_on_add_clicked|selectedDate|InlineAddViewMonth|db_manager\.add_schedule|user_selected_date" src/ui/month_window.py
```

要求：

- `_on_add_clicked(...)` 不应被重写为使用 `user_selected_date`。
- `InlineAddViewMonth` 写库逻辑不应改变。

语法检查：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import py_compile, tempfile, os; targets=['src/ui/month_window.py','src/ui/main_window.py','main.py']; [py_compile.compile(t, cfile=os.path.join(tempfile.gettempdir(), os.path.basename(t)+'.m2.pyc'), doraise=True) for t in targets]; print('py_compile temp ok')"
```

禁止范围检查：

```powershell
git diff --name-only -- src/ui/calendar_pop.py
git diff --name-only -- src/ui/common/action_context_menu.py
git diff --name-only -- src/ui/popups
git diff --name-only -- src/ui/common
git diff --name-only -- src/ui/dashboard.py
git diff --name-only -- src/ui/week_window.py
git diff --name-only -- src/ui/todo.py
git diff --name-only -- src/ui/todo_board.py
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
git diff --name-only -- src/ui/main_window.py
git diff --name-only
git status --short --branch
```

预期：

- 允许 `src/ui/month_window.py` 有 diff。
- 允许 `src/ui/main_window.py` 有最小 diff，但优先应无 diff。
- 允许 `manage_instruction/Work_Log.md` 有 diff。
- 必要时允许 `manage_instruction/Work_Task_Prompts.md` 有 diff。
- 禁止范围均无 diff。
- `schedule.db` 无 tracked diff。
- `src/data`、`src/services`、`src/repositories` 无 diff。

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：`M-2（月格单击选中与双击跳日视图）`
- 开工前 git 状态。
- 开工前既有 diff。
- 实际修改文件。
- 用户主动选中日期状态的实现方式。
- 单击日期如何只更新选中态、不跳日视图。
- 双击日期如何跳转日视图。
- 双击跳转前是否调用 `close_day_panels()` 或等价安全接口。
- 是否预留 `open_day_panels` 或等价生命周期状态。
- 是否保持 M-1 三角数量角标颜色/数量逻辑不变。
- 是否保持今天金色日期逻辑不变。
- 是否保持添加按钮日期来源不变。
- 是否未实现 hover 预览。
- 是否未实现持久浮窗。
- 是否未接右键菜单。
- 验证命令和结果。
- diff 范围检查结果。
- 未完成事项。
- 风险或疑点。

完成后不要提交 Git，等待决策/顾问窗口复核。
