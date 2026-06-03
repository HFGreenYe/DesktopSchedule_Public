# Work Task Prompts

用途：保存主窗口审核后的最终执行提示词或当前复核锚点。执行窗口只应执行本文件中的最终版本。

---

# 当前待执行提示词：M-4

## M-4：单击日期持久浮窗壳

请执行 `M-4：单击日期持久浮窗壳`。本轮只实现月界面单击日期后显示的外侧持久浮窗壳：单击日期仍更新选中态，不跳日视图，同时在月界面外侧打开一个可手动关闭的日期面板壳。本轮不实现编辑能力，不改变添加按钮日期来源，不接入右键菜单，不修改数据库写入逻辑。

## 1. 本轮目标

基于 `Final_Formulation.md`、M-0 / M-1 / M-2 / M-3 结论，在月界面增加“单击日期持久浮窗壳”：

- 单击日期格：
  - 继续更新 `user_selected_date`。
  - 继续更新选中高亮。
  - 不跳转日视图。
  - 新增：在月界面外侧显示该日期的持久浮窗壳。
- 持久浮窗：
  - 显示在月界面外侧，优先在月界面右侧，不与月历主体重叠。
  - 可多个并存。
  - 至少有关闭按钮。
  - 当前只做壳或简版只读列表，不提供编辑、删除、添加能力。
  - 鼠标移走后不自动隐藏。
  - 点击其他日期时，已有持久浮窗不自动关闭。
- 双击日期跳日视图：
  - 仍先调用 `close_day_panels()`。
  - 必须关闭全部已打开持久浮窗。
  - 然后跳转日视图。
- 月界面关闭或隐藏：
  - 必须关闭全部已打开持久浮窗，避免孤儿窗口。
- 保持 M-3 hover 预览：
  - hover 只读预览仍可用。
  - 鼠标移出日期格仍立即隐藏 hover 预览。
  - hover 预览不得变成持久浮窗。
- 不实现 M-5 的添加日期来源联动。
- 不实现 M-6 的右键菜单。

## 2. 允许/禁止

允许修改：

- `src/ui/month_window.py`
- `src/ui/popups/month_day_panel.py`（如需要新增持久浮窗壳组件）
- `src/ui/popups/__init__.py`（仅在必须导出新组件时允许；优先不改）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/ui/main_window.py`
- `src/ui/calendar_pop.py`
- `src/ui/common/action_context_menu.py`
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
- 不改变 M-3 hover 预览的只读和移出隐藏语义。
- 不把 hover 预览组件改造成持久浮窗。
- 不改变 `_on_add_clicked(...)` 日期来源。
- 不修改 `InlineAddViewMonth` 写库逻辑。
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
Get-Content -Path src\ui\popups\month_day_hover_preview.py -Encoding UTF8
Get-ChildItem -Path src\ui\popups -Force
```

重点确认：

- `Final_Formulation.md` 中关于月界面、UI popup、窗口类膨胀风险和技术债的约束。
- M-4 在阶段合同中的边界。
- M-2 当前 `user_selected_date`、`open_day_panels`、`close_day_panels()` 实现。
- M-3 当前 hover 预览组件和 hover 数据缓存。
- 当前 `_on_calendar_date_clicked(qdate)` 单击入口。
- 当前 `_on_calendar_date_activated(qdate)` 双击 / activated 跳转入口。
- 当前 `_on_add_clicked(...)` 日期来源，本轮不得修改。

### 3.2 新增持久浮窗壳组件

如当前没有合适组件，新增：

- `src/ui/popups/month_day_panel.py`

建议类名：

```python
class MonthDayPanel(QWidget):
    closed = pyqtSignal(object)
```

组件要求：

- 独立顶层浮窗或 tool window，避免被 `MonthWindow` 裁剪。
- 不抢主窗口焦点或尽量减少焦点干扰。
- 至少包含：
  - 日期标题。
  - 关闭按钮。
  - 简单内容区。
- 内容区本轮可显示：
  - 空白占位。
  - 或简版只读日程列表。
