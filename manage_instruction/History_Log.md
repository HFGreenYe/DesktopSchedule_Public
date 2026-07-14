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

---

### 2026-07-06：坐标看板归档后增强与高 DPI / 多屏回归归档

实际修改文件：

- `src/services/schedule_axis_service.py`
- `src/ui/popups/schedule_axis_board.py`
- `src/utils/axis_board_preferences.py`
- `manage_instruction/Final_Formulation.md`
- `manage_instruction/Work_Formulation.md`
- `manage_instruction/Work_Log.md`

完成内容：

- 完成日程显示开关：默认开启，可同步过滤设置预览和真实画布，状态持久化。
- 设置页布局重排：“已完成显示”与“非均匀显示”同高，数轴标题与范围标题对齐，后续清单列从轴体行开始。
- 一分钟驻留刷新：仅看板可见时运行，不重复加载清单或重写偏好。
- 轨道自动扩窗：复用真实 marker 轨道结果，`80ms` 防抖，只增高不缩小，屏幕高度封顶。
- 设置齿轮恢复 `360ms InOutCubic` 旋转；设置页空白和显示框外侧空白可拖动，按钮、画布和最外 `12px` resize 保持优先。
- 最低高度最终设为 `320px`；跨度选项不重叠，清单首列容量 4。
- 增加 `__uncategorized__` “默认”颜色行，无清单 / 未分类 marker 不再只能显示白色，颜色与透明度可持久化。
- 外框横向 resize 按新旧画布像素宽度补偿内部 zoom，保持未来、过去、双向模式的两端时间不变；滚轮继续作为主动缩放入口。
- 新增显示后基于真实 `frameGeometry()` 的二次屏幕夹紧，修复高 DPI 下 hover / 持久预览和共享详情右下角约 `4px` 越界。

验收结果：

- 项目 `.venv` 目标文件 `py_compile` 通过，`git diff --check` 无内容错误。
- 完成日程过滤、默认颜色覆盖 / 透明度、偏好规范化和旧配置兼容 smoke 通过；测试 `QSettings` 键已清理。
- 定时器显示时启动、隐藏时停止；单轨 / 八轨高度为 `79px / 238px`，16 条同时间 marker 触发窗口自动增高到 `519px`。
- 齿轮旋转中间角度、设置页实际拖动、外侧空白拖动和左边缘手动 resize smoke 通过。
- 最低 `320px` 时跨度间距 `0/1/1/1px`，清单首列容量 4。
- 外框拉宽前后双向端点保持 `-62.725h / +62.725h`；滚轮后变为 `-36.605h / +36.605h`。未来、过去、双向端点误差均低于 `1e-6`。
- Qt offscreen `1.0 / 1.5 / 2.0` 三档缩放全部通过；负坐标双屏四角 frame 夹紧和原生 resize 手动回退通过。
- 当前 Windows 实际检测为 1 块 `2048×1152` 屏幕、available `2048×1104`、DPR `1.25`；真实 Qt 平台 `WA_DontShowOnScreen` 构造、布局和 grab 渲染通过。

风险和后续事项：

- 当前无坐标看板阶段阻塞项。
- 多屏为负坐标几何模拟，真实物理双屏仍可在硬件条件具备时补人工点测。
- Qt 非原生 `QColorDialog` 的系统拾色继续由 Qt 处理 screen / DPR，本轮未自行重写抓屏坐标。
- 大型 `schedule_axis_board.py` 的拆分属于后续测试基线后的架构债，不影响当前功能归档。

---

## 2026-07-08 至 2026-07-14：课程表模式阶段归档

归档说明：以下内容迁自 `Work_Log.md`，覆盖日界面、周界面和月持久日期弹窗课程表模式从原型到收尾验证的全过程。
## 2026-07-08：日界面课表模式与相关视觉细修（追补记录）

### 本轮背景
- 本轮在用户连续验收与微调中推进，日志未逐步同步；本条为追补汇总记录。
- 当前阶段仍属于日 / 周课程表模式探索中的日界面课表模式原型与视觉交互细化。

### 实际修改文件
- `src/ui/dashboard.py`
- `src/ui/schedule_detail_pop.py`
- `src/ui/common/themed_color_dialog.py`
- `src/ui/header.py`
- `src/ui/main_window.py`
- `src/ui/month_window.py`
- `src/utils/timetable_preferences.py`（新增）
- `assets/icons/refresh.svg`（新增，用户提供）

