# Work Task Prompts

## 第八轮 8-8：第八轮整体验收与归档准备

```markdown
请执行第八轮 8-8：第八轮整体验收与归档准备。本轮只做总体验收、日志汇总和归档判断，不改源码。

## 1. 本轮目标

汇总第八轮 8-0 到 8-7 的执行结果，验证第八轮已完成的 UI 包骨架、公共 helper、单类提取和只读基线没有破坏现有导入与基础运行边界，并判断第八轮是否可以归档。

本轮目标：

- 汇总第八轮已完成小工单：
  - 8-0 UI 拆分静态审查与职责地图
  - 8-1 UI 包目录骨架
  - 8-2a icon loader 静态基线
  - 8-2b Header icon loader 单点提取
  - 8-3a tooltip / toast 静态基线
  - 8-3b MainWindow toast helper 单点提取
  - 8-4a WeekWindow 类提取候选复核
  - 8-4b DayBlock 单类提取
  - 8-5 TodoBoard 只读基线
  - 8-6 AddFolderCard 单类提取
  - 8-7 剩余 UI 大文件拆分候选复核
- 验证已新增/提取模块可 import。
- 验证关键 UI 文件可 import。
- 验证第七轮主题/skin preset 基础仍可 import。
- 验证第六轮协调层基础仍可 import。
- 验证旧入口 `main` 可 import。
- 确认 `src/data`、`src/repositories`、`src/services`、`src/controllers` 等非本轮目标层无非预期 diff。
- 确认 `schedule.db` 无 tracked diff。
- 记录第八轮已完成内容、未拆债务、后续建议。
- 判断第八轮是否可归档。
- 不新增功能。
- 不改源码。

## 2. 允许/禁止

本轮允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）
- `manage_instruction/History_Instruction.md`（仅当项目流程要求归档当前指令，且需先说明）
- `manage_instruction/History_Log.md`（仅当项目流程要求归档当前日志，且需先说明）

本轮默认只应修改：

- `manage_instruction/Work_Log.md`
- 必要时 `manage_instruction/Work_Task_Prompts.md`

本轮禁止修改：

- `src/`
- `assets/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不新增 UI 组件。
- 不迁移类。
- 不修改 import。
- 不清理未使用 import。
- 不修改 QSS。
- 不修改 icon loader / toast helper / DayBlock / AddFolderCard。
- 不修改数据层、服务层、控制层。
- 不写数据库。
- 不提交 Git。

若开工前已有 diff，需在 `Work_Log.md` 单独记录，不视为本轮源码问题。

## 3. 具体任务

1. 读取当前基线：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8

2. 汇总第八轮完成项。

    至少记录：

    - 新增 UI 包骨架：
      - `src/ui/common/`
      - `src/ui/views/`
      - `src/ui/dialogs/`
      - `src/ui/popups/`
      - `src/ui/utils/`
    - 新增 helper / 组件：
      - `src/ui/utils/icon_loader.py`
      - `src/ui/common/toast.py`
      - `src/ui/common/week_day_block.py`
      - `src/ui/common/todo_board_add_folder_card.py`
    - 已替换调用边界：
      - `header.py::_load_colored_svg(...)`
      - `main_window.py::show_toast(...)`
      - `week_window.py` 中 `DayBlock` 导入
      - `todo_board.py` 中 `AddFolderCard` 导入
    - 只读基线结论：
      - tooltip/toast 地图
      - WeekWindow 类提取风险
      - TodoBoard 拆分风险
      - 剩余 UI 大文件拆分建议

3. 验证第八轮新增模块 import：

    - UI 包骨架
    - icon loader
    - toast helper
    - DayBlock
    - AddFolderCard

4. 验证关键 UI import：

    - `HeaderBar`
    - `MainWindow`
    - `WeekWindow`
    - `MonthWindow`
    - `TodoBoardWindow`
    - `AddScheduleView`
    - `AddScheduleViewWeek`
    - `ScheduleDetailPop`

5. 验证第七轮主题基础：

    - `ThemeManager`
    - `ThemeManager.DEFAULT_PRESET`
    - `SUPPORTED_PRESETS`
    - `default.qss` 存在

6. 验证第六轮协调层基础：

    - `MainController`
    - `ViewRouter`
    - `RefreshCoordinator`
    - `global_signals`

7. 验证旧数据路径基础 import：

    - `db_manager`
    - `get_all_schedules`
    - `get_active_categories`

8. 验证默认入口 import：

    - `main import ok`

