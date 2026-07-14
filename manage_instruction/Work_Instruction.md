# Work Instruction

用途：记录当前待执行的小工单阶段合同。执行窗口只能根据主窗口确认后的最终提示词行动。

---

# 当前状态：搜索 / 筛选第六轮小工单

小工单名称：待办列表搜索与筛选接入。

允许范围：

- `src/ui/todo.py`
- `src/ui/main_window.py`
- `src/ui/header.py`
- `src/ui/popups/day_query_options_panel.py`
- `manage_instruction/Work_Formulation.md`
- `manage_instruction/Work_Instruction.md`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

目标：

- 待办搜索与待办筛选使用独立弹窗和独立状态。
- 待办筛选提供清单和重要性；待办搜索额外提供搜索范围和匹配方式。
- 逐字符关键词和选项变化即时更新待办卡片；清空关键词后恢复待办筛选结果。
- 日界面与待办界面切换时分别恢复各自搜索关键词和筛选高亮。

---

## 当前禁止

- 不修改日、周、月界面既有查询条件和结果规则。
- 不接入独立待办看板窗口和“全部日程”全局结果页。
- 不修改数据库、Repository 和表结构。
- 不新增查询偏好持久化。
- 不增加待办状态、时间形式筛选，不修改待办拖拽、详情和右键规则。
- 不修改 `manage_instruction/ReconstructionDolder/` 历史归档区。

---

## 下一步

本轮完成后先人工验收待办搜索 / 筛选，再决定进入“全部日程”全局窗口。
