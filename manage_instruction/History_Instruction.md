# History Instruction

本文件用于归档已经完成或废弃的历史执行指令，避免 `Work_Instruction.md` 长期累积内容、增加后续窗口读取成本。

使用规则：

- `Work_Instruction.md` 只保留当前正在执行或下一步即将执行的指令。
- 当前指令完成、验收并提交 Git 后，再将该指令移动到本文件归档。
- 归档时保留任务标题、执行日期、对应 Git commit、结果摘要和后续备注。
- 不把未完成的当前任务提前归档。

---

## 归档记录

## 2026-05-14 第一轮总归档 - 基建与 Repository 兼容层

状态：已完成。

结果：第一轮架构改写已收口，并已由用户创建 checkpoint：

```text
cbf0175 checkpoint: complete first architecture refactor round
```

第一轮拆为两个主要部分：

- 第一轮 A：目录骨架、ThemeManager/QSS 占位、兼容式 EventBus。
- 第一轮 B：Repository 薄封装、`DatabaseManager` 兼容委托、迁移作用域修复、整体验收。

第一轮的核心架构变化：

```text
改写前：UI -> db_manager/database.py -> Peewee Model
改写后：UI -> db_manager 兼容门面 -> Repository -> Peewee Model/database.py
```

第一轮没有做的事：

- 未拆 UI 大文件。
- 未让 UI 直接调用 Repository。
- 未迁移重复日程高风险写入逻辑。
- 未实现四象限、搜索、筛选、导出、同步等新功能。
- 未正式接入完整主题/换肤 UI。

第一轮验收结论：

- 应用可启动。
- Repository import 可用。
- `db_manager` 读写路径基础验证通过。
- GUI smoke test 通过。
- `src/ui` 未在 B 轮被修改。
- `schedule.db` 未留下 tracked diff。

## 2026-05-13 第一轮 A - 架构骨架 + 主题/EventBus 基建

状态：已完成。

对应提交：

- `3ca93f1 refactor: add architecture skeleton theme manager and event bus`
- `2803436 fix: add missing zhdate dependency`
- `a7bca33 docs: clarify python sandbox validation issue`

### 任务目标

执行第一轮 A，只建立低风险基础设施，不触碰数据库逻辑，不接入旧 UI，不实现新功能。

本轮完成后，项目外部行为应保持不变。

### 允许修改

- `src/models/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `src/theme/`
- `src/utils/signals.py`
- `manage_instruction/Work_Log.md`

如发现必须修改上述范围以外的文件，需要先停止并说明原因，不得擅自扩大范围。

### 禁止修改

- 不修改 `src/data/database.py`。
- 不修改任何现有 UI 页面逻辑。
- 不替换旧 UI 中已有的 `setStyleSheet(...)`。
- 不接入换肤 UI。
- 不实现搜索、筛选、导出、同步、四象限等新功能。
- 不修改数据库字段、迁移逻辑或 `schedule.db`。
- 不修改 `Work_Snapshot.md`，除非决策窗口另行要求。

### 具体要求

1. 建立以下目录，并添加 `__init__.py`：

```text
src/models/
src/repositories/
src/services/
src/controllers/
src/theme/
```

2. 新增主题基础文件：

```text
src/theme/theme_manager.py
src/theme/light.qss
src/theme/dark.qss
```

3. `ThemeManager` 只提供基础能力：

- 读取 QSS 文件。
- 应用 QSS 到 `QApplication`。
- 刷新动态属性样式，例如对 widget 执行 `unpolish/polish/update`。

4. `ThemeManager` 本轮不做的事：

- 不主动应用到现有应用启动流程。
- 不替换旧页面样式。
- 不实现完整换肤 UI。
- 不改变当前默认视觉效果。

5. 扩展 `src/utils/signals.py` 为兼容式事件总线。

硬性兼容要求：

- 必须保留 `global_signals` 名称。
- 必须保留无参 `skin_changed = pyqtSignal()`。
- 不修改旧信号签名。

6. 可新增以下信号：

```python
theme_changed = pyqtSignal(str)
schedule_added = pyqtSignal(object)
schedule_updated = pyqtSignal(object)
schedule_deleted = pyqtSignal(int)
category_changed = pyqtSignal()
```

7. 本轮只提供事件通道，不要求旧窗口迁移到事件总线。

### 验收要求

- 应用仍可启动。
- `from src.utils.signals import global_signals` 可用。
- `global_signals.skin_changed` 仍是无参信号，可连接无参 slot 并 emit。
- `ThemeManager` 可被 import。
- `ThemeManager` 能读取 `light.qss` 和 `dark.qss`。
- 没有修改 `src/data/database.py`。
- 已更新 `manage_instruction/Work_Log.md`。

### 验收摘要

- 执行窗口按步骤完成目录骨架、Theme 基础文件、`ThemeManager` 和 `signals.py` 兼容式扩展。
- `signals.py` 保留 `global_signals` 和无参 `skin_changed`，新增事件总线信号。
- `ThemeManager` 提供读取 QSS、应用 QSS、刷新 widget 样式能力。
- 初期 Python 验证受沙箱/解释器路径限制失败，后续用户本地 CMD 验证通过。
- 用户侧验证记录：
  - signals import 输出 `signals ok`。
  - ThemeManager 读取 QSS 输出 `theme ok`。
  - `.\.venv\Scripts\python.exe .\main.py` 应用成功启动，图标正常。
- 执行窗口后续确认沙箱外权限下 signals 验证通过。

### 后续备注

- 第一轮 A 不接入旧 UI，不改变默认视觉效果。
- 后续任务切换 `Work_Instruction.md` 前，应先把已完成指令归档到本文件。

## 2026-05-14 第一轮 B - Repository + DatabaseManager 兼容委托（已完成归档）

状态：已完成。

完成范围摘要：
- Repository 薄封装完成（`ScheduleRepository`、`CategoryRepository`）。
- DatabaseManager 低风险公开方法兼容委托完成（读路径与低风险写路径逐步委托，UI 仍通过 `db_manager` 调用）。
- `_migrate_db` 中 `migrator` 作用域风险修复完成。
- B-15 整体技术验收通过（import、读写路径、GUI smoke、范围检查通过）。

关键提交摘要（简述）：

- `562eb0b docs: prepare repository refactor instruction`
- `b63c097 refactor: add schedule and category repositories`
- `dc5c68a refactor: delegate basic read methods to repositories`
- `f93f902 refactor: delegate schedule date query and category map`
- `e012696 fix: define migrator for category list type migration`
- `9c504d0 refactor: delegate category lookup to repository`
- `ee5a317 refactor: delegate category status check`
- `5c9b449 refactor: delegate category field updates`
- `ab29c0e refactor: delegate category creation`
- `71cdcbf refactor: delegate category soft delete`
- `64f0427 refactor: delegate category hard delete`
- `a493df6 refactor: delegate schedule status update`
- `cc0274b refactor: delegate schedule pin toggle`
- `b2894b4 refactor: delegate schedule field updates`
- `1079352 refactor: delegate schedule deletion`
- `333b7f2 test: validate repository delegation round`
- `31bc1f7 docs: close out repository delegation round`
- `d57c9d6 docs: archive repository delegation instructions`

备注：
- 第一轮 B 的执行明细与验证命令见 `Work_Log.md`。
- 下一阶段应在 `Work_Instruction.md` 发布新任务，不再复用本轮指令文本。


---

## 2026-05-14 第二轮 A - Data 层连接与 Peewee 模型拆分（已完成归档）

状态：已完成。

# 当前执行任务：第二轮 A - 只拆 Peewee 模型到 src/data/models.py

## 本轮目标

第二轮 A 的总目标是创建 `src/data/connection.py` 和 `src/data/models.py`，并把 Peewee 模型定义从 `src/data/database.py` 移入 `models.py`。

但第二轮 A 不允许一次性完整执行。执行窗口必须按 A-1 ~ A-6 的小工单逐步推进，每次只执行当前被明确下发的小节。

当前建议第一步只执行：

```text
第二轮 A-1：只新增 src/data/connection.py，暂不切换旧代码引用。
```

本轮只处理数据层最底部依赖：

- `BASE_DIR`
- `DB_PATH`
- `db`
- `BaseModel`
- `Category`
- `Schedule`

同时调整必要 import，让现有行为保持不变。

## 第二轮 A 小工单拆分

### 第二轮 A-1：只新增 connection.py，不切换旧引用

目标：

- 新增 `src/data/connection.py`。
- 在该文件中定义与当前 `src/data/database.py` 一致的 `BASE_DIR`、`DB_PATH`、`db = SqliteDatabase(DB_PATH)`。
- 暂不修改 `src/data/database.py`。
- 暂不新增或修改 `src/data/models.py`。
- 暂不修改 Repository。

允许修改：

- `src/data/connection.py`
- `manage_instruction/Work_Log.md`

禁止修改：

- 不修改 `src/data/database.py`。
- 不修改 `src/data/models.py`。
- 不修改 `src/repositories/`。
- 不修改 `src/ui/`。
- 不修改 `schedule.db`。
- 不修改业务逻辑。

验收：

- `from src.data.connection import db, BASE_DIR, DB_PATH` 可执行。
- `DB_PATH` 与 `src.data.database.DB_PATH` 一致。
- `src.data.database` 和 `db_manager` 仍可 import。
- 基础读路径仍可调用。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。
- `git diff --name-only` 只包含 `src/data/connection.py` 和 `manage_instruction/Work_Log.md`，以及本轮开始前已有的管理文档改动。

### 第二轮 A-2：database.py 改用 connection.py 的 db

目标：

- 只让 `src/data/database.py` 从 `src/data/connection.py` 导入 `BASE_DIR`、`DB_PATH`、`db`。
- 删除或替换 `database.py` 中原本直接创建 `SqliteDatabase(DB_PATH)` 的定义。
- 暂不移动 Peewee 模型。
- 暂不修改 Repository。

允许修改：

- `src/data/database.py`
- `manage_instruction/Work_Log.md`

禁止修改：

- 不修改 `src/data/models.py`。
- 不修改 `src/repositories/`。
- 不修改 `src/ui/`。
- 不修改业务逻辑。
- 不改 `_migrate_db` 迁移步骤、迁移顺序和补值策略。

验收：

- `src.data.connection` 可 import。
- `src.data.database` 可 import。
- `db_manager` 可创建。
- `db_manager.get_all_schedules()`、`get_active_categories()`、`get_schedules_for_date(date.today())` 可调用。
- 临时分类增删路径可用。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。

### 第二轮 A-3：新增 models.py 并移动 BaseModel/Category/Schedule

目标：

- 新增 `src/data/models.py`。
- 将 `BaseModel`、`Category`、`Schedule` 从 `database.py` 移入 `models.py`。
- `models.py` 必须从 `connection.py` 导入 `db`。
- `database.py` 从 `models.py` 导入 `BaseModel`、`Category`、`Schedule`。
- 暂不修改 Repository。

允许修改：

- `src/data/models.py`
- `src/data/database.py`
- `manage_instruction/Work_Log.md`

禁止修改：

- 不修改 `src/repositories/`。
- 不修改 `src/ui/`。
- 不改字段含义、默认值、字段名、表名。
- 不改 `_migrate_db` 迁移步骤、迁移顺序和补值策略。
- 不改业务逻辑。

验收：

- `src.data.models` 可 import。
- `src.data.database` 可 import。
- `db_manager` 可创建。
- 基础读路径可调用。
- 临时分类增删路径可用。
- 临时日程创建/删除路径可用。
- GUI smoke test 通过或记录环境限制并执行 `import main` 兜底。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。

### 第二轮 A-4：调整 ScheduleRepository 模型导入来源

目标：

- 只调整 `src/repositories/schedule_repository.py`。
- 如果当前从 `src.data.database` 延迟导入 `Schedule`，改为从 `src.data.models` 导入 `Schedule`。
- 保留构造函数注入模型类的兼容能力。
- 不改变任何 Repository 方法语义。

允许修改：

- `src/repositories/schedule_repository.py`
- `manage_instruction/Work_Log.md`

禁止修改：

- 不修改 `src/data/database.py`。
- 不修改 `src/data/models.py`，除非发现 A-3 明显遗漏且先说明。
- 不修改 `src/repositories/category_repository.py`。
- 不修改 `src/ui/`。
- 不改日程 CRUD 返回语义。

验收：

- `ScheduleRepository` 可单独 import。
- `db_manager` 可 import。
- `db_manager.get_all_schedules()` 可调用。
- `db_manager.get_schedules_for_date(date.today())` 可调用。
- 临时日程创建/删除路径可用。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。

### 第二轮 A-5：调整 CategoryRepository 模型导入来源

目标：

- 只调整 `src/repositories/category_repository.py`。
- 如果当前从 `src.data.database` 延迟导入 `Category`、`Schedule`，改为从 `src.data.models` 导入。
- 保留构造函数注入模型类的兼容能力。
- 不改变任何 Repository 方法语义。

允许修改：

- `src/repositories/category_repository.py`
- `manage_instruction/Work_Log.md`

禁止修改：

- 不修改 `src/data/database.py`。
- 不修改 `src/data/models.py`，除非发现 A-3 明显遗漏且先说明。
- 不修改 `src/repositories/schedule_repository.py`。
- 不修改 `src/ui/`。
- 不改清单 CRUD、状态判断、删除策略返回语义。

验收：

- `CategoryRepository` 可单独 import。
- `db_manager` 可 import。
- `db_manager.get_active_categories()` 可调用。
- `db_manager.get_category_map()` 可调用。
- 临时分类创建、读取、软删、硬删路径可用。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。

### 第二轮 A-6：第二轮 A 整体验收

目标：

- 不做新的代码改动。
- 对 A-1 ~ A-5 的模型拆分和导入关系做总体验收。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅当顾问窗口要求维护复核锚点）

禁止修改：

- 不修改任何源码文件。
- 不修改 `src/data/connection.py`。
- 不修改 `src/data/models.py`。
- 不修改 `src/data/database.py`。
- 不修改 `src/repositories/`。
- 不修改 `src/ui/`。
- 不修改 `schedule.db`。

验收：

- `src.data.connection`、`src.data.models`、`src.data.database` 可 import。
- `ScheduleRepository`、`CategoryRepository` 可 import。
- `db_manager` 可创建。
- 读路径可调用：
  - `get_all_schedules`
  - `get_schedules_for_date`
  - `get_active_categories`
  - `get_category_map`
- 分类临时写路径可用。
- 日程临时写路径可用。
- GUI smoke test 通过或执行 `import main` 兜底。
- `models.py` 没有从 `database.py` 导入 `db`。
- Repository 没有依赖 `db_manager`。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。
- `git diff --name-only` 只包含允许的日志/提示词文件，或本轮开始前已有的管理文档改动。

---



---

## 2026-05-15 第二轮 B - 数据库连接与迁移边界整理（已完成归档）

状态：已完成。

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

## 第二轮 C - Repository 依赖清理与导入关系复核（已完成归档）

归档时间：2026-05-15。

对应提交：

- `9054c43 docs: finalize round c repository review instructions`
- `39237f1 docs: record round c1 repository dependency review`
- `92df0c0 docs: record round c2 repository import review`
- `a9c66ce docs: record round c3 repository package review`
- `e4a2fb0 docs: record round c4 repository behavior regression`
- `5b95c18 docs: close round c repository dependency review`

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

## 第二轮 D - Data 层整体技术验收（已完成归档）

归档时间：2026-05-17。

对应提交：

- `51bf837 docs: record round d1 data import boundary review`
- `56dab09 docs: record round d2 data read path regression`
- `f4f7a11 docs: record round d3 category write path validation`
- `005df9b docs: record round d4 schedule write path validation`
- `10c4fbc docs: close round d data layer validation`

### 本轮目标

在第二轮 A/B/C 完成后，不做新的代码改动，只对 Data 层整理结果做总体验收，确认模型拆分、数据库初始化、Repository、`db_manager` 兼容门面和旧 UI 启动路径均未破坏。

第二轮 D 不允许一次性完整执行。执行窗口必须按 D-1 ~ D-5 的小工单逐步推进，每次只执行决策窗口明确下发的当前小节。

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

### 第二轮 D 小工单拆分

#### 第二轮 D-1：Data 层静态边界与 import 复核

目标：

- 复核第二轮 A/B/C 后的核心 import 边界。
- 确认 `src.data.connection`、`src.data.models`、`src.data.database`、Repository、`db_manager` 均可 import。
- 静态确认 Repository 不依赖 `db_manager`、UI 或 `src.data.database`。
- 静态确认 `src/repositories/__init__.py` 只做轻量导出。

验收：

- `src.data.connection`、`src.data.models`、`src.data.database` 可 import。
- `ScheduleRepository`、`CategoryRepository`、`src.repositories`、`db_manager` 可 import。
- `src.data.connection.db` 与 `src.data.database.db` 指向同一个对象。
- `DB_PATH` 一致。
- `rg` 检查 `src/repositories` 中无 `db_manager`、UI、`src.data.database` 或 `database.py` 模型导入痕迹。
- `src/repositories/__init__.py` 不导入 `db_manager`、UI、`src.data.database`。
- `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

