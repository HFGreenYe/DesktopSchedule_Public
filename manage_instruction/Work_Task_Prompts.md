# Work Task Prompts

## 第五轮 5-5 提示词（提醒服务轻量回归验收）

### 1. 本轮目标

- 本工单为验收工单：对第五轮 5-1 到 5-4 的提醒服务改造做轻量回归验收。
- 原则上不改源码，只做验证、静态检查、行为边界复核和日志记录。
- 重点确认 `ReminderService`、`MainWindow.check_reminders()`、`MainWindow.show_reminder_popup()` 的当前边界符合第五轮合同。
- 如果发现必须修正的问题，不得自行扩大修复范围；先记录到 `Work_Log.md` 并交回顾问/决策窗口确认。

### 2. 允许/禁止

- 允许读取：`src/services/reminder_service.py`
- 允许读取：`src/ui/main_window.py`
- 允许读取：`src/ui/reminder_pop.py`
- 允许读取：`main.py`
- 允许更新：`manage_instruction/Work_Log.md`
- 禁止修改：`src/services/reminder_service.py`
- 禁止修改：`src/ui/*`
- 禁止修改：`main.py`
- 禁止修改：`requirements.txt`
- 禁止修改：`schedule.db`
- 禁止修改本提示词文件 `manage_instruction/Work_Task_Prompts.md`；如发现提示词问题，只能在 `Work_Log.md` 记录并交回顾问/决策窗口处理。
- 禁止新增依赖。
- 禁止提交 Git。
- 禁止做功能修复、代码重构、格式化或顺手清理。
- 禁止迁移 `QTimer`、`winsound.PlaySound(...)`、`ReminderPop` 或数据库访问边界。
- 禁止新增提醒持久化字段、表或数据库迁移。

### 3. 具体任务

- 开工前先记录 `git status --short`。
- 正常情况下，开工前不应存在源码、`main.py`、`requirements.txt`、`schedule.db` 的 diff。
- 若开工前存在 `manage_instruction/Work_Task_Prompts.md` diff，应标记为“既有提示词 diff”，不得算作 5-5 新增改动。
- 若开工前存在 5-4 遗留源码 diff，必须先停止并在 `Work_Log.md` 记录，不得继续执行 5-5 验收。
- 对 `ReminderService` 做回归确认：
  - `has_reminder_time(schedule)` 无提醒时返回 False。
  - `get_reminder_diff_seconds(schedule, now)` 使用 `total_seconds()` 语义。
  - `is_in_trigger_window(diff)` 保持 `0 <= diff < 60`。
  - `should_trigger(schedule, now)` 保持无状态纯判断，不受去重状态影响。
  - `collect_due_schedules(schedules, now)` 不隐式标记。
  - `mark_triggered(id)` 后同 id 不再由 `collect_due_schedules` 返回。
  - 新 `ReminderService()` 实例去重状态为空。
  - `select_target_time(schedule)` 仍优先 `start_time`，否则 `end_time`，都无则 `None`。
  - `build_reminder_popup_data(schedule)` 只返回 `title`、`is_alarm`、`target_time` 三个 key，字段值保持旧语义。
- 对 `MainWindow` 做静态复核：
  - `_init_scheduler()` 仍创建 QTimer，并保持 `start(1000)`。
  - `_init_scheduler()` 创建 `self.reminder_service = ReminderService()`。
  - `check_reminders()` 数据来源仍为 `db_manager.get_all_schedules()`。
  - `check_reminders()` 顺序仍为 `collect_due_schedules` -> `show_reminder_popup(s)` -> `mark_triggered(s.id)`。
  - `show_reminder_popup()` 仍负责创建 `ReminderPop(data_dict)`、`show()` 和 `winsound.PlaySound(...)`。
  - `show_reminder_popup()` 的声音播放条件仍基于 `schedule_data.is_alarm`。
