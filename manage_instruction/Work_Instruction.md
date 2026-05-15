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

## 第二轮当前状态

- 第二轮 A：已完成并归档。
- 第二轮 B：已完成并归档。
- 第二轮 C：已完成并归档。
- 当前待执行：第二轮 D（Data 层整体技术验收）。

## 第二轮总体禁止事项

- 不修改任何 `src/ui/` 文件。
- 不修改 `main.py`。
- 不修改 `src/theme/`。
- 不修改 `src/utils/signals.py`。
- 不修改 `requirements.txt`。
- 不保留 `schedule.db` 变更。
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

# 第二轮 D - Data 层整体技术验收

## 本轮目标

在第二轮 A/B/C 完成后，不做新的代码改动，只对 Data 层整理结果做总体验收，确认模型拆分、数据库初始化、Repository、`db_manager` 兼容门面和旧 UI 启动路径均未破坏。

第二轮 D 不允许一次性完整执行。执行窗口必须按 D-1 ~ D-5 的小工单逐步推进，每次只执行决策窗口明确下发的当前小节。

## 本轮允许修改

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅当顾问窗口要求维护复核锚点）

## 本轮禁止修改

- 不修改任何源码文件。
- 不修改 `src/data/database.py`。
- 不修改 `src/data/connection.py`。
- 不修改 `src/data/models.py`。
- 不修改 `src/repositories/`。
- 不修改 `src/ui/`。
- 不修改 `main.py`。
- 不修改 `src/theme/`。
- 不修改 `src/utils/signals.py`。
- 不修改 `requirements.txt`。
- 不修改 `Work_Snapshot.md`。
- 不修改 `Work_Formulation.md`。
- 不保留 `schedule.db` 变更；允许为了验收进行临时数据库写入，但必须清理，并确认 `git diff --name-only -- schedule.db` 无输出。
- 不做任何新功能。
- 不改业务逻辑。
- 不改 `db_manager` 公开 API。
- 不改 Repository 方法名、参数、返回语义、查询排序、过滤或删除策略。

若开工前已有管理文档 diff，需在 `Work_Log.md` 中单独记录，不视为本轮源码改动。

---

## 第二轮 D 小工单拆分

### 第二轮 D-1：Data 层静态边界与 import 复核

目标：

- 复核第二轮 A/B/C 后的核心 import 边界。
- 确认 `src.data.connection`、`src.data.models`、`src.data.database`、Repository、`db_manager` 均可 import。
- 静态确认 Repository 不依赖 `db_manager`、UI 或 `src.data.database`。
- 静态确认 `src/repositories/__init__.py` 只做轻量导出。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅当顾问窗口要求维护复核锚点）

禁止修改：

- 不修改任何源码文件。
- 不修改 `schedule.db`。

验收：