### 已完成内容
- 日界面增加课表模式显示：卡片模式切到课表模式后隐藏原卡片区，显示课表时间网格、时间段日程块和 DDL / 单时间线段。
- 课表默认以当前小时为起点；滚轮按小时上下浏览，跨 00:00 时联动切换日期；顶部排序按钮在课表模式下切换为刷新按钮，一键回到今天当前小时。
- 课表日程块支持冲突分栏、标题和时间居中显示，超长标题 / 时间使用省略号；块内时间最终恢复为白色，完成日程标题和时间使用背景上沿色。
- 课表增加当前时间灰白虚线；完成日程显示为白底 + 背景上沿色文字，过期未完成日程显示为灰色，未完成未过期日程保留白色边框。
- 课表右键菜单限定为完成 / 撤销完成 / 删除日程；删除后清理对应课表颜色覆盖并刷新。
- 课表点击日程块或 DDL 线段打开既有日程详情弹窗；详情弹窗增加课表颜色色块，点击色块复用 `ThemedColorDialog` 修改课表显示颜色。
- 新增独立 `timetable_preferences.py`，以 `QSettings` 保存按日程 ID 的课表颜色覆盖，不与坐标看板配置混用。
- 取色弹窗样式修正：课表入口标题改为“选择某某日程颜色”，并收窄按钮样式作用范围，避免基本颜色 / 自定义颜色 / 色谱控件继承按钮边框。
- 课表显示框多轮视觉细调：右侧内容区最终内缩 `3px`，日程列间隙为 `1px`，避免右侧日程块与 2px 外框视觉重合。
- 月界面日期三角标短暂试验空心 / 斜边方案后，已恢复为原本红 / 黄 / 绿实心三角 + 白色数字；白色 / 灰色历史状态规则不变。

### 验证记录
- 多次运行 Codex bundled Python 语法检查：
  - `python -m py_compile src\ui\dashboard.py`
  - `python -m py_compile src\ui\dashboard.py src\ui\month_window.py`
  - `python -m py_compile src\ui\header.py src\ui\main_window.py src\ui\schedule_detail_pop.py src\ui\common\themed_color_dialog.py src\utils\timetable_preferences.py`
- 多次运行 `git diff --check`，结果通过。
- 项目 `.venv` 在沙箱内仍会被重定向到旧 `Python311` 启动器；本轮未伪称 `.venv` GUI 运行验证通过，改用 bundled Python 做静态语法验证。

### 当前风险与未完成
- 课表模式仍处于视觉验收阶段，尚未做完整 GUI 自动化回归。
- 当前工作区仍有未提交改动；提交前应再次运行 `git status --short --branch` 与必要的语法检查。
- 日课表模式已具备可用原型，但后续仍可能继续微调日程块间距、字体大小、当前时间线样式和月界面标记观感。

### 2026-07-08：月界面白色三角与非白数量提示试验
- 在上一提交后继续试验月界面视觉：恢复左上角三角形日程提示，但三角形底色统一改为白色，避免红黄绿底色和其他界面语义混淆。
- 当前规则：日期数字本身保留原有今日、周末、非本月颜色规则；有日程标记时显示白色三角形，灰色/红黄绿状态继续显示对应颜色的日程数量，纯白状态不显示数量数字。
- 验证：`python -m py_compile src\ui\month_window.py` 与 `git diff --check` 通过。

### 2026-07-08：月界面切换日视图路由修复
- 修复月界面视图选择器点击“日”只发送视图名、不同步月历当前日期的问题。
- 当前规则：月界面点击“日”时使用当前选中日期或日历选中日期走 `date_selected` 路由，进入日界面前关闭月日程浮层，避免浮层恢复导致看起来仍停留在月界面。

### 2026-07-08：宽屏窗口课表模式同步修复
- 修复月/周窗口更多菜单选择“课表模式”只更新菜单内部状态、没有同步到主窗口日界面的问题。
- 当前规则：月/周窗口提供 `schedule_display_mode_requested` 桥接信号，更多菜单调用窗口 `set_schedule_display_mode` 后转发给主窗口统一切换日界面的卡片/课表模式。
- 验证：项目 `.venv` 导入 `MainWindow`、`MonthWindow`、`WeekWindow` 通过；offscreen 实例化 `MonthWindow` 后调用 `set_schedule_display_mode("timetable")` 可收到 `schedule_display_mode_requested` 信号。

### 2026-07-08：月界面三角计数字号调整
- 将月界面左上角三角形内的非白状态日程数量数字从固定 6pt 改为最高 8pt 的自适应字号。
- 当前规则：单数字优先放大；`9+` 等较宽文本按字体度量自动降级，避免文字超出三角形区域。

### 2026-07-08：日课表左侧内容内缩微调
- 确认日课表日程列间隙常量为单侧 `1px`，相邻日程块之间的可见间隙实际为 `2px`。
- 新增右侧课表内容区左内缩 `1px`，使第一列日程块与左侧分隔线的距离更接近日程块之间的间隙。

