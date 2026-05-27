# Work Task Prompts

## 第八轮 8-4b：WeekWindow DayBlock 单类提取试点

```markdown
请执行第八轮 8-4b：WeekWindow DayBlock 单类提取试点。本轮只提取 `DayBlock` 一个类，不处理 `WeekScheduleCard`，不改周视图业务流程。

## 1. 本轮目标

基于 8-4a 只读复核结论，将 `src/ui/week_window.py` 中的 `DayBlock` 类移动到独立文件，并保持 `WeekWindow` 对 `DayBlock` 的使用行为不变。

本轮目标：

- 新增 `src/ui/common/week_day_block.py`。
- 将 `DayBlock` 类完整移动到该文件。
- `src/ui/week_window.py` 从新文件导入 `DayBlock`。
- 保持 `DayBlock` 类名、构造函数、signal、方法名、样式、tooltip、异常兜底逻辑不变。
- 保持 `WeekWindow` 中 `self.day_blocks` 创建、`block.clicked.connect(...)`、`set_data(...)`、`set_selected(...)` 调用不变。
- 不提取 `WeekScheduleCard`。
- 不修改拖拽、排序、写库、toast、tooltip 公共实现、icon loader。
- 不改变周视图 UI 行为。

## 2. 允许/禁止

本轮允许修改：

- `src/ui/common/week_day_block.py`
- `src/ui/week_window.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

本轮禁止修改：

- `src/ui/components.py`
- `src/ui/header.py`
- `src/ui/common/toast.py`
- `src/ui/utils/icon_loader.py`
- `src/ui/todo_board.py`
- `src/ui/month_window.py`
- `src/ui/main_window.py`
- `src/ui/dashboard.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- 除 `src/ui/week_window.py` 与 `src/ui/common/week_day_block.py` 外的任何 `src/ui/` 文件
- `src/theme/`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `src/utils/signals.py`
- `src/utils/styles.py`
- `assets/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不提取 `WeekScheduleCard`。
- 不修改 `WeekScheduleCard`。
- 不修改 `WeekWindow` 写库逻辑。
- 不修改 `WeekWindow` 拖拽/排序逻辑。
- 不修改 `WeekWindow.show_toast`。
- 不修改 tooltip 公共实现。
- 不新增 `src/ui/views/week_window.py`。
- 不新增 `src/ui/common/week_cards.py`。
- 不修改 `src/ui/common/__init__.py`，除非确有必要；若修改，只能做轻量导出且必须说明原因。
- 不清理 8-2b 遗留的 `header.py` unused import。
- 不提交 Git。

若开工前已有 diff，需在 `Work_Log.md` 单独记录，不视为本轮源码问题。

## 3. 具体任务

1. 读取当前基线：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
    Get-Content -Path src\ui\week_window.py -Encoding UTF8

2. 新增 `src/ui/common/week_day_block.py`。

    将 `DayBlock` 类从 `src/ui/week_window.py` 移入新文件。

    必须保留：

    - `class DayBlock(QFrame)`
    - `clicked = pyqtSignal(QDate)`
    - `__init__(self, parent=None)`
    - `set_data(...)`
    - `set_selected(...)`
    - `mouseReleaseEvent(...)`
    - 原有控件结构
    - 原有样式字符串
    - 原有 tooltip 文案与 `ToolTipFilter` 使用方式
    - 原有 `removeEventFilter/deleteLater/installEventFilter` 逻辑
    - 原有农历计算和异常兜底逻辑

3. 调整 `src/ui/week_window.py`。

    只允许做以下最小改动：

    - 删除原 `DayBlock` 类定义。
    - 从 `src.ui.common.week_day_block` 或相对路径导入 `DayBlock`。
    - 保持 `WeekWindow` 中所有 `DayBlock` 使用方式不变。
    - 不修改 `WeekScheduleCard`。
    - 不修改 `WeekWindow` 其它方法行为。

4. 处理 import。

    - `week_day_block.py` 只导入 `DayBlock` 实际需要的依赖。
    - `week_window.py` 中如果因移出 `DayBlock` 产生明确未使用 import，可以只删除与 `DayBlock` 独占相关且确定不再使用的 import。
    - 不做大范围 import 整理。
    - 不重排无关 import。
    - 不改业务逻辑。

5. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

定位 DayBlock 新旧位置：

    rg -n "^class DayBlock|from .*week_day_block import DayBlock|DayBlock" src/ui/week_window.py src/ui/common/week_day_block.py

