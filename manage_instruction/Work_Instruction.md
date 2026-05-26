# Work Instruction

用途：本文件用于“当前阶段”的执行指令发布。

- 仅保留正在执行或即将执行的任务。
- 已完成阶段请归档到 `History_Instruction.md`，避免本文件长期堆积。
- 当前主路线图见 `Work_Formulation.md` 的“架构改写轮次路线图”。
- 改写前行为和目录快照见 `Work_Snapshot.md`。
- 执行过程记录写入 `Work_Log.md`。

---

# 当前阶段：第八轮 - UI 拆分与样式债务整理（待规划）

## 已完成并归档

- 第一轮：基建 + repository + db_manager 兼容委托。
- 第二轮：Data 层整理与模型拆分。
- 第三轮：纯业务查询与排序服务。
- 第四轮：日程写入与重复规则服务。
- 第五轮：提醒与运行期状态服务。
- 第六轮：Controller / Router / EventBus 协调层。
- 第七轮：Theme / QSS 接入与样式债务控制。

---

## 当前执行要求

当前只完成第七轮归档，尚未发布第八轮阶段合同。

在决策窗口写入第八轮阶段合同前，执行窗口不得自行开始源码改造、UI 拆分、样式迁移、数据库改造或管理文档大范围改写。

第八轮规划应继承第七轮结论：

- 基于 `default.qss / skin preset`，不建立 light/dark mode matrix。
- 继续使用 `role/state/variant` 动态属性规范。
- UI 拆分和样式迁移必须拆成小工单，不一次性迁移 `todo_board.py` / `week_window.py` / `month_window.py` / `add_view.py` 等大文件。
- 真实换肤 UI、`theme_color/设置字体` 功能闭环仍需后续单独规划，不默认并入第八轮。
