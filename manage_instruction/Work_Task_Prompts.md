请执行第六轮 6-3：添加页来源与 picker 返回状态基线。本轮只做静态审查、代码阅读、搜索和日志记录，不改源码。

## 1. 本轮目标

基于 Work_Instruction.md 第六轮阶段合同，以及 Work_Log.md 中 6-0/6-1/6-2 的结论，审查并记录当前添加页来源、picker add/edit 模式、picker 返回路径和相关状态字段的旧行为基线。

本轮只做基线定位，不做接管，不创建新 controller 方法，不修改 UI。

重点定位：

- MainWindow 中的添加页来源记录：
  - source_view_for_add
  - page_add.btn_cancel 返回目标
  - handle_header_action 中进入 page_add 的逻辑
  - on_schedule_saved 保存后的返回目标
- MainWindow 中 time/alarm/list picker 的 add/edit 模式：
  - time_picker_mode
  - alarm_picker_mode
  - list_picker_mode
  - list_picker_source
  - editing_schedule
- WeekWindow 中独立 picker 返回路径：
  - time_picker_mode
  - alarm_picker_mode
  - list_picker_mode
  - body_stack 返回 page_add 或 page_week_board
- TodoBoardWindow 中独立 list picker 返回路径：
  - list_picker_mode
  - current_folder_id/current_folder_name
  - inline_add_view
  - page_list
  - view_stack 返回目标
- 哪些状态适合后续 6-4 做最小接管，哪些应留在 UI 或推迟到第八轮 UI 拆分。

本轮必须输出：

- 添加页来源与返回链路地图。
- time/alarm/list picker add/edit 返回链路地图。
- MainWindow、WeekWindow、TodoBoardWindow 各自状态字段清单。
- 每个状态字段的写入点、读取点、返回目标。
- 风险等级。
- 是否建议进入 6-4 最小接管。
- 如果建议接管，建议只接管哪个最低风险闭环。
- 如果不建议接管，说明原因。

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

禁止事项：

- 不修改 src/ui/main_window.py。
- 不修改 src/ui/week_window.py。
- 不修改 src/ui/todo_board.py。
- 不修改 controller 文件。
- 不新增 MainController/ViewRouter/RefreshCoordinator 方法。
- 不修改 signals.py。
- 不写数据库。
- 不改 UI 布局、文案、视觉和交互流程。
- 不迁移 picker 返回逻辑。
- 不迁移添加页来源逻辑。
- 不提交 Git。

若开工前已有管理文档 diff，需要在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取阶段合同和最近日志：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8

    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8

2. 定位 MainWindow 添加页来源与返回逻辑：

    rg -n "source_view_for_add|page_add\\.btn_cancel|on_schedule_saved|handle_header_action|setCurrentWidget\\(self\\.page_add|return_target|page_add\\.reset|default_to_schedule|body_stack\\.currentWidget" src/ui/main_window.py

3. 定位 MainWindow time picker add/edit 流程：

    rg -n "time_picker_mode|go_to_time_picker|go_to_time_picker_for_edit|back_from_time_picker|on_time_confirmed|req_open_time_picker|req_edit_time|editing_schedule|setCurrentWidget\\(self\\.page_time|setCurrentWidget\\(self\\.page_add|setCurrentWidget\\(self\\.page_dashboard" src/ui/main_window.py

4. 定位 MainWindow alarm picker add/edit 流程：

    rg -n "alarm_picker_mode|go_to_alarm_picker|go_to_alarm_picker_for_edit|back_from_alarm_picker|on_alarm_confirmed|req_open_alarm_picker|req_edit_alarm|editing_schedule|setCurrentWidget\\(self\\.page_alarm|setCurrentWidget\\(self\\.page_add|setCurrentWidget\\(self\\.page_dashboard" src/ui/main_window.py

5. 定位 MainWindow list picker add/edit 流程：

    rg -n "list_picker_mode|list_picker_source|go_to_list_picker|go_to_list_picker_for_edit|back_from_list_picker|on_list_confirmed|req_open_list_picker|req_edit_list|editing_schedule|setCurrentWidget\\(self\\.page_list|setCurrentWidget\\(self\\.page_add|setCurrentWidget\\(self\\.page_todo|setCurrentWidget\\(self\\.page_dashboard" src/ui/main_window.py

