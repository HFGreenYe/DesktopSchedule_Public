# 当前复核锚点：M-5f 已执行

当前状态：

- M-5f 已执行，等待决策/顾问窗口复核。
- 下一步候选：M-5g。
- 下方保留 M-5f 已执行提示词全文，供日志对照复核。

## M-5f：月界面紧急性 / 重复规则 / 保存结构对齐

请执行 `M-5f：月界面紧急性 / 重复规则 / 保存结构对齐`。本轮只对齐月界面添加表单的紧急性、重复规则和最终保存字段语义，不接右键菜单，不进入 `M-5g`。

## 1. 本轮目标

基于 `M-5b` 审查结论、`M-5c` 表单壳、`M-5d` 时间选择、`M-5e` 提醒与清单选择，本轮完成月界面添加表单保存结构与主界面添加页的字段语义对齐。

重点：

- 对齐主界面 `AddScheduleView._on_save(...)` 的已实现语义。
- `priority` 使用 `combo_priority.currentIndex()`。
- `repeat_rule` 使用 `combo_repeat.currentText().strip()`。
- 不直接按 UI 文案硬写新的映射表。
- 不新增数据库字段。
- 不新增新的重复规则。
- 不新增 todo 支持。
- 不修改主界面 / 周界面添加页。

必须先确认当前真实基线：

- 主界面 `src/ui/add_view.py`：
  - `priority = self.combo_priority.currentIndex()`
  - `repeat_text = self.combo_repeat.currentText().strip()`
  - 保存字段包含：
    - `title`
    - `item_type`
    - `priority`
    - `repeat_rule`
    - `description`
    - `start_time`
    - `end_time`
    - `reminder_time`
    - `is_alarm`
    - `alarm_duration`
    - `category_id`
- 周界面 `src/ui/add_view_week.py` 也使用相同保存字段语义。
- 当前重复服务只明确支持：
  - `每天`
  - `每周`
  - `每月`
- 非重复兼容：
  - `none`
  - `无`
  - `不重复`
  - 空字符串
- `none` 是历史兼容值 / 数据库默认值之一，不得误删或改动服务层兼容规则。
- 本轮月界面 UI 保存时应对齐主界面显示值，不新增 `daily / weekly / monthly / yearly` 行为。
- 不新增 `每年` 行为。

本轮应修正一个现有月界面语义风险：

- 月界面当前 `combo_priority` 为 `["无", "低", "中", "高"]`。
- 主界面和周界面的紧急性选项是 `["低", "中", "高"]`，保存值为 index：
  - `0 = 低`
  - `1 = 中`
  - `2 = 高`
- 因此 M-5f 应将月界面紧急性控件对齐为 `["低", "中", "高"]`，不要保留“无”，避免保存值与 UI 文案错位。

重复规则控件应继续对齐主界面语义：

- 显示项为：
  - `无`
  - `每天`
  - `每周`
  - `每月`
- 保存值使用 `currentText().strip()`。
- 不写新的英文 repeat rule。
- 不新增每年。

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
- `manage_instruction/Work_Snapshot.md`
- `manage_instruction/ReconstructionDolder/`

### 数据库约束

- 本轮不得真实写入 `schedule.db`。
- 不运行 `db_manager.add_schedule(...)` 的真实数据库写入路径。
- 保存结构验收必须用 mock / monkeypatch 截获 `db_manager.add_schedule(schedule_data)` 入参。
- 不允许用 `每天 / 每周 / 每月` 做真实写库验收，避免批量生成重复日程。
- 最终 `schedule.db` 必须无 tracked diff。

### 禁止事项

