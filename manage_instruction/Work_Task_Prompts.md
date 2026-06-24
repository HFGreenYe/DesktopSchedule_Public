# Work Task Prompts

# 当前待执行提示词：MP-3

## MP-3：月日程弹窗生命周期与跨视图保留规则

请执行 `MP-3（月日程弹窗生命周期与跨视图保留规则）`。本轮只处理月日程持久 panel 及其子详情弹窗的生命周期规则，不改编辑路由，不改详情内容，不改保存刷新策略。

## 1. 本轮目标

基于 `MP-0 ~ MP-2` 当前结论，本轮专门收口月日程弹窗生命周期。

当前事实：

- `MonthDayPanel` 已能承载日程列表。
- `MonthDayPanel` 已支持日程项双击请求详情。
- `MonthDayPanel` 已能登记并关闭自己打开的子 `ScheduleDetailPop`。
- `MonthWindow.hideEvent(...)` 当前会调用 `close_day_panels()`。
- `MainWindow.switch_view(...)` 从月视图切到日/周/待办时，会调用 `self.month_window.hide()`。
- 因此普通视图切换目前会误触发 `MonthWindow.hideEvent(...)` 并关闭月日程 panel。

本轮目标：

- 普通视图切换导致的 `MonthWindow.hide()` 不应关闭月日程 panel。
- 普通视图切换导致的 `MonthWindow.hide()` 不应关闭 panel 打开的子详情弹窗。
- 用户手动关闭某个 `MonthDayPanel` 时，仍关闭它打开的子详情弹窗。
- 子详情弹窗手动关闭时，不关闭父 `MonthDayPanel`。
- 子详情弹窗手动关闭后，应从父 panel 的 `child_detail_popups` 中移除。
- `MonthWindow.closeEvent(...)` 仍应清理所有月日程 panel。
- 显式调用 `close_day_panels()` 的路径仍应清理所有 panel。
- 双击月格跳日视图、右键菜单跳日视图、进入月界面 picker / edit picker 等已显式调用 `close_day_panels()` 的路径，本轮默认保持现状，不擅自改变产品规则。
- 不改跨视图编辑路由；该项留给 MP-4。
- 不改保存后多视图刷新；该项留给 MP-5。

重要边界：

- 本轮只修正“普通 `hide()` 误清理 panel”的问题。
- 本轮不把“所有视图变化都保留 panel”扩大到显式清理路径。
- 如果执行中发现普通视图切换和显式跳日 / picker 清理无法区分，必须记录并暂停该分支，不得自行扩大修改。

## 2. 允许 / 禁止

允许修改：

- `src/ui/month_window.py`
- `src/ui/popups/month_day_panel.py`（仅当需要补强生命周期兼容时）
- `src/ui/schedule_detail_pop.py`（仅当需要补强非业务生命周期信号兼容时；若无需修改则不改）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

禁止修改：

- `src/ui/main_window.py`
- `src/ui/dashboard.py`
- `src/ui/week_window.py`
- `src/ui/todo.py`
- `src/ui/todo_board.py`
- `src/controllers/`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/theme/`
- `src/utils/signals.py`
- `src/utils/styles.py`
- `assets/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `manage_instruction/Work_Instruction.md`
- `manage_instruction/Work_Formulation.md`
- `manage_instruction/Work_Snapshot.md`
- `manage_instruction/ReconstructionDolder/`

禁止事项：

- 不改 `MainWindow.switch_view(...)`。
- 不改 `_resolve_detail_edit_target(...)`。
- 不改 `ScheduleDetailPop` 的编辑字段逻辑。
- 不改月日程 panel UI 样式。
- 不改日程项双击打开详情逻辑。
- 不改数据库。
- 不写入 `schedule.db`。
- 不提交 Git。

若开工前已有 diff，必须在 `Work_Log.md` 记录，并区分是否为本轮产生。尤其如果 MP-2 尚未提交，必须明确记录已有 diff。

## 3. 具体任务

### 3.1 开工前检查

运行：

```powershell
git status --short --branch
git diff --name-only
```

记录：

- 开工前 git 状态。
- 是否存在已有 diff。
- 已有 diff 是否来自 MP-2 未提交内容。
- 本轮不得回退或改动无关 diff。

### 3.2 读取基线

读取：

```powershell
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
Get-Content -Path src\ui\month_window.py -Encoding UTF8
Get-Content -Path src\ui\popups\month_day_panel.py -Encoding UTF8
Get-Content -Path src\ui\schedule_detail_pop.py -Encoding UTF8
```

确认：

- 本轮只执行 MP-3，不执行 MP-4 / MP-5。
- `MonthWindow.hideEvent(...)` 当前是否仍调用 `close_day_panels()`。
- `MonthWindow.closeEvent(...)` 当前是否调用 `close_day_panels()`。
- `MonthWindow.close_day_panels()` 当前是否关闭所有 panel。
- `MonthDayPanel.closeEvent(...)` 当前是否关闭子详情弹窗。
- `MonthDayPanel.register_child_detail_popup(...)` 是否仍存在。
- 显式调用 `close_day_panels()` 的路径有哪些。

