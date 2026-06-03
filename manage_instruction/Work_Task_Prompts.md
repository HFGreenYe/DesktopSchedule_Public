# Work Task Prompts

用途：保存主窗口审核后的最终执行提示词或当前复核锚点。执行窗口只应执行本文件中的最终版本。

---

# 当前待执行提示词：M-5

## M-5：月界面添加按钮日期来源联动

请执行 `M-5：月界面添加按钮日期来源联动`。本轮只调整月界面左侧添加按钮的默认日期来源：当用户已经单击选中某个日期时，添加按钮应优先使用该 `user_selected_date`；没有用户主动选中日期时，沿用当前默认逻辑。本轮不修改日程写入逻辑，不接右键菜单，不改变 hover 预览或持久浮窗行为。

## 1. 本轮目标

基于 `Final_Formulation.md`、M-0 / M-1 / M-2 / M-3 / M-4 结论，调整月界面添加入口：

- 有用户主动选中日期时：
  - 点击月界面添加按钮，应使用 `user_selected_date` 作为添加页默认日期。
- 没有用户主动选中日期时：
  - 沿用当前默认逻辑，继续使用 `calendar.selectedDate()`。
- 过去日期不可添加：
  - 如果最终解析出的目标日期是过去日期，应阻止进入添加页。
  - 过去日期判断应基于最终目标日期，而不是只看 `calendar.selectedDate()`。
- 保持当前写入逻辑：
  - 不修改 `InlineAddViewMonth._on_save(...)`。
  - 不修改 `db_manager.add_schedule(...)`。
  - 不写数据库。
- 保持 M-1 / M-2 / M-3 / M-4 行为：
  - 三角数量角标不变。
  - 单击选中和打开持久 panel 不变。
  - 双击跳日视图不变。
  - hover 只读预览不变。
  - 持久浮窗生命周期不变。
- 不接入 M-6 右键菜单。

## 2. 允许/禁止

允许修改：

- `src/ui/month_window.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/ui/main_window.py`
- `src/ui/calendar_pop.py`
- `src/ui/common/action_context_menu.py`
- `src/ui/common/`
- `src/ui/popups/month_day_hover_preview.py`
- `src/ui/popups/month_day_panel.py`
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
- `manage_instruction/Final_Formulation.md`
- `manage_instruction/Work_Formulation.md`
- `manage_instruction/Work_Instruction.md`
- `manage_instruction/Work_Snapshot.md`
- `manage_instruction/History_Instruction.md`
- `manage_instruction/History_Log.md`
- `manage_instruction/ReconstructionDolder/`

禁止事项：

- 不改变 M-1 三角数量角标颜色、数量、过滤规则。
- 不改变今天金色日期逻辑。
- 不改变 M-2 单击选中语义。
- 不改变 M-2 双击跳日视图语义。
- 不改变 `date_selected` 信号语义。
- 不改变 M-3 hover 预览语义。
- 不改变 M-4 持久浮窗语义。
- 不修改 `InlineAddViewMonth._on_save(...)`。
- 不修改 `db_manager.add_schedule(...)`。
- 不接入右键菜单。
- 不新增数据库字段。
- 不写数据库。
- 不提交 Git。

若开工前已有 diff，必须在 `Work_Log.md` 中单独记录，并区分是否属于本轮产生。

## 3. 具体任务

### 3.1 读取当前上下文

读取：

```powershell
Get-Content -Path manage_instruction\Final_Formulation.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
Get-Content -Path src\ui\month_window.py -Encoding UTF8
```

重点确认：

- 当前 `user_selected_date` 的设置位置。
- 当前 `_on_add_clicked(...)` 使用 `self.calendar.selectedDate()` 的旧逻辑。
- 当前 `InlineAddViewMonth.reset(target_date)` 接收日期的方式。
- 当前过去日期限制逻辑。
- 当前 M-4 持久 panel 单击逻辑，本轮不能破坏。
- 当前 hover preview 和 day panel 文件，本轮不能修改。

### 3.2 增加添加目标日期解析

在 `src/ui/month_window.py` 中新增或调整一个小方法，用于解析添加按钮目标日期，例如：

```python
def _get_add_target_date(self):
    ...
```

要求：