- 不提供编辑按钮。
- 不提供删除按钮。
- 不提供添加按钮。
- 不连接数据库写入。
- 不依赖 `db_manager`。
- 不依赖 Repository / Service。
- 不依赖 `MainWindow`。
- 不依赖 `MonthWindow` 具体实例。
- 可接收日期和日程列表数据用于展示。
- 关闭按钮应只关闭当前 panel，并通知 `MonthWindow` 从 `open_day_panels` 中移除，避免列表保留死对象。

建议：

- 使用轻量白底样式，视觉可先保持基础可用。
- 不做复杂 QSS 接入。
- 不复用 `MonthDayHoverPreview` 作为可编辑容器。
- 如果复用显示文本逻辑，只能复用纯展示辅助，不要把 hover popup 变成持久 panel。

### 3.3 在 MonthWindow 中打开持久浮窗

在 `src/ui/month_window.py` 中扩展单击日期逻辑：

- 单击日期格后：
  - 保持已有 `_on_calendar_date_clicked(qdate)` 中更新 `user_selected_date` 的逻辑。
  - 保持刷新选中高亮。
  - 新增打开持久浮窗壳。
- 不 emit `date_selected`。
- 不跳日视图。
- 不打开添加页。
- 不写数据库。
- 可在打开持久浮窗前隐藏 hover 预览，避免两个浮窗重叠。
- 不关闭已有持久浮窗。
- 不改变其他已打开持久浮窗。

建议新增方法：

```python
def _open_day_panel(self, qdate):
    ...
```

要求：

- 使用 `open_day_panels` 记录已打开 panel。
- panel 关闭时必须从 `open_day_panels` 移除。
- 同一天如已有 panel，优先激活/置顶已有 panel，避免重复打开完全相同日期。
- 不同日期 panel 可并存。
- 多个 panel 的位置应错开，避免完全重叠。
- panel 移除逻辑必须能处理用户手动关闭、程序批量关闭、重复关闭三种情况，不应抛异常。

### 3.4 持久浮窗定位

持久浮窗必须显示在月界面外侧，优先右侧。

定位要求：

- 不要显示在日期格右下角。
- 不要作为月历内部子控件被裁剪。
- 不挤压月历布局。
- 不遮挡月历主体为优先目标。
- 位置可基于 `MonthWindow.frameGeometry().topRight()` 或等价全局坐标。
- 多个 panel 并存时，按打开顺序做垂直或斜向偏移，避免完全重叠。
- 若屏幕边界不足，本轮可记录风险，不必做复杂屏幕边界回退。

### 3.5 完善生命周期清理

完善 `close_day_panels()`：

- 关闭所有已打开 panel。
- 清空 `open_day_panels`。
- 对已被用户手动关闭的 panel，不应报错。
- 当前没有 panel 时安全无副作用。

在以下场景调用或确保会调用：

- 双击 / activated 跳日视图前。
- `MonthWindow.closeEvent(...)`。
- `MonthWindow.hideEvent(...)`。

注意：

- 不改变双击跳转日视图逻辑。
- 不改变 `date_selected.emit(qdate)` 的位置，除非只是为了保证关闭 panel 在 emit 前发生。
- hover 预览隐藏逻辑仍独立，不应加入 `open_day_panels`。

### 3.6 提供持久 panel 展示数据

本轮可以复用 M-3 的只读日程缓存：

- `hover_schedule_cache`
- 或重命名为更通用的 `day_schedule_cache`

要求：

- 不改变数据过滤规则。
- 不写数据库。
- 不改 `db_manager`。
- 不改 repository / service。
- 排除 `status == 2`。
- 排除 `item_type != "schedule"`。
- 日期来源优先 `start_time.date()`，缺失时用 `end_time.date()`。
- 重复日程实例按独立记录展示。
- 不改变 M-1 marker 颜色/数量计算。

如果为了命名合理，将 `hover_schedule_cache` 重命名为通用名称，必须确认 M-3 hover 预览仍正常，并在日志说明。

