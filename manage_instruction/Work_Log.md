# Work Log

本文件只记录当前阶段/当前轮次的执行日志。

历史日志已归档到 `manage_instruction/History_Log.md`。

## 当前状态

第一轮：基建 + repository + db_manager 兼容委托，已完成并归档。

第二轮：Data 层整理与模型拆分，已完成并归档。

第三轮：纯业务查询与排序服务，已完成并归档。

第四轮：日程写入与重复规则服务，已完成并归档。

第五轮：提醒与运行期状态服务，已完成并归档。

第六轮：Controller / Router / EventBus 协调层，已完成并归档。

第七轮：Theme / QSS 接入，已完成 7-4（低风险真实控件动态属性样式试点），等待顾问窗口复核与 7-5 工单。

## 当前轮次注意事项

- 第六轮已归档，历史记录见 `History_Instruction.md` 与 `History_Log.md`。
- 7-0、7-1、7-2、7-3、7-3b、7-4 已完成，已完成单个真实控件试点，尚未扩大到其他控件或页面。
- 第七轮后续应保持第六轮回归重点不变：路由决策、添加页来源、三连刷新、`refresh_requested` 并行通知、详情弹窗回流链路。

## 2026-05-26 第七轮 7-0（主题与样式债务静态审查）

- 本轮任务名称：第七轮 7-0（主题与样式债务静态审查）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 11]`
  - 既有变更：`M manage_instruction/Work_Task_Prompts.md`
  - 说明：开工前已有管理文档 diff，本轮不视为源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 读取的第七轮阶段合同结论：
  - 第七轮以 Theme/QSS 小步接入为目标，先做静态审查，不批量清理内联样式，不改业务逻辑。

- 静态搜索命令与关键结果：
  - `Get-ChildItem src/theme`：`theme_manager.py/light.qss/dark.qss/__init__.py` 均存在，`__init__.py` 为空。
  - `rg -n "ThemeManager|...|theme"`：`ThemeManager` 仅定义未接入 `main.py`；`light.qss/dark.qss` 均为 placeholder 注释；`signals.py` 存在 `skin_changed/theme_changed`。
  - `rg -n "setStyleSheet\\(" src`：全项目大量内联样式。
  - `rg -c "setStyleSheet\\("` 热点计数：
    - `todo_board.py:58`
    - `week_window.py:42`
    - `schedule_detail_pop.py:25`
    - `month_window.py:24`
    - `add_view.py:24`
    - `add_view_week.py:20`
    - `list_picker.py:19`
    - `header.py:10`
    - `main_window.py:3`
    - `calendar_pop.py:2`
  - `rg -n "StyleManager\\.|get_..."`：`StyleManager` 在 header/week/month/time/list/components/suspend/main 等多处被调用。
  - `rg -n "setProperty\\(|property\\(|role|state|variant"`：存在 `minutes/delta` 这类功能属性；未形成统一 `role/state/variant` 动态样式体系。
  - `rg -n "设置字体|btn_font|theme_color|font|color"`：`add_view/add_view_week` 有“设置字体”按钮入口；`Schedule.theme_color` 字段存在，但无完整主题闭环。

- ThemeManager 能力/缺口清单：
  - 已有能力：
    - 可读取 QSS（`read_qss`）。
    - 可应用到 `QApplication`（`apply_qss/apply_theme`）。
    - 可刷新单个 `QWidget` 样式（`refresh_widget_style`）。
  - 缺口：
    - 无 skin preset 列表/校验与默认主题名策略。
    - 无读取失败兜底（文件不存在将抛异常）。
    - 无 apply 结果状态/日志接口。
    - 仅支持单 widget 刷新，缺少批量刷新约定。
  - 依赖边界：
    - 依赖 Qt（`QApplication/QWidget`），不依赖 UI/db/Repository。
  - 接入现状：
    - `main.py` 未接入 ThemeManager，应用启动仅 `app.setStyle("Fusion")`。

- QSS 文件状态：
  - `light.qss`：placeholder 注释，无实质规则。
  - `dark.qss`：placeholder 注释，无实质规则。
  - 当前无动态属性选择器（如 `[role=...]`）。
  - 当前无全局基础规则，不能直接承担生产级统一样式。

- main.py 启动流程中的主题接入现状：
  - 启动流程：创建 `QApplication` -> `setApplicationName` -> `setStyle("Fusion")` -> `MainWindow.show()`。
  - 无 QSS 加载、无 ThemeManager 实例化、无主题失败兜底。

- StyleManager 职责地图：
  - 提供公共样式方法：窗口背景/玻璃态/button/menu/header/search/tool/window-control/tooltip/calendar。
  - 实际使用：header/week/month/time/list/components/suspend/main 等文件直接拼接调用。
  - 并存问题：
    - 一部分公共样式已集中在 `StyleManager`。
    - 大量页面仍以内联 `setStyleSheet` 为主，样式源分散。

- setStyleSheet 热点文件与热点类型：
  - 高频页面：`todo_board.py`、`week_window.py`、`schedule_detail_pop.py`、`add_view*.py`、`month_window.py`、`list_picker.py`。
  - 热点类型：
    - 按钮 hover/pressed 样式。
    - 标题/文字字体与颜色。
    - 卡片背景、边框、圆角。
    - toast/tooltip 局部样式。
    - page 级大块样式初始化。

- 动态属性使用现状：
  - 已见 `setProperty("minutes")`、`setProperty("delta")`，用于时间逻辑，不是主题 role/state 规范。
  - 尚未形成统一 `role/state/variant` 命名与 QSS 对应选择器体系。

- `skin_changed/theme_changed` 信号现状：
  - `skin_changed = pyqtSignal()`（无参兼容保留）。
  - `theme_changed = pyqtSignal(str)`（存在但未见主题接入链路）。
  - `refresh_requested = pyqtSignal(str)` 为第六轮并行通知，不是主题链路。

- `theme_color/设置字体` 既有缺口：
  - `Schedule.theme_color` 字段存在（模型层）。
  - `add_view/add_view_week` 有 `btn_font`（“设置字体”）入口，但无完整持久化-渲染闭环。
  - 该能力跨 UI+数据+详情页显示，非第七轮低风险项。

- 低风险试点候选项（建议 7-4）：
  - tooltip 样式统一（先从 `StyleManager.get_tooltip_style` 映射到轻量 QSS 规则）。
  - 窗口控制按钮（more/sync/close）增加 `role` 动态属性试点。
  - Header 单个非业务按钮/输入框（局部、可回滚）。

- 中/高风险样式债务：
  - 中风险：
    - Header 与 ListPicker 局部控件替换（涉及多处重复拼接）。
  - 高风险：
    - `add_view.py/add_view_week.py` 全面样式迁移。
    - `todo_board.py/week_window.py/month_window.py` 大块内联重构。
    - `calendar_pop.py` 自带 light/dark 切换逻辑与主主题体系冲突。
    - `schedule_detail_pop.py` 复杂 source_view 分支样式。
    - `theme_color/设置字体` 功能闭环。

- 建议推迟到第八轮 UI 拆分或第九轮功能轮：
  - `todo_board/week_window/main_window` 大文件样式结构清理（第八轮）。
  - `schedule_detail_pop` 样式与 source_view 分支重构（第八轮后）。
  - `theme_color/设置字体` 端到端能力（第九轮功能轮）。

- 对后续 7-1/7-2/7-3/7-4 建议：
  - 7-1：
    - 给 ThemeManager 增加 skin preset 白名单、默认 skin 常量、读取失败兜底返回空样式或保守日志。
  - 7-2：
    - 启动默认接入 `light.qss`，先保持低侵入（可为空安全规则），保证视觉不突变。
  - 7-3：
    - 定义动态属性命名：`role/state/variant`；
    - 先用临时控件验证 `setProperty + refresh_widget_style` 闭环，不触碰业务 UI。
  - 7-4：
    - 仅选一个低风险控件试点，优先“窗口控制按钮 role 动态属性”。
    - 不建议一次性迁移 `add_view` 或 `todo_board`。

- diff 范围检查结果：
  - `git diff --name-only -- src`：无输出。
  - `git diff --name-only -- main.py`：无输出。
  - `git diff --name-only -- requirements.txt`：无输出。
  - `git diff --name-only -- schedule.db`：无输出。
  - 当前总 diff 仅管理文档：`manage_instruction/Work_Log.md`（本轮）+ `manage_instruction/Work_Task_Prompts.md`（开工前既有）。

- 未完成事项：
  - 进入 7-1 前需确定 skin preset 命名和失败兜底策略。
  - 进入 7-4 前需在顾问窗口确认唯一试点控件，避免范围扩散。

- 风险或疑点：
  - `calendar_pop.py` 内部主题切换与第七轮统一 ThemeManager 可能冲突，需要后续明确整合策略。
  - 现有大量内联样式与少量 StyleManager 共存，若无严格分批策略，容易出现视觉回归。

## 2026-05-26 第七轮 7-1（ThemeManager 与 Skin Preset 边界确认）

- 本轮任务名称：第七轮 7-1（ThemeManager 与 Skin Preset 边界确认）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 12]`
  - 既有变更：`M manage_instruction/Work_Task_Prompts.md`
  - 说明：开工前已有管理文档 diff，本轮不视为源码改动。
