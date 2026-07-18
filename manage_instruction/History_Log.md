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

---

## 2026-07-14 至 2026-07-16：搜索筛选、排序、全局查询、导出 UI 与辅助看板收尾阶段归档

归档说明：以下为本阶段 `Work_Log.md` 原文，覆盖上次课程表归档后至当前月界面 10% 背景遮罩收尾的连续记录。

# Work Log

## 2026-07-15：全部日程阶段收尾与规划更新
- 审查：全局“日程查看”已覆盖跨日期全量数据、完成情况、日程类型、重要性、提醒、重复、清单、搜索范围、模糊 / 精准搜索、按时间 / 重要性 / 创建时间排序、日程 / 待办分组、双击详情和详情修改后刷新。
- 结论：按当前已确认需求，“全部日程”全局查询窗口可归档；右键操作、分页 / 虚拟滚动和更复杂结果操作暂未纳入当前必做范围，可作为后续增强。
- 更新：`Final_Formulation.md` 将排序功能和“全部日程”全局查询窗口改为已完成并归档，下一主线明确为导出功能。

## 2026-07-15：全部日程筛选行等分布局
- 原因：完成情况、重要性、提醒、重复等 3/4 项选项行继续使用 5 列网格定位，实际每项只能获得单列宽度，导致“已完成 / 已过期 / 未完成”等文本大量省略。
- 修复：完成情况、重要性、提醒、重复改用与排序方式一致的紧凑横向等分布局；四项行平均分配剩余宽度，三项行平均分配剩余宽度，日程类型五项行保持原网格布局。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证完成情况、重要性、提醒、重复各行宽度分配通过。

## 2026-07-15：全部日程排序行紧凑布局
- 原因：排序方式行新增第三项后仍沿用网格列布局，三项分别落在固定网格列中，单项宽度不足，导致“创建时间”等文本被省略。
- 修复：排序方式行改为专用紧凑横向布局，三个选项共同横跨设置区剩余宽度，内部仅保留 2px 间距；其他筛选行继续使用原网格布局，不影响清单、重要性、提醒等行的对齐。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证排序按钮文本、绑定值和展开后的按钮宽度通过。

## 2026-07-15：全部日程排序圆点重叠修复
- 原因：圆点按钮原先按完整文本宽度绘制文字，新增“按创建时间”后排序行每项分配宽度不足，圆点被压到右侧时会覆盖文字。
- 修复：圆点按钮绘制时先为右侧圆点预留固定空间，再对文本做右侧省略，保证任何宽度下文字和圆点不会重叠；同时排序方式文案改为“重要性 / 时间 / 创建时间”，由行标题承担“按……排序”的语义。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证排序按钮文本、绑定值和 tooltip 通过。

