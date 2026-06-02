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
