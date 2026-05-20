# Work Instruction

用途：本文件用于“当前阶段”的执行指令发布。

- 仅保留正在执行或即将执行的任务。
- 已完成阶段请归档到 `History_Instruction.md`，避免本文件长期堆积。
- 当前主路线图见 `Work_Formulation.md` 的“架构改写轮次路线图”。
- 改写前行为和目录快照见 `Work_Snapshot.md`。
- 执行过程记录写入 `Work_Log.md`。

---

# 当前阶段：第五轮 - 提醒与运行期状态服务

## 已完成并归档

- 第一轮：基建 + repository + db_manager 兼容委托。
- 第二轮：Data 层整理与模型拆分。
- 第三轮：纯业务查询与排序服务。
- 第四轮：日程写入与重复规则服务。
  - 第四轮 4-0 ~ 4-9 均已完成并归档。
  - 已完成 `ScheduleRepeatService` 与 `ScheduleService` 的第四轮服务边界。
  - 已验证 `add_schedule` 非重复/重复路径，以及 `update_schedule_with_repeat` 当前条、非组转重复、已有组改重复、取消重复路径。
  - 第四轮最终验收通过，`src`、`main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。

---

## 第五轮目标

第五轮目标是把提醒扫描、提醒触发判断和本次运行内去重状态，从 `MainWindow` 中逐步拆到 service 层，但继续保留 UI 弹窗、声音播放和 QTimer 驱动方式不变。

本轮重点处理：

- `MainWindow._init_scheduler()`
- `MainWindow.check_reminders()`
- `MainWindow.triggered_reminders`
- 提醒时间判断：`0 <= now - reminder_time < 60`
- 无提醒项跳过规则
- 本次运行内同一日程不重复弹窗规则
- 提醒触发后仍由 UI 层调用 `show_reminder_popup`
- `ReminderPop` 和 `winsound.PlaySound(...)` 的边界保持在 UI 层

本轮风险中等。提醒逻辑看似小，但涉及秒级定时器、内存状态、弹窗和声音副作用，必须先做只读基线定位，再拆纯逻辑，最后做最小委托。

---

## 第五轮允许修改范围

第五轮整体允许修改：

- `src/services/reminder_service.py`
- `src/services/__init__.py`
- `src/ui/main_window.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

如具体小工单明确需要，允许读取但默认不修改：

- `src/ui/reminder_pop.py`
- `src/ui/alarm_picker.py`
- `src/ui/alarm_picker_week.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- `src/ui/schedule_detail_pop.py`
- `src/data/models.py`
- `src/repositories/schedule_repository.py`
- `src/data/database.py`

---

## 第五轮禁止事项

- 不修改 `ReminderPop` UI 布局、尺寸、窗口 flag、倒计时显示和关闭按钮行为。
- 不迁移或封装 `winsound.PlaySound(...)`，声音播放和停止仍留在 UI/弹窗层。
- 不改变 `QTimer` 扫描频率，仍保持每秒扫描一次。
- 不改变提醒触发窗口，仍保持提醒时间之后 60 秒内触发。
- 不新增提醒持久化表、字段或数据库迁移。
- 不让已触发提醒状态写入数据库。
- 不改变重启后提醒去重状态清空的旧行为。
- 不修改提醒选择页校验规则。
- 不修改 `db_manager` 对外公开 API。
- 不修改 `main.py`。
- 不修改 `requirements.txt`。
- 不修改 `schedule.db`。
- 不处理 Controller / Router / EventBus 迁移。
- 不处理系统通知、托盘通知、Toast 通知等新功能。
- 不处理四象限、搜索、筛选、导出、同步等占位功能。

---

## 行为保持原则

第五轮所有改动必须满足：

- 应用启动后仍由 `MainWindow` 创建提醒扫描定时器。
- 扫描间隔仍为 1000ms。
- 提醒数据来源仍为 `db_manager.get_all_schedules()`。
- 无 `reminder_time` 的日程必须跳过。
- 当前时间处于 `reminder_time` 之后 60 秒内才触发。
- 未到提醒时间不触发。
- 超过 60 秒窗口不补弹。
- 同一日程 ID 在本次运行内只弹一次。
- 应用重启后，已触发集合重新为空，不持久化。
- 到点后仍调用原 `show_reminder_popup(schedule)`。
- 弹窗数据仍包含 `title`、`is_alarm`、`target_time`。
- `target_time` 仍优先使用 `start_time`，没有开始时间时使用 `end_time`。
- `is_alarm` 为真时仍播放系统声音 `SystemHand`。
- 关闭弹窗、点击“关闭闹钟”、点击“知道了”仍能停止声音。
- service 不依赖 QWidget、QTimer、winsound、ReminderPop、db_manager。

---

## 第五轮小工单拆分草案

第五轮采用 `5-0`、`5-1` 等编号。执行时仍可根据基线结果继续拆分更小工单，不得为了匹配编号一次迁移过多逻辑。

### 5-0：静态审查与只读基线定位

目标：

- 不改代码。
- 不写数据库。
- 定位当前提醒扫描、触发判断、去重集合、弹窗和声音调用位置。
- 明确提醒触发窗口、无提醒规则、过期规则和重启后状态规则。
- 明确哪些逻辑可抽 service，哪些 UI 副作用必须留在 UI 层。

必须定位：

- `src/ui/main_window.py`
- `src/ui/reminder_pop.py`
- `src/ui/alarm_picker.py`
- `src/ui/alarm_picker_week.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- `src/ui/schedule_detail_pop.py`
- `src/data/models.py`

