# 当前复核锚点：M-6 已执行

当前状态：

- `M-6（月界面右键菜单接入）` 已执行。
- 主窗口按提示词和日志对照复核，并对 offscreen 验证中暴露出的业务 handler `self.show()` 进行了最小修正。
- 下一步候选：`M-7（月界面功能补齐整体验收）`。
- 下方保留 M-6 已执行提示词全文，供日志对照复核。

## M-6：月界面右键菜单接入

请执行 `M-6（月界面右键菜单接入）`。本轮只在月界面日期格空白区域接入右键菜单，复用现有 `ActionContextMenu`，只实装“视图”和“添加”，不扩展其他功能。

## 1. 本轮目标

基于已完成的：

- CM 阶段公共 `ActionContextMenu`
- 主界面右键菜单接入
- 周界面右键菜单接入
- M-5 到 M-5g 月界面添加能力补齐

本轮为月界面接入右键菜单。

目标：

- 在月界面日期格空白区域右键，弹出 `ActionContextMenu`。
- 右键某个日期时，该日期作为本次菜单动作上下文。
- 右键不改变 `user_selected_date`。
- 右键不打开 / 关闭持久日期 panel。
- 右键不影响 hover 预览生命周期，除非弹出菜单前需要隐藏 hover 预览避免遮挡。
- 菜单“添加”：
  - 若右键日期是今天或未来，打开月界面添加表单。
  - 添加表单默认日期为右键日期。
  - 复用 M-5 到 M-5g 已补齐的月界面添加入口能力。
  - 若右键日期是过去日期，不打开添加表单，应提示不可添加或保持无动作。
- 菜单“视图”：
  - 日视图：跳转右键日期对应的日界面，并关闭月界面全部持久 panel。
  - 周视图：切换周视图。
  - 月视图：当前已在月视图，无动作。
  - 待办：切换待办视图。
  - 四象限：保持禁用，沿用 `ActionContextMenu` 默认禁用。
- 菜单“换肤 / 排序 / 筛选”：
  - 保持禁用 / 占位，不实现。
- 不修改数据库。
- 不修改添加保存逻辑。
- 不修改 `ActionContextMenu` 组件。
- 不修改主界面 / 周界面右键菜单。

本轮必须保持：

- M-1 marker 语义不变。
- M-2 单击选中 / 双击跳日视图语义不变。
- M-3 hover 只读预览语义不变。
- M-4 持久 panel 语义不变。
- M-5 到 M-5g 添加表单能力不回退。
- 新功能继续符合 `manage_instruction/Final_Formulation.md` 与 `manage_instruction/ReconstructionDolder/Work_Formulation.md` 的最终架构方向：功能补充可小步修改现有 UI，但不得把月界面功能扩展成新的大范围架构重写。

## 2. 允许/禁止

允许修改：

