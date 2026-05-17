请执行第三轮 3-1：服务骨架与边界确认。本轮只确认并建立第三轮必要的最小 service 边界，不迁移复杂逻辑，不接 UI。

## 1. 本轮目标

基于 `manage_instruction/Work_Instruction.md` 第三轮阶段合同，以及 `manage_instruction/Work_Log.md` 中 3-0 静态审查结论，确认第三轮后续服务抽取需要哪些最小 service 文件。

本轮重点：

- 确认查询过滤服务边界。
- 确认排序策略服务边界。
- 确认分类策略服务边界。
- 谨慎评估四象限服务是否现在需要创建。
- 新 service 必须可 import。
- 新 service 不得依赖 QWidget / PyQt UI。
- 旧 `db_manager` / repository / UI 调用路径保持不变。

本轮不迁移日期过滤、排序、分类状态、删除策略等具体业务逻辑；这些留给后续 3-2、3-3、3-4。

## 2. 允许/禁止

本轮允许修改：

- `src/services/schedule_query_service.py`（仅在确认 3-2 会立即承接时）
- `src/services/schedule_sort_service.py`（仅在确认 3-3 会立即承接时）
- `src/services/category_policy_service.py`（仅在确认 3-4 会立即承接时）
- `src/services/__init__.py`（仅做轻量导出，且必须无副作用）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮原则上不创建：

- `src/services/matrix_classification_service.py`

除非你能基于 3-0 结论明确说明它会在下一小工单立即承接稳定纯逻辑；否则只在日志中记录“四象限服务暂不创建，规则缺口留待 3-5”。

本轮禁止修改：

- `src/services/weather_service.py`
- `src/data/`
- `src/repositories/`
- `src/ui/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不接 UI。
- 不替换旧调用路径。
- 不修改 `db_manager` 对外 API。
- 不修改 Repository 方法名、参数、返回语义。
- 不迁移具体排序/过滤/分类策略逻辑。
- 不创建无明确后续承接目标的空壳文件。
- 不新增数据库字段。
- 不修改迁移逻辑。
- 不实现新功能。

若开工前已有管理文档 diff，需在 `Work_Log.md` 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取 `manage_instruction/Work_Instruction.md` 第三轮阶段合同。
2. 读取 `manage_instruction/Work_Log.md` 中第三轮 3-0 结论。
3. 基于 3-0 结论确认以下候选服务是否需要在本轮创建：
   - `schedule_query_service.py`
   - `schedule_sort_service.py`
   - `category_policy_service.py`
   - `matrix_classification_service.py`
4. 对确认需要创建的 service 文件，只建立最小可 import 边界：
   - 不导入 PyQt / QWidget。
   - 不导入 UI。
   - 不导入 `db_manager`。
   - 不导入 Repository。
   - 不写数据库。
   - 不实现复杂业务迁移。
5. 如果更新 `src/services/__init__.py`，只能做轻量导出，不得触发数据库、UI 或网络副作用。
6. 不修改 `weather_service.py`；最多在日志里记录它与第三轮无关。
7. 更新 `Work_Log.md`，说明：
   - 哪些 service 创建了。
   - 哪些 service 暂不创建。
   - 每个创建/不创建的依据。
   - 后续 3-2、3-3、3-4、3-5 分别承接什么。

## 4. 验收命令

读取合同和 3-0 结论：

Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8

检查 services 文件：

rg --files src/services
Get-Content -Path src\services\*.py -Encoding UTF8

import 验证：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import importlib; mods=['src.services.schedule_query_service','src.services.schedule_sort_service','src.services.category_policy_service']; existing=[]; missing=[]; [existing.append(m) if importlib.util.find_spec(m) else missing.append(m) for m in mods]; [importlib.import_module(m) for m in existing]; print('existing service imports ok:', existing); print('missing service modules:', missing)"

验证旧路径仍可用：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('db_manager import ok'); print('schedules', len(db_manager.get_all_schedules())); print('categories', len(db_manager.get_active_categories()))"

静态依赖检查，确认新 service 不依赖 UI / QWidget / db_manager / repository：

rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services

如果该命令只命中 `weather_service.py` 或无关既有内容，请在日志中说明；新建第三轮 service 文件不得命中上述依赖。

diff 范围检查：

git diff --name-only -- src/services/weather_service.py
git diff --name-only -- src/data
git diff --name-only -- src/repositories
git diff --name-only -- src/ui
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch

预期：

- `src/services/weather_service.py` 无 diff。
- `src/data` 无 diff。
- `src/repositories` 无 diff。
- `src/ui` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- 最终只允许必要的 `src/services/` 新增/轻量导出文件，以及 `manage_instruction/Work_Log.md`，必要时包含 `manage_instruction/Work_Task_Prompts.md`。

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第三轮 3-1（服务骨架与边界确认）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 读取的依据文件
- 基于 3-0 结论创建了哪些 service 文件
- 哪些候选 service 暂不创建及原因
- 是否修改 `src/services/__init__.py`
- 是否确认 `weather_service.py` 未改动
- service import 验证结果
- 旧 `db_manager` 路径验证结果
- 静态依赖检查结果
- diff 范围检查结果
- 后续 3-2 / 3-3 / 3-4 / 3-5 的承接建议
- 未完成事项
- 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
