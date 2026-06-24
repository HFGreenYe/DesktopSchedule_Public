# Work Task Prompts

# 当前待执行提示词：MP-2

## MP-2：月日程弹窗日程项双击打开共享详情弹窗

请执行 `MP-2（月日程弹窗日程项双击打开共享详情弹窗）`。本轮只增加“月日程弹窗内日程项双击请求详情”与“主窗口统一打开共享 `ScheduleDetailPop`”的最小链路，不改跨视图编辑路由，不改普通视图切换时 panel 保留/关闭规则。

## 1. 本轮目标

基于 `MP-0` 审查结论和 `MP-1` 已完成的 `MonthDayPanel` 列表承载能力，本轮新增：

- 月日程弹窗中的日程项支持双击。
- 双击某条日程项后，打开共享 `ScheduleDetailPop`。
- `MonthDayPanel` 不直接持有 `MainWindow`。
- `MonthWindow` 只转发详情请求，不直接创建 `ScheduleDetailPop`。
- `ScheduleDetailPop` 不直接调用具体页面。
- 详情弹窗打开入口由 `MainWindow` 的最小桥接方法承接。
- 月日程弹窗关闭时，应关闭由它打开的子详情弹窗。
- 同一个 `owner_panel` 内同一 `schedule.id` 的详情弹窗重复打开时优先复用/置顶，避免重复多个相同详情。
- 不处理详情编辑路由重构；现有 `_resolve_detail_edit_target(...)` 不在本轮重写。
- 不处理普通视图切换时 panel 保留/关闭规则；留给 `MP-3`。
- 不处理保存后多视图刷新；留给 `MP-5`。

重要范围说明：

- 阶段合同中曾把“跨视图切换不关闭 panel/详情弹窗”列入 MP-2 验收，但本轮按 `MP-0` 后的拆分收窄执行，该项明确留给 `MP-3`。
- 本轮只验证“panel 手动关闭时关闭其子详情弹窗”，不验证普通视图切换保留规则。
- 本轮不复用 `DashboardView._show_detail_popup(...)` 作为月 panel 的详情创建入口，因为当前该方法不返回 popup，且 `dashboard.py` 不在允许修改范围内。

## 2. 允许 / 禁止

允许修改：

- `src/ui/popups/month_day_panel.py`
- `src/ui/month_window.py`
- `src/ui/main_window.py`（仅允许增加/连接月日程弹窗详情打开桥接）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

原则上不修改，但若静态审查证明必须适配才可最小修改并在日志说明：

- `src/ui/schedule_detail_pop.py`

禁止修改：

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

- 不改数据库。
- 不改 `db_manager`。
- 不改 `ScheduleDetailPop` 的编辑字段逻辑。
- 不重写 `_resolve_detail_edit_target(...)`。
- 不复用或修改 `DashboardView._show_detail_popup(...)`。
- 不把 `MonthDayPanel` 绑定到 `MainWindow`。
- 不让 `ScheduleDetailPop` 直接调用 `MonthWindow` / `DashboardView` / `WeekWindow` / `TodoView`。
- 不改变 `MonthWindow.hideEvent(...)` / `closeEvent(...)` / `close_day_panels(...)` 生命周期规则。
- 不改 `MP-1` 的青色渐变 UI、紧凑列表布局和列表数量规则。
- 不处理普通视图切换时 panel 保留/关闭规则。
- 不提交 Git。

若开工前已有 diff，必须记录到 `Work_Log.md`，不得清理或回退无关 diff。

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

### 3.2 读取基线

读取：

```powershell
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
Get-Content -Path src\ui\popups\month_day_panel.py -Encoding UTF8
Get-Content -Path src\ui\month_window.py -Encoding UTF8
Get-Content -Path src\ui\main_window.py -Encoding UTF8
Get-Content -Path src\ui\schedule_detail_pop.py -Encoding UTF8
```

确认：

- 本轮只执行 `MP-2`，不执行 `MP-3 / MP-4 / MP-5`。
- `MonthDayPanel` 当前只负责展示和关闭信号。
- `MainWindow` 当前已有 `_resolve_detail_edit_target(...)`，本轮不重写。
- 当前共享详情弹窗为 `ScheduleDetailPop`。
- 当前 `DashboardView._show_detail_popup(...)` 不返回 popup，本轮不复用它作为月 panel 详情入口。

