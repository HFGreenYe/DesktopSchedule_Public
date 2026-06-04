# History Instruction

用途：归档已经完成或废弃的阶段合同、执行指令和重要规划结论。

本文件只存历史，不作为当前执行依据。当前执行依据见：

- `Work_Formulation.md`
- `Work_Instruction.md`
- `Work_Task_Prompts.md`

---

## 归档规则

- 每个阶段结束后，由主窗口确认可归档。
- 归档内容应包含阶段目标、允许/禁止范围、关键小工单、验收结论。
- 已归档内容不得在当前阶段直接修改；如需引用，只读查看。
- 旧架构改写阶段的完整历史已移入 `ReconstructionDolder/`。

---

## 当前归档索引

### 2026-06-01：右键上下文菜单阶段

阶段名称：功能补充 - 主界面 / 周界面右键上下文菜单。

归档结论：

- 右键上下文菜单阶段已完成并通过 CM-4 整体验收。
- 本阶段可归档。
- 后续可继续进入月界面功能补齐或新的功能补充规划。

阶段目标：

- 主界面日程空状态区域和列表空白区域支持页面级右键菜单。
- 周界面日期白色空白区域支持页面级右键菜单。
- 菜单采用公共 `ActionContextMenu` 组件。
- 已实装动作：
  - 添加
  - 日 / 周 / 月 / 待办视图切换
- 保持禁用或占位：
  - 换肤
  - 排序
  - 筛选
  - 四象限视图

关键小工单：

- `CM-0`：右键菜单现状审查与精确边界。
- `CM-1`：公共 icon-text 上下文菜单组件试点。
- `CM-2`：主界面日程区域右键菜单接入。
- `CM-3`：周界面日期空白区域右键菜单接入。
- `CM-4`：右键上下文菜单整体验收与归档准备。

关键提交：

- `8a6c551 docs: record cm-0 context menu boundary review`
- `6fb847f refactor: add reusable action context menu`
- `3481655 feat: add dashboard context menu bridge`
- `76f2f94 feat: add week empty area context menu`
- `bae834e docs: close context menu validation`

保留边界：

- 未实现真实换肤 UI。
- 未实现排序和筛选完整功能。
- 未实现四象限视图。
- 未修改数据库字段。
- 未改变 `ScheduleCard` / `WeekScheduleCard` 既有右键菜单。
- 未改变周界面左键选中、双击跳日视图和卡片拖拽排序。

---

### 2026-06-04：月界面功能补齐阶段

阶段名称：功能补充 - 月界面功能补齐。

归档结论：

- 月界面功能补齐阶段已完成并通过 M-7 整体验收。
- 本阶段可归档。
- 后续不应继续在本阶段追加零散功能，应进入下一阶段规划或单独开启 UI 适配阶段。

阶段目标：

- 月格显示日程状态摘要，不在小格内塞完整日程文本。
- 今天只用日期数字金色表示，不再默认整格高亮。
- 单击日期表示用户选中，选中态使用整格高亮。
- 双击 / activated 日期跳转对应日视图，并关闭所有月界面持久浮窗。
- hover 日期显示只读预览，移出后隐藏。
- 单击日期显示月界面外侧持久 panel。
- 添加按钮优先使用用户选中日期，过去日期不可添加。
- 月界面左侧添加表单补齐 time / alarm / list picker 承接和保存结构。
- 月界面右键菜单复用 `ActionContextMenu`，只实装“添加”和“视图”。

关键小工单：

- `M-0`：月界面现状审查与交互边界定位。
- `M-1`：月格状态 marker 与今天金色日期。
- `M-2`：月格单击选中与双击跳日视图。
- `M-3`：hover 只读预览弹窗。
- `M-4`：单击日期持久 panel 壳。
- `M-5`：添加按钮使用选中日期。
- `M-5b`：月界面添加表单能力只读审查与 picker 承接方案确认。
- `M-5c`：月界面添加表单 UI 壳补齐。
- `M-5d`：月界面 time picker 接入。
- `M-5e`：月界面 alarm / list picker 接入。
- `M-5f`：月界面 priority / repeat / 保存结构对齐。
- `M-5g`：月界面添加能力整体验收。
- `M-6`：月界面右键菜单接入。
- `M-7`：月界面功能补齐整体验收。

关键提交：

- `ba1a7f5 docs: plan month view feature phase`
- `1057220 docs: record m-0 month view boundary review`
- `0d3f375 feat: add month view schedule markers`
- `44bff9f feat: update month date click behavior`
- `9002bd7 feat: add month day hover preview`
- `de35fe7 feat: add month day persistent panel shell`
- `4726625 feat: use selected month date for add action`
- `20eb377 feat: add month add form shell`
- `c7db4fa feat: connect month add time picker`
- `af76634 feat: connect month add alarm and list pickers`
- `bd0c378 feat: align month add save fields`
- `166b2c3 feat: add month view context menu`
- `742b6be docs: close month view feature validation`

保留边界：

- 未实现四象限视图。
- 未实现真实换肤 UI。
- 未实现排序和筛选完整功能。
- 未修改数据库字段。
- 未进行像素级 UI 适配和布局重排。
- 未做真实写库自动化验收；保存结构通过 mock / monkeypatch 验证。
- 周视图右键切换仍不携带“跳到指定周”的上下文，保持既有主路由边界。
