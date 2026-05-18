# Work Log

本文件只记录当前阶段/当前轮次的执行日志。

历史日志已归档到 `manage_instruction/History_Log.md`。

## 当前状态

第一轮：基建 + repository + db_manager 兼容委托，已完成并归档。

第二轮：Data 层整理与模型拆分，已完成并归档。

第三轮：纯业务查询与排序服务，已完成并归档。

第四轮（日程写入与重复规则服务）已启动。

当前已完成 4-1（重复日期计算纯逻辑抽取），等待顾问窗口复核与后续 4-2 小工单发布。

## 当前轮次注意事项

- 4-1 只抽取重复日期计算纯逻辑，不写数据库，不改变写入流程、事务边界或生成数量。
- 后续第四轮涉及 `add_schedule`、`update_schedule_with_repeat`、重复规则日期计算等高风险写入逻辑，必须继续拆成多个小工单推进。
- 执行窗口不得沿用第三轮 3-6 或第三轮任一提示词继续执行。
- 执行窗口不得在未收到 4-1 正式提示词前自行开始写入路径改造。

## 2026-05-17 第四轮 4-0（静态审查与只读基线定位）

- 本轮任务名称：第四轮 4-0（静态审查与只读基线定位）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 4-0 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 已读取的关键文件：
  - `manage_instruction/Work_Instruction.md`
  - `manage_instruction/Work_Log.md`
  - `src/data/database.py`
  - `src/data/models.py`
  - `src/ui/add_view.py`
  - `src/ui/add_view_week.py`
  - `src/ui/main_window.py`
  - `src/ui/week_window.py`
  - `src/ui/todo_board.py`
  - `src/ui/schedule_detail_pop.py`
  - `src/ui/month_window.py`
  - `src/services/` 文件清单（核对第四轮 service 是否已存在）
- `_add_months` 当前位置和行为摘要：
  - 位置：`src/data/database.py:85`。
  - 行为：按 `year/month/day` 重新计算目标日期；使用目标月最大天数兜底（如 1 月 31 日 +1 月落到 2 月最后一天）；返回 `sourcedate.replace(...)`。
  - 目前仅被 `add_schedule` 与 `update_schedule_with_repeat` 的“每月”分支调用。
- `add_schedule` 当前位置和行为摘要：
  - 位置：`src/data/database.py:97`。
  - 非重复路径：`rule in ('none','无','不重复','')` 时直接 `Schedule.create(**data)`，成功 `True`，异常 `False`。
  - 重复路径：
    - 先创建 `group_id = uuid4` 并写入当前 data。
    - `schedules_to_insert` 先放当前这条，再生成未来条目。
    - 生成数量控制：`每天=365`、`每周=52`、`每月=12`（加上当前条，总数分别 366/53/13）。
    - 时间偏移：`每天/每周` 用 `timedelta`；`每月` 用 `_add_months`。
    - 批量写入：`with db.atomic()` + `Schedule.insert_many(batch)`，`batch_size=100`。
- `update_schedule_with_repeat` 当前位置和行为摘要：
  - 位置：`src/data/database.py:160`。
  - 输入：`(schedule_id, new_data, update_future=False)`。
  - 分支语义：
    - `update_future=False`：只更新当前条；若旧条有 `group_id`，先把 `new_data['group_id']=None`，实现脱离循环。
    - `update_future=True`：影响当前及未来。
      - 若旧条无 `group_id` 且新规则是重复，则新建 `group_id`；否则沿用旧 `group_id`。
      - 当前条先更新；若新规则非重复则当前条 `group_id=None`。
      - 若旧条原本属于组：先删除“未来同组实例”（按 `start_time` 或 `end_time` 或 `id` 回退分支）。
      - 若新规则是重复：重建未来实例（不含当前条，数量分别 365/52/12）。
  - 返回：成功 `True`，异常 `False`。
- 当前非重复规则值清单：
  - `none`
  - `无`
  - `不重复`
  - `''`（空字符串）
  - 证据位置：`src/data/database.py`（`add_schedule` 与 `update_schedule_with_repeat` 分支条件），以及 UI 判定分支。
- 当前重复规则值清单：
  - `每天`
  - `每周`
  - `每月`
  - 证据位置：`src/data/database.py` 生成分支；`src/ui/add_view.py`、`src/ui/add_view_week.py`、`src/ui/schedule_detail_pop.py` 下拉选项。
