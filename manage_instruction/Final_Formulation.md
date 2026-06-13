# Final Formulation

用途：沉淀项目最终架构目标、当前阶段功能开发约束和已累积技术债。后续新功能规划应优先读取本文，再读取当前 `Work_Formulation.md` / `Work_Instruction.md`。

依据：

- `manage_instruction/ReconstructionDolder/Work_Formulation.md`
- 当前已完成的架构改写轮次 1-8
- 当前功能补充阶段日志和近期月界面、右键菜单实现结果
- 月界面功能补齐阶段归档结果（`M-0` 到 `M-7`）

---

## 1. 总体方向

项目采用兼容式渐进演进，不重写产品，不一次性替换旧 UI。

核心原则：

- 保留现有运行行为优先于目录形式整齐。
- 保留 `db_manager` 作为旧 UI 过渡门面。
- 新增功能优先旁路接入，不破坏旧调用链。
- 新公共 UI 组件优先放入 `src/ui/common/`、`src/ui/popups/` 或 `src/ui/utils/`。
- 新功能不得把大量业务判断继续堆入窗口类；能抽纯逻辑时应进入 service 或 helper。
- 占位功能必须保持占位，不伪实现。
- 每个阶段继续采用小工单推进，先审查、再单点试点、最后整体验收。

---

## 2. 最终目标架构

长期目标不是推翻当前结构，而是逐步形成以下分层：

```text
src/
  app/ or controllers/
    bootstrap.py              # QApplication、窗口创建、全局装配
    main_controller.py         # 主窗口级路由与跨视图协调
    view_router.py             # day/week/month/todo/add/picker 切换
    refresh_coordinator.py     # 跨视图刷新协调

  domain/ or models/
    models.py                  # 轻量领域对象、枚举、状态常量
    schedule_rules.py          # 重复日程、日期计算、过期判断
    sorting.py                 # 日程/待办排序规则
    reminders.py               # 提醒触发判断

  data/
    models.py                  # Peewee Schedule/Category
    database.py                # db 连接、初始化、迁移、db_manager 兼容门面

  repositories/
    schedule_repository.py     # 日程 CRUD
    category_repository.py     # 清单 CRUD

  services/
    schedule_query_service.py          # 日程/待办过滤
    schedule_sort_service.py           # 排序规则
    schedule_service.py                # 新建、编辑、重复日程写入
    category_policy_service.py         # 清单删除策略
    reminder_service.py                # 提醒扫描与触发判断
    matrix_classification_service.py   # 四象限分类纯逻辑
    weather_service.py                 # 天气服务

  theme/
    theme_manager.py           # Skin Preset / QSS 加载与刷新
    default.qss                # 默认皮肤
    *.qss                      # 后续皮肤

  ui/
    common/                    # 可复用 UI 小组件
    popups/                    # 独立弹窗/浮窗
    utils/                     # UI 工具 helper
    views/                     # 后续视图拆分目标
    dialogs/                   # 后续对话框拆分目标
    *.py                       # 现有兼容 UI 文件
```

当前项目已经采用实际目录：

- `src/controllers/`
- `src/repositories/`
- `src/services/`
- `src/theme/`
- `src/ui/common/`
- `src/ui/popups/`
- `src/ui/utils/`

后续不必为了和旧规划的 `app/`、`domain/` 名称完全一致而重排目录；实际原则是职责边界一致。

---

## 3. 当前已完成的架构基础

已完成内容：

- Repository 层已建立。
- `DatabaseManager` 已保留为 `db_manager` 兼容门面。
- 部分查询、排序、清单策略、提醒逻辑已进入 `services/`。
- Controller / Router / RefreshCoordinator 已建立，用于承接跨视图协调。
- ThemeManager 和 Skin Preset 路线已建立：
  - 默认皮肤为 `default.qss`。
  - `light.qss` / `dark.qss` 仅作为兼容或测试 preset，不代表 light/dark mode matrix。
- QSS 动态属性规范已建立：
  - `role`
  - `state`
  - `variant`
- UI 包骨架已建立：
  - `src/ui/common/`
  - `src/ui/views/`
  - `src/ui/dialogs/`
  - `src/ui/popups/`
  - `src/ui/utils/`
- 已提取低风险 UI helper / component：
  - `src/ui/utils/icon_loader.py`
  - `src/ui/common/toast.py`
  - `src/ui/common/week_day_block.py`
  - `src/ui/common/todo_board_add_folder_card.py`
  - `src/ui/common/action_context_menu.py`
- 主界面和周界面已接入右键上下文菜单：
  - 仅实装视图切换和添加。
  - 换肤、排序、筛选、四象限保持占位禁用。

---

## 4. 后续功能开发约束

新增功能必须遵守：

