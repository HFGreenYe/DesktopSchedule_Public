# Work Log

用途：记录当前阶段执行过程、验证结果、风险和结论。

---

# 当前状态：暂无活动阶段日志

截至 2026-07-06，坐标看板第一版、归档后增强及高 DPI / 多屏边界回归均已完成并归档。

归档位置：

- `manage_instruction/History_Instruction.md`
- `manage_instruction/History_Log.md`

归档结论：

- 坐标看板当前无阶段阻塞项。
- 完成日程开关、驻留刷新、轨道自动扩窗、未分类默认颜色、广域拖动、resize 时间跨度锁定和屏幕边界修复均已完成。
- 下一阶段尚未规划，本文件等待新的执行记录。

---

## 新阶段记录规则

- 开工前记录 `git status --short --branch` 和既有 diff。
- 每轮记录实际修改文件、验证命令与结果、未完成事项和风险。
- 阶段完成后由主窗口复核并迁入 `History_Log.md`。

---

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