- 实际修改文件：
  - `src/theme/theme_manager.py`
  - `src/theme/__init__.py`
  - `manage_instruction/Work_Log.md`

- ThemeManager 新增/调整的方法清单：
  - 常量：
    - `DEFAULT_PRESET = "light.qss"`
    - `SUPPORTED_PRESETS = ("light.qss", "dark.qss")`
  - 新增：
    - `get_available_presets() -> tuple[str, ...]`
    - `is_supported_preset(file_name: str) -> bool`
    - `resolve_preset(file_name: str | None) -> str`
    - `read_qss_safe(file_name: str | None, fallback: str = "") -> str`
  - 调整：
    - `apply_theme(app, file_name)` 改为 `apply_theme(app, file_name: str | None)`，内部改为 `resolve_preset + read_qss_safe + apply_qss` 组合。
  - 保持：
    - `read_qss`、`apply_qss`、`refresh_widget_style` 保留兼容语义。

- skin preset 白名单与默认 preset：
  - 白名单：`("light.qss", "dark.qss")`
  - 默认：`"light.qss"`

- 非法 preset 回落策略：
  - `resolve_preset` 仅负责合法性判断。
  - 非法值或 `None` 均回落到 `DEFAULT_PRESET`。

- QSS 读取失败兜底策略：
  - `read_qss_safe` 只捕获读取相关异常：`OSError`、`UnicodeDecodeError`。
  - 读取失败返回调用方提供的 `fallback`（默认空字符串）。
  - 未使用宽泛 `except Exception`。

