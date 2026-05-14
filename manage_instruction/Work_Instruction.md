# Work Instruction

用途：本文件用于“当前阶段”的执行指令发布。

- 仅保留正在执行或即将执行的任务。
- 已完成阶段请归档到 `History_Instruction.md`，避免本文件长期堆积。
- 当前主路线图见 `Work_Formulation.md` 的“架构改写轮次路线图”。
- 改写前行为和目录快照见 `Work_Snapshot.md`。
- 执行过程记录写入 `Work_Log.md`。

---

# 当前阶段：第二轮 - Data 层整理与模型拆分

## 阶段目标

第二轮目标是把数据层职责进一步分清，让 Peewee 模型、数据库连接/迁移、Repository、`DatabaseManager` 兼容门面之间的边界更清楚。

第一轮已经完成：

```text
UI -> db_manager 兼容门面 -> Repository -> Peewee Model/database.py
```

第二轮目标逐步调整为：

```text
UI -> db_manager 兼容门面 -> Repository -> src/data/models.py -> src/data/connection.py
                          -> database.py 负责建表、迁移、兼容门面，并导入同一个 db
```

本轮仍然必须保留旧 UI 调用方式：旧 UI 继续通过 `db_manager` 工作，不让 UI 直接改调 Repository 或 Peewee Model。

## 第二轮总体允许范围

第二轮整体允许修改：

- `src/data/database.py`
- `src/data/connection.py`
- `src/data/models.py`
- `src/repositories/`
- `manage_instruction/Work_Log.md`

如发现必须修改上述范围以外的文件，请先停止，并在窗口中说明原因，不要擅自扩大范围。

## 第二轮总体禁止事项

- 不修改任何 `src/ui/` 文件。
- 不修改 `main.py`。
- 不修改 `src/theme/`。
- 不修改 `src/utils/signals.py`。
- 不修改 `requirements.txt`。
- 不修改 `schedule.db`。
- 不修改 `Work_Snapshot.md`。
- 不实现任何新功能。
- 不改变数据库字段含义。
- 不改变 `db_manager` 公开方法名、参数、返回类型和返回语义。
- 不让 UI 层直接引用 Repository、Service 或 Peewee Model。
- 不迁移业务 service。
- 不迁移重复日程逻辑。
- 不迁移提醒逻辑。
- 不拆 UI 大文件。

---

# 当前执行任务：第二轮 A - 只拆 Peewee 模型到 src/data/models.py

## 本轮目标

只创建 `src/data/connection.py` 和 `src/data/models.py`，并把 Peewee 模型定义从 `src/data/database.py` 移入 `models.py`。

本轮只处理数据层最底部依赖：

- `BASE_DIR`
- `DB_PATH`
- `db`
- `BaseModel`
- `Category`
- `Schedule`

同时调整必要 import，让现有行为保持不变。

## 本轮允许修改

- `src/data/models.py`
- `src/data/connection.py`
- `src/data/database.py`
- `src/repositories/category_repository.py`
- `src/repositories/schedule_repository.py`
- `manage_instruction/Work_Log.md`

## 本轮禁止修改

- 不修改任何 `src/ui/` 文件。
- 不修改 `main.py`。
- 不修改 `src/theme/`。
- 不修改 `src/utils/signals.py`。
- 不修改 `requirements.txt`。
- 不修改 `schedule.db`。
- 不修改 `Work_Snapshot.md`。
- 不修改 `Work_Formulation.md`，除非决策窗口另行要求。
- 不修改 `Work_Task_Prompts.md`，除非顾问窗口另行要求。
- 不改任何业务逻辑。
- 不改任何数据库字段定义的含义、默认值、字段名、表名。
- 不改 `_migrate_db` 的迁移步骤、迁移顺序和补值策略。
- 不改 `DatabaseManager` 公开方法行为。
- 不迁移 `add_schedule`、`update_schedule_with_repeat`、`_add_months`。
- 不新增 Service。
- 不做格式化大扫除。

## 具体要求

1. 新增 `src/data/connection.py`。

该文件只放数据库连接基础对象：

