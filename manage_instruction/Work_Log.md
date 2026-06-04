# Work Log

用途：记录当前阶段/当前小工单的执行过程、验证结果和风险。

历史日志归档见：

- `History_Log.md`

旧架构改写阶段日志已移入：

- `ReconstructionDolder/History_Log.md`

---

## 当前状态

右键上下文菜单阶段已完成并归档。

`M-5（月界面添加按钮日期来源联动）` 已执行完成并提交。

下一步建议：

- 先执行 `M-5b：月界面添加表单能力只读审查与 picker 承接方案确认`。
- 暂缓 `M-6（月界面右键菜单接入）`，直到月界面添加入口补齐。

---

## 2026-06-03 M-5 后续规划修订

- 任务目标：
  - 根据决策窗口评估，补充 `M-5` 后续月界面添加表单能力规划。
  - 明确 `M-6（月界面右键菜单接入）` 推迟到月界面添加入口补齐之后。
- 实际修改文件：
  - `manage_instruction/Work_Formulation.md`
  - `manage_instruction/Work_Instruction.md`
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`
- 规划结论：
  - 月界面左侧按键组和搜索框下方区域，类比主界面按键组下方的添加区域。
  - 月界面可做竖向压缩适配，不必完全复制主界面添加页 UI。
  - 月界面由于空间更竖，详情输入框后续可默认显示。
  - 进入 `M-6` 前，先补齐月界面添加表单能力，避免右键“添加”接到半成品入口。
- 新增路线：
  - `M-5b`：月界面添加表单能力只读审查与 picker 承接方案确认。
  - `M-5c`：月界面添加表单 UI 壳补齐。
  - `M-5d`：月界面时间选择接入。
  - `M-5e`：月界面提醒与清单接入。
  - `M-5f`：月界面紧急性 / 重复规则 / 保存结构对齐。
  - `M-5g`：月界面添加能力整体验收。
  - `M-6`：月界面右键菜单接入，后移到 M-5g 之后。
- 按决策窗口意见补强的边界：
  - `M-5b` 必须审查 picker 承接方式：月界面内部页面栈、复用主窗口 picker、或左侧局部切换 picker。
  - `M-5b` 必须确认 picker 返回后如何回填 `InlineAddViewMonth`。
  - `M-5b` 必须确认 picker 打开期间 hover 预览 / 持久 panel 是否需要隐藏。
  - `M-5b` 必须确认时间语义：默认日期、是否允许跨天、未选时间时继续 `00:00` 兼容还是提示必须选择时间。
  - `M-5b` 必须确认提醒依赖时间规则：未设置 start/end 时不能设置提醒，target_time 使用 start 优先还是 end 优先。
  - `M-5b` 必须确认清单 picker 的 `list_type`，以及月界面是否只支持添加日程。
  - `M-5b` 必须确认 `repeat_rule` 的真实入库值、显示值和 `ScheduleRepeatService` 归一化规则；后续不新增新规则，只沿用现有真实值体系，避免误伤历史默认值 `none`。
  - `M-5c` 只做 UI 壳时，如需要避免误触，按钮可禁用或显示轻量 toast；不得写入状态，不得打开 picker。
  - 保存后必须刷新月格 marker cache、hover 预览数据和已打开的同日期持久 panel；如暂时不能刷新全部 panel，至少关闭或重载目标日期 panel。
- `Work_Task_Prompts.md` 处理：
  - 已将旧 M-5 执行提示词替换为复核锚点。
  - 当前下一步候选为 `M-5b`。
  - 未写入 `M-5b` 最终执行提示词，等待决策/顾问窗口产出。
- 边界确认：
  - 未修改 `src/`、`assets/`、`main.py`、`requirements.txt`、`schedule.db`。
  - 未修改 `manage_instruction/ReconstructionDolder/`。
- 未完成事项：
  - 需要决策窗口产出 `M-5b` 最终提示词。
  - `M-6` 暂缓。

---

## 2026-06-03 M-5b 最终提示词写入

- 任务：
  - 审核并写入 `M-5b（月界面添加表单能力只读审查与 picker 承接方案确认）` 最终执行提示词。
- 实际修改文件：
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`
- 审核结论：
  - 提示词方向符合 `Work_Formulation.md` / `Work_Instruction.md` 中 M-5 后续规划。
  - 本轮只读审查，不改 `src/`、不写数据库、不接 picker。
  - 读取范围覆盖月界面、主/周添加页、time/alarm/list picker、主/周 picker 承接链路和 `ScheduleRepeatService`。
  - 输出要求覆盖 picker 承接方案、时间语义、提醒依赖时间、清单 `list_type`、`repeat_rule` 真实值体系和 M-5c~M-5g 边界。
- 本次修正：
  - 明确只读 repeat_rule 数据检查若因环境、权限或数据库状态失败，不得改源码或数据库，只记录失败原因并继续用静态代码形成保守结论。
  - 保留 `Work_Task_Prompts.md` 为唯一提示词落点，当前写入完整 M-5b 最终提示词。
- 下一步：
  - 执行窗口可按 `Work_Task_Prompts.md` 中最终 M-5b 提示词执行。

---

## 2026-06-03 Final_Formulation.md 新增

- 任务目标：
  - 从 `manage_instruction/ReconstructionDolder/Work_Formulation.md` 中摘取最终目标架构和长期演进原则。
  - 汇总当前架构改写后累积的技术债，形成后续功能规划优先读取的总纲文件。
- 实际修改文件：
  - `manage_instruction/Final_Formulation.md`
  - `manage_instruction/Work_Log.md`
- 写入内容：
  - 最终目标架构与当前实际目录对应关系。
  - 已完成的架构基础。
  - 后续功能开发约束。
  - 当前月界面功能补齐阶段状态。
  - Data / Repository / Service、Controller / Router / Refresh、Theme/QSS、UI 大文件、Month View、Weather、Git/文档流程等技术债清单。
  - 后续阶段建议和文档读取顺序。
- 边界确认：
  - 未修改 `manage_instruction/ReconstructionDolder/`。
  - 未修改 `src/`、`assets/`、`main.py`、`requirements.txt`、`schedule.db`。
- 未完成事项：
  - 后续若决策窗口认为技术债分类需要调整，可再单独修订本文。

---

## 2026-06-03 M-4 最终提示词写入

- 任务：
  - 审核并写入 `M-4（月格单击持久浮窗壳）` 最终执行提示词。
- 实际修改文件：
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`
- 审核修正：
  - 在读取上下文中加入 `manage_instruction/Final_Formulation.md`，确保执行窗口先读取最终架构目标和技术债索引。
  - 明确 `Final_Formulation.md` 本轮禁止修改。
  - 明确 `MonthDayPanel` 不依赖 `db_manager`、Repository、Service、`MainWindow` 或 `MonthWindow` 具体实例。
  - 明确 panel 手动关闭时必须从 `open_day_panels` 移除，避免悬挂引用。
  - 明确同一天重复单击优先复用/置顶已有 panel，不重复打开相同日期面板。
  - 增加同日复用验证命令和 `month_day_panel.py` 静态依赖检查。
  - 保留 M-1 三角数量角标、M-2 单击/双击语义、M-3 hover 预览、添加按钮日期来源、右键菜单未接入等边界。
- 下一步：
  - 执行窗口可按 `Work_Task_Prompts.md` 中最终 M-4 提示词执行。

## 2026-06-03 M-4（月格单击日期持久浮窗壳）

- 本轮任务名称：
  - `M-4（月格单击日期持久浮窗壳）`

- 开工前 git 状态：
  - `## main...temp/main [ahead 57]`

- 开工前既有 diff：
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`

- 实际修改文件：
  - `src/ui/month_window.py`
  - `src/ui/popups/month_day_panel.py`
  - `manage_instruction/Work_Log.md`

- 持久浮窗组件位置：
  - 新增 `src/ui/popups/month_day_panel.py`
  - 类名：`MonthDayPanel`

- 持久浮窗是否为独立顶层窗口：
  - 是。
  - 使用 `Qt.Tool | Qt.FramelessWindowHint`。
  - 设置了 `WA_ShowWithoutActivating` 和 `WA_TranslucentBackground`。
  - 不作为月历内部子控件，避免被 `MonthWindow` 裁剪。

- 单击日期如何打开持久浮窗且不跳日视图：
  - `_on_calendar_date_clicked(qdate)` 仍先：
    - 更新 `user_selected_date`
    - 调用 `_refresh_schedule_marker_cache()` 更新选中高亮
  - 然后：
    - 调用 `_hide_hover_preview()`，避免 hover 预览与持久 panel 重叠
    - 调用 `_open_day_panel(qdate)` 打开外侧 panel
  - 单击路径不 emit `date_selected`，不跳日视图。

- 持久浮窗定位方式，是否在月界面外侧：
  - 是。
  - 基于 `MonthWindow.frameGeometry().topRight()` 计算外侧位置。
  - `_get_day_panel_position(index)` 当前策略：
    - `x = topRight.x() + 16`
    - `y = topRight.y() + 24 + index * 36`
  - 结果是 panel 优先显示在月界面右侧，并按打开顺序做垂直错位。

- 多个持久浮窗如何并存和错位：
  - 使用 `open_day_panels` 保存所有已打开 panel。
  - 不同日期可同时存在多个 panel。
  - 新 panel 根据当前列表长度做垂直偏移，避免完全重叠。

- 同一天重复单击如何复用已有 panel：
  - 新增 `_find_open_day_panel(qdate)` 查找同一天已打开 panel。
  - 若已存在：
    - 直接 `show()`
    - `raise_()`
    - `activateWindow()`
  - 不重复创建同一天 panel。

- 关闭按钮如何关闭单个 panel：
  - `MonthDayPanel` 头部提供关闭按钮 `×`。
  - 点击关闭按钮调用 `close()`。
  - `MonthDayPanel.closeEvent(...)` 只发出 `closed.emit(self)`。
  - `MonthWindow` 侧连接 `panel.closed.connect(self._remove_day_panel)`，将其从 `open_day_panels` 移除。

- `open_day_panels` 如何维护：
  - 打开新 panel 时 append。
  - `closed` 信号触发 `_remove_day_panel(panel)` 时 remove。
  - `_find_open_day_panel()` 进入时会先过滤掉 `None` 残留引用。

- `close_day_panels()` 如何关闭全部 panel：
  - 遍历 `list(self.open_day_panels)`。
  - 对仍存在且有 `close()` 的对象调用 `close()`。
  - 最后统一 `self.open_day_panels.clear()`。
  - 即使用户已手动关闭过，重复关闭也不会抛异常。

- 月界面 hide/close/双击跳转时是否关闭全部 panel：
  - 是。
  - 双击 / activated 跳转前：
    - `_on_calendar_date_activated(qdate)` 先同步 `user_selected_date` 和高亮，再 `_hide_hover_preview()`，再 `close_day_panels()`，最后 `date_selected.emit(qdate)`。
  - `hideEvent(...)`：
    - 调用 `close_day_panels()`
    - 调用 `_hide_hover_preview()`
  - `closeEvent(...)`：
    - 调用 `close_day_panels()`
    - 调用 `_hide_hover_preview()`

- 是否保持 M-1 三角数量角标逻辑不变：
  - 是。
  - `schedule_marker_cache` / `schedule_marker_count_cache` 计算未改。
  - 今天金色日期逻辑未改。

- 是否保持 M-2 单击/双击语义不变：
  - 是。
  - `calendar.clicked` 仍连接 `_on_calendar_date_clicked`
  - `calendar.activated` 仍连接 `_on_calendar_date_activated`
  - `date_selected.emit(...)` 仍只在 activated 跳转路径触发
  - 单击仍不 emit `date_selected`

- 是否保持 M-3 hover 预览语义不变：
  - 是。
  - hover 预览仍是只读组件 `MonthDayHoverPreview`
  - hover 路径仍在 `viewport Leave` 后立即隐藏
  - hover 预览没有被改造成持久 panel

- 是否保持添加按钮日期来源不变：
  - 是。
  - `_on_add_clicked(...)` 仍使用 `self.calendar.selectedDate()`
  - 未改 `InlineAddViewMonth`
  - 未改数据库写入路径

- 是否未接右键菜单：
  - 是。

- 是否未写数据库：
  - 是。
  - 本轮仅复用现有只读 `hover_schedule_cache` 数据。

- 验证命令和结果：
  - `rg -n "MonthDayPanel|month_day_panel|open_day_panels|close_day_panels|_open_day_panel|user_selected_date|calendar\.clicked|calendar\.activated|date_selected\.emit|hover_preview|hovered_date|MonthDayHoverPreview|hideEvent|closeEvent|_on_add_clicked|selectedDate|ActionContextMenu|contextMenu" src/ui/month_window.py src/ui/popups`
    - 结果：持久 panel、生命周期清理、hover/activated/单击链路均已命中。
  - `rg -n "db_manager|Repository|Service|MainWindow|MonthWindow|DashboardView|TodoBoardWindow|global_signals|switch_view|switch_to_add_page|add_schedule|update_schedule|delete_schedule" src/ui/popups/month_day_panel.py`
    - 结果：无输出。
    - 说明：新 panel 组件无运行期业务依赖。
  - import 验证：
    - `MonthWindow / CalendarCellDelegate / InlineAddViewMonth / MonthDayHoverPreview`：通过
    - `MonthDayPanel`：通过
  - offscreen 构造验证：
    - `MonthWindow()` 可构造
    - `has open_day_panels == True`
    - 初始 `panel count == 0`
    - `has close_day_panels == True`
  - 单击打开 panel 验证：
    - 调用 `_on_calendar_date_clicked(QDate(2026, 6, 15))`
    - 结果：
      - `user_selected_date == 2026-06-15`
      - `date_selected hits == 0`
      - `panel count == 1`
  - 同日复用验证：
    - 同一天连续两次 `_on_calendar_date_clicked(...)`
    - 结果：`same day counts 1 1`
  - 关闭全部 panel 验证：
    - 连续打开两天 panel 后调用 `close_day_panels()`
    - 结果：`before close 2`，`after close 0`
  - 双击 / activated 路径验证：
    - 先打开一个 panel，再调用 `_on_calendar_date_activated(QDate(2026,6,16))`
    - 结果：
      - `before activated panels 1`
      - `after activated panels 0`
      - `hits == ['2026-06-16']`
  - M-3 hover 回归验证：
    - `_show_hover_preview(...)` 后 `hover visible == True`
    - `_hide_hover_preview()` 后 `hover hidden == False`
    - 说明：这里打印的是 `isVisible()`，输出 `False` 表示已隐藏；断言通过。
  - hide / close 生命周期验证：
    - `hideEvent(QHideEvent())` 前后 panel 数量：`1 -> 0`
    - `closeEvent(QCloseEvent())` 前后 panel 数量：`1 -> 0`
  - M-2 行为静态回归：
    - `calendar.clicked` 仍连接 `_on_calendar_date_clicked`
    - `calendar.activated` 仍连接 `_on_calendar_date_activated`
    - `date_selected.emit(...)` 仍只在 activated 路径中
    - `_on_add_clicked(...)` 仍使用 `selectedDate()`
  - 语法检查：
    - 使用 `py_compile.compile(..., cfile=%TEMP%\\*.m4.pyc, doraise=True)` 编译：
      - `src/ui/month_window.py`
      - `main.py`
      - `src/ui/popups/month_day_hover_preview.py`
      - `src/ui/popups/month_day_panel.py`
    - 结果：通过。

- diff 范围检查结果：
  - 禁止范围均无 diff：
    - `src/ui/main_window.py`
    - `src/ui/calendar_pop.py`
    - `src/ui/common/action_context_menu.py`
    - `src/ui/common`
    - `src/ui/dashboard.py`
    - `src/ui/week_window.py`
    - `src/ui/todo.py`
    - `src/ui/todo_board.py`
    - `src/controllers`
    - `src/services`
    - `src/data`
    - `src/repositories`
    - `src/theme`
    - `src/utils/signals.py`
    - `src/utils/styles.py`
    - `assets`
    - `main.py`
    - `requirements.txt`
    - `schedule.db`
    - `manage_instruction/Final_Formulation.md`
    - `manage_instruction/Work_Formulation.md`
    - `manage_instruction/Work_Instruction.md`
    - `manage_instruction/Work_Snapshot.md`
    - `manage_instruction/History_Instruction.md`
    - `manage_instruction/History_Log.md`
    - `manage_instruction/ReconstructionDolder`
  - 允许范围：
    - `src/ui/month_window.py`
    - `src/ui/popups/month_day_panel.py`
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`（开工前既有）

- 未完成事项：
  - 未实现添加按钮优先使用用户选中日期，留待 `M-5`。
  - 未接入月界面右键菜单，留待 `M-6`。
  - 当前持久 panel 仍是壳 / 简版只读列表，未提供编辑能力。

- 风险或疑点：
  - 当前 panel 外侧定位只做了右侧 + 垂直偏移，未做屏幕边界回退；如果屏幕右边界不足，后续需单开小工单处理，不在本轮扩大。
  - `raise_()` / `activateWindow()` 在 offscreen 验证下只能确认调用路径，不代表真实桌面环境下一定带来完全一致的焦点效果；当前不影响功能边界。

---

## 2026-06-03 M-4 持久浮窗屏幕边界回退小修

- 任务目标：
  - 在 M-4 已完成的持久浮窗壳基础上，补充外侧 panel 的屏幕边界回退，避免月界面靠近屏幕右边缘时 panel 出屏。
- 实际修改文件：
  - `src/ui/month_window.py`
  - `manage_instruction/Work_Log.md`
- 修改内容：
  - `_get_day_panel_position(...)` 增加 `panel` 参数，用 `panel.sizeHint()` 估算 panel 宽高。
  - 默认仍优先放在月界面右侧。
  - 如果右侧空间不足，则回退到月界面左侧。
  - 最终使用当前屏幕 `availableGeometry()` 将 x/y 限制在屏幕可用区域内。
  - `_open_day_panel(...)` 创建 panel 后，将 panel 传入 `_get_day_panel_position(...)` 计算位置。
- 保持不变：
  - 未改变单击打开 panel 语义。
  - 未改变同日复用逻辑。
  - 未改变双击关闭 panel 并跳转日界面逻辑。
  - 未改变 M-1 角标、M-2 单击/双击、M-3 hover 预览、添加按钮日期来源和右键菜单边界。
  - 未修改数据层、服务层、控制层、主题、assets 或 `schedule.db`。
- 风险或疑点：
  - 当前只做单屏可用区域约束；多屏交界和极端小屏下的更精细级联布局后续可再单独优化。

---

## 2026-06-03 M-5 最终提示词写入

- 任务：
  - 审核并写入 `M-5（月界面添加按钮日期来源联动）` 最终执行提示词。
- 实际修改文件：
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`
- 审核修正：
  - 在阶段依据中补充 `Final_Formulation.md`。
  - 明确 `_get_add_target_date()` 应优先使用有效的 `user_selected_date`，无用户选中或无效时回退 `calendar.selectedDate()`。
  - 明确目标日期无效时应安全返回或沿用现有提示逻辑，不进入添加页。
  - 明确添加按钮不得打开、关闭或修改持久 panel 列表。
  - 明确添加按钮不得改变 hover 预览的显示/隐藏生命周期。
  - 在验证命令中增加 panel 数量不变检查，确保 M-4 持久浮窗语义不被 M-5 破坏。
- 下一步：
  - 执行窗口可按 `Work_Task_Prompts.md` 中最终 M-5 提示词执行。

## 2026-06-03 M-5（月界面添加按钮日期来源联动）

- 本轮任务名称：
  - `M-5（月界面添加按钮日期来源联动）`

- 开工前 git 状态：
  - `## main...temp/main [ahead 59]`

