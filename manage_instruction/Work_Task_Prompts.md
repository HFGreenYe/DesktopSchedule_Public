# Work Task Prompts

本文件用于保存每个小工单实际下发给执行窗口的提示词，作为复核 `Work_Log.md`、`git diff` 和运行验证结果的依据。

使用规则：
- `Work_Instruction.md` 记录当前阶段总合同。
- 本文件记录从总合同拆出的单次施工提示词。
- `Work_Log.md` 记录执行窗口实际操作和验收结果。
- 每个小工单完成并提交后，在对应条目补充提交号。

---

## 2026-05-13 B-7 update_category_fields 委托

状态：已复核/待提交
对应提交：待填写

### 提示词

```text
请执行第一轮 B-7：只委托一个低风险写入方法 DatabaseManager.update_category_fields(cat_id, **kwargs)，不执行完整 B 轮。

本轮允许修改：
- src/data/database.py
- manage_instruction/Work_Log.md

本轮禁止修改：
- src/repositories/（除非你发现 CategoryRepository.update_category_fields 不存在；若需改先说明）
- src/ui/
- main.py
- src/theme/
- src/utils/signals.py
- schedule.db
- requirements.txt
- Work_Snapshot.md
- 不改 migration 逻辑
- 不改任何其他写入/状态方法（add_category、soft_delete_category、hard_delete_category、check_category_status、Schedule 相关写入等）

本轮目标：
1. 仅将 DatabaseManager.update_category_fields(cat_id, **kwargs) 内部委托到：
   self.category_repository.update_category_fields(cat_id, **kwargs)
2. 保持 db_manager 对外方法名、参数、返回语义不变。
3. 不做额外重构。

验收要求：
1. import 和基础调用验证（使用内层目录 + 显式 .venv）：
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; print('db import ok'); cats=db_manager.get_active_categories(); print('cats', len(cats)); result=db_manager.update_category_fields(cats[0].id, color=cats[0].color) if cats else 'no sample'; print('update_category_fields path:', result)"

2. 验证 src/ui 无改动：
git diff --name-only -- src/ui

3. 验证本轮修改范围：
git diff --name-only
应只包含：
- src/data/database.py
- manage_instruction/Work_Log.md

4. 更新 Work_Log.md，至少记录：
- 本轮任务名称：第一轮 B-7（update_category_fields 委托）
- 实际修改文件
- 验证命令和结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。
完成后不要提交 Git，等待顾问窗口复核。
```

### 复核结果

- `Work_Log.md` 已记录 B-7 任务名称、修改文件、验证命令和结果、未完成事项、风险或疑点。
- `git diff -- src/data/database.py` 显示仅将 `DatabaseManager.update_category_fields(cat_id, **kwargs)` 委托为 `self.category_repository.update_category_fields(cat_id, **kwargs)`。
- `git diff --name-only -- src/ui` 无输出，确认 UI 未改动。
- `git diff --name-only` 显示本轮代码/日志改动范围符合提示词要求，另新增本提示词记录文件。
- 顾问窗口已复跑验证命令，输出：
  - `db import ok`
  - `cats 6`
  - `update_category_fields path: True`
