# Work Task Prompts

用途：保存主窗口审核后的最终执行提示词或当前复核锚点。执行窗口只应执行本文件中的最终版本。

---

# 当前待执行提示词：M-5b

## M-5b：月界面添加表单能力只读审查与 picker 承接方案确认

请执行 `M-5b：月界面添加表单能力只读审查与 picker 承接方案确认`。本轮只做静态审查、代码阅读、搜索、只读数据检查和日志记录，不修改源码，不写数据库，不实现 UI，不接 picker。

## 1. 本轮目标

当前 `M-5（月界面添加按钮日期来源联动）` 已完成，月界面添加按钮已经能优先使用用户选中日期。但 `InlineAddViewMonth` 仍是极简添加壳，不能直接进入 `M-6（月界面右键菜单接入）`。

本轮目标是只读审查月界面添加表单能力，确认后续 `M-5c` 到 `M-5g` 的真实边界：

- 审查 `InlineAddViewMonth` 与主/周添加页字段差异。
- 审查主界面 / 周界面 picker 承接链路。
- 确认月界面 picker 承接方案候选：
  - 月界面内部页面栈。
  - 复用主窗口 picker。
  - 月界面左侧局部切换 picker。
- 确认 picker 返回后如何回填 `InlineAddViewMonth`。
- 确认 picker 打开期间 hover 预览 / 持久 panel 是否需要隐藏。
- 确认时间语义：
  - 默认日期。
  - 是否允许跨天。
  - 未选时间时继续 `00:00` 兼容还是提示必须选择时间。
- 确认提醒依赖时间规则：
  - 未设置 start/end 时是否禁止设置提醒。
  - target_time 使用 start 优先还是 end 优先。
- 确认清单 picker 的 `list_type` 建议。
- 确认月界面是否只支持添加日程，还是也支持待办。
- 确认 `repeat_rule` 的真实入库值、显示值和 `ScheduleRepeatService` 归一化规则。
- 输出 `M-5c` 到 `M-5g` 的精确边界、允许文件、风险等级和验收重点。

本轮不直接修改 `src/`。

## 2. 允许/禁止

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
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

- 不改源码。
- 不改 UI。
- 不接 picker。
- 不新增信号。
- 不新增页面栈。
- 不修改 `InlineAddViewMonth`。
- 不修改主界面 / 周界面添加页。
- 不修改 `TimePickerView` / `AlarmPickerView` / `ListPickerView`。
- 不修改 `ScheduleRepeatService`。
- 不改数据库字段。
- 不写数据库。
- 不提交 Git。
- 不生成 M-5c/M-5d 等源码实现。

若开工前已有 diff，必须在 `Work_Log.md` 中单独记录，并区分是否属于本轮产生。

## 3. 具体任务

### 3.1 读取规划与当前日志

读取：

```powershell
Get-Content -Path manage_instruction\Final_Formulation.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Formulation.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
```

重点确认：

- M-5 后续路线是否已写入。
- M-6 是否已明确后移。
- 当前下一步是否为 M-5b。
- 最终架构约束中对 UI popup、窗口膨胀、功能补充阶段的要求。
- 后续功能开发是否仍应保持渐进式、小工单、低耦合。

### 3.2 读取月界面添加相关源码

读取：

```powershell
Get-Content -Path src\ui\month_window.py -Encoding UTF8
```

重点审查：

- `InlineAddViewMonth` 当前字段、按钮和保存逻辑。
- `InlineAddViewMonth.reset(target_date)` 当前行为。
- `InlineAddViewMonth._on_save(...)` 当前写入字段。
- `MonthWindow._get_add_target_date(...)` 当前日期来源。
- `MonthWindow._on_add_clicked(...)` 当前添加入口。
- `MonthWindow._on_schedule_saved(...)` 当前刷新链路。
- hover 预览和持久 panel 当前缓存是否与添加保存后刷新相关。

必须输出：

- 当前月添加表单已有字段。
- 当前月添加表单缺失字段。
- 当前保存字段与主/周添加页的差异。
- 当前保存后刷新是否覆盖 marker、hover cache、持久 panel。

### 3.3 读取主界面和周界面添加页

读取：

```powershell
Get-Content -Path src\ui\add_view.py -Encoding UTF8
Get-Content -Path src\ui\add_view_week.py -Encoding UTF8
```

重点审查：

- 主界面 `AddScheduleView`：
  - 字段状态。
  - 信号。
  - picker 请求方式。
  - 回填方法。
  - `_on_save(...)` 写入字段。
  - 时间/提醒/清单/紧急性/重复规则逻辑。
- 周界面 `AddScheduleViewWeek`：
  - 与主界面差异。
  - 是否更适合月界面竖向布局参考。
  - picker 请求和回填方式。
  - `_on_save(...)` 写入字段。

必须输出：

- `InlineAddViewMonth` 与 `AddScheduleView` 字段差异表。
- `InlineAddViewMonth` 与 `AddScheduleViewWeek` 字段差异表。
- 哪些业务语义应复用。
- 哪些 UI 结构不应复制。
- 月界面更适合参考主界面还是周界面，或二者混合。

