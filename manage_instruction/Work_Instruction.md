# Work Instruction

用途：本文件用于“当前阶段”的执行指令发布。

- 仅保留正在执行或即将执行的任务。
- 已完成阶段请归档到 `History_Instruction.md`，避免本文件长期堆积。
- 当前主路线图见 `Work_Formulation.md` 的“架构改写轮次路线图”。
- 改写前行为和目录快照见 `Work_Snapshot.md`。
- 执行过程记录写入 `Work_Log.md`。

---

# 当前阶段：第三轮 - 纯业务查询与排序服务

## 已完成并归档

- 第一轮：基建 + repository + db_manager 兼容委托。
- 第二轮：Data 层整理与模型拆分。
  - 第二轮 A/B/C/D 均已完成并归档。
  - 第二轮最终验收通过，`src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

---

## 第三轮目标

第三轮目标是把“查询、过滤、排序、分类策略”等纯业务逻辑从 UI、Repository、DatabaseManager 中逐步分离出来，形成可单独验证、可复用、不依赖 QWidget 的服务层。

本轮重点处理：

- 日期过滤与日程/待办区分逻辑。
- 日视图、周视图、待办列表、待办看板等排序规则。
- 分类状态判断和分类删除策略。
- 四象限分类的纯逻辑评估与最小服务准备。

本轮仍保持旧 UI 行为不变，旧 UI 继续通过 `db_manager` 或现有调用路径工作。

---

## 第三轮允许修改范围

第三轮整体允许修改：

- `src/services/`
- `src/data/database.py`
- `src/repositories/`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`

`src/services/` 允许范围仅限第三轮相关服务文件，例如查询、排序、分类策略、四象限纯逻辑服务。现有无关服务（例如 `src/services/weather_service.py`）默认不修改，除非后续小工单明确说明原因。

第三轮默认不修改 `src/ui/`。仅当具体小工单明确要求时，允许对 `src/ui/` 做最小调用替换：

- 不改布局。
- 不改视觉。
- 不改交互流程。
- 只把原本内联的纯排序/过滤/分类判断逻辑替换为 service 调用。
- 必须保留旧展示结果和用户可见行为。

---

## 第三轮禁止事项

- 不修改 `main.py`。
- 不修改 `requirements.txt`。
- 不修改 `Work_Snapshot.md`。
- 不修改 `Work_Formulation.md`。
- 不接四象限 UI。
- 不新增数据库字段。
- 不修改数据库字段含义、表名、默认值、迁移逻辑。
- 不修改现有无关 service，例如 `src/services/weather_service.py`，除非小工单明确要求。
- 不迁移重复日程写入逻辑。
- 不迁移提醒逻辑。
- 不迁移 Controller / Router / EventBus 协调逻辑。
- 不改变 `db_manager` 对外公开方法名、参数、返回语义。
- 不改变 Repository 方法名、参数、返回语义，除非小工单明确要求且完成兼容验证。
- 不实现新功能。
- 不拆 UI 大文件。
- 不改变现有 `priority` 等字段语义。
- 不保留 `schedule.db` 变更；如验收需要临时写入，必须清理并确认 `git diff --name-only -- schedule.db` 无输出。

---

## 行为保持原则

第三轮所有服务抽取必须满足：

- UI 展示顺序与旧逻辑一致。
- 查询结果集合与旧逻辑一致。
- 分类状态判断结果与旧逻辑一致。
- 临时服务调用不得改变数据库数据，除非小工单明确进入临时写入验收。
- 新 service 应尽量是纯 Python 逻辑，不依赖 QWidget。
- 如某段逻辑当前耦合在 UI 内，不直接搬动 UI，先记录位置和行为，再决定是否抽取纯函数。

---

## 第三轮小工单拆分草案

第三轮不沿用第二轮 A/B/C/D，采用 `3-0`、`3-1` 这种编号。

3-0 后可根据定位结果将 3-2、3-3、3-4 继续拆分为更小工单；不得为了匹配合同编号而一次抽取过多逻辑。

### 3-0：静态审查与旧逻辑定位

目标：

- 不改代码。
- 定位当前日期过滤、排序、分类状态、四象限相关逻辑分别在哪些文件。
- 标记逻辑来源：`database.py`、repository、UI、其他服务。
- 判断哪些逻辑适合第三轮抽取，哪些应留到后续轮次。

重点定位：

- 日期过滤与日程/待办区分。
- 日视图排序。
- 周视图排序。
- 待办列表排序。
- 待办看板排序。
- 分类状态判断和删除策略。
- 四象限分类相关现有逻辑或缺口。

验收重点：

- 输出清晰的位置清单。
- 明确第三轮可抽取项与禁止项。
- 明确是否需要拆分 3-2、3-3、3-4。
- `src/ui`、`src/data`、`src/repositories`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

