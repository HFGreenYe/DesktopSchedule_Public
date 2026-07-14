# Work Instruction

用途：记录当前待执行的小工单阶段合同。执行窗口只能根据主窗口确认后的最终提示词行动。

---

# 当前状态：搜索 / 筛选第四轮小工单

小工单名称：周界面星期多选搜索与筛选接入。

允许范围：

- `src/services/schedule_query_service.py`
- `src/ui/week_window.py`
- `src/ui/popups/week_query_options_panel.py`
- `manage_instruction/Work_Formulation.md`
- `manage_instruction/Work_Instruction.md`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

目标：

- 周搜索与周筛选使用独立弹窗和独立状态。
- 新增周一至周日及“全部”八点多选时间范围。
- 逐字符关键词、搜索选项和已应用筛选同步更新卡片与课表。
- 清空关键词后恢复周筛选结果。
- 周范围内跨天日程按每一天的可见列正确保留或排除。

---

## 当前禁止

- 不修改日界面既有查询状态和弹窗布局。
- 不接入月界面、待办和“全部日程”全局结果页。
- 不修改数据库、Repository 和表结构。
- 不新增查询偏好持久化。
- 不修改周课表颜色、详情、拖拽、拉伸和右键交互规则。
- 不修改 `manage_instruction/ReconstructionDolder/` 历史归档区。

---

## 下一步

本轮完成后先人工验收周搜索 / 筛选，再决定进入月界面当前月查询或“全部日程”全局窗口。
