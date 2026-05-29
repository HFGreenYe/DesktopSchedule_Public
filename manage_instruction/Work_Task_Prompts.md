# Work Task Prompts

用途：保存主窗口审核后的最终执行提示词。执行窗口只应执行本文件中的最终版本。

---

# 当前待执行提示词：CM-0

## CM-0：右键菜单现状审查与精确边界

请执行 `CM-0：右键菜单现状审查与精确边界`。本轮只做静态审查、代码阅读、搜索和日志记录，不修改任何源码，不实现右键菜单功能。

## 1. 本轮目标

基于当前功能规划，审查主界面和周界面右键上下文菜单的现有代码边界，为后续 `CM-1 / CM-2 / CM-3` 提供精确执行建议。

重点审查：

- 主界面 `DashboardView` 中适合接入右键菜单的区域。
- 主界面 `ScheduleCard` 已有右键菜单，确认新菜单不得与卡片右键菜单冲突。
- 周界面 `WeekWindow.bottom_panels` 的日期映射和事件过滤逻辑。
- 周界面白色空白区域右键菜单是否会影响左键选中、双击跳日视图、拖拽排序、卡片右键菜单。
- 现有 `SharedMoreMenu` / `ScheduleContextMenu` / `get_colored_icon` 是否可复用。
- 顶部按钮组和已有动作入口：
  - `handle_header_action(...)`
  - `switch_to_add_page(...)`
  - `switch_view(...)`
  - `WeekWindow.switch_to_add_page(...)`
  - `WeekWindow.view_selected`
- 是否应在 `CM-1` 新增 `src/ui/common/action_context_menu.py`，或最小复用/扩展现有菜单组件。

本轮必须输出：

- 主界面可右键区域地图。
- 主界面卡片右键冲突风险说明。
- 周界面可右键区域与日期映射地图。
- 可复用动作入口清单。
- 可复用 icon 清单。
- 菜单组件复用/新增建议。
- `CM-1 / CM-2 / CM-3` 是否需要继续拆分的建议。

## 2. 允许/禁止

### 允许修改

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

### 禁止修改

