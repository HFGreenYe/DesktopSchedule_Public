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
    matrix_classification_service.py   # 坐标显示 / 重要性-紧急性分类纯逻辑
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
  - 换肤、排序、筛选保持占位禁用。

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
  - 换肤、排序、筛选仍为占位或未接入。
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
- 待办看板文字适配小修：
  - 便签视图长标题已改为先换行、再按需缩小字号。
  - pin 图标已固定在左上角，不随标题换行下移。
  - 文件夹视图已增加标题显示宽度约束，避免长名称挤出界面。
- 天气服务失败兜底小修：
  - 天气服务空响应、非 JSON、配置缺失、定位失败和 API 异常已进入 fallback 路径。
  - `HeaderBar`、`WeekWindow`、`MonthWindow` 初始化等待态已使用 `hourglass.svg` 上下翻转 loading。
  - 超时或失败后显示 `assets/weather/999-fill.svg` 与 `--°C`，不再出现 emoji 或普通问号中间态。
- 右键菜单与视图入口细节小修：
  - 主 / 周 / 月视图选择项已移除“四象限”文字。
  - 更多菜单已新增“坐标显示”入口。
  - 页面级右键菜单图标已统一为深灰高 DPR 渲染。

当前未完成但已明确存在的功能缺口：

- 月界面 UI 适配仍明显不足，尤其是窄侧栏添加表单、picker 面板和月历区域的协调。
- 坐标显示看板仍未实现。
- 真实换肤 UI 尚未接入。
- 搜索 / 筛选仍未完整实现。
- 导出功能仍未实现。
- 云同步 / 多设备同步尚未实现，且不应作为当前本地版闭环的前置条件。

后续阶段应先规划再执行，不应直接进入源码修改。候选方向：

- UI 适配 / 布局债务整理。
- 导出 / 备份能力。
- 坐标显示轻量看板。
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

已处理的基础兜底：

- `weather_service` 已对 API 配置缺失、HTTP 错误、空响应、非 JSON、定位失败、天气 API code 异常和关键字段缺失做显式校验。
- 失败时不再向 UI 发空 dict，而是发结构完整的 fallback 数据：
  - `temp = "--"`
  - `icon = "999"`
  - `text = "天气暂不可用"`
  - `city = "未知位置"`
  - `available = False`
  - `error = <失败原因>`
- 成功数据增加 `available = True`。
- `HeaderBar`、`WeekWindow`、`MonthWindow` 初始化等待阶段使用 `assets/icons/hourglass.svg` 做上下翻转过渡，最长 3000ms。
- 沙漏在独立 loading label 内按 78% 尺寸居中绘制，并围绕画布几何中心水平线做上下翻转；weather label 独立显示真实天气 / `999-fill.svg`，避免过渡动画影响正常天气图标位置。
- 若 3000ms 内未收到天气结果，UI 自动切换到 `assets/weather/999-fill.svg`。
- 若 loading 期间先收到 fallback `999-fill.svg`，仍等到 3000ms 后切换；真实天气数据返回时立即停止 loading 并显示真实天气 SVG。
- 若后续收到真实天气数据，UI 停止加载态并显示 API 对应天气 SVG。
- 天气图标加载失败时使用 `assets/weather/999-fill.svg`，不再使用天气 emoji 或普通问号作为中间态。
- 如果 `999-fill.svg` 也异常缺失，则清空天气图标，不再显示普通问号。

仍未实现：

- 不自动重试。
- 不缓存上一次成功天气。
- 不切换备用天气源。
- 不提供用户可见的详细错误面板。

建议：

- 若后续继续增强天气模块，应单独开小工单处理重试、缓存上次成功天气或备用天气源。
- 天气增强不应混入月界面 UI 适配、坐标显示或导出功能阶段。

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

1. 修整月界面的功能 UI。

   整理月界面窄侧栏添加表单、picker 页面、hover 预览、持久浮窗和月历区域的视觉适配；该阶段以布局和可用性为目标，不新增数据字段。

2. 实现坐标显示看板。

   基于已有日程 / 待办数据做第一象限式坐标看板展示，横轴建议为重要性，纵轴建议为时间紧急性。先支持查看、修改、删除，不提供新增入口。实现前必须确认“重要性”字段来源；若当前数据模型不足，应单独规划字段或降级规则。

3. 日界面 / 周界面课程表视图。

   作为新的展示模式实现，优先只读显示和点击详情，不优先做拖拽改时间或拉伸改时长。

4. 搜索 / 筛选功能。

   补齐日程和待办的搜索、筛选入口，优先覆盖标题、日期范围、清单、完成状态、紧急性等基础条件。

5. 实现导出功能。

   导出功能建议分阶段实现，先做结构稳定、低风险的 Markdown，再扩展 PDF 和 PNG。

   目标能力：

   - 支持导出内容类型：
     - 仅日程。
     - 仅待办。
     - 日程 + 待办。
   - 支持日程导出范围：
     - 某日。
     - 某月。
     - 某年。
     - 全部。
   - 支持导出格式：
     - Markdown (`.md`)。
     - PDF (`.pdf`)。
     - PNG (`.png`)。

   推荐实现顺序：

   - `Export-0`：导出需求与数据字段只读审查。

     确认日程、待办、分类、提醒、重复规则、完成状态、紧急性字段的真实存储和显示语义。

   - `Export-1`：建立导出数据模型 / 中间结构。

     建立统一 `ExportPayload` 或等价结构，避免 Markdown / PDF / PNG 各自重复查库和拼数据。

   - `Export-2`：Markdown 导出。

     先实现 `.md` 导出，按日期或清单分组，包含时间、标题、状态、紧急性、重复、提醒、所属清单等基础信息。

   - `Export-3`：导出入口 UI。

     增加导出入口和导出选项，支持选择内容类型、时间范围和导出路径。

   - `Export-4`：PDF 导出。

     基于同一份导出数据模型生成 PDF。优先保证文字内容、分页和中文字体稳定，不追求复杂排版。

   - `Export-5`：PNG 导出。

     PNG 先作为摘要图或海报图能力，不建议一开始支持“全部数据”长图。优先支持某日 / 某月摘要，可后续再支持背景图设置。

   边界约束：

   - 不新增数据库字段。
   - 不修改日程 / 待办写入逻辑。
   - 不把导出逻辑写进大型窗口类。
   - 数据查询和格式组装应放入 service / helper。
   - UI 只负责选择导出范围、格式和保存路径。
   - PNG 背景图属于后续增强，不阻塞 Markdown / PDF。
   - 导出功能可作为后续本地备份 / 云同步的数据结构参考，但本阶段不实现备份恢复和云同步。

6. 实现皮肤功能。

   基于现有 ThemeManager / Skin Preset，接入真实换肤入口，逐步处理内联样式覆盖问题。

7. 本地备份 / 恢复。

    先做本地 JSON 或数据库备份，作为云同步前的数据安全底座。

8. 云功能。

    最后单独规划账号、设备、同步、冲突解决、服务端和安全策略。

可选增强：

- 天气模块可后续单独处理自动重试、缓存上次成功天气、备用天气源或错误详情面板；基础失败兜底已完成，不再作为主线任务。
- 待办看板文字适配已完成当前小修；如后续实际 UI 仍有局部问题，再作为小修处理，不再列为主线任务。

不建议：

- 在没有阶段规划的情况下直接启动坐标显示看板或云同步。
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
