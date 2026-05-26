# Work Task Prompts

## 第八轮 8-1：UI 包目录骨架与导入边界准备

```markdown
请执行第八轮 8-1：UI 包目录骨架与导入边界准备。本轮只建目录骨架与 `__init__.py`，不迁移任何类，不改调用方。

## 1. 本轮目标

基于 8-0 结论，建立第八轮后续拆分需要的 UI 包骨架，确保可 import、无副作用、无循环导入风险。

本轮目标：

- 新增（若不存在）以下目录与 `__init__.py`：
  - `src/ui/common/__init__.py`
  - `src/ui/views/__init__.py`
  - `src/ui/dialogs/__init__.py`
  - `src/ui/popups/__init__.py`
  - `src/ui/utils/__init__.py`
- 不移动旧类。
- 不替换旧 import。
- 不改运行行为。

## 2. 允许/禁止

允许修改：

- `src/ui/common/__init__.py`
- `src/ui/views/__init__.py`
- `src/ui/dialogs/__init__.py`
- `src/ui/popups/__init__.py`
- `src/ui/utils/__init__.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

禁止修改：

- 现有 `src/ui/*.py` 业务文件
- `src/theme/`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `src/utils/signals.py`
- `src/utils/styles.py`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不新增功能。
- 不触发 QApplication。
- 不连接 signal。
- 不创建与现有 `src/ui/*.py` 同名的包目录，例如不得创建 `src/ui/components/`，以免遮蔽既有 `src/ui/components.py` 和 `from .components import ...` 导入。
- 不提交 Git。

## 3. 具体任务

1. 读取：

- `manage_instruction/Work_Instruction.md`
- `manage_instruction/Work_Log.md`（含 8-0 结论）

2. 检查目录现状：

- `Get-ChildItem -Path src\ui -Force`

3. 新建目录骨架（如不存在则创建）：

- `src/ui/common/`
- `src/ui/views/`
- `src/ui/dialogs/`
- `src/ui/popups/`
- `src/ui/utils/`

4. 在以上目录新增 `__init__.py`（轻量空文件或仅模块说明注释）。

- 不写任何会触发副作用的代码。
- 不 import 具体 UI 类。

5. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

目录检查：

- `Get-ChildItem -Path src\ui -Directory | Select-Object Name`
- `Get-ChildItem -Path src\ui\common,src\ui\views,src\ui\dialogs,src\ui\popups,src\ui\utils -Force`

import 验证：

- `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import src.ui.common, src.ui.views, src.ui.dialogs, src.ui.popups, src.ui.utils; from src.ui.components import SharedMoreMenu; print('ui package skeleton import ok')"`

语法检查：

- `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/common/__init__.py src/ui/views/__init__.py src/ui/dialogs/__init__.py src/ui/popups/__init__.py src/ui/utils/__init__.py`

范围检查：

- `git diff --name-only -- src/ui`
- `git diff --name-only -- src/theme`
- `git diff --name-only -- src/data`
- `git diff --name-only -- src/repositories`
- `git diff --name-only -- src/services`
- `git diff --name-only -- src/controllers`
- `git diff --name-only -- src/utils/signals.py`
- `git diff --name-only -- src/utils/styles.py`
- `git diff --name-only -- main.py`
- `git diff --name-only -- requirements.txt`
- `git diff --name-only -- schedule.db`
- `git diff --name-only`
- `git status --short --branch`

预期：

- 仅允许新增/修改：
  - `src/ui/common/__init__.py`
  - `src/ui/views/__init__.py`
  - `src/ui/dialogs/__init__.py`
  - `src/ui/popups/__init__.py`
  - `src/ui/utils/__init__.py`
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. Work_Log.md 记录要求

至少记录：

- 本轮任务名称：第八轮 8-1（UI 包目录骨架与导入边界准备）
- 开工前 git 状态
- 实际修改文件
- 新增目录和 `__init__.py` 清单
- import 验证结果
- py_compile 结果
- 无副作用说明（未触发 QApplication/未连接信号/未迁移类）
- diff 范围检查结果
- 未完成事项
- 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
```
