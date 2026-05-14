# Work Log

本文件只记录当前阶段/当前轮次的执行日志。

历史日志已归档到 `manage_instruction/History_Log.md`。

## 当前状态

第二轮 A 已完成并归档。等待第二轮 B 小工单发布。

## 2026-05-14 第二轮 B-1（database.py import 与边界清理）

- 本轮任务名称：第二轮 B-1（database.py import 与边界清理）。
- 实际修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- import 清理内容：
  - 将 `from peewee import *` 替换为最小显式导入：`from peewee import CharField, DoubleField`。
  - 移除不再需要的模型导入 `BaseModel`：
    - 从 `from src.data.models import BaseModel, Category, Schedule`
    - 调整为 `from src.data.models import Category, Schedule`
- 约束确认：
  - 未修改 `_connect`、`_create_tables`、`_migrate_db` 方法体。
  - 未修改建表逻辑、迁移逻辑、业务逻辑、DatabaseManager 对外行为。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('database import ok'); print('all schedules', len(db_manager.get_all_schedules())); print('active categories', len(db_manager.get_active_categories()))"`
    - 结果：
      - `database import ok`
      - `all schedules 62`
      - `active categories 7`
  - `rg -n "BaseModel" src/data/database.py`
    - 结果：无输出（退出码 1，符合预期）。
  - `rg -n "from peewee import \*" src/data/database.py`
    - 结果：无输出（退出码 1，符合预期）。
- diff 范围检查结果：
  - `git diff --name-only -- src/data/connection.py` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> 写日志前仅 `src/data/database.py`；写日志后包含 `src/data/database.py` 与 `manage_instruction/Work_Log.md`。
  - `git status --short --branch` -> 写日志前 `M src/data/database.py`；写日志后另含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - B-2/B-3/B-4/B-5 待后续工单执行。
- 风险或疑点：
  - 未发现循环导入风险。
  - 本轮仅 import 边界清理，运行行为变化风险低。

## 2026-05-14 第二轮 B-2（只抽离 schedules 表迁移块）

- 本轮任务名称：第二轮 B-2（只抽离 schedules 表迁移块）。
- 实际修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 抽离的方法名：
  - `_migrate_schedules_table(self)`
- 改动说明：
  - 已将 `_migrate_db` 中 schedules 表迁移逻辑抽离为 `_migrate_schedules_table(self)`，包含：
    - `columns = [col.name for col in db.get_columns('schedules')]`
    - `group_id` 迁移分支
    - `sort_order` 迁移分支
    - `sort_order` 老数据补值循环
  - `_migrate_db` 现先调用 `self._migrate_schedules_table()`，随后继续执行原 categories 迁移块。
- 顺序与范围确认：
  - 已确认 `_migrate_db` 仍保持先 schedules、后 categories 的顺序。
  - 已确认本轮未处理 categories 表迁移块抽离（categories 逻辑仍保留在 `_migrate_db`）。
  - 已确认未改迁移字段、默认值、字段名、表名、补值策略、异常捕获和 migrate 调用顺序（仅做代码位置抽离）。
  - 已确认未修改 `_connect`、`_create_tables`、DatabaseManager 对外方法和业务方法。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('database import ok'); print('all schedules', len(db_manager.get_all_schedules()))"`
    - 结果：`database import ok`，`all schedules 62`
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_b2_schedule_'+str(int(time.time())); data={'title':name,'item_type':'schedule','priority':0,'repeat_rule':'none','description':'temporary b2 validation','category_id':None}; created=db_manager.add_schedule(data); print('created schedule', created); assert created is True; matches=[s for s in db_manager.get_all_schedules() if s.title==name]; print('matches', len(matches)); assert len(matches)==1; sid=matches[0].id; deleted=db_manager.delete_schedule(sid); print('deleted schedule', deleted); assert deleted is True; remaining=[s for s in db_manager.get_all_schedules() if s.id==sid]; print('remaining', len(remaining)); assert len(remaining)==0"`
    - 结果：`created schedule True`，`matches 1`，`deleted schedule True`，`remaining 0`
  - `rg -n "def _migrate_schedules_table|self\._migrate_schedules_table\(\)" src/data/database.py`
    - 结果：命中方法定义与调用。
  - `rg -n "columns_cat|get_columns\('categories'\)|list_type|cat_sort_order_field" src/data/database.py`
    - 结果：categories 相关迁移代码仍在 `_migrate_db` 中。
- diff 范围检查结果：
  - `git diff --name-only -- src/data/connection.py` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `src/data/database.py` + `manage_instruction/Work_Task_Prompts.md`（本轮开始前既有改动）；写日志后另含 `manage_instruction/Work_Log.md`。
  - `git status --short --branch` -> `M src/data/database.py`，`M manage_instruction/Work_Task_Prompts.md`（既有改动）；写日志后另含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - B-3/B-4/B-5 待后续工单执行。
- 风险或疑点：
  - 本轮中途曾出现一次文本编码导致的语法错误风险，已通过恢复并采用局部补丁方式完成，最终 import/读写验证通过。
  - 未发现循环导入问题；`schedule.db` 无 diff。
