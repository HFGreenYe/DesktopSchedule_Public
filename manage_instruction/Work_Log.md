# Work Log

本文件只记录当前阶段/当前轮次的执行日志。

历史日志已归档到 `manage_instruction/History_Log.md`。

## 当前状态

第一轮：基建 + repository + db_manager 兼容委托，已完成并归档。

第二轮：Data 层整理与模型拆分，已完成并归档。

第三轮：纯业务查询与排序服务，已完成并归档。

第四轮：日程写入与重复规则服务，已完成并归档。

当前处于第五轮“提醒与运行期状态服务”。

第五轮 `5-1` ReminderService 骨架与纯判断函数已完成，等待 `5-2` 正式提示词。

## 当前轮次注意事项

- 第四轮 4-0 ~ 4-9 已归档到 `History_Log.md`。
- 当前没有正在执行的小工单；下一步等待 `5-2` 提示词。
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
