# Work Instruction

用途：记录当前待执行的小工单阶段合同。执行窗口只能根据主窗口确认后的最终提示词行动。

---

# 当前状态：搜索 / 筛选第一轮小工单

小工单名称：日界面卡片模式查询面板入口。

允许范围：

- `src/ui/header.py`
- `src/ui/main_window.py`
- `src/ui/popups/schedule_search_panel.py`
- `manage_instruction/Work_Formulation.md`
- `manage_instruction/Work_Instruction.md`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

目标：

- 主窗口搜索框左侧放大镜可点击。
- 点击后仅在日界面卡片模式显示独立“搜索 / 筛选”面板。
- 面板提供关键词、范围、清单、状态、重要性、日程类型选项和清空 / 应用按钮。
- 本轮不让选项真实过滤日程。

---

## 当前禁止

- 不修改数据库、Repository 或真实查询语义。
- 不接入周界面、月界面、待办和课表模式。
- 不新增搜索 / 筛选偏好持久化。
- 不顺手实现导出、换肤、加密或云同步。
- 不修改 `manage_instruction/ReconstructionDolder/` 历史归档区。

---

## 下一步

本轮完成后先人工验收弹窗位置、样式和开关行为，再决定是否进入真实查询模型接线。
