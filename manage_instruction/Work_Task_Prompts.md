# Work Task Prompts

# 当前待执行提示词：MP-1

## MP-1：月日程弹窗青色渐变 UI 与列表承载

请执行 `MP-1（月日程弹窗青色渐变 UI 与列表承载）`。本轮只改造月日程弹窗自身 UI 和只读日程列表承载，不接 `ScheduleDetailPop`，不改跨视图编辑路由，不改 popup 生命周期规则。

## 1. 本轮目标

基于 `MP-0` 审查结论，对当前 `MonthDayPanel` 做低风险 UI 与列表展示增强。

当前事实：

- `src/ui/popups/month_day_panel.py::MonthDayPanel` 已存在。
- 当前 panel 是独立 `QWidget(Qt.Tool | FramelessWindowHint)`。
- 当前 panel 已接收 `qdate, schedules`。
- 当前 panel 已有：
  - `closed = pyqtSignal(object)`
  - `set_panel_data(qdate, schedules)`
  - `closeEvent(...)`
  - 左键拖动逻辑
- 当前 panel 已能展示简版文本列表，但 UI 仍偏占位。
- `MP-0` 已确认：`MonthWindow.hideEvent(...)` 当前会调用 `close_day_panels()`；因此“普通视图切换时 panel 保留”不属于 MP-1 范围，留到 MP-3 生命周期工单处理。

本轮目标：

- 将 `MonthDayPanel` 改造成青色渐变风格的月日程弹窗。
- 保留外侧独立浮窗形态。
- 保留关闭按钮。
- 保留拖动能力。
- 保留 `closed` 信号。
- 保留 `set_panel_data(qdate, schedules)` 对外入口。
- 将日程列表从单个文本 label 升级为可承载多条日程项的只读列表 UI。
- 每条日程项显示基础信息：
  - 时间
  - 标题
  - 重要性（priority）
  - 完成状态
- 无日程时显示稳定空状态。
- 超过可展示数量时保留“共 N 条”或等价提示。
- 不接双击详情。
- 不打开 `ScheduleDetailPop`。
- 不改编辑路由。
- 不改数据库。

## 2. 允许 / 禁止

允许修改：

- `src/ui/popups/month_day_panel.py`
- `src/ui/month_window.py`（仅在现有传入数据或 panel 刷新调用必须适配时允许最小修改；如果无需修改则不改）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

禁止修改：

- `src/ui/schedule_detail_pop.py`
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

- 不接 `ScheduleDetailPop`。
- 不新增详情弹窗打开信号。
- 不新增日程项双击行为。
- 不改 `MainWindow`。
- 不改编辑路由。
- 不改跨视图刷新链路。
- 不写数据库。
- 不改月界面添加表单。
- 不改月界面右键菜单。
- 不改 `close_day_panels(...)` 语义。
- 不改 `hideEvent(...) / closeEvent(...)` 清理策略。
- 不提交 Git。

若开工前已有 diff，必须在 `Work_Log.md` 中记录，并区分是否属于本轮产生。

## 3. 具体任务

### 3.1 开工前状态检查

先运行：

```powershell
git status --short --branch
git diff --name-only
```

要求：

- 记录开工前 git 状态。
- 若已有 diff，记录具体文件，并说明这些 diff 不视为本轮源码问题。
- 本轮不得清理、回退或改动开工前已有无关 diff。

### 3.2 读取当前基线

读取：

```powershell
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
Get-Content -Path src\ui\popups\month_day_panel.py -Encoding UTF8
Get-Content -Path src\ui\month_window.py -Encoding UTF8
```

确认：

- 本轮只执行 MP-1。
- 不执行 MP-2 ~ MP-5。
- `MP-0` 已记录当前 panel 生命周期和路由边界。
- `MonthDayPanel` 当前已接收 `qdate, schedules`。
- 本轮不触碰 `ScheduleDetailPop`。
- 本轮不解决“普通视图切换时 panel 保留”的生命周期问题，该问题留到 MP-3。

### 3.3 改造 MonthDayPanel UI