6. 定位 WeekWindow 添加页和 picker 返回流程：

    rg -n "page_add\\.btn_cancel|on_schedule_saved|switch_to_main_board|time_picker_mode|alarm_picker_mode|list_picker_mode|go_to_time_picker|go_to_time_picker_for_edit|back_from_time_picker|on_time_confirmed|go_to_alarm_picker|go_to_alarm_picker_for_edit|back_from_alarm_picker|on_alarm_confirmed|go_to_list_picker|go_to_list_picker_for_edit|back_from_list_picker|on_list_confirmed|body_stack|setCurrentWidget\\(self\\.page_add|setCurrentWidget\\(self\\.page_week_board|setCurrentWidget\\(self\\.page_time|setCurrentWidget\\(self\\.page_alarm|setCurrentWidget\\(self\\.page_list" src/ui/week_window.py

7. 定位 TodoBoardWindow list picker 与 inline add 返回流程：

    rg -n "inline_add_view|page_list|list_picker_mode|current_folder_id|current_folder_name|go_to_list_picker|go_to_list_picker_for_edit|back_from_list_picker|on_list_confirmed|_on_inline_add_saved|view_stack|setCurrentWidget\\(self\\.page_list|setCurrentWidget\\(self\\.inline_add_view|setCurrentWidget\\(self\\.folder_view|setCurrentWidget\\(self\\.stick_view|setCurrentWidget\\(self\\.empty_placeholder" src/ui/todo_board.py

8. 读取必要代码片段并记录关键行号。

建议按需使用类似命令：

    Get-Content -Path src\ui\main_window.py -Encoding UTF8 | Select-Object -Skip 110 -First 390

    Get-Content -Path src\ui\main_window.py -Encoding UTF8 | Select-Object -Skip 500 -First 80

    Get-Content -Path src\ui\week_window.py -Encoding UTF8 | Select-Object -Skip 730 -First 210

    Get-Content -Path src\ui\todo_board.py -Encoding UTF8 | Select-Object -Skip 1510 -First 170

9. 形成 MainWindow 基线地图，至少记录：

- 添加页取消返回目标。
- 添加页保存后返回目标。
- 从 dashboard/todo 进入添加页时 default_to_schedule 的判断。
- time picker add 模式返回目标。
- time picker edit 模式返回目标和刷新目标。
- alarm picker add 模式返回目标。
- alarm picker edit 模式返回目标和刷新目标。
- list picker add 模式返回目标。
- list picker edit 模式在 dashboard/todo 来源下的返回目标和刷新目标。
- source_view_for_add 与 list_picker_source 的写入点和读取点。

10. 形成 WeekWindow 基线地图，至少记录：

- 添加页取消返回目标。
- 添加页保存后返回目标。
- time/alarm/list picker add 模式返回目标。
- time/alarm/list picker edit 模式返回目标。
- 编辑后 refresh_week_data 与 schedule_updated.emit 的触发位置。

11. 形成 TodoBoardWindow 基线地图，至少记录：

- inline_add_view 打开 list picker 的路径。
- add 模式 list picker confirm 后返回目标。
- edit 模式 list picker confirm 后返回目标。
- current_folder_id/current_folder_name 对返回目标的影响。
- view_stack 在 folder/stick/empty/page_list/inline_add_view 之间的切换规则。

12. 给每个候选接管点标记风险等级：

- 低：纯状态字段读取/写入点清晰，不涉及写库和多窗口刷新。
- 中：涉及一个 UI 文件内的 add/edit 返回路径，但可静态回归。
- 高：涉及多个窗口、编辑写库、刷新顺序、详情弹窗或 TodoBoard 多状态 view_stack。

13. 输出后续 6-4 建议：

- 如果建议执行 6-4，明确只建议接管一个最低风险闭环。
- 如果不建议执行源码接管，记录应继续拆更小基线或推迟。
- 明确不建议一次性迁移 MainWindow 全部 picker 状态。
- 明确不建议在 6-4 同时碰 WeekWindow 和 TodoBoardWindow。

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
- 如果开工前已有管理文档 diff，需要在日志中明确说明它是开工前既有状态，不属于 6-3 执行改动。

## 5. 日志要求

更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第六轮 6-3（添加页来源与 picker 返回状态基线）
- 开工前 git 状态
- 实际修改文件
- 读取的阶段合同和 6-0/6-1/6-2 结论
- 静态搜索命令和关键结果
- MainWindow 添加页来源与返回链路地图
- MainWindow time/alarm/list picker add/edit 返回链路地图
- WeekWindow 添加页与 picker 返回链路地图
- TodoBoardWindow list picker 与 inline add 返回链路地图
- 状态字段清单：
  - source_view_for_add
  - list_picker_source
  - time_picker_mode
  - alarm_picker_mode
  - list_picker_mode
  - editing_schedule
  - current_folder_id/current_folder_name
- 每个状态字段的写入点、读取点、返回目标
- 风险等级
- 适合 6-4 最小接管的候选项
- 不适合 6-4 接管、应推迟或继续拆分的项
- diff 范围检查结果
- 未完成事项
- 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
