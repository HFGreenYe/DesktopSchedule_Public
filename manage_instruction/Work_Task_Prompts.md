# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 A-4：调整 `ScheduleRepository` 模型导入来源。

状态：等待执行窗口执行，执行后由顾问窗口复核。

## 正式执行提示词

~~~text
请执行第二轮 A-4：只调整 ScheduleRepository 的模型导入来源，不执行 A-5/A-6，也不执行第二轮 B/C/D。

本轮允许修改：
- src/repositories/schedule_repository.py
- manage_instruction/Work_Log.md

本轮禁止修改：
- src/repositories/category_repository.py
- src/data/database.py
- src/data/models.py
- src/data/connection.py
- src/ui/
- main.py
- src/theme/
- src/utils/signals.py
- requirements.txt
- schedule.db
- Work_Snapshot.md
- Work_Formulation.md
- Work_Task_Prompts.md

原则：
- 只把 ScheduleRepository 中从 src.data.database 延迟导入 Schedule 的位置，改为从 src.data.models 导入 Schedule。
- 保留构造函数注入能力，schedule_model 参数仍然可用。
- 不改变任何 Repository 方法名、参数、返回值语义、排序逻辑、过滤逻辑、CRUD 行为。
- 不修改 CategoryRepository。
- 不做额外重构。
- 不改数据库字段、迁移逻辑或业务逻辑。

具体任务：
1. 在 src/repositories/schedule_repository.py 中定位 ScheduleRepository.__init__。
2. 将 schedule_model is None 时的 Schedule 导入来源改为 src.data.models。
3. 保持 self._schedule_model = schedule_model 的注入逻辑不变。
4. 不修改其他方法实现。

验收要求：

1. Repository import 和默认模型来源验证：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories.schedule_repository import ScheduleRepository; from src.data.models import Schedule; repo=ScheduleRepository(); print('schedule repo import ok'); print('uses models Schedule:', repo._schedule_model is Schedule)"

2. db_manager 基础读取验证：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; print('db import ok'); print('all schedules', len(db_manager.get_all_schedules())); print('today schedules', len(db_manager.get_schedules_for_date(date.today())))"

3. 静态检查 ScheduleRepository 不再从 database.py 导入 Schedule：

rg -n "from src\.data\.database import Schedule|from \.\.data\.database import Schedule|from \.database import Schedule" src/repositories/schedule_repository.py

预期：没有输出。

4. 验证禁止文件无改动：

git diff --name-only -- src/repositories/category_repository.py
git diff --name-only -- src/data/database.py
git diff --name-only -- src/data/models.py
git diff --name-only -- src/data/connection.py
git diff --name-only -- src/ui
git diff --name-only -- schedule.db

5. 验证本轮修改范围：

git diff --name-only

预期只包含：
- src/repositories/schedule_repository.py
- manage_instruction/Work_Log.md

更新 manage_instruction/Work_Log.md，至少记录：
- 本轮任务名称：第二轮 A-4（ScheduleRepository 模型导入来源调整）
- 实际修改文件
- 修改内容说明
- 是否保留构造函数注入能力
- 验证命令和结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
~~~

## 复核锚点

- 只允许修改 `src/repositories/schedule_repository.py` 和 `manage_instruction/Work_Log.md`。
- `ScheduleRepository.__init__` 默认导入来源应改为 `src.data.models.Schedule`。
- `schedule_model` 注入能力必须保留。
- 不得修改 `CategoryRepository`、`src/data/*`、`src/ui/`、`schedule.db`。
