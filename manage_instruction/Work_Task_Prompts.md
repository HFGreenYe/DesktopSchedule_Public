# 当前复核锚点：M-5e 已执行

当前状态：

- M-5e 已执行，等待决策/顾问窗口复核。
- 下一步候选：M-5f。
- 下方保留 M-5e 已执行提示词全文，供日志对照复核。

## M-5e：月界面提醒与清单选择接入

请执行 `M-5e：月界面提醒与清单选择接入`。本轮只接入月界面添加表单的提醒 picker 和清单 picker，不处理紧急性 / 重复规则保存，不接右键菜单，不进入 `M-5f / M-5g`。

## 1. 本轮目标

基于 `M-5b` 审查结论、`M-5c` 表单壳、`M-5d` 时间选择接入，本轮为月界面添加表单接入现有：

- `AlarmPickerView`
- `ListPickerView`

目标：

- 点击月界面添加表单的提醒按钮时，打开月界面内部提醒选择页。
- 提醒 picker 的目标时间应来自已选日程时间：
  - 优先 `selected_start_time`
  - 否则 `selected_end_time`
- 若尚未设置日程时间，提醒按钮不得打开提醒 picker，应提示先设置时间。
- 提醒确认后回填到：
  - `InlineAddViewMonth.set_alarm_data(reminder_time, is_alarm_mode, alarm_duration)`
- 点击月界面添加表单的清单按钮时，打开月界面内部清单选择页。
- 清单 picker 必须使用 `list_type="schedule"`。
- 清单确认后回填到：
  - `InlineAddViewMonth.set_list_data(category_id, category_name)`
- 保存时允许写入现有提醒与清单字段：
  - `reminder_time`
  - `is_alarm`
  - `alarm_duration`
  - `category_id`
- 不修改主界面 / 周界面添加页。
- 不修改 picker 源文件。
- 不新增数据库字段。
- 不新增 todo 支持。

本轮必须保持：

- M-5d 时间选择行为不回退。
- 未设置时间时仍不得保存日程。
- `priority` 仍保持旧值 `0`。
- `repeat_rule` 仍保持旧值 `none`。
- 不让 `combo_priority / combo_repeat` 影响保存。
- 不接右键菜单。

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

- 不修改 `AlarmPickerView` 源文件。
- 不修改 `ListPickerView` 源文件。
- 不修改 `TimePickerView` 源文件。
- 不修改主窗口 / 周窗口 picker 链路。
- 不新增数据库字段。
- 不新增 todo 保存支持。
- 不处理紧急性保存。
- 不处理重复规则保存。
- 不接月界面右键菜单。
- 不在验证中创建或删除真实清单。
- 不为通过测试写入 `schedule.db`。
- 不提交 Git。

说明：

- `ListPickerView` 本身已有新增 / 删除清单 UI，本轮不修改该组件，不额外屏蔽其既有能力。
- 但本轮验证不得通过 UI 或数据库创建、删除真实清单，只允许读取已有清单并回填已有 id 或 `None`。

若开工前已有 diff，必须在 `Work_Log.md` 中单独记录，不视为本轮问题。

## 3. 具体任务

### 3.1 读取当前基线

读取并确认：

```powershell
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
Get-Content -Path src\ui\month_window.py -Encoding UTF8
Get-Content -Path src\ui\alarm_picker.py -Encoding UTF8
Get-Content -Path src\ui\list_picker.py -Encoding UTF8
Get-Content -Path src\data\database.py -Encoding UTF8
```

重点确认：

- `InlineAddViewMonth.req_open_alarm_picker` 已存在。
- `InlineAddViewMonth.req_open_list_picker` 已存在。
- `InlineAddViewMonth.set_alarm_data(...)` 已存在。
- `InlineAddViewMonth.set_list_data(...)` 已存在。
- `AlarmPickerView` 的接口是：
  - `set_initial_data(target_time, is_alarm=False, duration=0)`
  - `confirm_requested(remind_dt, is_alarm, duration)`
  - `back_requested`
- `ListPickerView` 的接口是：
  - `load_data(current_selected_id=None, list_type=None)`
  - `confirm_requested(category_id)`
  - `back_requested`
- `db_manager.get_category(category_id)` 可用于按 id 获取清单名称。

### 3.2 在 `MonthWindow` 中接入月内 `AlarmPickerView / ListPickerView`

在 `src/ui/month_window.py` 中做最小接入。

建议实现方向：

- 从现有 picker 导入：
  - `AlarmPickerView`
  - `ListPickerView`
- 在 `MonthWindow` 内创建月界面专用页面，例如：

```python
self.page_alarm = AlarmPickerView(self)
self.page_list = ListPickerView(self)
```

