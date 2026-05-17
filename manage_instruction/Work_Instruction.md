# Work Instruction

用途：本文件用于“当前阶段”的执行指令发布。

- 仅保留正在执行或即将执行的任务。
- 已完成阶段请归档到 `History_Instruction.md`，避免本文件长期堆积。
- 当前主路线图见 `Work_Formulation.md` 的“架构改写轮次路线图”。
- 改写前行为和目录快照见 `Work_Snapshot.md`。
- 执行过程记录写入 `Work_Log.md`。

---

# 当前状态：等待第三轮规划

## 已完成并归档

- 第一轮：基建 + repository + db_manager 兼容委托。
- 第二轮：Data 层整理与模型拆分。
  - 第二轮 A/B/C/D 均已完成并归档。
  - 第二轮最终验收通过，`src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

## 下一轮候选方向

根据 `Work_Formulation.md` 的“架构改写轮次路线图”，下一轮候选为：

- 第三轮：纯业务查询与排序服务。

第三轮目标、允许范围、禁止范围、小工单拆分和验收命令尚未由决策窗口定稿。

## 当前禁止事项

- 执行窗口不得沿用第二轮 D 的旧提示词继续执行。
- 未发布第三轮正式小工单前，不修改源码、不修改数据库、不运行写入型验证。
- 如需准备第三轮，应先由决策窗口生成第三轮阶段合同或首个小工单提示词，再由顾问窗口复核。
