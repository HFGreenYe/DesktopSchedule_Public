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

# 后续小工单预案：第二轮 C/D

以下内容用于固定第二轮后续边界，防止后续窗口遗忘。除非决策窗口明确下发对应小工单，否则执行窗口不得提前执行。

后续审查时可按需只读取：

- “第二轮总体允许范围 / 总体禁止事项”
- 对应小工单章节，例如“第二轮 C”
- `Work_Log.md` 中对应轮次记录

这样比每次读取整份 `Work_Instruction.md` 更省上下文，但不能忽略总体禁止事项。

---

## 第二轮 C - Repository 依赖清理与导入关系复核

### 本轮目标

确认 Repository 只依赖模型与数据基础设施，不反向依赖 `DatabaseManager` 或 UI，进一步降低循环导入风险。

本轮主要是依赖关系清理与复核，不做业务行为变更。

第二轮 C 不允许一次性完整执行。执行窗口必须按 C-1 ~ C-5 的小工单逐步推进，每次只执行决策窗口明确下发的当前小节。

### 本轮允许修改

- `src/repositories/category_repository.py`
- `src/repositories/schedule_repository.py`
- `src/repositories/__init__.py`
- `manage_instruction/Work_Log.md`

### 本轮禁止修改

- 不修改 `src/data/database.py`，除非 C-1/C-2 发现 repository 导入边界存在明确兼容问题；如需修改须先说明。
- 不修改 `src/data/connection.py`。
- 不修改 `src/data/models.py`，除非 C-1/C-2 发现模型导入边界存在明确兼容问题；如需修改须先说明。
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
- 不新增抽象基类。
- 不做 repository 大重构。
- 若开工前已有管理文档 diff，需在日志中单独记录，不视为本轮源码改动。

### 第二轮 C 小工单拆分

#### 第二轮 C-1：Repository 静态依赖审查

目标：
- 不改代码，只做静态审查。
- 检查 `src/repositories/schedule_repository.py`、`src/repositories/category_repository.py`、`src/repositories/__init__.py` 是否依赖 `db_manager`、UI 或 `src.data.database`。
- 确认 Repository 是否只依赖 `src.data.models` 中的模型，且保留构造函数注入能力。

允许修改：
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅当顾问窗口要求维护复核锚点）

禁止修改：
- 不修改任何源码文件。
- 不修改 `src/repositories/`。
- 不修改 `src/data/`。
- 不修改 `src/ui/`。
- 不修改 `main.py`。
- 不修改 `schedule.db`。

验收：
- 静态检查 repository 文件中是否存在 `db_manager`、`src.ui`、`src.data.database` 或从 `database.py` 导入模型的痕迹。
- 静态检查 repository 文件中是否从 `src.data.models` 导入 `Schedule`、`Category`。
- `ScheduleRepository`、`CategoryRepository` 可单独 import。
- `src/repositories/__init__.py` 可 import。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。
- `git diff --name-only` 只包含允许的日志/提示词文件。

#### 第二轮 C-2：Repository import 残留修正

目标：
- 仅当 C-1 发现残留导入问题时，做最小 import 修正。
- 如没有问题，只记录“无需改代码”。
- 保留 `category_model`、`schedule_model` 构造函数注入能力。
- 不改变任何 Repository 方法名、参数、返回语义。

允许修改：
- `src/repositories/category_repository.py`
- `src/repositories/schedule_repository.py`
- `manage_instruction/Work_Log.md`

禁止修改：
- 不修改 `src/repositories/__init__.py`。
- 不修改 `src/data/database.py`。
- 不修改 `src/data/connection.py`。
- 不修改 `src/data/models.py`。
- 不修改 `src/ui/`。
- 不修改 `main.py`。
- 不修改 `schedule.db`。
- 不改变查询排序、过滤、删除策略。
- 不新增抽象基类。
- 不做 repository 大重构。

验收：
- `ScheduleRepository`、`CategoryRepository` 可单独 import。
- 默认模型来源如需验证，应来自 `src.data.models`。
- 构造函数注入能力保留。
- `db_manager` 可 import。
- `get_all_schedules`、`get_active_categories` 可调用。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。
- 如无需代码改动，`git diff --name-only` 只包含 `manage_instruction/Work_Log.md`。
- 如确有 import 修正，`git diff --name-only` 只包含本小工单允许文件。

