# Work Instruction

用途：本文件用于“当前阶段”的执行指令发布。

- 仅保留正在执行或即将执行的任务。
- 已完成阶段请归档到 `History_Instruction.md`，避免本文件长期堆积。
- 当前主路线图见 `Work_Formulation.md` 的“架构改写轮次路线图”。
- 改写前行为和目录快照见 `Work_Snapshot.md`。
- 执行过程记录写入 `Work_Log.md`。

---

# 当前阶段：第四轮 - 日程写入与重复规则服务

## 已完成并归档

- 第一轮：基建 + repository + db_manager 兼容委托。
- 第二轮：Data 层整理与模型拆分。
  - 第二轮 A/B/C/D 均已完成并归档。
  - 第二轮最终验收通过，`src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。
- 第三轮：纯业务查询与排序服务。
  - 第三轮 3-0 ~ 3-6 均已完成并归档。
  - 已完成 `ScheduleQueryService`、`ScheduleSortService`、`CategoryPolicyService` 的服务边界和关键纯逻辑抽取。
  - 四象限纯逻辑已完成评估，因规则合同不足，暂未创建 `matrix_classification_service.py`。
  - 第三轮最终验收通过，`src`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

---

## 第四轮目标

第四轮目标是把日程写入和重复规则相关逻辑，从 `DatabaseManager` 中逐步拆到 service 层，但继续保留 `db_manager` 作为旧 UI 的兼容门面。

本轮重点处理：

- `DatabaseManager.add_schedule(data)`
- `DatabaseManager.update_schedule_with_repeat(schedule_id, new_data, update_future=False)`
- `_add_months` 或重复日期计算逻辑
- `repeat_rule` 旧语义和规则值映射
- `group_id`、`update_future` 的旧行为基线
- `parent_id` 是否存在及是否参与旧行为
- 重复日程生成数量、日期偏移、批量插入、未来实例删除/重建行为

本轮风险高，必须先做静态审查和只读基线定位，再逐步抽取纯逻辑和写入协调。不得一上来迁移复杂写入逻辑。

---

## 第四轮允许修改范围

第四轮整体允许修改：

- `src/services/schedule_service.py`
- `src/services/schedule_repeat_service.py` 或等价重复规则服务文件
- `src/data/database.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

如具体小工单明确需要，允许读取但默认不修改：

- `src/data/models.py`
- `src/repositories/schedule_repository.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- `src/ui/main_window.py`
- `src/ui/week_window.py`
- `src/ui/todo_board.py`
- `src/ui/schedule_detail_pop.py`
- `src/ui/month_window.py`

---

## 第四轮禁止事项

- 不修改 `src/ui/`，除非后续小工单明确只是只读审查；第四轮默认不做 UI 调用替换。
- 不修改 `main.py`。
- 不修改 `requirements.txt`。
- 不修改 `Work_Snapshot.md`。
- 不修改 `Work_Formulation.md`。
- 不新增数据库字段。
- 不修改数据库字段含义、表名、默认值、迁移逻辑。
- 不新增 `parent_id` 字段；当前模型未发现 `parent_id`，第四轮只记录事实，不补模型。
- 不改变 `db_manager` 对外公开方法名、参数、返回语义。
- 不改变 UI 行为、弹窗流程、编辑流程、添加页流程。
- 不迁移提醒逻辑。
- 不迁移 Controller / Router / EventBus。
- 不处理四象限 UI。
- 不保留 `schedule.db` 变更；如验收需要临时写入，必须清理并确认 `git diff --name-only -- schedule.db` 无输出。

---

## 行为保持原则

第四轮所有改动必须满足：

- `db_manager` 仍是旧 UI 调用入口。
- `add_schedule(data)` 成功/失败返回语义保持：成功 `True`，失败 `False`。
- `update_schedule_with_repeat(schedule_id, new_data, update_future)` 成功/失败返回语义保持：成功 `True`，失败 `False`。
- 单次日程新增行为不变。
- `每天 / 每周 / 每月` 重复生成行为不变。
- `每年 / yearly` 如 4-0 确认无旧实现，本轮不得新增或伪实现。
- `daily / weekly / monthly / yearly` 如 4-0 确认无旧实现，本轮不得新增或伪实现。
- 重复日程生成数量、时间偏移、`group_id` 分配保持旧行为。
- `update_future=False`：只改当前条；如原来属于循环组，当前条脱离 `group_id`。
- `update_future=True`：影响当前及未来，沿用或创建 `group_id`，删除旧未来实例，再重建新未来实例。
- UI 中可能存在的内存态同步行为必须先记录，再决定是否需要保留在旧 UI 层；第四轮默认不改 UI。
- 临时写库验收必须清理临时数据。
- 每个小工单结束必须确认 `git diff --name-only -- schedule.db` 无输出。

---

## 第四轮小工单拆分草案

第四轮采用 `4-0`、`4-1` 等编号。执行时仍可根据基线结果继续拆分更小工单，不得为了匹配编号一次迁移过多逻辑。

### 4-0：静态审查与只读基线定位

目标：

- 不改代码。
- 不写数据库。
- 定位当前 `add_schedule`、`update_schedule_with_repeat`、`_add_months`、重复规则 UI 来源。
- 明确当前支持的 `repeat_rule` 实际值。
- 明确 `daily / weekly / monthly / yearly`、`每年` 是否存在旧实现。
- 明确 `group_id`、`parent_id` 是否实际存在。
- 定位 UI 中对 `update_future` 和 `group_id` 的内存态同步逻辑。

必须定位：

- `src/data/database.py`
- `src/data/models.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- `src/ui/main_window.py`
- `src/ui/week_window.py`
- `src/ui/todo_board.py`
- `src/ui/schedule_detail_pop.py`
- `src/ui/month_window.py`