- 开工前既有 diff：
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`

- 实际修改文件：
  - `src/ui/month_window.py`
  - `manage_instruction/Work_Log.md`

- 添加目标日期解析方法：
  - 新增 `MonthWindow._get_add_target_date()`。
  - 规则：
    - 若 `self.user_selected_date` 存在且有效，则返回 `self.user_selected_date`
    - 否则返回 `self.calendar.selectedDate()`

- 无用户选中日期时是否沿用 `calendar.selectedDate()`：
  - 是。
  - 验证结果：
    - `target == w.calendar.selectedDate()`

- 有用户选中日期时是否优先使用 `user_selected_date`：
  - 是。
  - 验证结果：
    - 先 `_on_calendar_date_clicked(QDate.currentDate().addDays(3))`
    - 再调用 `_get_add_target_date()`
    - 返回值等于 `user_selected_date`

- 过去日期不可添加是否基于最终目标日期判断：
  - 是。
  - `_on_add_clicked(...)` 改为先获取 `target_date = self._get_add_target_date()`
  - 过去日期判断改为基于 `target_date < today`
  - 当 `target_date` 无效时，安全返回，不进入添加页

- 是否保持 `InlineAddViewMonth._on_save(...)` 不变：
  - 是。
  - 未改 `InlineAddViewMonth._on_save(...)`

- 是否保持 `db_manager.add_schedule(...)` 不变：
  - 是。
  - 未改写库结构和调用路径

- 是否保持 M-1 三角数量角标逻辑不变：
  - 是。
  - marker 颜色、数量、过滤规则未改
  - 今天金色日期逻辑未改

- 是否保持 M-2 单击/双击语义不变：
  - 是。
  - `calendar.clicked` 仍连接 `_on_calendar_date_clicked`
  - `calendar.activated` 仍连接 `_on_calendar_date_activated`
  - `date_selected.emit(...)` 仍只在 activated 跳转路径中

- 是否保持 M-3 hover 预览语义不变：
  - 是。
  - hover preview 文件无 diff
  - hover 命中、只读展示、移出隐藏逻辑未改

- 是否保持 M-4 持久浮窗语义不变：
  - 是。
  - 单击仍会打开/复用持久 panel
  - `_on_add_clicked(...)` 不关闭已有 panel
  - `open_day_panels` 生命周期未改
  - `month_day_panel.py` 无 diff

- 是否未接右键菜单：
  - 是。

- 是否未写数据库：
  - 是。

- 验证命令和结果：
  - `rg -n "user_selected_date|_get_add_target_date|_on_add_clicked|selectedDate|InlineAddViewMonth|reset\(|db_manager\.add_schedule|calendar\.clicked|calendar\.activated|date_selected\.emit|_open_day_panel|MonthDayPanel|hover_preview|ActionContextMenu|contextMenu" src/ui/month_window.py`
    - 结果：
      - `_get_add_target_date()` 已新增
      - `_on_add_clicked(...)` 已改为使用 `target_date`
      - `InlineAddViewMonth.reset(target_date)` 仍走原有添加页 reset 入口
      - 未出现 `ActionContextMenu` / `contextMenu` 新链路
  - import 验证：
    - `MonthWindow / CalendarCellDelegate / InlineAddViewMonth / MonthDayHoverPreview / MonthDayPanel`：通过
  - offscreen 构造验证：
    - `MonthWindow()` 可构造
    - `has _get_add_target_date == True`
  - 无用户选中日期时默认逻辑验证：
    - `target == calendar.selectedDate()`：通过
  - 有用户选中日期时优先使用选中日期验证：
    - `target == user_selected_date`：通过
  - 添加页 reset 目标日期验证：
    - 先单击未来日期，再调用 `_on_add_clicked()`
    - `inline_add_view.selected_date == user_selected_date`
    - `open_day_panels` 数量不变
  - 过去日期不可添加验证：
    - 先单击过去日期，再调用 `_on_add_clicked()`
    - `inline_add_view.selected_date` 保持不变
    - `open_day_panels` 数量不变
  - M-2 / M-3 / M-4 静态回归：
    - `calendar.clicked` 仍连接 `_on_calendar_date_clicked`
    - `calendar.activated` 仍连接 `_on_calendar_date_activated`
    - `date_selected.emit(...)` 仍只在 activated 路径中
    - `_on_add_clicked(...)` 仍未接右键菜单或其他新链路
  - 语法检查：
    - 使用 `py_compile.compile(..., cfile=%TEMP%\\*.m5.pyc, doraise=True)` 编译：
      - `src/ui/month_window.py`
      - `main.py`
      - `src/ui/popups/month_day_hover_preview.py`
      - `src/ui/popups/month_day_panel.py`
    - 结果：通过

- diff 范围检查结果：
  - 禁止范围均无 diff：
    - `src/ui/main_window.py`
    - `src/ui/calendar_pop.py`
    - `src/ui/common/action_context_menu.py`
    - `src/ui/common`
    - `src/ui/popups/month_day_hover_preview.py`
    - `src/ui/popups/month_day_panel.py`
    - `src/ui/dashboard.py`
    - `src/ui/week_window.py`
    - `src/ui/todo.py`
    - `src/ui/todo_board.py`
    - `src/controllers`
    - `src/services`
    - `src/data`
    - `src/repositories`
    - `src/theme`
    - `src/utils/signals.py`
    - `src/utils/styles.py`
    - `assets`
    - `main.py`
    - `requirements.txt`
    - `schedule.db`
    - `manage_instruction/Final_Formulation.md`
    - `manage_instruction/Work_Formulation.md`
    - `manage_instruction/Work_Instruction.md`
    - `manage_instruction/Work_Snapshot.md`
    - `manage_instruction/History_Instruction.md`
    - `manage_instruction/History_Log.md`
    - `manage_instruction/ReconstructionDolder`
  - 允许范围：
    - `src/ui/month_window.py`
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`（开工前既有）

- 未完成事项：
  - 未接入月界面右键菜单，留待 `M-6`
  - 月界面功能补齐整体验收留待 `M-7`

- 风险或疑点：
  - 当前添加入口的“最终目标日期”已经优先使用 `user_selected_date`，但 `QCalendarWidget.selectedDate()` 仍会继续变化；如果后续产品要求彻底统一月界面内部所有日期来源，还需要在整体验收时复核其余路径，不在本轮扩大范围。
  - 当 `user_selected_date` 为过去日期时，单击仍会打开持久 panel，但添加入口会被阻止；这是当前按阶段要求保留的行为组合，不在本轮调整。

---

## 2026-06-02 M-0 复核锚点更新

- 任务目标：
  - M-0 执行完成后，更新 `Work_Task_Prompts.md`，避免继续显示“当前待执行提示词：M-0”导致重复执行。
- 实际修改文件：
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`
- 更新结果：
  - `Work_Task_Prompts.md` 已改为：`M-0` 已执行完成，等待复核。
  - 下一步候选标记为：`M-1：月格状态圆点与今天金色日期`。
- 验证：
  - 本次更新未修改 `src/`、`assets/`、`main.py`、`requirements.txt`、`schedule.db`。

---

## 2026-06-02 月界面功能补齐阶段规划写入

- 任务目标：
  - 将用户提出的月界面功能补齐构想整理为阶段规划和小工单边界。
  - 本轮只改管理文档，不改源码。
- 实际修改文件：
  - `manage_instruction/Work_Formulation.md`
  - `manage_instruction/Work_Instruction.md`
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`
- 写入内容：
  - 阶段名：`功能补充 - 月界面功能补齐`。
  - 明确下一步先做 `M-0` 只读审查，不直接修改 `month_window.py`。
  - 记录月格状态圆点规则：
    - 无日程不显示圆点。
    - 今天及未来只统计未完成日程，按最高紧急性显示红/黄/绿。
    - 过去日期有日程且全部完成为白点，有未完成为灰点，无日程不显示圆点。
  - 记录今天/选中态规则：
    - 今天只将日期数字改金色。
    - 整格高亮留给选中日期。
  - 记录交互规则：
    - 单击选中日期。
    - 双击跳转日界面并关闭所有月界面持久浮窗。
    - hover 显示只读预览，移走立即隐藏。
    - 单击显示月界面外侧持久浮窗，可多个并存。
  - 记录添加与右键菜单规则：
    - 添加按钮优先使用选中日期，过去日期不可添加。
    - 月界面右键菜单复用 `ActionContextMenu`，实装视图和添加，其余禁用。
    - 右键日期作为菜单上下文，建议不改变当前选中日期。
  - 记录 `M-0` 到 `M-7` 小工单路线。
- 特别补强的执行边界：
  - `M-0` 必须读取 `manage_instruction/ReconstructionDolder/Work_Formulation.md`、`History_Instruction.md`、`Workflow_Guide.md`，确认新增月界面功能不违背旧架构规划中的分层、公共组件、刷新协调和渐进式改造原则。
  - `M-0` 必须确认 `QCalendarWidget` / `QTableView` 鼠标位置到日期的映射方式。
  - `M-0` 必须确认 `QCalendarWidget.selectedDate()` 默认选中今天与后续“用户主动选中日期”状态如何区分，避免今天默认 selected 状态继续造成整格高亮。
  - `M-0` 必须确认 `priority`、完成状态、软删除/历史/todo/重复日程等字段语义。
  - `M-2` 允许最小修改 `MainWindow` 月界面信号连接。
  - 持久浮窗必须由 `MonthWindow` 管理生命周期，避免孤儿窗口。
  - `month` 当前项和周视图日期上下文如何处理，留给 `M-0` 结合现有路由确认。
- 验证：
  - 本轮未修改 `src/`、`assets/`、`main.py`、`requirements.txt`、`schedule.db`。
- 未完成事项：
  - 尚未生成 `M-0` 最终执行提示词。
  - 等待决策窗口复核本阶段规划。
- 风险或疑点：
  - 月界面当前基于 `QCalendarWidget` 原生表格与 delegate 绘制，后续日期映射和 hover/右键事件边界需要先读代码确认。

---

## 2026-06-02 M-0 最终提示词写入

- 任务目标：
  - 将决策窗口拟定并经主窗口修正的 `M-0（月界面现状审查与交互边界定位）` 提示词写入 `Work_Task_Prompts.md`。
- 实际修改文件：
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`
- 修正点：
  - 保留 M-0 只读审查边界，不允许修改源码、不写数据库。
  - 明确读取 `ReconstructionDolder` 旧规划，确认月界面功能补齐符合分层、公共组件、刷新协调和渐进式改造原则。
  - 明确审查 `QCalendarWidget.selectedDate()` 默认选中今天与“用户主动选中日期”的区分风险。
  - 明确当前已存在的月界面规划文档 diff 应作为开工前既有 diff 记录，避免执行窗口误判为 M-0 新增改动。
- 当前状态：
  - `M-0` 最终提示词已写入。
  - 等待执行窗口执行，完成后等待决策/顾问窗口复核。

---

## 2026-06-01 右键菜单子菜单与 hover 细节修正

- 任务目标：
  - 修正 `ActionContextMenu` 视图子菜单显示/隐藏、位置、宽度、图标颜色和选中背景覆盖范围。
- 实际修改：
  - `src/ui/common/action_context_menu.py`
    - 将菜单项改为 `QWidgetAction` 自绘行，扩大 hover 青色背景覆盖范围，使背景覆盖图标与文字整行。
    - 主菜单图标与视图子菜单图标统一通过 `load_colored_svg_pixmap(..., "#333333", ...)` 染色，避免白色图标融入浅色背景。
    - `视图` 项不再依赖 Qt 原生 `setMenu(...)` 子菜单延迟，改为 hover 时手动 `popup(...)`。
    - 视图子菜单显示位置改为主菜单右边界贴合子菜单左边界，减少原生子菜单重叠。
    - 视图子菜单固定宽度缩窄为 `150px`，主菜单固定宽度为 `160px`。
    - 鼠标离开主菜单/子菜单区域后通过零延迟检查关闭视图子菜单，避免原生子菜单长时间残留。
- 保持不变：
  - 未修改 Dashboard / WeekWindow 接入逻辑。
  - 未修改 `action_requested("add")` 与 `view_requested(day/week/month/todo)` 的信号语义。
  - 未启用换肤、排序、筛选、四象限。
  - 未修改数据库、服务层、控制层、assets。
- 验证：
  - `ActionContextMenu` import 通过。
  - offscreen 构造通过。
  - 信号回归通过：`add`、`day/week/month/todo` 仍按原语义发出，禁用项不触发动作。
  - `DashboardView` / `WeekWindow` import 回归通过。
  - `py_compile` 通过。
- 未完成事项：
  - 未做真实 GUI 截图自动验收；本轮需要用户本地目视确认菜单贴边、宽度和 hover 体验。
- 风险或疑点：
  - 子菜单显示改为手动 `popup(...)`，如果后续发现边缘屏幕位置溢出，需要另开小修正处理屏幕边界回退。

---

## 2026-06-01 右键菜单圆角样式微调

- 任务目标：
  - 将主界面和周界面共用的右键上下文菜单外观对齐到“更多”弹窗样式。
  - 仅调整菜单组件样式，不改变右键菜单功能、动作信号、接入位置和业务流程。
- 开工前状态：
  - 已存在归档管理文档 diff。
  - 本轮源码改动仅限 `src/ui/common/action_context_menu.py`。
- 实际修改：
  - `src/ui/common/action_context_menu.py`
    - 引入 `StyleManager.get_menu_style()`。
    - `ActionContextMenu` 主菜单复用“更多”弹窗同款 QMenu 样式。
    - `view_menu` 子菜单同步复用同款样式。
    - 为菜单设置 `WA_TranslucentBackground`、`Popup`、`FramelessWindowHint`、`NoDropShadowWindowHint`，对齐 `SharedMoreMenu` 的圆角显示方式。
- 保持不变：
  - 未修改 Dashboard / WeekWindow 的右键菜单接入逻辑。
  - 未修改 `action_requested` / `view_requested` 信号。
  - 未修改换肤、排序、筛选、四象限禁用策略。
  - 未修改数据库、服务层、控制层、QSS、assets。
- 验证：
  - `ActionContextMenu` import 通过。
  - offscreen 构造通过，主菜单和视图子菜单均可创建。
  - 信号回归通过：`add`、`day/week/month/todo` 行为保持一致，禁用项不触发新增动作。
  - `py_compile` 通过。
  - diff 范围符合预期：源码仅 `src/ui/common/action_context_menu.py` 有改动，另有归档管理文档既有 diff。
- 未完成事项：
  - 未做真实 GUI 截图验收；本轮为低风险样式对齐，运行期仍建议用户本地目视确认圆角效果。
- 风险或疑点：
  - Qt 原生菜单在不同 Windows 主题/合成器下对圆角和阴影的渲染可能略有差异，但样式来源已与“更多”弹窗统一。

---

## 2026-06-01 右键上下文菜单阶段归档

- 已归档到：
  - `History_Instruction.md`
  - `History_Log.md`
- 阶段结论：
  - `CM-0` 到 `CM-4` 已完成。
  - 右键上下文菜单阶段可归档。
  - 本阶段未实现换肤、排序、筛选、四象限。
  - 后续建议回到月界面功能补齐规划。

---

## 2026-06-02 M-0（月界面现状审查与交互边界定位）

- 本轮任务名称：
  - `M-0（月界面现状审查与交互边界定位）`
- 开工前 git 状态：
  - `## main...temp/main [ahead 51]`
  - `git diff --name-only` 无输出。
- 开工前既有 diff：
  - 无源码 diff。
  - 无月界面规划文档既有 diff；`Work_Formulation.md`、`Work_Instruction.md`、`Work_Task_Prompts.md` 当前内容已提交，不属于本轮新增改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`

- 读取的规划文件：
  - `manage_instruction/Work_Formulation.md`
  - `manage_instruction/Work_Instruction.md`
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/ReconstructionDolder/Work_Formulation.md`
  - `manage_instruction/ReconstructionDolder/History_Instruction.md`
  - `manage_instruction/ReconstructionDolder/Workflow_Guide.md`

- 读取的源码文件：
  - `src/ui/month_window.py`
  - `src/ui/main_window.py`
  - `src/ui/calendar_pop.py`
  - `src/ui/common/action_context_menu.py`
- 追加只读文件与原因：
  - `src/data/models.py`：确认 `Schedule` 字段语义。
  - `src/services/schedule_query_service.py`：确认 `item_type` 与日期过滤旧语义。
  - `src/repositories/schedule_repository.py`：确认 `get_all_schedules` / `get_schedules_for_date` 可用边界。
  - `src/ui/dashboard.py`：确认 `priority/status` 旧颜色与状态语义。

- 旧规划与当前阶段原则确认：
  - 月界面功能补齐符合旧规划中的兼容式渐进改造原则，不需要新建 controller/router 取代现有链路。
  - 新增纯 UI 浮窗/预览组件优先考虑 `src/ui/popups/`；仅当后续确认可跨页面复用时再放 `src/ui/common/`。
  - 现有 `MainController` / `ViewRouter` / `RefreshCoordinator` 不需要在 `M-0`~`M-2` 被扩展；月界面现有 `date_selected` / `view_selected` 信号链已足够支撑第一批改造。
  - 后续仍应遵守 `ActionContextMenu` 复用方向、`default.qss / skin preset` 路线和 `role/state/variant` 动态属性规范。

- 当前月界面点击跳转链路：
  - `MonthWindow.calendar.clicked.connect(self.date_selected.emit)`。
  - `MainWindow.__init__` 中 `self.month_window.date_selected.connect(self.jump_to_date_from_month)`。
  - `jump_to_date_from_month(qdate)` 仅转调 `jump_to_date(qdate)`。
  - `jump_to_date(qdate)` 调用 `on_calendar_date_picked(py_date)` 后执行 `switch_view("day")`。
  - 结论：当前是“单击日期即跳日视图”，不是“单击选中 / 双击跳转”。

- 当前月界面添加入口和日期来源：
  - `MonthWindow._on_add_clicked()` 直接读取 `self.calendar.selectedDate()`。
  - 过去日期限制也直接基于 `selectedDate()` 判断。
  - `InlineAddViewMonth.reset(target_date)` 保存该日期。
  - `InlineAddViewMonth._on_save()` 用 `selected_date.toPyDate()` 组装默认 `start_time`，并通过 `db_manager.add_schedule(...)` 写入。
  - 结论：当前月界面“添加”完全依赖 `QCalendarWidget.selectedDate()`，没有单独的“用户主动选中日期”状态。

- `QCalendarWidget.selectedDate()` 默认今天与用户主动选中日期的区分风险：
  - `MonthWindow` 初始化时未显式清空选择，也未维护 `user_selected_date`。
  - `QCalendarWidget.selectedDate()` 默认就是今天。
  - 当前 `_on_add_clicked()` 会把“默认今天”与“用户真的选了某天”混为一谈。
  - 用户只翻月不点击日期时，`selectedDate()` 仍可能停留在今天；这会让“添加”落到错误日期。
  - 结论：后续不能继续把 `selectedDate()` 当作唯一真实业务选中态，至少需要单独维护 `user_selected_date` 或等价状态。

