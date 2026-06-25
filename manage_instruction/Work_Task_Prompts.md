# Work Task Prompts

# 当前待执行提示词：MP-5

## MP-5：保存后多视图刷新与 MP 阶段整体验收

请执行 `MP-5（保存后多视图刷新与阶段整体验收）`。本轮优先做刷新链路审查和验收；只有发现明确刷新缺口时，才做最小源码修正。不得扩大为新功能开发。

## 1. 本轮目标

基于 `MP-0 ~ MP-4` 当前结论，收口月日程 panel、详情弹窗、月格 marker、hover cache 与相关视图的数据刷新关系。

目标行为：

- 详情编辑保存后：
  - 月格 marker 刷新。
  - hover cache 刷新。
  - 已打开月日程 panel 的对应日期列表刷新。
  - 月日程 panel 打开的子 `ScheduleDetailPop` 显示最新数据，或有明确的关闭/刷新策略。
  - 当前可见日/周/月/待办相关数据按已有入口刷新。
- 月 panel 子详情弹窗内直接修改标题、详情、重要性、重复等字段后，也应触发月界面 marker/cache/panel 列表刷新策略。
- 时间、提醒、清单等 picker 编辑完成后，应有一致刷新策略。
- 删除、完成状态修改、时间变更导致日程跨日期后，应有明确刷新策略，至少不能让已打开 panel 长期显示脏数据。
- 不新增数据库字段。
- 不改变保存接口语义。
- 不改重复规则写入语义。
- 不改 MP-3 生命周期规则。
- 不改 MP-4 动态路由规则。
- 不新建全局 EventBus。
- 不把刷新逻辑写进 `ScheduleDetailPop` 去直接调用具体页面。

本轮执行策略：

1. 先审查现有刷新链路。
2. 再用 monkeypatch / fake schedule 做无写库验证。
3. 若现有链路已满足，则不改源码，只记录结论。
4. 若发现明确缺口，只做最小源码修正，并记录修正点与验证结果。

明确缺口判定：

- 如果 `MonthWindow._complete_schedule_edit(...)` 只刷新 marker/cache 并发 `schedule_updated`，但不刷新 `open_day_panels`，应视为刷新缺口。
- 如果 `MonthWindow._complete_schedule_edit(...)` 不刷新或关闭相关 `child_detail_popups`，应视为刷新缺口。
- 如果 `MainWindow.open_schedule_detail_from_month_panel(...)` 创建的月 panel 子详情弹窗没有把 `ScheduleDetailPop.schedule_updated` 接回月界面刷新链路，应视为刷新缺口。
- 如果保存后只刷新主界面 dashboard，而月 panel、hover cache 或月 marker 仍可能保留旧数据，应视为刷新缺口。
- 如果某一类刷新暂不补齐，必须在 `Work_Log.md` 明确说明为什么不阻塞 MP 阶段归档。

## 2. 允许 / 禁止

允许修改：

- `src/ui/main_window.py`（仅当需要补齐统一刷新入口或月 panel 子详情 popup 的刷新连接时）
- `src/ui/month_window.py`（仅当需要刷新 marker/cache/open panels 时）
- `src/ui/popups/month_day_panel.py`（仅当需要补齐 panel 刷新/子详情刷新辅助方法时）
- `src/ui/schedule_detail_pop.py`（仅限刷新方法兼容；原则上不改）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

可选允许，但必须先在日志说明原因：

- `src/ui/dashboard.py`
- `src/ui/week_window.py`
- `src/ui/todo.py`
- `src/ui/todo_board.py`

仅当现有刷新入口缺失且无法由 `MainWindow` / `MonthWindow` 聚合时，才允许最小修改。

禁止修改：

- `src/controllers/`（除非已有协调层必须补齐；若需改，先记录原因）
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

- 不新增功能入口。
- 不新增数据库字段。
- 不改变 `db_manager` API。
- 不改变 `update_schedule_with_repeat(...)` 语义。
- 不改变重复规则写入语义。
- 不重构全局事件总线。
- 不把 `ScheduleDetailPop` 变成具体页面调用者。
- 不改月日程 panel UI 样式。
- 不改月日程 panel 双击详情行为。
- 不改普通视图切换保留 panel 的 MP-3 行为。
- 不改动态编辑路由的 MP-4 行为。
- 不提交 Git。

若开工前已有 diff，必须记录到 `Work_Log.md`，并区分是否为本轮产生。

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
- 已有 diff 是否与本轮有关。
- 不得回退或清理无关 diff。