## 2026-07-15：全部日程排序增加创建时间与待办分组
- 调整：全局“日程查看”排序方式新增“按创建时间”，排序值使用日程 / 待办的 `created_at` 字段。
- 调整：全局排序入口单独处理日程与待办分组，任何排序方案下日程均显示在待办上方；按时间排序时，日程按有效时间排序，待办按创建时间排序。
- 调整：当筛选结果同时包含日程与待办时，列表在第一条待办前插入灰色分界线，避免两类数据混在一起。
- 验证：`schedule_sort_service.py`、`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证按时间、按重要性、按创建时间排序顺序和待办分界线入口通过。

## 2026-07-15：全部日程详情联动与刷新同步
- 修复：全局“日程查看”面板结果标题支持双击请求打开详情弹窗；面板只发出日程对象信号，不直接判断日 / 周 / 月 / 待办弹窗类型。
- 路由：`SharedMoreMenu` 在创建全局面板时按父窗口绑定详情路由；主窗口走当前可见页面判断，周窗口转发 `request_schedule_detail`，月窗口转发 `schedule_detail_requested`，复用既有详情弹窗链路。
- 刷新：主窗口将日界面、待办界面的刷新信号和统一 `_refresh_dashboard_todo_week()` 同步到所有已创建的全局日程面板，确保详情弹窗修改标题、详情、时间、提醒或清单后面板即时刷新。
- 验证：`all_schedules_panel.py`、`components.py`、`main_window.py` 语法检查通过；PyQt offscreen smoke 验证标题双击信号发射和面板信号入口通过。

## 2026-07-15：全部日程结果列表文本化
- 调整：全局“日程查看”结果项取消卡片背景、边框和前置颜色圆点，改为透明背景上的纯文本列表；标题使用黑色加粗，时间、详情和元信息使用灰黑色小字。
- 调整：标题、详情、时间和元信息均允许自动换行；存在详情时完整展示详情内容，不再用单行截断或隐藏。
- 调整：结果滚动区隐藏可见垂直滑块并保留滚轮滚动能力，减少右侧空间占用。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证结果项创建、换行标签和隐藏滚动条策略通过。

## 2026-07-15：全部日程全局查询功能接入
- 确认：查询管线为“全量数据 → 基础筛选 → 关键词搜索 → 排序 → 渲染列表”；每一层在未设置有效条件时都默认透传，空关键词不会拦截数据。
- 实现：`AllSchedulesPanel` 绑定完成情况、日程类型、重要性、提醒、重复、清单、排序方式与搜索范围 / 搜索设置，打开面板时刷新清单候选和全量日程数据。
- 实现：新增全局日程结果卡片渲染，显示标题、类型、时间、清单 / 重要性 / 状态等摘要；筛选、搜索、排序或清单变化后即时刷新滚动结果。
- 服务：`ScheduleQueryService` 支持“不重复”过滤；`ScheduleSortService` 新增全局日程排序入口，避免全局面板借用待办排序语义。
- 验证：`all_schedules_panel.py`、`schedule_query_service.py`、`schedule_sort_service.py` 语法检查通过；PyQt offscreen smoke 验证默认透传、空关键词恢复、关键词拦截、DDL 类型筛选和“不重复”过滤通过。

## 2026-07-15：全部日程设置区统一网格对齐
- 原因：设置区原本每一行都是独立 QHBoxLayout，并按各自行的选项数量、文字宽度和剩余空间自行分配坐标；同时圆点按钮内部又居中文本，导致清单下拉只能靠 spacer 硬凑位置，视觉上仍与上方行不一致。
- 修复：设置区与搜索设置区统一改为 QGridLayout，固定标题列和 5 个选项列；圆点选项改为在网格单元内左对齐绘制，清单下拉框从同一选项列起点开始并横跨选项区，取消 COMBO_OPTION_LEADING_SPACER 这类试错常量。
- 验证：ll_schedules_panel.py 语法检查通过；PyQt offscreen smoke 验证完成情况、日程类型、重要性、提醒、重复五行第一选项与清单下拉框左沿均为同一网格列起点。

## 2026-07-15：全部日程日程类型圆点与清单下拉修正
- 评估：日程类型最后“全部”圆点截断来自五项选项总宽接近设置区可用宽度，圆点描边压到右边界；清单下拉空白来自系统弹出列表不可靠继承父 `QComboBox QAbstractItemView` 样式，不能继续只靠 QSS 试错。
- 修复：圆点控件统一使用 `Microsoft YaHei UI 7pt` 度量，选项行间距从 `4px` 收窄为 `2px`，并在圆点绘制时预留 `1px` 描边安全边，避免最后一项圆点被裁切。
- 修复：清单下拉复用搜索 / 筛选弹窗的 `DayQueryOptionsPanel._apply_combo_popup_style()`，即独立 `QListView + ComboPopupItemDelegate`，让弹出列表白底上使用主题背景上沿色文字和主题色选中态。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证日程类型五项宽度、最后一项圆点预留空间、清单下拉 delegate 类型和高度通过。

## 2026-07-15：全部日程查询设置项扩展
- 调整：全局“日程查看”基础设置区按优先级作为筛选条件，原“显示范围”改为“完成情况”，原“显示类型”改为“日程类型”，并新增“重要性”“提醒”“重复”“清单”设置；排序方式保留为“按重要性 / 按时间”。
- 搜索语义：搜索设置单独挂在搜索框点击入口下，只提供“搜索范围：标题 / 标题+详情”和“搜索设置：模糊搜索 / 精准搜索”；该搜索 UI 作为低优先级条件，后续数据绑定时应基于基础筛选后的结果再搜索。
- 清单 UI：新增清单下拉框，默认含“全部清单 / 未分类”，并尝试读取当前数据库活动清单作为候选项；本轮仍只完成 UI，不接实际查询。
- 修复：搜索框事件过滤器改到所有子控件创建后再安装，避免构造期事件访问尚未创建的搜索设置区导致 PyQt 进程退出。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证基础设置标签、清单下拉、搜索设置两行选项和搜索框点击展开 / 收起通过。

## 2026-07-15：全部日程设置选项行等宽修正
- 原因：设置项圆点控件按文字宽度自适应，导致“显示类型”中 `日程 / DDL / 时间段 / 待办 / 全部` 的视觉间距不一致。
- 修复：每一行选项按该行最长文本计算统一宽度，并在行布局中等权分布，保证同一行内选项间距一致。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证三行选项各自行内宽度一致。

## 2026-07-15：全部日程窗口下沿拉伸命中修正
- 原因：原实现只在 `AllSchedulesPanel.mouseMoveEvent()` 中判断上下沿并切换光标；鼠标位于显示框、滚动区等子控件上时，外层面板收不到移动事件，因此光标不变，按下位置又可能落入拖拽逻辑，造成“有时拖窗口、有时拉伸”的不稳定感。
- 修复：将下沿 / 上沿拉伸命中区从 `8px` 放宽为 `14px`，并给显示框、滚动区、滚动 viewport、结果容器和设置区安装事件过滤器；子控件靠近上下沿时也显示竖向拉伸光标，按下后直接进入拉伸流程。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证下沿命中范围、拉伸高度变化、事件过滤子控件 mouse tracking 和显示框底边竖向拉伸光标通过。

## 2026-07-15：全部日程设置圆点选中色同步显示框
- 调整：设置项选中圆点填充色改为与显示框背景一致的 `rgba(255, 255, 255, 0.75)`，避免与下方显示框背景产生色相差异；未选中仍为空心白边。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证设置项点击状态正常。

## 2026-07-15：全部日程设置选中圆点颜色调整
- 调整：设置项选中圆点不再使用纯白填充，改为主题渐变下沿色叠加半透明遮罩效果；未选中项仍为空心白边，保持可辨识。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证设置项点击与重绘无异常。

## 2026-07-15：全部日程设置齿轮缩小修正
- 原因：旋转动画将齿轮绘制到 `24px` 透明画布中，但按钮 `iconSize` 仍为 `18px`，Qt 缩放的是整张透明画布，导致实际齿轮从 `18px` 视觉缩小到约 `13.5px`。
- 修复：设置按钮 `iconSize` 改为 `24px`，保持旋转所需透明画布不变，同时让画布内 `18px` 齿轮按原视觉尺寸显示。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证设置按钮图标显示尺寸和旋转角度状态通过。

## 2026-07-15：全部日程设置齿轮旋转动画
- 调整：`AllSchedulesPanel` 设置齿轮增加 `QPropertyAnimation`，展开设置区时从当前角度旋转到 `180°`，再次点击收起时旋转回 `0°`，展开和收起方向不同。
- 实现：设置图标保留高清染色源 pixmap，通过 `settingsIconAngle` 属性重绘旋转图标，不影响置顶和关闭按钮渲染。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证展开动画目标角度 `180°`、收起动画目标角度 `0°` 和最终角度状态通过。

## 2026-07-15：全部日程设置项圆点移到文字右侧
- 调整：`_DotOptionButton` 圆点从选项文字下方移动到文字右侧，文字与圆点整体居中；选中实心、未选中空心逻辑保持不变。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证圆点选项高度、文字宽度预留和点击互斥状态通过。

## 2026-07-15：全部日程设置项改为文字圆点样式
- 调整：`AllSchedulesPanel` 设置区选项不再使用胶囊按钮框，改为自绘 `_DotOptionButton`，显示为选项文字和下方圆点；选中项为实心白点，未选中项为空心白点。
- 保留：三组选项仍维持互斥单选逻辑，点击同组任一项会取消同组其他项；本轮仍不绑定真实筛选 / 排序数据。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证圆点选项控件存在、透明无按钮框、默认选中和同组互斥点击状态通过。

## 2026-07-15：全部日程设置区移出显示框
- 调整：`AllSchedulesPanel` 设置选项区从显示框内部移到主布局中，位于搜索行与显示框之间；显示框本身只保留结果滚动区。
- 交互：设置按钮继续作为开关使用，点击展开外部设置区，再次点击收起；原显示框内部 `2px` 设置分隔线同步移除。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证设置区父级为主面板、展开后位于显示框上方、收起后隐藏。

## 2026-07-15：全部日程窗口右上图标尺寸回调
- 按待办看板规格回调 `AllSchedulesPanel` 右上按钮图标：置顶 `pin.svg` 为 `16px`，关闭 `close.png` 为 `12px`；按钮槽仍保持 `30x30` 和零边距贴边定位。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证置顶 / 关闭图标尺寸和右上贴边几何通过。

## 2026-07-15：全部日程窗口按钮零边距贴边
- 继续按截图修正：右上角置顶 / 关闭按钮定位从 `4px` 边距改为零边距，关闭按钮 `x + width == panel.width()`、`y == 0`，置顶按钮紧贴关闭按钮左侧。
- 搜索框占位文字改为“搜索日程...”，放大镜内缩图标尺寸从 `10px` 增至 `12px`，保持高清画布渲染。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证按钮零边距贴边、置顶 / 关闭相邻和搜索框占位文字通过。

## 2026-07-15：全部日程窗口右上按钮贴边修正
- 澄清：置顶 / 关闭按钮已是 `AllSchedulesPanel` 的直接子控件，不在标题栏布局容器里；未贴边的真实原因是定位仍沿用 `offset=40`，等价于按钮右侧保留 `10px` 安全边距，且图标居中在 `30px` 按钮内进一步放大了视觉空隙。
- 修复：右上按钮组改为按 `right_margin=4px` 显式定位，关闭按钮贴近弹窗右上角，置顶按钮紧贴其左侧；置顶和关闭图标同步放大到 `18px` 并用高清染色渲染。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证关闭按钮右边距、顶部边距、置顶与关闭相邻关系和图标尺寸通过。

## 2026-07-15：全部日程窗口右上按钮与搜索行修正
- 原因：上一轮将置顶 / 关闭按钮放在标题行布局中，按钮受内容区 `12px` 边距约束，无法像坐标看板 / 待办看板一样贴近弹窗右上角；同时关闭图标误用 `search_clear.svg`，置顶 / 关闭按钮槽也从 `30px` 缩到 `24px`，视觉清晰度弱于待办看板。
- 修复：置顶 / 关闭按钮改为 `30x30` 绝对定位，沿用坐标看板 / 待办看板的 `width - offset, 10` 布局；图标改为待办看板同类高清染色方案，置顶用 `pin.svg 16px`，关闭用 `close.png 16px`。
- 调整：设置按钮移入搜索行并放大为 `30x24 / 18px` 图标；搜索框改为横向自适应扩展，右侧接近设置按钮，设置按钮右沿与显示框右沿保持同一竖线。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证右上按钮位置、设置按钮尺寸、搜索框与设置按钮中心线及显示框右沿对齐。

## 2026-07-15：全部日程窗口标题栏布局微调
- 调整 `AllSchedulesPanel` 标题区：搜索框下移到“日程查看”标题下方；设置、置顶、关闭按钮保留在右上角同一行，减少设置齿轮视觉尺寸，使其与置顶图标接近。
- 图标清晰度修正：搜索框放大镜改用与周 / 月搜索框一致的内缩高清 SVG 画布渲染方案，避免 `QLineEdit.addAction()` 图标槽拉伸导致发糊；关闭键改为高清矢量叉号并放大到 `14px` 点击按钮槽内显示。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证搜索框宽度、设置 / 关闭图标尺寸和设置区展开流程通过。

## 2026-07-15：全部日程全局查询窗口 UI 骨架
- 新增 `AllSchedulesPanel` 标题栏控件：右侧搜索框、设置、置顶和关闭按钮；设置 / 置顶 / 关闭图标沿用坐标看板的白色透明按钮风格，置顶按钮接入窗口置顶状态但不绑定查询业务。
- 显示框内部拆为设置区、`2px` 水平分隔线和结果滚动区；设置区由显示范围、显示类型和排序方式三组选项组成，点击设置按钮可展开 / 收起。
- 滚动语义按 UI 目标预留：设置区隐藏时结果滚动区占满显示框；设置区展开时只有分隔线下方结果区滚动。本轮仅搭建界面结构，不接入全局搜索 / 筛选 / 排序数据。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen smoke 验证搜索框、设置区展开 / 收起和 `2px` 分隔线状态通过。

## 2026-07-15：月日期弹窗排序实时同步修复
- 根因：月窗口排序面板的 `options_changed -> apply_sort_options -> _refresh_schedule_marker_cache(refresh_panels=True)` 信号链已经存在，已打开的 `MonthDayPanel` 也会通过 `refresh_open_day_panels()` 重收数据；真正覆盖排序结果的是 `_build_hover_schedule_cache()` 内部又对每日列表按时间固定 `sort()`。
- 修复：移除月弹窗缓存层的二次时间排序，让 `hover_schedule_cache` 保持 `_filtered_month_schedules()` 经过 `ScheduleSortService.sort_for_month_day_panel()` 后的顺序；搜索、筛选和排序统一从同一个有序结果进入月格计数、悬停预览和单击日期弹窗。

## 2026-07-15：视图切换时退出排序控制态
- 评估结论：排序属于当前视图的临时显示控制；如果从日 / 周 / 月 / 待办切到其他视图时继续保留排序高亮和排序服务接管，语义上与“退出排序”和“关闭窗口时退出排序”不一致。
- 修复：`MainWindow.switch_view()` 在实际切换前调用 `_exit_sort_state_for_view_switch()`，只处理正在离开的视图；日 / 待办 / 周会先冻结当前可见顺序再清除排序配置，月视图则直接清除月排序配置。

## 2026-07-15：模式切换退出排序与月弹窗高亮清理
- 补齐：卡片 / 课表模式切换也进入排序退出语义；当前可见日视图会冻结卡片顺序再清排序，当前可见周视图复用周排序退出，当前可见月视图清除月排序控制态。
- 修复：月界面日期单击弹窗再次单击收回时，不再保留该日期高亮；关闭日期弹窗按钮同样会在关闭的是当前选中日期时清掉 `user_selected_date` 并刷新月格。

用途：记录当前活动阶段的执行日志。阶段归档时迁移到 `History_Log.md`，并清空为下一阶段准备。

---

# 当前状态：搜索 / 筛选功能第四轮

## 2026-07-14：课程表模式阶段已归档

- 归档范围：日界面、周界面和月持久日期弹窗课程表模式。
- 归档位置：`manage_instruction/History_Instruction.md` 与 `manage_instruction/History_Log.md`。
- 收尾验证：用户人工 GUI 验收未发现阻塞问题；Codex `.venv` PyQt offscreen smoke 验证通过。
- 验证覆盖：`src/**/*.py` 语法编译、日课表 `TimetablePlaceholderFrame`、周课表 `WeekTimetableBoard`、月持久 `MonthDayPanel` 课表弹窗渲染和暗色局部切换、主窗口卡片 / 课表模式同步。
- 下一主线：按 `Final_Formulation.md` 进入搜索 / 筛选功能规划。

## 2026-07-14：日界面搜索 / 筛选面板入口

- `HeaderBar` 将搜索框左侧放大镜保存为 `search_action`，点击后发出 `search_requested` 信号；点击输入框本体仍只负责聚焦输入。
- 新增 `ScheduleSearchPanel` 轻量弹窗，采用主题渐变外框和半透明内容框，提供关键词、范围、清单、状态、重要性、日程类型、清空和应用控件。
- `MainWindow` 负责创建、定位和切换该面板；第一轮仅允许日界面卡片模式打开，非日界面或课表模式给出 toast。
- 切换出日界面、进入添加页或切换到课表模式时自动关闭面板，避免悬浮状态残留。
- 当前“应用”只提示下一轮接入查询生效逻辑；本轮不修改数据库、不过滤卡片列表、不接入周 / 月 / 待办。
- 验证：`.venv\Scripts\python.exe -m py_compile src\ui\header.py src\ui\main_window.py src\ui\popups\schedule_search_panel.py` 通过；PyQt offscreen 构造 `ScheduleSearchPanel` 并检查默认选项、清空和关闭流程通过。

### 2026-07-14：周界面搜索框放大镜补齐
- 问题：周界面 `search_box` 只设置了占位文字和样式，没有像月界面一样通过 `QLineEdit.addAction()` 加入放大镜图标，因此搜索框左侧为空。
- 修复：在 `WeekWindow` 搜索框创建时保存 `search_action`，并新增 `_apply_search_icon()`，使用 `get_colored_icon("search.svg", foreground, 10)` 生成 16px 画布图标。
- 明暗色适配：`_apply_week_header_foreground()` 刷新搜索框样式时同步重染搜索图标，保持亮色为白色、暗色为头部前景灰黑色。
- 验证：`.venv\Scripts\python.exe -m py_compile src\ui\week_window.py` 通过。

### 2026-07-14：周 / 月搜索框图标清晰度与间距修正
- 原因：月界面和上一轮周界面都先把 `search.svg` 渲染成 `10px` pixmap，再手绘到 `16px` 画布中作为 `QLineEdit` action 图标；这会引入额外透明边距和低尺寸重采样，表现为边缘发糊、形状不稳、图标与占位文字距离偏大。
- 修复：周 / 月搜索框都改为直接使用 `get_colored_icon("search.svg", ..., 14)` 生成的高分辨率 pixmap 作为 action 图标，不再经过 16px 手绘画布；周界面仍按明暗模式重染图标颜色。
- 间距：周 / 月搜索框附加样式的 `padding` 从 `3~4px` 收窄到 `1px`，让放大镜和“搜索日程...”占位文字更贴近。
- 验证：`.venv\Scripts\python.exe -m py_compile src\ui\week_window.py src\ui\month_window.py` 通过。

### 2026-07-14：周 / 月搜索框放大镜尺寸微调
- 用户反馈：周界面和月界面的搜索框放大镜仍偏大。
- 调整：周 / 月搜索框搜索图标尺寸先从 `14px` 降为 `12px`，随后按截图反馈继续降为 `10px`；仍直接使用高清 SVG pixmap，不恢复到此前 `10px + 16px` 手绘画布方案。
- 追补原因：`QLineEdit.addAction()` 的 action 图标槽会按固定槽位绘制，直接传入 `10px` pixmap 仍可能被 `QIcon` 拉伸到槽位尺寸，视觉上看不出变小。
- 追补修复：新增 `get_padded_colored_icon()`，在 `16px` 逻辑画布内高分辨率渲染 `10px` SVG 图形；周 / 月搜索框改用该内缩图标，既保留 action 槽位，又让可见放大镜真正变小。

## 2026-07-14：日界面卡片模式真实搜索与筛选

- 施工前提交当前累计成果，基线提交为 `97a0623`（完成课表模式并建立搜索筛选入口）。
- `ScheduleQueryOptions` 保存清单、重要性、状态、时间形式、搜索范围和匹配方式；`ScheduleQueryService.apply_options()` 统一执行纯内存匹配。
- 精准搜索按标题或详情字段完整相等判断；模糊搜索按字段包含关键词判断，匹配前去除首尾空格并忽略英文字母大小写。
- `DashboardView` 分离已应用筛选与临时搜索快照：搜索开始时继承当前筛选，搜索设置修改不回写筛选，关键词清空后丢弃搜索快照并恢复筛选结果。
- 日界面日期刷新时保存卡片数据快照；逐字符搜索只重绘当前卡片，不重新查询数据库或重建课表数据。
- 新增 `DayQueryOptionsPanel`，搜索入口提供清单、重要性、状态、时间形式、标题 / 标题加详情、精准 / 模糊选项；筛选按钮使用独立面板维护基础筛选。
- 主搜索框新增尾部清空 action，仅在文本非空时显示；点击或手动删空都会恢复筛选基线。长文本失焦后使用左侧省略，聚焦编辑时恢复原生输入滚动。
- 第一轮 `ScheduleSearchPanel` 不再作为日界面入口，保留给后续“更多 → 全部日程”全局结果窗口；本轮未实现全局结果页。
- 验证：目标文件 `py_compile` 通过；纯查询规则、查询状态生命周期、动态清空键、弹窗选项回填、主窗口集成和长文本左侧省略 PyQt offscreen smoke 均通过。

### 2026-07-14：日界面查询弹窗下拉文字对比度修正

- 搜索设置与筛选弹窗的 `QComboBox` 当前值、展开列表文字改用主题渐变上沿颜色；展开列表选中项继续使用主题色背景和白字，避免浅色系统列表背景上的白字不可读。
- 按 GUI 反馈将下拉框本体、箭头区域和展开列表统一恢复为白色背景，仅文字与焦点边框使用主题渐变上沿颜色。
- 二次澄清后按状态拆分：收起状态恢复半透明浅底、白色当前值和白色下三角；只有展开后的白色列表使用主题渐变上沿色文字。
- 继续按截图修正：保留下拉框原控件结构，只使用较大的白色箭头图像覆盖默认箭头；展开列表改为直接设置其独立 `QListView` 的白底、主题色文字和选中态，避免弹出窗口未继承父 QSS 导致列表文字空白。
- 主搜索框尾部清空 `×` 嵌入 `16px` 透明画布中的 `11px` 图形，保持 action 点击区域不变，仅缩小可见符号。
- 最终修正：组合框显式使用独立 `QListView`，展开项的白底、主题色文字与选中态改由 `ComboPopupItemDelegate` 直接绘制，不再依赖 Windows 私有组合框弹窗继承父 QSS；收起状态仍保持半透明底、白字和白色下三角。
- 图标修正：新增紧边界 `combo_down_white.svg` 与 `search_clear.svg`；下三角不再受原 SVG 大画布内边距影响，搜索清空键不再缩放 `close.png`，改为高分辨率渲染约 `8~9px` 可见范围、约 `1px` 圆头线条的矢量叉号。
- 验证：项目 `.venv` 目标文件语法检查通过；PyQt offscreen 实际展开列表截图可见每一项文字绘制，列表项调色板为白底 `#ffffff` / 主题色文字 `#0066cc`，矢量清空键离屏图形边缘清晰。
- 条件交互修正：搜索设置下拉项由“修改草稿后点击应用才生效”改为选择后即时作用于当前关键词；“应用”继续负责确认并关闭弹窗。面板批量回填时使用同步保护，不会因逐项设值触发中间态查询；“重置”完成后只统一刷新一次。
- 选项布局修正：保持现有颜色、边框和图标样式不变，将每个下拉框固定为 `29px` 高、选项行间距统一为 `3px`；标签同步占满 `29px` 行高并使用左对齐加垂直居中，消除原先首行 `4px`、其余 `3px` 的间距差异及标签中心偏上 `3px` 的问题。
- 说明区留白修正：搜索弹窗高度由 `330px` 调整为 `346px`，并在六行选项与说明文字之间增加独立 `4px` 附加间隔，避免中文说明实际占两行时反向挤压选项区；四行筛选弹窗尺寸保持不变。
- 卡片模式阶段验收：清单、重要性、状态、时间形式、标题 / 标题加详情、精准 / 模糊搜索矩阵全部通过；筛选基线继承、搜索临时条件隔离、逐字符刷新、清空恢复和动态清空键生命周期通过；项目 `.venv` 全量编译 `77` 个 Python 文件通过。本阶段无阻塞遗漏，可以提交并进入日课表模式接入。