- 不新增数据库字段，除非阶段规划明确说明并单独验收迁移。
- UI 层可以短期继续通过 `db_manager` 兼容门面读取数据，但不应直接新增 Repository 依赖。
- 新增复杂业务规则优先进入 `services/`，不要写进窗口类。
- 新弹窗优先进入 `src/ui/popups/`。
- 可复用小组件优先进入 `src/ui/common/`。
- 纯 UI helper 优先进入 `src/ui/utils/`。
- 新右键菜单优先复用 `ActionContextMenu`。
- 新视图样式应优先考虑 `default.qss / skin preset / role-state-variant`，旧 UI 内联样式暂不强行清理。
- 所有功能阶段都必须先写规划，再写分步指令，再生成提示词。

---

## 5. 当前完成状态

当前状态：架构改写阶段已收束，月界面功能补齐阶段已归档，当前暂无活动阶段。

已完成阶段：

- 架构改写轮次 1-8：
  - 数据层、Repository、Service、Controller、Theme、UI 包骨架已建立。
  - 旧 UI 仍保留兼容运行，不再继续以大范围架构重写为主线。
- 右键菜单阶段：
  - `ActionContextMenu` 已建立。
  - 主界面与周界面已接入页面级右键菜单。
  - 已实装视图切换和添加。
  - 换肤、排序、筛选、四象限仍为占位或未接入。
- 月界面功能补齐阶段：
  - `M-0`：月界面现状审查。
  - `M-1`：月格日程状态标记和今天金色日期。
  - `M-2`：单击选中、双击跳日视图。
  - `M-3`：hover 只读预览弹窗。
  - `M-4`：单击日期持久浮窗壳。
  - `M-5`：添加按钮日期来源联动。
  - `M-5b`：月界面添加表单能力只读审查。
  - `M-5c`：月界面添加表单 UI 壳。
  - `M-5d`：时间 picker 接入。
  - `M-5e`：提醒与清单 picker 接入。
  - `M-5f`：紧急性、重复规则和保存字段对齐。
  - `M-5g`：月界面添加能力整体验收。
  - `M-6`：月界面右键菜单接入。
  - `M-7`：月界面功能补齐整体验收与归档。

当前未完成但已明确存在的功能缺口：

- 月界面 UI 适配仍明显不足，尤其是窄侧栏添加表单、picker 面板和月历区域的协调。
- 四象限仍未实现。
- 真实换肤 UI 尚未接入。
- 搜索 / 筛选仍未完整实现。
- 导出功能仍未实现。
- 云同步 / 多设备同步尚未实现，且不应作为当前本地版闭环的前置条件。

后续阶段应先规划再执行，不应直接进入源码修改。候选方向：

- UI 适配 / 布局债务整理。
- 导出 / 备份能力。
- 四象限轻量视图或看板。
- Skin Preset 真实切换入口。
- 搜索 / 筛选。
- 云同步方案设计。

---

## 6. 当前技术债总表

### 6.1 Data / Repository / Service

- `db_manager` 仍承担大量旧 UI 兼容入口。
- 部分 UI 仍直接调用 `db_manager` 做查询或写入。
- 月界面当前在 `MonthWindow` 内部构建 marker cache 和 hover cache，短期可接受，长期应考虑提到 service/read-model helper。
- 重复日程写入和编辑逻辑仍属于高风险区域，后续修改必须单独小工单验证。

建议：

- 保持 `db_manager` 门面不动。
- 后续新增复杂查询优先进入 `ScheduleQueryService` 或专门 read-model helper。
- 不在功能工单中顺手重构重复规则写入。

### 6.2 Controller / Router / Refresh

- `MainWindow` 仍保留大量视图切换、picker 回流、详情弹窗回流和提醒协调逻辑。
- 已有 `ViewRouter` / `MainController` / `RefreshCoordinator`，但旧 UI 还未完全迁移。
- 新功能如果需要跨视图刷新，应优先复用既有信号或 RefreshCoordinator，不要新增窗口互相调用。

建议：

- 月界面后续添加/右键/浮窗阶段继续复用现有 `date_selected`、`view_selected`、`ActionContextMenu`。
- 不在月界面阶段扩大 Controller 改造范围。

### 6.3 Theme / QSS / Style

- 旧 UI 中仍有大量 `setStyleSheet(...)`。
- 新增 `MonthDayHoverPreview` 当前使用局部 `paintEvent` 与内联样式，属于小范围样式债。
- `ActionContextMenu` 已向右键菜单样式收口，但仍为组件级样式。
- 真实换肤 UI 尚未实现。

建议：

- 旧内联样式暂不批量清理。
- 新公共组件若继续扩展，应优先考虑 QSS 动态属性。
- 后续单独做 Theme/QSS 功能轮时再迁移 hover preview / context menu 等组件样式。

### 6.4 UI 大文件

高风险大文件仍包括：

