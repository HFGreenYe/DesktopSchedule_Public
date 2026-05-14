# Workflow Guide

本文件记录多窗口协作方式、管理文件职责边界、标准执行流程及日常注意事项。

## 窗口分工

### 决策窗口
- 负责阶段目标、架构方向和边界约束。
- 产出或修订阶段级指令。
- 主要写入：`Work_Instruction.md`。

### 顾问窗口
- 负责把阶段任务拆分成小工单。
- 负责复核执行结果与风险。
- 主要写入：`Work_Formulation.md`、`Work_Task_Prompts.md`、`Workflow_Guide.md`。
- 必要时补充 `Work_Log.md` 的复核记录。

### 执行窗口
- 按用户转发的小工单执行。
- 不主动扩张任务范围。
- 完成后更新 `Work_Log.md`。
- 不提交 Git，等待顾问窗口复核。

## 文件职责

### `Work_Formulation.md`
- 总体方案与长期演进方向。

### `Work_Instruction.md`
- 当前阶段的执行合同（目标、边界、验收）。

### `Work_Task_Prompts.md`
- 当前/最近小工单提示词与复核锚点。
- 保持短期、轻量，不沉淀长期阶段历史。

### `Work_Log.md`
- 每轮执行记录（任务、改动、验证、风险、未完成项）。
- 只保留当前阶段/当前轮次日志，避免读取当前进度时带入大量历史内容。

### `History_Log.md`
- 已完成阶段的执行日志归档。
- 仅在追溯旧阶段问题、核对历史验证细节时读取。

### `History_Instruction.md`
- 已完成阶段指令归档。

### `Work_Snapshot.md`
- 改写前快照，通常不随日常管理变动频繁更新。

### `code_pack.txt`
- 代码打包快照，必要时再生成。

## 标准流程

1. 决策窗口更新 `Work_Instruction.md`。
2. 顾问窗口拆分小工单并给出可执行提示词。
3. 执行窗口按提示词实现并更新 `Work_Log.md`。
4. 顾问窗口复核 `Work_Log.md`、`git diff`、关键验证结果。
5. 用户确认后提交 Git。
6. 阶段完成后，将 `Work_Log.md` 中的旧阶段日志迁移到 `History_Log.md`，并清空为下一阶段日志入口。

## Git 与验证注意事项

- 开工前先看：`git status --short`。
- 结束后至少检查：
  - `git diff --name-only`
  - `git diff --name-only -- src/ui`
- Python 验证优先在内层项目根目录执行：
```cmd
cd /d D:\CodeProjects\DesktopSchedule\DesktopSchedule
.\.venv\Scripts\python.exe ...
```
- 若执行窗口受沙箱限制导致 Python 无法运行，优先申请沙箱外权限或由用户本地 CMD 复跑，并在 `Work_Log.md` 留痕。
- 涉及临时验证数据时，需清理临时数据，避免遗留不必要变更。