## 2026-07-14：日界面课表模式搜索与筛选接入

- 卡片模式阶段已提交：`391aa34`（完成日界面卡片搜索筛选）。
- 日课表与卡片共享筛选基线、搜索临时条件和 `ScheduleQueryService`，不建立第二套匹配逻辑。
- 课表保留当前日期加跨午夜所需次日数据的原始内存源，筛选后再调用 `set_schedule_data()`；逐字符输入不重复查询数据库。
- 搜索设置和筛选弹窗不再限制为卡片模式，日课表模式可直接打开。
- 卡片删除时同步移除课表内存源并立即重绘，避免切换模式后短暂显示已删除日程。
- 验证：真实主窗口课表模式的弹窗入口、逐字符查询、实时条件、空结果网格、清空恢复、筛选与搜索隔离及卡片切换一致性通过；跨午夜次日 DDL 的清单、状态、时间形式和标题加详情精准搜索组合通过；项目 `.venv` 全量编译 `77` 个 Python 文件通过。
- 最终验收：使用完整日程模型字段再次执行日课表离屏绘制回归，搜索 / 筛选入口、跨午夜时间段、次日 DDL、无匹配网格、恢复筛选与切换回卡片均通过；本小工单完成，可以提交。

## 2026-07-14：周界面星期多选搜索与筛选接入

- 日课表搜索 / 筛选阶段已提交：`abcf69f`（完成日课表搜索筛选接入）。
- 新增 `WeekScheduleQueryOptions`，在既有清单、重要性、状态、时间形式和搜索设置之外保存独立星期集合；周查询状态不与日界面混用。
- 新增 `WeekQueryOptionsPanel` 和 `WeekdayPointSelector`：周一至周日及“全部”八个圆点同排显示，支持自由多选、全部一键全选、取消任意日期时取消全部、七天全选时恢复全部。
- 周搜索与周筛选使用两个独立弹窗；周搜索初始条件继承已应用筛选，搜索期间修改条件不回写筛选，清空关键词后恢复筛选结果。
- 周搜索框接入放大镜设置入口、动态清空键和逐字符刷新；筛选工具键接入周筛选弹窗。
- 周数据先按七天拆分，再按所选星期和查询条件过滤，因此跨天日程只会在被选中的可见日期列出现；卡片模式与课表模式共用同一结果。
- 时间范围样式按 GUI 验收调整为“周一至周日 / 全部”文字标签在上、独立 `10px` 状态圆点在下；实心白点表示选中，空心点表示取消，联动规则保持不变。
- 验证：项目 `.venv` 全量语法解析 `78` 个 Python 文件通过；八点联动、弹窗选项回填、周查询日期路由、筛选继承、搜索隔离、动态清空键和清空恢复 PyQt offscreen 检查通过。
- 提交前回归：穷举 `128` 种星期组合，执行 `20` 组清单 / 重要性 / 状态 / 时间形式 / 精准与模糊搜索场景，并用当前周 `16` 个实际日程逐列核对；周卡片与周课表的日程 ID 集合完全一致，模式切换保持查询条件。
- 筛选恢复修复：确认原查询逻辑在点击“应用”后可以从低重要性恢复“不限”，问题来自筛选弹窗只修改草稿、导致选择“不限”和“重置”在应用前看起来无效；日、周筛选统一接入 `options_changed` 实时预览，“应用”仅负责确认关闭。
- 修复回归：周卡片、周课表、日卡片和日课表均验证低重要性 → 不限、低重要性 → 重置可以立即恢复；搜索期间修改筛选仍只更新筛选基线，清空关键词后正确采用新筛选条件。

## 2026-07-14：月界面当前自然月搜索与筛选接入

- 施工前提交日 / 周筛选实时恢复修复：`0e8fc6d`（修复筛选条件实时恢复）。
- `MonthWindow` 新增独立月筛选基线、临时搜索条件和逐字符关键词状态；搜索开始时继承月筛选，搜索条件不回写筛选，清空关键词恢复月筛选结果。
- 月数据源固定为当前显示自然月；翻月时关闭旧月份日期弹窗，重新加载新月份日程。
- 月格标记、日程数量、悬停预览和日期持久弹窗统一由过滤后的缓存驱动，避免主界面数量与点击结果不一致。
- 已打开日期弹窗会随搜索 / 筛选条件即时刷新；选择“不限”和点击“重置”均可立即恢复结果。
- 卡片 / 课表模式只控制日期弹窗的渲染形式，不改变月格数量或过滤后的日程集合。
- 验证：项目 `.venv` 全量语法解析 `78` 个 Python 文件通过；基于当前月 `17` 条真实日程的 PyQt offscreen 回归覆盖月范围、计数一致性、精准搜索、筛选继承与隔离、清空恢复、日期弹窗刷新、卡片 / 课表切换、空结果和翻月。
- 筛选状态提示：日、周、月工具栏筛选按钮在存在清单、重要性、状态、时间形式或周日期范围约束时保持半透明高亮；选择“不限”或重置为无约束后自动取消高亮，搜索临时条件不会误点亮筛选按钮。