- `src/ui/todo_board.py`
- `src/ui/week_window.py`
- `src/ui/month_window.py`
- `src/ui/main_window.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- `src/ui/schedule_detail_pop.py`

已完成低风险拆分：

- `DayBlock`
- `AddFolderCard`
- icon loader
- MainWindow toast helper
- ActionContextMenu

剩余债务：

- `WeekScheduleCard` 未拆。
- `FolderCard` 未拆。
- `TodoBoardWindow` 主状态机未拆。
- `month_window.py` 正在因月界面功能补齐继续增长。
- `add_view.py` / `add_view_week.py` 表单逻辑重复仍未收口。
- `schedule_detail_pop.py` 的 source_view 分支和编辑回流仍高风险。

建议：

- 当前月界面阶段结束前，不再主动拆大 UI 文件。
- 如果 `MonthWindow` 继续膨胀，应优先将持久浮窗组件放入 `src/ui/popups/`，将数据聚合 helper 单独抽出，而不是继续堆入窗口类。

### 6.5 Month View

当前月界面已引入：

- 日期状态角标。
- 今天金色日期。
- 用户选中日期高亮。
- 双击跳日视图。
- hover 只读预览。
- 单击日期持久浮窗壳。
- 添加按钮使用用户选中日期。
- 月界面左侧添加表单壳。
- 时间 picker、提醒 picker、清单 picker 回填。
- 紧急性、重复规则和保存字段对齐。
- 月界面右键菜单，复用 `ActionContextMenu`。

技术债：

- hover cache / marker cache 仍在 `MonthWindow` 内构建。
- 月界面添加表单、picker 栈、日期选择、持久浮窗和右键菜单均集中在 `MonthWindow`，文件继续膨胀。
- `QCalendarWidget.activated(QDate)` 仍承担“双击/激活跳转”职责，并非严格只代表鼠标双击。
- 月界面窄侧栏表单当前属于功能可用但 UI 适配不足状态。
- picker 页面在月界面侧栏中复用后，局部布局需要单独 UI 整理。
- hover 预览和持久浮窗视觉样式仍为局部实现，尚未纳入统一 QSS / skin preset。
- 月格状态角标已经可用，但视觉方案经历多次调整，后续如继续修改应单独作为 UI 工单处理。

建议：

- 月界面功能补齐阶段已经结束，不建议继续向 `M-*` 阶段追加任务。
- 后续若处理月界面，应另开 UI 适配 / 布局债务阶段。
- 优先整理窄侧栏添加表单和 picker 面板布局，不要混入新的数据字段或云同步逻辑。
- 如继续抽离 `MonthWindow`，优先抽取 popup / panel / read-model helper，不要一次性重构整个月界面。

### 6.6 Weather

当前观察到运行期错误：

```text
天气服务错误: Expecting value: line 1 column 1 (char 0)
```

判断：

- 更像网络/API 返回空响应或非 JSON。
- 与月界面 hover / marker / popup 改动无直接关系。

建议：

- 后续可单独开小工单增强 `weather_service` 的响应校验与失败兜底。
- 不应混入月界面功能阶段。

### 6.7 Git / 文档 / 流程

- `manage_instruction/` 当前被 `.gitignore` 忽略，管理文档提交需要 `git add -f`。
- `ReconstructionDolder/` 是旧架构改写归档区，不应继续修改。
- 当前阶段文档应写在 `manage_instruction/` 根目录。

建议：

- 后续所有阶段规划引用本文和 `ReconstructionDolder/Work_Formulation.md`。
- 归档区只读，不再写入。
- 功能阶段完成后再将当前工作文档归档到 History 文件。

---

## 7. 后续阶段建议

推荐顺序：

1. 先确认下一个阶段主题，不再向已归档的月界面功能补齐阶段追加任务。
2. 若以使用体验为优先，建议先做 UI 适配 / 布局债务整理，重点处理月界面窄侧栏和 picker 显示问题。
3. 若以功能闭环为优先，建议优先选择低风险功能，例如导出 / 备份能力。
4. 四象限、换肤、搜索 / 筛选、天气服务失败兜底、表单重复逻辑收口均应单独规划。
5. 云同步属于后续大功能，不建议作为本地个人版完成前的阻塞项。

不建议：

- 在没有阶段规划的情况下直接启动四象限或云同步。
- 在 UI 适配阶段顺手大拆数据层、服务层或 Controller。
- 在功能阶段顺手改数据库结构。
- 在功能阶段伪实现换肤、排序、筛选、同步。
- 把视觉微调和复杂业务链路混在同一个工单中。

---

## 8. 使用规则

后续规划窗口、决策窗口、执行窗口应按以下顺序读取：

1. `manage_instruction/Final_Formulation.md`
2. `manage_instruction/Work_Formulation.md`
3. `manage_instruction/Work_Instruction.md`
4. `manage_instruction/Work_Log.md`
5. `manage_instruction/Work_Task_Prompts.md`
6. 必要时再读取 `manage_instruction/ReconstructionDolder/Work_Formulation.md`

本文作为最终目标和技术债索引；当前阶段细节仍以 `Work_Formulation.md` 和 `Work_Instruction.md` 为准。
