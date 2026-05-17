# Work Log

本文件只记录当前阶段/当前轮次的执行日志。

历史日志已归档到 `manage_instruction/History_Log.md`。

## 当前状态

第二轮 Data 层整理与模型拆分已完成并归档。

当前等待第三轮（纯业务查询与排序服务）规划与小工单发布。

## 当前轮次注意事项

- 暂无可执行小工单。
- 第三轮任务发布前，应先由决策窗口基于 `Work_Formulation.md` 细化第三轮边界。
- 执行窗口不得沿用第二轮 D 的提示词继续执行。

## 2026-05-17 第三轮 3-0（静态审查与旧逻辑定位）

- 本轮任务名称：第三轮 3-0（静态审查与旧逻辑定位）。
- 开工前是否已有管理文档 diff：
  - 有。开工前已有 `manage_instruction/Work_Task_Prompts.md`（顾问窗口维护的 3-0 提示词锚点）diff，不视为本轮源码改动。
- 实际修改文件：
  - `manage_instruction/Work_Log.md`
- 已读取的关键文件：
  - `manage_instruction/Work_Instruction.md`
  - `src/repositories/schedule_repository.py`
  - `src/repositories/category_repository.py`
  - `src/repositories/__init__.py`
  - `src/data/database.py`
  - `src/data/models.py`
  - `src/ui/dashboard.py`
  - `src/ui/week_window.py`
  - `src/ui/todo.py`
  - `src/ui/todo_board.py`
  - `src/ui/list_picker.py`
  - `src/ui/main_window.py`
  - `src/ui/month_window.py`
  - `src/services/weather_service.py`
- 日期过滤逻辑位置清单：
  - `src/repositories/schedule_repository.py:53` `get_schedules_for_date(target_date)`：核心日期过滤（`start_time/end_time` 与 `target_date` 比较）。
  - `src/repositories/schedule_repository.py:63-71`：`start_date/end_date` 分支判断（区间命中、截止日命中）。
  - `src/ui/week_window.py:1031-1032`：周视图按每天调用 `db_manager.get_schedules_for_date(target_date)`。
  - `src/ui/dashboard.py:499`：日视图调用 `db_manager.get_schedules_for_date(self.current_date)`。
- 日程/待办区分逻辑位置清单：
  - Repository 侧：`src/repositories/schedule_repository.py:57-60`（`item_type == "todo"` 的特殊分支）。
  - 日视图：`src/ui/dashboard.py:506-510`（`item_type == 'todo'` 或 `type == 1` 判为待办并排除）。
  - 周视图：`src/ui/week_window.py:1032`（仅保留 `item_type == 'schedule'` 且 `status != 2`）。
  - 待办列表：`src/ui/todo.py:445-450`（同样以 `item_type/type` 判定待办）。
  - 待办看板：`src/ui/todo_board.py:1298-1302`（`is_todo` 且 `status == 0` 才进入渲染集合）。
- 日视图排序逻辑位置清单：
  - `src/ui/dashboard.py:512-519`：`rank_pin` + `rank_status` + `sort_order`（降序）组合排序。
- 周视图排序逻辑位置清单：
  - `src/ui/week_window.py:1038-1045`：与日视图同构（`rank_pin/rank_status/sort_order`）。
- 待办列表排序逻辑位置清单：
  - `src/ui/todo.py:454-463`：与日视图同构（`rank_pin/rank_status/sort_order`）。
- 待办看板排序逻辑位置清单：
  - 主看板渲染排序：`src/ui/todo_board.py:1316-1322`（`rank_pin` + `sort_order`）。
  - 看板“一键按重要性排序”：`src/ui/todo_board.py:1765-1794`（按 `priority`、`created_at` 排，再写回 `sort_order`）。
- 分类状态判断逻辑位置清单：
  - 核心策略：`src/repositories/category_repository.py:50-61`（`empty/active/historical`）。
  - 委托门面：`src/data/database.py:294-295`（`db_manager.check_category_status -> category_repository`）。
  - UI 使用点：`src/ui/list_picker.py:356-382`、`src/ui/todo_board.py:976-990`、`src/ui/todo_board.py:2028-2048`。