#### 第二轮 D-2：Data 层读路径回归验收

目标：

- 不写数据库。
- 验证 `db_manager` 兼容门面的核心读路径仍可用。
- 有样本时补充验证单项读取与分类状态判断。

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

#### 第二轮 D-3：分类写路径临时验收

目标：

- 允许为了验收临时写入分类数据。
- 验证分类创建、字段更新、软删除、硬删除路径。
- 临时分类必须清理干净。

验收：

- 使用唯一临时名称调用 `add_category` 创建分类。
- 使用 `get_category` 确认临时分类可读取。
- 调用 `update_category_fields`，并确认返回成功。
- 调用 `soft_delete_category`，并确认返回成功。
- 调用 `hard_delete_category`，并确认返回成功。
- 清理后 `get_category(cat_id)` 返回 `None`。
- 确认 `schedule.db` 无 tracked diff。
- `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt` 无 diff。

#### 第二轮 D-4：日程写路径临时验收

目标：

- 允许为了验收临时写入日程数据。
- 验证日程状态、置顶、字段更新的写回恢复路径。
- 验证临时日程创建与删除路径。
- 所有样本改动必须恢复，临时日程必须清理。

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

#### 第二轮 D-5：GUI smoke 与第二轮整体验收收口

目标：

- 汇总 D-1 ~ D-4 的验收结果。
- 验证旧 UI 启动路径仍可创建并关闭主窗口。
- 确认第二轮 A/B/C/D 的 Data 层整理具备归档条件。

验收：

- 读取并汇总 `Work_Log.md` 中 D-1 ~ D-4 记录。
- 优先执行 `MainWindow` 创建并关闭的 GUI smoke test。
- 如 GUI smoke 受环境限制失败，记录原因并执行 `import main` 兜底。
- 复跑最小 import 验证：`src.data.connection`、`src.data.models`、`src.data.database`、Repository、`db_manager`。
- 复跑最小读路径验证：`get_all_schedules`、`get_schedules_for_date`、`get_active_categories`、`get_category_map`。
- 确认 `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。
- `git diff --name-only` 最终只包含允许的管理文档 diff。
- 记录是否可以归档第二轮并进入第三轮规划。

### Work_Log.md 记录要求

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

### 完成后要求

- 每个 D 小工单完成后不要提交 Git，等待顾问窗口复核。
- D-5 顾问/决策确认后，可归档第二轮指令和日志，再进入第三轮规划。

---

---

# 2026-05-17 第三轮归档：纯业务查询与排序服务

# Work Instruction

用途：本文件用于“当前阶段”的执行指令发布。

- 仅保留正在执行或即将执行的任务。
- 已完成阶段请归档到 `History_Instruction.md`，避免本文件长期堆积。
- 当前主路线图见 `Work_Formulation.md` 的“架构改写轮次路线图”。
- 改写前行为和目录快照见 `Work_Snapshot.md`。
- 执行过程记录写入 `Work_Log.md`。

---

# 当前阶段：第三轮 - 纯业务查询与排序服务

## 已完成并归档

- 第一轮：基建 + repository + db_manager 兼容委托。
- 第二轮：Data 层整理与模型拆分。
  - 第二轮 A/B/C/D 均已完成并归档。
  - 第二轮最终验收通过，`src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

---

## 第三轮目标

第三轮目标是把“查询、过滤、排序、分类策略”等纯业务逻辑从 UI、Repository、DatabaseManager 中逐步分离出来，形成可单独验证、可复用、不依赖 QWidget 的服务层。

本轮重点处理：

- 日期过滤与日程/待办区分逻辑。
- 日视图、周视图、待办列表、待办看板等排序规则。
- 分类状态判断和分类删除策略。
- 四象限分类的纯逻辑评估与最小服务准备。

本轮仍保持旧 UI 行为不变，旧 UI 继续通过 `db_manager` 或现有调用路径工作。

---

## 第三轮允许修改范围

第三轮整体允许修改：

- `src/services/`
- `src/data/database.py`
- `src/repositories/`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

`src/services/` 允许范围仅限第三轮相关服务文件，例如查询、排序、分类策略、四象限纯逻辑服务。现有无关服务（例如 `src/services/weather_service.py`）默认不修改，除非后续小工单明确说明原因。

第三轮默认不修改 `src/ui/`。仅当具体小工单明确要求时，允许对 `src/ui/` 做最小调用替换：

- 不改布局。
- 不改视觉。
- 不改交互流程。
- 只把原本内联的纯排序/过滤/分类判断逻辑替换为 service 调用。
- 必须保留旧展示结果和用户可见行为。

---

## 第三轮禁止事项

- 不修改 `main.py`。
- 不修改 `requirements.txt`。
- 不修改 `Work_Snapshot.md`。
- 不修改 `Work_Formulation.md`。
- 不接四象限 UI。
- 不新增数据库字段。
- 不修改数据库字段含义、表名、默认值、迁移逻辑。
- 不修改现有无关 service，例如 `src/services/weather_service.py`，除非小工单明确要求。
- 不迁移重复日程写入逻辑。
- 不迁移提醒逻辑。
- 不迁移 Controller / Router / EventBus 协调逻辑。
- 不改变 `db_manager` 对外公开方法名、参数、返回语义。
- 不改变 Repository 方法名、参数、返回语义，除非小工单明确要求且完成兼容验证。
- 不实现新功能。
- 不拆 UI 大文件。
- 不改变现有 `priority` 等字段语义。
- 不保留 `schedule.db` 变更；如验收需要临时写入，必须清理并确认 `git diff --name-only -- schedule.db` 无输出。

---

## 行为保持原则

第三轮所有服务抽取必须满足：

- UI 展示顺序与旧逻辑一致。
- 查询结果集合与旧逻辑一致。
- 分类状态判断结果与旧逻辑一致。
- 临时服务调用不得改变数据库数据，除非小工单明确进入临时写入验收。
- 新 service 应尽量是纯 Python 逻辑，不依赖 QWidget。
- 如某段逻辑当前耦合在 UI 内，不直接搬动 UI，先记录位置和行为，再决定是否抽取纯函数。

---

## 第三轮小工单拆分草案

第三轮不沿用第二轮 A/B/C/D，采用 `3-0`、`3-1` 这种编号。

3-0 后可根据定位结果将 3-2、3-3、3-4 继续拆分为更小工单；不得为了匹配合同编号而一次抽取过多逻辑。

### 3-0：静态审查与旧逻辑定位

目标：

- 不改代码。
- 定位当前日期过滤、排序、分类状态、四象限相关逻辑分别在哪些文件。
- 标记逻辑来源：`database.py`、repository、UI、其他服务。
- 判断哪些逻辑适合第三轮抽取，哪些应留到后续轮次。

重点定位：

- 日期过滤与日程/待办区分。
- 日视图排序。
- 周视图排序。
- 待办列表排序。
- 待办看板排序。
- 分类状态判断和删除策略。
- 四象限分类相关现有逻辑或缺口。

验收重点：

- 输出清晰的位置清单。
- 明确第三轮可抽取项与禁止项。
- 明确是否需要拆分 3-2、3-3、3-4。
- `src/ui`、`src/data`、`src/repositories`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

### 3-1：服务骨架与边界确认

目标：

- 仅创建后续小工单确认会立即使用的最小 service 文件。
- 不创建无调用、无测试、无行为承接的空壳文件。
- 不接 UI。
- 不迁移复杂逻辑。

候选文件：

- `src/services/schedule_query_service.py`
- `src/services/schedule_sort_service.py`
- `src/services/category_policy_service.py`
- `src/services/matrix_classification_service.py`

是否创建上述文件，以 3-0 定位结果为准。

验收重点：

- 新 service 可 import。
- 不影响应用启动。
- 不改变旧调用路径。
- 不产生无用空壳文件。

### 3-2：日期过滤 / 查询逻辑抽取

目标：

- 抽取日程按日期过滤、日程/待办区分等纯逻辑。
- 优先从 Repository 或 DatabaseManager 中已有查询逻辑平移。
- 如需要替换 UI 内联过滤逻辑，必须在小工单中明确允许 `src/ui/` 最小调用替换。
- 保持旧 `db_manager.get_schedules_for_date(date)` 结果语义不变。

验收重点：

- 同一日期下，新旧结果数量和关键 id 一致。
- 返回类型不变。
- UI 可见结果不变。
- `schedule.db` 无 tracked diff。

### 3-3：排序策略抽取

目标：

- 抽取日视图、周视图、待办列表、待办看板等排序规则。
- 排序规则可能不完全一致，需按 3-0 结果拆分，不得一次性粗暴合并。
- 可引入 `schedule_sort_service.py` 或等价服务文件。
- 如需要替换 UI 内联排序逻辑，必须在小工单中明确允许 `src/ui/` 最小调用替换。

