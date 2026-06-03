# 当前待执行提示词：M-5d

## M-5d：月界面时间选择接入

请执行 `M-5d：月界面时间选择接入`。本轮只接入月界面添加表单的时间选择流程，不接提醒，不接清单，不处理紧急性 / 重复规则保存，不接右键菜单，不进入 `M-5e / M-5f / M-5g`。

## 1. 本轮目标

基于 `M-5b` 审查结论和 `M-5c` 已完成的 `InlineAddViewMonth` 表单壳，本轮为月界面添加表单接入现有 `TimePickerView`。

目标：

- 点击月界面添加表单的时间按钮时，打开月界面内部时间选择页。
- 时间选择页默认日期应使用当前月添加目标日期。
- 时间确认后回填到 `InlineAddViewMonth.set_time_data(start, end)`。
- 返回 / 取消时间选择时回到月添加表单。
- `InlineAddViewMonth._on_save(...)` 可以开始使用用户选择的 `selected_start_time / selected_end_time` 作为 `start_time / end_time`。
- 对齐主界面 / 周界面 schedule 语义：日程未选择时间时不得保存，应提示用户先设置计划时间。
- 不接提醒 picker。
- 不接清单 picker。
- 不改变主界面 / 周界面添加页行为。

本轮必须保持：

- `db_manager.add_schedule(...)` 对外调用方式不变。
- 月界面仍只保存 `schedule`，不新增 todo 支持。
- 不新增数据库字段。
- 不写入提醒字段。
- 不写入清单字段。
- 不改变重复规则真实写入语义。
- 不让紧急性 / 重复控件影响保存。

## 2. 允许 / 禁止

### 允许修改

- `src/ui/month_window.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

### 禁止修改

- `src/ui/main_window.py`
- `src/ui/week_window.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- `src/ui/time_picker.py`
- `src/ui/time_picker_week.py`
- `src/ui/alarm_picker.py`
- `src/ui/list_picker.py`
- `src/ui/calendar_pop.py`
- `src/ui/common/`
- `src/ui/popups/`
- `src/ui/utils/`
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
- `.env`
- `.gitignore`
- `manage_instruction/Final_Formulation.md`
- `manage_instruction/Work_Formulation.md`
- `manage_instruction/Work_Instruction.md`
- `manage_instruction/ReconstructionDolder/`

### 禁止事项

- 不修改 `TimePickerView` 本身。
- 不修改主窗口 / 周窗口的 picker 链路。
- 不接提醒 picker。
- 不接清单 picker。
- 不让紧急性 / 重复控件影响保存。
- 不新增 `parent_id` 或数据库字段。
- 不新增 English repeat rule 行为。
- 不接月界面右键菜单。
- 不提交 Git。

若开工前已有 diff，必须在 `Work_Log.md` 中单独记录，不视为本轮问题。

## 3. 具体任务

### 3.1 读取当前基线

读取并确认：

```powershell
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
Get-Content -Path src\ui\month_window.py -Encoding UTF8
Get-Content -Path src\ui\time_picker.py -Encoding UTF8
Get-Content -Path src\ui\add_view.py -Encoding UTF8
Get-Content -Path src\ui\week_window.py -Encoding UTF8
```

重点确认：

- `InlineAddViewMonth.req_open_time_picker` 已存在。
- `InlineAddViewMonth.set_time_data(start_time, end_time)` 已存在。
- `InlineAddViewMonth.btn_time` 已存在。
- 当前 `btn_time` 仍是 M-5c 的 toast 占位。
- `TimePickerView` 的接口是：
  - `set_initial_data(start_dt, end_dt)`
  - `confirm_requested(start, end)`
  - `back_requested`
- `TimePickerView` 当前通过 `set_initial_data(None, end_dt)` 设置默认日期和结束时间。
- `TimePickerView` 自带 `btn_close`，当前会调用 `self.window().close()`；嵌入 `MonthWindow` 时必须在实例层处理，避免关闭整个月界面。

### 3.2 在 `MonthWindow` 中接入月内 `TimePickerView`

在 `src/ui/month_window.py` 中做最小接入。

建议实现方向：

- 从现有 `src.ui.time_picker` 导入 `TimePickerView`。
- 在 `MonthWindow` 内创建月界面专用时间选择页，例如：

```python
self.page_time = TimePickerView(self)
```

