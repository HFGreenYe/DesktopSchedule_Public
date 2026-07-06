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

---

### 2026-06-13 至 2026-06-17：功能补充与 UI 细修阶段归档

阶段范围：

- 坐标显示入口调整。
- 待办看板文字截断与紧凑视图状态修正。
- 添加表单“紧急性”语义调整为“重要性”。
- 右键菜单视图子菜单图标替换。
- 天气服务失败兜底与 loading 过渡。
- 月界面日期弹窗 toggle 与标题色细节。
- 日界面详情输入框视觉与滚动条调整。
- 更多菜单“使用帮助”入口与分隔线一致性修正。
- 日程显示“卡片模式 / 课表模式”规划与更多菜单入口壳。

实际修改文件摘要：

- `src/ui/components.py`
- `src/ui/common/action_context_menu.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- `src/ui/month_window.py`
- `src/ui/popups/month_day_hover_preview.py`
- `src/ui/popups/month_day_panel.py`
- `src/ui/todo_board.py`
- `src/ui/dashboard.py`
- `src/ui/main_window.py`
- `src/ui/todo.py`
- `assets/icons/axis.svg`
- `assets/icons/help.svg`
- `assets/icons/user_manual.svg`
- `assets/icons/assistant.svg`
- `assets/icons/hourglass.svg`
- `assets/icons/question-mark.svg`
- `assets/icons/weather-question.svg`
- `assets/icons/interface-day.svg`
- `assets/icons/interface-week.svg`
- `assets/icons/interface-month.svg`
- `assets/icons/model_switch.svg`
- `assets/icons/schedule_card.svg`
- `assets/icons/timetable.svg`
- `manage_instruction/Final_Formulation.md`
- `manage_instruction/Work_Log.md`

完成内容：

- 从视图选择入口移除“四象限 / 象限”显示文案，改为后续“坐标显示”方向。
- 右上角更多菜单新增“坐标显示”占位入口。
- 待办看板便签标题修复：
  - pin 图标保持左上角固定。
  - 长标题先换行，再按需缩小字号。
  - 文件夹视图长标题限制在卡片内部，避免撑出界面。
- 主界面和待办界面的紧凑视图拓展框增加当前视图文字状态：
  - 当前视图为白色。
  - 非当前视图为浅灰色。
- 日 / 周 / 月添加表单语义从“紧急性”调整为“重要性”。
- 月界面添加表单的重要性选项改为 `高 / 中 / 低`，重复选项改为 `无 / 日 / 周 / 月`。
- 月界面下方状态文本去除三个小背景框，仅保留外层大框。
- 右键菜单视图子菜单替换为 `interface-day.svg`、`interface-week.svg`、`interface-month.svg`。
- 天气服务增加失败兜底：
  - 空响应、非 JSON、网络异常不再只打印错误。
  - loading 阶段使用沙漏图标过渡。
  - 失败后使用问号天气图标和 `--°C`。
- 月界面日期单击持久 panel 支持同日二次点击关闭。
- 月界面 hover 预览和持久 panel 标题日期 / 周几调整为主题色方向。
- 日界面详情输入框关闭后清除详情按钮高亮。
- 日界面详情输入框隐藏横向 / 纵向滚动条，并略调背景以降低白字混入问题。
- 更多菜单新增“使用帮助”主项与二级菜单：
  - `使用手册`
  - `帮助助手`
- 更多菜单分隔线改为自绘 `QWidgetAction + QFrame`，并记录当前 Windows / PyQt6 / 高 DPI 下仍可能存在视觉观感差异。
- 更多菜单新增“模式切换”主项与二级菜单：
  - `卡片模式`
  - `课表模式`
- 模式切换二级菜单当前只做 UI 壳：
  - 默认卡片模式高亮。
  - 两项互斥高亮。
  - 点击仅更新内部占位状态并打印“功能待接入”。
  - 不驱动日 / 周 / 月真实渲染。
- “模式切换”和“使用帮助”二级菜单交互修正：
  - 悬停主项临时展开，离开主项和二级菜单区域后关闭。
  - 单击主项锁定二级菜单，鼠标移走不关闭。
  - 再次单击取消锁定。
  - 两个二级菜单互斥显示。

验收结果：

- 多轮 `py_compile` 覆盖相关文件通过，包括：
  - `src/ui/components.py`
  - `src/ui/common/action_context_menu.py`
  - `src/ui/add_view.py`
  - `src/ui/add_view_week.py`
  - `src/ui/month_window.py`
  - `src/ui/todo_board.py`
  - `src/ui/dashboard.py`
  - `src/ui/main_window.py`
  - `src/ui/todo.py`
  - `main.py`
- offscreen 验证通过：
  - `SharedMoreMenu` help 子菜单构造。
  - `SharedMoreMenu` mode 子菜单构造、默认卡片模式高亮、互斥切换。
  - mode/help 二级菜单单击锁定、再次单击解锁、互斥关闭、主菜单关闭重置状态。
  - 相关新增图标可作为 `QIcon` 加载。
  - 日界面详情框滚动条隐藏策略。
  - 日界面详情按钮关闭后清除高亮。
- `git diff --check` 仅出现 LF/CRLF 提示，无内容格式错误。

风险和后续事项：

- `坐标显示` 仍是占位入口，未实现坐标看板。
- `课表模式` 仍是占位入口，未接入真实日 / 周 / 月渲染。
- 更多菜单分隔线肉眼粗细问题仍需纳入后续“弹窗统一检查与美化”阶段，不再重复用局部 QSS 参数试错。
- 月界面单击日期持久 panel 后续仍需支持修改 / 删除日程。
- 天气 loading 动画和图标显示已做兜底，但真实网络差场景仍应人工点测。
- `Final_Formulation.md` 已同步记录：
  - 坐标显示方向。
  - 月界面可编辑持久 panel 目标。
  - 自定义重复规则。
  - 弹窗统一检查与美化。
  - 模式切换入口与后续卡片 / 课表真实渲染目标。

---

### 2026-06-18 至 2026-07-06：功能补充、月 panel 路由与坐标看板第一版归档

阶段范围：

- 月界面窄栏添加表单、清单 / 时间 / 提醒 picker 和持久 panel 的多轮 UI 修正。
- `MP-0` 到 `MP-5` 月日程持久 panel 详情、生命周期、动态编辑路由和刷新阶段。
- 坐标看板样本、架构收口、真实显示设置接线、视觉交互及持久化。
- 主题选色弹窗单窗口化、圆角和内部几何对齐、自定义颜色槽持久化。
- 日 / 周 / 月 / 挂起窗口的主题色与拖动交互细修。
- 天气看板与安全加密入口壳，以及本地数据库加密 / 多账号长期规划记录。

实际修改文件摘要：

- 数据与服务：
  - `src/data/database.py`
  - `src/repositories/category_repository.py`
  - `src/services/category_color_service.py`
  - `src/services/schedule_axis_service.py`
- 坐标看板与设置：
  - `src/ui/popups/schedule_axis_board.py`
  - `src/utils/axis_board_preferences.py`
  - `src/utils/color_preferences.py`
  - `src/ui/common/themed_color_dialog.py`
  - `src/ui/main_window.py`
  - `src/utils/signals.py`
- 月 panel 与共享详情：
  - `src/ui/month_window.py`
  - `src/ui/popups/month_day_panel.py`
  - `src/ui/popups/month_day_hover_preview.py`
  - `src/ui/schedule_detail_pop.py`
- 其他 UI：
  - `src/ui/add_view.py`
  - `src/ui/add_view_week.py`
  - `src/ui/list_picker.py`
  - `src/ui/time_picker.py`
  - `src/ui/time_picker_week.py`
  - `src/ui/week_window.py`
  - `src/ui/dashboard.py`
  - `src/ui/todo.py`
  - `src/ui/todo_board.py`
  - `src/ui/suspend_window.py`
  - `src/ui/suspend_window_week.py`
  - `src/ui/suspend_window_month.py`
  - `src/ui/popups/weather_board.py`
  - `src/ui/encryption_window.py`
  - `src/ui/utils/window_drag_controller.py`
- 配置、样式与资源：
  - `src/config.py`
  - `src/utils/styles.py`
  - `src/utils/startup_manager.py`
  - `src/utils/window_preferences.py`
  - `assets/icons/axis.svg`
  - `assets/icons/calendar.svg`
  - `assets/icons/festival.svg`
  - `assets/icons/security_lock.svg`
  - `assets/icons/set.svg`
- 管理文档：
  - `manage_instruction/Final_Formulation.md`
  - `manage_instruction/Work_Instruction.md`
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`

