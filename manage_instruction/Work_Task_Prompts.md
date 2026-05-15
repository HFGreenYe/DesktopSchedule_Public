# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 C-1：Repository 静态依赖审查。

状态：顾问窗口已审查，提示词与 `Work_Instruction.md` 中 C-1 边界一致，可转执行窗口。

提示词：

~~~~markdown
请执行第二轮 C-1：Repository 静态依赖审查。本轮只做静态审查，不改源码。

## 1. 本轮目标

检查 Repository 当前依赖关系是否符合第二轮 C 的边界要求。

重点检查：
- src/repositories/schedule_repository.py
- src/repositories/category_repository.py
- src/repositories/__init__.py

确认它们是否依赖：
- db_manager
- src.ui 或任何 UI 模块
- src.data.database
- 从 database.py 导入 Schedule 或 Category

同时确认：
- Repository 默认模型来源是否为 src.data.models。
- ScheduleRepository 是否保留 schedule_model 构造函数注入能力。
- CategoryRepository 是否保留 category_model / schedule_model 构造函数注入能力。
- repositories/__init__.py 是否可 import。

## 2. 允许/禁止

本轮允许修改：
- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在需要维护本轮复核锚点时）

本轮禁止修改：
- src/repositories/
- src/data/
- src/ui/
- main.py
- src/theme/
- src/utils/signals.py
- requirements.txt
- schedule.db
- Work_Snapshot.md
- Work_Formulation.md

禁止修改任何源码文件。本轮如果发现问题，只记录问题，不自行修复。

若开工前已有管理文档 diff，需在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 静态检查 src/repositories/schedule_repository.py。
2. 静态检查 src/repositories/category_repository.py。
3. 静态检查 src/repositories/__init__.py。
4. 确认 repository 文件是否存在 db_manager、UI、src.data.database 或从 database.py 导入模型的痕迹。
5. 确认 repository 文件是否从 src.data.models 导入 Schedule / Category。
6. 确认构造函数注入能力是否保留。
7. 不做任何代码修复。

## 4. 验收命令

1. 检查 repository 是否依赖 db_manager、UI、database.py：

```cmd
rg -n "db_manager|src\.ui|from .*data\.database|src\.data\.database|from .*database import" src/repositories
```

预期：没有输出。若有输出，请记录具体文件和行号，不要修复。

2. 检查 repository 是否从 models.py 导入模型：

```cmd
rg -n "from src\.data\.models import|from \.\.data\.models import|from .*models import" src/repositories
```

预期：能看到 ScheduleRepository / CategoryRepository 中的模型导入。

3. 检查构造函数注入能力：

```cmd
rg -n "def __init__\(self, schedule_model=None\)|def __init__\(self, category_model=None, schedule_model=None\)" src/repositories
```

预期：能看到两个 Repository 的构造函数注入参数。

4. import 验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories.schedule_repository import ScheduleRepository; from src.repositories.category_repository import CategoryRepository; import src.repositories as repos; print('repository imports ok'); print(ScheduleRepository is not None, CategoryRepository is not None, repos is not None)"
```

5. 验证禁止范围无改动：

```cmd
git diff --name-only -- src/repositories
git diff --name-only -- src/data
git diff --name-only -- src/ui
git diff --name-only -- main.py
git diff --name-only -- schedule.db
```

6. 验证本轮修改范围：

```cmd
git diff --name-only
```

预期只包含：
- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（如本轮维护了复核锚点）
- 开工前已存在的管理文档 diff（如有，需在日志中单独记录）

## 5. 日志要求

更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第二轮 C-1（Repository 静态依赖审查）
- 实际修改文件
- 开工前是否已有管理文档 diff
- Repository 当前依赖关系结论
- 是否发现 repository 依赖 db_manager
- 是否发现 repository 依赖 UI
- 是否发现 repository 依赖 src.data.database 或从 database.py 导入模型
- 是否确认默认模型来源为 src.data.models
- 是否确认构造函数注入能力保留
- 验证命令和结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
~~~~

## 复核锚点

- C-1 是纯静态审查；执行窗口不得修改源码或修复 import。
- 若发现 repository 依赖问题，只记录到 `Work_Log.md`，后续由 C-2 决定是否修正。
- 复核时重点检查 `src/repositories/`、`src/data/`、`src/ui/`、`main.py`、`schedule.db` 均无 diff。
