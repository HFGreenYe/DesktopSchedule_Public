# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 D-4：日程写路径临时验收。

状态：顾问窗口已审查并微调，提示词与 `Work_Instruction.md` 中 D-4 边界一致，可转执行窗口。

提示词：

~~~~markdown
请执行第二轮 D-4：日程写路径临时验收。本轮只验证日程写路径，不改源码。

## 1. 本轮目标

允许为了验收临时写入日程数据，验证日程写路径可用，并确保所有改动恢复或清理干净。

重点验证：
- 有安全样本时，update_schedule_status 写入测试值后恢复原值。
- 有安全样本时，toggle_pin_status 切换后恢复原值。
- 有安全样本时，update_schedule_fields 写入测试 title 后恢复原 title。
- add_schedule 创建 repeat_rule='none' 的唯一临时日程。
- delete_schedule 删除临时日程。
- 删除后 get_all_schedules() 找不到该临时 id。
- 最终 schedule.db 无 tracked diff。

如果没有可安全恢复的已有日程样本，记录跳过样本写回验证原因，不要强行修改真实数据。

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

本轮允许临时写入 schedule.db，但必须恢复/清理，并确认：

git diff --name-only -- schedule.db

无输出。

禁止改源码、禁止改业务逻辑、禁止改 Repository 方法名/参数/返回语义。

若开工前已有管理文档 diff，需在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 尝试获取一个已有日程样本。
2. 如存在样本：
   - 记录原 status。
   - 用 update_schedule_status 写入一个测试值，再恢复原 status。
   - 记录原 is_pinned。
   - 用 toggle_pin_status 切换一次，再切换回原值。
   - 记录原 title。
   - 用 update_schedule_fields 写入临时 title，再恢复原 title。
3. 如不存在可安全恢复样本：
   - 记录跳过原因。
   - 不强行修改真实数据。
4. 创建唯一临时日程，repeat_rule='none'。
5. 删除该临时日程。
6. 确认删除后 get_all_schedules() 找不到该临时 id。
7. 确认 schedule.db 无 tracked diff。
8. 不做任何源码修改。

## 4. 验收命令

1. 既有样本状态/置顶/title 写回恢复验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time, sys; schedules=db_manager.get_all_schedules(); print('sample count', len(schedules)); sample=schedules[0] if schedules else None; print('sample id', getattr(sample,'id',None)); sys.exit(0) if not sample else None; sid=sample.id; old_status=sample.status; old_pin=sample.is_pinned; old_title=sample.title; print('old status', old_status); print('old pin', old_pin); print('old title', old_title); status_test=0 if old_status != 0 else 1; temp_title=str(old_title)+'__d4_tmp_'+str(int(time.time())); ok1=db_manager.update_schedule_status(sid, status_test); ok2=db_manager.update_schedule_status(sid, old_status); ok3=db_manager.toggle_pin_status(sid, old_pin); ok4=db_manager.toggle_pin_status(sid, (not old_pin)); ok5=db_manager.update_schedule_fields(sid, title=temp_title); mid=[s for s in db_manager.get_all_schedules() if s.id==sid][0]; print('temp title set', mid.title == temp_title); ok6=db_manager.update_schedule_fields(sid, title=old_title); refreshed=[s for s in db_manager.get_all_schedules() if s.id==sid][0]; print('status write/restore', ok1, ok2); print('pin toggle/restore', ok3, ok4); print('title temp/restore', ok5, ok6); print('restored status', refreshed.status); print('restored pin', refreshed.is_pinned); print('restored title', refreshed.title); assert ok1 and ok2 and ok3 and ok4 and ok5 and ok6; assert mid.title == temp_title; assert refreshed.status == old_status; assert refreshed.is_pinned == old_pin; assert refreshed.title == old_title"
```

2. 临时日程创建/删除验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; import time; name='__tmp_d4_schedule_'+str(int(time.time())); data={'title':name,'item_type':'schedule','priority':0,'repeat_rule':'none','description':'temporary d4 validation','category_id':None}; created=db_manager.add_schedule(data); print('created schedule', created); assert created is True; matches=[s for s in db_manager.get_all_schedules() if s.title==name]; print('matches', len(matches)); assert len(matches)==1; sid=matches[0].id; deleted=db_manager.delete_schedule(sid); print('deleted schedule', deleted); assert deleted is True; remaining=[s for s in db_manager.get_all_schedules() if s.id==sid]; print('remaining', len(remaining)); assert len(remaining)==0"
```

3. diff 范围检查：

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

- 本轮任务名称：第二轮 D-4（日程写路径临时验收）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 是否存在可安全恢复的日程样本
- update_schedule_status 写入/恢复验证结果，或跳过原因
- toggle_pin_status 切换/恢复验证结果，或跳过原因
- update_schedule_fields 临时 title 写入/恢复验证结果，或跳过原因
- 临时日程名称与 id
- add_schedule 验证结果
- delete_schedule 验证结果
- 删除后是否查询不到临时 id
- schedule.db 是否无 tracked diff
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
~~~~

## 复核锚点

- D-4 允许为了验收临时写入 `schedule.db`，但必须恢复真实样本改动并清理临时日程。
- 复核时重点确认 `update_schedule_status` 写入测试值后恢复原值。
- 复核时重点确认 `toggle_pin_status` 切换后恢复原值。
- 复核时重点确认 `update_schedule_fields` 写入临时 title 后恢复原 title。
- 复核时重点确认临时日程创建后删除，删除后查询不到临时 id。
- 复核时重点检查 `schedule.db`、`src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt` 均无 diff。
