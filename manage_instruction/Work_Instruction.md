# Work Instruction

用途：本文件用于“当前阶段”的执行指令发布。

- 仅保留正在执行或即将执行的任务。
- 已完成阶段请归档到 `History_Instruction.md`，避免本文件长期堆积。
- 当前主路线图见 `Work_Formulation.md` 的“架构改写轮次路线图”。
- 改写前行为和目录快照见 `Work_Snapshot.md`。
- 执行过程记录写入 `Work_Log.md`。

---

# 当前阶段：等待第四轮规划

## 已完成并归档

- 第一轮：基建 + repository + db_manager 兼容委托。
- 第二轮：Data 层整理与模型拆分。
  - 第二轮 A/B/C/D 均已完成并归档。
  - 第二轮最终验收通过，`src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。
- 第三轮：纯业务查询与排序服务。
  - 第三轮 3-0 ~ 3-6 均已完成并归档。
  - 已完成 `ScheduleQueryService`、`ScheduleSortService`、`CategoryPolicyService` 的服务边界和关键纯逻辑抽取。
  - 四象限纯逻辑已完成评估，因规则合同不足，暂未创建 `matrix_classification_service.py`。
  - 第三轮最终验收通过，`src`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

---

## 下一阶段候选：第四轮 - 日程写入与重复规则服务

第四轮尚未发布正式阶段合同。执行窗口在收到第四轮正式提示词前，不得修改源码、数据库或管理文档以外文件。

决策窗口下一步应基于 `Work_Formulation.md` 的“第四轮：日程写入与重复规则服务”拟定阶段合同。

第四轮预计重点：

- 新增或完善 `src/services/schedule_service.py`。
- 迁移或委托 `add_schedule` 相关写入逻辑。
- 迁移或委托 `update_schedule_with_repeat` 相关写入逻辑。
- 梳理 `_add_months` 或重复规则日期计算。
- 明确 `group_id`、`update_future`、`repeat_rule` 的行为基线。

第四轮必须保持：

- 旧 `db_manager` 对外 API 不变。
- 单次日程新增行为不变。
- 每日、每周、每月、每年重复生成行为不变。
- 编辑重复日程时“只改本条/改后续”行为不变。
- 不改变数据库字段含义。
- 不保留 `schedule.db` 变更；如验收需要临时写入，必须清理并确认 `git diff --name-only -- schedule.db` 无输出。

第四轮风险提示：

- 第四轮涉及写入路径与重复规则，是前几轮中风险最高的一轮。
- 必须先做静态审查和行为基线记录，再分小工单抽取，不得直接大范围迁移。