重点搜索：

- `add_schedule`
- `update_schedule_with_repeat`
- `_add_months`
- `repeat_rule`
- `group_id`
- `parent_id`
- `update_future`
- `editing_schedule.group_id = None`
- `p.data.group_id = None`
- `daily`
- `weekly`
- `monthly`
- `yearly`
- `每天`
- `每周`
- `每月`
- `每年`

验收重点：

- 输出规则值清单。
- 记录非重复值是否为 `none / 无 / 不重复 / ''`。
- 记录重复值是否实际只有 `每天 / 每周 / 每月`。
- 记录 `每年 / yearly / daily / weekly / monthly` 是否无旧生成逻辑。
- 记录当前模型是否只有 `group_id`、没有 `parent_id`。
- 记录 UI 内存态同步位置，例如 `if not update_future: ... group_id = None`。
- `src`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

### 4-1：重复日期计算纯逻辑抽取

目标：

- 只抽 `_add_months` 和日期偏移计算。
- 新建最小纯逻辑 service，例如 `schedule_repeat_service.py`。
- 不改 `add_schedule`。
- 不改 `update_schedule_with_repeat`。
- 不写数据库。

验收重点：

- 月末规则保持：如 1 月 31 日加 1 月落到 2 月最后一天。
- 闰年规则保持旧逻辑。
- `start_time`、`end_time`、`reminder_time` 的偏移逻辑一致。
- service 不依赖 UI / db_manager / Repository。
- `schedule.db` 无 diff。

### 4-2：重复规则待插入数据计划服务

目标：

- 抽取“根据 base data + repeat_rule 生成待插入数据列表”的纯逻辑。
- 只生成待插入数据计划。
- 不决定数据库事务边界。
- 不执行数据库写入。
- 事务和写库协调暂留 `DatabaseManager`，直到后续小工单明确迁移。
- 只支持当前旧规则，不新增未实现规则。

验收重点：

- `none / 无 / 不重复 / ''` 按旧语义不进入重复批量生成。
- `每天` 生成原始项 + 365 个未来项，共 366 条计划。
- `每周` 生成原始项 + 52 个未来项，共 53 条计划。
- `每月` 生成原始项 + 12 个未来项，共 13 条计划。
- `每年 / yearly / daily / weekly / monthly` 如无旧实现，只记录不支持，不新增行为。
- 生成计划中 `group_id` 语义与旧逻辑一致。
- 不写数据库。

### 4-3：add_schedule 非重复路径委托

目标：

- 只处理 `add_schedule` 的非重复路径。
- `DatabaseManager.add_schedule` 仍对外不变。
- 可让 service 判断是否非重复，DatabaseManager 保持实际写入。
- 不影响重复规则路径。

验收重点：

- 用临时单次日程验证创建和删除。
- 不改变默认字段。
- 不影响 `每天 / 每周 / 每月` 重复路径。
- 临时数据清理后 `schedule.db` 无 tracked diff。

### 4-4：add_schedule 重复路径委托

目标：

- 将重复日程生成计划委托给 service。
- DatabaseManager 仍负责事务和批量插入，除非小工单进一步明确迁移写入协调。
- 不改变生成数量和 `group_id` 语义。

验收重点：