### 2026-07-08：日课表列间隙统一 1px 试验
- 在上一提交后继续试验日课表视觉：将日程块横向布局从“单侧留白”改为“实际可见间隙”计算。
- 当前规则：分隔线到第一列日程块为 `1px`，相邻日程块之间也为 `1px`；列宽按 `(列数 + 1)` 个间隙扣除后平均分配。
- 后续微调：右侧内容区向右扩大 `1px`，并将同一时间点 DDL 线段也改为实际 `1px` 间隙计算，避免继续沿用旧的两侧 `2px` 留白方案。
- 再次微调：日程块横向可见间隙单独恢复为 `2px`，右侧内容区对应缩回 `1px`；DDL 线段继续保留实际 `1px` 间隙。
- 继续微调：仅将右侧内容区再次向右扩大 `1px`，不改变日程块 `2px` 间隙与 DDL `1px` 间隙逻辑。

### 2026-07-08：时间段结束时间下限调整
- 将主界面/月界面共用时间选择器与周界面时间选择器的时间段校验改为仅限制结束时间不能早于当前时间。
- 当前规则：开始时间允许早于当前时间，便于给正在进行或已开始的工作补录/延长结束时间；滚轮实时回弹也只作用于结束时间。

### 2026-07-08：日课表默认颜色持久化
- 确认日课表默认颜色此前会在启动时随机打乱调色板，未手动改色的日程可能在重启后变色。
- 当前规则：自动分配的默认颜色会按日程 `id` 写入课表偏好；后续重启优先读取已保存颜色，只有首次出现的新日程才自动分配新颜色。

### 2026-07-08：日程显示模式持久化
- 将“卡片模式/课表模式”的选择写入课表偏好，避免每次重启后回到默认卡片模式。
- 当前规则：主窗口启动时先恢复上次保存的显示模式，再刷新当天日程；在任意窗口的更多菜单中切换模式时同步保存，并更新菜单选中态与顶部排序/刷新图标。

### 2026-07-08：月界面日期点击弹窗高度调整
- 将月界面日期点击弹窗的日程列表滚动区最大高度从 `220px` 提高到 `270px`。
- 当前规则：弹窗仍最多预渲染 8 条日程，但 8 条以内时列表区可完整显示，不再截断底部日程项。
- 修正：不再只预渲染前 8 条，改为渲染当天全部日程；滚动区高度仍限制在约 8 条范围内，超过部分通过纵向滚动查看。
- 视觉调整：移除弹窗内部白色描边框，仅保留外层弹窗边界与渐变背景。

### 2026-07-09：周界面课表模式占位
- 为后续周课表模式设计先接入模式占位行为：当全局日程显示模式为课表模式时，周界面工具栏排序按钮显示为刷新图标，但暂不绑定刷新功能。
- 当前规则：周界面课表模式下底部原周日程卡片展示板切换为空白占位页；切回卡片模式时恢复原周日程展示板。
- 验证：offscreen 实例化 `WeekWindow`，调用 `apply_schedule_display_mode("timetable")` 后当前页为占位页且排序按钮图标非空；切回 `card` 后恢复周日程展示板。

### 2026-07-09：周界面课表刷新键染白
- 撤回误加到月/周右上控制按钮的 PNG 白色 mask，右上更多、同步、关闭键恢复原图标逻辑。
- 当前规则：仅周界面工具栏在课表模式下由排序切换出的 `refresh.svg` 使用白色 SVG 渲染；暂不绑定刷新功能。

### 2026-07-09：周界面课表网格与基础日程绘制
- 先提交当前已验收工作区，提交号：`2179f96`，提交信息：`完善课表模式状态与月周界面细节`。
- 新增 `WeekTimetableBoard`，替换周界面课表模式空白占位页；周课表按 7 天均分，每天显示 7 个小时格。
- 网格绘制规则：6 条纵向日期分隔线与 6 条横向小时分隔线均使用单次 `1px` 灰色填充绘制，避免左右各画 `1px` 造成视觉 `2px`。
- 每个小时格右上角显示对应整时；鼠标滚轮仅在当天 0-23 小时范围内上下移动，不切换周或日期。
- 周课表复用日课表颜色偏好和日程显示规则：时间段日程按冲突分列绘制色块，DDL / 单时间点日程绘制 `3px` 线段，自动颜色写入 `timetable_preferences`。
- 验证：`python -m py_compile src\ui\week_window.py` 通过；`.venv` offscreen 实例化 `WeekWindow` 后切换 `timetable` 页通过；离屏渲染样例确认网格、日程块和线段均可绘制。

