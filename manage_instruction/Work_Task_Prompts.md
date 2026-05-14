# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 A-3：新增 `src/data/models.py`，并移动 Peewee 模型类。

状态：等待执行窗口执行，执行后由顾问窗口复核。

## 正式执行提示词

~~~text
请执行第二轮 A-3：新增 src/data/models.py，并将 Peewee 模型类从 src/data/database.py 移入 models.py。不执行 A-4/A-5/A-6，也不执行第二轮 B/C/D。

本轮允许修改：
- src/data/models.py
- src/data/database.py
- manage_instruction/Work_Log.md

本轮禁止修改：
- src/data/connection.py
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

原则：
- 只移动模型类，不改业务逻辑。
- 不修改 Repository。
- 不改数据库字段含义、默认值、字段名、表名。
- 不改 _migrate_db 的迁移步骤、迁移顺序和补值策略。
- 不改 DatabaseManager 公开方法行为。
- 不迁移 add_schedule、update_schedule_with_repeat、_add_months。
- 不新增 Service。
- 不做额外重构。
- 保持 db_manager 对外方法名、参数、返回值语义不变。

具体任务：
1. 新增 src/data/models.py。
2. 将以下类从 src/data/database.py 移入 src/data/models.py：
   - BaseModel
   - Category
   - Schedule
3. models.py 必须从 connection.py 导入 db：
   from src.data.connection import db
   或：
   from .connection import db
4. models.py 不得从 database.py 导入任何内容。
5. database.py 应从 models.py 导入：
   from src.data.models import BaseModel, Category, Schedule
   或等价相对导入。
6. database.py 中不再保留 BaseModel、Category、Schedule 的类定义。
7. 暂不修改 src/repositories/，Repository 导入来源留到 A-4/A-5 单独处理。

验收要求：
1. 验证 models.py 和 database.py import：
   D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.models import BaseModel, Category, Schedule; from src.data.database import db_manager; print('models import ok'); print('db import ok'); print(len(db_manager.get_all_schedules()))"

2. 验证基础读路径：
   D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; print('all schedules', len(db_manager.get_all_schedules())); print('active categories', len(db_manager.get_active_categories())); print('today schedules', len(db_manager.get_schedules_for_date(date.today())))"

3. 验证临时分类写路径：
   D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_round2a3_category_'+str(int(time.time())); cat_id=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created category', cat_id); assert cat_id is not None; cat=db_manager.get_category(cat_id); print('category exists', bool(cat)); assert cat and cat.name == name; deleted=db_manager.hard_delete_category(cat_id); print('deleted category', deleted); assert deleted is True; after=db_manager.get_category(cat_id); print('after delete', after); assert after is None"

4. 验证临时日程创建/删除路径：
   D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_round2a3_schedule_'+str(int(time.time())); data={'title': name, 'item_type': 'schedule', 'priority': 0, 'repeat_rule': 'none', 'description': 'temporary round2a3 validation', 'category_id': None}; created=db_manager.add_schedule(data); print('created schedule', created); assert created is True; matches=[s for s in db_manager.get_all_schedules() if s.title == name]; print('matches', len(matches)); assert len(matches) == 1; schedule_id=matches[0].id; deleted=db_manager.delete_schedule(schedule_id); print('deleted schedule', deleted); assert deleted is True; remaining=[s for s in db_manager.get_all_schedules() if s.id == schedule_id]; print('remaining', len(remaining)); assert len(remaining) == 0"

5. 验证 GUI smoke test：
   D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); print('gui smoke ok'); w.close(); app.quit()"

如果 GUI smoke test 因显示环境或沙箱限制失败，请记录原因，并执行兜底：
   D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import main; print('main import ok')"

6. 验证导入边界：
   rg -n "from .*database import|import .*database" src/data/models.py
   rg -n "^class (BaseModel|Category|Schedule)" src/data/database.py
   rg -n "^class (BaseModel|Category|Schedule)" src/data/models.py

预期：
- models.py 不应导入 database.py。
- database.py 不应再定义 BaseModel、Category、Schedule。
- models.py 应定义 BaseModel、Category、Schedule。

7. 验证未改禁止范围：
   git diff --name-only -- src/data/connection.py
   git diff --name-only -- src/repositories
   git diff --name-only -- src/ui
   git diff --name-only -- schedule.db

8. 验证本轮修改范围：
   git diff --name-only
   git status --short --branch

预期只包含：
- src/data/models.py
- src/data/database.py
- manage_instruction/Work_Log.md

更新 Work_Log.md，至少记录：
- 本轮任务名称：第二轮 A-3（新增 models.py 并移动 Peewee 模型类）
- 实际修改文件
- 移动的模型类：BaseModel、Category、Schedule
- 是否确认 models.py 从 connection.py 导入 db
- 是否确认 models.py 没有从 database.py 导入内容
- 是否确认本轮没有修改 Repository
- 是否确认字段含义、默认值、字段名、表名未改变
- 验证命令和结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点，尤其是是否出现循环导入

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
~~~

## 复核锚点

- 只允许修改 `src/data/models.py`、`src/data/database.py`、`manage_instruction/Work_Log.md`。
- `BaseModel`、`Category`、`Schedule` 应从 `database.py` 移到 `models.py`。
- `models.py` 必须从 `connection.py` 导入 `db`，不得从 `database.py` 导入。
- 本轮不得修改 `src/repositories/`、`src/ui/`、`schedule.db`。
- 字段含义、默认值、字段名、表名必须保持不变。
