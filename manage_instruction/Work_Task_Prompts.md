# 当前待执行提示词：M-5c

## M-5c：月界面添加表单 UI 壳补齐

请执行 `M-5c：月界面添加表单 UI 壳补齐`。本轮只补齐月界面 `InlineAddViewMonth` 的添加表单 UI 壳、内部状态字段、picker 请求信号占位和回填接口。本轮不接真实 picker，不修改 `_on_save(...)` 保存字段，不写数据库，不修改主界面 / 周界面添加页，不进入 M-5d / M-5e / M-5f。

## 1. 本轮目标

基于 `M-5b` 只读审查结论，在 `src/ui/month_window.py` 内对 `InlineAddViewMonth` 做最小 UI 壳补齐：

- 补齐月界面左侧添加表单的展示壳，使其更接近主界面添加表单的能力布局。
- 增加内部状态字段，为后续时间、提醒、清单 picker 接入预留承接位置。
- 增加回填接口，为后续 `M-5d / M-5e` 做准备。
- 保留时间 / 提醒 / 清单按钮为可定位实例属性：
  - `self.btn_time`
  - `self.btn_alarm`
  - `self.btn_list`
- 本轮不打开真实 picker。
- 本轮不连接 `MainWindow` picker。
- 本轮不新增 `MonthWindow` picker 页面栈。
- 本轮不改变 `_on_save(...)` 当前入库字段。
- 本轮不改变已有保存逻辑和数据库写入行为。

本轮目标是“可见 UI 壳 + 状态承接接口”，不是完整添加功能闭环。

## 2. 允许 / 禁止

### 允许修改

- `src/ui/month_window.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

如 UI 壳需要新增 Qt 控件类导入，例如 `QComboBox`，只能在 `src/ui/month_window.py` 内补充必要 import，不得改其他文件。

### 禁止修改

- `src/ui/main_window.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- `src/ui/week_window.py`
- `src/ui/calendar_pop.py`
- `src/ui/common/`
- `src/ui/popups/`
- `src/ui/utils/`
- 除 `src/ui/month_window.py` 以外的任何 `src/ui/` 文件
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

- 不接真实时间 picker。
- 不接真实提醒 picker。
- 不接真实清单 picker。
- 不新增 `MonthWindow.page_time / page_alarm / page_list`。
- 不新增 `MonthWindow.go_to_time_picker / go_to_alarm_picker / go_to_list_picker`。
- 不连接 `MainWindow` 的 picker 页面或方法。
- 不修改 `_on_save(...)` 保存字段。
- 不新增 `reminder_time` / `is_alarm` / `alarm_duration` 入库。
- 不让 UI 壳阶段的紧急性 / 重复控件影响保存。
- 不新增重复规则。
- 不新增英文 `repeat_rule`。
- 不新增数据库字段。
- 不修改数据层、服务层、控制层。
- 不修改月界面右键菜单。
- 不提交 Git。

若开工前已有 diff，必须在 `Work_Log.md` 中单独记录，并区分是否属于本轮产生。

## 3. 具体任务

### 3.1 读取当前依据

读取：

```powershell
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
Get-Content -Path manage_instruction\Final_Formulation.md -Encoding UTF8
Get-Content -Path src\ui\month_window.py -Encoding UTF8
Get-Content -Path src\ui\add_view.py -Encoding UTF8
```

重点确认：

- `M-5b` 结论：先补月界面添加表单能力，再做右键菜单。
- 月界面添加目标日期已由 `M-5` 接入。
- 本轮只做 UI 壳与状态承接，不接 picker。
- 后续真实功能分拆为：
  - `M-5d` 时间 picker。
  - `M-5e` 提醒 / 清单 picker。
  - `M-5f` 紧急性 / 重复规则 / 保存结构对齐。

### 3.2 补齐 `InlineAddViewMonth` 内部状态字段

在 `InlineAddViewMonth` 初始化或 reset 相关位置补充后续 picker 需要的内部状态字段。

建议字段：

```python
self.selected_start_time = None
self.selected_end_time = None
self.selected_reminder = None
self.selected_alarm_duration = 0
self.selected_list_id = None
self.selected_list_name = None
```

要求：

- 字段只作为状态承接。
- 本轮不得写入数据库。
- 本轮不得影响 `_on_save(...)`。
- reset 时必须清空。

### 3.3 增加回填接口

在 `InlineAddViewMonth` 中增加轻量回填方法，供后续 picker 使用。

建议方法：

```python
def set_time_data(self, start_time, end_time): ...
def set_alarm_data(self, reminder_time, is_alarm_mode=False, alarm_duration=0): ...
def set_list_data(self, category_id, category_name): ...
```

要求：

- 只更新内部状态字段和 UI 文案。
- 不保存数据库。
- 不调用 `_on_save(...)`。
- 不 emit 保存信号。
- 不访问 `db_manager` / Repository / Service。
- 不依赖 `MainWindow`。

### 3.4 增加 picker 请求信号占位

可在 `InlineAddViewMonth` 上增加信号占位，供后续 `M-5d / M-5e` 使用。