- `apply_theme` 兼容行为说明：
  - 通过 `resolve_preset` 获取 preset。
  - 通过 `read_qss_safe` 读取内容（失败时可返回空字符串）。
  - 始终调用 `apply_qss(app, qss_content)`，保持当前 smoke 可不中断流程。
  - 7-2 启动接入前仍需确认“读取失败时应用空样式”与“保留当前样式”的最终策略。

- `refresh_widget_style` 可用性：
  - 保持原实现未改：`unpolish -> polish -> update`。

- `__init__.py` 导出说明：
  - 增加轻量导出：
    - `from .theme_manager import ThemeManager`
    - `__all__ = ["ThemeManager"]`
  - 无副作用（不创建 QApplication，不读取文件，不连信号）。

- 验证命令与结果：
  - import 验证：
    - 命令：`python -c "from src.theme.theme_manager import ThemeManager; from src.theme import ThemeManager as ThemeManager2; ..."`
    - 结果：`theme manager import ok True`
  - 行为验证（白名单/回落/安全读取）：
    - 结果：
      - `presets ('light.qss', 'dark.qss')`
      - `resolve light light.qss`
      - `resolve bad light.qss`
      - `light len 104`
      - `missing len 0`
  - QApplication apply 烟测（offscreen）：
    - 结果：
      - `applied light True`
      - `applied missing fallback True`
  - 静态依赖检查：
    - 命令：`rg -n "src\.ui|MainWindow|...|CategoryRepository" src/theme/theme_manager.py src/theme/__init__.py`
    - 结果：无输出（`rg` 退出码 1，按预期通过）。
  - py_compile：
    - 命令：`python -m py_compile src/theme/theme_manager.py src/theme/__init__.py`
    - 结果：通过。

