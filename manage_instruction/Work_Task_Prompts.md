# Work Task Prompts

## 第八轮 8-4a：WeekWindow 低风险类提取候选只读复核

```markdown
请执行第八轮 8-4a：WeekWindow 低风险类提取候选只读复核。本轮只做静态审查、代码阅读、搜索和日志记录，不改源码。

## 1. 本轮目标

基于第八轮阶段合同和 8-0 结论，对 `src/ui/week_window.py` 中的 `WeekScheduleCard` 与 `DayBlock` 做提取前只读复核，判断哪一个更适合作为 8-4b 的唯一类提取试点。

本轮目标：

- 只读审查 `WeekScheduleCard`。
- 只读审查 `DayBlock`。
- 定位二者的：
  - 构造参数
  - public 属性
  - signal
  - event handler
  - paint / style / tooltip 依赖
  - db_manager / service / repository 依赖
  - WeekWindow 反向访问点
  - 生命周期管理点
  - 与拖拽、排序、详情弹窗、toast、刷新链路的关系
- 比较 `WeekScheduleCard` 与 `DayBlock` 的提取风险。
- 锁定 8-4b 唯一候选类，或明确“不适合直接提取，需要继续拆 8-4b 基线”。
- 不迁移任何类。
- 不新增文件。
- 不替换任何 import。
- 不改变周视图行为。

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

- 不新增 `src/ui/views/week_window.py`。
- 不新增 `src/ui/common/week_cards.py`。
- 不新增任何 WeekWindow 相关组件文件。
- 不修改 `src/ui/week_window.py`。
- 不修改 `src/ui/components.py`。
- 不修改 `src/ui/header.py`。
- 不修改 tooltip / toast / icon loader。
- 不清理 8-2b 遗留的 `header.py` unused import。
- 不提交 Git。

若开工前已有 diff，需在 `Work_Log.md` 单独记录，不视为本轮源码问题。

## 3. 具体任务

1. 读取当前基线：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
    Get-Content -Path src\ui\week_window.py -Encoding UTF8

2. 定位 `WeekScheduleCard` 与 `DayBlock` 定义范围：

    rg -n "^class WeekScheduleCard|^class DayBlock|^class WeekWindow" src/ui/week_window.py

3. 定位 `WeekScheduleCard` 的依赖与被使用点：

    rg -n "WeekScheduleCard|schedule_obj|data\\[|self\\.schedule|card_|_tooltip_filter|CountdownToolTipFilter|mousePressEvent|mouseMoveEvent|paintEvent|contextMenuEvent|deleteLater|removeEventFilter" src/ui/week_window.py

4. 定位 `DayBlock` 的依赖与被使用点：

    rg -n "DayBlock|date_obj|day_block|add_card|clear_cards|refresh|dragEnterEvent|dropEvent|dragMoveEvent|scheduleDropped|QMimeData|sort_order|card_dropped|date\\(" src/ui/week_window.py

5. 定位 `week_window.py` 中写库/排序/拖拽/详情弹窗/tooltip/toast 相关耦合：

    rg -n "db_manager|update_schedule|delete_schedule|add_schedule|sort_order|drag|drop|show_toast|ToolTipFilter|CountdownToolTipFilter|detail|popup|_show_detail|emit|pyqtSignal" src/ui/week_window.py

6. 定位 import 依赖：

    rg -n "^from |^import " src/ui/week_window.py

7. 分析 `WeekScheduleCard`：

    记录：

    - 类定义行号范围。
    - 构造函数签名。
    - 依赖的外部类/函数。
    - 是否直接访问 db_manager。
    - 是否直接调用 WeekWindow。
    - 是否发出 signal。
    - 是否安装 eventFilter。
    - 是否依赖 `CountdownToolTipFilter`。
    - 是否参与拖拽/排序。
    - 是否有自定义 paint / style。
    - 提取到新文件时需要带走哪些 import。
    - 提取后调用方需要改哪些 import。
    - 风险等级。

8. 分析 `DayBlock`：

    记录：

    - 类定义行号范围。
    - 构造函数签名。
    - 依赖的外部类/函数。
    - 是否直接访问 db_manager。
    - 是否直接调用 WeekWindow。
    - 是否发出 signal。
    - 是否管理 `WeekScheduleCard` 实例。
    - 是否参与拖拽/排序。
    - 是否有自定义 paint / style。
    - 是否触发详情弹窗或刷新链路。
    - 提取到新文件时需要带走哪些 import。
    - 提取后调用方需要改哪些 import。
    - 风险等级。

9. 给出 8-4b 建议：

    - 若 `WeekScheduleCard` 更低风险，建议 8-4b 只提取 `WeekScheduleCard`。
    - 若 `DayBlock` 更低风险，建议 8-4b 只提取 `DayBlock`。
    - 若二者都仍有不清晰耦合，建议 8-4b 继续只读或先做 import/依赖清理，不进行类迁移。

10. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

类定位：

    rg -n "^class WeekScheduleCard|^class DayBlock|^class WeekWindow" src/ui/week_window.py

WeekScheduleCard 依赖定位：

    rg -n "WeekScheduleCard|schedule_obj|data\\[|self\\.schedule|card_|_tooltip_filter|CountdownToolTipFilter|mousePressEvent|mouseMoveEvent|paintEvent|contextMenuEvent|deleteLater|removeEventFilter" src/ui/week_window.py

DayBlock 依赖定位：

    rg -n "DayBlock|date_obj|day_block|add_card|clear_cards|refresh|dragEnterEvent|dropEvent|dragMoveEvent|scheduleDropped|QMimeData|sort_order|card_dropped|date\\(" src/ui/week_window.py

写库/排序/拖拽/回流耦合定位：

    rg -n "db_manager|update_schedule|delete_schedule|add_schedule|sort_order|drag|drop|show_toast|ToolTipFilter|CountdownToolTipFilter|detail|popup|_show_detail|emit|pyqtSignal" src/ui/week_window.py

import 依赖定位：

    rg -n "^from |^import " src/ui/week_window.py

确认未新增 WeekWindow 拆分文件：

    Test-Path src\ui\common\week_cards.py
    Test-Path src\ui\views\week_window.py
    Test-Path src\ui\views\week_cards.py

WeekWindow import 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.week_window import WeekWindow, WeekScheduleCard, DayBlock; print('week imports ok', WeekWindow, WeekScheduleCard, DayBlock)"

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

- 本轮任务名称：第八轮 8-4a（WeekWindow 低风险类提取候选只读复核）
- 开工前 git 状态
- 实际修改文件
- `WeekScheduleCard` 定义范围与职责
- `WeekScheduleCard` 构造参数、signal、event handler、tooltip、拖拽、style、外部依赖
- `WeekScheduleCard` 是否直接访问 db_manager / Repository / Service
- `WeekScheduleCard` 提取风险等级
- `DayBlock` 定义范围与职责
- `DayBlock` 构造参数、signal、event handler、tooltip、拖拽、style、外部依赖
- `DayBlock` 是否直接访问 db_manager / Repository / Service
- `DayBlock` 提取风险等级
- 二者风险对比
- 8-4b 建议的唯一候选类
- 若不建议直接提取，说明原因和下一步只读/清理建议
- WeekWindow import 回归结果
- 8-3b toast helper 回归结果
- 8-2b icon loader 回归结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

特别记录：

- 本轮只读审查，不改源码。
- 本轮不拆 `week_window.py`。
- 本轮不新增任何 WeekWindow 组件文件。
- 本轮不修改 tooltip/toast/icon loader。
- 本轮只为 8-4b 锁定唯一候选类。

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
```
