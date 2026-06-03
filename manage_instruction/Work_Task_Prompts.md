# Work Task Prompts

用途：保存主窗口审核后的最终执行提示词或当前复核锚点。执行窗口只应执行本文件中的最终版本。

---

# 当前待执行提示词：M-3

## M-3：月格 hover 只读预览弹窗

请执行 `M-3：月格 hover 只读预览弹窗`。本轮只实现月界面日期格 hover 只读预览：鼠标移入有效日期格时，在该日期格右下角显示只读日程列表；鼠标移出日期格后立即隐藏。

本轮不改变 M-2 的单击/双击语义，不实现持久浮窗，不改变添加按钮日期来源，不接入右键菜单，不修改数据库写入逻辑。

## 1. 本轮目标

基于 M-0 / M-1 / M-2 结论，在月界面增加 hover 只读预览能力：

- 鼠标移入有效日期格：
  - 显示该日期的只读日程列表预览。
  - 预览弹窗显示在该日期格右下角附近。
- 鼠标移出日期格：
  - 预览弹窗立即隐藏。
- 预览弹窗只读：
  - 不提供编辑入口。
  - 不提供删除入口。
  - 不提供添加入口。
  - 不触发任何业务动作。
  - 不写数据库。
- 保持 M-2 行为：
  - 单击仍只更新 `user_selected_date` 和选中高亮。
  - 双击 / activated 仍跳转日视图。
  - 双击跳转前仍调用 `close_day_panels()`。
- 不实现 M-4 的持久浮窗。
- 不实现 M-5 的添加日期来源联动。
- 不实现 M-6 的右键菜单。

## 2. 允许/禁止

允许修改：

- `src/ui/month_window.py`
- `src/ui/popups/month_day_hover_preview.py`（如需要新增专用 hover 预览组件）
- `src/ui/popups/__init__.py`（仅在必须导出新组件时允许；优先不改）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/ui/main_window.py`
- `src/ui/calendar_pop.py`
- `src/ui/common/action_context_menu.py`
- `src/ui/common/`
- `src/ui/dashboard.py`
- `src/ui/week_window.py`
- `src/ui/todo.py`
- `src/ui/todo_board.py`
- `src/controllers/`
- `src/services/`
- `src/data/`
- `src/repositories/`
- `src/theme/`
- `src/utils/signals.py`
- `src/utils/styles.py`
- `assets/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `manage_instruction/Work_Formulation.md`
- `manage_instruction/Work_Instruction.md`
- `manage_instruction/Work_Snapshot.md`
- `manage_instruction/History_Instruction.md`
- `manage_instruction/History_Log.md`
- `manage_instruction/ReconstructionDolder/`

禁止事项：

- 不改变 M-1 三角数量角标颜色、数量、过滤规则。
- 不改变今天金色日期逻辑。
- 不改变 M-2 单击选中语义。
- 不改变 M-2 双击跳日视图语义。
- 不改变 `date_selected` 信号语义。
- 不改变 `close_day_panels()` / `open_day_panels` 当前职责。
- 不实现单击持久浮窗。
- 不改变 `_on_add_clicked(...)` 日期来源。
- 不修改 `InlineAddViewMonth` 写库逻辑。
- 不接入右键菜单。
- 不新增数据库字段。
- 不写数据库。
- 不提交 Git。

若开工前已有 diff，必须在 `Work_Log.md` 中单独记录，并区分是否属于本轮产生。

## 3. 具体任务

### 3.1 读取当前上下文

读取：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
    Get-Content -Path src\ui\month_window.py -Encoding UTF8
    Get-ChildItem -Path src\ui\popups -Force

重点确认：

- M-0 对 M-3 的建议。
- M-1 当前三角数量角标缓存和日期映射能力。
- M-2 当前 `user_selected_date`、`calendar.clicked`、`calendar.activated`、`date_selected.emit(...)`、`close_day_panels()` 实现。
- 当前 `QTableView` 获取方式。
- 当前 `CalendarCellDelegate._date_for_index(...)` 或等价日期映射方法。
- 当前是否已有可复用的 `date -> schedules` 数据结构；如果没有，本轮可新增只读预览用缓存，但不得改数据层。

### 3.2 新增 hover 只读预览组件

如当前没有合适组件，新增：

- `src/ui/popups/month_day_hover_preview.py`

建议类名：

    class MonthDayHoverPreview(QFrame):
        ...

组件要求：

- 只读显示。
- 不包含编辑按钮。
- 不包含删除按钮。
- 不包含添加按钮。
- 不连接数据库写入。
- 不依赖 `db_manager`。
- 不依赖 Repository / Service。
- 不依赖 `MainWindow`。
- 不依赖 `MonthWindow` 具体实例。
- 只接收日期和日程列表数据用于展示。
- 可显示简化信息，例如日期、标题、时间、优先级/状态文本。
- 无日程时可显示“无日程”或简洁空状态，但不能触发任何业务动作。