- 不使用 `MainWindow.page_alarm / page_list`。
- 不修改 `MainWindow`。
- 不修改 `WeekWindow`。
- 不修改 picker 源文件。
- 将两个 picker 放入月界面左侧添加区域所在布局。
- 默认隐藏：

```python
self.page_alarm.hide()
self.page_list.hide()
```

打开 picker 时：

- 隐藏 `inline_add_view`
- 隐藏 `page_time`
- 隐藏另一个非目标 picker
- 只显示当前目标 picker

返回 picker 时：

- 隐藏当前 picker
- 恢复 `inline_add_view`

### 3.3 处理 picker 内嵌窗口控制按钮

`AlarmPickerView` 和 `ListPickerView` 都有独立页面风格的悬浮按钮。本轮内嵌到月界面时必须处理实例按钮，不改 picker 源文件。

对 `self.page_alarm` 和 `self.page_list`：

- `btn_suspend`：
  - 隐藏。
  - 不触发月界面挂起。
- `btn_close`：
  - 不得关闭整个 `MonthWindow`。
  - 断开实例原有 `window().close()` 行为。
  - 重连到对应返回方法：
    - `back_from_alarm_picker()`
    - `back_from_list_picker()`

只允许在 `MonthWindow` 创建的实例上处理。

### 3.4 连接提醒请求信号

连接：

```python
self.inline_add_view.req_open_alarm_picker.connect(self.go_to_alarm_picker)
```

修改 `InlineAddViewMonth.btn_alarm` 点击行为：

- 不再只是 M-5c toast。
- 点击时先判断是否已有时间：
  - 优先使用 `selected_start_time`
  - 否则使用 `selected_end_time`
- 若没有时间：
  - 不 emit picker 请求。
  - toast 提示先设置时间。
- 若有时间：
  - emit：

```python
self.req_open_alarm_picker.emit(target_time, self.selected_is_alarm_mode, self.selected_alarm_duration)
```

要求：

- `InlineAddViewMonth` 不直接依赖 `AlarmPickerView`。
- `InlineAddViewMonth` 不直接写数据库。

新增或完善 `MonthWindow.go_to_alarm_picker(target_time, is_alarm, duration)`：

- 调用：

```python
self.page_alarm.set_initial_data(target_time, is_alarm, duration)
```

- 隐藏其他月添加页组件。
- 显示 `page_alarm`。

### 3.5 提醒确认回填

连接：

```python
self.page_alarm.back_requested.connect(self.back_from_alarm_picker)
self.page_alarm.confirm_requested.connect(self.on_alarm_confirmed)
```

新增方法，例如：

```python
def back_from_alarm_picker(self):
    self.page_alarm.hide()
    self.inline_add_view.show()

def on_alarm_confirmed(self, remind_dt, is_alarm, duration):
    self.inline_add_view.set_alarm_data(remind_dt, is_alarm, duration)
    self.back_from_alarm_picker()
```

要求：

- 只回填到 `InlineAddViewMonth`。
- 不直接写数据库。
- 不触发保存。
- 不刷新日程列表。

### 3.6 连接清单请求信号

连接：

```python
self.inline_add_view.req_open_list_picker.connect(self.go_to_list_picker)
```

修改 `InlineAddViewMonth.btn_list` 点击行为：

- 不再只是 M-5c toast。
- 点击时 emit：

```python
self.req_open_list_picker.emit(self.selected_list_id, "schedule")
```

要求：

- 月界面当前只支持 schedule 保存语义。
- list picker 必须使用 `list_type="schedule"`。
- 不新增 todo 支持。
- `InlineAddViewMonth` 不直接依赖 `ListPickerView`。

新增或完善 `MonthWindow.go_to_list_picker(current_category_id, list_type="schedule")`：

- 强制使用 schedule 类型：

```python
self.page_list.load_data(current_category_id, list_type="schedule")
```

- 隐藏其他月添加页组件。
- 显示 `page_list`。

### 3.7 清单确认回填

连接：

```python
self.page_list.back_requested.connect(self.back_from_list_picker)
self.page_list.confirm_requested.connect(self.on_list_confirmed)
```

新增方法，例如：

```python
def back_from_list_picker(self):
    self.page_list.hide()
    self.inline_add_view.show()

def on_list_confirmed(self, category_id):
    ...
    self.inline_add_view.set_list_data(category_id, category_name)
    self.back_from_list_picker()
```

`category_name` 获取建议：

- 若 `category_id is None`：
  - `category_name = None`
- 若有 `category_id`：
  - 使用 `db_manager.get_category(category_id)` 获取名称。
  - 若查询不到，允许名称为空或显示 `#id`，但必须日志说明。
- 不修改 `ListPickerView.confirm_requested` 签名。
- 不创建、删除清单。

### 3.8 保存字段最小接入

