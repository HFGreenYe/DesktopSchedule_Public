# Work Task Prompts

## 第八轮 8-7：MainWindow / MonthWindow / AddView 拆分候选复核

```markdown
请执行第八轮 8-7：MainWindow / MonthWindow / AddView 拆分候选复核。本轮只做静态审查、代码阅读、搜索和日志记录，不改源码。

## 1. 本轮目标

基于第八轮阶段合同和 8-0 到 8-6 的结果，对剩余中高风险 UI 文件做拆分候选复核，明确哪些边界适合第八轮继续小步提取，哪些应推迟到后续轮次。

本轮重点审查：

- `src/ui/main_window.py`
- `src/ui/month_window.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- `src/ui/schedule_detail_pop.py`

本轮目标：

- 建立剩余 UI 大文件的职责地图。
- 定位可拆边界：
  - toast / tooltip / icon loader
  - window controls
  - inline add
  - picker 回流
  - detail popup 回流
  - view selector
  - refresh / signal / coordinator 调用
  - 样式债务
- 判断是否还适合在第八轮继续做一个小提取工单。
- 输出建议：
  - 可继续在第八轮处理的低风险项
  - 需要先做只读基线的中风险项
  - 应推迟到后续轮次的高风险项
- 不迁移任何类。
- 不新增文件。
- 不替换任何 import。
- 不改变 UI 行为。

## 2. 允许/禁止

本轮允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

本轮禁止修改：

