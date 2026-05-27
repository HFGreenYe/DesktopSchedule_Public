# Work Task Prompts

## 第八轮 8-5：TodoBoard 只读基线与低风险拆分候选确认

```markdown
请执行第八轮 8-5：TodoBoard 只读基线与低风险拆分候选确认。本轮只做静态审查、代码阅读、搜索和日志记录，不改源码。

## 1. 本轮目标

基于第八轮阶段合同和 8-0 结论，对 `src/ui/todo_board.py` 做拆分前只读基线审查，明确哪些类或函数适合后续低风险单点提取，哪些状态机、写库路径和跨视图链路必须暂缓。

本轮目标：

- 只读审查 `src/ui/todo_board.py`。
- 建立 TodoBoard 职责地图。
- 定位文件内类、函数、状态字段、写库调用、刷新链路、拖拽/排序、toast、tooltip、icon loader、folder/stick 双模式状态机。
- 判断后续 `8-6` 是否可以只提取一个低风险卡片类。
- 优先评估：
  - `FolderCard`
  - `AddFolderCard`
  - 其它纯展示小类或 helper
- 明确不适合第八轮直接迁移的高风险项：
  - `TodoBoardWindow` 主状态机
  - folder/stick 模式切换
  - sort_order 写回
  - list picker / inline add / refresh 通知链路
  - 详情弹窗借道 Dashboard 的回流路径
- 不迁移任何类。
- 不新增文件。
- 不替换任何 import。
- 不改变待办看板行为。

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

- 不新增 `src/ui/common/todo_board_cards.py`。
- 不新增任何 TodoBoard 相关组件文件。
- 不修改 `src/ui/todo_board.py`。
- 不修改 `src/ui/common/toast.py`。
- 不修改 `src/ui/common/week_day_block.py`。
- 不修改 `src/ui/utils/icon_loader.py`。
- 不修改 tooltip / toast / icon loader。
- 不修改数据层、服务层、控制层。
- 不提交 Git。

若开工前已有 diff，需在 `Work_Log.md` 单独记录，不视为本轮源码问题。

## 3. 具体任务

1. 读取当前基线：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
    Get-Content -Path src\ui\todo_board.py -Encoding UTF8

2. 定位 `todo_board.py` 文件结构和类分布：

    rg -n "^class |^def |^    def " src/ui/todo_board.py

3. 定位候选卡片类：

    rg -n "^class FolderCard|^class AddFolderCard|^class .*Card|FolderCard|AddFolderCard" src/ui/todo_board.py

4. 定位主状态机和模式字段：

    rg -n "view_mode|folder|stick|current_folder|current_folder_id|current_folder_name|view_stack|views_frame|page_list|folder_back|btn_folder|btn_stick" src/ui/todo_board.py

5. 定位写库和业务状态调用：

    rg -n "db_manager|add_schedule|update_schedule|delete_schedule|add_category|soft_delete_category|hard_delete_category|check_category_status|update_category_fields|toggle_pin_status|update_schedule_fields|update_schedule_status|sort_order" src/ui/todo_board.py

6. 定位拖拽、排序和写回链路：

    rg -n "drag|drop|mime|QDrag|QMimeData|sort|sort_order|_sort_by_priority|card_dropped|reorder|move" src/ui/todo_board.py

7. 定位 toast / tooltip / icon loader：

    rg -n "show_toast|toast_label|_apply_custom_tooltip|ToolTipFilter|get_colored_icon|_get_icon|QSvgRenderer|setIcon|setPixmap" src/ui/todo_board.py

8. 定位跨视图与详情弹窗回流：

    rg -n "main_window|page_dashboard|_show_detail_popup|ScheduleDetail|request_schedule_detail|global_signals|refresh|reload|load_|emit|clicked" src/ui/todo_board.py

9. 分析候选类：

    对 `FolderCard`、`AddFolderCard` 以及其它低风险候选分别记录：

    - 类定义行号范围。
    - 构造函数签名。
    - signal。
    - public 属性。
    - event handler。
    - 是否直接访问 db_manager。
    - 是否直接调用 TodoBoardWindow。
    - 是否依赖 `view_mode/current_folder_id/view_stack`。
    - 是否参与拖拽/排序写回。
    - 是否依赖 toast / tooltip / icon loader。
    - 提取到新文件时需要带走哪些 import。
    - 提取后调用方需要改哪些 import。
    - 风险等级。

10. 输出 8-6 建议：

    - 若存在明确低风险候选，建议 8-6 只提取一个类，并写明唯一候选类名。
    - 若 `FolderCard` 更低风险，建议 8-6 只提取 `FolderCard`。
    - 若 `AddFolderCard` 更低风险，建议 8-6 只提取 `AddFolderCard`。
    - 若二者仍有不清晰耦合，建议 8-6 继续只读或先做 import/依赖清理，不进行类迁移。

11. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

文件结构定位：

    rg -n "^class |^def |^    def " src/ui/todo_board.py

候选卡片类定位：

    rg -n "^class FolderCard|^class AddFolderCard|^class .*Card|FolderCard|AddFolderCard" src/ui/todo_board.py

主状态机定位：

    rg -n "view_mode|folder|stick|current_folder|current_folder_id|current_folder_name|view_stack|views_frame|page_list|folder_back|btn_folder|btn_stick" src/ui/todo_board.py

写库调用定位：

    rg -n "db_manager|add_schedule|update_schedule|delete_schedule|add_category|soft_delete_category|hard_delete_category|check_category_status|update_category_fields|toggle_pin_status|update_schedule_fields|update_schedule_status|sort_order" src/ui/todo_board.py

拖拽排序定位：

    rg -n "drag|drop|mime|QDrag|QMimeData|sort|sort_order|_sort_by_priority|card_dropped|reorder|move" src/ui/todo_board.py

toast / tooltip / icon loader 定位：

    rg -n "show_toast|toast_label|_apply_custom_tooltip|ToolTipFilter|get_colored_icon|_get_icon|QSvgRenderer|setIcon|setPixmap" src/ui/todo_board.py

跨视图与详情弹窗回流定位：

    rg -n "main_window|page_dashboard|_show_detail_popup|ScheduleDetail|request_schedule_detail|global_signals|refresh|reload|load_|emit|clicked" src/ui/todo_board.py

确认未新增 TodoBoard 拆分文件：

    Test-Path src\ui\common\todo_board_cards.py
    Test-Path src\ui\views\todo_board.py
    Test-Path src\ui\views\todo_board_cards.py

TodoBoard import 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.todo_board import TodoBoardWindow; print('todo board import ok', TodoBoardWindow)"

8-4b DayBlock 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.common.week_day_block import DayBlock; print('day block import ok', DayBlock)"

8-3b toast helper 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.common.toast import show_center_toast; print('toast helper import ok', show_center_toast)"

8-2b icon loader 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.utils.icon_loader import load_colored_svg_pixmap; print('icon loader import ok', load_colored_svg_pixmap)"

范围检查：

    git diff --name-only -- src
    git diff --name-only -- assets
    git diff --name-only -- main.py
    git diff --name-only -- requirements.txt
    git diff --name-only -- schedule.db
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

- 本轮任务名称：第八轮 8-5（TodoBoard 只读基线与低风险拆分候选确认）
- 开工前 git 状态
- 实际修改文件
- `todo_board.py` 类/函数结构地图
- 主状态机字段与职责地图
- 写库调用地图
- 拖拽/排序/写回链路地图
- toast / tooltip / icon loader 地图
- 跨视图与详情弹窗回流地图
- `FolderCard` 定义范围、职责、依赖、风险等级
- `AddFolderCard` 定义范围、职责、依赖、风险等级
- 其它候选类或 helper 的风险等级
- 高风险暂缓项
- 8-6 建议的唯一候选类
- 若不建议直接提取，说明原因和下一步只读/清理建议
- TodoBoard import 回归结果
- 8-4b DayBlock 回归结果
- 8-3b toast helper 回归结果
- 8-2b icon loader 回归结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

特别记录：

- 本轮只读审查，不改源码。
- 本轮不拆 `todo_board.py`。
- 本轮不新增任何 TodoBoard 组件文件。
- 本轮不修改 tooltip/toast/icon loader。
- 本轮不修改数据库或服务层。
- 本轮只为 8-6 判断是否存在唯一低风险候选类。

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
```