允许在 `InlineAddViewMonth._on_save(...)` 中只新增提醒与清单现有字段：

- `reminder_time`: `self.selected_reminder`
- `is_alarm`: `self.selected_is_alarm_mode`
- `alarm_duration`: `self.selected_alarm_duration`
- `category_id`: `self.selected_list_id`

保持以下字段不变：

- `item_type`: 仍为 `schedule`
- `priority`: 仍为 `0`
- `repeat_rule`: 仍为 `none`
- `description`: 仍取详情输入
- `start_time / end_time`: 仍使用 M-5d 选中时间逻辑

禁止在 `_on_save(...)` 中新增：

- `combo_priority` 保存
- `combo_repeat` 保存
- 新数据库字段
- todo 保存分支

本轮不要求执行真实保存验证，避免写入 `schedule.db`。真实写入回归留到 `M-5g`。

### 3.9 更新 `Work_Log.md`

至少记录：

- 本轮任务名称：`M-5e（月界面提醒与清单选择接入）`
- 开工前 git 状态
- 实际修改文件
- `AlarmPickerView` 接入方式
- `ListPickerView` 接入方式
- 内嵌后 `btn_close / btn_suspend` 处理方式
- `btn_alarm` 是否按“必须先有时间”打开 picker
- `btn_list` 是否以 `list_type="schedule"` 打开 picker
- `on_alarm_confirmed(...)` 回填结果
- `on_list_confirmed(...)` 回填结果
- `_on_save(...)` 提醒 / 清单字段接入策略
- 是否未接 priority/repeat 保存
- 是否未创建 / 删除清单
- 是否未写入 `schedule.db`
- 验证命令和结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

## 4. 验收命令

### 4.1 定位新增链路

```powershell
rg -n "AlarmPickerView|ListPickerView|page_alarm|page_list|go_to_alarm_picker|back_from_alarm_picker|on_alarm_confirmed|go_to_list_picker|back_from_list_picker|on_list_confirmed|req_open_alarm_picker|req_open_list_picker|set_alarm_data|set_list_data|btn_alarm|btn_list|selected_reminder|selected_is_alarm_mode|selected_alarm_duration|selected_list_id|selected_list_name|_on_save|btn_close|btn_suspend" src/ui/month_window.py
```

预期：

- `AlarmPickerView / ListPickerView` 只在 `month_window.py` 中被月界面局部使用。
- `btn_alarm` 会在有时间时 emit `req_open_alarm_picker`。
- `btn_list` 会 emit `req_open_list_picker`。
- 新增 `go_to_alarm_picker / back_from_alarm_picker / on_alarm_confirmed` 或等价方法。
- 新增 `go_to_list_picker / back_from_list_picker / on_list_confirmed` 或等价方法。
- `page_alarm.btn_close / page_list.btn_close` 不会关闭整个月界面。

### 4.2 import 验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.month_window import MonthWindow, InlineAddViewMonth; from src.ui.alarm_picker import AlarmPickerView; from src.ui.list_picker import ListPickerView; print('month alarm/list imports ok', MonthWindow, InlineAddViewMonth, AlarmPickerView, ListPickerView)"
```

### 4.3 offscreen 构造验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); print('month created', w is not None); print('has page_alarm', hasattr(w, 'page_alarm')); print('has page_list', hasattr(w, 'page_list')); assert hasattr(w, 'page_alarm'); assert hasattr(w, 'page_list')"
```

### 4.4 未设置时间时提醒不打开验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); w.inline_add_view.reset(QDate.currentDate().addDays(1)); w.inline_add_view.btn_alarm.click(); print('alarm visible without time', w.page_alarm.isVisible()); assert not w.page_alarm.isVisible()"
```

### 4.5 有时间时提醒 picker 打开验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from datetime import datetime; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); target=QDate.currentDate().addDays(1); end=datetime(target.year(), target.month(), target.day(), 10, 0); w.inline_add_view.reset(target); w.inline_add_view.set_time_data(None, end); w.inline_add_view.btn_alarm.click(); print('alarm visible', w.page_alarm.isVisible()); print('target time', w.page_alarm.target_time); assert w.page_alarm.isVisible(); assert w.page_alarm.target_time == end"
```

### 4.6 提醒确认回填验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from datetime import datetime; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); target=QDate.currentDate().addDays(1); remind=datetime(target.year(), target.month(), target.day(), 9, 50); w.inline_add_view.reset(target); w.on_alarm_confirmed(remind, True, 1); print('alarm state', w.inline_add_view.selected_reminder, w.inline_add_view.selected_is_alarm_mode, w.inline_add_view.selected_alarm_duration); assert w.inline_add_view.selected_reminder == remind; assert w.inline_add_view.selected_is_alarm_mode is True; assert w.inline_add_view.selected_alarm_duration == 1"
```

### 4.7 清单 picker 打开验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); w.inline_add_view.reset(QDate.currentDate().addDays(1)); w.inline_add_view.btn_list.click(); print('list visible', w.page_list.isVisible()); print('list type', getattr(w.page_list, 'current_list_type', None)); assert w.page_list.isVisible(); assert w.page_list.current_list_type == 'schedule'"
```

