# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 D-5：GUI smoke 与第二轮整体验收收口。

状态：顾问窗口已审查并补充进度估算要求，提示词与 `Work_Instruction.md` 中 D-5 边界一致，可转执行窗口。

提示词：

~~~~markdown
请执行第二轮 D-5：GUI smoke 与第二轮整体验收收口。本轮只做最终验收与日志记录，不改源码。

## 1. 本轮目标

汇总 D-1 ~ D-4 的验收结果，确认第二轮 Data 层整理可以归档，并为进入第三轮规划做准备。

重点确认：
- D-1 静态边界与 import 复核已通过。
- D-2 读路径回归验收已通过。
- D-3 分类写路径临时验收已通过并清理。
- D-4 日程写路径临时验收已通过并恢复/清理。
- GUI smoke test 可通过，或失败时有 import main 兜底。
- src/data、src/repositories、src/ui、main.py、requirements.txt、schedule.db 无 diff。
- 第二轮可归档，后续可进入第三轮规划。
- 估算当前进度占总规划进度的百分比。

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

若开工前已有管理文档 diff，需在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取 Work_Log.md 中 D-1 ~ D-4 的记录。
2. 汇总每轮结论：
   - D-1：静态边界与 import
   - D-2：读路径
   - D-3：分类写路径
   - D-4：日程写路径
3. 复跑最小 import 验证。
4. 复跑最小读路径验证。
5. 执行 GUI smoke test；如失败，记录原因并执行 import main 兜底。
6. 检查源码、UI、数据库无 diff。
7. 记录是否可以归档第二轮并进入第三轮规划。
8. 记录当前进度估算：
   - 按 `Work_Formulation.md` 的至少 8 轮架构迁移口径，D-5 通过后约为 25%。
   - 若把第九轮及后续新功能轮也算入总目标，当前约为 22%，且后续功能范围未完全定稿。
9. 不做任何代码修复。

## 4. 验收命令

1. 最小 import 验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.connection import db as db1, DB_PATH as p1; from src.data.database import db as db2, DB_PATH as p2, db_manager; from src.data.models import Category, Schedule; from src.repositories import ScheduleRepository, CategoryRepository; print('imports ok'); print('same db object:', db1 is db2); print('same DB_PATH:', p1 == p2); print('repos ok:', ScheduleRepository is not None, CategoryRepository is not None); print('db_manager ok:', db_manager is not None)"
```

2. 最小读路径验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; all_schedules=db_manager.get_all_schedules(); today=db_manager.get_schedules_for_date(date.today()); cats=db_manager.get_active_categories(); cmap=db_manager.get_category_map(); print('all schedules', len(all_schedules)); print('today schedules', len(today)); print('active categories', len(cats)); print('category map', len(cmap)); assert isinstance(all_schedules, list); assert isinstance(today, list); assert isinstance(cats, list); assert isinstance(cmap, dict)"
```

3. GUI smoke test：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); print('gui smoke ok'); w.close(); app.quit()"
```

如果 GUI smoke 因环境限制失败，记录原因并执行兜底：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import main; print('main import ok')"
```

4. diff 范围检查：

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

- 本轮任务名称：第二轮 D-5（GUI smoke 与第二轮整体验收收口）
- 开工前是否已有管理文档 diff
- 实际修改文件
- D-1 验收结论摘要
- D-2 验收结论摘要
- D-3 验收结论摘要
- D-4 验收结论摘要
- 最小 import 验证结果
- 最小读路径验证结果
- GUI smoke test 结果或 import main 兜底结果
- src/data、src/repositories、src/ui、main.py、requirements.txt、schedule.db diff 检查结果
- 是否可以归档第二轮并进入第三轮规划
- 当前进度估算及估算口径
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
~~~~

## 复核锚点

- D-5 只做最终验收与日志记录，不允许源码、数据库或业务逻辑改动。
- 复核时重点确认 D-1 ~ D-4 结论被准确汇总。
- 复核时重点确认 GUI smoke 通过，或失败时有 `import main` 兜底。
- 复核时重点检查 `schedule.db`、`src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt` 均无 diff。
- 复核时确认进度估算口径：8 轮架构迁移口径 D-5 后约 25%；含第九轮及后续功能轮约 22%，且功能轮范围未完全定稿。