## 2026-07-14：待办列表搜索与筛选接入

- 待办筛选采用最小选项集：清单、重要性；待办搜索额外提供标题 / 标题加详情和模糊 / 精准匹配，不新增状态与时间形式选项。
- `TodoView` 分离数据库待办源、筛选基线、临时搜索条件和当前渲染结果；逐字符搜索只重绘内存数据，定时刷新数据库后继续应用现有查询状态。
- 待办搜索默认继承已应用筛选，搜索期间修改条件不回写筛选；清空关键词后丢弃临时搜索条件并恢复筛选结果。
- 主窗口共享搜索框按日界面和待办界面分别恢复关键词、占位文字、动态清空键和筛选按钮高亮，两个视图的查询状态互不覆盖。
- 共享查询弹窗增加待办精简布局：搜索四项、筛选两项；选择“不限”和重置均即时刷新，筛选有约束时持续高亮。
- 验证：项目 `.venv` 全量语法解析 `78` 个 Python 文件通过；基于当前数据库 `10` 条真实待办的 PyQt offscreen 回归覆盖精简弹窗、重要性筛选、精准搜索、筛选继承、搜索隔离、清空恢复、日 / 待办文本恢复和高亮生命周期。
- 跨视图审查补漏：从周 / 月窗口恢复到主日界面时，重新同步日界面独立关键词、占位文字、动态清空键和筛选高亮，避免此前从待办进入周 / 月后恢复时残留待办搜索文本。
- 全视图最终验收：日卡片 `8` 条、日课表源 `12` 条、当前周分列 `16` 条、当前月 `17` 条、待办 `10` 条真实数据全部通过查询矩阵；卡片 / 课表结果、星期多选、月格数量与日期弹窗、待办精简条件均与纯查询结果一致。
- 交互最终验收：日、周、月、待办均验证条件即时生效、“不限”与“重置”恢复、搜索继承但不回写筛选、清空关键词恢复筛选、动态清空键和筛选高亮生命周期；当前本地视图与模式无阻塞遗漏，“全部日程”全局搜索保留为下一独立阶段。

## 2026-07-15：排序设置与日 / 周额外筛选条件接入

- 施工前提交上一轮最终规划归档：`3f02fa7`（更新搜索筛选阶段规划归档）。
- `ScheduleQueryOptions` 新增提醒状态与重复类型条件，日界面和周界面的搜索 / 筛选弹窗增加“提醒：不限 / 提醒 / 无提醒”和“重复：不限 / 重复 / 日重复 / 周重复 / 月重复”。
- 新增 `ScheduleSortOptions` 与 `ScheduleSortService` 展示排序策略，支持包括已完成、包括已过期、排序范围（全部 / 仅 DDL / 时间段）和排序方案（按时间 / 按重要性）。
- 排序默认保持旧 `sort_order` 兼容顺序；用户在排序弹窗应用或修改后才启用新排序策略，避免一启动就改变现有手动顺序。
- 新增 `schedule_sort_preferences.py`，按 `day / week / month / todo` 独立持久保存排序设置，不与课表、坐标看板或搜索筛选状态混用。
- 新增 `ScheduleSortOptionsPanel`，日 / 待办主窗口、周窗口、月窗口均接入排序弹窗；日 / 周课表模式的排序按钮位继续执行刷新到当前时间，不参与列表排序。
- 月界面排序设置作用于月格计数、悬停预览和日期弹窗的可见日程集合；月格本体仍只显示计数 / 标记，不做列表视觉排序。

### 2026-07-15：排序与菜单视觉细节修复
- 修复 `ScheduleSortOptionsPanel` 分段选项高度被布局压缩的问题：明确分段组高度并将弹窗高度微调到 `330px`，避免“排序范围 / 排序方案”按钮底边被裁切。
- 清单选择卡片与待办清单管理卡片的清单圆点统一使用主题渐变上沿色，并增加 `1px` 白色描边。
- 更多菜单与课表右键菜单的箭头、选中态和 hover 背景不再写死浅青色，改为基于主题渐变上沿色的低透明度遮罩；当前采用 hover `10%`、当前项 `16%`。
- `StyleManager.get_menu_style()` 动态生成主题色 `check.svg` 缓存图标，使更多菜单复选框确认对钩跟随背景上沿色。
- 新增“全部日程”入口骨架弹窗 `AllSchedulesPanel`：宽度为主界面 `3/4`，默认 / 最小高度为主界面 `2/3`，背景使用主界面渐变，标题为“日程查看”，内容区为 `2px` 白边和 `75%` 不透明白色显示框，并支持上下拉伸。

### 2026-07-15：排序弹窗交互与窗口外边线修复
- 修复排序弹窗开关无法从视觉上关闭的问题：`IOSSwitch` 新增左键按下接收逻辑，避免父级无边框弹窗把开关点击误判为拖拽。
- 排序范围与排序方案分段按钮保持 `clicked` 后切换；此前尝试在 `pressed` 阶段切换会被 Qt checkable 后续状态翻转覆盖，导致点击后看似无变化。
- 排序弹窗的“应用”改为“退出”，因为排序选项在切换时已即时应用，退出按钮只负责关闭弹窗。
- 主窗口与周窗口 `paintEvent` 外轮廓线加深为灰色描边，恢复在浅色外部背景上的窗口边界识别。

### 2026-07-15：排序退出状态与周窗口圆角边框修复
- 根因确认：排序弹窗底部“退出”此前只调用 `close()`，没有清除已启用的排序状态；排序选项又是即时生效并持久化的，因此关闭弹窗后工具栏仍高亮，列表仍被排序服务接管，手动顺序看起来无法恢复。
- 修复：`ScheduleSortOptionsPanel.exit_sort_mode()` 在点击“退出”时回写默认 `ScheduleSortOptions()` 并触发既有 `applied` 流程；右上角 `×` 仍只关闭弹窗，保留当前排序设置。
- 根因确认：周窗口灰色边线原先画在父窗口 `paintEvent` 里，但下方 `content_area/body_stack` 子控件零边距覆盖父级描边；同时 QSS 中 `rgba(..., 0.1)` 在 Qt 中接近完全透明，不等同于 CSS 的 10%。
- 修复：周窗口顶部与内容区边框改为明确 alpha 的灰色 `rgba(120,120,120,120)`；内容区布局保留 `1px` 左右和底部内边距，让子页面不再盖住底边与两个底部圆角。

### 2026-07-15：排序退出语义二次修正
- 语义修正：排序弹窗“退出”不应撤销排序后的可见顺序，而应将当前显示顺序冻结为新的手动 `sort_order`，随后关闭排序模式；这样工具栏不再高亮，用户仍可继续拖拽调整顺序。
- 日界面、周界面和待办界面在收到排序退出的默认选项前，先从当前卡片布局读取可见顺序并写回 `sort_order`；周界面按日期列分别冻结，跨日重复出现的同一日程只写一次。
- 周窗口下方灰边圆角改为 `WeekContentSurface` 自绘：不再依赖 QWidget QSS 的局部 `border-bottom-left/right-radius`，避免左右线条到达底部后仍显示为直角。
### 2026-07-15：日 / 周排序方案初始高亮修正
- 根因确认：排序方案分段控件初始化时强制选中第一项，且默认排序配置的 `scheme` 为 `time`，导致日 / 周在未启用排序时也显示“按时间”高亮，容易误解为当前列表已经按时间排序。
- 修复：日 / 周排序面板在 `options.enabled == False` 时清空“排序方案”选中态；用户点击“按时间”或“按重要性”后才显示高亮并启用排序。月 / 待办暂保持原有默认回填逻辑。
- 边角分析：当前周窗口下方圆角仍可能看起来是直角，主要因为 `WeekContentSurface` 仍以完整矩形填充白色背景，圆角弧线外侧的角落像素没有被透明化或裁剪；视觉上白色矩形会继续贴到外部白色背景上，即使灰色描边路径存在，也不形成清晰的圆角外轮廓。
### 2026-07-15：关闭窗口时退出排序状态
- 交互语义补齐：如果用户不点击排序弹窗底部“退出”，而是直接点击主窗口、周窗口或月窗口关闭键，也应退出排序控制状态，避免下次打开仍保留排序高亮或排序服务接管列表。
- 主窗口关闭时会处理日界面和待办界面：若排序已启用，先冻结当前可见卡片顺序为新的 `sort_order`，再回写默认排序配置；同时联动清理已创建的周窗口和月窗口排序状态。
- 周窗口关闭时同样冻结当前周卡片显示顺序再清除排序配置；月窗口无手动列表顺序冻结需求，关闭时仅清除月排序配置。
- 层级分析补充：历史 `d92b223` 后周内容区确实存在左 / 右 / 底灰边和底部 `8px` 圆角；当前底角视觉被削成直角，直接遮挡源是 `body_stack`、`page_week_board` 以及每个 `QScrollArea.viewport()` 的矩形白底铺满到内容区边缘。
### 2026-07-15：周窗口底角圆角与轻灰边重构
- 将周窗口下方内容区改为 `WeekContentSurface` 路径填充：白色背景按底部圆角路径绘制，不再先铺满完整矩形，避免底角天然变直角。
- 新增 `WeekContentBorderOverlay` 透明覆盖层专门绘制左 / 右 / 底边和两个底部圆角，并在 resize 与主题刷新时置顶；灰边不再被 `body_stack`、`QScrollArea.viewport()` 等子控件白底覆盖。
- 灰边透明度从此前偏重的 `rgba(120,120,120,120)` 降为 `rgba(120,120,120,72)`，暗色模式对应边线降为 `rgba(255,255,255,44)`，减少边框喧宾夺主与局部粗细错觉。

### 2026-07-15：全部日程右键操作与虚拟滚动
- 实现全局结果项右键菜单：支持打开详情、完成 / 撤销完成、删除日程；删除前弹出确认，操作完成后刷新“日程查看”面板并通知主界面、周窗口或月窗口同步。
- 将“全部日程”结果列表改为虚拟滚动：保留完整查询结果与估算高度，只创建视口附近的结果项和上下占位，避免大量日程时一次性生成全部卡片控件；条件持久化按当前决策暂不实现。
- 验证：`src\ui\popups\all_schedules_panel.py` 语法检查通过；PyQt offscreen 烟测确认虚拟列表仅创建可见卡片、滚动后会重渲染、右键入口方法存在。

### 2026-07-15：全部日程结果间距固定修复
- 根因确认：虚拟列表容器高度至少等于视口高度，但结果卡片使用可扩展的纵向尺寸策略，单条或少量结果会被布局拉伸铺满显示框，造成元素间距不一致。
- 修复：结果卡片改为固定纵向尺寸，并在虚拟渲染时按估算文本高度设置固定高度；显示框剩余空间保留为空白，不再分配给结果项。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen 烟测确认多条结果和强制单条结果均按内容高度显示，单条结果不再铺满窗口。