验收重点：

- 同一输入列表，新旧排序后的 id 顺序一致。
- 置顶、完成、过期、时间、优先级等排序权重不变。
- 对应 UI 展示顺序不变。
- 不改数据库。

### 3-4：分类状态 / 分类策略抽取

目标：

- 抽取分类状态判断、分类删除策略等纯业务判断。
- 可引入 `category_policy_service.py`。
- `db_manager.check_category_status(cat_id)` 对外结果不变。
- 不改变分类删除策略。

验收重点：

- `empty`、`active`、`historical` 等返回语义不变。
- 临时分类和临时日程验证后清理。
- 不改 UI。
- `schedule.db` 无 tracked diff。

### 3-5：四象限纯逻辑评估与最小服务准备

目标：

- 仅做四象限纯逻辑评估和最小服务准备。
- 如现有字段足够定义稳定规则，可准备 `MatrixClassificationService` 的纯逻辑。
- 如现有字段不足以定义稳定规则，只记录规则缺口，不强行实现分类结果。
- 不接 UI。
- 不新增字段。
- 不改变现有 `priority` 语义。

候选边界：

- 输入：Schedule 列表、当前时间。
- 输出：四组分类结果，或规则缺口报告。
- 依据：现有 `priority`、`start_time`、`end_time` 等字段。

验收重点：

- 服务可单独 import。
- 不依赖 QWidget。
- 不写数据库。
- 不接四象限界面。
- 不伪实现 UI 功能。

### 3-6：第三轮整体验收

目标：

- 汇总 3-0 到 3-5。
- 验证旧查询、排序、分类状态行为不变。
- 验证应用可启动。
- 确认第三轮可归档。

验收重点：

- `db_manager` 对外 API 不变。
- 读路径结果不变。
- 关键排序结果不变。
- 分类状态结果不变。
- 新增 service 可 import。
- 新增 service 不依赖 QWidget。
- `src/data`、`src/repositories`、`src/ui` 无非预期 diff。
- `main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。

---

## 第三轮整体验收标准

第三轮完成后必须确认：

- 所有新增 service 可 import。
- service 不依赖 QWidget。
- 旧 UI 启动路径不变。
- 旧 `db_manager` 调用仍可用。
- 查询结果、排序结果、分类状态结果与旧逻辑一致。
- 不产生数据库结构变化。
- 不接四象限界面。
- `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。

---

## 首个小工单建议

第三轮首个小工单应为：

`3-0：静态审查与旧逻辑定位`

原因：

- 当前查询、排序、分类策略逻辑可能分散在 `database.py`、repository 和 UI 文件中。
- 直接抽 service 容易遗漏 UI 内隐含排序/过滤规则。
- 先定位旧逻辑，才能定义后续 3-1 到 3-5 的真实边界。

执行窗口在收到 3-0 正式提示词前，不得修改源码、数据库或管理文档以外文件。
---

## 2026-05-18 第四轮总归档 - 日程写入与重复规则服务

状态：已完成。

结果：第四轮 4-0 ~ 4-9 已完成并通过整体验收，当前可进入第五轮提醒服务阶段合同/规划。

第四轮完成内容摘要：

- 4-0：静态审查与只读基线定位。
- 4-1：重复日期计算纯逻辑抽取。
- 4-2：重复规则待插入数据计划服务。
- 4-3：`add_schedule` 非重复路径委托。
- 4-4：`add_schedule` 重复路径收口验收。
- 4-5：update_future=False 当前条脱组行为验收。
- 4-6：update_future=True 非组转重复行为验收。
- 4-7a：已有重复组未来更新行为基线。
- 4-7b：旧未来删除策略最小委托。
- 4-8a：取消重复路径行为基线。
- 4-8b：取消重复路径条件收口复核。
- 4-9：第四轮整体验收与归档准备。

关键结论：

- `ScheduleRepeatService` 和 `ScheduleService` 已承接第四轮目标范围内的日期计算、重复计划和部分写入协调边界。
- `DatabaseManager` 仍保留事务、批量插入、旧 API 和返回语义。
- 未新增 `parent_id`。
- 未新增 `每年 / yearly / daily / weekly / monthly` 行为。
- `src`、`main.py`、`requirements.txt`、`schedule.db` 在 4-9 验收时无非预期 diff。

后续备注：

- 下一步应由决策窗口基于 `Work_Formulation.md` 拟定第五轮“提醒与运行期状态服务”阶段合同。
- 执行窗口在收到第五轮正式提示词前，不得自行开始提醒服务改造。

### 第四轮归档前 Work_Instruction 全文

# Work Instruction

用途：本文件用于“当前阶段”的执行指令发布。

- 仅保留正在执行或即将执行的任务。
- 已完成阶段请归档到 `History_Instruction.md`，避免本文件长期堆积。
- 当前主路线图见 `Work_Formulation.md` 的“架构改写轮次路线图”。
- 改写前行为和目录快照见 `Work_Snapshot.md`。
- 执行过程记录写入 `Work_Log.md`。

---

# 当前阶段：第四轮 - 日程写入与重复规则服务

## 已完成并归档

- 第一轮：基建 + repository + db_manager 兼容委托。
- 第二轮：Data 层整理与模型拆分。
  - 第二轮 A/B/C/D 均已完成并归档。
  - 第二轮最终验收通过，`src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。
- 第三轮：纯业务查询与排序服务。
  - 第三轮 3-0 ~ 3-6 均已完成并归档。
  - 已完成 `ScheduleQueryService`、`ScheduleSortService`、`CategoryPolicyService` 的服务边界和关键纯逻辑抽取。
  - 四象限纯逻辑已完成评估，因规则合同不足，暂未创建 `matrix_classification_service.py`。
  - 第三轮最终验收通过，`src`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

---

## 第四轮目标

第四轮目标是把日程写入和重复规则相关逻辑，从 `DatabaseManager` 中逐步拆到 service 层，但继续保留 `db_manager` 作为旧 UI 的兼容门面。

本轮重点处理：

- `DatabaseManager.add_schedule(data)`
- `DatabaseManager.update_schedule_with_repeat(schedule_id, new_data, update_future=False)`
- `_add_months` 或重复日期计算逻辑
- `repeat_rule` 旧语义和规则值映射
- `group_id`、`update_future` 的旧行为基线
- `parent_id` 是否存在及是否参与旧行为
- 重复日程生成数量、日期偏移、批量插入、未来实例删除/重建行为

本轮风险高，必须先做静态审查和只读基线定位，再逐步抽取纯逻辑和写入协调。不得一上来迁移复杂写入逻辑。

---

## 第四轮允许修改范围

第四轮整体允许修改：

- `src/services/schedule_service.py`
- `src/services/schedule_repeat_service.py` 或等价重复规则服务文件
- `src/data/database.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

如具体小工单明确需要，允许读取但默认不修改：

- `src/data/models.py`
- `src/repositories/schedule_repository.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- `src/ui/main_window.py`
- `src/ui/week_window.py`
- `src/ui/todo_board.py`
- `src/ui/schedule_detail_pop.py`
- `src/ui/month_window.py`

---

## 第四轮禁止事项

- 不修改 `src/ui/`，除非后续小工单明确只是只读审查；第四轮默认不做 UI 调用替换。
- 不修改 `main.py`。
- 不修改 `requirements.txt`。
- 不修改 `Work_Snapshot.md`。
- 不修改 `Work_Formulation.md`。
- 不新增数据库字段。
- 不修改数据库字段含义、表名、默认值、迁移逻辑。
- 不新增 `parent_id` 字段；当前模型未发现 `parent_id`，第四轮只记录事实，不补模型。
- 不改变 `db_manager` 对外公开方法名、参数、返回语义。
- 不改变 UI 行为、弹窗流程、编辑流程、添加页流程。
- 不迁移提醒逻辑。
- 不迁移 Controller / Router / EventBus。
- 不处理四象限 UI。
- 不保留 `schedule.db` 变更；如验收需要临时写入，必须清理并确认 `git diff --name-only -- schedule.db` 无输出。

---

## 行为保持原则

第四轮所有改动必须满足：

- `db_manager` 仍是旧 UI 调用入口。
- `add_schedule(data)` 成功/失败返回语义保持：成功 `True`，失败 `False`。
- `update_schedule_with_repeat(schedule_id, new_data, update_future)` 成功/失败返回语义保持：成功 `True`，失败 `False`。
- 单次日程新增行为不变。
- `每天 / 每周 / 每月` 重复生成行为不变。
- `每年 / yearly` 如 4-0 确认无旧实现，本轮不得新增或伪实现。
- `daily / weekly / monthly / yearly` 如 4-0 确认无旧实现，本轮不得新增或伪实现。
- 重复日程生成数量、时间偏移、`group_id` 分配保持旧行为。
- `update_future=False`：只改当前条；如原来属于循环组，当前条脱离 `group_id`。
- `update_future=True`：影响当前及未来，沿用或创建 `group_id`，删除旧未来实例，再重建新未来实例。
- UI 中可能存在的内存态同步行为必须先记录，再决定是否需要保留在旧 UI 层；第四轮默认不改 UI。
- 临时写库验收必须清理临时数据。
- 每个小工单结束必须确认 `git diff --name-only -- schedule.db` 无输出。

---

## 第四轮小工单拆分草案

第四轮采用 `4-0`、`4-1` 等编号。执行时仍可根据基线结果继续拆分更小工单，不得为了匹配编号一次迁移过多逻辑。

### 4-0：静态审查与只读基线定位

目标：

- 不改代码。
- 不写数据库。
- 定位当前 `add_schedule`、`update_schedule_with_repeat`、`_add_months`、重复规则 UI 来源。
- 明确当前支持的 `repeat_rule` 实际值。
- 明确 `daily / weekly / monthly / yearly`、`每年` 是否存在旧实现。
- 明确 `group_id`、`parent_id` 是否实际存在。
- 定位 UI 中对 `update_future` 和 `group_id` 的内存态同步逻辑。

必须定位：

- `src/data/database.py`
- `src/data/models.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- `src/ui/main_window.py`
- `src/ui/week_window.py`
- `src/ui/todo_board.py`
- `src/ui/schedule_detail_pop.py`
- `src/ui/month_window.py`

重点搜索：

- `add_schedule`
- `update_schedule_with_repeat`
- `_add_months`
- `repeat_rule`
- `group_id`
- `parent_id`
- `update_future`
- `editing_schedule.group_id = None`
- `p.data.group_id = None`
- `daily`
- `weekly`
- `monthly`
- `yearly`
- `每天`
- `每周`
- `每月`
- `每年`

验收重点：

- 输出规则值清单。
- 记录非重复值是否为 `none / 无 / 不重复 / ''`。
- 记录重复值是否实际只有 `每天 / 每周 / 每月`。
- 记录 `每年 / yearly / daily / weekly / monthly` 是否无旧生成逻辑。
- 记录当前模型是否只有 `group_id`、没有 `parent_id`。
- 记录 UI 内存态同步位置，例如 `if not update_future: ... group_id = None`。
- `src`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

### 4-1：重复日期计算纯逻辑抽取

目标：

- 只抽 `_add_months` 和日期偏移计算。
- 新建最小纯逻辑 service，例如 `schedule_repeat_service.py`。
- 不改 `add_schedule`。
- 不改 `update_schedule_with_repeat`。
- 不写数据库。

验收重点：

- 月末规则保持：如 1 月 31 日加 1 月落到 2 月最后一天。
- 闰年规则保持旧逻辑。
- `start_time`、`end_time`、`reminder_time` 的偏移逻辑一致。
- service 不依赖 UI / db_manager / Repository。
- `schedule.db` 无 diff。

### 4-2：重复规则待插入数据计划服务

目标：

- 抽取“根据 base data + repeat_rule 生成待插入数据列表”的纯逻辑。
- 只生成待插入数据计划。
- 不决定数据库事务边界。
- 不执行数据库写入。
- 事务和写库协调暂留 `DatabaseManager`，直到后续小工单明确迁移。
- 只支持当前旧规则，不新增未实现规则。

验收重点：

- `none / 无 / 不重复 / ''` 按旧语义不进入重复批量生成。
- `每天` 生成原始项 + 365 个未来项，共 366 条计划。
- `每周` 生成原始项 + 52 个未来项，共 53 条计划。
- `每月` 生成原始项 + 12 个未来项，共 13 条计划。
- `每年 / yearly / daily / weekly / monthly` 如无旧实现，只记录不支持，不新增行为。
- 生成计划中 `group_id` 语义与旧逻辑一致。
- 不写数据库。

### 4-3：add_schedule 非重复路径委托

目标：

- 只处理 `add_schedule` 的非重复路径。
- `DatabaseManager.add_schedule` 仍对外不变。
- 可让 service 判断是否非重复，DatabaseManager 保持实际写入。
- 不影响重复规则路径。

验收重点：

