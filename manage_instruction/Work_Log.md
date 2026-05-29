# Work Log

用途：记录当前阶段/当前小工单的执行过程、验证结果和风险。

历史日志归档见：

- `History_Log.md`

旧架构改写阶段日志已移入：

- `ReconstructionDolder/History_Log.md`

---

## 当前状态

架构改写主线已经结束。

当前进入功能补充阶段，优先完善月界面功能。暂不优先实现四象限视图。

---

## 2026-05-29 工作文档重建

- 背景：
  - 旧 `manage_instruction` 文档已由用户移入 `ReconstructionDolder/`。
  - 当前需要为后续三窗口联动重新建立轻量工作文档。

- 新建/重建文件：
  - `History_Instruction.md`
  - `History_Log.md`
  - `Workflow_Guide.md`
  - `Work_Formulation.md`
  - `Work_Instruction.md`
  - `Work_Log.md`
  - `Work_Task_Prompts.md`

- 不重建文件：
  - `code_pack.txt`
  - `Device_Sync_Guide.md`
  - `Work_Snapshot.md`
  - `Work_Discussion.md`

- 当前协作模式：
  - 主窗口：调度、审核、决策收口、最终提示词输出。
  - 决策窗口：提出方案供主窗口审核。
  - 执行窗口：按最终提示词执行具体任务。

- 当前阶段规划：
  - 先完善月界面。
  - 可穿插处理低风险交互增强，例如周界面日期双击跳转日视图。
  - 月界面稳定后，再制定后续功能补充规划。

- 未完成事项：
  - 尚未发布具体 M-0 / W-1 执行提示词。

- 风险或疑点：
  - 旧文档移入 `ReconstructionDolder/` 后，Git 当前可能显示旧文件删除和新文件重建，需要主窗口复核 diff 后再提交。

## 2026-05-29 功能补充 W-1（周界面日期双击跳转日视图）