### 2026-07-15：全部日程窗口右侧外置定位修复
- 根因确认：`AllSchedulesPanel.reset_geometry_for_parent()` 仍沿用早期居中逻辑，会把“日程查看”窗口放到父窗口内部，覆盖主界面内容。
- 修复：默认位置改为父窗口右侧外部并与父窗口顶部对齐；若右侧空间不足则回退到左侧，左右都不足时才在当前屏幕可用区域内夹取，避免越出屏幕。
- 验证：`all_schedules_panel.py` 语法检查通过；PyQt offscreen 几何测试确认默认 `x` 坐标位于父窗口右边界之外。

### 2026-07-15：导出日程弹窗 UI 骨架
- 新增 `ExportSchedulePanel`，更多菜单“导出日程”不再只打印日志，而是打开独立弹窗；弹窗标题为“导出日程”，右上角置顶 / 关闭按钮沿用坐标看板尺寸、图标和贴边风格。
- 弹窗主体为 `2px` 白边、`70%` 不透明度白色设置框，包含内容类型、日程范围、导出格式三行单选项；每个选项使用文字下方圆点样式，选中后圆点填充背景上沿颜色。
- 设置框下方新增白色可滚动预览框，点击预览框可打开放大预览弹窗；预览框右侧预留四个空白样式调整按钮，后续再绑定具体样式功能。
- 验证：`export_schedule_panel.py` 与 `components.py` 语法检查通过；PyQt offscreen 烟测确认弹窗可实例化、默认选项正确、选项可切换、预览放大弹窗可打开。

### 2026-07-15：导出日程弹窗竖版设置布局
- 将导出设置框从“三行横排”改为接近坐标看板设置页的横向分区：左侧三组竖列选项（内容类型、日程范围、导出格式），中间为“背景 / 字体”两个竖形样式按钮，右侧为竖向白色预览板。
- 选项按钮改为“文字 + 后置圆点”样式，圆点默认透明灰边，选中后填充背景上沿颜色；各组选项保持互斥单选。
- 验证：`export_schedule_panel.py` 语法检查通过；PyQt offscreen 烟测确认竖版弹窗可实例化、三组选项数量正确、默认选项和切换逻辑正确、预览放大弹窗仍可打开。

### 2026-07-15：导出日程弹窗尺寸按钮与高度回调
- 将导出日程弹窗高度回调为父窗口 `frameGeometry()` 高度的 `2/3`，宽度调整为 `540px`，保持右侧外置定位。
- 在“背景 / 字体”竖形按钮下方新增“尺寸”竖形按钮；该按钮仅在导出格式选择 `PNG` 时可点击，Markdown / PDF 状态下禁用并显示为灰白弱化状态。
- 验证：`export_schedule_panel.py` 语法检查通过；PyQt offscreen 烟测确认高度按父窗口 `2/3` 计算、宽度为 `540px`，尺寸按钮随 PNG / 非 PNG 切换正确启用和禁用。

### 2026-07-15：导出日程弹窗坐标看板风格修正
- 修正此前仅做“横向列”而未对齐坐标看板设置页视觉的问题：设置框内新增“导出设置”黑色加粗标题，各组选项标题改为黑色加粗小标题。
- 内容类型、日程范围、导出格式和样式四组均增加前置 `2px` 背景上沿色竖线；选项改用 `QRadioButton`，文字为深灰色，圆点位于文字右侧，未选中为灰边透明，选中填充背景上沿色。
- “背景 / 字体 / 尺寸”按钮纳入“样式”分组并带同样竖线；尺寸仍保持仅 PNG 格式启用。
- 验证：`export_schedule_panel.py` 语法检查通过；PyQt offscreen 烟测确认三组选项、导出设置 / 样式标题、默认选中和 PNG 尺寸启用逻辑正常。

### 2026-07-15：导出日程弹窗选项列压缩与预览边距修复
- 将内容类型、日程范围、导出格式三组从三列并排改为同一左侧纵列堆叠，减少横向占用；每组仍保留自身标题、前置蓝色竖线和右侧圆点单选项。
- “样式”组取消前置蓝色竖线，仅保留标题和“背景 / 字体 / 尺寸”竖形按钮，避免和导出选项组视觉权重混淆。
- 预览白框最小宽度增加并在右侧增加额外间距，避免贴近设置框圆角边缘时出现右侧被截断的观感。
- 验证：`export_schedule_panel.py` 语法检查通过；PyQt offscreen 烟测确认三组选项默认值、样式标题、预览框宽度和 PNG 尺寸启用逻辑正常。

### 2026-07-15：导出日程样式按钮无框与顶部对齐
- 将“背景 / 字体 / 尺寸”三个样式按钮改为无白色边框、透明背景的竖排按钮，hover 时仅显示轻微白色遮罩。
- 三个样式按钮整体从选项区中独立出来，顶部与“导出设置”标题上沿对齐；按钮高度从 `78px` 增加到 `86px`，保持竖形按钮观感。
- 验证：`export_schedule_panel.py` 语法检查通过；PyQt offscreen 烟测确认三个样式按钮存在、背景按钮高度为 `86px`、顶部位置贴近设置框上沿，PNG 尺寸启用逻辑仍正常。

### 2026-07-15：导出日程样式按钮还原
- 将“背景 / 字体 / 尺寸”三个样式按钮恢复为此前白色描边、半透明白底的竖形按钮；保留当前顶部对齐和“尺寸”按钮仅在 PNG 导出格式下启用的逻辑。
- 验证：`export_schedule_panel.py` 语法检查通过；PyQt offscreen 烟测确认三个样式按钮存在、按钮高度恢复为 `68px`，PNG 尺寸启用逻辑正常。
### 2026-07-15：导出日程样式按钮垂直对齐
- 将“背景 / 字体 / 尺寸”三个样式按钮放入固定高度承载区：背景按钮上沿与“内容类型”文字上沿对齐，尺寸按钮下沿与“导出格式”竖线下端对齐。
- 三个样式按钮之间使用等分弹簧间距，保持按钮间距一致；原有白色描边、半透明白底样式和“尺寸”仅 PNG 启用逻辑不变。
- 验证：`export_schedule_panel.py` 语法检查通过；PyQt offscreen 几何烟测确认上沿、下沿和两个按钮间距均对齐。### 2026-07-15：导出日程样式按钮间距与预览宽度调整
- 将“背景 / 字体 / 尺寸”三个样式按钮高度从 `68px` 增加到 `80px`，在保持上下沿对齐的前提下把两个按钮间距压缩为 `15px`。
- 将导出预览框固定宽度从 `210px` 收窄为 `168px`，并取消横向 stretch，避免布局自动把预览框重新撑宽。
- 验证：`export_schedule_panel.py` 语法检查通过；PyQt offscreen 几何烟测确认按钮高度、预览宽度、上下沿和等距间隔均符合预期。### 2026-07-15：导出日程预览宽度自适应修复
- 修复预览框收窄后左侧导出选项被横向拉开的布局问题：导出选项单选按钮改为固定宽度，保持选项文字与前置竖线的原有距离。
- 将导出弹窗宽度改为按预览框宽度计算：当前预览框为 `168px` 时弹窗宽度为 `498px`；后续通过尺寸功能把预览框调回 `210px` 时弹窗宽度同步变为 `540px`。
- 新增 `set_preview_width()` 作为后续“尺寸”选项绑定入口，在高度不变的前提下同步调整预览框和弹窗宽度。
- 验证：`export_schedule_panel.py` 语法检查通过；PyQt offscreen 几何烟测确认选项按钮固定宽度、当前宽度和预览宽度调整后的弹窗宽度均正确。### 2026-07-15：导出日程横向间距压缩
- 根因确认：预览框收窄后弹窗基准宽度仍偏大，Qt 将多余横向空间分配到左侧竖线、样式按钮、预览框和右边距之间，导致间距被整体拉大。
- 修复：将导出弹窗宽度计算从 `330 + preview_width` 调整为 `208 + preview_width`，保留预览框宽度可变逻辑；当前 `168px` 预览宽度对应弹窗总宽 `376px`。
- 验证：`export_schedule_panel.py` 语法检查通过；PyQt offscreen 几何烟测确认四处横向间距分别为 `14px / 12px / 12px / 14px`，预览宽度调到 `210px` 时弹窗宽度同步变为 `418px`。### 2026-07-15：导出日程背景样式弹窗骨架
- 新增“背景”样式选择小弹窗：弹窗背景沿用主界面渐变，内部显示框距离外沿 `10px`，显示框使用 `2px` 白边。
- 弹窗横向展示四个选项：纯色背景、渐变背景、默认图片、自定义；每个选项下方带竖向预览框，其中默认图片显示“web：待施工”，自定义显示“+”，均暂不绑定实际功能。
- “背景”按钮改为重复点击显示 / 隐藏该弹窗，弹窗右上角关闭键可单独关闭；关闭导出窗口时会同步关闭背景弹窗。
- 验证：`export_schedule_panel.py` 语法检查通过；PyQt offscreen 烟测确认弹窗尺寸、四个选项、重复点击隐藏和关闭键均正常。### 2026-07-16：导出背景样式弹窗细节调整
- 将背景样式弹窗的关闭键下移并内收，使 `×` 完整落在白边显示框内部。
- 将背景样式弹窗内部显示框背景改为 `70%` 不透明白底，和当前导出设置框透明度语义保持一致。
- 默认图片预览框文字从“web：待施工”改为“待施工”；自定义预览框的 `+` 号字号放大。
- 验证：`export_schedule_panel.py` 语法检查通过；PyQt offscreen 烟测确认关闭键位于白框内、第三/第四预览文字正确、关闭键可正常关闭弹窗。### 2026-07-16：导出日程样式列内联化
- 将导出弹窗第二列从“背景 / 字体 / 尺寸”三个竖形按钮改为内联设置区：背景设置、字体、尺寸三组纵向排列。
- 背景设置组内联四个缩小预览项：纯色、渐变、默认、自定义；纯色点击复用 `ThemedColorDialog` 修改单色预览，渐变预览上半区修改上沿颜色、下半区修改下沿颜色，默认 / 自定义暂不绑定功能。
- 字体组新增右侧颜色小方块并复用 `ThemedColorDialog` 修改字体颜色；下方提供标题字体、详情字体、备注字体三个字体下拉框。
- 尺寸组仅当导出格式选择 `PNG` 时显示，包含常用尺寸选项和 `__ * __` 自定义尺寸输入骨架；非 PNG 状态下隐藏。
- 验证：`export_schedule_panel.py` 语法检查通过；PyQt offscreen 烟测确认背景/字体/尺寸组存在、PNG 尺寸显隐正常、纯色/渐变/字体颜色入口能更新预览状态。### 2026-07-16：导出样式第二列细节补齐
- 修复背景设置中“默认 / 自定义”预览框没有边框的问题，并将四个背景预览框宽度统一到第二列右边界；最后一个背景框右边缘与字体下拉框右边缘对齐。
- 字体设置中将“标题字体 / 详情字体 / 备注字体”改为“标题 / 详情 / 备注”，并新增“加粗 / 斜体”两个圆点选项。
- 尺寸组改为常驻显示：非 PNG 状态下尺寸标题为白色且控件禁用，选择 PNG 后标题变黑并启用；尺寸选项改为三行两列，包含五个常用尺寸和 `__ * __` 自定义输入位。
- 验证：`export_schedule_panel.py` 语法检查通过；PyQt offscreen 烟测确认默认/自定义框存在、加粗/斜体存在、尺寸组 PNG 启用逻辑正常、背景框右边缘与下拉框右边缘均为同一坐标。### 2026-07-16：导出样式第二列对齐修正
- 将字体设置里的“标题 / 详情 / 备注”字号调整为与左侧日期范围选项一致，并保持三者与“加粗”同一左列。
- 调整“加粗 / 斜体”布局：加粗与备注标签同列，斜体控件右端与上方字体下拉框右侧对齐，两个选项内部文字与圆点距离保持一致。
- 尺寸组保持与导出格式组对齐：尺寸标题与导出格式同一区域，三行尺寸选项分别与 Markdown / PDF / PNG 同一水平高度；非 PNG 时尺寸组禁用色从白色改为灰色。
- 验证：`export_schedule_panel.py` 语法检查通过；PyQt offscreen 几何烟测确认斜体右端与下拉框右端同为 `279`，尺寸三行 y 坐标分别与 Markdown / PDF / PNG 一致。
## 2026-07-16：导出样式第二列运行态对齐修正
- 根因确认：第二列固定布局中“尺寸”分组实际比“导出格式”低 2px，因此运行截图里“尺寸”标题与 A4 / 4:3 / 长图三行都比左侧导出格式组选项低一档；另外禁用态单选圆点没有显式写 width/height/radius，Qt 会回退到默认禁用 indicator，视觉上比 Markdown / PDF / PNG 的圆点更小。
- 修复：将尺寸分组 y 坐标从 190 调整为 188，让“尺寸”标题与“导出格式”标题同一水平线；同时给禁用态单选圆点补齐 9px 宽高和 5px 圆角，并显式保持 10px 字号，避免禁用态看起来缩小。
- 验证：export_schedule_panel.py 语法检查通过；PyQt offscreen 几何断言确认“日程范围/字体”为 176/176，“导出格式/尺寸”为 276/276，Markdown/A4、PDF/4:3、PNG/长图 三组 y 坐标分别一致。

