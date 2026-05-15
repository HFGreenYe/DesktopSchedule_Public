# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 C-5：第二轮 C 整体验收与归档准备。

状态：顾问窗口已审查，提示词与 `Work_Instruction.md` 中 C-5 边界一致，可转执行窗口。

提示词：

~~~~markdown
请执行第二轮 C-5：第二轮 C 整体验收与归档准备。本轮只做整体验收和日志记录，不做任何代码改动。

## 1. 本轮目标

汇总并复核第二轮 C-1 到 C-4 的结果，为进入第二轮 D 做准备。

重点确认：
- Repository 不依赖 db_manager、UI 或 src.data.database。
- Repository 默认模型来源为 src.data.models。
- Repository 构造函数注入能力保留。
- src/repositories/__init__.py 只做轻量导出。
- ScheduleRepository、CategoryRepository、src.repositories、db_manager 可 import。
- 已委托读写路径关键验证通过。
- GUI smoke test 通过，或有 import main 兜底记录。
- src/repositories、src/data、src/ui、main.py、requirements.txt、schedule.db 无 diff。

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

禁止修改任何源码文件、数据库文件或业务逻辑。

若开工前已有管理文档 diff，需在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取 Work_Log.md 中 C-1 到 C-4 的记录。
2. 汇总 C-1 结论：Repository 静态依赖审查。
3. 汇总 C-2 结论：Repository import 残留修正是否无需改代码。
4. 汇总 C-3 结论：repositories/__init__.py 是否轻量导出。
5. 汇总 C-4 结论：Repository 行为回归验收是否通过。
6. 复跑最小关键验证：
   - repository import
   - db_manager import
   - 基础读路径
   - GUI smoke 或 import main 兜底
   - diff 范围
7. 记录是否可进入第二轮 D。
8. 不做任何代码修复。

## 4. 验收命令

1. Repository 与 db_manager import 验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories import ScheduleRepository, CategoryRepository; from src.repositories.schedule_repository import ScheduleRepository as SR; from src.repositories.category_repository import CategoryRepository as CR; from src.data.database import db_manager; print('imports ok'); print(ScheduleRepository is SR, CategoryRepository is CR); print('db_manager ok', db_manager is not None)"
```

2. 依赖边界静态复核：

```cmd
rg -n "db_manager|src\.ui|from .*data\.database|src\.data\.database|from .*database import" src/repositories
```

预期：无输出。

3. 模型来源与注入能力复核：

```cmd
rg -n "from src\.data\.models import|def __init__\(self, schedule_model=None\)|def __init__\(self, category_model=None, schedule_model=None\)" src/repositories
```

预期：能看到 models 导入和两个 Repository 的构造函数注入参数。

4. __init__.py 轻量导出复核：

```cmd
Get-Content -Path src\repositories\__init__.py -Encoding UTF8
rg -n "db_manager|src\.ui|src\.data\.database|from .*database import|import .*database" src/repositories/__init__.py
```

预期：__init__.py 只导出 Repository；静态检查无输出。

5. 基础读路径复核：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; all_schedules=db_manager.get_all_schedules(); today=db_manager.get_schedules_for_date(date.today()); cats=db_manager.get_active_categories(); cmap=db_manager.get_category_map(); print('all schedules', len(all_schedules)); print('today schedules', len(today)); print('active categories', len(cats)); print('category map', len(cmap)); assert isinstance(all_schedules, list); assert isinstance(today, list); assert isinstance(cats, list); assert isinstance(cmap, dict)"
```

6. GUI smoke test：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); print('gui smoke ok'); w.close(); app.quit()"
```

如果 GUI smoke 因环境限制失败，记录原因并执行兜底：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import main; print('main import ok')"
```

7. diff 范围检查：

```cmd
git diff --name-only -- src/repositories
git diff --name-only -- src/data
git diff --name-only -- src/ui
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch
```

预期：
- `src/repositories` 无 diff。
- `src/data` 无 diff。
- `src/ui` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- 最终只允许 `manage_instruction/Work_Log.md`，以及必要时的 `manage_instruction/Work_Task_Prompts.md`。

## 5. 日志要求

更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第二轮 C-5（第二轮 C 整体验收与归档准备）
- 开工前是否已有管理文档 diff
- 实际修改文件
- C-1 依赖审查结论
- C-2 import 残留修正确认结论
- C-3 __init__.py 轻量导出结论
- C-4 行为回归验收结论
- Repository 依赖边界最终结论
- import 验证结果
- 基础读路径复核结果
- GUI smoke test 结果或 import main 兜底结果
- diff 范围检查结果
- 是否可以进入第二轮 D
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
~~~~

## 复核锚点

- C-5 不允许源码、数据库或业务逻辑改动，只更新管理记录。
- 复核时重点确认 C-1 到 C-4 结论被准确汇总，并且最终判断是否可进入第二轮 D。
- 复核时重点检查 `src/repositories/`、`src/data/`、`src/ui/`、`main.py`、`requirements.txt`、`schedule.db` 均无 diff。