### 3.7 保持 M-2 / M-3 行为不变

必须确认并保持：

- `calendar.clicked` 仍连接 `_on_calendar_date_clicked`。
- 单击日期不 emit `date_selected`。
- `calendar.activated` 仍负责跳日视图。
- `date_selected.emit(...)` 仍只在双击 / activated 跳转路径中触发。
- `close_day_panels()` 在双击跳转前调用。
- hover 预览仍只读。
- hover 预览仍在鼠标移出日期格后立即隐藏。
- `_on_add_clicked(...)` 仍使用 `selectedDate()`，不得改为 `user_selected_date`。
- `InlineAddViewMonth` 不改。
- `schedule.db` 无 tracked diff。

### 3.8 更新日志

更新 `manage_instruction/Work_Log.md`，记录本轮修改、验证和风险。

## 4. 验收命令

开工状态：

```powershell
git status --short --branch
git diff --name-only
```

定位本轮链路：

```powershell
rg -n "MonthDayPanel|month_day_panel|open_day_panels|close_day_panels|_open_day_panel|user_selected_date|calendar\.clicked|calendar\.activated|date_selected\.emit|hover_preview|hovered_date|MonthDayHoverPreview|hideEvent|closeEvent|_on_add_clicked|selectedDate|ActionContextMenu|contextMenu" src/ui/month_window.py src/ui/popups
```

静态依赖检查：

```powershell
rg -n "db_manager|Repository|Service|MainWindow|MonthWindow|DashboardView|TodoBoardWindow|global_signals|switch_view|switch_to_add_page|add_schedule|update_schedule|delete_schedule" src/ui/popups/month_day_panel.py
```

预期：无运行依赖命中。若命中来自注释或类型说明，必须在日志中解释；更推荐代码注释里避免这些词。

import 验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.month_window import MonthWindow, CalendarCellDelegate, InlineAddViewMonth; from src.ui.popups.month_day_hover_preview import MonthDayHoverPreview; print('month/hover import ok', MonthWindow, CalendarCellDelegate, InlineAddViewMonth, MonthDayHoverPreview)"
```

如新增 `month_day_panel.py`，执行：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.popups.month_day_panel import MonthDayPanel; print('day panel import ok', MonthDayPanel)"
```

offscreen 构造验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); print('month construct ok'); print('has open_day_panels', hasattr(w, 'open_day_panels')); print('panel count', len(getattr(w, 'open_day_panels', []))); print('has close_day_panels', hasattr(w, 'close_day_panels')); assert hasattr(w, 'open_day_panels'); assert hasattr(w, 'close_day_panels')"
```

单击打开 panel 验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); hits=[]; w.date_selected.connect(lambda d: hits.append(d)); q=QDate(2026, 6, 15); w._on_calendar_date_clicked(q); print('user selected', w.user_selected_date.toString('yyyy-MM-dd') if w.user_selected_date else None); print('date_selected hits', len(hits)); print('panel count', len(w.open_day_panels)); assert w.user_selected_date == q; assert len(hits) == 0; assert len(w.open_day_panels) >= 1"
```

同日复用 / 不重复打开验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); q=QDate(2026,6,15); w._on_calendar_date_clicked(q); first_count=len(w.open_day_panels); w._on_calendar_date_clicked(q); second_count=len(w.open_day_panels); print('same day counts', first_count, second_count); assert second_count == first_count"
```

关闭全部 panel 验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); w._on_calendar_date_clicked(QDate(2026,6,15)); w._on_calendar_date_clicked(QDate(2026,6,16)); print('before close', len(w.open_day_panels)); assert len(w.open_day_panels) >= 1; w.close_day_panels(); print('after close', len(w.open_day_panels)); assert len(w.open_day_panels) == 0"
```

