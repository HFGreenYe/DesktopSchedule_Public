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

第七轮：Theme / QSS 接入，已完成 7-0（主题与样式债务静态审查），等待顾问窗口复核与 7-1 工单。

## 当前轮次注意事项

- 第六轮已归档，历史记录见 `History_Instruction.md` 与 `History_Log.md`。
- 7-0 已完成，当前仅形成主题接入基线，不包含源码改造。
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