### 2026-07-09：周课表每日独立滚动与交互补齐
- 先提交上一轮周课表基础实现，提交号：`ae00fe8`，提交信息：`实现周课表基础网格与日程绘制`。
- 周课表纵向日期分隔线统一改为单次绘制 `2px` 灰线，取消小时横向分隔线，避免粗细不一致和横线视觉干扰。
- 每一天维护独立的起始小时；鼠标在哪一列滚动，只移动该日期的 0-23 小时视窗，其他日期不受影响。
- 默认起点规则：当前周内的今天从当前整小时开始，其他日期从 `00:00` 开始；小时标记改到每个小时格左上角。
- 增加当前时间灰白虚线，仅在今天列且当前时间位于该列可见时段内显示。
- 周课表日程命中区域接入交互：悬停复用日课表的轴向信息预览，左键点击复用周窗口日程详情入口，右键复用周日程卡片菜单。
- 验证：`python -m py_compile src\ui\week_window.py` 与 `git diff --check` 通过；`.venv` offscreen 验证因额度/审批限制被拒绝，本轮未绕过执行。

### 2026-07-09：周课表视觉精简与交互增强
- 先提交上一轮"每日独立滚动与交互补齐"，提交号：`e7fd31d`，提交信息：`周课表每日独立滚动与交互补齐`。
- **移除竖分隔线**：删除 `paintEvent` 中 6 条 2px 日分隔竖线绘制循环，解决因像素取整导致的粗细不一致问题。
- **日列选中高亮**：`WeekTimetableBoard` 新增 `selected_day_index` 状态和 `day_selected` 信号；点击课表空白区域 → `mousePressEvent` 计算 `_day_index_at_x` → 设置选中列 → 绘制 `rgba(0,0,0,15)` 浅灰高亮 → 发送 `day_selected` 信号 → `WeekWindow._on_day_clicked` 同步更新顶部 DayBlock 选中状态；`_on_day_clicked` 同时反调 `set_selected_day()` 实现双向同步；`refresh_week_data` 末尾同步选中日期。
- **加深时间虚线**：`_draw_current_time_line` 中虚线颜色从 `QColor(235,238,240,215)` 改为 `QColor(120,120,120,200)`，白色背景下清晰可见。
- **删除整时标签**：移除 `paintEvent` 中每格左上角 `HH:00` 小时标注循环。
- 验证：`python -m py_compile src\ui\week_window.py` 通过。

### 2026-07-09：周课表文本标注系统与菜单修正
- **日程块文字标注**（`_draw_interval_labels` 完全重写）：
  - 顶部左对齐显示开始时间（`HH:MM`），底部左对齐显示结束时间，字体 8px。
  - 普通/过期日程文字白色 `QColor(255,255,255,235)`；已完成日程（白色背景）文字使用该日程原分配颜色 `QColor(230 alpha)`。
  - 标题智能分行算法（`_wrap_title_lines`）：逐字按 `QFontMetrics.horizontalAdvance` 计算折行。
  - 空间优先级：块高度 < 时间总高度 → 不显示任何文字；块高度仅够时间 → 只显示时间无标题；否则按可用标题行数 N 决定：
    - N=0：无标题
    - N=1 且放得下：完整显示；放不下：首字 + `...`
    - N=2 且放得下：完整 2 行；放不下：第1行正文 + 第2行 `...`
    - N=3 且放得下：完整 3 行；放不下：前2行正文 + 第3行 `...`
    - N≥4：最多 3 行正文；放不下则前2行正文 + 第3行 `...`
  - 标题区域在时间标签之间的剩余空间中垂直居中。
- **DDL 时间标签**（新增 `_draw_ddl_labels`）：线段上方 2px 处绘制灰色 `HH:MM`（`QColor(140,140,140)`，字体 8px）；检测与日程块 `_occupied_label_rects` 重叠则自动跳过；宽度 < 22px 则跳过。
- **空日程占位**：`paintEvent` 末尾根据 `_hit_regions` 计算有内容的日期集合，无日程的列居中显示灰色 `"空日程"`（`QColor(185,185,185)`，字体 11px）。
- **课表右键菜单去置顶**：`WeekWindow._show_timetable_schedule_context_menu` 改为手动构建菜单（仿日界面 `dashboard.py:_show_timetable_context_menu`），仅保留"完成/撤销完成"、"隐藏"、"删除"，移除"置顶"选项。`WeekScheduleCard` 和 `_handle_schedule_pin_change` 未修改，卡片模式右键不受影响。
- 新增辅助方法：`_text_color_for_schedule`、`_format_schedule_time_text`（返回 `(start_str, end_str)` 元组）、`_wrap_title_lines`。
- 新增导入：`QFont`、`QFontMetrics`。
- 清理：移除不再使用的 `_truncate_title` 静态方法。
- 影响范围确认：仅修改 `src/ui/week_window.py`（+336/−40 行），未触及 `WeekScheduleCard`、`bottom_panels`、拖拽逻辑、日界面、月界面。`_handle_schedule_pin_change` 方法保留供卡片模式使用。
- 验证：`python -m py_compile src\ui\week_window.py` 通过。