```python
import os
from peewee import SqliteDatabase

BASE_DIR = ...
DB_PATH = ...
db = SqliteDatabase(DB_PATH)
```

`BASE_DIR`、`DB_PATH`、`db` 应从 `src/data/database.py` 移入该文件，避免 `models.py` 反向导入 `database.py` 造成循环导入。

2. 新增 `src/data/models.py`。

3. 将以下定义从 `src/data/database.py` 移动到 `src/data/models.py`：

```python
class BaseModel(Model):
    ...

class Category(BaseModel):
    ...

class Schedule(BaseModel):
    ...
```

4. `src/data/models.py` 必须从 `connection.py` 导入同一个 `db` 实例。

推荐方式固定为：

```python
from src.data.connection import db
```

或等价相对导入：

```python
from .connection import db
```

不得让 `models.py` 从 `database.py` 导入 `db`。

5. `src/data/database.py` 应从 `connection.py` 导入并继续暴露同一个连接对象：

```python
from src.data.connection import BASE_DIR, DB_PATH, db
```

或等价相对导入。

`database.py` 不再直接定义 `db = SqliteDatabase(DB_PATH)`，但可以导入并暴露 `db`，以保持旧模块内使用方式和外部兼容性。

6. `src/data/database.py` 中保留：

- `DatabaseManager`
- `db_manager`
- 数据库连接、建表、迁移逻辑

7. `src/data/database.py` 应从模型文件导入：

```python
from src.data.models import BaseModel, Category, Schedule
```

如需使用相对导入，也必须确保从项目根目录执行验证命令时可正常 import。

8. 调整 Repository 的模型导入来源。

当前 Repository 如仍从 `src.data.database` 延迟导入模型，应改为从 `src.data.models` 导入：

```python
from src.data.models import Schedule
from src.data.models import Category
```

或等价的低风险写法。

9. 保持 Repository 构造函数兼容。

如果当前构造函数支持注入模型类，例如：

```python
def __init__(self, schedule_model=None):
```

该能力必须保留，不要删除。

10. 不移动 `src/repositories/` 目录。

第二轮 A 只整理 import 依赖，不做目录路径震荡。

## 循环导入处理原则

本轮最大风险是 `database.py`、`models.py`、repository 之间出现循环导入。

处理原则：

- `db` 的定义移动到 `src/data/connection.py`。
- `database.py` 可以导入并暴露同一个 `db`。
- `models.py` 只定义 Peewee 模型，不创建 `DatabaseManager`。
- `models.py` 只允许依赖 `connection.py`，不得依赖 `database.py`。
- repository 只依赖模型，不依赖 `db_manager`。
- `DatabaseManager.__init__` 中仍可延迟导入 Repository，保持第一轮的低风险结构。
- 不在 UI 文件中引入新的数据层导入。

如果发现上述依赖方向仍无法避免循环导入，不要扩大重构范围；先停止并在窗口中说明原因，等待决策窗口确认。

## 验收要求

执行窗口完成后至少验证：

1. `src.data.models` 可以 import。
2. `src.data.connection` 可以 import，并能导出 `db`、`BASE_DIR`、`DB_PATH`。
3. `src.data.database` 可以 import。
4. `db_manager` 可以正常创建。
5. `ScheduleRepository`、`CategoryRepository` 可以 import。
6. `db_manager.get_all_schedules()` 可调用。
7. `db_manager.get_active_categories()` 可调用。
8. `db_manager.get_schedules_for_date(date.today())` 可调用。
9. 使用临时分类验证清单基础写路径：
   - `add_category`
   - `get_category`
   - `hard_delete_category`
10. 使用临时日程验证日程删除路径：
   - `add_schedule` 创建 `repeat_rule='none'` 的临时日程。
   - `delete_schedule` 删除该临时日程。
   - 确认删除后 `get_all_schedules()` 找不到该 id。
11. GUI smoke test 至少通过一种：
    - 优先：创建并关闭 `MainWindow`。
    - 若 GUI 环境受限：执行 `import main` 兜底，并记录限制原因。
12. `src/ui/` 无改动。
13. `schedule.db` 无 tracked diff。
14. `git diff --name-only` 只出现本轮允许文件。