- 当前绘制方式和月格日期映射可行性：
  - 月界面当前使用 `QCalendarWidget` + 内部 `QTableView` + `CalendarCellDelegate.paint(...)`。
  - `paint(...)` 只能拿到 `index.data()` 文本和 `row/column`，没有直接拿到完整 `QDate`。
  - 现有“是否本月”判断依赖启发式规则：
    - 前两行且数字大于 20 视为上月补位。
    - 后两行且数字小于 15 视为下月补位。
  - 该规则用于上色还勉强可用，但不适合作为 hover/右键/双击/圆点的数据源。
  - `MonthWindow` 已通过 `self.calendar.findChild(QTableView)` 拿到内部表格，说明后续可在该 `QTableView` 上接 `indexAt(...)`、`visualRect(...)`、mouse tracking、eventFilter。
  - 当前代码里尚未实现：
    - `indexAt(...)`
    - `visualRect(...)`
    - `mouseMoveEvent` 针对月格命中
    - `mouseDoubleClickEvent` 针对月格命中
    - `contextMenuEvent` 针对月格命中
  - 结论：鼠标到日期映射是可做的，但应基于 `QTableView` 显式计算 `cell -> QDate`；不能继续依赖 delegate 内的数字启发式。
  - 建议：后续维护 `visible_month/current_page` + `cell_date_map` 或实现独立 `_date_for_index(index)` 帮助方法。

- 上月/下月补位日期判断方式结论：
  - 当前月界面没有正式的补位日期映射函数。
  - 仅有 `CalendarCellDelegate.paint(...)` 中的行号 + 数字阈值启发式判断。
  - `MonthWindow.current_date` 在翻页后会被 `_on_calendar_page_changed(year, month)` 修正为该月 1 号，可作为“当前可见页月份”基础状态。
  - 建议后续按“当前页年/月 + 首日 weekday + 42 格偏移”精确计算格子日期，替代阈值启发式。

- 日程圆点所需字段语义审查结论：
  - `Schedule.priority` 语义已在现有 UI 中固定：
    - `0` = 低 = 绿色
    - `1` = 中 = 黄色
    - `2` = 高 = 红色
  - `Schedule.status` 语义按现有 UI/服务判断：
    - `0` = 活动/未完成
    - `1` = 已完成
    - `2` = 删除/历史，不应进入正常展示
  - `Schedule.item_type`：
    - `"schedule"` = 日程
    - `"todo"` = 待办
  - 重复日程实例：
    - 已按独立记录存在，`group_id` 只表达循环组归属，不影响“月格按日期聚合”。
  - 日期来源旧语义：
    - `calendar_pop.py` 当前按 `start_time.date()` 优先，缺失时回退 `end_time.date()`。
    - 该规则与月界面现状最接近，短期可沿用为月格圆点日期来源。
  - 整月数据可行性：
    - 当前可直接用 `db_manager.get_all_schedules()` 拉全量，再在月界面本地聚合 `date -> schedules`。
    - `get_schedules_for_date()` 只适合单日过滤，不适合整月 42 格反复调用。
  - 过滤建议：
    - 排除 `status == 2`。
    - 排除 `item_type == "todo"`。
    - 保留重复实例的独立记录。
    - 圆点日期来源短期按 `start_time` 优先、`end_time` 兜底，与 `calendar_pop.py` 对齐。
  - `calendar_pop.py` 参考价值：
    - 有现成 `HighlightCalendarWidget.paintCell(...)` 与整日聚合逻辑。
    - 但颜色规则目前是 `white/grey/cyan`，不符合月界面新规划。
    - 适合作为“按 `QDate` 精确绘制圆点”的参考，不适合直接复用 UI 规则。

- hover 只读预览组件建议：
  - 不建议先塞进 `month_window.py` 临时类。
  - 更适合单独放到 `src/ui/popups/`，例如月界面专用只读预览弹窗。
  - 原因：
    - 明确是弹出层语义，不是共享基础控件。
    - 需要脱离月历本体处理显示/隐藏和定位。
    - 未来若要复用，再上提到 `common` 更安全。
  - 风险等级：中高。核心风险不在 UI 壳，而在 hover 命中、跨格移动和生命周期去抖。

- 持久浮窗组件建议和生命周期管理建议：
  - 持久浮窗壳应优先放 `src/ui/popups/`，不要先写在 `month_window.py` 内部。
  - 应使用独立顶层窗口或至少独立 popup/tool 窗口，避免被 `MonthWindow` 裁剪。
  - `MonthWindow` 需要维护 `open_day_panels` 或等价列表。
  - 统一关闭入口建议：
    - `MonthWindow.closeEvent(...)`
    - `MonthWindow.hideEvent(...)`
    - 双击跳日视图前的统一清理方法
  - 多个持久浮窗并存建议：
    - 以点击日期格的全局位置为锚点做级联偏移，避免完全重叠。
  - 风险等级：高。原因是多窗口生命周期与位置管理，而不是 UI 绘制本身。

- 月界面右键菜单接入建议：
  - `ActionContextMenu` 已具备所需 action/view 出口，`M-6` 优先复用，不建议先改组件。
  - 月界面当前没有右键链路，也没有右键日期上下文状态。
  - 右键日期应通过 `QTableView.indexAt(...)` 命中后单独存为临时上下文，例如 `context_menu_date`。
  - 右键建议不改变当前选中日期；这在现有架构中可实现，因为右键菜单和单击选中还未耦合。
  - `添加` 动作应使用右键日期，不应读取 `calendar.selectedDate()`。
  - 过去日期添加禁用建议在弹菜单前设置 `menu.actions_by_id["add"].setEnabled(False)`，不建议改菜单组件的默认策略。
  - `month` 当前项：
    - 现有 `MonthWindow._on_view_selected("month")` 已是 no-op。
    - 短期可保持可点但无动作，或在接入时禁用；优先保持组件不变、在月界面集成层处理。
  - 周视图日期上下文限制：
    - 当前 `switch_view("week")` / `view_selected.emit("week")` 不支持携带目标日期。
    - 因此从月界面右键直接“带日期跳周视图”目前没有现成路由，应在 `M-6` 明确记录为限制，不强行实现。

- 当前月界面缺失链路汇总：
  - 无 hover 事件链路。
  - 无双击日期格链路。
  - 无右键菜单链路。
  - 无“用户主动选中日期”独立状态。
  - 无整月 `date -> schedules` 缓存。
  - 无持久浮窗列表和关闭策略。

- M-1 建议：
  - 建议修改文件：
    - `src/ui/month_window.py`
  - 风险等级：
    - 中
  - 验收重点：
    - 只补今天金色数字与日程圆点，不改变单击跳转。
    - 优先用精确日期映射或子类化 `QCalendarWidget.paintCell(...)`，不要继续扩大 delegate 数字阈值逻辑。
    - 圆点过滤规则必须排除 `status == 2`、`item_type == "todo"`。
    - `schedule.db` 无 diff。

- M-2 建议：
  - 建议修改文件：
    - `src/ui/month_window.py`
    - `src/ui/main_window.py`
  - 风险等级：
    - 中高
  - 验收重点：
    - 单击只选中，不再跳日视图。
    - 双击才发出跳转链路。
    - 现有 `MainWindow.jump_to_date_from_month` 复用不变，只调整月界面发射时机。
    - 为月格引入精确双击命中，不破坏视图切换和挂起链路。

- M-3 建议：
  - 建议修改文件：
    - `src/ui/month_window.py`
    - `src/ui/popups/` 下新增月界面 hover 预览组件文件
  - 风险等级：
    - 中高
  - 验收重点：
    - hover 预览只读，移出立即隐藏。
    - 不影响单击选中、双击跳转、未来右键命中。
    - 需要 `QTableView` mouse tracking + 日期命中，不得靠 `selectedDate()` 推断。

- M-4 建议：
  - 建议修改文件：
    - `src/ui/month_window.py`
    - `src/ui/popups/` 下新增持久浮窗壳组件文件
  - 风险等级：
    - 高
  - 验收重点：
    - 独立顶层浮窗不被裁剪。
    - `MonthWindow` 正确维护 `open_day_panels`。
    - close/hide/双击跳日视图时统一清理全部持久浮窗。
    - 多浮窗并存不完全重叠。

- M-5 建议：
  - 建议修改文件：
    - `src/ui/month_window.py`
  - 风险等级：
    - 中
  - 验收重点：
    - 添加优先使用用户主动选中日期。
    - 无主动选中时再决定是否回退旧逻辑。
    - 过去日期禁止添加保持。
    - 不改 `InlineAddViewMonth` 写库语义，只改日期来源。

- M-6 建议：
  - 建议修改文件：
    - `src/ui/month_window.py`
    - 如必须桥接到日视图日期跳转，再最小修改 `src/ui/main_window.py`
  - 风险等级：
    - 中高
  - 验收重点：
    - 复用 `ActionContextMenu`，不新增菜单组件。
    - 右键日期上下文与当前选中日期解耦。
    - `add` 只用右键日期，过去日期禁用。
    - `day/month/todo` 视图动作复用旧入口。
    - `week` 日期上下文当前不支持时，要明确保持限制，不做伪实现。

- M-7 整体验收重点：
  - 圆点颜色与过滤规则正确。
  - 今天金色数字与选中整格高亮分离。
  - 单击/双击/hover/右键互不冲突。
  - 持久浮窗生命周期正确。
  - 添加日期来源正确且过去日期禁用。
  - `schedule.db` 无 tracked diff。
  - `main.py`、数据层、服务层、控制层无非必要 diff。

- 对现有规划的调整建议：
  - `M-1` 不建议继续沿用现有 `CalendarCellDelegate.paint(...)` 的数字启发式扩展圆点逻辑，建议改为“精确日期可得”的绘制路径。
  - `M-6` 需要在提示词中明确：周视图跳转暂不携带日期上下文，除非另开小工单先补路由能力。

- 静态搜索命令与关键结果：
  - 全局月界面搜索已执行，确认 `MonthWindow.date_selected` 当前直接由 `calendar.clicked` 发出。
  - `jump_to_date_from_month` 只做 `jump_to_date` 代理。
  - `MonthWindow` 中不存在 `mouseDoubleClickEvent`、`contextMenuEvent`、`indexAt(...)`、`visualRect(...)` 的月格链路。
  - `calendar_pop.py` 已有 `paintCell(...)` 与整日聚合逻辑，可参考但不宜直接复用规则。

- diff 范围检查结果：
  - `git diff --name-only -- src`：无输出。
  - `git diff --name-only -- assets`：无输出。
  - `git diff --name-only -- main.py`：无输出。
  - `git diff --name-only -- requirements.txt`：无输出。
  - `git diff --name-only -- schedule.db`：无输出。
  - `git diff --name-only -- manage_instruction/Work_Formulation.md`：无输出。
  - `git diff --name-only -- manage_instruction/Work_Instruction.md`：无输出。
  - `git diff --name-only -- manage_instruction/Work_Snapshot.md`：无输出。
  - `git diff --name-only -- manage_instruction/History_Instruction.md`：无输出。
  - `git diff --name-only -- manage_instruction/History_Log.md`：无输出。
  - `git diff --name-only -- manage_instruction/ReconstructionDolder`：无输出。
  - 本轮结束后应仅新增 `manage_instruction/Work_Log.md` diff。

- 未完成事项：
  - 等待决策/顾问窗口基于本轮结论下发 `M-1` 最终执行提示词。

- 风险或疑点：
  - 现有 `MonthWindow` 把视觉绘制、添加入口、天气 tooltip、toast、视图切换都放在单文件内，后续 `M-2`~`M-6` 若不控制范围，容易顺手把多条链路混在一轮里。
  - `QCalendarWidget` 内部模型结构依赖 Qt 实现细节，后续日期命中建议尽量基于“当前页年月 + 表格 index”自算，不要过度依赖 `index.data()` 文本规则。

---

## 2026-06-02 M-1（月格状态圆点与今天金色日期）

- 本轮任务名称：
  - `M-1（月格状态圆点与今天金色日期）`
- 开工前 git 状态：
  - `## main...temp/main [ahead 52]`
  - `git diff --name-only`：
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`
    - `src/ui/month_window.py`
- 开工前既有 diff：
  - `manage_instruction/Work_Log.md`：来自 `M-0` 日志记录。
  - `manage_instruction/Work_Task_Prompts.md`：开工前既有管理文档 diff，本轮未修改。
  - `src/ui/month_window.py`：本轮新增源码改动目标文件。
- 实际修改文件：
  - `src/ui/month_window.py`
  - `manage_instruction/Work_Log.md`

- 月格圆点实现位置：
  - `src/ui/month_window.py`
  - `CalendarCellDelegate.paint(...)`：负责在格子右下角绘制圆点。
  - `MonthWindow._build_schedule_marker_cache()`：负责构建 `date -> QColor` 缓存。
  - `MonthWindow._refresh_schedule_marker_cache()`：负责把当前页年月、今天日期和 marker 缓存同步给 delegate，并触发 `calendar.updateCells()`。

- 月格圆点数据来源：
  - 只读使用 `db_manager.get_all_schedules()`。
  - 在月界面本地做聚合，不对 42 个格子重复调用 `get_schedules_for_date(...)`。

- 圆点过滤规则：
  - 已排除 `status == 2`。
  - 已排除 `item_type == "todo"`。
  - 日期来源为 `start_time.date()` 优先、`end_time.date()` 兜底。
  - 重复日程实例按独立记录参与统计，不按 `group_id` 合并。

- 未来/今天未完成日程红黄绿规则实现说明：
  - 今天及未来仅统计未完成记录。
  - `priority == 2` -> 红色 `#FF4D4F`
  - `priority == 1` -> 黄色 `#FAAD14`
  - `priority == 0` -> 绿色 `#52C41A`
  - 若当天没有未完成日程，则不显示圆点。

- 过去日期白/灰规则实现说明：
  - 过去日期只要有日程：
    - 全部完成 -> 白色 `#FFFFFF`
    - 存在未完成 -> 灰色 `#999999`
  - 无日程则不显示圆点。

- 今天日期数字金色实现说明：
  - 在 `CalendarCellDelegate.paint(...)` 中先精确计算当前格子的 `QDate`。
  - 若格子日期等于 `QDate.currentDate()`，数字直接使用金色 `#FFD700` 绘制。
  - 本月/非本月/周末判断不再依赖旧的数字阈值上色分支覆盖今天颜色。

- 如何处理 `selectedDate()` 默认今天导致整格高亮的风险：
  - 本轮未引入 `user_selected_date`，也未改 `selectedDate()` 业务语义。
  - 仅在绘制层规避：若当前格子是“今天”，即使命中 Qt 的 `State_Selected`，也不再绘制整格选中遮罩。
  - 已知限制：
    - 用户主动单击今天时，本轮仍不会显示整格高亮。
    - 该限制已按提示词要求留给 `M-2` 的交互重构处理。

- 精确日期映射实现说明：
  - 本轮没有继续扩张旧的“数字 + 行号阈值”启发式作为业务日期来源。
  - `CalendarCellDelegate` 新增：
    - `set_calendar_state(...)`
    - `_date_for_index(index)`
  - 计算方式基于：
    - 当前可见页年月
    - `QCalendarWidget.firstDayOfWeek()`
    - `row/column -> day offset`
  - 该映射只服务于本轮绘制，不接 hover/右键/双击交互。

- 刷新时机：
  - `MonthWindow.__init__` 完成 UI 后首次建立 marker 缓存。
  - `_on_calendar_page_changed(...)` 翻月后重建 marker 缓存。
  - `_on_schedule_saved()` 保存成功后重建 marker 缓存。

- 是否保持单击跳日视图链路不变：
  - 是。
  - `calendar.clicked.connect(self.date_selected.emit)` 仍存在。
  - `MainWindow.jump_to_date_from_month(...)` 未修改。

- 是否保持添加按钮日期来源不变：
  - 是。
  - `_on_add_clicked(...)` 仍直接使用 `calendar.selectedDate()`。
  - `InlineAddViewMonth` 写入逻辑未改。

- 是否未新增双击/hover/右键/持久浮窗逻辑：
  - 是。
  - 静态搜索未新增：
    - `mouseDoubleClickEvent`
    - `contextMenuEvent`
    - `ActionContextMenu`
    - `customContextMenuRequested`
    - `setContextMenuPolicy`
    - `open_day_panels`
    - `user_selected_date`
    - `setSelectedDate`
    - `clearSelection`
  - `hover` 命中仅来自既有按钮 stylesheet 文本，不是新增 hover 预览逻辑。

- 验证命令和结果：
  - `from src.ui.month_window import MonthWindow, CalendarCellDelegate, InlineAddViewMonth`
    - 通过。
  - offscreen 构造：
    - `MonthWindow()` 可构造。
    - 输出选中日期：`2026-06-02`。
  - 只读数据路径：
    - `db_manager.get_all_schedules()` 可调用。
    - 输出 `schedules 78`
    - `priority/status/item_type` 字段抽样检查通过。
  - 行为链路静态检查：
    - `calendar.clicked.connect(self.date_selected.emit)` 仍存在。
    - `_on_add_clicked(...)` 仍存在并使用 `selectedDate()`。
    - `view_selected` 链路未变。

- 语法检查：
  - 按提示词原命令执行：
    - `python -m py_compile src/ui/month_window.py main.py`
  - 结果：
    - 失败，原因不是语法错误，而是写入 `src/ui/__pycache__/month_window...pyc` 时遇到 `[WinError 5] 拒绝访问`。
  - 等价兜底验证：
    - 使用 `py_compile.compile(..., cfile=%TEMP%\\*.pyc, doraise=True)` 编译 `src/ui/month_window.py` 与 `main.py`。
    - 结果：通过，说明语法层面无错误。

- diff 范围检查结果：
  - 禁止范围均无 diff：
    - `src/ui/main_window.py`
    - `src/ui/calendar_pop.py`
    - `src/ui/common/action_context_menu.py`
    - `src/ui/popups`
    - `src/ui/common`
    - `src/controllers`
    - `src/services`
    - `src/data`
    - `src/repositories`
    - `src/theme`
    - `src/utils/signals.py`
    - `src/utils/styles.py`
    - `assets`
    - `main.py`
    - `requirements.txt`
    - `schedule.db`
    - `manage_instruction/Work_Formulation.md`
    - `manage_instruction/Work_Instruction.md`
    - `manage_instruction/Work_Snapshot.md`
    - `manage_instruction/History_Instruction.md`
    - `manage_instruction/History_Log.md`
    - `manage_instruction/ReconstructionDolder`
  - 允许范围：
    - `git diff --name-only -- src/ui/month_window.py`：有 diff。
    - `git diff --name-only`：
      - `manage_instruction/Work_Log.md`
      - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
      - `src/ui/month_window.py`

- 未完成事项：
  - 尚未做 `M-2` 的单击/双击语义拆分。
  - 尚未处理“用户主动单击今天仍不高亮”的限制。
  - 尚未接入 hover 预览、持久浮窗、右键菜单。

- 风险或疑点：
  - 本轮圆点绘制使用了精确的 `index -> QDate` 计算，但仍依赖 `QCalendarWidget` 内部 `QTableView` 的标准 7 列网格结构；后续如果 Qt 内部视图布局差异化，需要重新验证。
  - 今天默认选中整格高亮已在绘制层压掉，但没有区分“默认今天”和“用户主动点了今天”；该行为差异已按计划留给 `M-2` 处理，不在本轮扩大范围。