### 2026-07-09：选中日列白色整时标注
- 用户要求：之前删除的整时标注改为选中某天时才显示，白色字体，若与日程块重叠则跳过。
- 新增 `WeekTimetableBoard._draw_hour_labels_for_selected_day` 方法：仅当 `selected_day_index` 有效时绘制；遍历可见小时范围（`visible_start_hour` 起 `HOUR_ROWS` 格），每格左上角白色 `HH:00`（`QColor(255,255,255,210)`，9px）。
- 每个整时标签与 `_occupied_label_rects`（已收集的日程块矩形）做 `intersects` 碰撞检测，重叠则跳过不绘制。
- `paintEvent` 中在空日程占位之后调用该方法，确保标签在日程块之上但不产生重叠文字。
- 验证：`python -m py_compile src\ui\week_window.py` 通过。

### 2026-07-11：周界面暗色模式头部前景统一
- 用户要求：周界面暗色模式下，头部时间、天气、工具栏图标、搜索框边框、星期文本、日期块文本、左右切周按钮、挂起/更多/同步/关闭图标均使用与底部内容区一致的灰黑色，不再保留白色或不一致灰色；卡片模式和课表模式都要生效。
- 实现：新增 `WeekWindow._apply_week_header_foreground()` 统一入口，集中刷新头部标签、搜索框、视图选择器、SVG 工具栏图标和 PNG 窗口控制图标；`_set_toolbar_button_icon()` 同步记录当前 `sort.svg` / `refresh.svg`，确保卡片/课表模式切换后仍按当前暗色状态重染色。
- 日期块：`DayBlock.update_style()` 在暗色模式下优先使用 `#2b2b2b`，覆盖今天黄色和非今天灰色，避免日期文字与底部背景色不一致。
- 天气图标：`WeatherIconLabel` 增加当前图标路径记录和 `set_icon_color()`，暗色切换时可立即重染加载图标或天气 SVG，不必等待天气刷新。
- 影响范围：未修改周窗口 `paintEvent` 渐变背景绘制逻辑，不新增任何头部灰色遮罩；只调整前景色、边框色、图标 mask 与悬停样式。
- 验证：AST 解析通过 `src/ui/week_window.py`、`src/ui/common/week_day_block.py`、`src/ui/common/weather_icon_label.py`；`.venv` 验证 `QImage.Format_ARGB32` 与 `QPainter.CompositionMode_SourceIn` 可用。
- 追补：周界面暗色详情弹窗的详情框背景从 `#3a3a3a` 改为 `#2b2b2b`，与下方信息区底色保持一致；该规则仅作用于 `source_view == "week"` 且 `dark_mode=True` 的详情弹窗。
- 追补：修复课表颜色块在长标题换行时按整块标题垂直居中的问题；详情弹窗标题行、颜色块和标题编辑框统一改为顶部对齐，使颜色块固定在第一行正前方。
- 追补修正：颜色块显示会压缩标题可用宽度，原逻辑只 `adjustSize()` 没有重算 `QLabel` 换行高度，导致第二行被裁剪；新增标题可用宽度/高度刷新逻辑，并在颜色块显示/隐藏、标题编辑完成后调用。
- 追补修正：上一轮将暗色头部前景临时改为 `#F2F2F2` 属于误判，已恢复 `#2b2b2b`；真正问题是 `refresh_week_data()` 在左右切周时把选中空列强制设为 `#F5F5F5`，未判断暗色模式，导致暗色内容区出现白色色块。现已在暗色模式下保持底部列背景 `#2b2b2b`。

### 2026-07-12：周界面卡片模式选中列高光承载层修复
- 问题原因：周界面卡片模式的底部选中列高光此前写在 `TodoListContainer` 内部内容面板上，而该面板高度受日程卡片、占位提示和 `layout.sizeHint()` 影响；当某列内容较少或为空时，背景只覆盖内容高度，表现为高光被截断或下方完全没有高光。
- 修复方案：新增 `bottom_scroll_areas` 记录 7 个 `QScrollArea`，将选中列/普通列/暗色模式背景统一写到 `scroll_area.viewport()`，内部 `TodoListContainer` 改为透明，仅负责卡片和拖拽承载。
- 同步修复：`refresh_week_data()` 和 `_apply_dark_mode()` 都改为调用统一的 `_apply_week_board_column_background()`，避免暗色模式或刷新流程再次把背景写回内容面板。
- 验证：`D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src\ui\week_window.py` 通过。

### 2026-07-12：周界面卡片模式选中列高亮补齐
- 问题原因：上一轮已将卡片模式底部列背景移到 `QScrollArea.viewport()`，但暗色模式下选中列仍返回普通底色 `#2b2b2b`，因此卡片模式下看不出与课表模式一致的选中日显示板高亮。
- 修复方案：`_week_board_column_background()` 改为按选中态返回预混合高亮色；暗色选中列使用 `#3A3A3A`，等效于课表模式在 `#2b2b2b` 上叠加白色 alpha 18；亮色选中列使用 `#F0F0F0`，等效于白底叠加黑色 alpha 15。
- 影响范围：仅调整周界面卡片模式底部 7 列的选中列背景色，不改变顶部 `DayBlock` 高亮、课表模式绘制逻辑和日程卡片内容。