在 `src/ui/popups/month_day_panel.py` 中做 UI 改造。

要求：

- 保持 `class MonthDayPanel(QWidget)`。
- 保持 `Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint`。
- 保持 `WA_ShowWithoutActivating`。
- 保持 `WA_TranslucentBackground`。
- `paintEvent(...)` 改为青色渐变圆角背景。
- 可参考项目现有青色视觉：
  - `#0cc0df`
  - `#71dce8`
  - 白色文字
  - 半透明白色边框
- 不引入外部依赖。
- 不新增图片资源。
- 不读取/写入 QSS 文件。

建议 UI 结构：

- 顶部 header：
  - 日期文本，例如 `2026-06-24 周三`
  - 关闭按钮
- 中部列表区域：
  - 多条只读日程项
  - 每条 item 可以是 `QFrame` / `QWidget` / `QLabel` 组合
- 底部可选摘要：
  - `共 N 条`
  - 或超过展示数量时显示 `... 共 N 条`

显示要求：

- 标题和日期不能溢出 panel。
- 日程标题较长时，优先在 item 内换行或省略，不得把 panel 撑出异常宽度。
- 不新增横向滚动条。

### 3.4 日程项展示规则

`set_panel_data(qdate, schedules)` 仍是唯一数据入口。

每条日程项至少展示：

- 时间：
  - 优先 `start_time.strftime("%H:%M")`
  - 否则 `end_time.strftime("%H:%M")`
  - 都没有则 `--:--`
- 标题：
  - `schedule.title`
  - 空标题显示 `未命名日程`
- 重要性（priority）：
  - `priority == 2`：高
  - `priority == 1`：中
  - 其他：低
- 状态：
  - `status == 1`：已完成
  - 其他：未完成

显示顺序应保持传入 `schedules` 的顺序，不在本轮重新排序。

不要在 panel 内重新查数据库。

### 3.5 空状态与数量限制

要求：

- 无日程时显示空状态，例如 `当日暂无日程`。
- 多日程时最多显示一个合理数量，例如前 8 条。
- 超过数量时显示 `... 共 N 条` 或等价文案。
- 不改变 `MonthWindow` 的筛选和排序规则。

### 3.6 保持生命周期不变

必须保持：

- `closed = pyqtSignal(object)`
- `closeEvent(...)` 中只 emit 一次 `closed`
- `btn_close.clicked.connect(self.close)`
- 左键拖动逻辑
- `panel_date` 更新逻辑
- `set_panel_data(qdate, schedules)` 可重复调用刷新内容

不得改：

- `MonthWindow.close_day_panels(...)`
- `MonthWindow._remove_day_panel(...)`
- `MonthWindow._find_open_day_panel(...)`
- `MonthWindow.hideEvent(...)`
- `MonthWindow.closeEvent(...)`

说明：

- MP-0 已确认当前 `hideEvent(...)` 会关闭 day panel。
- 本轮不把“普通视图切换时 panel 保留”作为验收项。
- 跨视图保留与双击跳日关闭规则的冲突，留到 MP-3 单独处理。

### 3.7 更新 Work_Log.md

在 `manage_instruction/Work_Log.md` 追加记录，至少包含：

- 本轮任务名称：`MP-1（月日程弹窗青色渐变 UI 与列表承载）`
- 开工前 git 状态
- 实际修改文件
- 是否存在开工前 diff
- `MonthDayPanel` UI 改造说明
- 日程项展示字段说明
- 空状态说明
- 是否保持 `closed` 信号
- 是否保持拖动能力
- 是否保持 `set_panel_data(...)` 对外入口
- 是否未接 `ScheduleDetailPop`
- 是否未改编辑路由
- 是否未改 popup 生命周期规则
- 验证命令与结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

## 4. 验收命令

### 4.1 静态定位

