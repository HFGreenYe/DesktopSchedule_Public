# History Log

本文件用于归档已经完成阶段的执行日志，避免 `Work_Log.md` 长期累积内容、增加当前阶段复核成本。

使用规则：

- `Work_Log.md` 只保留当前阶段或当前轮次的执行记录。
- 每个阶段完成、验收并提交 Git 后，将该阶段日志迁移到本文件。
- 历史日志通常只在追溯问题、核对旧阶段细节时读取。
- 当前阶段开工前，应保持 `Work_Log.md` 简洁。

---

# 归档日志

## 第一轮架构改写日志归档（2026-05-13 至 2026-05-14）

## 2026-05-13 第一轮A - 第1步（目录骨架 + __init__.py）

- 本轮任务名称：执行 `Work_Instruction.md` 具体要求第 1 步。
- 实际修改的文件：
  - `src/models/__init__.py`
  - `src/repositories/__init__.py`
  - `src/services/__init__.py`
  - `src/controllers/__init__.py`
  - `src/theme/__init__.py`
- 新建目录：
  - `src/models/`
  - `src/repositories/`
  - `src/controllers/`
  - `src/theme/`
  - `src/services/`（已存在，仅补 `__init__.py`）
- 执行过的验证命令或人工验证结果：
  - 验证目录存在与文件创建：`Get-ChildItem src/models,src/repositories,src/services,src/controllers,src/theme -Force`
  - 结果：上述 5 个目录均存在，且各目录下均有 `__init__.py`。
- 未完成事项：
  - 仅完成第 1 步；第 2~7 步尚未执行。
- 风险、疑点或需要决策窗口确认的问题：
  - 本次未触碰 `src/data/database.py`、未改 UI 逻辑，风险低。

## 2026-05-13 第一轮A - 第2/3步（Theme 基础文件 + ThemeManager 基础能力）

- 本轮任务名称：执行 `Work_Instruction.md` 第一轮 A 的第 2、3 步。
- 实际修改的文件：
  - `src/theme/light.qss`
  - `src/theme/dark.qss`
  - `src/theme/theme_manager.py`
  - `manage_instruction/Work_Log.md`
- 执行过的验证命令或人工验证结果：
  - `git diff --name-only -- src/data/database.py`
  - 结果：无输出，确认未修改 `src/data/database.py`。
  - 计划验证（失败）：
    - `python -c "from src.theme.theme_manager import ThemeManager; ..."`
    - 失败摘要：当前 shell 中 `python` 命令不存在。
  - 兜底验证（失败）：
    - `.\.venv\Scripts\python.exe -c "from src.theme.theme_manager import ThemeManager; ..."`
    - 失败摘要：虚拟环境解释器无法创建进程，指向不存在的 `Python311\python.exe`。
  - 再兜底验证（失败）：
    - `py -3 -c "from src.theme.theme_manager import ThemeManager; ..."`
    - 失败摘要：系统无可用 Python 3 安装。
  - 人工静态核对：`ThemeManager` 已实现 3 项基础能力（读取 QSS、应用到 `QApplication`、刷新 widget 样式）。
- 未完成事项：
  - 受当前环境缺少可运行 Python 解释器影响，未完成 import 级运行验证。
  - 第一轮 A 的第 4~7 步尚未执行。
- 风险、疑点或需要决策窗口确认的问题：
  - 代码改动范围仍在允许清单内；但运行级验收需在可用 Python 环境恢复后补做。
  - 失败位置：运行验证阶段；回滚状态：未回滚（代码按指令保留）。

## 2026-05-13 第一轮A - 剩余任务（signals 兼容式 EventBus 扩展）

- 本轮任务名称：第一轮 A 剩余任务，仅扩展 `src/utils/signals.py` 事件通道并记录日志。
- 修改文件：
  - `src/utils/signals.py`
  - `manage_instruction/Work_Log.md`
- 验证命令和结果：
  - 执行命令（按要求）：
    - `cd D:\CodeProjects\DesktopSchedule\DesktopSchedule`
    - `.\.venv\Scripts\python.exe -c "from src.utils.signals import global_signals; global_signals.skin_changed.connect(lambda: None); global_signals.skin_changed.emit(); print('signals ok')"`
  - 结果：失败。
  - 失败摘要：`Unable to create process using '"C:\Users\hfgre\AppData\Local\Programs\Python\Python311\python.exe" ...'`，说明当前虚拟环境解释器指向的基础 Python 路径不可用。
  - 静态确认（已执行）：
    - `global_signals = AppSignals()` 存在。
    - `skin_changed = pyqtSignal()` 存在且为无参。
    - 新增信号均存在：
      - `theme_changed = pyqtSignal(str)`
      - `schedule_added = pyqtSignal(object)`
      - `schedule_updated = pyqtSignal(object)`
      - `schedule_deleted = pyqtSignal(int)`
      - `category_changed = pyqtSignal()`
  - 数据库文件检查：`git diff --name-only -- src/data/database.py` 无输出，确认未修改数据库逻辑文件。
- 是否仍有 Python 环境问题：是，仍存在（虚拟环境 Python 入口损坏/目标解释器缺失）。
- 未完成事项或风险：
  - 运行级信号连通验证未完成，仅完成静态确认。
  - 本轮未改 UI、未接入 ThemeManager、未实现新功能，改动范围符合约束。

## 2026-05-13 指定解释器验证（内层目录 + 显式 .venv python）

- 本轮任务名称：按用户新规则执行路径固定验证并记录日志。
- 修改文件：
  - `manage_instruction/Work_Log.md`
- 验证命令和结果：
  - `cd /d D:\CodeProjects\DesktopSchedule\DesktopSchedule`（在 PowerShell 中等价执行为 `Set-Location 'D:\CodeProjects\DesktopSchedule\DesktopSchedule'`）
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.utils.signals import global_signals; print('signals ok')"`
  - 结果：失败。
  - 错误摘要：`Unable to create process using '"C:\Users\hfgre\AppData\Local\Programs\Python\Python311\python.exe" ...'`
- 是否仍有 Python 环境问题：是。当前 `.venv\Scripts\python.exe` 仍依赖不存在的基础解释器路径。
- 未完成事项或风险：
  - 该环境下仍无法完成运行级 Python 验证；仅能继续进行静态代码确认。

## 2026-05-13 复核指令与环境重测

- 本轮任务名称：复读日志并对照指令文件检查遗漏，重跑环境验证。
- 修改文件：
  - `manage_instruction/Work_Log.md`
- 指令对照结论（第一轮 A）：
  - 已完成：目录骨架（第1步）、Theme 基础文件与 ThemeManager 基础能力（第2/3步）、signals 兼容式扩展（第5~7步要求已覆盖）。
  - 无需单独施工：第4步为“本轮不做事项”约束，当前实现未违反。
  - 仍遗漏：运行级验收尚未通过（应用可启动、signals import+emit、ThemeManager import/read_qss 需在可运行 Python 环境下验证）。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe --version` -> 失败
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.utils.signals import global_signals; global_signals.skin_changed.connect(lambda: None); global_signals.skin_changed.emit(); print('signals ok')"` -> 失败
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.theme.theme_manager import ThemeManager; tm=ThemeManager(); print('theme manager ok'); print('light len', len(tm.read_qss('light.qss'))); print('dark len', len(tm.read_qss('dark.qss')))"` -> 失败
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); print('app startup ok'); w.close(); app.quit()"` -> 失败
  - 统一失败摘要：`Unable to create process using '"C:\Users\hfgre\AppData\Local\Programs\Python\Python311\python.exe" ...'`
  - 数据库改动检查：`git diff --name-only -- src/data/database.py` 无输出。
- 是否仍有 Python 环境问题：是，仍存在。
- 未完成事项或风险：
  - 第一轮 A 的代码改造基本完成，但运行级验收被 Python 解释器损坏阻塞。
  - 风险：若不修复 `.venv` 解释器指向，后续所有 Python 验证与测试都会失败。

## 2026-05-13 环境修复状态同步（用户本地已完成）

- 本轮任务名称：记录用户已完成的环境修复与验证结果（仅日志更新）。
- 修改文件：
  - `manage_instruction/Work_Log.md`
- 环境处理说明：
  - 按用户要求，本轮未重建 `.venv`，未执行任何代码修改。
  - 环境问题由用户在本地 CMD 修复。
- 用户侧已完成事项：
  - 删除旧 `.venv_old`。
  - 重建 `.venv`。
  - 安装 `requirements.txt`。
  - 补装 `zhdate==0.1`。
  - 将 `zhdate==0.1` 写入 `requirements.txt`。
  - 已提交 commit：`2803436 fix: add missing zhdate dependency`。
- 用户侧验证结果（已通过）：
  - `.\.venv\Scripts\python.exe -c "from src.utils.signals import global_signals; print('signals ok')"` -> 输出 `signals ok`
  - `.\.venv\Scripts\python.exe -c "from src.theme.theme_manager import ThemeManager; tm=ThemeManager(); print(tm.read_qss('light.qss')[:20]); print('theme ok')"` -> 输出 `theme ok`
  - `.\.venv\Scripts\python.exe .\main.py` -> 应用成功启动，图标正常。
- 风险/未完成事项：
  - 本条记录基于用户提供的本地验证结果；当前轮次未再次本地复跑。

## 2026-05-13 执行沙箱权限说明

- 执行窗口此前使用普通沙箱运行 Python 验证失败，错误根因不是代码或当前 `.venv` 损坏，而是沙箱内访问基础解释器路径受限。
- 当前 `.venv` 会转调 `C:\Users\hfgre\AppData\Local\Programs\Python\Python311\python.exe`。
- 执行窗口使用沙箱外权限复跑：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.utils.signals import global_signals; print('signals ok')"`
  - 结果通过，输出 `signals ok`。
- 后续需要运行 Python 验证时，应优先使用用户本地 CMD 验证，或由执行窗口申请沙箱外权限运行。
- 这不是第一轮 A 代码问题。

## 2026-05-13 第一轮 B-1（仅新增 Repository 薄封装）

- 本轮任务名称：阅读 `Work_Instruction.md` 后，仅执行第一轮 B-1，不执行完整第一轮 B。
- 修改文件：
  - `src/repositories/schedule_repository.py`
  - `src/repositories/category_repository.py`
  - `src/repositories/__init__.py`
  - `manage_instruction/Work_Log.md`
- 主要方法（按指令清单实现）：
  - `ScheduleRepository`：
    - `delete_schedule(schedule_id)`
    - `update_schedule_status(schedule_id, new_status)`
    - `update_schedule_fields(schedule_id, **kwargs)`
    - `toggle_pin_status(schedule_id, current_pin_status)`
    - `get_all_schedules()`
    - `get_schedules_for_date(target_date)`
  - `CategoryRepository`：
    - `get_active_categories(list_type=None)`
    - `update_category_fields(cat_id, **kwargs)`
    - `get_category_map()`
    - `get_category(cat_id)`
    - `add_category(name, color="#0cc0df", list_type="schedule")`
    - `check_category_status(cat_id)`
    - `soft_delete_category(cat_id)`
    - `hard_delete_category(cat_id)`
- 实现边界说明：
  - 仅做 Peewee 模型低风险薄封装；未迁移 Peewee Model。
  - 未修改 `DatabaseManager`，未让 UI 直接引用 Repository，未实现新功能。
- 验证命令和结果：
  - import 验证（沙箱外权限）：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories.schedule_repository import ScheduleRepository; from src.repositories.category_repository import CategoryRepository; from src.repositories import ScheduleRepository as SR, CategoryRepository as CR; print('repositories ok')"`
    - 结果：通过，输出 `repositories ok`。
  - 禁止改动检查：
    - `git diff --name-only -- src/data/database.py` -> 无输出（未修改）
    - `git diff --name-only -- src/ui` -> 无输出（未修改）
  - 当前工作区变更检查：
    - `git status --short` -> 仅显示 `src/repositories/*` 本轮相关改动。
- 未完成事项：
  - 第一轮 B 的后续步骤（`DatabaseManager` 内部委托、`_migrate_db` 风险修复、数据库低风险调用链验证）本轮未执行。
- 风险/疑点：
  - Repository 当前为独立层，尚未接入 `db_manager`；行为一致性需在后续 B-2/B-3 委托接入后再做联调验证。

## 2026-05-13 第一轮 B-2（DatabaseManager 最小读方法委托）

- 本轮任务名称：只执行第一轮 B-2，不执行完整第一轮 B。
- 修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 委托的方法：
  - `DatabaseManager.get_all_schedules()` -> `self.schedule_repository.get_all_schedules()`
  - `DatabaseManager.get_active_categories(list_type=None)` -> `self.category_repository.get_active_categories(list_type)`
- 结构性最小变更：
  - 在 `DatabaseManager.__init__` 中延迟导入并实例化：
    - `self.schedule_repository = ScheduleRepository()`
    - `self.category_repository = CategoryRepository()`
  - 未修改写入方法（`add_schedule`、`update_schedule_with_repeat`、`delete_schedule`、`update_schedule_status`、分类删除等）。
  - 未修改 `_migrate_db` 迁移逻辑。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories.schedule_repository import ScheduleRepository; from src.repositories.category_repository import CategoryRepository; print('repositories import ok'); from src.data.database import db_manager; print('database import ok'); print('all_schedules len', len(db_manager.get_all_schedules())); print('active_categories len', len(db_manager.get_active_categories()))"`
  - 结果：通过。
    - `repositories import ok`
    - `database import ok`
    - `all_schedules len 9`
    - `active_categories len 6`
  - `git diff --name-only -- src/ui` -> 无输出（未修改 UI）。
  - `git diff --name-only` -> 仅 `src/data/database.py`（写日志前）。
- 未完成事项：
  - 第一轮 B 其余步骤未执行（例如更多方法委托、迁移逻辑修复、更广泛联调验证）。
- 风险或疑点：
  - 本轮为最小读委托，外部接口保持兼容；更深层行为一致性需在后续 B 阶段继续验证。

## 2026-05-13 第一轮 B-2 顾问窗口复核修正

- 本轮任务名称：复核执行窗口 B-2 改动并清理非逻辑性文件头问题。
- 修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 修正内容：
  - 复核 `git diff -- src/data/database.py` 时发现文件首行被加入 UTF-8 BOM/隐藏字符，表现为首行从 `# src/data/database.py` 变成带隐藏字符的 `﻿# src/data/database.py`。
  - 已移除该隐藏字符，恢复为普通 `# src/data/database.py`。
- 逻辑影响：
  - 未修改 `DatabaseManager` 委托逻辑。
  - 未修改数据库迁移逻辑。
  - 未修改 UI、Repository、主题或信号文件。
- 复核结果：
  - 当前 `database.py` diff 仅剩 B-2 预期改动：在 `DatabaseManager.__init__` 中实例化 Repository，并让 `get_all_schedules()`、`get_active_categories(list_type=None)` 委托 Repository。

## 2026-05-13 第一轮 B-3（两个查询方法委托）

- 本轮任务名称：第一轮 B-3（两个查询方法委托）。
- 实际修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 委托的方法：
  - `DatabaseManager.get_schedules_for_date(target_date)` -> `self.schedule_repository.get_schedules_for_date(target_date)`
  - `DatabaseManager.get_category_map()` -> `self.category_repository.get_category_map()`
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; schedules=db_manager.get_schedules_for_date(date.today()); category_map=db_manager.get_category_map(); print('database import ok'); print('today schedules', len(schedules), type(schedules).__name__); print('category map', len(category_map), type(category_map).__name__)"`
  - 结果：通过。
    - `database import ok`
    - `today schedules 8 list`
    - `category map 6 dict`
  - `git diff --name-only -- src/ui` -> 无输出（UI 未改动）。
  - `git diff --name-only` -> 写日志前仅 `src/data/database.py`。
- 是否有未完成事项：
  - 第一轮 B 仍未完整执行；本轮仅按要求完成 B-3 两个查询方法委托。
- 风险或疑点：
  - 本轮仅做最小读委托，外部接口保持不变；其余委托与迁移相关事项仍待后续轮次处理。

## 2026-05-13 第一轮 B-4（_migrate_db migrator 作用域修复）

- 本轮任务名称：第一轮 B-4（`_migrate_db` migrator 作用域修复）。
- 实际修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 修复内容：
  - 在 `_migrate_db` 的 `if 'list_type' not in columns_cat:` 分支内补充：
    - `from playhouse.migrate import migrate, SqliteMigrator`
    - `migrator = SqliteMigrator(db)`
  - 目的：消除 `migrator` 在该分支中可能未定义的作用域风险。
  - 未改变迁移判断顺序（`group_id` -> `schedules.sort_order` -> `categories.list_type` -> `categories.sort_order`）。
  - 未改变迁移目标与旧数据 `sort_order` 补值策略。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('database import ok')"`
  - 结果：通过，输出 `database import ok`。
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; print(len(db_manager.get_all_schedules())); print(len(db_manager.get_active_categories())); print(len(db_manager.get_schedules_for_date(date.today()))); print(len(db_manager.get_category_map()))"`
  - 结果：通过，输出：
    - `9`
    - `6`
    - `8`
    - `6`
  - `git diff --name-only -- src/ui` -> 无输出（UI 未改动）。
  - `git diff --name-only` -> 写日志前仅 `src/data/database.py`。
- 是否有未完成事项：
  - 第一轮 B 仍未完整执行；本轮仅完成 `_migrate_db` 的作用域风险修复。
- 风险或疑点：
  - 本轮未触碰迁移策略与业务逻辑，风险较低；后续仍需在完整 B 轮中继续执行剩余任务并联调验证。

## 2026-05-13 第一轮 B-5（get_category 单条读取委托）

- 本轮任务名称：第一轮 B-5（get_category 单条读取委托）。
- 实际修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 委托的方法：
  - `DatabaseManager.get_category(cat_id)` -> `self.category_repository.get_category(cat_id)`
- 语义说明：
  - 保持旧行为：查不到或异常时返回 `None`（由 `CategoryRepository.get_category` 内部 `try/except` 保持）。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('database import ok'); print('missing category', db_manager.get_category(-999999))"`
  - 结果：通过。
    - `database import ok`
    - `missing category None`
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; cats=db_manager.get_active_categories(); print('active categories', len(cats)); print('first category ok', bool(db_manager.get_category(cats[0].id)) if cats else 'no sample')"`
  - 结果：通过。
    - `active categories 6`
    - `first category ok True`
  - `git diff --name-only -- src/ui` -> 无输出（UI 未改动）。
  - `git diff --name-only` -> 写日志前仅 `src/data/database.py`。
- 是否有未完成事项：
  - 第一轮 B 仍未完整执行；本轮仅完成 `get_category` 单条读取委托。
- 风险或疑点：
  - 本轮为低风险读路径委托，外部接口与返回语义保持不变；其余委托与迁移相关任务待后续轮次执行。

## 2026-05-13 第一轮 B-6（check_category_status 只读状态判断委托）

- 本轮任务名称：第一轮 B-6（check_category_status 只读状态判断委托）。
- 实际修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 改动说明：
  - `DatabaseManager.check_category_status(cat_id)` 内部逻辑替换为委托调用：
    - `return self.category_repository.check_category_status(cat_id)`
  - 未修改 Repository 逻辑、迁移逻辑、UI、写入方法。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; allowed={'empty','active','historical'}; print('db import ok'); missing=db_manager.check_category_status(-999999); print('missing status:', missing); cats=db_manager.get_active_categories(); sample=[(c.id, db_manager.check_category_status(c.id)) for c in cats[:3]]; print('sample:', sample); assert missing in allowed; assert all(status in allowed for _, status in sample)"`
  - 结果：通过。
    - `db import ok`
    - `missing status: empty`
    - `sample: [(2, 'active'), (1, 'active'), (6, 'active')]`
  - `git diff --name-only -- src/ui` -> 无输出（UI 无改动）。
  - `git diff --name-only` -> 写日志前仅 `src/data/database.py`。
- 是否有未完成事项：
  - 第一轮 B 仍未完整执行；本轮仅完成 `check_category_status` 单方法委托。
- 风险或疑点：
  - 本轮为只读状态判断委托，返回值集合语义保持为 `empty / active / historical`。

## 2026-05-13 第一轮 B-7（update_category_fields 委托）

- 本轮任务名称：第一轮 B-7（update_category_fields 委托）。
- 实际修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 改动说明：
  - `DatabaseManager.update_category_fields(cat_id, **kwargs)` 内部逻辑替换为委托调用：
    - `return self.category_repository.update_category_fields(cat_id, **kwargs)`
  - 未修改 repository 文件、迁移逻辑、UI、其他写入/状态方法。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('db import ok'); cats=db_manager.get_active_categories(); print('cats', len(cats)); result=db_manager.update_category_fields(cats[0].id, color=cats[0].color) if cats else 'no sample'; print('update_category_fields path:', result)"`
  - 结果：通过。
    - `db import ok`
    - `cats 6`
    - `update_category_fields path: True`
  - `git diff --name-only -- src/ui` -> 无输出（UI 未改动）。
  - `git diff --name-only` -> 写日志前仅 `src/data/database.py`。
- 是否有未完成事项：
  - 第一轮 B 仍未完整执行；本轮仅完成 `update_category_fields` 单方法委托。
- 风险或疑点：
  - 本轮为低风险写入路径委托，外部接口与返回语义保持不变；其余写入/状态方法待后续轮次推进。

## 2026-05-13 第一轮 B-8（add_category 委托）

- 本轮任务名称：第一轮 B-8（add_category 委托）。
- 实际修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 改动说明：
  - `DatabaseManager.add_category(name, color="#0cc0df", list_type='schedule')` 内部逻辑替换为委托调用：
    - `return self.category_repository.add_category(name, color, list_type)`
  - 保持默认参数与返回语义不变（成功返回分类 id，失败返回 `None`）。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; print('db import ok'); name='__tmp_b8_category_'+str(int(time.time())); cat_id=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created id:', cat_id); assert cat_id is not None; cat=db_manager.get_category(cat_id); print('created name:', cat.name if cat else None); assert cat and cat.name == name; cleanup=db_manager.hard_delete_category(cat_id); print('cleanup:', cleanup); assert cleanup; print('after cleanup:', db_manager.get_category(cat_id))"`
  - 结果：通过。
    - `db import ok`
    - `created id: 7`
    - `created name: __tmp_b8_category_1778685487`
    - `cleanup: True`
    - `after cleanup: None`
  - `git diff --name-only -- src/ui` -> 无输出（UI 未改动）。
  - `git diff --name-only -- schedule.db` -> 无输出（验证创建/清理后未留下数据库文件 diff）。
  - `git diff --name-only` -> 显示：
    - `src/data/database.py`
    - `manage_instruction/Work_Task_Prompts.md`（既有改动，非本轮新增）
    - 写日志后另含 `manage_instruction/Work_Log.md`。
- 未完成事项：
  - 第一轮 B 仍未完整执行；本轮仅完成 `add_category` 单方法委托。
- 风险或疑点：
  - 工作区存在 `manage_instruction/Work_Task_Prompts.md` 的既有改动，影响“仅两文件改动”校验观感；本轮未触碰该文件内容。

## 2026-05-13 第一轮 B-9（soft_delete_category 委托）

- 本轮任务名称：第一轮 B-9（soft_delete_category 委托）。
- 实际修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 改动说明：
  - `DatabaseManager.soft_delete_category(cat_id)` 内部逻辑替换为委托调用：
    - `return self.category_repository.soft_delete_category(cat_id)`
  - 未修改 repository 文件、迁移逻辑、UI、其他写入/状态方法。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; print('db import ok'); name='__tmp_b9_soft_delete_'+str(int(time.time())); cat_id=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created id:', cat_id); assert cat_id is not None; result=db_manager.soft_delete_category(cat_id); print('soft delete:', result); assert result is True; active_ids=[c.id for c in db_manager.get_active_categories()]; print('still active:', cat_id in active_ids); assert cat_id not in active_ids; cleanup=db_manager.hard_delete_category(cat_id); print('cleanup:', cleanup); assert cleanup is True; print('after cleanup:', db_manager.get_category(cat_id)); assert db_manager.get_category(cat_id) is None"`
  - 结果：通过。
    - `db import ok`
    - `created id: 7`
    - `soft delete: True`
    - `still active: False`
    - `cleanup: True`
    - `after cleanup: None`
  - `git diff --name-only -- src/ui` -> 无输出（UI 未改动）。
  - `git diff --name-only -- schedule.db` -> 无输出（未留下数据库文件 diff）。
  - `git diff --name-only` -> 写日志前显示：
    - `src/data/database.py`
    - `manage_instruction/Work_Task_Prompts.md`（既有改动，非本轮新增）
    - 写日志后另含 `manage_instruction/Work_Log.md`。
- 未完成事项：
  - 第一轮 B 仍未完整执行；本轮仅完成 `soft_delete_category` 单方法委托。
- 风险或疑点：
  - 工作区存在 `manage_instruction/Work_Task_Prompts.md` 既有改动，影响“仅两文件改动”校验观感；本轮未触碰该文件。

## 2026-05-13 第一轮 B-10（hard_delete_category 委托）

- 本轮任务名称：第一轮 B-10（hard_delete_category 委托）。
- 实际修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 改动说明：
  - `DatabaseManager.hard_delete_category(cat_id)` 内部逻辑替换为委托调用：
    - `return self.category_repository.hard_delete_category(cat_id)`
  - 未修改 repository 文件、迁移逻辑、UI、其他写入/状态方法。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; print('db import ok'); name='__tmp_b10_hard_delete_'+str(int(time.time())); cat_id=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created id:', cat_id); assert cat_id is not None; before=db_manager.get_category(cat_id); print('before delete:', before.name if before else None); assert before and before.name == name; result=db_manager.hard_delete_category(cat_id); print('hard delete:', result); assert result is True; after=db_manager.get_category(cat_id); print('after delete:', after); assert after is None"`
  - 结果：通过。
    - `db import ok`
    - `created id: 7`
    - `before delete: __tmp_b10_hard_delete_1778686831`
    - `hard delete: True`
    - `after delete: None`
  - `git diff --name-only -- src/ui` -> 无输出（UI 未改动）。
  - `git diff --name-only -- schedule.db` -> 无输出（未留下数据库文件 diff）。
  - `git diff --name-only` -> 写日志前显示：
    - `src/data/database.py`
    - `manage_instruction/Work_Task_Prompts.md`（既有改动，非本轮新增）
    - 写日志后另含 `manage_instruction/Work_Log.md`。
- 未完成事项：
  - 第一轮 B 仍未完整执行；本轮仅完成 `hard_delete_category` 单方法委托。
- 风险或疑点：
  - 工作区存在 `manage_instruction/Work_Task_Prompts.md` 的既有改动，影响“仅两文件改动”校验观感；本轮未触碰该文件。

## 2026-05-13 第一轮 B-11（update_schedule_status 委托）

- 本轮任务名称：第一轮 B-11（update_schedule_status 委托）。
- 实际修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 改动说明：
  - `DatabaseManager.update_schedule_status(schedule_id, new_status)` 内部逻辑替换为委托调用：
    - `return self.schedule_repository.update_schedule_status(schedule_id, new_status)`
  - 未修改 repository 文件、迁移逻辑、UI、分类方法、其他 Schedule 写入/状态方法。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('db import ok'); missing=db_manager.update_schedule_status(-999999, 0); print('missing id path:', missing); schedules=db_manager.get_all_schedules(); print('schedules', len(schedules)); sample=schedules[0] if schedules else None; sid=getattr(sample, 'id', None); original=getattr(sample, 'status', None); result=db_manager.update_schedule_status(sid, original) if sample else 'no sample'; refreshed=next((s for s in db_manager.get_all_schedules() if sample and s.id == sid), None) if sample else None; verified=(refreshed is not None and refreshed.status == original) if sample else 'no sample'; print('sample id:', sid); print('original status:', original); print('update result:', result); print('verified:', verified); assert (sample is None) or (result is True and verified is True)"`
  - 结果：通过。
    - `db import ok`
    - `missing id path: True`
    - `schedules 9`
    - `sample id: 15`
    - `original status: 0`
    - `update result: True`
    - `verified: True`
  - `git diff --name-only -- src/ui` -> 无输出（UI 未改动）。
  - `git diff --name-only -- schedule.db` -> 无输出（未留下数据库文件 diff）。
  - `git diff --name-only` -> 写日志前显示：
    - `src/data/database.py`
    - `manage_instruction/Work_Task_Prompts.md`（既有改动，非本轮新增）
    - 写日志后另含 `manage_instruction/Work_Log.md`。
- 未完成事项：
  - 第一轮 B 仍未完整执行；本轮仅完成 `update_schedule_status` 单方法委托。
- 风险或疑点：
  - 缺失 ID 路径当前返回 `True`（保持现有语义，不在本轮调整）。
  - 工作区存在 `manage_instruction/Work_Task_Prompts.md` 既有改动，影响“仅两文件改动”校验观感；本轮未触碰该文件。

## 2026-05-13 第一轮 B-12（toggle_pin_status 委托）

- 本轮任务名称：第一轮 B-12（toggle_pin_status 委托）。
- 实际修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 改动说明：
  - `DatabaseManager.toggle_pin_status(schedule_id, current_pin_status)` 内部逻辑替换为委托调用：
    - `return self.schedule_repository.toggle_pin_status(schedule_id, current_pin_status)`
  - 未修改 repository 文件、迁移逻辑、UI、分类方法、其他 Schedule 写入方法。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('db import ok'); missing=db_manager.toggle_pin_status(-999999, False); print('missing id path:', missing); schedules=db_manager.get_all_schedules(); print('schedules', len(schedules)); sample=schedules[0] if schedules else None; sid=getattr(sample, 'id', None); original=getattr(sample, 'is_pinned', None); first=db_manager.toggle_pin_status(sid, original) if sample else 'no sample'; refreshed=next((s for s in db_manager.get_all_schedules() if sample and s.id == sid), None) if sample else None; toggled_ok=(refreshed is not None and refreshed.is_pinned == (not original)) if sample else 'no sample'; second=db_manager.toggle_pin_status(sid, refreshed.is_pinned) if sample and refreshed else 'no sample'; restored=next((s for s in db_manager.get_all_schedules() if sample and s.id == sid), None) if sample else None; restored_ok=(restored is not None and restored.is_pinned == original) if sample else 'no sample'; print('sample id:', sid); print('original pinned:', original); print('first toggle:', first); print('toggled ok:', toggled_ok); print('second toggle:', second); print('restored ok:', restored_ok); assert (sample is None) or (first is True and second is True and toggled_ok is True and restored_ok is True)"`
  - 结果：通过。
    - `db import ok`
    - `missing id path: True`
    - `schedules 9`
    - `sample id: 15`
    - `original pinned: False`
    - `first toggle: True`
    - `toggled ok: True`
    - `second toggle: True`
    - `restored ok: True`
  - `git diff --name-only -- src/ui` -> 无输出（UI 未改动）。
  - `git diff --name-only -- schedule.db` -> 无输出（未留下数据库文件 diff）。
  - `git diff --name-only` -> 写日志前显示：
    - `src/data/database.py`
    - `manage_instruction/Work_Task_Prompts.md`（既有改动，非本轮新增）
    - 写日志后另含 `manage_instruction/Work_Log.md`。
- 未完成事项：
  - 第一轮 B 仍未完整执行；本轮仅完成 `toggle_pin_status` 单方法委托。
- 风险或疑点：
  - 缺失 ID 路径当前返回 `True`（保持现有语义，不在本轮调整）。
  - 工作区存在 `manage_instruction/Work_Task_Prompts.md` 既有改动，影响“仅两文件改动”校验观感；本轮未触碰该文件。

## 2026-05-13 第一轮 B-13（update_schedule_fields 委托）

- 本轮任务名称：第一轮 B-13（update_schedule_fields 委托）。
- 实际修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 改动说明：
  - `DatabaseManager.update_schedule_fields(schedule_id, **kwargs)` 内部逻辑替换为委托调用：
    - `return self.schedule_repository.update_schedule_fields(schedule_id, **kwargs)`
  - 未修改 repository 文件、迁移逻辑、UI、分类方法、其他 Schedule 写入方法。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('db import ok'); missing=db_manager.update_schedule_fields(-999999, title='__missing__'); print('missing id path:', missing); schedules=db_manager.get_all_schedules(); print('schedules', len(schedules)); sample=schedules[0] if schedules else None; sid=getattr(sample, 'id', None); original=getattr(sample, 'title', None); result=db_manager.update_schedule_fields(sid, title=original) if sample else 'no sample'; refreshed=next((s for s in db_manager.get_all_schedules() if sample and s.id == sid), None) if sample else None; verified=(refreshed is not None and refreshed.title == original) if sample else 'no sample'; print('sample id:', sid); print('original title:', original); print('update result:', result); print('verified:', verified); assert (sample is None) or (result is True and verified is True)"`
  - 结果：通过。
    - `db import ok`
    - `missing id path: True`
    - `schedules 9`
    - `sample id: 15`
    - `original title: Бхзы`
    - `update result: True`
    - `verified: True`
  - `git diff --name-only -- src/ui` -> 无输出（UI 未改动）。
  - `git diff --name-only -- schedule.db` -> 无输出（未留下数据库文件 diff）。
  - `git diff --name-only` -> 写日志前显示：
    - `src/data/database.py`
    - `manage_instruction/Work_Task_Prompts.md`（既有改动，非本轮新增）
    - 写日志后另含 `manage_instruction/Work_Log.md`。
- 未完成事项：
  - 第一轮 B 仍未完整执行；本轮仅完成 `update_schedule_fields` 单方法委托。
- 风险或疑点：
  - 缺失 ID 路径当前返回 `True`（保持现有语义，不在本轮调整）。
  - 旧 `DatabaseManager` 的异常打印文案与当前 `ScheduleRepository.update_schedule_fields` 打印文案可能不一致；本轮按约束未修改 Repository。
  - 工作区存在 `manage_instruction/Work_Task_Prompts.md` 既有改动，影响“仅两文件改动”校验观感；本轮未触碰该文件。


## 2026-05-14 第一轮 B-14（delete_schedule 委托）

- 本轮任务名称：第一轮 B-14（delete_schedule 委托）。
- 实际修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 改动说明：
  - `DatabaseManager.delete_schedule(schedule_id)` 内部逻辑替换为委托调用：
    - `return self.schedule_repository.delete_schedule(schedule_id)`
  - 未修改 repository、UI、migration、分类方法、其他 Schedule 写入方法。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; print('db import ok'); missing=db_manager.delete_schedule(-999999); print('missing id path:', missing); name='__tmp_b14_delete_'+str(int(time.time())); data={'title': name, 'item_type': 'schedule', 'priority': 0, 'repeat_rule': 'none', 'description': 'temporary delete validation', 'category_id': None}; created=db_manager.add_schedule(data); print('created:', created); assert created is True; matches=[s for s in db_manager.get_all_schedules() if s.title == name]; print('matches:', len(matches)); assert len(matches) == 1; temp_id=matches[0].id; print('temp id:', temp_id); result=db_manager.delete_schedule(temp_id); print('delete result:', result); assert result is True; remaining=[s for s in db_manager.get_all_schedules() if s.id == temp_id]; print('remaining:', len(remaining)); assert len(remaining) == 0"`
  - 结果：通过。
    - `db import ok`
    - `missing id path: True`
    - `created: True`
    - `matches: 1`
    - `temp id: 16`
    - `delete result: True`
    - `remaining: 0`
  - `git diff --name-only -- src/ui` -> 无输出（UI 未改动）。
  - `git diff --name-only -- schedule.db` -> 无输出（未留下数据库文件 diff）。
  - `git diff --name-only` -> 写日志前显示：
    - `src/data/database.py`
    - `manage_instruction/Work_Task_Prompts.md`（既有改动，非本轮新增）
    - 写日志后另含 `manage_instruction/Work_Log.md`。
- 未完成事项：
  - 第一轮 B 仍未完整执行；本轮仅完成 `delete_schedule` 单方法委托。
- 风险或疑点：
  - 缺失 ID 路径当前返回 `True`（保持现有语义，不在本轮调整）。
  - 工作区存在 `manage_instruction/Work_Task_Prompts.md` 既有改动，影响“仅两文件改动”校验观感；本轮未触碰该文件。

## 2026-05-14 第一轮 B-15（B 轮整体技术验收）

- 本轮任务名称：第一轮 B-15（B 轮整体技术验收）。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 验收命令与结果摘要：
  - 读路径 / import 验证：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.repositories.schedule_repository import ScheduleRepository; from src.repositories.category_repository import CategoryRepository; from src.data.database import db_manager; ..."`
    - 结果：通过。
      - `repositories import ok`
      - `db import ok`
      - `all schedules: 9`
      - `today schedules: 8`
      - `active categories: 6`
      - `category map: 6`
      - `sample category id: 2`
      - `get_category sample: True`
      - `category status: active`
  - 分类写路径临时数据验证：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; ..."`
    - 结果：通过。
      - `created category: 7`
      - `category update: True`
      - `soft delete: True`
      - `still active: False`
      - `hard delete: True`
      - `after hard delete: None`
  - 日程写路径原值写回 + 临时删除验证：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; ..."`
    - 结果：通过。
      - `schedules: 9`
      - `status writeback: True True`
      - `pin toggle restore: True True True True`
      - `field writeback: True True`
      - `created temp schedule: True`
      - `temp matches: 1`
      - `deleted temp schedule: True`
      - `temp remaining: 0`
  - GUI smoke test：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); print('gui smoke ok'); w.close(); app.quit()"`
    - 结果：通过，输出 `gui smoke ok`（伴随 `libpng warning: tRNS: invalid with alpha channel`，不影响本轮验收结论）。
