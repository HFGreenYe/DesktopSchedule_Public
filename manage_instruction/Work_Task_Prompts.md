# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 D-1：Data 层静态边界与 import 复核。

状态：顾问窗口已审查，提示词与 `Work_Instruction.md` 中 D-1 边界一致，可转执行窗口。

提示词：

~~~~markdown
请执行第二轮 D-1：Data 层静态边界与 import 复核。本轮只做静态边界与 import 验证，不做任何源码改动。

## 1. 本轮目标

复核第二轮 A/B/C 后的核心 Data 层边界是否稳定。

重点确认：
- src.data.connection 可 import。
- src.data.models 可 import。
- src.data.database 可 import。
- ScheduleRepository、CategoryRepository、src.repositories 可 import。
- db_manager 可 import。
- src.data.connection.db 与 src.data.database.db 是同一个对象。
- src.data.connection.DB_PATH 与 src.data.database.DB_PATH 一致。
- Repository 不依赖 db_manager、UI 或 src.data.database。
- src/repositories/__init__.py 只做轻量导出。

本轮不做代码修复。如果发现问题，只记录问题和风险。

## 2. 允许/禁止

本轮允许修改：
- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在需要维护本轮复核锚点时）

本轮禁止修改：
- src/
- main.py
- requirements.txt
- schedule.db
- Work_Snapshot.md
- Work_Formulation.md

禁止修改任何源码文件、数据库文件、业务逻辑、UI 文件。

若 import 后发现 schedule.db 出现 diff，立即记录为异常，不自行修复。

若开工前已有管理文档 diff，需在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 验证 connection/models/database/repositories/db_manager import。
2. 验证 db 对象一致性。
3. 验证 DB_PATH 一致性。
4. 静态检查 repository 文件中是否存在 db_manager、UI、src.data.database 或 database.py 模型导入。
5. 静态检查 repositories/__init__.py 是否存在 db_manager、UI、src.data.database 或重型导入。
6. 检查源码、UI、数据库无 diff。
7. 不做任何代码改动。

## 4. 验收命令

1. import、db 对象和 DB_PATH 一致性验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.connection import db as db1, DB_PATH as p1; from src.data.models import BaseModel, Category, Schedule; from src.data.database import db as db2, DB_PATH as p2, db_manager; from src.repositories import ScheduleRepository, CategoryRepository; import src.repositories as repos; print('imports ok'); print('same db object:', db1 is db2); print('same DB_PATH:', p1 == p2); print('repositories ok:', ScheduleRepository is not None, CategoryRepository is not None, repos is not None); print('db_manager ok:', db_manager is not None)"
```

2. 静态检查 repository 不依赖 db_manager、UI、src.data.database：

```cmd
rg -n "db_manager|src\.ui|from .*data\.database|src\.data\.database|from .*database import" src/repositories
```

预期：无输出。

3. 静态检查 repositories/__init__.py 轻量导出：

```cmd
Get-Content -Path src\repositories\__init__.py -Encoding UTF8

rg -n "db_manager|src\.ui|src\.data\.database|from .*database import|import .*database" src/repositories/__init__.py
```

预期：__init__.py 只导出 ScheduleRepository / CategoryRepository；rg 无输出。

4. 确认 repository 模型来源与注入能力仍存在：

```cmd
rg -n "from src\.data\.models import|def __init__\(self, schedule_model=None\)|def __init__\(self, category_model=None, schedule_model=None\)" src/repositories
```

预期：能看到 models 导入和两个 Repository 构造函数注入参数。

5. diff 范围检查：

```cmd
git diff --name-only -- src/data
git diff --name-only -- src/repositories
git diff --name-only -- src/ui
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch
```

预期：
- src/data 无 diff。
- src/repositories 无 diff。
- src/ui 无 diff。
- main.py 无 diff。
- requirements.txt 无 diff。
- schedule.db 无 tracked diff。
- 最终只允许 manage_instruction/Work_Log.md，以及必要时的 manage_instruction/Work_Task_Prompts.md。

## 5. 日志要求

更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第二轮 D-1（Data 层静态边界与 import 复核）
- 开工前是否已有管理文档 diff
- 实际修改文件
- import 验证结果
- db 对象一致性验证结果
- DB_PATH 一致性验证结果
- Repository 依赖静态检查结果
- repositories/__init__.py 轻量导出检查结果
- Repository 模型来源与构造函数注入能力检查结果
- schedule.db 是否无 tracked diff
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
~~~~

## 复核锚点

- D-1 只做静态边界与 import 验证，不允许源码、数据库或业务逻辑改动。
- 复核时重点确认 `src.data.connection.db` 与 `src.data.database.db` 同对象、`DB_PATH` 一致。
- 复核时重点检查 Repository 无 `db_manager`、UI、`src.data.database` 依赖，`src/repositories/__init__.py` 只做轻量导出。
- 复核时重点检查 `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 均无 diff。