- 不使用 `MainWindow.page_time`。
- 不修改 `MainWindow`。
- 不修改 `WeekWindow`。
- 将 `TimePickerView` 放入月界面左侧添加区域所在布局。
- 若当前月界面左侧没有 `QStackedWidget`，可采用最小 hide/show 页面切换：
  - `inline_add_view.hide()`
  - `page_time.show()`
  - 返回时 `page_time.hide()`，`inline_add_view.show()`
- 不重构整个 `MonthWindow` 布局。
- 不改变月历右侧区域。

如果现有布局不适合直接放入完整 `TimePickerView`，必须保持最小改动，并在日志中说明采用的承接方式。

### 3.3 处理 `TimePickerView` 内嵌窗口控制按钮

由于 `TimePickerView` 原本是按页面 / 窗口环境设计的，内部存在悬浮关闭与挂起按钮。本轮在月界面内嵌时必须处理：

- `page_time.btn_close` 不得关闭 `MonthWindow`。
- 推荐做法：
  - 将 `btn_close` 的点击行为改接到 `back_from_time_picker()`。
  - 或直接隐藏 `btn_close`。
- `page_time.btn_suspend` 不得触发月界面挂起或新链路。
- 推荐做法：
  - 隐藏 `btn_suspend`。
  - 或保持未连接但必须确认无副作用。

要求：

- 不修改 `src/ui/time_picker.py`。
- 只在 `MonthWindow` 创建的 `self.page_time` 实例上处理。
- 日志必须记录采用的处理方式。

### 3.4 连接时间请求信号

连接：

```python
self.inline_add_view.req_open_time_picker.connect(self.go_to_time_picker)
```

新增月窗口内部方法，例如：

```python
def go_to_time_picker(self, start, end):
    ...
```

要求：

- 本方法只服务月界面添加流程。
- 不处理编辑已有日程。
- 不接详情弹窗。
- 不接主窗口路由。
- 不接周窗口路由。

打开时间选择前：

- 隐藏 hover 预览。
- 关闭或隐藏已打开的月界面持久日期面板，避免上下文混乱。
- 保留月添加表单当前标题、详情、时间 / 提醒 / 清单状态字段。

### 3.5 时间选择默认日期

打开时间选择器时，默认日期应优先使用月添加目标日期。

目标日期来源：

- 优先使用 `InlineAddViewMonth.selected_date`。
- 若为空，使用 `MonthWindow._get_add_target_date()`。
- 若仍无法取得，使用 `QDate.currentDate()`。

若 `start` 和 `end` 都为空：

- 构造默认 `end` datetime：
  - 日期为目标日期。
  - 时间使用当前真实小时 / 分钟。
- 必须避免让时间选择器默认跳到错误日期。

注意当前 `month_window.py` 已使用 `import datetime`，示例中应写成 `datetime.datetime.now()` 或局部 `from datetime import datetime`，不得写出会运行失败的 `datetime.now()`。

建议逻辑：

```python
target_qdate = self.inline_add_view.selected_date or self._get_add_target_date()
if target_qdate is None or not target_qdate.isValid():
    target_qdate = QDate.currentDate()

target_pydate = target_qdate.toPyDate()
now = datetime.datetime.now()
default_end = datetime.datetime(
    target_pydate.year,
    target_pydate.month,
    target_pydate.day,
    now.hour,
    now.minute,
)
self.page_time.set_initial_data(start, end or default_end)
```

如果实际代码需要调整，请保持等价语义。

### 3.6 时间确认回填

连接：

```python
self.page_time.confirm_requested.connect(self.on_time_confirmed)
self.page_time.back_requested.connect(self.back_from_time_picker)
```

新增方法，例如：

```python
def on_time_confirmed(self, start, end):
    self.inline_add_view.set_time_data(start, end)
    self.back_from_time_picker()
```

要求：

- 只回填到 `InlineAddViewMonth`。
- 不直接写数据库。
- 不触发保存。
- 不刷新日程列表。
- 不修改提醒 / 清单状态。

### 3.7 时间按钮从占位改为请求信号

修改 `InlineAddViewMonth` 中 `btn_time` 的点击行为：

- 从 M-5c 的 toast 占位，改为 emit：

```python
self.req_open_time_picker.emit(self.selected_start_time, self.selected_end_time)
```

要求：