### 3.2 读取基线

读取：

```powershell
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
Get-Content -Path src\ui\main_window.py -Encoding UTF8
Get-Content -Path src\ui\month_window.py -Encoding UTF8
Get-Content -Path src\ui\popups\month_day_panel.py -Encoding UTF8
Get-Content -Path src\ui\schedule_detail_pop.py -Encoding UTF8
Get-Content -Path src\ui\dashboard.py -Encoding UTF8
Get-Content -Path src\ui\week_window.py -Encoding UTF8
Get-Content -Path src\ui\todo.py -Encoding UTF8
Get-Content -Path src\ui\todo_board.py -Encoding UTF8
```

确认：

- 本轮只执行 MP-5。
- `MonthWindow._complete_schedule_edit(...)` 当前刷新了哪些内容。
- `MonthWindow._refresh_schedule_marker_cache(...)` 是否同时刷新 hover cache。
- `MonthWindow.open_day_panels` 是否有刷新已打开 panel 的机制。
- `MonthWindow` 是否已有 open panel / detail popup 刷新 helper。
- `MonthDayPanel.set_panel_data(...)` 是否可重复调用刷新列表。
- `MonthDayPanel.child_detail_popups` 是否可遍历刷新子详情弹窗。
- `ScheduleDetailPop` 已有哪些刷新方法：
  - `refresh_time_display`
  - `refresh_alarm_display`
  - `refresh_list_display`
  - `refresh_created_display`
  - 其他已存在刷新方法
- `ScheduleDetailPop.schedule_updated` 在 dashboard/todo/month panel 详情链路中分别如何连接。
- `MainWindow` 当前如何响应 `month_window.schedule_updated`。
- day/week/todo/dashboard 现有刷新入口有哪些。

### 3.3 先做刷新链路审查，不默认改源码

审查并记录：

- 月界面编辑保存后是否调用 `_complete_schedule_edit(...)`。
- `_complete_schedule_edit(...)` 是否刷新 marker / hover cache。
- `_complete_schedule_edit(...)` 是否刷新已打开的 `MonthDayPanel`。
- 已打开 `MonthDayPanel` 的 child `ScheduleDetailPop` 是否能刷新显示。
- 从月 panel 打开的 `ScheduleDetailPop.schedule_updated` 是否已接回月界面刷新链路。
- `MainWindow` 是否已经通过 `month_window.schedule_updated` 刷新 day/dashboard/week/todo 相关数据。
- 删除/状态变化是否有同类刷新入口。
- 当前是否存在明确刷新缺口。

如果没有明确缺口：

- 不修改源码。
- 只更新 `Work_Log.md`，记录“MP-5 无需源码修正”。
- 必须说明为什么 open panel、child popup、`ScheduleDetailPop.schedule_updated` 都不会产生脏数据。

如果发现明确缺口：

- 优先在 `MonthWindow` 增加最小刷新 helper，例如：
  - 刷新 marker/cache。
  - 遍历 `open_day_panels`，按 `panel.panel_date` 取最新日程列表并调用 `panel.set_panel_data(...)`。
  - 遍历 panel 的 `child_detail_popups`，对同 id 的 popup 调用已有 refresh 方法。
- 或在 `MainWindow` 现有月 panel 详情桥接中补齐 `popup.schedule_updated` -> 月界面刷新 helper。
- 或在 `MainWindow` 现有 `schedule_updated` 处理入口中补齐月相关刷新。
- 不改变保存逻辑和数据库写入逻辑。

### 3.4 如需补源码，建议最小目标

如确需补源码，建议优先实现可测试的小 helper，而不是把刷新逻辑散在各处。

可选 helper 示例：

- `MonthWindow.refresh_open_day_panels()`
- `MonthWindow.refresh_month_detail_popups(updated_schedule)`
- `MonthWindow.refresh_after_schedule_change(updated_schedule=None)`

要求：

- helper 内部只做 UI/cache 刷新。
- 不写数据库。
- 不调用 `db_manager.update_*`。
- 不改变 picker 保存逻辑。
- 不改变 panel 生命周期。
- 不让 `ScheduleDetailPop` 直接调用 `MonthWindow` 或 `MainWindow`。
- 只调用 `ScheduleDetailPop` 已有刷新显示方法；若某刷新方法不存在，使用 `hasattr` 安全判断。
- 如果日程时间改变导致它不再属于某个已打开 panel 的日期，该 panel 必须重新加载列表，不能继续显示旧日程。
- 如果无法可靠刷新某个子详情弹窗，可以关闭该子弹窗，但必须在日志中说明采用关闭策略的原因。

