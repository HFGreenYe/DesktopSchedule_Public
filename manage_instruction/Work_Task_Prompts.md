# Work Task Prompts

## 第五轮 5-0 提示词（静态审查与只读基线定位）

### 1. 本轮目标

- 本工单为只读审查工单：建立“当前提醒链路”的源码基线，不做任何重构与行为修改。
- 结论必须以源码为准，不得根据 README、旧日志或历史文档推断运行行为。
- 特别注意：`main.py` 是应用启动入口；`src/ui/main_window.py` 是主窗口协调器与提醒扫描所在地，不得混淆。

### 2. 允许/禁止

- 允许：读取代码、检索调用链、执行只读命令、更新 `manage_instruction/Work_Log.md` 日志。
- 禁止：修改任何源码文件、修改数据库、补做“顺手重构”、新增/删除依赖、改 `requirements.txt`、改 `schedule.db`。
- 禁止：修改本提示词文件 `manage_instruction/Work_Task_Prompts.md`；如发现提示词问题，只能在 `Work_Log.md` 记录并交回顾问/决策窗口处理。
- 禁止将本工单升级为实现工单（例如提前创建 `reminder_service.py`）。

### 3. 具体任务

- 必须定位 `src/ui/main_window.py` 中：
  - `_init_scheduler`
  - `check_reminders`
  - `triggered_reminders`
  - `show_reminder_popup`
- 必须定位 `src/ui/reminder_pop.py` 中三条停声路径并说明触发入口：
  - 顶部关闭按钮
  - “知道了”
  - “关闭闹钟”
- 必须检查下列提醒设置/展示相关文件，仅做“位置与作用说明”，不改代码：
  - `src/ui/alarm_picker.py`
  - `src/ui/alarm_picker_week.py`
  - `src/ui/add_view.py`
  - `src/ui/add_view_week.py`
  - `src/ui/schedule_detail_pop.py`
  - `src/data/models.py`
- 位置说明必须尽量包含文件、类/函数、关键行号；如果行号因工具限制无法稳定获取，必须说明原因。
- 输出必须使用以下固定结构（按顺序）：
  - 扫描链路
  - 触发条件
  - 去重生命周期
  - 弹窗/声音边界
  - 提醒设置入口
  - 可抽 service 的逻辑
  - 必须留 UI 的副作用
  - 风险点

### 4. 验收命令

- 开工前记录：`git status --short`，并把开工时已经存在的 diff 记为“既有基线”，不得误判为 5-0 新增 diff。
- 审查后至少执行：
  - `git status --short`
  - `git diff --name-only`
  - `git diff --name-only -- src`
  - `git diff --name-only -- main.py requirements.txt schedule.db`
- 验收标准：
  - `src` 无由本工单产生的新 diff。
  - `main.py`、`requirements.txt`、`schedule.db` 无由本工单产生的新 diff。
  - 若 `git diff --name-only` 显示开工前已有的管理文档或依赖文件 diff，必须在日志中标注为“既有 diff”，不得声称由 5-0 产生。

### 5. 日志要求

- 在 `manage_instruction/Work_Log.md` 新增 `5-0` 记录，至少包含：
  - 本轮任务名与边界（只读）
  - 开工前 git 状态基线，以及哪些 diff 属于既有状态
  - 实际检索到的关键函数/文件位置
  - 8 段固定结构结论摘要
  - 验收命令与结果（含“无新增 diff”结论）
  - 风险与后续建议（供 5-1 使用）