完成内容：

- 月日程 panel 完成紧凑列表、共享详情打开、跨视图保留、动态编辑路由和保存后多视图刷新；后续补齐无子详情时的层级恢复。
- 月界面 hover 预览完成宽度限制、长标题换行和屏幕边界回退；持久 panel 标题省略、拖动、主题边框和日程项层次继续细化。
- 坐标看板完成数据库日程投影、DDL / 时间段 marker、完成状态上下分区、重要性高度、重叠轨道、范围筛选与跨边界裁剪。
- 坐标看板完成未来 / 双向 / 过去、五档范围、线性 / 非均匀映射、拖动、缩放、resize、置顶、hover 辅助线、主题化信息弹窗和单击详情。
- 设置页完成响应式分列、实时清单同步、效果预览和真实画布接线；方向、跨度、非均匀开关、轴体 / 字体外观及清单覆盖通过独立 `QSettings` 持久化。
- 新清单创建改为从未使用的高区分度色板随机选择初始颜色，色板耗尽后继续生成不重复颜色；不批量改写既有清单。
- 主题选色弹窗完成单顶级窗口、圆角透明背景、动态中文标题、深浅主题适配、HSV / RGB / HTML 区域校准及自定义颜色槽持久化。
- 日 / 周 / 月及挂起窗口完成多项主题派生色、广域拖动和布局细修；天气看板、安全加密入口壳和加密 / 多账号长期规划已记录。