- 本轮任务名称：功能补充 W-1（周界面日期双击跳转日视图）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 39]`
  - 既有变更：`M manage_instruction/Work_Task_Prompts.md`
  - 说明：开工前已有管理文档 diff，本轮不视为源码问题。
- 实际修改文件：
  - `src/ui/common/week_day_block.py`
  - `src/ui/week_window.py`
  - `src/ui/main_window.py`
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有 diff，本轮未新增修改）

- `DayBlock` 新增信号和事件说明：
  - 新增信号：`double_clicked = pyqtSignal(QDate)`。
  - 新增方法：`mouseDoubleClickEvent(self, event)`。
  - 左键双击时：`emit self.double_clicked(self.date)` 并 `event.accept()`。
  - 非左键双击时：调用 `super().mouseDoubleClickEvent(event)`。
  - 保持 `clicked = pyqtSignal(QDate)` 与 `mouseReleaseEvent(...)` 单击语义不变。

- `WeekWindow` 新增信号和转发说明：
  - 新增信号：`day_double_clicked = pyqtSignal(QDate)`。
  - `DayBlock` 连接：
    - 保留 `block.clicked.connect(self._on_day_clicked)`。
    - 新增 `block.double_clicked.connect(self._on_day_double_clicked)`。
  - 新增 `_on_day_double_clicked(self, qdate)`：
    - 先调用 `self._on_day_clicked(qdate)` 保持选中行为；
    - 再 `self.day_double_clicked.emit(qdate)` 转发给主窗口。

- `MainWindow` 日期跳转方法泛化说明：
  - 新增 `jump_to_date(self, qdate)`：
    - `py_date = qdate.toPyDate()`
    - `self.on_calendar_date_picked(py_date)`
    - `self.switch_view("day")`
  - 保留 `jump_to_date_from_month(self, qdate)` 方法名，改为调用 `self.jump_to_date(qdate)`。
  - 新增连接：`self.week_window.day_double_clicked.connect(self.jump_to_date)`。

- 单击行为是否保持不变：
  - 是。单击日期仍只更新周视图选中日期，不触发日视图跳转。

- 添加日程日期来源是否保持不变：
  - 是。`WeekWindow.switch_to_add_page(...)` 仍使用当前 `current_selected_date`，本轮未修改。

- 验证结果：
  - 链路定位命令通过：
    - `rg -n "double_clicked|day_double_clicked|mouseDoubleClickEvent|jump_to_date|jump_to_date_from_month|_on_day_double_clicked|_on_day_clicked" ...`
  - DayBlock import：
    - `day block import ok <class 'src.ui.common.week_day_block.DayBlock'>`
  - WeekWindow import：
    - `week import ok <class 'src.ui.week_window.WeekWindow'> <class 'src.ui.common.week_day_block.DayBlock'>`
  - MainWindow import：
    - `main window import ok <class 'src.ui.main_window.MainWindow'>`
  - DayBlock offscreen 信号验证：
    - 输出：`hits [('double', PyQt6.QtCore.QDate(2026, 5, 30))]`
    - 断言通过：双击仅触发 `double_clicked`，且日期正确。
  - WeekWindow offscreen 连接验证：
    - 输出：`selected 2026-05-31`，`hits ['2026-05-31']`
    - 断言通过：双击后选中日期与对外信号一致。
  - MainWindow offscreen 方法验证：
    - 输出：`dashboard date 2026-06-01`
    - 断言通过：跳转后日视图日期更新，并保留 `jump_to_date_from_month`。
  - 语法检查：
    - `python -m py_compile src/ui/common/week_day_block.py src/ui/week_window.py src/ui/main_window.py main.py`
    - 结果：通过。

- diff 范围检查结果：
  - 禁止范围均无 diff：
    - `src/ui/month_window.py`
    - `src/ui/dashboard.py`
    - `src/ui/add_view.py`
    - `src/ui/add_view_week.py`
    - `src/ui/todo_board.py`
    - `src/ui/common/toast.py`
    - `src/ui/utils/icon_loader.py`
    - `src/controllers`
    - `src/data`
    - `src/repositories`
    - `src/services`
    - `src/theme`
    - `src/utils/signals.py`
    - `src/utils/styles.py`
    - `assets`
    - `main.py`
    - `requirements.txt`
    - `schedule.db`
  - 允许范围：
    - `git diff --name-only -- src/ui` 仅：
      - `src/ui/common/week_day_block.py`
      - `src/ui/main_window.py`
      - `src/ui/week_window.py`
  - 总范围：
    - `git diff --name-only`：
      - `manage_instruction/Work_Log.md`
      - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
      - `src/ui/common/week_day_block.py`
      - `src/ui/main_window.py`
      - `src/ui/week_window.py`
    - `git status --short --branch`：
      - `## main...temp/main [ahead 39]`
      - `M manage_instruction/Work_Log.md`
      - `M manage_instruction/Work_Task_Prompts.md`
      - `M src/ui/common/week_day_block.py`
      - `M src/ui/main_window.py`
      - `M src/ui/week_window.py`

- 未完成事项：
  - 等待决策/顾问窗口复核本轮变更。

- 风险或疑点：
  - `DayBlock.mouseReleaseEvent(...)` 旧实现本就未调用 `super()`；本轮保持原样，未扩大修改范围。

### 主窗口复核补记

- 复核时间：2026-05-29。
- 对照 `Work_Task_Prompts.md`：
  - `DayBlock.double_clicked`、`mouseDoubleClickEvent(...)` 已按提示词实现。
  - `WeekWindow.day_double_clicked` 与 `_on_day_double_clicked(...)` 已按提示词实现。
  - `MainWindow.jump_to_date(...)` 已复用 `on_calendar_date_picked(py_date)`，`jump_to_date_from_month(...)` 保持兼容。
  - 单击链路仍为 `DayBlock.clicked -> WeekWindow._on_day_clicked(...)`。
  - 添加日程日期来源 `current_selected_date` 未被修改。
- 主窗口复跑验证：
  - 链路定位、DayBlock import、WeekWindow import、MainWindow import：通过。
  - DayBlock offscreen 双击信号验证：通过。
  - WeekWindow offscreen 转发验证：通过。
  - MainWindow offscreen 跳转验证：通过。
  - `py_compile`：通过。
  - 禁止范围检查：无越界 diff。
- 复核修正：
  - 原执行日志的总范围漏列 `manage_instruction/Work_Log.md`，已补正；源码未因复核发生额外修改。