窗口行为建议：

- 使用轻量顶层窗口，例如 `Qt.ToolTip` 或 `Qt.FramelessWindowHint | Qt.Tool`。
- 设置不抢焦点属性，例如 `WA_ShowWithoutActivating`。
- 鼠标移出日期格后由 `MonthWindow` 立即隐藏该预览，不要求用户进入预览窗口交互。
- 样式保持轻量，不做复杂 QSS 主题接入。
- 后续 M-4 的持久浮窗不直接复用该只读组件作为编辑容器，除非后续另行评估。

### 3.3 在 MonthWindow 中接入 hover 命中

在 `src/ui/month_window.py` 中接入 hover：

- 对月历内部 `QTableView.viewport()` 开启 mouse tracking。
- 对 `QTableView.viewport()` 安装 event filter；优先不要把 hover 事件装到整个 `MonthWindow`。
- 使用 `eventFilter(...)` 或等价方式监听：
  - `QEvent.Type.MouseMove`
  - `QEvent.Type.Leave`
- 鼠标移动时通过 `table_view.indexAt(event.pos())` 命中日期格。
- 通过现有精确日期映射方法获取 `QDate`。
- 仅对有效日期显示预览。
- 表头行、无效 index、无效 `QDate`、移出 viewport 时必须立即隐藏预览。
- 预览位置应基于该日期格 `visualRect(index)` 的右下角，转换为全局坐标后显示。
- 不要使用 `calendar.selectedDate()` 推断 hover 日期。
- 不要改变 `user_selected_date`。
- 不要 emit `date_selected`。
- 不要调用 `close_day_panels()`。
- 不要影响 `calendar.clicked` / `calendar.activated`。

建议：

- 维护 `self.hover_preview_popup` 或等价实例。
- 维护 `self.hovered_date` 或等价状态，避免同一格内重复重建弹窗。
- 如果鼠标在同一日期格内移动，只更新位置或保持显示，不要反复销毁重建。
- 如果切换到另一个日期格，更新预览内容和位置。
- 如果翻月、刷新 marker 缓存或窗口隐藏，应隐藏 hover 预览，避免显示旧日期数据。

### 3.4 提供只读日程数据

本轮可以在 `MonthWindow` 内部构建 hover 预览所需的只读日程缓存。

要求：

- 不写数据库。
- 不改 `db_manager`。
- 不改 repository / service。
- 可只读调用 `db_manager.get_all_schedules()`。
- 优先复用 M-1 已有数据聚合路径；如 M-1 只保存 marker，不保存列表，可新增 `date -> schedules` 只读缓存。
- 过滤规则应与 M-1 月格标记保持一致：
  - 排除 `status == 2`。
  - 排除 `item_type == "todo"`。
  - 日期来源优先 `start_time.date()`，缺失时用 `end_time.date()`。
  - 重复日程实例作为独立记录显示。
- 显示顺序可先使用稳定简单顺序，例如开始时间、优先级、标题；如果当前代码已有月界面候选排序规则，可记录但不要引入大排序重构。
- 不改变 M-1 marker 颜色/数量计算。

### 3.5 保持 M-2 行为不变

必须确认并保持：

- `calendar.clicked` 仍连接单击内部处理方法。
- 单击日期仍只更新 `user_selected_date`。
- `calendar.activated` 或等价双击/激活入口仍负责跳日视图。
- `date_selected.emit(...)` 仍只在双击/activated 跳转路径中触发。
- `close_day_panels()` 仍只用于双击跳转前关闭后续持久浮窗。
- `_on_add_clicked(...)` 不改为使用 `user_selected_date`。
- `InlineAddViewMonth` 不改。
- `schedule.db` 无 tracked diff。

### 3.6 更新日志

更新 `manage_instruction/Work_Log.md`，记录本轮修改、验证和风险。

## 4. 验收命令

开工状态：

    git status --short --branch
    git diff --name-only

定位本轮链路：

    rg -n "hover|Hover|mouseMove|mouseTracking|setMouseTracking|eventFilter|Leave|MouseMove|indexAt|visualRect|hover_preview|hovered_date|MonthDayHoverPreview|month_day_hover_preview|user_selected_date|calendar\.clicked|calendar\.activated|date_selected\.emit|_on_add_clicked|close_day_panels|open_day_panels" src/ui/month_window.py src/ui/popups

import 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.month_window import MonthWindow, CalendarCellDelegate, InlineAddViewMonth; print('month import ok', MonthWindow, CalendarCellDelegate, InlineAddViewMonth)"

如新增 `month_day_hover_preview.py`，执行：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.popups.month_day_hover_preview import MonthDayHoverPreview; print('hover preview import ok', MonthDayHoverPreview)"