- `src/`
- `assets/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不修改 `main_window.py`。
- 不修改 `month_window.py`。
- 不修改 `add_view.py`。
- 不修改 `add_view_week.py`。
- 不修改 `schedule_detail_pop.py`。
- 不新增 `src/ui/common/` 下的新组件文件。
- 不修改 `src/ui/common/toast.py`。
- 不修改 `src/ui/common/week_day_block.py`。
- 不修改 `src/ui/common/todo_board_add_folder_card.py`。
- 不修改 `src/ui/utils/icon_loader.py`。
- 不修改数据层、服务层、控制层。
- 不提交 Git。

若开工前已有 diff，需在 `Work_Log.md` 单独记录，不视为本轮源码问题。

## 3. 具体任务

1. 读取当前基线：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8

2. 定位目标文件体量和类/函数结构：

    Get-ChildItem src\ui\main_window.py,src\ui\month_window.py,src\ui\add_view.py,src\ui\add_view_week.py,src\ui\schedule_detail_pop.py | Select-Object Name,Length
    rg -n "^class |^def |^    def " src/ui/main_window.py src/ui/month_window.py src/ui/add_view.py src/ui/add_view_week.py src/ui/schedule_detail_pop.py

3. 定位 toast / tooltip / icon loader 候选：

    rg -n "show_toast|toast_label|CustomToolTip|ToolTipFilter|setToolTip|_load_colored|_get_icon|get_colored_icon|QSvgRenderer|setIcon|setPixmap" src/ui/main_window.py src/ui/month_window.py src/ui/add_view.py src/ui/add_view_week.py src/ui/schedule_detail_pop.py

4. 定位 picker 回流、详情弹窗和跨视图协调：

    rg -n "picker|go_to_|back_from|confirm|confirmed|edit|editing|ScheduleDetail|_show_detail|open_popups|ViewRouter|MainController|RefreshCoordinator|global_signals|req_refresh|saved|emit" src/ui/main_window.py src/ui/month_window.py src/ui/add_view.py src/ui/add_view_week.py src/ui/schedule_detail_pop.py

5. 定位写库和业务状态调用：

    rg -n "db_manager|add_schedule|update_schedule|update_schedule_with_repeat|delete_schedule|update_schedule_fields|update_schedule_status|toggle_pin_status|add_category|soft_delete_category|hard_delete_category|check_category_status" src/ui/main_window.py src/ui/month_window.py src/ui/add_view.py src/ui/add_view_week.py src/ui/schedule_detail_pop.py

6. 定位样式债务：

    rg -n "setStyleSheet|StyleManager|get_.*style|role|variant|state|setProperty|default.qss|theme" src/ui/main_window.py src/ui/month_window.py src/ui/add_view.py src/ui/add_view_week.py src/ui/schedule_detail_pop.py

7. 分析 `main_window.py`：

    记录：

    - 主要职责。
    - 已由第六轮 Controller/Router 承接的边界。
    - 仍留在 MainWindow 内的展示辅助。
    - toast 是否已由 8-3b 收口。
    - 详情弹窗回流风险。
    - 视图容器/切换/挂起窗口风险。
    - 是否还有适合第八轮的小提取项。
    - 风险等级。

8. 分析 `month_window.py`：

    记录：

    - 主要职责。
    - inline add、calendar、weather、view selector、window controls、toast 的边界。
    - 是否直接写库。
    - 是否适合提取单个低风险类或 helper。
    - 与 `week_window.py` 的相似点和不可直接复用点。
    - 风险等级。

9. 分析 `add_view.py` 与 `add_view_week.py`：

    记录：

    - 两文件重复结构。
    - 保存/校验/重复规则/时间提醒/list picker 相关边界。
    - tooltip/icon loader 重复点。
    - 是否适合第八轮做单点提取。
    - 哪些应推迟到后续表单重构轮次。
    - 风险等级。

10. 分析 `schedule_detail_pop.py`：

    记录：

    - 主要职责。
    - source_view 分支。
    - 编辑回流。
    - 写库调用。
    - tooltip/icon loader/style 债务。
    - 为什么是否应继续推迟。
    - 风险等级。

11. 输出下一步建议：

    - 如果存在一个明确低风险候选，建议下一步编号和唯一目标。
    - 如果没有低风险候选，建议进入 `8-8` 第八轮整体验收与归档准备。
    - 不得建议一次性拆多个文件。
    - 不得建议直接拆高风险主流程。

12. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

文件体量和结构：

    Get-ChildItem src\ui\main_window.py,src\ui\month_window.py,src\ui\add_view.py,src\ui\add_view_week.py,src\ui\schedule_detail_pop.py | Select-Object Name,Length
    rg -n "^class |^def |^    def " src/ui/main_window.py src/ui/month_window.py src/ui/add_view.py src/ui/add_view_week.py src/ui/schedule_detail_pop.py

toast / tooltip / icon loader 定位：

    rg -n "show_toast|toast_label|CustomToolTip|ToolTipFilter|setToolTip|_load_colored|_get_icon|get_colored_icon|QSvgRenderer|setIcon|setPixmap" src/ui/main_window.py src/ui/month_window.py src/ui/add_view.py src/ui/add_view_week.py src/ui/schedule_detail_pop.py

picker / popup / coordinator 定位：

    rg -n "picker|go_to_|back_from|confirm|confirmed|edit|editing|ScheduleDetail|_show_detail|open_popups|ViewRouter|MainController|RefreshCoordinator|global_signals|req_refresh|saved|emit" src/ui/main_window.py src/ui/month_window.py src/ui/add_view.py src/ui/add_view_week.py src/ui/schedule_detail_pop.py

写库调用定位：

    rg -n "db_manager|add_schedule|update_schedule|update_schedule_with_repeat|delete_schedule|update_schedule_fields|update_schedule_status|toggle_pin_status|add_category|soft_delete_category|hard_delete_category|check_category_status" src/ui/main_window.py src/ui/month_window.py src/ui/add_view.py src/ui/add_view_week.py src/ui/schedule_detail_pop.py

样式债务定位：

    rg -n "setStyleSheet|StyleManager|get_.*style|role|variant|state|setProperty|default.qss|theme" src/ui/main_window.py src/ui/month_window.py src/ui/add_view.py src/ui/add_view_week.py src/ui/schedule_detail_pop.py

确认本轮未新增源码文件：

    git diff --name-only -- src
    git diff --name-only -- assets
    git diff --name-only -- main.py
    git diff --name-only -- requirements.txt
    git diff --name-only -- schedule.db

已提取组件 import 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.common.toast import show_center_toast; from src.ui.common.week_day_block import DayBlock; from src.ui.common.todo_board_add_folder_card import AddFolderCard; from src.ui.utils.icon_loader import load_colored_svg_pixmap; print('round 8 extracted imports ok')"

主要 UI import 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.main_window import MainWindow; from src.ui.month_window import MonthWindow; from src.ui.add_view import AddView; from src.ui.add_view_week import AddViewWeek; from src.ui.schedule_detail_pop import ScheduleDetailPopup; print('target ui imports ok')"

范围检查：

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

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第八轮 8-7（MainWindow / MonthWindow / AddView 拆分候选复核）
- 开工前 git 状态
- 实际修改文件
- 文件体量与类/函数结构摘要
- toast / tooltip / icon loader 候选地图
- picker / popup / coordinator 回流地图
- 写库调用地图
- 样式债务地图
- `main_window.py` 拆分候选与风险等级
- `month_window.py` 拆分候选与风险等级
- `add_view.py` / `add_view_week.py` 拆分候选与风险等级
- `schedule_detail_pop.py` 拆分候选与风险等级
- 可继续第八轮处理的低风险项
- 应推迟的高风险项
- 下一步建议：继续一个小提取工单，或进入 8-8 整体验收与归档准备
- 已提取组件 import 回归结果
- 主要 UI import 回归结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

特别记录：

- 本轮只读审查，不改源码。
- 本轮不新增组件文件。
- 本轮不修改 toast/tooltip/icon loader。
- 本轮不修改数据库或服务层。
- 本轮不一次性拆多个 UI 文件。
- 本轮用于判断第八轮是否还应继续提取，或是否应进入归档验收。

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
```