- `每天 / 每周 / 每月` 生成数量：
  - `add_schedule`：未来生成 365/52/12，加当前条总计 366/53/13。
  - `update_schedule_with_repeat(update_future=True)`：未来重建 365/52/12（当前条已单独 update）。
- `每年 / yearly / daily / weekly / monthly` 是否存在旧生成逻辑：
  - 在 `src` 范围内未检出上述规则实现（`rg -n "\\b(daily|weekly|monthly|yearly)\\b|每年" src` 无输出）。
  - 结论：当前旧生成逻辑仅覆盖中文 `每天/每周/每月`。
- `group_id` 字段和行为位置：
  - 字段：`src/data/models.py:40`，`Schedule.group_id = CharField(null=True, index=True)`。
  - 迁移：`src/data/database.py:27-33` 含 group_id 字段迁移逻辑。
  - 行为：
    - 新建重复组时分配 `uuid`。
    - `update_future=False` 下脱组（`group_id=None`）。
    - `update_future=True` 下沿用或创建组，并删除/重建未来实例。
    - UI 存在内存态同步（见下文）。
- `parent_id` 是否存在：
  - `src` 全局未命中 `parent_id`（`rg -n "parent_id" src` 无输出）。
  - `Schedule` 模型无 `parent_id` 字段。
- `update_future` 调用位置和分支语义：
  - 数据层分支：`src/data/database.py:167`（仅当前）与 `:173`（影响未来）。
  - UI 调用点：
    - `src/ui/main_window.py:323/410/476` 闭包 `_do_update(update_future)` -> `db_manager.update_schedule_with_repeat(...)`。
    - `src/ui/week_window.py:819/867/912` 同结构。
    - `src/ui/todo_board.py:1624` 同结构。
    - `src/ui/schedule_detail_pop.py:573-601` 根据弹窗选择与规则切换计算 `update_future` 后调用。
  - UI 通用拦截器：`_check_repeat_and_execute`（main/week/todo_board）在“重复日程”提示框里把“修改所有”映射 `True`、“仅修改本次”映射 `False`。
- UI 中 `group_id` 内存态同步位置：
  - `editing_schedule.group_id = None`：
    - `src/ui/main_window.py:331/419/483`
    - `src/ui/week_window.py:827/876/919`
    - `src/ui/todo_board.py:1632`
  - `p.data.group_id = None`：`src/ui/todo_board.py:1644`
  - `dragged_item.group_id = None`：`src/ui/week_window.py:1300`
  - `group_id=None` 直接写库参数：`src/ui/week_window.py:1309`
- 事务和批量插入位置：
  - `add_schedule`：`with db.atomic()` + `insert_many` 分批（`src/data/database.py`）。
  - `update_schedule_with_repeat`：仅“未来重建插入”段使用 `with db.atomic()` + `insert_many` 分批；当前条 update 与旧未来 delete 不在同一显式原子块中。
- 未来实例删除/重建逻辑位置：
  - 删除旧未来：`src/data/database.py:191-206`，按 `start_time` / `end_time` / `id` 分支删除同组未来条目。
  - 重建新未来：`src/data/database.py:211-253`，按新规则生成并批量插入。
- 后续建议拆分小工单：
  - `4-1`：仅抽 `_add_months` 与重复日期偏移纯逻辑（不写库）。
  - `4-2`：仅抽“重复计划生成器”（输出待插入数据，不落库）。
  - `4-3`：`add_schedule` 非重复路径委托。
  - `4-4`：`add_schedule` 重复路径委托（保持 366/53/13）。
  - `4-5`：`update_future=False` 路径委托（保持脱组语义）。
  - `4-6`：非组改重复且影响未来路径。
  - `4-7`：已有组的未来删除/重建路径（建议先 `4-7a` 纯基线验证，再 `4-7b` 改造）。
  - `4-8`：取消重复路径（`none/无/不重复/''`）。
- diff 范围检查结果：
  - `git diff --name-only -- src` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`（写入本日志后另含 `manage_instruction/Work_Log.md`）。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`（写入本日志后另含 `M manage_instruction/Work_Log.md`）。
- 未完成事项：
  - 待顾问窗口确认 4-1 拆单边界（是否先只抽日期偏移，还是先做重复计划生成）。