建议：

```python
req_open_time_picker = pyqtSignal(object, object)
req_open_alarm_picker = pyqtSignal(object, bool, int)
req_open_list_picker = pyqtSignal(object, str)
```

要求：

- 本轮可以声明信号。
- 本轮不得在 `MonthWindow` 中连接这些信号。
- 本轮不得打开 picker 页面。
- 本轮按钮不得 emit 半成品 picker 请求。
- 若为了避免误触，可禁用按钮或显示轻量 toast；不得写入状态，不得打开 picker。

### 3.5 补齐 UI 壳

在月界面左侧添加表单区域补齐以下 UI 壳：

- 标题输入框。
- 详情描述输入框。
- 图标按钮行：
  - 时间按钮，实例属性保留为 `self.btn_time`。
  - 提醒按钮，实例属性保留为 `self.btn_alarm`。
  - 清单按钮，实例属性保留为 `self.btn_list`。
- 紧急性显示 / 控件壳。
- 重复规则显示 / 控件壳。
- 当前状态摘要文案：
  - 时间未设置。
  - 无提醒。
  - 清单未选择。
- 取消 / 保存按钮保持原有语义。

要求：

- UI 可见即可，不要求和主界面完全一致。
- 可根据月界面左侧窄栏做紧凑布局。
- 时间 / 提醒 / 清单按钮本轮不得打开真实 picker。
- 紧急性 / 重复控件如果可操作，本轮也不得影响 `_on_save(...)`。
- 重复规则如显示选项，只能沿用当前已有显示体系，例如 `无 / 每天 / 每周 / 每月`；不得新增 `每年`，不得新增英文规则。
- 若按钮点击需要反馈，只能禁用或显示轻量提示，不得产生业务状态。

### 3.6 reset 行为

确保 `reset_form(...)` 或等价重置逻辑清空：

- 标题。
- 详情。
- `selected_start_time`。
- `selected_end_time`。
- `selected_reminder`。
- `selected_alarm_duration`。
- `selected_list_id`。
- `selected_list_name`。
- 时间 / 提醒 / 清单 UI 文案。
- 紧急性 / 重复 UI 壳状态。

不得改变 `reset_form(...)` 的既有调用方语义。

### 3.7 `_on_save(...)` 保持不变

本轮必须保持 `_on_save(...)` 的保存字段不变。

当前保存结构仍应只沿用既有字段，例如：

```python
title
item_type
priority
repeat_rule
description
start_time
end_time
category_id
```

要求：

- 不新增 `reminder_time`。
- 不新增 `is_alarm`。
- 不新增 `alarm_duration`。
- 不使用 `selected_start_time` / `selected_end_time` 写入保存。
- 不使用 `selected_reminder` 写入保存。
- 不使用 `selected_list_id` 写入保存。
- 不让紧急性 / 重复 UI 壳影响保存。

注意：上述新字段允许出现在 reset、回填接口和 UI 更新方法中；验收时必须单独检查 `_on_save(...)` 方法体，避免误判。

### 3.8 更新日志

更新 `manage_instruction/Work_Log.md`，记录本轮修改、验证结果和未完成事项。

## 4. 验收命令

### 4.1 静态定位

```powershell
rg -n "class InlineAddViewMonth|selected_start_time|selected_end_time|selected_reminder|selected_alarm_duration|selected_list_id|selected_list_name|set_time_data|set_alarm_data|set_list_data|req_open_time_picker|req_open_alarm_picker|req_open_list_picker|btn_time|btn_alarm|btn_list" src/ui/month_window.py
```

### 4.2 import 验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.month_window import MonthWindow, InlineAddViewMonth; print('month imports ok', MonthWindow, InlineAddViewMonth)"
```

### 4.3 offscreen 构造验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import InlineAddViewMonth; app=QApplication([]); v=InlineAddViewMonth(); print('created', v is not None); print('has btn_time', hasattr(v, 'btn_time')); print('has btn_alarm', hasattr(v, 'btn_alarm')); print('has btn_list', hasattr(v, 'btn_list')); assert hasattr(v, 'btn_time'); assert hasattr(v, 'btn_alarm'); assert hasattr(v, 'btn_list')"
```

### 4.4 reset 状态验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import InlineAddViewMonth; app=QApplication([]); v=InlineAddViewMonth(); v.set_time_data('09:00','10:00'); v.set_alarm_data('09:00', True, 10); v.set_list_data(123, '测试清单'); v.reset_form(); print('states', v.selected_start_time, v.selected_end_time, v.selected_reminder, v.selected_alarm_duration, v.selected_list_id, v.selected_list_name); assert v.selected_start_time is None; assert v.selected_end_time is None; assert v.selected_reminder is None; assert v.selected_alarm_duration == 0; assert v.selected_list_id is None; assert v.selected_list_name is None"
```

### 4.5 回填接口验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import InlineAddViewMonth; app=QApplication([]); v=InlineAddViewMonth(); v.set_time_data('08:30','09:30'); v.set_alarm_data('08:20', True, 5); v.set_list_data(7, '工作'); print('time', v.selected_start_time, v.selected_end_time); print('alarm', v.selected_reminder, v.selected_alarm_duration); print('list', v.selected_list_id, v.selected_list_name); assert v.selected_start_time == '08:30'; assert v.selected_end_time == '09:30'; assert v.selected_reminder == '08:20'; assert v.selected_alarm_duration == 5; assert v.selected_list_id == 7; assert v.selected_list_name == '工作'"
```

