# Work Task Prompts

用途：保存主窗口审核后的最终执行提示词。执行窗口只应执行本文件中的最终版本。

---

# 当前待执行提示词：功能补充 W-1

## 功能补充 W-1：周界面日期双击跳转日视图

请执行功能补充 W-1：周界面日期双击跳转日视图。本轮只增加周界面日期块双击跳转，不改变单击选中日期和添加日程行为。

## 1. 本轮目标

当前周界面中，点击一周日期块会选中该日期，后续添加日程会添加到该日期。本轮在保留单击行为不变的基础上，新增：

- 双击周界面某个日期块时，跳转到对应日期的日视图。
- 日视图日期应切换为双击的日期。
- 主窗口顶部日期文案应同步更新。
- 日视图数据应刷新。

要求：

- 单击日期仍只在周界面选中日期，不跳转日视图。
- 双击日期跳转日视图。
- 不改变添加日程使用 `current_selected_date` 的行为。
- 不修改数据库。
- 不修改 picker、详情弹窗、刷新协调层、主题/QSS。
- 不提交 Git，等待复核。

## 2. 允许修改

允许修改：

- `src/ui/common/week_day_block.py`
- `src/ui/week_window.py`
- `src/ui/main_window.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

禁止修改：

- `src/ui/month_window.py`
- `src/ui/dashboard.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- `src/ui/todo_board.py`
- `src/ui/common/toast.py`
- `src/ui/utils/icon_loader.py`
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

禁止事项：

- 不改变 `DayBlock.clicked` 单击语义。
- 不删除或重写 `WeekWindow._on_day_clicked(...)`。
- 不改变 `WeekWindow.switch_to_add_page(...)` 中使用当前选中日期的逻辑。
- 不改变 `MainWindow.switch_view(...)` 路由行为。
- 不新增 EventBus 信号。
- 不写数据库。
- 不提交 Git。

若开工前已有 diff，需要在 `Work_Log.md` 中单独记录，不视为本轮问题。

## 3. 具体任务

1. 读取当前基线：

```powershell
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
Get-Content -Path src\ui\common\week_day_block.py -Encoding UTF8
Get-Content -Path src\ui\week_window.py -Encoding UTF8
Get-Content -Path src\ui\main_window.py -Encoding UTF8
```

2. 在 `src/ui/common/week_day_block.py` 中为 `DayBlock` 增加双击信号。

建议：

- 新增 `double_clicked = pyqtSignal(QDate)`。
- 新增 `mouseDoubleClickEvent(self, event)`。
- 左键双击时 emit 当前 `self.date` 并 `event.accept()`。
- 右键或非左键双击时调用 `super().mouseDoubleClickEvent(event)`。
- 不改变现有 `clicked = pyqtSignal(QDate)`。
- 不改变现有 `mouseReleaseEvent(...)` 单击发射逻辑。
- 不改变样式、tooltip、农历逻辑。

3. 在 `src/ui/week_window.py` 中增加周窗口对外双击信号。

建议：

- 在 `WeekWindow` 类上新增 `day_double_clicked = pyqtSignal(QDate)`。
- 创建 `DayBlock` 时保留：

```python
block.clicked.connect(self._on_day_clicked)
```

- 同时新增：

```python
block.double_clicked.connect(self._on_day_double_clicked)
```

- 新增 `_on_day_double_clicked(self, qdate)` 方法。
- 方法中应先复用/保持选中行为：

```python
self._on_day_clicked(qdate)
```

然后：

```python
self.day_double_clicked.emit(qdate)
```

- 不改变 `_on_day_clicked(...)` 的现有逻辑。
- 不改变 `switch_to_add_page(...)`、picker、刷新、拖拽、写库逻辑。

4. 在 `src/ui/main_window.py` 中接入周窗口双击跳转。

当前已有 `jump_to_date_from_month(self, qdate)`，用于从月视图跳转到日视图。建议做最小泛化：

- 新增通用方法：

```python
jump_to_date(self, qdate)
```

逻辑应复用现有日历选日入口，避免复制顶部日期文案更新逻辑：

- `py_date = qdate.toPyDate()`
- `self.on_calendar_date_picked(py_date)`
- `self.switch_view("day")`

建议实现：

