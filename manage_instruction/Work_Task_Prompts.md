# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 B-4：database.py 迁移入口与职责复核。

状态：等待执行窗口执行，执行后由顾问窗口复核。

## 正式执行提示词

```text
请执行第二轮 B-4：database.py 迁移入口与职责复核。本轮重点是复核 _migrate_db 是否只承担迁移调度职责；如果没有必要整理代码，可以只记录“无需改代码”。

## 1. 本轮目标

复核 src/data/database.py 中 DatabaseManager._migrate_db 的职责是否已经收敛为迁移调度入口。

目标状态：
- _migrate_db 只按顺序调用：
  - self._migrate_schedules_table()
  - self._migrate_categories_table()
- schedules 表迁移逻辑保留在 _migrate_schedules_table。
- categories 表迁移逻辑保留在 _migrate_categories_table。

本轮只允许极小范围的命名、注释、空行整理；如果当前代码已经满足目标，优先不改代码，只更新 Work_Log.md 记录复核结论。

## 2. 允许/禁止

本轮允许修改：
- src/data/database.py
- manage_instruction/Work_Log.md

本轮禁止修改：
- src/data/connection.py
- src/data/models.py
- src/repositories/
- src/ui/
- main.py
- src/theme/
- src/utils/signals.py
- requirements.txt
- schedule.db
- Work_Snapshot.md
- Work_Formulation.md
- Work_Task_Prompts.md

本轮禁止改动：
- 迁移目标
- 迁移顺序
- 旧数据补值策略
- 异常捕获
- migrate 调用顺序
- _connect
- _create_tables
- DatabaseManager 对外 API
- 所有业务方法
- 重复日程逻辑

禁止抽取业务方法，禁止移动重复日程逻辑，禁止重写迁移逻辑。

如果发现必须修改禁止范围内的文件，先停止并说明原因，不要自行扩大修改范围。

## 3. 具体任务

1. 检查 src/data/database.py 中的 _migrate_db。
2. 确认 _migrate_db 是否只承担迁移调度职责。
3. 确认 _migrate_db 是否按顺序调用：
   - self._migrate_schedules_table()
   - self._migrate_categories_table()
4. 如果已有结构清晰，不要改代码，只在 Work_Log.md 记录“无需改代码”。
5. 如果确有必要，只允许做极小范围的命名、注释或空行整理。
6. 不修改 _migrate_schedules_table 和 _migrate_categories_table 内部迁移逻辑。
7. 不修改任何业务方法。

## 4. 验收命令

1. import 验证：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.connection import db as db1; from src.data.models import Category, Schedule; from src.data.database import db as db2, db_manager; print('imports ok'); print('same db object:', db1 is db2)"

2. 基础读取验证：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('all schedules', len(db_manager.get_all_schedules())); print('active categories', len(db_manager.get_active_categories()))"

3. 临时分类创建/硬删除验证，验证后必须清理：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_b4_category_'+str(int(time.time())); cid=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created category', cid); assert cid is not None; cat=db_manager.get_category(cid); assert cat and cat.name == name; deleted=db_manager.hard_delete_category(cid); print('deleted category', deleted); assert deleted is True; assert db_manager.get_category(cid) is None"

4. 临时日程创建/删除验证，验证后必须清理：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_b4_schedule_'+str(int(time.time())); data={'title':name,'item_type':'schedule','priority':0,'repeat_rule':'none','description':'temporary b4 validation','category_id':None}; created=db_manager.add_schedule(data); print('created schedule', created); assert created is True; matches=[s for s in db_manager.get_all_schedules() if s.title==name]; assert len(matches)==1; sid=matches[0].id; deleted=db_manager.delete_schedule(sid); print('deleted schedule', deleted); assert deleted is True; assert not [s for s in db_manager.get_all_schedules() if s.id==sid]"

5. GUI smoke test：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); print('gui smoke ok'); w.close(); app.quit()"

如果 GUI smoke 因环境限制失败，请记录原因，并执行兜底：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import main; print('main import ok')"

6. 静态检查 _migrate_db 调度顺序：

rg -n "def _migrate_db|self\._migrate_schedules_table\(\)|self\._migrate_categories_table\(\)" src/data/database.py

预期：_migrate_db 中先调用 _migrate_schedules_table，再调用 _migrate_categories_table。

7. 验证禁止文件无改动：

git diff --name-only -- src/data/connection.py
git diff --name-only -- src/data/models.py
git diff --name-only -- src/repositories
git diff --name-only -- src/ui
git diff --name-only -- main.py
git diff --name-only -- schedule.db

8. 验证本轮修改范围：

git diff --name-only

如果本轮无需代码改动，预期只包含：
- manage_instruction/Work_Log.md

如果确实做了极小范围整理，预期只包含：
- src/data/database.py
- manage_instruction/Work_Log.md

## 5. 日志要求

更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第二轮 B-4（database.py 迁移入口与职责复核）
- 实际修改文件
- 是否有代码改动；如果没有，记录“无需改代码”
- _migrate_db 职责复核结论
- 是否确认 _migrate_db 只负责顺序调用 _migrate_schedules_table 和 _migrate_categories_table
- 是否确认未改迁移目标、迁移顺序、旧数据补值策略、异常捕获和 migrate 调用顺序
- 是否确认未改 _connect、_create_tables、DatabaseManager 对外 API 和业务方法
- 验证命令和结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点，尤其是迁移行为变化、循环导入、schedule.db 变更风险

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
```

## 复核锚点

- B-4 优先不改代码；如果无需整理，只更新 `Work_Log.md`。
- `_migrate_db` 应只负责顺序调用 `_migrate_schedules_table()` 和 `_migrate_categories_table()`。
- 不允许改迁移目标、迁移顺序、旧数据补值策略、异常捕获和 `migrate(...)` 调用顺序。
- 不允许修改业务方法、重复日程逻辑、`src/ui/`、`schedule.db`。