重点搜索：

- `check_reminders`
- `_init_scheduler`
- `triggered_reminders`
- `show_reminder_popup`
- `reminder_time`
- `is_alarm`
- `alarm_duration`
- `PlaySound`
- `ReminderPop`
- `QTimer`
- `target_time`

验收重点：

- 输出当前提醒扫描流程。
- 输出当前触发条件。
- 输出当前去重状态生命周期。
- 输出弹窗和声音调用边界。
- 输出提醒选择和提醒显示相关位置。
- `src`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

### 5-1：ReminderService 骨架与纯判断函数

目标：

- 新增 `src/services/reminder_service.py`。
- 只建立 service 边界和纯判断函数。
- 不接入 `MainWindow`。
- 不修改 UI 行为。

建议能力：

- 判断日程是否有提醒时间。
- 计算 `now - reminder_time` 秒差。
- 判断是否处于旧触发窗口：`0 <= diff < 60`。
- 提供 `target_time` 选择辅助，优先 `start_time`，否则 `end_time`。
- 不在本工单生成完整弹窗 dict；完整 dict 构造留到 5-4 收口。

验收重点：

- service 可单独 import。
- service 不依赖 QWidget、QTimer、winsound、ReminderPop、db_manager。
- 用轻量假对象验证未到、到点、超过 60 秒、无提醒四类情况。
- `MainWindow` 行为未改变。
- `schedule.db` 无 diff。

### 5-2：运行期去重状态抽取

目标：

- 在 `ReminderService` 中增加运行期去重状态能力，或新增轻量状态类。
- 把 `triggered_reminders` 的 set 语义抽象出来。
- 暂不接入 UI。
- 不持久化。

建议能力：

- `is_triggered(schedule_id)`
- `mark_triggered(schedule_id)`
- `should_trigger(schedule, now)`
- `collect_due_schedules(schedules, now)`

边界要求：

- `should_trigger(schedule, now)` 只负责判断当前日程在不考虑去重写入时是否满足提醒触发条件，不得写入已触发状态。
- `collect_due_schedules(schedules, now)` 可负责批量筛选候选项，但不得隐式标记已触发；标记动作必须由调用方在弹窗触发成功后显式调用 `mark_triggered(schedule_id)`。

行为要求：

- 同一 ID 第一次满足条件时可触发。
- 同一 ID 已标记后不再触发。
- 新 service 实例状态为空，模拟应用重启后清空。
- 不写数据库。

验收重点：

- 用假对象验证同一日程不会重复触发。
- 用新 service 实例验证去重状态不持久化。
- service 仍不依赖 UI 和数据库。
- `schedule.db` 无 diff。

### 5-3：MainWindow 提醒扫描最小委托

目标：

- 让 `MainWindow.check_reminders()` 委托 `ReminderService` 判断哪些日程应触发。
- 保留 `MainWindow._init_scheduler()` 创建 QTimer。
- 保留 `MainWindow.show_reminder_popup()`。
- 保留 `db_manager.get_all_schedules()` 数据来源。

改造边界：

- `MainWindow` 可以持有 `self.reminder_service`。
- `MainWindow` 不再直接维护裸 `triggered_reminders` 判断细节。
- 触发后仍调用 `self.show_reminder_popup(s)`。
- `MainWindow` 应在 `self.show_reminder_popup(s)` 成功调用后，再显式调用 `mark_triggered(s.id)`，避免只筛选不标记导致重复弹窗。
- 打印日志可保持或等价迁移，但不得改变核心行为。

