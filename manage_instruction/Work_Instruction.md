# Work Instruction

用途：本文件用于“当前阶段”的执行指令发布。

- 仅保留正在执行或即将执行的任务。
- 已完成阶段请归档到 `History_Instruction.md`，避免本文件长期堆积。
- 当前主路线图见 `Work_Formulation.md` 的“架构改写轮次路线图”。
- 改写前行为和目录快照见 `Work_Snapshot.md`。
- 执行过程记录写入 `Work_Log.md`。

---

# 当前阶段：第七轮 - Theme / QSS 接入与样式债务控制

## 已完成并归档

- 第一轮：基建 + repository + db_manager 兼容委托。
- 第二轮：Data 层整理与模型拆分。
- 第三轮：纯业务查询与排序服务。
- 第四轮：日程写入与重复规则服务。
- 第五轮：提醒与运行期状态服务。
- 第六轮：Controller / Router / EventBus 协调层。

---

## 第七轮目标

第七轮目标是让主题系统开始真正参与应用，同时控制样式债务，不追求一次性清理全部旧 `setStyleSheet(...)`。

本轮采用“颜色皮肤 / Skin Preset”路线，不按每套皮肤再拆 light/dark 双模式。深色主题可作为一种深色皮肤存在，但本轮不实现完整换肤 UI。

重点范围：

- 复核现有 `ThemeManager`、QSS 文件、`StyleManager`、`setStyleSheet(...)` 分布。
- 在应用启动处接入默认主题 QSS，保持默认视觉尽量不变。
- 建立 QSS 动态属性命名规范，例如 `role`、`state`、`variant`。
- 只选择少量低风险公共控件做样式试点。
- 为后续第八轮 UI 拆分建立样式规范，避免继续复制硬编码样式。

不追求：

- 不批量删除旧内联样式。
- 不一次性重写 `StyleManager`。
- 不实现完整设置页、换肤页、字体/颜色选择闭环。
- 不顺带改第六轮 Controller / Router / EventBus 行为。

---

## 第七轮允许修改范围

第七轮整体允许修改：

- `src/theme/theme_manager.py`
- `src/theme/light.qss`
- `src/theme/dark.qss`
- `src/theme/__init__.py`
- `main.py`（仅在明确小工单中接入默认 QSS）
- `src/utils/signals.py`（仅在明确小工单中使用既有 `theme_changed` / `skin_changed`；不得改旧签名）
- `src/utils/styles.py`（仅在明确小工单中做极小兼容整理）
- 少量低风险 UI 文件（仅在明确小工单列出时做动态属性或试点调用替换）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

默认不修改 UI。只有具体小工单明确列出 UI 文件时，才允许最小样式接入。

---

## 第七轮禁止事项

第七轮整体禁止：

- 不修改 `src/data/`。
- 不修改 `src/repositories/`。
- 不修改 `src/services/`。
- 不修改 `src/controllers/`，除非后续小工单明确需要读取第六轮协调层状态；默认不碰。
- 不修改 `requirements.txt`。
- 不修改 `schedule.db`。
- 不新增数据库字段。
- 不改数据库迁移逻辑。
- 不改 `db_manager` 对外 API。
- 不改业务逻辑。
- 不改路由、刷新、picker、详情弹窗回流行为。
- 不批量替换 UI 文件中的 `setStyleSheet(...)`。
- 不批量移动样式到 QSS。
- 不实现完整主题设置 UI。
- 不实现字体/颜色选择功能闭环。
- 不改变 `global_signals.skin_changed` 无参签名。
- 不改变 `global_signals.theme_changed(str)` 既有签名。
- 不引入新的第三方依赖。
- 不做第八轮 UI 大文件拆分。

---

## 行为保持原则

本轮所有改动必须满足：

- 应用可启动。
- 默认视觉尽量保持，不出现大面积颜色、字体、间距、圆角突变。
- 日、周、月、待办切换行为不变。
- 添加、编辑、删除、提醒、详情弹窗行为不变。
- 第六轮 `ViewRouter`、`MainController`、`RefreshCoordinator`、`refresh_requested` 行为不变。
- 旧 `setStyleSheet(...)` 可以继续存在。
- 新 QSS 只先覆盖明确试点范围，不影响未纳入试点的旧 UI。
- 动态属性刷新必须可验证。

---

## 第七轮小工单拆分

第七轮采用 `7-0`、`7-1` 等编号。执行时可根据 `7-0` 审查结果继续拆分更小工单，不得为了匹配编号一次迁移过多样式。

### 7-0：主题与样式债务静态审查

目标：

- 只读审查当前主题/QSS/内联样式状态，不改源码。
- 建立第七轮样式接入基线。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

审查重点：

- `ThemeManager` 当前能力与缺口。
- `light.qss` / `dark.qss` 当前内容与命名。
- `main.py` 当前 QApplication 启动流程。
- `StyleManager` 当前承担的公共样式。
- `setStyleSheet(...)` 高频分布文件。
- 适合 QSS 试点的低风险控件。
- 不适合本轮处理、应推迟到第八轮 UI 拆分的样式债务。

验收重点：

- 输出样式债务地图。
- 输出可进入 7-1/7-2/7-3 的候选项。
- 确认 `src`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

Work_Log 记录：

- 静态审查命令和结果。
- `ThemeManager` 能力/缺口。
- QSS 文件状态。
- 内联样式热点。
- 低风险试点候选。
- 推迟项及原因。

### 7-1：ThemeManager 与 Skin Preset 边界确认

目标：

- 只完善 ThemeManager 的最小主题边界和命名约定。
- 不接入应用启动。
- 不改 UI。

允许修改：

