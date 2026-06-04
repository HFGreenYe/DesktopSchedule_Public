# History Log

用途：归档已经完成阶段的执行日志和验收记录。

本文件只存历史日志，不作为当前执行窗口的实时日志。当前阶段实时日志见：

- `Work_Log.md`

---

## 归档规则

- 每个阶段完成后，由主窗口把 `Work_Log.md` 中的阶段记录迁入本文件。
- 归档条目应保留：
  - 阶段名称
  - 时间范围
  - 实际修改文件
  - 验收命令和结果
  - 未完成事项
  - 风险或疑点
- 旧架构改写阶段的完整日志已移入 `ReconstructionDolder/`。

---

## 当前归档索引

### 2026-06-01：右键上下文菜单阶段归档

阶段范围：

- `CM-0` 到 `CM-4`。
- 起点：右键菜单现状审查与精确边界。
- 终点：右键上下文菜单整体验收与归档准备。

实际修改文件摘要：

- `src/ui/common/action_context_menu.py`
- `src/ui/dashboard.py`
- `src/ui/main_window.py`
- `src/ui/week_window.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

完成内容：

- 新增 `ActionContextMenu` 公共菜单组件。
- 主菜单包含：
  - 换肤
  - 视图
  - 添加
  - 排序
  - 筛选
- 视图子菜单包含：
  - 日视图
  - 周视图
  - 月视图
  - 四象限视图
  - 待办
- `add` 通过 `action_requested("add")` 发出。
- `day/week/month/todo` 通过 `view_requested(view_id)` 发出。
- `skin/sort/filter/priority` 保持禁用。
- 主界面 `DashboardView.lbl_empty` 和 `DashboardView.scroll_content` 接入页面级右键菜单。
- 主界面右键添加复用 `MainWindow.switch_to_add_page()`。
- 主界面右键视图切换复用 `MainWindow.switch_view(...)`。
- 周界面 `WeekWindow.bottom_panels` 空白区接入页面级右键菜单。
- 周界面右键日期映射使用 `bottom_panels.index(obj)` + `current_monday.addDays(index)`。
- 周界面右键添加复用 `WeekWindow.switch_to_add_page()`。
- 周界面右键视图切换复用 `_on_view_selected(...)` / `view_selected` 既有链路。

验收结果：

- `ActionContextMenu` import、offscreen 构造和信号验证通过。
- 主界面 `DashboardView` context 信号验证通过。
- `MainWindow` dashboard context bridge 验证通过。
- 周界面 `WeekWindow` context bridge 验证通过。
- 周界面日期映射验证通过。
- 周界面添加日期路径验证通过。
- `py_compile` 通过：
  - `src/ui/common/action_context_menu.py`
  - `src/ui/dashboard.py`
  - `src/ui/main_window.py`
  - `src/ui/week_window.py`
- `src`、`assets`、`main.py`、`requirements.txt`、`schedule.db` 在 CM-4 验收阶段均无 diff。

风险和后续事项：

- 真实桌面环境下仍建议人工点测菜单焦点、右键命中和复杂鼠标轨迹。
- 换肤、排序、筛选、四象限仍是后续功能，不属于本阶段完成内容。
- 后续功能补充建议回到月界面功能补齐路线。

---

### 2026-06-04：月界面功能补齐阶段归档

阶段范围：

- `M-0` 到 `M-7`，包含 `M-5b` 到 `M-5g` 的月界面添加能力补齐子阶段。
- 起点：月界面现状审查与交互边界定位。
- 终点：月界面功能补齐整体验收。

实际修改文件摘要：

- `src/ui/month_window.py`
- `src/ui/popups/month_day_panel.py`
- `manage_instruction/Final_Formulation.md`
- `manage_instruction/Work_Formulation.md`
- `manage_instruction/Work_Instruction.md`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

完成内容：

- 月格状态 marker / 数量角标接入。
- 今天日期数字改为金色显示。
- 日期格单击改为用户选中，双击 / activated 跳转日视图。
- hover 只读预览弹窗接入。
- 单击日期持久 panel 壳接入，并支持关闭和集中清理。
- 持久 panel 屏幕边界回退逻辑接入。
- 添加按钮改为优先使用用户选中日期，过去日期不可添加。
- 月界面添加表单壳接入。
- 月界面 time picker 接入。
- 月界面 alarm / list picker 接入。
- 月界面保存结构对齐：
  - `item_type == "schedule"`
  - `priority`
  - `repeat_rule`
  - `reminder_time`
  - `is_alarm`
  - `alarm_duration`
  - `category_id`
- 月界面右键菜单接入：
  - 复用 `ActionContextMenu`
  - 右键日期作为 `context_menu_date`
  - 添加使用右键日期且不改变 `user_selected_date`
  - 日视图跳转关闭持久 panel 并发出 `date_selected(context_date)`
  - 周视图 / 待办发出视图切换
  - 月视图 / 四象限无动作

验收结果：

- `M-7` 整体验收通过。
- 功能链路静态定位通过。
- 视觉状态静态定位通过。
- import 验证通过：
  - `MonthWindow`
  - `InlineAddViewMonth`
  - `ActionContextMenu`
  - `AddScheduleView`
  - `AddScheduleViewWeek`
- offscreen 构造与缓存 smoke 通过：
  - marker cache
  - marker count cache
  - hover cache
  - `_on_schedule_saved()`
- 添加链路回归通过：
  - `user_selected_date` 优先
  - 过去日期不可添加
  - 未设置时间保存拦截
  - mock 保存结构断言通过
- 右键菜单回归通过：
  - 右键添加不改变 `user_selected_date`
  - 右键添加使用 `context_menu_date`
  - 过去日期右键添加拦截
  - `day` 关闭持久 panel 并 emit `date_selected(context_date)`
  - `week / todo` 正常发出视图切换
  - `month / priority` 无动作
- 主界面 / 周界面回归通过：
  - `py_compile` 通过：
    - `src/ui/dashboard.py`
    - `src/ui/week_window.py`
    - `src/ui/main_window.py`
    - `src/ui/add_view.py`
    - `src/ui/add_view_week.py`
    - `src/ui/month_window.py`
    - `main.py`
  - `main import ok` 通过。
- `schedule.db` 无 tracked diff。
- `src`、`assets`、`main.py`、`requirements.txt` 在 M-7 验收阶段均无 diff。

风险和后续事项：

- 本阶段没有做像素级 UI 适配；用户已确认界面适配问题后续另开阶段处理。
- 本阶段没有真实写库自动化验收，保存结构通过 mock / monkeypatch 验证；真实桌面使用仍需要人工点测。
- marker / hover / panel / inline add 都集中在 `month_window.py`，后续若继续扩展，应优先规划 UI 适配和局部拆分，而不是继续堆主文件。
- 换肤、排序、筛选、四象限仍未实现。
- 月界面右键 `week` 动作只切换周视图，不携带指定日期上下文，保持既有主路由边界。
- Windows 控制台可能出现中文编码显示问题；验收以 Python 断言和实际行为为准。