- 用临时单次日程验证创建和删除。
- 不改变默认字段。
- 不影响 `每天 / 每周 / 每月` 重复路径。
- 临时数据清理后 `schedule.db` 无 tracked diff。

### 4-4：add_schedule 重复路径委托

目标：

- 将重复日程生成计划委托给 service。
- DatabaseManager 仍负责事务和批量插入，除非小工单进一步明确迁移写入协调。
- 不改变生成数量和 `group_id` 语义。

验收重点：

- 用临时日程分别验证 `每天 / 每周 / 每月`。
- 验证同一批生成项 `group_id` 一致。
- 验证生成数量和日期偏移。
- 验证 `每年 / yearly` 不被新增支持。
- 验证后按 `group_id` 清理临时数据。
- `schedule.db` 无 tracked diff。

### 4-5：update_schedule_with_repeat 的 update_future=False 路径

目标：

- 只处理“仅修改当前这一条”路径。
- 不碰影响未来的删除/重建逻辑。
- 保持 `update_future=False` 时当前条脱离旧 `group_id` 的语义。

验收重点：

- 临时重复组中选一条修改。
- 验证该条按旧语义脱离 `group_id`。
- 验证同组其他未来项不被修改或删除。
- 如 UI 侧也有内存态同步，本轮只记录，不改 UI。
- 清理全部临时数据。
- `schedule.db` 无 tracked diff。

### 4-6：update_schedule_with_repeat 的 update_future=True 非组转重复路径

目标：

- 只处理“原本非重复，修改为重复并影响未来”的路径。
- 验证新 `group_id` 创建和未来实例生成。

验收重点：

- 临时单次日程改为重复。
- 验证当前条获得 `group_id`。
- 验证未来实例生成数量和时间偏移。
- 验证规则仅限旧支持值。
- 清理临时组。
- `schedule.db` 无 tracked diff。

### 4-7：update_schedule_with_repeat 的既有重复组未来更新路径

目标：

- 处理已有 `group_id` 时影响当前及未来。
- 保持旧逻辑：删除旧未来实例，重建新未来实例。
- 不改变过去实例处理规则。

风险控制：

- 本工单风险最高。
- 如果 4-0 或前置验收无法明确旧行为，必须先拆成：
  - `4-7a`：基线写入验证，只用临时数据验证旧行为，不改代码。
  - `4-7b`：在基线明确后再做委托改造。
- 不得在基线不清楚时直接迁移。

验收重点：

- 临时重复组中选中间一条。
- 验证早于当前的同组项保留。
- 验证当前条更新。
- 验证当前之后旧未来项删除并按新规则重建。
- 清理临时数据。
- `schedule.db` 无 tracked diff。

### 4-8：update_schedule_with_repeat 取消重复路径

目标：

- 处理重复改为 `none / 无 / 不重复 / ''`。
- 验证当前条 `group_id=None`。
- 验证未来实例删除行为保持旧语义。

验收重点：

- 临时重复组取消重复。
- 验证当前条脱离 `group_id`。
- 验证未来项按旧逻辑删除。
- 清理临时数据。
- `schedule.db` 无 tracked diff。

### 4-9：第四轮整体验收

目标：

- 汇总 4-0 到 4-8。
- 验证 `add_schedule` 和 `update_schedule_with_repeat` 关键路径。
- 确认第四轮可归档。

验收重点：

- service 可 import。
- service 不依赖 QWidget。
- `db_manager.add_schedule` API 不变。
- `db_manager.update_schedule_with_repeat` API 不变。
- 单次、每天、每周、每月旧行为不变。
- `每年 / yearly / daily / weekly / monthly` 如无旧实现，明确记录未实现且未新增。
- `parent_id` 如不存在，明确记录未新增。
- `src/ui` 无 diff。
- `schedule.db` 无 tracked diff。

---

## 第四轮整体验收标准

第四轮完成后必须确认：

- `db_manager.add_schedule(data)` 对外行为不变。
- `db_manager.update_schedule_with_repeat(schedule_id, new_data, update_future)` 对外行为不变。
- 临时写库测试全部清理。
- 非重复新增、重复新增、仅当前修改、影响未来修改、取消重复均通过验证。
- `group_id` 旧语义保持。
- 当前模型未发现 `parent_id` 时，已记录“不存在，不纳入第四轮实现”。
- 无 `每年 / yearly` 旧行为时，已记录“不新增，不伪实现”。
- 不新增数据库字段。
- 不修改 UI。
- `src/ui`、`main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。
- 第四轮可归档进入第五轮提醒服务。

---

## 首个小工单建议

第四轮首个小工单应为：

`4-0：静态审查与只读基线定位`

原因：

- 当前 `add_schedule` 与 `update_schedule_with_repeat` 是高风险写入路径。
- 重复规则实际支持值需要先以代码为准确认。
- UI 中存在 `update_future` 与 `group_id` 的内存态同步逻辑，必须先定位。
- 先只读定位，后续才能设计可清理的临时写库验收。

执行窗口在收到 4-0 正式提示词前，不得修改源码、数据库或管理文档以外文件。

## 2026-05-25 第五轮总归档 - 提醒与运行期状态服务

归档时间：2026-05-25。

结果：第五轮 5-0 ~ 5-6 已完成并通过整体验收，当前可进入第六轮 Controller / Router / EventBus 协调层规划。

第五轮完成内容摘要：

- 5-0：完成提醒链路静态审查与只读基线定位。
- 5-1：新增 `ReminderService` 骨架与纯判断辅助。
- 5-2：抽取本次运行内提醒去重状态。
- 5-3：将 `MainWindow.check_reminders()` 最小委托给 `ReminderService`。
- 5-4：将提醒弹窗数据 dict 纯构造逻辑收口到 `ReminderService`。
- 5-5：完成提醒服务轻量回归验收。
- 5-6：完成第五轮整体验收与归档准备。

第五轮最终边界：

- `ReminderService` 负责提醒时间判断、触发窗口判断、运行期去重、到期候选筛选、`target_time` 选择和弹窗 dict 纯构造。
- `MainWindow` 仍负责 QTimer 扫描驱动、数据来源 `db_manager.get_all_schedules()`、弹窗触发调用和触发成功后的去重标记。
- `ReminderPop` 与 `winsound.PlaySound(...)` 仍留在 UI 层，未迁移到 service。
- 未新增数据库字段、表或提醒持久化。
- 未修改 `db_manager` 对外 API。
- `main.py`、`requirements.txt`、`schedule.db` 无非预期变更。

对应 Git commits：
- 41c176e docs: prepare reminder service fifth round
- 7a3b2cb feat: add reminder service decision helpers
- 4a7546c feat: add reminder runtime dedup state
- 16ede10 feat: delegate reminder scanning to service
- 608f82b feat: delegate reminder popup data construction
- 78d2ff8 test: record reminder service regression checks
- 3520b31 test: complete reminder fifth round acceptance

后续备注：

- 第五轮已归档。
- 下一步应由决策窗口/顾问窗口基于 `Work_Formulation.md` 规划第六轮 Controller / Router / EventBus 协调层。
- 执行窗口在收到第六轮正式提示词前，不得自行开始第六轮实现改造。

### 第五轮归档前 Work_Instruction 全文

# Work Instruction

用途：本文件用于“当前阶段”的执行指令发布。

- 仅保留正在执行或即将执行的任务。
- 已完成阶段请归档到 `History_Instruction.md`，避免本文件长期堆积。
- 当前主路线图见 `Work_Formulation.md` 的“架构改写轮次路线图”。
- 改写前行为和目录快照见 `Work_Snapshot.md`。
- 执行过程记录写入 `Work_Log.md`。

---

# 当前阶段：第五轮 - 提醒与运行期状态服务

## 已完成并归档

- 第一轮：基建 + repository + db_manager 兼容委托。
- 第二轮：Data 层整理与模型拆分。
- 第三轮：纯业务查询与排序服务。
- 第四轮：日程写入与重复规则服务。
  - 第四轮 4-0 ~ 4-9 均已完成并归档。
  - 已完成 `ScheduleRepeatService` 与 `ScheduleService` 的第四轮服务边界。
  - 已验证 `add_schedule` 非重复/重复路径，以及 `update_schedule_with_repeat` 当前条、非组转重复、已有组改重复、取消重复路径。
  - 第四轮最终验收通过，`src`、`main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。

---

## 第五轮目标

第五轮目标是把提醒扫描、提醒触发判断和本次运行内去重状态，从 `MainWindow` 中逐步拆到 service 层，但继续保留 UI 弹窗、声音播放和 QTimer 驱动方式不变。

本轮重点处理：

- `MainWindow._init_scheduler()`
- `MainWindow.check_reminders()`
- `MainWindow.triggered_reminders`
- 提醒时间判断：`0 <= now - reminder_time < 60`
- 无提醒项跳过规则
- 本次运行内同一日程不重复弹窗规则
- 提醒触发后仍由 UI 层调用 `show_reminder_popup`
- `ReminderPop` 和 `winsound.PlaySound(...)` 的边界保持在 UI 层

本轮风险中等。提醒逻辑看似小，但涉及秒级定时器、内存状态、弹窗和声音副作用，必须先做只读基线定位，再拆纯逻辑，最后做最小委托。

---

## 第五轮允许修改范围

第五轮整体允许修改：

- `src/services/reminder_service.py`
- `src/services/__init__.py`
- `src/ui/main_window.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

如具体小工单明确需要，允许读取但默认不修改：

- `src/ui/reminder_pop.py`
- `src/ui/alarm_picker.py`
- `src/ui/alarm_picker_week.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- `src/ui/schedule_detail_pop.py`
- `src/data/models.py`
- `src/repositories/schedule_repository.py`
- `src/data/database.py`

---

## 第五轮禁止事项

- 不修改 `ReminderPop` UI 布局、尺寸、窗口 flag、倒计时显示和关闭按钮行为。
- 不迁移或封装 `winsound.PlaySound(...)`，声音播放和停止仍留在 UI/弹窗层。
- 不改变 `QTimer` 扫描频率，仍保持每秒扫描一次。
- 不改变提醒触发窗口，仍保持提醒时间之后 60 秒内触发。
- 不新增提醒持久化表、字段或数据库迁移。
- 不让已触发提醒状态写入数据库。
- 不改变重启后提醒去重状态清空的旧行为。
- 不修改提醒选择页校验规则。
- 不修改 `db_manager` 对外公开 API。
- 不修改 `main.py`。
- 不修改 `requirements.txt`。
- 不修改 `schedule.db`。
- 不处理 Controller / Router / EventBus 迁移。
- 不处理系统通知、托盘通知、Toast 通知等新功能。
- 不处理四象限、搜索、筛选、导出、同步等占位功能。

---

## 行为保持原则

第五轮所有改动必须满足：

- 应用启动后仍由 `MainWindow` 创建提醒扫描定时器。
- 扫描间隔仍为 1000ms。
- 提醒数据来源仍为 `db_manager.get_all_schedules()`。
- 无 `reminder_time` 的日程必须跳过。
- 当前时间处于 `reminder_time` 之后 60 秒内才触发。
- 未到提醒时间不触发。
- 超过 60 秒窗口不补弹。
- 同一日程 ID 在本次运行内只弹一次。
- 应用重启后，已触发集合重新为空，不持久化。
- 到点后仍调用原 `show_reminder_popup(schedule)`。
- 弹窗数据仍包含 `title`、`is_alarm`、`target_time`。
- `target_time` 仍优先使用 `start_time`，没有开始时间时使用 `end_time`。
- `is_alarm` 为真时仍播放系统声音 `SystemHand`。
- 关闭弹窗、点击“关闭闹钟”、点击“知道了”仍能停止声音。
- service 不依赖 QWidget、QTimer、winsound、ReminderPop、db_manager。

---

## 第五轮小工单拆分草案

第五轮采用 `5-0`、`5-1` 等编号。执行时仍可根据基线结果继续拆分更小工单，不得为了匹配编号一次迁移过多逻辑。

### 5-0：静态审查与只读基线定位

目标：

- 不改代码。
- 不写数据库。
- 定位当前提醒扫描、触发判断、去重集合、弹窗和声音调用位置。
- 明确提醒触发窗口、无提醒规则、过期规则和重启后状态规则。
- 明确哪些逻辑可抽 service，哪些 UI 副作用必须留在 UI 层。

必须定位：