- `btn_alarm` 和 `btn_list` 仍保持 M-5c 占位行为，不打开 picker。
- 不让时间按钮直接调用 `TimePickerView`。
- 不让 `InlineAddViewMonth` 直接依赖 `TimePickerView`。

### 3.8 保存字段最小调整

允许在 `InlineAddViewMonth._on_save(...)` 中只做时间字段的最小接入。

保存策略本轮明确为：

- 月界面仍只保存 `schedule`。
- schedule 必须设置时间。
- 若 `selected_start_time` 和 `selected_end_time` 都为空：
  - 不保存。
  - 通过 `window().show_toast(...)` 或等价轻量提示告知“请先设置计划时间”。
- 若用户已选择时间：
  - `start_time` 使用 `selected_start_time`。
  - `end_time` 使用 `selected_end_time`。
  - 允许 `selected_start_time` 为 `None`，此时 `start_time` 为 `None`，`end_time` 为用户选择的结束时间；该语义与主界面 / 周界面当前添加页一致。

禁止在 `_on_save(...)` 中新增：

- `reminder_time`
- `is_alarm`
- `alarm_duration`
- `category_id` 的新来源
- 紧急性控件保存
- 重复控件保存

本轮保存结构除 `start_time / end_time` 可使用已选时间外，其余字段必须保持 M-5c 语义。

### 3.9 更新 `Work_Log.md`

至少记录：

- 本轮任务名称：`M-5d（月界面时间选择接入）`
- 开工前 git 状态
- 实际修改文件
- `TimePickerView` 接入方式
- `TimePickerView` 内嵌后 `btn_close / btn_suspend` 处理方式
- `req_open_time_picker` 连接方式
- 默认日期来源策略
- `confirm_requested` 回填结果
- `back_requested` 返回结果
- `btn_time` 是否改为 emit 请求信号
- `btn_alarm / btn_list` 是否仍未接入
- `_on_save(...)` 是否只接入时间字段
- 未选择时间时采用的保存策略
- 验证命令和结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

## 4. 验收命令

### 4.1 定位新增链路

```powershell
rg -n "TimePickerView|page_time|go_to_time_picker|back_from_time_picker|on_time_confirmed|req_open_time_picker|set_time_data|btn_time|btn_alarm|btn_list|selected_start_time|selected_end_time|_on_save|btn_close|btn_suspend" src/ui/month_window.py
```

预期：

- `TimePickerView` 只在 `month_window.py` 中被月界面局部使用。
- `btn_time` 会 emit `req_open_time_picker`。
- `btn_alarm / btn_list` 不打开真实 picker。
- 新增 `go_to_time_picker / back_from_time_picker / on_time_confirmed` 或等价方法。
- `page_time.btn_close` 不会关闭整个月界面。

### 4.2 import 验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.month_window import MonthWindow, InlineAddViewMonth; from src.ui.time_picker import TimePickerView; print('month time imports ok', MonthWindow, InlineAddViewMonth, TimePickerView)"
```

### 4.3 offscreen 构造验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); print('month created', w is not None); print('has inline', hasattr(w, 'inline_add_view')); print('has page_time', hasattr(w, 'page_time')); assert hasattr(w, 'inline_add_view'); assert hasattr(w, 'page_time')"
```

### 4.4 时间请求连接验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); target=QDate.currentDate().addDays(1); w.inline_add_view.reset(target); w.inline_add_view.req_open_time_picker.emit(None, None); print('opened time picker ok'); assert hasattr(w, 'page_time'); assert w.page_time.isVisible()"
```

### 4.5 时间确认回填验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from datetime import datetime; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); target=QDate.currentDate().addDays(1); w.inline_add_view.reset(target); start=datetime(target.year(), target.month(), target.day(), 9, 0); end=datetime(target.year(), target.month(), target.day(), 10, 0); w.on_time_confirmed(start, end); print('time state', w.inline_add_view.selected_start_time, w.inline_add_view.selected_end_time); assert w.inline_add_view.selected_start_time == start; assert w.inline_add_view.selected_end_time == end"
```

