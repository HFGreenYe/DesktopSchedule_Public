# Work Instruction

用途：记录当前待执行的小工单阶段合同。执行窗口只能根据主窗口确认后的最终提示词行动。

---

# 当前状态：搜索 / 筛选第二轮小工单

小工单名称：日界面卡片模式真实搜索与筛选。

允许范围：

- `src/services/schedule_query_service.py`
- `src/ui/dashboard.py`
- `src/ui/header.py`
- `src/ui/main_window.py`
- `src/ui/popups/day_query_options_panel.py`
- `manage_instruction/Work_Formulation.md`
- `manage_instruction/Work_Instruction.md`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

目标：

- 建立不可变查询选项对象和纯匹配服务。
- 接通日界面卡片的清单、重要性、状态、时间形式筛选。
- 接通标题 / 标题加详情、精准 / 模糊搜索。
- 筛选基线与搜索临时快照互不污染。
- 输入每个字符立即重绘当前日期卡片；清空关键词恢复筛选结果。
- 搜索框尾部清空键只在文本非空时显示。

---

## 当前禁止

- 不接入日课表、周界面、月界面、待办和“全部日程”全局结果页。
- 不修改数据库、Repository 和表结构。
- 不新增查询偏好持久化。
- 不顺手实现导出、换肤、加密或云同步。
- 不修改 `manage_instruction/ReconstructionDolder/` 历史归档区。

---

## 下一步

本轮完成后先人工验收 UI 和状态恢复语义，再决定扩展周 / 月本地查询还是先做“全部日程”全局窗口。
