# Work Instruction

本文件用于决策窗口向执行窗口下达具体执行指令。

当前主架构改写方案见 `Work_Formulation.md`；架构改写前行为和目录快照见 `Work_Snapshot.md`；执行过程记录写入 `Work_Log.md`。

## 执行日志硬性要求

执行窗口每次完成一轮操作后，必须更新 `manage_instruction/Work_Log.md`。

日志至少记录：

- 本轮任务名称。
- 实际修改的文件。
- 执行过的验证命令或人工验证结果。
- 未完成事项。
- 风险、疑点或需要决策窗口确认的问题。

如果任务中途失败，也必须写入失败位置、错误信息摘要和已回滚/未回滚状态。

---

# 当前执行任务：第一轮 B - Repository + DatabaseManager 兼容委托

## 任务目标

执行第一轮 B，在不改变 UI 调用方式和外部行为的前提下，新增 Repository 层，并让 `DatabaseManager` 对部分低风险方法进行内部委托。

本轮目标是“内部结构开始分层，外部接口完全兼容”。旧 UI 仍继续调用 `db_manager`，不要让 UI 直接改调 Repository。

## 允许修改

- `src/repositories/`
- `src/data/database.py`
- `manage_instruction/Work_Log.md`

如发现必须修改上述范围以外的文件，请先停止并在窗口中说明原因，不要擅自扩大范围。

## 禁止修改

- 不修改任何 `src/ui/` 文件。
- 不修改 `main.py`。
- 不修改 `src/theme/`、`src/utils/signals.py`。
- 不移动 Peewee 模型类 `Schedule`、`Category`。
- 不改变数据库字段含义。
- 不改 `schedule.db`。
- 不实现任何新功能。
- 不改变 `db_manager` 公开方法名、参数、返回类型和返回语义。
- 不让 UI 层直接引用 Repository。
- 不修改 `Work_Snapshot.md`，除非决策窗口另行要求。

## 具体要求

1. 新增 Repository 文件：

```text
src/repositories/schedule_repository.py
src/repositories/category_repository.py
```

2. `ScheduleRepository` 封装低风险日程数据操作，至少覆盖：

- `delete_schedule(schedule_id)`
- `update_schedule_status(schedule_id, new_status)`
- `update_schedule_fields(schedule_id, **kwargs)`
- `toggle_pin_status(schedule_id, current_pin_status)`
- `get_all_schedules()`
- `get_schedules_for_date(target_date)`

3. `CategoryRepository` 封装低风险清单数据操作，至少覆盖：

- `get_active_categories(list_type=None)`
- `update_category_fields(cat_id, **kwargs)`
- `get_category_map()`
- `get_category(cat_id)`
- `add_category(name, color="#0cc0df", list_type="schedule")`
- `check_category_status(cat_id)`
- `soft_delete_category(cat_id)`
- `hard_delete_category(cat_id)`

4. 暂时不要迁移高风险重复日程逻辑：

- `add_schedule(data)`
- `update_schedule_with_repeat(schedule_id, new_data, update_future=False)`
- `_add_months(...)`

这些方法本轮可以继续留在 `DatabaseManager` 中原样运行，避免把重复日程生成和批量删除/重建逻辑混进第一轮 B。

5. 修改 `DatabaseManager`，让上面第 2、3 条列出的低风险公开方法内部委托 Repository。

兼容要求：

- `db_manager.xxx(...)` 调用方式必须不变。
- 成功返回值、失败返回值和异常吞吐语义应尽量保持原样。
- 现有排序规则、过滤规则、清单删除策略不得改变。
- 不要改变 `Schedule.select()` 和 `Category.select()` 的现有业务结果语义。

6. 修复 `_migrate_db` 中 `migrator` 作用域风险。

要求：

- 不删除现有迁移步骤。
- 不改变迁移目标字段。
- 不改变旧数据 `sort_order` 补值策略。
- 只修复 `migrator` 可能未定义的问题和必要的局部健壮性。

7. 注意循环导入风险。

`src/repositories/*.py` 需要引用 `Schedule`、`Category`、`db` 等对象时，要避免在 `database.py` 顶部直接导入 Repository 导致循环导入。可采用以下任一稳妥方式：

- 在 `DatabaseManager.__init__` 或相关方法内部延迟导入 Repository。
- 或让 Repository 构造函数接收模型类/数据库对象。

优先选择最小改动、最容易读懂的方案。

## 验收要求

执行窗口完成后至少验证：

- 应用仍可启动。
- `src/data/database.py` 可以正常 import。
- `db_manager` 可以正常创建并完成数据库初始化。
- `ScheduleRepository`、`CategoryRepository` 可以 import。
- `db_manager.get_all_schedules()` 可调用。
- `db_manager.get_active_categories()` 可调用。
- `db_manager.get_schedules_for_date(date.today())` 可调用。
- `db_manager.add_category(...)`、`get_category(...)`、`hard_delete_category(...)` 的基础路径可用，测试时请使用临时唯一名称并清理。
- `db_manager.update_schedule_status(...)` 等需要真实日程 ID 的方法，如果当前数据库没有可安全操作的测试日程，不要强造复杂数据；记录“无样本，未执行写入验证”即可。
- `src/data/database.py` 的公开方法名仍存在。
- `src/ui/` 无改动。
- 已更新 `manage_instruction/Work_Log.md`。

## 建议验证命令

可使用类似命令做 import 和低风险调用验证。当前执行窗口如受沙箱限制，应申请沙箱外权限或让用户在本地 CMD 复跑，并把结果记录到 `Work_Log.md`。

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; print('db import ok'); print(len(db_manager.get_all_schedules())); print(len(db_manager.get_active_categories())); print(len(db_manager.get_schedules_for_date(date.today())))"

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories.schedule_repository import ScheduleRepository; from src.repositories.category_repository import CategoryRepository; print('repositories ok')"
```

建议额外检查修改范围：

```powershell
git diff --name-only
git diff --name-only -- src/ui
```

如果启动 GUI 验证受限，请记录限制原因，并至少完成 import 级和数据库低风险调用验证。
