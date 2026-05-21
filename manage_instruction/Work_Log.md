# Work Log

本文件只记录当前阶段/当前轮次的执行日志。

历史日志已归档到 `manage_instruction/History_Log.md`。

## 当前状态

第一轮：基建 + repository + db_manager 兼容委托，已完成并归档。

第二轮：Data 层整理与模型拆分，已完成并归档。

第三轮：纯业务查询与排序服务，已完成并归档。

第四轮：日程写入与重复规则服务，已完成并归档。

当前处于第五轮“提醒与运行期状态服务”。

第五轮 `5-6` 整体验收与归档准备已完成，等待归档收口或第六轮规划提示词。

## 当前轮次注意事项

- 第四轮 4-0 ~ 4-9 已归档到 `History_Log.md`。
- 当前没有正在执行的小工单；下一步等待归档收口或第六轮规划提示词。
- 执行窗口不得沿用第四轮 4-9 或第四轮任一提示词继续执行。
- 执行窗口不得在未收到第五轮后续正式提示词前自行开始提醒服务改造。

## 2026-05-21 第五轮 5-0（静态审查与只读基线定位）

- 本轮任务名与边界（只读）：
  - 工单：第五轮 `5-0` 静态审查与只读基线定位。
  - 边界：仅做源码定位与链路审查，不改任何源码、不写数据库、不改 `requirements.txt`、不改 `schedule.db`、不改提示词文件。
  - 实际修改：仅更新本日志文件。

- 开工前 git 状态基线（既有 diff）：
  - `git status --short` 结果：
    - `M manage_instruction/Work_Instruction.md`
    - `M manage_instruction/Work_Task_Prompts.md`
    - `M requirements.txt`
    - `?? requirements.txt.bak`
  - 以上均记为开工前既有状态，不计入 5-0 新增 diff。

- 实际检索到的关键函数/文件位置：
  - `src/ui/main_window.py`
    - `_init_scheduler`: `160`
    - `check_reminders`: `225`
    - `triggered_reminders` 初始化: `164`
    - `show_reminder_popup`: `240`
    - `page_add.req_open_alarm_picker -> go_to_alarm_picker`: `138`
    - `page_dashboard.req_edit_alarm -> go_to_alarm_picker_for_edit`: `141`
    - `go_to_alarm_picker`: `374`
    - `go_to_alarm_picker_for_edit`: `381`
    - `on_alarm_confirmed`: `405`
  - `src/ui/reminder_pop.py`
    - 顶部关闭按钮绑定 `self.close`: `123`
    - “知道了”按钮绑定 `self.close`: `92`
    - “关闭闹钟”按钮绑定 `_stop_alarm`: `79`
    - `_stop_alarm` 中 `winsound.PlaySound(None, winsound.SND_PURGE)`: `182-186`
    - `closeEvent` 中 `winsound.PlaySound(None, winsound.SND_PURGE)`: `191-194`
  - `src/ui/alarm_picker.py`
    - `AlarmPickerView`: `40`
    - `set_initial_data`: `243`
    - `_validate_time`: `297`
    - `_on_confirm`（最终提醒时间校验 + `confirm_requested.emit`）: `355-397`
  - `src/ui/alarm_picker_week.py`
    - `AlarmPickerViewWeek`: `40`
    - `set_initial_data`: `235`
    - `_validate_time`: `276`
    - `_on_confirm`（最终提醒时间校验 + `confirm_requested.emit`）: `315-342`
  - `src/ui/add_view.py`
    - `_emit_alarm_request`（计算 `target_time` 并发起请求）: `427-436`
    - `set_alarm_data`: `438`
    - 保存时写入提醒字段：`schedule_data['reminder_time'/'is_alarm'/'alarm_duration']`: `642-644`
  - `src/ui/add_view_week.py`
    - `_emit_alarm_request`（计算 `target_time` 并发起请求）: `426-435`
    - `set_alarm_data`: `437`
    - 保存时写入提醒字段：`schedule_data['reminder_time'/'is_alarm'/'alarm_duration']`: `592-594`
  - `src/ui/schedule_detail_pop.py`
    - 提醒展示 Label + 双击提示：`323-329`
    - `refresh_alarm_display`: `514-517`
    - 双击提醒后发出 `req_edit_alarm`: `622-623`
  - `src/data/models.py`
    - `Schedule.reminder_time`: `30`
    - `Schedule.is_alarm`: `31`
    - `Schedule.alarm_duration`: `32`