- 不新增数据库字段。
- 不新增 todo 保存支持。
- 不新增 English repeat rule 行为。
- 不新增 `每年/yearly` 行为。
- 不修改 `ScheduleRepeatService`。
- 不修改 `DatabaseManager.add_schedule(...)`。
- 不修改主界面 / 周界面添加页。
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
Get-Content -Path src\ui\add_view.py -Encoding UTF8
Get-Content -Path src\ui\add_view_week.py -Encoding UTF8
Get-Content -Path src\services\schedule_repeat_service.py -Encoding UTF8
Get-Content -Path src\data\database.py -Encoding UTF8
```

重点确认：

- 主界面 `priority` 保存方式。
- 主界面 `repeat_rule` 保存方式。
- 周界面 `priority / repeat_rule` 保存方式。
- 月界面当前 `combo_priority / combo_repeat` 的选项。
- 月界面 `_on_save(...)` 当前字段。
- `ScheduleRepeatService` 支持的重复规则与非重复兼容值。
- `DatabaseManager.add_schedule(...)` 对 `none / 无 / 不重复 / 空字符串` 的兼容。

### 3.2 对齐月界面紧急性控件

修改 `InlineAddViewMonth` 的 `combo_priority`：

- 从当前：
  - `["无", "低", "中", "高"]`
- 改为对齐主界面 / 周界面：
  - `["低", "中", "高"]`

要求：

- `reset_form(...)` 仍设置 `combo_priority.setCurrentIndex(0)`。
- index 0 表示低紧急性。
- index 1 表示中紧急性。
- index 2 表示高紧急性。
- 不新增“无紧急性”的数据库语义。
- 不修改主界面 / 周界面的选项。

### 3.3 保持重复规则控件语义

确认 `combo_repeat` 保持：

- `无`
- `每天`
- `每周`
- `每月`

要求：

- 不新增 `每年`。
- 不新增 `daily / weekly / monthly / yearly`。
- 不在 UI 和保存层做额外映射。
- 保存时使用 `self.combo_repeat.currentText().strip()`。
- 不修改 `ScheduleRepeatService.NON_REPEAT_RULES`，保留历史兼容值 `none`。

### 3.4 对齐 `_on_save(...)` 保存结构

修改 `InlineAddViewMonth._on_save(...)`，使其与主界面已实现字段语义对齐。

保存字段应包含：

```python
schedule_data = {
    "title": title,
    "item_type": "schedule",
    "priority": self.combo_priority.currentIndex(),
    "repeat_rule": self.combo_repeat.currentText().strip(),
    "description": self.input_desc.toPlainText().strip(),
    "start_time": self.selected_start_time,
    "end_time": self.selected_end_time,
    "reminder_time": self.selected_reminder,
    "is_alarm": self.selected_is_alarm_mode,
    "alarm_duration": self.selected_alarm_duration,
    "category_id": self.selected_list_id,
}
```

要求：

- 继续保持 M-5d 的“未设置时间不保存”策略。
- 继续保持 `item_type = "schedule"`。
- 不新增 todo 分支。
- 不新增字段。
- 不改 `db_manager.add_schedule(...)` 调用方式。
- 保存成功后继续 emit `saved`。
- 保存成功后的 reset / 刷新逻辑保持现有月界面行为。

### 3.5 不做真实写库验收

本轮只用 mock / monkeypatch 验证 `_on_save(...)` 传给 `db_manager.add_schedule(...)` 的 `schedule_data`。

原因：

- `每天 / 每周 / 每月` 会批量生成 366 / 53 / 13 条日程。
- 即使非重复临时日程保存后删除，也可能改变本地 SQLite 文件内容。
- M-5g 才做整体验收，可另行设计真实写库和清理策略。

本轮不得：

- 真实保存临时日程。
- 真实删除临时日程。
- 通过 UI 新增 / 删除清单。
- 让 `schedule.db` 出现 tracked diff。

### 3.6 更新 Work_Log.md

至少记录：

- 本轮任务名称：`M-5f（月界面紧急性 / 重复规则 / 保存结构对齐）`
- 开工前 git 状态
- 实际修改文件
- 主界面 priority / repeat_rule 基线确认结果
- 周界面 priority / repeat_rule 基线确认结果
- `ScheduleRepeatService` 重复规则基线确认结果
- 月界面 `combo_priority` 是否已从 `无/低/中/高` 改为 `低/中/高`
- 月界面 `combo_repeat` 是否保持 `无/每天/每周/每月`
- `_on_save(...)` 保存字段对齐结果
- 是否未新增 todo 支持
- 是否未新增每年 / English repeat rule
- 是否未修改重复服务 / 数据层
- mock 保存结构验收结果
- 是否未真实写入 `schedule.db`
- `schedule.db` 是否无 tracked diff
- 验证命令和结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

## 4. 验收命令

### 4.1 定位保存结构与控件项

```powershell
rg -n "combo_priority|combo_repeat|priority|repeat_rule|selected_start_time|selected_end_time|selected_reminder|selected_is_alarm_mode|selected_alarm_duration|selected_list_id|_on_save|每天|每周|每月|每年|daily|weekly|monthly|yearly|none" src/ui/month_window.py src/ui/add_view.py src/ui/add_view_week.py src/services/schedule_repeat_service.py src/data/database.py
```

预期：

- 月界面 `combo_priority` 只有 `低 / 中 / 高`。
- 月界面 `combo_repeat` 只有 `无 / 每天 / 每周 / 每月`。
- 月界面 `_on_save(...)` 使用：
  - `combo_priority.currentIndex()`
  - `combo_repeat.currentText().strip()`
- 不出现新增 `每年/yearly` 行为。
- `none` 只作为历史兼容 / 默认值存在，不作为月界面新增写入值。

### 4.2 import 验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.month_window import MonthWindow, InlineAddViewMonth; print('month import ok', MonthWindow, InlineAddViewMonth)"
```

### 4.3 offscreen 控件语义验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import InlineAddViewMonth; app=QApplication([]); v=InlineAddViewMonth(); priorities=[v.combo_priority.itemText(i).strip() for i in range(v.combo_priority.count())]; repeats=[v.combo_repeat.itemText(i).strip() for i in range(v.combo_repeat.count())]; print('priorities', priorities); print('repeats', repeats); assert priorities == ['低', '中', '高']; assert repeats == ['无', '每天', '每周', '每月']"
```

### 4.4 reset 默认值验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import InlineAddViewMonth; app=QApplication([]); v=InlineAddViewMonth(); v.combo_priority.setCurrentIndex(2); v.combo_repeat.setCurrentIndex(2); v.reset_form(); print('priority index', v.combo_priority.currentIndex(), v.combo_priority.currentText().strip()); print('repeat index', v.combo_repeat.currentIndex(), v.combo_repeat.currentText().strip()); assert v.combo_priority.currentIndex() == 0; assert v.combo_priority.currentText().strip() == '低'; assert v.combo_repeat.currentIndex() == 0; assert v.combo_repeat.currentText().strip() == '无'"
```