```python
def jump_to_date(self, qdate):
    py_date = qdate.toPyDate()
    self.on_calendar_date_picked(py_date)
    self.switch_view("day")
```

- 保留 `jump_to_date_from_month(self, qdate)` 方法名，改为调用：

```python
self.jump_to_date(qdate)
```

这样不破坏月视图已有调用。

- 在 `MainWindow.__init__` 中连接：

```python
self.week_window.day_double_clicked.connect(self.jump_to_date)
```

- 不改变 `switch_view(...)`。
- 不改变月视图现有连接。
- 不改变添加页、picker、详情弹窗、刷新协调逻辑。

5. 更新 `manage_instruction/Work_Log.md`。

至少记录：

- 本轮任务名称：功能补充 W-1（周界面日期双击跳转日视图）
- 开工前 git 状态
- 实际修改文件
- `DayBlock` 新增信号和事件说明
- `WeekWindow` 新增信号和转发说明
- `MainWindow` 日期跳转方法泛化说明
- 单击行为是否保持不变
- 添加日程日期来源是否保持不变
- 验证结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

## 4. 验收命令

定位新增链路：

```powershell
rg -n "double_clicked|day_double_clicked|mouseDoubleClickEvent|jump_to_date|jump_to_date_from_month|_on_day_double_clicked|_on_day_clicked" src/ui/common/week_day_block.py src/ui/week_window.py src/ui/main_window.py
```

DayBlock import 验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.common.week_day_block import DayBlock; print('day block import ok', DayBlock)"
```

WeekWindow import 验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.week_window import WeekWindow, DayBlock; print('week import ok', WeekWindow, DayBlock)"
```

MainWindow import 验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.main_window import MainWindow; print('main window import ok', MainWindow)"
```

DayBlock offscreen 信号验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate, Qt, QEvent, QPointF; from PyQt6.QtGui import QMouseEvent; from src.ui.common.week_day_block import DayBlock; app=QApplication([]); b=DayBlock(); q=QDate.currentDate().addDays(1); b.set_data(q, '初一'); hits=[]; b.clicked.connect(lambda d: hits.append(('click', d))); b.double_clicked.connect(lambda d: hits.append(('double', d))); ev=QMouseEvent(QEvent.Type.MouseButtonDblClick, QPointF(1,1), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier); b.mouseDoubleClickEvent(ev); print('hits', hits); assert hits == [('double', q)]"
```

WeekWindow offscreen 连接验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.week_window import WeekWindow; app=QApplication([]); w=WeekWindow(); hits=[]; w.day_double_clicked.connect(lambda d: hits.append(d)); q=QDate.currentDate().addDays(2); w._on_day_double_clicked(q); print('selected', w.current_selected_date.toString('yyyy-MM-dd')); print('hits', [d.toString('yyyy-MM-dd') for d in hits]); assert w.current_selected_date == q; assert hits == [q]"
```

MainWindow offscreen 方法验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); q=QDate.currentDate().addDays(3); w.jump_to_date(q); print('dashboard date', w.page_dashboard.current_date); assert w.page_dashboard.current_date == q.toPyDate(); assert hasattr(w, 'jump_to_date_from_month')"
```

语法检查：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/common/week_day_block.py src/ui/week_window.py src/ui/main_window.py main.py
```

禁止范围检查：

```powershell
git diff --name-only -- src/ui/month_window.py
git diff --name-only -- src/ui/dashboard.py
git diff --name-only -- src/ui/add_view.py
git diff --name-only -- src/ui/add_view_week.py
git diff --name-only -- src/ui/todo_board.py
git diff --name-only -- src/ui/common/toast.py
git diff --name-only -- src/ui/utils/icon_loader.py
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

允许范围检查：

```powershell
git diff --name-only -- src/ui
```

预期 `src/ui` diff 仅允许：

```text
src/ui/common/week_day_block.py
src/ui/week_window.py
src/ui/main_window.py
```

总范围检查：

```powershell
git diff --name-only
git status --short --branch
```

预期最终只允许：

- `src/ui/common/week_day_block.py`
- `src/ui/week_window.py`
- `src/ui/main_window.py`
- `manage_instruction/Work_Log.md`
- 必要时 `manage_instruction/Work_Task_Prompts.md`

完成后不要提交 Git，等待决策/顾问窗口复核。
