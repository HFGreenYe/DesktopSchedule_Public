# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 C-4：Repository 行为回归验收。

状态：顾问窗口已审查，提示词与 `Work_Instruction.md` 中 C-4 边界一致，可转执行窗口。

提示词：

~~~~markdown
请执行第二轮 C-4：Repository 行为回归验收。本轮只做行为回归验证，不做源码改动。

## 1. 本轮目标

验证 Repository 相关委托路径在 C-1 ~ C-3 依赖清理复核后没有行为回归。

重点验证：
- Repository / db_manager import 正常。
- 已委托读路径可用。
- 临时分类写入路径可用，并清理干净。
- 临时日程写入路径可用，并清理干净。
- GUI smoke test 可通过，或失败时记录原因并执行 import main 兜底。
- `src/ui`、`src/data`、`src/repositories`、`schedule.db` 最终无 tracked diff。

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

本轮允许为了验收进行临时数据库写入，但必须清理，并确认 `git diff --name-only -- schedule.db` 无输出。

禁止改源码、禁止改业务逻辑、禁止改 Repository 方法名/参数/返回语义、禁止改查询排序/过滤/删除策略。

若开工前已有管理文档 diff，需在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 验证 Repository 和 db_manager import。
2. 验证基础读路径：
   - get_all_schedules
   - get_schedules_for_date
   - get_active_categories
   - get_category_map
3. 验证分类临时写路径：
   - add_category
   - update_category_fields
   - soft_delete_category
   - hard_delete_category
4. 验证日程临时写路径：
   - add_schedule 创建 repeat_rule='none' 的临时日程
   - delete_schedule 删除临时日程
   - 删除后确认查询不到该临时 id
5. 执行 GUI smoke test；如失败，记录原因并执行 import main 兜底。
6. 检查源码、UI、数据库最终无 diff。
7. 不做任何代码修复。

## 4. 验收命令

1. import 验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories import ScheduleRepository, CategoryRepository; from src.repositories.schedule_repository import ScheduleRepository as SR; from src.repositories.category_repository import CategoryRepository as CR; from src.data.database import db_manager; print('imports ok'); print(ScheduleRepository is SR, CategoryRepository is CR); print('db_manager ok', db_manager is not None)"
```

2. 基础读路径验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; all_schedules=db_manager.get_all_schedules(); today=db_manager.get_schedules_for_date(date.today()); cats=db_manager.get_active_categories(); cmap=db_manager.get_category_map(); print('all schedules', len(all_schedules)); print('today schedules', len(today)); print('active categories', len(cats)); print('category map', len(cmap)); assert isinstance(all_schedules, list); assert isinstance(today, list); assert isinstance(cats, list); assert isinstance(cmap, dict)"
```

3. 临时分类写入/清理验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_c4_category_'+str(int(time.time())); cid=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created category', cid); assert cid is not None; cat=db_manager.get_category(cid); assert cat and cat.name == name; updated=db_manager.update_category_fields(cid, color='#0cc0df'); print('updated', updated); assert updated is True; soft=db_manager.soft_delete_category(cid); print('soft deleted', soft); assert soft is True; hard=db_manager.hard_delete_category(cid); print('hard deleted', hard); assert hard is True; assert db_manager.get_category(cid) is None"
```

4. 临时日程写入/清理验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_c4_schedule_'+str(int(time.time())); data={'title':name,'item_type':'schedule','priority':0,'repeat_rule':'none','description':'temporary c4 validation','category_id':None}; created=db_manager.add_schedule(data); print('created schedule', created); assert created is True; matches=[s for s in db_manager.get_all_schedules() if s.title==name]; print('matches', len(matches)); assert len(matches)==1; sid=matches[0].id; deleted=db_manager.delete_schedule(sid); print('deleted schedule', deleted); assert deleted is True; remaining=[s for s in db_manager.get_all_schedules() if s.id==sid]; print('remaining', len(remaining)); assert len(remaining)==0"
```

5. GUI smoke test：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); print('gui smoke ok'); w.close(); app.quit()"
```

如果 GUI smoke 因环境限制失败，记录原因并执行兜底：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import main; print('main import ok')"
```

6. diff 范围检查：

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

- 本轮任务名称：第二轮 C-4（Repository 行为回归验收）
- 开工前是否已有管理文档 diff
- 实际修改文件
- import 验证结果
- 基础读路径验证结果
- 临时分类写入/清理验证结果
- 临时日程写入/清理验证结果
- GUI smoke test 结果或 import main 兜底结果
- `src/repositories`、`src/data`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` diff 检查结果
- `git diff --name-only` 与 `git status --short --branch` 结果
- 未完成事项
- 风险或疑点，尤其是临时数据是否清理、schedule.db 是否无 tracked diff

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
~~~~

## 复核锚点

- C-4 允许临时写入数据库，但必须清理，最终 `schedule.db` 无 tracked diff。
- C-4 不允许源码改动；复核时重点检查 `src/repositories/`、`src/data/`、`src/ui/`、`main.py`、`requirements.txt`、`schedule.db` 均无 diff。
- 若 GUI smoke 失败，日志必须记录原因，并有 `import main` 兜底结果。