- 用临时日程分别验证 `每天 / 每周 / 每月`。
- 验证同一批生成项 `group_id` 一致。
- 验证生成数量和日期偏移。
- 验证 `每年 / yearly` 不被新增支持。
- 验证后按 `group_id` 清理临时数据。
- `schedule.db` 无 tracked diff。

### 4-5：update_schedule_with_repeat 的 update_future=False 路径

目标：

- 只处理“仅修改当前这一条”路径。
- 不碰影响未来的删除/重建逻辑。
- 保持 `update_future=False` 时当前条脱离旧 `group_id` 的语义。

验收重点：

- 临时重复组中选一条修改。
- 验证该条按旧语义脱离 `group_id`。
- 验证同组其他未来项不被修改或删除。
- 如 UI 侧也有内存态同步，本轮只记录，不改 UI。
- 清理全部临时数据。
- `schedule.db` 无 tracked diff。

### 4-6：update_schedule_with_repeat 的 update_future=True 非组转重复路径

目标：

- 只处理“原本非重复，修改为重复并影响未来”的路径。
- 验证新 `group_id` 创建和未来实例生成。

验收重点：

- 临时单次日程改为重复。
- 验证当前条获得 `group_id`。
- 验证未来实例生成数量和时间偏移。
- 验证规则仅限旧支持值。
- 清理临时组。
- `schedule.db` 无 tracked diff。

### 4-7：update_schedule_with_repeat 的既有重复组未来更新路径

目标：

- 处理已有 `group_id` 时影响当前及未来。
- 保持旧逻辑：删除旧未来实例，重建新未来实例。
- 不改变过去实例处理规则。

风险控制：

- 本工单风险最高。
- 如果 4-0 或前置验收无法明确旧行为，必须先拆成：
  - `4-7a`：基线写入验证，只用临时数据验证旧行为，不改代码。
  - `4-7b`：在基线明确后再做委托改造。
- 不得在基线不清楚时直接迁移。

验收重点：

- 临时重复组中选中间一条。
- 验证早于当前的同组项保留。
- 验证当前条更新。
- 验证当前之后旧未来项删除并按新规则重建。
- 清理临时数据。
- `schedule.db` 无 tracked diff。

### 4-8：update_schedule_with_repeat 取消重复路径

目标：

- 处理重复改为 `none / 无 / 不重复 / ''`。
- 验证当前条 `group_id=None`。
- 验证未来实例删除行为保持旧语义。

验收重点：

- 临时重复组取消重复。
- 验证当前条脱离 `group_id`。
- 验证未来项按旧逻辑删除。
- 清理临时数据。
- `schedule.db` 无 tracked diff。

### 4-9：第四轮整体验收

目标：

- 汇总 4-0 到 4-8。
- 验证 `add_schedule` 和 `update_schedule_with_repeat` 关键路径。
- 确认第四轮可归档。

验收重点：

- service 可 import。
- service 不依赖 QWidget。
- `db_manager.add_schedule` API 不变。
- `db_manager.update_schedule_with_repeat` API 不变。
- 单次、每天、每周、每月旧行为不变。
- `每年 / yearly / daily / weekly / monthly` 如无旧实现，明确记录未实现且未新增。
- `parent_id` 如不存在，明确记录未新增。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。

---

## 第四轮整体验收标准

第四轮完成后必须确认：

- `db_manager.add_schedule(data)` 对外行为不变。
- `db_manager.update_schedule_with_repeat(schedule_id, new_data, update_future)` 对外行为不变。
- 临时写库测试全部清理。
- 非重复新增、重复新增、仅当前修改、影响未来修改、取消重复均通过验证。
- `group_id` 旧语义保持。
- 当前模型未发现 `parent_id` 时，已记录“不存在，不纳入第四轮实现”。
- 无 `每年 / yearly` 旧行为时，已记录“不新增，不伪实现”。
- 不新增数据库字段。
- 不修改 UI。
- `src/ui`、`main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。
- 第四轮可归档进入第五轮提醒服务。

---

## 首个小工单建议

第四轮首个小工单应为：

`4-0：静态审查与只读基线定位`

原因：

- 当前 `add_schedule` 与 `update_schedule_with_repeat` 是高风险写入路径。
- 重复规则实际支持值需要先以代码为准确认。
- UI 中存在 `update_future` 与 `group_id` 的内存态同步逻辑，必须先定位。
- 先只读定位，后续才能设计可清理的临时写库验收。

执行窗口在收到 4-0 正式提示词前，不得修改源码、数据库或管理文档以外文件。