- diff 范围检查结果：
  - `git diff --name-only -- src/theme/light.qss`：无输出。
  - `git diff --name-only -- src/theme/dark.qss`：无输出。
  - `git diff --name-only -- main.py`：无输出。
  - `git diff --name-only -- src/ui`：无输出。
  - `git diff --name-only -- src/utils/signals.py`：无输出。
  - `git diff --name-only -- src/utils/styles.py`：无输出。
  - `git diff --name-only -- src/data`：无输出。
  - `git diff --name-only -- src/repositories`：无输出。
  - `git diff --name-only -- src/services`：无输出。
  - `git diff --name-only -- src/controllers`：无输出。
  - `git diff --name-only -- requirements.txt`：无输出。
  - `git diff --name-only -- schedule.db`：无输出。
  - 最终 diff：
    - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
    - `src/theme/__init__.py`
    - `src/theme/theme_manager.py`
    - `manage_instruction/Work_Log.md`

- 未完成事项：
  - 7-2 需在启动接入时最终确认 QSS 读取失败的默认处理策略（空样式 vs 保留当前样式）。
  - 7-3 需定义并验证 `role/state/variant` 动态属性规范。

- 风险或疑点：
  - 当前 fallback 使用空字符串时，若在启动期应用会清空应用级 QSS；虽然本轮未接入 `main.py`，但 7-2 需谨慎处理默认行为。

## 2026-05-26 第七轮 7-2（默认 QSS 启动接入）

- 本轮任务名称：第七轮 7-2（默认 QSS 启动接入）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 13]`
  - 既有变更：`M manage_instruction/Work_Task_Prompts.md`
  - 说明：开工前已有管理文档 diff，本轮不视为源码改动。
- 实际修改文件：
  - `main.py`
  - `manage_instruction/Work_Log.md`

- 默认 skin preset 名称：
  - `ThemeManager.DEFAULT_PRESET = "light.qss"`。

- `main.py` 接入位置：
  - 在 `QApplication` 创建与 `app.setStyle("Fusion")` 之后、`MainWindow()` 之前新增：
    - `theme_manager = ThemeManager()`
    - `theme_manager.apply_theme(app, ThemeManager.DEFAULT_PRESET)`
  - 保持原启动流程与业务路径不变。

- 是否修改 `ThemeManager`：
  - 否。本轮未修改 `src/theme/theme_manager.py`。

- 是否修改 `light.qss`：
  - 否。本轮未修改 `src/theme/light.qss`，保持低侵入占位内容。

- QSS 读取失败时的启动期处理策略：
  - 采用 7-1 已有保守兜底：`apply_theme -> read_qss_safe(..., fallback="")`。
  - 读取失败时应用空字符串样式，不阻断启动流程。
  - 后续 7-3/7-4 前保留该策略，7-2 不扩展复杂主题错误处理系统。

- 验证结果：
  - 读取接入位置：
    - `rg -n "ThemeManager|apply_theme|DEFAULT_PRESET|setStyle\\(" main.py src/theme/theme_manager.py`
    - 命中 `main.py` 新接入点，`theme_manager.py` 常量与方法命中正常。
  - ThemeManager import 验证：
    - `theme import ok light.qss light.qss`
  - main import 验证（offscreen）：
    - `main import ok`
  - QApplication 启动接入 smoke（offscreen）：
    - `default preset light.qss`
    - `before len 0`
    - `after len 104`
    - `stylesheet type ok True`
  - QSS 文件验证：
    - `qss len 104`
  - py_compile：
    - `python -m py_compile main.py src/theme/theme_manager.py src/theme/__init__.py` 通过。

- diff 范围检查结果：
  - `git diff --name-only -- src/ui`：无输出。
  - `git diff --name-only -- src/utils/signals.py`：无输出。
  - `git diff --name-only -- src/utils/styles.py`：无输出。
  - `git diff --name-only -- src/theme/dark.qss`：无输出。
  - `git diff --name-only -- src/data`：无输出。
  - `git diff --name-only -- src/repositories`：无输出。
  - `git diff --name-only -- src/services`：无输出。
  - `git diff --name-only -- src/controllers`：无输出。
  - `git diff --name-only -- requirements.txt`：无输出。
  - `git diff --name-only -- schedule.db`：无输出。
  - 当前总 diff：
    - `main.py`
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`（开工前既有）

- 未完成事项：
  - 7-3 需建立 `role/state/variant` 动态属性规范与刷新验证。
  - 7-4 需选择单一低风险控件做样式试点，避免范围扩散。