- `src/ui/main_window.py`
- `src/ui/reminder_pop.py`
- `src/ui/alarm_picker.py`
- `src/ui/alarm_picker_week.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- `src/ui/schedule_detail_pop.py`
- `src/data/models.py`

重点搜索：

- `check_reminders`
- `_init_scheduler`
- `triggered_reminders`
- `show_reminder_popup`
- `reminder_time`
- `is_alarm`
- `alarm_duration`
- `PlaySound`
- `ReminderPop`
- `QTimer`
- `target_time`

验收重点：

- 输出当前提醒扫描流程。
- 输出当前触发条件。
- 输出当前去重状态生命周期。
- 输出弹窗和声音调用边界。
- 输出提醒选择和提醒显示相关位置。
- `src`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

### 5-1：ReminderService 骨架与纯判断函数

目标：

- 新增 `src/services/reminder_service.py`。
- 只建立 service 边界和纯判断函数。
- 不接入 `MainWindow`。
- 不修改 UI 行为。

建议能力：

- 判断日程是否有提醒时间。
- 计算 `now - reminder_time` 秒差。
- 判断是否处于旧触发窗口：`0 <= diff < 60`。
- 提供 `target_time` 选择辅助，优先 `start_time`，否则 `end_time`。
- 不在本工单生成完整弹窗 dict；完整 dict 构造留到 5-4 收口。

验收重点：

- service 可单独 import。
- service 不依赖 QWidget、QTimer、winsound、ReminderPop、db_manager。
- 用轻量假对象验证未到、到点、超过 60 秒、无提醒四类情况。
- `MainWindow` 行为未改变。
- `schedule.db` 无 diff。

### 5-2：运行期去重状态抽取

目标：

- 在 `ReminderService` 中增加运行期去重状态能力，或新增轻量状态类。
- 把 `triggered_reminders` 的 set 语义抽象出来。
- 暂不接入 UI。
- 不持久化。

建议能力：

- `is_triggered(schedule_id)`
- `mark_triggered(schedule_id)`
- `should_trigger(schedule, now)`
- `collect_due_schedules(schedules, now)`

边界要求：

- `should_trigger(schedule, now)` 只负责判断当前日程在不考虑去重写入时是否满足提醒触发条件，不得写入已触发状态。
- `collect_due_schedules(schedules, now)` 可负责批量筛选候选项，但不得隐式标记已触发；标记动作必须由调用方在弹窗触发成功后显式调用 `mark_triggered(schedule_id)`。

行为要求：

- 同一 ID 第一次满足条件时可触发。
- 同一 ID 已标记后不再触发。
- 新 service 实例状态为空，模拟应用重启后清空。
- 不写数据库。

验收重点：

- 用假对象验证同一日程不会重复触发。
- 用新 service 实例验证去重状态不持久化。
- service 仍不依赖 UI 和数据库。
- `schedule.db` 无 diff。

### 5-3：MainWindow 提醒扫描最小委托

目标：

- 让 `MainWindow.check_reminders()` 委托 `ReminderService` 判断哪些日程应触发。
- 保留 `MainWindow._init_scheduler()` 创建 QTimer。
- 保留 `MainWindow.show_reminder_popup()`。
- 保留 `db_manager.get_all_schedules()` 数据来源。

改造边界：

- `MainWindow` 可以持有 `self.reminder_service`。
- `MainWindow` 不再直接维护裸 `triggered_reminders` 判断细节。
- 触发后仍调用 `self.show_reminder_popup(s)`。
- `MainWindow` 应在 `self.show_reminder_popup(s)` 成功调用后，再显式调用 `mark_triggered(s.id)`，避免只筛选不标记导致重复弹窗。
- 打印日志可保持或等价迁移，但不得改变核心行为。

验收重点：

- `check_reminders()` 可读性提升。
- 到点仍会调用 `show_reminder_popup`。
- 同一 ID 本次运行内不重复触发。
- 未到、过期、无提醒不触发。
- `show_reminder_popup` 行为不变。
- `schedule.db` 无 diff。

### 5-4：提醒弹窗数据构造边界收口

目标：

- 将弹窗数据 dict 的纯构造逻辑委托给 `ReminderService`。
- 不修改 `ReminderPop`。
- 不迁移声音播放。
- 不改变 dict 字段和值。

旧字段必须保持：

- `title`
- `is_alarm`
- `target_time`

行为要求：

- `target_time = start_time if start_time else end_time`
- `is_alarm` 原样来自日程对象。
- `title` 原样来自日程对象。

验收重点：

- `show_reminder_popup()` 仍创建 `ReminderPop(data_dict)`。
- `is_alarm` 为真时仍在 `MainWindow` 播放系统声音。
- `ReminderPop` 文件无 diff。
- `winsound` 调用边界未改变。
- `schedule.db` 无 diff。

### 5-5：提醒服务轻量回归验收

目标：

- 汇总 5-1 到 5-4。
- 做不写库或可清理的轻量验证。
- 确认第五轮提醒服务边界稳定。

建议验证：

- service import。
- service 静态依赖检查。
- 假对象验证未到提醒不触发。
- 假对象验证到点触发。
- 假对象验证超过 60 秒不触发。
- 假对象验证无提醒不触发。
- 假对象验证同一 ID 不重复触发。
- fake/new service 实例验证重启后状态为空。
- `MainWindow` import 或 `main` import 兜底。
- `py_compile` 覆盖 `src/services/reminder_service.py`、`src/ui/main_window.py`、`main.py`。

验收重点：

- `ReminderService` 可 import。
- `ReminderService` 不依赖 UI、winsound、db_manager。
- `MainWindow` 外部行为不变。
- `ReminderPop` 无 diff。
- `main.py`、`requirements.txt`、`schedule.db` 无 diff。

### 5-6：第五轮整体验收与归档准备

目标：

- 汇总 5-0 到 5-5。
- 确认第五轮可归档进入第六轮 Controller / Router / EventBus 协调层。
- 更新当前轮次日志。

验收重点：

- 提醒扫描逻辑已从 `MainWindow` 中最小委托到 service。
- UI 副作用仍留在 UI 层。
- 弹窗和声音行为未改变。
- 已触发提醒去重状态仍只存在于本次运行内。
- 未新增数据库字段。
- 未新增提醒持久化。
- 未修改提醒选择页和弹窗 UI。
- `src/services/reminder_service.py` 是纯服务边界。
- `src/ui/main_window.py` 只做最小接入。
- `src/ui/reminder_pop.py` 无 diff。
- `main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。

---

## 第五轮整体验收标准

第五轮完成后必须确认：

- 应用仍可启动。
- 提醒每秒扫描仍由主窗口定时器驱动。
- 到点提醒仍弹窗。
- 强提醒仍播放系统声音。
- 关闭弹窗或停止闹钟仍停止声音。
- 同一日程本次运行内不重复弹出。
- 重启后去重状态不保留。
- 未到提醒、无提醒、超过 60 秒窗口均不触发。
- service 不依赖 QWidget、QTimer、winsound、ReminderPop、db_manager。
- 不新增数据库字段。
- 不修改 `db_manager` 对外 API。
- 不修改 `ReminderPop` UI。
- 不修改 `requirements.txt`。
- 不保留 `schedule.db` 变更。
- 第五轮可归档进入第六轮。

---

## 首个小工单建议

第五轮首个小工单应为：

`5-0：静态审查与只读基线定位`

原因：

- 提醒逻辑涉及定时器、弹窗、声音和内存去重，副作用边界必须先确认。
- `MainWindow.check_reminders()` 当前逻辑很短，适合小步抽取，但不适合直接迁移。
- `ReminderPop` 和 `winsound` 必须先明确保留在 UI 层，避免 service 被 UI 副作用污染。
- 先只读定位，后续才能安全拆分纯判断、运行期状态和 MainWindow 最小委托。

执行窗口在收到 5-0 正式提示词前，不得修改源码、数据库或除 `Work_Log.md` / `Work_Task_Prompts.md` 以外的管理文档。

## 2026-05-26 第六轮总归档 - Controller / Router / EventBus 协调层

归档时间：2026-05-26。

结果：第六轮 6-0 ~ 6-8 已完成并通过整体验收，当前可进入第七轮 Theme/QSS 接入阶段合同/规划。

对应关键提交：

```text
3748091 docs: plan round 6 coordination layer
674adad docs: record round 6-0 coordination coupling review
7bf2122 refactor: add coordination controller skeleton
6fbc9dc refactor: route main view decisions through view router
51d8248 docs: record round 6-3 picker return baseline
bb591b8 refactor: delegate add source decisions to main controller
f71702f refactor: coordinate main view refresh targets
b833e3e refactor: add parallel refresh event signal
3588eb0 docs: record round 6-7 detail popup review
7f57a14 docs: close round 6 coordination validation
```

第六轮完成摘要：

- 6-0：静态审查与跨视图耦合定位。
- 6-1：建立 `MainController` / `ViewRouter` / `RefreshCoordinator` 最小骨架。
- 6-2：`ViewRouter.classify_main_view` 接管 `MainWindow.switch_view` 的纯路由决策。
- 6-3：完成添加页来源与 picker 返回状态基线。
- 6-4：`MainController` 接管 `source_view_for_add` 最小闭环决策。
- 6-5：`RefreshCoordinator` 建立 Dashboard / Todo / Week 三连刷新协调边界。
- 6-6：新增 `global_signals.refresh_requested(str)` 并行 EventBus 通知试点。
- 6-7：完成详情弹窗与跨视图刷新回流复核。
- 6-8：完成第六轮整体验收与归档准备。

第六轮核心结果：

- controller/router/coordinator 最小边界已建立并可 import。
- 视图切换、添加页来源、三连刷新已完成低风险纯决策或协调边界接管。
- 旧 UI 实际路由、picker 写库/返回路径、详情弹窗 `source_view` 分支仍保留在 UI 层。
- `refresh_requested` 仅作为并行通知试点，未替代旧刷新主路径。
- `src/data`、`src/repositories`、`src/services`、`main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。

第六轮遗留到后续的事项：

- MainWindow Qt 实际路由仍在 UI 层。
- time/alarm/list picker edit 写库和返回路径仍在 UI 层。
- WeekWindow 内部 picker 路径仍独立。
- TodoBoardWindow `view_stack/list picker` 状态机仍未迁移。
- 详情弹窗打开和 `source_view` 分支仍未迁移。
- `refresh_requested` 当前无 UI 监听者，后续若接入监听需先定义主刷新路径与辅助通知边界。

后续备注：

- 第六轮已归档。
- 下一步应由决策窗口/顾问窗口基于 `Work_Formulation.md` 规划第七轮 Theme/QSS 接入。
- 执行窗口在收到第七轮正式提示词前，不得自行开始第七轮源码改造。

### 第六轮归档前 Work_Instruction 全文
# Work Instruction

用途：本文件用于“当前阶段”的执行指令发布。

- 仅保留正在执行或即将执行的任务。
- 已完成阶段请归档到 `History_Instruction.md`，避免本文件长期堆积。
- 当前主路线图见 `Work_Formulation.md` 的“架构改写轮次路线图”。
- 改写前行为和目录快照见 `Work_Snapshot.md`。
- 执行过程记录写入 `Work_Log.md`。

---

# 当前阶段：第六轮 - Controller / Router / EventBus 协调层

## 已完成并归档

- 第一轮：基建 + repository + db_manager 兼容委托。
- 第二轮：Data 层整理与模型拆分。
- 第三轮：纯业务查询与排序服务。
- 第四轮：日程写入与重复规则服务。
- 第五轮：提醒与运行期状态服务。
  - 第五轮 5-0 ~ 5-6 均已完成并归档。
  - 已完成 `ReminderService` 服务边界。
  - 已验证提醒扫描、提醒触发窗口、运行期去重、弹窗数据构造和 UI/声音边界保持。
  - 第五轮最终验收通过，`src`、`main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。

---

## 第六轮目标

第六轮目标是逐步降低 `MainWindow`、`WeekWindow`、`TodoBoardWindow`、`MonthWindow` 之间的互相引用、直接路由和直接刷新耦合。

本轮更准确的定位是“跨视图协调层接管”，不是 UI 大拆分。应先建立 controller/router/coordinator 边界，再用小工单把旧 UI 中最明确、最低风险的协调逻辑迁出或委托。

重点范围：

- 视图切换：日视图、周视图、月视图、待办视图之间的切换协调。
- 添加页来源记录：`source_view_for_add` 等返回目标状态。
- picker 返回流程：时间、提醒、清单 picker 的 add/edit 返回路径。
- 跨视图刷新：日程/清单变更后的 Dashboard、Todo、Week、Month 刷新。
- EventBus 使用边界：新协调层可使用 `global_signals` 的新增信号，但必须保留旧信号签名和旧 UI 信号兼容。

不追求一次清空 `MainWindow`。本轮每一步只迁移一个可验证闭环。

---

## 第六轮允许修改范围

第六轮整体允许修改：

- `src/controllers/__init__.py`
- `src/controllers/main_controller.py`
- `src/controllers/view_router.py`
- `src/controllers/refresh_coordinator.py`
- `src/utils/signals.py`（仅在小工单明确需要补充信号时；不得修改旧信号签名）
- `src/ui/main_window.py`（仅在小工单明确要求时做最小调用替换）
- `src/ui/week_window.py`（仅在小工单明确要求时做最小调用替换）
- `src/ui/month_window.py`（仅在小工单明确要求时做最小调用替换）
- `src/ui/todo.py`（仅在小工单明确要求时做最小调用替换）
- `src/ui/todo_board.py`（仅在小工单明确要求时做最小调用替换）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