- 8 段固定结构结论摘要：
  - 扫描链路：
    - `MainWindow.__init__` 调用 `_init_scheduler`（`158`）。
    - `_init_scheduler` 创建 `QTimer`（`161`）并每 1000ms 触发 `check_reminders`（`162-163`）。
    - `check_reminders` 从 `db_manager.get_all_schedules()` 拉取全量日程（`227`）并逐条筛选提醒。
    - 命中条件后调用 `show_reminder_popup`（`236`），再记录到 `triggered_reminders`（`237`）。
  - 触发条件：
    - 无 `reminder_time` 直接跳过（`230`）。
    - 触发窗口是 `0 <= (now - reminder_time).total_seconds() < 60`（`232-235`）。
    - 到点后 60 秒外不会触发；未到点不会触发。
  - 去重生命周期：
    - `triggered_reminders` 在 `_init_scheduler` 中初始化为内存 `set`（`164`）。
    - 同一 `schedule.id` 在本次进程内只要已加入 set，就不会再次弹窗（`235`）。
    - 无持久化写库逻辑；应用重启后集合重建为空（由初始化位置可推断）。
  - 弹窗/声音边界：
    - 弹窗对象在 `MainWindow.show_reminder_popup` 内创建：`ReminderPop(data_dict)`（`247`）。
    - 声音开启在 `MainWindow.show_reminder_popup` 内，仅 `is_alarm` 为真时调用 `winsound.PlaySound("SystemHand", ... LOOP|ASYNC)`（`250-252`）。
    - 声音停止在 `ReminderPop` 内部：`_stop_alarm`（`182-186`）与 `closeEvent`（`191-194`）。
    - 三条停声路径：
      - 顶部关闭按钮（`123`）-> `close()` -> `closeEvent` 停声。
      - “知道了”按钮（`92`）-> `close()` -> `closeEvent` 停声。
      - “关闭闹钟”按钮（`79`）-> `_stop_alarm` 立即停声并隐藏按钮（`189`）。
  - 提醒设置入口：
    - 新建入口：`AddScheduleView._emit_alarm_request` 计算 `target_time = start_time or end_time` 后发信号（`435-436`）。
    - 周视图新建入口：`AddScheduleViewWeek._emit_alarm_request` 同逻辑（`434-435`）。
    - 编辑入口：`ScheduleDetailPop` 双击提醒标签发出 `req_edit_alarm`（`622-623`）；主窗口连接到 `go_to_alarm_picker_for_edit`（`141`）。
    - 主窗口接入提醒页：`go_to_alarm_picker`（`374`）与 `go_to_alarm_picker_for_edit`（`381`）。
  - 可抽 service 的逻辑：
    - `check_reminders` 中纯判断部分可抽离：无提醒过滤、秒差计算、触发窗口判断、批量筛选。
    - 运行期去重状态语义（`triggered_reminders` 的 `is_triggered/mark_triggered`）可抽为轻量状态服务。
    - `target_time = start_time or end_time` 的纯数据选择可抽为纯函数。
  - 必须留 UI 的副作用：
    - `ReminderPop` 的窗口创建/显示、倒计时 UI 更新、交互按钮行为必须留在 UI 层。
    - `winsound.PlaySound(...)` 的播放与停止边界当前都在 UI 层（`MainWindow` + `ReminderPop`），不应在 5-0 修改。
    - `QTimer` 驱动节奏（1000ms）当前在主窗口层，不在本工单中改变。
  - 风险点：
    - 当前扫描源是 `get_all_schedules()` 全量扫描，秒级定时器下规模增大可能带来性能压力。
    - 去重是进程内内存态，崩溃/重启后会丢失“已弹过”状态（这是现有行为，不是缺陷修复项）。
    - 触发窗口固定 60 秒，若系统挂起或事件循环阻塞可能出现错过窗口不补弹。
    - `show_reminder_popup` 目前先弹窗再标记已触发，若未来改动异常处理顺序需谨慎（避免重复弹窗或漏标记）。

- 验收命令与结果：
  - 执行：
    - `git status --short`
    - `git diff --name-only`
    - `git diff --name-only -- src`
    - `git diff --name-only -- main.py requirements.txt schedule.db`
  - 结果结论：
    - `src` 无新增 diff（5-0 未改源码）。
    - `main.py` 无 diff。
    - `schedule.db` 无 diff。
    - `requirements.txt` 仍为开工前既有 diff，非 5-0 新增。
    - 管理文档 diff 中，`Work_Log.md` 为本工单预期更新，`Work_Instruction.md` / `Work_Task_Prompts.md` 为既有 diff。

- 风险与后续建议（供 5-1 使用）：
  - 先抽“纯判断函数”与“去重状态容器”，不要触碰 UI 弹窗与声音边界。
  - 抽离时保持 `0 <= diff < 60` 与 `target_time` 选择语义不变，避免行为回归。
  - `mark_triggered` 的调用时机建议仍放在“弹窗成功触发后”。

## 2026-05-21 第五轮 5-1（ReminderService 骨架与纯判断函数）

- 本轮任务名与边界：
  - 工单：第五轮 `5-1` ReminderService 骨架与纯判断函数。
  - 边界：仅新增提醒纯逻辑 service，不接入 `MainWindow`，不改 UI，不改数据库，不改依赖。

- 开工前 git 状态基线：
  - `git status --short` 结果：
    - `M manage_instruction/Work_Task_Prompts.md`
  - 该 diff 为开工前既有状态。

- 实际新增/修改文件：
  - 新增：`src/services/reminder_service.py`
  - 更新：`manage_instruction/Work_Log.md`
  - 未修改：`src/services/__init__.py`（本轮无需导出调整）

