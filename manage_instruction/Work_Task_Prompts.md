# 当前复核锚点：M-5g 已执行

当前状态：

- `M-5g（月界面添加能力整体验收）` 已执行。
- 主窗口已按提示词与日志对照复核，并复跑关键验证。
- 下一步候选：`M-6（月界面右键菜单接入）`。
- 下方保留 M-5g 已执行提示词全文，供日志对照复核。

## M-5g：月界面添加能力整体验收

请执行 `M-5g：月界面添加能力整体验收`。本轮只做整体验收和日志记录，不扩展功能，不改源码。

## 1. 本轮目标

基于 `M-5`、`M-5b`、`M-5c`、`M-5d`、`M-5e`、`M-5f` 的完成结果，对月界面添加能力做整体验收。

重点验证：

- 月界面添加日期来源：
  - 有用户选中日期时，添加表单默认使用选中日期。
  - 无用户选中日期时，fallback 正常。
  - 过去日期不可添加。
- 时间选择链路：
  - `btn_time` 打开月内 `TimePickerView`。
  - 确认后回填 `selected_start_time / selected_end_time`。
  - 未设置时间时保存被阻止。
- 提醒链路：
  - 未设置时间时不打开提醒 picker。
  - 有时间时打开月内 `AlarmPickerView`。
  - 确认后回填 `selected_reminder / selected_is_alarm_mode / selected_alarm_duration`。
- 清单链路：
  - `btn_list` 打开月内 `ListPickerView`。
  - `list_type == "schedule"`。
  - 确认后回填 `selected_list_id / selected_list_name`。
- 保存结构：
  - `priority` 来自 `combo_priority.currentIndex()`。
  - `repeat_rule` 来自 `combo_repeat.currentText().strip()`。
  - `reminder_time / is_alarm / alarm_duration / category_id` 使用现有字段。
  - 不新增 todo 支持。
  - 不新增每年 / English repeat rule。
- 月界面刷新链路：
  - 保存成功后调用 marker / hover cache 刷新入口。
  - 保存成功后不保留添加页。
  - 持久日期 panel 关闭链路可用。
- 主界面 / 周界面添加能力不回归。
- 最终 `schedule.db` 无 tracked diff。

本轮原则：

- 不修改 `src/`。
- 不修改 `main.py`。
- 不修改 `requirements.txt`。
- 不修改 `schedule.db`。
- 不真实保存 `每天 / 每周 / 每月` 重复日程。
- 保存结构验证必须使用 mock / monkeypatch 截获 `db_manager.add_schedule(...)` 入参。
- 默认不做真实写库验收。

## 2. 允许 / 禁止

### 允许修改

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

### 禁止修改

- `src/`
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

### 禁止事项

- 不改源码。
- 不新增功能。
- 不接月界面右键菜单。
- 不修改 picker 源文件。
- 不修改数据层 / 服务层 / 控制层。
- 不真实保存 `每天 / 每周 / 每月` 重复日程。
- 不真实写入临时日程。
- 不新增或删除真实清单。
- 不提交 Git。

若开工前已有 diff，必须在 `Work_Log.md` 中单独记录，不视为本轮问题。

## 3. 具体任务

### 3.1 读取当前基线

读取：

```powershell
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
Get-Content -Path src\ui\month_window.py -Encoding UTF8
```

重点确认：

- M-5 当前日期来源逻辑。
- M-5c 表单壳字段。
- M-5d 时间 picker 接入。
- M-5e 提醒 / 清单 picker 接入。
- M-5f 保存结构对齐。
- M-6 仍未执行，右键菜单仍不在本轮范围。

### 3.2 静态检查月界面添加链路

检查以下逻辑是否存在且边界正确：

- `_get_add_target_date(...)`
- `_on_add_clicked(...)`
- `InlineAddViewMonth.reset(...)`
- `InlineAddViewMonth.reset_form(...)`
- `InlineAddViewMonth._on_save(...)`
- `go_to_time_picker(...)`
- `on_time_confirmed(...)`
- `go_to_alarm_picker(...)`
- `on_alarm_confirmed(...)`
- `go_to_list_picker(...)`
- `on_list_confirmed(...)`
- `_on_schedule_saved(...)`
- `_build_schedule_marker_cache(...)`
- `_build_hover_schedule_cache(...)`
- `_refresh_schedule_marker_cache(...)`
- `open_day_panels`
- `close_day_panels(...)`

### 3.3 mock 验证保存结构

用 mock / monkeypatch 截获 `db_manager.add_schedule(...)` 入参，验证完整字段结构。

要求：

- 不真实写入数据库。
- 不生成真实重复日程。
- 不创建 / 删除清单。
- 可模拟：
  - 未来日期
  - start/end
  - reminder
  - category_id
  - priority 高
  - repeat_rule 无
- 不验证 `每天 / 每周 / 每月` 真实保存，只静态确认选项存在。

### 3.4 验证 marker / hover / panel 刷新不回归

不真实写库的情况下，做静态与 offscreen smoke：

