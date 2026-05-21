# Work Task Prompts

## 第五轮 5-6 提示词（第五轮整体验收与归档准备）

### 1. 本轮目标

- 本工单为整体验收工单：汇总并复核第五轮 5-0 到 5-5 的提醒服务改造结果。
- 原则上不改源码，只做最终验收、范围复核、日志收口和归档准备结论。
- 重点确认第五轮目标已经达成：提醒扫描逻辑已最小委托到 `ReminderService`，UI 弹窗、声音播放、QTimer、数据库行为保持原位。
- 本工单只确认“第五轮可归档”，不实际搬迁日志、不更新历史归档文件、不直接开启第六轮 Controller / Router / EventBus 改造。
- 如果发现必须修正的问题，不得自行扩大修复范围；先记录到 `Work_Log.md` 并交回顾问/决策窗口确认。

### 2. 允许/禁止

- 允许读取：`manage_instruction/Work_Instruction.md`
- 允许读取：`manage_instruction/Work_Formulation.md`
- 允许读取：`manage_instruction/Work_Task_Prompts.md`
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
- 禁止修改：`manage_instruction/Work_Task_Prompts.md`
- 禁止修改：除 `manage_instruction/Work_Log.md` 以外的任何 `manage_instruction/*` 文件。
- 如发现提示词或阶段文档问题，只能在 `Work_Log.md` 记录并交回顾问/决策窗口处理。
- 禁止新增依赖。
- 禁止提交 Git。
- 禁止做功能修复、代码重构、格式化或顺手清理。
- 禁止迁移 `QTimer`、`winsound.PlaySound(...)`、`ReminderPop` 或数据库访问边界。
- 禁止新增提醒持久化字段、表或数据库迁移。
- 禁止实际执行归档搬迁，例如修改 `History_Log.md`、`History_Instruction.md` 或清空当前阶段文档。
- 禁止开启第六轮改造。

### 3. 具体任务

- 开工前记录：`git status --short`
- 若开工前存在 `manage_instruction/Work_Task_Prompts.md` diff，应标记为“既有提示词 diff”，不得算作 5-6 新增改动。
- 若开工前存在源码、`main.py`、`requirements.txt`、`schedule.db` diff，必须先停止并在 `Work_Log.md` 记录，不得继续执行 5-6 整体验收。
- 汇总第五轮完成情况：
  - `5-0`：静态审查与只读基线定位。
  - `5-1`：ReminderService 骨架与纯判断函数。
  - `5-2`：运行期去重状态抽取。
  - `5-3`：MainWindow 提醒扫描最小委托。
  - `5-4`：提醒弹窗数据构造边界收口。
  - `5-5`：提醒服务轻量回归验收。
- 复核 `ReminderService` 最终职责：
  - 纯提醒时间判断。
  - 触发窗口判断：`0 <= diff < 60`。
  - 本次运行内去重状态。
  - 到期候选筛选。
  - `target_time` 选择。
  - 弹窗 dict 纯构造。
- 复核 `ReminderService` 禁止边界：
  - 不依赖 UI。
  - 不依赖 `winsound`。
  - 不依赖 `ReminderPop`。
  - 不依赖 `QTimer`。
  - 不依赖 `db_manager`。
  - 不写数据库。
- 复核 `MainWindow` 最终职责：
  - 仍创建 QTimer。
  - 仍每 1000ms 扫描。
  - 仍通过 `db_manager.get_all_schedules()` 取数据。
  - 仍调用 `show_reminder_popup(s)`。
  - 仍在弹窗调用后 `mark_triggered(s.id)`。
  - 仍保留 `ReminderPop` 创建、显示和声音播放。
- 复核旧行为保持：
  - 无 `reminder_time` 不触发。
  - 未到提醒时间不触发。
  - 超过 60 秒窗口不补弹。
  - 到点且在 60 秒窗口内触发。
  - 同一日程 ID 本次运行内不重复触发。
  - 新应用进程/新 service 实例去重状态为空。
  - `target_time` 仍优先 `start_time`，否则 `end_time`。
  - 弹窗 dict 仍只有 `title`、`is_alarm`、`target_time`。
  - 强提醒声音仍由 UI 层播放。
  - 关闭弹窗/停止闹钟逻辑仍在 `ReminderPop`。