验收结果：

- `MP-0 ~ MP-5` 的结构、信号、生命周期、路由、刷新 fake / monkeypatch / offscreen smoke 和目标文件 `py_compile` 已通过，阶段日志明确结论为可归档。
- 坐标映射正反变换、方向边界、范围筛选、跨边界裁剪、marker 轨道、hover 辅助线、文字层级、resize 回退和设置真实画布接线均在对应小轮完成纯逻辑或 PyQt offscreen 验证。
- 主题选色弹窗在对应小轮完成单窗口、中文文本、圆角遮罩、控件几何和自定义颜色持久化检查；系统级屏幕拾色继续依赖真实 Windows 回归。
- 本次归档复核通过静态源码对照和 `git diff --check`；最后新增的看板设置持久化与随机清单配色因 Codex 工具额度审批限制未能再次运行项目 `.venv`，未伪称本轮运行时复验通过。

风险和后续事项：

- 坐标看板后续可增加完成日程独立开关、驻留低频定时刷新、按轨道自动扩窗和 Windows 高 DPI / 多屏持续回归；这些不阻塞第一版归档。
- `schedule_axis_board.py` 仍同时承载窗口、画布、设置 UI、预览和 resize 行为；后续扩展前应先用测试锁定映射与状态，再做拆分。
- 课程表模式、搜索 / 筛选、导出、自动化测试与 CI、真实换肤、字体设置、本地加密 / 多账号及云同步仍属于后续独立阶段。
- 安全加密窗口当前只是入口壳，不包含真实加密、密钥或迁移逻辑。