- 风险或疑点：
  - 读取失败时“应用空样式”在更复杂接入场景下可能清空既有应用级样式；当前因 `light.qss` 可读且接入点位于启动早期，风险可控。

## 2026-05-26 第七轮 7-3（动态属性命名规范与刷新验证）

- 本轮任务名称：第七轮 7-3（动态属性命名规范与刷新验证）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 14]`
  - 既有变更：`M manage_instruction/Work_Task_Prompts.md`
  - 说明：开工前已有管理文档 diff，本轮不视为源码改动。
- 实际修改文件：
  - `src/theme/light.qss`
  - `src/theme/dark.qss`
  - `manage_instruction/Work_Log.md`

- 动态属性命名规范：
  - `role`：组件角色（`primaryButton`、`ghostButton`、`panel`、`input`）
  - `state`：语义状态（`normal`、`active`、`warning`、`danger`）
  - `variant`：视觉变体（`compact`、`toolbar`）

- `light.qss` 新增选择器说明（仅动态属性选择器，低侵入）：
  - `QPushButton[role="primaryButton"]`
  - `QPushButton[role="ghostButton"]`
  - `QWidget[role="panel"]`
  - `*[state="warning"]`
  - `*[state="danger"]`
  - `*[variant="compact"]`
  - 说明：未新增全局 `QWidget/QPushButton/QLabel` 默认规则，避免影响未设置属性的旧 UI。

- `dark.qss` 新增选择器说明（与 light 同名规范）：
  - `QPushButton[role="primaryButton"]`
  - `QPushButton[role="ghostButton"]`
  - `QWidget[role="panel"]`
  - `*[state="warning"]`
  - `*[state="danger"]`
  - `*[variant="compact"]`
  - 说明：仅用于深色 preset 下的同名属性 smoke，不等于完整深色主题实现。

- 是否修改 `ThemeManager`：
  - 否。本轮未修改 `src/theme/theme_manager.py`，现有 `refresh_widget_style(...)` 即可完成闭环验证。

- 验证结果：
  - 选择器定位：
    - `rg -n "role=|state=|variant=|primaryButton|ghostButton|panel|warning|danger|compact" src/theme/light.qss src/theme/dark.qss` 命中正常。
  - ThemeManager import：
    - `theme import ok light.qss ('light.qss', 'dark.qss')`
  - 临时控件动态属性刷新 smoke（light）：
    - `dynamic property refresh ok primaryButton warning panel compact`
  - dark preset 动态属性 smoke：
    - `dark dynamic refresh ok ghostButton danger True`
  - 默认启动接入回归：
    - `main import ok`
  - py_compile：
    - `python -m py_compile main.py src/theme/theme_manager.py src/theme/__init__.py` 通过。

- diff 范围检查结果：
  - `git diff --name-only -- main.py`：无输出。
  - `git diff --name-only -- src/ui`：无输出。
  - `git diff --name-only -- src/utils/signals.py`：无输出。
  - `git diff --name-only -- src/utils/styles.py`：无输出。
  - `git diff --name-only -- src/data`：无输出。
  - `git diff --name-only -- src/repositories`：无输出。
  - `git diff --name-only -- src/services`：无输出。
  - `git diff --name-only -- src/controllers`：无输出。
  - `git diff --name-only -- requirements.txt`：无输出。
  - `git diff --name-only -- schedule.db`：无输出。
  - 当前总 diff：
    - `src/theme/light.qss`
    - `src/theme/dark.qss`
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`（开工前既有）

- 未完成事项：
  - 7-4 需仅选择一个低风险真实业务控件做试点，避免范围扩散。
  - 需明确 7-4 是先做 window-control 按钮还是 tooltip 单点试点。

- 风险或疑点：
  - 当前 `*[state=...]` 规则在未来大范围使用时可能与个别控件已有边框/前景色叠加；本轮仅作为命名规范与闭环验证，未接入真实业务 UI。

## 2026-05-26 第七轮 7-3b（Skin Preset 命名语义收口）