```powershell
rg -n "class MonthDayPanel|closed|set_panel_data|paintEvent|closeEvent|mousePressEvent|mouseMoveEvent|mouseReleaseEvent|btn_close|panel_date" src/ui/popups/month_day_panel.py
rg -n "ScheduleDetailPop|db_manager|MainWindow|mouseDoubleClickEvent|doubleClicked|detail_requested" src/ui/popups/month_day_panel.py
rg -n "close_day_panels|_remove_day_panel|_find_open_day_panel|hideEvent|closeEvent|_open_day_panel" src/ui/month_window.py
```

预期：

- `MonthDayPanel` 仍有 `closed` 信号。
- `set_panel_data(...)` 仍存在。
- 拖动事件方法仍存在。
- `ScheduleDetailPop` 不应出现在 `month_day_panel.py`。
- `db_manager` 不应出现在 `month_day_panel.py`。
- `MainWindow` 不应出现在 `month_day_panel.py`。
- `MonthWindow` 生命周期方法可以被定位，但本轮不应改语义。

### 4.2 import 验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.popups.month_day_panel import MonthDayPanel; from src.ui.month_window import MonthWindow; print('mp1 imports ok', MonthDayPanel, MonthWindow)"
```

### 4.3 offscreen 构造与空状态验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.popups.month_day_panel import MonthDayPanel; app=QApplication([]); p=MonthDayPanel(QDate.currentDate(), []); print('panel created', p is not None); print('date', p.panel_date.toString('yyyy-MM-dd')); assert p.panel_date == QDate.currentDate(); assert hasattr(p, 'closed'); assert hasattr(p, 'set_panel_data'); p.set_panel_data(QDate.currentDate().addDays(1), []); assert p.panel_date == QDate.currentDate().addDays(1); print('empty state ok')"
```

### 4.4 offscreen 日程列表展示验证

使用轻量假对象，不读数据库：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from datetime import datetime; from types import SimpleNamespace; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.popups.month_day_panel import MonthDayPanel; app=QApplication([]); q=QDate.currentDate(); schedules=[SimpleNamespace(title='高重要日程', start_time=datetime(2026,6,24,9,0), end_time=datetime(2026,6,24,10,0), priority=2, status=0), SimpleNamespace(title='已完成日程', start_time=None, end_time=datetime(2026,6,24,15,30), priority=1, status=1)]; p=MonthDayPanel(q, schedules); p.set_panel_data(q, schedules); print('panel list smoke ok'); assert p.panel_date == q"
```

### 4.5 生命周期 smoke

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.popups.month_day_panel import MonthDayPanel; app=QApplication([]); p=MonthDayPanel(QDate.currentDate(), []); hits=[]; p.closed.connect(lambda panel: hits.append(panel)); p.show(); app.processEvents(); p.close(); app.processEvents(); print('closed hits', len(hits)); assert hits == [p]"
```

### 4.6 月界面复用链路 smoke

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); q=QDate.currentDate().addDays(1); w._open_day_panel(q); count1=len(w.open_day_panels); w._open_day_panel(q); count2=len(w.open_day_panels); print('panel counts', count1, count2); assert count1 == 1; assert count2 == 1; w.close_day_panels(); assert w.open_day_panels == []"
```

### 4.7 禁止范围检查

```powershell
git diff --name-only -- src/ui/schedule_detail_pop.py
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

预期以上均无输出。

### 4.8 语法检查

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/popups/month_day_panel.py src/ui/month_window.py main.py
```

### 4.9 总范围检查

```powershell
git diff --check
git diff --name-only
git status --short --branch
```

预期最终只允许：

```text
src/ui/popups/month_day_panel.py
src/ui/month_window.py
manage_instruction/Work_Log.md
manage_instruction/Work_Task_Prompts.md
```

其中 `src/ui/month_window.py` 只有在必须适配 panel 数据传入/刷新时才允许出现；如未修改更好。

## 5. Work_Task_Prompts.md 处理要求

如需要维护复核锚点，可将当前状态更新为：

```text
MP-1 已执行，等待决策/顾问窗口复核。
下一步候选：MP-2。
```

不得在本轮自行写入 `MP-2` 的执行提示词。

## 6. 完成后要求

完成后不要提交 Git，等待决策/顾问窗口复核。