### 4.6 picker 未接入验证

```powershell
rg -n "go_to_time_picker|go_to_alarm_picker|go_to_list_picker|page_time|page_alarm|page_list" src/ui/month_window.py
```

预期无输出。

允许 `InlineAddViewMonth` 中存在以下信号声明：

```text
req_open_time_picker
req_open_alarm_picker
req_open_list_picker
```

但不得出现 `MonthWindow` 对这些信号的连接、页面栈或真实 picker 打开逻辑。

### 4.7 `_on_save(...)` 方法体隔离检查

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import inspect; from src.ui.month_window import InlineAddViewMonth; src=inspect.getsource(InlineAddViewMonth._on_save); print(src); assert 'reminder_time' not in src; assert 'is_alarm' not in src; assert 'alarm_duration' not in src; assert 'selected_start_time' not in src; assert 'selected_end_time' not in src; assert 'selected_reminder' not in src; assert 'selected_list_id' not in src"
```

### 4.8 保存字段静态检查

```powershell
rg -n "reminder_time|is_alarm|alarm_duration|selected_start_time|selected_end_time|selected_reminder|selected_list_id|selected_list_name" src/ui/month_window.py
```

允许这些字段出现在状态字段、reset、回填接口和 UI 文案更新中。
必须结合 4.7 确认 `_on_save(...)` 没有使用这些字段。

### 4.9 M-1 到 M-5 回归定位

```powershell
rg -n "schedule_markers|marker|paint|mouseDoubleClickEvent|selected_date|jump|persistent|MonthDayPanel|switch_to_add_page|target_date|reset_form" src/ui/month_window.py src/ui/popups/month_day_panel.py
```

### 4.10 语法检查

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/month_window.py main.py
```

### 4.11 禁止范围检查

```powershell
git diff --name-only -- src/ui/main_window.py
git diff --name-only -- src/ui/add_view.py
git diff --name-only -- src/ui/add_view_week.py
git diff --name-only -- src/ui/week_window.py
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

预期以上命令均无输出。

### 4.12 允许范围检查

```powershell
git diff --name-only
git status --short --branch
```

预期最终只允许：

```text
src/ui/month_window.py
manage_instruction/Work_Log.md
manage_instruction/Work_Task_Prompts.md
```

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：`M-5c（月界面添加表单 UI 壳补齐）`
- 开工前 git 状态。
- 实际修改文件。
- `InlineAddViewMonth` 新增状态字段清单。
- 新增回填接口清单：
  - `set_time_data`
  - `set_alarm_data`
  - `set_list_data`
- 是否新增 picker 请求信号占位。
- 是否连接真实 picker：必须记录为否。
- 是否新增 `MonthWindow.page_time / page_alarm / page_list`：必须记录为否。
- 是否新增 `MonthWindow.go_to_*_picker`：必须记录为否。
- `btn_time / btn_alarm / btn_list` 是否作为实例属性保留。
- UI 壳新增内容：
  - 详情输入。
  - 时间按钮。
  - 提醒按钮。
  - 清单按钮。
  - 紧急性显示 / 控件壳。
  - 重复规则显示 / 控件壳。
- 必要 Qt import 是否仅在 `src/ui/month_window.py` 内补充。
- `_on_save(...)` 兼容性说明：
  - 未新增保存字段。
  - 未写入提醒字段。
  - 未写入 picker 状态。
  - 未让紧急性 / 重复 UI 壳影响保存。
- `_on_save(...)` 方法体隔离检查结果。
- import 验证结果。
- offscreen 构造验证结果。
- reset 状态验证结果。
- 回填接口验证结果。
- picker 未接入验证结果。
- M-1 到 M-5 回归定位结果。
- `py_compile` 结果。
- diff 范围检查结果。
- 未完成事项。
- 风险或疑点。

特别记录：

- 本轮只做 UI 壳和状态承接。
- 本轮不接时间 picker。
- 本轮不接提醒 picker。
- 本轮不接清单 picker。
- 本轮不修改保存字段。
- 后续 `M-5d` 再接时间 picker。
- 后续 `M-5e` 再接提醒 / 清单 picker。
- 后续 `M-5f` 再处理紧急性 / 重复规则 / 保存结构对齐。

## 6. Work_Task_Prompts.md 处理要求

如需要维护复核锚点，可将当前状态更新为：

```text
M-5c 已执行，等待决策/顾问窗口复核。
下一步候选：M-5d。
```

不得在本轮自行写入 `M-5d` 的执行提示词。

## 7. 完成后要求

完成后不要提交 Git，等待决策/顾问窗口复核。