### 2026-07-12：最终规划同步暗色模式与课表状态
- 更新 `Final_Formulation.md` 当前完成状态：日 / 周课程表模式已形成可用原型并进入收尾复核阶段，月格本体暂不课表化。
- 在课程表章节补充日课表、周课表已实现能力和剩余收尾项：人工 GUI 验收、刷新键行为复核、DDL / 省略号 / 选中高亮 / 悬停预览高 DPI 复查，确认拖拽改时间、拉伸改时长和月持久弹窗课表化均不作为第一版完成条件。
- 在皮肤功能之后新增暗色模式专项规划：暗色模式后续应建立在 Theme Tokens 和 skin preset 上，按硬编码颜色盘点、暗色 preset、窗口头部、弹窗 / picker、自绘组件和视觉回归分阶段推进，不再在普通功能轮中继续扩大单窗口点修。

### 2026-07-12：日课表单击选中与双击详情
- 用户确认先从日界面课表开始做交互底座，不直接实现拖拽改时间或拉伸改时长。
- `TimetablePlaceholderFrame` 新增按 `schedule_id` 保存的选中态：单击日程块或 DDL / 单时间线段只选中，不再立即打开详情；双击同一类命中区域才打开原共享详情弹窗。
- 选中视觉：时间段日程块在网格线和当前时间线之后叠绘 `#FFD700` 2px 圆角边框；DDL / 单时间线段在同层叠绘整条金色线，确保不会被小时线覆盖。
- 命中区补充 `kind` 字段，为后续如需继续做拖拽 / 拉伸预览保留交互元数据入口；刷新数据时若选中日程已不存在，会自动清除选中态。
- 当前范围仅限日课表；周课表仍保持当前左键点击详情逻辑，待日课表验收通过后再独立迁移。

### 2026-07-12：日课表外部点击清除选中
- `TimetablePlaceholderFrame` 在应用级鼠标按下事件中过滤左键点击：当日课表已有选中日程，且实际点击目标不是日课表自身命中的日程块 / DDL 区域时，立即清除金色选中态。
- 该规则覆盖点击日课表空白处、顶部工具按钮、搜索框、窗口控制按钮和其它界面区域；点击另一个日程仍由日课表自身 `mousePressEvent` 切换选中，不改变双击打开详情的规则。
- 影响范围仅限日课表选中态，不写数据库，不影响卡片模式、周课表和月界面。

### 2026-07-12：日课表时间段拖拽与拉伸原型
- 基线提交：先提交已验收的日课表选中交互，提交号 `db8552e`，提交信息 `完善日课表选中交互`；用户的 `src/config.py` 主题色切换未纳入该提交。
- 交互范围：仅对日课表中的时间段日程块启用编辑；按下日程块会先建立选中态，移动距离超过系统拖拽阈值后进入编辑，普通单击仍只保留选中态；DDL / 单时间点线段暂不启用拖拽。
- 操作规则：块内部拖动整体平移开始/结束时间；靠近上边缘拖动修改开始时间；靠近下边缘拖动修改结束时间；时间变化按 `1 分钟` 吸附，最短时长限制为 `5 分钟`。
- 保存规则：释放鼠标后写入数据库并刷新日视图和全局视图；重复日程走现有 `update_schedule_with_repeat(..., update_future=False)` 语义，只修改当前这一条并脱离重复组。
- 验证：`py_compile src\ui\dashboard.py` 与 `git diff --check` 通过；本轮未做 GUI 人工验收，需运行程序确认拖拽手感和边缘命中阈值。
- 追补修正：上一版只在“按下前已经选中”的情况下建立拖拽状态，导致用户按正常方式直接拖动日程块时没有进入编辑；现改为按下即选中并建立待编辑状态，移动超过系统拖拽阈值后才正式编辑，同时将上下沿命中范围从 `7px` 调整为 `10px`。
- 追补增强：拖拽 / 拉伸进行中若鼠标停在课表显示框上沿或下沿 `24px` 热区内，自动每 `120ms` 将可见视窗向前或向后滚动 `1 分钟`；滚动位移同步计入本次时间编辑增量，避免只能靠滚轮先切换视窗再继续拖动，同时降低贴边时误拉过头的概率。
- 追补修正：同一时间段日程较多时，拖拽中的日程会因为实时冲突分列重算而改变横向车道和宽度，叠加边缘自动滚动后容易表现为“视窗继续滚动但原选中块不再按预期变化”；现对正在拖拽的时间段日程冻结按下时的横向车道和宽度，并将其放到同批日程块最后绘制，减少冲突重排对拖拽预览的干扰。
- 追补增强：拖拽 / 拉伸时新增独立时间提示窗，显示当前编辑后的时间点或时间段；提示窗位于主窗口左侧，几何中心与鼠标保持同一水平高度，不接收鼠标事件。同步将拖拽吸附粒度从 `5 分钟` 改为 `1 分钟`，自动滚动步长先改为 `1 分钟 / 60ms`，后因贴边滚动仍偏快调整为 `1 分钟 / 120ms`，用于更精细调整。
- 追补配置：日界面课表模式的右键菜单在“模式”下方新增“拖拉”子菜单，使用 `drag.svg`；子菜单提供 `1分钟刻度` / `5分钟刻度` 两项，分别使用 `1.svg` / `5.svg`，选择后立即切换日课表拖拽吸附粒度并写入 `timetable_preferences`，仅日课表模式显示。