### 4.6 返回时间页验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); target=QDate.currentDate().addDays(1); w.inline_add_view.reset(target); w.inline_add_view.show(); w.go_to_time_picker(None, None); print('time visible', w.page_time.isVisible()); w.back_from_time_picker(); print('inline visible', w.inline_add_view.isVisible()); assert not w.page_time.isVisible(); assert w.inline_add_view.isVisible()"
```

### 4.7 非目标 picker 未接入检查

```powershell
rg -n "go_to_alarm_picker|go_to_list_picker|page_alarm|page_list|AlarmPicker|ListPicker|req_open_alarm_picker.connect|req_open_list_picker.connect" src/ui/month_window.py
```

预期：

- 无真实 alarm/list picker 接入。
- 如只命中 M-5c 的信号声明或按钮占位，需在日志说明无真实接入。

### 4.8 保存字段隔离检查

检查 `_on_save(...)`：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import inspect; from src.ui.month_window import InlineAddViewMonth; src=inspect.getsource(InlineAddViewMonth._on_save); assert 'reminder_time' not in src; assert 'is_alarm' not in src; assert 'alarm_duration' not in src; assert 'selected_list_id' not in src; assert 'combo_priority' not in src; assert 'combo_repeat' not in src; assert 'selected_start_time' in src; assert 'selected_end_time' in src; print('_on_save time-only isolation ok')"
```

允许 `_on_save(...)` 中出现：

- `selected_start_time`
- `selected_end_time`

但仅用于 `start_time / end_time` 和未设置时间判断。

不得出现提醒、清单、重复、紧急性的新保存字段。

### 4.9 未选择时间保存拦截验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import InlineAddViewMonth; app=QApplication([]); v=InlineAddViewMonth(); calls=[]; v.saved.connect(lambda: calls.append('saved')); v.reset(QDate.currentDate().addDays(1)); v.input_title.setText('未设时间测试'); v._on_save(); print('saved calls', calls); assert calls == []"
```

### 4.10 语法检查

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/month_window.py src/ui/time_picker.py main.py
```

### 4.11 禁止范围检查

```powershell
git diff --name-only -- src/ui/main_window.py
git diff --name-only -- src/ui/week_window.py
git diff --name-only -- src/ui/add_view.py
git diff --name-only -- src/ui/add_view_week.py
git diff --name-only -- src/ui/time_picker.py
git diff --name-only -- src/ui/time_picker_week.py
git diff --name-only -- src/ui/alarm_picker.py
git diff --name-only -- src/ui/list_picker.py
git diff --name-only -- src/ui/calendar_pop.py
git diff --name-only -- src/ui/common
git diff --name-only -- src/ui/popups
git diff --name-only -- src/ui/utils
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

### 4.12 总范围检查

```powershell
git diff --check
git diff --name-only
git status --short --branch
```

预期最终只允许：

```text
src/ui/month_window.py
manage_instruction/Work_Log.md
manage_instruction/Work_Task_Prompts.md
```

其中 `Work_Task_Prompts.md` 仅在维护本轮复核锚点时允许修改。

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：`M-5d（月界面时间选择接入）`
- 开工前 git 状态
- 实际修改文件
- 是否存在开工前既有 diff
- `TimePickerView` 接入方式
- `TimePickerView` 内嵌后 `btn_close / btn_suspend` 处理方式
- 时间选择页如何显示 / 返回
- 默认日期来源策略
- `btn_time` 是否从 toast 占位改为 `req_open_time_picker.emit(...)`
- `btn_alarm / btn_list` 是否仍未接入
- `set_time_data(...)` 回填验证结果
- `_on_save(...)` 时间字段接入策略
- 未选择时间时的保存策略
- import / offscreen / py_compile 验证结果
- 禁止范围检查结果
- 未完成事项
- 风险或疑点

特别记录：

- 本轮只接时间 picker。
- 本轮不接提醒 picker。
- 本轮不接清单 picker。
- 本轮不修改 `TimePickerView` 源文件。
- 本轮不修改主界面 / 周界面添加链路。
- 后续 `M-5e` 再接提醒 / 清单 picker。
- 后续 `M-5f` 再处理紧急性 / 重复规则 / 保存结构对齐。

## 6. Work_Task_Prompts.md 处理要求

如需要维护复核锚点，可将当前状态更新为：

```text
M-5d 已执行，等待决策/顾问窗口复核。
下一步候选：M-5e。
```

不得在本轮自行写入 `M-5e` 的执行提示词。

## 7. 完成后要求

完成后不要提交 Git，等待决策/顾问窗口复核。
