请执行第六轮 6-0：静态审查与跨视图耦合定位。本轮只做代码阅读、搜索、分析和日志记录，不改源码。

## 1. 本轮目标

基于 manage_instruction/Work_Instruction.md 中第六轮阶段合同，定位当前跨视图协调逻辑，为后续 Controller / Router / EventBus 小步改造建立基线。

重点审查：

- MainWindow 中的主视图路由、添加页来源、picker 返回、跨视图刷新。
- WeekWindow 中的内部路由、picker 返回、刷新和对主窗口的通知。
- MonthWindow 中的视图切换、日期选择、恢复/挂起信号。
- TodoView 中的刷新信号、详情弹窗回流。
- TodoBoardWindow 中的内部路由、清单 picker、详情弹窗、刷新链路、对主窗口/其他视图的直接调用。
- global_signals 当前信号是否已足够支撑第六轮协调层。

本轮必须输出：

- 跨视图耦合地图。
- 每个耦合点的风险等级。
- 适合第六轮迁移的候选项。
- 应推迟到第八轮 UI 拆分的项。
- 是否需要后续补充 EventBus 信号。

## 2. 允许/禁止

本轮允许修改：

- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- src/
- main.py
- requirements.txt
- schedule.db
- Work_Snapshot.md
- Work_Formulation.md

禁止做任何源码改造、数据库写入、UI 调整、信号签名修改、controller 文件创建或功能实现。

若开工前已有 manage_instruction/Work_Instruction.md 或其他管理文档 diff，需要在 Work_Log.md 单独记录为开工前既有状态，不视为本轮源码改动。

## 3. 具体任务

1. 读取第六轮阶段合同：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8

2. 审查 src/utils/signals.py，记录 global_signals 当前已有信号、参数和兼容边界：

    Get-Content -Path src\utils\signals.py -Encoding UTF8

3. 定位主窗口路由与跨视图刷新：

    rg -n "def switch_view|source_view_for_add|list_picker_source|time_picker_mode|alarm_picker_mode|list_picker_mode|body_stack|setCurrentWidget|setCurrentIndex|req_refresh_all|schedule_updated|refresh_data|refresh_week|request_schedule_detail|_show_detail_popup|global_signals" src/ui/main_window.py

4. 定位周视图内部路由、picker 返回、刷新和主窗口通知：

    rg -n "body_stack|setCurrentWidget|setCurrentIndex|go_to_time_picker|go_to_alarm_picker|go_to_list_picker|back_from_time_picker|back_from_alarm_picker|back_from_list_picker|on_list_confirmed|refresh_week_data|schedule_updated|request_schedule_detail|view_selected|restore_requested|suspend_requested|global_signals" src/ui/week_window.py

5. 定位月视图切换、日期选择、恢复/挂起链路：

    rg -n "view_selected|date_selected|restore_requested|suspend_requested|refresh|show|hide|global_signals" src/ui/month_window.py

6. 定位待办视图刷新和详情弹窗回流：

    rg -n "req_refresh_all|refresh_data|req_show_detail|_show_detail_popup|schedule_updated|req_change_view|req_edit_list|global_signals" src/ui/todo.py

7. 定位待办看板内部路由、picker 返回、清单管理、刷新和详情弹窗回流：

    rg -n "view_stack|setCurrentWidget|go_to_list_picker|back_from_list_picker|on_list_confirmed|refresh_data|req_open_list_picker|req_show_detail|_show_detail_popup|window\(\)|parent\.|page_dashboard|page_todo|req_refresh_all|global_signals|soft_delete_category|hard_delete_category|check_category_status" src/ui/todo_board.py

8. 定位跨文件直接调用和信号连接：

    rg -n "page_dashboard|page_todo|week_window|month_window|todo_board|req_refresh_all|schedule_updated|request_schedule_detail|view_selected|restore_requested|suspend_requested|global_signals" src/ui

9. 检查 controller 目录当前状态：

    Get-ChildItem -Path src\controllers -Force

    Get-Content -Path src\controllers\__init__.py -Encoding UTF8

10. 形成耦合地图，至少按以下分类记录：

- 主视图切换链路。
- 添加页来源与返回链路。
- time/alarm/list picker add/edit 返回链路。
- 日程/待办保存后的刷新链路。
- 清单新增/删除/修改后的刷新链路。
- 周/月/待办窗口与主窗口之间的信号链路。
- 详情弹窗打开与更新后的刷新回流。
- global_signals 当前可用信号与缺口。

11. 给每个候选迁移点标记风险等级：

- 低：只做纯路由映射或只读状态记录，不影响写库和 UI 生命周期。
- 中：涉及一个 UI 文件的最小调用替换，但可明确回归。
- 高：涉及多个窗口、弹窗生命周期、刷新顺序、拖拽、写库或旧信号互相联动。

12. 分类输出建议：

- 适合第六轮迁移。
- 需要先做行为基线再决定。
- 应推迟到第八轮 UI 大文件拆分。
- 不应迁移或暂不迁移。

## 4. 验收命令

完成审查和日志记录后执行范围检查：

    git diff --name-only -- src

    git diff --name-only -- main.py

    git diff --name-only -- requirements.txt

    git diff --name-only -- schedule.db

    git diff --name-only

    git status --short --branch

预期：

- src 无 diff。
- main.py 无 diff。
- requirements.txt 无 diff。
- schedule.db 无 diff。
- 最终只允许 manage_instruction/Work_Log.md，以及必要时的 manage_instruction/Work_Task_Prompts.md。
- 如果开工前已有 manage_instruction/Work_Instruction.md diff，需要在日志中明确说明它是开工前既有状态，不属于 6-0 执行改动。

## 5. 日志要求

更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第六轮 6-0（静态审查与跨视图耦合定位）
- 开工前 git 状态，特别是是否已有管理文档 diff
- 实际修改文件
- 读取的阶段合同结论
- 静态搜索命令和关键结果
- global_signals 当前信号清单与缺口判断
- 跨视图耦合地图
- 每个耦合点的风险等级
- 适合第六轮迁移的候选项
- 需要先做行为基线再决定的候选项
- 应推迟到第八轮 UI 拆分的项
- diff 范围检查结果
- 未完成事项
- 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
