# Work Log

用途：记录当前阶段/当前小工单的执行过程、验证结果和风险。

历史日志归档见：

- `History_Log.md`

旧架构改写阶段日志已移入：

- `ReconstructionDolder/History_Log.md`

---

## 当前状态

右键上下文菜单阶段已完成并归档。

当前无待执行小工单。

下一步建议：

- 制定月界面功能补齐阶段规划。

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