- `ReminderService` 纯函数/方法清单：
  - `has_reminder_time(schedule)`：判断是否存在 `reminder_time`。
  - `get_reminder_diff_seconds(schedule, now)`：计算 `now - reminder_time` 秒差；无提醒返回 `None`。
  - `is_in_trigger_window(diff_seconds)`：判断是否命中旧窗口 `0 <= diff < 60`。
  - `should_trigger(schedule, now)`：仅基于当前对象与时间判断是否触发；不考虑去重、无状态写入。
  - `select_target_time(schedule)`：`start_time` 优先，否则 `end_time`，若都无返回 `None`。

- 本轮明确未做事项（按工单要求）：
  - 未接入 `MainWindow`。
  - 未修改 `src/ui/*`。
  - 未实现运行期去重状态（未实现 `mark_triggered`、`collect_due_schedules`）。
  - 未生成完整弹窗 dict。
  - 未迁移声音播放。

- 假对象验证结果：
  - 无提醒：不触发（通过）。
  - 未到提醒时间：不触发（通过）。
  - 到点且在 60 秒窗口：触发（通过）。
  - 超过 60 秒窗口：不触发（通过）。
  - `target_time` 优先取 `start_time`（通过）。
  - 无 `start_time` 时取 `end_time`；都无时为 `None`（通过）。

- py_compile / import / 静态依赖检查结果：
  - `.\.venv\Scripts\python.exe -m py_compile src/services/reminder_service.py`：失败。
    - 原因：当前 `.venv` 指向的本地 Python 路径不可用（`Unable to create process ... Python311\python.exe`）。
  - 回退解释器：`C:\Users\22339\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`
    - `-m py_compile src/services/reminder_service.py`：通过。
    - `-c "from src.services.reminder_service import ReminderService; print(...)"`：通过，输出 `reminder service import ok`。
  - 轻量假对象脚本：通过，输出 `fake object checks ok`。
  - 静态依赖检查：
    - `rg -n "QWidget|QTimer|winsound|ReminderPop|db_manager|src\.ui|PyQt|PySide" src/services/reminder_service.py`
    - 结果：无输出、无匹配（`rg` 退出码 `1`，符合无匹配预期）。

- diff 范围检查结果：
  - `git status --short`：
    - `M manage_instruction/Work_Log.md`（本轮预期）
    - `M manage_instruction/Work_Task_Prompts.md`（开工前既有）
    - `A src/services/reminder_service.py`（本轮预期）
  - `git diff --name-only -- src/ui`：无输出（`src/ui` 无 diff）。
  - `git diff --name-only -- main.py requirements.txt schedule.db`：无输出（这三项无新增 diff）。

- 风险与后续建议（供 5-2 使用）：
  - 5-2 只需在当前 `ReminderService` 基础上补充“运行期去重状态容器”，不应改动 `should_trigger` 的纯判断语义。
  - `should_trigger` 目前无异常吞噬，后续接入前可由调用层保证传入对象字段类型正确，以避免隐藏错误。

