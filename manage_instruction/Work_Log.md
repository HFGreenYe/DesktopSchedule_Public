# Work Log

用途：记录当前阶段执行过程、验证结果、风险和结论。

---

# 当前状态：暂无活动阶段日志

月界面功能补齐阶段已于 2026-06-04 归档。

归档位置：

- `manage_instruction/History_Instruction.md`
- `manage_instruction/History_Log.md`

当前工作区等待下一阶段规划。

---

## 2026-06-04 月界面功能补齐阶段归档

- 归档内容：
  - `M-0` 到 `M-7` 阶段合同摘要已追加到 `History_Instruction.md`。
  - `M-0` 到 `M-7` 执行与验收摘要已追加到 `History_Log.md`。
- 当前工作文档重置：
  - `Work_Formulation.md`：暂无活动阶段。
  - `Work_Instruction.md`：暂无待执行阶段合同。
  - `Work_Task_Prompts.md`：暂无待执行提示词。
- 后续建议：
  - 不继续向月界面功能补齐阶段追加任务。
  - 若处理界面适配问题，应另开 UI 适配 / 布局债务整理阶段。

---

## 2026-06-13 坐标显示入口调整记录

- 背景：
  - 后续四象限不再按完整独立视图推进，暂调整为“坐标显示”入口。
  - 本次只做入口和显示形式调整，不实现坐标/象限看板内容。
- 已完成提交：
  - `77a7fde refactor: simplify view selectors`
    - 从主界面、周界面、月界面和右键菜单的视图切换入口中移除“四象限/象限”显示项。
    - 周视图拓展框改为短文案 `日 / 周 / 月 / 待办`，并固定宽度到 124px，使右侧与上方工具按钮组对齐。
  - `61788b8 feat: add axis display menu entry`
    - 在右上角 `SharedMoreMenu` 中新增 `坐标显示` 菜单项。
    - 新增 `assets/icons/axis.svg`。
    - 当前点击行为为占位打印，不打开新窗口，不实现坐标看板。
- 验证记录：
  - `rg -n "四象限|象限" src\ui src\controllers`：源码 UI / controller 范围无旧显示文案命中。
  - `py_compile` 覆盖 `dashboard.py`、`week_window.py`、`month_window.py`、`main_window.py`、`action_context_menu.py`、`components.py`、`main.py`：通过。
  - offscreen 构造验证：
    - `ViewSelectorCard` 仅包含 `day/week/month/todo`。
    - `ActionContextMenu.view_actions_by_id` 仅包含 `day/week/month/todo`。
    - `WeekWindow` 视图拓展按钮为 `['日', '周', '月', '待办']`，拓展框宽度为 124px。
    - `SharedMoreMenu` 菜单项包含 `坐标显示`。
- 风险或后续：
  - `坐标显示` 仍是入口占位，后续实现坐标看板前需先确认紧急性轴和重要性轴的数据来源。
  - 当前数据模型中 `priority` 语义仍存在“紧急性/重要性”混用历史，不能直接固化为双轴规则。

---

## 2026-06-13 待办看板文字与紧凑视图拓展状态小修

- 背景：
  - 待办看板便签视图中，长标题存在截断策略不一致、pin 图标随文字换行下移的问题。
  - 待办看板文件夹视图中，长文件夹名会撑开布局并导致最右列被滚动条或窗口边界裁剪。
  - 主界面和待办界面复用的视图拓展框缺少当前视图状态提示，日视图和待办视图容易混淆。
- 已完成提交：
  - `6879a03 fix: adapt todo board card titles`
    - `StickyNoteCard` 标题改为固定高度区域内显示，pin 图标保持左上角固定。
    - 长标题先换行，再按需缩小字号，避免不同卡片出现不一致截断。
    - `FolderCard` 文件夹名限制在卡片内部，先缩小字号，仍无法完整显示时省略。
    - `FolderViewContainer` 按可用宽度控制三列卡片宽度，并给右侧滚动条留安全边距，避免最右列显示不全。
  - `1524615 refactor: highlight active compact view selector`
    - `ViewSelectorCard` 增加当前视图状态。
    - `MainWindow.switch_view(...)` 同步日 / 周 / 月 / 待办状态到主界面和待办界面的视图拓展框。
    - 当前视图文字保持白色，非当前视图文字改为浅灰色；已取消高亮块、白边和金色文字方案。
- 验证记录：
  - `py_compile` 覆盖 `src/ui/todo_board.py`、`src/ui/dashboard.py`、`src/ui/todo.py`、`src/ui/main_window.py`、`main.py`：通过。
  - offscreen 构造验证：
    - `FolderCard` 长文件夹名不会撑开卡片宽度，超长内容使用省略文本。
    - `FolderViewContainer` 三列卡片宽度受控。
    - `StickyNoteCard` 长标题区域高度稳定。
    - `ViewSelectorCard` 可在 `day/todo` 状态间切换，当前项白字、非当前项浅灰。
- 风险或后续：
  - 本次仅修复待办看板文字适配和紧凑视图拓展状态，不处理待办看板整体 UI 重排。
  - `main.py` 当前仍有既有未提交改动，本次日志不包含也不解释该改动。

---

