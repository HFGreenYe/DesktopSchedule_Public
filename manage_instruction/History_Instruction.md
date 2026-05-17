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