验收重点：

- `check_reminders()` 可读性提升。
- 到点仍会调用 `show_reminder_popup`。
- 同一 ID 本次运行内不重复触发。
- 未到、过期、无提醒不触发。
- `show_reminder_popup` 行为不变。
- `schedule.db` 无 diff。

### 5-4：提醒弹窗数据构造边界收口

目标：

- 将弹窗数据 dict 的纯构造逻辑委托给 `ReminderService`。
- 不修改 `ReminderPop`。
- 不迁移声音播放。
- 不改变 dict 字段和值。

旧字段必须保持：

- `title`
- `is_alarm`
- `target_time`

行为要求：

- `target_time = start_time if start_time else end_time`
- `is_alarm` 原样来自日程对象。
- `title` 原样来自日程对象。

验收重点：

- `show_reminder_popup()` 仍创建 `ReminderPop(data_dict)`。
- `is_alarm` 为真时仍在 `MainWindow` 播放系统声音。
- `ReminderPop` 文件无 diff。
- `winsound` 调用边界未改变。
- `schedule.db` 无 diff。

### 5-5：提醒服务轻量回归验收

目标：

- 汇总 5-1 到 5-4。
- 做不写库或可清理的轻量验证。
- 确认第五轮提醒服务边界稳定。

建议验证：

- service import。
- service 静态依赖检查。
- 假对象验证未到提醒不触发。
- 假对象验证到点触发。
- 假对象验证超过 60 秒不触发。
- 假对象验证无提醒不触发。
- 假对象验证同一 ID 不重复触发。
- fake/new service 实例验证重启后状态为空。
- `MainWindow` import 或 `main` import 兜底。
- `py_compile` 覆盖 `src/services/reminder_service.py`、`src/ui/main_window.py`、`main.py`。

验收重点：

- `ReminderService` 可 import。
- `ReminderService` 不依赖 UI、winsound、db_manager。
- `MainWindow` 外部行为不变。
- `ReminderPop` 无 diff。
- `main.py`、`requirements.txt`、`schedule.db` 无 diff。

### 5-6：第五轮整体验收与归档准备

目标：

- 汇总 5-0 到 5-5。
- 确认第五轮可归档进入第六轮 Controller / Router / EventBus 协调层。
- 更新当前轮次日志。

验收重点：

- 提醒扫描逻辑已从 `MainWindow` 中最小委托到 service。
- UI 副作用仍留在 UI 层。
- 弹窗和声音行为未改变。
- 已触发提醒去重状态仍只存在于本次运行内。
- 未新增数据库字段。
- 未新增提醒持久化。
- 未修改提醒选择页和弹窗 UI。
- `src/services/reminder_service.py` 是纯服务边界。
- `src/ui/main_window.py` 只做最小接入。
- `src/ui/reminder_pop.py` 无 diff。
- `main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。

---

## 第五轮整体验收标准

第五轮完成后必须确认：

- 应用仍可启动。
- 提醒每秒扫描仍由主窗口定时器驱动。
- 到点提醒仍弹窗。
- 强提醒仍播放系统声音。
- 关闭弹窗或停止闹钟仍停止声音。
- 同一日程本次运行内不重复弹出。
- 重启后去重状态不保留。
- 未到提醒、无提醒、超过 60 秒窗口均不触发。
- service 不依赖 QWidget、QTimer、winsound、ReminderPop、db_manager。
- 不新增数据库字段。
- 不修改 `db_manager` 对外 API。
- 不修改 `ReminderPop` UI。
- 不修改 `requirements.txt`。
- 不保留 `schedule.db` 变更。
- 第五轮可归档进入第六轮。

---

## 首个小工单建议

第五轮首个小工单应为：

`5-0：静态审查与只读基线定位`

原因：

- 提醒逻辑涉及定时器、弹窗、声音和内存去重，副作用边界必须先确认。
- `MainWindow.check_reminders()` 当前逻辑很短，适合小步抽取，但不适合直接迁移。
- `ReminderPop` 和 `winsound` 必须先明确保留在 UI 层，避免 service 被 UI 副作用污染。
- 先只读定位，后续才能安全拆分纯判断、运行期状态和 MainWindow 最小委托。

执行窗口在收到 5-0 正式提示词前，不得修改源码、数据库或除 `Work_Log.md` / `Work_Task_Prompts.md` 以外的管理文档。
