# Work Task Prompts

## 第五轮 5-3 提示词（MainWindow 提醒扫描最小委托）

### 1. 本轮目标

- 本工单为实现工单：让 `MainWindow.check_reminders()` 最小委托 `ReminderService` 完成提醒触发筛选与本次运行内去重判断。
- 只接入提醒扫描路径，不改提醒弹窗 UI，不改声音播放，不改提醒选择页。
- 保留 `MainWindow._init_scheduler()` 创建 QTimer 的职责。
- 保留 `db_manager.get_all_schedules()` 作为提醒扫描数据来源。
- 保留 `MainWindow.show_reminder_popup(schedule)` 作为弹窗与声音副作用入口。
- 保持提醒触发窗口 `0 <= now - reminder_time < 60` 不变。

### 2. 允许/禁止

- 允许修改：`src/ui/main_window.py`
- 允许读取：`src/services/reminder_service.py`
- 必要时允许修改：`src/services/reminder_service.py`，但只限发现接入所需的小兼容修正，不得改变 5-1/5-2 既定语义。
- 允许更新：`manage_instruction/Work_Log.md`
- 禁止修改：`src/ui/reminder_pop.py`
- 禁止修改：除 `src/ui/main_window.py` 以外的任何 `src/ui/*`
- 禁止修改：`main.py`
- 禁止修改：`requirements.txt`
- 禁止修改：`schedule.db`
- 禁止修改本提示词文件 `manage_instruction/Work_Task_Prompts.md`；如发现提示词问题，只能在 `Work_Log.md` 记录并交回顾问/决策窗口处理。
- 禁止新增依赖。
- 禁止迁移 `QTimer` 到 service。
- 禁止迁移 `winsound.PlaySound(...)` 到 service。
- 禁止创建或修改 `ReminderPop`。
- 禁止新增提醒持久化字段、表或数据库迁移。
- 禁止生成完整弹窗 dict，完整 dict 构造留到 5-4。
- 禁止修改 `show_reminder_popup` 的弹窗数据字段和值。
- 禁止改变 `db_manager` 对外 API。

### 3. 具体任务

- 在 `src/ui/main_window.py` 中引入 `ReminderService`。
- 在 `_init_scheduler()` 中创建 `self.reminder_service = ReminderService()`，用于替代裸 `triggered_reminders` 细节。
- 保留 `self.reminder_timer = QTimer(self)`、`timeout.connect(self.check_reminders)`、`start(1000)` 的旧行为。
- 将 `check_reminders()` 改为：
  - 获取 `now = datetime.now()`。
  - 继续使用 `db_manager.get_all_schedules()` 拉取扫描数据。
  - 使用 `self.reminder_service.collect_due_schedules(schedules, now)` 获取应触发日程。
  - 对每个 due schedule 调用 `self.show_reminder_popup(s)`。
  - 在 `self.show_reminder_popup(s)` 成功调用后，再显式调用 `self.reminder_service.mark_triggered(s.id)`。
- `mark_triggered` 的调用顺序必须保持在弹窗触发调用之后，避免弹窗创建失败却提前标记。
- 如果为了保护扫描循环而添加异常处理，`mark_triggered` 必须只放在 `show_reminder_popup(s)` 成功后的路径，不得放在 `finally` 中。
- 打印日志可保持等价，若需要延迟秒数，可用 `ReminderService.get_reminder_diff_seconds(s, now)` 计算；不得改变核心行为。
- `show_reminder_popup(schedule_data)` 本轮原则上不改；如仅为 import/格式化产生无行为差异调整，必须在日志中说明。
- 不再在 `MainWindow` 中直接维护或判断裸 `triggered_reminders` set；如为了兼容暂时保留属性，必须说明原因，且不得继续由 `MainWindow` 直接操作去重 set。

### 4. 验收命令

- 开工前记录：`git status --short`
- 实现后优先执行：
  - `.\.venv\Scripts\python.exe -m py_compile src/services/reminder_service.py src/ui/main_window.py`
  - `.\.venv\Scripts\python.exe -c "from src.services.reminder_service import ReminderService; print('reminder service import ok')"`
- 若顾问窗口或 Codex 工具环境运行 `.venv` 报 `Unable to create process`，但用户本机 CMD 中 `.venv` 验证通过，可在日志中说明，并使用 bundled Python 复验作为补充依据。
- 执行静态检查：
  - `rg -n "triggered_reminders" src/ui/main_window.py`
  - 期望无输出；若仍有输出，必须说明为什么保留且不违反本轮目标。
  - `rg -n "winsound|ReminderPop|show_reminder_popup|PlaySound" src/services/reminder_service.py`
  - 期望无输出，确认 service 没有吸收 UI/声音副作用。
- 执行源码范围检查：
  - `git diff --name-only -- src/ui`
  - 期望只出现 `src/ui/main_window.py`，不得出现 `src/ui/reminder_pop.py` 或其他 UI 文件。
  - `git diff --name-only -- main.py requirements.txt schedule.db`
  - 期望无输出。
- 建议执行轻量行为验证：
  - 用静态阅读或小型 monkeypatch 说明 `check_reminders()` 的顺序是：collect due -> show popup -> mark triggered。
  - 验证 `ReminderService.collect_due_schedules` 不隐式标记的语义没有被改坏。
  - 验证 `ReminderService.should_trigger` 仍不受去重状态影响。

验收标准：

- `MainWindow` 创建并持有 `ReminderService`。
- `QTimer` 仍由 `MainWindow` 创建并每 1000ms 调用 `check_reminders`。
- 扫描数据来源仍为 `db_manager.get_all_schedules()`。
- 到点后仍调用原 `show_reminder_popup(s)`。
- 弹窗触发调用后才显式 `mark_triggered(s.id)`。
- 同一 id 本次运行内不会重复触发。
- `show_reminder_popup` 弹窗和声音行为不变。
- `src/services/reminder_service.py` 不依赖 UI、声音、db_manager。
- `src/ui/reminder_pop.py` 无 diff。
- `src/ui` diff 除 `main_window.py` 外无其它文件。
- `main.py`、`requirements.txt`、`schedule.db` 无由本工单产生的新 diff。

### 5. 日志要求

- 在 `manage_instruction/Work_Log.md` 新增 `5-3` 记录，至少包含：
  - 本轮任务名与边界。
  - 开工前 git 状态基线。
  - 实际新增/修改文件。
  - `MainWindow` 接入 `ReminderService` 的位置说明。
  - `check_reminders()` 新扫描流程摘要。
  - 明确记录本轮未做事项：
    - 未修改 `ReminderPop`。
    - 未修改提醒选择页。
    - 未迁移声音播放。
    - 未迁移 QTimer。
    - 未生成完整弹窗 dict。
    - 未新增提醒持久化。
  - py_compile / import / 静态检查结果。
  - diff 范围检查结果。
  - 风险与后续建议，供 5-4 使用。
  - 特别记录：本工单完成后不要提交 Git，等待顾问窗口审核。

### 6. 提交要求

- 执行窗口不得提交 Git。
- 本工单完成后等待顾问窗口审核。
- Git 提交只能由用户在顾问验收后执行。