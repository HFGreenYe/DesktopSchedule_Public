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

第二轮 B 不允许一次性完整执行。执行窗口必须按 B-1 ~ B-5 的小工单逐步推进，每次只执行决策窗口明确下发的当前小节。

### 本轮允许修改

- `src/data/database.py`
- `manage_instruction/Work_Log.md`

### 本轮禁止修改

- 不修改 `src/ui/`。
- 不修改 `main.py`。
- 不修改 `src/repositories/`，除非发现第二轮 A 遗留的 import 问题；如需修改须先说明。
- 不修改 `src/data/connection.py`，除非发现连接基础对象边界存在明确错误；如需修改须先说明。
- 不修改 `src/data/models.py`，除非发现模型导入边界存在明确错误；如需修改须先说明。
- 不修改 `src/theme/`。
- 不修改 `src/utils/signals.py`。
- 不修改 `requirements.txt`。
- 不修改 `schedule.db`。
- 不改数据库字段含义、默认值、字段名、表名。
- 不改 `_migrate_db` 的迁移目标、迁移顺序、旧数据补值策略。
- 不迁移业务 service。
- 不迁移重复日程逻辑。

### 第二轮 B 小工单拆分

#### 第二轮 B-1：database.py import 与边界清理

目标：
- 只整理 `src/data/database.py` 顶部 import 边界。
- 移除明显不再需要的模型导入，例如 `BaseModel`。
- 如当前仍存在 `from peewee import *`，只允许替换为 `database.py` 当前实际使用的最小显式导入；不得引入模型字段重构。
- 不改 `_connect`、`_create_tables`、`_migrate_db`、`DatabaseManager` 对外方法。
- 不改变任何运行逻辑。

允许修改：
- `src/data/database.py`
- `manage_instruction/Work_Log.md`

禁止修改：
- 不修改 `src/data/connection.py`。
- 不修改 `src/data/models.py`。
- 不修改 `src/repositories/`。
- 不修改 `src/ui/`。
- 不修改 `schedule.db`。
- 不改迁移逻辑、建表逻辑、业务逻辑。

验收：
- `src.data.database` 可 import。
- `db_manager.get_all_schedules()` 可调用。
- `db_manager.get_active_categories()` 可调用。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。
- `git diff --name-only` 只包含 `src/data/database.py` 和 `manage_instruction/Work_Log.md`。

#### 第二轮 B-2：只抽离 schedules 表迁移块

目标：
- 只把 `_migrate_db` 中针对 `schedules` 表的迁移逻辑抽成私有方法，例如 `_migrate_schedules_table()`。
- `_migrate_db` 中仍按原顺序先处理 schedules，再处理 categories。
- 只移动原有代码块，不改变迁移字段、默认值、字段名、表名、补值策略和异常处理语义。
- 不改条件判断，不改异常捕获，不改 `migrate(...)` 调用顺序，不合并任何迁移分支。
- 不处理 categories 表迁移块。

允许修改：
- `src/data/database.py`
- `manage_instruction/Work_Log.md`

禁止修改：
- 不修改 `src/data/connection.py`。
- 不修改 `src/data/models.py`。
- 不修改 `src/repositories/`。
- 不修改 `src/ui/`。
- 不修改 `schedule.db`。
- 不改 `DatabaseManager` 对外方法。
- 不改任何非迁移相关业务方法。
- 不重写迁移逻辑，不重命名迁移字段，不改变已有数据库兼容策略。

验收：
- `src.data.database` 可 import。
- `db_manager` 可创建。
- `db_manager.get_all_schedules()` 可调用。
- 临时日程创建/删除路径可用。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。
- `git diff --name-only` 只包含 `src/data/database.py` 和 `manage_instruction/Work_Log.md`。

#### 第二轮 B-3：只抽离 categories 表迁移块

目标：
- 只把 `_migrate_db` 中针对 `categories` 表的迁移逻辑抽成私有方法，例如 `_migrate_categories_table()`。
- `_migrate_db` 中仍按原顺序先处理 schedules，再处理 categories。
- 只移动原有代码块，不改变迁移字段、默认值、字段名、表名、补值策略和异常处理语义。
- 不改条件判断，不改异常捕获，不改 `migrate(...)` 调用顺序，不合并任何迁移分支。
- 不再改 schedules 表迁移块。