## 2026-07-16：导出样式第二列共享行基准重构
- 根因修正：此前左侧选项使用自动布局，右侧背景 / 字体 / 尺寸使用三个独立固定坐标容器；即使单独微调某个 `y` 值，标题高度、内部间距与禁用态尺寸仍会在后续分组继续累计误差。
- 布局重构：将内容类型 / 背景设置、日程范围 / 字体、导出格式 / 尺寸放入同一 `QGridLayout` 行体系；标题 / 详情 / 备注 / 加粗分别与某日 / 某月 / 某年 / 全部共用四行，A4 / 4:3 / 长图分别与 Markdown / PDF / PNG 共用三行。
- 加粗斜体：将带文字的单选按钮拆为“固定宽度文字 + 独立圆点”，使“加粗”文字左沿与“备注”严格一致，两个文字到圆点的距离一致，同时保证斜体圆点右沿与字体下拉框右沿一致。
- 尺寸规格：尺寸选项统一使用与左侧导出格式相同的 `10px` 字号和 `9px` 圆点，不再依赖禁用态原生指标尺寸。
- 验证：`.venv` Python 语法检查通过；PyQt offscreen 运行态坐标确认日程范围 / 字体标题同为 `y=172`、导出格式 / 尺寸标题同为 `y=276`，七组对应内容行逐项同高；加粗与备注左沿同为 `x=114`，斜体圆点和下拉框右沿同为 `x=270`。

## 2026-07-16：导出 PNG 比例与预览宽度联动
- 将尺寸选项中的 `A4`、`长图` 替换为常用且不与既有规格重复的 `3:2`、`9:16`，最终预设为 `3:2 / 16:9 / 4:3 / 1:1 / 9:16`。
- 尺寸预设改为互斥选择，默认使用 `9:16`；选择 PNG 后，预览框保持高度不变并按所选比例计算宽度，导出弹窗仅随预览框宽度同步伸缩，左侧设置区的尺寸与位置不变。切回 Markdown / PDF 时恢复默认预览宽度。
- 自定义 `宽 * 高` 输入也接入相同比例计算；输入有效正整数后取消预设圆点，并按自定义比例调整预览宽度。
- 点击预览框打开的预览弹窗不再固定为 `420 * 520`，其窗口尺寸始终与当前白色预览框完全一致，并在比例变化时同步更新。
- 验证：`.venv` Python 语法检查通过；PyQt offscreen 验证预览高度 `296px` 时 `9:16 / 16:9 / 自定义 3:2` 的宽度依次为 `166 / 526 / 444px`，外层弹窗宽度增量与预览框宽度增量一致，左侧控件坐标不变，预览弹窗尺寸与预览框一致。

## 2026-07-16：导出字体分项语言与颜色设置
- 取消“字体”标题右侧的统一色块，将标题、详情、备注改为三套独立设置；每行依次为名称、中 / 英切换键、字体下拉框、独立字体色块。
- 三行总宽固定为 `156px`：名称 `28px`、语言键 `24px`、字体框 `78px`、色块 `14px`，三处间距均为 `4px`；纵向仍严格复用某日 / 某月 / 某年三行基准，不改变既有布局高度。
- 中文字体提供微软雅黑、宋体、黑体、仿宋；英文字体提供 Times New Roman、Arial、Calibri、Georgia。每一行分别记忆上次选择的中英字体，切换语言不会影响另外两行。
- 新增省略显示字体下拉框，当前字体名称超出可用宽度时在右侧显示省略号；下拉列表仍保留完整字体名。
- 标题、详情、备注分别保存颜色并复用主题取色弹窗，修改任意一项只更新该行色块。
- 验证：项目 `.venv` 语法检查通过；PyQt offscreen 确认三行保持 `y=192/212/232`，色块右沿均为 `x=270`，标题切换为英文时首项为 Times New Roman，切换回中文再返回英文可恢复上次选择，另外两行状态不受影响。

## 2026-07-16：导出 UI 阶段基线提交
- 提交 `e65cbbf feat: add schedule overview and export UI`，包含此前“全部日程”收尾、导出窗口入口与 UI、最终规划和工作日志。
- 提交前通过 `git diff --check`、三个改动 Python 文件语法检查，以及“全部日程 / 导出日程”离屏实例化、字体切换和 PNG 尺寸联动烟测。

## 2026-07-16：导出格式能力灰化与放大预览弹窗
- 明确 Markdown 能力边界：标准 Markdown / Obsidian 文档不可靠保存字体、颜色、背景和画布尺寸，因此选择 Markdown 时背景、字体和尺寸三组全部灰化禁用；PDF 启用背景和字体，PNG 启用全部设置。
- 放大预览弹窗改为按原预览框尺寸乘 `1.45` 放大，并随 PNG 比例变化同步调整；其尺寸始终大于原预览框。
- 预览弹窗头部保留主题渐变，使用 `2px` 白色横线与内容区分隔；下部内容区增加 `70%` 不透明白色遮罩，正文在遮罩上显示；窗口圆角从 `12px` 收小为与周窗口一致的 `8px`。
- 验证：项目 `.venv` 语法检查通过；PyQt offscreen 确认 Markdown / PDF / PNG 三种启用矩阵正确，`526 * 296` 原预览对应 `791 * 485` 放大弹窗，比例变化会同步更新弹窗尺寸；离屏截图确认分隔线、遮罩和圆角均正常显示。

## 2026-07-16：Export-0 / Export-1 / Export-2 首轮实现
- 字段审查：确认日程和待办共用 `Schedule` 表并由 `item_type` 区分；时间段由不同的起止时间判定，DDL / 单时间使用截止或开始时间；分类、提醒、强提醒、重复、状态、重要性和创建时间均直接复用现有字段，不新增数据库字段。
- 新增 `schedule_export_service.py`，建立不可变 `ExportOptions / ExportItem / ExportPayload` 中间结构；service 负责从 Repository 只读数据、内容类型过滤、日 / 周 / 月 / 全部范围过滤、分类解析和稳定排序。
- 新增 `ScheduleMarkdownExporter`：支持按日期或清单分组，输出标题、详情、类型、时间、状态、重要性、清单、提醒、重复和创建时间；`write_markdown()` 使用 UTF-8 写入 `.md`。
- 导出窗口接入真实 Markdown 预览：内容类型和范围切换后即时重新构建 payload；PDF / PNG 尚未接入生成器时明确显示“待接入”，并暂用同一 payload 的 Markdown 结构作为数据预览。
- 当前“某日 / 某月 / 某年”以系统当前日期为目标；具体日期选择器、保存路径和导出执行按钮留到下一轮 UI 接线。
- 验证：项目 `.venv` 语法检查通过；纯内存样本验证日程 / 待办内容过滤、日范围与全部范围、分类、提醒、重复、详情、UTF-8 文件写入；真实数据库离屏烟测确认预览从当天 `972` 字符切换为全部范围 `3712` 字符，PDF 状态和放大预览仍正常。

## 2026-07-16：导出日 / 周 / 月范围选择与隐藏滚动条
- 将范围选项由“某日 / 某月 / 某年 / 全部”调整为“某日 / 某周 / 某月 / 全部”；service 新增 ISO 周边界过滤，周范围固定从周一开始、到下周一结束。
- “某日”使用导出面板私有的 `CalendarPop` 实例复用日界面日历视觉，单击日期只更新导出目标，不触发主窗口日期切换；“某周 / 某月”新增独立双下拉弹窗，分别选择年份加周数、年份加月份。
- 完成选择后，原范围选项文字分别更新为“某年某月某日 / 某年第几周 / 某年某月”，并立即重建真实数据库预览；按钮内部使用稳定 `option_value`，显示文字变化不会破坏筛选映射。
- 内嵌预览和放大预览都隐藏水平、垂直滚动条，但保留鼠标滚轮和触控滚动能力。
- PNG 溢出策略确定为固定画布分页多图，后续生成器按顺序输出带编号图片，避免强行缩放、截断或无限长图。

## 2026-07-16：导出字体预览联动与放大预览遮罩修正
- 明确当前 PDF 状态：已接入真实 `ExportPayload` 数据和预览入口，但尚未接入 `.pdf` 文件生成器；此前“PDF 导出尚未接入”下面显示的是同一 payload 的 Markdown 结构预览。
- 修复字体设置只更新色块、不更新预览的问题：标题、详情、备注现在分别生成富文本样式；颜色、字体、中英切换、加粗和斜体变化都会即时同步到内嵌预览及放大预览。
- 放大预览取消显式 `2px` 白色分隔线；头部以下直接由 `70%` 不透明遮罩形成自然色差边界，遮罩横向连接窗口左右边缘并覆盖到底部，不再保留额外渐变边框。
- 下部遮罩保留 `8px` 底部圆角；离屏几何验证遮罩区域为 `x=0`、宽度等于弹窗宽度、下沿等于弹窗下沿，三类字体颜色同时出现在两个预览的富文本内容中。