- 范围检查：
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`（既有改动，非本轮新增）。
  - `git status --short --branch` -> `main...origin/main [ahead 20]`，并显示 `M manage_instruction/Work_Task_Prompts.md`。
- 未完成事项：
  - 本轮仅做 B-15 验收，不执行新架构改动。
- 风险或疑点：
  - 工作区存在既有非本轮文件改动：`manage_instruction/Work_Task_Prompts.md`，导致“git diff 只包含日志文件”的理想状态不成立；本轮未触碰该文件。

## 2026-05-14 第一轮 B 完成总结（B-16）

- 第一轮 B 范围结论：
  - B-1 ~ B-14 已完成（Repository 薄封装 + DatabaseManager 兼容委托逐步落地）。
  - B-15 整体技术验收已完成（读写路径、GUI smoke、非侵入约束均通过）。
- 本轮（B-16）仅文档收口，不做代码改动。
- 本轮文档更新：
  - `manage_instruction/Work_Log.md`（追加完成总结）
  - `manage_instruction/Workflow_Guide.md`（更新第一轮 B 进度）
  - `manage_instruction/Work_Task_Prompts.md`（补充 B-15 复核结论）
  - `manage_instruction/Work_Formulation.md`（补充阶段完成说明）
- 当前状态：
  - 第一轮 B 已完成，可进入下一轮规划与拆单。

## 2026-05-14 第一轮 B-17（第一轮 B 归档与管理文件职责清理）

- 本轮任务名称：第一轮 B-17（归档第一轮 B 指令，并清理管理文件职责边界）。
- 本轮性质：仅文档归档与职责清理，不修改项目代码。
- 实际修改文件：
  - `manage_instruction/Work_Instruction.md`
  - `manage_instruction/History_Instruction.md`
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Workflow_Guide.md`
  - `manage_instruction/Work_Task_Prompts.md`
- 处理结果：
  - 已将第一轮 B 指令完成状态归档到 `History_Instruction.md`。
  - `Work_Instruction.md` 已清理为“等待下一阶段指令”状态，并保留执行日志硬性要求。
  - `Workflow_Guide.md` 已移除阶段进度残留，保留分工、职责、流程与注意事项。
  - `Work_Task_Prompts.md` 已清理为“等待下一小工单”的简洁状态。
- 验证命令与结果：
  - 未运行 Python（按本轮要求）。
  - 通过 `git diff --name-only` / `git status --short --branch` 进行范围检查（见本轮末尾）。
- 未完成事项：
  - 无。
- 风险或疑点：
  - 无代码层风险；本轮仅涉及管理文档文本整理。


---

## 2026-05-14 第二轮 A - Data 层连接与 Peewee 模型拆分执行日志（已完成归档）

# Work Log

本文件只记录当前阶段/当前轮次的执行日志。

历史日志已归档到 `manage_instruction/History_Log.md`。

## 当前状态

第二轮尚未开始，等待 `Work_Instruction.md` 发布第二轮阶段指令。
## 2026-05-14 第二轮 A-1（只新增 connection.py，不切换旧引用）

- 本轮任务名称：第二轮 A-1（只新增 connection.py，不切换旧引用）。
- 实际修改文件：
  - `src/data/connection.py`
  - `manage_instruction/Work_Log.md`
- 实现说明：
  - 新增 `src/data/connection.py`，仅定义数据库连接基础对象：`BASE_DIR`、`DB_PATH`、`db = SqliteDatabase(DB_PATH)`。
  - 其定义逻辑与 `src/data/database.py` 当前连接定义保持一致，用于后续 A-2 准备。
  - 本轮未切换任何旧代码引用；`database.py` 仍使用其原有 `BASE_DIR` / `DB_PATH` / `db` 定义。
- 来源说明（BASE_DIR / DB_PATH / db）：
  - 直接按 `src/data/database.py` 中现有定义等价复制。
- 依赖/导入边界确认：
  - `connection.py` 未导入 `database.py`、`models.py`、`src.repositories`、`db_manager`、UI 模块。
  - 静态检查命令：
    - `rg -n "src\.data\.database|src\.data\.models|src\.repositories|db_manager|src\.ui" src/data/connection.py`
    - 结果：无匹配（命令退出码 1）。
- connection.py import 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.connection import db, BASE_DIR, DB_PATH; print('connection import ok'); print(BASE_DIR); print(DB_PATH); print(type(db).__name__)"`
  - 结果：通过。
    - `connection import ok`
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule`
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\schedule.db`
    - `SqliteDatabase`
- DB_PATH 对比与旧 db_manager 可用性验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.connection import DB_PATH as p1; from src.data.database import DB_PATH as p2, db_manager; print('same path:', p1 == p2); print('db import ok'); print(len(db_manager.get_all_schedules()))"`
  - 结果：通过。
    - `same path: True`
    - `db import ok`
    - `62`
- diff 范围检查结果：
  - `git diff --name-only -- src/data/database.py` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`（本轮开始前既有改动）。
  - `git status --short --branch` ->
    - `M manage_instruction/Work_Task_Prompts.md`（既有改动）
    - `?? src/data/connection.py`（本轮新增）
- 未完成事项：
  - 第二轮 A-2/A-3/A-4/A-5/A-6 本轮未执行（按约束保留到后续）。
- 风险或疑点：
  - 无代码行为风险；本轮仅新增连接基础文件，未改旧引用路径。

## 2026-05-14 第二轮 A-2（database.py 改用 connection.py 的 db）

- 本轮任务名称：第二轮 A-2（database.py 改用 connection.py 的 db）。
- 实际修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 改动说明：
  - `database.py` 顶部已从 `src.data.connection` 导入 `BASE_DIR`、`DB_PATH`、`db`：
    - `from src.data.connection import BASE_DIR, DB_PATH, db`
  - 已删除 `database.py` 原本本地定义的：
    - `BASE_DIR = ...`
    - `DB_PATH = ...`
    - `db = SqliteDatabase(DB_PATH)`
  - `database.py` 对外仍保留 `BASE_DIR`、`DB_PATH`、`db` 这几个名称（通过导入暴露）。
  - 仅清理了与本轮直接相关且不再需要的 `import os`。
- 约束确认：
  - 本轮没有新增 `src/data/models.py`。
  - 本轮没有修改 `src/repositories/`。
  - 本轮未执行 A-3/A-4/A-5/A-6，也未执行第二轮 B/C/D。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.connection import DB_PATH as p1, db as db1; from src.data.database import DB_PATH as p2, db as db2, db_manager; print('same path:', p1 == p2); print('same db object:', db1 is db2); print('db import ok'); print(len(db_manager.get_all_schedules()))"`
  - 结果：
    - `same path: True`
    - `same db object: True`
    - `db import ok`
    - `62`
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; print('all schedules', len(db_manager.get_all_schedules())); print('active categories', len(db_manager.get_active_categories())); print('today schedules', len(db_manager.get_schedules_for_date(date.today())))"`
  - 结果：
    - `all schedules 62`
    - `active categories 7`
    - `today schedules 9`
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_round2a2_category_'+str(int(time.time())); cat_id=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created category', cat_id); assert cat_id is not None; cat=db_manager.get_category(cat_id); print('category exists', bool(cat)); assert cat and cat.name == name; deleted=db_manager.hard_delete_category(cat_id); print('deleted category', deleted); assert deleted is True; after=db_manager.get_category(cat_id); print('after delete', after); assert after is None"`
  - 结果：
    - `created category 8`
    - `category exists True`
    - `deleted category True`
    - `after delete None`
- diff 范围检查结果：
  - `git diff --name-only -- src/data/connection.py` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` ->
    - `src/data/database.py`
    - `manage_instruction/Work_Task_Prompts.md`（本轮开始前既有改动）
    - 写日志后另含 `manage_instruction/Work_Log.md`。
  - `git status --short --branch` ->
    - `M src/data/database.py`
    - `M manage_instruction/Work_Task_Prompts.md`（既有改动）
    - 写日志后另含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - 第二轮 A-3/A-4/A-5/A-6 待后续工单执行。
- 风险或疑点：
  - 未发现循环导入。
  - `database.py` 与 `connection.py` 数据库连接对象一致（`same db object: True`）。

## 2026-05-14 第二轮 A-3（新增 models.py 并移动 Peewee 模型类）

- 本轮任务名称：第二轮 A-3（新增 models.py 并移动 Peewee 模型类）。
- 实际修改文件：
  - `src/data/models.py`
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 移动的模型类：
  - `BaseModel`
  - `Category`
  - `Schedule`
- 结构调整结果：
  - `models.py` 已从 `connection.py` 导入 `db`：`from src.data.connection import db`
  - `models.py` 未从 `database.py` 导入任何内容。
  - `database.py` 已改为从 `models.py` 导入模型：`from src.data.models import BaseModel, Category, Schedule`
  - `database.py` 中不再保留 `BaseModel`、`Category`、`Schedule` 类定义。
- 约束确认：
  - 本轮没有修改 `src/repositories/`。
  - 本轮没有修改数据库字段含义、默认值、字段名、表名（仅类定义迁移位置）。
  - 本轮未执行 A-4/A-5/A-6，未执行第二轮 B/C/D。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.models import BaseModel, Category, Schedule; from src.data.database import db_manager; print('models import ok'); print('db import ok'); print(len(db_manager.get_all_schedules()))"`
    - 结果：`models import ok` / `db import ok` / `62`
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; print('all schedules', len(db_manager.get_all_schedules())); print('active categories', len(db_manager.get_active_categories())); print('today schedules', len(db_manager.get_schedules_for_date(date.today())))"`
    - 结果：`all schedules 62` / `active categories 7` / `today schedules 9`
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_round2a3_category_'+str(int(time.time())); cat_id=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created category', cat_id); assert cat_id is not None; cat=db_manager.get_category(cat_id); print('category exists', bool(cat)); assert cat and cat.name == name; deleted=db_manager.hard_delete_category(cat_id); print('deleted category', deleted); assert deleted is True; after=db_manager.get_category(cat_id); print('after delete', after); assert after is None"`
    - 结果：`created category 8` / `category exists True` / `deleted category True` / `after delete None`
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_round2a3_schedule_'+str(int(time.time())); data={'title': name, 'item_type': 'schedule', 'priority': 0, 'repeat_rule': 'none', 'description': 'temporary round2a3 validation', 'category_id': None}; created=db_manager.add_schedule(data); print('created schedule', created); assert created is True; matches=[s for s in db_manager.get_all_schedules() if s.title == name]; print('matches', len(matches)); assert len(matches) == 1; schedule_id=matches[0].id; deleted=db_manager.delete_schedule(schedule_id); print('deleted schedule', deleted); assert deleted is True; remaining=[s for s in db_manager.get_all_schedules() if s.id == schedule_id]; print('remaining', len(remaining)); assert len(remaining) == 0"`
    - 结果：`created schedule True` / `matches 1` / `deleted schedule True` / `remaining 0`
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); print('gui smoke ok'); w.close(); app.quit()"`
    - 结果：`gui smoke ok`（附带 `libpng warning: tRNS: invalid with alpha channel`，不影响结论）
- 导入边界验证：
  - `rg -n "from .*database import|import .*database" src/data/models.py` -> 无匹配（退出码 1，符合预期）。
  - `rg -n "^class (BaseModel|Category|Schedule)" src/data/database.py` -> 无匹配（退出码 1，符合预期）。
  - `rg -n "^class (BaseModel|Category|Schedule)" src/data/models.py` -> 匹配到 3 个类定义（符合预期）。
- diff 范围检查结果：
  - `git diff --name-only -- src/data/connection.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `src/data/database.py` + `src/data/models.py` + `manage_instruction/Work_Task_Prompts.md`（本轮开始前既有改动）；写日志后另含 `manage_instruction/Work_Log.md`。
  - `git status --short --branch` -> `M src/data/database.py`、`?? src/data/models.py`、`M manage_instruction/Work_Task_Prompts.md`（既有改动）；写日志后另含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - 第二轮 A-4/A-5/A-6 待后续工单执行。
- 风险或疑点：
  - 未发现循环导入问题；`models.py` -> `connection.py` 单向依赖，`database.py` -> `models.py` + `connection.py`，当前导入链可用。

## 2026-05-14 第二轮 A-4（ScheduleRepository 模型导入来源调整）

- 本轮任务名称：第二轮 A-4（ScheduleRepository 模型导入来源调整）。
- 实际修改文件：
  - `src/repositories/schedule_repository.py`
  - `manage_instruction/Work_Log.md`
- 修改内容说明：
  - 仅调整 `ScheduleRepository.__init__` 在 `schedule_model is None` 时的延迟导入来源：
    - 从 `from src.data.database import Schedule`
    - 改为 `from src.data.models import Schedule`
  - 其余方法实现未改动。
- 构造函数注入能力确认：
  - 已保留 `schedule_model` 注入能力与 `self._schedule_model = schedule_model` 逻辑不变。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories.schedule_repository import ScheduleRepository; from src.data.models import Schedule; repo=ScheduleRepository(); print('schedule repo import ok'); print('uses models Schedule:', repo._schedule_model is Schedule)"`
    - 结果：
      - `schedule repo import ok`
      - `uses models Schedule: True`
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; print('db import ok'); print('all schedules', len(db_manager.get_all_schedules())); print('today schedules', len(db_manager.get_schedules_for_date(date.today())))"`
    - 结果：
      - `db import ok`
      - `all schedules 62`
      - `today schedules 9`
  - 静态检查：
    - `rg -n "from src\.data\.database import Schedule|from \.\.data\.database import Schedule|from \.database import Schedule" src/repositories/schedule_repository.py`
    - 结果：无输出（退出码 1，符合预期）。
- diff 范围检查结果：
  - `git diff --name-only -- src/repositories/category_repository.py` -> 无输出。
  - `git diff --name-only -- src/data/database.py` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/data/connection.py` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` ->
    - `src/repositories/schedule_repository.py`
    - `manage_instruction/Work_Task_Prompts.md`（本轮开始前既有改动）
    - 写日志后另含 `manage_instruction/Work_Log.md`。
  - `git status --short --branch` ->
    - `M src/repositories/schedule_repository.py`
    - `M manage_instruction/Work_Task_Prompts.md`（既有改动）
    - 写日志后另含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - A-5/A-6 待后续工单执行。
- 风险或疑点：
  - 未发现行为回归或循环导入；默认模型来源已切换至 `models.py`，兼容注入路径保持不变。

## 2026-05-14 第二轮 A-5（CategoryRepository 模型导入来源调整）

- 本轮任务名称：第二轮 A-5（CategoryRepository 模型导入来源调整）。
- 实际修改文件：
  - `src/repositories/category_repository.py`
  - `manage_instruction/Work_Log.md`
- 修改内容说明：
  - 仅调整 `CategoryRepository.__init__` 在 `category_model is None` 或 `schedule_model is None` 时的延迟导入来源：
    - 从 `from src.data.database import Category, Schedule`
    - 改为 `from src.data.models import Category, Schedule`
  - 其他方法实现未改动。
- 构造函数注入能力确认：
  - 已保留 `category_model / schedule_model` 注入能力与 `self._category_model = category_model`、`self._schedule_model = schedule_model` 逻辑不变。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories.category_repository import CategoryRepository; from src.data.models import Category, Schedule; repo=CategoryRepository(); print('category repo import ok'); print('uses models Category:', repo._category_model is Category); print('uses models Schedule:', repo._schedule_model is Schedule)"`
    - 结果：
      - `category repo import ok`
      - `uses models Category: True`
      - `uses models Schedule: True`
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('db import ok'); cats=db_manager.get_active_categories(); cmap=db_manager.get_category_map(); print('active categories', len(cats)); print('category map', len(cmap)); print('sample status', db_manager.check_category_status(cats[0].id) if cats else 'no sample')"`
    - 结果：
      - `db import ok`
      - `active categories 7`
      - `category map 7`
      - `sample status active`
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_round2a5_category_'+str(int(time.time())); cat_id=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created category', cat_id); assert cat_id is not None; cat=db_manager.get_category(cat_id); print('category exists', bool(cat)); assert cat and cat.name == name; updated=db_manager.update_category_fields(cat_id, color='#0cc0df'); print('updated category', updated); assert updated is True; soft=db_manager.soft_delete_category(cat_id); print('soft deleted', soft); assert soft is True; hard=db_manager.hard_delete_category(cat_id); print('hard deleted', hard); assert hard is True; after=db_manager.get_category(cat_id); print('after delete', after); assert after is None"`
    - 结果：
      - `created category 8`
      - `category exists True`
      - `updated category True`
      - `soft deleted True`
      - `hard deleted True`
      - `after delete None`
  - 静态检查：
    - `rg -n "from src\.data\.database import Category|from src\.data\.database import Schedule|from src\.data\.database import Category, Schedule|from \.\.data\.database import Category|from \.\.data\.database import Schedule|from \.database import Category|from \.database import Schedule" src/repositories/category_repository.py`
    - 结果：无输出（退出码 1，符合预期）。
- diff 范围检查结果：
  - `git diff --name-only -- src/repositories/schedule_repository.py` -> 无输出。
  - `git diff --name-only -- src/data/database.py` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/data/connection.py` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` ->
    - `src/repositories/category_repository.py`
    - `manage_instruction/Work_Task_Prompts.md`（本轮开始前既有改动）
    - 写日志后另含 `manage_instruction/Work_Log.md`。
  - `git status --short --branch` ->
    - `M src/repositories/category_repository.py`
    - `M manage_instruction/Work_Task_Prompts.md`（既有改动）
    - 写日志后另含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - A-6 待后续工单执行。
- 风险或疑点：
  - 未发现行为回归或循环导入；默认模型来源已切换至 `models.py`，注入路径保持兼容。

## 2026-05-14 第二轮 A-6（第二轮 A 整体验收）

- 本轮任务名称：第二轮 A-6（第二轮 A 整体验收）。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 验收前范围前置检查：
  - 执行前 `git diff --name-only` 仅显示 `manage_instruction/Work_Task_Prompts.md`（既有改动），无代码文件 diff，符合“可继续验收”前置条件。
- 验证命令与结果摘要：
  - import 链路 + 模型来源 + 连接一致性：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.connection import db as db1, DB_PATH as p1; from src.data.models import BaseModel, Category, Schedule; from src.data.database import db as db2, DB_PATH as p2, db_manager; from src.repositories.schedule_repository import ScheduleRepository; from src.repositories.category_repository import CategoryRepository; ..."`
    - 结果：通过。
      - `connection/models/database/repositories import ok`
      - `db_manager import ok`
      - `same db object: True`
      - `same path: True`
      - `schedule repo uses models.Schedule: True`
      - `category repo uses models.Category: True`
      - `category repo uses models.Schedule: True`
  - 导入边界静态检查：
    - `rg -n "from .*database import|import .*database" src/data/models.py` -> 无输出（符合预期）。
    - `rg -n "^class (BaseModel|Category|Schedule)" src/data/database.py` -> 无输出（符合预期）。
    - `rg -n "^class (BaseModel|Category|Schedule)" src/data/models.py` -> 命中 3 条（符合预期）。
  - 基础读路径：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; ..."`
    - 结果：
      - `all schedules 62`
      - `today schedules 9`
      - `active categories 7`
      - `category map 7`
      - `sample category id 7`
      - `get_category sample True`
      - `check_category_status sample active`
  - 临时分类写路径（已清理）：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; ..."`
    - 结果：
      - `created category 8`
      - `category exists True`
      - `updated True`
      - `soft deleted True`
      - `hard deleted True`
      - `after delete None`
  - 临时日程写路径（已清理，repeat_rule='none'）：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; ..."`
    - 结果：
      - `created schedule True`
      - `matches 1`
      - `deleted schedule True`
      - `remaining 0`
  - GUI smoke test：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); print('gui smoke ok'); w.close(); app.quit()"`
    - 结果：通过，输出 `gui smoke ok`；附带 `libpng warning: tRNS: invalid with alpha channel`，不影响验收结论。
- diff 范围检查结果：
  - `git diff --name-only -- src/data/connection.py` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/data/database.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`（既有改动）；写日志后另含 `manage_instruction/Work_Log.md`。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`（既有改动）；写日志后另含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - 无；第二轮 A 的 A-6 验收项已完成。
- 风险或疑点：
  - 未发现循环导入、连接对象不一致或行为回归。
  - 当前工作区存在 `manage_instruction/Work_Task_Prompts.md` 既有改动（非本轮新增代码改动）。



---

## 2026-05-15 第二轮 B - 数据库连接与迁移边界整理执行日志（已完成归档）

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

## 2026-05-14 第二轮 B-3（只抽离 categories 表迁移块）

- 本轮任务名称：第二轮 B-3（只抽离 categories 表迁移块）。
- 实际修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 抽离的方法名：
  - `_migrate_categories_table(self)`
- 改动说明：
  - 将 `_migrate_db` 中 categories 表迁移逻辑抽离到 `_migrate_categories_table(self)`，包含：
    - `columns_cat = [col.name for col in db.get_columns('categories')]`
    - `list_type` 字段迁移分支
    - `sort_order` 字段迁移分支
    - `categories.sort_order` 老数据补值循环
  - `_migrate_db` 调整为顺序调用：
    - `self._migrate_schedules_table()`
    - `self._migrate_categories_table()`
- 顺序与边界确认：
  - 已确认 `_migrate_db` 保持先 schedules、后 categories 顺序。
  - 已确认本轮未改 `_migrate_schedules_table` 的实现代码（仅在 `_migrate_db` 调用顺序中引用）。
  - 已确认未改迁移字段、默认值、字段名、表名、补值策略、异常捕获和 migrate 调用顺序（categories 逻辑仅位置迁移）。
  - 已确认未修改 `_connect`、`_create_tables`、DatabaseManager 对外方法和业务方法。
- 验证命令与结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('database import ok'); print('active categories', len(db_manager.get_active_categories()))"`
    - 结果：失败。
    - 报错：`SyntaxError: unterminated string literal (detected at line 49)`（位于 `_migrate_schedules_table` 中的旧打印字符串行）。
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_b3_category_'+str(int(time.time())); ..."`
    - 结果：失败。
    - 原因同上（import 阶段即触发同一 SyntaxError）。
  - `rg -n "def _migrate_categories_table|self\._migrate_categories_table\(\)" src/data/database.py`
    - 结果：命中方法定义与调用。
  - `rg -n "self\._migrate_schedules_table\(\)|self\._migrate_categories_table\(\)" src/data/database.py`
    - 结果：两者均命中，且 `self._migrate_schedules_table()` 行号在前，`self._migrate_categories_table()` 行号在后。
  - `rg -n "def _migrate_schedules_table|group_id_field|sort_order_field" src/data/database.py`
    - 结果：命中 schedules 迁移方法与字段定义，说明方法仍存在。
- diff 范围检查结果：
  - `git diff --name-only -- src/data/connection.py` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `src/data/database.py` + `manage_instruction/Work_Task_Prompts.md`（本轮开始前既有改动）；写日志后另含 `manage_instruction/Work_Log.md`。
  - `git status --short --branch` -> `M src/data/database.py`、`M manage_instruction/Work_Task_Prompts.md`（既有改动）；写日志后另含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - Python 运行验收未通过（被 `_migrate_schedules_table` 中既有语法错误阻断）。
- 风险或疑点：
  - 主要风险：`src/data/database.py` 目前存在语法错误，影响 import 与运行验证。
  - 按本轮约束“不修改 _migrate_schedules_table”，本轮未修复该语法错误。
  - 未发现循环导入迹象；`schedule.db` 未产生 diff。
- 失败位置/回滚状态：
  - 失败位置：Python import `src.data.database` 阶段。
  - 关键报错：`SyntaxError: unterminated string literal (line 49)`。
  - 回滚状态：未回滚本轮 B-3 抽离改动（保留等待复核/后续决策）。

## 2026-05-14 第二轮 B-3 重试记录（恢复 database.py 后重做）

- 重试背景：
  - 第一次 B-3 失败日志已保留在 `Work_Log.md`。
  - 按指令先执行恢复：`git checkout HEAD -- src/data/database.py`（保留 `Work_Log.md` 与 `Work_Task_Prompts.md` 改动）。
- 重试执行约束：
  - 不整文件重写业务区块；仅对 categories 迁移块进行最小局部抽离。
  - 不修改 `_migrate_schedules_table`。
  - 不修改 `add_schedule`、`update_schedule_with_repeat`、`_add_months` 等业务方法。
- 本次重试实际修改文件：
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 重试改动内容：
  - 新增私有方法：`_migrate_categories_table(self)`。
  - 将 `_migrate_db` 中 categories 迁移逻辑迁移到 `_migrate_categories_table`。
  - `_migrate_db` 调整为按顺序调用：
    - `self._migrate_schedules_table()`
    - `self._migrate_categories_table()`
- 关键确认：
  - 已确认 `_migrate_db` 调用顺序为先 schedules、后 categories。
  - 已确认未修改 `_migrate_schedules_table` 实现内容。
  - 已确认未修改迁移字段、默认值、字段名、表名、补值策略、异常捕获和 migrate 调用顺序（categories 逻辑仅位置迁移）。
  - 已确认未修改 `_connect`、`_create_tables`、DatabaseManager 对外方法和业务方法。
- 验证命令与结果：
  - 语法预检（按要求先执行）：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src\data\database.py`
    - 结果：通过。
  - 基础分类读取：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('database import ok'); print('active categories', len(db_manager.get_active_categories()))"`
    - 结果：`database import ok`，`active categories 7`。
  - 临时分类创建/硬删除（并清理）：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_b3_category_'+str(int(time.time())); cat_id=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created category', cat_id); assert cat_id is not None; cat=db_manager.get_category(cat_id); print('category exists', bool(cat)); assert cat and cat.name == name; deleted=db_manager.hard_delete_category(cat_id); print('deleted category', deleted); assert deleted is True; after=db_manager.get_category(cat_id); print('after delete', after); assert after is None"`
    - 结果：`created category 8`，`category exists True`，`deleted category True`，`after delete None`。
  - 静态检查：
    - `rg -n "def _migrate_categories_table|self\._migrate_categories_table\(\)" src/data/database.py`
      - 结果：命中方法定义与调用。
    - `rg -n "self\._migrate_schedules_table\(\)|self\._migrate_categories_table\(\)" src/data/database.py`
      - 结果：`_migrate_schedules_table` 行号在 `_migrate_categories_table` 之前。
    - `rg -n "def _migrate_schedules_table|group_id_field|sort_order_field" src/data/database.py`
      - 结果：schedules 迁移方法及字段定义仍存在。
- diff 范围检查结果：
  - `git diff --name-only -- src/data/connection.py` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` ->
    - `src/data/database.py`
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`（本轮开始前既有改动）
  - `git status --short --branch` -> `M src/data/database.py`、`M manage_instruction/Work_Log.md`、`M manage_instruction/Work_Task_Prompts.md`（既有改动）。
- 未完成事项：
  - B-4/B-5 待后续工单。
- 风险或疑点：
  - 未发现迁移行为新增风险、循环导入风险。
  - `schedule.db` 无 diff；临时分类验证数据已清理。

## 2026-05-14 第二轮 B-4（database.py 迁移入口与职责复核）

- 本轮任务名称：第二轮 B-4（database.py 迁移入口与职责复核）。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 是否有代码改动：
  - 无需改代码。
- _migrate_db 职责复核结论：
  - `_migrate_db` 当前已收敛为迁移调度入口。
  - 仅顺序调用：
    - `self._migrate_schedules_table()`
    - `self._migrate_categories_table()`
- 关键确认：
  - 已确认 `_migrate_db` 只负责顺序调度两个迁移私有方法。
  - 已确认未改迁移目标、迁移顺序、旧数据补值策略、异常捕获和 migrate 调用顺序。
  - 已确认未改 `_connect`、`_create_tables`、DatabaseManager 对外 API 和业务方法。
- 验证命令和结果：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.connection import db as db1; from src.data.models import Category, Schedule; from src.data.database import db as db2, db_manager; print('imports ok'); print('same db object:', db1 is db2)"`
    - 结果：`imports ok`，`same db object: True`
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('all schedules', len(db_manager.get_all_schedules())); print('active categories', len(db_manager.get_active_categories()))"`
    - 结果：`all schedules 62`，`active categories 7`
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_b4_category_'+str(int(time.time())); cid=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created category', cid); assert cid is not None; cat=db_manager.get_category(cid); assert cat and cat.name == name; deleted=db_manager.hard_delete_category(cid); print('deleted category', deleted); assert deleted is True; assert db_manager.get_category(cid) is None"`
    - 结果：`created category 8`，`deleted category True`（已清理）
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_b4_schedule_'+str(int(time.time())); data={'title':name,'item_type':'schedule','priority':0,'repeat_rule':'none','description':'temporary b4 validation','category_id':None}; created=db_manager.add_schedule(data); print('created schedule', created); assert created is True; matches=[s for s in db_manager.get_all_schedules() if s.title==name]; assert len(matches)==1; sid=matches[0].id; deleted=db_manager.delete_schedule(sid); print('deleted schedule', deleted); assert deleted is True; assert not [s for s in db_manager.get_all_schedules() if s.id==sid]"`
    - 结果：`created schedule True`，`deleted schedule True`（已清理）
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); print('gui smoke ok'); w.close(); app.quit()"`
    - 结果：`gui smoke ok`（伴随 `libpng warning: tRNS: invalid with alpha channel`，不影响结论）
  - `rg -n "def _migrate_db|self\._migrate_schedules_table\(\)|self\._migrate_categories_table\(\)" src/data/database.py`
    - 结果：命中 `_migrate_db` 与两个调度调用，顺序正确（schedules 在前，categories 在后）。
- diff 范围检查结果：
  - `git diff --name-only -- src/data/connection.py` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`（本轮开始前既有改动）；写日志后另含 `manage_instruction/Work_Log.md`。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`（既有改动）；写日志后另含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - B-5 待后续工单。
- 风险或疑点：
  - 未发现迁移行为变化风险、循环导入风险或 `schedule.db` 变更风险。

## 2026-05-14 第二轮 B-5（第二轮 B 整体技术验收）

- 本轮任务名称：第二轮 B-5（第二轮 B 整体技术验收）。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- import 验证结果：
  - 命令：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.connection import db as db1, DB_PATH as p1; from src.data.models import Category, Schedule; from src.data.database import db as db2, DB_PATH as p2, db_manager; from src.repositories.schedule_repository import ScheduleRepository; from src.repositories.category_repository import CategoryRepository; print('imports ok'); print('same db object:', db1 is db2); print('same path:', p1 == p2); print('repos ok', ScheduleRepository is not None, CategoryRepository is not None)"`
  - 结果：
    - `imports ok`
    - `same db object: True`
    - `same path: True`
    - `repos ok True True`
- _migrate_db 迁移调度职责验证结果：
  - 命令：
    - `rg -n "def _migrate_db|self\._migrate_schedules_table\(\)|self\._migrate_categories_table\(\)" src/data/database.py`
  - 结果：
    - `def _migrate_db` 存在。
    - `_migrate_db` 中按顺序调用：`self._migrate_schedules_table()` -> `self._migrate_categories_table()`。
- 基础读路径验证结果：
  - 命令：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; all_schedules=db_manager.get_all_schedules(); today=db_manager.get_schedules_for_date(date.today()); cats=db_manager.get_active_categories(); cmap=db_manager.get_category_map(); print('all schedules', len(all_schedules)); print('today schedules', len(today)); print('active categories', len(cats)); print('category map', len(cmap))"`
  - 结果：
    - `all schedules 62`
    - `today schedules 9`
    - `active categories 7`
    - `category map 7`
- 临时分类写入/清理验证结果：
  - 命令：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_b5_category_'+str(int(time.time())); cid=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created category', cid); assert cid is not None; cat=db_manager.get_category(cid); assert cat and cat.name == name; updated=db_manager.update_category_fields(cid, color='#0cc0df'); print('updated', updated); assert updated is True; soft=db_manager.soft_delete_category(cid); print('soft deleted', soft); assert soft is True; hard=db_manager.hard_delete_category(cid); print('hard deleted', hard); assert hard is True; assert db_manager.get_category(cid) is None"`
  - 结果：
    - `created category 8`
    - `updated True`
    - `soft deleted True`
    - `hard deleted True`
  - 临时分类已清理。
- 临时日程写入/清理验证结果：
  - 命令：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_b5_schedule_'+str(int(time.time())); data={'title':name,'item_type':'schedule','priority':0,'repeat_rule':'none','description':'temporary b5 validation','category_id':None}; created=db_manager.add_schedule(data); print('created schedule', created); assert created is True; matches=[s for s in db_manager.get_all_schedules() if s.title==name]; assert len(matches)==1; sid=matches[0].id; deleted=db_manager.delete_schedule(sid); print('deleted schedule', deleted); assert deleted is True; assert not [s for s in db_manager.get_all_schedules() if s.id==sid]"`
  - 结果：
    - `created schedule True`
    - `deleted schedule True`
  - 临时日程已清理。
- GUI smoke test 结果：
  - 命令：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); print('gui smoke ok'); w.close(); app.quit()"`
  - 结果：通过。
    - `gui smoke ok`
    - 附带 `libpng warning: tRNS: invalid with alpha channel`，不影响验收结论。
  - 兜底 `import main` 未触发。
- diff 检查结果：
  - `git diff --name-only -- src/data` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
- git diff / status 结果：
  - 记录前：
    - `git diff --name-only` -> 无输出。
    - `git status --short --branch` -> `## main...origin/main [ahead 40]`。
  - 写日志后：
    - `git diff --name-only` -> `manage_instruction/Work_Log.md`。
    - `git status --short --branch` -> 含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - 第二轮 B 后续任务（如有）待顾问窗口继续拆分。
- 风险或疑点：
  - 本轮未发现迁移行为变化风险、循环导入风险。
  - `schedule.db` 未产生 diff。

---

## 2026-05-15 第二轮 C - Repository 依赖清理与导入关系复核（已完成归档）

归档状态：已完成。

对应提交：

- `9054c43 docs: finalize round c repository review instructions`
- `39237f1 docs: record round c1 repository dependency review`
- `92df0c0 docs: record round c2 repository import review`
- `a9c66ce docs: record round c3 repository package review`
- `e4a2fb0 docs: record round c4 repository behavior regression`
- `5b95c18 docs: close round c repository dependency review`

归档结论：

- Repository 未发现对 `db_manager`、`src.ui`、`src.data.database` 或 `database.py` 模型导入的依赖残留。
- Repository 默认模型来源确认为 `src.data.models`。
- `ScheduleRepository` 保留 `schedule_model` 构造函数注入能力。
- `CategoryRepository` 保留 `category_model / schedule_model` 构造函数注入能力。
- `src/repositories/__init__.py` 仅做轻量导出。
- C-4 / C-5 行为回归与整体验收通过。
- `src/repositories`、`src/data`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 最终均无 tracked diff。

### 2026-05-15 第二轮 C-1（Repository 静态依赖审查）

- 本轮任务名称：第二轮 C-1（Repository 静态依赖审查）。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 开工前是否已有管理文档 diff：
  - 有。开工前 `git diff --name-only` 显示 `manage_instruction/Work_Task_Prompts.md`（既有改动）。
- Repository 当前依赖关系结论：
  - 未发现 repository 依赖 `db_manager`。
  - 未发现 repository 依赖 `src.ui` 或任何 UI 模块。
  - 未发现 repository 依赖 `src.data.database`，也未发现从 `database.py` 导入模型。
  - 默认模型来源已在两个 repository 中指向 `src.data.models`。
- 构造函数注入能力确认：
  - `ScheduleRepository` 保留 `schedule_model` 注入能力。
  - `CategoryRepository` 保留 `category_model / schedule_model` 注入能力。
- 验证命令和结果：
  - `rg -n "db_manager|src\.ui|from .*data\.database|src\.data\.database|from .*database import" src/repositories`
    - 结果：无输出（退出码 1，符合预期）。
  - `rg -n "from src\.data\.models import|from \.\.data\.models import|from .*models import" src/repositories`
    - 结果：
      - `src/repositories/schedule_repository.py:9: from src.data.models import Schedule`
      - `src/repositories/category_repository.py:9: from src.data.models import Category, Schedule`
  - `rg -n "def __init__\(self, schedule_model=None\)|def __init__\(self, category_model=None, schedule_model=None\)" src/repositories`
    - 结果：
      - `src/repositories/schedule_repository.py:7: def __init__(self, schedule_model=None):`
      - `src/repositories/category_repository.py:7: def __init__(self, category_model=None, schedule_model=None):`
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories.schedule_repository import ScheduleRepository; from src.repositories.category_repository import CategoryRepository; import src.repositories as repos; print('repository imports ok'); print(ScheduleRepository is not None, CategoryRepository is not None, repos is not None)"`
    - 结果：
      - `repository imports ok`
      - `True True True`
- diff 范围检查结果：
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/data` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`（既有改动）；写日志后另含 `manage_instruction/Work_Log.md`。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`（既有改动）；写日志后另含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - 第二轮 C 后续工单待继续。
- 风险或疑点：
  - 本轮为静态依赖审查，未发现 repository 依赖边界违规项。
  - 当前存在既有管理文档改动 `manage_instruction/Work_Task_Prompts.md`，非本轮新增源码改动。

### 2026-05-15 第二轮 C-2（Repository 依赖残留修正，条件执行）- 按对话提示词复跑

- 本轮任务名称：第二轮 C-2（Repository 依赖残留修正，条件执行）。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 开工前是否已有管理文档 diff：
  - 有。开工前 `git status --short --branch` 显示：
  - `M manage_instruction/Work_Log.md`
  - `M manage_instruction/Work_Task_Prompts.md`
  - `M manage_instruction/Workflow_Guide.md`（该临时管理规范改动已在后续收口中移出本轮）。
- C-1 结论复核结果：
  - 已读取 `Work_Log.md` 中最新 C-1 记录，结论为 repository 未发现依赖 `db_manager` / `src.ui` / `src.data.database` 的残留问题；本轮复核与该结论一致。
- 静态检查结果：
  - 命令：`rg -n "db_manager|src\.ui|from .*data\.database|src\.data\.database|from .*database import" src/repositories`
  - 结果：无输出（退出码 1，符合“未命中”预期）。
- 模型来源检查结果：
  - 命令：`rg -n "from src\.data\.models import|from \.\.data\.models import|from .*models import" src/repositories`
  - 结果：
    - `src/repositories/schedule_repository.py:9: from src.data.models import Schedule`
    - `src/repositories/category_repository.py:9: from src.data.models import Category, Schedule`
- 注入能力检查结果：
  - 命令：`rg -n "def __init__\(self, schedule_model=None\)|def __init__\(self, category_model=None, schedule_model=None\)" src/repositories`
  - 结果：
    - `src/repositories/schedule_repository.py:7: def __init__(self, schedule_model=None):`
    - `src/repositories/category_repository.py:7: def __init__(self, category_model=None, schedule_model=None):`
- import 验证结果：
  - 命令：`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories.schedule_repository import ScheduleRepository; from src.repositories.category_repository import CategoryRepository; import src.repositories as repos; print('repository imports ok'); print(ScheduleRepository is not None, CategoryRepository is not None, repos is not None)"`
  - 输出：
    - `repository imports ok`
    - `True True True`