- `src/`
- `assets/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `.env`
- `.gitignore`
- `manage_instruction/Work_Formulation.md`
- `manage_instruction/Work_Instruction.md`
- `manage_instruction/ReconstructionDolder/`

### 禁止事项

- 不实现右键菜单。
- 不新增 UI 组件。
- 不修改任何 Python 源码。
- 不修改 QSS。
- 不新增 assets。
- 不写数据库。
- 不提交 Git。
- 不根据规划直接执行 `CM-1 / CM-2 / CM-3`。

若开工前已有 diff，必须在 `Work_Log.md` 中单独记录，并区分是否属于本轮产生。

## 3. 具体任务

### 3.1 读取规划文件

读取以下文件，确认当前阶段合同和历史架构原则：

```powershell
Get-Content -Path manage_instruction\Work_Formulation.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
Get-Content -Path manage_instruction\ReconstructionDolder\Work_Formulation.md -Encoding UTF8
Get-Content -Path manage_instruction\ReconstructionDolder\History_Instruction.md -Encoding UTF8
```

需要在日志里记录确认到的架构原则：

- 新功能优先兼容式旁路，不一次性替换旧 UI 流程。
- 新公共 UI 组件优先放入 `src/ui/common/` 或 `src/ui/utils/`。
- 右键菜单不得直接大段塞入 `MainWindow` / `WeekWindow`。
- 不伪实现四象限、换肤、排序、筛选。
- 视图切换和添加来源优先复用既有路由与添加入口。

### 3.2 审查主界面右键区域

读取并搜索：

```powershell
Get-Content -Path src\ui\dashboard.py -Encoding UTF8
Get-Content -Path src\ui\main_window.py -Encoding UTF8
rg -n "class DashboardView|class ScheduleCard|scroll|scroll_area|scroll_content|card|empty|placeholder|setContextMenuPolicy|customContextMenuRequested|_show_context_menu|MouseButton|RightButton|contextMenu" src/ui/dashboard.py src/ui/main_window.py
```

输出：

- `DashboardView` 中日程列表容器、滚动区域、空状态区域、卡片区域分别在哪里。
- 哪些区域适合接入“主界面区域右键菜单”。
- 哪些区域不应接入，以避免覆盖 `ScheduleCard` 既有右键菜单。
- 当前 `ScheduleCard` 右键菜单入口和行为摘要。
- 主界面右键菜单接入建议位置。

### 3.3 审查周界面右键区域和日期映射

读取并搜索：

```powershell
Get-Content -Path src\ui\week_window.py -Encoding UTF8
Get-Content -Path src\ui\common\week_day_block.py -Encoding UTF8
rg -n "bottom_panels|eventFilter|MouseButtonPress|RightButton|LeftButton|card_dropped|WeekScheduleCard|ScheduleContextMenu|setContextMenuPolicy|customContextMenuRequested|current_selected_date|current_monday|_on_day_clicked|_on_day_double_clicked|switch_to_add_page|view_selected|_on_view_selected" src/ui/week_window.py src/ui/common/week_day_block.py
```

输出：

- `bottom_panels` 的创建位置、数量、索引与日期关系。
- 当前左键点击空白区域如何映射到日期。
- W-1 双击跳日视图链路是否可能与右键菜单冲突。
- 卡片拖拽和卡片右键菜单现有链路。
- 周界面白色空白区域右键菜单建议接入位置。
- 右键所在日期如何安全传递给添加逻辑。
- 过去日期禁止添加应复用或对齐哪个现有判断。

### 3.4 审查现有菜单组件和图标复用

读取并搜索：

```powershell
Get-Content -Path src\ui\components.py -Encoding UTF8
Get-Content -Path src\ui\header.py -Encoding UTF8
Get-ChildItem -Path assets\icons -Force
rg -n "class SharedMoreMenu|class ScheduleContextMenu|get_colored_icon|QMenu|QAction|QWidgetAction|addAction|exec|show_menu|Skin|theme|view|add|sort|filter|Calendar|todo" src/ui/components.py src/ui/header.py
```

输出：

- `SharedMoreMenu` 当前职责、耦合对象、是否适合复用。
- `ScheduleContextMenu` 当前职责、耦合对象、是否适合复用。
- 是否建议在 `CM-1` 新增 `src/ui/common/action_context_menu.py`。
- 若复用现有组件，需要最小改动哪些点。
- 可复用 icon 清单，至少覆盖：
  - 换肤
  - 视图
  - 添加
  - 排序
  - 筛选
  - 日视图
  - 周视图
  - 月视图
  - 待办
  - 四象限占位

### 3.5 审查已有动作入口

搜索：

```powershell
rg -n "handle_header_action|switch_to_add_page|switch_view|view_selected|_on_view_selected|ViewRouter|MainController|default_to_schedule|current_selected_date|page_add.reset|set_time_data|on_schedule_saved" src/ui/main_window.py src/ui/week_window.py src/controllers
```

输出：

- 主界面 `添加` 应复用哪个入口。
- 主界面 `视图` 应复用哪个入口。
- 周界面 `添加` 应复用哪个入口。
- 周界面 `视图` 应复用哪个入口。
- 是否需要新增 Controller 方法，还是现阶段不需要。
- 哪些逻辑绝对不应在右键菜单组件中处理。

## 4. 验收命令

### 4.1 确认本轮没有源码修改

```powershell
git diff --name-only -- src
git diff --name-only -- assets
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
```

预期：以上命令均无输出。

### 4.2 确认只允许管理文档 diff

```powershell
git diff --name-only
git status --short --branch
```

预期最终只允许：

```text
manage_instruction/Work_Log.md
manage_instruction/Work_Task_Prompts.md
```

如果开工前已有其他 diff，必须在 `Work_Log.md` 中记录来源，不得混入本轮结论。

### 4.3 静态搜索记录

将以下搜索结果摘要写入日志，不需要全文粘贴：

```powershell
rg -n "setContextMenuPolicy|customContextMenuRequested|_show_context_menu|RightButton|MouseButtonPress|bottom_panels|SharedMoreMenu|ScheduleContextMenu|handle_header_action|switch_to_add_page|switch_view|view_selected" src/ui src/controllers
```

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：`CM-0（右键菜单现状审查与精确边界）`
- 开工前 git 状态。
- 实际修改文件。
- 读取的规划文件清单。
- 确认的架构原则。
- 主界面可右键区域地图。
- 主界面 `ScheduleCard` 既有右键菜单冲突风险。
- 周界面 `bottom_panels` 日期映射结论。
- 周界面右键与左键选中、双击跳转、拖拽排序、卡片右键菜单的冲突风险。
- `SharedMoreMenu` / `ScheduleContextMenu` 复用评估。
- 可复用 icon 清单。
- 主界面和周界面的动作入口清单。
- `CM-1` 建议：复用/扩展现有组件，还是新增 `src/ui/common/action_context_menu.py`。
- `CM-2` 建议：主界面接入位置、允许修改范围、验收重点。
- `CM-3` 建议：周界面接入位置、允许修改范围、验收重点。
- 是否建议继续拆分 `CM-1 / CM-2 / CM-3`。
- diff 范围检查结果。
- 未完成事项。
- 风险或疑点。

## 6. Work_Task_Prompts.md 处理要求

如需要维护复核锚点，可将当前状态更新为：

```text
CM-0 已执行，等待决策/顾问窗口复核。
下一步候选：CM-1。
```

不得在本轮自行写入 `CM-1` 的执行提示词。

## 7. 完成后要求

完成后不要提交 Git，等待决策/顾问窗口复核。