### 3.3 调整 MonthWindow.hideEvent 生命周期

目标：普通 `hide()` 不再清理月日程 panel。

建议修改：

- 修改 `MonthWindow.hideEvent(...)`：
  - 不再调用 `self.close_day_panels()`。
  - 如当前类中已有 hover preview 隐藏 helper，可继续隐藏 hover preview。
  - 仍调用 `super().hideEvent(event)`。

要求：

- 不删除 `close_day_panels()`。
- 不改变 `close_day_panels()` 本身的显式清理语义。
- 不改变 `closeEvent(...)` 清理语义。
- 不改变 `_on_calendar_date_activated(...)` 中显式 `close_day_panels()`。
- 不改变 `_handle_context_view("day")` 中显式 `close_day_panels()`。
- 不改变 `go_to_time_picker(...)`、`go_to_alarm_picker(...)`、`go_to_list_picker(...)`、`_show_edit_picker(...)` 等已有显式 `close_day_panels()` 路径，除非该路径被明确证明是普通视图切换误清理。
- 若发现歧义，记录并暂停该分支，不擅自扩大修改。

### 3.4 保持显式清理路径

必须保持：

- 用户点击 panel 关闭按钮时，该 panel 关闭。
- panel 关闭时，它打开的子详情弹窗关闭。
- 子详情弹窗手动关闭时，不关闭父 panel。
- 子详情弹窗手动关闭后，从父 panel 维护列表移除。
- `MonthWindow.closeEvent(...)` 清理所有 panel。
- `MonthWindow.close_day_panels()` 显式调用时清理所有 panel。
- 双击月格跳日视图目前仍显式清理所有 panel。
- 右键菜单跳日视图目前仍显式清理所有 panel。
- 进入月界面添加/编辑 picker 时目前仍显式清理所有 panel。

说明：

- “普通视图切换不关闭 panel”与“显式跳日 / picker 清理 panel”在当前产品规则中分开处理。
- 本轮只修正普通 `hide()` 误清理。
- 若执行中发现双击跳日与普通切换无法区分，必须写入日志并暂停该分支。

### 3.5 更新 Work_Log.md

在 `manage_instruction/Work_Log.md` 追加记录，至少包含：

- 本轮任务名称：`MP-3（月日程弹窗生命周期与跨视图保留规则）`
- 开工前 git 状态
- 开工前是否已有 diff
- 实际修改文件
- `MonthWindow.hideEvent(...)` 调整说明
- `MonthWindow.closeEvent(...)` 是否保持清理
- `close_day_panels(...)` 是否保持显式清理
- panel 手动关闭是否仍关闭子详情
- 子详情手动关闭是否不关闭父 panel
- 子详情手动关闭后是否从父 panel 维护列表移除
- 双击跳日/右键跳日/进入 picker 的显式清理是否保持现状
- 验证命令和结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

## 4. 验收命令

### 4.1 静态定位

```powershell
rg -n "def hideEvent|def closeEvent|close_day_panels|_on_calendar_date_activated|_handle_context_view|go_to_time_picker|go_to_alarm_picker|go_to_list_picker|_show_edit_picker" src/ui/month_window.py
rg -n "register_child_detail_popup|child_detail_popups|_close_child_detail_popups|closeEvent|popup_closed|schedule_double_clicked" src/ui/popups/month_day_panel.py
rg -n "popup_closed|closeEvent" src/ui/schedule_detail_pop.py
```

预期：

- `MonthWindow.hideEvent(...)` 不再调用 `close_day_panels()`。
- `MonthWindow.closeEvent(...)` 仍调用 `close_day_panels()`。
- `close_day_panels()` 方法仍存在。
- 显式调用 `close_day_panels()` 的路径仍可定位。
- `MonthDayPanel.closeEvent(...)` 仍关闭子详情弹窗。
- `MonthDayPanel.register_child_detail_popup(...)` 仍存在。

### 4.2 import 验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.month_window import MonthWindow; from src.ui.popups.month_day_panel import MonthDayPanel; from src.ui.schedule_detail_pop import ScheduleDetailPop; print('mp3 imports ok', MonthWindow, MonthDayPanel, ScheduleDetailPop)"
```

### 4.3 普通 hide 不清理 panel 验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); q=QDate.currentDate().addDays(1); w.show(); app.processEvents(); w._open_day_panel(q); assert len(w.open_day_panels) == 1; panel=w.open_day_panels[0]; w.hide(); app.processEvents(); print('panel count after hide', len(w.open_day_panels)); assert len(w.open_day_panels) == 1; assert w.open_day_panels[0] is panel; w.close_day_panels(); assert w.open_day_panels == []"
```