- 是否进入“无需修正”分支：
  - 是。进入分支 A，本轮 C-2 无需修正。
- 源码修正情况：
  - 无。未修改 `src/repositories/schedule_repository.py`、`src/repositories/category_repository.py`。
- diff 范围检查结果（最终状态）：
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/data` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Log.md`、`manage_instruction/Work_Task_Prompts.md`。
  - `git status --short --branch` -> `M manage_instruction/Work_Log.md`、`M manage_instruction/Work_Task_Prompts.md`。
- 未完成事项：
  - 等待顾问窗口复核并下发后续小工单。
- 风险或疑点：
  - `Workflow_Guide.md` 的临时改动已移出本轮 C-2；当前最终范围仅包含 `Work_Log.md` 与 `Work_Task_Prompts.md`。

### 2026-05-15 第二轮 C-3（repositories/__init__.py 轻量导出复核）

- 本轮任务名称：第二轮 C-3（repositories/__init__.py 轻量导出复核）。
- 开工前是否已有管理文档 diff：
  - 有。开工前 `git status --short --branch` 显示 `D manage_instruction/Work_Task_Prompts.md`（顾问窗口流程相关变更，按对话说明不作为本轮源码改动）。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- `__init__.py` 当前导出内容：
  - `from .category_repository import CategoryRepository`
  - `from .schedule_repository import ScheduleRepository`
  - `__all__ = ["ScheduleRepository", "CategoryRepository"]`
- 是否发现 `db_manager`、UI、`src.data.database` 或重型副作用导入：
  - 未发现。
  - 静态检查命令：`rg -n "db_manager|src\.ui|src\.data\.database|from .*database import|import .*database" src/repositories/__init__.py`
  - 结果：无输出（退出码 1，符合预期）。
- 是否进入“无需整理”分支：
  - 是。C-3 无需整理，不修改 `src/repositories/__init__.py`。
- import 验证结果：
  - 包级导入：
    - 命令：`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories import ScheduleRepository, CategoryRepository; print('repositories package import ok'); print(ScheduleRepository is not None, CategoryRepository is not None)"`
    - 输出：`repositories package import ok` / `True True`
  - 模块级导入：
    - 命令：`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories.schedule_repository import ScheduleRepository; from src.repositories.category_repository import CategoryRepository; print('repository modules import ok'); print(ScheduleRepository is not None, CategoryRepository is not None)"`
    - 输出：`repository modules import ok` / `True True`
  - `db_manager` 导入与读取：
    - 命令：`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('db_manager import ok'); print('all schedules', len(db_manager.get_all_schedules()))"`
    - 输出：`db_manager import ok` / `all schedules 75`
- diff 范围检查结果：
  - `git diff --name-only -- src/repositories/category_repository.py` -> 无输出。
  - `git diff --name-only -- src/repositories/schedule_repository.py` -> 无输出。
  - `git diff --name-only -- src/data` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Log.md`、`manage_instruction/Work_Task_Prompts.md`。
  - `git status --short --branch` -> `M manage_instruction/Work_Log.md`、`M manage_instruction/Work_Task_Prompts.md`。
- 未完成事项：
  - 等待顾问窗口复核并下发后续小工单。
- 风险或疑点：
  - 本轮仅做复核与日志记录；管理文档 `Work_Task_Prompts.md` 的变更来自顾问流程，不属于本轮源码改动。

### 2026-05-15 第二轮 C-4（Repository 行为回归验收）

- 本轮任务名称：第二轮 C-4（Repository 行为回归验收）。
- 开工前是否已有管理文档 diff：
  - 有。开工前 `git status --short --branch` 显示：`M manage_instruction/Work_Task_Prompts.md`（顾问窗口维护变更，不视为本轮源码改动）。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- import 验证结果：
  - 命令：`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories import ScheduleRepository, CategoryRepository; from src.repositories.schedule_repository import ScheduleRepository as SR; from src.repositories.category_repository import CategoryRepository as CR; from src.data.database import db_manager; print('imports ok'); print(ScheduleRepository is SR, CategoryRepository is CR); print('db_manager ok', db_manager is not None)"`
  - 输出：`imports ok` / `True True` / `db_manager ok True`
- 基础读路径验证结果：
  - 命令：`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; all_schedules=db_manager.get_all_schedules(); today=db_manager.get_schedules_for_date(date.today()); cats=db_manager.get_active_categories(); cmap=db_manager.get_category_map(); print('all schedules', len(all_schedules)); print('today schedules', len(today)); print('active categories', len(cats)); print('category map', len(cmap)); assert isinstance(all_schedules, list); assert isinstance(today, list); assert isinstance(cats, list); assert isinstance(cmap, dict)"`
  - 输出：`all schedules 75` / `today schedules 8` / `active categories 7` / `category map 7`
- 临时分类写入/清理验证结果：
  - 命令：`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_c4_category_'+str(int(time.time())); cid=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created category', cid); assert cid is not None; cat=db_manager.get_category(cid); assert cat and cat.name == name; updated=db_manager.update_category_fields(cid, color='#0cc0df'); print('updated', updated); assert updated is True; soft=db_manager.soft_delete_category(cid); print('soft deleted', soft); assert soft is True; hard=db_manager.hard_delete_category(cid); print('hard deleted', hard); assert hard is True; assert db_manager.get_category(cid) is None"`
  - 输出：`created category 8` / `updated True` / `soft deleted True` / `hard deleted True`
- 临时日程写入/清理验证结果：
  - 命令：`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_c4_schedule_'+str(int(time.time())); data={'title':name,'item_type':'schedule','priority':0,'repeat_rule':'none','description':'temporary c4 validation','category_id':None}; created=db_manager.add_schedule(data); print('created schedule', created); assert created is True; matches=[s for s in db_manager.get_all_schedules() if s.title==name]; print('matches', len(matches)); assert len(matches)==1; sid=matches[0].id; deleted=db_manager.delete_schedule(sid); print('deleted schedule', deleted); assert deleted is True; remaining=[s for s in db_manager.get_all_schedules() if s.id==sid]; print('remaining', len(remaining)); assert len(remaining)==0"`
  - 输出：`created schedule True` / `matches 1` / `deleted schedule True` / `remaining 0`
- GUI smoke test 结果：
  - 命令：`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); print('gui smoke ok'); w.close(); app.quit()"`
  - 输出：`gui smoke ok`
  - 备注：出现 `libpng warning: tRNS: invalid with alpha channel`，不影响本次 smoke 通过。
- diff 检查结果：
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/data` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> 验证时为 `manage_instruction/Work_Task_Prompts.md`；写入本日志后另含 `manage_instruction/Work_Log.md`。
  - `git status --short --branch` -> 验证时为 `M manage_instruction/Work_Task_Prompts.md`；写入本日志后另含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - 等待顾问窗口复核并下发后续工单。
- 风险或疑点：
  - 本轮临时分类与临时日程均已清理，`schedule.db` 无 tracked diff。

### 2026-05-15 第二轮 C-5（第二轮 C 整体验收与归档准备）

- 本轮任务名称：第二轮 C-5（第二轮 C 整体验收与归档准备）。
- 开工前是否已有管理文档 diff：
  - 有。开工前 `git status --short --branch` 显示：`M manage_instruction/Work_Task_Prompts.md`（顾问窗口维护变更，不视为本轮源码改动）。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- C-1 依赖审查结论：
  - Repository 未发现对 `db_manager`、`src.ui`、`src.data.database` 或 `database.py` 模型导入的依赖残留。
- C-2 import 残留修正确认结论：
  - 进入“无需修正”分支；未修改 `schedule_repository.py`、`category_repository.py`。
- C-3 `__init__.py` 轻量导出结论：
  - `src/repositories/__init__.py` 仅导出 `ScheduleRepository`、`CategoryRepository`，未发现重型副作用导入。
- C-4 行为回归验收结论：
  - 读路径、临时分类写入/清理、临时日程写入/清理验证通过；GUI smoke test 通过。
- Repository 依赖边界最终结论：
  - Repository 依赖边界满足第二轮 C 预期：不依赖 `db_manager`、UI、`src.data.database`；默认模型来源为 `src.data.models`；构造函数注入能力保留。
- import 验证结果（C-5 复跑）：
  - 命令：`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.repositories import ScheduleRepository, CategoryRepository; from src.repositories.schedule_repository import ScheduleRepository as SR; from src.repositories.category_repository import CategoryRepository as CR; from src.data.database import db_manager; print('imports ok'); print(ScheduleRepository is SR, CategoryRepository is CR); print('db_manager ok', db_manager is not None)"`
  - 输出：`imports ok` / `True True` / `db_manager ok True`
- 依赖边界静态复核（C-5 复跑）：
  - 命令：`rg -n "db_manager|src\.ui|from .*data\.database|src\.data\.database|from .*database import" src/repositories`
  - 结果：无输出（退出码 1，符合预期）。
- 模型来源与注入能力复核（C-5 复跑）：
  - 命令：`rg -n "from src\.data\.models import|def __init__\(self, schedule_model=None\)|def __init__\(self, category_model=None, schedule_model=None\)" src/repositories`
  - 结果：命中 `src.data.models` 导入与两个 Repository 的注入构造函数签名。
- `__init__.py` 轻量导出复核（C-5 复跑）：
  - `Get-Content` 结果：
    - `from .category_repository import CategoryRepository`
    - `from .schedule_repository import ScheduleRepository`
    - `__all__ = ["ScheduleRepository", "CategoryRepository"]`
  - 命令：`rg -n "db_manager|src\.ui|src\.data\.database|from .*database import|import .*database" src/repositories/__init__.py`
  - 结果：无输出（退出码 1，符合预期）。
- 基础读路径复核结果（C-5 复跑）：
  - 命令：`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; all_schedules=db_manager.get_all_schedules(); today=db_manager.get_schedules_for_date(date.today()); cats=db_manager.get_active_categories(); cmap=db_manager.get_category_map(); print('all schedules', len(all_schedules)); print('today schedules', len(today)); print('active categories', len(cats)); print('category map', len(cmap)); assert isinstance(all_schedules, list); assert isinstance(today, list); assert isinstance(cats, list); assert isinstance(cmap, dict)"`
  - 输出：`all schedules 75` / `today schedules 8` / `active categories 7` / `category map 7`
- GUI smoke test 结果（C-5 复跑）：
  - 命令：`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); print('gui smoke ok'); w.close(); app.quit()"`
  - 输出：`gui smoke ok`
  - 备注：出现 `libpng warning: tRNS: invalid with alpha channel`，不影响 smoke 通过。
- diff 范围检查结果：
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/data` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> 验证时为 `manage_instruction/Work_Task_Prompts.md`；写入本日志后另含 `manage_instruction/Work_Log.md`。
  - `git status --short --branch` -> 验证时为 `M manage_instruction/Work_Task_Prompts.md`；写入本日志后另含 `M manage_instruction/Work_Log.md`。
- 是否可以进入第二轮 D：
  - 可以。第二轮 C（C-1 ~ C-5）关键复核项已满足，具备进入第二轮 D 的条件。
- 未完成事项：
  - 等待顾问窗口复核并下发第二轮 D 工单。
- 风险或疑点：
  - 本轮未做源码改动；`schedule.db` 无 tracked diff。当前仅管理文档存在变更。

---

## 2026-05-17 第二轮 D - Data 层整体技术验收（已完成归档）

归档状态：已完成。

对应提交：

- `51bf837 docs: record round d1 data import boundary review`
- `56dab09 docs: record round d2 data read path regression`
- `f4f7a11 docs: record round d3 category write path validation`
- `005df9b docs: record round d4 schedule write path validation`
- `10c4fbc docs: close round d data layer validation`

归档结论：

- D-1 静态边界与 import 复核通过。
- D-2 Data 层读路径回归验收通过。
- D-3 分类写路径临时验收通过，临时分类已清理。
- D-4 日程写路径临时验收通过，真实样本已恢复，临时日程已清理。
- D-5 GUI smoke 与第二轮整体验收收口通过。
- `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 最终均无 tracked diff。
- 第二轮 Data 层整理与模型拆分可归档，可进入第三轮规划。
- 进度估算：按至少 8 轮架构迁移口径约 25%；若纳入第九轮及后续功能轮约 22%，后续功能范围未完全定稿。

### 2026-05-15 第二轮 D-1（Data 层静态边界与 import 复核）

- 本轮任务名称：第二轮 D-1（Data 层静态边界与 import 复核）。
- 开工前是否已有管理文档 diff：
  - 有。开工前 `git status --short --branch` 显示：`M manage_instruction/Work_Task_Prompts.md`（顾问窗口维护变更，不视为本轮源码改动）。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- import 验证结果：
  - 输出：`imports ok` / `same db object: True` / `same DB_PATH: True` / `repositories ok: True True True` / `db_manager ok: True`
- db 对象一致性验证结果：
  - `src.data.connection.db is src.data.database.db` -> `True`
- DB_PATH 一致性验证结果：
  - `src.data.connection.DB_PATH == src.data.database.DB_PATH` -> `True`
- Repository 依赖静态检查结果：
  - `rg -n "db_manager|src\.ui|from .*data\.database|src\.data\.database|from .*database import" src/repositories`
  - 结果：无输出（退出码 1，符合预期）。
- repositories/__init__.py 轻量导出检查结果：
  - `src/repositories/__init__.py` 只导出 `CategoryRepository`、`ScheduleRepository` 和 `__all__`。
  - 重型导入静态检查无输出。
- Repository 模型来源与构造函数注入能力检查结果：
  - `ScheduleRepository` 保留 `schedule_model=None` 注入参数，并从 `src.data.models` 延迟导入 `Schedule`。
  - `CategoryRepository` 保留 `category_model=None, schedule_model=None` 注入参数，并从 `src.data.models` 延迟导入 `Category, Schedule`。
- schedule.db 是否无 tracked diff：
  - `git diff --name-only -- schedule.db` -> 无输出。
- diff 范围检查结果：
  - `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 均无 diff。
  - 最终仅管理文档有 diff。
- 未完成事项：
  - D-2 待继续。
- 风险或疑点：
  - 未发现边界异常或数据库 tracked diff。

### 2026-05-15 第二轮 D-2（Data 层读路径回归验收）

- 本轮任务名称：第二轮 D-2（Data 层读路径回归验收）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 D-2 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- `get_all_schedules` 验证结果：
  - `all schedules 75 list`，返回类型为 `list`，通过。
- `get_schedules_for_date` 验证结果：
  - `today schedules 8 list`，返回类型为 `list`，通过。
- `get_active_categories` 验证结果：
  - `active categories 7 list`，返回类型为 `list`，通过。
- `get_category_map` 验证结果：
  - `category map 7 dict`，返回类型为 `dict`，通过。
- 分类样本读取与 `check_category_status` 验证结果：
  - 样本数 `7`，`get_category` 匹配通过，`check_category_status` 返回 `historical`，在允许集合 `{empty, active, historical}` 内。
- 日程样本基础字段读取验证结果：
  - 样本数 `75`，样本 id `72`，`title/item_type/status` 字段可访问。
- 是否确认本轮未执行任何写入方法：
  - 是。仅执行读路径相关命令。
- schedule.db 是否无 tracked diff：
  - `git diff --name-only -- schedule.db` -> 无输出。
- diff 范围检查结果：
  - `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 均无 diff。
  - 最终仅管理文档有 diff。
- 未完成事项：
  - D-3 待继续。
- 风险或疑点：
  - 未触发写入；未发现 `schedule.db` tracked diff 或源码范围异常。

### 2026-05-15 第二轮 D-3（分类写路径临时验收）

- 本轮任务名称：第二轮 D-3（分类写路径临时验收）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 D-3 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 临时分类名称与 id：
  - 名称：`__tmp_d3_category_1778843489`
  - id：`8`
- `add_category` 验证结果：
  - `created category 8`，通过。
- `get_category` 验证结果：
  - `category exists True`，通过。
- `update_category_fields` 验证结果：
  - `updated True`，通过。
- `soft_delete_category` 验证结果：
  - `soft deleted True`，通过。
- `hard_delete_category` 验证结果：
  - `hard deleted True`，通过。
- 清理后 `get_category(cat_id)` 是否返回 `None`：
  - `after delete None`，通过。
- 是否确认本轮未修改源码：
  - 是。本轮仅执行验收写路径命令与日志记录。
- schedule.db 是否无 tracked diff：
  - `git diff --name-only -- schedule.db` -> 无输出。
- diff 范围检查结果：
  - `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 均无 diff。
  - 最终仅管理文档有 diff。
- 未完成事项：
  - D-4 待继续。
- 风险或疑点：
  - 分类临时数据已清理；未发现 `schedule.db` tracked diff。

### 2026-05-15 第二轮 D-4（日程写路径临时验收）

- 本轮任务名称：第二轮 D-4（日程写路径临时验收）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 D-4 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 是否存在可安全恢复的日程样本：
  - 是。样本数量 `75`，样本 id `72`。
- `update_schedule_status` 写入/恢复验证结果：
  - 原值 `status=0`，测试写入值 `1`，输出 `status write/restore True True`，恢复结果 `restored status 0`，通过。
- `toggle_pin_status` 切换/恢复验证结果：
  - 原值 `is_pinned=False`，输出 `pin toggle/restore True True`，恢复结果 `restored pin False`，通过。
- `update_schedule_fields` 临时 title 写入/恢复验证结果：
  - 原值 `title=测试`，临时值 `测试__d4_tmp_1778843910`，输出 `temp title set True`、`title temp/restore True True`，恢复结果 `restored title 测试`，通过。
- 临时日程名称与 id：
  - 名称：`__tmp_d4_schedule_1778843910`
  - id：`83`
- `add_schedule` 验证结果：
  - `created schedule True`、`matches 1`，通过。
- `delete_schedule` 验证结果：
  - `deleted schedule True`，通过。
- 删除后是否查询不到临时 id：
  - `remaining 0`，删除后查询不到该临时 id。
- schedule.db 是否无 tracked diff：
  - `git diff --name-only -- schedule.db` -> 无输出。
- diff 范围检查结果：
  - `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 均无 diff。
  - 最终仅管理文档有 diff。
- 未完成事项：
  - D-5 待继续。
- 风险或疑点：
  - 真实样本已恢复，临时日程已清理；未发现 `schedule.db` tracked diff。

### 2026-05-15 第二轮 D-5（GUI smoke 与第二轮整体验收收口）

- 本轮任务名称：第二轮 D-5（GUI smoke 与第二轮整体验收收口）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 D-5 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- D-1 结论汇总（静态边界与 import）：
  - 通过。`connection/models/database/repositories/db_manager` 可 import，`db` 对象与 `DB_PATH` 一致；repository 边界无 `db_manager/UI/src.data.database` 残留依赖。
- D-2 结论汇总（读路径回归）：
  - 通过。`get_all_schedules/get_schedules_for_date/get_active_categories/get_category_map` 返回类型正确；分类与日程样本读取可用。
- D-3 结论汇总（分类写路径临时验收）：
  - 通过。`add/get/update/soft_delete/hard_delete` 路径可用，删除后 `get_category(cat_id)` 返回 `None`，临时数据已清理。
- D-4 结论汇总（日程写路径临时验收）：
  - 通过。样本 `status/is_pinned/title` 写回并恢复成功；临时日程创建删除成功且删除后查询不到，临时数据已清理。
- 最小 import 复跑结果：
  - 输出：`imports ok` / `same db object: True` / `same DB_PATH: True` / `repos ok: True True` / `db_manager ok: True`
  - 结论：通过。
- 最小读路径复跑结果：
  - 输出：`all 75 list` / `today 8 list` / `cats 7 list` / `cmap 7 dict`
  - 断言：四条读路径返回类型验证通过。
- GUI smoke test 结果：
  - 输出：`gui smoke ok`
  - 备注：出现 `libpng warning: tRNS: invalid with alpha channel`，不影响 smoke 通过；无需 `import main` 兜底。
- diff 范围检查结果：
  - `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 均无 diff。
  - 最终仅管理文档有 diff。
- 是否可以归档第二轮并进入第三轮规划：
  - 可以。第二轮 D（D-1~D-5）验收收口通过，且第二轮整体可归档，可进入第三轮规划。
- 当前进度估算：
  - 按 `Work_Formulation.md` 至少 8 轮架构迁移口径：D-5 通过后约 `25%`。
  - 若把第九轮及后续新功能轮纳入总目标：当前约 `22%`，且后续功能范围未完全定稿。
- 未完成事项：
  - 第二轮归档后等待第三轮规划。
- 风险或疑点：
  - 归档前最终总检查通过；源码与 `schedule.db` 范围保持干净。

---

# 2026-05-17 第三轮归档：纯业务查询与排序服务

# Work Log

本文件只记录当前阶段/当前轮次的执行日志。

历史日志已归档到 `manage_instruction/History_Log.md`。

## 当前状态

第二轮 Data 层整理与模型拆分已完成并归档。

当前等待第三轮（纯业务查询与排序服务）规划与小工单发布。

## 当前轮次注意事项

- 暂无可执行小工单。
- 第三轮任务发布前，应先由决策窗口基于 `Work_Formulation.md` 细化第三轮边界。
- 执行窗口不得沿用第二轮 D 的提示词继续执行。

## 2026-05-17 第三轮 3-0（静态审查与旧逻辑定位）

- 本轮任务名称：第三轮 3-0（静态审查与旧逻辑定位）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 3-0 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 已读取的关键文件：
  - `manage_instruction/Work_Instruction.md`
  - `src/repositories/schedule_repository.py`
  - `src/repositories/category_repository.py`
  - `src/repositories/__init__.py`
  - `src/data/database.py`
  - `src/data/models.py`
  - `src/ui/dashboard.py`
  - `src/ui/week_window.py`
  - `src/ui/todo.py`
  - `src/ui/todo_board.py`
  - `src/ui/list_picker.py`
  - `src/ui/main_window.py`
  - `src/ui/month_window.py`
  - `src/services/weather_service.py`
- 日期过滤逻辑位置清单：
  - `src/repositories/schedule_repository.py:53` `get_schedules_for_date(target_date)`：核心日期过滤（`start_time/end_time` 与 `target_date` 比较）。
  - `src/repositories/schedule_repository.py:63-71`：`start_date/end_date` 分支判断（区间命中、截止日命中）。
  - `src/ui/week_window.py:1031-1032`：周视图按每天调用 `db_manager.get_schedules_for_date(target_date)`。
  - `src/ui/dashboard.py:499`：日视图调用 `db_manager.get_schedules_for_date(self.current_date)`。
- 日程/待办区分逻辑位置清单：
  - Repository 侧：`src/repositories/schedule_repository.py:57-60`（`item_type == "todo"` 的特殊分支）。
  - 日视图：`src/ui/dashboard.py:506-510`（`item_type == 'todo'` 或 `type == 1` 判为待办并排除）。
  - 周视图：`src/ui/week_window.py:1032`（仅保留 `item_type == 'schedule'` 且 `status != 2`）。
  - 待办列表：`src/ui/todo.py:445-450`（同样以 `item_type/type` 判定待办）。
  - 待办看板：`src/ui/todo_board.py:1298-1302`（`is_todo` 且 `status == 0` 才进入渲染集合）。
- 日视图排序逻辑位置清单：
  - `src/ui/dashboard.py:512-519`：`rank_pin` + `rank_status` + `sort_order`（降序）组合排序。
- 周视图排序逻辑位置清单：
  - `src/ui/week_window.py:1038-1045`：与日视图同构（`rank_pin/rank_status/sort_order`）。
- 待办列表排序逻辑位置清单：
  - `src/ui/todo.py:454-463`：与日视图同构（`rank_pin/rank_status/sort_order`）。
- 待办看板排序逻辑位置清单：
  - 主看板渲染排序：`src/ui/todo_board.py:1316-1322`（`rank_pin` + `sort_order`）。
  - 看板“一键按重要性排序”：`src/ui/todo_board.py:1765-1794`（按 `priority`、`created_at` 排，再写回 `sort_order`）。
- 分类状态判断逻辑位置清单：
  - 核心策略：`src/repositories/category_repository.py:50-61`（`empty/active/historical`）。
  - 委托门面：`src/data/database.py:294-295`（`db_manager.check_category_status -> category_repository`）。
  - UI 使用点：`src/ui/list_picker.py:356-382`、`src/ui/todo_board.py:976-990`、`src/ui/todo_board.py:2028-2048`。
- 分类删除策略位置清单：
  - 核心执行：`src/repositories/category_repository.py:63-72`（`soft_delete_category` / `hard_delete_category`）。
  - 委托门面：`src/data/database.py:297-301`。
  - UI 决策：
    - `src/ui/list_picker.py:356-382`（active 拦截、historical 二次确认后软删、empty 硬删）。
    - `src/ui/todo_board.py:976-990` 与 `2028-2048`（同类策略）。
- 四象限相关现有逻辑或缺口：
  - 已有入口/文案：
    - `src/ui/dashboard.py:74` 视图项包含 `priority: 四象限`。
    - `src/ui/week_window.py:435`、`src/ui/month_window.py:472` 视图切换含“象限/四象限”。
    - `src/ui/main_window.py:632-634` 仅 toast：`准备切换至：四象限视图`。
  - 已有可用字段：`src/data/models.py:33` `priority`，以及 `start_time/end_time/status/is_pinned/created_at/sort_order`。
  - 缺口结论：当前无独立“四象限分类服务”或稳定分类规则实现，现状主要是“优先级展示/排序”，非四象限业务分类。
- 按来源归类的逻辑分布：
  - `database.py`：主要是兼容门面委托（`get_schedules_for_date`、分类状态/删除等转发），非策略主实现。
  - `repositories`：
    - `schedule_repository.py`：日期过滤 + 一套基础排序。
    - `category_repository.py`：分类状态判断与删除策略核心。
  - `UI`：
    - `dashboard/week_window/todo/todo_board` 各自有二次过滤与排序规则。
    - `list_picker/todo_board` 承担分类删除流程分支决策。
  - `services`：当前仅 `weather_service.py`，与第三轮目标无关；暂无查询/排序/分类策略服务。
  - 其他：`models.py` 提供可用于四象限纯逻辑的字段基础。
- 第三轮适合抽取的逻辑清单：
  - 统一的“日程/待办判定谓词”和“状态判定谓词（完成/隐藏/逾期）”。
  - 日期过滤核心规则（从 `schedule_repository.get_schedules_for_date` 抽离为纯函数/服务）。
  - 视图排序 key 生成逻辑（day/week/todo/todo_board 主排序分别抽为明确策略函数）。
  - 分类状态判断与删除策略判定（`empty/active/historical` 与 soft/hard delete 决策条件）抽为 category policy。
  - 四象限仅做“纯逻辑规则准备与缺口报告”，不接 UI。
- 应留到后续轮次的逻辑清单：
  - 拖拽重排后写回 `sort_order`（`dashboard/week_window/todo/todo_board` 的写库行为）。
  - `todo_board._sort_by_priority` 的“排序+持久化写回”整段（非纯查询逻辑）。
  - 重复日程写入、提醒、编辑流程、UI 路由切换等非第三轮纯逻辑目标。
- 是否建议拆分 3-2、3-3、3-4：
  - 建议继续拆分。
  - 3-2 可拆：`3-2a` Repository 日期过滤纯逻辑抽取；`3-2b` UI 侧 todo/schedule 区分统一。
  - 3-3 可拆：`3-3a` day/week/todo 排序 key 抽取；`3-3b` todo_board 主排序与 priority 排序（后者含写库，需单独边界）。
  - 3-4 可拆：`3-4a` 分类状态判断抽取；`3-4b` 删除策略分支抽取（active 拦截、historical 软删、empty 硬删）。
- 范围检查结果：
  - `git diff --name-only -- src/data` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Log.md`、`manage_instruction/Work_Task_Prompts.md`。
  - `git status --short --branch` -> `M manage_instruction/Work_Log.md`、`M manage_instruction/Work_Task_Prompts.md`。
- 未完成事项：
  - 等待顾问窗口基于本定位结果下发 3-1 或 3-2a 细化工单。
- 风险或疑点：
  - 同一业务在 Repository 与多个 UI 层存在重复/并行排序与过滤规则，若直接合并易改变可见顺序。
  - `todo_board._sort_by_priority` 含持久化写回，不能与纯读排序策略混做一轮抽取。
  - “四象限”目前是入口占位，不是完整业务实现，需先明确稳定规则再落地服务。

## 2026-05-17 第三轮 3-1（服务骨架与边界确认）

- 本轮任务名称：第三轮 3-1（服务骨架与边界确认）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 3-1 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/services/schedule_query_service.py`（新增）
  - `src/services/schedule_sort_service.py`（新增）
  - `src/services/category_policy_service.py`（新增）
  - `src/services/__init__.py`（轻量导出）
  - `manage_instruction/Work_Log.md`
- 读取的依据文件：
  - `manage_instruction/Work_Instruction.md`（第三轮合同与 3-1 边界）
  - `manage_instruction/Work_Log.md`（3-0 定位结论）
  - `src/services/__init__.py`、`src/services/weather_service.py`
- 基于 3-0 结论创建了哪些 service 文件：
  - `schedule_query_service.py`：承接 3-2（日期过滤、日程/待办区分）边界。
  - `schedule_sort_service.py`：承接 3-3（day/week/todo/todo_board 排序策略）边界。
  - `category_policy_service.py`：承接 3-4（分类状态判断、删除策略判定）边界。
- 哪些候选 service 暂不创建及原因：
  - `matrix_classification_service.py` 暂不创建。
  - 原因：3-0 结论显示当前仅有四象限入口与 `priority` 基础字段，尚无稳定分类规则实现；按合同留待 3-5 做规则评估与最小服务准备。
- 是否修改 `src/services/__init__.py`：
  - 是。仅添加轻量导出（`ScheduleQueryService`、`ScheduleSortService`、`CategoryPolicyService`、`CategoryStatus`、`CategoryDeleteAction`），无副作用调用。
- 是否确认 `weather_service.py` 未改动：
  - 是。`git diff --name-only -- src/services/weather_service.py` 无输出。
- service import 验证结果：
  - 给定命令在当前环境报错：`AttributeError: module 'importlib' has no attribute 'util'`。
  - 使用等价修正版命令复核通过：
    - `existing service imports ok: ['src.services.schedule_query_service', 'src.services.schedule_sort_service', 'src.services.category_policy_service']`
    - `missing service modules: []`
- 旧 `db_manager` 路径验证结果：
  - 输出：`db_manager import ok` / `schedules 75` / `categories 7`。
  - 结论：旧路径可用，未受服务骨架影响。
- 静态依赖检查结果：
  - 命令：`rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services`
  - 命中：仅 `src/services/weather_service.py` 的既有 `PyQt6` 依赖。
  - 新建第三轮 service 文件未命中 UI / QWidget / db_manager / repository 依赖。
- diff 范围检查结果：
  - `git diff --name-only -- src/services/weather_service.py` -> 无输出。
  - `git diff --name-only -- src/data` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`、`src/services/__init__.py`、`src/services/schedule_query_service.py`、`src/services/schedule_sort_service.py`、`src/services/category_policy_service.py`（写入本日志后另含 `manage_instruction/Work_Log.md`）。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`、`M src/services/__init__.py`、`?? src/services/schedule_query_service.py`、`?? src/services/schedule_sort_service.py`、`?? src/services/category_policy_service.py`（写入本日志后另含 `M manage_instruction/Work_Log.md`）。
- 后续 3-2 / 3-3 / 3-4 / 3-5 承接建议：
  - 3-2：在 `ScheduleQueryService` 实现日期过滤与 todo/schedule 判定，先对齐 `schedule_repository.get_schedules_for_date` 语义。
  - 3-3：在 `ScheduleSortService` 分别实现 day/week/todo/todo_board 排序键，避免一次合并导致顺序回归。
  - 3-4：在 `CategoryPolicyService` 实现 `empty/active/historical` 判定与删除动作映射，保持旧 UI 删除分支语义。
  - 3-5：仅在规则明确后评估并实现四象限纯逻辑服务；当前继续保持“暂不创建 matrix 服务”。
- 未完成事项：
  - 等待顾问窗口复核并下发 3-2（建议先 3-2a）工单。
- 风险或疑点：
  - 本轮仅建立边界，后续实现时需逐视图比对排序结果，避免 UI 可见顺序回归。
  - 给定 import 验证命令在当前环境存在 `importlib.util` 调用兼容问题，已用等价命令完成验证。

## 2026-05-17 第三轮 3-2a（ScheduleQueryService 日期过滤纯逻辑抽取）

- 本轮任务名称：第三轮 3-2a（ScheduleQueryService 日期过滤纯逻辑抽取）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 3-2a 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/services/schedule_query_service.py`
  - `src/repositories/schedule_repository.py`
  - `manage_instruction/Work_Log.md`
- 开工前基线命令和输出摘要：
  - 命令：`python -c "... db_manager.get_schedules_for_date(d) ..."`（昨天/今天/明天）
  - 输出：
    - `2026-05-16 [8, 9, 10, 11, 12, 13, 14, 15]`
    - `2026-05-17 [8, 9, 10, 11, 12, 13, 14, 15]`
    - `2026-05-18 [8, 9, 10, 11, 12, 13, 14, 15]`
- 实现的 service 方法：
  - 在 `ScheduleQueryService.filter_for_date(items, target_date)` 中实现了旧 Repository 日期过滤规则：
    - `item_type == "todo"` 且无 `end_time` 保留。
    - 同时有 `start_time/end_time` 时，`start_date <= target_date <= end_date` 保留。
    - 仅有 `end_time` 时，`end_date == target_date` 保留。
    - 其余（无 `end_time`）保留。
  - 方法输入 iterable，输出 list；不访问数据库，不依赖 UI/db_manager/Repository。
- Repository 委托方式：
  - `ScheduleRepository.get_schedules_for_date(target_date)` 仍先执行 `self._schedule_model.select()`，再调用 `ScheduleQueryService.filter_for_date(all_data, target_date)` 生成 `filtered`。
- 排序逻辑迁移说明：
  - 本轮未迁移排序逻辑，`get_schedules_for_date` 内现有排序逻辑保持在 Repository。
- `split_schedule_and_todo` 状态说明：
  - 未实现，保持 3-1 的占位状态，留给后续 3-2b。
- 修改后同一日期 id 顺序是否与基线一致：
  - 一致。改后输出：
    - `2026-05-16 [8, 9, 10, 11, 12, 13, 14, 15]`
    - `2026-05-17 [8, 9, 10, 11, 12, 13, 14, 15]`
    - `2026-05-18 [8, 9, 10, 11, 12, 13, 14, 15]`
- service import / direct call 验证结果：
  - `service filter ok True 8`（返回 list，长度 8）。
- 旧 `db_manager.get_schedules_for_date` 验证结果：
  - `db_manager path ok True 8`（返回 list，长度 8）。
- 静态依赖检查结果：
  - 命令：`rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_query_service.py`
  - 结果：无输出（退出码 1，符合预期）。
- 本轮未误动其他 service 检查：
  - `git diff --name-only -- src/services/schedule_sort_service.py` -> 无输出。
  - `git diff --name-only -- src/services/category_policy_service.py` -> 无输出。
  - `git diff --name-only -- src/services/weather_service.py` -> 无输出。
- diff 范围检查结果：
  - `git diff --name-only -- src/data` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> 验证时为 `manage_instruction/Work_Task_Prompts.md`、`src/repositories/schedule_repository.py`、`src/services/schedule_query_service.py`；写入本日志后另含 `manage_instruction/Work_Log.md`。
  - `git status --short --branch` -> 验证时为 `M manage_instruction/Work_Task_Prompts.md`、`M src/repositories/schedule_repository.py`、`M src/services/schedule_query_service.py`；写入本日志后另含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - 等待顾问窗口复核并下发 3-2b 或 3-3 工单。
- 风险或疑点：
  - 本轮仅迁移过滤，不迁移排序；后续 3-3 需确保排序抽取后顺序不变。
  - `item_type` 仍按旧语义直接读取对象属性，保持与原 Repository 行为一致。

## 2026-05-17 第三轮 3-2b（日程/待办区分纯逻辑抽取）