### 3.4 读取 picker 和承接链路

读取：

```powershell
Get-Content -Path src\ui\time_picker.py -Encoding UTF8
Get-Content -Path src\ui\time_picker_week.py -Encoding UTF8
Get-Content -Path src\ui\alarm_picker.py -Encoding UTF8
Get-Content -Path src\ui\alarm_picker_week.py -Encoding UTF8
Get-Content -Path src\ui\list_picker.py -Encoding UTF8
Get-Content -Path src\ui\main_window.py -Encoding UTF8
Get-Content -Path src\ui\week_window.py -Encoding UTF8
```

重点审查：

- 主界面 picker 承接：
  - `req_open_time_picker`
  - `req_open_alarm_picker`
  - `req_open_list_picker`
  - `go_to_time_picker`
  - `go_to_alarm_picker`
  - `go_to_list_picker`
  - `set_time_data`
  - `set_alarm_data`
  - `set_list_data`
- 周界面 picker 承接：
  - 是否自带 `page_time`、`page_alarm`、`page_list`。
  - 是否使用 week 专用 picker。
  - 回填方式。
- picker 本身：
  - `TimePickerView` / `TimePickerViewWeek` 的确认信号。
  - `AlarmPickerView` / `AlarmPickerViewWeek` 的确认信号。
  - `ListPickerView.load_data(current_selected_id, list_type)` 行为。
  - `ListPickerView.confirm_requested` 参数。

必须输出：

- 月界面 picker 承接的 3 个候选方案。
- 每个方案的优点、风险、预计修改文件。
- 推荐方案。
- M-5d/M-5e 应采用哪个方案。
- picker 打开时是否隐藏 hover 预览。
- picker 打开时是否关闭或保留持久 panel。
- picker 返回后如何回到 `InlineAddViewMonth`。

### 3.5 审查时间语义

只读判断：

- 当前主界面日程模式是否要求时间。
- 当前周界面日程模式是否要求时间。
- 当前月界面是否仍使用 `00:00` 兜底。
- 月界面后续是否应：
  - 沿用主/周“必须设置时间”的语义；
  - 还是暂时保留 `00:00` 兼容；
  - 或先 UI 壳阶段不改变保存语义，到 M-5d 再处理。
- 打开时间 picker 时默认日期应如何传入：
  - 使用 `_get_add_target_date()`。
  - 使用 `user_selected_date`。
  - 使用 `calendar.selectedDate()` fallback。
- 是否允许跨天 start/end。
- 如果不允许跨天，应在哪里限制或提示。

必须输出：

- 推荐时间语义。
- M-5d 需要实现的最小边界。
- M-5d 不应碰的逻辑。

### 3.6 审查提醒语义

只读判断：

- 主界面未设置时间时如何处理提醒按钮。
- 周界面未设置时间时如何处理提醒按钮。
- target_time 使用 start 优先还是 end 优先。
- 保存字段：
  - `reminder_time`
  - `is_alarm`
  - `alarm_duration`
- 月界面后续如何复用该语义。

必须输出：

- M-5e 提醒接入边界。
- 未设置时间时是否禁用提醒或 toast 提示。
- 提醒 picker 回填字段。
- 不应修改 picker 内部逻辑。

### 3.7 审查清单语义

只读判断：

- 主界面清单 picker 是否传 `list_type`。
- 周界面清单 picker 是否传 `list_type`。
- `ListPickerView.load_data(current_selected_id, list_type)` 如何过滤。
- 月界面是否只支持日程。
- 如果只支持日程，是否应传 `list_type="schedule"`。
- 是否有待办模式需求，是否应推迟。

必须输出：

- M-5e 清单接入边界。
- 推荐 `list_type`。
- 是否允许待办模式。
- 保存字段是否仍为 `category_id`。

### 3.8 审查紧急性与重复规则

读取或搜索：

```powershell
Get-Content -Path src\services\schedule_repeat_service.py -Encoding UTF8
rg -n "repeat_rule|REPEAT|NON_REPEAT|每天|每周|每月|每年|none|daily|weekly|monthly|yearly|ScheduleRepeatService" src manage_instruction
```