- `src/ui/month_window.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/ui/common/action_context_menu.py`
- `src/ui/dashboard.py`
- `src/ui/week_window.py`
- `src/ui/main_window.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- `src/ui/time_picker.py`
- `src/ui/alarm_picker.py`
- `src/ui/list_picker.py`
- `src/ui/calendar_pop.py`
- `src/ui/common/`
- `src/ui/popups/`
- `src/ui/utils/`
- `src/controllers/`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/theme/`
- `src/utils/signals.py`
- `src/utils/styles.py`
- `assets/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `manage_instruction/Final_Formulation.md`
- `manage_instruction/Work_Formulation.md`
- `manage_instruction/Work_Instruction.md`
- `manage_instruction/Work_Snapshot.md`
- `manage_instruction/ReconstructionDolder/`

禁止事项：

- 不新增右键菜单组件。
- 不修改 `ActionContextMenu`。
- 不修改主界面 / 周界面右键菜单。
- 不新增 EventBus / global signal。
- 不修改 `MainWindow` 路由。
- 不修改数据库和保存逻辑。
- 不真实写库。
- 不新增四象限功能。
- 不实现换肤 / 排序 / 筛选。
- 不提交 Git。

若开工前已有 diff，必须在 `Work_Log.md` 中单独记录，不视为本轮问题。

## 3. 具体任务

### 3.1 读取当前基线

读取：

```powershell
Get-Content -Path manage_instruction\Final_Formulation.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
Get-Content -Path manage_instruction\ReconstructionDolder\Work_Formulation.md -Encoding UTF8
Get-Content -Path src\ui\month_window.py -Encoding UTF8
Get-Content -Path src\ui\common\action_context_menu.py -Encoding UTF8
Get-Content -Path src\ui\dashboard.py -Encoding UTF8
Get-Content -Path src\ui\week_window.py -Encoding UTF8
```

重点确认：

- `ActionContextMenu` API：
  - `action_requested`
  - `view_requested`
  - `get_action(...)`
  - `get_view_action(...)`
- 主界面右键菜单如何连接 `action_requested / view_requested`。
- 周界面右键菜单如何用日期上下文调用添加。
- 月界面当前：
  - `eventFilter(...)`
  - `calendar_table_view`
  - `calendar_viewport`
  - `_get_add_target_date(...)`
  - `_on_add_clicked(...)`
  - `_on_view_selected(...)`
  - `_on_calendar_date_clicked(...)`
  - `_on_calendar_date_activated(...)`
  - `close_day_panels(...)`
  - `_hide_hover_preview(...)`
  - `open_day_panels`
  - `user_selected_date`

### 3.2 导入 ActionContextMenu

在 `src/ui/month_window.py` 中导入：

```python
from .common.action_context_menu import ActionContextMenu
```

要求：

- 不修改 `ActionContextMenu`。
- 不新增公共组件。
- 不新增 assets。

### 3.3 在月历 viewport 右键日期格时弹出菜单

在 `MonthWindow.eventFilter(...)` 中，对 `self.calendar_viewport` 的右键按下事件做最小处理。

建议逻辑：

- 只处理：
  - `obj is self.calendar_viewport`
  - `event.type() == QEvent.Type.MouseButtonPress`
  - `event.button() == Qt.MouseButton.RightButton`
- 使用当前已有日期命中方式，基于 viewport 的 `indexAt(event.pos())` 获取日期格。
- 建议复用当前 delegate 的日期解析能力：
  - `qdate = self.cell_delegate._date_for_index(index)`
- 若 index 无效或日期无效：
  - 不弹菜单，交给原逻辑或返回 `False`。
- 弹出菜单前可调用 `_hide_hover_preview()`，避免 hover 预览遮挡菜单。
- 不调用 `_on_calendar_date_clicked(...)`。
- 不修改 `user_selected_date`。
- 不调用 `_open_day_panel(...)`。
- 不调用 `close_day_panels()`，除非后续用户选择“日视图”跳转。
- 弹出菜单后返回 `True`，阻止右键继续传递到其他月历默认行为。

如果当前 `eventFilter(...)` 已经处理 hover / leave / mouse move，必须保持原有逻辑顺序，不破坏 M-3 hover 行为。

### 3.4 新增月界面右键上下文字段

在 `MonthWindow` 中新增轻量上下文字段，例如：

```python
self.context_menu_date = None
```

或等价字段。

要求：

- 只用于当前右键菜单动作。
- 不等同于 `user_selected_date`。
- 右键菜单关闭后可清空，也可在下一次右键覆盖。
- 不影响单击选中日期。
- 不影响添加按钮默认日期来源，除非是右键菜单“添加”动作显式使用。

### 3.5 新增菜单显示方法

新增方法，例如：

```python
def _show_context_menu_for_date(self, qdate, global_pos):
    ...
```

建议逻辑：

- `self.context_menu_date = qdate`
- `menu = ActionContextMenu(self)`
- 连接：
  - `menu.action_requested.connect(self._handle_context_action)`
  - `menu.view_requested.connect(self._handle_context_view)`
- 若右键日期是过去日期：
  - 本轮优先不动态禁用菜单 row，只在点击 `add` 时按日期拦截并 toast。
  - 如选择禁用 `menu.get_action("add")`，必须确认不修改 `ActionContextMenu`，并在日志说明禁用是否只影响 QAction 还是也影响视觉 row。
- 弹出：
  - `menu.exec(global_pos)`

优先策略：

- 为减少对 `ActionContextMenu` 内部 row 状态依赖，本轮建议不动态禁用 add action，只在 `_handle_context_action("add")` 中拦截过去日期。

### 3.6 新增菜单动作处理

新增方法，例如：

```python
def _handle_context_action(self, action_name):
    ...