- 本轮任务名称：第三轮 3-2b（日程/待办区分纯逻辑抽取）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 3-2b 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/services/schedule_query_service.py`
  - `src/ui/dashboard.py`
  - `src/ui/week_window.py`
  - `src/ui/todo.py`
  - `src/ui/todo_board.py`
  - `manage_instruction/Work_Log.md`
- 开工前四组候选集合基线输出摘要：
  - `baseline dashboard []`
  - `baseline week []`
  - `baseline todo [15, 14, 13, 12, 11, 10, 9, 8]`
  - `baseline board [15, 14, 13, 12, 11, 10, 9, 8]`
- 实现的 service 方法：
  - `ScheduleQueryService.is_todo(item)`：
    - `getattr(item, 'item_type', None) == 'todo'` 或 `getattr(item, 'type', 0) == 1` 返回 `True`。
  - `ScheduleQueryService.is_schedule(item)`：
    - 严格按周视图旧语义：`getattr(item, 'item_type', None) == 'schedule'`。
  - `ScheduleQueryService.split_schedule_and_todo(items)`：
    - 返回 `(schedules, todos)`；`todos` 用 `is_todo`，`schedules` 用 `not is_todo`。
- 每个 UI 文件替换了哪一处判断：
  - `src/ui/dashboard.py`：将内联 `is_todo` 判定替换为 `ScheduleQueryService.is_todo(s)`。
  - `src/ui/week_window.py`：将 `s.item_type == 'schedule'` 替换为 `ScheduleQueryService.is_schedule(s)`。
  - `src/ui/todo.py`：将内联 `is_todo` 判定替换为 `ScheduleQueryService.is_todo(s)`。
  - `src/ui/todo_board.py`：将 `is_todo = (item_type=='todo' or type==1)` 替换为 `is_todo = ScheduleQueryService.is_todo(s)`。
- 明确记录：未修改排序逻辑。
  - 各文件排序 key 与排序顺序保持原样，未迁移到 `schedule_sort_service.py`。
- 明确记录：未修改 Repository 日期过滤。
  - 本轮未修改 `src/repositories/`，3-2a 中的日期过滤委托保持不变。
- 修改后四组候选集合 id 是否与基线一致：
  - `after dashboard []`（一致）
  - `after week []`（一致）
  - `after todo [15, 14, 13, 12, 11, 10, 9, 8]`（一致）
  - `after board [15, 14, 13, 12, 11, 10, 9, 8]`（一致）
- `split_schedule_and_todo` 验证结果：
  - `split ok True True 67 8`
  - `sample flags [(72, False, True), (73, False, True), (74, False, True), (75, False, True), (76, False, True)]`
- 旧 `db_manager.get_schedules_for_date` 验证结果：
  - `db_manager path ok True 8`
- 静态依赖检查结果：
  - 命令：`rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_query_service.py`
  - 结果：无输出（退出码 1，符合预期）。
- UI 引用检查结果：
  - 命令：`rg -n "ScheduleQueryService|schedule_query_service|ScheduleSortService|CategoryPolicyService|src\.repositories|db_manager" ...`
  - 结果：四个 UI 文件已引入并使用 `ScheduleQueryService`；未引入 `ScheduleSortService`/`CategoryPolicyService`/`src.repositories`。
  - `db_manager` 命中均为既有取数与写回路径，未新增调用路径。
- 本轮未误动其他 service 检查：
  - `git diff --name-only -- src/services/schedule_sort_service.py` -> 无输出。
  - `git diff --name-only -- src/services/category_policy_service.py` -> 无输出。
  - `git diff --name-only -- src/services/weather_service.py` -> 无输出。
- diff 范围检查结果：
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/data` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`、`src/services/schedule_query_service.py`、`src/ui/dashboard.py`、`src/ui/week_window.py`、`src/ui/todo.py`、`src/ui/todo_board.py`（写入本日志后另含 `manage_instruction/Work_Log.md`）。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`、`M src/services/schedule_query_service.py`、`M src/ui/dashboard.py`、`M src/ui/week_window.py`、`M src/ui/todo.py`、`M src/ui/todo_board.py`（写入本日志后另含 `M manage_instruction/Work_Log.md`）。
- 未完成事项：
  - 等待顾问窗口复核并下发 3-3 小工单。
- 风险或疑点：
  - `is_schedule` 严格保持 `item_type == 'schedule'` 语义，未扩展到 `not is_todo`，避免周视图行为变更。
  - 目前仅抽取判定逻辑；排序仍分散在 UI，后续 3-3 需逐视图对齐迁移。

## 2026-05-17 第三轮 3-3a（day/week/todo 三处同构排序 key 抽取）

- 本轮任务名称：第三轮 3-3a（day/week/todo 三处同构排序 key 抽取）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 3-3a 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/services/schedule_sort_service.py`
  - `src/ui/dashboard.py`
  - `src/ui/week_window.py`
  - `src/ui/todo.py`
  - `manage_instruction/Work_Log.md`
- 开工前三组排序 id 基线输出摘要：
  - `baseline dashboard []`
  - `baseline week []`
  - `baseline todo [8, 10, 14, 15, 11, 12, 9, 13]`
- 实现的 `ScheduleSortService` 方法：
  - 实现内部同构 key：
    - `rank_pin = 0 if is_pinned else 1`
    - `rank_status = 3 if status == 1 else 1`
    - `sort_val = -sort_order`
    - key = `(rank_pin, rank_status, sort_val)`
  - 实现：
    - `sort_for_day_view(items)`
    - `sort_for_week_view(items)`
    - `sort_for_todo_list(items)`
  - 三个方法均返回新 list（`sorted(list(items), key=...)`）。
- 每个 UI 文件替换了哪一处排序：
  - `src/ui/dashboard.py`：用 `ScheduleSortService.sort_for_day_view(dashboard_schedules)` 替换本地 `sort_key + list.sort(...)`。
  - `src/ui/week_window.py`：用 `ScheduleSortService.sort_for_week_view(valid_schedules)` 替换本地 `sort_key + list.sort(...)`。
  - `src/ui/todo.py`：用 `ScheduleSortService.sort_for_todo_list(dashboard_todos)` 替换本地 `sort_key + list.sort(...)`。
- 明确记录：未修改 `todo_board.py`。
- 明确记录：未修改 `ScheduleQueryService`。
- 明确记录：未修改 Repository 日期过滤。
- 修改后三组排序 id 是否与基线一致：
  - `after dashboard []`（一致）
  - `after week []`（一致）
  - `after todo [8, 10, 14, 15, 11, 12, 9, 13]`（一致）
- service import / direct call 验证结果：
  - `sort day ok True`
  - `sort week ok True`
  - `sort todo ok True`
- 旧 `db_manager.get_schedules_for_date` 验证结果：
  - `db_manager path ok True 8`
- 静态依赖检查结果：
  - 命令：`rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_sort_service.py`
  - 结果：无输出（退出码 1，符合预期）。
- UI 引用检查结果：
  - `dashboard.py`、`week_window.py`、`todo.py` 命中 `ScheduleSortService`（符合预期）。
  - `todo_board.py` 未新增 `ScheduleSortService` 命中。
  - 未命中 `CategoryPolicyService`、`src.repositories`。
  - `ScheduleQueryService` 命中为既有 3-2b 逻辑，保持不变。
- `todo_board.py` 未改确认：
  - `git diff --name-only -- src/ui/todo_board.py` -> 无输出。
- 本轮未误动其他 service 检查：
  - `git diff --name-only -- src/services/schedule_query_service.py` -> 无输出。
  - `git diff --name-only -- src/services/category_policy_service.py` -> 无输出。
  - `git diff --name-only -- src/services/weather_service.py` -> 无输出。
- py_compile 结果：
  - `python -m py_compile src/services/schedule_sort_service.py src/ui/dashboard.py src/ui/week_window.py src/ui/todo.py` 通过（无输出）。
- diff 范围检查结果：
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/data` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`、`src/services/schedule_sort_service.py`、`src/ui/dashboard.py`、`src/ui/week_window.py`、`src/ui/todo.py`（写入本日志后另含 `manage_instruction/Work_Log.md`）。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`、`M src/services/schedule_sort_service.py`、`M src/ui/dashboard.py`、`M src/ui/week_window.py`、`M src/ui/todo.py`（写入本日志后另含 `M manage_instruction/Work_Log.md`）。
- 未完成事项：
  - 等待顾问窗口复核并下发 3-3b（todo_board 专项）工单。
- 风险或疑点：
  - 本轮仅抽取 day/week/todo 同构排序；`todo_board` 的差异化排序与写回仍待 3-3b 单独处理。

## 2026-05-17 第三轮 3-3b（todo_board 主看板渲染排序抽取）

- 本轮任务名称：第三轮 3-3b（todo_board 主看板渲染排序抽取）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 3-3b 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/services/schedule_sort_service.py`
  - `src/ui/todo_board.py`
  - `manage_instruction/Work_Log.md`
- 开工前 todo_board 主排序 id 基线输出摘要：
  - `baseline todo_board [8, 10, 14, 15, 11, 12, 9, 13]`
- 实现的 `ScheduleSortService.sort_for_todo_board` 方法：
  - 返回 `sorted(list(items), key=(rank_pin, sort_val))` 新 list。
  - key 语义保持旧逻辑：
    - `rank_pin = 0 if is_pinned else 1`
    - `sort_val = -sort_order`
- `todo_board.py` 替换了哪一处排序：
  - 主渲染路径中 `todos` 生成后原内联 `sort_key + todos.sort(key=sort_key)` 替换为：
  - `todos = ScheduleSortService.sort_for_todo_board(todos)`
- 明确记录：未修改 `_sort_by_priority`。
- 明确记录：未修改 priority 排序和 `sort_order` 写回逻辑。
- 明确记录：未修改 dashboard/week/todo。
- 明确记录：未修改 `ScheduleQueryService`。
- 修改后 todo_board 主排序 id 是否与基线一致：
  - `after todo_board [8, 10, 14, 15, 11, 12, 9, 13]`（一致）。
- `sort_for_todo_board` 是否返回新 list 且不原地修改输入：
  - `returns list True`
  - `new object True`
  - `input unchanged True`
- service import / direct call 验证结果：
  - `day True` / `week True` / `todo True` / `board True`
- 旧 `db_manager.get_schedules_for_date` 验证结果：
  - `db_manager path ok True 8`
- 静态依赖检查结果：
  - 命令：`rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_sort_service.py`
  - 结果：无输出（退出码 1，符合预期）。
- `todo_board.py` 引用检查结果：
  - 命中 `ScheduleSortService`：`src/ui/todo_board.py:12`、`1318`。
  - 未命中 `CategoryPolicyService` 与 `src.repositories`。
- `_sort_by_priority` 检查结果：
  - `def _sort_by_priority` 及其 priority 排序、`update_schedule_fields(sort_order=...)` 仍在原位置，未参与本轮改动。
- 本轮未误动其他 UI / service：
  - `git diff --name-only -- src/ui/dashboard.py` -> 无输出。
  - `git diff --name-only -- src/ui/week_window.py` -> 无输出。
  - `git diff --name-only -- src/ui/todo.py` -> 无输出。
  - `git diff --name-only -- src/services/schedule_query_service.py` -> 无输出。
  - `git diff --name-only -- src/services/category_policy_service.py` -> 无输出。
  - `git diff --name-only -- src/services/weather_service.py` -> 无输出。
- py_compile 结果：
  - `python -m py_compile src/services/schedule_sort_service.py src/ui/todo_board.py` 通过（无输出）。
- diff 范围检查结果：
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/data` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`、`src/services/schedule_sort_service.py`、`src/ui/todo_board.py`（写入本日志后另含 `manage_instruction/Work_Log.md`）。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`、`M src/services/schedule_sort_service.py`、`M src/ui/todo_board.py`（写入本日志后另含 `M manage_instruction/Work_Log.md`）。
- 未完成事项：
  - 等待顾问窗口复核并下发 3-4 工单。
- 风险或疑点：
  - 本轮只抽主看板渲染排序；`_sort_by_priority` 与拖拽写回逻辑仍为历史实现，后续若要统一需单独工单。

## 2026-05-17 第三轮 3-4a（CategoryPolicyService 分类状态判断抽取）

- 本轮任务名称：第三轮 3-4a（CategoryPolicyService 分类状态判断抽取）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 3-4a 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/services/category_policy_service.py`
  - `src/repositories/category_repository.py`
  - `manage_instruction/Work_Log.md`
- 开工前分类状态基线输出摘要：
  - `baseline categories [(7,'测试','historical'), (1,'尚书令','active'), (2,'中书监','active'), (4,'司徒','active'), (6,'太尉','active'), (5,'司空','active'), (3,'散骑常侍','empty')]`
  - `baseline missing empty`
- 实现的 `CategoryPolicyService.evaluate_status` 逻辑：
  - 输入 iterable 先转 list；空列表返回 `CategoryStatus.EMPTY`。
  - `now` 默认 `datetime.datetime.now()`，允许外部传入。
  - 遍历每条 schedule：
    - `is_completed = (status == 1)`（`getattr` 读取 `status`）。
    - `is_expired = bool(end_time and end_time < now and not is_completed)`（`getattr` 读取 `end_time`）。
    - 命中 `not is_completed and not is_expired` 立即返回 `CategoryStatus.ACTIVE`。
  - 遍历结束返回 `CategoryStatus.HISTORICAL`。
- `CategoryRepository.check_category_status` 委托方式：
  - Repository 仍执行数据库查询：`self._schedule_model.select().where(...)`。
  - 将查询结果 list 传入 `CategoryPolicyService.evaluate_status(schedules)`。
  - 对外返回旧字符串语义：`status.value`（兼容分支保留 `str(status)` 兜底）。
- 明确记录：Repository 仍负责数据库查询。
- 明确记录：service 不访问数据库。
- 明确记录：未修改 `soft_delete_category` / `hard_delete_category`。
- 明确记录：未修改 UI 删除分支。
- 修改后分类状态是否与基线一致：
  - `after categories` 与 baseline 一致；`after missing empty`。
- 不存在 id 返回语义是否仍为 `"empty"`：
  - 通过，`db_manager.check_category_status(-999999) == 'empty'`。
- service direct call 验证结果：
  - `rows` 返回 `CategoryStatus` 枚举值，且均在 `EMPTY/ACTIVE/HISTORICAL` 允许集合内。
- `db_manager.check_category_status` 返回字符串验证结果：
  - 输出示例：`['historical', 'active', 'active', 'active', 'active', 'empty']`。
  - 全部为 `str`，且仅在 `{empty, active, historical}` 集合内。
- 样本覆盖情况：active / historical / empty / missing
  - `status coverage {'historical':[7], 'active':[1,2,4,6,5], 'empty':[3], 'missing':[-999999]}`
- 静态依赖检查结果：
  - 命令：`rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|CategoryRepository|ScheduleRepository" src/services/category_policy_service.py`
  - 结果：无输出（退出码 1，符合预期）。
- py_compile 结果：
  - `python -m py_compile src/services/category_policy_service.py src/repositories/category_repository.py` 通过（无输出）。
- diff 范围检查结果：
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- src/data` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only -- src/services/schedule_query_service.py` -> 无输出。
  - `git diff --name-only -- src/services/schedule_sort_service.py` -> 无输出。
  - `git diff --name-only -- src/services/weather_service.py` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`、`src/repositories/category_repository.py`、`src/services/category_policy_service.py`（写入本日志后另含 `manage_instruction/Work_Log.md`）。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`、`M src/repositories/category_repository.py`、`M src/services/category_policy_service.py`（写入本日志后另含 `M manage_instruction/Work_Log.md`）。
- 未完成事项：
  - 等待顾问窗口复核，并下发 3-4b（删除策略抽取）工单。
- 风险或疑点：
  - 当前数据样本已覆盖 `active/historical/empty/missing`，但并未人为构造边界时间样本；`end_time == now` 的语义沿用旧逻辑（不视为过期）。

## 2026-05-17 第三轮 3-4b（CategoryPolicyService 分类删除动作决策抽取）

- 本轮任务名称：第三轮 3-4b（CategoryPolicyService 分类删除动作决策抽取）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 3-4b 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/services/category_policy_service.py`
  - `src/ui/list_picker.py`
  - `src/ui/todo_board.py`
  - `manage_instruction/Work_Log.md`
- 开工前动作映射基线：
  - `baseline actions {'active': 'block', 'historical': 'soft_delete', 'empty': 'hard_delete'}`
- 实现的 `CategoryPolicyService.choose_delete_action` 逻辑：
  - 输入支持 `CategoryStatus` 或旧字符串状态。
  - 映射：
    - `active` -> `CategoryDeleteAction.BLOCK`
    - `historical` -> `CategoryDeleteAction.SOFT_DELETE`
    - `empty` -> `CategoryDeleteAction.HARD_DELETE`
- 未知状态兜底策略：
  - 返回 `CategoryDeleteAction.BLOCK`，避免异常中断 UI 删除流程。
- `list_picker.py` 替换了哪一处分支判断：
  - `_delete_category_logic` 中 `status == 'active'/'historical'/else` 改为 `action == CategoryDeleteAction.BLOCK/SOFT_DELETE/else(HARD_DELETE)`。
- `todo_board.py` 替换了哪两处分支判断：
  - `_delete_category`：状态字符串分支替换为 `CategoryDeleteAction` 分支。
  - `_handle_folder_delete`：状态字符串分支替换为 `CategoryDeleteAction` 分支。
- 明确记录：未修改 Repository。
- 明确记录：未修改 `soft_delete_category` / `hard_delete_category`。
- 明确记录：未修改 `db_manager` API。
- 明确记录：未改 UI 文案、布局、交互流程。
- 修改后 active / historical / empty 动作映射是否与基线一致：
  - 一致。
  - `actual {'active': 'block', 'historical': 'soft_delete', 'empty': 'hard_delete'}`
  - `enum_actual {'active': 'block', 'historical': 'soft_delete', 'empty': 'hard_delete'}`
- 当前分类状态到动作映射验证结果：
  - `rows [(7,'测试','historical','soft_delete'), (1,'尚书令','active','block'), (2,'中书监','active','block'), (4,'司徒','active','block'), (6,'太尉','active','block'), (5,'司空','active','block'), (3,'散骑常侍','empty','hard_delete'), (-999999,'missing','empty','hard_delete')]`
- `db_manager.check_category_status` 返回字符串验证结果：
  - 输出 `values ['historical', 'active', 'active', 'active', 'active', 'empty']`。
  - 全部为 `str`，且均在 `{'empty','active','historical'}`。
- 静态依赖检查结果：
  - 命令：`rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|CategoryRepository|ScheduleRepository" src/services/category_policy_service.py`
  - 结果：无输出（退出码 1，符合预期）。
- UI 引用检查结果：
  - `list_picker.py`、`todo_board.py` 命中 `CategoryPolicyService` / `CategoryDeleteAction`（符合预期）。
  - 未命中 `src.repositories`。
  - 未新增 `CategoryStatus` UI 直接依赖。
- py_compile 结果：
  - `python -m py_compile src/services/category_policy_service.py src/ui/list_picker.py src/ui/todo_board.py` 通过（无输出）。
- diff 范围检查结果：
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/data` -> 无输出。
  - `git diff --name-only -- src/ui/dashboard.py` -> 无输出。
  - `git diff --name-only -- src/ui/week_window.py` -> 无输出。
  - `git diff --name-only -- src/ui/todo.py` -> 无输出。
  - `git diff --name-only -- src/services/schedule_query_service.py` -> 无输出。
  - `git diff --name-only -- src/services/schedule_sort_service.py` -> 无输出。
  - `git diff --name-only -- src/services/weather_service.py` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`、`src/services/category_policy_service.py`、`src/ui/list_picker.py`、`src/ui/todo_board.py`（写入本日志后另含 `manage_instruction/Work_Log.md`）。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`、`M src/services/category_policy_service.py`、`M src/ui/list_picker.py`、`M src/ui/todo_board.py`（写入本日志后另含 `M manage_instruction/Work_Log.md`）。
- 未完成事项：
  - 等待顾问窗口复核并下发下一小工单。
- 风险或疑点：
  - 未知状态目前统一拦截（BLOCK）是保守策略；若后续引入新状态，需要同步更新策略映射与产品文案。

## 2026-05-17 第三轮 3-5（四象限纯逻辑评估与最小服务准备）

- 本轮任务名称：第三轮 3-5（四象限纯逻辑评估与最小服务准备）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 3-5 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 已读取的关键文件：
  - `manage_instruction/Work_Instruction.md`
  - `manage_instruction/Work_Log.md`
  - `src/data/models.py`
  - `src/ui/dashboard.py`
  - `src/ui/week_window.py`
  - `src/ui/month_window.py`
  - `src/ui/main_window.py`
  - `src/ui/todo_board.py`
  - `src/services/` 文件清单与全局 `matrix/quadrant/四象限` 搜索结果
- 当前四象限入口位置：
  - `src/ui/dashboard.py:76`：视图按钮 `"priority": "四象限"`。
  - `src/ui/week_window.py:437`：视图按钮 `"priority": "四象限"`。
  - `src/ui/month_window.py:472`：视图按钮 `"priority": "象限"`。
  - `src/ui/main_window.py:632-634`：`view_name == "priority"` 时仅 toast `准备切换至：四象限视图`。
- 当前四象限相关文案：
  - 仅见入口名称/提示文案（“四象限/象限/准备切换至四象限视图”）。
  - 未发现可执行的象限判定规则文案（例如“重要且紧急”四象限分层规则）。
- 当前 `priority` 使用位置和语义判断：
  - `src/data/models.py:33` 字段注释为 `紧急性`。
  - `src/ui/todo_board.py:1094-1097`、`1166` 文案为 `低/中/高重要性`。
  - `src/ui/todo_board.py:1764-1785` 存在“一键按重要性排序”，以 `priority` 高到低排序后写回 `sort_order`。
  - `src/ui/dashboard.py:330`、`src/ui/week_window.py:81` 用 `priority` 显示红黄绿点，不体现“四象限分类”。
  - 结论：`priority` 在模型与 UI 文案间存在“紧急性/重要性”语义不一致，当前更像单轴优先级，不是稳定四象限双轴规则。
- 当前字段可用性：
  - `priority`：存在（`Schedule.priority`），取值用于颜色与排序；语义不一致（紧急性 vs 重要性）。
  - `start_time`：存在；用于日期范围过滤与展示，不是稳定“紧急性”定义。
  - `end_time`：存在；用于日期过滤/过期判断，不等价于“紧急性”阈值规则。
  - `status`：存在；用于完成/删除状态过滤，不代表重要或紧急。
  - `created_at`：存在；用于同优先级下排序辅助，不代表象限维度。
  - `sort_order`：存在；用于展示顺序权重及拖拽/重排结果，不代表象限维度。
- 是否存在稳定四象限分类规则：
  - 不存在。
  - 原因：
    - 未发现“重要/不重要”与“紧急/不紧急”双轴判定标准。
    - `priority` 仅单轴，且语义在不同位置不一致。
    - `start_time/end_time` 当前用于日期过滤，不足以单独稳定定义“紧急性”。
    - 现有 UI 仅入口占位与提示，未形成可复用业务规则。
- 结论与执行决策：
  - 不创建 `src/services/matrix_classification_service.py`。
  - 不接四象限 UI。
  - 不实现新功能。
  - 规则缺口留待后续轮次先明确产品/业务规则后再实现。
- diff 范围检查结果：
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- src/data` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/services/schedule_query_service.py` -> 无输出。
  - `git diff --name-only -- src/services/schedule_sort_service.py` -> 无输出。
  - `git diff --name-only -- src/services/category_policy_service.py` -> 无输出。
  - `git diff --name-only -- src/services/weather_service.py` -> 无输出。
  - `git diff --name-only -- src/services/__init__.py` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`（写入本日志后另含 `manage_instruction/Work_Log.md`）。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`（写入本日志后另含 `M manage_instruction/Work_Log.md`）。
- 未完成事项：
  - 需要顾问/决策窗口先给出四象限稳定规则合同（双轴定义、阈值、边界样例）后再进入实现工单。
- 风险或疑点：
  - 在未统一 `priority` 语义前直接实现四象限服务，会把当前语义冲突固化为错误行为。
  - 目前 `end_time` 主要用于日期过滤与过期判断，若直接映射“紧急性”可能导致大量误分。

## 2026-05-17 第三轮 3-6（第三轮整体验收与归档准备）

- 本轮任务名称：第三轮 3-6（第三轮整体验收与归档准备）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 3-6 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 第三轮完成项汇总：
  - `3-0`：静态审查与旧逻辑定位完成。
  - `3-1`：`ScheduleQueryService`/`ScheduleSortService`/`CategoryPolicyService` 服务边界建立完成。
  - `3-2a`：日期过滤逻辑抽取到 `ScheduleQueryService.filter_for_date` 完成。
  - `3-2b`：日程/待办判定与 `split_schedule_and_todo` 抽取完成。
  - `3-3a`：day/week/todo 同构排序抽取完成。
  - `3-3b`：todo_board 主看板渲染排序抽取完成（不含 `_sort_by_priority`）。
  - `3-4a`：分类状态判断抽取完成。
  - `3-4b`：分类删除动作决策抽取完成。
  - `3-5`：四象限规则评估完成，确认暂不创建 matrix service。
- service import 验证结果：
  - 命令：`from src.services.schedule_query_service import ScheduleQueryService; from src.services.schedule_sort_service import ScheduleSortService; from src.services.category_policy_service import CategoryPolicyService, CategoryStatus, CategoryDeleteAction`
  - 输出：`service imports ok`。
- service 静态依赖检查结果：
  - 命令：`rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_query_service.py src/services/schedule_sort_service.py src/services/category_policy_service.py`
  - 结果：无输出（退出码 1，符合预期，视为通过）。
- 旧 `db_manager` 路径验证结果：
  - `all schedules 75`
  - `today schedules 8`
  - `active categories 7`
  - `missing category status empty`
  - 返回类型断言通过（list/list/list + 状态字符串集合）。
- UI import 验证结果：
  - 命令：`importlib.import_module` 导入 `src.ui.dashboard/week_window/todo/todo_board/list_picker`。
  - 输出：`ui imports ok ['src.ui.dashboard', 'src.ui.week_window', 'src.ui.todo', 'src.ui.todo_board', 'src.ui.list_picker']`。
- 日期过滤验证结果：
  - 输出：`date filter rows [('2026-05-16',[8,9,10,11,12,13,14,15]), ('2026-05-17',[8,9,10,11,12,13,14,15]), ('2026-05-18',[8,9,10,11,12,13,14,15])]`。
  - 结论：路径可用，返回结构正确。
- 日程/待办判定验证结果：
  - 输出：`split 67 8`。
  - 输出样例：`sample [(72, False, True), (73, False, True), (74, False, True), (75, False, True), (76, False, True)]`。
  - 结论：`is_todo/is_schedule/split_schedule_and_todo` 可用。
- 排序关键结果验证：
  - `dashboard sorted []`
  - `week sorted []`
  - `todo sorted [8, 10, 14, 15, 11, 12, 9, 13]`
  - `board sorted [8, 10, 14, 15, 11, 12, 9, 13]`
  - 结论：与第三轮既有日志基线一致。
- 排序方法是否返回新 list 且不原地修改输入：
  - `sort list behavior [('sort_for_day_view', True, True, True), ('sort_for_week_view', True, True, True), ('sort_for_todo_list', True, True, True), ('sort_for_todo_board', True, True, True)]`
  - 结论：四个排序方法均返回新 list，且不改输入列表。
- 分类状态和删除动作映射验证结果：
  - 输出：`category rows [(7,'测试','historical','soft_delete'), (1,'尚书令','active','block'), (2,'中书监','active','block'), (4,'司徒','active','block'), (6,'太尉','active','block'), (5,'司空','active','block'), (3,'散骑常侍','empty','hard_delete'), (-999999,'missing','empty','hard_delete')]`。
  - 结论：`active->block`、`historical->soft_delete`、`empty->hard_delete` 映射正确。
- `db_manager.check_category_status` 返回字符串验证结果：
  - 输出：`category status values ['historical', 'active', 'active', 'active', 'active', 'empty']`。
  - 结论：仍为字符串且仅在 `{empty, active, historical}`。
- `matrix_classification_service.py` 是否未创建：
  - `Test-Path src\services\matrix_classification_service.py` -> `False`。
  - `rg -n "matrix_classification_service|MatrixClassificationService" src manage_instruction` 仅命中管理文档，不命中 `src/` 实际实现。
- 四象限规则缺口是否已记录：
  - 已记录于 3-5：规则不足，暂不创建 service，不接 UI，不实现新功能。
- py_compile 结果：
  - `python -m py_compile src/services/schedule_query_service.py src/services/schedule_sort_service.py src/services/category_policy_service.py src/repositories/schedule_repository.py src/repositories/category_repository.py src/ui/dashboard.py src/ui/week_window.py src/ui/todo.py src/ui/todo_board.py src/ui/list_picker.py` 通过（无输出）。
- diff 范围检查结果：
  - `git diff --name-only -- src` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`（写入本日志后另含 `manage_instruction/Work_Log.md`）。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`（写入本日志后另含 `M manage_instruction/Work_Log.md`）。
- 第三轮是否可归档：
  - 可归档。
  - 依据：第三轮 3-0~3-5 目标均完成，3-6 复核通过，且本轮确认 `src`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。
- 未完成事项：
  - 等待顾问窗口复核 3-6 记录并给出归档/下轮（第四轮）指令。
- 风险或疑点：
  - 四象限功能仍无稳定规则合同，下一轮若推进实现，需先统一 `priority` 语义与“重要/紧急”双轴判定标准。
---

## 第四轮日志归档（2026-05-17 至 2026-05-18）

归档结论：第四轮 4-0 ~ 4-9 已完成并通过整体验收，可进入第五轮提醒服务阶段合同/规划。

# Work Log

本文件只记录当前阶段/当前轮次的执行日志。

历史日志已归档到 `manage_instruction/History_Log.md`。

## 当前状态

第一轮：基建 + repository + db_manager 兼容委托，已完成并归档。

第二轮：Data 层整理与模型拆分，已完成并归档。

第三轮：纯业务查询与排序服务，已完成并归档。

第四轮（日程写入与重复规则服务）已启动。

当前已完成 4-9（第四轮整体验收与归档准备），建议归档第四轮并进入第五轮提醒服务阶段合同/规划。

## 当前轮次注意事项

- 4-9 已完成第四轮整体验收与归档准备；关键写入路径回归通过，第四轮可归档。
- 第四轮小工单已完成至 4-9，当前进入归档收口阶段。
- 执行窗口不得沿用第三轮 3-6 或第三轮任一提示词继续执行。
- 执行窗口不得在未收到后续正式提示词前自行开始第五轮实现改造。

## 2026-05-17 第四轮 4-0（静态审查与只读基线定位）

- 本轮任务名称：第四轮 4-0（静态审查与只读基线定位）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 4-0 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 已读取的关键文件：
  - `manage_instruction/Work_Instruction.md`
  - `manage_instruction/Work_Log.md`
  - `src/data/database.py`
  - `src/data/models.py`
  - `src/ui/add_view.py`
  - `src/ui/add_view_week.py`
  - `src/ui/main_window.py`
  - `src/ui/week_window.py`
  - `src/ui/todo_board.py`
  - `src/ui/schedule_detail_pop.py`
  - `src/ui/month_window.py`
  - `src/services/` 文件清单（核对第四轮 service 是否已存在）
- `_add_months` 当前位置和行为摘要：
  - 位置：`src/data/database.py:85`。
  - 行为：按 `year/month/day` 重新计算目标日期；使用目标月最大天数兜底（如 1 月 31 日 +1 月落到 2 月最后一天）；返回 `sourcedate.replace(...)`。
  - 目前仅被 `add_schedule` 与 `update_schedule_with_repeat` 的“每月”分支调用。
- `add_schedule` 当前位置和行为摘要：
  - 位置：`src/data/database.py:97`。
  - 非重复路径：`rule in ('none','无','不重复','')` 时直接 `Schedule.create(**data)`，成功 `True`，异常 `False`。
  - 重复路径：
    - 先创建 `group_id = uuid4` 并写入当前 data。
    - `schedules_to_insert` 先放当前这条，再生成未来条目。
    - 生成数量控制：`每天=365`、`每周=52`、`每月=12`（加上当前条，总数分别 366/53/13）。
    - 时间偏移：`每天/每周` 用 `timedelta`；`每月` 用 `_add_months`。
    - 批量写入：`with db.atomic()` + `Schedule.insert_many(batch)`，`batch_size=100`。
- `update_schedule_with_repeat` 当前位置和行为摘要：
  - 位置：`src/data/database.py:160`。
  - 输入：`(schedule_id, new_data, update_future=False)`。
  - 分支语义：
    - `update_future=False`：只更新当前条；若旧条有 `group_id`，先把 `new_data['group_id']=None`，实现脱离循环。
    - `update_future=True`：影响当前及未来。
      - 若旧条无 `group_id` 且新规则是重复，则新建 `group_id`；否则沿用旧 `group_id`。
      - 当前条先更新；若新规则非重复则当前条 `group_id=None`。
      - 若旧条原本属于组：先删除“未来同组实例”（按 `start_time` 或 `end_time` 或 `id` 回退分支）。
      - 若新规则是重复：重建未来实例（不含当前条，数量分别 365/52/12）。
  - 返回：成功 `True`，异常 `False`。
- 当前非重复规则值清单：
  - `none`
  - `无`
  - `不重复`
  - `''`（空字符串）
  - 证据位置：`src/data/database.py`（`add_schedule` 与 `update_schedule_with_repeat` 分支条件），以及 UI 判定分支。
- 当前重复规则值清单：
  - `每天`
  - `每周`
  - `每月`
  - 证据位置：`src/data/database.py` 生成分支；`src/ui/add_view.py`、`src/ui/add_view_week.py`、`src/ui/schedule_detail_pop.py` 下拉选项。
- `每天 / 每周 / 每月` 生成数量：
  - `add_schedule`：未来生成 365/52/12，加当前条总计 366/53/13。
  - `update_schedule_with_repeat(update_future=True)`：未来重建 365/52/12（当前条已单独 update）。
- `每年 / yearly / daily / weekly / monthly` 是否存在旧生成逻辑：
  - 在 `src` 范围内未检出上述规则实现（`rg -n "\\b(daily|weekly|monthly|yearly)\\b|每年" src` 无输出）。
  - 结论：当前旧生成逻辑仅覆盖中文 `每天/每周/每月`。
- `group_id` 字段和行为位置：
  - 字段：`src/data/models.py:40`，`Schedule.group_id = CharField(null=True, index=True)`。
  - 迁移：`src/data/database.py:27-33` 含 group_id 字段迁移逻辑。
  - 行为：
    - 新建重复组时分配 `uuid`。
    - `update_future=False` 下脱组（`group_id=None`）。
    - `update_future=True` 下沿用或创建组，并删除/重建未来实例。
    - UI 存在内存态同步（见下文）。
- `parent_id` 是否存在：
  - `src` 全局未命中 `parent_id`（`rg -n "parent_id" src` 无输出）。
  - `Schedule` 模型无 `parent_id` 字段。
- `update_future` 调用位置和分支语义：
  - 数据层分支：`src/data/database.py:167`（仅当前）与 `:173`（影响未来）。
  - UI 调用点：
    - `src/ui/main_window.py:323/410/476` 闭包 `_do_update(update_future)` -> `db_manager.update_schedule_with_repeat(...)`。
    - `src/ui/week_window.py:819/867/912` 同结构。
    - `src/ui/todo_board.py:1624` 同结构。
    - `src/ui/schedule_detail_pop.py:573-601` 根据弹窗选择与规则切换计算 `update_future` 后调用。
  - UI 通用拦截器：`_check_repeat_and_execute`（main/week/todo_board）在“重复日程”提示框里把“修改所有”映射 `True`、“仅修改本次”映射 `False`。
- UI 中 `group_id` 内存态同步位置：
  - `editing_schedule.group_id = None`：
    - `src/ui/main_window.py:331/419/483`
    - `src/ui/week_window.py:827/876/919`
    - `src/ui/todo_board.py:1632`
  - `p.data.group_id = None`：`src/ui/todo_board.py:1644`
  - `dragged_item.group_id = None`：`src/ui/week_window.py:1300`
  - `group_id=None` 直接写库参数：`src/ui/week_window.py:1309`
- 事务和批量插入位置：
  - `add_schedule`：`with db.atomic()` + `insert_many` 分批（`src/data/database.py`）。
  - `update_schedule_with_repeat`：仅“未来重建插入”段使用 `with db.atomic()` + `insert_many` 分批；当前条 update 与旧未来 delete 不在同一显式原子块中。
- 未来实例删除/重建逻辑位置：
  - 删除旧未来：`src/data/database.py:191-206`，按 `start_time` / `end_time` / `id` 分支删除同组未来条目。
  - 重建新未来：`src/data/database.py:211-253`，按新规则生成并批量插入。
- 后续建议拆分小工单：
  - `4-1`：仅抽 `_add_months` 与重复日期偏移纯逻辑（不写库）。
  - `4-2`：仅抽“重复计划生成器”（输出待插入数据，不落库）。
  - `4-3`：`add_schedule` 非重复路径委托。
  - `4-4`：`add_schedule` 重复路径委托（保持 366/53/13）。
  - `4-5`：`update_future=False` 路径委托（保持脱组语义）。
  - `4-6`：非组改重复且影响未来路径。
  - `4-7`：已有组的未来删除/重建路径（建议先 `4-7a` 纯基线验证，再 `4-7b` 改造）。
  - `4-8`：取消重复路径（`none/无/不重复/''`）。
- diff 范围检查结果：
  - `git diff --name-only -- src` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`（写入本日志后另含 `manage_instruction/Work_Log.md`）。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`（写入本日志后另含 `M manage_instruction/Work_Log.md`）。
- 未完成事项：
  - 待顾问窗口确认 4-1 拆单边界（是否先只抽日期偏移，还是先做重复计划生成）。
- 风险或疑点：
  - 当前 `update_schedule_with_repeat` 的“更新当前 + 删除旧未来 + 重建新未来”不在同一大事务块，后续拆分时需谨慎保持失败回滚语义。
  - UI 已存在多处 `group_id` 内存态同步，后续若改数据层行为，需同步核对这些 UI 假设是否仍成立。
  - 当前无 `parent_id`；后续工单不得隐式引入“父子实例”新语义。

## 2026-05-18 第四轮 4-1（重复日期计算纯逻辑抽取）

- 本轮任务名称：第四轮 4-1（重复日期计算纯逻辑抽取）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 4-1 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/services/schedule_repeat_service.py`（新增）
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- service 方法清单与输入/输出说明：
  - `ScheduleRepeatService.add_months(sourcedate, months)`：输入 datetime/None 与整月偏移；输出偏移后的 datetime/None；保持月末与闰年兼容。
  - `ScheduleRepeatService.shift_datetime(value, rule, step)`：输入 datetime/None、规则（仅 `每天/每周/每月`）与步长；输出偏移后的 datetime/None。
  - `ScheduleRepeatService.shift_triplet(start_time, end_time, reminder_time, rule, step)`：输入三元时间与规则步长；输出偏移后三元组。