## 建议验证命令

### 1. import 与读路径验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.connection import db, BASE_DIR, DB_PATH; from src.data.models import BaseModel, Category, Schedule; from src.repositories.schedule_repository import ScheduleRepository; from src.repositories.category_repository import CategoryRepository; from src.data.database import db_manager; print('connection import ok', bool(DB_PATH)); print('models import ok'); print('repositories import ok'); print('db import ok'); print('all schedules', len(db_manager.get_all_schedules())); print('active categories', len(db_manager.get_active_categories())); print('today schedules', len(db_manager.get_schedules_for_date(date.today())))"
```

### 2. 临时分类写路径验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_round2a_category_'+str(int(time.time())); cat_id=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created category', cat_id); assert cat_id is not None; cat=db_manager.get_category(cat_id); print('category exists', bool(cat)); assert cat and cat.name == name; deleted=db_manager.hard_delete_category(cat_id); print('deleted category', deleted); assert deleted is True; after=db_manager.get_category(cat_id); print('after delete', after); assert after is None"
```

### 3. 临时日程删除路径验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_round2a_schedule_'+str(int(time.time())); data={'title': name, 'item_type': 'schedule', 'priority': 0, 'repeat_rule': 'none', 'description': 'temporary round2a validation', 'category_id': None}; created=db_manager.add_schedule(data); print('created schedule', created); assert created is True; matches=[s for s in db_manager.get_all_schedules() if s.title == name]; print('matches', len(matches)); assert len(matches) == 1; schedule_id=matches[0].id; deleted=db_manager.delete_schedule(schedule_id); print('deleted schedule', deleted); assert deleted is True; remaining=[s for s in db_manager.get_all_schedules() if s.id == schedule_id]; print('remaining', len(remaining)); assert len(remaining) == 0"
```

### 4. GUI smoke test

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); print('gui smoke ok'); w.close(); app.quit()"
```

