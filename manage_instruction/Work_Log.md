# Work Log

用途：记录当前活动阶段的执行日志。阶段归档时迁移到 `History_Log.md`，并清空为下一阶段准备。

---

# 当前状态：搜索 / 筛选功能第一轮

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
