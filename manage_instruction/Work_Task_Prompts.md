# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 C-3：repositories/__init__.py 轻量导出复核。

状态：顾问窗口已审查，提示词与 `Work_Instruction.md` 中 C-3 边界一致，可转执行窗口。

提示词：

~~~~markdown
请执行第二轮 C-3：repositories/__init__.py 轻量导出复核。本轮优先复核，不默认改代码。

## 1. 本轮目标

检查 src/repositories/__init__.py 是否只做轻量导出，不触发数据库连接、db_manager 创建、UI 导入、src.data.database 导入或其他重型副作用。

本轮预期：
- 如果 __init__.py 已经只做轻量导出，则不改源码，只在 Work_Log.md 记录“C-3 无需整理”。
- 如果发现 __init__.py 存在重型副作用或错误导入，仅做最小导出关系整理。

## 2. 允许/禁止

本轮允许修改：
- src/repositories/__init__.py（仅在发现问题时）
- manage_instruction/Work_Log.md

本轮禁止修改：
- src/repositories/category_repository.py
- src/repositories/schedule_repository.py
- src/data/
- src/ui/
- main.py
- src/theme/
- src/utils/signals.py
- requirements.txt
- schedule.db
- Work_Snapshot.md
- Work_Formulation.md
- Work_Task_Prompts.md

禁止新增抽象基类，禁止做 repository 大重构，禁止改变 Repository 方法名、参数、返回语义、排序、过滤、删除策略。

若开工前已有管理文档 diff，需在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取 src/repositories/__init__.py。
2. 检查它是否只导出 ScheduleRepository 和 CategoryRepository。
3. 检查它是否导入或触发：
   - db_manager
   - src.ui 或任何 UI 模块
   - src.data.database
   - 数据库连接/建表/迁移
4. 如果没有问题，不修改源码，只记录“C-3 无需整理”。
5. 如果有问题，仅最小整理 __init__.py 的导出关系。
6. 不修改两个 repository 实现文件。

## 4. 验收命令

1. 查看 __init__.py 内容：

```cmd
Get-Content -Path src\repositories\__init__.py -Encoding UTF8
```

2. 静态检查 __init__.py 不导入 db_manager、UI、src.data.database：

```cmd
rg -n "db_manager|src\.ui|src\.data\.database|from .*database import|import .*database" src/repositories/__init__.py
```

预期：无输出。

3. import 验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories import ScheduleRepository, CategoryRepository; print('repositories package import ok'); print(ScheduleRepository is not None, CategoryRepository is not None)"
```

4. 单独 import 验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories.schedule_repository import ScheduleRepository; from src.repositories.category_repository import CategoryRepository; print('repository modules import ok'); print(ScheduleRepository is not None, CategoryRepository is not None)"
```

5. db_manager import 验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('db_manager import ok'); print('all schedules', len(db_manager.get_all_schedules()))"
```

6. 范围检查：

```cmd
git diff --name-only -- src/repositories/category_repository.py
git diff --name-only -- src/repositories/schedule_repository.py
git diff --name-only -- src/data
git diff --name-only -- src/ui
git diff --name-only -- main.py
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch
```

预期：
- 如果无需代码改动，最终只允许 manage_instruction/Work_Log.md diff。
- 如果确有最小整理，最终只允许 src/repositories/__init__.py 和 manage_instruction/Work_Log.md diff。

## 5. 日志要求

更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第二轮 C-3（repositories/__init__.py 轻量导出复核）
- 开工前是否已有管理文档 diff
- 实际修改文件
- __init__.py 当前导出内容
- 是否发现 db_manager、UI、src.data.database 或重型副作用导入
- 是否进入“无需整理”分支
- 若有整理，记录具体改动点
- import 验证结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
~~~~

## 复核锚点

- C-3 预期走“无需整理”分支，只更新 `Work_Log.md`。
- 如果执行窗口修改 `src/repositories/__init__.py`，必须能对应到轻量导出复核发现的问题，否则视为越界。
- 复核时重点检查 `src/repositories/category_repository.py`、`src/repositories/schedule_repository.py`、`src/data/`、`src/ui/`、`main.py`、`schedule.db` 均无 diff。