```

只处理：

- `action_name == "add"`

行为：

- 获取 `target_date = self.context_menu_date`
- 若日期无效，返回。
- 若 `target_date < QDate.currentDate()`：
  - `show_toast("🚫 该日期已过期，无法添加日程")`
  - 不打开添加表单。
- 若日期合法：
  - 不改变 `user_selected_date`
  - 关闭/隐藏当前左侧 picker 页面：
    - `page_time.hide()`
    - `page_alarm.hide()`
    - `page_list.hide()`
  - 隐藏搜索框和视图选择器。
  - 调用：
    - `self.inline_add_view.reset(target_date)`
    - `self.inline_add_view.show()`
  - 不触发 `_on_add_clicked()`，因为 `_on_add_clicked()` 会使用用户选中日期 fallback，可能误用旧选中日期。
  - 不写数据库。

禁止：

- 不打开持久 panel。
- 不改变 `user_selected_date`。
- 不触发 `date_selected.emit(...)`。
- 不调用 `db_manager.add_schedule(...)`。

### 3.7 新增菜单视图处理

新增方法，例如：

```python
def _handle_context_view(self, view_name):
    ...
```

处理规则：

- `day`：
  - 使用右键日期作为上下文。
  - 先：
    - `_hide_hover_preview()`
    - `close_day_panels()`
  - emit：
    - `self.date_selected.emit(target_date)`
  - 这应沿用月界面双击日期跳日视图链路。
- `week`：
  - 可直接调用 `_on_view_selected("week")` 或 `self.view_selected.emit("week")`。
  - 不要求在本轮传递日期上下文，因为现有主路由未定义“跳指定周”的公开 API。
  - 若代码已有可安全传递日期的既有链路，可记录但不扩展。
- `month`：
  - 当前就在月视图，无动作。
- `todo`：
  - 调用 `_on_view_selected("todo")` 或 `self.view_selected.emit("todo")`。
- `priority`：
  - `ActionContextMenu` 默认禁用，理论上不会触发。
  - 如触发，直接 return。

禁止：

- 不改 `MainWindow.switch_view(...)`。
- 不新增路由参数。
- 不新增四象限功能。

### 3.8 保持现有行为不变

必须确认：

- 左键单击日期仍选中并打开/复用持久 panel。
- 双击 / activated 日期仍跳日视图并关闭持久 panel。
- 添加按钮仍使用 `user_selected_date` 或 fallback 日期。
- 右键不改变添加按钮后续默认日期。
- 右键菜单“添加”只使用右键日期本次上下文。

### 3.9 更新 Work_Log.md

至少记录：

- 本轮任务名称：`M-6（月界面右键菜单接入）`
- 开工前 git 状态
- 实际修改文件
- 是否存在开工前既有 diff
- `ActionContextMenu` 复用方式
- 右键日期命中方式
- 右键是否不改变 `user_selected_date`
- “添加”菜单动作实现方式
- 过去日期添加拦截结果
- “视图”菜单动作实现方式
- 日视图跳转是否关闭持久 panel
- 周/月/待办视图动作处理结果
- 是否保持换肤/排序/筛选/四象限未实现
- 是否未改主界面 / 周界面右键菜单
- 验证命令和结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

## 4. 验收命令

### 4.1 定位右键菜单链路

```powershell
rg -n "ActionContextMenu|context_menu_date|_show_context_menu_for_date|_handle_context_action|_handle_context_view|MouseButtonPress|RightButton|indexAt|_on_calendar_date_clicked|_on_calendar_date_activated|_get_add_target_date|_on_add_clicked|user_selected_date|date_selected.emit|view_selected.emit|close_day_panels|_hide_hover_preview" src/ui/month_window.py
```

预期：

- `ActionContextMenu` 只在 `month_window.py` 中新增月界面复用。
- 存在右键处理方法。
- 存在 context date 字段或等价上下文。
- 右键 add 不调用 `_on_add_clicked()`。
- 日视图跳转会关闭 panel。

### 4.2 import 验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.month_window import MonthWindow; from src.ui.common.action_context_menu import ActionContextMenu; print('month context imports ok', MonthWindow, ActionContextMenu)"
```

### 4.3 offscreen 构造验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); print('month created', w is not None); assert hasattr(w, '_show_context_menu_for_date'); assert hasattr(w, '_handle_context_action'); assert hasattr(w, '_handle_context_view')"
```

### 4.4 右键添加不改变 user_selected_date 验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); selected=QDate.currentDate().addDays(5); context=QDate.currentDate().addDays(2); w.user_selected_date=selected; w.context_menu_date=context; w._handle_context_action('add'); print('user selected', w.user_selected_date.toString('yyyy-MM-dd')); print('inline selected', w.inline_add_view.selected_date.toString('yyyy-MM-dd')); assert w.user_selected_date == selected; assert w.inline_add_view.selected_date == context; assert w.inline_add_view.isVisible()"
```