- 复核后最小补修：
  - 触发原因：
    - 顾问复核指出 `_date_for_index()` 中对 `firstDayOfWeek()` 做 `int(...)` 转换会在 PyQt6 下抛 `TypeError`。
    - 顾问复核同时指出日期映射未正确处理模型第 0 行表头，以及月历固定 6 周日期行带来的首个可见日期偏移。
  - 实际补修：
    - 将 `firstDayOfWeek()` 转换改为 `.value`，避免 `DayOfWeek` 枚举直接 `int(...)`。
    - `index.row() == 0` 时直接返回无效 `QDate()`，使表头不参与日期映射和圆点绘制。
    - 将首个可见日期改为：
      - 先按当前页年月计算 `first_of_month`。
      - 按 `firstDayOfWeek().value` 计算相对偏移。
      - 当偏移为 `0` 时额外回退 7 天，以对齐 `QCalendarWidget` 当前内部固定 6 周日期行布局。
      - 再用 `(row - 1) * 7 + column` 推导真实日期。
    - `cell_date` 无效时不再调用 `toPyDate()`。
  - 复验结果：
    - `MonthWindow / CalendarCellDelegate / InlineAddViewMonth` import：通过。
    - 日期映射验证：通过。
      - `row 0 / col 0` -> 无效日期（表头跳过）
      - `row 1 / col 0` -> `2026-05-25`
      - `row 2 / col 0` -> `2026-06-01`
    - `w.calendar.grab()` 绘制触发验证：通过。
      - 输出：`grab ok True 540 436`
    - 说明：
      - `w.show()` 在 offscreen 下仍会导致进程异常退出，但不属于本轮圆点逻辑问题。
      - 顾问要求的“实际绘制触发验证”已通过 `w.calendar.grab()` 完成。

## 2026-06-02 M-1 最终提示词写入

- 任务：审核并写入 `M-1（月格状态圆点与今天金色日期）` 最终执行提示词。
- 实际修改文件：
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`
- 审核结论：
  - 决策窗口给出的 M-1 方向可用，但需要收紧边界。
  - 已补充：本轮只做视觉状态，不改单击、双击、hover、右键、添加和跳转行为。
  - 已补充：`QCalendarWidget.selectedDate()` 默认今天的风险只允许在绘制层处理，不允许本轮引入 `user_selected_date`、清空选择或改变添加日期来源。
  - 已补充：月格圆点应使用精确日期映射或可见年月 + row/column 计算，不能继续扩大旧的数字阈值启发式作为业务日期来源。
  - 已补充：本轮只允许只读调用 `db_manager.get_all_schedules()`，不得写数据库，不得改数据层、服务层、Repository 或 `calendar_pop.py`。
  - 已补充：如外部刷新不能即时反映到月格圆点，本轮只记录风险，不接入 `RefreshCoordinator` 或新增 signal。
- 下一步：
  - 执行窗口可按 `Work_Task_Prompts.md` 中最终 M-1 提示词执行。

## 2026-06-02 月格圆点位置微调

- 任务：
  - 将月界面日程状态圆点从日期格右下角改为日期数字下方居中，随后按视觉复核反馈改为日期格左上角。
- 修改原因：
  - 右下角位置视觉上和日期数字关联较弱；日期数字下方居中试调后仍显得拥挤，因此改为左上角作为状态标记。
- 实际修改文件：
  - `src/ui/month_window.py`
  - `manage_instruction/Work_Log.md`
- 修改内容：
  - 仅调整 `CalendarCellDelegate.paint(...)` 中圆点绘制坐标。
  - 当前坐标策略：`inner_rect.left() + 6` / `inner_rect.top() + 6`。
  - 圆点颜色规则、数据来源、日期映射、点击/添加/跳转行为均未修改。
- 验证要求：
  - 复跑 `MonthWindow` import。
  - 复跑 offscreen `calendar.grab()` 绘制触发。
  - 确认禁止范围无 diff。

## 2026-06-03 月格状态标记改为边框染色

- 任务：
  - 取消月格状态圆点试调，先尝试给有日程状态的日期格边框染色；随后按视觉反馈取消边框染色，改为使用 label 染色图标。
- 修改原因：
  - 圆点无论放右下角、日期下方还是左上角，视觉上都显得突兀；边框染色更像日期格自身状态，不额外占用格内信息空间。
- 实际修改文件：
  - `src/ui/month_window.py`
  - `manage_instruction/Work_Log.md`
- 修改内容：
  - `CalendarCellDelegate.paint(...)` 中不再绘制状态圆点。
  - 边框恢复为原白色细边框，不再用状态色染边框。
  - 当前方案：对有 marker 的日期格，在左上角绘制三角形 label 标记。
  - 三角形 label 按 marker 颜色染色：高/中/低/过去完成/过去未完成仍沿用原颜色规则。
  - 新增 delegate 内部 icon 缓存，避免每格重复渲染同色 SVG。
  - 按视觉反馈将 label 图标上移到接近日期格上边框的位置；最终坐标贴到 `inner_rect.top()`，不额外保留 1px 间隙。
  - 按视觉反馈从 `Label.svg` 切换为 `Label_fill.svg` 试看填充版效果。
  - 随后替换 `Label.svg` 为左上角三角形标签图标，并将绘制位置改为日期格左上角，紧贴 `inner_rect.left()` / `inner_rect.top()`。
  - 针对小尺寸 SVG 斜边锯齿问题，改为直接用 `QPainterPath` 绘制三角形 label，避免 SVG 缩放导致的斜边像素抖动。
  - 按新视觉构想取消左上角 label 标记，改为在有 marker 的日期格内部绘制一个居中的小型空心方框。
  - 小方框只使用状态色细边框，`QPen.setWidth(0)` 保持尽可能细的 cosmetic pen，不填充背景。
  - 绘制顺序调整为先画状态小方框、再绘制日期数字，避免状态框压住日期文字。
  - 按视觉反馈将状态小方框从 `42x28` 放大到 `56x34`，仅调整尺寸，不改变颜色规则和刷新逻辑。
  - 按视觉反馈取消固定宽高，改为从日期格内矩形四边等距内缩 `14px` 绘制状态框，使状态框到原日期格边框的上下左右距离一致。
  - 最终按视觉决策取消状态小方框，改回左上角三角形 label 方案。
  - 三角形 label 内新增白色数字，显示该日期有效日程总数；数量超过 9 时显示 `9+`。
  - 按视觉反馈将三角形 label 从 `26px` 缩小到 `22px`，数量字体从 `7pt` 缩小到 `6pt`。
  - 新增 `schedule_marker_count_cache` / `marker_count_cache`，仅用于绘制数量角标，不改变 marker 颜色规则、数据写入或刷新链路。
  - 新增 `MonthWindow.showEvent(...)`，每次月界面显示时调用 `_refresh_schedule_marker_cache()`。
  - marker 颜色规则、数据来源、日期映射、点击/添加/跳转行为均未修改。
- 问题定位：
  - 数据库中 `2026-06-18` 两条 schedule 记录均为 `priority == 2`，当前 marker 缓存计算结果为红色 `#ff4d4f`。
  - 界面仍显示旧颜色的原因是月界面缓存未在日界面/详情弹窗编辑后刷新。
- 验证要求：
  - 复跑 `MonthWindow` import。
  - 复跑 offscreen `calendar.grab()` 绘制触发。
  - 复跑临时 `py_compile`。
  - 确认禁止范围无 diff。

## 2026-06-03 M-2 最终提示词写入

- 任务：
  - 审核并写入 `M-2（月格单击选中与双击跳日视图）` 最终执行提示词。
- 实际修改文件：
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`
- 审核修正：
  - 将原提示词中“M-1 圆点”表述修正为当前真实实现的“三角数量角标”。
  - 明确单击只更新 `user_selected_date`，不得 emit 跳转信号。
  - 明确选中高亮必须基于用户主动选中状态，不能直接依赖 `QCalendarWidget.selectedDate()` 默认今天。
  - 明确优先使用 `QCalendarWidget.activated(QDate)` 作为双击/激活入口。
  - 明确优先保留 `MonthWindow.date_selected` 作为双击跳转信号，复用 `MainWindow.jump_to_date_from_month(...)` 既有连接，优先不修改 `main_window.py`。
  - 明确预留 `close_day_panels()` / `open_day_panels` 仅作为 M-4 生命周期接口，不实现持久浮窗。
  - 明确本轮不得重写 `_on_add_clicked(...)` 为使用 `user_selected_date`，添加日期来源联动仍留到 M-5。
- 下一步：
  - 执行窗口可按 `Work_Task_Prompts.md` 中最终 M-2 提示词执行。

## 2026-06-03 M-2（月格单击选中与双击跳日视图）

- 本轮任务名称：
  - `M-2（月格单击选中与双击跳日视图）`

- 开工前 git 状态：
  - `## main...temp/main [ahead 54]`

- 开工前既有 diff：
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`

- 实际修改文件：
  - `src/ui/month_window.py`
  - `manage_instruction/Work_Log.md`

- 用户主动选中日期状态的实现方式：
  - 在 `MonthWindow` 上新增 `self.user_selected_date = None`。
  - 在 `CalendarCellDelegate` 上新增 `user_selected_date` 状态，并通过 `set_calendar_state(...)` 传入。
  - 整格高亮不再直接依赖 Qt 原生 `State_Selected`，改为仅在 `cell_date == user_selected_date` 时绘制。

- 单击日期如何只更新选中态、不跳日视图：
  - 将 `self.calendar.clicked.connect(self.date_selected.emit)` 改为：
    - `self.calendar.clicked.connect(self._on_calendar_date_clicked)`
  - `_on_calendar_date_clicked(qdate)` 只做两件事：
    - 更新 `self.user_selected_date = qdate`
    - 调用 `_refresh_schedule_marker_cache()` 刷新月格视觉
  - 单击路径不再 emit `date_selected`，不再触发 `MainWindow.jump_to_date_from_month(...)`。

- 双击日期如何跳转日视图：
  - 新增：`self.calendar.activated.connect(self._on_calendar_date_activated)`。
  - `_on_calendar_date_activated(qdate)` 顺序为：
    - 先复用 `_on_calendar_date_clicked(qdate)` 同步用户选中态
    - 再调用 `close_day_panels()`
    - 最后 `self.date_selected.emit(qdate)`
  - `MainWindow` 继续复用现有连接：
    - `self.month_window.date_selected.connect(self.jump_to_date_from_month)`
  - 本轮未修改 `src/ui/main_window.py`。

- 双击跳转前是否调用 `close_day_panels()` 或等价安全接口：
  - 是。
  - 新增 `MonthWindow.close_day_panels()`，当前为安全空壳 + 生命周期清理接口。

- 是否预留 `open_day_panels` 或等价生命周期状态：
  - 是。
  - 新增 `self.open_day_panels = []`。
  - `close_day_panels()` 会遍历其中对象，若存在 `close()` 方法则调用，然后清空列表。
  - 当前未实现真实持久浮窗，仅为后续 `M-4` 预留。

- 是否保持 M-1 三角数量角标颜色/数量逻辑不变：
  - 是。
  - 未修改 marker 颜色规则。
  - 未修改 marker 数量统计。
  - 未修改 marker 显示条件。

- 是否保持今天金色日期逻辑不变：
  - 是。
  - 今天仍通过日期数字金色显示。
  - 变化仅在于“今天整格高亮”现在由 `user_selected_date` 决定，而不再受默认 selected today 影响。

- 是否保持添加按钮日期来源不变：
  - 是。
  - `_on_add_clicked(...)` 仍使用 `self.calendar.selectedDate()`。
  - 未改 `InlineAddViewMonth`。
  - 未改 `db_manager.add_schedule(...)` 调用。

- 是否未实现 hover 预览：
  - 是。

- 是否未实现持久浮窗：
  - 是。

- 是否未接右键菜单：
  - 是。

- 验证命令和结果：
  - `rg -n "user_selected_date|selected_date|date_selected|date_double_clicked|activated|mouseDoubleClickEvent|clicked|calendar\.clicked|jump_to_date_from_month|close_day_panels|open_day_panels|_on_add_clicked|InlineAddViewMonth|marker|schedule_marker|marker_count" src/ui/month_window.py src/ui/main_window.py`
    - 结果：
      - `calendar.clicked` 已改为连接 `_on_calendar_date_clicked`
      - `calendar.activated` 已连接 `_on_calendar_date_activated`
      - `date_selected.emit(...)` 只出现在激活跳转路径
      - `jump_to_date_from_month(...)` 仅保留在 `MainWindow` 既有连接处
  - `from src.ui.month_window import MonthWindow, CalendarCellDelegate, InlineAddViewMonth; from src.ui.main_window import MainWindow`
    - 结果：通过。
  - offscreen 构造验证：
    - `MonthWindow()` 可构造。
    - `has close_day_panels == True`
    - `has calendar == True`
    - `user_selected_date is None`
  - 单击行为验证：
    - 直接调用 `_on_calendar_date_clicked(QDate(2026, 6, 15))`
    - 结果：
      - `user_selected_date == 2026-06-15`
      - `date_selected` 未触发
  - 激活/双击路径验证：
    - 在 `open_day_panels` 放入带 `close()` 的 dummy 对象后调用 `_on_calendar_date_activated(QDate(2026, 6, 16))`
    - 结果：
      - `user_selected_date == 2026-06-16`
      - dummy `closed == True`
      - `open_day_panels == []`
      - `date_selected` 收到 `2026-06-16`
  - 添加逻辑静态验证：
    - `_on_add_clicked(...)` 仍使用 `selectedDate()`
    - `InlineAddViewMonth` 和 `db_manager.add_schedule(...)` 未变
  - 语法检查：
    - 使用 `py_compile.compile(..., cfile=%TEMP%\\*.m2.pyc, doraise=True)` 编译：
      - `src/ui/month_window.py`
      - `src/ui/main_window.py`
      - `main.py`
    - 结果：通过。

- diff 范围检查结果：
  - 禁止范围均无 diff：
    - `src/ui/calendar_pop.py`
    - `src/ui/common/action_context_menu.py`
    - `src/ui/popups`
    - `src/ui/common`
    - `src/ui/dashboard.py`
    - `src/ui/week_window.py`
    - `src/ui/todo.py`
    - `src/ui/todo_board.py`
    - `src/controllers`
    - `src/services`
    - `src/data`
    - `src/repositories`
    - `src/theme`
    - `src/utils/signals.py`
    - `src/utils/styles.py`
    - `assets`
    - `main.py`
    - `requirements.txt`
    - `schedule.db`
    - `manage_instruction/Work_Formulation.md`
    - `manage_instruction/Work_Instruction.md`
    - `manage_instruction/Work_Snapshot.md`
    - `manage_instruction/History_Instruction.md`
    - `manage_instruction/History_Log.md`
    - `manage_instruction/ReconstructionDolder`
  - 允许范围：
    - `git diff --name-only -- src/ui/month_window.py`：有 diff
    - `git diff --name-only -- src/ui/main_window.py`：无 diff
    - `git diff --name-only`：
      - `manage_instruction/Work_Log.md`
      - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
      - `src/ui/month_window.py`

- 未完成事项：
  - 未实现 hover 只读预览，留待 `M-3`。
  - 未实现月界面持久浮窗壳，留待 `M-4`。
  - 未实现添加按钮优先使用用户选中日期，留待 `M-5`。
  - 未接入月界面右键菜单，留待 `M-6`。

- 风险或疑点：
  - 本轮选中高亮完全基于 `user_selected_date`，而添加入口仍基于 `QCalendarWidget.selectedDate()`；两者在用户单击日期时通常同步，但产品语义尚未统一，已按要求留到 `M-5` 处理。
  - `QCalendarWidget.activated(QDate)` 在当前实现中承担“双击/激活跳转”职责；如果后续要严格区分鼠标双击与键盘激活，需要在后续工单单独细化，不在本轮扩大范围。

## 2026-06-03 M-3 最终提示词写入

- 任务：
  - 审核并写入 `M-3（月格 hover 只读预览弹窗）` 最终执行提示词。
- 实际修改文件：
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`
- 审核修正：
  - 明确 hover 事件应优先安装在 `QTableView.viewport()`，避免扩大到整个 `MonthWindow`。
  - 明确使用 `indexAt(event.pos())` + 现有精确日期映射，不能用 `calendar.selectedDate()` 推断 hover 日期。
  - 明确表头行、无效 index、无效 `QDate`、移出 viewport 时必须立即隐藏预览。
  - 明确 hover 路径不得改变 `user_selected_date`、不得 emit `date_selected`、不得调用 `close_day_panels()`。
  - 明确预览组件只接收日期和日程列表数据，不依赖 `db_manager`、Repository、Service、MainWindow 或 MonthWindow 具体实例。
  - 明确可以新增 `date -> schedules` 只读缓存，但不得改变 M-1 marker 颜色/数量计算。
  - 明确翻月、刷新 marker 缓存或窗口隐藏时应隐藏 hover 预览，避免旧日期浮窗残留。
- 下一步：
  - 执行窗口可按 `Work_Task_Prompts.md` 中最终 M-3 提示词执行。

## 2026-06-03 M-3（月格 hover 只读预览弹窗）

- 本轮任务名称：
  - `M-3（月格 hover 只读预览弹窗）`

- 开工前 git 状态：
  - `## main...temp/main [ahead 55]`