- 本轮任务名称：第七轮 7-3b（Skin Preset 命名语义收口）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 15]`
  - 既有变更：`M manage_instruction/Work_Task_Prompts.md`
  - 说明：开工前已有管理文档 diff，本轮不视为源码改动。
- 实际修改文件：
  - `src/theme/theme_manager.py`
  - `src/theme/default.qss`（新增）
  - `src/theme/light.qss`
  - `src/theme/dark.qss`
  - `manage_instruction/Work_Log.md`

- 最终默认 preset 名称：
  - `default.qss`

- `SUPPORTED_PRESETS` 清单：
  - `("default.qss", "light.qss", "dark.qss")`

- `light.qss` / `dark.qss` 兼容定位说明：
  - `light.qss`：legacy compatibility preset（历史命名保留）。
  - `dark.qss`：legacy/test preset（兼容/测试用途），不代表每个皮肤都需要暗色版本。
  - 两者均保留读取能力，不删除，避免破坏历史 smoke 与兼容路径。

- 是否新增 `default.qss`：
  - 是。新增 `src/theme/default.qss` 作为 canonical 默认皮肤 preset。
  - 内容采用与 7-3 同步的动态属性选择器语义（`role/state/variant`），低侵入，不建立全局样式 matrix。

- 是否修改 `main.py`：
  - 否。`main.py` 已通过 `ThemeManager.DEFAULT_PRESET` 间接读取默认 preset，不需要硬编码文件名，兼容 7-3b 收口。

- `resolve_preset(None)` 与非法值回落结果：
  - `resolve_preset(None) -> "default.qss"`
  - `resolve_preset("bad.qss") -> "default.qss"`

- 默认 QSS 读取验证结果：
  - `default qss len 1136`
  - 类型 `str`，长度大于 0，验证通过。

- 兼容 preset 读取验证结果：
  - `light len 1166`
  - `dark len 1031`
  - 两者均可安全读取，类型为 `str`。

- 动态属性刷新回归结果：
  - offscreen 临时控件验证通过：
    - `default skin dynamic refresh ok primaryButton warning panel compact`

- 默认启动接入回归结果：
  - `main import ok`（offscreen）通过。

- py_compile 结果：
  - `python -m py_compile main.py src/theme/theme_manager.py src/theme/__init__.py` 通过。

- diff 范围检查结果：
  - `git diff --name-only -- src/ui`：无输出。
  - `git diff --name-only -- src/utils/signals.py`：无输出。
  - `git diff --name-only -- src/utils/styles.py`：无输出。
  - `git diff --name-only -- src/data`：无输出。
  - `git diff --name-only -- src/repositories`：无输出。
  - `git diff --name-only -- src/services`：无输出。
  - `git diff --name-only -- src/controllers`：无输出。
  - `git diff --name-only -- requirements.txt`：无输出。
  - `git diff --name-only -- schedule.db`：无输出。
  - 当前总 diff：
    - `src/theme/theme_manager.py`
    - `src/theme/default.qss`
    - `src/theme/light.qss`
    - `src/theme/dark.qss`
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`（开工前既有）

- 特别记录（语义收口结论）：
  - 第七轮采用 Skin Preset 路线。
  - 本轮不建立 light/dark mode matrix。
  - `dark.qss` 不代表每个皮肤都需要暗色版本。
  - 后续 7-4 控件试点应基于默认 skin preset，而不是基于 light/dark 模式切换。

- 未完成事项：
  - 7-4 仅选择一个低风险真实业务控件做试点，保持改动单点可回滚。

- 风险或疑点：
  - 当前 `default/light/dark` 三个 preset 规则仍有重复，后续若继续扩展 preset 需要避免重复维护（建议后续再考虑抽取共用片段，但不在本轮执行）。

## 2026-05-26 第七轮 7-4（低风险真实控件动态属性样式试点）

- 本轮任务名称：第七轮 7-4（低风险真实控件动态属性样式试点）。
- 开工前 git 状态：
  - `## main...temp/main [ahead 16]`
  - 既有变更：`M manage_instruction/Work_Task_Prompts.md`
  - 说明：开工前已有管理文档 diff，本轮不视为源码改动。
- 实际修改文件：
  - `src/theme/default.qss`
  - `src/ui/header.py`
  - `manage_instruction/Work_Log.md`

- 试点控件：
  - 文件：`src/ui/header.py`
  - 控件：`btn_sync`