## 2026-07-16：导出执行按键入口
- 使用新增 `assets/icons/printer.svg` 在导出窗口顶栏增加打印 / 导出按键，位置固定在置顶键左侧，尺寸、图标大小和悬停样式与置顶键一致。
- 新增独立 `export_requested` 信号；当前按钮仅作为后续 Markdown / PDF / PNG 文件生成与保存路径流程的统一执行入口，不把格式生成逻辑写入窗口类。

## 2026-07-16：导出背景预览联动与范围年份缩写
- 修复背景色仅更新设置色块的问题：纯色与渐变背景现在共享统一 `export_background_mode`，修改后同时作用于内嵌预览和放大预览；Markdown 因不携带视觉样式仍固定使用白色预览背景。
- 放大预览继续保持 `70%` 不透明度：纯色转换为对应 RGBA，渐变则将上下沿颜色分别转换为 RGBA 后绘制，遮罩范围和底部圆角不变。
- 为避免范围选项文字碰到左侧蓝色分组线，选中后的日 / 周 / 月年份只显示后两位，例如 `26年07月16日 / 26年第29周 / 26年07月`；导出数据与 Markdown 正文仍保留四位完整年份。

## 2026-07-16：导出主窗口上下分区外观统一
- 导出主窗口改为与放大预览一致的上下分区：顶部保留主题渐变标题栏，下部从 `y=42px` 起直接铺设 `70%` 不透明遮罩，依靠上下区域自然色差形成分界。
- 移除下部设置区原有 `2px` 白色外边框；遮罩横向贴合窗口左右边缘并覆盖到底部，仅保留与主窗口一致的 `12px` 底部圆角。
- 项目 `.venv` 语法检查通过；PyQt offscreen 验证设置区几何为 `x=0 / y=42 / width=窗口宽度 / bottom=窗口底边`，并通过离屏截图确认分区、遮罩与底部圆角显示正常。

## 2026-07-16：待办看板主体遮罩与便签主题色
- 待办看板保留顶部主题渐变工具栏，从实际 `view_stack` 上沿向上提前 `2px` 在窗口绘制层叠加 `70%` 不透明白色遮罩；遮罩受主窗口圆角路径裁切，不改变现有标题、按钮、滚动区和拖拽布局。
- 待办便签背景使用主题渐变上下沿颜色的 `50%` 中间色，悬停时基于同一颜色轻微提亮；普通便签不显示轮廓线，置顶便签继续使用原有白色轮廓区分状态。
- 文件夹视图保留 `10px` 顶部边距；便签视图最终使用左 / 上 / 右 `5 / 6 / 5px` 网格边距。
- 便签视图与文件夹视图统一隐藏垂直滚动条，但保留滚轮和触控滚动能力，避免窄滑块占用主体空间。
- 将看板内容区底部布局边距由 `16px` 收到 `6px`，使显示区域下沿向下扩展 `10px`；卡片高度公式同步计入新增的 `10px` 顶部留白，避免最后一行被滚动视口裁掉，同时保持原有卡片高度基准。
- 修复便签拖拽结束后恢复旧半透明白色样式的问题，统一重新应用当前主题便签样式。
- 文件夹视图网格边距最终为 `8 / 17 / 14 / 0px`，文件夹与“新建清单”加号卡相对初始位置整体右移 `8px`、下移 `7px`；有待办文件夹恢复白色，空文件夹图标由 `#CCCCCC` 加深为 `#999999`。
- 项目 `.venv` 语法检查通过；PyQt offscreen 确认文件夹网格边距为 `8 / 17 / 14 / 0px`、首行组件局部坐标为 `y=17px`，测试数据包含两个白色活动文件夹和两个 `#999999` 空文件夹；普通便签样式不含灰黑边线，两种滚动区均为 `ScrollBarAlwaysOff`。

## 2026-07-16：主界面待办视图路由修复
- 定位到提交 `c9a86ba`（2026-07-15 02:58:19，“完善搜索筛选与排序交互”）在乱码改写时将待办分支的 `setCurrentWidget(page_todo)` 和查询头同步语句拼进注释，导致点击待办后主体堆栈继续停留在日界面。
- 恢复待办分支的三条独立操作：切换 `body_stack` 到 `page_todo`、刷新待办数据、同步主查询头状态。
- 项目 `.venv` 语法检查通过；PyQt offscreen 实际执行 `day → todo → day`，两次切换均确认 `body_stack.currentWidget()` 指向目标页面。

## 2026-07-16：待办看板分界线与整行滚动修复
- 修复“管理清单”主体分界线出现约 `2px` 台阶的问题：取消父窗口遮罩相对 `view_stack` 的 `-2px` 人工偏移，使遮罩和页面主体严格共用同一上沿；页面切换后延迟触发主窗口重绘，避免隐藏顶栏控件引起布局变化后残留旧边界。
- 新增两种看板共用的整行滚动基类；根据当前卡片高度、行距、视口高度和实际行数动态补足底部滚动空间，隐藏滚动条的同时让滚轮每次只移动完整一行。
- 文件夹视图三行测试中，滚动范围由不足一行的 `37px` 修正为完整行距 `100px`；第一行可以完全退出视口，“新建清单”可移动到原第二行位置，不再残留顶部截断文字。
- 便签视图四行测试中，滚动范围由 `78px` 修正为完整行距 `85px`；第十项以后仍可按整行查看，不再留下约 `7px` 的首行残片。
- 验证：项目 `.venv` 语法检查通过；PyQt offscreen 确认文件夹视口 / 内容 / 最大滚动为 `260 / 360 / 100px`，便签为 `260 / 345 / 85px`；管理清单分界处从左至右六点像素颜色完全一致。

## 2026-07-16：管理清单顶栏高度与卡片吸附滚动
- 根因确认：正常文件夹页由两个 `26px` 视图按钮撑起顶栏，进入管理清单后按钮隐藏，顶栏会退化为标题文字的 `16px` 高度，使主体分界线整体上移 `10px`。
- 将待办看板标题行固定为 `26px` 并垂直居中，正常页和管理页不再因按钮显隐改变主体起点；离屏实测两种状态下 `view_stack` 上沿均为 `68px`。
- 抽出通用吸附点滚动区，管理清单根据输入区和卡片列表生成非等距吸附点：输入区显示时先完整滚过 `60px` 输入区域，再按 `45px` 卡片加 `8px` 间距滚动；输入区隐藏时直接按卡片序列滚动。
- 动态补足管理列表底部空间，确保滚动到底时上一张卡片下沿恰好停在视口 `y=0`、下一张完整卡片从 `y=8` 开始，不再显示被截断的卡片文字或边缘。
- 验证：项目 `.venv` 语法检查通过；五张真实清单数据下，输入区显示时吸附点为 `0 / 60 / 115px`，隐藏时为 `0 / 55px`；文件夹 `100px` 和便签 `85px` 整行滚动回归通过。

## 2026-07-16：周界面底角、日程查看尺寸与子窗置顶状态修复
- 周界面内容表面新增与现有 `8px` 底部圆角一致的真实窗口遮罩，卡片模式白色滚动视口和课表模式内容均被同一圆角区域裁剪，不再穿透父容器形成底角白色直角尖角；原有灰色圆角描边覆盖层继续负责边线显示。
- “日程查看”取消按当前父窗口宽度乘 `75%` 的横向尺寸推导，固定使用 `300px` 竖版宽度；高度保持至少 `384px`，并可随父窗口高度和现有下沿拉伸逻辑向下扩展，周界面打开时不再变成横版。
- 更多菜单打开“导出日程”和“全部日程”前，改为读取实际父窗口的 `WindowStaysOnTopHint` 并调用子窗口 `set_pinned()`；子窗置顶行为、内部 `is_pinned` 状态和白色置顶图标现在保持一致，隐藏后重新打开也会重新继承父窗口状态。
- 验证：项目 `.venv` 对四个相关模块的语法检查通过；PyQt offscreen 定向检查确认周内容区最底角像素被裁剪、底边圆角内侧保留，日程查看尺寸为 `300 × 384px`，子窗置顶标志与内部状态同步。

## 2026-07-16：周界面圆角毛边消除
- 根因确认：上一轮用于阻止白色子视口穿透圆角的 `QRegion` 属于整数像素、单色窗口遮罩，不支持抗锯齿，因此虽然消除了直角尖角，却在弧线上形成明显阶梯毛边。
- 移除窗口 mask，改由 `WeekContentSurface` 在同一个抗锯齿 `QPainterPath` 内绘制基础背景和七列背景；卡片模式的 `QScrollArea.viewport()` 改为透明，不再以矩形白底覆盖父层圆角。
- 选中日期列继续保留原有浅灰 / 深灰高亮，但改由父层路径与列矩形求交后绘制；课表模式的选中列和日程内容使用独立的 `7px` 底部圆角路径裁剪，避免切换模式后重新出现方角或背景叠色。
- 编辑页、卡片模式和课表模式切换时同步启停列背景，避免父层选中列透过其他页面；原有灰色圆角描边、暗色模式颜色和列宽逻辑保持不变。
- 验证：项目 `.venv` 语法检查通过；PyQt offscreen 分别渲染卡片与课表模式，确认内容区不再使用 mask、两侧底角抗锯齿平滑、选中列和日程块显示正常。

## 2026-07-16：全部日程弹窗上下分区样式统一
- “日程查看”标题、搜索框、设置键以及右上角按键继续保留在原有主题渐变头部，头部内部位置和尺寸不变。
- 原显示框上沿改为固定上下分界：从 `y=72px` 起铺设覆盖弹窗全部宽度和底部的 `70%` 不透明白色主体遮罩，依靠渐变头部与遮罩的自然色差分区，不再绘制额外白色横线。
- 原 `2px` 白边结果框改为透明无边框容器；搜索选项、显示设置和结果滚动区统一放入主体遮罩内部，设置展开/收起时遮罩起点保持不动，仅压缩或恢复下方结果区高度。
- 主体遮罩保留与弹窗一致的 `12px` 底部圆角，顶部保持直角并与头部无缝连接；现有虚拟滚动、隐藏滚动条、上下拉伸和结果交互逻辑不变。
- 验证：项目 `.venv` 离屏渲染确认弹窗为 `300 × 384px` 时主体几何为 `x=0 / y=72 / width=300 / bottom=384`；设置展开前后主体几何一致，结果区分别正常占用剩余高度。

## 2026-07-16 日程查看分界位置与上沿拖拉手感调整