- 开工前既有 diff：
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`

- 实际修改文件：
  - `src/ui/month_window.py`
  - `src/ui/popups/month_day_hover_preview.py`
  - `manage_instruction/Work_Log.md`

- hover 预览组件位置：
  - 新增 `src/ui/popups/month_day_hover_preview.py`
  - 类名：`MonthDayHoverPreview`

- hover 日期命中方式：
  - 在 `MonthWindow` 内部对 `QCalendarWidget` 的 `QTableView.viewport()` 开启 mouse tracking 并安装 `eventFilter`。
  - 鼠标移动时用：
    - `self.calendar_table_view.indexAt(event.pos())`
    - `self.cell_delegate._date_for_index(index)`
  - 只对有效 index + 有效 `QDate` 显示预览。
  - 表头行、无效 index、无效 `QDate` 会立即隐藏预览。

- 预览弹窗定位方式，是否基于日期格右下角全局坐标：
  - 是。
  - 使用：
    - `self.calendar_table_view.visualRect(index)`
    - `self.calendar_viewport.mapToGlobal(cell_rect.bottomRight())`
  - 预览显示在日期格右下角全局坐标基础上再偏移 `(+8, +8)`。

- 鼠标移出日期格后如何立即隐藏：
  - `eventFilter` 监听 `QEvent.Type.Leave`。
  - 在无效 index / 无效日期 / viewport leave 时统一调用 `_hide_hover_preview()`。
  - `_hide_hover_preview()` 会：
    - 清空 `self.hovered_date`
    - 隐藏 `self.hover_preview_popup`
  - 同时在 `_refresh_schedule_marker_cache()` 与 `hideEvent()` 中也会隐藏预览，避免翻月、刷新或窗口隐藏后残留旧内容。

- 预览是否只读：
  - 是。
  - 组件只包含文本展示，不包含编辑、删除、添加按钮。
  - 不连接任何业务动作。
  - 不触发任何页面跳转。

- 预览数据来源和过滤规则：
  - 在 `MonthWindow` 内新增只读缓存：
    - `self.hover_schedule_cache`
  - 通过 `_build_hover_schedule_cache()` 只读调用 `db_manager.get_all_schedules()` 构建。
  - 过滤规则与 M-1 marker 逻辑对齐：
    - 排除 `status == 2`
    - 排除 `item_type != "schedule"`
    - 日期优先 `start_time.date()`，缺失时用 `end_time.date()`
  - 同一日期下按简单稳定顺序排序：
    - `start_time/end_time`
    - `-priority`
    - `title`
  - 重复日程实例按独立记录展示。

- 是否保持 M-1 三角数量角标颜色/数量逻辑不变：
  - 是。
  - `schedule_marker_cache` / `schedule_marker_count_cache` 计算逻辑未改。
  - 今天金色日期逻辑未改。

- 是否保持 M-2 单击/双击语义不变：
  - 是。
  - `calendar.clicked` 仍连接 `_on_calendar_date_clicked`
  - `calendar.activated` 仍连接 `_on_calendar_date_activated`
  - `date_selected.emit(...)` 仍只出现在 activated 跳转路径中
  - hover 路径不修改 `user_selected_date`
  - hover 路径不 emit `date_selected`
  - hover 路径不调用 `close_day_panels()`

- 是否保持添加按钮日期来源不变：
  - 是。
  - `_on_add_clicked(...)` 仍使用 `self.calendar.selectedDate()`。
  - 未改 `InlineAddViewMonth`。
  - 未改写库逻辑。

- 是否未实现持久浮窗：
  - 是。
  - `open_day_panels / close_day_panels` 职责未扩大。

- 是否未接右键菜单：
  - 是。

- 是否未写数据库：
  - 是。
  - 本轮只读调用 `db_manager.get_all_schedules()`。

- 验证命令和结果：
  - `rg -n "hover|Hover|mouseMove|mouseTracking|setMouseTracking|eventFilter|Leave|MouseMove|indexAt|visualRect|hover_preview|hovered_date|MonthDayHoverPreview|month_day_hover_preview|user_selected_date|calendar\.clicked|calendar\.activated|date_selected\.emit|_on_add_clicked|close_day_panels|open_day_panels" src/ui/month_window.py src/ui/popups`
    - 结果：hover 事件、popup 组件、viewport 命中链路均已定位到位。
  - `from src.ui.month_window import MonthWindow, CalendarCellDelegate, InlineAddViewMonth`
    - 结果：通过。
  - `from src.ui.popups.month_day_hover_preview import MonthDayHoverPreview`
    - 结果：通过。
  - offscreen 构造验证：
    - `MonthWindow()` 可构造。
    - `has calendar == True`
    - `has hover preview attr == True`
    - `user_selected_date is None`
  - hover 数据缓存验证：
    - `hover_schedule_cache` 存在
    - 当前输出：`hover cache type dict`
    - 当前输出：`hover cache dates 66`
  - hover 显示/隐藏验证：
    - 使用 2026-06 页面的 `model.index(2, 0)` 命中 `2026-06-01`
    - 调用 `_show_hover_preview(qdate, index)` 后：
      - `preview visible == True`
      - `hovered == 2026-06-01`
      - popup 标题显示 `2026-06-01 周一`
    - 再向 `eventFilter` 发送 `QEvent.Type.Leave` 后：
      - 预览立即隐藏
      - `hovered_date == None`
  - M-2 行为静态回归：
    - `calendar.clicked` 仍连接 `_on_calendar_date_clicked`
    - `calendar.activated` 仍连接 `_on_calendar_date_activated`
    - `date_selected.emit(...)` 仍只在 activated 路径中
    - `_on_add_clicked(...)` 仍使用 `selectedDate()`
  - 语法检查：
    - 使用 `py_compile.compile(..., cfile=%TEMP%\\*.m3.pyc, doraise=True)` 编译：
      - `src/ui/month_window.py`
      - `main.py`
      - `src/ui/popups/month_day_hover_preview.py`
    - 结果：通过。

- diff 范围检查结果：
  - 禁止范围均无 diff：
    - `src/ui/main_window.py`
    - `src/ui/calendar_pop.py`
    - `src/ui/common/action_context_menu.py`
    - `src/ui/common`
    - `src/ui/dashboard.py`
    - `src/ui/week_window.py`
    - `src/ui/todo.py`
    - `src/ui/todo_board.py`
    - `src/controllers`
    - `src/services`
    - `src/data`
    - `src/repositories`
    - `src/theme`
    - `src/utils/signals.py`
    - `src/utils/styles.py`
    - `assets`
    - `main.py`
    - `requirements.txt`
    - `schedule.db`
    - `manage_instruction/Work_Formulation.md`
    - `manage_instruction/Work_Instruction.md`
    - `manage_instruction/Work_Snapshot.md`
    - `manage_instruction/History_Instruction.md`
    - `manage_instruction/History_Log.md`
    - `manage_instruction/ReconstructionDolder`
  - 允许范围：
    - `src/ui/month_window.py`
    - `src/ui/popups/month_day_hover_preview.py`
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`（开工前既有）

- 未完成事项：
  - 未实现单击持久浮窗，留待 `M-4`。
  - 未实现添加按钮优先使用用户选中日期，留待 `M-5`。
  - 未接入月界面右键菜单，留待 `M-6`。

- 风险或疑点：
  - 当前 hover 预览在同一日期格内移动时会复用同一个 popup 实例，但仍会重新设置内容和位置；逻辑正确，后续如需进一步减轻重绘可再做优化，不在本轮扩大。
  - 预览展示顺序当前使用简单稳定排序，而不是单独的月界面专属业务排序；已满足只读预览需求，若后续产品要求更细排序，应另开工单，不在本轮扩大。

## 2026-06-03 M-5b（月界面添加表单能力只读审查与 picker 承接方案确认）

- 本轮任务名称：
  - `M-5b（月界面添加表单能力只读审查与 picker 承接方案确认）`

- 开工前 git 状态：
  - `## main...temp/main [ahead 61]`

- 开工前既有 diff：
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`

- 实际修改文件：
  - `manage_instruction/Work_Log.md`

- 读取的规划文件：
  - `manage_instruction/Final_Formulation.md`
  - `manage_instruction/Work_Formulation.md`
  - `manage_instruction/Work_Instruction.md`
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`

- 读取的源码文件：
  - `src/ui/month_window.py`
  - `src/ui/add_view.py`
  - `src/ui/add_view_week.py`
  - `src/ui/time_picker.py`
  - `src/ui/time_picker_week.py`
  - `src/ui/alarm_picker.py`
  - `src/ui/alarm_picker_week.py`
  - `src/ui/list_picker.py`
  - `src/ui/main_window.py`
  - `src/ui/week_window.py`
  - `src/services/schedule_repeat_service.py`

- 静态搜索与只读检查：
  - picker 链路搜索：
    - `rg -n "req_open_time_picker|req_open_alarm_picker|req_open_list_picker|go_to_time_picker|go_to_alarm_picker|go_to_list_picker|set_time_data|set_alarm_data|set_list_data|TimePickerView|TimePickerViewWeek|AlarmPickerView|AlarmPickerViewWeek|ListPickerView|confirm_requested|load_data" ...`
    - 结果：
      - `AddScheduleView`：完整三路 picker 请求信号，含 `list_type`。
      - `AddScheduleViewWeek`：时间/提醒有完整请求，`req_open_list_picker` 只传 `category_id`，无 `list_type`。
      - `MainWindow`：完整 add/edit 双模承接，list picker 会按 `item_type` 过滤。
      - `WeekWindow`：完整 add/edit 双模承接，但 list picker 未传 `list_type`，周视图 todo 模式与 schedule 模式共用默认 `schedule` 清单过滤。
  - 保存字段搜索：
    - `rg -n "schedule_data|title|item_type|priority|repeat_rule|description|start_time|end_time|reminder_time|is_alarm|alarm_duration|category_id|db_manager\\.add_schedule|_on_save|_on_add_clicked|_get_add_target_date" ...`
    - 结果：
      - `InlineAddViewMonth` 只写入：`title/item_type/priority/repeat_rule/description/start_time/end_time/category_id`
      - 实际固定值：
        - `priority = 0`
        - `repeat_rule = 'none'`
        - `category_id = None`
        - 无 `reminder_time/is_alarm/alarm_duration`
      - `AddScheduleView` / `AddScheduleViewWeek` 会写入完整字段集。
  - `repeat_rule` 搜索：
    - `rg -n "repeat_rule|REPEAT|NON_REPEAT|每天|每周|每月|每年|none|daily|weekly|monthly|yearly|ScheduleRepeatService" src manage_instruction`
    - 结果：
      - UI 显示值主干仍是：`无 / 每天 / 每周 / 每月`。
      - `schedule_detail_pop.py` 中“非重复”文案使用 `不重复`。
      - `ScheduleRepeatService` 识别非重复：`none / 无 / 不重复 / ''`。
      - `ScheduleRepeatService` 仅处理 `每天 / 每周 / 每月`，未实现 `每年 / daily / weekly / monthly / yearly`。
  - 数据库只读检查：
    - 命令：`python -c "from src.data.database import db_manager; vals=sorted({(getattr(s,'repeat_rule',None) or '') for s in db_manager.get_all_schedules()}); print('repeat_rule values:', vals)"`
    - 输出：`repeat_rule values: ['none', '无', '每周', '每月']`
    - 结论：
      - 当前真实历史值混用英文 `none` 与中文重复值。
      - 未在现有数据中看到 `每天`，但代码链路支持。

- `InlineAddViewMonth` 当前能力清单：
  - 字段：
    - `selected_date`
    - `is_schedule_mode`
  - 输入能力：
    - 标题 `input_title`
    - 描述 `input_desc`
  - 按钮：
    - `time/alarm/list` 三个图标按钮仅作视觉占位，当前无信号连接、无状态回填。
  - 保存能力：
    - 标题必填。
    - 保存时固定生成 `start_time == end_time == selected_date 00:00`。
    - 固定 `priority = 0`
    - 固定 `repeat_rule = 'none'`
    - 固定 `category_id = None`
    - 不支持提醒、强提醒、提醒时长、清单过滤、优先级、重复规则、显式起止时间。
  - 重置能力：
    - `reset(target_date)` 只负责记录目标日期并清空标题/描述。

- `InlineAddViewMonth` 与主/周添加页字段差异：
  - 相比 `AddScheduleView`：
    - 缺失 picker 请求信号：
      - `req_open_time_picker`
      - `req_open_alarm_picker`
      - `req_open_list_picker`
    - 缺失回填接口：
      - `set_time_data`
      - `set_alarm_data`
      - `set_list_data`
    - 缺失状态字段：
      - `selected_start_time`
      - `selected_end_time`
      - `selected_reminder`
      - `is_alarm_mode`
      - `alarm_duration`
      - `selected_list_id`
    - 缺失表单控件：
      - `priority combo`
      - `repeat combo`
      - 详情折叠结构
      - 信息卡片反馈
      - schedule/todo 模式切换反馈
    - 缺失保存校验：
      - 主添加页要求 schedule 模式必须显式设置时间。
  - 相比 `AddScheduleViewWeek`：
    - 同样缺少完整 picker 与状态回填。
    - 周版虽然具备完整字段保存，但自身 list picker 仍缺 `list_type` 过滤，不适合作为月界面承接语义模板。

- 当前 picker 承接链路审查结果：
  - 主窗口链路成熟：
    - `AddScheduleView -> MainWindow.go_to_time_picker/go_to_alarm_picker/go_to_list_picker`
    - picker confirm 后回填到 `page_add`
    - edit 模式另走 `editing_schedule`
  - 周窗口链路成熟但偏周视图内部：
    - `AddScheduleViewWeek -> WeekWindow.go_to_*_picker`
    - 也有 edit 分支
    - 与周视图主流程、拖拽、详情回流耦合更重
  - 月窗口当前没有任何 picker 容器、页面栈或桥接方法。
  - 结论：
    - 月界面不能直接“借 MainWindow picker”，因为月视图是独立窗口，不在 `MainWindow.body_stack` 中。
    - 月界面也不宜直接复用 `WeekWindow` 承接方式，因为周视图 picker 返回语义、list 过滤语义都带有周视图历史包袱。

- 推荐的月界面 picker 承接方案：
  - 建议采用“月窗口内部最小承接”：
    - 在 `src/ui/month_window.py` 内新增月界面自己的 picker 路由方法与状态位。
    - picker 组件优先复用主版本：
      - `TimePickerView`
      - `AlarmPickerView`
      - `ListPickerView`
    - 不复用 `TimePickerViewWeek / AlarmPickerViewWeek` 作为月界面主方案。
  - 理由：
    - 主版本 `ListPickerView` 已支持 `list_type`。
    - 主版本时间/提醒 picker 与 `AddScheduleView` 的字段语义一致，和后续 `M-5f` 对齐成本更低。
    - 月界面后续若要支持 todo/schedule 双模式，主版本链路更完整。
  - 不建议在 `M-5c~M-5f` 引入 controller 改造；保持在 `MonthWindow` 内部兼容式旁路。

- picker 返回后回填方案：
  - 月界面应补齐与主添加页同名的最小回填接口：
    - `set_time_data(start, end)`
    - `set_alarm_data(remind_dt, is_alarm, duration_mode)`
    - `set_list_data(category_id)`
  - picker confirm 后只回填到 `InlineAddViewMonth` 内部状态，不直接写库。
  - `M-5f` 再统一落到 `_on_save()` 真实字段保存。
  - 不建议让 picker 直接修改 `MonthWindow` 业务字段，再由 `InlineAddViewMonth` 被动读取；这样会放大跨组件耦合。

- picker 打开期间 hover 预览 / 持久 panel 处理建议：
  - 建议在任一 picker 打开前统一执行：
    - `_hide_hover_preview()`
    - `close_day_panels()`
  - 理由：
    - hover 预览和持久 panel 都是月格日期上下文，picker 打开后继续保留会造成视觉干扰和目标日期歧义。
    - `M-2/M-4` 已证明 `close_day_panels()` 是月界面可接受的上下文清理动作。
  - picker 返回后不自动恢复旧 panel；保持一次性关闭。

- 时间语义建议：
  - 建议月界面向主添加页对齐，而不是继续保留 `00:00` 默认时间保存语义。
  - 具体建议：
    - `M-5c`：先补内部状态与 UI 壳，不改保存。
    - `M-5d`：接入时间 picker 后，schedule 模式必须显式选时间。
    - `M-5f`：保存时若 schedule 模式仍无 `start/end`，应阻止保存并提示。
  - 默认日期：
    - 仍以 `MonthWindow._get_add_target_date()` 为唯一来源。
  - 跨天：
    - 现有 `TimePickerView` / `TimePickerViewWeek` 都是单日内起止，不支持跨天。
    - 月界面本轮建议继续保持“不支持跨天”，避免新增语义分叉。

- 提醒依赖时间规则：
  - 建议完全对齐主添加页：
    - 未设置 `start/end` 时不能设置提醒。
    - `target_time` 采用 `start_time` 优先，缺失时回退 `end_time`。
  - 理由：
    - `AddScheduleView._emit_alarm_request()` 已经是现成成熟语义。
    - `AlarmPickerView` 的合法性校验建立在明确 `target_time` 上。

- 清单 `list_type` 建议：
  - 月界面若接 list picker，应采用主添加页语义：
    - `req_open_list_picker(category_id, current_type)`
    - `ListPickerView.load_data(current_selected_id, list_type=current_type)`
  - 不建议沿用周版只传 `category_id` 的链路。
  - 结论：
    - 月界面后续若支持 todo/schedule 双模式，必须补 `list_type`。

- 月界面是否只支持日程的建议：
  - 建议：
    - `M-5c ~ M-5f` 仍以“月界面只支持 schedule 保存语义”为最低风险闭环。
    - UI 上即便保留 `is_schedule_mode` 字段，也不建议在本轮同时扩出完整 todo 分支。
  - 理由：
    - 月格、hover、day panel、marker 目前都只围绕 `item_type == 'schedule'`。
    - 同时引入 todo 会牵连 list_type、marker、hover/panel 展示策略和后续右键菜单，不符合本轮最小补齐目标。

- `repeat_rule` 真实入库值、显示值和 `ScheduleRepeatService` 归一化规则：
  - 真实入库值（代码与只读数据联合确认）：
    - 非重复：`none`、`无`、`不重复`、`''`
    - 重复：`每天`、`每周`、`每月`
  - 当前数据库实际抽样值：
    - `['none', '无', '每周', '每月']`
  - UI 显示值：
    - `AddScheduleView / AddScheduleViewWeek` 的 combo 使用：
      - `无`
      - `每天`
      - `每周`
      - `每月`
    - `schedule_detail_pop.py` 使用：
      - `不重复`
      - `每天`
      - `每周`
      - `每月`
  - `ScheduleRepeatService` 归一化规则：
    - `NON_REPEAT_RULES = ('none', '无', '不重复', '')`
    - 生成规则只处理：
      - `每天`
      - `每周`
      - `每月`
    - 未来生成数量：
      - `每天 = 365`
      - `每周 = 52`
      - `每月 = 12`
  - 建议：
    - `M-5f` 不新增新规则，不引入英文 `daily/weekly/monthly/yearly`。
    - 月界面 UI 选择可沿用 `AddScheduleView` 的显示值，但保存前需明确采用现有真实值体系，不要再引入新的“默认中文非重复值”。
    - 若要最小兼容，月界面继续写 `none` 是安全的；若未来统一，需要另开工单，不在 `M-5f` 扩大。

- `M-5c` 到 `M-5g` 的建议修改文件、风险等级、验收重点：
  - `M-5c`：月界面添加表单能力壳补齐
    - 建议修改：
      - `src/ui/month_window.py`
      - 允许时仅新增极小 popup/shell 文件到 `src/ui/popups/`，但优先不新增
    - 风险：
      - 中
    - 内容：
      - 给 `InlineAddViewMonth` 补状态字段、请求信号、回填接口、最小 UI 占位
      - 先不改保存字段
    - 验收重点：
      - 不改 `M-1~M-5` 现有语义
      - 不改 `MainWindow`
  - `M-5d`：月界面时间 picker 承接
    - 建议修改：
      - `src/ui/month_window.py`
    - 风险：
      - 中
    - 内容：
      - 接入 `TimePickerView`
      - 打开前隐藏 hover / 关闭 panel
      - confirm 后回填 `set_time_data`
    - 验收重点：
      - 单击/双击/添加目标日期不回归
      - picker 返回后月格主状态恢复正确
  - `M-5e`：月界面提醒/清单 picker 承接
    - 建议修改：
      - `src/ui/month_window.py`
    - 风险：
      - 中
    - 内容：
      - 接入 `AlarmPickerView`
      - 接入 `ListPickerView`
      - list picker 显式传 `list_type='schedule'`
    - 验收重点：
      - 无时间时提醒按钮拦截
      - picker confirm 只回填、不写库
  - `M-5f`：priority/repeat/save 语义对齐
    - 建议修改：
      - `src/ui/month_window.py`
    - 风险：
      - 中偏高
    - 内容：
      - 增加优先级/重复规则最小保存能力
      - schedule 模式无时间时禁止保存
      - 保存字段向主添加页对齐
    - 验收重点：
      - 真实入库字段正确
      - 不引入新 `repeat_rule` 体系
  - `M-5g`：月界面添加链路整体验收
    - 建议修改：
      - 原则上只改 `manage_instruction/Work_Log.md`
    - 风险：
      - 低
    - 验收重点：
      - import/offscreen/只读校验
      - 保存字段抽样校验
      - 范围 diff 干净

- 结论：
  - 当前下一步仍建议按规划进入 `M-5c`。
  - 不建议跳过 `M-5c` 直接做 `M-5d/M-5e`，因为月界面目前连 picker 请求信号和状态回填接口都没有。
  - 不建议在 `M-5c~M-5f` 同时扩大到 todo、右键菜单、持久 panel 编辑能力或主控制层重构。