- `src.data.connection`、`src.data.models`、`src.data.database` 可 import。
- `ScheduleRepository`、`CategoryRepository`、`src.repositories`、`db_manager` 可 import。
- `src.data.connection.db` 与 `src.data.database.db` 指向同一个对象。
- `DB_PATH` 一致。
- `rg` 检查 `src/repositories` 中无 `db_manager`、UI、`src.data.database` 或 `database.py` 模型导入痕迹。
- `src/repositories/__init__.py` 不导入 `db_manager`、UI、`src.data.database`。
- `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

### 第二轮 D-2：Data 层读路径回归验收

目标：

- 不写数据库。
- 验证 `db_manager` 兼容门面的核心读路径仍可用。
- 有样本时补充验证单项读取与分类状态判断。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅当顾问窗口要求维护复核锚点）

禁止修改：

- 不修改任何源码文件。
- 不修改 `schedule.db`。

验收：

- `db_manager.get_all_schedules()` 返回 list。
- `db_manager.get_schedules_for_date(date.today())` 返回 list。
- `db_manager.get_active_categories()` 返回 list。
- `db_manager.get_category_map()` 返回 dict。
- 有分类样本时，`db_manager.get_category(cat_id)` 可返回对应分类。
- 有分类样本时，`db_manager.check_category_status(cat_id)` 返回允许状态。
- 有日程样本时，可通过公开读路径确认样本对象基本字段可访问。
- `schedule.db` 无 tracked diff。
- 最终只允许管理文档 diff。

### 第二轮 D-3：分类写路径临时验收

目标：

- 允许为了验收临时写入分类数据。
- 验证分类创建、字段更新、软删除、硬删除路径。
- 临时分类必须清理干净。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅当顾问窗口要求维护复核锚点）

禁止修改：

- 不修改任何源码文件。
- 不保留 `schedule.db` 变更。

验收：

- 使用唯一临时名称调用 `add_category` 创建分类。
- 使用 `get_category` 确认临时分类可读取。
- 调用 `update_category_fields`，并确认返回成功。
- 调用 `soft_delete_category`，并确认返回成功。
- 调用 `hard_delete_category`，并确认返回成功。
- 清理后 `get_category(cat_id)` 返回 `None`。
- 确认 `schedule.db` 无 tracked diff。
- `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt` 无 diff。

### 第二轮 D-4：日程写路径临时验收

目标：

- 允许为了验收临时写入日程数据。
- 验证日程状态、置顶、字段更新的写回恢复路径。
- 验证临时日程创建与删除路径。
- 所有样本改动必须恢复，临时日程必须清理。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅当顾问窗口要求维护复核锚点）

禁止修改：

- 不修改任何源码文件。
- 不保留 `schedule.db` 变更。

验收：

- 有日程样本时，`update_schedule_status` 写入测试值后恢复原值。
- 有日程样本时，`toggle_pin_status` 切换后恢复原值。
- 有日程样本时，`update_schedule_fields` 写入测试 title 后恢复原 title。
- 使用 `add_schedule` 创建 `repeat_rule='none'` 的唯一临时日程。
- 使用 `delete_schedule` 删除临时日程。
- 删除后 `get_all_schedules()` 找不到该临时 id。
- 如没有可安全恢复的样本，记录跳过原因，不造假通过。
- 确认 `schedule.db` 无 tracked diff。
- `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt` 无 diff。

### 第二轮 D-5：GUI smoke 与第二轮整体验收收口

目标：

- 汇总 D-1 ~ D-4 的验收结果。
- 验证旧 UI 启动路径仍可创建并关闭主窗口。
- 确认第二轮 A/B/C/D 的 Data 层整理具备归档条件。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅当顾问窗口要求维护复核锚点）

禁止修改：

- 不修改任何源码文件。
- 不保留 `schedule.db` 变更。

验收：

- 读取并汇总 `Work_Log.md` 中 D-1 ~ D-4 记录。
- 优先执行 `MainWindow` 创建并关闭的 GUI smoke test。
- 如 GUI smoke 受环境限制失败，记录原因并执行 `import main` 兜底。
- 复跑最小 import 验证：`src.data.connection`、`src.data.models`、`src.data.database`、Repository、`db_manager`。
- 复跑最小读路径验证：`get_all_schedules`、`get_schedules_for_date`、`get_active_categories`、`get_category_map`。
- 确认 `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。
- `git diff --name-only` 最终只包含允许的管理文档 diff。
- 记录是否可以归档第二轮并进入第三轮规划。

---

## Work_Log.md 记录要求

每个 D 小工单都必须记录：

- 本轮任务名称，例如：第二轮 D-1（Data 层静态边界与 import 复核）。
- 开工前是否已有管理文档 diff。
- 实际修改文件。
- 执行分支或跳过项说明。
- 验证命令和结果。
- 临时数据库写入是否已清理。
- `schedule.db` 是否无 tracked diff。
- diff 范围检查结果。
- 未完成事项。
- 风险或疑点。

## 完成后要求

- 每个 D 小工单完成后不要提交 Git，等待顾问窗口复核。
- D-5 顾问/决策确认后，可归档第二轮指令和日志，再进入第三轮规划。
