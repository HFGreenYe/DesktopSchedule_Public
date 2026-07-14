# Work Instruction

用途：记录当前待执行的小工单阶段合同。执行窗口只能根据主窗口确认后的最终提示词行动。

---

# 当前状态：搜索 / 筛选第三轮小工单

小工单名称：日界面课表模式搜索与筛选接入。

允许范围：

- `src/ui/dashboard.py`
- `src/ui/main_window.py`
- `manage_instruction/Work_Formulation.md`
- `manage_instruction/Work_Instruction.md`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

目标：

- 允许日课表模式打开既有搜索设置与筛选弹窗。
- 卡片和课表共享查询状态与匹配服务。
- 逐字符输入和条件变化立即更新课表绘制数据。
- 清空关键词后恢复筛选后的课表内容。
- 过滤为空时仍显示课表时间网格。

---

## 当前禁止

- 不接入周界面、月界面、待办和“全部日程”全局结果页。
- 不修改数据库、Repository 和表结构。
- 不新增查询偏好持久化。
- 不修改课表颜色、详情、拖拽、拉伸和右键交互规则。
- 不顺手实现导出、换肤、加密或云同步。
- 不修改 `manage_instruction/ReconstructionDolder/` 历史归档区。

---

## 下一步

本轮完成后先人工验收日课表查询，再决定扩展周 / 月本地查询还是先做“全部日程”全局窗口。