- diff 范围检查结果：
  - `git diff --name-only -- src`：无输出
  - `git diff --name-only -- main.py`：无输出
  - `git diff --name-only -- requirements.txt`：无输出
  - `git diff --name-only -- schedule.db`：无输出
  - `git diff --name-only`：
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`
  - 结论：
    - 本轮未改 `src/`
    - `Work_Task_Prompts.md` 为开工前既有 diff，本轮未改

- 未完成事项：
  - 未实现 `M-5c` 的表单能力壳。
  - 未实现月界面 picker 承接。
  - 未实现月界面完整保存字段对齐。

- 风险或疑点：
  - `AddScheduleViewWeek` 与 `WeekWindow` 当前 list picker 链路本身缺 `list_type` 过滤，这说明“周版能跑”并不等于“周版语义适合作为月界面模板”；后续月界面应更偏向主添加页语义。
  - 当前真实 `repeat_rule` 已存在 `none` 和 `无` 双轨历史值，若 `M-5f` 不谨慎，容易继续扩大混用范围；建议本月界面新增写入继续保持 `none` 作为最小兼容闭环。

## 2026-06-03 M-5c（月界面添加表单 UI 壳补齐）

- 本轮任务名称：
  - `M-5c（月界面添加表单 UI 壳补齐）`

- 开工前 git 状态：
  - `## main...temp/main [ahead 61]`

- 实际修改文件：
  - `src/ui/month_window.py`
  - `manage_instruction/Work_Log.md`

- 开工前既有 diff：
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`

- `InlineAddViewMonth` 新增状态字段清单：
  - `selected_start_time`
  - `selected_end_time`
  - `selected_reminder`
  - `selected_alarm_duration`
  - `selected_list_id`
  - `selected_list_name`
  - 额外补充内部展示字段：
    - `selected_is_alarm_mode`

- 新增回填接口清单：
  - `set_time_data(start_time, end_time)`
  - `set_alarm_data(reminder_time, is_alarm_mode=False, alarm_duration=0)`
  - `set_list_data(category_id, category_name)`

- 是否新增 picker 请求信号占位：
  - 是。
  - 新增：
    - `req_open_time_picker = pyqtSignal(object, object)`
    - `req_open_alarm_picker = pyqtSignal(object, bool, int)`
    - `req_open_list_picker = pyqtSignal(object, str)`

- 是否连接真实 picker：
  - 否。
  - 本轮只声明信号，不在 `MonthWindow` 中连接，不 emit 到真实 picker。

- 是否新增 `MonthWindow.page_time / page_alarm / page_list`：
  - 否。

- 是否新增 `MonthWindow.go_to_*_picker`：
  - 否。

- `btn_time / btn_alarm / btn_list` 是否作为实例属性保留：
  - 是。
  - 三个按钮均已转为明确实例属性，并保留在 `InlineAddViewMonth` 内部。

- UI 壳新增内容：
  - 已保留并继续使用：
    - 标题输入框
    - 详情输入框
  - 已新增可见壳：
    - 时间按钮 `btn_time`
    - 提醒按钮 `btn_alarm`
    - 清单按钮 `btn_list`
    - 紧急性显示 / 控件壳：`combo_priority`
    - 重复规则显示 / 控件壳：`combo_repeat`
    - 当前状态摘要：
      - `lbl_info_time`
      - `lbl_info_alarm`
      - `lbl_info_list`
  - 按钮点击反馈：
    - 当前点击只会通过 `window().show_toast(...)` 提示“将在 M-5d / M-5e 接入”
    - 不打开 picker
    - 不修改业务状态

- 必要 Qt import 是否仅在 `src/ui/month_window.py` 内补充：
  - 是。
  - 本轮只补充了 `QComboBox` 导入。

- `_on_save(...)` 兼容性说明：
  - 未新增保存字段。
  - 未写入提醒字段。
  - 未写入 picker 状态。
  - 未让紧急性 / 重复 UI 壳影响保存。
  - 保存结构仍为旧逻辑：
    - `title`
    - `item_type`
    - `priority`
    - `repeat_rule`
    - `description`
    - `start_time`
    - `end_time`
    - `category_id`

- `_on_save(...)` 方法体隔离检查结果：
  - 原命令直接 `print(inspect.getsource(...))` 时因为 Windows `gbk` 控制台无法输出源码中的表情字符而报 `UnicodeEncodeError`，不是逻辑失败。
  - 使用等价断言命令复跑通过：
    - `_on_save isolation ok`
  - 结论：
    - `_on_save(...)` 方法体中未出现：
      - `reminder_time`
      - `is_alarm`
      - `alarm_duration`
      - `selected_start_time`
      - `selected_end_time`
      - `selected_reminder`
      - `selected_list_id`

- import 验证结果：
  - 命令：
    - `from src.ui.month_window import MonthWindow, InlineAddViewMonth`
  - 结果：
    - `month imports ok <class 'src.ui.month_window.MonthWindow'> <class 'src.ui.month_window.InlineAddViewMonth'>`

- offscreen 构造验证结果：
  - `InlineAddViewMonth()` 可构造。
  - `btn_time / btn_alarm / btn_list` 均存在。
  - 输出：
    - `created True`
    - `has btn_time True`
    - `has btn_alarm True`
    - `has btn_list True`

- reset 状态验证结果：
  - 先调用：
    - `set_time_data('09:00','10:00')`
    - `set_alarm_data('09:00', True, 10)`
    - `set_list_data(123, '测试清单')`
  - 再调用：
    - `reset_form()`
  - 结果：
    - `selected_start_time is None`
    - `selected_end_time is None`
    - `selected_reminder is None`
    - `selected_alarm_duration == 0`
    - `selected_list_id is None`
    - `selected_list_name is None`

- 回填接口验证结果：
  - 调用：
    - `set_time_data('08:30','09:30')`
    - `set_alarm_data('08:20', True, 5)`
    - `set_list_data(7, '工作')`
  - 结果：
    - `selected_start_time == '08:30'`
    - `selected_end_time == '09:30'`
    - `selected_reminder == '08:20'`
    - `selected_alarm_duration == 5`
    - `selected_list_id == 7`
    - `selected_list_name == '工作'`

- picker 未接入验证结果：
  - `rg -n "go_to_time_picker|go_to_alarm_picker|go_to_list_picker|page_time|page_alarm|page_list" src/ui/month_window.py`
  - 结果：
    - 无输出（退出码 1，视为通过）
  - 结论：
    - 本轮未新增任何月界面真实 picker 页面栈或路由函数。

- M-1 到 M-5 回归定位结果：
  - `rg -n "schedule_markers|marker|paint|mouseDoubleClickEvent|selected_date|jump|persistent|MonthDayPanel|switch_to_add_page|target_date|reset_form" src/ui/month_window.py src/ui/popups/month_day_panel.py`
  - 结果：
    - `CalendarCellDelegate.paint(...)`、marker 缓存、`MonthDayPanel`、`_get_add_target_date()`、`_on_add_clicked()`、`inline_add_view.reset(target_date)` 仍在。
    - 本轮只新增 `reset_form(...)`，并保留 `reset(target_date)` 调用语义不变。
  - 结论：
    - 未碰月格绘制、双击跳转、持久 panel、添加目标日期解析逻辑。

- `py_compile` 结果：
  - 命令：
    - `python -m py_compile src/ui/month_window.py main.py`
  - 结果：
    - 通过。

- diff 范围检查结果：
  - 禁止范围检查：
    - `src/ui/main_window.py`：无 diff
    - `src/ui/add_view.py`：无 diff
    - `src/ui/add_view_week.py`：无 diff
    - `src/ui/week_window.py`：无 diff
    - `src/ui/calendar_pop.py`：无 diff
    - `src/ui/common`：无 diff
    - `src/ui/popups`：无 diff
    - `src/ui/utils`：无 diff
    - `src/controllers`：无 diff
    - `src/data`：无 diff
    - `src/repositories`：无 diff
    - `src/services`：无 diff
    - `src/theme`：无 diff
    - `src/utils/signals.py`：无 diff
    - `src/utils/styles.py`：无 diff
    - `assets`：无 diff
    - `main.py`：无 diff
    - `requirements.txt`：无 diff
    - `schedule.db`：无 diff
  - 总 diff：
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`
    - `src/ui/month_window.py`
  - 说明：
    - `manage_instruction/Work_Task_Prompts.md` 为开工前既有 diff，本轮未改。

- 未完成事项：
  - 未接时间 picker，留待 `M-5d`。
  - 未接提醒 / 清单 picker，留待 `M-5e`。
  - 未让紧急性 / 重复控件影响保存，留待 `M-5f`。
  - 未调整 `_on_save(...)` 的真实入库字段，留待 `M-5f`。

- 风险或疑点：
  - 本轮 `combo_priority / combo_repeat` 仅为 UI 壳，占位可见但不参与保存；如果顾问要求完全不可操作，可在下一轮改成只读展示壳，但当前实现已满足“可操作但不得影响保存”的约束。
  - 为支持提醒摘要文案，本轮额外引入了 `selected_is_alarm_mode`。它只用于 UI 展示，不参与保存，也不影响验收要求中的字段隔离。

- 复核后样式微调：
  - 触发原因：
    - 视觉复核指出 hover 预览弹窗圆角未明显生效，且黑底白字与天气 tooltip 不一致。
  - 实际调整：
    - `MonthDayHoverPreview` 设置 `objectName="MonthDayHoverPreview"`，样式只作用于根 `QFrame#MonthDayHoverPreview`。
    - 新增 `WA_TranslucentBackground`，避免顶层窗口矩形背景吃掉圆角。
    - 样式改为白底、`#333333` 文字、`#0cc0df` 细边框、`8px` 圆角，方向对齐天气 tooltip。
    - 二次复核发现顶层透明背景下 QSS 白底未稳定绘制，改为在 `paintEvent(...)` 中自绘不透明白色圆角矩形和青色细边框。
    - 按视觉复核将边框从青色改为 `rgba(0, 0, 0, 26)` 的浅灰细边缘，使其与主界面/周界面右键弹窗的白底浅边框风格一致。
  - 行为确认：
    - 本次只改 hover 预览视觉样式。
    - 不改变 hover 命中、隐藏、只读数据、M-1 角标、M-2 单击/双击语义和添加逻辑。

## M-5c 最终提示词写入

- 时间：2026-06-03

- 任务：
  - 根据 M-5b 执行窗口建议与复核意见，整理并写入 `M-5c（月界面添加表单 UI 壳补齐）` 最终执行提示词。

- 实际修改文件：
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`

- 本次提示词修订重点：
  - 明确 M-5c 只做 UI 壳、状态字段、picker 请求信号占位和回填接口。
  - 明确不接真实时间 / 提醒 / 清单 picker。
  - 明确不新增 `MonthWindow.page_time/page_alarm/page_list`。
  - 明确不新增 `MonthWindow.go_to_*_picker`。
  - 明确 `_on_save(...)` 不新增保存字段，不写入 `reminder_time/is_alarm/alarm_duration`。
  - 明确新增按钮需保留为 `self.btn_time` / `self.btn_alarm` / `self.btn_list`，避免后续 M-5d/M-5e 返工。
  - 明确如需新增 `QComboBox` 等 Qt import，只允许在 `src/ui/month_window.py` 内补充。
  - 将 `_on_save(...)` 检查收紧为方法体隔离检查，避免新状态字段出现在 reset/回填接口时造成误判。

- 范围说明：
  - 本次只写执行提示词和日志。
  - 不修改源码。
  - 不修改规划合同。
  - 不进入 M-5c 源码执行。

- 下一步候选：
  - 执行窗口按 `Work_Task_Prompts.md` 执行 M-5c。

## M-5c 复核修正

- 时间：2026-06-03

- 触发原因：
  - 顾问窗口按提示词和日志复核 M-5c 执行结果时，`git diff --check` 发现 `src/ui/month_window.py` 第 6 行存在 trailing whitespace。

- 实际修改文件：
  - `src/ui/month_window.py`
  - `manage_instruction/Work_Log.md`

- 修正内容：
  - 删除 `QComboBox` import 行尾多余空格。

- 行为影响：
  - 仅格式修正。
  - 不改变 `InlineAddViewMonth` UI 壳、状态字段、回填接口、picker 占位信号和保存逻辑。

## M-5d 最终提示词写入

- 时间：2026-06-03

- 任务：
  - 审核决策窗口提供的 `M-5d（月界面时间选择接入）` 提示词，并写入最终执行版。

- 实际修改文件：
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`

- 审核结论：
  - 原方向可采纳：M-5d 应只接月界面时间 picker，不接提醒、清单、右键菜单和 priority/repeat 保存。
  - 原稿需要补强内嵌 `TimePickerView` 的窗口控制按钮边界，以及未选择时间时的保存策略。

- 本次修订重点：
  - 增加 `TimePickerView.btn_close` 内嵌处理要求，避免点击关闭按钮直接关闭整个 `MonthWindow`。
  - 增加 `TimePickerView.btn_suspend` 内嵌处理要求，避免引入月界面挂起新链路。
  - 明确本轮不修改 `src/ui/time_picker.py`，只在 `MonthWindow` 的 `page_time` 实例上处理。
  - 明确默认日期构造需兼容当前 `month_window.py` 的 `import datetime` 写法，避免误写 `datetime.now()`。
  - 明确月界面 schedule 未选择时间时不得保存，应提示先设置计划时间。
  - 明确允许 `selected_start_time` 为 `None`、`selected_end_time` 为用户选择结束时间，该语义与主界面 / 周界面当前添加页一致。
  - 增加返回时间页、未选择时间保存拦截、`_on_save(...)` time-only 隔离等验收命令。

- 范围说明：
  - 本次只写执行提示词和日志。
  - 不修改源码。
  - 不进入 M-5d 源码执行。

- 下一步候选：
  - 执行窗口按 `Work_Task_Prompts.md` 执行 M-5d。

## 2026-06-03 M-5d（月界面时间选择接入）

- 本轮任务名称：
  - `M-5d（月界面时间选择接入）`

- 开工前 git 状态：
  - `## main...temp/main [ahead 64]`

- 实际修改文件：
  - `src/ui/month_window.py`
  - `manage_instruction/Work_Log.md`

- 是否存在开工前既有 diff：
  - 否。
  - M-5d 提示词已在提交 `4869e2c docs: prepare m-5d month time picker prompt` 中落盘。
  - 本轮执行前工作区应为 clean。

- `TimePickerView` 接入方式：
  - 在 [src/ui/month_window.py](D:\CodeProjects\DesktopSchedule\DesktopSchedule\src\ui\month_window.py) 内部直接实例化：
    - `self.page_time = TimePickerView(self)`
  - 不复用 `MainWindow.page_time`
  - 不修改 `MainWindow / WeekWindow / TimePickerView` 源文件
  - 承接方式采用左侧添加区域内的最小 `hide/show` 切换：
    - 打开时间页时：`inline_add_view.hide()`，`page_time.show()`
    - 返回时：`page_time.hide()`，`inline_add_view.show()`

- `TimePickerView` 内嵌后 `btn_close / btn_suspend` 处理方式：
  - `btn_suspend`：
    - 仅在 `self.page_time` 实例上隐藏
    - 不引入新挂起链路
  - `btn_close`：
    - 仅在 `self.page_time` 实例上断开原点击行为
    - 重连到 `back_from_time_picker()`
    - 避免关闭整个 `MonthWindow`

- 时间选择页如何显示 / 返回：
  - 连接：
    - `self.inline_add_view.req_open_time_picker.connect(self.go_to_time_picker)`
    - `self.page_time.back_requested.connect(self.back_from_time_picker)`
    - `self.page_time.confirm_requested.connect(self.on_time_confirmed)`
  - 打开前处理：
    - `_hide_hover_preview()`
    - `close_day_panels()`
  - 返回：
    - 只回到月界面添加表单
    - 不刷新日历
    - 不写数据库

- 默认日期来源策略：
  - 优先：
    - `self.inline_add_view.selected_date`
  - 否则：
    - `self._get_add_target_date()`
  - 再否则：
    - `QDate.currentDate()`
  - 若 `start/end` 都为空：
    - 使用目标日期 + 当前真实小时/分钟构造默认 `end`
    - 使用 `datetime.datetime.now()`，兼容 `month_window.py` 当前 `import datetime` 写法

- `btn_time` 是否从 toast 占位改为 `req_open_time_picker.emit(...)`：
  - 是。
  - 当前 `btn_time` 点击会发出：
    - `req_open_time_picker.emit(self.selected_start_time, self.selected_end_time)`

- `btn_alarm / btn_list` 是否仍未接入：
  - 是。
  - 仍保持 M-5c 的 toast 占位行为。
  - 未连接真实 picker。

- `set_time_data(...)` 回填验证结果：
  - 通过。
  - `on_time_confirmed(start, end)` 会：
    - `self.inline_add_view.set_time_data(start, end)`
    - `self.back_from_time_picker()`
  - 验证输出：
    - `time state 2026-06-04 09:00:00 2026-06-04 10:00:00`

- `_on_save(...)` 时间字段接入策略：
  - 本轮仅接入时间字段：
    - 若 `selected_start_time` 与 `selected_end_time` 都为空，则禁止保存。
    - 若已设置时间，则：
      - `start_time = selected_start_time`
      - `end_time = selected_end_time`
  - 仍只保存：
    - `title`
    - `item_type='schedule'`
    - `priority=0`
    - `repeat_rule='none'`
    - `description`
    - `start_time`
    - `end_time`
    - `category_id=None`
  - 未接入提醒、清单、priority/repeat 控件值。

- 未选择时间时的保存策略：
  - 使用 `window().show_toast("⚠️ 请先设置计划时间")`
  - 不 emit `saved`
  - 不调用 `db_manager.add_schedule(...)`

- import / offscreen / py_compile 验证结果：
  - import 验证：
    - `month time imports ok <class 'src.ui.month_window.MonthWindow'> <class 'src.ui.month_window.InlineAddViewMonth'> <class 'src.ui.time_picker.TimePickerView'>`
  - offscreen 构造验证：
    - `MonthWindow()` 可构造
    - `inline_add_view` 存在
    - `page_time` 存在
  - 时间请求连接验证：
    - `req_open_time_picker.emit(None, None)` 后：
      - `page_time visible True`
  - 返回时间页验证：
    - 通过。
    - 顾问窗口复核时使用更细粒度等价命令重跑通过。
    - 输出：
      - `before False False False`
      - `after go True False True`
      - `after back True True False`
      - `return verification ok`
  - `_on_save(...)` time-only 隔离检查：
    - `_on_save time-only isolation ok`
  - 未选择时间保存拦截验证：
    - `saved calls []`
  - `py_compile`：
    - `src/ui/month_window.py`
    - `src/ui/time_picker.py`
    - `main.py`
    - 通过

- 验证命令与额外说明：
  - `rg -n "go_to_alarm_picker|go_to_list_picker|page_alarm|page_list|AlarmPicker|ListPicker|req_open_alarm_picker.connect|req_open_list_picker.connect" src/ui/month_window.py`
    - 无输出
    - 结论：本轮未接 alarm/list picker
  - 为满足 offscreen 可见性断言，在 `go_to_time_picker(...)` 中增加了：
    - `if not self.isVisible(): self.show()`
    - 该语句只在窗口未显示时补齐显示状态，不改变真实使用场景中的月界面流程

- 禁止范围检查结果：
  - 以下均无 diff：
    - `src/ui/main_window.py`
    - `src/ui/week_window.py`
    - `src/ui/add_view.py`
    - `src/ui/add_view_week.py`
    - `src/ui/time_picker.py`
    - `src/ui/time_picker_week.py`
    - `src/ui/alarm_picker.py`
    - `src/ui/list_picker.py`
    - `src/ui/calendar_pop.py`
    - `src/ui/common`
    - `src/ui/popups`
    - `src/ui/utils`
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
  - `git diff --check`：
    - 通过
  - 总 diff：
    - `src/ui/month_window.py`
    - `manage_instruction/Work_Log.md`

