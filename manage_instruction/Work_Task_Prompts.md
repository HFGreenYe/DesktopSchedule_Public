# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第二轮 A-1：只新增 `src/data/connection.py`，不切换旧引用。

状态：等待执行窗口执行，执行后由顾问窗口复核。

## 正式执行提示词

~~~text
# 第二轮 A-1 执行提示词：只新增 connection.py，不切换旧引用

请执行第二轮 A-1：只新增 `src/data/connection.py`，不切换旧代码引用。

本次只执行 A-1，不得执行 A-2/A-3/A-4/A-5/A-6。

## 本轮目标

新增 `src/data/connection.py`，在其中定义与当前 `src/data/database.py` 完全一致的数据库连接基础对象：

- `BASE_DIR`
- `DB_PATH`
- `db = SqliteDatabase(DB_PATH)`

本轮只是建立连接基础文件，不让任何旧代码改用它。

## 允许修改

只允许修改：

- `src/data/connection.py`
- `manage_instruction/Work_Log.md`

## 禁止修改

禁止修改：

- `src/data/database.py`
- `src/data/models.py`
- `src/repositories/`
- `src/ui/`
- `main.py`
- `src/theme/`
- `src/utils/signals.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`
- `Work_Task_Prompts.md`

同时禁止：

- 不执行 A-2/A-3/A-4/A-5/A-6。
- 不让 `database.py` 改用 `connection.py`。
- 不新增 `models.py`。
- 不修改 Repository。
- 不改业务逻辑。
- 不改数据库字段。
- 不改迁移逻辑。
- 不实现新功能。
- 不做格式化大扫除。

## 实现要求

1. 新增文件：

   `src/data/connection.py`

2. `connection.py` 中只放数据库连接基础对象，逻辑必须与当前 `src/data/database.py` 中的定义一致。

   也就是保持同样的：

   - `BASE_DIR` 计算方式
   - `DB_PATH` 计算方式
   - `db = SqliteDatabase(DB_PATH)`

3. `connection.py` 不得导入：

   - `src.data.database`
   - `src.data.models`
   - `src.repositories`
   - `db_manager`
   - 任何 UI 模块

4. 本轮完成后，旧运行路径仍然保持：

   `database.py` 继续使用它自己当前的 `BASE_DIR`、`DB_PATH`、`db` 定义。

5. 本轮只是为后续 A-2 做准备，不改变当前应用行为。

## 建议验收命令

### 1. connection.py import 验证

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.connection import db, BASE_DIR, DB_PATH; print('connection import ok'); print(BASE_DIR); print(DB_PATH); print(type(db).__name__)"
```

### 2. 对比 DB_PATH 与旧 database.py，并确认旧 db_manager 仍可用

```powershell
D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.data.connection import DB_PATH as p1; from src.data.database import DB_PATH as p2, db_manager; print('same path:', p1 == p2); print('db import ok'); print(len(db_manager.get_all_schedules()))"
```

预期：

- `same path: True`
- `db import ok`
- `get_all_schedules()` 可正常返回数量

### 3. 范围检查

```powershell
git diff --name-only -- src/data/database.py
git diff --name-only -- src/data/models.py
git diff --name-only -- src/repositories
git diff --name-only -- src/ui
git diff --name-only -- schedule.db
git diff --name-only
git status --short --branch
```

预期：

- `git diff --name-only -- src/data/database.py` 无输出
- `git diff --name-only -- src/data/models.py` 无输出
- `git diff --name-only -- src/repositories` 无输出
- `git diff --name-only -- src/ui` 无输出
- `git diff --name-only -- schedule.db` 无输出
- `git diff --name-only` 只包含：
  - `src/data/connection.py`
  - `manage_instruction/Work_Log.md`
  - 以及本轮开始前已经存在的管理文档改动

如出现非允许范围文件，停止并说明原因。

## Work_Log.md 记录要求

完成后必须更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第二轮 A-1（只新增 connection.py，不切换旧引用）
- 实际修改文件
- `connection.py` 中 `BASE_DIR` / `DB_PATH` / `db` 的来源说明
- 是否确认 `connection.py` 没有导入 `database.py`、`models.py`、Repository、UI 或 `db_manager`
- connection.py import 验证命令和结果
- DB_PATH 对比与旧 `db_manager` 可用性验证命令和结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果任务中途失败，也必须写入：

- 失败位置
- 关键报错摘要
- 是否已回滚
- 当前工作区状态

## 完成后要求

完成后不要提交 Git，等待顾问窗口复核。
~~~

## 复核锚点

- 只允许新增 `src/data/connection.py` 并更新 `Work_Log.md`。
- `src/data/database.py` 本轮必须无 diff。
- `src/data/models.py` 本轮不得出现。
- `connection.py` 不得导入 `database.py`、`models.py`、Repository、UI 或 `db_manager`。
- `DB_PATH` 必须与旧 `src.data.database.DB_PATH` 一致。