- `_build_schedule_marker_cache()` 可调用。
- `_build_hover_schedule_cache()` 可调用。
- `_refresh_schedule_marker_cache()` 可调用。
- `schedule_marker_cache / schedule_marker_count_cache / hover_schedule_cache` 类型正确。
- `close_day_panels()` 可调用。
- `_on_schedule_saved()` 可调用且不会报错。
- 若某些方法依赖 UI 状态，允许只做 import/offscreen smoke，并在日志说明。

### 3.5 验证主界面 / 周界面不回归

只做 import / py_compile / 静态检查：

- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- `src/ui/main_window.py`
- `src/ui/week_window.py`

不得修改这些文件。

### 3.6 更新 Work_Log.md

至少记录：

- 本轮任务名称：`M-5g（月界面添加能力整体验收）`
- 开工前 git 状态
- 实际修改文件
- M-5 到 M-5f 完成结论汇总
- 日期来源验收结果
- 过去日期不可添加验收结果
- 时间 picker 验收结果
- 提醒 picker 验收结果
- 清单 picker 验收结果
- 未设置时间保存拦截结果
- 完整保存结构 mock 验收结果
- 重复规则是否仅做静态验证
- marker cache 链路验收结果
- hover cache 链路验收结果
- 持久 panel 关闭链路验收结果
- `_on_schedule_saved(...)` 刷新入口验收结果
- 主界面 / 周界面添加页回归检查结果
- 是否未真实写入重复日程
- 是否未新增 / 删除清单
- `schedule.db` 是否无 tracked diff
- diff 范围检查结果
- 未完成事项
- 风险或疑点
- 是否建议进入 `M-6（月界面右键菜单接入）`

## 4. 验收命令

### 4.1 定位月界面添加链路

```powershell
rg -n "_get_add_target_date|_on_add_clicked|reset_form|def reset\(|def _on_save|go_to_time_picker|on_time_confirmed|go_to_alarm_picker|on_alarm_confirmed|go_to_list_picker|on_list_confirmed|_on_schedule_saved|_build_schedule_marker_cache|_build_hover_schedule_cache|_refresh_schedule_marker_cache|hover_schedule_cache|schedule_marker_cache|schedule_marker_count_cache|MonthDayPanel|open_day_panels|close_day_panels|marker" src/ui/month_window.py
```

### 4.2 import 验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.month_window import MonthWindow, InlineAddViewMonth; from src.ui.add_view import AddScheduleView; from src.ui.add_view_week import AddScheduleViewWeek; print('month/main/week add imports ok', MonthWindow, InlineAddViewMonth, AddScheduleView, AddScheduleViewWeek)"
```

### 4.3 offscreen 月窗口构造

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); print('month created', w is not None); print('has inline', hasattr(w, 'inline_add_view')); print('has page_time', hasattr(w, 'page_time')); print('has page_alarm', hasattr(w, 'page_alarm')); print('has page_list', hasattr(w, 'page_list')); assert hasattr(w, 'inline_add_view'); assert hasattr(w, 'page_time'); assert hasattr(w, 'page_alarm'); assert hasattr(w, 'page_list')"
```

### 4.4 日期来源验证

验证未来选中日期会进入添加表单：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); target=QDate.currentDate().addDays(3); w.user_selected_date=target; result=w._get_add_target_date(); print('target date', result.toString('yyyy-MM-dd')); assert result == target; w._on_add_clicked(); print('inline selected', w.inline_add_view.selected_date.toString('yyyy-MM-dd')); assert w.inline_add_view.selected_date == target"
```

验证过去日期不可添加：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); past=QDate.currentDate().addDays(-1); w.user_selected_date=past; w.inline_add_view.hide(); w._on_add_clicked(); after=w.inline_add_view.isVisible(); print('past add visible after', after); assert not after"
```

### 4.5 时间 / 提醒 / 清单链路验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from datetime import datetime; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); target=QDate.currentDate().addDays(1); start=datetime(target.year(), target.month(), target.day(), 9, 0); end=datetime(target.year(), target.month(), target.day(), 10, 0); remind=datetime(target.year(), target.month(), target.day(), 8, 50); w.inline_add_view.reset(target); w.on_time_confirmed(start, end); assert w.inline_add_view.selected_start_time == start; assert w.inline_add_view.selected_end_time == end; w.on_alarm_confirmed(remind, True, 1); assert w.inline_add_view.selected_reminder == remind; assert w.inline_add_view.selected_is_alarm_mode is True; assert w.inline_add_view.selected_alarm_duration == 1; w.on_list_confirmed(None); assert w.inline_add_view.selected_list_id is None; print('time/alarm/list callbacks ok')"
```

### 4.6 未设置时间保存拦截验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import InlineAddViewMonth; app=QApplication([]); v=InlineAddViewMonth(); calls=[]; v.saved.connect(lambda: calls.append('saved')); v.reset(QDate.currentDate().addDays(1)); v.input_title.setText('未设时间测试'); v._on_save(); print('saved calls', calls); assert calls == []"
```

### 4.7 完整保存结构 mock 验证

