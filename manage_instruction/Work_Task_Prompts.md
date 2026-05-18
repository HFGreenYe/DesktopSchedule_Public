请执行第四轮 4-1：重复日期计算纯逻辑抽取。本轮只抽取日期计算纯逻辑，不改写入流程，不写数据库。

## 1. 本轮目标

基于 `manage_instruction/Work_Instruction.md` 第四轮合同和 `manage_instruction/Work_Log.md` 的 4-0 结论，抽取以下纯逻辑：

- `_add_months` 月份推进逻辑
- `每天 / 每周 / 每月` 的日期偏移逻辑（仅时间计算，不含写库）

本轮目标：

- 可新增 `src/services/schedule_repeat_service.py`
- 可修改 `src/data/database.py`，但仅用于委托纯日期计算
- 保持 `add_schedule` / `update_schedule_with_repeat` 的写入流程、批量插入流程、事务边界不变
- 不新增任何新规则（不得新增 `daily/weekly/monthly/yearly/每年` 行为）
- 验证月末、闰年、`start_time/end_time/reminder_time` 偏移结果与旧逻辑一致

## 2. 允许/禁止

本轮允许修改：

- `src/services/schedule_repeat_service.py`（可新建）
- `src/data/database.py`（仅委托纯日期计算）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- `src/ui/`
- `src/data/models.py`
- `src/repositories/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不改变 `add_schedule` / `update_schedule_with_repeat` 的写入流程与事务边界
- 不改变重复生成数量（每天365、每周52、每月12；总数语义保持）
- 不改变 `group_id` 语义
- 不新增 `parent_id`
- 不实现 `每年` / `yearly`
- 不运行写入验证（不调用 add/update 写库路径做数据变更）

若开工前已有管理文档 diff，需在 `Work_Log.md` 单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取：
   - `manage_instruction/Work_Instruction.md`（第四轮合同）
   - `manage_instruction/Work_Log.md`（4-0 结论）
2. 阅读 `src/data/database.py` 当前：
   - `_add_months`
   - `add_schedule` 中 `每天/每周/每月` 时间偏移段
   - `update_schedule_with_repeat` 中 `每天/每周/每月` 时间偏移段
3. 新建（或完善）`src/services/schedule_repeat_service.py`，仅包含纯逻辑方法，建议最小边界：
   - `add_months(sourcedate, months)`
   - `shift_datetime(value, rule, step)`（rule 仅支持 `每天/每周/每月`）
   - 可选：`shift_triplet(start_time, end_time, reminder_time, rule, step)`（返回偏移后三元组）
4. 修改 `src/data/database.py`：
   - `_add_months` 可保留壳函数并委托 service，或直接改为调用 service
   - `add_schedule` 与 `update_schedule_with_repeat` 内的日期偏移分支改为调用 service
   - 严禁改动写入流程、分支结构、事务块、批量插入逻辑与数量
5. 不修改 UI / models / repository
6. 更新 `Work_Log.md`

## 4. 验收命令

读取与定位：

Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
rg -n "def _add_months|def add_schedule|def update_schedule_with_repeat|每天|每周|每月|timedelta|loop_count|insert_many|db\.atomic" src/data/database.py

service 导入验证：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.services.schedule_repeat_service import ScheduleRepeatService; print('repeat service import ok', ScheduleRepeatService)"

静态依赖检查（service 不依赖 UI/db_manager/Repository）：

rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|ScheduleRepository|CategoryRepository" src/services/schedule_repeat_service.py

预期：无输出（退出码 1 视为通过）。

结果一致性验证（只读，不写库）：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import datetime as dt; from src.services.schedule_repeat_service import ScheduleRepeatService as S; legacy=lambda d,m: None if not d else d.replace(year=(d.year+((d.month-1+m)//12)), month=((d.month-1+m)%12)+1, day=min(d.day,[31,29 if ((d.year+((d.month-1+m)//12))%4==0 and not (d.year+((d.month-1+m)//12))%100==0) or (d.year+((d.month-1+m)//12))%400==0 else 28,31,30,31,30,31,31,30,31,30,31][((d.month-1+m)%12)])); cases=[dt.datetime(2023,1,31,10,0),dt.datetime(2024,1,31,10,0),dt.datetime(2024,2,29,8,30),dt.datetime(2025,3,30,23,59),None]; ms=[1,2,11,12,13]; ok=True; rows=[];
for c in cases:
  for m in ms:
    a=legacy(c,m); b=S.add_months(c,m); rows.append((c,m,a,b,a==b)); ok=ok and (a==b);
print('month rows', rows); assert ok"

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import datetime as dt; from src.services.schedule_repeat_service import ScheduleRepeatService as S; st=dt.datetime(2026,1,31,9,0); en=dt.datetime(2026,1,31,10,0); rm=dt.datetime(2026,1,30,9,0);
for rule,step in [('每天',1),('每周',2),('每月',1)]:
  ns,ne,nr=S.shift_triplet(st,en,rm,rule,step) if hasattr(S,'shift_triplet') else (S.shift_datetime(st,rule,step),S.shift_datetime(en,rule,step),S.shift_datetime(rm,rule,step));
  print(rule,step,ns,ne,nr)"

验证未新增不允许规则实现（仅检查新 service 和 database）：

rg -n "每年|yearly|daily|weekly|monthly" src/services/schedule_repeat_service.py src/data/database.py

预期：不应出现新增实现分支；如仅注释或既有文本命中，需在日志说明不构成新行为。

语法检查：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/services/schedule_repeat_service.py src/data/database.py

范围检查：

git diff --name-only -- src/ui
git diff --name-only -- src/data/models.py
git diff --name-only -- src/repositories
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch

预期：

- `src/ui` 无 diff
- `src/data/models.py` 无 diff
- `src/repositories` 无 diff
- `main.py` 无 diff
- `requirements.txt` 无 diff
- `schedule.db` 无 tracked diff
- 最终只允许：
  - `src/services/schedule_repeat_service.py`
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. Work_Log.md 记录要求

至少记录：

- 本轮任务名称：第四轮 4-1（重复日期计算纯逻辑抽取）
- 开工前是否已有管理文档 diff
- 实际修改文件
- service 方法清单与输入/输出说明
- `database.py` 委托点位置
- 明确记录：未改写入流程、未改事务边界、未改生成数量
- 月末与闰年一致性验证结果
- `start_time/end_time/reminder_time` 偏移一致性验证结果
- service import 验证结果
- service 静态依赖检查结果
- 未新增 `每年/yearly/daily/weekly/monthly` 行为说明
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