- 风险或疑点：
  - 当前 `update_schedule_with_repeat` 的“更新当前 + 删除旧未来 + 重建新未来”不在同一大事务块，后续拆分时需谨慎保持失败回滚语义。
  - UI 已存在多处 `group_id` 内存态同步，后续若改数据层行为，需同步核对这些 UI 假设是否仍成立。
  - 当前无 `parent_id`；后续工单不得隐式引入“父子实例”新语义。

## 2026-05-18 第四轮 4-1（重复日期计算纯逻辑抽取）

- 本轮任务名称：第四轮 4-1（重复日期计算纯逻辑抽取）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 4-1 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/services/schedule_repeat_service.py`（新增）
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- service 方法清单与输入/输出说明：
  - `ScheduleRepeatService.add_months(sourcedate, months)`：输入 datetime/None 与整月偏移；输出偏移后的 datetime/None；保持月末与闰年兼容。
  - `ScheduleRepeatService.shift_datetime(value, rule, step)`：输入 datetime/None、规则（仅 `每天/每周/每月`）与步长；输出偏移后的 datetime/None。
  - `ScheduleRepeatService.shift_triplet(start_time, end_time, reminder_time, rule, step)`：输入三元时间与规则步长；输出偏移后三元组。
- `database.py` 委托点位置：
  - `_add_months` 改为委托 `ScheduleRepeatService.add_months`。
  - `add_schedule` 的未来偏移段改为调用 `ScheduleRepeatService.shift_triplet(...)`。
  - `update_schedule_with_repeat` 的未来重建偏移段改为调用 `ScheduleRepeatService.shift_triplet(...)`。
- 明确记录：未改写入流程、未改事务边界、未改生成数量。
  - `add_schedule` 仍保持 `loop_count: 每天365/每周52/每月12`，仍用 `with db.atomic()` + `insert_many` 分批写入。
  - `update_schedule_with_repeat` 仍保持旧分支结构（仅当前/影响未来）、旧删除旧未来与重建未来流程，未来重建仍保持 `loop_count: 每天365/每周52/每月12`。
  - 未改 `group_id` 语义。
- 月末与闰年一致性验证结果：
  - 命令（legacy 对照）通过，`month rows` 全部 `True`。
  - 样例包含：
    - `2023-01-31 +1月 -> 2023-02-28`
    - `2024-01-31 +1月 -> 2024-02-29`
    - `2024-02-29 +12月 -> 2025-02-28`
- `start_time/end_time/reminder_time` 偏移一致性验证结果：
  - 输出：
    - `每天 1 -> 2026-02-01 09:00 / 10:00 / 2026-01-31 09:00`
    - `每周 2 -> 2026-02-14 09:00 / 10:00 / 2026-02-13 09:00`
    - `每月 1 -> 2026-02-28 09:00 / 10:00 / 2026-02-28 09:00`
- service import 验证结果：
  - 输出：`repeat service import ok <class 'src.services.schedule_repeat_service.ScheduleRepeatService'>`。
- service 静态依赖检查结果：
  - 命令：`rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_repeat_service.py`
  - 结果：无输出（退出码 1，符合预期）。
- 未新增 `每年/yearly/daily/weekly/monthly` 行为说明：
  - 命令：`rg -n "每年|yearly|daily|weekly|monthly" src/services/schedule_repeat_service.py src/data/database.py`
  - 结果：无输出（退出码 1）。
  - 结论：未引入英文规则分支，未新增 `每年/yearly` 行为。
- py_compile 结果：
  - `python -m py_compile src/services/schedule_repeat_service.py src/data/database.py` 通过（无输出）。
- diff 范围检查结果：
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`、`src/data/database.py`、`src/services/schedule_repeat_service.py`（写入本日志后另含 `manage_instruction/Work_Log.md`）。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`、`M src/data/database.py`、`?? src/services/schedule_repeat_service.py`（写入本日志后另含 `M manage_instruction/Work_Log.md`）。
- 未完成事项：
  - 等待顾问窗口复核并下发 4-2（重复规则待插入数据计划服务）或其他后续小工单。
- 风险或疑点：
  - 当前 `shift_datetime` 对未知规则返回原值仅作防御兜底；数据库层仍只在 `每天/每周/每月` 分支调用，未改变现有规则面。
  - `update_schedule_with_repeat` 仍保留原有“更新/删除/重建”事务边界现状，后续拆分时需继续保持行为一致。