### 3-1：服务骨架与边界确认

目标：

- 仅创建后续小工单确认会立即使用的最小 service 文件。
- 不创建无调用、无测试、无行为承接的空壳文件。
- 不接 UI。
- 不迁移复杂逻辑。

候选文件：

- `src/services/schedule_query_service.py`
- `src/services/schedule_sort_service.py`
- `src/services/category_policy_service.py`
- `src/services/matrix_classification_service.py`

是否创建上述文件，以 3-0 定位结果为准。

验收重点：

- 新 service 可 import。
- 不影响应用启动。
- 不改变旧调用路径。
- 不产生无用空壳文件。

### 3-2：日期过滤 / 查询逻辑抽取

目标：

- 抽取日程按日期过滤、日程/待办区分等纯逻辑。
- 优先从 Repository 或 DatabaseManager 中已有查询逻辑平移。
- 如需要替换 UI 内联过滤逻辑，必须在小工单中明确允许 `src/ui/` 最小调用替换。
- 保持旧 `db_manager.get_schedules_for_date(date)` 结果语义不变。

验收重点：

- 同一日期下，新旧结果数量和关键 id 一致。
- 返回类型不变。
- UI 可见结果不变。
- `schedule.db` 无 tracked diff。

### 3-3：排序策略抽取

目标：

- 抽取日视图、周视图、待办列表、待办看板等排序规则。
- 排序规则可能不完全一致，需按 3-0 结果拆分，不得一次性粗暴合并。
- 可引入 `schedule_sort_service.py` 或等价服务文件。
- 如需要替换 UI 内联排序逻辑，必须在小工单中明确允许 `src/ui/` 最小调用替换。

验收重点：

- 同一输入列表，新旧排序后的 id 顺序一致。
- 置顶、完成、过期、时间、优先级等排序权重不变。
- 对应 UI 展示顺序不变。
- 不改数据库。

### 3-4：分类状态 / 分类策略抽取

目标：

- 抽取分类状态判断、分类删除策略等纯业务判断。
- 可引入 `category_policy_service.py`。
- `db_manager.check_category_status(cat_id)` 对外结果不变。
- 不改变分类删除策略。

验收重点：

- `empty`、`active`、`historical` 等返回语义不变。
- 临时分类和临时日程验证后清理。
- 不改 UI。
- `schedule.db` 无 tracked diff。

### 3-5：四象限纯逻辑评估与最小服务准备

目标：

- 仅做四象限纯逻辑评估和最小服务准备。
- 如现有字段足够定义稳定规则，可准备 `MatrixClassificationService` 的纯逻辑。
- 如现有字段不足以定义稳定规则，只记录规则缺口，不强行实现分类结果。
- 不接 UI。
- 不新增字段。
- 不改变现有 `priority` 语义。

候选边界：

- 输入：Schedule 列表、当前时间。
- 输出：四组分类结果，或规则缺口报告。
- 依据：现有 `priority`、`start_time`、`end_time` 等字段。

验收重点：

- 服务可单独 import。
- 不依赖 QWidget。
- 不写数据库。
- 不接四象限界面。
- 不伪实现 UI 功能。

### 3-6：第三轮整体验收

目标：

- 汇总 3-0 到 3-5。
- 验证旧查询、排序、分类状态行为不变。
- 验证应用可启动。
- 确认第三轮可归档。

验收重点：

- `db_manager` 对外 API 不变。
- 读路径结果不变。
- 关键排序结果不变。
- 分类状态结果不变。
- 新增 service 可 import。
- 新增 service 不依赖 QWidget。
- `src/data`、`src/repositories`、`src/ui` 无非预期 diff。
- `main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。

---

## 第三轮整体验收标准

第三轮完成后必须确认：

- 所有新增 service 可 import。
- service 不依赖 QWidget。
- 旧 UI 启动路径不变。
- 旧 `db_manager` 调用仍可用。
- 查询结果、排序结果、分类状态结果与旧逻辑一致。
- 不产生数据库结构变化。
- 不接四象限界面。
- `src/data`、`src/repositories`、`src/ui`、`main.py`、`requirements.txt`、`schedule.db` 无非预期 diff。

---

## 首个小工单建议

第三轮首个小工单应为：

`3-0：静态审查与旧逻辑定位`

原因：

- 当前查询、排序、分类策略逻辑可能分散在 `database.py`、repository 和 UI 文件中。
- 直接抽 service 容易遗漏 UI 内隐含排序/过滤规则。
- 先定位旧逻辑，才能定义后续 3-1 到 3-5 的真实边界。

执行窗口在收到 3-0 正式提示词前，不得修改源码、数据库或管理文档以外文件。
