# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 B-3：只抽离 categories 表迁移块。

状态：等待执行窗口执行，执行后由顾问窗口复核。

## 正式执行提示词

```text
请执行第二轮 B-3：只抽离 categories 表迁移块。本轮只做这一项，不再改 schedules 表迁移块，不做其他重构。

## 1. 本轮目标

只把 src/data/database.py 中 _migrate_db 里的 categories 表相关迁移逻辑抽成私有方法，例如：

_migrate_categories_table(self)

本轮要求：
- _migrate_db 仍保持先调用 self._migrate_schedules_table()，再调用 categories 迁移。
- 本轮不再改 schedules 表迁移块。
- 只移动原代码，不改迁移字段、默认值、字段名、表名、补值策略、异常捕获和 migrate 调用顺序。
- 不改条件判断。
- 不合并任何迁移分支。
- 不重写迁移逻辑。
- 不改变已有数据库兼容策略。

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
- _connect
- _create_tables
- _migrate_schedules_table
- DatabaseManager 对外方法
- add_schedule
- update_schedule_with_repeat
- _add_months
- delete_schedule
- update_schedule_status
- toggle_pin_status
- update_schedule_fields
- 所有分类业务方法
- 任何非迁移相关业务方法

如果发现必须修改禁止范围内的文件，先停止并说明原因，不要自行扩大修改范围。

## 3. 具体任务

1. 在 src/data/database.py 中定位 DatabaseManager._migrate_db。
2. 将 categories 表相关迁移逻辑抽成私有方法，例如：

   def _migrate_categories_table(self):

3. categories 表相关迁移逻辑包括：
   - columns_cat = [col.name for col in db.get_columns('categories')]
   - list_type 字段迁移分支
   - sort_order 字段迁移分支
   - sort_order 老数据补值循环

4. 修改后 _migrate_db 应保持调度顺序：
   - 先调用 self._migrate_schedules_table()
   - 再调用 self._migrate_categories_table()

5. 不修改 _migrate_schedules_table 的实现。
6. 不改变任何迁移字段、默认值、字段名、表名、补值策略、异常捕获和 migrate 调用顺序。
7. 不做额外重构。

## 4. 验收命令

1. database import 和基础分类读取验证：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('database import ok'); print('active categories', len(db_manager.get_active_categories()))"

2. 临时分类创建/硬删除路径验证，验证后必须清理：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_b3_category_'+str(int(time.time())); cat_id=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created category', cat_id); assert cat_id is not None; cat=db_manager.get_category(cat_id); print('category exists', bool(cat)); assert cat and cat.name == name; deleted=db_manager.hard_delete_category(cat_id); print('deleted category', deleted); assert deleted is True; after=db_manager.get_category(cat_id); print('after delete', after); assert after is None"

3. 静态检查新私有方法存在：

rg -n "def _migrate_categories_table|self\._migrate_categories_table\(\)" src/data/database.py

预期：能看到方法定义和 _migrate_db 中的调用。

4. 静态检查 _migrate_db 中调用顺序正确：

rg -n "self\._migrate_schedules_table\(\)|self\._migrate_categories_table\(\)" src/data/database.py

预期：_migrate_schedules_table 的调用行号在 _migrate_categories_table 之前。

5. 静态检查 schedules 迁移方法仍存在：

rg -n "def _migrate_schedules_table|group_id_field|sort_order_field" src/data/database.py

预期：仍能看到 schedules 迁移方法和原有字段定义。

6. 验证禁止文件无改动：

git diff --name-only -- src/data/connection.py
git diff --name-only -- src/data/models.py
git diff --name-only -- src/repositories
git diff --name-only -- src/ui
git diff --name-only -- main.py
git diff --name-only -- schedule.db

7. 验证本轮修改范围：

git diff --name-only

预期只包含：
- src/data/database.py
- manage_instruction/Work_Log.md

## 5. 日志要求

更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第二轮 B-3（只抽离 categories 表迁移块）
- 实际修改文件
- 抽离的方法名，例如 _migrate_categories_table
- 是否确认 _migrate_db 仍保持先 schedules、后 categories 的顺序
- 是否确认本轮未修改 _migrate_schedules_table
- 是否确认未改迁移字段、默认值、字段名、表名、补值策略、异常捕获和 migrate 调用顺序
- 是否确认未修改 _connect、_create_tables、DatabaseManager 对外方法和业务方法
- 验证命令和结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点，尤其是迁移行为变化、循环导入、schedule.db 变更风险

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
```

## 复核锚点

- 本轮只允许抽离 categories 表迁移块。
- `_migrate_schedules_table` 的实现不得修改。
- `_migrate_db` 必须先调用 `self._migrate_schedules_table()`，再调用 `self._migrate_categories_table()`。
- 不允许改迁移字段、默认值、字段名、表名、补值策略、异常捕获和 `migrate(...)` 调用顺序。
- 不允许修改 `src/data/connection.py`、`src/data/models.py`、`src/repositories/`、`src/ui/`、`main.py`、`schedule.db`。
