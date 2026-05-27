# Work Task Prompts

## 第八轮 8-6：TodoBoard AddFolderCard 单类提取试点

```markdown
请执行第八轮 8-6：TodoBoard AddFolderCard 单类提取试点。本轮只提取 `AddFolderCard` 一个类，不处理 `FolderCard`，不改 TodoBoard 主状态机。

## 1. 本轮目标

基于 8-5 只读基线结论，将 `src/ui/todo_board.py` 中的 `AddFolderCard` 类移动到独立文件，并保持 `FolderViewContainer` 对 `AddFolderCard` 的使用行为不变。

本轮目标：

- 新增 `src/ui/common/todo_board_add_folder_card.py`。
- 将 `AddFolderCard` 类完整移动到该文件。
- `src/ui/todo_board.py` 从新文件导入 `AddFolderCard`。
- 保持 `AddFolderCard` 类名、构造函数、signal、方法名、样式、图标加载、点击行为不变。
- 保持 `FolderViewContainer` 中 `AddFolderCard` 实例化、`clicked.connect(...)`、布局位置不变。
- 不提取 `FolderCard`。
- 不修改 `TodoBoardWindow`。
- 不修改拖拽、排序、写库、toast、tooltip、icon loader。
- 不改变待办看板 UI 行为。

## 2. 允许/禁止

本轮允许修改：

- `src/ui/common/todo_board_add_folder_card.py`
- `src/ui/todo_board.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

本轮禁止修改：

