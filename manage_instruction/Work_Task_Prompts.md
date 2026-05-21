# Work Task Prompts

## 第五轮 5-2 提示词（运行期去重状态抽取）

### 1. 本轮目标

- 本工单为实现工单：在 `ReminderService` 中补充本次运行内的提醒去重状态能力。
- 只处理运行期内存状态，不接入 `MainWindow`。
- 不修改任何 `src/ui/*` 文件。
- 不改变现有提醒弹窗、声音播放、QTimer 扫描、数据库结构和提醒触发窗口。
- 保持 5-1 已实现的纯判断语义不变，尤其是 `should_trigger(schedule, now)` 不得写入去重状态。

### 2. 允许/禁止

- 允许修改：`src/services/reminder_service.py`
- 必要时允许修改：`src/services/__init__.py`
- 允许更新：`manage_instruction/Work_Log.md`
- 禁止修改：`src/ui/*`
- 禁止修改：`main.py`
- 禁止修改：`requirements.txt`
- 禁止修改：`schedule.db`
- 禁止修改本提示词文件 `manage_instruction/Work_Task_Prompts.md`；如发现提示词问题，只能在 `Work_Log.md` 记录并交回顾问/决策窗口处理。
- 禁止新增依赖。
- 禁止接入 `MainWindow`。
- 禁止迁移 `QTimer`。
- 禁止迁移 `winsound.PlaySound(...)`。
- 禁止创建或修改 `ReminderPop`。
- 禁止新增提醒持久化字段、表或数据库迁移。
- 禁止生成完整弹窗 dict，完整 dict 构造留到 5-4。
- service 不得依赖 `QWidget`、`QTimer`、`winsound`、`ReminderPop`、`db_manager`。

### 3. 具体任务

- 在 `ReminderService` 中增加本次运行内去重状态容器，建议使用实例级 `set` 保存已触发 schedule id。
- 顺手修正 `get_reminder_diff_seconds` 的 docstring，把 `.seconds` 改为 `total_seconds()`，不得改变函数行为。
- 增加或完善以下能力，命名可略作调整，但语义必须清楚：
  - `is_triggered(schedule_id)`：判断指定 id 是否已在本 service 实例中标记触发。
  - `mark_triggered(schedule_id)`：显式标记指定 id 已触发。
  - `collect_due_schedules(schedules, now)`：批量筛选当前应触发且尚未标记的日程列表。
- 去重 key 必须与旧逻辑一致，使用 `schedule.id`；轻量假对象验证时也必须提供 `id` 字段，不得改用 title、reminder_time 或其它组合 key。
- `collect_due_schedules(schedules, now)` 不得隐式调用 `mark_triggered`，不得写入已触发状态。
- `should_trigger(schedule, now)` 仍只判断提醒时间条件，不得考虑去重状态，不得写入状态。
- 如需要辅助读取 schedule id，可新增纯辅助方法，但不得依赖 Peewee 类型。
- 对没有 `reminder_time` 的对象，不得触发。
- 对未到提醒时间或超过 60 秒窗口的对象，不得触发。
- 对已调用 `mark_triggered(id)` 的对象，`collect_due_schedules` 不应再返回该对象。
- 新建 `ReminderService()` 实例时，去重状态必须为空，用于保持“应用重启后去重状态不持久化”的旧行为。

### 4. 验收命令

- 开工前记录：`git status --short`
- 实现后优先执行：`.\.venv\Scripts\python.exe -m py_compile src/services/reminder_service.py`
- 执行 service import 验证：`.\.venv\Scripts\python.exe -c "from src.services.reminder_service import ReminderService; print('reminder service import ok')"`
- 若顾问窗口或 Codex 工具环境运行 `.venv` 报 `Unable to create process`，但用户本机 CMD 中 `.venv` 验证通过，可在日志中说明，并使用 bundled Python 复验作为补充依据。
- 执行轻量假对象验证，至少覆盖：
  - 无提醒：`collect_due_schedules` 不返回。
  - 未到提醒时间：`collect_due_schedules` 不返回。
  - 到点且处于 60 秒窗口内：`collect_due_schedules` 返回。
  - 超过 60 秒窗口：`collect_due_schedules` 不返回。
  - 已调用 `mark_triggered(id)` 后：同 id 不再由 `collect_due_schedules` 返回。
  - `collect_due_schedules` 本身不隐式标记；同一个未标记对象连续 collect 两次仍应返回。
  - 新建另一个 `ReminderService()` 实例后，去重状态为空。
  - `should_trigger(schedule, now)` 在 `mark_triggered(id)` 后仍保持纯判断语义，不因去重状态变成 False。
- 执行静态依赖检查：`rg -n "QWidget|QTimer|winsound|ReminderPop|db_manager|src\.ui|PyQt|PySide" src/services/reminder_service.py`
- 静态依赖检查期望无输出；`rg` 无匹配时可能返回退出码 1，此时只要确认为“无输出/无匹配”即视为通过。
- 收尾检查：
  - `git status --short`
  - `git diff --name-only -- src/ui`
  - `git diff --name-only -- main.py requirements.txt schedule.db`

验收标准：

- `src/services/reminder_service.py` 可 import。
- `src/services/reminder_service.py` 可 py_compile。
- 假对象验证通过。
- 静态检索确认无 UI/db/sound 依赖。
- `should_trigger` 仍为无状态纯判断。
- `collect_due_schedules` 不隐式标记。
- 新 service 实例去重状态为空。
- `src/ui` 无 diff。
- `main.py`、`requirements.txt`、`schedule.db` 无由本工单产生的新 diff。

### 5. 日志要求

- 在 `manage_instruction/Work_Log.md` 新增 `5-2` 记录，至少包含：
  - 本轮任务名与边界。
  - 开工前 git 状态基线。
  - 实际新增/修改文件。
  - `ReminderService` 新增的运行期去重方法清单。
  - 明确记录本轮未做事项：
    - 未接入 `MainWindow`。
    - 未修改 `src/ui/*`。
    - 未生成完整弹窗 dict。
    - 未迁移声音播放。
    - 未新增提醒持久化。
  - 假对象验证结果。
  - py_compile / import / 静态依赖检查结果。
  - diff 范围检查结果。
  - 风险与后续建议，供 5-3 使用。
  - 特别记录：本工单完成后不要提交 Git，等待顾问窗口审核。

### 6. 提交要求

- 执行窗口不得提交 Git。
- 本工单完成后等待顾问窗口审核。
- Git 提交只能由用户在顾问验收后执行。