### 4.5 `_on_save(...)` 字段表达式检查

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import inspect; from src.ui.month_window import InlineAddViewMonth; src=inspect.getsource(InlineAddViewMonth._on_save); assert 'combo_priority.currentIndex()' in src; assert 'combo_repeat.currentText().strip()' in src; assert \"'item_type': 'schedule'\" in src or '\"item_type\": \"schedule\"' in src; assert 'selected_start_time' in src; assert 'selected_end_time' in src; assert 'selected_reminder' in src; assert 'selected_is_alarm_mode' in src; assert 'selected_alarm_duration' in src; assert 'selected_list_id' in src; assert 'yearly' not in src; assert '每年' not in src; print('_on_save priority/repeat/save structure ok')"
```

### 4.6 mock 保存结构验收

使用 monkeypatch 截获 `db_manager.add_schedule(...)` 入参，不真实写库。

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from datetime import datetime; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import InlineAddViewMonth; from src.data import database; app=QApplication([]); v=InlineAddViewMonth(); target=QDate.currentDate().addDays(1); start=datetime(target.year(), target.month(), target.day(), 9, 0); end=datetime(target.year(), target.month(), target.day(), 10, 0); v.reset(target); v.input_title.setText('__mock_m5f_month_save__'); v.input_desc.setPlainText('mock validation only'); v.set_time_data(start, end); v.set_alarm_data(start, True, 1); v.set_list_data(12345, 'mock-list'); v.combo_priority.setCurrentIndex(2); v.combo_repeat.setCurrentIndex(0); calls=[]; captured=[]; original=database.db_manager.add_schedule; database.db_manager.add_schedule=lambda data: captured.append(dict(data)) or True; v.saved.connect(lambda: calls.append('saved')); v._on_save(); database.db_manager.add_schedule=original; print('saved calls', calls); print('captured', captured); assert calls == ['saved']; assert len(captured) == 1; data=captured[0]; assert data['title'] == '__mock_m5f_month_save__'; assert data['item_type'] == 'schedule'; assert data['priority'] == 2; assert data['repeat_rule'] == '无'; assert data['description'] == 'mock validation only'; assert data['start_time'] == start; assert data['end_time'] == end; assert data['reminder_time'] == start; assert data['is_alarm'] is True; assert data['alarm_duration'] == 1; assert data['category_id'] == 12345"
```

### 4.7 确认未做重复真实写库

本轮不运行 `每天 / 每周 / 每月` 的 `_on_save()` 真实保存测试。

只做静态确认：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import InlineAddViewMonth; app=QApplication([]); v=InlineAddViewMonth(); repeats=[v.combo_repeat.itemText(i).strip() for i in range(v.combo_repeat.count())]; print('repeat options', repeats); assert repeats == ['无', '每天', '每周', '每月']"
```

### 4.8 schedule.db diff 检查

```powershell
git diff --name-only -- schedule.db
```

预期无输出。

### 4.9 语法检查

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/month_window.py main.py
```

### 4.10 禁止范围检查

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

### 4.11 总范围检查

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

- 本轮任务名称：`M-5f（月界面紧急性 / 重复规则 / 保存结构对齐）`
- 开工前 git 状态
- 实际修改文件
- 是否存在开工前既有 diff
- 主界面 priority 保存基线
- 主界面 repeat_rule 保存基线
- 周界面 priority / repeat_rule 保存基线
- 月界面 `combo_priority` 选项修正结果
- 月界面 `combo_repeat` 选项确认结果
- `_on_save(...)` 保存字段对齐结果
- 是否未新增 todo 支持
- 是否未新增每年 / English repeat rule
- 是否未修改重复服务 / 数据层
- mock 保存结构验收结果
- 是否未真实写入 `schedule.db`
- `schedule.db` 是否无 tracked diff
- import / offscreen / py_compile 验证结果
- 禁止范围检查结果
- 未完成事项
- 风险或疑点

特别记录：

- 本轮只对齐月界面 priority / repeat_rule / 保存结构。
- 本轮不做真实写库验收。
- 本轮不修改 `ScheduleRepeatService` 或 `DatabaseManager.add_schedule(...)`。
- 本轮不接月界面右键菜单。
- 后续 `M-5g` 再做整体验收。

## 6. Work_Task_Prompts.md 处理要求

如需要维护复核锚点，可将当前状态更新为：

```text
M-5f 已执行，等待决策/顾问窗口复核。
下一步候选：M-5g。
```

不得在本轮自行写入 `M-5g` 的执行提示词。

## 7. 完成后要求

完成后不要提交 Git，等待决策/顾问窗口复核。
