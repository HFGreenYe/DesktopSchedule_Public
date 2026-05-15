# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 D-2：Data 层读路径回归验收。

状态：顾问窗口已审查，提示词与 `Work_Instruction.md` 中 D-2 边界一致，可转执行窗口。

提示词：

~~~~markdown
请执行第二轮 D-2：Data 层读路径回归验收。本轮只验证读路径，不写数据库，不做任何源码改动。

## 1. 本轮目标

验证 db_manager 兼容门面的核心读路径仍可用。

重点验证：
- db_manager.get_all_schedules() 返回 list。
- db_manager.get_schedules_for_date(date.today()) 返回 list。
- db_manager.get_active_categories() 返回 list。
- db_manager.get_category_map() 返回 dict。
- 有分类样本时，db_manager.get_category(cat_id) 可返回对应分类。
- 有分类样本时，db_manager.check_category_status(cat_id) 返回允许状态。
- 有日程样本时，可通过公开读路径确认样本对象基本字段可访问。

本轮不写数据库，不做代码修复。如果发现问题，只记录问题和风险。

## 2. 允许/禁止

本轮允许修改：
- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在需要维护本轮复核锚点时）

本轮禁止修改：
- src/
- main.py
- requirements.txt
- schedule.db
- Work_Snapshot.md
- Work_Formulation.md

禁止执行任何写入方法，包括但不限于：
- add_category
- update_category_fields
- soft_delete_category
- hard_delete_category
- add_schedule
- delete_schedule
- update_schedule_status
- toggle_pin_status
- update_schedule_fields
- update_schedule_with_repeat

若执行读路径后发现 schedule.db 出现 diff，立即记录为异常，不自行修复。

若开工前已有管理文档 diff，需在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 验证四个核心读路径返回类型。
2. 如存在分类样本，验证 get_category 和 check_category_status。
3. 如存在日程样本，验证样本对象的基础字段可访问。
4. 检查 schedule.db 无 tracked diff。
5. 检查源码、UI、数据库无 diff。
6. 不做任何代码改动，不执行任何写入方法。

## 4. 验收命令

1. 核心读路径与返回类型验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from datetime import date; from src.data.database import db_manager; all_schedules=db_manager.get_all_schedules(); today=db_manager.get_schedules_for_date(date.today()); cats=db_manager.get_active_categories(); cmap=db_manager.get_category_map(); print('all schedules', len(all_schedules), type(all_schedules).__name__); print('today schedules', len(today), type(today).__name__); print('active categories', len(cats), type(cats).__name__); print('category map', len(cmap), type(cmap).__name__); assert isinstance(all_schedules, list); assert isinstance(today, list); assert isinstance(cats, list); assert isinstance(cmap, dict)"
```

2. 分类样本读取与状态判断验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; cats=db_manager.get_active_categories(); allowed={'empty','active','historical'}; print('category sample count', len(cats)); sample=cats[0] if cats else None; result='no sample'; status='no sample'; matched=False;  \
if sample: \
    got=db_manager.get_category(sample.id); matched=bool(got and got.id == sample.id); status=db_manager.check_category_status(sample.id); result=getattr(got, 'name', None); \
print('get_category sample', result); print('category matched', matched); print('category status', status); assert (not sample) or matched; assert (not sample) or status in allowed"
```

如果 PowerShell 对上面的换行命令处理失败，请改用下面单行版本：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; cats=db_manager.get_active_categories(); allowed={'empty','active','historical'}; print('category sample count', len(cats)); sample=cats[0] if cats else None; got=db_manager.get_category(sample.id) if sample else None; status=db_manager.check_category_status(sample.id) if sample else 'no sample'; print('get_category sample', getattr(got,'name',None) if got else 'no sample'); print('category matched', bool(got and got.id == sample.id) if sample else 'no sample'); print('category status', status); assert (not sample) or (got and got.id == sample.id); assert (not sample) or status in allowed"
```

3. 日程样本基础字段读取验证：

```cmd
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; schedules=db_manager.get_all_schedules(); print('schedule sample count', len(schedules)); sample=schedules[0] if schedules else None; print('sample id', getattr(sample,'id',None)); print('sample title', getattr(sample,'title',None)); print('sample item_type', getattr(sample,'item_type',None)); print('sample status', getattr(sample,'status',None)); assert (not sample) or hasattr(sample, 'id'); assert (not sample) or hasattr(sample, 'title'); assert (not sample) or hasattr(sample, 'item_type'); assert (not sample) or hasattr(sample, 'status')"
```

4. 禁止范围 diff 检查：

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

- 本轮任务名称：第二轮 D-2（Data 层读路径回归验收）
- 开工前是否已有管理文档 diff
- 实际修改文件
- get_all_schedules 验证结果
- get_schedules_for_date 验证结果
- get_active_categories 验证结果
- get_category_map 验证结果
- 分类样本读取与 check_category_status 验证结果
- 日程样本基础字段读取验证结果
- 是否确认本轮未执行任何写入方法
- schedule.db 是否无 tracked diff
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
~~~~

## 复核锚点

- D-2 只验证读路径，不允许执行任何写入方法。
- 复核时重点确认核心读路径返回类型、分类样本读取与状态判断、日程样本基础字段可访问。
- 复核时重点检查 `schedule.db` 无 tracked diff。
- 复核时重点检查 `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt` 均无 diff。
