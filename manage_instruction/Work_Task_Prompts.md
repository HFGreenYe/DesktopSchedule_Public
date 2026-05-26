# Work Task Prompts

## 第八轮 8-0：UI 拆分静态审查与职责地图

```markdown
请执行第八轮 8-0：UI 拆分静态审查与职责地图。本轮只做代码阅读、静态搜索、职责定位和日志记录，不修改源码。

## 1. 本轮目标

基于 `manage_instruction/Work_Instruction.md` 的第八轮阶段合同，建立 UI 拆分基线。

本轮目标：

- 审查当前 `src/ui/` 文件体量、类分布、公共组件重复、样式债务和高风险状态机。
- 输出 UI 职责地图。
- 输出可拆候选清单和风险等级。
- 明确哪些适合第八轮继续拆，哪些应推迟。
- 为后续 `8-1` 及之后的小工单提供依据。

本轮不做：

- 不修改源码。
- 不移动类。
- 不新增目录。
- 不替换 import。
- 不迁移样式。
- 不实现新功能。

## 2. 允许/禁止

本轮允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不拆 `todo_board.py`。
- 不拆 `week_window.py`。
- 不新增 `src/ui/components/` 等目录。
- 不改 `default.qss`。
- 不改 `theme_manager.py`。
- 不改 `styles.py`。
- 不改 `signals.py`。
- 不提交 Git。

若开工前已有 diff，需在 `Work_Log.md` 单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取第八轮合同和当前日志：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8

2. 统计 `src/ui/` 文件体量：

    - 按文件大小排序。
    - 标记超大文件和高风险文件。
    - 重点关注：
      - `todo_board.py`
      - `week_window.py`
      - `main_window.py`
      - `schedule_detail_pop.py`
      - `month_window.py`
      - `add_view.py`
      - `add_view_week.py`
      - `dashboard.py`
      - `components.py`
      - `todo.py`
      - `list_picker.py`
      - `header.py`

3. 定位 UI 类分布：

    - 搜索 `class ...`。
    - 记录每个大文件内主要类及职责。
    - 重点输出：
      - `todo_board.py` 类地图。
      - `week_window.py` 类地图。
      - `month_window.py` 类地图。
      - `main_window.py` 主要职责。
      - `components.py` / `widgets.py` 现有公共组件。

4. 定位重复公共逻辑：

    - `CustomToolTip`
    - `ToolTipFilter`
    - `CountdownToolTip`
    - `show_toast`
    - `_get_icon`
    - `_apply_custom_tooltip`
    - window control button 创建/样式
    - icon loader
    - card 类
    - inline add 类

5. 定位样式债务：

    - 统计 `setStyleSheet(...)` 热点。
    - 定位 `StyleManager` 调用点。
    - 定位已经使用动态属性的 UI 点。
    - 标记适合 `default.qss / role/state/variant` 的低风险样式候选。
    - 不要提出 light/dark mode matrix。

6. 定位高风险行为边界：

    - 数据库写入调用。
    - `db_manager` 直接调用。
    - `global_signals` 使用。
    - 第六轮 controller/router/refresh coordinator 调用。
    - picker 返回链路。
    - 详情弹窗回流。
    - 拖拽、右键菜单、sort_order 写回、folder/stick 状态机。
    - toast / timer / tooltip 生命周期。

7. 输出拆分建议：

    - 低风险候选。
    - 中风险候选。
    - 高风险暂缓项。
    - 建议下一步小工单。
    - 判断 `8-1` 是否适合只建 UI 包目录骨架。
    - 判断 `8-2/8-3/8-4/8-5` 是否需要进一步拆成 `8-xa/8-xb`。

8. 更新 `manage_instruction/Work_Log.md`。

## 4. 建议静态搜索命令

文件体量：

    Get-ChildItem -Path src\ui -File | Sort-Object Length -Descending | Select-Object Name,Length

目录现状：

    Get-ChildItem -Path src\ui -Directory | Select-Object Name

类分布：

    rg -n "^class " src/ui

大文件类分布：

    rg -n "^class " src/ui/todo_board.py src/ui/week_window.py src/ui/month_window.py src/ui/main_window.py src/ui/schedule_detail_pop.py src/ui/add_view.py src/ui/add_view_week.py

公共组件与重复逻辑：

    rg -n "CustomToolTip|ToolTipFilter|CountdownToolTip|show_toast|_get_icon|_apply_custom_tooltip|SharedMoreMenu|WindowControl|window control|btn_close|btn_sync|btn_more" src/ui

样式债务：

    rg -n "setStyleSheet\(" src/ui
    rg -c "setStyleSheet\(" src/ui/*.py
    rg -n "StyleManager\.|get_window_control_style|get_tooltip_style|get_button_style|get_menu_style|get_search_input_style" src/ui src/utils/styles.py
    rg -n "setProperty\(|property\(|role|state|variant|windowControl" src/ui src/theme/default.qss

写库和业务调用边界：

    rg -n "db_manager|add_schedule|update_schedule|delete_schedule|soft_delete|hard_delete|update_schedule_with_repeat|sort_order|toggle_pin|update_category|global_signals|refresh_requested|ViewRouter|MainController|RefreshCoordinator" src/ui

TodoBoard 重点定位：

    rg -n "class |def |_get_icon|_apply_custom_tooltip|show_toast|sort_order|folder|stick|view_stack|notify_main_window_refresh|db_manager|global_signals" src/ui/todo_board.py

WeekWindow 重点定位：

    rg -n "class |def |WeekScheduleCard|DayBlock|show_toast|btn_sync|btn_more|btn_close|view_selector|weather|db_manager|global_signals|refresh" src/ui/week_window.py

MonthWindow / MainWindow 重点定位：

    rg -n "class |def |InlineAdd|show_toast|btn_sync|btn_more|btn_close|view_selector|calendar|weather|db_manager|global_signals|refresh" src/ui/month_window.py src/ui/main_window.py

禁止范围检查：

    git diff --name-only -- src
    git diff --name-only -- main.py
    git diff --name-only -- requirements.txt
    git diff --name-only -- schedule.db

总范围检查：

    git diff --name-only
    git status --short --branch

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第八轮 8-0（UI 拆分静态审查与职责地图）
- 开工前 git 状态
- 实际修改文件
- UI 文件体量排序摘要
- 大文件类分布
- `todo_board.py` 职责地图
- `week_window.py` 职责地图
- `month_window.py` 职责地图
- `main_window.py` 职责地图
- `components.py` / `widgets.py` 现有公共组件结论
- tooltip/toast/icon loader/window control 重复逻辑分布
- `setStyleSheet(...)` 热点
- 适合 `default.qss / role/state/variant` 的低风险样式候选
- 写库、刷新、picker、详情弹窗、拖拽、右键菜单、sort_order、folder/stick 状态机风险点
- 低风险拆分候选
- 中风险拆分候选
- 高风险暂缓项
- 建议下一步小工单
- 是否建议 `8-1` 只建 UI 包目录骨架
- diff 范围检查结果
- 未完成事项
- 风险或疑点

特别记录：

- 本轮只读审查，不改源码。
- 第八轮继续基于 `default.qss / skin preset`。
- 不建立 light/dark mode matrix。
- 不把真实换肤 UI、`theme_color/设置字体` 功能闭环并入本轮。
- 不直接拆 `todo_board.py` 或 `week_window.py`。

如果 PowerShell 命令因路径或编码问题失败，请记录失败原因并换等价只读命令重跑。

完成后不要提交 Git，等待顾问窗口复核。
```