### 3.3 MonthDayPanel 增加日程项双击请求

在 `src/ui/popups/month_day_panel.py` 中增加轻量信号和日程项双击入口。

建议新增信号：

```python
schedule_double_clicked = pyqtSignal(object, object)
```

参数：

- 第一个参数：schedule 对象。
- 第二个参数：当前 `MonthDayPanel` 实例。

要求：

- 每个日程 item 保存对应 schedule 对象。
- 双击日程 item 时 emit：

```python
self.schedule_double_clicked.emit(schedule, self)
```

- 为了便于测试，可新增内部 helper：

```python
def _emit_schedule_double_clicked(self, schedule):
    self.schedule_double_clicked.emit(schedule, self)
```

- 日程 item 可以使用自定义轻量 `QFrame` 子类或事件过滤器实现双击。
- 不改变 `set_panel_data(qdate, schedules)` 对外入口。
- 不改变列表展示顺序。
- 不在 panel 内查数据库。
- 不导入 `MainWindow`。
- 不导入 `db_manager`。
- 不导入 Repository / Service。
- 原有 `closed` 信号仍保留。
- 原有拖动能力仍保留。

### 3.4 MonthDayPanel 管理由它打开的子详情弹窗

在 `MonthDayPanel` 内新增子详情弹窗生命周期管理能力。

建议：

```python
self.child_detail_popups = []
```

新增注册方法，例如：

```python
def register_child_detail_popup(self, popup):
    ...
```

要求：

- `register_child_detail_popup(...)` 只登记由当前 panel 打开的详情弹窗。
- 子详情弹窗自身关闭后，应从 `child_detail_popups` 中移除。
- panel 关闭时关闭这些子详情弹窗。
- 如果 popup 已被销毁或已关闭，关闭 panel 时不得报错。
- panel 关闭时只负责关闭自己打开的子详情弹窗。
- 不关闭 Dashboard / Week / Todo 等其他入口打开的详情弹窗。
- 不改变 `closed` 信号只 emit 一次的语义。

重复打开规则：

- 复用范围限定为同一个 `owner_panel` 内同一 `schedule.id` 的详情弹窗。
- 不得把 Dashboard / Week / Todo 已打开的同日程详情弹窗注册为 `owner_panel` 的子弹窗。
- 如果实现全局复用，必须记录 popup 的 `owner_panel`；只有 `owner_panel` 相同的 popup 才允许被 panel 关闭。

### 3.5 MonthWindow 转发详情请求

在 `src/ui/month_window.py` 中增加从 panel 到主窗口的转发信号。

建议在 `MonthWindow` 类上新增信号：

```python
schedule_detail_requested = pyqtSignal(object, object)
```

参数：

- schedule 对象。
- owner panel。

在创建 `MonthDayPanel` 后连接：

```python
panel.schedule_double_clicked.connect(self.schedule_detail_requested.emit)
```

要求：

- `MonthWindow` 不直接创建 `ScheduleDetailPop`。
- `MonthWindow` 不直接调用 `MainWindow` 方法。
- 不改变 `_open_day_panel(...)` 的定位和复用逻辑。
- 不改变 `hideEvent(...) / closeEvent(...) / close_day_panels(...)`。
- 不改变普通视图切换时 panel 生命周期规则。

### 3.6 MainWindow 增加月日程详情打开桥接

在 `src/ui/main_window.py` 中最小接入 `MonthWindow.schedule_detail_requested`。

建议在 `MainWindow.__init__` 中连接：

```python
self.month_window.schedule_detail_requested.connect(self.open_schedule_detail_from_month_panel)
```

新增方法：

```python
def open_schedule_detail_from_month_panel(self, schedule_data, owner_panel=None):
    ...
```

目标：

- 在 `MainWindow` 内创建/复用共享 `ScheduleDetailPop`。
- `source_view` 使用 `"month"`，以保持来源兼容。
- 将详情弹窗注册回 `owner_panel.register_child_detail_popup(pop)`。
- 同一个 `owner_panel` 内同一 `schedule.id` 重复请求时复用/置顶已有 popup，不再创建新 popup。
- 不把 Dashboard / Week / Todo 已打开的同日程 popup 注册到 owner panel。
- 详情弹窗的编辑信号继续走现有 `go_to_time_picker_for_edit(...)` / `go_to_alarm_picker_for_edit(...)` / `go_to_list_picker_for_edit(...)` 链路。
- `ScheduleDetailPop.schedule_updated` 可连接到现有刷新入口，但不得在本轮扩展“保存后多视图刷新”策略。
- 不重写 `_resolve_detail_edit_target(...)`。
- 不改变 Dashboard / Week / Todo 的详情打开链路。