### 2026-07-12：周课表选中与拖拽 / 拉伸原型
- 交互迁移：周课表由“左键点击直接详情”改为“单击选中、双击详情”，与日课表保持一致；时间段日程显示金色边框，DDL / 单时间线段显示金色整条线。
- 时间编辑：周课表时间段日程支持块内拖动平移、上沿拉开始时间、下沿拉结束时间；块内拖动允许跨日列改日期，拉伸固定在原日列内，避免起止点跨列造成歧义。
- 滚动与提示：拖动 / 拉伸时复用左侧时间提示窗；鼠标贴近日列上/下边缘时仅滚动当前编辑日列，步进为 `1 小时 / 650ms`，避免影响其他日期列。
- 保存规则：释放鼠标后写入数据库并刷新周课表；重复日程继续走 `update_schedule_with_repeat(..., update_future=False)`，只修改当前这一条并脱离重复组。
- 配置复用：周课表空白处右键菜单同样接入“拖拉”子菜单，复用 `1分钟刻度` / `5分钟刻度` 偏好；该偏好与日课表共用 `timetable_preferences.drag_snap_minutes`。

### 2026-07-13：日课表 DDL / 单时间线段拖拽补齐
- 补齐范围：日课表的 DDL / 单时间线段此前仅支持单击选中、双击详情和右键菜单；本轮补充拖拽改时间点，不增加拉伸行为。
- 交互规则：按下线段后先保持选中，移动超过系统拖拽阈值后进入编辑；时间点按当前 `1分钟刻度` / `5分钟刻度` 偏好吸附，贴边时继续沿用日课表 `1 分钟 / 120ms` 自动滚动。
- 字段规则：若日程只使用 `end_time`，拖拽只改 `end_time`；若只使用 `start_time`，拖拽只改 `start_time`；若 `start_time == end_time`，拖拽同步改两个字段。
- 视觉规则：拖拽中的 DDL 线段冻结按下时的横向位置和宽度，避免移动到同时间点密集区域时因重新分段造成左右跳动。

### 2026-07-13：周课表拖拽被窗口移动抢占修复
- 问题原因：周课表画布没有设置 `windowDragDisabled`，全局 `WindowDragController` 会在按下课表日程后记录待拖动窗口状态；鼠标移动超过系统阈值时，窗口拖动过滤器先吞掉 `MouseMove` 并移动整个周窗口，导致课表日程块没有收到拖拽预览事件。
- 连带现象：释放鼠标时窗口拖动过滤器也可能吞掉 `MouseButtonRelease`，周课表内部 `_pending_time_edit` 没被清理；后续无按键移动鼠标时又被误激活为时间编辑，表现为“松开后日程才跟着鼠标动，再点一次才确认”。
- 修复方案：`WeekTimetableBoard` 初始化时设置 `windowDragDisabled=True`，将整块周课表画布排除出窗口拖动热区；同时 `_maybe_activate_pending_time_edit()` 增加左键仍按住的校验，若释放事件已丢失则先取消 pending 编辑，避免幽灵拖拽。

### 2026-07-13：周课表 DDL / 单时间线段跨日拖拽补齐
- 补齐范围：周课表此前只支持时间段日程块拖拽平移、跨列改日期和上下沿拉伸；本轮将 DDL / 单时间线段也接入选中后拖拽改时间点，不增加拉伸行为。
- 交互规则：按下已选中线段并移动超过系统拖拽阈值后进入 `move_point` 编辑；纵向位置计算目标整时 / 分钟，横向位置计算目标日期列，因此可在同一周的 7 个日期列之间拖动切换日期。
- 字段规则：若日程只使用 `end_time`，拖拽只改 `end_time`；若只使用 `start_time`，拖拽只改 `start_time`；若 `start_time == end_time`，拖拽同步改两个字段。保存后当前选中日期按实际存在的时间字段回落。
- 视觉规则：拖拽中的 DDL 线段冻结按下时的列内横向位置和宽度，切换日期列时保持相同列内偏移，避免同时间点密集线段重新分段造成横向跳动。