双击路径关闭 panel 并跳转信号验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); w._on_calendar_date_clicked(QDate(2026,6,15)); hits=[]; w.date_selected.connect(lambda d: hits.append(d)); q=QDate(2026,6,16); print('before activated panels', len(w.open_day_panels)); w._on_calendar_date_activated(q); print('after activated panels', len(w.open_day_panels)); print('hits', [d.toString('yyyy-MM-dd') for d in hits]); assert len(w.open_day_panels) == 0; assert hits == [q]"
```

M-3 hover 回归验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); idx=w.calendar_table_view.model().index(2,0); q=w.cell_delegate._date_for_index(idx); w._show_hover_preview(q, idx); print('hover visible', w.hover_preview_popup.isVisible()); assert w.hover_preview_popup.isVisible(); w._hide_hover_preview(); print('hover hidden', w.hover_preview_popup.isVisible()); assert not w.hover_preview_popup.isVisible()"
```

M-2 行为静态回归：

```powershell
rg -n "calendar\.clicked\.connect\(self\._on_calendar_date_clicked\)|calendar\.clicked\.connect|calendar\.activated\.connect|date_selected\.emit|jump_to_date_from_month|_on_add_clicked|selectedDate|user_selected_date|close_day_panels|open_day_panels" src/ui/month_window.py src/ui/main_window.py
```

要求：

- 不应出现 `calendar.clicked.connect(self.date_selected.emit)`。
- `calendar.clicked` 仍应连接 `_on_calendar_date_clicked`。
- `date_selected.emit(...)` 仍只应在双击 / activated 跳转路径中。
- `_on_add_clicked(...)` 仍应使用 `selectedDate()`，不得改为使用 `user_selected_date`。
- `close_day_panels()` 应关闭真实 panel，但不应改变添加逻辑。

语法检查：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import py_compile, tempfile, os, pathlib; targets=['src/ui/month_window.py','main.py']; extras=['src/ui/popups/month_day_hover_preview.py','src/ui/popups/month_day_panel.py']; targets += [e for e in extras if pathlib.Path(e).exists()]; [py_compile.compile(t, cfile=os.path.join(tempfile.gettempdir(), os.path.basename(t)+'.m4.pyc'), doraise=True) for t in targets]; print('py_compile temp ok', targets)"
```

禁止范围检查：

```powershell
git diff --name-only -- src/ui/main_window.py
git diff --name-only -- src/ui/calendar_pop.py
git diff --name-only -- src/ui/common/action_context_menu.py
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
git diff --name-only -- src/ui/popups
git diff --name-only
git status --short --branch
```

预期：

- 允许 `src/ui/month_window.py` 有 diff。
- 允许 `src/ui/popups/month_day_panel.py` 有 diff。
- 如确需导出组件，允许 `src/ui/popups/__init__.py` 有最小 diff；优先不改。
- 允许 `manage_instruction/Work_Log.md` 有 diff。
- 必要时允许 `manage_instruction/Work_Task_Prompts.md` 有 diff。
- 禁止范围均无 diff。
- `schedule.db` 无 tracked diff。
- `src/ui/main_window.py` 无 diff。
- `src/data`、`src/services`、`src/repositories` 无 diff。

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：`M-4（月格单击持久浮窗壳）`
- 开工前 git 状态。
- 开工前既有 diff。
- 实际修改文件。
- 持久浮窗组件位置。
- 持久浮窗是否为独立顶层窗口。
- 单击日期如何打开持久浮窗且不跳日视图。
- 持久浮窗定位方式，是否在月界面外侧。
- 多个持久浮窗如何并存和错位。
- 同一天重复单击如何复用已有 panel。
- 关闭按钮如何关闭单个 panel。
- `open_day_panels` 如何维护。
- `close_day_panels()` 如何关闭全部 panel。
- 月界面 hide/close/双击跳转时是否关闭全部 panel。
- 是否保持 M-1 三角数量角标逻辑不变。
- 是否保持 M-2 单击/双击语义不变。
- 是否保持 M-3 hover 预览语义不变。
- 是否保持添加按钮日期来源不变。
- 是否未接右键菜单。
- 是否未写数据库。
- 验证命令和结果。
- diff 范围检查结果。
- 未完成事项。
- 风险或疑点。

完成后不要提交 Git，等待决策/顾问窗口复核。