若 GUI smoke test 因显示环境或沙箱限制失败，记录原因，并执行：

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import main; print('main import ok')"
```

### 5. 修改范围检查

```powershell
git diff --name-only -- src/ui
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch
```

## Work_Log.md 记录要求

执行窗口完成后，必须更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第二轮 A（Peewee 模型拆分到 src/data/models.py）。
- 实际修改文件。
- import 与读路径验证命令和结果。
- 临时分类写路径验证命令和结果。
- 临时日程删除路径验证命令和结果。
- GUI smoke test 结果；若失败，记录失败原因和兜底验证结果。
- `src/ui` diff 结果。
- `schedule.db` diff 结果。
- `git diff --name-only` 范围。
- 未完成事项。
- 风险或疑点，尤其是 `connection.py -> models.py -> database.py/repositories` 的依赖方向是否保持干净。

如果任务中途失败，也必须写入：

- 失败位置。
- 关键报错摘要。
- 是否已回滚。
- 当前工作区状态。

## 完成后要求

- 完成后不要提交 Git，等待顾问窗口复核。
- 不要继续执行第二轮 B 或其他后续任务。

---

# 后续小工单预案：第二轮 B/C/D

以下内容用于固定第二轮后续边界，防止后续窗口遗忘。除非决策窗口明确下发对应小工单，否则执行窗口不得提前执行。

后续审查时可按需只读取：

- “第二轮总体允许范围 / 总体禁止事项”
- 对应小工单章节，例如“第二轮 C”
- `Work_Log.md` 中对应轮次记录

这样比每次读取整份 `Work_Instruction.md` 更省上下文，但不能忽略总体禁止事项。

---

## 第二轮 B - 数据库连接与迁移边界整理

### 本轮目标

在第二轮 A 模型拆分稳定后，整理 `src/data/database.py` 的数据库连接、建表、迁移职责，让它更像数据层基础设施文件，而不是模型定义文件。

本轮仍不改变业务行为，不改变 `db_manager` 对外 API。

### 本轮允许修改

- `src/data/database.py`
- `src/data/connection.py`（仅当第二轮 A 后发现连接基础对象边界需要极小修正）
- `src/data/models.py`（仅当第二轮 A 后发现 import 或注释边界需要极小修正）
- `manage_instruction/Work_Log.md`

### 本轮禁止修改

- 不修改 `src/ui/`。
- 不修改 `main.py`。
- 不修改 `src/repositories/`，除非发现第二轮 A 遗留的 import 问题；如需修改须先说明。
- 不修改 `src/theme/`。
- 不修改 `src/utils/signals.py`。
- 不修改 `requirements.txt`。
- 不修改 `schedule.db`。
- 不改数据库字段含义、默认值、字段名、表名。
- 不改 `_migrate_db` 的迁移目标、迁移顺序、旧数据补值策略。
- 不迁移业务 service。
- 不迁移重复日程逻辑。

### 建议处理内容

1. 确认 `database.py` 只保留：
   - `BASE_DIR`
   - `DB_PATH`
   - `db`
   - `DatabaseManager`
   - `db_manager`
   - `_connect`
   - `_create_tables`
   - `_migrate_db`
   - 现有兼容方法

2. 如果 `database.py` 中模型相关 import 或注释还容易误导，可做小范围整理。

3. 不要把 `db` 从 `src/data/connection.py` 再次迁移到其他新文件，除非第二轮 A 的实现已经证明必须如此，并经过决策窗口确认。

4. 不拆 `DatabaseManager` 的业务方法。高风险写入逻辑留到第四轮。

### 验收要求

- `src.data.database` 可 import。
- `src.data.models` 可 import。
- `db_manager` 可创建。
- `db_manager.get_all_schedules()` 可调用。
- `db_manager.get_active_categories()` 可调用。
- 临时分类创建/读取/硬删除路径可用。
- 临时日程创建/删除路径可用。
- GUI smoke test 通过，或记录环境限制并执行 `import main` 兜底。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。
- `git diff --name-only` 只包含本轮允许文件。

### Work_Log.md 记录要求

记录：

- 本轮任务名称：第二轮 B（数据库连接与迁移边界整理）。
- 实际修改文件。
- 修改是否只涉及连接/建表/迁移边界整理。
- 验证命令和结果。
- 未完成事项。
- 风险或疑点，尤其是是否存在循环导入或迁移行为变化风险。

---

## 第二轮 C - Repository 依赖清理与导入关系复核

### 本轮目标

确认 Repository 只依赖模型与数据基础设施，不反向依赖 `DatabaseManager` 或 UI，进一步降低循环导入风险。

本轮主要是依赖关系清理与复核，不做业务行为变更。

### 本轮允许修改

- `src/repositories/category_repository.py`
- `src/repositories/schedule_repository.py`
- `src/repositories/__init__.py`
- `src/data/database.py`（仅当需要配合延迟导入或导出兼容）
- `src/data/connection.py`（仅当需要配合连接对象导入）
- `src/data/models.py`（仅当需要配合模型导入）
- `manage_instruction/Work_Log.md`

### 本轮禁止修改

- 不修改 `src/ui/`。
- 不修改 `main.py`。
- 不修改 `src/theme/`。
- 不修改 `src/utils/signals.py`。
- 不修改 `requirements.txt`。
- 不修改 `schedule.db`。
- 不改变 Repository 方法名、参数、返回语义。
- 不改变 `DatabaseManager` 对外公开方法。
- 不改变查询排序、过滤、删除策略。
- 不迁移业务 service。
- 不迁移重复日程逻辑。

### 建议处理内容

1. 检查 `src/repositories/*.py` 是否仍从 `src.data.database` 导入 `Schedule` 或 `Category`。

2. 如仍存在，应改为从 `src.data.models` 导入模型。

3. 保留现有构造函数注入能力，例如：

```python
def __init__(self, schedule_model=None):
```

4. 检查 `src/repositories/__init__.py` 是否只导出 Repository，不触发重型副作用。

5. 不新增抽象基类，不做 repository 大重构。

### 验收要求

- `ScheduleRepository`、`CategoryRepository` 可单独 import。
- `src.data.database` 可 import。
- `db_manager` 可创建。
- 所有第一轮已委托读写路径仍可调用。
- 至少验证：
  - `get_all_schedules`
  - `get_schedules_for_date`
  - `get_active_categories`
  - `get_category_map`
  - 临时分类增删
  - 临时日程增删
- GUI smoke test 通过，或记录限制并执行 `import main` 兜底。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。
- `git diff --name-only` 只包含本轮允许文件。

### Work_Log.md 记录要求

记录：

- 本轮任务名称：第二轮 C（Repository 依赖清理与导入关系复核）。
- 实际修改文件。
- Repository 当前依赖关系结论。
- 是否仍存在从 repository 到 `db_manager` 的依赖。
- 验证命令和结果。
- 未完成事项。
- 风险或疑点。

---

## 第二轮 D - Data 层整体技术验收

### 本轮目标

在第二轮 A/B/C 完成后，不做新的代码改动，只对 Data 层整理结果做总体验收，确认模型拆分、数据库初始化、Repository、`db_manager` 兼容门面和旧 UI 启动路径均未破坏。

### 本轮允许修改

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅当顾问窗口要求维护复核锚点）

### 本轮禁止修改

- 不修改任何源码文件。
- 不修改 `src/data/database.py`。
- 不修改 `src/data/connection.py`。
- 不修改 `src/data/models.py`。
- 不修改 `src/repositories/`。
- 不修改 `src/ui/`。
- 不修改 `main.py`。
- 不修改 `schedule.db`。
- 不修改 `requirements.txt`。
- 不做任何新功能。

### 验收内容

1. import 验证：
   - `src.data.models`
   - `src.data.connection`
   - `src.data.database`
   - `ScheduleRepository`
   - `CategoryRepository`
   - `db_manager`

2. 读路径验证：
   - `db_manager.get_all_schedules()`
   - `db_manager.get_schedules_for_date(date.today())`
   - `db_manager.get_active_categories()`
   - `db_manager.get_category_map()`
   - 有样本时验证 `db_manager.get_category(cat_id)`
   - 有样本时验证 `db_manager.check_category_status(cat_id)`

3. 分类临时写路径验证：
   - `add_category`
   - `update_category_fields`
   - `soft_delete_category`
   - `hard_delete_category`
   - 清理后 `get_category(cat_id)` 返回 `None`

4. 日程临时写路径验证：
   - 有样本时 `update_schedule_status` 写回原值。
   - 有样本时 `toggle_pin_status` toggle 后恢复原值。
   - 有样本时 `update_schedule_fields` 写回原 title。
   - 使用 `add_schedule` 创建 `repeat_rule='none'` 的临时日程。
   - 使用 `delete_schedule` 删除临时日程。
   - 删除后 `get_all_schedules()` 找不到该临时 id。

5. GUI 验证：
   - 优先执行 `MainWindow` 创建并关闭的 smoke test。
   - 如受环境限制，执行 `import main` 兜底，并记录原因。

6. 范围检查：
   - `git diff --name-only -- src/ui` 无输出。
   - `git diff --name-only -- schedule.db` 无输出。
   - `git diff --name-only` 只包含允许的日志/提示词文件。
   - `git status --short --branch` 状态明确。

### 建议验证命令

可复用第二轮 A 的验证命令，并额外补充分类更新、软删除、日程状态写回、置顶恢复、字段写回等完整路径。

如果执行窗口受沙箱限制导致 GUI 或 Python 验证失败，应申请沙箱外权限；若仍失败，则记录失败原因和用户本地 CMD 复跑命令。

### Work_Log.md 记录要求

记录：

- 本轮任务名称：第二轮 D（Data 层整体技术验收）。
- 实际修改文件。
- import 验证结果。
- 读路径验证结果。
- 分类临时写路径验证结果。
- 日程临时写路径验证结果。
- GUI smoke test 或兜底验证结果。
- `src/ui` diff 结果。
- `schedule.db` diff 结果。
- `git diff --name-only` 范围。
- 未完成事项。
- 风险或疑点。

### 完成后要求

- 完成后不要提交 Git，等待顾问窗口复核。
- 顾问/决策确认后，可归档第二轮指令并进入第三轮规划。