- `src/ui/common/todo_board_cards.py`
- `src/ui/common/toast.py`
- `src/ui/common/week_day_block.py`
- `src/ui/utils/icon_loader.py`
- `src/ui/components.py`
- `src/ui/header.py`
- `src/ui/week_window.py`
- `src/ui/month_window.py`
- `src/ui/main_window.py`
- `src/ui/dashboard.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- 除 `src/ui/todo_board.py` 与 `src/ui/common/todo_board_add_folder_card.py` 外的任何 `src/ui/` 文件
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

- 不提取 `FolderCard`。
- 不修改 `FolderCard`。
- 不修改 `FolderViewContainer` 拖拽/排序/写回逻辑。
- 不修改 `TodoBoardWindow` 主状态机。
- 不修改 `TodoBoardWindow.show_toast`。
- 不修改 `get_colored_icon` 实现。
- 不修改 `_get_icon` 实现。
- 不新增 `src/ui/common/todo_board_cards.py`。
- 不新增 `src/ui/views/todo_board.py`。
- 不修改 `src/ui/common/__init__.py`，除非确有必要；若修改，只能做轻量导出且必须说明原因。
- 不提交 Git。

若开工前已有 diff，需在 `Work_Log.md` 单独记录，不视为本轮源码问题。

## 3. 具体任务

1. 读取当前基线：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
    Get-Content -Path src\ui\todo_board.py -Encoding UTF8

2. 新增 `src/ui/common/todo_board_add_folder_card.py`。

    将 `AddFolderCard` 类从 `src/ui/todo_board.py` 移入新文件。

    必须保留：

    - `class AddFolderCard(QFrame)`
    - `clicked = pyqtSignal()`
    - `__init__(self, parent=None)`
    - `mouseReleaseEvent(...)`
    - 原有控件结构
    - 原有样式字符串
    - 原有 `get_colored_icon("plus-circle.svg", "#FFFFFF", 32)` 调用语义
    - 原有鼠标指针设置
    - 原有点击发射 `clicked`

3. 调整 `src/ui/todo_board.py`。

    只允许做以下最小改动：

    - 删除原 `AddFolderCard` 类定义。
    - 从 `src.ui.common.todo_board_add_folder_card` 或相对路径导入 `AddFolderCard`。
    - 保持 `FolderViewContainer` 中所有 `AddFolderCard` 使用方式不变。
    - 不修改 `FolderCard`。
    - 不修改 `FolderViewContainer` 拖拽/排序/写回逻辑。
    - 不修改 `TodoBoardWindow`。
    - 不修改其它方法行为。

4. 处理 import。

    - `todo_board_add_folder_card.py` 只导入 `AddFolderCard` 实际需要的依赖。
    - 如果需要复用 `get_colored_icon`，允许从 `src.ui.todo_board` 导入该函数，但必须评估并记录是否造成循环导入风险。
    - 更推荐将 `get_colored_icon` 保留在 `todo_board.py`，并在本轮仅做最小可运行导入；不得同时迁移 icon helper。
    - `todo_board.py` 中如果因移出 `AddFolderCard` 产生明确未使用 import，可以只删除与 `AddFolderCard` 独占相关且确定不再使用的 import。
    - 不做大范围 import 整理。
    - 不重排无关 import。
    - 不改业务逻辑。

5. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

定位 AddFolderCard 新旧位置：

    rg -n "^class AddFolderCard|from .*todo_board_add_folder_card import AddFolderCard|AddFolderCard" src/ui/todo_board.py src/ui/common/todo_board_add_folder_card.py

确认 FolderCard 未迁移：

    rg -n "^class FolderCard|doubleClicked|delete_requested|current_drag_widget|QDrag|QMimeData" src/ui/todo_board.py
    Test-Path src\ui\common\todo_board_cards.py
    Test-Path src\ui\views\todo_board.py
    Test-Path src\ui\views\todo_board_cards.py

AddFolderCard import 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.common.todo_board_add_folder_card import AddFolderCard; print('add folder card import ok', AddFolderCard)"

TodoBoard import 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.todo_board import TodoBoardWindow, FolderCard, AddFolderCard; print('todo board imports ok', TodoBoardWindow, FolderCard, AddFolderCard)"

AddFolderCard offscreen 基础实例化验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.common.todo_board_add_folder_card import AddFolderCard; app=QApplication([]); c=AddFolderCard(); print('add folder card created', c is not None); print('cursor', c.cursor().shape().name); print('has icon label', hasattr(c, 'icon_label')); print('has name label', hasattr(c, 'name_label')); assert hasattr(c, 'icon_label'); assert hasattr(c, 'name_label')"

TodoBoardWindow offscreen 基础实例化验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.todo_board import TodoBoardWindow; app=QApplication([]); w=TodoBoardWindow(); print('todo board created', w is not None); print('view mode', getattr(w, 'view_mode', None)); assert w is not None"

8-4b DayBlock 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.common.week_day_block import DayBlock; print('day block import ok', DayBlock)"

8-3b toast helper 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.common.toast import show_center_toast; print('toast helper import ok', show_center_toast)"

8-2b icon loader 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.utils.icon_loader import load_colored_svg_pixmap; print('icon loader import ok', load_colored_svg_pixmap)"

默认入口 import 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; import main; print('main import ok')"

语法检查：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/common/todo_board_add_folder_card.py src/ui/todo_board.py main.py

禁止范围检查：

    git diff --name-only -- src/ui/common/todo_board_cards.py
    git diff --name-only -- src/ui/common/toast.py
    git diff --name-only -- src/ui/common/week_day_block.py
    git diff --name-only -- src/ui/utils/icon_loader.py
    git diff --name-only -- src/ui/components.py
    git diff --name-only -- src/ui/header.py
    git diff --name-only -- src/ui/week_window.py
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

    src/ui/todo_board.py
    src/ui/common/todo_board_add_folder_card.py

总范围检查：

    git diff --name-only
    git status --short --branch

预期最终只允许：

- `src/ui/common/todo_board_add_folder_card.py`
- `src/ui/todo_board.py`
- `manage_instruction/Work_Log.md`
- 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第八轮 8-6（TodoBoard AddFolderCard 单类提取试点）
- 开工前 git 状态
- 实际修改文件
- `AddFolderCard` 新文件路径
- `AddFolderCard` 保持兼容的内容：
  - 类名
  - signal
  - 构造函数
  - `mouseReleaseEvent`
  - 图标加载语义
  - 样式字符串
  - 点击发射逻辑
- `todo_board.py` 中 import 替换说明
- 是否存在循环导入风险及判断依据
- 确认 `FolderViewContainer` 中 `AddFolderCard` 使用方式未改
- 确认未修改 `FolderCard`
- 确认未修改拖拽/排序/写库/toast/icon loader/tooltip 公共实现
- AddFolderCard import 验证结果
- TodoBoard import 回归结果
- AddFolderCard offscreen 基础实例化验证结果
- TodoBoardWindow offscreen 基础实例化验证结果
- 8-4b DayBlock 回归结果
- 8-3b toast helper 回归结果
- 8-2b icon loader 回归结果
- main import 回归结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

特别记录：

- 本轮只提取 `AddFolderCard`。
- 本轮不提取 `FolderCard`。
- 本轮不拆 `TodoBoardWindow` 主状态机。
- 本轮不修改待办看板业务行为。
- 本轮不修改 tooltip/toast/icon loader。
- 本轮不修改数据库或服务层。
- 若因 `get_colored_icon` 导入造成循环导入或 import 失败，不要扩大重构；应停止并记录问题，等待复核。

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
```