明确禁止：

- 不调用 `self.page_dashboard._show_detail_popup(...)` 来打开月 panel 详情弹窗。
- 不修改 `src/ui/dashboard.py` 来让 `_show_detail_popup(...)` 返回 popup。
- 不让 `MonthDayPanel` 或 `MonthWindow` 承担主窗口业务路由。

## 4. 验收命令

### 4.1 静态定位

```powershell
rg -n "schedule_double_clicked|register_child_detail_popup|child_detail_popups|_emit_schedule_double_clicked|mouseDoubleClickEvent|closed|set_panel_data" src/ui/popups/month_day_panel.py
rg -n "schedule_detail_requested|schedule_double_clicked|_open_day_panel|close_day_panels|hideEvent|closeEvent" src/ui/month_window.py
rg -n "open_schedule_detail_from_month_panel|schedule_detail_requested|ScheduleDetailPop|_resolve_detail_edit_target|go_to_time_picker_for_edit|go_to_alarm_picker_for_edit|go_to_list_picker_for_edit|_show_detail_popup" src/ui/main_window.py
```

### 4.2 禁止依赖检查

```powershell
rg -n "MainWindow|db_manager|Repository|Service|ScheduleRepository|CategoryRepository|switch_view|_resolve_detail_edit_target" src/ui/popups/month_day_panel.py
rg -n "db_manager|Repository|ScheduleRepository|CategoryRepository" src/ui/popups/month_day_panel.py src/ui/month_window.py
rg -n "_show_detail_popup" src/ui/month_window.py src/ui/popups/month_day_panel.py
```

预期：

- `month_day_panel.py` 不应出现 `MainWindow`、`db_manager`、Repository、Service、`switch_view`。
- `month_window.py` 不应新增数据库或 Repository 依赖。
- `month_day_panel.py` / `month_window.py` 不应调用 `_show_detail_popup(...)`。
- 若命中来自既有代码或注释，必须在日志中说明。

### 4.3 import 验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.popups.month_day_panel import MonthDayPanel; from src.ui.month_window import MonthWindow; from src.ui.main_window import MainWindow; from src.ui.schedule_detail_pop import ScheduleDetailPop; print('mp2 imports ok', MonthDayPanel, MonthWindow, MainWindow, ScheduleDetailPop)"
```

### 4.4 MonthDayPanel 双击信号 offscreen 验证

使用假 schedule 对象，不读数据库：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from types import SimpleNamespace; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.popups.month_day_panel import MonthDayPanel; app=QApplication([]); schedule=SimpleNamespace(id=123, title='mp2 sample', priority=1, status=0); p=MonthDayPanel(QDate.currentDate(), [schedule]); hits=[]; p.schedule_double_clicked.connect(lambda s, owner: hits.append((s, owner))); p._emit_schedule_double_clicked(schedule); print('hits', len(hits)); assert hits == [(schedule, p)]"
```

如果实现没有 `_emit_schedule_double_clicked(...)`，请改用等价公开/内部方法验证，并在日志说明实际方法名。

### 4.5 子详情弹窗生命周期 offscreen 验证

使用假 popup 对象，不打开真实详情弹窗：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication, QWidget; from PyQt6.QtCore import QDate; from src.ui.popups.month_day_panel import MonthDayPanel; app=QApplication([]); p=MonthDayPanel(QDate.currentDate(), []); child=QWidget(); hits=[]; child.destroyed.connect(lambda *_: hits.append('destroyed')); p.register_child_detail_popup(child); assert child in p.child_detail_popups; p.close(); app.processEvents(); print('child count', len(p.child_detail_popups)); print('destroy hits', len(hits)); assert child not in p.child_detail_popups or len(p.child_detail_popups) == 0"
```

若 Qt offscreen 下 `destroyed` 信号时机不稳定，以 `child.isVisible()` / `child.close()` 调用结果和列表清理为主，并在日志说明。

### 4.6 MonthWindow 转发信号 offscreen 验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from types import SimpleNamespace; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); q=QDate.currentDate().addDays(1); w._open_day_panel(q); assert len(w.open_day_panels) == 1; panel=w.open_day_panels[0]; schedule=SimpleNamespace(id=456, title='mp2 month'); hits=[]; w.schedule_detail_requested.connect(lambda s, owner: hits.append((s, owner))); panel._emit_schedule_double_clicked(schedule); print('hits', len(hits)); assert hits == [(schedule, panel)]; w.close_day_panels()"
```