第六轮默认不修改 UI。只有某个小工单明确列出 UI 文件时，才允许最小调用替换。

---

## 第六轮禁止事项

第六轮整体禁止：

- 不修改 `src/data/`。
- 不修改 `src/repositories/`。
- 不修改 `src/services/`，除非后续阶段合同明确把某个 service 纳入当前小工单。
- 不修改 `main.py`。
- 不修改 `requirements.txt`。
- 不修改 `schedule.db`，也不保留任何数据库变更。
- 不新增数据库字段。
- 不改数据库迁移逻辑。
- 不改 `db_manager` 对外 API。
- 不改 Repository / Service 方法名、参数、返回语义。
- 不改 UI 布局、视觉、文案和交互流程。
- 不批量拆分 UI 大文件；UI 大文件拆分留到第八轮。
- 不修改旧 signal 的名称、参数和触发语义。
- 不删除旧直连刷新路径，除非对应小工单已经完成行为基线、替代路径验证和回归验收。
- 不实现新功能。

---

## 行为保持原则

本轮所有改动必须满足：

- 日、周、月、待办之间切换行为不变。
- 添加日程/待办后的返回页面不变。
- picker add/edit 模式下的返回路径不变。
- 编辑时间、提醒、清单后的数据写入和页面刷新不变。
- 删除、置顶、状态变更后的相关视图刷新不变。
- 已打开详情弹窗的刷新行为不变。
- `global_signals.skin_changed` 仍为无参信号。
- `global_signals` 名称必须保留。
- 如引入新的 EventBus 信号，只能作为兼容增强，不得强迫旧 UI 一次性迁移。

---

## 第六轮小工单拆分

第六轮采用 `6-0`、`6-1` 等编号。执行时可根据 `6-0` 审查结果继续拆分更小工单，不得为了匹配编号一次迁移过多逻辑。

### 6-0：静态审查与跨视图耦合定位

目标：

- 只读定位当前跨视图协调逻辑，不改源码。
- 建立第六轮改造基线，确认哪些逻辑适合本轮迁移，哪些应留到第八轮 UI 拆分。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

审查重点：

- `MainWindow.switch_view(...)` 的视图切换路径。
- `source_view_for_add`、`list_picker_source`、`time_picker_mode`、`alarm_picker_mode`、`list_picker_mode` 等路由状态。
- time/alarm/list picker 的 add/edit 返回路径。
- `DashboardView.req_refresh_all`、`TodoView.req_refresh_all`、`WeekWindow.schedule_updated` 等跨视图刷新链路。
- `WeekWindow`、`MonthWindow`、`TodoBoardWindow` 对主窗口或其他窗口的直接调用。
- 详情弹窗打开和刷新回流路径。
- `global_signals` 当前信号是否已足够支撑本轮协调层。

验收重点：

- 输出耦合地图：按文件、函数、信号、刷新目标记录。
- 标记每个候选迁移点的风险等级。
- 明确哪些进入 `6-1` 后续小工单，哪些推迟。
- 确认 `src`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

Work_Log 记录：

- 本轮任务名称。
- 静态审查命令和结果。
- 跨视图耦合地图。
- 建议进入第六轮的小工单候选。
- 不适合本轮处理的内容及原因。
- diff 范围检查结果。
- 未完成事项和风险疑点。

### 6-1：Controller / Router / Coordinator 最小骨架

目标：

- 只创建第六轮确认会使用的最小协调层文件。
- 保证新增 controller 文件可 import，且不依赖数据库、不依赖具体 UI 创建过程。
- 不接入旧 UI，不替换旧路由和刷新逻辑。

允许修改：

- `src/controllers/__init__.py`
- `src/controllers/main_controller.py`
- `src/controllers/view_router.py`
- `src/controllers/refresh_coordinator.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/ui/`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/utils/signals.py`（本轮先不补信号）
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- `MainController`、`ViewRouter`、`RefreshCoordinator` 可 import。
- 新 controller 文件不 import `db_manager`、Repository、Service 写入对象或 QWidget 具体类。
- 旧应用入口和旧 UI 路径不变。
- diff 范围只包含允许文件。

Work_Log 记录：

- 新增/修改文件。
- 每个 controller 文件的当前职责边界。
- import 验证结果。
- 静态依赖检查结果。
- diff 范围检查结果。
- 未完成事项和风险疑点。

### 6-2：ViewRouter 视图切换基线与低风险接管

目标：

- 基于 `6-0` 结论，先处理最清晰的主视图切换映射。
- 如基线不清楚，本轮只记录“不改源码”；不得强行接管。
- 如接管，优先让 `ViewRouter` 承担 view_name 到目标视图/窗口动作的轻量映射或决策，`MainWindow` 继续执行实际 Qt 操作。

允许修改：

- `src/controllers/view_router.py`
- `src/ui/main_window.py`（仅最小调用替换）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/ui/week_window.py`
- `src/ui/month_window.py`
- `src/ui/todo.py`
- `src/ui/todo_board.py`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- `switch_view("day" / "week" / "month" / "todo")` 的旧行为不变。
- `ViewRouter` 不创建 QWidget，不直接 show/hide 窗口，不写数据库。
- 如果改 `main_window.py`，只能替换路由决策调用，不能改布局和交互流程。
- GUI smoke 或 import 兜底通过。
- diff 范围只包含允许文件。

Work_Log 记录：

- 是否接管源码；如未接管，记录原因。
- 接管的 view_name 范围。
- 替换前后行为基线。
- 验证命令和结果。
- 风险疑点。

### 6-3：添加页来源与 picker 返回状态基线

目标：

- 先审查并记录 add/picker 返回状态，不默认改源码。
- 重点确认 `source_view_for_add`、`list_picker_source`、`time_picker_mode`、`alarm_picker_mode`、`list_picker_mode` 的旧语义。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- 记录 add 页从 dashboard/todo 返回的路径。
- 记录 time/alarm/list picker 的 add/edit 返回路径。
- 记录 week/todo_board 内部 picker 是否存在独立路径。
- 判断是否需要拆出 `MainController` 状态辅助；若需要，必须进入后续小工单，不在本轮直接修改。
- diff 范围只包含管理文档。

Work_Log 记录：

- 状态字段清单。
- 每个字段的写入点、读取点、返回目标。
- 后续是否建议接管及拆分方式。
- diff 范围检查结果。

### 6-4：添加页来源与 picker 返回状态最小接管（条件执行）

目标：

- 仅在 `6-3` 结论明确、风险可控时执行。
- 把一个最小状态决策迁入 `MainController` 或 `ViewRouter`，不一次迁移所有 picker。
- 如 `6-3` 判断不适合，本轮不改源码，只记录“无需/暂不接管”。

允许修改：

- `src/controllers/main_controller.py`
- `src/controllers/view_router.py`
- `src/ui/main_window.py`（仅最小调用替换）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/ui/week_window.py`
- `src/ui/todo_board.py`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/utils/signals.py`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- 被接管的返回路径行为不变。
- 未接管的 picker 路径行为不变。
- 不改变 add/edit 保存逻辑。
- 不改变 UI 布局、文案、交互。
- diff 范围只包含允许文件。

Work_Log 记录：

- 是否进入源码修改分支。
- 接管的具体字段/路径。
- 未接管路径及原因。
- 行为验证结果。
- 风险疑点。

### 6-5：RefreshCoordinator 跨视图刷新边界建立

目标：

- 建立跨视图刷新协调边界。
- 优先封装“调用哪些 refresh 方法”的协调动作，不改变触发时机。
- 本轮不删除旧信号，不改变旧 UI 信号签名。

允许修改：

- `src/controllers/refresh_coordinator.py`
- `src/ui/main_window.py`（仅最小调用替换或注册刷新目标）
- `src/utils/signals.py`（仅当 `6-0` 证明缺少必要兼容信号时）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/ui/week_window.py`（除非后续提示词明确纳入）
- `src/ui/todo_board.py`（除非后续提示词明确纳入）
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- Dashboard、Todo、Week 的刷新调用顺序和可见性判断保持。
- `global_signals` 旧信号保持兼容。
- `RefreshCoordinator` 不写数据库，不创建窗口，不修改业务对象。
- add/edit/delete 后的旧刷新路径仍可用。
- diff 范围只包含允许文件。

Work_Log 记录：

- 刷新目标注册方式。
- 接管的刷新链路。
- 保留的旧直连路径。
- 验证命令和结果。
- 风险疑点。

### 6-6：EventBus 并行通知试点

目标：

- 在不移除旧直接刷新路径的前提下，选择一个低风险变更点增加 EventBus 并行通知。
- 该通知只能作为兼容增强，不得成为唯一刷新路径。

允许修改：

- `src/controllers/refresh_coordinator.py`
- `src/ui/main_window.py`（仅低风险变更点）
- `src/utils/signals.py`（仅补充必要信号，且不改旧签名）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/ui/week_window.py`（除非后续提示词明确纳入）
- `src/ui/todo_board.py`（除非后续提示词明确纳入）
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- 旧刷新路径仍执行。
- 新 EventBus 信号可连接、可触发。
- 不出现重复写库。
- 不改变 UI 行为。
- diff 范围只包含允许文件。

Work_Log 记录：

- 选择的低风险通知点。
- 旧路径与新路径是否并存。
- 信号触发验证结果。
- 风险疑点。

### 6-7：详情弹窗与跨视图刷新回流复核

目标：

- 复核详情弹窗打开、编辑、关闭后的刷新回流。
- 默认只做行为验收和耦合记录；如需接管，必须另拆小工单。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- Dashboard 详情弹窗刷新行为不变。
- Week 打开 Dashboard 详情弹窗的路径不变。
- Todo/TodoBoard 打开详情弹窗的路径不变。
- 标记哪些回流适合后续接入 `RefreshCoordinator`。
- diff 范围只包含管理文档。

Work_Log 记录：

- 弹窗打开来源。
- 弹窗更新后的刷新目标。
- 直接耦合点。
- 是否建议后续迁移。

### 6-8：第六轮整体验收与归档准备

目标：