- 顾问复验补充：
  - 用户在本机 CMD 重建 `.venv` 后，执行 `.\.venv\Scripts\python.exe -m py_compile src\services\reminder_service.py` 通过。
  - 用户在本机 CMD 执行 `.\.venv\Scripts\python.exe -c "from src.services.reminder_service import ReminderService; print('reminder service import ok')"` 通过。
  - 顾问工具环境中 `.venv` redirector 仍受工具权限/进程创建限制影响，但使用 Codex bundled Python 复跑 `py_compile`、import 和轻量假对象验证均通过。
  - 顾问复验确认：`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 无 diff；5-1 可验收通过。

## 2026-05-21 第五轮 5-2（运行期去重状态抽取）

- 本轮任务名与边界：
  - 工单：第五轮 `5-2` 运行期去重状态抽取。
  - 边界：仅在 `ReminderService` 增加运行期内存去重能力；不接入 `MainWindow`；不改 UI、数据库、依赖、触发窗口语义。

- 开工前 git 状态基线：
  - `git status --short` 结果：
    - `M manage_instruction/Work_Task_Prompts.md`
  - 该 diff 为开工前既有状态。

- 实际新增/修改文件：
  - 修改：`src/services/reminder_service.py`
  - 更新：`manage_instruction/Work_Log.md`
  - 未修改：`src/services/__init__.py`（本轮无需变更导出）

- `ReminderService` 新增的运行期去重方法清单：
  - `__init__()`：初始化实例级 `self._triggered_ids`（`set[int]`）。
  - `_get_schedule_id(schedule)`：纯辅助读取 `schedule.id`（仅接收 `int`）。
  - `is_triggered(schedule_id)`：判断 id 是否已在当前实例标记。
  - `mark_triggered(schedule_id)`：显式标记 id 已触发。
  - `collect_due_schedules(schedules, now)`：批量筛选“满足提醒条件且未标记”的对象列表；不隐式标记。
  - 同步修正：`get_reminder_diff_seconds` docstring 从 `.seconds` 改为 `total_seconds()` 表述（函数行为未变）。

- 本轮明确未做事项（按工单要求）：
  - 未接入 `MainWindow`。
  - 未修改 `src/ui/*`。
  - 未生成完整弹窗 dict（留给 5-4）。
  - 未迁移声音播放。
  - 未新增提醒持久化字段/表/迁移。

- 假对象验证结果：
  - 无提醒：`collect_due_schedules` 不返回（通过）。
  - 未到提醒时间：不返回（通过）。
  - 到点且在 60 秒窗口：返回（通过）。
  - 超过 60 秒窗口：不返回（通过）。
  - `mark_triggered(id)` 后：同 id 不再返回（通过）。
  - `collect_due_schedules` 不隐式标记：同一未标记对象连续 collect 两次仍返回（通过）。
  - 新建 `ReminderService()` 实例：去重状态为空（通过）。
  - `should_trigger(schedule, now)` 在 `mark_triggered(id)` 后仍返回纯判断结果，不受去重状态影响（通过）。

- py_compile / import / 静态依赖检查结果：
  - `.\.venv\Scripts\python.exe -m py_compile src/services/reminder_service.py`：失败（Unable to create process，`.venv` redirector 指向不可用本机 Python 路径）。
  - `.\.venv\Scripts\python.exe -c "from src.services.reminder_service import ReminderService; ..."`：同样失败（同原因）。
  - 回退 bundled Python：
    - `C:\Users\22339\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m py_compile src/services/reminder_service.py`：通过。
    - import 校验：通过，输出 `reminder service import ok`。
  - 静态依赖检查：
    - `rg -n "QWidget|QTimer|winsound|ReminderPop|db_manager|src\.ui|PyQt|PySide" src/services/reminder_service.py`
    - 结果：无输出/无匹配（`rg` 退出码 1，符合预期）。

- diff 范围检查结果：
  - `git status --short`：
    - `M manage_instruction/Work_Log.md`（本轮预期）
    - `M manage_instruction/Work_Task_Prompts.md`（既有）
    - `M src/services/reminder_service.py`（本轮预期）
  - `git diff --name-only -- src/ui`：无输出（`src/ui` 无 diff）。
  - `git diff --name-only -- main.py requirements.txt schedule.db`：无输出（本工单未引入这三项 diff）。

- 风险与后续建议（供 5-3 使用）：
  - 5-3 接入 `MainWindow` 时，应在弹窗成功后显式调用 `mark_triggered(id)`，避免重复弹窗。
  - `collect_due_schedules` 当前对 `id` 非 `int` 的对象会跳过；接入层需确保日程对象带有效 `id`。
  - 保持 `should_trigger` 的无状态纯判断边界，不要在其中引入去重写入。

- 特别记录：
  - 本工单完成后不要提交 Git，等待顾问窗口审核。

## 2026-05-21 第五轮 5-3（MainWindow 提醒扫描最小委托）

- 本轮任务名与边界：
  - 工单：第五轮 `5-3` MainWindow 提醒扫描最小委托。
  - 边界：仅改 `src/ui/main_window.py` 的提醒扫描接入；保持 UI 弹窗/声音/QTimer/数据源语义不变。

- 开工前 git 状态基线：
  - `git status --short` 结果：
    - `M manage_instruction/Work_Task_Prompts.md`
  - 该 diff 为开工前既有状态。

- 实际新增/修改文件：
  - 修改：`src/ui/main_window.py`
  - 更新：`manage_instruction/Work_Log.md`
  - 未修改：`src/services/reminder_service.py`（本轮无兼容修正需求）

- `MainWindow` 接入 `ReminderService` 的位置说明：
  - 新增 import：`from ..services.reminder_service import ReminderService`（`src/ui/main_window.py:27`）。
  - `_init_scheduler()` 中创建 service 实例：`self.reminder_service = ReminderService()`（`src/ui/main_window.py:162`）。
  - 保留原有 QTimer 行为：
    - `self.reminder_timer = QTimer(self)`
    - `self.reminder_timer.timeout.connect(self.check_reminders)`
    - `self.reminder_timer.start(1000)`
  - 删除主窗口直接维护裸 `triggered_reminders` 的细节。

- `check_reminders()` 新扫描流程摘要：
  - `now = datetime.now()`
  - `schedules = db_manager.get_all_schedules()`
  - `due_schedules = self.reminder_service.collect_due_schedules(schedules, now)`
  - 遍历 due：
    - 先 `self.show_reminder_popup(s)`
    - 后 `self.reminder_service.mark_triggered(s.id)`
    - 打印日志（延迟由 `get_reminder_diff_seconds` 计算）
  - 已确认顺序是 `collect -> show -> mark`（定位行：`226/230/232/233`）。

- 本轮明确未做事项（按工单要求）：
  - 未修改 `src/ui/reminder_pop.py`。
  - 未修改提醒选择页（`alarm_picker*`、`add_view*`、`schedule_detail_pop` 均未改）。
  - 未迁移声音播放（`winsound.PlaySound(...)` 仍在 `show_reminder_popup`）。
  - 未迁移 QTimer（仍由 `MainWindow` 创建与驱动）。
  - 未生成完整弹窗 dict（`show_reminder_popup` 字段与语义保持不变）。
  - 未新增提醒持久化字段/表/迁移。

- py_compile / import / 静态检查结果：
  - `.venv` 验证：
    - `.\.venv\Scripts\python.exe -m py_compile ...`：失败（Unable to create process）。
    - `.\.venv\Scripts\python.exe -c "from src.services.reminder_service ..."`：失败（同原因）。
  - bundled Python 复验：
    - `py_compile src/services/reminder_service.py src/ui/main_window.py`：通过。
    - import `ReminderService`：通过，输出 `reminder service import ok`。
  - 静态检查：
    - `rg -n "triggered_reminders" src/ui/main_window.py`：无输出（主窗口已不直接操作裸 set）。
    - `rg -n "winsound|ReminderPop|show_reminder_popup|PlaySound" src/services/reminder_service.py`：无输出（service 未吸收 UI/声音副作用）。
  - 轻量语义复验（bundled Python）：通过，确认
    - `collect_due_schedules` 不隐式标记；
    - `mark_triggered` 后过滤生效；
    - `should_trigger` 仍不受去重状态影响。

- diff 范围检查结果：
  - `git diff --name-only -- src/ui`：仅 `src/ui/main_window.py`。
  - `git diff --name-only -- main.py requirements.txt schedule.db`：无输出。
  - `git status --short`：
    - `M manage_instruction/Work_Log.md`（本轮预期）
    - `M manage_instruction/Work_Task_Prompts.md`（既有）
    - `M src/ui/main_window.py`（本轮预期）

- 风险与后续建议（供 5-4 使用）：
  - 5-4 若收口弹窗 dict 构造到 service，需保证字段仍是 `title/is_alarm/target_time` 且 `target_time` 语义不变。
  - `mark_triggered` 目前依赖 `s.id`；接入层应确保日程对象存在有效 `id`。
  - 若后续加入异常保护循环，需继续保证“仅 show 成功后才 mark”，不得放在 `finally`。

- 特别记录：
  - 本工单完成后不要提交 Git，等待顾问窗口审核。

- 顾问复验补充：
  - 使用 Codex bundled Python 复跑 `py_compile src/services/reminder_service.py src/ui/main_window.py` 和 `ReminderService` import 验证，均通过。
  - 静态检查确认 `src/ui/main_window.py` 中已无 `triggered_reminders`，`src/services/reminder_service.py` 中无 UI/声音副作用关键字。
  - 复验 `check_reminders()` 文本顺序为 `collect_due_schedules` -> `show_reminder_popup(s)` -> `mark_triggered(s.id)`，且未把标记放入 `finally`。
  - 复验 `ReminderService.collect_due_schedules` 不隐式标记、`mark_triggered` 后过滤、`should_trigger` 不受去重状态影响。
  - diff 范围确认：`src/ui` 仅 `main_window.py` 有 diff；`src/ui/reminder_pop.py`、`main.py`、`requirements.txt`、`schedule.db` 无 diff；`main_window.py` 末尾补换行属于无行为格式变化。
  - 5-3 可验收通过。

## 2026-05-21 第五轮 5-4（提醒弹窗数据构造边界收口）

- 本轮任务名与边界：
  - 工单：第五轮 `5-4` 提醒弹窗数据构造边界收口。
  - 边界：仅把弹窗 `data_dict` 纯构造逻辑收口到 `ReminderService`；不改扫描主流程语义，不改 UI/声音/QTimer 边界。

- 开工前 git 状态基线：
  - `git status --short` 结果：
    - `M manage_instruction/Work_Task_Prompts.md`
  - 该项为开工前既有 diff。

- 实际新增/修改文件：
  - 修改：`src/services/reminder_service.py`
  - 修改：`src/ui/main_window.py`
  - 更新：`manage_instruction/Work_Log.md`

- `ReminderService` 新增的弹窗数据构造方法说明：
  - 新增 `build_reminder_popup_data(schedule)`。
  - 返回字段固定为：`title`、`is_alarm`、`target_time`。
  - 值语义保持：
    - `title` 来自 `schedule.title`
    - `is_alarm` 来自 `schedule.is_alarm`
    - `target_time` 复用 `select_target_time(schedule)`（`start_time` 优先，否则 `end_time`，都无时 `None`）。

- `show_reminder_popup` 保持不变的副作用边界说明（弹窗 + 声音）：
  - `MainWindow.show_reminder_popup()` 仍负责：
    - `ReminderPop(data_dict)` 创建
    - `self.current_popup.show()` 显示
    - `winsound.PlaySound(...)` 播放声音（仅 `schedule_data.is_alarm` 为真）
  - 本轮仅把 `data_dict` 的构造改为：
    - `data_dict = self.reminder_service.build_reminder_popup_data(schedule_data)`

- 假对象验证结果（bundled Python）：
  - `start_time` 存在时：`target_time == start_time`（通过）。
  - `start_time` 为空且 `end_time` 存在时：`target_time == end_time`（通过）。
  - `start_time` / `end_time` 都为空时：`target_time is None`（通过）。
  - `title` / `is_alarm` 原样来自 schedule（通过）。
  - dict key 精确等于 `title/is_alarm/target_time`（通过，无新增遗漏字段）。

- py_compile / import / 静态依赖检查结果：
  - `.venv` 验证：
    - `.\.venv\Scripts\python.exe -m py_compile src/services/reminder_service.py src/ui/main_window.py`：失败（Unable to create process）。
    - `.\.venv\Scripts\python.exe -c "from src.services.reminder_service import ReminderService; ..."`：失败（同原因）。
  - 回退 bundled Python：
    - `py_compile src/services/reminder_service.py src/ui/main_window.py`：通过。
    - import `ReminderService`：通过，输出 `reminder service import ok`。
  - 静态依赖检查：
    - `rg -n "QWidget|QTimer|winsound|ReminderPop|db_manager|src\.ui|PyQt|PySide" src/services/reminder_service.py`
    - 结果：无输出/无匹配（`rg` 退出码 1，符合预期）。

- diff 范围检查结果：
  - `git diff --name-only -- src/ui`：仅 `src/ui/main_window.py`。
  - `git diff --name-only -- main.py requirements.txt schedule.db`：无输出。
  - `git status --short`：
    - `M manage_instruction/Work_Task_Prompts.md`（既有）
    - `M src/services/reminder_service.py`（本轮预期）
    - `M src/ui/main_window.py`（本轮预期）

- 本轮未做事项（按工单要求）：
  - 未修改 `src/ui/reminder_pop.py`。
  - 未迁移声音播放到 service。
  - 未迁移 QTimer 到 service。
  - 未改变 `check_reminders()` 的 `collect -> show -> mark` 顺序。
  - 未新增提醒持久化字段/表/迁移。

- 风险与后续建议（供 5-5 使用）：
  - 5-5 可重点做回归验证：`show_reminder_popup` 输入 dict 字段一致性与到点触发行为保持。
  - 若后续补异常保护，仍需保证 `mark_triggered(s.id)` 在 `show_reminder_popup(s)` 成功调用之后。

- 特别记录：
  - 本工单完成后不要提交 Git，等待顾问窗口审核。
- 顾问复验补充：
  - 顾问修正 `build_reminder_popup_data(schedule)`，将 `title` / `is_alarm` 改为直接读取 `schedule.title` / `schedule.is_alarm`，保持与旧 `MainWindow.show_reminder_popup()` 内联构造完全一致。
  - 使用 Codex bundled Python 复跑 `py_compile src/services/reminder_service.py src/ui/main_window.py` 和 `ReminderService` import 验证，均通过。
  - 复跑弹窗 dict 假对象验证，确认 key 精确等于 `title`、`is_alarm`、`target_time`，且 `target_time` 选择语义保持不变。
  - 静态依赖检查确认 `ReminderService` 未依赖 UI、声音或 `db_manager`。
  - 复验 `show_reminder_popup()` 仍创建 `ReminderPop(data_dict)`、调用 `show()`，并按 `schedule_data.is_alarm` 在 UI 层调用 `winsound.PlaySound(...)`。
  - 复验 `check_reminders()` 仍保持 `collect -> show -> mark` 顺序。
  - diff 范围确认：`src/ui` 仅 `main_window.py` 有 diff；`src/ui/reminder_pop.py`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。
  - 5-4 可验收通过。

## 2026-05-21 第五轮 5-5（提醒服务轻量回归验收）

- 本轮任务名与边界：
  - 工单：第五轮 `5-5` 提醒服务轻量回归验收。
  - 边界：仅做验证与边界复核，不改源码、不改数据库、不改依赖；仅更新本日志。

- 开工前 git 状态基线：
  - `git status --short`：
    - `M manage_instruction/Work_Task_Prompts.md`
  - 该项记为既有提示词 diff，不计入 5-5 新增改动。
  - 开工前未发现 5-4 遗留源码 diff，因此继续执行 5-5。

- 实际修改文件：
  - `manage_instruction/Work_Log.md`（本轮预期）

- ReminderService 回归验证结果：
  - `has_reminder_time(schedule)`：无提醒返回 False（通过）。
  - `get_reminder_diff_seconds(schedule, now)`：沿用 `total_seconds()` 语义（通过）。
  - `is_in_trigger_window(diff)`：保持 `0 <= diff < 60`（通过）。
  - `should_trigger(schedule, now)`：保持无状态纯判断，不受去重状态影响（通过）。
  - `collect_due_schedules(schedules, now)`：不隐式标记（通过）。
  - `mark_triggered(id)` 后：同 id 不再被 collect 返回（通过）。
  - 新建 `ReminderService()` 实例：去重状态为空（通过）。
  - `select_target_time(schedule)`：`start_time` 优先，否则 `end_time`，都无时 `None`（通过）。
  - `build_reminder_popup_data(schedule)`：key 精确为 `title/is_alarm/target_time`，字段值语义正确（通过）。

- MainWindow 静态边界复核结果：
  - `_init_scheduler()` 仍创建 QTimer 且 `start(1000)`（保留）。
  - `_init_scheduler()` 已创建 `self.reminder_service = ReminderService()`（保留）。
  - `check_reminders()` 数据来源仍为 `db_manager.get_all_schedules()`（保留）。
  - 顺序仍为：`collect_due_schedules -> show_reminder_popup(s) -> mark_triggered(s.id)`（保留）。
  - `show_reminder_popup()` 仍负责 `ReminderPop(data_dict)`、`show()`、`winsound.PlaySound(...)`（保留）。
  - 声音播放条件仍基于 `schedule_data.is_alarm`（保留）。

- UI/声音/数据库副作用边界复核结果：
  - `src/ui/reminder_pop.py` 无 diff。
  - `winsound.PlaySound(...)` 未迁移到 service。
  - `ReminderPop` 未迁移到 service。
  - `QTimer` 未迁移到 service。
  - service 未依赖 `db_manager`。
  - `schedule.db` 无 diff。

- py_compile / import / 假对象验证 / 静态依赖检查结果：
  - `.venv` 两条命令均失败：`Unable to create process ... Python311\python.exe`（工具环境问题，已留痕）。
  - 使用 bundled Python 复验：
    - `py_compile src/services/reminder_service.py src/ui/main_window.py`：通过。
    - `from src.services.reminder_service import ReminderService`：通过，输出 `reminder service import ok`。
  - 轻量假对象回归脚本：通过，输出 `5-5 regression checks ok`。
  - service 静态依赖检查：
    - `rg -n "QWidget|QTimer|winsound|ReminderPop|db_manager|src\.ui|PyQt|PySide" src/services/reminder_service.py`
    - 结果：无输出/无匹配（`rg` 退出码 1，符合预期）。

- diff 范围检查结果：
  - `git diff --name-only -- src/ui`：无输出。
  - `git diff --name-only -- src/services/reminder_service.py`：无输出。
  - `git diff --name-only -- main.py requirements.txt schedule.db`：无输出。
  - `git status --short`（收尾）：
    - `M manage_instruction/Work_Log.md`（本轮预期）
    - `M manage_instruction/Work_Task_Prompts.md`（既有提示词 diff）

- 风险与后续建议（供 5-6 使用）：
  - 当前 `.venv` 在工具环境仍不可直接执行，5-6 若要求强依赖 `.venv` 命令，应继续使用“`.venv`失败留痕 + bundled Python复验”策略。
  - 第五轮可进入整体验收与归档准备，重点确认外部行为无回归。

- 特别记录：
  - 本工单完成后不要提交 Git，等待顾问窗口审核。

- 顾问复验补充：
  - 使用 Codex bundled Python 复跑 `py_compile src/services/reminder_service.py src/ui/main_window.py` 和 `ReminderService` import 验证，均通过。
  - 复跑 5-5 轻量假对象回归验证，确认提醒窗口、运行期去重状态、`target_time` 选择和弹窗 dict 构造均符合预期。
  - 静态依赖检查确认 `ReminderService` 无 UI、声音或 `db_manager` 依赖；`MainWindow` 中无 `triggered_reminders`。
  - 复验 `check_reminders()` 顺序仍为 `collect_due_schedules` -> `show_reminder_popup(s)` -> `mark_triggered(s.id)`。
  - diff 范围确认：`src/ui`、`src/services/reminder_service.py`、`main.py`、`requirements.txt`、`schedule.db` 均无 diff；5-5 只追加日志记录。
  - 5-5 可验收通过。

## 2026-05-21 第五轮 5-6（第五轮整体验收与归档准备）

- 本轮任务名与边界：
  - 工单：第五轮 `5-6` 整体验收与归档准备。
  - 边界：仅做最终验收、范围复核与日志收口；不改源码、不改数据库、不改依赖，不执行实际归档搬迁。

- 开工前 git 状态基线：
  - `git status --short`：
    - `M manage_instruction/Work_Task_Prompts.md`
  - 该项为既有提示词 diff，不计入 5-6 新增改动。
  - 开工前 `src`、`main.py`、`requirements.txt`、`schedule.db` 无 diff，满足继续执行条件。

- 实际修改文件：
  - `manage_instruction/Work_Log.md`（本轮预期）

- 5-0 到 5-5 完成摘要：
  - `5-0`：完成提醒链路静态基线定位，确认触发窗口与 UI/声音边界。
  - `5-1`：完成 `ReminderService` 纯判断骨架（无去重、无 UI 副作用）。
  - `5-2`：完成运行期去重状态抽取（`is_triggered/mark_triggered/collect_due_schedules`）。
  - `5-3`：完成 `MainWindow.check_reminders()` 最小委托（`collect -> show -> mark`）。
  - `5-4`：完成弹窗 dict 纯构造收口（`build_reminder_popup_data`）。
  - `5-5`：完成轻量回归验收并确认边界与行为保持。

- ReminderService 最终职责与禁止边界复核结果：
  - 最终职责已覆盖：
    - 提醒时间存在判断。
    - 秒差计算与触发窗口判断（`0 <= diff < 60`）。
    - 运行期去重状态管理。
    - 到期候选筛选。
    - `target_time` 选择。
    - 弹窗 dict 纯构造（`title/is_alarm/target_time`）。
  - 禁止边界满足：
    - 无 UI 依赖、无 `winsound`、无 `ReminderPop`、无 `QTimer`、无 `db_manager`、无数据库写入。

- MainWindow 最终职责复核结果：
  - 仍由 `MainWindow` 创建 QTimer，且 `start(1000)`。
  - 扫描数据来源仍为 `db_manager.get_all_schedules()`。
  - `check_reminders()` 顺序仍为 `collect_due_schedules -> show_reminder_popup(s) -> mark_triggered(s.id)`。
  - `show_reminder_popup()` 仍负责：
    - 创建 `ReminderPop(data_dict)`；
    - 弹窗 `show()`；
    - 按 `schedule_data.is_alarm` 播放系统声音。

- 旧行为保持复核结果：
  - 无 `reminder_time` 不触发（通过）。
  - 未到提醒时间不触发（通过）。
  - 超过 60 秒窗口不补弹（通过）。
  - 到点且在 60 秒窗口内触发（通过）。
  - 同一日程 ID 本次运行内不重复触发（通过）。
  - 新 service 实例去重状态为空（通过）。
  - `target_time` 仍优先 `start_time`，否则 `end_time`，都无则 `None`（通过）。
  - 弹窗 dict 仍仅 `title/is_alarm/target_time`（通过）。
  - 强提醒声音仍由 UI 层播放（通过）。
  - 关闭弹窗/停止闹钟逻辑仍在 `ReminderPop`（通过）。

- 未做事项确认：
  - 未修改 `ReminderPop`。
  - 未修改提醒选择页。
  - 未修改数据库模型。
  - 未新增数据库字段或提醒持久化。
  - 未修改 `db_manager` 对外 API。
  - 未修改 `main.py`、`requirements.txt`、`schedule.db`。
  - 未开启第六轮 Controller / Router / EventBus 改造。

- py_compile / import / 假对象验证 / 静态依赖检查结果：
  - `.venv` 命令在工具环境失败：`Unable to create process ... Python311\python.exe`（已留痕）。
  - bundled Python 复验：
    - `py_compile main.py src/services/reminder_service.py src/ui/main_window.py src/ui/reminder_pop.py`：通过。
    - `ReminderService` import：通过，输出 `reminder service import ok`。
  - 轻量假对象整体验证：通过，输出 `5-6 overall regression checks ok`。
  - service 静态依赖检查：
    - `rg -n "QWidget|QTimer|winsound|ReminderPop|db_manager|src\.ui|PyQt|PySide" src/services/reminder_service.py`
    - 结果：无输出/无匹配（`rg` 退出码 1，符合预期）。
  - MainWindow 静态检查：
    - `rg -n "triggered_reminders" src/ui/main_window.py`：无输出。
    - 顺序/边界关键词检查输出符合预期（含 `get_all_schedules`、`start(1000)`、`collect`、`show`、`mark`、`ReminderPop`、`PlaySound`）。

- diff 范围检查结果：
  - `git diff --name-only -- src`：无输出。
  - `git diff --name-only -- main.py requirements.txt schedule.db`：无输出。
  - `git diff --name-only -- manage_instruction`：
    - `manage_instruction/Work_Log.md`（本轮预期）
    - `manage_instruction/Work_Task_Prompts.md`（既有提示词 diff）
  - `git status --short`（收尾）：
    - `M manage_instruction/Work_Log.md`（本轮预期）
    - `M manage_instruction/Work_Task_Prompts.md`（既有）

- 第五轮整体验收结论：
  - 结论：通过。
  - 可归档性：第五轮可进入归档/阶段收口流程。
  - 下一步建议：可由决策窗口/顾问窗口规划第六轮（Controller / Router / EventBus 协调层）。

- 明确声明：
  - 本工单未实际执行归档搬迁。
  - 未修改 `History_Log.md`、`History_Instruction.md` 等历史归档文件。
  - 未开启第六轮改造。

- 特别记录：
  - 本工单完成后不要提交 Git，等待顾问窗口审核。
- 顾问复验补充：
  - 已同步 `Work_Log.md` 顶部当前状态：第五轮 `5-6` 已完成，下一步等待归档收口或第六轮规划提示词。
  - 使用 Codex bundled Python 复跑 `py_compile main.py src/services/reminder_service.py src/ui/main_window.py src/ui/reminder_pop.py` 和 `ReminderService` import 验证，均通过。
  - 复跑 5-6 轻量假对象整体验证，确认提醒窗口、运行期去重、`target_time` 选择、弹窗 dict 构造和 `check_reminders()` 顺序均符合预期，输出 `5-6 overall regression checks ok`。
  - 静态依赖检查确认 `ReminderService` 无 UI、声音或 `db_manager` 依赖；`MainWindow` 中无 `triggered_reminders`。
  - 范围检查确认：`src`、`main.py`、`requirements.txt`、`schedule.db` 均无 diff；当前仅 `Work_Log.md` 和既有 `Work_Task_Prompts.md` 有 diff。
  - 5-6 可验收通过；第五轮可进入归档/阶段收口流程。