只读数据检查允许执行：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; vals=sorted({(getattr(s,'repeat_rule',None) or '') for s in db_manager.get_all_schedules()}); print('repeat_rule values:', vals)"
```

如果只读数据检查因环境、权限或数据库状态失败，不要改源码，不要改数据库；记录失败原因，并继续用静态代码结果形成保守结论。

重点确认：

- `ScheduleRepeatService` 当前支持哪些规则。
- 当前数据库中真实 `repeat_rule` 值有哪些。
- 主/周添加页 combo 显示值是什么。
- `InlineAddViewMonth` 当前默认写入什么值。
- 是否存在历史默认值 `none`。
- 后续是否应先做显示值 -> 入库值归一化。
- 不得新增新重复规则。
- 不得改重复日程生成逻辑。

必须输出：

- 当前真实 repeat_rule 值。
- 当前显示值。
- 当前服务归一化规则。
- M-5f 应使用的规则体系建议。
- M-5f 禁止触碰的重复生成逻辑边界。

### 3.9 输出小工单边界

在 `Work_Log.md` 中输出：

#### M-5c：UI 壳补齐

必须写明：

- 建议修改文件。
- 允许做什么 UI。
- 哪些按钮可禁用或 toast。
- 不得打开 picker。
- 不得写入状态。
- 不得改 `_on_save(...)`。
- 验收重点。

#### M-5d：时间选择接入

必须写明：

- 建议修改文件。
- picker 承接方案。
- 默认日期来源。
- start/end 回填方式。
- 未选时间行为。
- 是否允许跨天。
- 不接提醒/清单/重复。
- 验收重点。

#### M-5e：提醒与清单接入

必须写明：

- 建议修改文件。
- 提醒依赖时间规则。
- reminder 字段回填。
- list picker 的 `list_type`。
- `category_id` 保存语义。
- 不改 picker 内部。
- 验收重点。

#### M-5f：紧急性 / 重复规则 / 保存结构对齐

必须写明：

- 建议修改文件。
- priority 控件与保存语义。
- repeat_rule 显示值、入库值、归一化建议。
- 保存字段对齐清单。
- 保存后刷新 marker、hover cache、持久 panel 的策略。
- 不改重复生成逻辑。
- 验收重点。

#### M-5g：整体验收

必须写明：

- 需要复跑的用户路径。
- 临时数据验证策略。
- 如何清理临时数据。
- `schedule.db` 最终无 tracked diff。
- 主/周添加页回归检查。
- 月界面单击、双击、hover、持久 panel 回归检查。

## 4. 验收命令

开工状态：

```powershell
git status --short --branch
git diff --name-only
```

静态搜索 picker 链路：

```powershell
rg -n "req_open_time_picker|req_open_alarm_picker|req_open_list_picker|go_to_time_picker|go_to_alarm_picker|go_to_list_picker|set_time_data|set_alarm_data|set_list_data|TimePickerView|TimePickerViewWeek|AlarmPickerView|AlarmPickerViewWeek|ListPickerView|confirm_requested|load_data" src/ui/month_window.py src/ui/add_view.py src/ui/add_view_week.py src/ui/main_window.py src/ui/week_window.py src/ui/time_picker.py src/ui/time_picker_week.py src/ui/alarm_picker.py src/ui/alarm_picker_week.py src/ui/list_picker.py
```

静态搜索保存字段：

```powershell
rg -n "schedule_data|title|item_type|priority|repeat_rule|description|start_time|end_time|reminder_time|is_alarm|alarm_duration|category_id|db_manager\\.add_schedule|_on_save|_on_add_clicked|_get_add_target_date" src/ui/month_window.py src/ui/add_view.py src/ui/add_view_week.py
```

静态搜索重复规则：

```powershell
rg -n "repeat_rule|REPEAT|NON_REPEAT|每天|每周|每月|每年|none|daily|weekly|monthly|yearly|ScheduleRepeatService" src manage_instruction
```

只读 repeat_rule 数据检查：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; vals=sorted({(getattr(s,'repeat_rule',None) or '') for s in db_manager.get_all_schedules()}); print('repeat_rule values:', vals)"
```

import 验证：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.month_window import MonthWindow, InlineAddViewMonth; from src.ui.add_view import AddScheduleView; from src.ui.add_view_week import AddScheduleViewWeek; from src.ui.time_picker import TimePickerView; from src.ui.alarm_picker import AlarmPickerView; from src.ui.list_picker import ListPickerView; from src.services.schedule_repeat_service import ScheduleRepeatService; print('m5b imports ok')"
```

禁止范围检查：

```powershell
git diff --name-only -- src
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
git diff --name-only
git status --short --branch
```

预期：

- `src` 无 diff。
- `assets` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- `Final_Formulation.md` 无 diff。
- `Work_Formulation.md` 无 diff。
- `Work_Instruction.md` 无 diff。
- `Work_Snapshot.md` 无 diff。
- `History_Instruction.md` 无 diff。
- `History_Log.md` 无 diff。
- `ReconstructionDolder/` 无 diff。
- 最终只允许：
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：`M-5b（月界面添加表单能力只读审查与 picker 承接方案确认）`
- 开工前 git 状态。
- 开工前既有 diff。
- 实际修改文件。
- 读取的规划文件。
- 读取的源码文件。
- `InlineAddViewMonth` 当前能力清单。
- `InlineAddViewMonth` 与主/周添加页字段差异。
- 当前 picker 承接链路审查结果。
- 推荐的月界面 picker 承接方案。
- picker 返回后回填方案。
- picker 打开期间 hover 预览 / 持久 panel 处理建议。
- 时间语义建议。
- 提醒依赖时间规则。
- 清单 `list_type` 建议。
- 月界面是否只支持日程的建议。
- `repeat_rule` 真实入库值、显示值和 `ScheduleRepeatService` 归一化规则。
- M-5c 到 M-5g 的建议修改文件、风险等级、验收重点。
- diff 范围检查结果。
- 未完成事项。
- 风险或疑点。

完成后不要提交 Git，等待决策/顾问窗口复核。