## 2026-06-14 添加表单重要性与月界面选项显示小修

- 背景：
  - `priority` 实际更接近“重要性”；“紧急性”应由截止时间或时间距离推导。
  - 月界面左侧添加表单空间较窄，`紧急性`、`每天`、`每周`、`每月` 等文字显示拥挤。
  - 月界面下拉弹窗在当前样式下存在白底白字不可读风险。
  - 月界面摘要三行已有外层信息框，小文本背景框显得拥挤。
- 本次代码改动：
  - `src/ui/add_view.py`：日界面添加表单 `紧急性：` 改为 `重要性：`。
  - `src/ui/add_view_week.py`：周界面添加表单 `紧急性：` 改为 `重要性：`，同步相关注释。
  - `src/ui/month_window.py`：
    - 月界面添加表单 `紧急性` 改为 `重要性`。
    - 月界面重要性显示项改为 `高 / 中 / 低`，默认仍为低。
    - 月界面重复显示项改为 `无 / 日 / 周 / 月`。
    - 新增显示值到保存值映射：`日 -> 每天`，`周 -> 每周`，`月 -> 每月`。
    - 下拉弹窗文字颜色对齐日 / 周添加页，使用灰色 `#333333`；选中项仍为青底白字。
    - 摘要三行小文本框改为透明背景、无边框；外层信息框保留。
  - 二次微调：
    - 月界面重要性 / 重复行改为固定 label 与 combo 宽度，避免 `重要性` 与短选项被压缩截断。
    - 月界面 `QComboBox` 隐藏下拉箭头区域，给短文案留出完整显示空间。
  - 三次微调：
    - 周界面添加页的 `QComboBox` 取消前置空格假居中，改为非 editable 的自绘居中显示。
    - 周界面下拉列表项也设置为居中显示，并保留 Qt 原生点击弹出行为。
    - 日界面本次仅保留 `紧急性：` 到 `重要性：` 的文案调整，不改变原有下拉框显示实现。
    - 月界面重要性 / 重复行继续压缩 label 宽度和控件间距，两个短下拉框均缩窄为 30px，并改为非 editable 的自绘居中显示，避免重复框贴到右侧边界。
  - 纠偏记录：
    - 曾临时尝试把日界面添加页下拉框也改为居中实现；复核后确认日界面原本已满足显示要求，已回退。
    - 当前 `src/ui/add_view.py` 实际代码差异只保留 `紧急性：` 到 `重要性：` 的文案改动，以及文件末尾换行规范化；未保留任何 `QComboBox` 行为或样式改动。
- 验证记录：
  - `py_compile` 覆盖 `src/ui/add_view.py`、`src/ui/add_view_week.py`、`src/ui/month_window.py`、`main.py`：通过。
  - offscreen 构造验证：
    - `InlineAddViewMonth.lbl_priority == "重要性"`。
    - 月界面重要性显示项为 `['高', '中', '低']`，默认 index 为 `2`（低）。
    - 月界面重复显示项为 `['无', '日', '周', '月']`。
    - 月界面重要性 / 重复下拉框宽度均为 30px，文本居中。
    - 周界面重要性与重复下拉框文本居中，显示项保持原有真实文案。
    - 日 / 周 / 月三处下拉框均保持非 editable，避免 editable 方案影响点击弹出。
    - 日界面重要性下拉仍沿用原有显示方式。
    - 摘要标签样式包含透明背景和无边框。
    - `AddScheduleView` / `AddScheduleViewWeek` 可构造。
  - monkeypatch 保存验证：
    - 月界面显示 `高 + 日` 时，保存数据为 `priority=2`、`repeat_rule="每天"`。
    - 验证过程未写入数据库。
- 范围说明：
  - 本次不调整日界面 / 周界面的重复项。
  - 本次不改数据模型、不改数据库、不改重复规则服务。
  - 本次只处理添加表单文案、月界面显示短文案和下拉 / 摘要局部样式。
- 风险或后续：
  - 月界面整体左侧布局仍需后续 UI 适配。
  - `priority` 字段历史语义仍存在“紧急性 / 重要性”混用，后续坐标显示或课程表视图规划时需继续区分。

---

## 2026-06-14 右键菜单视图子菜单图标替换

- 背景：
  - 用户已将 `interface-day.svg`、`interface-week.svg`、`interface-month.svg` 放入 `assets/icons/`。
  - 右键弹窗的视图子菜单仍使用旧的日历 / 周视图图标，和新图标资源不一致。
- 本次代码改动：
  - `src/ui/common/action_context_menu.py`：
    - `日视图` 优先使用 `interface-day.svg`，保留 `Calendar.svg` 作为 fallback。
    - `周视图` 优先使用 `interface-week.svg`，保留 `week_top_color.svg` / `view.svg` 作为 fallback。
    - `月视图` 优先使用 `interface-month.svg`，保留 `Calendar.svg` 作为 fallback。
- 范围说明：
  - 本次不修改右键菜单交互行为。
  - 本次不修改主界面 / 周界面 / 月界面的右键接入逻辑。
  - 本次不修改待办图标。
  - 新增图标文件由用户放入 `assets/icons/`，当前作为待提交资源。
