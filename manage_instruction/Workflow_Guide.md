# Workflow Guide

本文档记录本项目架构改写期间的多窗口协作方式、管理文件职责和 Git 保存流程。

## 窗口分工

### 决策窗口

职责：
- 负责较高层的架构判断和阶段方案。
- 产出或修订阶段级指令。
- 不直接承担大量执行和验证。

主要写入：
- `Work_Instruction.md`

### 顾问窗口

职责：
- 负责审阅决策窗口方案。
- 将阶段级指令拆成小工单。
- 评估执行窗口结果。
- 对照提示词、日志、`git diff` 和运行结果做复核。
- 必要时补充管理文档。

主要写入：
- `Work_Formulation.md`
- `Work_Task_Prompts.md`
- `Workflow_Guide.md`
- 必要时追加 `Work_Log.md` 的顾问复核记录。

### 执行窗口

职责：
- 按用户转发的小工单提示词执行代码修改。
- 每次执行后更新 `Work_Log.md`。
- 不主动扩大任务范围。
- 完成后不提交 Git，等待顾问窗口复核。

主要写入：
- `src/...`
- `Work_Log.md`

## 文件职责

### `Work_Formulation.md`

总体方案和顾问层规划。

用途：
- 记录架构改写思路。
- 记录最终目标架构。
- 记录阶段划分和 Git 策略。

### `Work_Instruction.md`

当前阶段的施工合同。

用途：
- 记录当前大阶段目标、允许修改范围、禁止事项和总体验收要求。
- 不要求执行窗口一次性全部完成。
- 小工单应从这里拆出。

### `Work_Task_Prompts.md`

当前或最近小工单的提示词凭证。

用途：
- 保存实际发给执行窗口的小工单提示词。
- 供顾问窗口复核 `Work_Log.md` 和 `git diff` 时使用。
- 执行窗口通常不需要读取本文件，用户直接把提示词复制给执行窗口即可。

### `Work_Log.md`

执行记录。

用途：
- 执行窗口每轮完成后必须追加。
- 至少记录任务名称、修改文件、验证命令和结果、未完成事项、风险或疑点。
- 如果中途失败，也要记录失败位置、错误摘要和是否回滚。

### `History_Instruction.md`

历史阶段指令归档。

用途：
- 当 `Work_Instruction.md` 中的阶段完成并提交 Git 后，将旧指令归档到这里。
- 避免 `Work_Instruction.md` 长期堆积，浪费读取成本。

### `Work_Snapshot.md`

架构改写前快照。

用途：
- 保存改写前的项目功能和目录结构快照。
- 作为行为一致性参考。
- 通常不跟随 `manage_instruction` 文件夹日常变动更新。

### `code_pack.txt`

代码打包快照。

用途：
- 供外部窗口或模型快速阅读项目代码。
- 不是实时文件，必要时再重新生成。

## 标准流程

### 1. 决策窗口产出阶段方案

决策窗口写入或更新：
- `Work_Instruction.md`

顾问窗口负责审查：
- 阶段目标是否过大。
- 是否需要拆成小工单。
- 允许修改范围是否清楚。
- 验收要求是否足够具体。

### 2. 顾问窗口拆小工单

顾问窗口将阶段任务拆成 B-1、B-2 等小工单。

原则：
- 每次尽量只动一个行为面。
- 能读不写时先读。
- 写入方法单独拆。
- 高风险方法最后做。
- 不把迁移、UI、Repository 委托和新功能混在同一小工单。

顾问窗口应：
- 在聊天中直接给用户完整提示词，方便用户复制给执行窗口。
- 将同一份提示词写入 `Work_Task_Prompts.md`，作为复核依据。

### 3. 执行窗口执行

执行窗口按用户转发的提示词修改文件。

要求：
- 不扩大范围。
- 不提交 Git。
- 完成后更新 `Work_Log.md`。
- 如 Python 验证受沙箱限制，应申请沙箱外权限，或记录需用户本地 CMD 复跑的命令。

### 4. 顾问窗口复核

顾问窗口复核时至少检查：
- `Work_Task_Prompts.md` 中的小工单提示词。
- `Work_Log.md` 最新记录。
- `git status --short`。
- `git diff --name-only`。
- 关键文件的实际 diff。
- 必要的运行验证。

复核通过后，顾问窗口给出 Git 提交命令。

### 5. 用户提交 Git

每个小工单复核通过后，用户提交一次 Git。

示例：

```cmd
git add src/data/database.py manage_instruction/Work_Log.md manage_instruction/Work_Task_Prompts.md
git commit -m "refactor: delegate category creation"
git status
```

提交后应确认：

```text
nothing to commit, working tree clean
```

## 当前注意事项

- 当前 Python 验证应使用内层项目根目录：

```cmd
cd /d D:\CodeProjects\DesktopSchedule\DesktopSchedule
.\.venv\Scripts\python.exe ...
```

- 执行窗口普通沙箱可能无法访问基础解释器路径。遇到 `Unable to create process` 时，不一定是代码问题，优先申请沙箱外权限或由用户本地 CMD 验证。
- `schedule.db` 当前存在但不应提交。涉及临时数据验证时，必须清理临时数据。
- `src/ui/` 在当前第一轮 B 中原则上不得修改。
- `Work_Snapshot.md` 作为改写前快照，通常不要因为管理文件变化而更新。

## 第一轮 B 小工单进度

已完成：
- B-1：新增 Repository 薄封装。
- B-2：委托 `get_all_schedules()`、`get_active_categories(list_type=None)`。
- B-3：委托 `get_schedules_for_date(target_date)`、`get_category_map()`。
- B-4：修复 `_migrate_db` 的 `migrator` 作用域风险。
- B-5：委托 `get_category(cat_id)`。
- B-6：委托 `check_category_status(cat_id)`。
- B-7：委托 `update_category_fields(cat_id, **kwargs)`。

待推进：
- B-8：委托 `add_category(name, color="#0cc0df", list_type="schedule")`。
- 后续：`soft_delete_category`、`hard_delete_category`、`update_schedule_status`、`toggle_pin_status`、`update_schedule_fields`、`delete_schedule` 等。

## 2026-05-14 第一轮 B 进度更新（B-16）

- B-1 到 B-14：已完成。
- B-15（B 轮整体技术验收）：已完成。
- 第一轮 B 当前状态：已完成，可进入下一轮任务拆分。
