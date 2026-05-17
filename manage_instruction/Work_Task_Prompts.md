请执行第三轮 3-4b：CategoryPolicyService 分类删除动作决策抽取。本轮只抽取“根据分类状态决定删除动作”的纯分支判断，不修改实际删除方法。

## 1. 本轮目标

基于 3-0 到 3-4a 结论，在 `CategoryPolicyService` 中实现 `choose_delete_action(status)`，并对 UI 中根据 `db_manager.check_category_status(cat_id)` 返回值决定删除方式的分支做最小调用替换。

旧 UI 删除分支语义必须保持：

- `active` -> 拦截删除，对应 `CategoryDeleteAction.BLOCK`
- `historical` -> 二次确认后软删除，对应 `CategoryDeleteAction.SOFT_DELETE`
- `empty` -> 直接硬删除，对应 `CategoryDeleteAction.HARD_DELETE`

本轮只替换“状态到动作”的判断方式，不改变：

- UI 文案
- QMessageBox 交互流程
- toast / tooltip 内容
- soft delete / hard delete 调用方式
- 刷新逻辑
- `db_manager` API
- Repository 删除方法

## 2. 允许/禁止

本轮允许修改：

- `src/services/category_policy_service.py`
- `src/ui/list_picker.py`
- `src/ui/todo_board.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- `src/repositories/`
- `src/data/`
- `src/ui/dashboard.py`
- `src/ui/week_window.py`
- `src/ui/todo.py`
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

- 不修改 `CategoryRepository.soft_delete_category`。
- 不修改 `CategoryRepository.hard_delete_category`。
- 不修改 `db_manager` 对外 API。
- 不修改数据库字段、迁移逻辑或写入逻辑。
- 不改 UI 布局。
- 不改 UI 文案。
- 不改 UI 交互流程。
- 不改 toast / tooltip / QMessageBox 内容。
- 不修改排序、查询、过滤逻辑。
- 不创建 matrix 服务。
- 不保留 `schedule.db` 变更。

若开工前已有管理文档 diff，需在 `Work_Log.md` 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取 `manage_instruction/Work_Instruction.md` 第三轮合同。
2. 读取 `manage_instruction/Work_Log.md` 中 3-0 到 3-4a 结论。
3. 读取当前三处 UI 删除分支：
   - `src/ui/list_picker.py` 中 `_delete_category_logic`
   - `src/ui/todo_board.py` 中 `_delete_category`
   - `src/ui/todo_board.py` 中 `_handle_folder_delete`
4. 在 `src/services/category_policy_service.py` 中实现：
   - `CategoryPolicyService.choose_delete_action(status)`
   - 输入允许为：
     - `CategoryStatus` 枚举
     - 旧字符串：`"empty"` / `"active"` / `"historical"`
   - 输出必须为 `CategoryDeleteAction` 枚举。
   - 映射必须为：
     - `active` -> `CategoryDeleteAction.BLOCK`
     - `historical` -> `CategoryDeleteAction.SOFT_DELETE`
     - `empty` -> `CategoryDeleteAction.HARD_DELETE`
   - 对未知状态建议保守处理为 `CategoryDeleteAction.BLOCK`，并在日志中记录该兜底策略；不要抛异常影响 UI 删除流程。
   - 不访问数据库。
   - 不导入 UI / db_manager / Repository。
5. 修改 `src/ui/list_picker.py`：
   - 引入 `CategoryPolicyService` 和 `CategoryDeleteAction`。
   - 保留 `status = db_manager.check_category_status(cat_id)`。
   - 新增 `action = CategoryPolicyService.choose_delete_action(status)`。
   - 将原 `status == 'active' / 'historical' / else` 分支替换为 `action == CategoryDeleteAction.BLOCK / SOFT_DELETE / HARD_DELETE`。
   - 不改文案、不改弹窗、不改 soft/hard delete 调用、不改刷新逻辑。
6. 修改 `src/ui/todo_board.py` 两处删除分支：
   - `_delete_category`
   - `_handle_folder_delete`
   - 同样只替换分支判断，不改文案、不改交互、不改删除调用、不改刷新逻辑。
7. 不修改 Repository。
8. 不修改 `db_manager`。
9. 不写数据库。
10. 更新 `Work_Log.md`。

## 4. 验收命令

开工前动作映射基线，修改代码前先执行并记录输出：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "statuses=['active','historical','empty']; old={s:('block' if s=='active' else 'soft_delete' if s=='historical' else 'hard_delete') for s in statuses}; print('baseline actions', old)"

修改后验证 service 动作映射一致：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.services.category_policy_service import CategoryPolicyService, CategoryStatus, CategoryDeleteAction; expected={'active':CategoryDeleteAction.BLOCK,'historical':CategoryDeleteAction.SOFT_DELETE,'empty':CategoryDeleteAction.HARD_DELETE}; actual={s:CategoryPolicyService.choose_delete_action(s) for s in expected}; enum_actual={s:CategoryPolicyService.choose_delete_action(CategoryStatus(s)) for s in expected}; print('actual', {k:v.value for k,v in actual.items()}); print('enum_actual', {k:v.value for k,v in enum_actual.items()}); assert actual==expected; assert enum_actual==expected"

验证未知状态兜底不破坏 UI 流程：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.services.category_policy_service import CategoryPolicyService, CategoryDeleteAction; result=CategoryPolicyService.choose_delete_action('unknown'); print('unknown action', result.value); assert result == CategoryDeleteAction.BLOCK"

验证当前分类状态到动作映射覆盖 active / historical / empty / missing：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; from src.services.category_policy_service import CategoryPolicyService; cats=db_manager.get_active_categories(); rows=[(c.id,c.name,db_manager.check_category_status(c.id),CategoryPolicyService.choose_delete_action(db_manager.check_category_status(c.id)).value) for c in cats]; rows.append((-999999,'missing',db_manager.check_category_status(-999999),CategoryPolicyService.choose_delete_action(db_manager.check_category_status(-999999)).value)); print('rows', rows); assert all(action in {'block','soft_delete','hard_delete'} for _,_,_,action in rows)"

验证 `db_manager.check_category_status` 仍返回字符串：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.database import db_manager; cats=db_manager.get_active_categories(); ids=[c.id for c in cats[:5]]+[-999999]; vals=[db_manager.check_category_status(i) for i in ids]; print('values', vals); assert all(isinstance(v, str) for v in vals); assert all(v in {'empty','active','historical'} for v in vals)"

静态依赖检查，确认 `category_policy_service.py` 不依赖 UI / db_manager / Repository / QWidget：

rg -n "QWidget|PyQt|PySide|src\.ui|db_manager|src\.repositories|CategoryRepository|ScheduleRepository" src/services/category_policy_service.py

检查 UI 引用范围：

rg -n "CategoryPolicyService|CategoryDeleteAction|CategoryStatus|src\.repositories" src/ui/list_picker.py src/ui/todo_board.py

预期：

- `list_picker.py` 和 `todo_board.py` 允许命中 `CategoryPolicyService` / `CategoryDeleteAction`。
- 不应命中 `src.repositories`。
- UI 不需要直接使用 `CategoryStatus`，如出现需在日志中说明原因。

检查 Repository / Data 未改：

git diff --name-only -- src/repositories
git diff --name-only -- src/data

检查本轮未误动其他 UI / service：

git diff --name-only -- src/ui/dashboard.py
git diff --name-only -- src/ui/week_window.py
git diff --name-only -- src/ui/todo.py
git diff --name-only -- src/services/schedule_query_service.py
git diff --name-only -- src/services/schedule_sort_service.py
git diff --name-only -- src/services/weather_service.py

语法检查：

D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src\services\category_policy_service.py src\ui\list_picker.py src\ui\todo_board.py

范围检查：

git diff --name-only -- main.py
git diff --name-only -- requirements.txt
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch

预期：

- `src/repositories` 无 diff。
- `src/data` 无 diff。
- `dashboard.py` 无 diff。
- `week_window.py` 无 diff。
- `todo.py` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- `schedule_query_service.py` 无 diff。
- `schedule_sort_service.py` 无 diff。
- `weather_service.py` 无 diff。
- 最终只允许：
  - `src/services/category_policy_service.py`
  - `src/ui/list_picker.py`
  - `src/ui/todo_board.py`
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第三轮 3-4b（CategoryPolicyService 分类删除动作决策抽取）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 开工前动作映射基线
- 实现的 `CategoryPolicyService.choose_delete_action` 逻辑
- 未知状态兜底策略
- `list_picker.py` 替换了哪一处分支判断
- `todo_board.py` 替换了哪两处分支判断
- 明确记录：未修改 Repository
- 明确记录：未修改 `soft_delete_category` / `hard_delete_category`
- 明确记录：未修改 `db_manager` API
- 明确记录：未改 UI 文案、布局、交互流程
- 修改后 active / historical / empty 动作映射是否与基线一致
- 当前分类状态到动作映射验证结果
- `db_manager.check_category_status` 返回字符串验证结果
- 静态依赖检查结果
- UI 引用检查结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
