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

## 2026-05-29 右键上下文菜单功能规划

- 本轮任务名称：主界面 / 周界面右键上下文菜单规划。
- 开工前 git 状态：
  - 原规划记录时为 `## main...temp/main [ahead 39]`，当时存在 W-1 未提交变更。
  - 提交前复核时 W-1 已提交：`792ab6c feat: jump to day view on week date double click`。
  - 当前状态为 `## main...temp/main [ahead 40]`，仅管理文档存在 diff。
  - 本轮只做管理文档规划，不新增源码修改。

- 读取的历史规划依据：
  - `manage_instruction/ReconstructionDolder/Work_Formulation.md`
  - `manage_instruction/ReconstructionDolder/History_Instruction.md`
  - `manage_instruction/ReconstructionDolder/Workflow_Guide.md`
  - 关键结论：
    - 新功能应沿用兼容式渐进路线，不一次性替换旧 UI 流程。
    - 视图切换和添加页来源应优先复用第六轮 `MainController` / `ViewRouter` 边界。
    - 新 UI 组件应沿用第七轮 `default.qss / skin preset` 和动态属性方向。
    - 新公共 UI 组件应沿用第八轮 `src/ui/common/` / `src/ui/utils/` 拆分方向。
    - 四象限、换肤 UI、排序、筛选等未实现功能不得伪实现。

- 实际修改文件：
  - `manage_instruction/Work_Formulation.md`
  - `manage_instruction/Work_Instruction.md`
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`

- 规划结果：
  - 当前阶段从“月界面优先”扩展为“月界面优先与上下文菜单增强”。
  - 右键菜单功能拆为：
    - `CM-0`：右键菜单现状审查与精确边界。
    - `CM-1`：公共 icon-text 上下文菜单组件试点。
    - `CM-2`：主界面日程区域右键菜单接入。
    - `CM-3`：周界面日期空白区域右键菜单接入。
    - `CM-4`：右键菜单整体验收。

- 主界面右键菜单规划：
  - 右键区域：主界面日程卡片区、空状态区或日程列表容器区，待 `CM-0` 精确定位。
  - 菜单项：
    - 换肤
    - 视图
    - 添加
    - 排序
    - 筛选
  - 本阶段先实装：
    - `视图`
    - `添加`
  - 其它项保留占位或禁用。

- 周界面右键菜单规划：
  - 右键区域：某日期对应的白色空白区域，待 `CM-0` 精确确认 `bottom_panels` 事件边界。
  - 添加行为：
    - 使用右键所在日期。
    - 过去日期不能添加日程。
  - 视图行为：
    - 使用与主界面一致的视图子菜单。
    - 四象限视图暂不实现。

- 菜单视觉规划：
  - 布局参考现有菜单：左侧图标，右侧文字。
  - 图标优先复用 `assets/icons/`：
    - `Skin.svg` / `theme.svg`
    - `view.svg`
    - `add.svg`
    - `sort.svg`
    - `filter.svg`
    - `Calendar.svg`
    - `todo.svg`
  - 不在本规划阶段新增 assets。

- 架构方向：
  - 不把完整右键菜单逻辑直接塞入 `MainWindow` 或 `WeekWindow`。
  - `CM-1` 应根据 `CM-0` 结论，新增或最小复用/扩展公共菜单组件。
  - 若现有 `SharedMoreMenu` / `ScheduleContextMenu` 不适合作为通用右键菜单，再新增 `src/ui/common/action_context_menu.py`。
  - 公共菜单组件只负责菜单 UI 和 action 信号，不直接访问数据库，不直接持有大窗口业务状态。
  - 主界面 / 周界面分别把菜单 action 接入已有动作入口。

- 当前未生成执行提示词：
  - `Work_Task_Prompts.md` 已重置为“暂无待执行提示词”。
  - 下一步应先由主窗口生成 `CM-0` 最终提示词。

- 未完成事项：
  - W-1 已完成并提交：`792ab6c`。
  - CM-0 提示词尚未生成。

- 风险或疑点：
  - 主界面右键区域需要防止与日程卡片现有右键菜单冲突。
  - 周界面白色区域右键需要防止破坏左键选中、双击跳转和拖拽排序。
  - 视图子菜单若做成紧邻弹窗，需要单独验证焦点、关闭和多菜单生命周期。
