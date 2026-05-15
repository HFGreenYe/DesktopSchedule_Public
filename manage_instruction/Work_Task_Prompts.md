# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 C-2：Repository 依赖残留修正（条件执行）。

状态：顾问窗口已审查，并按 `Work_Instruction.md` 中 C-2 边界做了轻微收窄：执行窗口只允许修改 `Work_Log.md`，以及仅在发现残留问题时修改两个 repository 文件；`Work_Task_Prompts.md` 由顾问窗口维护，不列入执行窗口允许修改范围。

提示词：

~~~~markdown
请执行第二轮 C-2：Repository 依赖残留修正（条件执行）。本轮优先复核，不默认改代码。

【本轮目标】
基于 C-1 日志结论，确认 repositories 是否仍存在残留依赖问题。
- 若无残留问题：本轮不改源码，只记录“C-2 无需修正”。
- 若有残留问题：仅最小修正 `schedule_repository.py` / `category_repository.py` 中的残留导入问题。

【允许修改】
- `src/repositories/schedule_repository.py`（仅在发现残留问题时）
- `src/repositories/category_repository.py`（仅在发现残留问题时）
- `manage_instruction/Work_Log.md`

【禁止修改】
- `src/repositories/__init__.py`（这是 C-3 再处理）
- `src/data/`
- `src/ui/`
- `main.py`
- `src/theme/`
- `src/utils/signals.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

【执行步骤】
1. 先读取 `manage_instruction/Work_Log.md` 最新 C-1 记录，确认 C-1 结论。
2. 复跑静态检查：
```cmd
rg -n "db_manager|src\.ui|from .*data\.database|src\.data\.database|from .*database import" src/repositories
```
3. 复跑模型来源检查：
```cmd
rg -n "from src\.data\.models import|from \.\.data\.models import|from .*models import" src/repositories
```
4. 复跑构造注入检查：
```cmd
rg -n "def __init__\(self, schedule_model=None\)|def __init__\(self, category_model=None, schedule_model=None\)" src/repositories
```
5. import 验证：
```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories.schedule_repository import ScheduleRepository; from src.repositories.category_repository import CategoryRepository; import src.repositories as repos; print('repository imports ok'); print(ScheduleRepository is not None, CategoryRepository is not None, repos is not None)"
```

【执行分支】
- 分支 A（预期）：
  - 若第 2 步无输出，且第 3/4/5 步均通过；
  - 不修改任何源码；
  - 仅在 `Work_Log.md` 记录“C-2 无需修正”。
- 分支 B（仅当发现问题）：
  - 若第 2 步出现命中；
  - 仅在 `schedule_repository.py` / `category_repository.py` 做最小修正；
  - 不做重构，不改方法签名/排序/过滤/CRUD 语义；
  - 修正后必须重跑第 2~5 步并记录结果。

【范围检查】
```cmd
git diff --name-only -- src/repositories
git diff --name-only -- src/data
git diff --name-only -- src/ui
git diff --name-only -- main.py
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch
```

【预期】
- 分支 A（本轮大概率）：
  - `src/repositories` 无 diff；
  - 最终仅允许 `manage_instruction/Work_Log.md` diff。
- 分支 B：
  - 仅允许 `schedule_repository.py` / `category_repository.py` 与 `manage_instruction/Work_Log.md` diff。

【Work_Log.md 记录要求】
至少记录：
- 本轮任务名称：第二轮 C-2（Repository 依赖残留修正，条件执行）
- 开工前是否已有管理文档 diff
- C-1 结论复核结果
- 静态检查/模型来源/注入能力/import 验证结果
- 是否进入“无需修正”分支
- 若有修正，记录具体文件与具体改动点
- diff 范围检查结果
- 未完成事项
- 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
~~~~

## 复核锚点

- C-2 预期走“无需修正”分支，只更新 `Work_Log.md`。
- 如果执行窗口修改了源码，必须能对应到静态检查命中的残留导入问题，否则视为越界。
- 复核时重点检查 `src/repositories/__init__.py`、`src/data/`、`src/ui/`、`main.py`、`schedule.db` 均无 diff。