- `src/theme/theme_manager.py`
- `src/theme/__init__.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `main.py`
- `src/ui/`
- `src/utils/signals.py`
- `src/utils/styles.py`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `requirements.txt`
- `schedule.db`

验收重点：

- `ThemeManager` 可 import。
- 可列出/解析允许的 skin preset，例如 `light.qss`、`dark.qss`。
- 读取 QSS、应用 QSS、刷新动态属性样式能力保持。
- 不引入 UI/db/Repository/Service 依赖。
- diff 范围只包含允许文件。

Work_Log 记录：

- ThemeManager 当前职责边界。
- skin preset 命名规则。
- import / py_compile / 静态依赖验证。
- 未接入应用启动的说明。

### 7-2：默认 QSS 启动接入

目标：

- 在应用启动处接入默认 skin preset。
- 默认视觉尽量保持。
- 不实现换肤 UI。

允许修改：

- `main.py`
- `src/theme/theme_manager.py`（仅在 7-2 验证发现需要极小兼容修正时）
- `src/theme/light.qss`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/ui/`
- `src/utils/signals.py`
- `src/utils/styles.py`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `requirements.txt`
- `schedule.db`

验收重点：

- 应用启动仍可 import / smoke。
- 默认 QSS 加载失败时有明确日志或保守失败方式，不破坏应用启动。
- 不改变窗口结构和业务行为。
- `light.qss` 初始内容应尽量低侵入，只放全局基础规则或空安全规则。
- diff 范围只包含允许文件。

Work_Log 记录：

- 默认 skin preset 名称。
- 接入位置。
- 启动/import 验证。
- 默认视觉风险评估。

### 7-3：动态属性命名规范与刷新验证

目标：

- 建立动态属性命名规范。
- 验证 `ThemeManager.refresh_widget_style(...)` 能刷新动态属性样式。
- 默认不改业务 UI。

允许修改：

- `src/theme/theme_manager.py`
- `src/theme/light.qss`
- `src/theme/dark.qss`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `main.py`（除非只读验证）
- `src/ui/`
- `src/utils/signals.py`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `requirements.txt`
- `schedule.db`

建议规范：

- `role`：组件角色，例如 `primaryButton`、`ghostButton`、`panel`、`input`。
- `state`：状态，例如 `normal`、`active`、`warning`、`danger`。
- `variant`：变体，例如 `compact`、`toolbar`。

验收重点：

- QSS 动态属性选择器存在且语义清楚。
- 使用临时 QWidget/QPushButton 验证 setProperty + refresh_widget_style。
- 不修改真实业务 UI。
- diff 范围只包含允许文件。

Work_Log 记录：

- 动态属性规范。
- QSS 选择器示例。
- 临时控件验证命令和结果。

### 7-4：低风险公共控件样式试点

目标：

- 选择一个低风险公共控件做 QSS 动态属性试点。
- 不批量替换旧样式。
- 不改变业务行为。

允许修改：

- `src/theme/light.qss`
- `src/theme/dark.qss`
- 一个明确列出的低风险 UI 文件（执行提示词必须写死具体文件）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

候选试点优先级：

- 窗口控制按钮的非业务样式。
- tooltip 或 toast 的低风险外观。
- 单个公共按钮 role 动态属性。

禁止修改：

- 未在提示词列出的 UI 文件。
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `main.py`（除非本轮提示词明确需要启动 smoke）
- `requirements.txt`
- `schedule.db`

验收重点：

- 只试点一个小范围。
- 默认视觉变化可控。
- 文案、布局、信号、业务行为不变。
- UI 文件 diff 可解释。

Work_Log 记录：

- 试点控件与文件。
- 替换前旧样式说明。
- 新动态属性/role 说明。
- py_compile / import / 静态 diff 结果。

### 7-5：Theme 信号兼容与手动切换 smoke（不做 UI）

目标：

- 只验证 `ThemeManager` 与既有 `global_signals.theme_changed(str)` / `skin_changed()` 兼容。
- 不实现换肤 UI。
- 不让旧 UI 依赖新信号。

允许修改：

- `src/theme/theme_manager.py`（仅必要兼容修正）
- `src/utils/signals.py`（仅当不改变旧签名且必须补注释/极小兼容时；默认不改）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `main.py`
- `src/ui/`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `requirements.txt`
- `schedule.db`

验收重点：

- `global_signals.skin_changed` 仍无参可 emit。
- `global_signals.theme_changed(str)` 可 emit。
- `ThemeManager` 可手动 apply `light.qss` / `dark.qss` 到临时 QApplication。
- 不修改真实 UI。

Work_Log 记录：

- 信号兼容验证结果。
- 手动切换 smoke 结果。
- 未实现换肤 UI 的说明。

### 7-6：第七轮整体验收与归档准备

目标：

- 汇总第七轮 Theme/QSS 接入结果。
- 明确第八轮 UI 拆分前的样式规范与债务。

允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`

验收重点：

- `ThemeManager` 可 import。
- 默认 QSS 接入可用。
- 动态属性规范已记录。
- 试点控件可回归。
- `skin_changed` / `theme_changed` 兼容。
- 第六轮协调层行为不变。
- `src/data`、`src/repositories`、`src/services`、`src/controllers`、`main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。
- 明确第七轮是否可归档。

Work_Log 记录：

- 7-0 到 7-5 完成摘要。
- 实际接入的主题能力。
- 未迁移样式债务。
- 第八轮 UI 拆分前的样式约束。
- 可归档性结论。

---

## 当前执行要求

- 当前只完成第七轮阶段合同与小工单拆分。
- 执行窗口在收到 `7-0` 正式提示词前，不得自行开始源码改造、数据库改造或管理文档大范围改写。
- 第七轮应避免顺带改动第六轮协调层行为路径。