### 4.8 清单确认回填验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import MonthWindow; from src.data.database import db_manager; app=QApplication([]); w=MonthWindow(); cats=db_manager.get_active_categories(list_type='schedule'); sample=cats[0] if cats else None; cid=sample.id if sample else None; w.on_list_confirmed(cid); print('list state', w.inline_add_view.selected_list_id, w.inline_add_view.selected_list_name); assert w.inline_add_view.selected_list_id == cid"
```

### 4.9 内嵌关闭按钮验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -u -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from datetime import datetime; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); target=QDate.currentDate().addDays(1); end=datetime(target.year(), target.month(), target.day(), 10, 0); w.inline_add_view.reset(target); w.inline_add_view.set_time_data(None, end); w.go_to_alarm_picker(end, False, 0); print('before alarm close', w.page_alarm.isVisible(), w.inline_add_view.isVisible(), w.isHidden(), flush=True); w.page_alarm.btn_close.click(); print('after alarm close', w.page_alarm.isVisible(), w.inline_add_view.isVisible(), w.isHidden(), flush=True); assert not w.page_alarm.isVisible(); assert w.inline_add_view.isVisible(); assert not w.isHidden(); w.go_to_list_picker(None, 'schedule'); print('before list close', w.page_list.isVisible(), w.inline_add_view.isVisible(), w.isHidden(), flush=True); w.page_list.btn_close.click(); print('after list close', w.page_list.isVisible(), w.inline_add_view.isVisible(), w.isHidden(), flush=True); assert not w.page_list.isVisible(); assert w.inline_add_view.isVisible(); assert not w.isHidden()"
```

### 4.10 保存字段隔离检查

检查 `_on_save(...)`：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import inspect; from src.ui.month_window import InlineAddViewMonth; src=inspect.getsource(InlineAddViewMonth._on_save); assert 'reminder_time' in src; assert 'selected_reminder' in src; assert 'is_alarm' in src; assert 'selected_is_alarm_mode' in src; assert 'alarm_duration' in src; assert 'selected_alarm_duration' in src; assert 'category_id' in src; assert 'selected_list_id' in src; assert 'combo_priority' not in src; assert 'combo_repeat' not in src; print('_on_save alarm/list-only extension ok')"
```

### 4.11 不创建 / 删除清单验证约束

本轮不要通过 UI 操作新增或删除清单。只允许读取已有清单并回填已有 id 或 `None`。

检查 `schedule.db`：

```powershell
git diff --name-only -- schedule.db
```

预期无输出。

### 4.12 语法检查

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/month_window.py src/ui/alarm_picker.py src/ui/list_picker.py main.py
```

### 4.13 禁止范围检查

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

### 4.14 总范围检查

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

- 本轮任务名称：`M-5e（月界面提醒与清单选择接入）`
- 开工前 git 状态
- 实际修改文件
- 是否存在开工前既有 diff
- `AlarmPickerView` 接入方式
- `ListPickerView` 接入方式
- 内嵌后 `btn_close / btn_suspend` 处理方式
- `btn_alarm` 未设置时间时是否阻止打开 picker
- `btn_alarm` 有时间时是否打开 picker
- `btn_list` 是否以 `list_type="schedule"` 打开 picker
- `on_alarm_confirmed(...)` 回填验证结果
- `on_list_confirmed(...)` 回填验证结果
- `_on_save(...)` 提醒与清单字段接入策略
- 是否未接 priority/repeat 保存
- 是否未创建 / 删除清单
- 是否未写入 `schedule.db`
- import / offscreen / py_compile 验证结果
- 禁止范围检查结果
- 未完成事项
- 风险或疑点

特别记录：

- 本轮只接提醒 picker 和清单 picker。
- 本轮不修改 `AlarmPickerView / ListPickerView` 源文件。
- 本轮不修改主界面 / 周界面添加链路。
- 本轮不接 priority/repeat 保存。
- 后续 `M-5f` 再处理紧急性 / 重复规则 / 保存结构对齐。

## 6. Work_Task_Prompts.md 处理要求

如需要维护复核锚点，可将当前状态更新为：

```text
M-5e 已执行，等待决策/顾问窗口复核。
下一步候选：M-5f。
```

不得在本轮自行写入 `M-5f` 的执行提示词。

## 7. 完成后要求

完成后不要提交 Git，等待决策/顾问窗口复核。