- 汇总第六轮所有 controller/router/coordinator 改动和未迁移债务。
- 确认可进入第七轮 Theme/QSS 接入。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- `MainController`、`ViewRouter`、`RefreshCoordinator` 可 import。
- `global_signals` 兼容性通过。
- 日/周/月/待办切换行为通过 GUI smoke 或 import 级兜底。
- add/edit/delete 后刷新链路按第六轮日志保持。
- picker 返回路径按第六轮日志保持。
- 详情弹窗刷新回流按第六轮日志保持。
- `src/data`、`src/repositories`、`src/services`、`main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。
- 明确第六轮是否可归档。

Work_Log 记录：

- 6-0 到 6-7 完成摘要。
- 实际迁移到 controller/router/coordinator 的职责。
- 保留在 UI 中的职责及原因。
- 整体验收命令和结果。
- 可归档性结论。

---

## 当前执行要求

当前只完成第六轮阶段合同与小工单拆分。

执行窗口在收到 `6-0` 正式提示词前，不得自行开始源码改造、数据库改造或管理文档大范围改写。

---

## 2026-05-26 第七轮总归档 - Theme / QSS 接入与样式债务控制

状态：已完成并归档。

归档说明：以下内容来自归档时的 Work_Instruction.md，保留第七轮阶段合同与小工单拆分。

# Work Instruction

用途：本文件用于“当前阶段”的执行指令发布。

- 仅保留正在执行或即将执行的任务。
- 已完成阶段请归档到 `History_Instruction.md`，避免本文件长期堆积。
- 当前主路线图见 `Work_Formulation.md` 的“架构改写轮次路线图”。
- 改写前行为和目录快照见 `Work_Snapshot.md`。
- 执行过程记录写入 `Work_Log.md`。

---

# 当前阶段：第七轮 - Theme / QSS 接入与样式债务控制

## 已完成并归档

- 第一轮：基建 + repository + db_manager 兼容委托。
- 第二轮：Data 层整理与模型拆分。
- 第三轮：纯业务查询与排序服务。
- 第四轮：日程写入与重复规则服务。
- 第五轮：提醒与运行期状态服务。
- 第六轮：Controller / Router / EventBus 协调层。

---

## 第七轮目标

第七轮目标是让主题系统开始真正参与应用，同时控制样式债务，不追求一次性清理全部旧 `setStyleSheet(...)`。

本轮采用“颜色皮肤 / Skin Preset”路线，不按每套皮肤再拆 light/dark 双模式。深色主题可作为一种深色皮肤存在，但本轮不实现完整换肤 UI。

重点范围：

- 复核现有 `ThemeManager`、QSS 文件、`StyleManager`、`setStyleSheet(...)` 分布。
- 在应用启动处接入默认主题 QSS，保持默认视觉尽量不变。
- 建立 QSS 动态属性命名规范，例如 `role`、`state`、`variant`。
- 只选择少量低风险公共控件做样式试点。
- 为后续第八轮 UI 拆分建立样式规范，避免继续复制硬编码样式。

不追求：

- 不批量删除旧内联样式。
- 不一次性重写 `StyleManager`。
- 不实现完整设置页、换肤页、字体/颜色选择闭环。
- 不顺带改第六轮 Controller / Router / EventBus 行为。

---

## 第七轮允许修改范围

第七轮整体允许修改：

- `src/theme/theme_manager.py`
- `src/theme/light.qss`
- `src/theme/dark.qss`
- `src/theme/__init__.py`
- `main.py`（仅在明确小工单中接入默认 QSS）
- `src/utils/signals.py`（仅在明确小工单中使用既有 `theme_changed` / `skin_changed`；不得改旧签名）
- `src/utils/styles.py`（仅在明确小工单中做极小兼容整理）
- 少量低风险 UI 文件（仅在明确小工单列出时做动态属性或试点调用替换）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

默认不修改 UI。只有具体小工单明确列出 UI 文件时，才允许最小样式接入。

---

## 第七轮禁止事项

第七轮整体禁止：

- 不修改 `src/data/`。
- 不修改 `src/repositories/`。
- 不修改 `src/services/`。
- 不修改 `src/controllers/`，除非后续小工单明确需要读取第六轮协调层状态；默认不碰。
- 不修改 `requirements.txt`。
- 不修改 `schedule.db`。
- 不新增数据库字段。
- 不改数据库迁移逻辑。
- 不改 `db_manager` 对外 API。
- 不改业务逻辑。
- 不改路由、刷新、picker、详情弹窗回流行为。
- 不批量替换 UI 文件中的 `setStyleSheet(...)`。
- 不批量移动样式到 QSS。
- 不实现完整主题设置 UI。
- 不实现字体/颜色选择功能闭环。
- 不改变 `global_signals.skin_changed` 无参签名。
- 不改变 `global_signals.theme_changed(str)` 既有签名。
- 不引入新的第三方依赖。
- 不做第八轮 UI 大文件拆分。

---

## 行为保持原则

本轮所有改动必须满足：

- 应用可启动。
- 默认视觉尽量保持，不出现大面积颜色、字体、间距、圆角突变。
- 日、周、月、待办切换行为不变。
- 添加、编辑、删除、提醒、详情弹窗行为不变。
- 第六轮 `ViewRouter`、`MainController`、`RefreshCoordinator`、`refresh_requested` 行为不变。
- 旧 `setStyleSheet(...)` 可以继续存在。
- 新 QSS 只先覆盖明确试点范围，不影响未纳入试点的旧 UI。
- 动态属性刷新必须可验证。

---

## 第七轮小工单拆分

第七轮采用 `7-0`、`7-1` 等编号。执行时可根据 `7-0` 审查结果继续拆分更小工单，不得为了匹配编号一次迁移过多样式。

### 7-0：主题与样式债务静态审查

目标：

- 只读审查当前主题/QSS/内联样式状态，不改源码。
- 建立第七轮样式接入基线。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

审查重点：

- `ThemeManager` 当前能力与缺口。
- `light.qss` / `dark.qss` 当前内容与命名。
- `main.py` 当前 QApplication 启动流程。
- `StyleManager` 当前承担的公共样式。
- `setStyleSheet(...)` 高频分布文件。
- 适合 QSS 试点的低风险控件。
- 不适合本轮处理、应推迟到第八轮 UI 拆分的样式债务。

验收重点：

- 输出样式债务地图。
- 输出可进入 7-1/7-2/7-3 的候选项。
- 确认 `src`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

Work_Log 记录：

- 静态审查命令和结果。
- `ThemeManager` 能力/缺口。
- QSS 文件状态。
- 内联样式热点。
- 低风险试点候选。
- 推迟项及原因。

### 7-1：ThemeManager 与 Skin Preset 边界确认

目标：

- 只完善 ThemeManager 的最小主题边界和命名约定。
- 不接入应用启动。
- 不改 UI。

允许修改：

- `src/theme/theme_manager.py`
- `src/theme/__init__.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `main.py`
- `src/ui/`
- `src/utils/signals.py`
- `src/utils/styles.py`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `requirements.txt`
- `schedule.db`

验收重点：

- `ThemeManager` 可 import。
- 可列出/解析允许的 skin preset，例如 `light.qss`、`dark.qss`。
- 读取 QSS、应用 QSS、刷新动态属性样式能力保持。
- 不引入 UI/db/Repository/Service 依赖。
- diff 范围只包含允许文件。

Work_Log 记录：

- ThemeManager 当前职责边界。
- skin preset 命名规则。
- import / py_compile / 静态依赖验证。
- 未接入应用启动的说明。

### 7-2：默认 QSS 启动接入

目标：

- 在应用启动处接入默认 skin preset。
- 默认视觉尽量保持。
- 不实现换肤 UI。

允许修改：

- `main.py`
- `src/theme/theme_manager.py`（仅在 7-2 验证发现需要极小兼容修正时）
- `src/theme/light.qss`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/ui/`
- `src/utils/signals.py`
- `src/utils/styles.py`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `requirements.txt`
- `schedule.db`

验收重点：

- 应用启动仍可 import / smoke。
- 默认 QSS 加载失败时有明确日志或保守失败方式，不破坏应用启动。
- 不改变窗口结构和业务行为。
- `light.qss` 初始内容应尽量低侵入，只放全局基础规则或空安全规则。
- diff 范围只包含允许文件。

Work_Log 记录：

- 默认 skin preset 名称。
- 接入位置。
- 启动/import 验证。
- 默认视觉风险评估。

### 7-3：动态属性命名规范与刷新验证

目标：

- 建立动态属性命名规范。
- 验证 `ThemeManager.refresh_widget_style(...)` 能刷新动态属性样式。
- 默认不改业务 UI。

允许修改：

- `src/theme/theme_manager.py`
- `src/theme/light.qss`
- `src/theme/dark.qss`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `main.py`（除非只读验证）
- `src/ui/`
- `src/utils/signals.py`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `requirements.txt`
- `schedule.db`

建议规范：

- `role`：组件角色，例如 `primaryButton`、`ghostButton`、`panel`、`input`。
- `state`：状态，例如 `normal`、`active`、`warning`、`danger`。
- `variant`：变体，例如 `compact`、`toolbar`。

验收重点：

- QSS 动态属性选择器存在且语义清楚。
- 使用临时 QWidget/QPushButton 验证 setProperty + refresh_widget_style。
- 不修改真实业务 UI。
- diff 范围只包含允许文件。

Work_Log 记录：

- 动态属性规范。
- QSS 选择器示例。
- 临时控件验证命令和结果。

### 7-4：低风险公共控件样式试点

目标：

- 选择一个低风险公共控件做 QSS 动态属性试点。
- 不批量替换旧样式。
- 不改变业务行为。

允许修改：

- `src/theme/light.qss`
- `src/theme/dark.qss`
- 一个明确列出的低风险 UI 文件（执行提示词必须写死具体文件）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

候选试点优先级：

- 窗口控制按钮的非业务样式。
- tooltip 或 toast 的低风险外观。
- 单个公共按钮 role 动态属性。

禁止修改：

- 未在提示词列出的 UI 文件。
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `main.py`（除非本轮提示词明确需要启动 smoke）
- `requirements.txt`
- `schedule.db`

验收重点：

- 只试点一个小范围。
- 默认视觉变化可控。
- 文案、布局、信号、业务行为不变。
- UI 文件 diff 可解释。

Work_Log 记录：

- 试点控件与文件。
- 替换前旧样式说明。
- 新动态属性/role 说明。
- py_compile / import / 静态 diff 结果。

### 7-5：Theme 信号兼容与手动切换 smoke（不做 UI）

目标：

- 只验证 `ThemeManager` 与既有 `global_signals.theme_changed(str)` / `skin_changed()` 兼容。
- 不实现换肤 UI。
- 不让旧 UI 依赖新信号。

允许修改：

- `src/theme/theme_manager.py`（仅必要兼容修正）
- `src/utils/signals.py`（仅当不改变旧签名且必须补注释/极小兼容时；默认不改）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `main.py`
- `src/ui/`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `requirements.txt`
- `schedule.db`

验收重点：

- `global_signals.skin_changed` 仍无参可 emit。
- `global_signals.theme_changed(str)` 可 emit。
- `ThemeManager` 可手动 apply `light.qss` / `dark.qss` 到临时 QApplication。
- 不修改真实 UI。

Work_Log 记录：

- 信号兼容验证结果。
- 手动切换 smoke 结果。
- 未实现换肤 UI 的说明。

### 7-6：第七轮整体验收与归档准备

目标：

- 汇总第七轮 Theme/QSS 接入结果。
- 明确第八轮 UI 拆分前的样式规范与债务。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- `ThemeManager` 可 import。
- 默认 QSS 接入可用。
- 动态属性规范已记录。
- 试点控件可回归。
- `skin_changed` / `theme_changed` 兼容。
- 第六轮协调层行为不变。
- `src/data`、`src/repositories`、`src/services`、`src/controllers`、`main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。
- 明确第七轮是否可归档。

Work_Log 记录：

- 7-0 到 7-5 完成摘要。
- 实际接入的主题能力。
- 未迁移样式债务。
- 第八轮 UI 拆分前的样式约束。
- 可归档性结论。

---

## 当前执行要求

- 当前只完成第七轮阶段合同与小工单拆分。
- 执行窗口在收到 `7-0` 正式提示词前，不得自行开始源码改造、数据库改造或管理文档大范围改写。
- 第七轮应避免顺带改动第六轮协调层行为路径。
---

## 2026-05-27 第八轮总归档 - UI 拆分与样式债务整理

状态：已完成并归档。

归档说明：以下内容来自归档时的 Work_Instruction.md，保留第八轮阶段合同与小工单拆分。

# Work Instruction

用途：本文件用于“当前阶段”的执行指令发布。

- 仅保留正在执行或即将执行的任务。
- 已完成阶段请归档到 `History_Instruction.md`，避免本文件长期堆积。
- 当前主路线图见 `Work_Formulation.md` 的“架构改写轮次路线图”。
- 改写前行为和目录快照见 `Work_Snapshot.md`。
- 执行过程记录写入 `Work_Log.md`。

---

# 当前阶段：第八轮 - UI 拆分与样式债务整理

## 已完成并归档

- 第一轮：基建 + repository + db_manager 兼容委托。
- 第二轮：Data 层整理与模型拆分。
- 第三轮：纯业务查询与排序服务。
- 第四轮：日程写入与重复规则服务。
- 第五轮：提醒与运行期状态服务。
- 第六轮：Controller / Router / EventBus 协调层。
- 第七轮：Theme / QSS 接入与样式债务控制。

---

## 第八轮目标

第八轮目标是在数据层、业务服务、协调层、Theme/QSS 基础已经稳定后，开始整理 UI 大文件和公共组件，但仍采用兼容式渐进重构。

本轮重点不是“把 UI 一次性拆漂亮”，而是建立可持续拆分方式：

- 先定位 UI 大文件内部的职责边界。
- 优先沉淀低风险公共组件或工具。
- 每次只迁移一个小边界。
- 保持页面显示、交互、信号、刷新、拖拽、右键菜单、弹窗行为不变。
- 延续第七轮样式路线：基于 `default.qss / skin preset`，不建立 light/dark mode matrix。
- 新增或拆出的 UI 组件应优先使用 `role/state/variant` 动态属性规范，避免继续复制硬编码主题色。

第八轮应优先处理：

- `src/ui/todo_board.py` 的职责地图和安全拆分点。
- `src/ui/week_window.py` 的卡片、日期块、窗口控制、toast 等可拆边界。
- `src/ui/main_window.py` 中仍残留的 UI 协调与展示辅助。
- picker、tooltip、icon loader、toast、schedule card、folder card 等公共组件候选。

第八轮不以“文件体积立刻明显变小”为唯一目标。若某个小工单只完成边界定位、目录骨架或单个低风险组件提取，也算有效推进。

---

## 第八轮允许修改范围

第八轮整体允许修改：

- `src/ui/`
- `src/ui/common/`（可新增；用于后续拆出的共享 UI 小组件，避免与既有 `src/ui/components.py` 冲突）
- `src/ui/views/`（可新增）
- `src/ui/dialogs/`（可新增）
- `src/ui/popups/`（可新增）
- `src/ui/utils/`（可新增）
- `src/theme/default.qss`（仅在明确小工单中为新拆组件补充低风险动态属性规则）
- `src/theme/theme_manager.py`（默认不改；仅在明确小工单中为样式刷新做极小兼容修正）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

默认允许新增 UI 包目录和 `__init__.py`，但只有具体小工单明确要求时，才允许移动类或改调用方。

阶段级允许范围不等于每个小工单的实际可改范围。第八轮执行时必须以具体 `8-x` 提示词中的允许清单为准；未在该小工单中明确列出的 UI 文件、主题文件或工具文件不得顺手修改。