9. 进行 diff 范围检查：

    - 确认 `src` 无未提交 diff。
    - 确认 `assets` 无 diff。
    - 确认 `main.py` 无 diff。
    - 确认 `requirements.txt` 无 diff。
    - 确认 `schedule.db` 无 tracked diff。
    - 确认工作区最终只允许管理文档 diff。

10. 输出第八轮归档判断：

    - 若所有验证通过，记录“第八轮可归档”。
    - 若有验证失败，记录失败命令、原因、是否阻塞归档。
    - 明确下一轮建议：
      - 若第八轮归档：建议进入第九轮规划或按 `Work_Formulation.md` 后续路线继续。
      - 若不归档：说明需要补哪一个最小修复工单。

11. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

UI 包骨架 import：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import src.ui.common, src.ui.views, src.ui.dialogs, src.ui.popups, src.ui.utils; print('ui package skeleton import ok')"

第八轮新增模块 import：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.utils.icon_loader import load_colored_svg_pixmap; from src.ui.common.toast import show_center_toast; from src.ui.common.week_day_block import DayBlock; from src.ui.common.todo_board_add_folder_card import AddFolderCard; print('round 8 extracted imports ok')"

关键 UI import：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.header import HeaderBar; from src.ui.main_window import MainWindow; from src.ui.week_window import WeekWindow; from src.ui.month_window import MonthWindow; from src.ui.todo_board import TodoBoardWindow; from src.ui.add_view import AddScheduleView; from src.ui.add_view_week import AddScheduleViewWeek; from src.ui.schedule_detail_pop import ScheduleDetailPop; print('key ui imports ok')"

第七轮主题基础验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.theme import ThemeManager; import os; print('theme manager ok', ThemeManager.DEFAULT_PRESET); print('supported', ThemeManager.SUPPORTED_PRESETS); print('default exists', os.path.exists(os.path.join('src','theme','default.qss'))); assert ThemeManager.DEFAULT_PRESET == 'default.qss'; assert os.path.exists(os.path.join('src','theme','default.qss'))"

第六轮协调层基础验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.controllers.main_controller import MainController; from src.controllers.view_router import ViewRouter; from src.controllers.refresh_coordinator import RefreshCoordinator; from src.utils.signals import global_signals; print('controllers/signals import ok', MainController, ViewRouter, RefreshCoordinator, global_signals)"

旧数据路径基础验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('db import ok'); print('schedules', len(db_manager.get_all_schedules())); print('categories', len(db_manager.get_active_categories()))"

默认入口 import：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; import main; print('main import ok')"

语法检查：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/utils/icon_loader.py src/ui/common/toast.py src/ui/common/week_day_block.py src/ui/common/todo_board_add_folder_card.py src/ui/header.py src/ui/main_window.py src/ui/week_window.py src/ui/todo_board.py main.py

确认本轮不新增/修改源码：

    git diff --name-only -- src
    git diff --name-only -- assets
    git diff --name-only -- main.py
    git diff --name-only -- requirements.txt
    git diff --name-only -- schedule.db

总范围检查：

    git diff --name-only
    git status --short --branch

预期：

- `src` 无 diff。
- `assets` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 diff。
- 最终只允许：
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`
  - 若流程要求归档，可包含明确说明后的 `History_Instruction.md` / `History_Log.md`

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第八轮 8-8（第八轮整体验收与归档准备）
- 开工前 git 状态
- 实际修改文件
- 第八轮完成项汇总：
  - 8-0 到 8-7 每项一句话摘要
  - 新增 UI 包目录
  - 新增 helper / 组件
  - 已替换调用边界
- 第八轮未拆 UI 债务：
  - `WeekScheduleCard`
  - `FolderCard`
  - `TodoBoardWindow`
  - `month_window.py`
  - `add_view.py` / `add_view_week.py`
  - `schedule_detail_pop.py`
- 第八轮推迟项和原因：
  - 拖拽/排序写回
  - picker/edit 回流
  - detail popup 回流
  - 复杂 tooltip / countdown tooltip
  - 统一 icon loader / toast / QSS 大范围迁移
- UI 包骨架 import 验证结果
- 第八轮新增模块 import 验证结果
- 关键 UI import 验证结果
- 第七轮主题基础验证结果
- 第六轮协调层验证结果
- 旧数据路径基础验证结果
- main import 验证结果
- py_compile 结果
- diff 范围检查结果
- 第八轮是否可归档
- 下一轮建议
- 未完成事项
- 风险或疑点

特别记录：

- 本轮不改源码。
- 本轮不新增 UI 组件。
- 本轮不修改数据库。
- 本轮只做整体验收与归档判断。
- 若某条验证命令因类名或环境问题失败，不要改源码；记录失败原因，并用项目真实类名或 offscreen 等价命令复核。

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
```