- 将 `AllSchedulesPanel` 头部底部留白由 `8px` 调整为 `11px`，使头部与主体遮罩的自然分界线整体下移 `3px`。
- 将上沿拉伸命中热区从统一的 `14px` 独立缩小为 `3px`，顶部其余区域优先用于拖动窗口；下沿拉伸热区仍保持 `14px`。
- 光标提示、鼠标按下和子控件事件过滤继续共用 `_hit_resize_edge()`，确保显示为拉伸光标的位置与实际拉伸命中区域一致。

## 2026-07-16 日程查看默认高度与设置区配色调整

- 根据验收截图中弹窗约 `720px` 的实际高度，将“日程查看”默认打开高度固定为 `720px`；窗口最小高度继续保持 `384px`，不影响后续向下缩小和上下拉伸。
- 设置区标题与全部选项文字统一改为灰黑色；选中圆点改为当前主题渐变上沿颜色，未选中圆点、字体大小、行高、间距与布局保持不变。
- 清单下拉框仅替换当前文本、边框与下三角颜色为主题渐变上沿色；原有高度、内边距、下拉按钮宽度和弹出列表布局不变。
- 在展开的设置选项与下方日程结果区之间增加 `1px` 灰黑半透明分割线，收起设置时同步隐藏。

## 2026-07-16 日程查看默认高度与设置收起联动修正

- 复核主窗口代码确认日界面默认高度为 `600px`；将“日程查看”默认打开高度由误按截图物理像素估算的 `720px` 修正为 `560px`，即比日界面默认高度低约 `40px`，最小高度继续保持 `384px`。
- 未选中选项圆点描边由白色改为 `#777777` 灰色；选中圆点继续使用主题渐变上沿颜色，选项文字、尺寸、位置和间距不变。
- 关闭显示设置时同步清除搜索选项展开状态并隐藏“搜索范围 / 搜索设置”，避免两个独立显隐状态残留；设置分割线仍与显示设置同步收起。

## 2026-07-16 坐标看板显示页与设置页公共背景分区

- 实测坐标看板原始 `320px` 高度中，画布下沿至窗口下沿由外层 `10px` 与内层 `16px` 两层底部留白组成；删除两层底部留白并将默认、最小高度同步缩减为 `294px`，画布和设置控件的实际位置及高度保持不变。
- 坐标看板公共绘制层保留顶部主题渐变，从原显示框上沿位置开始向下铺设 `70%` 不透明白色遮罩，并由窗口圆角路径统一裁剪；显示页和设置页使用相同分界位置与主体背景。
- 移除显示画布自身的白色圆角底框，以及设置页自身的白色边框和独立遮罩；设置页改用等效 `2px` 内边距补偿原边框占位，确保内部设置 UI 不发生位移或尺寸变化。
- 自动扩高计算的固定非画布高度由 `74px` 同步修正为 `48px`，避免新窗口打开后被定时自适应逻辑重新补回已裁掉的 `26px`。
- 运行回归修复：移除画布白框时误删了后续日程绘制裁剪仍需使用的 `canvas_rect` 几何变量，导致打开坐标看板触发 `NameError`；现仅恢复矩形计算，不恢复已取消的白框和独立背景。

## 2026-07-16 坐标看板底角与排序关闭收尾修正

- 坐标看板顶部两个圆角继续保持 `12px`，底部两个圆角单独减小为 `6px`；公共主体遮罩继续由同一窗口路径裁剪，因此显示页与设置页底角保持一致。
- 排查确认排序弹窗底部“退出”会先恢复默认排序控制，再通过 `applied` 信号由日、周、月、待办各自完成当前顺序冻结、排序状态清理、主界面高亮同步和弹窗关闭；右上角 `×` 原先直接调用 `close()`，绕过了这条收尾链路。
- 将排序弹窗右上角 `×` 改为复用 `exit_sort_mode()`，确保四类界面的关闭键行为与“退出”按钮完全一致。

## 2026-07-16 日月界面搜索框占位文字修正
- 修复主窗口查询头同步逻辑中因错误编码造成的日界面搜索框乱码，占位文字恢复为“搜索日程...”；同一分支的待办占位文字同步恢复为“搜索待办...”。
- 月界面搜索框占位文字由“搜索...”统一为“搜索日程...”，仅修改显示文本，不改变搜索图标、输入框尺寸和查询逻辑。

## 2026-07-16 月界面全窗背景遮罩
- 月界面在整个圆角窗口背景绘制层铺设 `10%` 不透明白色遮罩，包含 `y=24px` 横向分界线上方的顶部工具栏和下方主体；原有分界线继续在遮罩之后绘制。
- 遮罩在任何日历、日期文字、工具图标和左侧控件绘制之前完成，不作为覆盖层或子控件叠放，因此只改变背景，不降低文字和图案的清晰度；日历 delegate 原本单独绘制的不透明渐变格底同步使用与白色按 `10%` 混合后的颜色，文字、日期 marker、边框和交互高光仍在背景之后按原规则绘制。

---

## 2026-07-16 至 2026-07-19：真实导出、日程交互与纪念日期阶段归档

阶段范围：

- Markdown / ReportLab PDF / 固定画布分页 PNG 的真实导出、真实预览与保存分发。
- 默认 / 自定义图片背景、按目标比例裁剪和格式独立偏好记忆。
- 日课表下半区视觉重构与日界面右键“收起 / 放下”。
- 月日期卡片 / 课表弹窗交互收尾。
- 纪念日期弹窗、提醒、卡片、日历标记、删除和本地持久化。
- 日 / 周 / 纪念日期“多选”菜单入口壳。

实际修改文件摘要：

- 导出服务：`src/services/schedule_export_service.py`、`schedule_pdf_exporter.py`、`schedule_png_exporter.py`、`export_background_presets.py`。
- 导出 UI：`src/ui/popups/export_schedule_panel.py`、`export_default_background_popup.py`、`export_background_crop_popup.py`。
- 偏好状态：`src/utils/export_style_preferences.py`、`src/utils/commemoration_preferences.py`。
- 日程 UI：`src/ui/dashboard.py`、`src/ui/header.py`、`src/ui/main_window.py`、`src/ui/month_window.py`、`src/ui/week_window.py`、`src/ui/popups/month_day_panel.py`、`src/ui/common/action_context_menu.py`。
- 纪念日期：`src/ui/popups/commemoration_day_panel.py`、`assets/icons/commemorationday.svg`、`assets/icons/commemoryday_cal.svg`、`assets/icons/Multiplechoice.svg`。
- 资源与文档：`assets/Output_Background/`、`README.md`、`manage_instruction/Final_Formulation.md` 及当前阶段工作文件。

执行记录摘要：

1. Markdown 保存复用统一 `ExportPayload`，使用 UTF-8 写入和格式后缀规范化；取消、成功和错误路径均有明确反馈。
2. PDF 采用 `reportlab==4.4.9`，支持中文字体回退、整卡换页、超长续卡、A4、背景及标题 / 详情 / 备注独立样式；真实预览通过防抖单线程生成临时 PDF，并由 `QPdfDocument / QPdfView` 显示最终分页。
3. PNG 复用同一排版器，支持竖版与自定义尺寸、分页多图、准确张数提示、同名文件夹输出、冲突确认及真实多页预览；放大预览右上角入口绑定导出保存流程，不再误开系统打印。
4. 默认背景由程序化预设和图片目录自动扫描组成，一次显示 8 项并循环滚动；图片文件名保持英文，界面映射中文。默认图片和自定义图片共用裁剪弹窗，PDF 按 A4、PNG 按目标画布裁剪，确认后才生成预览和最终文件。
5. 导出样式按 Markdown / PDF / PNG 分开记忆；背景、字体、尺寸、自定义路径和裁剪状态不会跨格式串用。多页 PNG 统一输出到文件夹，解决桌面散落多张图片的问题。
6. 日课表改为横贯下半区的遮罩与 7 小时动态网格；左右边距、上下边线、时间栏颜色和拖拽时间映射同步调整，卡片模式保持原布局。
7. 日界面共享右键菜单仅在日视图增加“收起 / 放下”；正文隐藏不销毁，按头部工具实际下沿计算 20px 留白，放下恢复高度、模式、详情弹窗和布局状态，不触发刷新。收起时仍可挂起，切换正文功能或其他视图前自动放下。
8. 月日期弹窗完成置顶键、紧凑时间栏、遮罩布局、空白右键菜单以及课表块 / 时间线在当天范围内拖动；月卡片弹窗的多选入口最终放在非卡片区域，而不是数量随内容变化的列表容器。
9. 纪念日期弹窗完成默认收起设置区、添加表单、日历选日、提醒开关与提前量、卡片排序、今天金色标题、过期白色背景、右键删除、纪念日专用日历标记、空白右键多选和主体空白拖动；启动时按提醒条件可自动打开弹窗。
10. 多选目前只完成菜单入口和图标接入，没有实现业务选择、批量完成或批量删除，归档时明确列为下一阶段首要任务。
11. 2026-07-19 审计 `assets/Output_Background/` 共 21 张图片；Git 历史没有删除记录。错误创建的 `FINAL_VISION.md` 已删除，最终构想恢复到标准路径。

验收结果：

- 项目 `.venv` 为 Python 3.11.9，PyQt6 可正常导入；此前沙盒内进程创建失败不代表虚拟环境损坏。
- 全量 Python AST / 编译检查在各功能提交前通过；`git diff --check` 在各阶段收口时通过。
- PDF 验证覆盖中文与英文混排、8 种字体组合、空结果、普通多页、超长续卡、文本提取和逐页渲染。
- PNG 验证覆盖单页 / 多页、竖版 / 自定义画布、编号、文件夹输出、冲突处理、预览与最终尺寸一致。
- PyQt offscreen 验证覆盖导出范围弹窗、真实 PDF / PNG 预览、背景裁剪、日课表几何、菜单二级选择、收放坐标、20px 留白、圆角、挂起兼容和跨视图自动放下。
- 用户通过多轮真实 Windows 截图反馈完成月日期弹窗、纪念日期、默认背景、导出预览和切换菜单位置校正。

关键提交：

- `55db2c4`、`10ffa18`、`88b0278`、`011eec1`、`5f02b05`
- `4028757`、`69030bc`、`bf899ed`
- `1b38018`、`5b7e02a`、`e5e7428`

未完成事项：

- 多选业务闭环尚未实现。
- 自动化测试与 CI 基线尚未建立。
- `每年` / 自定义重复规则尚未实现。
- 本地备份 / 恢复、字体与 Skin Preset、本地数据库加密、本地多账号尚未实现。
- 云同步和最终 UI 审美统一尚未进入执行阶段。

风险或疑点：

- 纪念日期当前使用独立本地偏好存储，进入备份 / 云同步阶段时需明确稳定 ID、迁移和冲突规则。
- 导出背景保存本地路径；跨设备恢复时必须提供缺失资源提示或资源复制策略。
- 自定义重复规则会触及批量生成、未来实例编辑和数据一致性，必须在测试基线之后实施。
- 大型旧 UI 文件仍承担较多状态，不应在后续功能工单中顺手重构。