允许修改：
- `src/data/database.py`
- `manage_instruction/Work_Log.md`

禁止修改：
- 不修改 `src/data/connection.py`。
- 不修改 `src/data/models.py`。
- 不修改 `src/repositories/`。
- 不修改 `src/ui/`。
- 不修改 `schedule.db`。
- 不改 `DatabaseManager` 对外方法。
- 不改任何非迁移相关业务方法。
- 不重写迁移逻辑，不重命名迁移字段，不改变已有数据库兼容策略。

验收：
- `src.data.database` 可 import。
- `db_manager` 可创建。
- `db_manager.get_active_categories()` 可调用。
- 临时分类创建/读取/硬删除路径可用。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。
- `git diff --name-only` 只包含 `src/data/database.py` 和 `manage_instruction/Work_Log.md`。

#### 第二轮 B-4：database.py 迁移入口与职责复核

目标：
- 复核 `_migrate_db` 是否只承担迁移调度职责，例如调用 `_migrate_schedules_table()` 和 `_migrate_categories_table()`。
- 可做极小范围的命名、注释或空行整理，让 `database.py` 的连接、建表、迁移边界更清楚。
- 不抽取业务方法。
- 不移动重复日程逻辑。
- 不改变 `DatabaseManager` 对外 API。

允许修改：
- `src/data/database.py`
- `manage_instruction/Work_Log.md`

禁止修改：
- 不修改 `src/data/connection.py`。
- 不修改 `src/data/models.py`。
- 不修改 `src/repositories/`。
- 不修改 `src/ui/`。
- 不修改 `schedule.db`。
- 不改迁移目标、迁移顺序、旧数据补值策略。
- 不改业务行为。

验收：
- `src.data.connection`、`src.data.models`、`src.data.database` 均可 import。
- `db_manager.get_all_schedules()`、`db_manager.get_active_categories()` 可调用。
- 临时分类创建/硬删除路径可用。
- 临时日程创建/删除路径可用。
- GUI smoke test 通过，或记录环境限制并执行 `import main` 兜底。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。
- `git diff --name-only` 只包含 `src/data/database.py` 和 `manage_instruction/Work_Log.md`。

#### 第二轮 B-5：第二轮 B 整体技术验收

目标：
- 不做新的代码改动。
- 只对 B-1 ~ B-4 的 import 边界、迁移入口、基础读写路径、GUI 启动路径和 diff 范围做总体验收。

允许修改：
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅当顾问窗口要求维护复核锚点）

禁止修改：
- 不修改任何源码文件。
- 不修改 `src/data/database.py`。
- 不修改 `src/data/connection.py`。
- 不修改 `src/data/models.py`。
- 不修改 `src/repositories/`。
- 不修改 `src/ui/`。
- 不修改 `main.py`。
- 不修改 `schedule.db`。

验收：
- `src.data.connection`、`src.data.models`、`src.data.database` 可 import。
- `ScheduleRepository`、`CategoryRepository` 可 import。
- `db_manager` 可创建。
- `get_all_schedules`、`get_schedules_for_date`、`get_active_categories`、`get_category_map` 可调用。
- 临时分类写入/清理路径可用。
- 临时日程写入/清理路径可用。
- GUI smoke test 通过，或记录环境限制并执行 `import main` 兜底。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。
- `git diff --name-only` 只包含允许的日志/提示词文件，或本轮开始前已存在的管理文档改动。

### Work_Log.md 记录要求

每个 B 小工单都必须记录：

- 本轮任务名称，例如：第二轮 B-1（database.py import 与边界清理）。
- 实际修改文件。
- 修改是否只涉及本小工单允许的边界。
- 验证命令和结果。
- diff 范围检查结果。
- 未完成事项。
- 风险或疑点，尤其是是否存在循环导入、迁移行为变化或数据库文件变更风险。

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