确认 WeekScheduleCard 未迁移：

    rg -n "^class WeekScheduleCard|CountdownToolTipFilter|current_drag_widget|req_status|req_pin|req_delete" src/ui/week_window.py
    Test-Path src\ui\common\week_cards.py
    Test-Path src\ui\views\week_window.py
    Test-Path src\ui\views\week_cards.py

DayBlock import 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.common.week_day_block import DayBlock; print('day block import ok', DayBlock)"

WeekWindow import 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.week_window import WeekWindow, WeekScheduleCard, DayBlock; print('week imports ok', WeekWindow, WeekScheduleCard, DayBlock)"

DayBlock offscreen 基础实例化验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.common.week_day_block import DayBlock; app=QApplication([]); b=DayBlock(); b.set_data(QDate.currentDate(), False); print('day block created', b is not None); print('date obj', b.date_obj.toString('yyyy-MM-dd')); b.set_selected(True); print('selected true ok'); b.set_selected(False); print('selected false ok'); assert b.date_obj == QDate.currentDate()"

WeekWindow offscreen 基础实例化验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.week_window import WeekWindow; app=QApplication([]); w=WeekWindow(); print('week window created', w is not None); print('day blocks', len(getattr(w, 'day_blocks', []))); assert len(getattr(w, 'day_blocks', [])) == 7"

8-3b toast helper 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.common.toast import show_center_toast; print('toast helper import ok', show_center_toast)"

8-2b icon loader 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.utils.icon_loader import load_colored_svg_pixmap; print('icon loader import ok', load_colored_svg_pixmap)"

默认入口 import 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; import main; print('main import ok')"

语法检查：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/common/week_day_block.py src/ui/week_window.py main.py

禁止范围检查：

    git diff --name-only -- src/ui/components.py
    git diff --name-only -- src/ui/header.py
    git diff --name-only -- src/ui/common/toast.py
    git diff --name-only -- src/ui/utils/icon_loader.py
    git diff --name-only -- src/ui/todo_board.py
    git diff --name-only -- src/ui/month_window.py
    git diff --name-only -- src/ui/main_window.py
    git diff --name-only -- src/ui/dashboard.py
    git diff --name-only -- src/ui/add_view.py
    git diff --name-only -- src/ui/add_view_week.py
    git diff --name-only -- src/theme
    git diff --name-only -- src/data
    git diff --name-only -- src/repositories
    git diff --name-only -- src/services
    git diff --name-only -- src/controllers
    git diff --name-only -- src/utils/signals.py
    git diff --name-only -- src/utils/styles.py
    git diff --name-only -- assets
    git diff --name-only -- main.py
    git diff --name-only -- requirements.txt
    git diff --name-only -- schedule.db

允许范围检查：

    git diff --name-only -- src/ui

预期 `src/ui` diff 仅允许：

    src/ui/week_window.py
    src/ui/common/week_day_block.py

总范围检查：

    git diff --name-only
    git status --short --branch

预期最终只允许：

- `src/ui/common/week_day_block.py`
- `src/ui/week_window.py`
- `manage_instruction/Work_Log.md`
- 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第八轮 8-4b（WeekWindow DayBlock 单类提取试点）
- 开工前 git 状态
- 实际修改文件
- `DayBlock` 新文件路径
- `DayBlock` 保持兼容的内容：
  - 类名
  - signal
  - 构造函数
  - `set_data`
  - `set_selected`
  - `mouseReleaseEvent`
  - tooltip 逻辑
  - 农历异常兜底逻辑
- `week_window.py` 中 import 替换说明
- 确认 `WeekWindow` 中 `DayBlock` 使用方式未改
- 确认未修改 `WeekScheduleCard`
- 确认未修改拖拽/排序/写库/toast/icon loader/tooltip 公共实现
- DayBlock import 验证结果
- WeekWindow import 回归结果
- DayBlock offscreen 基础实例化验证结果
- WeekWindow offscreen 基础实例化验证结果
- 8-3b toast helper 回归结果
- 8-2b icon loader 回归结果
- main import 回归结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

特别记录：

- 本轮只提取 `DayBlock`。
- 本轮不提取 `WeekScheduleCard`。
- 本轮不拆 `WeekWindow` 主流程。
- 本轮不修改周视图业务行为。
- 本轮不修改 tooltip/toast/icon loader。
- 本轮不修改数据库或服务层。

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
```
