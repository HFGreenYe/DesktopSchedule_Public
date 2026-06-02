# Work Formulation

用途：记录当前阶段的总体规划、目标边界和小工单路线。由主窗口在审核决策窗口方案后维护。

---

# 当前阶段：功能补充规划待定

## 1. 已完成阶段

架构改写主线已结束。

右键上下文菜单阶段已完成并归档：

- 主界面日程区域右键菜单。
- 周界面日期空白区域右键菜单。
- 公共 `ActionContextMenu` 组件。
- 添加与视图切换已接入既有入口。
- 换肤、排序、筛选、四象限保持未实现。

归档位置：

- `History_Instruction.md`
- `History_Log.md`

旧架构规划参考：

- `manage_instruction/ReconstructionDolder/Work_Formulation.md`
- `manage_instruction/ReconstructionDolder/History_Instruction.md`
- `manage_instruction/ReconstructionDolder/Workflow_Guide.md`

---

## 2. 下一阶段建议

当前不建议直接启动四象限视图。

优先建议：

- 先完善月界面功能。
- 再制定后续功能补充规划。

月界面候选目标：

- 审查 `src/ui/month_window.py` 当前行为和缺口。
- 补齐月界面点击日期查看/添加日程能力。
- 明确月界面与日视图、周视图、添加页、详情弹窗、刷新链路的关系。
- 完成月界面整体验收。

---

## 3. 当前不做

- 不直接启动四象限视图。
- 不做完整云同步。
- 不做真实换肤 UI 闭环。
- 不做排序和筛选完整功能。
- 不做大范围 UI 重构。
- 不做大范围 QSS 迁移。
- 不重写 `MainWindow` / `WeekWindow` / `TodoBoardWindow`。
- 不改变现有数据库字段，除非后续小工单明确要求并完成迁移方案。

---

## 4. 等待事项

等待下一阶段规划。