不得真实写库。用 monkeypatch 截获 `db_manager.add_schedule(...)`。

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from datetime import datetime; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import InlineAddViewMonth; from src.data import database; app=QApplication([]); v=InlineAddViewMonth(); target=QDate.currentDate().addDays(1); start=datetime(target.year(), target.month(), target.day(), 9, 0); end=datetime(target.year(), target.month(), target.day(), 10, 0); remind=datetime(target.year(), target.month(), target.day(), 8, 50); v.reset(target); v.input_title.setText('__mock_m5g_month_full_save__'); v.input_desc.setPlainText('mock validation only'); v.set_time_data(start, end); v.set_alarm_data(remind, True, 1); v.set_list_data(12345, 'mock-list'); v.combo_priority.setCurrentIndex(2); v.combo_repeat.setCurrentIndex(0); calls=[]; captured=[]; original=database.db_manager.add_schedule; database.db_manager.add_schedule=lambda data: captured.append(dict(data)) or True; v.saved.connect(lambda: calls.append('saved')); v._on_save(); database.db_manager.add_schedule=original; assert calls == ['saved']; assert len(captured) == 1; data=captured[0]; print('captured', data); assert data['title'] == '__mock_m5g_month_full_save__'; assert data['item_type'] == 'schedule'; assert data['priority'] == 2; assert data['repeat_rule'] == '无'; assert data['description'] == 'mock validation only'; assert data['start_time'] == start; assert data['end_time'] == end; assert data['reminder_time'] == remind; assert data['is_alarm'] is True; assert data['alarm_duration'] == 1; assert data['category_id'] == 12345"
```

### 4.8 重复规则只做静态验证

不得真实保存 `每天 / 每周 / 每月`。

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import InlineAddViewMonth; app=QApplication([]); v=InlineAddViewMonth(); repeats=[v.combo_repeat.itemText(i).strip() for i in range(v.combo_repeat.count())]; print('repeat options', repeats); assert repeats == ['无', '每天', '每周', '每月']"
```

### 4.9 marker / hover / panel smoke 验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); marker_cache, marker_count_cache = w._build_schedule_marker_cache(); hover_cache = w._build_hover_schedule_cache(); print('marker cache types', type(marker_cache).__name__, type(marker_count_cache).__name__); print('hover cache type', type(hover_cache).__name__); assert isinstance(marker_cache, dict); assert isinstance(marker_count_cache, dict); assert isinstance(hover_cache, dict); w._refresh_schedule_marker_cache(); assert isinstance(w.schedule_marker_cache, dict); assert isinstance(w.schedule_marker_count_cache, dict); assert isinstance(w.hover_schedule_cache, dict); w.close_day_panels(); print('marker/hover/panel smoke ok')"
```

### 4.10 保存成功刷新链路 smoke

不得真实写库。只调用刷新入口。

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); w._on_schedule_saved(); print('schedule saved refresh callable ok')"
```

### 4.11 主界面 / 周界面添加页回归检查

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/add_view.py src/ui/add_view_week.py src/ui/main_window.py src/ui/week_window.py
```

### 4.12 schedule.db diff 检查

```powershell
git diff --name-only -- schedule.db
```

预期无输出。

### 4.13 禁止范围检查

```powershell
git diff --name-only -- src
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
manage_instruction/Work_Log.md
manage_instruction/Work_Task_Prompts.md
```

其中 `Work_Task_Prompts.md` 仅在维护本轮复核锚点时允许修改。

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：`M-5g（月界面添加能力整体验收）`
- 开工前 git 状态
- 实际修改文件
- 是否存在开工前既有 diff
- M-5 到 M-5f 完成结论汇总
- 日期来源验收结果
- 过去日期不可添加验收结果
- 时间 picker 链路验收结果
- 提醒 picker 链路验收结果
- 清单 picker 链路验收结果
- 未设置时间保存拦截结果
- 完整保存结构 mock 验收结果
- 重复规则是否仅做静态验证
- marker cache 链路验收结果
- hover cache 链路验收结果
- 持久 panel 关闭链路验收结果
- `_on_schedule_saved(...)` 刷新入口验收结果
- 主界面 / 周界面添加页回归检查结果
- 是否未真实写入重复日程
- 是否未新增 / 删除清单
- `schedule.db` 是否无 tracked diff
- diff 范围检查结果
- 未完成事项
- 风险或疑点
- 是否建议进入 `M-6（月界面右键菜单接入）`

特别记录：

- 本轮只做整体验收。
- 本轮不改源码。
- 本轮不真实写库。
- 本轮不接右键菜单。
- 本轮完成后若通过，可进入 `M-6（月界面右键菜单接入）`。

## 6. Work_Task_Prompts.md 处理要求

如需要维护复核锚点，可将当前状态更新为：

```text
M-5g 已执行，等待决策/顾问窗口复核。
下一步候选：M-6。
```

不得在本轮自行写入 `M-6` 的执行提示词。

## 7. 完成后要求

完成后不要提交 Git，等待决策/顾问窗口复核。
