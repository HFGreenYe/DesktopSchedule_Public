# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 D-3：分类写路径临时验收。

状态：顾问窗口已审查，提示词与 `Work_Instruction.md` 中 D-3 边界一致，可转执行窗口。

提示词：

~~~~markdown
请执行第二轮 D-3：分类写路径临时验收。本轮只验证分类写路径，不改源码。

## 1. 本轮目标

允许为了验收临时写入分类数据，验证分类写路径可用，并确保临时数据清理干净。

重点验证：
- add_category
- get_category
- update_category_fields
- soft_delete_category
- hard_delete_category
- 清理后 get_category(cat_id) 返回 None
- 最终 schedule.db 无 tracked diff

## 2. 允许/禁止

本轮允许修改：
- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在需要维护本轮复核锚点时）

本轮禁止修改：
- src/
- main.py
- requirements.txt
- Work_Snapshot.md
- Work_Formulation.md

本轮允许临时写入 schedule.db，但必须清理，并确认：

git diff --name-only -- schedule.db

无输出。

禁止改源码、禁止改业务逻辑、禁止改 Repository 方法名/参数/返回语义。

若开工前已有管理文档 diff，需在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 使用唯一临时分类名创建分类。
2. 使用 get_category 确认分类存在。
3. 使用 update_category_fields 写回安全字段，例如 color='#0cc0df'。
4. 使用 soft_delete_category 软删除。
5. 使用 hard_delete_category 硬删除。
6. 确认 get_category(cat_id) 返回 None。
7. 确认 schedule.db 无 tracked diff。
8. 不做任何源码修改。

## 4. 验收命令

1. 临时分类完整写入/清理验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_d3_category_'+str(int(time.time())); cid=db_manager.add_category(name, color='#0cc0df', list_type='schedule'); print('created category', cid); assert cid is not None; cat=db_manager.get_category(cid); print('category exists', bool(cat)); assert cat and cat.name == name; updated=db_manager.update_category_fields(cid, color='#0cc0df'); print('updated', updated); assert updated is True; soft=db_manager.soft_delete_category(cid); print('soft deleted', soft); assert soft is True; hard=db_manager.hard_delete_category(cid); print('hard deleted', hard); assert hard is True; after=db_manager.get_category(cid); print('after delete', after); assert after is None"
```

2. diff 范围检查：

```cmd
git diff --name-only -- src/data
git diff --name-only -- src/repositories
git diff --name-only -- src/ui
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch
```

预期：
- src/data 无 diff。
- src/repositories 无 diff。
- src/ui 无 diff。
- main.py 无 diff。
- requirements.txt 无 diff。
- schedule.db 无 tracked diff。
- 最终只允许 manage_instruction/Work_Log.md，以及必要时的 manage_instruction/Work_Task_Prompts.md。

## 5. 日志要求

更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第二轮 D-3（分类写路径临时验收）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 临时分类名称与 id
- add_category 验证结果
- get_category 验证结果
- update_category_fields 验证结果
- soft_delete_category 验证结果
- hard_delete_category 验证结果
- 清理后 get_category(cat_id) 是否返回 None
- schedule.db 是否无 tracked diff
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
~~~~

## 复核锚点

- D-3 允许为了验收临时写入 `schedule.db`，但必须清理临时分类。
- 复核时重点确认 `add_category`、`get_category`、`update_category_fields`、`soft_delete_category`、`hard_delete_category` 全部通过。
- 复核时重点确认清理后 `get_category(cat_id)` 返回 `None`。
- 复核时重点检查 `schedule.db`、`src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt` 均无 diff。