offscreen 构造验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); print('month construct ok'); print('has calendar', hasattr(w, 'calendar')); print('has hover preview attr', hasattr(w, 'hover_preview_popup') or hasattr(w, '_hover_preview_popup')); print('user selected', getattr(w, 'user_selected_date', None))"

hover 数据缓存验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); cache=getattr(w, 'hover_schedule_cache', getattr(w, '_hover_schedule_cache', None)); print('hover cache type', type(cache).__name__); print('hover cache dates', len(cache or {})); assert cache is not None"

M-2 行为静态回归：

    rg -n "calendar\.clicked\.connect\(self\._on_calendar_date_clicked\)|calendar\.clicked\.connect|calendar\.activated\.connect|date_selected\.emit|jump_to_date_from_month|_on_add_clicked|selectedDate|user_selected_date|close_day_panels|open_day_panels" src/ui/month_window.py src/ui/main_window.py

要求：

- 不应出现 `calendar.clicked.connect(self.date_selected.emit)`。
- `calendar.clicked` 仍应连接单击内部处理方法。
- `date_selected.emit(...)` 仍只应在双击/activated 跳转路径中。
- `_on_add_clicked(...)` 仍应使用 `selectedDate()`，不得改为使用 `user_selected_date`。
- `close_day_panels()` 不应被 hover 路径调用。

语法检查：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import py_compile, tempfile, os; targets=['src/ui/month_window.py','main.py']; extra='src/ui/popups/month_day_hover_preview.py'; import pathlib; p=pathlib.Path(extra); targets += [extra] if p.exists() else []; [py_compile.compile(t, cfile=os.path.join(tempfile.gettempdir(), os.path.basename(t)+'.m3.pyc'), doraise=True) for t in targets]; print('py_compile temp ok', targets)"

禁止范围检查：

    git diff --name-only -- src/ui/main_window.py
    git diff --name-only -- src/ui/calendar_pop.py
    git diff --name-only -- src/ui/common/action_context_menu.py
    git diff --name-only -- src/ui/common
    git diff --name-only -- src/ui/dashboard.py
    git diff --name-only -- src/ui/week_window.py
    git diff --name-only -- src/ui/todo.py
    git diff --name-only -- src/ui/todo_board.py
    git diff --name-only -- src/controllers
    git diff --name-only -- src/services
    git diff --name-only -- src/data
    git diff --name-only -- src/repositories
    git diff --name-only -- src/theme
    git diff --name-only -- src/utils/signals.py
    git diff --name-only -- src/utils/styles.py
    git diff --name-only -- assets
    git diff --name-only -- main.py
    git diff --name-only -- requirements.txt
    git diff --name-only -- schedule.db
    git diff --name-only -- manage_instruction/Work_Formulation.md
    git diff --name-only -- manage_instruction/Work_Instruction.md
    git diff --name-only -- manage_instruction/Work_Snapshot.md
    git diff --name-only -- manage_instruction/History_Instruction.md
    git diff --name-only -- manage_instruction/History_Log.md
    git diff --name-only -- manage_instruction/ReconstructionDolder

允许范围检查：

    git diff --name-only -- src/ui/month_window.py
    git diff --name-only -- src/ui/popups
    git diff --name-only
    git status --short --branch

预期：

- 允许 `src/ui/month_window.py` 有 diff。
- 如新增 hover 预览组件，允许 `src/ui/popups/month_day_hover_preview.py` 有 diff。
- 如确需导出组件，允许 `src/ui/popups/__init__.py` 有最小 diff；优先不改。
- 允许 `manage_instruction/Work_Log.md` 有 diff。
- 必要时允许 `manage_instruction/Work_Task_Prompts.md` 有 diff。
- 禁止范围均无 diff。
- `schedule.db` 无 tracked diff。
- `src/ui/main_window.py` 无 diff。
- `src/data`、`src/services`、`src/repositories` 无 diff。

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：`M-3（月格 hover 只读预览弹窗）`
- 开工前 git 状态。
- 开工前既有 diff。
- 实际修改文件。
- hover 预览组件位置。
- hover 日期命中方式。
- 预览弹窗定位方式，是否基于日期格右下角全局坐标。
- 鼠标移出日期格后如何立即隐藏。
- 预览是否只读。
- 预览数据来源和过滤规则。
- 是否保持 M-1 三角数量角标颜色/数量逻辑不变。
- 是否保持 M-2 单击/双击语义不变。
- 是否保持添加按钮日期来源不变。
- 是否未实现持久浮窗。
- 是否未接右键菜单。
- 是否未写数据库。
- 验证命令和结果。
- diff 范围检查结果。
- 未完成事项。
- 风险或疑点。

完成后不要提交 Git，等待决策/顾问窗口复核。
