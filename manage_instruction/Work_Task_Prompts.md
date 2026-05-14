# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 A-6：第二轮 A 整体验收。

状态：等待执行窗口执行，执行后由顾问窗口复核。

## 正式执行提示词

```text
请执行第二轮 A-6：只做第二轮 A 的整体验收，不做新的架构改动。

【本轮目标】
验证第二轮 A（A-1~A-5）改造后的 import 链路、模型来源、连接一致性、基础读写路径、GUI 启动能力和改动范围约束是否全部正常。

【允许修改】
- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在流程需要维护提示词锚点时）

【禁止修改】
- src/data/connection.py
- src/data/models.py
- src/data/database.py
- src/repositories/
- src/ui/
- main.py
- src/theme/
- src/utils/signals.py
- requirements.txt
- schedule.db
- Work_Snapshot.md
- Work_Formulation.md

【执行前要求】
1. 先进入内层项目根目录：
   cd /d D:\CodeProjects\DesktopSchedule\DesktopSchedule
2. Python 一律使用：
   D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe
3. 本轮原则上不改代码；若发现任何代码文件已产生 diff，先停止并记录异常，不要自行修复或扩大修改。

【验收命令】

1) import 链路 + 模型来源 + db连接一致性 一次验证
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.connection import db as db1, DB_PATH as p1; from src.data.models import BaseModel, Category, Schedule; from src.data.database import db as db2, DB_PATH as p2, db_manager; from src.repositories.schedule_repository import ScheduleRepository; from src.repositories.category_repository import CategoryRepository; srepo=ScheduleRepository(); crepo=CategoryRepository(); print('connection/models/database/repositories import ok'); print('db_manager import ok'); print('same db object:', db1 is db2); print('same path:', p1 == p2); print('schedule repo uses models.Schedule:', srepo._schedule_model is Schedule); print('category repo uses models.Category:', crepo._category_model is Category); print('category repo uses models.Schedule:', crepo._schedule_model is Schedule)"

2) 导入边界静态检查
rg -n "from .*database import|import .*database" src/data/models.py
rg -n "^class (BaseModel|Category|Schedule)" src/data/database.py
rg -n "^class (BaseModel|Category|Schedule)" src/data/models.py

预期：
- models.py 不应导入 database.py（无输出）
- database.py 不应再定义 BaseModel/Category/Schedule（无输出）
- models.py 应定义这三个类（有输出）

3) 基础读路径验证
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; print('all schedules', len(db_manager.get_all_schedules())); today=db_manager.get_schedules_for_date(date.today()); print('today schedules', len(today)); cats=db_manager.get_active_categories(); print('active categories', len(cats)); cmap=db_manager.get_category_map(); print('category map', len(cmap)); print('sample category id', cats[0].id if cats else None); print('get_category sample', bool(db_manager.get_category(cats[0].id)) if cats else 'no sample'); print('check_category_status sample', db_manager.check_category_status(cats[0].id) if cats else 'no sample')"

4) 临时分类写路径验证（必须清理）
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_round2a6_category_'+str(int(time.time())); cid=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created category', cid); assert cid is not None; cat=db_manager.get_category(cid); print('category exists', bool(cat)); assert cat and cat.name==name; upd=db_manager.update_category_fields(cid, color='#0cc0df'); print('updated', upd); assert upd is True; soft=db_manager.soft_delete_category(cid); print('soft deleted', soft); assert soft is True; hard=db_manager.hard_delete_category(cid); print('hard deleted', hard); assert hard is True; print('after delete', db_manager.get_category(cid)); assert db_manager.get_category(cid) is None"

5) 临时日程写路径验证（必须清理，repeat_rule='none'）
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_round2a6_schedule_'+str(int(time.time())); data={'title':name,'item_type':'schedule','priority':0,'repeat_rule':'none','description':'temporary round2a6 validation','category_id':None}; created=db_manager.add_schedule(data); print('created schedule', created); assert created is True; matches=[s for s in db_manager.get_all_schedules() if s.title==name]; print('matches', len(matches)); assert len(matches)==1; sid=matches[0].id; deleted=db_manager.delete_schedule(sid); print('deleted schedule', deleted); assert deleted is True; remaining=[s for s in db_manager.get_all_schedules() if s.id==sid]; print('remaining', len(remaining)); assert len(remaining)==0"

6) GUI smoke test
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); print('gui smoke ok'); w.close(); app.quit()"

若 GUI 因沙箱/显示环境失败，记录原因并执行兜底：
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import main; print('main import ok')"

7) 范围检查
git diff --name-only -- src/data/connection.py
git diff --name-only -- src/data/models.py
git diff --name-only -- src/data/database.py
git diff --name-only -- src/repositories
git diff --name-only -- src/ui
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch

预期：
- 前 6 条范围检查均无输出
- 最终 diff 只允许：
  - manage_instruction/Work_Log.md
  - manage_instruction/Work_Task_Prompts.md（如本轮确有维护）

若出现任何代码文件 diff：立即停止，记录异常，不要自行修复或扩大修改。

【Work_Log.md 记录要求】
至少记录：
1. 本轮任务名称：第二轮 A-6（第二轮 A 整体验收）
2. 实际修改文件
3. 每条验证命令和结果摘要
4. GUI smoke test 结果或兜底原因
5. diff 范围检查结果
6. 未完成事项
7. 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
```

## 复核锚点

- 本轮只做验收，不做代码改动。
- 允许修改 `manage_instruction/Work_Log.md`，以及本文件。
- 若出现 `src/data/*`、`src/repositories/*`、`src/ui/*` 或 `schedule.db` diff，应视为异常。
- 重点确认 `connection.py -> models.py -> database.py/repositories` 链路稳定。