#### 第二轮 C-3：repositories/__init__.py 轻量导出复核

目标：
- 检查 `src/repositories/__init__.py` 是否只做轻量导出，不触发数据库连接、`db_manager` 创建、UI 导入或其他重型副作用。
- 如无需整理，只记录“无需改代码”。
- 如需整理，只做最小导出关系修改。

允许修改：
- `src/repositories/__init__.py`
- `manage_instruction/Work_Log.md`

禁止修改：
- 不修改 `src/repositories/category_repository.py`。
- 不修改 `src/repositories/schedule_repository.py`。
- 不修改 `src/data/`。
- 不修改 `src/ui/`。
- 不修改 `main.py`。
- 不修改 `schedule.db`。
- 不新增抽象基类。
- 不做 repository 大重构。

验收：
- `from src.repositories import ScheduleRepository, CategoryRepository` 可执行。
- `ScheduleRepository`、`CategoryRepository` 可单独 import。
- 静态检查 `src/repositories/__init__.py` 不导入 `db_manager`、UI、`src.data.database`。
- `db_manager` 可 import。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。
- 如无需代码改动，`git diff --name-only` 只包含 `manage_instruction/Work_Log.md`。
- 如确有最小整理，`git diff --name-only` 只包含本小工单允许文件。

#### 第二轮 C-4：Repository 行为回归验收

目标：
- 不做新的架构改动。
- 验证 Repository 相关委托路径在依赖清理后行为未破坏。
- 覆盖已委托读写路径、临时分类/日程增删、GUI smoke、diff 范围。

允许修改：
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅当顾问窗口要求维护复核锚点）

禁止修改：
- 不修改任何源码文件。
- 不修改 `src/repositories/`。
- 不修改 `src/data/`。
- 不修改 `src/ui/`。
- 不修改 `main.py`。
- 不保留 `schedule.db` 变更；允许验收临时写入，但必须清理并确认 `schedule.db` 无 tracked diff。

验收：
- `ScheduleRepository`、`CategoryRepository`、`src.repositories`、`db_manager` 可 import。
- 验证读路径：
  - `get_all_schedules`
  - `get_schedules_for_date`
  - `get_active_categories`
  - `get_category_map`
- 验证分类临时写路径：
  - `add_category`
  - `update_category_fields`
  - `soft_delete_category`
  - `hard_delete_category`
- 验证日程临时写路径：
  - 使用 `add_schedule` 创建 `repeat_rule='none'` 的临时日程。
  - 使用 `delete_schedule` 删除临时日程。
  - 删除后 `get_all_schedules()` 找不到该临时 id。
- GUI smoke test 通过，或记录限制并执行 `import main` 兜底。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。
- `git diff --name-only` 只包含允许的日志/提示词文件。

#### 第二轮 C-5：第二轮 C 整体验收与归档准备

目标：
- 不做代码改动。
- 对 C-1 ~ C-4 的依赖审查、import 边界、轻量导出、行为回归结果做总体验收。
- 为第二轮 C 归档和进入第二轮 D 做准备。

允许修改：
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅当顾问窗口要求维护复核锚点）

禁止修改：
- 不修改任何源码文件。
- 不修改 `src/repositories/`。
- 不修改 `src/data/`。
- 不修改 `src/ui/`。
- 不修改 `main.py`。
- 不修改 `schedule.db`。
- 不修改 `requirements.txt`。

验收：
- Repository 不依赖 `db_manager`、UI 或 `src.data.database` 的结论明确。
- `src/repositories/__init__.py` 轻量导出结论明确。
- `ScheduleRepository`、`CategoryRepository`、`src.repositories`、`db_manager` 可 import。
- 已委托读写路径关键验证通过。
- GUI smoke test 通过，或记录限制并执行 `import main` 兜底。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。
- `git diff --name-only` 只包含允许的日志/提示词文件。

### Work_Log.md 记录要求

每个 C 小工单都必须记录：

- 本轮任务名称，例如：第二轮 C-1（Repository 静态依赖审查）。
- 实际修改文件。
- Repository 当前依赖关系结论。
- 是否仍存在从 repository 到 `db_manager`、UI 或 `src.data.database` 的依赖。
- 是否保留构造函数注入能力。
- 验证命令和结果。
- diff 范围检查结果。
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

