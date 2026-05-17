请执行第四轮 4-0：静态审查与只读基线定位。本轮只做代码阅读、静态搜索和日志记录，不修改源码，不写数据库。

## 1. 本轮目标

基于 `manage_instruction/Work_Instruction.md` 的第四轮阶段合同，定位当前项目中日程写入与重复规则相关旧行为，为后续高风险写入路径拆分做基线准备。

本轮重点定位：

- `DatabaseManager.add_schedule(data)`
- `DatabaseManager.update_schedule_with_repeat(schedule_id, new_data, update_future=False)`
- `_add_months`
- `repeat_rule` 实际支持值
- `group_id` 旧语义
- `parent_id` 是否存在
- `update_future` 调用与语义
- UI 中 `group_id` 内存态同步逻辑，例如：
  - `editing_schedule.group_id = None`
  - `p.data.group_id = None`
  - `dragged_item.group_id = None`
  - `group_id=None`

本轮只记录事实，不修复、不抽取、不创建 service、不运行写库验证。

## 2. 允许/禁止

本轮允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不修改源码。
- 不创建 `schedule_service.py`。
- 不创建 `schedule_repeat_service.py`。
- 不修改 `database.py`。
- 不修改 UI。
- 不运行 `add_schedule`。
- 不运行 `update_schedule_with_repeat`。
- 不写入、删除、更新任何数据库记录。
- 不新增数据库字段。
- 不实现 `daily / weekly / monthly / yearly`。
- 不实现 `每年`。
- 不新增 `parent_id`。
- 不改变任何业务行为。

若开工前已有管理文档 diff，需在 `Work_Log.md` 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取 `manage_instruction/Work_Instruction.md` 第四轮阶段合同。
2. 静态审查 `src/data/database.py`：
   - 定位 `_add_months`。
   - 定位 `add_schedule`。
   - 定位 `update_schedule_with_repeat`。
   - 记录重复规则生成数量。
   - 记录事务和批量插入位置。
   - 记录未来实例删除/重建逻辑。
3. 静态审查 `src/data/models.py`：
   - 确认 `Schedule` 字段。
   - 记录是否存在 `group_id`。
   - 记录是否存在 `parent_id`。
   - 记录 `repeat_rule` 字段默认值。
4. 静态审查 UI 中重复规则来源和调用点：
   - `src/ui/add_view.py`
   - `src/ui/add_view_week.py`
   - `src/ui/main_window.py`
   - `src/ui/week_window.py`
   - `src/ui/todo_board.py`
   - `src/ui/schedule_detail_pop.py`
   - `src/ui/month_window.py`
5. 定位所有 `repeat_rule` 相关值：
   - 非重复值：`none / 无 / 不重复 / ''`
   - 重复值：`每天 / 每周 / 每月`
   - 检查是否存在 `每年`
   - 检查是否存在 `daily / weekly / monthly / yearly`
6. 定位所有 `update_future` 调用和分支。
7. 定位所有 UI 内存态同步：
   - `editing_schedule.group_id = None`
   - `p.data.group_id = None`
   - `dragged_item.group_id = None`
   - `group_id=None`
   - 其他直接修改对象 `group_id` 的逻辑。
8. 记录哪些行为适合后续 4-1 / 4-2 / 4-3 等小工单处理。
9. 更新 `Work_Log.md`。

## 4. 建议静态搜索命令

读取第四轮合同：

Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8

定位核心写入路径：

rg -n "def add_schedule|def update_schedule_with_repeat|def _add_months|repeat_rule|group_id|parent_id|update_future" src/data src/ui

定位重复规则实际值：

rg -n "每天|每周|每月|每年|不重复|无|none|daily|weekly|monthly|yearly" src

定位 UI 内存态同步：

rg -n "editing_schedule\.group_id|p\.data\.group_id|dragged_item\.group_id|group_id\s*=\s*None|group_id=None|update_future" src/ui

重点读取文件：

Get-Content -Path src\data\database.py -Encoding UTF8
Get-Content -Path src\data\models.py -Encoding UTF8
Get-Content -Path src\ui\add_view.py -Encoding UTF8
Get-Content -Path src\ui\add_view_week.py -Encoding UTF8
Get-Content -Path src\ui\main_window.py -Encoding UTF8
Get-Content -Path src\ui\week_window.py -Encoding UTF8
Get-Content -Path src\ui\todo_board.py -Encoding UTF8
Get-Content -Path src\ui\schedule_detail_pop.py -Encoding UTF8
Get-Content -Path src\ui\month_window.py -Encoding UTF8

检查是否已有第四轮 service：

rg --files src/services
rg -n "schedule_service|schedule_repeat_service|Repeat|repeat" src/services

## 5. 验收命令

本轮不应产生源码或数据库 diff。执行范围检查：

git diff --name-only -- src
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch

预期：

- `src` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- 最终只允许：
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 6. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第四轮 4-0（静态审查与只读基线定位）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 已读取的关键文件
- `_add_months` 当前位置和行为摘要
- `add_schedule` 当前位置和行为摘要
- `update_schedule_with_repeat` 当前位置和行为摘要
- 当前非重复规则值清单
- 当前重复规则值清单
- `每天 / 每周 / 每月` 生成数量
- `每年 / yearly / daily / weekly / monthly` 是否存在旧生成逻辑
- `group_id` 字段和行为位置
- `parent_id` 是否存在
- `update_future` 调用位置和分支语义
- UI 中 `group_id` 内存态同步位置
- 事务和批量插入位置
- 未来实例删除/重建逻辑位置
- 后续建议拆分小工单
- diff 范围检查结果
- 未完成事项
- 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