禁止创建与现有 `src/ui/*.py` 同名的包目录。例如当前已有 `src/ui/components.py`，因此不得创建 `src/ui/components/`，以免遮蔽既有 `from .components import ...` 导入。

`src/theme/theme_manager.py` 的兼容修正必须由具体小工单明确方法名、修改原因和验收命令；否则默认禁止修改。`src/utils/styles.py` 也必须由具体小工单明确唯一修改点和兼容验收；否则默认禁止修改。

---

## 第八轮禁止事项

第八轮整体禁止：

- 不修改 `src/data/`。
- 不修改 `src/repositories/`。
- 不修改 `src/services/`，除非后续小工单明确只读验证已有 service 行为；默认不碰。
- 不修改 `src/controllers/`，除非后续小工单明确只读验证第六轮协调层；默认不碰。
- 不修改 `src/utils/signals.py`。
- 不修改 `src/utils/styles.py`，除非后续小工单明确做极小兼容整理；默认不碰。
- 不修改 `main.py`，除非小工单明确只做 import smoke 或极小入口兼容；默认不碰。
- 不修改 `requirements.txt`。
- 不修改 `schedule.db`。
- 不新增数据库字段。
- 不改数据库迁移逻辑。
- 不改 `db_manager` 对外 API。
- 不改业务服务语义。
- 不改第六轮 `ViewRouter`、`MainController`、`RefreshCoordinator`、`refresh_requested` 行为。
- 不实现新功能。
- 不实现真实换肤 UI。
- 不实现 `theme_color/设置字体` 功能闭环。
- 不实现四象限 UI。
- 不实现搜索、筛选、导出、同步等占位功能。
- 不一次性拆分 `todo_board.py` / `week_window.py` / `month_window.py` / `add_view.py` 等大文件。
- 不批量迁移所有 `setStyleSheet(...)`。
- 不删除旧 UI 类或旧导入路径，除非具体小工单已完成兼容验证。

---

## 行为保持原则

第八轮所有改动必须满足：

- 应用可 import / smoke。
- 日、周、月、待办切换行为不变。
- 添加、编辑、删除、提醒、详情弹窗行为不变。
- picker 返回行为不变。
- 拖拽、右键菜单、置顶、排序、文件夹/便签视图切换行为不变。
- 第六轮跨视图刷新链路不变。
- 第七轮 `default.qss / skin preset` 路线不变。
- 已试点的 `header.btn_sync` 动态属性样式不被破坏。
- 旧 UI 仍可继续使用既有 `setStyleSheet(...)`。
- 新拆出的组件必须保留旧类的公开行为、信号、参数和返回语义。

---

## 第八轮小工单拆分

第八轮采用 `8-0`、`8-1` 等编号。执行时可根据 `8-0` 审查结果继续拆成 `8-2a`、`8-2b` 这种更小工单，不得为了匹配编号一次迁移过多 UI。

### 8-0：UI 拆分静态审查与职责地图

目标：

- 只读审查当前 UI 大文件、公共组件、样式债务和可拆边界。
- 不改源码。
- 为第八轮后续小工单建立行为基线和风险分级。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

审查重点：

- UI 文件体量和类分布。
- `todo_board.py` 内部类、状态机、写库调用、toast、icon loader、list picker、folder/stick 视图边界。
- `week_window.py` 内部 `WeekScheduleCard`、`DayBlock`、window controls、toast、weather、view selector、周视图刷新边界。
- `month_window.py` 内部 inline add、window controls、calendar、toast、weather、view selector 边界。
- `main_window.py` 中仍承担的 UI 展示辅助、toast、详情弹窗回流、跨视图协调调用。
- `components.py`、`widgets.py`、`header.py` 中已有公共组件可复用性。
- 重复的 `CustomToolTip` / `ToolTipFilter` / icon loader / toast / window control 逻辑。
- `setStyleSheet(...)` 热点与适合使用 `default.qss` 动态属性的低风险位置。
- 哪些拆分适合第八轮，哪些应推迟到后续功能轮。

验收重点：

- 输出 UI 职责地图。
- 输出拆分候选清单和风险等级。
- 输出建议优先级。
- 确认 `src`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

Work_Log 记录：

- 静态审查命令和结果。
- UI 大文件体量。
- 高风险区域。
- 低风险拆分候选。
- 建议的下一步小工单。

### 8-1：UI 包目录骨架与导入边界准备

目标：

- 只建立第八轮后续拆分需要的 UI 包目录骨架。
- 不移动旧类。
- 不替换旧调用。
- 不改变运行行为。

允许修改：

- `src/ui/common/__init__.py`
- `src/ui/views/__init__.py`
- `src/ui/dialogs/__init__.py`
- `src/ui/popups/__init__.py`
- `src/ui/utils/__init__.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- 现有 `src/ui/*.py` 文件。
- `src/theme/`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `src/utils/signals.py`
- `src/utils/styles.py`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- 新目录可作为 Python package import。
- 不触发 QApplication。
- 不触发 UI 实例化。
- 不引入循环导入。
- 总 diff 只包含允许文件和日志。

Work_Log 记录：

- 新增目录和 `__init__.py`。
- import 验证。
- diff 范围检查。

### 8-2：公共 icon loader 静态定位与最小提取

目标：

- 先定位重复 icon loader 逻辑，再只提取一个低风险纯工具。
- 不改图标资源。
- 不改业务 UI 行为。

建议拆分保护：

- 若 `8-0` 发现 icon loader 逻辑差异较大，先执行 `8-2a` 只读基线，不改源码。
- 只有差异清楚后，执行 `8-2b` 最小提取。

允许修改：

- `src/ui/utils/icon_loader.py`（可新增）
- 一个明确列出的调用方文件（执行提示词必须写死具体文件，例如 `src/ui/header.py` 或 `src/ui/todo_board.py` 中的单个函数）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- 未在提示词列出的 UI 文件。
- `assets/`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `src/theme/`（除非只读验证）
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- 提取后的 helper 可 import。
- 旧图标加载结果不抛异常。
- 被替换调用方行为不变。
- 只替换一个低风险调用点。
- diff 范围严格受控。

Work_Log 记录：

- 旧逻辑位置。
- 提取后的函数职责。
- 替换的唯一调用点。
- import / py_compile / smoke 结果。

### 8-3：公共 tooltip / toast 边界定位与单点提取

目标：

- 整理重复的 tooltip/toast 候选，但只做一个小边界。
- 不改变提示文案、显示位置、持续时间、关闭行为。

建议拆分保护：

- 优先 `8-3a`：只读定位 `CustomToolTip`、`ToolTipFilter`、`show_toast` 分布。
- 如边界清楚，再 `8-3b`：只提取一个低风险组件或工具。

允许修改：

- `src/ui/common/tooltip.py` 或 `src/ui/common/toast.py`（具体文件由执行提示词写死）
- 一个明确列出的调用方文件
- `src/theme/default.qss`（仅在明确需要动态属性规则时）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- 未在提示词列出的 UI 文件。
- `src/utils/styles.py`（默认不碰）
- `src/utils/signals.py`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- tooltip/toast 显示语义不变。
- 不改变已有计时器、关闭、鼠标事件行为。
- 不改变 parent 归属、生命周期、eventFilter 安装/移除、focus 行为、hide/show 时机。
- `default.qss` 只新增动态属性选择器，不新增全局规则。
- 被替换调用方 import / py_compile 通过。

Work_Log 记录：

- 旧重复位置。
- 本轮只处理的唯一边界。
- 未处理的重复项和推迟原因。

### 8-4：WeekWindow 低风险类提取试点

目标：

- 从 `week_window.py` 中选择一个低风险 UI 类做文件级提取试点。
- 优先候选：`WeekScheduleCard` 或 `DayBlock`。
- 不改周视图业务流程。

执行前置条件：

- 必须基于 `8-0` 的静态审查结论锁定唯一最低风险候选类。
- 若 `8-0` 未明确建议 `WeekScheduleCard` 或 `DayBlock` 中的唯一候选，不得直接执行源码提取，应先补充只读复核或继续拆分为 `8-4a` / `8-4b`。
- 执行提示词必须写死被提取类名、新文件名和唯一替换范围，不允许执行窗口自行扩大到多个类。

允许修改：

- `src/ui/week_window.py`
- `src/ui/common/week_schedule_card.py` 或 `src/ui/common/day_block.py`（具体文件由执行提示词写死）
- `src/ui/common/__init__.py`（仅轻量导出，且不触发副作用）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/ui/todo_board.py`
- `src/ui/month_window.py`
- `src/ui/main_window.py`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `src/theme/`（除非只读验证）
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- 类公开构造参数、信号、属性访问保持兼容。
- `week_window.py` import 新类后行为不变。
- 周视图 import / offscreen smoke 通过。
- 不改变卡片排序、点击、拖拽、tooltip、详情弹窗行为。

Work_Log 记录：

- 提取的类。
- 原位置和新位置。
- 兼容性说明。
- import / py_compile / smoke 结果。

### 8-5：TodoBoard 只读基线与低风险拆分候选确认

目标：

- 只读审查 `todo_board.py`，不拆代码。
- 明确哪些类可以后续拆，哪些状态机必须暂缓。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

审查重点：

- `StickyNoteCard`
- `StickViewContainer`
- `FolderCard`
- `AddFolderCard`
- `FolderViewContainer`
- `ManageCategoryCard`
- `ManageListView`
- `InlineAddTodoView`
- `TodoBoardWindow`
- `_get_icon`
- `_apply_custom_tooltip`
- `show_toast`
- folder/stick 状态机。
- sort_order 写回路径。
- list picker / inline add / refresh 通知链路。

验收重点：

- 输出 TodoBoard 职责地图。
- 输出后续可拆小工单建议。
- 明确高风险状态机暂缓项。
- 确认无源码 diff。

Work_Log 记录：

- 类与职责地图。
- 写库/刷新/状态机风险点。
- 建议下一步是否可拆某个卡片类。

### 8-6：TodoBoard 单个卡片类提取试点

目标：

- 在 `8-5` 基线清楚后，只提取一个低风险卡片类。
- 优先候选：`FolderCard` 或 `AddFolderCard`。
- 不迁移 `TodoBoardWindow` 状态机。

允许修改：

- `src/ui/todo_board.py`
- `src/ui/common/todo_board_cards.py` 或明确的单类文件
- `src/ui/common/__init__.py`（仅轻量导出）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `src/theme/`（除非只读验证）
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- 提取类构造参数、信号、右键菜单、拖拽相关行为不变。
- `TodoBoardWindow` 仍按旧方式使用该类。
- 不改变 folder/stick 状态机。
- 不改变 sort_order 写回。
- 不改变新增/删除/刷新行为。

Work_Log 记录：

- 提取的唯一类。
- 旧行为保持说明。
- import / py_compile / offscreen smoke 结果。
- 未拆项和风险。

### 8-7：MainWindow / MonthWindow / AddView 拆分候选复核

目标：

- 只读或极小范围复核剩余 UI 大文件的拆分候选。
- 不默认改源码。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

审查重点：

- `main_window.py` 的 toast、详情弹窗回流、视图容器、刷新入口是否已由第六轮稳定承接。
- `month_window.py` 的 inline add、calendar、window controls、toast、view selector 是否适合后续拆。
- `add_view.py` / `add_view_week.py` 重复结构是否适合后续合并，但本轮不合并。
- `schedule_detail_pop.py` 复杂分支是否应继续推迟。

验收重点：

- 输出候选清单。
- 输出建议顺序。
- 明确不在第八轮处理或需另开功能轮的项。
- 确认无源码 diff。

Work_Log 记录：

- 文件级拆分建议。
- 高风险项。
- 下一轮或后续功能轮建议。

### 8-8：第八轮整体验收与归档准备

目标：

- 汇总第八轮已完成的小工单。
- 验证 UI 拆分没有破坏已有功能边界。
- 判断是否可归档第八轮。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- 新增 UI 包可 import。
- 被提取的组件可 import。
- 原调用方可 import / py_compile。
- 默认启动接入仍可 import smoke。
- 第七轮 `btn_sync` 试点仍可回归。
- 第六轮协调层行为不变。
- `src/data`、`src/repositories`、`src/services`、`src/controllers`、`main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。
- 明确第八轮是否可归档。

Work_Log 记录：

- 8-0 到已完成小工单摘要。
- 实际拆出的组件和目录。
- 未拆 UI 债务。
- 第九轮或后续功能轮建议。
- 可归档性结论。

---

## 当前执行要求

- 当前只完成第八轮阶段合同与小工单拆分。
- 执行窗口在收到 `8-0` 正式提示词前，不得自行开始源码改造、UI 拆分、样式迁移、数据库改造或管理文档大范围改写。
- 第八轮应优先执行 `8-0` 静态审查与职责地图，不应直接拆 `todo_board.py` 或 `week_window.py`。
- 若后续顾问窗口复核认为某个小工单仍过大，应继续拆成 `8-xa` / `8-xb`。

