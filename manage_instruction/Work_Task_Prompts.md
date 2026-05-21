# Work Task Prompts

## 第五轮 5-1 提示词（ReminderService 骨架与纯判断函数）

### 1. 本轮目标

- 本工单为实现工单：新增提醒服务骨架与纯判断辅助函数。
- 只建立 `ReminderService` 的纯逻辑边界，不接入 `MainWindow`。
- 不修改任何 `src/ui/*` 文件。
- 不改变现有提醒弹窗、声音播放、QTimer 扫描、去重行为。

### 2. 允许/禁止

- 允许新增：`src/services/reminder_service.py`
- 必要时允许修改：`src/services/__init__.py`
- 允许更新：`manage_instruction/Work_Log.md`
- 禁止修改：`src/ui/*`
- 禁止修改：`main.py`
- 禁止修改：`requirements.txt`
- 禁止修改：`schedule.db`
- 禁止修改本提示词文件 `manage_instruction/Work_Task_Prompts.md`；如发现提示词问题，只能在 `Work_Log.md` 记录并交回顾问/决策窗口处理。
- 禁止新增依赖。
- 禁止接入 `MainWindow`。
- 禁止提前实现运行期去重状态，`mark_triggered`、`collect_due_schedules` 留到 5-2。
- 禁止生成完整弹窗 dict，完整 dict 构造留到 5-4。
- service 不得依赖 `QWidget`、`QTimer`、`winsound`、`ReminderPop`、`db_manager`。

### 3. 具体任务

- 新建 `src/services/reminder_service.py`。
- 定义 `ReminderService`，只包含纯判断/纯选择辅助。
- 至少提供以下能力，命名可略作调整，但语义必须清楚：
  - 判断日程是否有 `reminder_time`。
  - 计算 `now - reminder_time` 的秒差。
  - 判断是否处于旧触发窗口：`0 <= diff < 60`。
  - 判断某个日程在当前时间是否满足提醒触发条件；该判断不得考虑运行期去重，也不得写入任何状态。
  - 选择 `target_time`：`start_time if start_time else end_time`。
- 纯函数应可接受轻量假对象，不要求 Peewee 模型实例。
- 对无 `reminder_time` 的对象，应返回“不触发”而不是抛出异常。
- 对缺少 `start_time` / `end_time` 的对象，`target_time` 选择辅助应保持旧语义：无开始时间则取结束时间，二者都无则返回 `None`。
- 如修改 `src/services/__init__.py`，只做轻量导出，不引入 UI 或数据库依赖。

### 4. 验收命令

- 开工前记录：`git status --short`
- 实现后至少执行：`.\.venv\Scripts\python.exe -m py_compile src/services/reminder_service.py`
- 如当前 venv Python 因本地环境问题不可用，可改用可用解释器执行等价 `py_compile`，并在日志中说明。
- 执行 service import 验证：`.\.venv\Scripts\python.exe -c "from src.services.reminder_service import ReminderService; print('reminder service import ok')"`
- 执行轻量假对象验证，至少覆盖：
  - 无提醒：不触发。
  - 未到提醒时间：不触发。
  - 到点且处于 60 秒窗口内：触发。
  - 超过 60 秒窗口：不触发。
  - `target_time` 优先取 `start_time`。
  - 无 `start_time` 时取 `end_time`。
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
- `src/ui` 无 diff。
- `main.py`、`requirements.txt`、`schedule.db` 无由本工单产生的新 diff。

### 5. 日志要求

- 在 `manage_instruction/Work_Log.md` 新增 `5-1` 记录，至少包含：
  - 本轮任务名与边界。
  - 开工前 git 状态基线。
  - 实际新增/修改文件。
  - `ReminderService` 提供的纯函数/方法清单。
  - 明确记录本轮未做事项：
    - 未接入 `MainWindow`。
    - 未修改 `src/ui/*`。
    - 未实现运行期去重状态。
    - 未生成完整弹窗 dict。
    - 未迁移声音播放。
  - 假对象验证结果。
  - py_compile / import / 静态依赖检查结果。
  - diff 范围检查结果。
  - 风险与后续建议，供 5-2 使用。

### 6. 提交要求

- 本工单完成后不要提交 Git。
- 完成后等待顾问窗口审核。