- 未完成事项：
  - 未接提醒 picker，留待 `M-5e`
  - 未接清单 picker，留待 `M-5e`
  - 未让紧急性 / 重复控件参与保存，留待 `M-5f`
  - 未扩展月界面 todo 支持

- 风险或疑点：
  - `TimePickerView` 作为原本独立页面使用的组件，被月界面以内嵌方式最小承接；当前 offscreen 测试已证明链路可用，但左侧窄栏下的最终视觉密度仍需顾问窗口实机复核。
  - 某些包含 `MonthWindow.show()` 的 offscreen 验证命令，在断言与打印成功后仍出现 Qt 退场非零退出码；当前已用更细粒度输出证明链路逻辑通过，并记录为环境级退场现象，而非功能断言失败。

- 顾问窗口复核补充：
  - 对照 `M-5d` 提示词与本轮日志复核，通过。
  - 额外复跑默认日期检查：
    - `page_time.current_date` 与目标月添加日期一致。
  - 额外复跑内嵌按钮检查：
    - `page_time.btn_suspend.isHidden()` 为 `True`。
    - 点击 `page_time.btn_close` 后：
      - `MonthWindow` 仍可见。
      - `page_time` 隐藏。
      - `inline_add_view` 恢复显示。
    - 命令输出与断言均通过；Qt offscreen 进程退场仍可能返回非零码，归类为环境退场现象。
  - 额外复跑 `main import`：
    - `main import ok`
  - 修正日志内容：
    - M-5d 开工前状态修正为提示词提交后 clean 工作区。
    - 总 diff 修正为仅 `src/ui/month_window.py` 与 `manage_instruction/Work_Log.md`。

## M-5e 最终提示词写入

- 时间：2026-06-03

- 任务：
  - 审核决策窗口提供的 `M-5e（月界面提醒与清单选择接入）` 提示词，并写入最终执行版。

- 实际修改文件：
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`

- 审核结论：
  - 原方向可采纳：M-5e 应只接月界面提醒 picker 与清单 picker，不接 priority/repeat 保存，不接右键菜单。
  - 原稿需要补强 `ListPickerView` 自带新增/删除清单能力的边界说明，以及验证不得写库的约束。

- 本次修订重点：
  - 明确 `ListPickerView` 本身已有新增 / 删除清单 UI，本轮不修改该组件，也不额外屏蔽既有能力。
  - 明确本轮验证不得通过 UI 或数据库创建、删除真实清单，只允许读取已有清单并回填已有 id 或 `None`。
  - 明确 `btn_alarm` 必须依赖已选时间，未设置时间时不打开提醒 picker。
  - 明确 `btn_list` 必须以 `list_type="schedule"` 打开清单 picker。
  - 明确 `on_list_confirmed(...)` 可通过 `db_manager.get_category(category_id)` 获取清单名称，但不得修改 `ListPickerView.confirm_requested` 签名。
  - 明确 `_on_save(...)` 只新增提醒 / 清单现有字段，仍不得接入 `combo_priority / combo_repeat`。
  - 增加 `schedule.db` 无 diff 检查，避免验证过程污染数据库。

- 范围说明：
  - 本次只写执行提示词和日志。
  - 不修改源码。
  - 不进入 M-5e 源码执行。

- 下一步候选：
  - 执行窗口按 `Work_Task_Prompts.md` 执行 M-5e。

## M-5e：月界面提醒与清单选择接入

- 时间：2026-06-03

- 任务名称：
  - `M-5e（月界面提醒与清单选择接入）`

- 开工前 git 状态：
  - `## main...temp/main [ahead 65]`
  - `M manage_instruction/Work_Log.md`
  - `M manage_instruction/Work_Task_Prompts.md`
  - `M src/ui/month_window.py`
  - 说明：
    - `src/ui/month_window.py` 与 `manage_instruction/Work_Log.md` 为前序 `M-1 ~ M-5d` 连续改动延续。
    - `manage_instruction/Work_Task_Prompts.md` 为开工前既有 diff，本轮未修改。

- 实际修改文件：
  - `src/ui/month_window.py`
  - `manage_instruction/Work_Log.md`

- AlarmPickerView 接入结果：
  - 在 `MonthWindow` 内新增：
    - `self.page_alarm = AlarmPickerView(self)`
  - 连接关系：
    - `inline_add_view.req_open_alarm_picker -> go_to_alarm_picker(...)`
    - `page_alarm.confirm_requested -> on_alarm_confirmed(...)`
    - `page_alarm.back_requested -> back_from_alarm_picker()`
  - 视图切换方式：
    - 仅在月界面左侧区域内部 `hide/show`
    - 不接 `MainWindow.body_stack`
    - 不修改主界面 / 周界面提醒 picker 链路

- ListPickerView 接入结果：
  - 在 `MonthWindow` 内新增：
    - `self.page_list = ListPickerView(self)`
  - 连接关系：
    - `inline_add_view.req_open_list_picker -> go_to_list_picker(...)`
    - `page_list.confirm_requested -> on_list_confirmed(...)`
    - `page_list.back_requested -> back_from_list_picker()`
  - 打开方式：
    - 强制 `list_type="schedule"`
    - 不修改 `ListPickerView` 组件本身
    - 不修改其既有新增/删除清单 UI 能力

- `btn_close / btn_suspend` 实例级处理：
  - `page_alarm.btn_suspend.hide()`
  - `page_list.btn_suspend.hide()`
  - `page_alarm.btn_close` 断开原行为后，重连到 `back_from_alarm_picker()`
  - `page_list.btn_close` 断开原行为后，重连到 `back_from_list_picker()`
  - 范围仅限月界面实例，不修改 `alarm_picker.py` / `list_picker.py`

- `btn_alarm` 依赖已选时间的策略：
  - `InlineAddViewMonth.btn_alarm` 改为触发 `_emit_alarm_request()`
  - 目标时间优先级：
    - `selected_start_time`
    - 否则 `selected_end_time`
  - 若两者都为空：
    - 不打开提醒 picker
    - 只 toast：`⚠️ 请先设置计划时间`

- `btn_list` 打开策略：
  - `InlineAddViewMonth.btn_list` 触发：
    - `req_open_list_picker.emit(self.selected_list_id, "schedule")`
  - 月界面接收后固定：
    - `page_list.load_data(current_category_id, list_type="schedule")`

- picker 打开前的月界面清理动作：
  - `go_to_alarm_picker(...)` 前执行：
    - `_hide_hover_preview()`
    - `close_day_panels()`
  - `go_to_list_picker(...)` 前执行：
    - `_hide_hover_preview()`
    - `close_day_panels()`
  - 与 `M-3 / M-4` 保持一致，避免 hover / 持久 panel 干扰 picker

- `on_alarm_confirmed(...)` 回填结果：
  - 回填到 `InlineAddViewMonth`：
    - `selected_reminder`
    - `selected_is_alarm_mode`
    - `selected_alarm_duration`
  - 使用既有接口：
    - `set_alarm_data(remind_dt, is_alarm_mode, alarm_duration)`
  - 回填后返回表单页，不停留在提醒 picker

- `on_list_confirmed(...)` 回填结果：
  - 不修改 `ListPickerView.confirm_requested` 签名，仍只接收 `category_id`
  - 月界面内部只读查询：
    - `db_manager.get_category(category_id)`
  - 回填到 `InlineAddViewMonth`：
    - `selected_list_id`
    - `selected_list_name`
  - 使用既有接口：
    - `set_list_data(category_id, category_name)`

- `_on_save(...)` 提醒 / 清单字段策略：
  - 在既有最小 `schedule` 保存结构上新增：
    - `reminder_time`
    - `is_alarm`
    - `alarm_duration`
    - `category_id`
  - 仍保持：
    - `item_type = "schedule"`
    - `priority = 0`
    - `repeat_rule = "none"`
  - 明确未接入：
    - `combo_priority`
    - `combo_repeat`

- 未修改项确认：
  - 未修改 `src/ui/alarm_picker.py`
  - 未修改 `src/ui/list_picker.py`
  - 未修改 `src/ui/main_window.py`
  - 未修改 `src/ui/week_window.py`
  - 未修改 `src/ui/add_view.py`
  - 未修改 `src/ui/add_view_week.py`
  - 未修改 `src/ui/common`
  - 未修改 `src/ui/popups`
  - 未修改 `src/ui/utils`
  - 未修改 `src/controllers`
  - 未修改 `src/data`
  - 未修改 `src/repositories`
  - 未修改 `src/services`
  - 未修改 `src/theme`
  - 未修改 `src/utils/signals.py`
  - 未修改 `src/utils/styles.py`
  - 未修改 `assets`
  - 未修改 `main.py`
  - 未修改 `requirements.txt`

- 验证结果：
  - import 验证：
    - `MonthWindow`
    - `InlineAddViewMonth`
    - `AlarmPickerView`
    - `ListPickerView`
    - 通过
  - offscreen 构造验证：
    - `MonthWindow()` 可构造
    - `page_alarm` / `page_list` 存在
    - 通过
  - `btn_alarm` 无时间阻断验证：
    - 点击后 `page_alarm.isVisible() == False`
    - 通过
  - `btn_alarm` 有时间打开验证：
    - 点击后 `page_alarm.isVisible() == True`
    - `page_alarm.target_time` 与目标结束时间一致
    - 通过
  - `on_alarm_confirmed(...)` 回填验证：
    - `selected_reminder`
    - `selected_is_alarm_mode`
    - `selected_alarm_duration`
    - 通过
  - `btn_list` 打开验证：
    - `page_list.isVisible() == True`
    - `page_list.current_list_type == "schedule"`
    - 通过
  - `on_list_confirmed(...)` 回填验证：
    - 使用现有真实 `schedule` 清单 id 只读验证
    - `selected_list_id` 正确回填
    - `selected_list_name` 正确回填
    - 通过
  - 内嵌关闭按钮回归：
    - `page_alarm.btn_close.click()` 后：
      - `page_alarm` 隐藏
      - `inline_add_view` 恢复显示
      - `MonthWindow` 保持可见
    - `page_list.btn_close.click()` 后：
      - `page_list` 隐藏
      - `inline_add_view` 恢复显示
      - `MonthWindow` 保持可见
    - 断言与打印输出均通过
    - 但含 `MonthWindow.show()` 的该条 offscreen 命令在 Qt 退场阶段返回非零码，记录为环境级退场现象，不认定为功能失败
  - `_on_save(...)` 扩展范围检查：
    - 已确认仅新增提醒 / 清单字段
    - 已确认未接入 `combo_priority / combo_repeat`
    - 通过
  - `py_compile`：
    - `src/ui/month_window.py`
    - `src/ui/alarm_picker.py`
    - `src/ui/list_picker.py`
    - `main.py`
    - 通过
  - `schedule.db` tracked diff：
    - 无输出
    - 通过

- 禁止范围检查结果：
  - 以下均无 diff：
    - `src/ui/main_window.py`
    - `src/ui/week_window.py`
    - `src/ui/add_view.py`
    - `src/ui/add_view_week.py`
    - `src/ui/time_picker.py`
    - `src/ui/time_picker_week.py`
    - `src/ui/alarm_picker.py`
    - `src/ui/list_picker.py`
    - `src/ui/calendar_pop.py`
    - `src/ui/common`
    - `src/ui/popups`
    - `src/ui/utils`
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

- 最终 diff 范围：
  - `src/ui/month_window.py`
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`
  - 说明：
    - `manage_instruction/Work_Task_Prompts.md` 为开工前既有 diff，本轮未修改

- 未完成事项：
  - 未接入 `combo_priority` 保存，留待 `M-5f`
  - 未接入 `combo_repeat` 保存，留待 `M-5f`
  - 未扩展月界面 todo 支持
  - 未处理右键菜单

- 风险或疑点：
  - `AlarmPickerView` 与 `ListPickerView` 原本设计为独立页面组件，当前采用月界面内部实例级最小接管；链路验证已通过，但左侧窄栏下的最终视觉密度仍需顾问窗口实机复核。
  - `ListPickerView` 自带新增/删除清单 UI，本轮未改组件；当前执行范围只验证读取已有清单与回填，不通过验证链路创建/删除真实清单，避免污染数据库。
  - 含 `MonthWindow.show()` 的个别 offscreen 命令在 Qt 退场阶段仍可能出现非零退出码；当前打印与断言均已证明功能链路通过，记录为环境级退场现象，而非功能阻断。

- 顾问窗口复核补充：
  - 对照 `Work_Task_Prompts.md` 与本轮执行日志复核，通过。
  - 修正说明：本轮源码修改前，M-5e 提示词与日志已存在管理文档 diff；`src/ui/month_window.py` 不应记录为“开工前既有 diff”，而是本轮源码修改产物。
  - 复跑 import 验证：通过。
  - 复跑 offscreen 构造验证：通过。
  - 复跑无时间提醒阻断验证：通过。
  - 复跑有时间提醒 picker 打开验证：通过；首次标准命令无输出非零，使用 `-u` / flush 等价命令复跑后断言通过，归类为 Qt offscreen 输出/退场现象。
  - 复跑提醒确认回填验证：通过。
  - 复跑清单 picker 打开验证：通过，`current_list_type == "schedule"`。
  - 复跑清单确认回填验证：通过，使用已有 schedule 清单只读回填，未创建/删除清单。
  - 复跑内嵌关闭按钮验证：打印与断言显示 alarm/list 返回后均恢复 `inline_add_view` 且 `MonthWindow` 未隐藏；命令退场码为 1，归类为已知 Qt offscreen 退场现象。
  - 复跑 `_on_save(...)` 字段隔离检查：通过，仅接入 reminder/list 字段，未接 `combo_priority` / `combo_repeat`。
  - 复跑 `py_compile`：通过。
  - 复跑 `main import`：通过。
  - 复跑 `schedule.db` tracked diff：无输出。
  - 复跑禁止范围检查：无输出。
  - `Work_Task_Prompts.md` 已更新为 M-5e 复核锚点，下一步候选为 M-5f，并保留 M-5e 已执行提示词全文供对照。

## M-5f 最终提示词写入

- 时间：2026-06-03

- 任务：
  - 审核决策窗口提供的 `M-5f（月界面紧急性 / 重复规则 / 保存结构对齐）` 提示词，并写入最终执行版。

- 实际修改文件：
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`

- 审核结论：
  - 原方向可采纳：M-5f 应只对齐月界面 `priority / repeat_rule / schedule_data` 保存结构，不接右键菜单，不进入 M-5g。
  - 原稿中“非重复临时保存后删除”的验收方式存在污染本地 SQLite 文件的风险，即使删除记录也可能导致 `schedule.db` 文件内容变化。

- 本次修订重点：
  - 将真实写库验收改为 mock / monkeypatch 截获 `db_manager.add_schedule(schedule_data)` 入参。
  - 明确本轮不得真实写入 `schedule.db`，不得真实保存或删除临时日程。
  - 明确 `none` 是历史兼容值 / 数据库默认值之一，不得误删或改动服务层兼容规则。
  - 明确月界面 UI 保存值对齐主界面：`combo_priority.currentIndex()` 与 `combo_repeat.currentText().strip()`。
  - 明确月界面 `combo_priority` 应从 `无/低/中/高` 收口为 `低/中/高`。
  - 保留 `combo_repeat` 为 `无/每天/每周/每月`，不新增 `每年/yearly` 或 English repeat rule。
  - 增加 `src/data/database.py` 读取与静态定位，用于确认数据库层对非重复值的兼容逻辑。

- 范围说明：
  - 本次只写执行提示词和日志。
  - 不修改源码。
  - 不进入 M-5f 源码执行。

- 下一步候选：
  - 执行窗口按 `Work_Task_Prompts.md` 执行 M-5f。

## M-5f：月界面紧急性 / 重复规则 / 保存结构对齐

- 时间：2026-06-03

- 任务名称：
  - `M-5f（月界面紧急性 / 重复规则 / 保存结构对齐）`

- 开工前 git 状态：
  - `## main...temp/main [ahead 66]`
  - `M manage_instruction/Work_Log.md`
  - `M manage_instruction/Work_Task_Prompts.md`
  - `M src/ui/month_window.py`
  - 说明：
    - `src/ui/month_window.py` 为 `M-1 ~ M-5e` 连续月界面改造延续。
    - `manage_instruction/Work_Task_Prompts.md` 为开工前既有 diff，本轮未修改。

- 实际修改文件：
  - `src/ui/month_window.py`
  - `manage_instruction/Work_Log.md`

- 是否存在开工前既有 diff：
  - 否。
  - M-5f 提示词已在前置管理文档提交中落盘后再执行源码修改。
  - `src/ui/month_window.py` 为本轮源码修改产物。
  - `manage_instruction/Work_Task_Prompts.md` 本轮执行后更新为复核锚点。

- 主界面 priority 保存基线：
  - `src/ui/add_view.py::_on_save(...)`
  - 使用：
    - `priority = self.combo_priority.currentIndex()`

- 主界面 repeat_rule 保存基线：
  - `src/ui/add_view.py::_on_save(...)`
  - 使用：
    - `repeat_text = self.combo_repeat.currentText().strip()`
    - `schedule_data['repeat_rule'] = repeat_text`

- 周界面 priority / repeat_rule 保存基线：
  - `src/ui/add_view_week.py::_on_save(...)`
  - 使用：
    - `priority = self.combo_priority.currentIndex()`
    - `repeat_text = self.combo_repeat.currentText().strip()`

- `ScheduleRepeatService` 重复规则基线：
  - `NON_REPEAT_RULES = ("none", "无", "不重复", "")`
  - `REPEAT_COUNTS = {"每天": 365, "每周": 52, "每月": 12}`
  - 只明确支持：
    - `每天`
    - `每周`
    - `每月`
  - 未支持：
    - `每年`
    - `daily / weekly / monthly / yearly`

- 数据层非重复兼容基线：
  - `src/data/database.py::add_schedule(...)`
  - 非重复分支兼容：
    - `none`
    - `无`
    - `不重复`
    - 空字符串
  - 本轮未修改该兼容逻辑

- 月界面 `combo_priority` 修正结果：
  - 已从：
    - `["无", "低", "中", "高"]`
  - 改为：
    - `["低", "中", "高"]`
  - 结果语义：
    - index 0 = 低
    - index 1 = 中
    - index 2 = 高
  - `reset_form(...)` 仍执行：
    - `combo_priority.setCurrentIndex(0)`

- 月界面 `combo_repeat` 确认结果：
  - 保持：
    - `无`
    - `每天`
    - `每周`
    - `每月`
  - 未新增：
    - `每年`
    - `daily / weekly / monthly / yearly`

- `_on_save(...)` 保存字段对齐结果：
  - 已对齐为使用：
    - `self.combo_priority.currentIndex()`
    - `self.combo_repeat.currentText().strip()`
  - 当前月界面 `schedule_data` 包含：
    - `title`
    - `item_type = "schedule"`
    - `priority`
    - `repeat_rule`
    - `description`
    - `start_time`
    - `end_time`
    - `reminder_time`
    - `is_alarm`
    - `alarm_duration`
    - `category_id`
  - 仍保持：
    - 未设置时间不保存
    - 保存成功后仍 `saved.emit()`

- 是否未新增 todo 支持：
  - 是。
  - 月界面仍固定：
    - `item_type = "schedule"`