### 2026-07-13：周课表拖动自动翻周
- 补齐范围：周课表时间段日程块的块内拖动，以及 DDL / 单时间线段的 `move_point` 拖动，支持贴近左右边缘后自动翻到上一周 / 下一周；上下沿拉伸仍固定在原日期列内，不参与翻周。
- 交互规则：拖动中鼠标进入画布左右 `28px` 边缘热区并停留约 `450ms` 后触发翻周，之后若持续停留在同侧边缘，每约 `700ms` 可继续翻一周。
- 状态保持：翻周由 `WeekTimetableBoard` 发出方向、目标列和该列可见小时起点，`WeekWindow` 更新 `current_monday/current_selected_date` 后刷新数据，再把目标列可见小时起点写回，避免翻周导致纵向时间突然跳到默认 `00:00`。
- 稳定性：`set_week_data()` 在活动拖拽期间保留当前选中日程 ID，即使该日程尚未写入新周数据，也不会清掉 `_active_time_edit` 和选中态；释放鼠标后再按最终预览时间写入数据库。
### 2026-07-13：月持久日期弹窗课表化原型
- 月界面单击日期的持久 `MonthDayPanel` 在全局“课表模式”且当日有日程时，不再显示紧凑日程卡片列表，改为显示只读课表框；无日程日期和卡片模式保持原样。
- 新增 `MonthDayTimetableFrame`：按当天 00:00-23:59 内的日程时间投影，绘制白底时间轴、整时标注、时间段色块和 DDL / 单时间点线段；颜色复用 `timetable_preferences.schedule_colors`，未持久化颜色时沿用日 / 周课表同类默认色持久化策略。
- 初始可见窗口按内容跨度计算：3 小时以内显示 3 小时且临近午夜时回退为 21:00-23:59；超过 6 小时只显示 6 小时；中间跨度按整小时上下界伸缩。滚轮只在当天范围内按小时滚动，不跨日期。
- 保留基础交互：课表中的日程块 / 线段可双击打开原月持久弹窗详情链路，右键沿用完成 / 撤销完成菜单。
- 月窗口新增 `apply_schedule_display_mode()`，主窗口切换卡片 / 课表模式时同步刷新已打开的日期 panel。
- 验证：`.venv\Scripts\python.exe -m py_compile src\ui\popups\month_day_panel.py src\ui\month_window.py src\ui\main_window.py` 通过；offscreen 构造 `MonthDayPanel` 验证 00:45/01:10 初始窗口为 00:00-03:00，23:10/23:50 初始窗口为 21:00-23:59。
- 追补修复：月持久弹窗课表绘制中 `QPainter.drawLine()` 误传 4 个 `float`，PyQt6 不匹配重载会在点击打开弹窗时崩溃；已改为 `QPointF` 重载，并通过 `py_compile` 与 offscreen `grab()` 绘制验证。
### 2026-07-13：月持久日弹窗课表暗色模式
- 月界面单击日期后的持久 `MonthDayPanel` 在课表模式下新增局部暗色状态，默认读取当前主界面已使用的 `week/dark_mode` 设置；无日程日期和卡片模式仍保持原样。
- `MonthDayTimetableFrame` 支持暗色绘制，课表内容区、时间轴、分割线、DDL 标签和当前时间虚线都会随弹窗暗色状态切换。
- 双击课表空白区域或弹窗空白区域可在该弹窗内切换明暗色；双击日程块 / 线段仍优先打开原有日程详情，不被暗色切换抢占。
- 验证：`python -m py_compile src\ui\popups\month_day_panel.py` 通过；offscreen 构造 `MonthDayPanel` 验证默认继承、局部切换和 `grab()` 绘制均正常。
- 追补修正：暗色模式只作用于内部课表显示框，外层弹窗继续使用主题蓝色渐变边框，不随课表暗色切换变为灰黑色。

### 2026-07-14：课程表模式收尾验证与归档结论
- 用户已完成人工 GUI 验收，未发现阻塞问题；本轮不继续追加课表交互。
- Codex 使用项目 `.venv` 在沙箱外运行 PyQt offscreen smoke：`src/**/*.py` 语法编译、日课表 `TimetablePlaceholderFrame`、周课表 `WeekTimetableBoard`、月持久 `MonthDayPanel` 课表弹窗渲染和暗色局部切换均通过。
- 主窗口集成 smoke 通过：`MainWindow.set_schedule_display_mode("timetable", persist=False)` 与 `"card"` 可同步更新日界面、周界面和月窗口模式状态。
- 归档结论：课程表模式阶段可归档；下一主线按 `Final_Formulation.md` 进入搜索 / 筛选功能规划。