### 3.5 更新 Work_Log.md

在 `manage_instruction/Work_Log.md` 追加记录，至少包含：

- 本轮任务名称：`MP-5（保存后多视图刷新与阶段整体验收）`
- 开工前 git 状态
- 开工前是否已有 diff
- 实际修改文件
- 是否修改源码；如果未改，明确记录“无需源码修正”
- 现有刷新链路审查结果
- marker / hover cache 刷新结论
- open day panels 刷新结论
- child detail popups 刷新结论
- 月 panel 子 `ScheduleDetailPop.schedule_updated` 连接结论
- day/week/month/todo 相关刷新结论
- 如果做了源码修正，记录 helper 名称、调用点和刷新策略
- 是否未改 MP-3 生命周期
- 是否未改 MP-4 动态路由
- 验证命令和结果
- diff 范围检查结果
- MP-0 ~ MP-5 阶段完成结论
- 未完成事项
- 风险或疑点

## 4. 验收命令

### 4.1 静态定位

```powershell
rg -n "_complete_schedule_edit|_refresh_schedule_marker_cache|open_day_panels|set_panel_data|child_detail_popups|schedule_updated|refresh_open|refresh_after|refresh_month|refresh_data|refresh_week_data|refresh_time_display|refresh_alarm_display|refresh_list_display|refresh_created_display" src/ui/main_window.py src/ui/month_window.py src/ui/popups/month_day_panel.py src/ui/schedule_detail_pop.py src/ui/dashboard.py src/ui/week_window.py src/ui/todo.py src/ui/todo_board.py
```

预期：

- 能定位月界面保存完成后的刷新入口。
- 能定位 `MonthDayPanel.set_panel_data(...)`。
- 能定位 `ScheduleDetailPop` 已有刷新方法。
- 若新增 helper，能定位 helper。

### 4.2 import 验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.main_window import MainWindow; from src.ui.month_window import MonthWindow; from src.ui.popups.month_day_panel import MonthDayPanel; from src.ui.schedule_detail_pop import ScheduleDetailPop; print('mp5 imports ok', MainWindow, MonthWindow, MonthDayPanel, ScheduleDetailPop)"
```

### 4.3 月 panel 可重复刷新列表验证

使用假 schedule，不写数据库：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from datetime import datetime; from types import SimpleNamespace; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.popups.month_day_panel import MonthDayPanel; app=QApplication([]); q=QDate.currentDate(); s1=SimpleNamespace(id=1, title='old title', start_time=datetime.now(), end_time=None, priority=0, status=0); s2=SimpleNamespace(id=1, title='new title', start_time=datetime.now(), end_time=None, priority=2, status=1); p=MonthDayPanel(q, [s1]); p.set_panel_data(q, [s2]); print('panel refresh ok', p.panel_date.toString('yyyy-MM-dd')); assert p.panel_date == q; p.close(); app.quit()"
```

### 4.4 MonthWindow marker/cache 刷新 smoke

不写数据库，只验证方法可调用：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); w._refresh_schedule_marker_cache(); print('marker cache type', type(w.hover_schedule_cache).__name__); assert isinstance(w.hover_schedule_cache, dict); w.close(); app.quit()"
```

### 4.5 如新增 open panel 刷新 helper，验证 helper

如果本轮新增了 `refresh_open_day_panels()` 或等价方法，运行：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); q=QDate.currentDate().addDays(1); w._open_day_panel(q); assert len(w.open_day_panels) == 1; assert hasattr(w, 'refresh_open_day_panels'); w.refresh_open_day_panels(); print('open panel refresh helper ok', len(w.open_day_panels)); assert len(w.open_day_panels) == 1; w.close_day_panels(); w.close(); app.quit()"
```

如果未新增该 helper，日志中必须说明现有链路如何满足，或说明为什么暂不需要。

### 4.6 如新增 detail popup 刷新 helper，验证 helper

