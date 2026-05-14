# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 A-2：`database.py` 改用 `connection.py` 的 `BASE_DIR`、`DB_PATH`、`db`。

状态：等待执行窗口执行，执行后由顾问窗口复核。

## 正式执行提示词

~~~text
请执行第二轮 A-2：只让 `src/data/database.py` 改用 `src/data/connection.py` 中的 `BASE_DIR`、`DB_PATH`、`db`，不执行第二轮 A-3/A-4/A-5/A-6，也不执行第二轮 B/C/D。

本轮允许修改：
- `src/data/database.py`
- `manage_instruction/Work_Log.md`

本轮禁止修改：
- `src/data/connection.py`
- `src/data/models.py`
- `src/repositories/`
- `src/ui/`
- `main.py`
- `src/theme/`
- `src/utils/signals.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`
- `Work_Task_Prompts.md`

原则：
- 不新增 `models.py`。
- 不移动 `BaseModel`、`Category`、`Schedule`。
- 不修改 Repository。
- 不改业务逻辑。
- 不改数据库字段。
- 不改 `_migrate_db` 的迁移步骤、迁移顺序和补值策略。
- 不改 `DatabaseManager` 公开方法行为。
- 不迁移 `add_schedule`、`update_schedule_with_repeat`、`_add_months`。
- 不做额外重构。
- 保持 `db_manager` 对外方法名、参数、返回值语义不变。

具体任务：
1. 在 `src/data/database.py` 中从 `src.data.connection` 导入 `BASE_DIR`、`DB_PATH`、`db`。
2. 删除或替换 `database.py` 中原本直接定义的 `BASE_DIR`、`DB_PATH`、`db = SqliteDatabase(DB_PATH)`。
3. `database.py` 仍应对外保留 `BASE_DIR`、`DB_PATH`、`db` 这几个名称。
4. Peewee 模型类 `BaseModel`、`Category`、`Schedule` 本轮继续留在 `database.py`。
5. 只允许清理与本轮直接相关且确实不再使用的 import。不要删除当前 Peewee 模型类仍需要的 `Model`、`CharField`、`DateTimeField` 等导入来源，不做无关格式整理。

验收要求：
1. 验证 `connection.py` 和 `database.py` 使用的是同一路径、同一个 db 对象：
   `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.connection import DB_PATH as p1, db as db1; from src.data.database import DB_PATH as p2, db as db2, db_manager; print('same path:', p1 == p2); print('same db object:', db1 is db2); print('db import ok'); print(len(db_manager.get_all_schedules()))"`

2. 验证基础读路径：
   `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; print('all schedules', len(db_manager.get_all_schedules())); print('active categories', len(db_manager.get_active_categories())); print('today schedules', len(db_manager.get_schedules_for_date(date.today())))"`

3. 验证临时分类写路径：
   `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_round2a2_category_'+str(int(time.time())); cat_id=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created category', cat_id); assert cat_id is not None; cat=db_manager.get_category(cat_id); print('category exists', bool(cat)); assert cat and cat.name == name; deleted=db_manager.hard_delete_category(cat_id); print('deleted category', deleted); assert deleted is True; after=db_manager.get_category(cat_id); print('after delete', after); assert after is None"`

4. 验证未改禁止范围：
   - `git diff --name-only -- src/data/connection.py`
   - `git diff --name-only -- src/data/models.py`
   - `git diff --name-only -- src/repositories`
   - `git diff --name-only -- src/ui`
   - `git diff --name-only -- schedule.db`

5. 验证本轮修改范围：
   - `git diff --name-only`

预期只包含：
- `src/data/database.py`
- `manage_instruction/Work_Log.md`

更新 `Work_Log.md`，至少记录：
- 本轮任务名称：第二轮 A-2（database.py 改用 connection.py 的 db）
- 实际修改文件
- `database.py` 是否已从 `connection.py` 导入 `BASE_DIR`、`DB_PATH`、`db`
- 是否确认本轮没有新增 `models.py`
- 是否确认本轮没有修改 Repository
- 验证命令和结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点，尤其是是否出现循环导入或数据库连接对象不一致

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
~~~

## 复核锚点

- 只允许修改 `src/data/database.py` 和 `manage_instruction/Work_Log.md`。
- `database.py` 应从 `src.data.connection` 导入 `BASE_DIR`、`DB_PATH`、`db`。
- `BaseModel`、`Category`、`Schedule` 本轮必须仍留在 `database.py`。
- `src/data/models.py` 本轮不得出现。
- `src/repositories/`、`src/ui/`、`schedule.db` 必须无 diff。
- 验证必须确认 `src.data.connection.db is src.data.database.db` 为 `True`。