- 如果 `self.user_selected_date` 不为 `None` 且有效：
  - 返回 `self.user_selected_date`。
- 如果 `self.user_selected_date` 为 `None` 或无效：
  - 返回 `self.calendar.selectedDate()`，保持旧默认逻辑。
- 返回值应为 `QDate` 或当前代码等价类型。
- 不修改 `QCalendarWidget.selectedDate()` 本身。
- 不在该方法里打开添加页。
- 不在该方法里写数据库。
- 不在该方法里打开、关闭或修改持久 panel。

### 3.3 调整添加按钮入口

修改 `_on_add_clicked(...)`：

- 使用 `_get_add_target_date()` 或等价方法取得目标日期。
- 如果目标日期无效，应安全返回或沿用现有提示逻辑，不进入添加页。
- 过去日期判断基于目标日期。
- 如果目标日期是过去日期：
  - 继续沿用当前提示/阻止逻辑。
  - 不进入添加页。
  - 不写数据库。
- 如果目标日期是今天或未来：
  - 调用 `InlineAddViewMonth.reset(target_date)`。
  - 显示添加页。
- 不改变 `InlineAddViewMonth._on_save(...)`。
- 不改变 `db_manager.add_schedule(...)` 写入数据结构。
- 不改变 add 按钮图标、布局、样式。
- 不改变 view/skin/sort/filter 按钮行为。
- 不关闭已有持久 panel。
- 不新增持久 panel。
- 不改变 hover 预览的显示/隐藏生命周期。

### 3.4 保持交互链路不变

必须确认并保持：

- 单击日期仍更新 `user_selected_date`。
- 单击日期仍打开持久 panel。
- 单击日期仍不 emit `date_selected`。
- 双击 / activated 仍跳日视图。
- 双击跳转前仍调用 `close_day_panels()`。
- hover 预览仍只读，移出日期格后立即隐藏。
- 持久 panel 仍可多个并存，同日复用。
- 添加按钮本身不改变持久 panel 列表。
- 右键菜单仍未接入。

### 3.5 更新日志

更新 `manage_instruction/Work_Log.md`，记录本轮修改、验证和风险。

## 4. 验收命令

开工状态：

```powershell
git status --short --branch
git diff --name-only
```

定位本轮链路：

```powershell
rg -n "user_selected_date|_get_add_target_date|_on_add_clicked|selectedDate|InlineAddViewMonth|reset\(|db_manager\.add_schedule|calendar\.clicked|calendar\.activated|date_selected\.emit|_open_day_panel|MonthDayPanel|hover_preview|ActionContextMenu|contextMenu" src/ui/month_window.py
```

import 验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.month_window import MonthWindow, CalendarCellDelegate, InlineAddViewMonth; from src.ui.popups.month_day_hover_preview import MonthDayHoverPreview; from src.ui.popups.month_day_panel import MonthDayPanel; print('month imports ok', MonthWindow, CalendarCellDelegate, InlineAddViewMonth, MonthDayHoverPreview, MonthDayPanel)"
```

offscreen 构造验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); print('construct ok'); print('user selected', getattr(w, 'user_selected_date', None)); print('has get target', hasattr(w, '_get_add_target_date')); assert hasattr(w, '_get_add_target_date')"
```

无用户选中日期时沿用默认逻辑验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); target=w._get_add_target_date(); print('target', target.toString('yyyy-MM-dd')); print('calendar selected', w.calendar.selectedDate().toString('yyyy-MM-dd')); assert target == w.calendar.selectedDate()"
```

有用户选中日期时优先使用选中日期验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); q=QDate.currentDate().addDays(3); w._on_calendar_date_clicked(q); target=w._get_add_target_date(); print('user selected', w.user_selected_date.toString('yyyy-MM-dd')); print('target', target.toString('yyyy-MM-dd')); assert target == q"
```