- `database.py` 委托点位置：
  - `_add_months` 改为委托 `ScheduleRepeatService.add_months`。
  - `add_schedule` 的未来偏移段改为调用 `ScheduleRepeatService.shift_triplet(...)`。
  - `update_schedule_with_repeat` 的未来重建偏移段改为调用 `ScheduleRepeatService.shift_triplet(...)`。
- 明确记录：未改写入流程、未改事务边界、未改生成数量。
  - `add_schedule` 仍保持 `loop_count: 每天365/每周52/每月12`，仍用 `with db.atomic()` + `insert_many` 分批写入。
  - `update_schedule_with_repeat` 仍保持旧分支结构（仅当前/影响未来）、旧删除旧未来与重建未来流程，未来重建仍保持 `loop_count: 每天365/每周52/每月12`。
  - 未改 `group_id` 语义。
- 月末与闰年一致性验证结果：
  - 命令（legacy 对照）通过，`month rows` 全部 `True`。
  - 样例包含：
    - `2023-01-31 +1月 -> 2023-02-28`
    - `2024-01-31 +1月 -> 2024-02-29`
    - `2024-02-29 +12月 -> 2025-02-28`
- `start_time/end_time/reminder_time` 偏移一致性验证结果：
  - 输出：
    - `每天 1 -> 2026-02-01 09:00 / 10:00 / 2026-01-31 09:00`
    - `每周 2 -> 2026-02-14 09:00 / 10:00 / 2026-02-13 09:00`
    - `每月 1 -> 2026-02-28 09:00 / 10:00 / 2026-02-28 09:00`
- service import 验证结果：
  - 输出：`repeat service import ok <class 'src.services.schedule_repeat_service.ScheduleRepeatService'>`。
- service 静态依赖检查结果：
  - 命令：`rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_repeat_service.py`
  - 结果：无输出（退出码 1，符合预期）。
- 未新增 `每年/yearly/daily/weekly/monthly` 行为说明：
  - 命令：`rg -n "每年|yearly|daily|weekly|monthly" src/services/schedule_repeat_service.py src/data/database.py`
  - 结果：无输出（退出码 1）。
  - 结论：未引入英文规则分支，未新增 `每年/yearly` 行为。
- py_compile 结果：
  - `python -m py_compile src/services/schedule_repeat_service.py src/data/database.py` 通过（无输出）。
- diff 范围检查结果：
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`、`src/data/database.py`、`src/services/schedule_repeat_service.py`（写入本日志后另含 `manage_instruction/Work_Log.md`）。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`、`M src/data/database.py`、`?? src/services/schedule_repeat_service.py`（写入本日志后另含 `M manage_instruction/Work_Log.md`）。
- 未完成事项：
  - 等待顾问窗口复核并下发 4-2（重复规则待插入数据计划服务）或其他后续小工单。
- 风险或疑点：
  - 当前 `shift_datetime` 对未知规则返回原值仅作防御兜底；数据库层仍只在 `每天/每周/每月` 分支调用，未改变现有规则面。
  - `update_schedule_with_repeat` 仍保留原有“更新/删除/重建”事务边界现状，后续拆分时需继续保持行为一致。

## 2026-05-18 第四轮 4-2（重复规则待插入数据计划服务）

- 本轮任务名称：第四轮 4-2（重复规则待插入数据计划服务）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 4-2 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/services/schedule_repeat_service.py`
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 新增/修改的 service 方法清单：
  - `is_non_repeat_rule(rule)`：识别 `none / 无 / 不重复 / ''`。
  - `get_repeat_count(rule)`：返回 `每天=365`、`每周=52`、`每月=12`，其他为 `0`。
  - `build_repeat_insert_plan(base_data, rule, group_id, include_base=True)`：生成待插入数据计划（纯逻辑）。
  - 保留并复用 `add_months` / `shift_datetime` / `shift_triplet`。
- `add_schedule` 委托生成计划的位置：
  - `src/data/database.py` 在重复路径中以：
  - `ScheduleRepeatService.build_repeat_insert_plan(data, rule, group_id, include_base=True)`
  - 取代原手工循环组装 `schedules_to_insert`。
- `update_schedule_with_repeat` 委托生成计划的位置：
  - `src/data/database.py` 在“重建新的未来”路径中以：
  - `ScheduleRepeatService.build_repeat_insert_plan(base_data, new_rule, group_id, include_base=False)`
  - 取代原手工循环组装未来项列表。
- 明确记录：未改事务边界。
  - `add_schedule` 仍在 `database.py` 中 `with db.atomic()` 执行 `insert_many`。
  - `update_schedule_with_repeat` 未来重建段仍在 `database.py` 中 `with db.atomic()` 执行 `insert_many`。
- 明确记录：未改批量插入流程。
  - 两处仍使用 `batch_size=100` + 分批 `insert_many`。
- 明确记录：未改返回语义。
  - `add_schedule` 与 `update_schedule_with_repeat` 仍保持成功 `True`、异常 `False`。
- 明确记录：未写数据库。
  - 本轮仅运行纯函数与静态检查命令，未调用写库路径进行行为验证。
- `每天 / 每周 / 每月` 计划数量验证结果：
  - `include_base=True`：`每天=366`、`每周=53`、`每月=13`。
  - `include_base=False`：`每天=365`、`每周=52`、`每月=12`。
- `group_id` 一致性验证结果：
  - 两类计划中所有项的 `group_id` 均一致为传入值（`gid-test`）。
- `start_time/end_time/reminder_time` 偏移验证结果：
  - `每天` 首个未来项：`2026-02-01 09:00 / 10:00 / 2026-01-31 08:00`。
  - `每周` 第二个未来项：`2026-02-14 09:00 / 10:00 / 2026-02-13 08:00`。
  - `每月` 首个未来项：`2026-02-28 09:00 / 10:00 / 2026-02-28 08:00`。
- 输入 base data 是否未被原地修改：
  - 验证输出：`base unchanged True`。
- 未新增 `每年/yearly/daily/weekly/monthly` 行为说明：
  - 命令：`rg -n "每年|yearly|daily|weekly|monthly" src/services/schedule_repeat_service.py src/data/database.py`
  - 结果：无输出（退出码 1）。
  - 结论：未新增上述规则分支。
- service import 验证结果：
  - 输出：`repeat service import ok <class 'src.services.schedule_repeat_service.ScheduleRepeatService'>`。
- service 静态依赖检查结果：
  - 命令：`rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_repeat_service.py`
  - 结果：无输出（退出码 1，符合预期）。
- `database.py` 写入边界复核结果：
  - 命令：`rg -n "with db\.atomic|insert_many|batch_size|return True|return False|Schedule\.create|Schedule\.update|Schedule\.delete" src/data/database.py`
  - 结论：
    - `add_schedule` 仍由 `DatabaseManager` 执行 `Schedule.create` 或 `insert_many`。
    - `update_schedule_with_repeat` 仍由 `DatabaseManager` 执行 `update/delete/insert_many`。
    - 事务块和批量插入仍保留在 `database.py`。
    - 返回语义仍是 `True/False`。
- py_compile 结果：
  - `python -m py_compile src/services/schedule_repeat_service.py src/data/database.py` 通过（无输出）。
- diff 范围检查结果：
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`、`src/data/database.py`、`src/services/schedule_repeat_service.py`（写入本日志后另含 `manage_instruction/Work_Log.md`）。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`、`M src/data/database.py`、`M src/services/schedule_repeat_service.py`（写入本日志后另含 `M manage_instruction/Work_Log.md`）。
- 未完成事项：
  - 等待顾问窗口复核并下发 4-3（`add_schedule` 非重复路径委托）或下一小工单。
- 风险或疑点：
  - `build_repeat_insert_plan` 对“非重复/未知规则”在 `include_base=True` 下返回单条 base 计划用于兼容；当前数据库路径不会用该分支替代非重复主路径，但后续工单应继续明确该边界。
  - 写入协调仍在 `database.py`，后续若继续抽取需重点保持异常与事务语义一致。

## 2026-05-18 第四轮 4-3（add_schedule 非重复路径委托）

- 本轮任务名称：第四轮 4-3（add_schedule 非重复路径委托）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 4-3 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/services/schedule_service.py`（新增）
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 新增/修改的 service 方法：
  - `ScheduleService.create_single_schedule(schedule_model, data)`：
    - 输入：模型类与单条日程 dict。
    - 行为：复制输入数据后执行 `schedule_model.create(**payload)`。
    - 输出：成功返回 `True`（异常由调用方捕获并转 `False`）。
- add_schedule 非重复路径委托方式：
  - 在 `src/data/database.py` 的 `add_schedule` 中，`rule in ('none','无','不重复','')` 分支改为：
  - `return ScheduleService.create_single_schedule(Schedule, data)`。
  - `try/except`、失败日志 `❌ [DB] 保存失败: ...` 与 `True/False` 返回语义保持原样。
- 明确记录：重复路径未改。
  - `add_schedule` 重复路径仍调用 `ScheduleRepeatService.build_repeat_insert_plan(...)`，仍在 `database.py` 中执行 `with db.atomic()` + `insert_many`。
- 明确记录：`update_schedule_with_repeat` 未改。
  - 本轮未改其分支、删除旧未来、重建未来、事务和返回语义。
- 明确记录：未新增 `parent_id`。
  - `rg -n "每年|yearly|daily|weekly|monthly|parent_id" src/services/schedule_service.py src/data/database.py` 无输出。
- 明确记录：未新增 `每年/yearly/daily/weekly/monthly` 行为。
  - 同上命令无输出，未引入新规则分支。
- 非重复临时日程创建结果：
  - 输出：`created result True`、`matches 1`。
- 临时日程删除清理结果：
  - 输出：`deleted result True`、`remaining 0`。
- schedule.db 是否无 tracked diff：
  - `git diff --name-only -- schedule.db` -> 无输出。
- service import 验证结果：
  - 输出：`schedule service import ok <class 'src.services.schedule_service.ScheduleService'>`。
- db import 验证结果：
  - 输出：`db import ok`、`all schedules 75`。
- service 静态依赖检查结果：
  - 命令：`rg -n "QWidget|PyQt|PySide|src.ui|db_manager|src.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_service.py`
  - 结果：无输出（退出码 1，符合预期）。
- py_compile 结果：
  - `python -m py_compile src/services/schedule_service.py src/data/database.py` 通过（无输出）。
- diff 范围检查结果：
  - `git diff --name-only -- src/services/schedule_repeat_service.py` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`、`src/data/database.py`、`src/services/schedule_service.py`（写入本日志后另含 `manage_instruction/Work_Log.md`）。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`、`M src/data/database.py`、`?? src/services/schedule_service.py`（写入本日志后另含 `M manage_instruction/Work_Log.md`）。
- 未完成事项：
  - 等待顾问窗口复核并下发 4-4（add_schedule 重复路径委托）或下一小工单。
- 风险或疑点：
  - 当前 `ScheduleService.create_single_schedule` 仅覆盖最小单次创建；后续若扩展写入协调，需继续保持 `db_manager` 对外语义不变。
  - 非重复路径委托完成后，重复路径与更新路径仍在 `database.py`，后续拆分需逐步保持事务与异常行为一致。

## 2026-05-18 第四轮 4-4（add_schedule 重复路径委托收口与写入验收）

- 本轮任务名称：第四轮 4-4（add_schedule 重复路径委托收口与写入验收）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 4-4 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 是否改源码：
  - 否。重复路径已符合 4-2 委托边界，本轮原计划仅验收。
- `add_schedule` 重复路径委托复核结论：
  - 复核通过。
  - 证据：`src/data/database.py` 中 `add_schedule` 重复分支仍调用 `ScheduleRepeatService.build_repeat_insert_plan(data, rule, group_id, include_base=True)`。
- `DatabaseManager` 职责复核：
  - 仍负责 `group_id` 创建（`uuid4`）。
  - 仍负责 `with db.atomic()`、`insert_many`、`batch_size=100`。
  - 仍负责 `True/False` 返回语义。
- 明确记录：非重复路径未改。
- 明确记录：`update_schedule_with_repeat` 未改。
- 明确记录：未新增 `parent_id`。
- 明确记录：未新增 `每年/yearly/daily/weekly/monthly` 行为。

### 首次验收编码异常说明（简述）

- 首次验收失败原因：控制台 `gbk` 编码下打印 `✅/❌` 触发 `UnicodeEncodeError`，属于验收命令/输出编码问题，不是 4-4 业务逻辑失败。
- 已处理：清理临时残留后，改用逐规则 `python.exe -X utf8 -c ...` 命令完成复跑。

### 复跑结果（最终结论以本节为准）

- 复跑前检查：
  - `__tmp_4_4_repeat_` 前缀残留：`0`。
  - `git diff --name-only -- schedule.db`：无输出。
- 临时数据标题前缀：`__tmp_4_4_repeat_`（逐规则命令会追加时间戳和规则名）。
- `每天` 验证：
  - 创建结果：`True`；命中数量：`366`；`group_id` 集合大小：`1`。
  - 按 `group_id` 删除数量：`366`；删除后残留：`0`。
- `每周` 验证：
  - 创建结果：`True`；命中数量：`53`；`group_id` 集合大小：`1`。
  - 按 `group_id` 删除数量：`53`；删除后残留：`0`。
- `每月` 验证：
  - 创建结果：`True`；命中数量：`13`；`group_id` 集合大小：`1`。
  - 按 `group_id` 删除数量：`13`；删除后残留：`0`。
- 复跑后残留检查：
  - `__tmp_4_4_repeat_` 前缀残留：`0`。
- `schedule.db` 是否无 tracked diff：
  - `git diff --name-only -- schedule.db` -> 无输出。

- service import 验证结果：
  - 通过：`from src.services.schedule_repeat_service import ScheduleRepeatService` 与 `from src.data.database import db_manager` 正常。
- service 静态依赖检查结果：
  - `rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_repeat_service.py` 无输出（退出码 1，视为通过）。
- 明确记录：未新增 `parent_id` / `每年` / `yearly` / `daily` / `weekly` / `monthly` 行为：
  - `rg -n "每年|yearly|daily|weekly|monthly|parent_id" src/data/database.py src/services/schedule_repeat_service.py` 无输出（退出码 1）。
- py_compile 结果：
  - `python -m py_compile src/services/schedule_repeat_service.py src/data/database.py` 通过。

- diff 范围检查结果：
  - `git diff --name-only -- src/services/schedule_service.py` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Log.md`、`manage_instruction/Work_Task_Prompts.md`。
  - `git status --short --branch` -> `M manage_instruction/Work_Log.md`、`M manage_instruction/Work_Task_Prompts.md`。

- 未完成事项：
  - 无（4-4 验收项已按新命令复跑完成）。
- 风险或疑点：
  - 需保持后续验收脚本统一使用 UTF-8 输出，避免在 `gbk` 控制台再次因 emoji 打印中断。

## 2026-05-18 第四轮 4-5（update_future=False 仅当前修改路径）

- 本轮任务名称：第四轮 4-5（update_future=False 仅当前修改路径）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 4-5 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 是否改源码：
  - 否。本轮仅做行为基线验收。
- `update_future=False` 分支复核结论：
  - 复核通过。`src/data/database.py` 中 `if not update_future` 分支在旧条存在 `group_id` 时设置 `new_data['group_id'] = None`，随后只对当前 `schedule_id` 执行 `Schedule.update(...)` 并返回 `True`。
  - `Schedule.delete(...)`、`ScheduleRepeatService.build_repeat_insert_plan(...)`、`insert_many` 均不属于 `update_future=False` 分支。
- 是否保持：只更新当前条：
  - 是。验收中被选中条目更新成功，原组其他 52 条仍存在。
- 是否保持：当前条脱离旧 `group_id`：
  - 是。被选中条目更新后 `group_id` 为 `None`。
- 是否保持：同组其他项不修改、不删除：
  - 是。原组剩余数量为 `52`，其他组内条目未出现目标新标题。
- 明确记录：`add_schedule` 未改。
- 明确记录：`update_future=True` 路径未改。
- 明确记录：未新增 `parent_id`。
- 明确记录：未新增 `每年/yearly/daily/weekly/monthly` 行为。
- 临时数据标题前缀：
  - `__tmp_4_5_update_current_1779087848834408300`
- 临时重复组创建数量和 `group_id`：
  - 创建规则：`每周`。
  - 创建数量：`53`。
  - `group_id`：`e4a82c40-2e21-4222-b20d-bc1655f29531`。
- 被选中的中间项 id：
  - `93`（按 `start_time, id` 排序后的第 10 条，脚本使用 `rows[10]`）。
- `update_schedule_with_repeat(..., update_future=False)` 返回结果：
  - `True`。
- 当前条更新结果和脱组结果：
  - 当前条标题更新为 `__tmp_4_5_update_current_1779087848834408300_updated_current_only`。
  - 当前条 `group_id` 为 `None`。
- 原组剩余数量：
  - `52`。
- 其他组内条目是否未被修改：
  - 是。`changed others []`。
- 删除脱组当前条结果：
  - `deleted current 1`。
- 删除剩余临时组结果：
  - `deleted group 52`。
- 前缀残留检查结果：
  - 验收脚本内：`leftovers 0`。
  - 复查命令：`tmp 4-5 leftovers 0`。
- 中断与复跑说明：
  - 本轮验收因执行环境/网络不稳定，前两次执行中途无响应并由用户手动终止，第三次完整执行成功。
  - 针对中断可能造成的临时数据残留，复核了 `__tmp_4_5_update_current_` 前缀残留，结果为 `0`。
  - 顾问窗口另用独立前缀 `__tmp_4_5_consult_` 复跑同一行为验收，创建、脱组更新、删除当前条、删除剩余组、残留检查均通过。
  - `schedule.db` 最终无 tracked diff。
- `schedule.db` 是否无 tracked diff：
  - `git diff --name-only -- schedule.db` -> 无输出。
- service import / db import 验证结果：
  - 输出：`imports ok <class 'src.services.schedule_service.ScheduleService'> 75`。
- service 静态依赖检查结果：
  - `rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_service.py` -> 无输出（退出码 1，视为通过）。
- 未新增不允许规则和字段检查结果：
  - `rg -n "每年|yearly|daily|weekly|monthly|parent_id" src/data/database.py src/services/schedule_service.py` -> 无输出（退出码 1）。
- py_compile 结果：
  - `python -m py_compile src/services/schedule_service.py src/data/database.py` 通过（无输出）。
- diff 范围检查结果：
  - `git diff --name-only -- src/services/schedule_repeat_service.py` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> 写入本日志前仅 `manage_instruction/Work_Task_Prompts.md`；写入本日志后为 `manage_instruction/Work_Log.md`、`manage_instruction/Work_Task_Prompts.md`。
  - `git status --short --branch` -> 写入本日志前仅 `M manage_instruction/Work_Task_Prompts.md`；写入本日志后另含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - 无。等待顾问窗口复核并下发 4-6 或下一小工单。
- 风险或疑点：
  - 本轮未做源码委托，仅确认旧行为边界；后续如抽取 `update_future=False` 写入协调，必须继续保持当前条脱组和原组不变语义。

## 2026-05-18 第四轮 4-6（update_future=True 非组转重复路径行为验收）

- 本轮任务名称：第四轮 4-6（update_future=True 非组转重复路径行为验收）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 4-6 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 是否改源码：
  - 否。本轮仅做行为基线验收。
- `update_future=True` 非组转重复路径静态复核结论：
  - 复核通过。`src/data/database.py` 中旧条无 `group_id` 且新规则不是 `none / 无 / 不重复 / ''` 时会创建新 `group_id`。
  - 当前条会写入新 `group_id` 并先执行 `Schedule.update(...)`。
  - 旧条无 `group_id` 时不会进入旧未来实例删除分支。
  - 未来项使用 `ScheduleRepeatService.build_repeat_insert_plan(..., include_base=False)` 生成，并由 `insert_many` 写入。
- 是否保持：旧条无 `group_id` 时创建新 `group_id`：
  - 是。
- 是否保持：当前条获得新 `group_id`：
  - 是。验收中更新后 `group_id` 为 `d82ac276-cc54-4593-a5e3-7d8e983d8309`。
- 是否保持：当前条本体先更新：
  - 是。当前条标题更新为 `__tmp_4_6_single_to_repeat_1779106513128966700_repeat_weekly`，规则更新为 `每周`。
- 是否保持：未来实例生成数量为 52 个，加当前条同组共 53 条：
  - 是。同组总数 `53`。
- 是否保持：同组所有项 `group_id` 一致：
  - 是。验收断言 `all(r.group_id==gid for r in rows)` 通过。
- 是否保持：未来项时间偏移正确：
  - 是。第一个未来项 `2026-01-14 09:00:00`，第二个未来项 `2026-01-21 09:00:00`。
- 明确记录：`add_schedule` 未改。
- 明确记录：`update_future=False` 路径未改。
- 明确记录：既有重复组未来更新路径未处理。
- 明确记录：取消重复路径未处理。
- 明确记录：未新增 `parent_id`。
- 明确记录：未新增 `每年/yearly/daily/weekly/monthly` 行为。
- 临时数据标题前缀：
  - `__tmp_4_6_single_to_repeat_1779106513128966700`
- 临时单次日程 id：
  - `83`
- 更新后 `group_id`：
  - `d82ac276-cc54-4593-a5e3-7d8e983d8309`
- 同组总数：
  - `53`
- 第一个和第二个未来项时间：
  - 第一个未来项：`2026-01-14 09:00:00`
  - 第二个未来项：`2026-01-21 09:00:00`
- 删除整组结果：
  - `deleted group 53`
- 前缀残留检查结果：
  - 验收脚本内：`leftovers 0`。
  - 复查命令：`tmp 4-6 leftovers 0`。
- `schedule.db` 是否无 tracked diff：
  - `git diff --name-only -- schedule.db` -> 无输出。
- service import / db import 验证结果：
  - 输出：`imports ok <class 'src.services.schedule_repeat_service.ScheduleRepeatService'> 75`。
- service 静态依赖检查结果：
  - `rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_repeat_service.py src/services/schedule_service.py` -> 无输出（退出码 1，视为通过）。
- 未新增不允许规则和字段检查结果：
  - `rg -n "每年|yearly|daily|weekly|monthly|parent_id" src/data/database.py src/services/schedule_repeat_service.py src/services/schedule_service.py` -> 无输出（退出码 1）。
- py_compile 结果：
  - `python -m py_compile src/services/schedule_repeat_service.py src/services/schedule_service.py src/data/database.py` 通过（无输出）。
- diff 范围检查结果：
  - `git diff --name-only -- src/data/database.py` -> 无输出。
  - `git diff --name-only -- src/services/schedule_service.py` -> 无输出。
  - `git diff --name-only -- src/services/schedule_repeat_service.py` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> 写入本日志前仅 `manage_instruction/Work_Task_Prompts.md`；写入本日志后为 `manage_instruction/Work_Log.md`、`manage_instruction/Work_Task_Prompts.md`。
  - `git status --short --branch` -> 写入本日志前仅 `M manage_instruction/Work_Task_Prompts.md`；写入本日志后另含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - 无。等待顾问窗口复核并下发 4-7 或下一小工单。
- 风险或疑点：
  - 本轮只验证原本无 `group_id` 的单次日程转重复路径；已有重复组的未来更新路径、取消重复路径尚未处理。
  - 后续 4-7 涉及删除旧未来实例和重建未来实例，风险高，建议继续先做行为基线再决定是否委托改造。

## 2026-05-18 第四轮 4-7a（已有重复组 update_future=True 未来更新路径行为基线）

- 本轮任务名称：第四轮 4-7a（已有重复组 update_future=True 未来更新路径行为基线）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 4-7a 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 是否改源码：
  - 否。本轮仅做行为基线验收。
- 已有重复组 `update_future=True` 路径静态复核结论：
  - 复核通过。`old_group_id` 存在时沿用旧 `group_id`。
  - 当前条先执行 `Schedule.update(...)`。
  - 旧未来实例删除分支存在，按 `start_time` / `end_time` / `id` 回退策略执行。
  - 新未来项使用 `ScheduleRepeatService.build_repeat_insert_plan(..., include_base=False)` 生成，并由 `insert_many` 写入。
- 是否保持：沿用旧 `group_id`：
  - 是。原 `group_id` 为 `a8b84aec-e167-42ee-a452-0d73443eb8ee`，更新后当前条仍使用该值。
- 是否保持：当前条本体先更新：
  - 是。当前条标题更新为 `__tmp_4_7a_existing_group_1779107007041862900_monthly_updated`，规则更新为 `每月`。
- 是否保持：当前之前旧实例保留：
  - 是。更新前当前之前旧实例数量 `10`，更新后保留旧实例数量 `10`，标题仍为旧标题。
- 是否保持：旧未来实例删除：
  - 是。更新后旧未来实例残留检查 `old future left []`。
- 是否保持：新未来实例重建：
  - 是。新未来实例数量 `12`，标题和规则均为新值。
- 是否保持：同组最终总数为 23：
  - 是。更新后同组总数 `23`（旧保留 10 + 当前 1 + 新未来 12）。
- 是否保持：新未来项时间偏移正确：
  - 是。第一个新未来项 `2026-04-18 09:00:00`，第二个新未来项 `2026-05-18 09:00:00`。
- 明确记录：`add_schedule` 未改。
- 明确记录：`update_future=False` 路径未改。
- 明确记录：非组转重复路径未改。
- 明确记录：取消重复路径未处理。
- 明确记录：未新增 `parent_id`。
- 明确记录：未新增 `每年/yearly/daily/weekly/monthly` 行为。
- 临时数据标题前缀：
  - `__tmp_4_7a_existing_group_1779107007041862900`
- 原 `group_id`：
  - `a8b84aec-e167-42ee-a452-0d73443eb8ee`
- 被选中的中间项 id：
  - `93`
- 被选中的中间项原 `start_time`：
  - `2026-03-18 09:00:00`
- 更新前当前之前旧实例数量：
  - `10`
- 更新前当前之后旧未来实例数量：
  - `42`
- 更新后当前条标题/规则/`group_id`：
  - 标题：`__tmp_4_7a_existing_group_1779107007041862900_monthly_updated`
  - 规则：`每月`
  - `group_id`：`a8b84aec-e167-42ee-a452-0d73443eb8ee`
- 更新后保留旧实例数量：
  - `10`
- 更新后新未来实例数量：
  - `12`
- 更新后旧未来实例残留检查结果：
  - `old future left []`
- 第一个和第二个新未来项时间：
  - 第一个：`2026-04-18 09:00:00`
  - 第二个：`2026-05-18 09:00:00`
- 删除整组结果：
  - `deleted group 23`
- 前缀残留检查结果：
  - 验收脚本内：`leftovers 0`。
  - 复查命令：`tmp 4-7a leftovers 0`。
- `schedule.db` 是否无 tracked diff：
  - `git diff --name-only -- schedule.db` -> 无输出。
- service import / db import 验证结果：
  - 输出：`imports ok <class 'src.services.schedule_repeat_service.ScheduleRepeatService'> 75`。
- service 静态依赖检查结果：
  - `rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_repeat_service.py src/services/schedule_service.py` -> 无输出（退出码 1，视为通过）。
- 未新增不允许规则和字段检查结果：
  - `rg -n "每年|yearly|daily|weekly|monthly|parent_id" src/data/database.py src/services/schedule_repeat_service.py src/services/schedule_service.py` -> 无输出（退出码 1）。
- py_compile 结果：
  - `python -m py_compile src/services/schedule_repeat_service.py src/services/schedule_service.py src/data/database.py` 通过（无输出）。
- diff 范围检查结果：
  - `git diff --name-only -- src/data/database.py` -> 无输出。
  - `git diff --name-only -- src/services/schedule_service.py` -> 无输出。
  - `git diff --name-only -- src/services/schedule_repeat_service.py` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> 写入本日志前仅 `manage_instruction/Work_Task_Prompts.md`；写入本日志后为 `manage_instruction/Work_Log.md`、`manage_instruction/Work_Task_Prompts.md`。
  - `git status --short --branch` -> 写入本日志前仅 `M manage_instruction/Work_Task_Prompts.md`；写入本日志后另含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - 无。等待顾问窗口复核并下发 4-7b 或下一小工单。
- 风险或疑点：
  - 本轮仅做 4-7a 行为基线，不做源码委托改造。
  - 4-7b 若要改造，应严格保持“旧未来删除 + 新未来重建”的边界和事务/返回语义。
- 是否建议进入 4-7b：
  - 可以进入 4-7b。当前行为基线清晰，且本轮验收未发现阻塞疑点。

## 2026-05-18 第四轮 4-7b（已有重复组 update_future=True 旧未来删除策略最小委托）

- 本轮任务名称：第四轮 4-7b（已有重复组 update_future=True 旧未来删除策略最小委托）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 4-7b 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/services/schedule_service.py`
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- 新增/修改的 `ScheduleService` 方法名：
  - `ScheduleService.delete_future_schedules_for_group(schedule_model, old_group_id, schedule_id, current_schedule)`
- 委托前后边界说明：
  - 委托前：`DatabaseManager.update_schedule_with_repeat(...)` 内联执行旧未来实例删除。
  - 委托后：旧未来删除策略由 `ScheduleService.delete_future_schedules_for_group(...)` 执行；`DatabaseManager` 仍负责整体流程协调。
- 明确记录：只委托旧未来删除策略。
- 明确记录：当前条 update 未迁移。
- 明确记录：新未来重建未迁移。
- 明确记录：事务边界未改。
- 明确记录：`insert_many` / `batch_size=100` 未改。
- 明确记录：`add_schedule` 未改。
- 明确记录：`update_future=False` 路径未改。
- 明确记录：非组转重复路径未改。
- 明确记录：取消重复路径未处理。
- 明确记录：未新增 `parent_id`。
- 明确记录：未新增 `每年/yearly/daily/weekly/monthly` 行为。
- 静态定位修改点复核：
  - `ScheduleService` 中保留 `start_time / end_time / id` 三段回退删除策略。
  - `DatabaseManager.update_schedule_with_repeat` 中调用位置仍在当前条 update 之后、新未来重建之前。
  - `ScheduleRepeatService.build_repeat_insert_plan(..., include_base=False)` 未改。
  - `insert_many` / `db.atomic` / `batch_size=100` 仍在 `database.py`。

### 4-7a 等价行为回归结果

- 临时数据标题前缀：
  - `__tmp_4_7b_existing_group_1779107566893408200`
- 原 `group_id`：
  - `5aedc29b-fc54-4bc1-90fa-f8a5cc28922e`
- 被选中的中间项 id：
  - `93`
- 更新前当前之前旧实例数量：
  - `10`
- 更新前当前之后旧未来实例数量：
  - `42`
- 更新后保留旧实例数量：
  - `10`
- 更新后新未来实例数量：
  - `12`
- 更新后旧未来实例残留检查结果：
  - `old future left []`
- 同组最终总数：
  - `23`
- 第一个和第二个新未来项时间：
  - 第一个：`2026-04-18 09:00:00`
  - 第二个：`2026-05-18 09:00:00`
- 删除整组结果：
  - `deleted group 23`
- 前缀残留检查结果：
  - 验收脚本内：`leftovers 0`。
  - 复查命令：`__tmp_4_7b_existing_group_` 残留 `0`。

### 4-5 轻量回归结果

- 临时数据标题前缀：
  - `__tmp_4_7b_current_only_guard_`
- 验证结果：
  - `update_future=False` 返回 `True`。
  - 当前条脱组，更新后 `group_id is None`。
  - 原组剩余 `52` 条。
  - 删除当前条 `1` 条，删除剩余组 `52` 条。
  - 前缀残留 `0`。

- `schedule.db` 是否无 tracked diff：
  - `git diff --name-only -- schedule.db` -> 无输出。
- service import / db import 验证结果：
  - 输出：`imports ok <class 'src.services.schedule_service.ScheduleService'> <class 'src.services.schedule_repeat_service.ScheduleRepeatService'> 75`。
- service 静态依赖检查结果：
  - `rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_repeat_service.py src/services/schedule_service.py` -> 无输出（退出码 1，视为通过）。
- 未新增不允许规则和字段检查结果：
  - `rg -n "每年|yearly|daily|weekly|monthly|parent_id" src/data/database.py src/services/schedule_repeat_service.py src/services/schedule_service.py` -> 无输出（退出码 1）。
- py_compile 结果：
  - `python -m py_compile src/services/schedule_repeat_service.py src/services/schedule_service.py src/data/database.py` 通过（无输出）。
- diff 范围检查结果：
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`、`src/data/database.py`、`src/services/schedule_service.py`（写入本日志后另含 `manage_instruction/Work_Log.md`）。
  - `git status --short --branch` -> `M manage_instruction/Work_Task_Prompts.md`、`M src/data/database.py`、`M src/services/schedule_service.py`（写入本日志后另含 `M manage_instruction/Work_Log.md`）。
- 未完成事项：
  - 等待顾问窗口复核并下发下一小工单。
- 风险或疑点：
  - 本轮只移动旧未来删除策略；取消重复路径仍未处理。
  - 4-7b 没有调整事务边界；旧逻辑中当前条 update、旧未来删除、新未来重建仍沿用既有流程。

## 2026-05-18 第四轮 4-8a（取消重复路径行为基线验收）

- 本轮任务名称：第四轮 4-8a（取消重复路径行为基线验收）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 4-8a 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 是否改源码：
  - 否。本轮仅做行为基线验收。
- 取消重复路径静态复核结论：
  - 复核通过。已有 `old_group_id`、`update_future=True` 且新规则为 `none / 无 / 不重复 / ''` 时，当前条会写入 `group_id=None`。
  - 当前条先执行 `Schedule.update(...)`。
  - 旧未来删除策略仍会执行。
  - 新规则为非重复时不会进入 `ScheduleRepeatService.build_repeat_insert_plan(..., include_base=False)` 未来重建分支。
- 是否保持：当前条 `group_id=None`：
  - 是。验收中当前条更新后 `group_id` 为 `None`。
- 是否保持：当前条本体先更新：
  - 是。当前条标题更新为 `__tmp_4_8a_cancel_repeat_1779108172711331200_cancelled_current`，规则更新为 `none`。
- 是否保持：当前之前旧实例保留：
  - 是。当前之前旧实例保留 `10` 条。
- 是否保持：旧未来实例删除：
  - 是。更新后旧未来实例残留 `old future left []`。
- 是否保持：不重建未来实例：
  - 是。`new future left 0`。
- 是否保持：原 `group_id` 下最终只剩当前之前旧实例：
  - 是。原组剩余 `10` 条，均早于目标条时间，标题仍为旧标题。
- 明确记录：`add_schedule` 未改。
- 明确记录：`update_future=False` 路径未改。
- 明确记录：非组转重复路径未改。
- 明确记录：已有重复组改重复路径未改。
- 明确记录：未新增 `parent_id`。
- 明确记录：未新增 `每年/yearly/daily/weekly/monthly` 行为。
- 临时数据标题前缀：
  - `__tmp_4_8a_cancel_repeat_1779108172711331200`
- 原 `group_id`：
  - `f28c536b-5b9a-405e-8b0d-fe646e85e0f0`
- 被选中的中间项 id：
  - `93`
- 被选中的中间项原 `start_time`：
  - `2026-03-18 09:00:00`
- 更新前当前之前旧实例数量：
  - `10`
- 更新前当前之后旧未来实例数量：
  - `42`
- 更新后当前条标题/规则/`group_id`：
  - 标题：`__tmp_4_8a_cancel_repeat_1779108172711331200_cancelled_current`
  - 规则：`none`
  - `group_id`：`None`
- 更新后保留旧实例数量：
  - `10`
- 更新后旧未来实例残留检查结果：
  - `old future left []`
- 更新后新未来实例残留检查结果：
  - `new future left 0`
- 删除脱组当前条结果：
  - `deleted current 1`
- 删除剩余旧实例结果：
  - `deleted remaining group 10`
- 前缀残留检查结果：
  - 验收脚本内：`leftovers 0`。
  - 复查命令：`__tmp_4_8a_cancel_repeat_` 残留 `0`。
- 4-7b 轻量回归结果：
  - 已有重复组从 `每周` 改为 `每月` 且 `update_future=True`，返回 `True`。
  - 同组最终总数 `23`，保留旧实例 `10` 条，重建新未来 `12` 条。
  - 删除整组 `23` 条，前缀残留 `0`。
- `schedule.db` 是否无 tracked diff：
  - `git diff --name-only -- schedule.db` -> 无输出。
- service import / db import 验证结果：
  - 输出：`imports ok <class 'src.services.schedule_service.ScheduleService'> <class 'src.services.schedule_repeat_service.ScheduleRepeatService'> 75`。
- service 静态依赖检查结果：
  - `rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_repeat_service.py src/services/schedule_service.py` -> 无输出（退出码 1，视为通过）。
- 未新增不允许规则和字段检查结果：
  - `rg -n "每年|yearly|daily|weekly|monthly|parent_id" src/data/database.py src/services/schedule_repeat_service.py src/services/schedule_service.py` -> 无输出（退出码 1）。
- py_compile 结果：
  - `python -m py_compile src/services/schedule_repeat_service.py src/services/schedule_service.py src/data/database.py` 通过（无输出）。
- diff 范围检查结果：
  - `git diff --name-only -- src/data/database.py` -> 无输出。
  - `git diff --name-only -- src/services/schedule_service.py` -> 无输出。
  - `git diff --name-only -- src/services/schedule_repeat_service.py` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> 写入本日志前仅 `manage_instruction/Work_Task_Prompts.md`；写入本日志后为 `manage_instruction/Work_Log.md`、`manage_instruction/Work_Task_Prompts.md`。
  - `git status --short --branch` -> 写入本日志前仅 `M manage_instruction/Work_Task_Prompts.md`；写入本日志后另含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - 无。等待顾问窗口复核并下发 4-8b 或下一小工单。
- 风险或疑点：
  - 本轮只做取消重复路径行为基线，不做源码委托改造。
  - 取消重复路径与 4-7b 共用旧未来删除策略，后续 4-8b 如委托改造需保持当前“不重建未来实例”的分支边界。
- 是否建议进入 4-8b：
  - 可以进入 4-8b。当前行为基线清晰，验收未发现阻塞疑点。

## 2026-05-18 第四轮 4-8b（取消重复路径条件收口复核）

- 本轮任务名称：第四轮 4-8b（取消重复路径条件收口复核）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 4-8b 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 是否改源码：
  - 否。`4-8b 无需额外源码改造`。
- 静态复核结论：取消重复路径是否已复用 `ScheduleService.delete_future_schedules_for_group(...)`：
  - 是。`update_schedule_with_repeat(...)` 在 `if old_group_id:` 下统一调用 `ScheduleService.delete_future_schedules_for_group(...)`，取消重复路径与 4-7b 路径共用该委托。
- 明确记录：未迁移当前条 update。
- 明确记录：未迁移事务边界。
- 明确记录：未迁移新未来重建。
- 明确记录：未修改 `insert_many` / `batch_size=100`。
- 明确记录：未修改 `add_schedule`。
- 明确记录：未修改 `update_future=False` 路径。
- 明确记录：未修改非组转重复路径。
- 明确记录：未修改已有重复组改重复路径的新未来重建逻辑。
- 明确记录：未新增 `parent_id`。
- 明确记录：未新增 `每年/yearly/daily/weekly/monthly` 行为。

### 取消重复路径回归结果

- 临时数据标题前缀：
  - `__tmp_4_8b_cancel_repeat_1779108861036718600`
- 原 `group_id`：
  - `43f4b4d9-98c5-49f0-ba17-bceaf5ad4b34`
- 被选中的中间项 id：
  - `93`
- 更新后当前条 `group_id`：
  - `None`
- 更新后保留旧实例数量：
  - `10`
- 更新后旧未来实例残留检查结果：
  - `old future left []`
- 更新后新未来实例残留检查结果：
  - `new future left 0`
- 删除脱组当前条结果：
  - `deleted current 1`
- 删除剩余旧实例结果：
  - `deleted remaining group 10`
- 前缀残留检查结果：
  - 验收脚本内：`leftovers 0`
  - 复查命令：`('__tmp_4_8b_cancel_repeat_', 0)`

### 4-7b 保护回归结果

- 临时数据标题前缀：
  - `__tmp_4_8b_existing_group_guard_1779109005132473600`
- 回归结果：
  - `existing group monthly ok True`
  - 同组最终总数 `23`（保留 `10` + 重建 `12` + 当前 `1`）
  - 删除整组 `23`
  - 前缀残留 `0`

- `schedule.db` 是否无 tracked diff：
  - `git diff --name-only -- schedule.db` -> 无输出。
- service import / db import 验证结果：
  - 输出：`imports ok <class 'src.services.schedule_service.ScheduleService'> <class 'src.services.schedule_repeat_service.ScheduleRepeatService'> 75`
- service 静态依赖检查结果：
  - `rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_repeat_service.py src/services/schedule_service.py` -> 无输出（退出码 1，视为通过）。
- py_compile 结果：
  - `python -m py_compile src/services/schedule_repeat_service.py src/services/schedule_service.py src/data/database.py` 通过（无输出）。
- diff 范围检查结果：
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- src/data/models.py` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> 写入本日志前仅 `manage_instruction/Work_Task_Prompts.md`；写入本日志后为 `manage_instruction/Work_Log.md`、`manage_instruction/Work_Task_Prompts.md`。
  - `git status --short --branch` -> 写入本日志前仅 `M manage_instruction/Work_Task_Prompts.md`；写入本日志后另含 `M manage_instruction/Work_Log.md`。
