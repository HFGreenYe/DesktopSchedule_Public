# Work Task Prompts

用途：记录“当前待执行小工单”的提示词锚点与简要复核状态。

## 当前小工单

第三轮 3-0：静态审查与旧逻辑定位。

状态：顾问窗口已审查，提示词与 `Work_Instruction.md` 中 3-0 边界一致，可转执行窗口。

提示词：

~~~~markdown
请执行第三轮 3-0：静态审查与旧逻辑定位。本轮只做代码阅读、静态搜索和日志记录，不修改源码。

## 1. 本轮目标

基于 manage_instruction/Work_Instruction.md 中的第三轮阶段合同，定位当前项目中“查询、过滤、排序、分类策略、四象限相关逻辑”的现有位置，为后续服务抽取做边界准备。

本轮只回答这些问题：

- 日期过滤与日程/待办区分逻辑在哪里？
- 日视图排序逻辑在哪里？
- 周视图排序逻辑在哪里？
- 待办列表排序逻辑在哪里？
- 待办看板排序逻辑在哪里？
- 分类状态判断和分类删除策略在哪里？
- 四象限相关逻辑是否已有？如果没有，现有字段是否足够支撑纯逻辑服务？
- 哪些逻辑适合第三轮抽取？
- 哪些逻辑应留到后续轮次？

本轮不做任何代码修复，不创建 service 文件，不替换 UI 调用。

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

禁止事项：

- 不修改源码。
- 不修改 UI。
- 不修改数据库。
- 不运行写入型验证。
- 不创建 service 文件。
- 不抽取逻辑。
- 不调整 import。
- 不接四象限 UI。
- 不改变任何业务行为。

若开工前已有管理文档 diff，需在 Work_Log.md 中单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取 manage_instruction/Work_Instruction.md 的第三轮阶段合同。
2. 使用静态搜索定位日期过滤逻辑。
3. 使用静态搜索定位日程/待办区分逻辑。
4. 使用静态搜索定位排序逻辑：
   - 日视图
   - 周视图
   - 待办列表
   - 待办看板
5. 使用静态搜索定位分类状态判断和分类删除策略。
6. 使用静态搜索定位四象限相关逻辑或确认缺口。
7. 按来源归类：
   - src/data/database.py
   - src/repositories/
   - src/ui/
   - src/services/
   - 其他文件
8. 给出第三轮可抽取项清单。
9. 给出应留到后续轮次的项清单。
10. 判断 3-2、3-3、3-4 是否需要继续拆成更小工单。
11. 记录所有结论到 Work_Log.md。

## 4. 建议静态搜索命令

先读取第三轮合同：

```cmd
Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
```

定位日期过滤、时间字段、日程/待办区分：

```cmd
rg -n "get_schedules_for_date|target_date|start_time|end_time|item_type|todo|schedule|date\(|today|selected_date" src
```

定位排序逻辑：

```cmd
rg -n "sort|sorted|sort_key|order_by|priority|is_pinned|status|created_at|sort_order|end_time|start_time" src
```

重点检查 UI 排序位置：

```cmd
rg -n "sort|sorted|sort_key|priority|is_pinned|status|created_at|sort_order|end_time|start_time" src/ui
```

重点检查 repository / data 排序位置：

```cmd
rg -n "sort|sorted|sort_key|order_by|priority|is_pinned|status|created_at|sort_order|end_time|start_time" src/data src/repositories
```

定位分类状态、删除策略：

```cmd
rg -n "check_category_status|soft_delete_category|hard_delete_category|category|categories|is_deleted|list_type|historical|active|empty" src
```

定位四象限相关逻辑或命名：

```cmd
rg -n "matrix|quadrant|四象限|重要|紧急|urgent|important|priority" src
```

定位已有 service 情况，确认不要误动无关 service：

```cmd
rg --files src/services
Get-Content -Path src\services\*.py -Encoding UTF8
```

查看候选核心文件时，可按需读取：

```cmd
Get-Content -Path src\data\database.py -Encoding UTF8
Get-Content -Path src\repositories\schedule_repository.py -Encoding UTF8
Get-Content -Path src\repositories\category_repository.py -Encoding UTF8
```

如搜索结果指向 UI 文件，只读相关文件，不修改：

```cmd
Get-Content -Path src\ui\dashboard.py -Encoding UTF8
Get-Content -Path src\ui\week_window.py -Encoding UTF8
Get-Content -Path src\ui\todo.py -Encoding UTF8
Get-Content -Path src\ui\todo_board.py -Encoding UTF8
```

如果某些文件不存在，记录“不存在/无需读取”，不要创建文件。

## 5. 验收与日志要求

完成后更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第三轮 3-0（静态审查与旧逻辑定位）
- 开工前是否已有管理文档 diff
- 实际修改文件
- 已读取的关键文件
- 日期过滤逻辑位置清单
- 日程/待办区分逻辑位置清单
- 日视图排序逻辑位置清单
- 周视图排序逻辑位置清单
- 待办列表排序逻辑位置清单
- 待办看板排序逻辑位置清单
- 分类状态判断逻辑位置清单
- 分类删除策略位置清单
- 四象限相关现有逻辑或缺口
- 按来源归类的逻辑分布：
  - database.py
  - repositories
  - UI
  - services
  - 其他
- 第三轮适合抽取的逻辑清单
- 应留到后续轮次的逻辑清单
- 是否建议拆分 3-2、3-3、3-4
- 未完成事项
- 风险或疑点

范围检查必须执行：

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

完成后不要提交 Git，等待顾问窗口复核。
~~~~

## 复核锚点

- 3-0 只做静态审查与旧逻辑定位，不允许修改源码、数据库或 UI。
- 复核时重点确认定位结果覆盖日期过滤、日/周/待办排序、分类状态/删除策略、四象限缺口。
- 复核时重点确认是否给出第三轮可抽取项、后续轮次保留项，以及 3-2/3-3/3-4 是否需要继续拆分。
- 复核时重点检查 `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 均无 diff。