- 分类删除策略位置清单：
  - 核心执行：`src/repositories/category_repository.py:63-72`（`soft_delete_category` / `hard_delete_category`）。
  - 委托门面：`src/data/database.py:297-301`。
  - UI 决策：
    - `src/ui/list_picker.py:356-382`（active 拦截、historical 二次确认后软删、empty 硬删）。
    - `src/ui/todo_board.py:976-990` 与 `2028-2048`（同类策略）。
- 四象限相关现有逻辑或缺口：
  - 已有入口/文案：
    - `src/ui/dashboard.py:74` 视图项包含 `priority: 四象限`。
    - `src/ui/week_window.py:435`、`src/ui/month_window.py:472` 视图切换含“象限/四象限”。
    - `src/ui/main_window.py:632-634` 仅 toast：`准备切换至：四象限视图`。
  - 已有可用字段：`src/data/models.py:33` `priority`，以及 `start_time/end_time/status/is_pinned/created_at/sort_order`。
  - 缺口结论：当前无独立“四象限分类服务”或稳定分类规则实现，现状主要是“优先级展示/排序”，非四象限业务分类。
- 按来源归类的逻辑分布：
  - `database.py`：主要是兼容门面委托（`get_schedules_for_date`、分类状态/删除等转发），非策略主实现。
  - `repositories`：
    - `schedule_repository.py`：日期过滤 + 一套基础排序。
    - `category_repository.py`：分类状态判断与删除策略核心。
  - `UI`：
    - `dashboard/week_window/todo/todo_board` 各自有二次过滤与排序规则。
    - `list_picker/todo_board` 承担分类删除流程分支决策。
  - `services`：当前仅 `weather_service.py`，与第三轮目标无关；暂无查询/排序/分类策略服务。
  - 其他：`models.py` 提供可用于四象限纯逻辑的字段基础。
- 第三轮适合抽取的逻辑清单：
  - 统一的“日程/待办判定谓词”和“状态判定谓词（完成/隐藏/逾期）”。
  - 日期过滤核心规则（从 `schedule_repository.get_schedules_for_date` 抽离为纯函数/服务）。
  - 视图排序 key 生成逻辑（day/week/todo/todo_board 主排序分别抽为明确策略函数）。
  - 分类状态判断与删除策略判定（`empty/active/historical` 与 soft/hard delete 决策条件）抽为 category policy。
  - 四象限仅做“纯逻辑规则准备与缺口报告”，不接 UI。
- 应留到后续轮次的逻辑清单：
  - 拖拽重排后写回 `sort_order`（`dashboard/week_window/todo/todo_board` 的写库行为）。
  - `todo_board._sort_by_priority` 的“排序+持久化写回”整段（非纯查询逻辑）。
  - 重复日程写入、提醒、编辑流程、UI 路由切换等非第三轮纯逻辑目标。
- 是否建议拆分 3-2、3-3、3-4：
  - 建议继续拆分。
  - 3-2 可拆：`3-2a` Repository 日期过滤纯逻辑抽取；`3-2b` UI 侧 todo/schedule 区分统一。
  - 3-3 可拆：`3-3a` day/week/todo 排序 key 抽取；`3-3b` todo_board 主排序与 priority 排序（后者含写库，需单独边界）。
  - 3-4 可拆：`3-4a` 分类状态判断抽取；`3-4b` 删除策略分支抽取（active 拦截、historical 软删、empty 硬删）。
- 范围检查结果：
  - `git diff --name-only -- src/data` -> 无输出。
  - `git diff --name-only -- src/repositories` -> 无输出。
  - `git diff --name-only -- src/ui` -> 无输出。
  - `git diff --name-only -- main.py` -> 无输出。
  - `git diff --name-only -- requirements.txt` -> 无输出。
  - `git diff --name-only -- schedule.db` -> 无输出。
  - `git diff --name-only` -> `manage_instruction/Work_Log.md`、`manage_instruction/Work_Task_Prompts.md`。
  - `git status --short --branch` -> `M manage_instruction/Work_Log.md`、`M manage_instruction/Work_Task_Prompts.md`。
- 未完成事项：
  - 等待顾问窗口基于本定位结果下发 3-1 或 3-2a 细化工单。
- 风险或疑点：
  - 同一业务在 Repository 与多个 UI 层存在重复/并行排序与过滤规则，若直接合并易改变可见顺序。
  - `todo_board._sort_by_priority` 含持久化写回，不能与纯读排序策略混做一轮抽取。
  - “四象限”目前是入口占位，不是完整业务实现，需先明确稳定规则再落地服务。