- 对 UI/副作用边界做确认：
  - `src/ui/reminder_pop.py` 无 diff。
  - `winsound.PlaySound(...)` 未迁移到 service。
  - `ReminderPop` 未迁移到 service。
  - `QTimer` 未迁移到 service。
  - `db_manager` 未被 service 依赖。
  - `schedule.db` 无 diff。

### 4. 验收命令

- 开工前记录：
  - `git status --short`
- 优先执行：
  - `.\.venv\Scripts\python.exe -m py_compile src/services/reminder_service.py src/ui/main_window.py`
  - `.\.venv\Scripts\python.exe -c "from src.services.reminder_service import ReminderService; print('reminder service import ok')"`
- 若 `.venv` 在工具环境报 `Unable to create process`，允许使用 bundled Python 复验并在日志留痕。
- 执行轻量假对象验证，至少覆盖：
  - 无提醒不触发。
  - 未到提醒时间不触发。
  - 到点且处于 60 秒窗口内触发。
  - 超过 60 秒窗口不触发。
  - `collect_due_schedules` 不隐式标记。
  - `mark_triggered` 后过滤同 id。
  - 新 service 实例状态为空。
  - `should_trigger` 不受去重状态影响。
  - `select_target_time` 的三种情况：有 `start_time`、仅有 `end_time`、二者都无。
  - `build_reminder_popup_data` 的 key 精确等于 `title`、`is_alarm`、`target_time`。
- 执行静态依赖检查：
  - `rg -n "QWidget|QTimer|winsound|ReminderPop|db_manager|src\.ui|PyQt|PySide" src/services/reminder_service.py`
  - 期望无输出；`rg` 无匹配返回码 1 视为通过。
- 执行 MainWindow 静态检查：
  - `rg -n "triggered_reminders" src/ui/main_window.py`
  - 期望无输出。
  - `rg -n "collect_due_schedules|show_reminder_popup\(s\)|mark_triggered|build_reminder_popup_data|ReminderPop|PlaySound" src/ui/main_window.py src/services/reminder_service.py`
  - 用输出确认边界和顺序。
- 执行 diff 范围检查：
  - `git diff --name-only -- src/ui`
  - 期望无输出；如开工前已有遗留 diff，应已在开工前停止。
  - `git diff --name-only -- src/services/reminder_service.py`
  - 期望无输出。
  - `git diff --name-only -- main.py requirements.txt schedule.db`
  - 期望无输出。
  - `git status --short`

验收标准：

- `py_compile` 通过。
- `ReminderService` import 通过。
- 轻量假对象验证通过。
- service 静态依赖检查无 UI/db/sound 依赖。
- `MainWindow` 中不再出现 `triggered_reminders`。
- `check_reminders()` 顺序仍是 `collect -> show -> mark`。
- `show_reminder_popup()` 仍保留弹窗和声音副作用边界。
- `build_reminder_popup_data()` 字段和值与旧内联 dict 构造一致。
- `src/ui/reminder_pop.py` 无 diff。
- `main.py`、`requirements.txt`、`schedule.db` 无 diff。
- 本工单不产生源码新 diff；若只有 `Work_Log.md` 追加验收记录，视为符合预期。

### 5. 日志要求

- 在 `manage_instruction/Work_Log.md` 新增 `5-5` 记录，至少包含：
  - 本轮任务名与边界。
  - 开工前 git 状态基线，并明确哪些 diff 是既有提示词 diff。
  - 实际修改文件，原则上只能是 `manage_instruction/Work_Log.md`。
  - `ReminderService` 回归验证结果。
  - `MainWindow` 静态边界复核结果。
  - UI/声音/数据库副作用边界复核结果。
  - py_compile / import / 假对象验证 / 静态依赖检查结果。
  - diff 范围检查结果。
  - 风险与后续建议，供 5-6 使用。
  - 特别记录：本工单完成后不要提交 Git，等待顾问窗口审核。

### 6. 提交要求

- 执行窗口不得提交 Git。
- 本工单完成后等待顾问窗口审核。
- Git 提交只能由用户在顾问验收后执行。