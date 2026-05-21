# Work Task Prompts

## 第五轮 5-4 提示词（提醒弹窗数据构造边界收口）

### 1. 本轮目标

- 本工单为实现工单：将提醒弹窗 `data_dict` 的纯构造逻辑收口到 `ReminderService`。
- 仅处理“弹窗数据构造边界”，不改提醒扫描主流程语义。
- 保留 `MainWindow.show_reminder_popup(schedule)` 作为弹窗显示与声音副作用入口。
- 保持提醒触发窗口 `0 <= now - reminder_time < 60` 不变。

### 2. 允许/禁止

- 允许修改：`src/services/reminder_service.py`
- 允许修改：`src/ui/main_window.py`
- 允许更新：`manage_instruction/Work_Log.md`
- 禁止修改：`src/ui/reminder_pop.py`
- 禁止修改：除 `src/ui/main_window.py` 外的任何 `src/ui/*`
- 禁止修改：`main.py`
- 禁止修改：`requirements.txt`
- 禁止修改：`schedule.db`
- 禁止修改本提示词文件 `manage_instruction/Work_Task_Prompts.md`；如发现提示词问题，只能在 `Work_Log.md` 记录并交回顾问/决策窗口处理。
- 禁止新增依赖。
- 禁止把 `winsound.PlaySound(...)`、`ReminderPop`、`QTimer` 迁移到 service。
- 禁止新增提醒持久化字段、表或数据库迁移。
- 禁止改变 `check_reminders()` 的扫描、筛选、弹窗、标记顺序。
- 禁止修改 `show_reminder_popup` 的弹窗创建、显示和声音播放副作用边界。
- service 不得依赖 `QWidget`、`QTimer`、`winsound`、`ReminderPop`、`db_manager`。

### 3. 具体任务

- 在 `ReminderService` 新增纯函数，命名可调整，例如 `build_reminder_popup_data(schedule)`，用于构造弹窗 dict。
- dict 字段必须保持为：
  - `title`
  - `is_alarm`
  - `target_time`
- 字段取值语义必须保持：
  - `title = schedule.title`
  - `is_alarm = schedule.is_alarm`
  - `target_time = schedule.start_time if schedule.start_time else schedule.end_time`
- `target_time` 可复用 5-1 已有的 `select_target_time(schedule)`，但不得改变其旧语义。
- `MainWindow.show_reminder_popup()` 改为调用 `ReminderService` 的纯构造函数获得 `data_dict`，再继续执行：
  - `ReminderPop(data_dict)`
  - `self.current_popup.show()`
- `is_alarm` 为真时，声音播放逻辑仍保留在 `MainWindow.show_reminder_popup()`。
- 若需兼容空字段，不得改变旧行为边界；`target_time` 允许为 `None`。
- 不得在 service 中创建弹窗、播放声音、读取数据库、读取全局配置或访问 Qt 对象。

### 4. 验收命令

- 开工前记录：`git status --short`
- 实现后优先执行：
  - `.\.venv\Scripts\python.exe -m py_compile src/services/reminder_service.py src/ui/main_window.py`
  - `.\.venv\Scripts\python.exe -c "from src.services.reminder_service import ReminderService; print('reminder service import ok')"`
- 若 `.venv` 在工具环境报 `Unable to create process`，允许使用 bundled Python 复验并在日志留痕。
- 执行轻量假对象验证，至少覆盖：
  - `start_time` 存在时，`target_time` 等于 `start_time`。
  - `start_time` 为空且 `end_time` 存在时，`target_time` 等于 `end_time`。
  - `start_time` / `end_time` 都为空时，`target_time` 为 `None`。
  - `title` 与 `is_alarm` 原样来自 schedule 对象。
  - dict key 精确等于 `title`、`is_alarm`、`target_time`，不得新增或遗漏字段。
- 执行静态依赖检查：
  - `rg -n "QWidget|QTimer|winsound|ReminderPop|db_manager|src\.ui|PyQt|PySide" src/services/reminder_service.py`
  - 期望无输出；`rg` 无匹配返回码 1 视为通过。
- 执行范围检查：
  - `git diff --name-only -- src/ui`
  - 期望仅出现 `src/ui/main_window.py`。
  - `git diff --name-only -- main.py requirements.txt schedule.db`
  - 期望无输出。
- 建议用静态阅读确认：
  - `show_reminder_popup()` 仍创建 `ReminderPop(data_dict)` 并调用 `show()`。
  - `winsound.PlaySound(...)` 仍只在 `MainWindow.show_reminder_popup()` 中按 `schedule_data.is_alarm` 判断后调用。
  - `check_reminders()` 的 `collect -> show -> mark` 顺序未改变。

验收标准：

- `ReminderService` 提供弹窗 dict 纯构造方法。
- 构造出的 dict 字段和值与旧 `MainWindow.show_reminder_popup()` 内联构造完全一致。
- `MainWindow.show_reminder_popup()` 仍负责创建 `ReminderPop`、显示弹窗和播放声音。
- `check_reminders()` 扫描和去重接线语义未改变。
- service 不依赖 UI、声音、db_manager。
- `src/ui/reminder_pop.py` 无 diff。
- `src/ui` diff 除 `main_window.py` 外无其它文件。
- `main.py`、`requirements.txt`、`schedule.db` 无由本工单产生的新 diff。

### 5. 日志要求

- 在 `manage_instruction/Work_Log.md` 新增 `5-4` 记录，至少包含：
  - 本轮任务名与边界。
  - 开工前 git 状态基线。
  - 实际新增/修改文件。
  - `ReminderService` 新增的弹窗数据构造方法说明。
  - `show_reminder_popup` 保持不变的副作用边界说明（弹窗 + 声音）。
  - 假对象验证结果。
  - py_compile / import / 静态依赖检查结果。
  - diff 范围检查结果。
  - 明确记录本轮未做事项：
    - 未修改 `ReminderPop`。
    - 未迁移声音播放。
    - 未迁移 QTimer。
    - 未改变 `check_reminders()` 扫描/标记顺序。
    - 未新增提醒持久化。
  - 风险与后续建议，供 5-5 使用。
  - 特别记录：本工单完成后不要提交 Git，等待顾问窗口审核。

### 6. 提交要求

- 执行窗口不得提交 Git。
- 本工单完成后等待顾问窗口审核。
- Git 提交只能由用户在顾问验收后执行。