如果本轮新增了 `refresh_month_detail_popups(updated_schedule)` 或等价方法，运行：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from datetime import datetime; from types import SimpleNamespace; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; from src.ui.popups.month_day_panel import MonthDayPanel; from src.ui.schedule_detail_pop import ScheduleDetailPop; app=QApplication([]); w=MonthWindow(); panel=MonthDayPanel(QDate.currentDate(), []); s=SimpleNamespace(id=55, title='mp5', description='', start_time=None, end_time=None, priority=0, status=0, item_type='schedule', category_id=None, is_alarm=False, alarm_duration=0, reminder_time=None, repeat_rule='无', created_at=datetime.now()); pop=ScheduleDetailPop(s, source_view='month'); panel.register_child_detail_popup(pop); w.open_day_panels.append(panel); assert hasattr(w, 'refresh_month_detail_popups'); w.refresh_month_detail_popups(s); print('detail popup refresh helper ok'); panel.close(); w.close(); app.quit()"
```

如果未新增该 helper，日志中必须说明现有链路如何满足，或说明为什么暂不需要。

### 4.7 如新增统一刷新 helper，验证 helper 组合

如果本轮新增 `refresh_after_schedule_change(updated_schedule=None)` 或等价方法，运行：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); q=QDate.currentDate().addDays(1); w._open_day_panel(q); assert hasattr(w, 'refresh_after_schedule_change'); w.refresh_after_schedule_change(); print('refresh after schedule change ok', len(w.open_day_panels), type(w.hover_schedule_cache).__name__); w.close_day_panels(); w.close(); app.quit()"
```

如果未新增该 helper，日志中必须说明现有链路如何满足，或说明为什么暂不需要。

### 4.8 MainWindow 现有 schedule_updated 链路 smoke

不写数据库，使用 monkeypatch 记录刷新调用：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from types import SimpleNamespace; from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); hits=[]; w.page_dashboard.refresh_data=lambda: hits.append('dashboard'); w._on_week_schedule_updated(SimpleNamespace(id=-999)); print('refresh hits', hits); assert 'dashboard' in hits; w.close(); app.quit()"
```

如果本轮新增了更多统一刷新入口，请补充对应 monkeypatch 验证。

### 4.9 月 panel 子详情 popup 的 schedule_updated 连接验证

如果本轮补齐 `ScheduleDetailPop.schedule_updated` 到月界面刷新链路的连接，必须做 monkeypatch 验证。

建议验证思路：

- 构造 `MainWindow`、`MonthDayPanel` 和 fake schedule。
- 调用 `open_schedule_detail_from_month_panel(...)`。
- monkeypatch `month_window.refresh_after_schedule_change(...)` 或等价 helper 记录调用。
- emit `popup.schedule_updated`。
- 断言刷新 helper 被调用。

如果未新增该连接，日志中必须说明为什么月 panel 子详情 popup 内联编辑不会造成 panel / marker / hover cache 脏数据。

### 4.10 可选：真实临时写库验收

默认不做真实写库。

只有在执行窗口判断必须验证真实保存链路时，才允许创建唯一临时日程并清理，且必须满足：

- 标题前缀：`__tmp_mp5_refresh_时间戳`
- 不使用重复规则。
- 保存后立即删除。
- 最终 `schedule.db` 无 tracked diff。
- 若任一步清理失败，立即停止并记录，不继续扩大测试。

### 4.11 语法检查

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/main_window.py src/ui/month_window.py src/ui/popups/month_day_panel.py src/ui/schedule_detail_pop.py src/ui/dashboard.py src/ui/week_window.py src/ui/todo.py src/ui/todo_board.py main.py
```

### 4.12 禁止范围检查

```powershell
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

预期以上均无输出。

### 4.13 总范围检查

```powershell
git diff --check
git diff --name-only
git status --short --branch
```

预期：

- `git diff --check` 无 whitespace error；LF/CRLF warning 可记录。
- 如无需源码修正，最终只允许：
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`
- 如需要源码修正，最终只允许本提示词允许范围内文件，并在日志说明具体原因。

## 5. 阶段归档判断

在 `Work_Log.md` 中写明：

- MP-0 到 MP-5 是否完成。
- 月日程 panel UI、详情打开、生命周期、动态路由、刷新验收是否达到阶段目标。
- 是否可以进入下一功能阶段。
- 尚未完成但不阻塞归档的事项。

如果存在未修复刷新缺口：

- 不得写“MP 阶段可归档”。
- 必须说明阻塞项和建议的最小补修工单。

## 6. Work_Task_Prompts.md 处理要求

如需要维护复核锚点，可将当前状态更新为：

```text
MP-5 已执行，等待决策/顾问窗口复核。
MP 阶段等待归档判断。
```

不得自行写入下一阶段执行提示词。

## 7. 完成后要求

完成后不要提交 Git，等待决策/顾问窗口复核。