- 选择该控件原因：
  - 窗口控制区单点控件，低风险、可回滚。
  - 不涉及数据库写入、路由切换、详情弹窗回流和复杂刷新链路。

- `default.qss` 新增选择器说明（仅单点试点，不做全局 QToolButton 规则）：
  - `QToolButton[role="windowControl"][variant="toolbar"]`
  - `QToolButton[role="windowControl"][variant="toolbar"]:hover`
  - `QToolButton[role="windowControl"][variant="toolbar"]:pressed`
  - 样式对齐原窗口控制按钮视觉：`transparent / no border / radius 6 / hover rgba(255,255,255,0.2) / pressed rgba(255,255,255,0.3)`。

- `btn_sync` 动态属性设置：
  - `role = "windowControl"`
  - `variant = "toolbar"`
  - `state = "normal"`

- 是否清除或避免 `btn_sync` 局部 stylesheet：
  - 是。对 `btn_sync` 单独执行 `setStyleSheet("")`，用于移除 `_create_control_btn(...)` 赋予的局部样式覆盖，让应用级 `default.qss` 动态属性规则生效。
  - 仅作用于 `btn_sync`，未改 `btn_more` / `btn_close` 逻辑。

- 确认未修改 `btn_more` / `btn_close` 行为：
  - 未修改 `btn_more` 点击菜单连接。
  - 未修改 `btn_close` 的 close 连接。
  - 未修改 header 布局结构。

- 验证结果：
  - 选择器定位：
    - `rg -n "windowControl|variant=\"toolbar\"|role=\"windowControl\"|QToolButton\\[role" ...` 命中正常。
  - 轻量检查：
    - `git diff --name-only -- src/theme/light.qss`：无输出。
    - `git diff --name-only -- src/theme/dark.qss`：无输出。
  - Header import：
    - `header import ok <class 'src.ui.header.HeaderBar'>`
  - Header offscreen 实例化与属性验证：
    - 初次按原命令 `HeaderBar()` 会因 `parent_window=None` 且 `btn_close.clicked.connect(self.parent_window.close)` 引发 `AttributeError`（验证脚本环境问题，不是本轮逻辑回归）。
    - 使用 `QWidget` 作为 parent 重跑通过：
      - `has sync True`
      - `sync role windowControl`
      - `sync variant toolbar`
      - `sync state normal`
  - 默认启动接入回归：
    - `main import ok`
  - py_compile：
    - `python -m py_compile src/ui/header.py main.py src/theme/theme_manager.py src/theme/__init__.py` 通过。

- 特别记录：
  - 本轮基于 `default.qss / skin preset`。
  - 本轮不围绕 `light.qss` / `dark.qss` 做模式切换。
  - 本轮只做单个真实控件试点，不做全局控件样式。
  - 后续若要扩大范围，必须另开小工单。

- diff 范围检查结果：
  - `git diff --name-only -- src/theme/light.qss`：无输出。
  - `git diff --name-only -- src/theme/dark.qss`：无输出。
  - `git diff --name-only -- src/theme/theme_manager.py`：无输出。
  - `git diff --name-only -- main.py`：无输出。
  - `git diff --name-only -- src/utils/signals.py`：无输出。
  - `git diff --name-only -- src/utils/styles.py`：无输出。
  - `git diff --name-only -- src/data`：无输出。
  - `git diff --name-only -- src/repositories`：无输出。
  - `git diff --name-only -- src/services`：无输出。
  - `git diff --name-only -- src/controllers`：无输出。
  - `git diff --name-only -- requirements.txt`：无输出。
  - `git diff --name-only -- schedule.db`：无输出。
  - `git diff --name-only -- src/ui`：仅 `src/ui/header.py`。
  - 当前总 diff：
    - `src/theme/default.qss`
    - `src/ui/header.py`
    - `manage_instruction/Work_Log.md`
    - `manage_instruction/Work_Task_Prompts.md`（开工前既有）

- 未完成事项：
  - 若进入 7-5，应做 Theme 信号兼容与手动切换 smoke，不扩大控件范围。
  - 若进入后续试点，应继续单控件单文件策略，避免跨页面并行改造。

- 风险或疑点：
  - `header.py` 当前构造函数对 `parent_window` 存在隐式依赖（`btn_close` 连接 close）；离线实例化测试需提供 parent。该问题为既有结构特点，本轮未改变行为。