如果实现没有 `_emit_schedule_double_clicked(...)`，请改用等价方法验证。

### 4.7 MainWindow 桥接静态/轻量验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.main_window import MainWindow; assert hasattr(MainWindow, 'open_schedule_detail_from_month_panel'); assert hasattr(MainWindow, '_resolve_detail_edit_target'); print('main bridge exists')"
```

可选 offscreen smoke：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); assert hasattr(w.month_window, 'schedule_detail_requested'); assert hasattr(w, 'open_schedule_detail_from_month_panel'); print('main window bridge smoke ok')"
```

如果完整 `MainWindow()` 构造受桌面环境影响失败，记录失败原因，并至少保证 import 与静态检查通过。

### 4.8 同 owner panel 重复打开复用验证

优先使用 offscreen 轻量方式验证。若完整 `MainWindow()` 可构造，建议验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from types import SimpleNamespace; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.main_window import MainWindow; from src.ui.popups.month_day_panel import MonthDayPanel; app=QApplication([]); w=MainWindow(); panel=MonthDayPanel(QDate.currentDate(), []); schedule=SimpleNamespace(id=789, title='mp2 duplicate', description='', start_time=None, end_time=None, priority=0, status=0, item_type='schedule', category_id=None, is_alarm=False, alarm_duration=0, reminder_time=None, repeat_rule='无', created_at=None); w.open_schedule_detail_from_month_panel(schedule, panel); w.open_schedule_detail_from_month_panel(schedule, panel); count=sum(1 for p in panel.child_detail_popups if getattr(getattr(p, 'data', None), 'id', None) == 789); print('same owner popup count', count); assert count == 1; panel.close()"
```

如果真实 `ScheduleDetailPop` 需要更多字段导致该 smoke 不稳定，则必须在日志中记录：

- 实际缺失字段。
- 已用静态检查确认桥接方法按 `owner_panel + schedule.id` 查重。
- 该风险是否阻塞本轮。

### 4.9 语法检查

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/popups/month_day_panel.py src/ui/month_window.py src/ui/main_window.py src/ui/schedule_detail_pop.py main.py
```

### 4.10 禁止范围检查

```powershell
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

预期以上均无输出。

### 4.11 总范围检查

```powershell
git diff --check
git diff --name-only
git status --short --branch
```

预期最终只允许：

```text
src/ui/popups/month_day_panel.py
src/ui/month_window.py
src/ui/main_window.py
manage_instruction/Work_Log.md
manage_instruction/Work_Task_Prompts.md
```

如果 `src/ui/schedule_detail_pop.py` 出现 diff，必须在日志说明为什么无法避免，并确认只做最小兼容修改。

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：`MP-2（月日程弹窗日程项双击打开共享详情弹窗）`
- 开工前 git 状态
- 实际修改文件
- 是否存在开工前 diff
- `MonthDayPanel` 新增信号/双击入口说明
- `MonthDayPanel` 子详情弹窗生命周期管理说明
- 同 `owner_panel + schedule.id` 的重复详情弹窗复用策略
- `MonthWindow` 转发信号说明
- `MainWindow` 详情打开桥接说明
- 是否未复用 `DashboardView._show_detail_popup(...)`
- 是否未修改 `src/ui/dashboard.py`
- 是否未改 `_resolve_detail_edit_target(...)`
- 是否未改 `MonthWindow.hideEvent(...) / closeEvent(...) / close_day_panels(...)`
- 是否未改 Dashboard / Week / Todo 详情链路
- 验证命令和结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

## 6. Work_Task_Prompts.md 处理要求

如需要维护复核锚点，可将当前状态更新为：

```text
MP-2 已执行，等待决策/顾问窗口复核。
下一步候选：MP-3。
```

不得在本轮自行写入 `MP-3` 的执行提示词。

## 7. 完成后要求

完成后不要提交 Git，等待决策/顾问窗口复核。
