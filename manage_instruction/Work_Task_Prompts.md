# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 A-5：调整 `CategoryRepository` 模型导入来源。

状态：等待执行窗口执行，执行后由顾问窗口复核。

## 正式执行提示词

~~~text
请执行第二轮 A-5：只调整 CategoryRepository 的模型导入来源，不执行 A-6，也不执行第二轮 B/C/D。

本轮允许修改：
- src/repositories/category_repository.py
- manage_instruction/Work_Log.md

本轮禁止修改：
- src/repositories/schedule_repository.py
- src/data/database.py
- src/data/models.py
- src/data/connection.py
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
- 只把 CategoryRepository 中从 src.data.database 延迟导入 Category、Schedule 的位置，改为从 src.data.models 导入 Category、Schedule。
- 保留构造函数注入能力，category_model / schedule_model 参数仍然可用。
- 不改变任何 Repository 方法名、参数、返回值语义、排序逻辑、过滤逻辑、状态判断逻辑、删除策略或 CRUD 行为。
- 不修改 ScheduleRepository。
- 不做额外重构。
- 不改数据库字段、迁移逻辑或业务逻辑。

具体任务：
1. 在 src/repositories/category_repository.py 中定位 CategoryRepository.__init__。
2. 将 category_model is None 或 schedule_model is None 时的 Category、Schedule 导入来源改为 src.data.models。
3. 保持 self._category_model = category_model 和 self._schedule_model = schedule_model 的注入逻辑不变。
4. 不修改其他方法实现。

验收要求：

1. Repository import 和默认模型来源验证：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories.category_repository import CategoryRepository; from src.data.models import Category, Schedule; repo=CategoryRepository(); print('category repo import ok'); print('uses models Category:', repo._category_model is Category); print('uses models Schedule:', repo._schedule_model is Schedule)"

2. db_manager 基础分类读取验证：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('db import ok'); cats=db_manager.get_active_categories(); cmap=db_manager.get_category_map(); print('active categories', len(cats)); print('category map', len(cmap)); print('sample status', db_manager.check_category_status(cats[0].id) if cats else 'no sample')"

3. 临时分类写入路径验证，验证后必须清理：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_round2a5_category_'+str(int(time.time())); cat_id=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created category', cat_id); assert cat_id is not None; cat=db_manager.get_category(cat_id); print('category exists', bool(cat)); assert cat and cat.name == name; updated=db_manager.update_category_fields(cat_id, color='#0cc0df'); print('updated category', updated); assert updated is True; soft=db_manager.soft_delete_category(cat_id); print('soft deleted', soft); assert soft is True; hard=db_manager.hard_delete_category(cat_id); print('hard deleted', hard); assert hard is True; after=db_manager.get_category(cat_id); print('after delete', after); assert after is None"

4. 静态检查 CategoryRepository 不再从 database.py 导入 Category 或 Schedule：

rg -n "from src\.data\.database import Category|from src\.data\.database import Schedule|from src\.data\.database import Category, Schedule|from \.\.data\.database import Category|from \.\.data\.database import Schedule|from \.database import Category|from \.database import Schedule" src/repositories/category_repository.py

预期：没有输出。

5. 验证禁止文件无改动：

git diff --name-only -- src/repositories/schedule_repository.py
git diff --name-only -- src/data/database.py
git diff --name-only -- src/data/models.py
git diff --name-only -- src/data/connection.py
git diff --name-only -- src/ui
git diff --name-only -- schedule.db

6. 验证本轮修改范围：

git diff --name-only

预期只包含：
- src/repositories/category_repository.py
- manage_instruction/Work_Log.md

更新 manage_instruction/Work_Log.md，至少记录：
- 本轮任务名称：第二轮 A-5（CategoryRepository 模型导入来源调整）
- 实际修改文件
- 修改内容说明
- 是否保留 category_model / schedule_model 构造函数注入能力
- 验证命令和结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
~~~

## 复核锚点

- 只允许修改 `src/repositories/category_repository.py` 和 `manage_instruction/Work_Log.md`。
- `CategoryRepository.__init__` 默认导入来源应改为 `src.data.models.Category` / `src.data.models.Schedule`。
- `category_model` / `schedule_model` 注入能力必须保留。
- 不得修改 `ScheduleRepository`、`src/data/*`、`src/ui/`、`schedule.db`。