- 是否未新增每年 / English repeat rule：
  - 是。
  - 月界面未引入：
    - `每年`
    - `daily`
    - `weekly`
    - `monthly`
    - `yearly`

- 是否未修改重复服务 / 数据层：
  - 是。
  - 未修改：
    - `src/services/schedule_repeat_service.py`
    - `src/data/database.py`

- mock 保存结构验收结果：
  - 使用 monkeypatch 截获：
    - `db_manager.add_schedule(schedule_data)`
  - 未走真实写库
  - 截获结果通过：
    - `title == '__mock_m5f_month_save__'`
    - `item_type == 'schedule'`
    - `priority == 2`
    - `repeat_rule == '无'`
    - `description == 'mock validation only'`
    - `start_time == 目标开始时间`
    - `end_time == 目标结束时间`
    - `reminder_time == 目标提醒时间`
    - `is_alarm is True`
    - `alarm_duration == 1`
    - `category_id == 12345`
  - `saved` 信号也已触发

- 是否未真实写入 `schedule.db`：
  - 是。
  - 本轮未运行真实 `db_manager.add_schedule(...)` 保存验收。
  - 未运行 `每天 / 每周 / 每月` 的真实保存测试。

- `schedule.db` 是否无 tracked diff：
  - `git diff --name-only -- schedule.db`
  - 无输出，通过。

- 验证结果：
  - 静态定位：
    - 已确认月界面 `combo_priority` 只有 `低 / 中 / 高`
    - 已确认月界面 `combo_repeat` 只有 `无 / 每天 / 每周 / 每月`
    - 已确认 `_on_save(...)` 使用：
      - `combo_priority.currentIndex()`
      - `combo_repeat.currentText().strip()`
  - import 验证：
    - `MonthWindow`
    - `InlineAddViewMonth`
    - 通过
  - offscreen 控件语义验证：
    - `priorities == ['低', '中', '高']`
    - `repeats == ['无', '每天', '每周', '每月']`
    - 通过
  - reset 默认值验证：
    - `combo_priority.currentIndex() == 0`
    - `combo_priority.currentText().strip() == '低'`
    - `combo_repeat.currentIndex() == 0`
    - `combo_repeat.currentText().strip() == '无'`
    - 通过
  - `_on_save(...)` 字段表达式检查：
    - 通过
    - 原始一条 Python 断言命令受 Windows / PowerShell 引号组合影响触发 `SyntaxError`
    - 已用等价断言命令复跑通过，不属于功能失败
  - mock 保存结构验收：
    - 通过
  - 重复选项静态确认：
    - `['无', '每天', '每周', '每月']`
    - 通过
  - `py_compile`：
    - `src/ui/month_window.py`
    - `main.py`
    - 通过

- 禁止范围检查结果：
  - 以下均无 diff：
    - `src/ui/main_window.py`
    - `src/ui/week_window.py`
    - `src/ui/add_view.py`
    - `src/ui/add_view_week.py`
    - `src/ui/time_picker.py`
    - `src/ui/time_picker_week.py`
    - `src/ui/alarm_picker.py`
    - `src/ui/list_picker.py`
    - `src/ui/calendar_pop.py`
    - `src/ui/common`
    - `src/ui/popups`
    - `src/ui/utils`
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

- 最终 diff 范围检查结果：
  - `git diff --check`
    - 通过
  - `git diff --name-only`
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`
    - `src/ui/month_window.py`
  - `git status --short --branch`
    - `## main...temp/main [ahead 66]`
    - `M manage_instruction/Work_Log.md`
    - `M manage_instruction/Work_Task_Prompts.md`
    - `M src/ui/month_window.py`
  - 说明：
    - `manage_instruction/Work_Task_Prompts.md` 已更新为 M-5f 复核锚点

- 未完成事项：
  - `M-5g` 再做整体验收
  - 月界面右键菜单未接入
  - 月界面 todo 支持未接入

- 风险或疑点：
  - 月界面当前 `repeat_rule` 保存已与主界面对齐，但真实重复写库仍未在本轮验证；这是刻意收口，以避免 `每天 / 每周 / 每月` 真实生成批量数据污染本地 SQLite。
  - 控制台在 `gbk` 输出下打印中文时仍可能出现乱码展示，例如 `无 -> ÎŢ`；当前断言已基于 Python 字符串真实值通过，不影响功能结论。

- 顾问窗口复核补充：
  - 对照 `Work_Task_Prompts.md` 与本轮执行日志复核，通过。
  - 修正说明：`src/ui/month_window.py` 是 M-5f 本轮源码修改，不应记录为开工前既有 diff；`Work_Task_Prompts.md` 本轮更新为 M-5f 复核锚点。
  - 复跑 import 验证：通过。
  - 复跑 offscreen 控件语义验证：通过，`combo_priority == ['低', '中', '高']`，`combo_repeat == ['无', '每天', '每周', '每月']`。
  - 复跑 reset 默认值验证：通过，priority 默认 `低`，repeat 默认 `无`；控制台中文显示乱码不影响断言。
  - 复跑 `_on_save(...)` 字段表达式检查：通过；原提示词命令在 PowerShell 引号组合下触发 `SyntaxError`，已用等价断言命令复跑。
  - 复跑 mock 保存结构验收：通过，截获 `schedule_data` 字段正确，未真实写入数据库。
  - 复跑重复选项静态确认：通过。
  - 复跑 `py_compile`：通过。
  - 复跑 `main import`：通过。
  - 复跑 `schedule.db` tracked diff：无输出。
  - 复跑禁止范围检查：无输出。

## M-5g 最终提示词写入

- 时间：2026-06-03

- 任务：
  - 审核决策窗口提供的 `M-5g（月界面添加能力整体验收）` 提示词，并写入最终执行版。

- 实际修改文件：
  - `manage_instruction/Work_Task_Prompts.md`
  - `manage_instruction/Work_Log.md`

- 审核结论：
  - 原方向可采纳：M-5g 应只做月界面添加能力整体验收和日志记录，不改源码、不真实写库、不接右键菜单。
  - 原稿中 marker / hover 验证命令有少量方法名和属性名风险，需要对齐当前 `month_window.py` 的真实接口。

- 本次修订重点：
  - 将 marker 验证统一改为当前真实方法：
    - `_build_schedule_marker_cache()`
    - `_build_hover_schedule_cache()`
    - `_refresh_schedule_marker_cache()`
  - 将缓存属性统一改为当前真实字段：
    - `schedule_marker_cache`
    - `schedule_marker_count_cache`
    - `hover_schedule_cache`
  - 保留保存结构 mock 验证，明确不得真实写入 `schedule.db`。
  - 明确 M-5g 不修改 `src/`、不新增功能、不接月界面右键菜单。
  - 明确 M-5g 通过后下一步候选为 `M-6（月界面右键菜单接入）`。

- 范围说明：
  - 本次只写执行提示词和日志。
  - 不修改源码。
  - 不进入 M-5g 执行。

- 下一步候选：
  - 执行窗口按 `Work_Task_Prompts.md` 执行 M-5g。

## M-5g：月界面添加能力整体验收

- 时间：2026-06-03

- 本轮任务名称：
  - `M-5g（月界面添加能力整体验收）`

- 开工前 git 状态：
  - `## main...temp/main [ahead 67]`
  - `M manage_instruction/Work_Log.md`
  - `M manage_instruction/Work_Task_Prompts.md`
  - 说明：
    - 本轮开工前 `src/` 已无 diff。
    - `manage_instruction/Work_Task_Prompts.md` 为开工前既有管理文档 diff，本轮未修改。

- 实际修改文件：
  - `manage_instruction/Work_Log.md`

- `M-5` 到 `M-5f` 完成结论汇总：
  - `M-5`：
    - 月界面“添加”目标日期从 `calendar.selectedDate()` 收口为 `_get_add_target_date()`。
    - 有用户主动选中日期时优先使用选中日期；无主动选中时 fallback 到 `calendar.selectedDate()`。
    - 过去日期不可添加。
  - `M-5b`：
    - 明确月界面后续承接策略应在 `month_window.py` 内部最小接管。
    - 复用主版本 picker 语义，不借 `MainWindow.body_stack`，不走周界面历史链路。
  - `M-5c`：
    - `InlineAddViewMonth` 补齐时间 / 提醒 / 清单状态字段。
    - 增加 `set_time_data / set_alarm_data / set_list_data` 与 picker 请求信号壳。
  - `M-5d`：
    - 月界面内部接入 `TimePickerView`。
    - `btn_time` 可打开时间页并回填 `selected_start_time / selected_end_time`。
    - 未设置时间时保存会被拦截。
  - `M-5e`：
    - 月界面内部接入 `AlarmPickerView / ListPickerView`。
    - `btn_alarm` 依赖已选时间。
    - `btn_list` 强制 `list_type="schedule"`。
    - 回填提醒 / 清单字段，不改 picker 源码。
  - `M-5f`：
    - `combo_priority` 收口为 `低 / 中 / 高`。
    - `combo_repeat` 保持 `无 / 每天 / 每周 / 每月`。
    - `_on_save(...)` 与主界面保存结构对齐。

- 日期来源验收结果：
  - 通过。
  - 验证结果：
    - 人工设置 `user_selected_date = QDate.currentDate().addDays(3)` 后，
      - `_get_add_target_date()` 返回该选中日期。
      - `_on_add_clicked()` 后 `inline_add_view.selected_date` 与该日期一致。
  - 说明：
    - 本轮已验证“有用户选中日期时优先使用选中日期”的链路。
    - “无用户选中日期时 fallback 正常”依据当前实现和前序 `M-5` / `M-5d` 结论确认，未单独改源码。

- 过去日期不可添加验收结果：
  - 通过。
  - 验证结果：
    - `user_selected_date = QDate.currentDate().addDays(-1)` 时，
    - `_on_add_clicked()` 后 `inline_add_view.isVisible() == False`。

- 时间 picker 验收结果：
  - 通过。
  - 验证结果：
    - `on_time_confirmed(start, end)` 后，
      - `selected_start_time == start`
      - `selected_end_time == end`
    - `InlineAddViewMonth` 可正确承接时间回填。

- 提醒 picker 验收结果：
  - 通过。
  - 验证结果：
    - `on_alarm_confirmed(remind, True, 1)` 后，
      - `selected_reminder == remind`
      - `selected_is_alarm_mode is True`
      - `selected_alarm_duration == 1`
  - 结合前序 `M-5e` 结论：
    - 未设置时间时 `btn_alarm` 不打开提醒 picker。
    - 有时间时可打开月内 `AlarmPickerView`。

- 清单 picker 验收结果：
  - 通过。
  - 验证结果：
    - `on_list_confirmed(None)` 后，
      - `selected_list_id is None`
    - 前序 `M-5e` 已验证：
      - `btn_list` 可打开月内 `ListPickerView`
      - `current_list_type == "schedule"`
      - 可只读回填已有 `schedule` 清单 id / 名称

- 未设置时间保存拦截结果：
  - 通过。
  - 验证结果：
    - 仅设置标题、不设置时间时执行 `_on_save()`，
    - `saved` 信号未触发。

- 完整保存结构 mock 验收结果：
  - 通过。
  - 使用 monkeypatch 截获：
    - `db_manager.add_schedule(schedule_data)`
  - 未真实写入数据库。
  - 截获字段确认：
    - `title == '__mock_m5g_month_full_save__'`
    - `item_type == 'schedule'`
    - `priority == 2`
    - `repeat_rule == '无'`
    - `description == 'mock validation only'`
    - `start_time == start`
    - `end_time == end`
    - `reminder_time == remind`
    - `is_alarm is True`
    - `alarm_duration == 1`
    - `category_id == 12345`
  - `saved` 信号已触发。
  - 说明：
    - 控制台在 `gbk` 环境下打印中文时，`'无'` 可能显示为乱码 `ÎŢ`，但 Python 断言已基于真实字符串值通过，不影响结论。

- 重复规则是否仅做静态验证：
  - 是。
  - 本轮只确认选项存在：
    - `['无', '每天', '每周', '每月']`
  - 未真实保存：
    - `每天`
    - `每周`
    - `每月`
  - 原因：
    - 避免触发批量重复写库。

- marker cache 链路验收结果：
  - 通过。
  - 验证结果：
    - `_build_schedule_marker_cache()` 可调用。
    - 返回：
      - `marker_cache` 为 `dict`
      - `marker_count_cache` 为 `dict`

- hover cache 链路验收结果：
  - 通过。
  - 验证结果：
    - `_build_hover_schedule_cache()` 可调用。
    - 返回 `hover_cache` 为 `dict`。
    - `_refresh_schedule_marker_cache()` 调用后：
      - `schedule_marker_cache` 为 `dict`
      - `schedule_marker_count_cache` 为 `dict`
      - `hover_schedule_cache` 为 `dict`

- 持久 panel 关闭链路验收结果：
  - 通过。
  - 验证结果：
    - `close_day_panels()` 可调用且不报错。

- `_on_schedule_saved(...)` 刷新入口验收结果：
  - 通过。
  - 验证结果：
    - `MonthWindow()._on_schedule_saved()` 可调用。
    - 不报错。
  - 说明：
    - 本轮不做真实保存，只验证刷新入口可调用。

- 主界面 / 周界面添加页回归检查结果：
  - 通过。
  - `py_compile` 已通过：
    - `src/ui/add_view.py`
    - `src/ui/add_view_week.py`
    - `src/ui/main_window.py`
    - `src/ui/week_window.py`
  - import 验证通过：
    - `MonthWindow`
    - `InlineAddViewMonth`
    - `AddScheduleView`
    - `AddScheduleViewWeek`

- 是否未真实写入重复日程：
  - 是。
  - 本轮未真实保存 `每天 / 每周 / 每月`。

- 是否未新增 / 删除清单：
  - 是。
  - 本轮未通过 UI 或数据库创建 / 删除真实清单。

- `schedule.db` 是否无 tracked diff：
  - `git diff --name-only -- schedule.db`
  - 无输出，通过。

- 验证命令与结果摘要：
  - `rg -n ... src/ui/month_window.py`
    - 月界面添加链路相关方法、缓存字段、panel 链路均存在。
  - import 验证：
    - `month/main/week add imports ok`
  - offscreen 构造：
    - `month created True`
    - `has inline True`
    - `has page_time True`
    - `has page_alarm True`
    - `has page_list True`
  - 日期来源验证：
    - `target date 2026-06-06`
    - `inline selected 2026-06-06`
  - 过去日期验证：
    - `past add visible after False`
  - 时间 / 提醒 / 清单回调：
    - `time/alarm/list callbacks ok`
  - 未设时间保存拦截：
    - `saved calls []`
  - mock 保存结构：
    - `captured {...}`
    - 断言通过
  - 重复选项静态确认：
    - `repeat options ['无', '每天', '每周', '每月']`
  - marker / hover / panel：
    - `marker cache types dict dict`
    - `hover cache type dict`
    - `marker/hover/panel smoke ok`
  - 保存成功刷新入口：
    - `schedule saved refresh callable ok`
  - 主界面 / 周界面回归：
    - `py_compile` 通过

- diff 范围检查结果：
  - `git diff --name-only -- src`
    - 无输出
  - `git diff --name-only -- assets`
    - 无输出
  - `git diff --name-only -- main.py`
    - 无输出
  - `git diff --name-only -- requirements.txt`
    - 无输出
  - `git diff --check`
    - 仅管理文档 CRLF 警告，无源码 diff
  - `git diff --name-only`
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`
  - `git status --short --branch`
    - `## main...temp/main [ahead 67]`
    - `M manage_instruction/Work_Log.md`
    - `M manage_instruction/Work_Task_Prompts.md`
  - 说明：
    - `manage_instruction/Work_Task_Prompts.md` 为开工前既有 diff，本轮未修改

- 未完成事项：
  - `M-6（月界面右键菜单接入）` 尚未执行
  - 月界面 todo 支持仍未进入范围

- 风险或疑点：
  - `M-5g` 只做了 mock 保存结构验收，没有做真实写库；这是刻意约束，用于避免本地 SQLite 被重复规则测试污染。
  - 控制台 `gbk` 输出对中文仍可能出现乱码展示，但当前所有关键字段断言均已通过，不影响本轮结论。

- 是否建议进入 `M-6（月界面右键菜单接入）`：
  - 建议可以进入。
  - 前提：
    - 继续保持“不改已有保存链路、不真实写库”的小步策略。

- 特别记录：
  - 本轮只做整体验收。
  - 本轮不改源码。
  - 本轮不真实写库。
  - 本轮不接右键菜单。

### 主窗口复核补充

- 时间：2026-06-03

- 复核方式：
  - 对照 `Work_Task_Prompts.md` 的 M-5g 提示词与本日志执行记录。
  - 复跑关键 Python smoke、mock 保存、缓存刷新和 diff 范围检查。

- 提示词与日志对照结论：
  - 执行窗口记录覆盖了 M-5g 要求的日期来源、过去日期拦截、time/alarm/list picker 回调、未设时间保存拦截、mock 保存结构、repeat 选项、marker/hover/panel、保存后刷新入口、py_compile 和 diff 范围。
  - 未发现执行范围扩大到源码修改、真实写库、月界面右键菜单或 todo 支持。

- 主窗口复跑结果：
  - import 验证通过：
    - `MonthWindow`
    - `InlineAddViewMonth`
    - `AddScheduleView`
    - `AddScheduleViewWeek`
  - offscreen `MonthWindow` 构造通过：
    - `inline_add_view`
    - `page_time`
    - `page_alarm`
    - `page_list`
  - 添加日期来源验证通过：
    - 用户选中 `2026-06-06` 后，添加表单 `selected_date` 为 `2026-06-06`。
  - 过去日期拦截验证通过：
    - 过去日期触发添加后，`inline_add_view.isVisible()` 为 `False`。
  - time / alarm / list 回调验证通过：
    - `selected_start_time`
    - `selected_end_time`
    - `selected_reminder`
    - `selected_is_alarm_mode`
    - `selected_alarm_duration`
    - `selected_list_id`
    - `selected_list_name`
  - 未设置时间保存拦截验证通过：
    - mock `add_schedule` 未被调用。
  - mock 完整保存结构验证通过：
    - `item_type == "schedule"`
    - `priority == 2`
    - `repeat_rule == "无"`
    - `reminder_time`
    - `is_alarm`
    - `alarm_duration`
    - `category_id`
  - repeat 选项静态验证通过：
    - `['无', '每天', '每周', '每月']`
  - marker / hover / panel smoke 通过：
    - `_build_schedule_marker_cache()`
    - `_build_hover_schedule_cache()`
    - `_refresh_schedule_marker_cache()`
    - `close_day_panels()`
  - 保存后刷新入口验证通过：
    - `_on_schedule_saved()` 可调用。
  - 语法检查通过：
    - `src/ui/add_view.py`
    - `src/ui/add_view_week.py`
    - `src/ui/main_window.py`
    - `src/ui/week_window.py`
    - `src/ui/month_window.py`
    - `main.py`

- 编码说明：
  - Windows 控制台中 mock 保存结构曾将中文 `无` 显示为乱码，但 Python 断言通过，实际字段值为 `无`，不影响结论。

- 主窗口 diff 复核：
  - `git diff --name-only -- src` 无输出。
  - `git diff --name-only -- schedule.db` 无输出。
  - 当前 diff 仅为管理文档：
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`

- 复核结论：
  - M-5g 通过。
  - 月界面添加能力阶段可以进入 `M-6（月界面右键菜单接入）`。
  - 继续保持小步策略：M-6 只接右键菜单，不改 M-5 保存链路，不做真实数据库测试。
