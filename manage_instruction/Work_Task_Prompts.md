请执行第三轮 3-4a：CategoryPolicyService 分类状态判断抽取。本轮只抽取 `CategoryRepository.check_category_status(cat_id)` 中 `empty / active / historical` 的纯判定逻辑，不处理删除策略。

## 1. 本轮目标

基于 3-0 到 3-3b 结论，在 `CategoryPolicyService` 中实现分类状态判断纯逻辑，并让 `CategoryRepository.check_category_status(cat_id)` 委托该 service 完成状态判定。

本轮目标：

- 实现 `CategoryPolicyService.evaluate_status(items, now=None)`。
- Repository 仍负责数据库查询。
- service 只接收查询结果列表/iterable，不访问数据库。
- service 不依赖 UI、db_manager、Repository。
- 保持 `db_manager.check_category_status(cat_id)` 对外返回语义不变：
  - 无日程：`"empty"`
  - 存在未完成且未过期日程：`"active"`
  - 否则：`"historical"`
- 不处理 `soft_delete_category` / `hard_delete_category`。
- 不修改 UI 删除分支。
- 不写 `schedule.db`。

## 2. 允许/禁止

本轮允许修改：

- `src/services/category_policy_service.py`
- `src/repositories/category_repository.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- `src/ui/`
- `src/data/`
- `src/services/schedule_query_service.py`
- `src/services/schedule_sort_service.py`
- `src/services/weather_service.py`
- `src/services/matrix_classification_service.py`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不处理 `soft_delete_category`。
- 不处理 `hard_delete_category`。
- 不修改 UI 删除分支。
- 不实现删除动作选择，`choose_delete_action` 留给 3-4b。
- 不修改排序逻辑。
- 不修改查询/过滤逻辑。
- 不创建 matrix 服务。
- 不修改数据库字段、迁移逻辑或写入逻辑。
- 不改变 `db_manager.check_category_status(cat_id)` 返回字符串语义。
- 不保留 `schedule.db` 变更。

若开工前已有管理文档 diff，需在 `Work_Log.md` 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取 `manage_instruction/Work_Instruction.md` 第三轮合同。
2. 读取 `manage_instruction/Work_Log.md` 中 3-0 到 3-3b 结论。
3. 读取 `src/repositories/category_repository.py` 当前 `check_category_status(cat_id)` 实现。
4. 在 `src/services/category_policy_service.py` 中实现：
   - `CategoryPolicyService.evaluate_status(items, now=None)`
   - 输入为某分类下的 schedule iterable。
   - 输出使用现有 `CategoryStatus` 枚举，或其字符串值；但 Repository 对外必须返回旧字符串。
   - 旧逻辑必须保持：
     - items 为空：`CategoryStatus.EMPTY`
     - 遍历每个 schedule：
       - `is_completed = schedule.status == 1`
       - `is_expired = bool(schedule.end_time and schedule.end_time < now and not is_completed)`
       - 如果 `not is_completed and not is_expired`，返回 `CategoryStatus.ACTIVE`
     - 遍历后无 active，返回 `CategoryStatus.HISTORICAL`
   - `now` 默认为 `datetime.datetime.now()`，允许测试传入固定时间。
   - 使用 `getattr` 读取 `status`、`end_time`，但语义必须等价旧逻辑。
   - 不访问数据库。
   - 不导入 UI / db_manager / Repository。
5. 修改 `CategoryRepository.check_category_status(cat_id)`：
   - 保持 Repository 查询 `self._schedule_model.select().where(...)`。
   - 将查询结果转为 list 后传给 `CategoryPolicyService.evaluate_status(...)`。
   - 返回值必须是旧字符串：`"empty"` / `"active"` / `"historical"`。
6. 不修改 `soft_delete_category` / `hard_delete_category`。
7. 不修改 UI。
8. 更新 `Work_Log.md`。

## 4. 验收命令

开工前基线命令，修改代码前先执行并记录输出：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; cats=db_manager.get_active_categories(); sample=[(c.id,c.name,db_manager.check_category_status(c.id)) for c in cats[:10]]; print('baseline categories', sample); print('baseline missing', db_manager.check_category_status(-999999))"

修改后复跑，确认分类状态与基线一致：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; cats=db_manager.get_active_categories(); sample=[(c.id,c.name,db_manager.check_category_status(c.id)) for c in cats[:10]]; print('after categories', sample); print('after missing', db_manager.check_category_status(-999999)); assert db_manager.check_category_status(-999999) == 'empty'"

验证 service 可直接调用，且返回状态值合法：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; from src.services.category_policy_service import CategoryPolicyService, CategoryStatus; cats=db_manager.get_active_categories(); allowed={CategoryStatus.EMPTY, CategoryStatus.ACTIVE, CategoryStatus.HISTORICAL}; print('allowed', [s.value for s in allowed]); rows=[]; [rows.append((c.id, c.name, CategoryPolicyService.evaluate_status([s for s in db_manager.get_all_schedules() if getattr(s,'category_id',None)==c.id]))) for c in cats[:5]]; print('rows', [(cid,name,status,getattr(status,'value',status)) for cid,name,status in rows]); assert all(status in allowed for _,_,status in rows)"

验证至少覆盖 active / historical / empty / missing 语义；如果当前数据没有某类样本，日志中说明缺失，不临时写库：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; cats=db_manager.get_active_categories(); statuses={}; [statuses.setdefault(db_manager.check_category_status(c.id), []).append(c.id) for c in cats]; statuses.setdefault('missing', []).append(-999999); print('status coverage', statuses)"

验证旧 `db_manager.check_category_status` 返回字符串：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; cats=db_manager.get_active_categories(); ids=[c.id for c in cats[:5]]+[-999999]; vals=[db_manager.check_category_status(i) for i in ids]; print('values', vals); assert all(isinstance(v, str) for v in vals); assert all(v in {'empty','active','historical'} for v in vals)"

静态依赖检查，确认 `category_policy_service.py` 不依赖 UI / db_manager / Repository / QWidget：

rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|CategoryRepository|ScheduleRepository" src/services/category_policy_service.py

确认未处理删除策略：

git diff -- src/repositories/category_repository.py

复核 diff 时必须确认 `soft_delete_category` 和 `hard_delete_category` 未被修改。

检查本轮未误动其他 service / UI：

git diff --name-only -- src/ui
git diff --name-only -- src/services/schedule_query_service.py
git diff --name-only -- src/services/schedule_sort_service.py
git diff --name-only -- src/services/weather_service.py

语法检查：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src\services\category_policy_service.py src\repositories\category_repository.py

范围检查：

git diff --name-only -- src/data
git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch

预期：

- `src/ui` 无 diff。
- `src/data` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- `schedule_query_service.py` 无 diff。
- `schedule_sort_service.py` 无 diff。
- `weather_service.py` 无 diff。
- 最终只允许：
  - `src/services/category_policy_service.py`
  - `src/repositories/category_repository.py`
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第三轮 3-4a（CategoryPolicyService 分类状态判断抽取）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 开工前分类状态基线输出摘要
- 实现的 `CategoryPolicyService.evaluate_status` 逻辑
- `CategoryRepository.check_category_status` 委托方式
- 明确记录：Repository 仍负责数据库查询
- 明确记录：service 不访问数据库
- 明确记录：未修改 `soft_delete_category` / `hard_delete_category`
- 明确记录：未修改 UI 删除分支
- 修改后分类状态是否与基线一致
- 不存在 id 返回语义是否仍为 `"empty"`
- service direct call 验证结果
- `db_manager.check_category_status` 返回字符串验证结果
- 样本覆盖情况：active / historical / empty / missing
- 静态依赖检查结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
