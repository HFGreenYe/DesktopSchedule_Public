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