添加页 reset 目标日期验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); q=QDate.currentDate().addDays(5); w._on_calendar_date_clicked(q); panel_count=len(w.open_day_panels); w._on_add_clicked(); selected=getattr(w.inline_add_view, 'selected_date', None); print('inline selected', selected.toString('yyyy-MM-dd') if selected else None); print('panel count', panel_count, len(w.open_day_panels)); assert selected == q; assert len(w.open_day_panels) == panel_count"
```

过去日期不可添加验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); old=QDate.currentDate().addDays(-1); w._on_calendar_date_clicked(old); before=getattr(w.inline_add_view, 'selected_date', None); panel_count=len(w.open_day_panels); w._on_add_clicked(); after=getattr(w.inline_add_view, 'selected_date', None); print('old target', old.toString('yyyy-MM-dd')); print('before', before.toString('yyyy-MM-dd') if before else None); print('after', after.toString('yyyy-MM-dd') if after else None); print('panel count', panel_count, len(w.open_day_panels)); assert after == before; assert len(w.open_day_panels) == panel_count"
```

M-2 / M-3 / M-4 行为静态回归：

```powershell
rg -n "calendar\.clicked\.connect\(self\._on_calendar_date_clicked\)|calendar\.clicked\.connect|calendar\.activated\.connect|date_selected\.emit|jump_to_date_from_month|_open_day_panel|open_day_panels|close_day_panels|hover_preview|hovered_date|_on_add_clicked|selectedDate|user_selected_date|ActionContextMenu|contextMenu" src/ui/month_window.py src/ui/main_window.py
```

要求：

- 不应出现 `calendar.clicked.connect(self.date_selected.emit)`。
- `calendar.clicked` 仍应连接 `_on_calendar_date_clicked`。
- `date_selected.emit(...)` 仍只应在双击 / activated 跳转路径中。
- `_on_add_clicked(...)` 应使用目标日期解析方法或等价逻辑。
- `InlineAddViewMonth._on_save(...)` 不应改动。
- 不应新增 `ActionContextMenu` 或 `contextMenu` 链路。

语法检查：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import py_compile, tempfile, os, pathlib; targets=['src/ui/month_window.py','main.py']; extras=['src/ui/popups/month_day_hover_preview.py','src/ui/popups/month_day_panel.py']; targets += [e for e in extras if pathlib.Path(e).exists()]; [py_compile.compile(t, cfile=os.path.join(tempfile.gettempdir(), os.path.basename(t)+'.m5.pyc'), doraise=True) for t in targets]; print('py_compile temp ok', targets)"
```

禁止范围检查：

```powershell
git diff --name-only -- src/ui/main_window.py
git diff --name-only -- src/ui/calendar_pop.py
git diff --name-only -- src/ui/common/action_context_menu.py
git diff --name-only -- src/ui/common
git diff --name-only -- src/ui/popups/month_day_hover_preview.py
git diff --name-only -- src/ui/popups/month_day_panel.py
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
git diff --name-only -- manage_instruction/Final_Formulation.md
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

- 允许 `src/ui/month_window.py` 有 diff。
- 允许 `manage_instruction/Work_Log.md` 有 diff。
- 必要时允许 `manage_instruction/Work_Task_Prompts.md` 有 diff。
- 禁止范围均无 diff。
- `src/ui/popups/month_day_hover_preview.py` 无 diff。
- `src/ui/popups/month_day_panel.py` 无 diff。
- `src/ui/main_window.py` 无 diff。
- `schedule.db` 无 tracked diff。
- `src/data`、`src/services`、`src/repositories` 无 diff。

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：`M-5（月界面添加按钮日期来源联动）`
- 开工前 git 状态。
- 开工前既有 diff。
- 实际修改文件。
- 添加目标日期解析方法。
- 无用户选中日期时是否沿用 `calendar.selectedDate()`。
- 有用户选中日期时是否优先使用 `user_selected_date`。
- 过去日期不可添加是否基于最终目标日期判断。
- 是否保持 `InlineAddViewMonth._on_save(...)` 不变。
- 是否保持 `db_manager.add_schedule(...)` 不变。
- 是否保持 M-1 三角数量角标逻辑不变。
- 是否保持 M-2 单击/双击语义不变。
- 是否保持 M-3 hover 预览语义不变。
- 是否保持 M-4 持久浮窗语义不变。
- 是否未接右键菜单。
- 是否未写数据库。
- 验证命令和结果。
- diff 范围检查结果。
- 未完成事项。
- 风险或疑点。

完成后不要提交 Git，等待决策/顾问窗口复核。
