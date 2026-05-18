# Work Instruction

用途：本文件用于“当前阶段”的执行指令发布。

- 仅保留正在执行或即将执行的任务。
- 已完成阶段请归档到 `History_Instruction.md`，避免本文件长期堆积。
- 当前主路线图见 `Work_Formulation.md` 的“架构改写轮次路线图”。
- 改写前行为和目录快照见 `Work_Snapshot.md`。
- 执行过程记录写入 `Work_Log.md`。

---

# 当前阶段：等待第五轮规划

## 已完成并归档

- 第一轮：基建 + repository + db_manager 兼容委托。
- 第二轮：Data 层整理与模型拆分。
- 第三轮：纯业务查询与排序服务。
- 第四轮：日程写入与重复规则服务。
  - 第四轮 4-0 ~ 4-9 均已完成并归档。
  - 已完成 `ScheduleRepeatService` 与 `ScheduleService` 的第四轮服务边界。
  - 已验证 `add_schedule` 非重复/重复路径，以及 `update_schedule_with_repeat` 当前条、非组转重复、已有组改重复、取消重复路径。
  - 第四轮最终验收通过，`src`、`main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。

---

## 下一步

下一步应由决策窗口基于 `manage_instruction/Work_Formulation.md` 拟定第五轮阶段合同。

第五轮候选：提醒与运行期状态服务。

第五轮启动前应先明确：

- 提醒扫描逻辑当前位置。
- 已触发提醒去重状态当前位置。
- 提醒时间判断和过期/无提醒规则。
- 弹窗与声音调用边界。
- 哪些逻辑可抽为 service，哪些 UI 行为必须保持原位。

执行窗口在收到第五轮正式提示词前，不得修改源码、数据库或管理文档以外文件。
