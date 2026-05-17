请执行第三轮 3-5：四象限纯逻辑评估与最小服务准备。本轮以评估为主，默认不创建 service；只有确认存在稳定规则时，才允许创建最小纯逻辑 service。

## 1. 本轮目标

基于 `manage_instruction/Work_Instruction.md` 第三轮合同，以及 `Work_Log.md` 中 3-0 到 3-4b 的结论，重新审查当前项目里的四象限相关入口、文案、字段和 priority 使用方式，判断是否具备实现 `matrix_classification_service.py` 的稳定规则基础。

本轮核心问题：

- 当前是否已有稳定四象限分类规则？
- 现有字段是否足够支撑稳定规则？
- `priority` 当前语义是“紧急性/重要性/优先级”中的哪一种，是否一致？
- 是否应该在本轮创建 `matrix_classification_service.py`？
- 如果规则不足，应明确记录“不创建，不实现，缺口留待后续轮次”。

本轮不接四象限 UI，不实现新功能，不写数据库。

## 2. 允许/禁止

本轮默认允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

仅当确认存在稳定四象限纯逻辑规则时，额外允许新增：

- `src/services/matrix_classification_service.py`

本轮禁止修改：

- `src/ui/`
- `src/data/`
- `src/repositories/`
- `src/services/schedule_query_service.py`
- `src/services/schedule_sort_service.py`
- `src/services/category_policy_service.py`
- `src/services/weather_service.py`
- `src/services/__init__.py`（除非创建 matrix service 且确有轻量导出必要；默认不改）
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不接四象限 UI。
- 不修改任何 UI 文件。
- 不新增数据库字段。
- 不修改 `priority` 语义。
- 不修改现有排序、查询、过滤、分类策略。
- 不修改 Repository 或 Data 层。
- 不修改 `db_manager` API。
- 不写 `schedule.db`。
- 不伪实现四象限功能。
- 不为了创建文件而创建空壳 service。
- 不改变现有用户可见行为。

若开工前已有管理文档 diff，需在 `Work_Log.md` 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取 `manage_instruction/Work_Instruction.md` 第三轮合同。
2. 读取 `manage_instruction/Work_Log.md` 中 3-0 到 3-4b 结论。
3. 静态审查以下文件中的四象限入口、文案、字段和 priority 使用：
   - `src/ui/dashboard.py`
   - `src/ui/week_window.py`
   - `src/ui/month_window.py`
   - `src/ui/main_window.py`
   - `src/ui/todo_board.py`
   - `src/data/models.py`
4. 必须记录以下字段当前是否存在、当前含义是否明确：
   - `priority`
   - `start_time`
   - `end_time`
   - `status`
   - `created_at`
   - `sort_order`
5. 判断当前是否存在稳定四象限规则，例如：
   - 是否明确区分“重要/不重要”？
   - 是否明确区分“紧急/不紧急”？
   - `priority` 是否足以单独代表“重要性”？
   - `start_time/end_time` 是否足以稳定代表“紧急性”？
   - 当前 UI 文案是否已经表达完整规则？
6. 如果规则不足：
   - 不创建 `matrix_classification_service.py`。
   - 只在 `Work_Log.md` 记录结论：暂不实现，缺口留待后续轮次。
7. 如果确实发现已有稳定规则：
   - 先在 `Work_Log.md` 说明依据。
   - 最多创建 `src/services/matrix_classification_service.py`。
   - 该 service 必须是纯逻辑，不依赖 UI、db_manager、Repository。
   - 不接 UI，不写数据库，不新增字段。
8. 更新 `Work_Log.md`。

## 4. 建议静态审查命令

读取第三轮合同和近期日志：

Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8

定位四象限入口、文案和 priority 使用：

rg -n "四象限|象限|priority|urgent|important|matrix|quadrant|重要|紧急" src/ui/dashboard.py src/ui/week_window.py src/ui/month_window.py src/ui/main_window.py src/ui/todo_board.py src/data/models.py

读取重点文件相关内容：

Get-Content -Path src\data\models.py -Encoding UTF8
Get-Content -Path src\ui\dashboard.py -Encoding UTF8
Get-Content -Path src\ui\week_window.py -Encoding UTF8
Get-Content -Path src\ui\month_window.py -Encoding UTF8
Get-Content -Path src\ui\main_window.py -Encoding UTF8
Get-Content -Path src\ui\todo_board.py -Encoding UTF8

检查是否已有 matrix service：

rg --files src/services
rg -n "matrix|quadrant|四象限|象限" src/services src

## 5. 验收命令

默认情况下，本轮不应创建源码文件。执行范围检查：

git diff --name-only -- src/ui
git diff --name-only -- src/data
git diff --name-only -- src/repositories
git diff --name-only -- src/services/schedule_query_service.py
git diff --name-only -- src/services/schedule_sort_service.py
git diff --name-only -- src/services/category_policy_service.py
git diff --name-only -- src/services/weather_service.py
git diff --name-only -- src/services/__init__.py
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch

默认预期：

- `src/ui` 无 diff。
- `src/data` 无 diff。
- `src/repositories` 无 diff。
- 既有 service 无 diff。
- `src/services/__init__.py` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- 最终只允许：
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

如果创建了 `src/services/matrix_classification_service.py`，必须额外执行：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.services.matrix_classification_service import MatrixClassificationService; print('matrix service import ok', MatrixClassificationService)"

rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/matrix_classification_service.py

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src\services\matrix_classification_service.py

并且 diff 范围最多允许：

- `src/services/matrix_classification_service.py`
- `manage_instruction/Work_Log.md`
- 必要时 `manage_instruction/Work_Task_Prompts.md`

## 6. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第三轮 3-5（四象限纯逻辑评估与最小服务准备）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 已读取的关键文件
- 当前四象限入口位置
- 当前四象限相关文案
- 当前 `priority` 使用位置和语义判断
- 当前字段可用性：
  - `priority`
  - `start_time`
  - `end_time`
  - `status`
  - `created_at`
  - `sort_order`
- 是否存在稳定四象限分类规则
- 如果规则不足，明确记录：
  - 不创建 `matrix_classification_service.py`
  - 不接四象限 UI
  - 不实现新功能
  - 缺口留待后续轮次
- 如果创建了 matrix service，记录：
  - 创建依据
  - service 输入/输出
  - import 验证结果
  - 静态依赖检查结果
  - py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