### 4.5 过去日期右键添加拦截验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); past=QDate.currentDate().addDays(-1); w.context_menu_date=past; w._handle_context_action('add'); print('inline visible', w.inline_add_view.isVisible()); assert not w.inline_add_view.isVisible()"
```

### 4.6 日视图跳转信号与关闭 panel 验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); target=QDate.currentDate().addDays(1); hits=[]; w.date_selected.connect(lambda d: hits.append(d)); p=type('DummyPanel', (), {'close': lambda self: setattr(self, 'closed', True)})(); p.closed=False; w.open_day_panels.append(p); w.context_menu_date=target; w._handle_context_view('day'); print('hits', [d.toString('yyyy-MM-dd') for d in hits]); print('panel closed', p.closed); print('panels', w.open_day_panels); assert hits == [target]; assert p.closed; assert w.open_day_panels == []"
```

### 4.7 周/月/待办视图动作验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); hits=[]; w.view_selected.connect(lambda v: hits.append(v)); w.context_menu_date=QDate.currentDate().addDays(1); w._handle_context_view('week'); w._handle_context_view('month'); w._handle_context_view('todo'); w._handle_context_view('priority'); print('view hits', hits); assert hits == ['week', 'todo']"
```

### 4.8 左键 / 双击关键链路静态确认

```powershell
rg -n "calendar.clicked.connect\(self._on_calendar_date_clicked\)|calendar.activated.connect\(self._on_calendar_date_activated\)|def _on_calendar_date_clicked|def _on_calendar_date_activated|date_selected.emit|close_day_panels|_open_day_panel" src/ui/month_window.py
```

预期：

- 左键 clicked 链路仍在。
- activated / 双击跳日链路仍在。
- `_on_calendar_date_activated(...)` 仍关闭持久 panel 并 emit `date_selected`。

### 4.9 不写数据库验证

```powershell
git diff --name-only -- schedule.db
```

预期无输出。

### 4.10 语法检查

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/month_window.py main.py
```

### 4.11 禁止范围检查

```powershell
git diff --name-only -- src/ui/common/action_context_menu.py
git diff --name-only -- src/ui/dashboard.py
git diff --name-only -- src/ui/week_window.py
git diff --name-only -- src/ui/main_window.py
git diff --name-only -- src/ui/add_view.py
git diff --name-only -- src/ui/add_view_week.py
git diff --name-only -- src/ui/time_picker.py
git diff --name-only -- src/ui/alarm_picker.py
git diff --name-only -- src/ui/list_picker.py
git diff --name-only -- src/ui/calendar_pop.py
git diff --name-only -- src/ui/common
git diff --name-only -- src/ui/popups
git diff --name-only -- src/ui/utils
git diff --name-only -- src/controllers
git diff --name-only -- src/data
git diff --name-only -- src/repositories
git diff --name-only -- src/services
git diff --name-only -- src/theme
git diff --name-only -- src/utils/signals.py
git diff --name-only -- src/utils/styles.py
git diff --name-only -- assets
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
```

预期以上均无输出。

### 4.12 总范围检查

```powershell
git diff --check
git diff --name-only
git status --short --branch
```

预期最终只允许：

```text
src/ui/month_window.py
manage_instruction/Work_Log.md
manage_instruction/Work_Task_Prompts.md
```

其中 `Work_Task_Prompts.md` 仅在维护本轮复核锚点时允许修改。

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：`M-6（月界面右键菜单接入）`
- 开工前 git 状态
- 实际修改文件
- 是否存在开工前既有 diff
- `ActionContextMenu` 复用方式
- 右键日期命中方式
- 右键菜单上下文字段
- 右键是否不改变 `user_selected_date`
- 添加动作是否使用右键日期
- 过去日期添加拦截结果
- 日视图动作是否 emit `date_selected(context_date)` 并关闭持久 panel
- 周/月/待办/四象限动作处理结果
- 是否保持换肤/排序/筛选禁用
- 是否未改主界面 / 周界面右键菜单
- 是否未写数据库
- import / offscreen / py_compile 验证结果
- 禁止范围检查结果
- 未完成事项
- 风险或疑点

## 6. 完成后要求

完成后不要提交 Git，等待决策/顾问窗口复核。