### 4.4 closeEvent 仍清理 panel 验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); q=QDate.currentDate().addDays(1); w.show(); app.processEvents(); w._open_day_panel(q); assert len(w.open_day_panels) == 1; w.close(); app.processEvents(); print('panel count after close', len(w.open_day_panels)); assert w.open_day_panels == []"
```

### 4.5 显式 close_day_panels 仍清理验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); q=QDate.currentDate().addDays(1); w._open_day_panel(q); assert len(w.open_day_panels) == 1; w.close_day_panels(); print('panel count after explicit close', len(w.open_day_panels)); assert w.open_day_panels == []"
```

### 4.6 panel 手动关闭仍关闭子详情验证

使用假 popup，不打开真实详情弹窗：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication, QWidget; from PyQt6.QtCore import QDate; from src.ui.popups.month_day_panel import MonthDayPanel; app=QApplication([]); p=MonthDayPanel(QDate.currentDate(), []); child=QWidget(); p.register_child_detail_popup(child); assert child in p.child_detail_popups; p.close(); app.processEvents(); print('child count after panel close', len(p.child_detail_popups)); assert len(p.child_detail_popups) == 0"
```

### 4.7 子详情手动关闭不关闭父 panel 验证

使用带 `popup_closed` 信号的假 popup，验证父 panel 不关闭且登记列表移除：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication, QWidget; from PyQt6.QtCore import QDate, pyqtSignal; from src.ui.popups.month_day_panel import MonthDayPanel; class FakeDetailPopup(QWidget):\n    popup_closed = pyqtSignal(object)\n    def closeEvent(self, event):\n        self.popup_closed.emit(self)\n        super().closeEvent(event)\napp=QApplication([]); p=MonthDayPanel(QDate.currentDate(), []); child=FakeDetailPopup(); p.register_child_detail_popup(child); p.show(); child.show(); app.processEvents(); assert child in p.child_detail_popups; child.close(); app.processEvents(); print('panel visible', p.isVisible()); print('child count', len(p.child_detail_popups)); assert p.isVisible(); assert child not in p.child_detail_popups; p.close()"
```

如果 Windows shell 对单行 class 定义转义不稳定，可改写为等价临时脚本或仅验证 `p.isVisible()`，但必须在日志说明验证方式差异。

### 4.8 双击跳日显式清理保持验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); q=QDate.currentDate().addDays(1); w._open_day_panel(q); assert len(w.open_day_panels) == 1; hits=[]; w.date_selected.connect(lambda d: hits.append(d)); w._on_calendar_date_activated(q); print('panel count after activated', len(w.open_day_panels)); print('date hits', len(hits)); assert w.open_day_panels == []; assert hits == [q]"
```

### 4.9 进入月界面 picker 显式清理保持验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from datetime import datetime, timedelta; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); q=QDate.currentDate().addDays(1); w._open_day_panel(q); assert len(w.open_day_panels) == 1; start=datetime.now(); end=start+timedelta(hours=1); w.go_to_time_picker(start, end); print('panel count after picker', len(w.open_day_panels)); assert w.open_day_panels == []"
```

### 4.10 语法检查

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/month_window.py src/ui/popups/month_day_panel.py src/ui/schedule_detail_pop.py main.py
```

### 4.11 禁止范围检查

```powershell
git diff --name-only -- src/ui/main_window.py
git diff --name-only -- src/ui/dashboard.py
git diff --name-only -- src/ui/week_window.py
git diff --name-only -- src/ui/todo.py
git diff --name-only -- src/ui/todo_board.py
git diff --name-only -- src/controllers
git diff --name-only -- src/data
git diff --name-only -- src/repositories
git diff --name-only -- src/services
git diff --name-only -- src/theme
git diff --name-only -- src/utils/signals.py
git diff --name-only -- src/utils/styles.py
git diff --name-only -- assets
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
```

预期以上均无本轮新增输出。

注意：

- 如果 MP-2 尚未提交，`src/ui/main_window.py` 可能已有开工前 diff。执行窗口必须在日志中明确它是开工前 MP-2 diff，不是 MP-3 新增修改。
- 若 MP-2 已提交，MP-3 本轮新增源码 diff 原则上只应出现在 `src/ui/month_window.py`，除非确有生命周期兼容需要。

### 4.12 总范围检查

```powershell
git diff --check
git diff --name-only
git status --short --branch
```

预期：

- `git diff --check` 无 whitespace error；LF/CRLF warning 可记录。
- 若 MP-2 已提交，本轮最终只允许：
  - `src/ui/month_window.py`
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`
- 若 MP-2 未提交，最终 diff 会包含 MP-2 文件；必须在日志中分清开工前 diff 与本轮新增 diff。

## 5. Work_Task_Prompts.md 处理要求

如需要维护复核锚点，可将当前状态更新为：

```text
MP-3 已执行，等待决策/顾问窗口复核。
下一步候选：MP-4。
```

不得在本轮自行写入 `MP-4` 的执行提示词。

## 6. 完成后要求

完成后不要提交 Git，等待决策/顾问窗口复核。