- 未完成事项：
  - 无。等待顾问窗口复核并下发下一小工单。
- 风险或疑点：
  - 本轮仅做条件收口复核，未扩大到源码改造；若后续要进一步抽取取消重复路径协调，应继续保持当前分支语义不变。

## 2026-05-18 第四轮 4-9（第四轮整体验收与归档准备）

- 本轮任务名称：第四轮 4-9（第四轮整体验收与归档准备）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`

### 第四轮 4-0 ~ 4-8b 完成摘要

- `4-0`：静态审查与只读基线定位完成。
- `4-1`：重复日期计算纯逻辑抽取完成。
- `4-2`：重复规则待插入数据计划服务完成。
- `4-3`：`add_schedule` 非重复路径委托完成。
- `4-4`：`add_schedule` 重复路径收口验收完成。
- `4-5`：`update_future=False` 行为基线完成。
- `4-6`：非组转重复行为基线完成。
- `4-7a`：已有重复组未来更新行为基线完成。
- `4-7b`：旧未来删除策略最小委托完成。
- `4-8a`：取消重复行为基线完成。
- `4-8b`：取消重复路径条件收口复核完成（无需额外源码改造）。

### 关键验收结果

- service import 验证结果：
  - `imports ok <class 'src.services.schedule_service.ScheduleService'> <class 'src.services.schedule_repeat_service.ScheduleRepeatService'>`
  - `all schedules 75`
  - `active categories 7`
- service 静态依赖检查结果：
  - `rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_service.py src/services/schedule_repeat_service.py` 无输出（退出码 1，视为通过）。
- 未新增 `parent_id` / `每年/yearly/daily/weekly/monthly` 行为检查结果：
  - `rg -n "每年|yearly|daily|weekly|monthly|parent_id" src/data/database.py src/services/schedule_repeat_service.py src/services/schedule_service.py` 无输出（退出码 1，视为通过）。

### 写入路径回归

- `add_schedule` 非重复路径验收结果：
  - 创建返回 `True`，命中 `1` 条，删除返回 `True`，残留 `0`。
- `add_schedule` 重复路径验收结果：
  - 创建返回 `True`，命中 `53` 条，单一 `group_id`，按组删除 `53`，残留 `0`。
- `update_future=False` 当前条脱组验收结果：
  - 更新返回 `True`，当前条 `group_id=None`，原组剩余 `52`，清理 `1 + 52`，残留 `0`。
- `update_future=True` 非组转重复验收结果：
  - 更新返回 `True`，新组总数 `53`，按组删除 `53`，残留 `0`。
- `update_future=True` 已有重复组改重复验收结果：
  - 更新返回 `True`，同组总数 `23`（保留 `10` + 当前 `1` + 新未来 `12`），按组删除 `23`，残留 `0`。
- `update_future=True` 取消重复验收结果：
  - 更新返回 `True`，当前条脱组，原组剩余 `10`，清理 `1 + 10`，残留 `0`。

### 清理与兼容性

- 所有第四轮临时前缀残留检查结果：
  - `[('__tmp_4_9_', 0), ('__tmp_4_8b_', 0), ('__tmp_4_8a_', 0), ('__tmp_4_7b_', 0), ('__tmp_4_7a_', 0), ('__tmp_4_6_', 0), ('__tmp_4_5_', 0), ('__tmp_4_4_', 0)]`
- GUI smoke 或 import 兜底结果：
  - `import main` 通过，输出 `main import ok`。
- py_compile 结果：
  - `python -m py_compile src/services/schedule_repeat_service.py src/services/schedule_service.py src/data/database.py main.py` 通过（无输出）。

### 范围与归档结论

- diff 范围检查结果：
  - `git diff --name-only -- src` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> 写入本日志前仅 `manage_instruction/Work_Task_Prompts.md`；写入本日志后为 `manage_instruction/Work_Log.md`、`manage_instruction/Work_Task_Prompts.md`。
  - `git status --short --branch` -> 写入本日志前仅 `M manage_instruction/Work_Task_Prompts.md`；写入本日志后另含 `M manage_instruction/Work_Log.md`。
- `schedule.db` 是否无 tracked diff：
  - 是，无输出。
- 未完成事项：
  - 无。
- 风险或疑点：
  - 第四轮关键路径已完成行为验证；第五轮开始前建议先冻结第四轮日志和提示词锚点，避免后续混写导致审计困难。
- 是否建议归档第四轮：
  - 是。第四轮可归档，下一步进入第五轮提醒服务阶段合同/规划。

## 第五轮日志归档（2026-05-21 至 2026-05-25）

归档结论：第五轮 5-0 ~ 5-6 已完成并通过整体验收，可进入第六轮 Controller / Router / EventBus 协调层规划。

归档摘要：

- 提醒扫描入口、扫描频率、触发窗口和去重生命周期已完成基线定位。
- `ReminderService` 已承接提醒判断、运行期去重、候选筛选、`target_time` 选择和弹窗数据构造。
- `MainWindow` 已最小委托提醒扫描判断，仍保留 QTimer、数据来源、弹窗和声音副作用。
- 到点弹窗、60 秒触发窗口、运行期去重、重启后去重清空、三条停声路径等旧行为已完成回归确认。
- `src`、`main.py`、`requirements.txt`、`schedule.db` 在最终验收时无 diff。

对应 Git commits：
- 41c176e docs: prepare reminder service fifth round
- 7a3b2cb feat: add reminder service decision helpers
- 4a7546c feat: add reminder runtime dedup state
- 16ede10 feat: delegate reminder scanning to service
- 608f82b feat: delegate reminder popup data construction
- 78d2ff8 test: record reminder service regression checks
- 3520b31 test: complete reminder fifth round acceptance

### 第五轮归档前 Work_Log 全文

# Work Log

本文件只记录当前阶段/当前轮次的执行日志。

历史日志已归档到 `manage_instruction/History_Log.md`。

## 当前状态

第一轮：基建 + repository + db_manager 兼容委托，已完成并归档。

第二轮：Data 层整理与模型拆分，已完成并归档。

第三轮：纯业务查询与排序服务，已完成并归档。

第四轮：日程写入与重复规则服务，已完成并归档。

当前处于第五轮“提醒与运行期状态服务”。

第五轮 `5-6` 整体验收与归档准备已完成，等待归档收口或第六轮规划提示词。

## 当前轮次注意事项

- 第四轮 4-0 ~ 4-9 已归档到 `History_Log.md`。
- 当前没有正在执行的小工单；下一步等待归档收口或第六轮规划提示词。
- 执行窗口不得沿用第四轮 4-9 或第四轮任一提示词继续执行。
- 执行窗口不得在未收到第五轮后续正式提示词前自行开始提醒服务改造。

## 2026-05-21 第五轮 5-0（静态审查与只读基线定位）

- 本轮任务名与边界（只读）：
  - 工单：第五轮 `5-0` 静态审查与只读基线定位。
  - 边界：仅做源码定位与链路审查，不改任何源码、不写数据库、不改 `requirements.txt`、不改 `schedule.db`、不改提示词文件。
  - 实际修改：仅更新本日志文件。

- 开工前 git 状态基线（既有 diff）：
  - `git status --short` 结果：
    - `M manage_instruction/Work_Instruction.md`
    - `M manage_instruction/Work_Task_Prompts.md`
    - `M requirements.txt`
    - `?? requirements.txt.bak`
  - 以上均记为开工前既有状态，不计入 5-0 新增 diff。

- 实际检索到的关键函数/文件位置：
  - `src/ui/main_window.py`
    - `_init_scheduler`: `160`
    - `check_reminders`: `225`
    - `triggered_reminders` 初始化: `164`
    - `show_reminder_popup`: `240`
    - `page_add.req_open_alarm_picker -> go_to_alarm_picker`: `138`
    - `page_dashboard.req_edit_alarm -> go_to_alarm_picker_for_edit`: `141`
    - `go_to_alarm_picker`: `374`
    - `go_to_alarm_picker_for_edit`: `381`
    - `on_alarm_confirmed`: `405`
  - `src/ui/reminder_pop.py`
    - 顶部关闭按钮绑定 `self.close`: `123`
    - “知道了”按钮绑定 `self.close`: `92`
    - “关闭闹钟”按钮绑定 `_stop_alarm`: `79`
    - `_stop_alarm` 中 `winsound.PlaySound(None, winsound.SND_PURGE)`: `182-186`
    - `closeEvent` 中 `winsound.PlaySound(None, winsound.SND_PURGE)`: `191-194`
  - `src/ui/alarm_picker.py`
    - `AlarmPickerView`: `40`
    - `set_initial_data`: `243`
    - `_validate_time`: `297`
    - `_on_confirm`（最终提醒时间校验 + `confirm_requested.emit`）: `355-397`
  - `src/ui/alarm_picker_week.py`
    - `AlarmPickerViewWeek`: `40`
    - `set_initial_data`: `235`
    - `_validate_time`: `276`
    - `_on_confirm`（最终提醒时间校验 + `confirm_requested.emit`）: `315-342`
  - `src/ui/add_view.py`
    - `_emit_alarm_request`（计算 `target_time` 并发起请求）: `427-436`
    - `set_alarm_data`: `438`
    - 保存时写入提醒字段：`schedule_data['reminder_time'/'is_alarm'/'alarm_duration']`: `642-644`
  - `src/ui/add_view_week.py`
    - `_emit_alarm_request`（计算 `target_time` 并发起请求）: `426-435`
    - `set_alarm_data`: `437`
    - 保存时写入提醒字段：`schedule_data['reminder_time'/'is_alarm'/'alarm_duration']`: `592-594`
  - `src/ui/schedule_detail_pop.py`
    - 提醒展示 Label + 双击提示：`323-329`
    - `refresh_alarm_display`: `514-517`
    - 双击提醒后发出 `req_edit_alarm`: `622-623`
  - `src/data/models.py`
    - `Schedule.reminder_time`: `30`
    - `Schedule.is_alarm`: `31`
    - `Schedule.alarm_duration`: `32`

- 8 段固定结构结论摘要：
  - 扫描链路：
    - `MainWindow.__init__` 调用 `_init_scheduler`（`158`）。
    - `_init_scheduler` 创建 `QTimer`（`161`）并每 1000ms 触发 `check_reminders`（`162-163`）。
    - `check_reminders` 从 `db_manager.get_all_schedules()` 拉取全量日程（`227`）并逐条筛选提醒。
    - 命中条件后调用 `show_reminder_popup`（`236`），再记录到 `triggered_reminders`（`237`）。
  - 触发条件：
    - 无 `reminder_time` 直接跳过（`230`）。
    - 触发窗口是 `0 <= (now - reminder_time).total_seconds() < 60`（`232-235`）。
    - 到点后 60 秒外不会触发；未到点不会触发。
  - 去重生命周期：
    - `triggered_reminders` 在 `_init_scheduler` 中初始化为内存 `set`（`164`）。
    - 同一 `schedule.id` 在本次进程内只要已加入 set，就不会再次弹窗（`235`）。
    - 无持久化写库逻辑；应用重启后集合重建为空（由初始化位置可推断）。
  - 弹窗/声音边界：
    - 弹窗对象在 `MainWindow.show_reminder_popup` 内创建：`ReminderPop(data_dict)`（`247`）。
    - 声音开启在 `MainWindow.show_reminder_popup` 内，仅 `is_alarm` 为真时调用 `winsound.PlaySound("SystemHand", ... LOOP|ASYNC)`（`250-252`）。
    - 声音停止在 `ReminderPop` 内部：`_stop_alarm`（`182-186`）与 `closeEvent`（`191-194`）。
    - 三条停声路径：
      - 顶部关闭按钮（`123`）-> `close()` -> `closeEvent` 停声。
      - “知道了”按钮（`92`）-> `close()` -> `closeEvent` 停声。
      - “关闭闹钟”按钮（`79`）-> `_stop_alarm` 立即停声并隐藏按钮（`189`）。
  - 提醒设置入口：
    - 新建入口：`AddScheduleView._emit_alarm_request` 计算 `target_time = start_time or end_time` 后发信号（`435-436`）。
    - 周视图新建入口：`AddScheduleViewWeek._emit_alarm_request` 同逻辑（`434-435`）。
    - 编辑入口：`ScheduleDetailPop` 双击提醒标签发出 `req_edit_alarm`（`622-623`）；主窗口连接到 `go_to_alarm_picker_for_edit`（`141`）。
    - 主窗口接入提醒页：`go_to_alarm_picker`（`374`）与 `go_to_alarm_picker_for_edit`（`381`）。
  - 可抽 service 的逻辑：
    - `check_reminders` 中纯判断部分可抽离：无提醒过滤、秒差计算、触发窗口判断、批量筛选。
    - 运行期去重状态语义（`triggered_reminders` 的 `is_triggered/mark_triggered`）可抽为轻量状态服务。
    - `target_time = start_time or end_time` 的纯数据选择可抽为纯函数。
  - 必须留 UI 的副作用：
    - `ReminderPop` 的窗口创建/显示、倒计时 UI 更新、交互按钮行为必须留在 UI 层。
    - `winsound.PlaySound(...)` 的播放与停止边界当前都在 UI 层（`MainWindow` + `ReminderPop`），不应在 5-0 修改。
    - `QTimer` 驱动节奏（1000ms）当前在主窗口层，不在本工单中改变。
  - 风险点：
    - 当前扫描源是 `get_all_schedules()` 全量扫描，秒级定时器下规模增大可能带来性能压力。
    - 去重是进程内内存态，崩溃/重启后会丢失“已弹过”状态（这是现有行为，不是缺陷修复项）。
    - 触发窗口固定 60 秒，若系统挂起或事件循环阻塞可能出现错过窗口不补弹。
    - `show_reminder_popup` 目前先弹窗再标记已触发，若未来改动异常处理顺序需谨慎（避免重复弹窗或漏标记）。

- 验收命令与结果：
  - 执行：
    - `git status --short`
    - `git diff --name-only`
    - `git diff --name-only -- src`
    - `git diff --name-only -- main.py requirements.txt schedule.db`
  - 结果结论：
    - `src` 无新增 diff（5-0 未改源码）。
    - `main.py` 无 diff。
    - `schedule.db` 无 diff。
    - `requirements.txt` 仍为开工前既有 diff，非 5-0 新增。
    - 管理文档 diff 中，`Work_Log.md` 为本工单预期更新，`Work_Instruction.md` / `Work_Task_Prompts.md` 为既有 diff。

- 风险与后续建议（供 5-1 使用）：
  - 先抽“纯判断函数”与“去重状态容器”，不要触碰 UI 弹窗与声音边界。
  - 抽离时保持 `0 <= diff < 60` 与 `target_time` 选择语义不变，避免行为回归。
  - `mark_triggered` 的调用时机建议仍放在“弹窗成功触发后”。

## 2026-05-21 第五轮 5-1（ReminderService 骨架与纯判断函数）

- 本轮任务名与边界：
  - 工单：第五轮 `5-1` ReminderService 骨架与纯判断函数。
  - 边界：仅新增提醒纯逻辑 service，不接入 `MainWindow`，不改 UI，不改数据库，不改依赖。

- 开工前 git 状态基线：
  - `git status --short` 结果：
    - `M manage_instruction/Work_Task_Prompts.md`
  - 该 diff 为开工前既有状态。

- 实际新增/修改文件：
  - 新增：`src/services/reminder_service.py`
  - 更新：`manage_instruction/Work_Log.md`
  - 未修改：`src/services/__init__.py`（本轮无需导出调整）

- `ReminderService` 纯函数/方法清单：
  - `has_reminder_time(schedule)`：判断是否存在 `reminder_time`。
  - `get_reminder_diff_seconds(schedule, now)`：计算 `now - reminder_time` 秒差；无提醒返回 `None`。
  - `is_in_trigger_window(diff_seconds)`：判断是否命中旧窗口 `0 <= diff < 60`。
  - `should_trigger(schedule, now)`：仅基于当前对象与时间判断是否触发；不考虑去重、无状态写入。
  - `select_target_time(schedule)`：`start_time` 优先，否则 `end_time`，若都无返回 `None`。

- 本轮明确未做事项（按工单要求）：
  - 未接入 `MainWindow`。
  - 未修改 `src/ui/*`。
  - 未实现运行期去重状态（未实现 `mark_triggered`、`collect_due_schedules`）。
  - 未生成完整弹窗 dict。
  - 未迁移声音播放。

- 假对象验证结果：
  - 无提醒：不触发（通过）。
  - 未到提醒时间：不触发（通过）。
  - 到点且在 60 秒窗口：触发（通过）。
  - 超过 60 秒窗口：不触发（通过）。
  - `target_time` 优先取 `start_time`（通过）。
  - 无 `start_time` 时取 `end_time`；都无时为 `None`（通过）。

- py_compile / import / 静态依赖检查结果：
  - `.\.venv\Scripts\python.exe -m py_compile src/services/reminder_service.py`：失败。
    - 原因：当前 `.venv` 指向的本地 Python 路径不可用（`Unable to create process ... Python311\python.exe`）。
  - 回退解释器：`C:\Users\22339\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`
    - `-m py_compile src/services/reminder_service.py`：通过。
    - `-c "from src.services.reminder_service import ReminderService; print(...)"`：通过，输出 `reminder service import ok`。
  - 轻量假对象脚本：通过，输出 `fake object checks ok`。
  - 静态依赖检查：
    - `rg -n "QWidget|QTimer|winsound|ReminderPop|db_manager|src\.ui|PyQt|PySide" src/services/reminder_service.py`
    - 结果：无输出、无匹配（`rg` 退出码 `1`，符合无匹配预期）。

- diff 范围检查结果：
  - `git status --short`：
    - `M manage_instruction/Work_Log.md`（本轮预期）
    - `M manage_instruction/Work_Task_Prompts.md`（开工前既有）
    - `A src/services/reminder_service.py`（本轮预期）
  - `git diff --name-only -- src/ui`：无输出（`src/ui` 无 diff）。
  - `git diff --name-only -- main.py requirements.txt schedule.db`：无输出（这三项无新增 diff）。

- 风险与后续建议（供 5-2 使用）：
  - 5-2 只需在当前 `ReminderService` 基础上补充“运行期去重状态容器”，不应改动 `should_trigger` 的纯判断语义。
  - `should_trigger` 目前无异常吞噬，后续接入前可由调用层保证传入对象字段类型正确，以避免隐藏错误。

- 顾问复验补充：
  - 用户在本机 CMD 重建 `.venv` 后，执行 `.\.venv\Scripts\python.exe -m py_compile src\services\reminder_service.py` 通过。
  - 用户在本机 CMD 执行 `.\.venv\Scripts\python.exe -c "from src.services.reminder_service import ReminderService; print('reminder service import ok')"` 通过。
  - 顾问工具环境中 `.venv` redirector 仍受工具权限/进程创建限制影响，但使用 Codex bundled Python 复跑 `py_compile`、import 和轻量假对象验证均通过。
  - 顾问复验确认：`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 无 diff；5-1 可验收通过。

## 2026-05-21 第五轮 5-2（运行期去重状态抽取）

- 本轮任务名与边界：
  - 工单：第五轮 `5-2` 运行期去重状态抽取。
  - 边界：仅在 `ReminderService` 增加运行期内存去重能力；不接入 `MainWindow`；不改 UI、数据库、依赖、触发窗口语义。

- 开工前 git 状态基线：
  - `git status --short` 结果：
    - `M manage_instruction/Work_Task_Prompts.md`
  - 该 diff 为开工前既有状态。

- 实际新增/修改文件：
  - 修改：`src/services/reminder_service.py`
  - 更新：`manage_instruction/Work_Log.md`
  - 未修改：`src/services/__init__.py`（本轮无需变更导出）

- `ReminderService` 新增的运行期去重方法清单：
  - `__init__()`：初始化实例级 `self._triggered_ids`（`set[int]`）。
  - `_get_schedule_id(schedule)`：纯辅助读取 `schedule.id`（仅接收 `int`）。
  - `is_triggered(schedule_id)`：判断 id 是否已在当前实例标记。
  - `mark_triggered(schedule_id)`：显式标记 id 已触发。
  - `collect_due_schedules(schedules, now)`：批量筛选“满足提醒条件且未标记”的对象列表；不隐式标记。
  - 同步修正：`get_reminder_diff_seconds` docstring 从 `.seconds` 改为 `total_seconds()` 表述（函数行为未变）。

- 本轮明确未做事项（按工单要求）：
  - 未接入 `MainWindow`。
  - 未修改 `src/ui/*`。
  - 未生成完整弹窗 dict（留给 5-4）。
  - 未迁移声音播放。
  - 未新增提醒持久化字段/表/迁移。

- 假对象验证结果：
  - 无提醒：`collect_due_schedules` 不返回（通过）。
  - 未到提醒时间：不返回（通过）。
  - 到点且在 60 秒窗口：返回（通过）。
  - 超过 60 秒窗口：不返回（通过）。
  - `mark_triggered(id)` 后：同 id 不再返回（通过）。
  - `collect_due_schedules` 不隐式标记：同一未标记对象连续 collect 两次仍返回（通过）。
  - 新建 `ReminderService()` 实例：去重状态为空（通过）。
  - `should_trigger(schedule, now)` 在 `mark_triggered(id)` 后仍返回纯判断结果，不受去重状态影响（通过）。

- py_compile / import / 静态依赖检查结果：
  - `.\.venv\Scripts\python.exe -m py_compile src/services/reminder_service.py`：失败（Unable to create process，`.venv` redirector 指向不可用本机 Python 路径）。
  - `.\.venv\Scripts\python.exe -c "from src.services.reminder_service import ReminderService; ..."`：同样失败（同原因）。
  - 回退 bundled Python：
    - `C:\Users\22339\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m py_compile src/services/reminder_service.py`：通过。
    - import 校验：通过，输出 `reminder service import ok`。
  - 静态依赖检查：
    - `rg -n "QWidget|QTimer|winsound|ReminderPop|db_manager|src\.ui|PyQt|PySide" src/services/reminder_service.py`
    - 结果：无输出/无匹配（`rg` 退出码 1，符合预期）。

- diff 范围检查结果：
  - `git status --short`：
    - `M manage_instruction/Work_Log.md`（本轮预期）
    - `M manage_instruction/Work_Task_Prompts.md`（既有）
    - `M src/services/reminder_service.py`（本轮预期）
  - `git diff --name-only -- src/ui`：无输出（`src/ui` 无 diff）。
  - `git diff --name-only -- main.py requirements.txt schedule.db`：无输出（本工单未引入这三项 diff）。

- 风险与后续建议（供 5-3 使用）：
  - 5-3 接入 `MainWindow` 时，应在弹窗成功后显式调用 `mark_triggered(id)`，避免重复弹窗。
  - `collect_due_schedules` 当前对 `id` 非 `int` 的对象会跳过；接入层需确保日程对象带有效 `id`。
  - 保持 `should_trigger` 的无状态纯判断边界，不要在其中引入去重写入。

- 特别记录：
  - 本工单完成后不要提交 Git，等待顾问窗口审核。

## 2026-05-21 第五轮 5-3（MainWindow 提醒扫描最小委托）

- 本轮任务名与边界：
  - 工单：第五轮 `5-3` MainWindow 提醒扫描最小委托。
  - 边界：仅改 `src/ui/main_window.py` 的提醒扫描接入；保持 UI 弹窗/声音/QTimer/数据源语义不变。

- 开工前 git 状态基线：
  - `git status --short` 结果：
    - `M manage_instruction/Work_Task_Prompts.md`
  - 该 diff 为开工前既有状态。

- 实际新增/修改文件：
  - 修改：`src/ui/main_window.py`
  - 更新：`manage_instruction/Work_Log.md`
  - 未修改：`src/services/reminder_service.py`（本轮无兼容修正需求）

- `MainWindow` 接入 `ReminderService` 的位置说明：
  - 新增 import：`from ..services.reminder_service import ReminderService`（`src/ui/main_window.py:27`）。
  - `_init_scheduler()` 中创建 service 实例：`self.reminder_service = ReminderService()`（`src/ui/main_window.py:162`）。
  - 保留原有 QTimer 行为：
    - `self.reminder_timer = QTimer(self)`
    - `self.reminder_timer.timeout.connect(self.check_reminders)`
    - `self.reminder_timer.start(1000)`
  - 删除主窗口直接维护裸 `triggered_reminders` 的细节。

- `check_reminders()` 新扫描流程摘要：
  - `now = datetime.now()`
  - `schedules = db_manager.get_all_schedules()`
  - `due_schedules = self.reminder_service.collect_due_schedules(schedules, now)`
  - 遍历 due：
    - 先 `self.show_reminder_popup(s)`
    - 后 `self.reminder_service.mark_triggered(s.id)`
    - 打印日志（延迟由 `get_reminder_diff_seconds` 计算）
  - 已确认顺序是 `collect -> show -> mark`（定位行：`226/230/232/233`）。

- 本轮明确未做事项（按工单要求）：
  - 未修改 `src/ui/reminder_pop.py`。
  - 未修改提醒选择页（`alarm_picker*`、`add_view*`、`schedule_detail_pop` 均未改）。
  - 未迁移声音播放（`winsound.PlaySound(...)` 仍在 `show_reminder_popup`）。
  - 未迁移 QTimer（仍由 `MainWindow` 创建与驱动）。
  - 未生成完整弹窗 dict（`show_reminder_popup` 字段与语义保持不变）。
  - 未新增提醒持久化字段/表/迁移。

- py_compile / import / 静态检查结果：
  - `.venv` 验证：
    - `.\.venv\Scripts\python.exe -m py_compile ...`：失败（Unable to create process）。
    - `.\.venv\Scripts\python.exe -c "from src.services.reminder_service ..."`：失败（同原因）。
  - bundled Python 复验：
    - `py_compile src/services/reminder_service.py src/ui/main_window.py`：通过。
    - import `ReminderService`：通过，输出 `reminder service import ok`。
  - 静态检查：
    - `rg -n "triggered_reminders" src/ui/main_window.py`：无输出（主窗口已不直接操作裸 set）。
    - `rg -n "winsound|ReminderPop|show_reminder_popup|PlaySound" src/services/reminder_service.py`：无输出（service 未吸收 UI/声音副作用）。
  - 轻量语义复验（bundled Python）：通过，确认
    - `collect_due_schedules` 不隐式标记；
    - `mark_triggered` 后过滤生效；
    - `should_trigger` 仍不受去重状态影响。

- diff 范围检查结果：
  - `git diff --name-only -- src/ui`：仅 `src/ui/main_window.py`。
  - `git diff --name-only -- main.py requirements.txt schedule.db`：无输出。
  - `git status --short`：
    - `M manage_instruction/Work_Log.md`（本轮预期）
    - `M manage_instruction/Work_Task_Prompts.md`（既有）
    - `M src/ui/main_window.py`（本轮预期）

- 风险与后续建议（供 5-4 使用）：
  - 5-4 若收口弹窗 dict 构造到 service，需保证字段仍是 `title/is_alarm/target_time` 且 `target_time` 语义不变。
  - `mark_triggered` 目前依赖 `s.id`；接入层应确保日程对象存在有效 `id`。
  - 若后续加入异常保护循环，需继续保证“仅 show 成功后才 mark”，不得放在 `finally`。

- 特别记录：
  - 本工单完成后不要提交 Git，等待顾问窗口审核。

- 顾问复验补充：
  - 使用 Codex bundled Python 复跑 `py_compile src/services/reminder_service.py src/ui/main_window.py` 和 `ReminderService` import 验证，均通过。
  - 静态检查确认 `src/ui/main_window.py` 中已无 `triggered_reminders`，`src/services/reminder_service.py` 中无 UI/声音副作用关键字。
  - 复验 `check_reminders()` 文本顺序为 `collect_due_schedules` -> `show_reminder_popup(s)` -> `mark_triggered(s.id)`，且未把标记放入 `finally`。
  - 复验 `ReminderService.collect_due_schedules` 不隐式标记、`mark_triggered` 后过滤、`should_trigger` 不受去重状态影响。
  - diff 范围确认：`src/ui` 仅 `main_window.py` 有 diff；`src/ui/reminder_pop.py`、`main.py`、`requirements.txt`、`schedule.db` 无 diff；`main_window.py` 末尾补换行属于无行为格式变化。
  - 5-3 可验收通过。

## 2026-05-21 第五轮 5-4（提醒弹窗数据构造边界收口）

- 本轮任务名与边界：
  - 工单：第五轮 `5-4` 提醒弹窗数据构造边界收口。
  - 边界：仅把弹窗 `data_dict` 纯构造逻辑收口到 `ReminderService`；不改扫描主流程语义，不改 UI/声音/QTimer 边界。

- 开工前 git 状态基线：
  - `git status --short` 结果：
    - `M manage_instruction/Work_Task_Prompts.md`
  - 该项为开工前既有 diff。

- 实际新增/修改文件：
  - 修改：`src/services/reminder_service.py`
  - 修改：`src/ui/main_window.py`
  - 更新：`manage_instruction/Work_Log.md`

- `ReminderService` 新增的弹窗数据构造方法说明：
  - 新增 `build_reminder_popup_data(schedule)`。
  - 返回字段固定为：`title`、`is_alarm`、`target_time`。
  - 值语义保持：
    - `title` 来自 `schedule.title`
    - `is_alarm` 来自 `schedule.is_alarm`
    - `target_time` 复用 `select_target_time(schedule)`（`start_time` 优先，否则 `end_time`，都无时 `None`）。

- `show_reminder_popup` 保持不变的副作用边界说明（弹窗 + 声音）：
  - `MainWindow.show_reminder_popup()` 仍负责：
    - `ReminderPop(data_dict)` 创建
    - `self.current_popup.show()` 显示
    - `winsound.PlaySound(...)` 播放声音（仅 `schedule_data.is_alarm` 为真）
  - 本轮仅把 `data_dict` 的构造改为：
    - `data_dict = self.reminder_service.build_reminder_popup_data(schedule_data)`

- 假对象验证结果（bundled Python）：
  - `start_time` 存在时：`target_time == start_time`（通过）。
  - `start_time` 为空且 `end_time` 存在时：`target_time == end_time`（通过）。
  - `start_time` / `end_time` 都为空时：`target_time is None`（通过）。
  - `title` / `is_alarm` 原样来自 schedule（通过）。
  - dict key 精确等于 `title/is_alarm/target_time`（通过，无新增遗漏字段）。

- py_compile / import / 静态依赖检查结果：
  - `.venv` 验证：
    - `.\.venv\Scripts\python.exe -m py_compile src/services/reminder_service.py src/ui/main_window.py`：失败（Unable to create process）。
    - `.\.venv\Scripts\python.exe -c "from src.services.reminder_service import ReminderService; ..."`：失败（同原因）。
  - 回退 bundled Python：
    - `py_compile src/services/reminder_service.py src/ui/main_window.py`：通过。
    - import `ReminderService`：通过，输出 `reminder service import ok`。
  - 静态依赖检查：
    - `rg -n "QWidget|QTimer|winsound|ReminderPop|db_manager|src\.ui|PyQt|PySide" src/services/reminder_service.py`
    - 结果：无输出/无匹配（`rg` 退出码 1，符合预期）。

- diff 范围检查结果：
  - `git diff --name-only -- src/ui`：仅 `src/ui/main_window.py`。
  - `git diff --name-only -- main.py requirements.txt schedule.db`：无输出。
  - `git status --short`：
    - `M manage_instruction/Work_Task_Prompts.md`（既有）
    - `M src/services/reminder_service.py`（本轮预期）
    - `M src/ui/main_window.py`（本轮预期）

- 本轮未做事项（按工单要求）：
  - 未修改 `src/ui/reminder_pop.py`。
  - 未迁移声音播放到 service。
  - 未迁移 QTimer 到 service。
  - 未改变 `check_reminders()` 的 `collect -> show -> mark` 顺序。
  - 未新增提醒持久化字段/表/迁移。

- 风险与后续建议（供 5-5 使用）：
  - 5-5 可重点做回归验证：`show_reminder_popup` 输入 dict 字段一致性与到点触发行为保持。
  - 若后续补异常保护，仍需保证 `mark_triggered(s.id)` 在 `show_reminder_popup(s)` 成功调用之后。

- 特别记录：
  - 本工单完成后不要提交 Git，等待顾问窗口审核。
- 顾问复验补充：
  - 顾问修正 `build_reminder_popup_data(schedule)`，将 `title` / `is_alarm` 改为直接读取 `schedule.title` / `schedule.is_alarm`，保持与旧 `MainWindow.show_reminder_popup()` 内联构造完全一致。
  - 使用 Codex bundled Python 复跑 `py_compile src/services/reminder_service.py src/ui/main_window.py` 和 `ReminderService` import 验证，均通过。
  - 复跑弹窗 dict 假对象验证，确认 key 精确等于 `title`、`is_alarm`、`target_time`，且 `target_time` 选择语义保持不变。
  - 静态依赖检查确认 `ReminderService` 未依赖 UI、声音或 `db_manager`。
  - 复验 `show_reminder_popup()` 仍创建 `ReminderPop(data_dict)`、调用 `show()`，并按 `schedule_data.is_alarm` 在 UI 层调用 `winsound.PlaySound(...)`。
  - 复验 `check_reminders()` 仍保持 `collect -> show -> mark` 顺序。
  - diff 范围确认：`src/ui` 仅 `main_window.py` 有 diff；`src/ui/reminder_pop.py`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。
  - 5-4 可验收通过。

## 2026-05-21 第五轮 5-5（提醒服务轻量回归验收）

- 本轮任务名与边界：
  - 工单：第五轮 `5-5` 提醒服务轻量回归验收。
  - 边界：仅做验证与边界复核，不改源码、不改数据库、不改依赖；仅更新本日志。

- 开工前 git 状态基线：
  - `git status --short`：
    - `M manage_instruction/Work_Task_Prompts.md`
  - 该项记为既有提示词 diff，不计入 5-5 新增改动。
  - 开工前未发现 5-4 遗留源码 diff，因此继续执行 5-5。

- 实际修改文件：
  - `manage_instruction/Work_Log.md`（本轮预期）

- ReminderService 回归验证结果：
  - `has_reminder_time(schedule)`：无提醒返回 False（通过）。
  - `get_reminder_diff_seconds(schedule, now)`：沿用 `total_seconds()` 语义（通过）。
  - `is_in_trigger_window(diff)`：保持 `0 <= diff < 60`（通过）。
  - `should_trigger(schedule, now)`：保持无状态纯判断，不受去重状态影响（通过）。
  - `collect_due_schedules(schedules, now)`：不隐式标记（通过）。
  - `mark_triggered(id)` 后：同 id 不再被 collect 返回（通过）。
  - 新建 `ReminderService()` 实例：去重状态为空（通过）。
  - `select_target_time(schedule)`：`start_time` 优先，否则 `end_time`，都无时 `None`（通过）。
  - `build_reminder_popup_data(schedule)`：key 精确为 `title/is_alarm/target_time`，字段值语义正确（通过）。

- MainWindow 静态边界复核结果：
  - `_init_scheduler()` 仍创建 QTimer 且 `start(1000)`（保留）。
  - `_init_scheduler()` 已创建 `self.reminder_service = ReminderService()`（保留）。
  - `check_reminders()` 数据来源仍为 `db_manager.get_all_schedules()`（保留）。
  - 顺序仍为：`collect_due_schedules -> show_reminder_popup(s) -> mark_triggered(s.id)`（保留）。
  - `show_reminder_popup()` 仍负责 `ReminderPop(data_dict)`、`show()`、`winsound.PlaySound(...)`（保留）。
  - 声音播放条件仍基于 `schedule_data.is_alarm`（保留）。

- UI/声音/数据库副作用边界复核结果：
  - `src/ui/reminder_pop.py` 无 diff。
  - `winsound.PlaySound(...)` 未迁移到 service。
  - `ReminderPop` 未迁移到 service。
  - `QTimer` 未迁移到 service。
  - service 未依赖 `db_manager`。
  - `schedule.db` 无 diff。

- py_compile / import / 假对象验证 / 静态依赖检查结果：
  - `.venv` 两条命令均失败：`Unable to create process ... Python311\python.exe`（工具环境问题，已留痕）。
  - 使用 bundled Python 复验：
    - `py_compile src/services/reminder_service.py src/ui/main_window.py`：通过。
    - `from src.services.reminder_service import ReminderService`：通过，输出 `reminder service import ok`。
  - 轻量假对象回归脚本：通过，输出 `5-5 regression checks ok`。
  - service 静态依赖检查：
    - `rg -n "QWidget|QTimer|winsound|ReminderPop|db_manager|src\.ui|PyQt|PySide" src/services/reminder_service.py`
    - 结果：无输出/无匹配（`rg` 退出码 1，符合预期）。

- diff 范围检查结果：
  - `git diff --name-only -- src/ui`：无输出。
  - `git diff --name-only -- src/services/reminder_service.py`：无输出。
  - `git diff --name-only -- main.py requirements.txt schedule.db`：无输出。
  - `git status --short`（收尾）：
    - `M manage_instruction/Work_Log.md`（本轮预期）
    - `M manage_instruction/Work_Task_Prompts.md`（既有提示词 diff）

- 风险与后续建议（供 5-6 使用）：
  - 当前 `.venv` 在工具环境仍不可直接执行，5-6 若要求强依赖 `.venv` 命令，应继续使用“`.venv`失败留痕 + bundled Python复验”策略。
  - 第五轮可进入整体验收与归档准备，重点确认外部行为无回归。

- 特别记录：
  - 本工单完成后不要提交 Git，等待顾问窗口审核。

- 顾问复验补充：
  - 使用 Codex bundled Python 复跑 `py_compile src/services/reminder_service.py src/ui/main_window.py` 和 `ReminderService` import 验证，均通过。
  - 复跑 5-5 轻量假对象回归验证，确认提醒窗口、运行期去重状态、`target_time` 选择和弹窗 dict 构造均符合预期。
  - 静态依赖检查确认 `ReminderService` 无 UI、声音或 `db_manager` 依赖；`MainWindow` 中无 `triggered_reminders`。
  - 复验 `check_reminders()` 顺序仍为 `collect_due_schedules` -> `show_reminder_popup(s)` -> `mark_triggered(s.id)`。
  - diff 范围确认：`src/ui`、`src/services/reminder_service.py`、`main.py`、`requirements.txt`、`schedule.db` 均无 diff；5-5 只追加日志记录。
  - 5-5 可验收通过。

## 2026-05-21 第五轮 5-6（第五轮整体验收与归档准备）

- 本轮任务名与边界：
  - 工单：第五轮 `5-6` 整体验收与归档准备。
  - 边界：仅做最终验收、范围复核与日志收口；不改源码、不改数据库、不改依赖，不执行实际归档搬迁。

- 开工前 git 状态基线：
  - `git status --short`：
    - `M manage_instruction/Work_Task_Prompts.md`
  - 该项为既有提示词 diff，不计入 5-6 新增改动。
  - 开工前 `src`、`main.py`、`requirements.txt`、`schedule.db` 无 diff，满足继续执行条件。

- 实际修改文件：
  - `manage_instruction/Work_Log.md`（本轮预期）

- 5-0 到 5-5 完成摘要：
  - `5-0`：完成提醒链路静态基线定位，确认触发窗口与 UI/声音边界。
  - `5-1`：完成 `ReminderService` 纯判断骨架（无去重、无 UI 副作用）。
  - `5-2`：完成运行期去重状态抽取（`is_triggered/mark_triggered/collect_due_schedules`）。
  - `5-3`：完成 `MainWindow.check_reminders()` 最小委托（`collect -> show -> mark`）。
  - `5-4`：完成弹窗 dict 纯构造收口（`build_reminder_popup_data`）。
  - `5-5`：完成轻量回归验收并确认边界与行为保持。

- ReminderService 最终职责与禁止边界复核结果：
  - 最终职责已覆盖：
    - 提醒时间存在判断。
    - 秒差计算与触发窗口判断（`0 <= diff < 60`）。
    - 运行期去重状态管理。
    - 到期候选筛选。
    - `target_time` 选择。
    - 弹窗 dict 纯构造（`title/is_alarm/target_time`）。
  - 禁止边界满足：
    - 无 UI 依赖、无 `winsound`、无 `ReminderPop`、无 `QTimer`、无 `db_manager`、无数据库写入。

- MainWindow 最终职责复核结果：
  - 仍由 `MainWindow` 创建 QTimer，且 `start(1000)`。
  - 扫描数据来源仍为 `db_manager.get_all_schedules()`。
  - `check_reminders()` 顺序仍为 `collect_due_schedules -> show_reminder_popup(s) -> mark_triggered(s.id)`。
  - `show_reminder_popup()` 仍负责：
    - 创建 `ReminderPop(data_dict)`；
    - 弹窗 `show()`；
    - 按 `schedule_data.is_alarm` 播放系统声音。

- 旧行为保持复核结果：
  - 无 `reminder_time` 不触发（通过）。
  - 未到提醒时间不触发（通过）。
  - 超过 60 秒窗口不补弹（通过）。
  - 到点且在 60 秒窗口内触发（通过）。
  - 同一日程 ID 本次运行内不重复触发（通过）。
  - 新 service 实例去重状态为空（通过）。
  - `target_time` 仍优先 `start_time`，否则 `end_time`，都无则 `None`（通过）。
  - 弹窗 dict 仍仅 `title/is_alarm/target_time`（通过）。
  - 强提醒声音仍由 UI 层播放（通过）。
  - 关闭弹窗/停止闹钟逻辑仍在 `ReminderPop`（通过）。

- 未做事项确认：
  - 未修改 `ReminderPop`。
  - 未修改提醒选择页。
  - 未修改数据库模型。
  - 未新增数据库字段或提醒持久化。
  - 未修改 `db_manager` 对外 API。
  - 未修改 `main.py`、`requirements.txt`、`schedule.db`。
  - 未开启第六轮 Controller / Router / EventBus 改造。

- py_compile / import / 假对象验证 / 静态依赖检查结果：
  - `.venv` 命令在工具环境失败：`Unable to create process ... Python311\python.exe`（已留痕）。
  - bundled Python 复验：
    - `py_compile main.py src/services/reminder_service.py src/ui/main_window.py src/ui/reminder_pop.py`：通过。
    - `ReminderService` import：通过，输出 `reminder service import ok`。
  - 轻量假对象整体验证：通过，输出 `5-6 overall regression checks ok`。
  - service 静态依赖检查：
    - `rg -n "QWidget|QTimer|winsound|ReminderPop|db_manager|src\.ui|PyQt|PySide" src/services/reminder_service.py`
    - 结果：无输出/无匹配（`rg` 退出码 1，符合预期）。
  - MainWindow 静态检查：
    - `rg -n "triggered_reminders" src/ui/main_window.py`：无输出。
    - 顺序/边界关键词检查输出符合预期（含 `get_all_schedules`、`start(1000)`、`collect`、`show`、`mark`、`ReminderPop`、`PlaySound`）。

- diff 范围检查结果：
  - `git diff --name-only -- src`：无输出。
  - `git diff --name-only -- main.py requirements.txt schedule.db`：无输出。
  - `git diff --name-only -- manage_instruction`：
    - `manage_instruction/Work_Log.md`（本轮预期）
    - `manage_instruction/Work_Task_Prompts.md`（既有提示词 diff）
  - `git status --short`（收尾）：
    - `M manage_instruction/Work_Log.md`（本轮预期）
    - `M manage_instruction/Work_Task_Prompts.md`（既有）

- 第五轮整体验收结论：
  - 结论：通过。
  - 可归档性：第五轮可进入归档/阶段收口流程。
  - 下一步建议：可由决策窗口/顾问窗口规划第六轮（Controller / Router / EventBus 协调层）。

- 明确声明：
  - 本工单未实际执行归档搬迁。
  - 未修改 `History_Log.md`、`History_Instruction.md` 等历史归档文件。
  - 未开启第六轮改造。

- 特别记录：
  - 本工单完成后不要提交 Git，等待顾问窗口审核。
- 顾问复验补充：
  - 已同步 `Work_Log.md` 顶部当前状态：第五轮 `5-6` 已完成，下一步等待归档收口或第六轮规划提示词。
  - 使用 Codex bundled Python 复跑 `py_compile main.py src/services/reminder_service.py src/ui/main_window.py src/ui/reminder_pop.py` 和 `ReminderService` import 验证，均通过。
  - 复跑 5-6 轻量假对象整体验证，确认提醒窗口、运行期去重、`target_time` 选择、弹窗 dict 构造和 `check_reminders()` 顺序均符合预期，输出 `5-6 overall regression checks ok`。
  - 静态依赖检查确认 `ReminderService` 无 UI、声音或 `db_manager` 依赖；`MainWindow` 中无 `triggered_reminders`。
  - 范围检查确认：`src`、`main.py`、`requirements.txt`、`schedule.db` 均无 diff；当前仅 `Work_Log.md` 和既有 `Work_Task_Prompts.md` 有 diff。
  - 5-6 可验收通过；第五轮可进入归档/阶段收口流程。

## 第六轮日志归档（2026-05-25 至 2026-05-26）

归档结论：第六轮 6-0 ~ 6-8 已完成并通过整体验收，可进入第七轮 Theme/QSS 接入阶段合同/规划。

归档摘要：

- 建立并验证 `MainController`、`ViewRouter`、`RefreshCoordinator` 最小协调层。
- `ViewRouter` 接管 MainWindow 视图切换纯路由决策。
- `MainController` 接管添加页来源与返回目标纯决策。
- `RefreshCoordinator` 接管 MainWindow Dashboard / Todo / Week 三连刷新协调边界。
- `global_signals.refresh_requested(str)` 作为并行 EventBus 通知试点加入。
- 详情弹窗与跨视图刷新回流已完成复核，但不在第六轮继续源码接管。
- 第六轮最终验收确认 `src`、`main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。

### 第六轮归档前 Work_Log 全文
# Work Log

本文件只记录当前阶段/当前轮次的执行日志。

历史日志已归档到 `manage_instruction/History_Log.md`。

## 当前状态

第一轮：基建 + repository + db_manager 兼容委托，已完成并归档。

第二轮：Data 层整理与模型拆分，已完成并归档。

第三轮：纯业务查询与排序服务，已完成并归档。

第四轮：日程写入与重复规则服务，已完成并归档。

第五轮：提醒与运行期状态服务，已完成并归档。

第六轮：Controller / Router / EventBus 协调层，已启动。

当前已完成 6-8（第六轮整体验收与归档准备），等待顾问窗口复核与第七轮 Theme/QSS 接入阶段合同。

## 当前轮次注意事项

- 6-8 仅做第六轮整体验收与归档准备，不改源码。
- 后续第六轮改造需按小工单逐步迁移，不得一次性重构 `MainWindow`/`WeekWindow`/`TodoBoardWindow`。
- 在未收到后续正式提示词前，不得自行开始第七轮 Theme/QSS 接入改造。

## 2026-05-25 第六轮 6-0（静态审查与跨视图耦合定位）

- 本轮任务名称：第六轮 6-0（静态审查与跨视图耦合定位）。
- 开工前 git 状态：
  - `git status --short --branch` -> `## main...temp/main`，`M manage_instruction/Work_Task_Prompts.md`。
  - `git diff --name-only` -> `manage_instruction/Work_Task_Prompts.md`。
  - 结论：开工前已有管理文档 diff（`Work_Task_Prompts.md`），不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`

### 读取的阶段合同结论

- 第六轮目标是“跨视图协调层接管”，不是 UI 大拆分。
- 第六轮首工单 `6-0` 仅做静态审查与耦合定位。
- 默认不改 UI，不改数据层，不改 `db_manager` API。
- 重点是为后续 `MainController` / `ViewRouter` / `RefreshCoordinator` 建立迁移基线。

### 静态搜索命令与关键结果

- `Get-Content manage_instruction/Work_Instruction.md`：确认第六轮合同与小工单拆分。
- `Get-Content src/utils/signals.py`：确认 `global_signals` 当前信号集。
- `rg ... src/ui/main_window.py`：命中 `switch_view`、`source_view_for_add`、picker 模式状态、跨视图刷新直连、周/月窗口 show/hide。
- `rg ... src/ui/week_window.py`：命中内部 `body_stack` 路由、picker 返回链、`schedule_updated/request_schedule_detail/view_selected/restore/suspend` 信号。
- `rg ... src/ui/month_window.py`：命中 `view_selected/date_selected/restore/suspend`。
- `rg ... src/ui/todo.py`：命中 `req_refresh_all`、详情弹窗回流、跨视图刷新发射。
- `rg ... src/ui/todo_board.py`：命中 `view_stack` 内部路由、picker 返回、`window()/parent` 直接调用主窗口子页面、详情弹窗借道 dashboard、清单删除策略分支。
- `rg ... src/ui`：确认跨文件强耦合主要集中在 `main_window.py` 与 `todo_board.py`。
- `Get-ChildItem src/controllers` + `Get-Content src/controllers/__init__.py`：当前 controller 目录只有空 `__init__.py`，无协调层实现。

### global_signals 当前信号清单与缺口

- 当前信号：
  - `skin_changed()`（无参，兼容约束）
  - `theme_changed(str)`
  - `schedule_added(object)`
  - `schedule_updated(object)`
  - `schedule_deleted(int)`
  - `category_changed()`
- 缺口判断（面向第六轮协调）：
  - 缺少显式“视图路由请求”信号（如 view intent）。
  - 缺少“刷新域”信号（如 dashboard/todo/week/month 精确刷新域）。
  - 缺少“picker 返回结果”统一总线信号。
  - 缺少“详情弹窗回流完成”统一信号。
  - 结论：当前信号足够做兼容并行接入试点，但不足以完全替代跨窗口直连调用。

### 跨视图耦合地图

- 主视图切换链路：
  - `MainWindow.switch_view` 直接控制 `body_stack` 与 `WeekWindow`/`MonthWindow` show/hide/position。
  - 同时处理 dashboard/todo/week/month/suspend 路由状态。
- 添加页来源与返回链路：
  - `source_view_for_add` 存于 `MainWindow`，由当前页决定 add 返回目标。
  - `WeekWindow`、`TodoBoardWindow`存在各自内部 add/picker 逻辑，未统一。
- time/alarm/list picker add/edit 返回链路：
  - `MainWindow`：`time_picker_mode/alarm_picker_mode/list_picker_mode/list_picker_source` 决定返回页与写回目标。
  - `WeekWindow`：独立 `go_to_* / back_from_* / on_list_confirmed`。
  - `TodoBoardWindow`：独立 `view_stack` + list picker 返回。
- 日程/待办保存后的刷新链路：
  - `MainWindow`内多处直接 `page_dashboard.refresh_data()`、`page_todo.refresh_data()`、`_refresh_week_if_visible()`。
  - `WeekWindow.schedule_updated` 回传 `MainWindow` 后再触发 dashboard refresh。
- 清单新增/删除/修改后的刷新链路：
  - `TodoBoardWindow` 直接 `window().refresh_data()` + `notify_main_window_refresh()` + parent 页面直刷。
  - 删除策略逻辑与刷新调用在同文件聚合。
- 周/月/待办窗口与主窗口信号链路：
  - `WeekWindow`: `restore_requested/suspend_requested/view_selected/request_schedule_detail/schedule_updated`。
  - `MonthWindow`: `restore_requested/suspend_requested/view_selected/date_selected`。
  - `TodoView`: `req_change_view/req_refresh_all/req_edit_list`。
- 详情弹窗打开与更新后的刷新回流：
  - `WeekWindow.request_schedule_detail -> MainWindow -> Dashboard._show_detail_popup`。
  - `TodoBoardWindow._show_detail_popup` 直接借道 `main_win.page_dashboard._show_detail_popup(...)`。
  - `TodoView`、`DashboardView` 弹窗更新后分别直连本视图 refresh + `req_refresh_all`。
- 跨文件直接调用热点：
  - `todo_board.py` 中大量 `self.window()/parent/page_dashboard/page_todo` 直接操作。
  - `main_window.py` 承担路由、picker 状态、跨视图刷新和弹窗回流，职责过重。

### 耦合点风险等级

- 高风险：
  - `MainWindow.switch_view`（多窗口生命周期 + 位置控制 + 视图状态联动）。
  - `TodoBoardWindow` 对 `page_dashboard/page_todo` 的直接调用链。
  - 详情弹窗跨视图回流（week/todo_board -> dashboard popup -> 多视图刷新）。
  - picker add/edit 状态分散在 `MainWindow/WeekWindow/TodoBoardWindow`。
- 中风险：
  - `req_refresh_all` 广播式刷新（可能重复刷新但行为可回归）。
  - `WeekWindow.schedule_updated` 与 `MainWindow._on_week_schedule_updated` 联动。
  - 月视图 `date_selected` 跳转到 dashboard 的路径。
- 低风险：
  - 纯路由映射（view_name -> target view decision）本身。
  - refresh 目标注册表（不改触发时机，仅聚合调用）。
  - controller 空骨架与轻量 import 接入。

### 第六轮迁移建议分类

- 适合第六轮迁移：
  - `6-1` 先建 `MainController/ViewRouter/RefreshCoordinator` 最小骨架并保证可 import。
  - `6-2` 仅接管 `switch_view` 的“路由决策映射”，Qt 实际 show/hide 仍在 `MainWindow`。
  - `6-5` 建立 `RefreshCoordinator`，先聚合 refresh 目标，不改触发时机。
  - `6-6` 做单点 EventBus 并行通知试点，保留旧直连刷新链路。
- 需要先做行为基线再决定：
  - picker add/edit 返回状态接管（`source_view_for_add` + 三种 picker mode/source）。
  - 详情弹窗回流链路接管（week/todo_board 来源保持）。
  - TodoBoard 的清单操作后跨视图刷新顺序。
- 应推迟到第八轮 UI 拆分：
  - `TodoBoardWindow` 大文件结构拆分。
  - `MainWindow` 超长流程分段重排与方法分仓。
  - Week/Month/Todo 的大规模页面组织重构。
- 不应迁移或暂不迁移：
  - 旧 `global_signals.skin_changed` 签名与触发语义。
  - Data/Repository/Service 写入行为与 API 语义。
  - UI 布局、文案、交互流程。

### 是否需要后续补充 EventBus 信号

- 需要，但应分阶段补充：
  - 建议新增“路由请求”“刷新域请求”“picker 结果回流”“详情回流完成”四类兼容增强信号。
  - 仅并行接入，不替换旧信号签名和旧直连路径，避免一次性风险。

### diff 范围检查结果

- `git diff --name-only -- src` -> 无输出。
- `git diff --name-only -- main.py` -> 无输出。
- `git diff --name-only -- requirements.txt` -> 无输出。
- `git diff --name-only -- schedule.db` -> 无输出。
- `git diff --name-only` -> 写入本日志前仅 `manage_instruction/Work_Task_Prompts.md`；写入本日志后为 `manage_instruction/Work_Log.md`、`manage_instruction/Work_Task_Prompts.md`。
- `git status --short --branch` -> 写入本日志前仅 `M manage_instruction/Work_Task_Prompts.md`；写入本日志后另含 `M manage_instruction/Work_Log.md`。

### 未完成事项

- 待顾问窗口下发 `6-1` 正式提示词，确认 controller 骨架文件命名与最小职责边界。

### 风险或疑点

- `TodoBoardWindow` 当前对主窗口子页面的直接访问较多，迁移时必须保持刷新顺序与弹窗回流行为。
- `MainWindow` 同时处理路由、picker 状态和刷新协调，任何接管都需要小步验证并保留兜底旧路径。

## 2026-05-25 第六轮 6-1（Controller / Router / Coordinator 最小骨架）

- 本轮任务名称：第六轮 6-1（Controller / Router / Coordinator 最小骨架）。
- 开工前 git 状态：
  - `git status --short --branch` -> `## main...temp/main [ahead 1]`，`M manage_instruction/Work_Task_Prompts.md`。
  - 结论：开工前已有管理文档 diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/controllers/__init__.py`
  - `src/controllers/main_controller.py`
  - `src/controllers/view_router.py`
  - `src/controllers/refresh_coordinator.py`
  - `manage_instruction/Work_Log.md`
- 新增或完善的 controller 文件：
  - `src/controllers/main_controller.py`
  - `src/controllers/view_router.py`
  - `src/controllers/refresh_coordinator.py`
- MainController 当前职责边界：
  - 只组合 `ViewRouter` 与 `RefreshCoordinator`。
  - 仅提供视图名归一化/判断与刷新回调触发代理方法。
  - 不持有具体 UI 实例，不执行 Qt 路由操作，不写数据库。
- ViewRouter 当前职责边界：
  - 只做视图名纯判断与归一化（`day/week/month/todo`）。
  - 提供 `normalize_view_name / is_known_view / resolve_or_default`。
  - 不涉及 `show/hide/setCurrentWidget` 或任何 QWidget 行为。
- RefreshCoordinator 当前职责边界：
  - 只做刷新回调注册、移除和显式触发。
  - 不自动连接 UI，不连接信号总线，不写数据库。
- `__init__.py` 导出说明：
  - 仅轻量导出 `MainController`、`ViewRouter`、`RefreshCoordinator`。
  - 无 UI 创建、无数据库连接、无信号连接副作用。

### 验证结果

- import 验证命令和结果：
  - 命令：
    - `python -c "from src.controllers.main_controller import MainController; from src.controllers.view_router import ViewRouter; from src.controllers.refresh_coordinator import RefreshCoordinator; import src.controllers as controllers; ..."`
  - 结果：
    - 输出 `controller imports ok`
    - `True True True True`
- py_compile 验证命令和结果：
  - 命令：
    - `python -m py_compile src/controllers/main_controller.py src/controllers/view_router.py src/controllers/refresh_coordinator.py src/controllers/__init__.py`
  - 结果：通过（无输出）。
- 静态依赖检查结果：
  - 命令：
    - `rg -n "QWidget|QStackedWidget|PyQt|PySide|MainWindow|WeekWindow|MonthWindow|TodoView|TodoBoard|db_manager|Repository|ScheduleRepository|CategoryRepository|add_schedule|update_schedule|delete_schedule|soft_delete|hard_delete" src/controllers`
  - 结果：无输出（退出码 1，视为通过）。

### 禁止范围检查

- `src/ui` 是否无 diff：
  - 是，`git diff --name-only -- src/ui` 无输出。
- `src/data` 是否无 diff：
  - 是，`git diff --name-only -- src/data` 无输出。
- `src/repositories` 是否无 diff：
  - 是，`git diff --name-only -- src/repositories` 无输出。
- `src/services` 是否无 diff：
  - 是，`git diff --name-only -- src/services` 无输出。
- `src/utils/signals.py` 是否无 diff：
  - 是，`git diff --name-only -- src/utils/signals.py` 无输出。
- `main.py`、`requirements.txt`、`schedule.db` 是否无 diff：
  - 是，三者 `git diff --name-only -- ...` 均无输出。

### 最终 diff 范围检查结果

- `git diff --name-only`（仅 tracked diff）：
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
  - `src/controllers/__init__.py`
  - 写入本日志后另含 `manage_instruction/Work_Log.md`
  - 注：`src/controllers/main_controller.py`、`src/controllers/refresh_coordinator.py`、`src/controllers/view_router.py` 为本轮新增未跟踪文件，需以 `git status --short --branch` 复核。
- `git status --short --branch`：
  - `## main...temp/main [ahead 1]`
  - `M manage_instruction/Work_Task_Prompts.md`
  - `M src/controllers/__init__.py`
  - `?? src/controllers/main_controller.py`
  - `?? src/controllers/refresh_coordinator.py`
  - `?? src/controllers/view_router.py`
  - 写入本日志后另含 `M manage_instruction/Work_Log.md`

### 未完成事项

- 待顾问窗口下发 `6-2` 正式提示词，决定是否接管 `switch_view` 的低风险路由决策映射。

### 风险或疑点

- 当前 controller 仅是边界骨架，尚未接入 UI，实际价值依赖后续小步接管工单。
- 后续接入时必须先保持旧路径并行，再逐步替换，避免跨窗口刷新顺序回归。

## 2026-05-25 第六轮 6-2（ViewRouter 视图切换基线与低风险接管）

- 本轮任务名称：第六轮 6-2（ViewRouter 视图切换基线与低风险接管）。
- 开工前 git 状态：
  - `git status --short --branch` 延续 6-1 收尾状态：`## main...temp/main [ahead 2]`，仅有 `M manage_instruction/Work_Task_Prompts.md` 作为开工前既有管理文档 diff。
  - 结论：开工前已有管理文档 diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/controllers/view_router.py`
  - `src/ui/main_window.py`
  - `manage_instruction/Work_Log.md`

### switch_view 旧行为基线

- `view_name == "week"`：
  - 主窗口 `hide()`
  - `week_window.refresh_week_data()`
  - 若有天气数据则 `week_window.update_weather_ui(...)`
  - 按主窗口中心计算位置后 `week_window.move(...); week_window.show()`
- `view_name == "month"`：
  - 主窗口 `hide()`
  - 若有天气数据则 `month_window.update_weather_ui(...)`
  - 按主窗口中心计算位置后 `month_window.move(...); month_window.show()`
- `view_name == "todo"`：
  - `body_stack.setCurrentWidget(self.page_todo)`
  - `page_todo.refresh_data()`
- `view_name == "day"`：
  - `body_stack.setCurrentWidget(self.page_dashboard)`
  - `page_dashboard.refresh_data()`
- `view_name == "priority"`：
  - `show_toast("准备切换至：四象限视图")`
- 未知 `view_name`：
  - `show_toast(f"准备切换至：{view_name}")`
- 从可见 `week_window` 切到非 week：
  - 主窗口移动到周视图中心后 `week_window.hide(); self.show()`
- 从可见 `month_window` 切到非 month：
  - 主窗口移动到月视图中心后 `month_window.hide(); self.show()`

### 本轮实现

- ViewRouter 新增方法名：
  - `classify_main_view(view_name)`
- 方法语义：
  - 仅精确匹配 `day/week/month/todo/priority`
  - 未知返回 `None`
  - 不做 `strip()`/`lower()`，保持 `switch_view` 旧分支匹配语义
- 为什么不直接使用 `normalize_view_name`：
  - `normalize_view_name` 会 `strip/lower`，会把 `" WEEK "`/`"Week"` 归一化，改变旧 `switch_view` 对未知输入的 toast 行为。
- MainWindow.switch_view 最小替换说明：
  - 新增 `route_action = ViewRouter.classify_main_view(view_name)`
  - 分支判断从 `view_name == ...` / `view_name != ...` 改为 `route_action == ...` / `route_action != ...`
  - Qt 操作代码（`hide/show/move/setCurrentWidget/refresh_data/refresh_week_data/update_weather_ui/show_toast`）全部保留在 `MainWindow`
  - 除 `switch_view` 处新增 `ViewRouter` import 外，无其他流程变更
- `priority` 分支是否保持原行为：
  - 是，仍为 `show_toast("准备切换至：四象限视图")`
- 未知 `view_name` 是否保持原 toast 行为：
  - 是，仍为 `show_toast(f"准备切换至：{view_name}")`

### 验证结果

- `py_compile` 验证结果：
  - 命令：`python -m py_compile src/controllers/view_router.py src/ui/main_window.py`
  - 结果：通过（无输出）
- ViewRouter 纯行为验证结果：
  - `day/week/month/todo/priority` 正确识别
  - `bad` 返回 `None`
  - `" WEEK "`、`"Week"` 返回 `None`
  - 结果：通过（输出 `view router exact switch behavior ok`）
- controller import 回归结果：
  - 命令通过，输出 `controller imports ok`
- MainWindow import 或兜底验证结果：
  - `from src.ui.main_window import MainWindow` 通过，输出 `main window import ok True`
- ViewRouter 静态依赖检查结果：
  - 命令：`rg -n "QWidget|QStackedWidget|PyQt|PySide|MainWindow|WeekWindow|MonthWindow|TodoView|TodoBoard|db_manager|Repository|ScheduleRepository|CategoryRepository" src/controllers/view_router.py`
  - 结果：无输出（退出码 1，视为通过）

### 禁止范围 diff 检查结果

- `src/ui/week_window.py`：无 diff
- `src/ui/month_window.py`：无 diff
- `src/ui/todo.py`：无 diff
- `src/ui/todo_board.py`：无 diff
- `src/data`：无 diff
- `src/repositories`：无 diff
- `src/services`：无 diff
- `src/utils/signals.py`：无 diff
- `main.py`：无 diff
- `requirements.txt`：无 diff
- `schedule.db`：无 tracked diff

### 最终 diff 范围检查结果

- `git diff --name-only`：
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
  - `src/controllers/view_router.py`
  - `src/ui/main_window.py`
  - 写入本日志后另含 `manage_instruction/Work_Log.md`
- `git status --short --branch`：
  - `## main...temp/main [ahead 2]`
  - `M manage_instruction/Work_Task_Prompts.md`
  - `M src/controllers/view_router.py`
  - `M src/ui/main_window.py`
  - 写入本日志后另含 `M manage_instruction/Work_Log.md`

### 未完成事项

- 待顾问窗口下发 `6-3` 正式提示词，进入 add/picker 返回状态基线审查。

### 风险或疑点

- `switch_view` 仍是多职责方法，本轮仅接管低风险字符串决策；后续若继续迁移需保持行为基线与回归用例。

## 2026-05-25 第六轮 6-3（添加页来源与 picker 返回状态基线）

- 本轮任务名称：第六轮 6-3（添加页来源与 picker 返回状态基线）。
- 开工前 git 状态：
  - `git status --short --branch` -> `## main...temp/main [ahead 3]`
  - 开工前既有 diff：`M manage_instruction/Work_Task_Prompts.md`
  - 结论：开工前已有管理文档 diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`

### 读取的阶段合同和 6-0/6-1/6-2 结论

- `6-3` 仅允许静态审查和日志记录，不改 `src`。
- 本轮需输出添加页来源与 picker 返回链路地图、状态字段写入/读取/返回目标表、风险等级和 6-4 建议。
- 延续 6-0/6-1/6-2 约束：不做跨窗口大迁移，不在 6-4 同时触碰 MainWindow/WeekWindow/TodoBoardWindow 全量链路。

### 静态搜索命令和关键结果

- MainWindow 添加页来源与返回：
  - `rg -n "source_view_for_add|page_add\\.btn_cancel|on_schedule_saved|handle_header_action|setCurrentWidget\\(self\\.page_add|return_target|page_add\\.reset|default_to_schedule|body_stack\\.currentWidget" src/ui/main_window.py`
  - 关键命中：`126-127, 491-497, 499-565`。
- MainWindow time picker：
  - `rg -n "time_picker_mode|...|editing_schedule|setCurrentWidget\\(self\\.page_time|..." src/ui/main_window.py`
  - 关键命中：`131-137, 268-336`。
- MainWindow alarm picker：
  - 命中：`139-143, 369-424`。
- MainWindow list picker：
  - 命中：`145-152, 427-488, 455-463`。
- WeekWindow 添加页与 picker：
  - `rg -n "page_add\\.btn_cancel|on_schedule_saved|switch_to_main_board|time_picker_mode|alarm_picker_mode|list_picker_mode|..." src/ui/week_window.py`
  - 关键命中：`748-761, 774-927`。
- TodoBoardWindow list picker / inline add：
  - `rg -n "inline_add_view|page_list|list_picker_mode|current_folder_id|current_folder_name|..." src/ui/todo_board.py`
  - 关键命中：`1223-1224, 1529-1660, 1692-1708, 1905-1957`。
- 代码片段阅读：
  - `main_window.py`：`Select-Object -Skip 110 -First 390` + `-Skip 500 -First 80`
  - `week_window.py`：`-Skip 730 -First 260`
  - `todo_board.py`：`-Skip 1510 -First 260` + `-Skip 1888 -First 95`

### MainWindow 添加页来源与返回链路地图

- 添加页取消：
  - `page_add.btn_cancel` -> `setCurrentWidget(getattr(source_view_for_add, page_dashboard))`（`main_window.py:126-127`）。
- 添加页保存：
  - `on_schedule_saved()` 内 `return_target = getattr(source_view_for_add, page_dashboard)` 后返回（`491-497`）。
  - 保存后还会 `page_dashboard.refresh_data()`、`page_todo.refresh_data()`、`_refresh_week_if_visible()`（`491-494`）。
- 进入添加页：
  - `switch_to_add_page()` 在当前页为 dashboard/todo 时写入 `source_view_for_add = current_widget`（`558-559`）。
  - 来源是 todo 时 `default_to_schedule=False`，否则 `True`（`562-563`）。
  - 若当前已在添加页，再点 add 会按 `source_view_for_add` 返回（`552-554`）。
- Header 触发：
  - `handle_header_action('add')` -> `switch_to_add_page()`（`499-501`）。

### MainWindow time/alarm/list picker add/edit 返回链路地图

- Time picker：
  - add 模式：`time_picker_mode='add'`（`270`）-> `back_from_time_picker()` 返回 `page_add`（`304-307`）。
  - edit 模式：`time_picker_mode='edit'` + `editing_schedule`（`290-291`）-> 返回 `page_dashboard`（`304-309`）。
  - edit 确认后触发：写库更新 + `page_dashboard/page_todo/_refresh_week_if_visible` + popup 刷新后返回（`316-336`）。
- Alarm picker：
  - add 模式：返回 `page_add`（`394-395`）。
  - edit 模式：返回 `page_dashboard`（`396-397`）。
  - edit 确认后触发：写库更新 + `page_dashboard/page_todo/_refresh_week_if_visible` + popup 刷新后返回（`404-424`）。
- List picker：
  - add 模式：返回 `page_add`（`456-457`）。
  - edit 模式：先写 `list_picker_source`（`445`），返回时按来源：
    - `todo` -> `page_todo`（`460-461`）
    - 否则 -> `page_dashboard`（`463`）
  - edit 确认后触发：写库更新 + `page_dashboard/page_todo/_refresh_week_if_visible` + popup 刷新后返回（`470-488`）。

### WeekWindow 添加页与 picker 返回链路地图

- 添加页取消：
  - `page_add.btn_cancel` -> `switch_to_main_board()`（`748, 777-778`）。
- 添加页保存：
  - `on_schedule_saved()` -> `switch_to_main_board()` + `refresh_week_data()`（`782-784`）。
- picker add/edit 返回：
  - time：edit 返回 `switch_to_main_board()`；add 返回 `page_add`（`810-815`）。
  - alarm：edit 返回 `switch_to_main_board()`；add 返回 `page_add`（`859-863`）。
  - list：edit 返回 `switch_to_main_board()`；add 返回 `page_add`（`904-908`）。
- edit 确认后刷新回流：
  - 三个 picker 在 edit 确认后均 `refresh_week_data()` + `schedule_updated.emit(editing_schedule)`（`827-833, 876-882, 919-925`）。

### TodoBoardWindow list picker 与 inline add 返回链路地图

- inline add 进入 list picker：
  - `inline_add_view.req_open_list_picker` -> `go_to_list_picker()`（`1544, 1550-1555`）。
  - 进入 picker 后 `view_stack` 切到 `page_list`，并临时隐藏顶部按钮（`1555-1561`）。
- edit 进入 list picker：
  - `go_to_list_picker_for_edit()` 设置 `list_picker_mode='edit'` + `editing_schedule`，切到 `page_list`（`1564-1573`）。
- picker 返回：
  - `back_from_list_picker()` 先根据 `current_folder_id/current_folder_name` 恢复标题与按钮（`1582-1599`）。
  - edit/manage 模式根据 `in_folder + view_mode + current_todos` 回到 `empty/stick/folder`（`1602-1610`）。
  - add 模式固定回 `inline_add_view`（`1613-1614`）。
- picker 确认：
  - edit：写库更新后 `refresh_data()` + `notify_main_window_refresh()` + popup 回流，再 `back_from_list_picker()`（`1620-1649`）。
  - add：给 `inline_add_view` 设分类后返回 `back_from_list_picker()`（`1659-1660`）。
- `current_folder_id/current_folder_name` 影响：
  - 文件夹进入写入（`1692-1693`），返回主看板重置（`1707-1708`）。
  - add 入口会把当前 folder 分类预填到 inline_add（`1907-1910`）。

### 状态字段清单（写入点 / 读取点 / 返回目标）

- `source_view_for_add`（MainWindow）：
  - 写入：`switch_to_add_page()`（`558-559`）
  - 读取：`btn_cancel`、`on_schedule_saved`、二次点击 add（`126-127, 496, 553`）
  - 返回目标：`page_dashboard` 或 `page_todo`
- `list_picker_source`（MainWindow）：
  - 写入：`go_to_list_picker_for_edit(..., source_view)`（`445`）
  - 读取：`back_from_list_picker()`（`460-463`）
  - 返回目标：edit 返回 `todo` 或 `dashboard`
- `time_picker_mode`（MainWindow/WeekWindow）：
  - 写入：`go_to_time_picker`/`go_to_time_picker_for_edit`（Main `270/290`，Week `788/799`）
  - 读取：`back_from_time_picker`、`on_time_confirmed`
  - 返回目标：Main add->`page_add`，edit->`page_dashboard`；Week add->`page_add`，edit->`page_week_board`
- `alarm_picker_mode`（MainWindow/WeekWindow）：
  - 写入：`go_to_alarm_picker`/`go_to_alarm_picker_for_edit`
  - 读取：`back_from_alarm_picker`、`on_alarm_confirmed`
  - 返回目标：Main add->`page_add`，edit->`page_dashboard`；Week add->`page_add`，edit->`page_week_board`
- `list_picker_mode`（MainWindow/WeekWindow/TodoBoardWindow）：
  - 写入：`go_to_list_picker`/`go_to_list_picker_for_edit`
  - 读取：`back_from_list_picker`、`on_list_confirmed`
  - 返回目标：
    - Main：add->`page_add`，edit->`page_todo`/`page_dashboard`
    - Week：add->`page_add`，edit->`page_week_board`
    - TodoBoard：add->`inline_add_view`，edit/manage->`stick/folder/empty` 动态
- `editing_schedule`（MainWindow/WeekWindow/TodoBoardWindow）：
  - 写入：各 picker `go_to_*_for_edit`
  - 读取：各 picker `on_*_confirmed` edit 分支
  - 返回目标：通过 `back_from_*` 返回到对应上级页面，同时驱动 popup/refresh 回流
- `current_folder_id/current_folder_name`（TodoBoardWindow）：
  - 写入：`_open_folder_view`（`1692-1693`），`_back_to_folder_view` 重置（`1707-1708`）
  - 读取：`back_from_list_picker`、`_on_add_clicked`、`_on_inline_add_canceled`、`refresh_data` 过滤
  - 返回目标：决定 `view_stack` 退回 `folder/stick/empty/inline_add`，并影响标题/按钮状态

### 风险等级

- 低风险：
  - MainWindow `source_view_for_add` 的来源记录与返回目标决策（纯状态+路由，不直接触写库）。
  - MainWindow `list_picker_source` 的 edit 返回目标决策（`todo/dashboard` 二选一）。
- 中风险：
  - WeekWindow 内部 picker add/edit 返回决策（单文件内，但联动 `schedule_updated.emit` 与 `refresh_week_data`）。
- 高风险：
  - MainWindow 三类 picker edit 分支（涉及写库、重复规则弹窗、跨视图刷新顺序）。
  - TodoBoardWindow `list_picker_mode + current_folder_id/current_folder_name + view_mode + view_stack` 组合状态机。
  - TodoBoard edit 路径对主窗口 dashboard popup 的回流联动。

### 适合 6-4 最小接管的候选项

- 建议仅接管一个最低风险闭环：
  - **MainWindow 添加页来源返回决策闭环**（`source_view_for_add` 写入 + cancel/save 返回目标读取）
  - 理由：单文件、纯路由状态、不涉及写库和跨窗口生命周期，回归面最小。

### 不适合 6-4 接管、应推迟或继续拆分的项

- 不建议在 6-4 一次性迁移 MainWindow 全部 picker 状态（time/alarm/list）。
- 不建议在 6-4 同时碰 WeekWindow 与 TodoBoardWindow。
- TodoBoard 的 list picker + inline add + folder/stick 状态机建议推迟到第八轮 UI 拆分前后，或至少另拆独立基线工单再做。

### diff 范围检查结果

- `git diff --name-only -- src` -> 无输出。
- `git diff --name-only -- main.py` -> 无输出。
- `git diff --name-only -- requirements.txt` -> 无输出。
- `git diff --name-only -- schedule.db` -> 无输出。
- `git diff --name-only` -> `manage_instruction/Work_Log.md`、`manage_instruction/Work_Task_Prompts.md`（后者为开工前既有）。
- `git status --short --branch` -> `## main...temp/main [ahead 3]`，`M manage_instruction/Work_Log.md`，`M manage_instruction/Work_Task_Prompts.md`。

### 未完成事项

- 待顾问窗口下发 `6-4` 正式提示词，确认是否仅接管 MainWindow `source_view_for_add` 最小闭环。

### 风险或疑点

- MainWindow picker edit 分支与写库/刷新顺序耦合较重，若进入接管需先做单路径行为回归脚本。
- TodoBoard 当前状态机依赖 `current_folder_id + view_mode + current_todos` 多条件组合，提前迁移会引入高回归风险。

## 2026-05-25 第六轮 6-4（添加页来源与 picker 返回状态最小接管）

- 本轮任务名称：第六轮 6-4（添加页来源与 picker 返回状态最小接管）。
- 开工前 git 状态：
  - `git status --short --branch` -> `## main...temp/main [ahead 4]`
  - 开工前既有 diff：`M manage_instruction/Work_Task_Prompts.md`
  - 结论：开工前已有管理文档 diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/controllers/main_controller.py`
  - `src/ui/main_window.py`
  - `manage_instruction/Work_Log.md`
- 是否进入源码修改分支：是（按 6-4 条件执行，仅接管最低风险闭环）。

### 接管的具体字段/路径

- `source_view_for_add` 写入决策：
  - `MainWindow.switch_to_add_page` 中改为调用 `MainController.resolve_add_source(...)`。
- 添加页取消返回目标：
  - `page_add.btn_cancel` 回调改为调用 `MainController.resolve_add_return_target(...)`。
- 添加页保存后返回目标：
  - `MainWindow.on_schedule_saved` 的 `return_target` 改为调用 `MainController.resolve_add_return_target(...)`。
- 添加页再次点击 add 的返回目标：
  - `switch_to_add_page` 中“当前已在 page_add”分支改为调用 `MainController.resolve_add_return_target(...)`。
- `default_to_schedule` 判断：
  - `switch_to_add_page` 中改为调用 `MainController.default_to_schedule_for_add(...)`。

### MainController 新增方法名和语义

- 新增方法：
  - `resolve_add_source(current_widget, dashboard_widget, todo_widget, existing_source=None)`
  - `resolve_add_return_target(source_view, dashboard_widget)`
  - `default_to_schedule_for_add(current_widget, todo_widget)`
- 语义：
  - 仅做对象比较和返回目标选择，不执行任何 UI 操作，不写数据库，不依赖 Qt/UI/db/Repository。

### MainWindow 最小替换说明

- 仅替换 `source_view_for_add` 闭环中的纯决策部分，Qt 实际操作仍在 MainWindow：
  - `setCurrentWidget(...)` 仍在 MainWindow。
  - `page_add.reset(...)` 仍在 MainWindow。
  - 保存后刷新顺序保持原样：
    - `page_dashboard.refresh_data()`
    - `page_todo.refresh_data()`
    - `_refresh_week_if_visible()`
- `handle_header_action` 未修改。
- `switch_view` 逻辑未修改。

### 未接管路径及原因

- `time picker`：未接管。原因：涉及 edit 写库、重复规则确认、跨视图刷新回流，风险高于本轮边界。
- `alarm picker`：未接管。原因同上。
- `list picker`：未接管。原因：除写库外还涉及 `list_picker_source` 和 todo/dashboard 返回分支，不属于本轮最小闭环。
- `WeekWindow`：未接管。原因：本轮明确禁止触碰。
- `TodoBoardWindow`：未接管。原因：本轮明确禁止触碰，且状态机复杂度高。

### 验证结果

- `py_compile` 验证结果：
  - 命令：`python -m py_compile src/controllers/main_controller.py src/ui/main_window.py`
  - 结果：通过（无输出）。
- MainController 纯决策行为验证结果：
  - 命令按提示词断言 `resolve_add_source/resolve_add_return_target/default_to_schedule_for_add`。
  - 结果：通过，输出 `main controller add source behavior ok`。
- controller import 回归结果：
  - 通过，输出 `controller imports ok`。
- MainWindow import 或兜底验证结果：
  - 通过，输出 `main window import ok True`。
- MainController 静态依赖检查结果：
  - 命令：`rg -n "QWidget|QStackedWidget|PyQt|PySide|MainWindow|WeekWindow|MonthWindow|TodoView|TodoBoard|db_manager|Repository|ScheduleRepository|CategoryRepository|add_schedule|update_schedule|delete_schedule|soft_delete|hard_delete|setCurrentWidget|refresh_data" src/controllers/main_controller.py`
  - 结果：无输出（退出码 1，视为通过）。

### 禁止范围 diff 检查结果

- `src/controllers/refresh_coordinator.py`：无 diff。
- `src/controllers/__init__.py`：无 diff。
- `src/ui/week_window.py`：无 diff。
- `src/ui/month_window.py`：无 diff。
- `src/ui/todo.py`：无 diff。
- `src/ui/todo_board.py`：无 diff。
- `src/data`：无 diff。
- `src/repositories`：无 diff。
- `src/services`：无 diff。
- `src/utils/signals.py`：无 diff。
- `main.py`：无 diff。
- `requirements.txt`：无 diff。
- `schedule.db`：无 tracked diff。

### 最终 diff 范围检查结果

- `git diff --name-only`：
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
  - `src/controllers/main_controller.py`
  - `src/ui/main_window.py`
  - 写入本日志后另含 `manage_instruction/Work_Log.md`
- `git status --short --branch`：
  - `## main...temp/main [ahead 4]`
  - `M manage_instruction/Work_Task_Prompts.md`
  - `M src/controllers/main_controller.py`
  - `M src/ui/main_window.py`
  - 写入本日志后另含 `M manage_instruction/Work_Log.md`

### 未完成事项

- 待顾问窗口下发 `6-5` 正式提示词，评估是否进入刷新协调边界建立。

### 风险或疑点

- `source_view_for_add` 闭环已迁入 controller 纯决策，但 MainWindow 内仍存在多个 picker 状态分支，后续若继续迁移需要保持“单闭环、可回归”节奏。

## 2026-05-25 第六轮 6-5（RefreshCoordinator 跨视图刷新边界建立）

- 本轮任务名称：第六轮 6-5（RefreshCoordinator 跨视图刷新边界建立）。
- 开工前 git 状态：
  - `git status --short --branch` -> `## main...temp/main [ahead 5]`
  - 开工前既有 diff：`M manage_instruction/Work_Task_Prompts.md`
  - 结论：开工前已有管理文档 diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/ui/main_window.py`
  - `manage_instruction/Work_Log.md`

### MainWindow 旧刷新基线

- `on_schedule_saved`：
  - 旧逻辑直接顺序调用：
    - `page_dashboard.refresh_data()`
    - `page_todo.refresh_data()`
    - `_refresh_week_if_visible()`
- `on_time_confirmed` edit 分支：
  - 更新成功后直接顺序调用上述三连刷新。
- `on_alarm_confirmed` edit 分支：
  - 更新成功后直接顺序调用上述三连刷新。
- `on_list_confirmed` edit 分支：
  - 更新成功后直接顺序调用上述三连刷新（含“为保险起见”注释）。
- 旧信号连接保留基线：
  - `page_dashboard.req_refresh_all.connect(self._refresh_week_if_visible)`
  - `page_todo.req_refresh_all.connect(self.page_dashboard.refresh_data)`
  - `page_dashboard.req_refresh_all.connect(self.page_todo.refresh_data)`
  - `week_window.schedule_updated.connect(self._on_week_schedule_updated)`

### RefreshCoordinator 当前能力或新增方法说明

- `RefreshCoordinator` 现有 `register/unregister/trigger/trigger_many` 已满足本轮，不新增方法。
- 本轮未修改 `src/controllers/refresh_coordinator.py`，仅复用现有能力。

### 刷新目标注册方式

- 在 MainWindow 新增 `_register_refresh_targets()`，通过 `MainController` 注册三个目标：
  - `dashboard` -> `self.page_dashboard.refresh_data`
  - `todo` -> `self.page_todo.refresh_data`
  - `week_if_visible` -> `self._refresh_week_if_visible`
- 在 `__init__` 中调用 `_register_refresh_targets()` 完成注册。

### 接管的刷新链路

- 新增 `MainWindow._refresh_dashboard_todo_week()`：
  - 使用 `self.main_controller.request_refresh_many(("dashboard", "todo", "week_if_visible"))`
  - 保持原顺序：dashboard -> todo -> week_if_visible
- 用该方法替换四处同构三连刷新：
  - `on_schedule_saved`
  - `on_time_confirmed` edit 分支
  - `on_alarm_confirmed` edit 分支
  - `on_list_confirmed` edit 分支

### 保留的旧直连路径及原因

- 保留 `req_refresh_all` 的旧连接：本轮不改触发时机和信号路径。
- 保留 `week_window.schedule_updated` 旧连接：本轮不改跨窗口更新入口。
- 保留 `_refresh_week_if_visible` 内部可见性判断：本轮仅封装协调调用，不改变判断逻辑。

### 行为保持结论

- 是否保持旧刷新顺序：是。
- 是否保持旧触发时机：是。
- 是否未接 global_signals：是（未新增/未连接 EventBus 信号）。

### 验证结果

- `py_compile` 验证结果：
  - 命令：`python -m py_compile src/controllers/refresh_coordinator.py src/controllers/main_controller.py src/ui/main_window.py`
  - 结果：通过（无输出）。
- RefreshCoordinator 纯行为验证结果：
  - 通过，输出 `refresh coordinator behavior ok`。
- controller import 回归结果：
  - 通过，输出 `controller imports ok`。
- MainWindow import 或兜底验证结果：
  - 通过，输出 `main window import ok True`。
- RefreshCoordinator 静态依赖检查结果：
  - 命令：`rg -n "QWidget|QStackedWidget|PyQt|PySide|MainWindow|WeekWindow|MonthWindow|TodoView|TodoBoard|db_manager|Repository|ScheduleRepository|CategoryRepository|add_schedule|update_schedule|delete_schedule|soft_delete|hard_delete|setCurrentWidget|refresh_data" src/controllers/refresh_coordinator.py`
  - 结果：无输出（退出码 1，视为通过）。
- `signals.py` 是否无 diff：
  - `git diff --name-only -- src/utils/signals.py` -> 无输出。

### 禁止范围 diff 检查结果

- `src/controllers/view_router.py`：无 diff。
- `src/controllers/__init__.py`：无 diff。
- `src/ui/week_window.py`：无 diff。
- `src/ui/month_window.py`：无 diff。
- `src/ui/todo.py`：无 diff。
- `src/ui/todo_board.py`：无 diff。
- `src/data`：无 diff。
- `src/repositories`：无 diff。
- `src/services`：无 diff。
- `main.py`：无 diff。
- `requirements.txt`：无 diff。
- `schedule.db`：无 tracked diff。

### 最终 diff 范围检查结果

- `git diff --name-only`：
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
  - `src/ui/main_window.py`
  - 写入本日志后另含 `manage_instruction/Work_Log.md`
- `git status --short --branch`：
  - `## main...temp/main [ahead 5]`
  - `M manage_instruction/Work_Task_Prompts.md`
  - `M src/ui/main_window.py`
  - 写入本日志后另含 `M manage_instruction/Work_Log.md`

### 未完成事项

- 待顾问窗口下发 `6-6` 正式提示词，再评估 EventBus 并行通知试点。

### 风险或疑点

- 当前仅在 MainWindow 建立刷新协调边界，跨窗口层面的统一刷新治理仍依赖后续小工单逐步收口。

## 2026-05-25 第六轮 6-6（EventBus 并行通知试点）

- 本轮任务名称：第六轮 6-6（EventBus 并行通知试点）。
- 开工前 git 状态：
  - `git status --short --branch` -> `## main...temp/main [ahead 6]`
  - 开工前既有 diff：`M manage_instruction/Work_Task_Prompts.md`
  - 结论：开工前已有管理文档 diff，不视为本轮源码改动。
- 实际修改文件：
  - `src/utils/signals.py`
  - `src/ui/main_window.py`
  - `manage_instruction/Work_Log.md`

### 选择的低风险通知点

- 选点：`MainWindow._refresh_dashboard_todo_week()`
- 原因：
  - 该方法已在 6-5 统一封装 Dashboard/Todo/Week 三连刷新。
  - 触发点清晰、影响面可控。
  - 可在旧刷新执行后追加并行通知，不改变现有刷新主路径。

### 新增或复用的 EventBus 信号

- 在 `src/utils/signals.py` 的 `AppSignals` 中新增：
  - `refresh_requested = pyqtSignal(str)`
- `global_signals` 名称保留，未改实例化方式。

### 并行通知接入方式

- 在 `MainWindow._refresh_dashboard_todo_week()` 中保持原逻辑：
  - `self.main_controller.request_refresh_many(("dashboard", "todo", "week_if_visible"))`
- 在其后追加：
  - `global_signals.refresh_requested.emit("dashboard_todo_week")`
- 结论：
  - 旧刷新路径仍执行。
  - 新 EventBus 通知仅作并行增强，不参与实际 UI 刷新决策。

### payload 语义

- `refresh_requested` 的 payload 为字符串刷新域：
  - 本轮试点值：`"dashboard_todo_week"`
- 语义：表示该刷新域已请求/已执行对应协调刷新，供后续兼容监听扩展。

### 兼容性与约束结论

- `skin_changed` 是否保持无参签名：是（`pyqtSignal()` 未改）。
- 其他旧信号签名是否保持：
  - `theme_changed(str)`：保持
  - `schedule_added(object)`：保持
  - `schedule_updated(object)`：保持
  - `schedule_deleted(int)`：保持
  - `category_changed()`：保持
- 是否未连接任何 UI 监听新信号：是（本轮只 emit，不新增 connect）。
- 是否未修改 WeekWindow / TodoView / TodoBoardWindow / MonthWindow：是。
- 是否未改刷新顺序：是（dashboard -> todo -> week_if_visible 仍保持）。

### 验证结果

- `py_compile` 验证结果：
  - 命令：`python -m py_compile src/utils/signals.py src/ui/main_window.py`
  - 结果：通过（无输出）。
- `global_signals` 兼容性和新信号验证结果：
  - 命令按提示词验证 `skin_changed` 与 `refresh_requested`。
  - 结果：通过，输出 `global signals compatibility ok`。
- MainWindow import 或兜底验证结果：
  - 通过，输出 `main window import ok True`。
- 静态检查结果：
  - `rg -n "_refresh_dashboard_todo_week|request_refresh_many|refresh_requested|global_signals|page_dashboard\\.refresh_data|page_todo\\.refresh_data|_refresh_week_if_visible" src/ui/main_window.py src/utils/signals.py`
  - 结果确认：
    - 旧刷新调用仍在。
    - `refresh_requested` 仅在 `_refresh_dashboard_todo_week` 中追加 emit。
  - `rg -n "skin_changed|theme_changed|schedule_added|schedule_updated|schedule_deleted|category_changed|refresh_requested|global_signals" src/utils/signals.py`
  - 结果确认旧信号签名未改，新增 `refresh_requested = pyqtSignal(str)`。

### 禁止范围 diff 检查结果

- `src/controllers/main_controller.py`：无 diff。
- `src/controllers/view_router.py`：无 diff。
- `src/controllers/__init__.py`：无 diff。
- `src/ui/week_window.py`：无 diff。
- `src/ui/month_window.py`：无 diff。
- `src/ui/todo.py`：无 diff。
- `src/ui/todo_board.py`：无 diff。
- `src/data`：无 diff。
- `src/repositories`：无 diff。
- `src/services`：无 diff。
- `main.py`：无 diff。
- `requirements.txt`：无 diff。
- `schedule.db`：无 tracked diff。

### 最终 diff 范围检查结果

- `git diff --name-only`：
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
  - `src/ui/main_window.py`
  - `src/utils/signals.py`
  - 写入本日志后另含 `manage_instruction/Work_Log.md`
- `git status --short --branch`：
  - `## main...temp/main [ahead 6]`
  - `M manage_instruction/Work_Task_Prompts.md`
  - `M src/ui/main_window.py`
  - `M src/utils/signals.py`
  - 写入本日志后另含 `M manage_instruction/Work_Log.md`

### 未完成事项

- 待顾问窗口下发 `6-7` 正式提示词，执行详情弹窗与跨视图刷新回流复核。

### 风险或疑点

- 当前 `refresh_requested` 尚无订阅方，本轮仅验证并行通知可用性；后续若接入监听需确保不造成重复刷新。

## 2026-05-25 第六轮 6-7（详情弹窗与跨视图刷新回流复核）

- 本轮任务名称：第六轮 6-7（详情弹窗与跨视图刷新回流复核）。
- 开工前 git 状态：
  - `git status --short --branch` -> `## main...temp/main [ahead 7]`
  - 开工前既有 diff：`M manage_instruction/Work_Task_Prompts.md`
  - 结论：开工前仅有管理文档 diff，不视为本轮源码改动；本轮不新增源码改动，仅记录复核结论。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`

### 读取的阶段合同和 6-0 ~ 6-6 结论

- 第六轮定位：先做跨视图协调层小步接管，不做 UI 大拆分。
- 本轮 6-7 要求：只读复核详情弹窗来源、更新回流、picker 编辑回流，不做源码改造。
- 6-6 已存在并行 EventBus 通知 `refresh_requested("dashboard_todo_week")`，需评估是否与弹窗回流形成并行风险。

### 静态搜索命令和关键结果

- 命令：
  - `rg -n "_show_detail_popup|request_schedule_detail|req_show_detail|schedule_updated|ScheduleDetailPop|source_view|req_edit_time|req_edit_alarm|req_edit_list|req_refresh_all|refresh_requested" src/ui/dashboard.py src/ui/todo.py src/ui/todo_board.py src/ui/week_window.py src/ui/main_window.py src/ui/schedule_detail_pop.py`
  - `Get-Content ... dashboard.py/todo.py/week_window.py/main_window.py/todo_board.py/schedule_detail_pop.py` 指定片段。
  - `rg -n "source_view|schedule_updated\\.emit|req_edit_time|req_edit_alarm|req_edit_list|delete|soft|hard|update|refresh" src/ui/schedule_detail_pop.py`
- 关键命中：
  - Dashboard 弹窗入口与回流：`dashboard.py:533-548`
  - Todo 弹窗入口与回流：`todo.py:469-480`
  - Week -> Main -> Dashboard 路径：`main_window.py:98-99`，`week_window.py:1044`
  - TodoBoard 借道 Dashboard 路径：`todo_board.py:1858-1867`
  - ScheduleDetailPop 发射点：`schedule_detail_pop.py:563,606,696,715`，编辑信号 `620/623/626`

### 详情弹窗打开来源地图

- Dashboard 卡片：
  - `ScheduleCard.req_show_detail` -> `DashboardView._show_detail_popup(schedule_data, source_view="dashboard")`
  - 位置：`dashboard.py:529, 533`
- TodoView 卡片：
  - `TodoCard.req_show_detail` -> `TodoView._show_detail_popup(schedule_data, source_view="todo")`
  - 位置：`todo.py:466, 469`
- WeekWindow 卡片：
  - `WeekScheduleCard.clicked` -> `WeekWindow.request_schedule_detail.emit(data)`（`week_window.py:1044`）
  - MainWindow 连接：`week_window.request_schedule_detail.connect(lambda data: page_dashboard._show_detail_popup(data, source_view="week"))`
  - 位置：`main_window.py:98-99`
- TodoBoardWindow 卡片：
  - `stick_view.req_show_detail` -> `TodoBoardWindow._show_detail_popup(schedule_data)`（`todo_board.py:1230,1858`）
  - 内部借道：`main_win.page_dashboard._show_detail_popup(schedule_data, source_view="todo_board")`
  - 位置：`todo_board.py:1867`

### 详情弹窗更新回流地图

- Dashboard 来源弹窗：
  - `pop.schedule_updated` 连接：
    - `DashboardView.refresh_data`
    - `DashboardView.req_refresh_all.emit`
  - 位置：`dashboard.py:543-544`
- Todo 来源弹窗：
  - `pop.schedule_updated` 连接：
    - `TodoView.refresh_data`
    - `TodoView.req_refresh_all.emit`
  - 位置：`todo.py:478-479`
- Week 来源弹窗：
  - 本质借道 Dashboard 弹窗机制，`schedule_updated -> Dashboard.req_refresh_all.emit`
  - MainWindow 已连接：
    - `page_dashboard.req_refresh_all -> page_todo.refresh_data`
    - `page_dashboard.req_refresh_all -> _refresh_week_if_visible`
  - 因此 Week 来源更新可通过 Dashboard 全局刷新广播回流周视图（可见时）。
- TodoBoard 来源弹窗：
  - 同样借道 Dashboard 弹窗回流（Dashboard refresh + req_refresh_all）
  - TodoBoard 自身还在 `__init__` 中监听 `parent.page_dashboard.req_refresh_all.connect(self.refresh_data)`（`todo_board.py:1242`）
  - 因此 TodoBoard 来源更新可经 Dashboard 广播回流到 TodoBoard 刷新。

### edit picker 回流地图

- 时间编辑：
  - `ScheduleDetailPop.req_edit_time.emit(self.data)`（`schedule_detail_pop.py:620`）
  - Dashboard 中转：`pop.req_edit_time -> Dashboard.req_edit_time.emit(data, source_view)`（`dashboard.py:546`）
  - MainWindow 接收：`go_to_time_picker_for_edit(schedule_data, source_view)`
  - 分支：`source_view == "week"` 时移交 `week_window.go_to_time_picker_for_edit(...)`（`main_window.py:302-306`）
- 提醒编辑：
  - `ScheduleDetailPop.req_edit_alarm`（`623`） -> Dashboard.req_edit_alarm（`547`） -> MainWindow
  - `source_view == "week"` 时移交周视图（`main_window.py:392-394`）
- 清单编辑：
  - `ScheduleDetailPop.req_edit_list`（`626`）
  - Dashboard/Todo 分别中转到 MainWindow `go_to_list_picker_for_edit(schedule_data, source_view)`
  - MainWindow 分支：
    - `source_view == "week"` -> `week_window.go_to_list_picker_for_edit(...)`
    - `source_view == "todo_board"` -> `todo_board.go_to_list_picker_for_edit(...)`
    - 其他走主窗口 list picker 路径
  - 位置：`main_window.py:449-454`

### ScheduleDetailPop 中 schedule_updated.emit 发射点

- 优先级修改成功后：`schedule_updated.emit()`（`schedule_detail_pop.py:563`）
- 重复规则修改成功后：`schedule_updated.emit()`（`606`）
- 标题修改成功后：`schedule_updated.emit()`（`696`）
- 描述修改成功后：`schedule_updated.emit()`（`715`）

### source_view 当前语义

- `"dashboard"`：主面板来源，使用主面板风格与回流链路。
- `"todo"`：待办来源，回流到 Todo 视图刷新并广播 req_refresh_all。
- `"week"`：周视图来源，但实际仍借道 Dashboard 弹窗机制，风格与分支有所差异。
- `"todo_board"`：待办看板来源，借道 Dashboard 打开弹窗，同时有看板图标提示与后续广播回流。
- `"month"`：在 ScheduleDetailPop 内与 week 同类风格分支（白底详情区域）。

### 直接耦合点

- WeekWindow 通过 MainWindow lambda 借 Dashboard 打开弹窗（`main_window.py:98-99`）。
- TodoBoardWindow 直接调用 `main_win.page_dashboard._show_detail_popup(...)`（`todo_board.py:1867`）。
- Dashboard/Todo 弹窗回流直接连接本视图 refresh 与 `req_refresh_all.emit`。
- ScheduleDetailPop 通过 `source_view` 改变弹窗风格与编辑回流路径分支。
- `req_refresh_all` 与 `refresh_requested` 当前并行存在，但 `refresh_requested` 尚无监听者；暂无重复刷新实效，仅存在未来并行接入风险。

### 风险等级

- 低风险：
  - 仅记录 `source_view` 字符串映射和弹窗来源地图。
  - 将“弹窗更新后刷新域”作为 RefreshCoordinator 注册候选（不改代码）。
- 中风险：
  - 将 Dashboard/Todo 的 `schedule_updated` 回流改为统一 RefreshCoordinator 协调调用。
  - Week 来源弹窗更新回流统一走 MainWindow 刷新协调入口。
- 高风险：
  - TodoBoard 借道 Dashboard 路径迁移。
  - ScheduleDetailPop 的 `source_view` 分支重构。
  - 弹窗内 edit picker 回流迁移（涉及 week/todo_board 双分支）。
  - 弹窗内删除/重复相关更新路径迁移。

### 适合后续接入 RefreshCoordinator 的候选项

- 候选（建议作为单独小工单）：
  - 仅在 Dashboard/Todo 两处 `_show_detail_popup` 中，把 `schedule_updated` 的“刷新动作”统一收敛为 MainWindow 侧已存在的 `_refresh_dashboard_todo_week()` 入口或对应协调接口。
  - 前提：保留 `req_refresh_all` 并行路径，先做行为等价回归。

### 应推迟到第八轮 UI 拆分或另拆工单的项

- TodoBoardWindow 借道 Dashboard 的详情弹窗打开链路（高耦合，建议留待 UI 拆分阶段）。
- ScheduleDetailPop 的 `source_view` 多分支 UI/行为收敛。
- picker 编辑回流（time/alarm/list）跨窗口路径统一。

### 是否建议第六轮继续做详情弹窗源码接管

- 结论：**不建议在当前第六轮继续直接接管详情弹窗主链路**。
- 原因：
  - 当前链路跨 Dashboard/Todo/Week/TodoBoard 多窗口耦合，且包含借道调用。
  - 6-8 临近整体验收，继续接管会增加高回归风险。
- 如必须前进，建议仅做一个最小候选：
  - 只在 Dashboard/Todo 的 `schedule_updated` 后刷新动作做协调层包装，不改弹窗打开来源与 source_view 分支。

### 6-8 整体验收前需要重点回归的弹窗行为

- Dashboard 来源弹窗：编辑 title/desc/priority/repeat 后是否触发本页刷新 + 全局刷新。
- Todo 来源弹窗：编辑 list 后 Todo 列表与主面板同步是否正常。
- Week 来源弹窗：通过 MainWindow lambda 借道打开后，更新是否回流周视图（可见时）。
- TodoBoard 来源弹窗：借道 Dashboard 打开后，看板是否通过 `req_refresh_all` 监听回流刷新。
- 弹窗编辑入口：
  - `req_edit_time/alarm/list` 的 source_view 分支是否仍正确落在 Main/Week/TodoBoard 对应路径。
- 并行信号：
  - `refresh_requested("dashboard_todo_week")` 的 emit 不应破坏现有 `req_refresh_all` 刷新行为。

### diff 范围检查结果

- `git diff --name-only -- src`：
  - 无输出。
- `git diff --name-only -- main.py`：无输出。
- `git diff --name-only -- requirements.txt`：无输出。
- `git diff --name-only -- schedule.db`：无输出。
- `git diff --name-only`：
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
- `git status --short --branch`：
  - `## main...temp/main [ahead 7]`
  - `M manage_instruction/Work_Log.md`
  - `M manage_instruction/Work_Task_Prompts.md`

### 未完成事项

- 待顾问窗口下发 `6-8` 第六轮整体验收与归档准备工单。

### 风险或疑点

- 详情弹窗回流目前依赖多条并行刷新通道（局部 refresh + `req_refresh_all` + 6-6 并行 EventBus emit），后续若继续接管必须先明确“主路径/辅路径”职责，避免重复刷新或时序竞态。

## 2026-05-26 第六轮 6-8（第六轮整体验收与归档准备）

- 本轮任务名称：第六轮 6-8（第六轮整体验收与归档准备）。
- 开工前 git 状态：
  - `git status --short --branch` -> `## main...temp/main [ahead 8]`
  - 开工前既有 diff：`M manage_instruction/Work_Task_Prompts.md`
  - 结论：开工前已有管理文档 diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`

### 6-0 ~ 6-7 完成摘要

- `6-0`：完成跨视图耦合静态定位，给出风险分级与迁移候选。
- `6-1`：建立 `MainController` / `ViewRouter` / `RefreshCoordinator` 最小骨架。
- `6-2`：`ViewRouter.classify_main_view` 接管 `switch_view` 纯决策，Qt 路由操作保留在 MainWindow。
- `6-3`：完成添加页来源与 picker 返回状态基线地图。
- `6-4`：`MainController` 接管 `source_view_for_add` 最小闭环决策。
- `6-5`：在 MainWindow 建立 Dashboard/Todo/Week 三连刷新协调边界。
- `6-6`：新增 `global_signals.refresh_requested(str)` 并在旧刷新后并行 emit。
- `6-7`：完成详情弹窗与跨视图刷新回流复核，形成后续接管建议与风险边界。

### 第六轮实际迁移到协调层的职责

- `ViewRouter`：
  - `classify_main_view` 提供 `day/week/month/todo/priority` 精确路由分类。
- `MainController`：
  - 添加页来源与返回的纯决策：
    - `resolve_add_source`
    - `resolve_add_return_target`
    - `default_to_schedule_for_add`
  - 刷新目标注册与触发代理（通过 `refresh_coordinator`）。
- `RefreshCoordinator`：
  - `register/unregister/trigger/trigger_many` 统一回调注册与顺序触发。
- `global_signals.refresh_requested`：
  - 并行通知试点，仅增强，不替代旧刷新主路径。

### 保留在 UI 中的职责及原因

- MainWindow 仍保留 Qt 实际路由与页面切换操作（`setCurrentWidget/show/hide/move`）。
- time/alarm/list picker edit 写库与返回路径仍在 UI（涉及写库和复杂回流，风险高）。
- WeekWindow 内部 picker 路径仍独立（未纳入本轮接管范围）。
- TodoBoardWindow `view_stack + list picker + folder/stick` 状态机仍未迁移（高耦合，建议第八轮处理）。
- 详情弹窗来源借道与 `source_view` 分支逻辑仍在 UI（跨窗口高耦合）。

### 验证命令与结果

- controller import 验证：
  - 命令通过，输出 `controller imports ok` 与 `True True True True`。
- py_compile 验证：
  - `main_controller.py/view_router.py/refresh_coordinator.py/__init__.py/signals.py/main_window.py` 全部通过。
- ViewRouter 行为验证：
  - 精确匹配通过；`' WEEK '`/`'Week'` 返回 `None`，保持旧语义。
- MainController 行为验证：
  - 添加页来源/返回/默认类型决策断言全部通过。
- RefreshCoordinator 行为验证：
  - register/trigger/trigger_many/unregister 断言全部通过。
- global_signals 兼容性验证：
  - `skin_changed` 无参兼容通过；
  - `refresh_requested('dashboard_todo_week')` 发射与接收通过。
- MainWindow import 验证：
  - 通过，输出 `main window import ok True`。

### MainWindow 关键接入点静态检查结果

- 命中项确认：
  - `MainController`、`ViewRouter`、`global_signals`
  - `_register_refresh_targets`
  - `_refresh_dashboard_todo_week`
  - `request_refresh_many`
  - `refresh_requested`
  - `resolve_add_source/resolve_add_return_target/default_to_schedule_for_add`
  - `classify_main_view`

### signals.py 旧信号签名检查结果

- `skin_changed`：`pyqtSignal()`（保持）
- `theme_changed`：`pyqtSignal(str)`（保持）
- `schedule_added`：`pyqtSignal(object)`（保持）
- `schedule_updated`：`pyqtSignal(object)`（保持）
- `schedule_deleted`：`pyqtSignal(int)`（保持）
- `category_changed`：`pyqtSignal()`（保持）
- `refresh_requested`：`pyqtSignal(str)`（新增）
- `global_signals` 名称保留。

### controller 静态依赖检查结果

- 命令：`rg -n "...|setCurrentWidget|refresh_data" src/controllers`
- 结果：无输出（退出码 1，视为通过），controller 不依赖 UI/db/Repository。

### diff 范围检查结果

- `git diff --name-only -- src`：无输出。
- `git diff --name-only -- main.py`：无输出。
- `git diff --name-only -- requirements.txt`：无输出。
- `git diff --name-only -- schedule.db`：无输出。
- `git diff --name-only`：
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
  - 写入本日志后另含 `manage_instruction/Work_Log.md`
- `git status --short --branch`：
  - `## main...temp/main [ahead 8]`
  - `M manage_instruction/Work_Task_Prompts.md`（开工前既有）
  - 写入本日志后另含 `M manage_instruction/Work_Log.md`

### 第六轮未迁移债务

- MainWindow Qt 实际路由仍是 UI 直控。
- picker time/alarm/list edit 写库与返回路径仍在 UI。
- WeekWindow 内部 picker 路径仍独立。
- TodoBoardWindow `view_stack/list picker` 状态机仍未迁移。
- 详情弹窗打开与 `source_view` 分支仍未迁移。
- `refresh_requested` 当前无 UI 监听者，仅并行通知试点。
- 第八轮 UI 拆分需重点处理 `TodoBoardWindow` / `MainWindow` / `WeekWindow` 大文件结构。

### 第七轮 Theme/QSS 接入前注意事项

- 不要在第七轮顺带改动第六轮协调层行为路径。
- Theme/QSS 改动应避免触碰详情弹窗回流、picker 返回、跨视图刷新触发时机。
- 保留第六轮回归集（路由决策、添加页来源、三连刷新、EventBus 并行通知、详情弹窗回流链路）作为 smoke 基线。

### 归档建议结论

- **第六轮可归档。**
- **可进入第七轮 Theme/QSS 接入阶段合同/规划。**

### 未完成事项

- 待顾问窗口复核 6-8 结论并确认归档后，发布第七轮正式执行提示词。

### 风险或疑点

- 第六轮的 EventBus 仅为并行通知试点，后续若接入监听需先定义“主刷新路径 vs 辅助通知路径”边界，防止重复刷新。