- 确认未做事项：
  - 未修改 `ReminderPop`。
  - 未修改提醒选择页。
  - 未修改数据库模型。
  - 未新增数据库字段。
  - 未新增提醒持久化。
  - 未修改 `db_manager` 对外 API。
  - 未修改 `main.py`。
  - 未修改 `requirements.txt`。
  - 未处理第六轮 Controller / Router / EventBus。

### 4. 验收命令

- 开工前记录：
  - `git status --short`
- 优先执行：
  - `.\.venv\Scripts\python.exe -m py_compile main.py src/services/reminder_service.py src/ui/main_window.py src/ui/reminder_pop.py`
  - `.\.venv\Scripts\python.exe -c "from src.services.reminder_service import ReminderService; print('reminder service import ok')"`
- 若 `.venv` 在工具环境报 `Unable to create process`，允许使用 bundled Python 复验并在日志留痕。
- 执行轻量假对象整体验证，至少覆盖：
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
- 执行 service 静态依赖检查：
  - `rg -n "QWidget|QTimer|winsound|ReminderPop|db_manager|src\.ui|PyQt|PySide" src/services/reminder_service.py`
  - 期望无输出；`rg` 无匹配返回码 1 视为通过。
- 执行 MainWindow 静态检查：
  - `rg -n "triggered_reminders" src/ui/main_window.py`
  - 期望无输出。
  - `rg -n "collect_due_schedules|show_reminder_popup\(s\)|mark_triggered|build_reminder_popup_data|ReminderPop|PlaySound|get_all_schedules|start\(1000\)" src/ui/main_window.py src/services/reminder_service.py`
  - 用输出确认边界和顺序。
- 执行范围检查：
  - `git diff --name-only -- src`
  - 期望无输出。
  - `git diff --name-only -- main.py requirements.txt schedule.db`
  - 期望无输出。
  - `git diff --name-only -- manage_instruction`
  - 期望只出现 `manage_instruction/Work_Log.md` 和开工前既有的 `manage_instruction/Work_Task_Prompts.md`。
  - `git status --short`

验收标准：

- `py_compile` 通过。
- `ReminderService` import 通过。
- 轻量假对象整体验证通过。
- `ReminderService` 无 UI/db/sound 依赖。
- `MainWindow` 中不再出现 `triggered_reminders`。
- `check_reminders()` 顺序仍是 `collect -> show -> mark`。
- `show_reminder_popup()` 仍保留弹窗和声音副作用边界。
- `build_reminder_popup_data()` 字段和值与旧内联 dict 构造一致。
- `src` 无 diff。
- `main.py`、`requirements.txt`、`schedule.db` 无 diff。
- 除 `Work_Log.md` 和既有 `Work_Task_Prompts.md` diff 外，`manage_instruction` 无其他新增 diff。
- 本工单不产生源码新 diff；若只有 `Work_Log.md` 追加验收记录，视为符合预期。
- 第五轮可进入归档/阶段收口流程。

### 5. 日志要求

- 在 `manage_instruction/Work_Log.md` 新增 `5-6` 记录，至少包含：
  - 本轮任务名与边界。
  - 开工前 git 状态基线，并明确哪些 diff 是既有提示词 diff。
  - 实际修改文件，原则上只能是 `manage_instruction/Work_Log.md`。
  - 5-0 到 5-5 完成摘要。
  - `ReminderService` 最终职责与禁止边界复核结果。
  - `MainWindow` 最终职责复核结果。
  - 旧行为保持复核结果。
  - 未做事项确认。
  - py_compile / import / 假对象验证 / 静态依赖检查结果。
  - diff 范围检查结果。
  - 第五轮整体验收结论：通过或不通过。
  - 若通过，明确写出：第五轮可归档，下一步可由决策窗口/顾问窗口规划第六轮。
  - 明确记录：本工单未实际执行归档搬迁，未修改历史归档文件，未开启第六轮改造。
  - 特别记录：本工单完成后不要提交 Git，等待顾问窗口审核。

### 6. 提交要求

- 执行窗口不得提交 Git。
- 本工单完成后等待顾问窗口审核。
- Git 提交只能由用户在顾问验收后执行。

