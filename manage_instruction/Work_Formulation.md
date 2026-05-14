# Work Formulation

生成日期：2026-05-13

用途：本文件是当前项目架构改写的主方案文件。当前执行阶段按本文前半部分的首批施工蓝图推进；长期演进目标见文末“最终目标版本”。

---

## 1. 结论

当前确认采用“兼容式渐进重构”方案。

核心原则：

- 不重写产品。
- 不大面积改 UI。
- 保留现有运行效果。
- 保留 `db_manager` 作为过渡门面。
- 新增架构能力优先走旁路，不替换旧调用。
- 新功能和新拆分组件必须遵守新的样式与事件规范。

本轮新增确认两项前置基础设施：

1. 皮肤/QSS 架构提前到阶段 0/1。
2. `signals.py` 兼容式扩展为全局事件总线。

这两项只做骨架和规范，不在第一批大规模迁移旧 UI。

---

## 2. 为什么要前置皮肤/QSS 架构

原计划将换肤放在阶段 6。这个安排对“补齐功能”本身没问题，但对后续 UI 拆分和四象限视图开发不够理想。

如果先拆 UI，再处理样式，旧代码中大量 `setStyleSheet(...)` 硬编码颜色会被复制到更多新文件。等以后实现换肤时，需要在更多位置清理硬编码样式，工作量和风险都会上升。

因此，当前方案改为：

- 旧 UI 中已有的 `setStyleSheet(...)` 暂时不主动清理。
- 新建 UI、新拆分组件、四象限视图不得新增硬编码主题颜色。
- 新 UI 必须使用 QSS + 动态属性。
- 第一批只建立 `ThemeManager`、`light.qss`、`dark.qss` 和加载能力。

主题方向补充：

- 后续主题系统不以“亮色模式 + 暗色模式”双体系为核心，而以“颜色皮肤 / Skin Preset”为核心。
- 第一轮留下的 `light.qss`、`dark.qss` 只是主题基建占位，不代表最终必须为每套皮肤维护亮暗两套 QSS。
- 深色外观可以作为一套深色皮肤实现，避免形成 `N 个皮肤 × 2 套亮暗模式` 的维护成本。
- 后续进入主题设计轮次时，优先考虑基础 QSS + 皮肤变量/皮肤配置，而不是提前承诺固定的 light/dark 文件结构。

---

## 3. Qt 样式编码规范

PyQt/Qt QSS 不应按 Web CSS 的 `.class` 思维实现动态样式。推荐使用 Qt 动态属性。

推荐写法：

```python
button.setProperty("role", "primary")
```

对应 QSS：

```css
QPushButton[role="primary"] {
    background: #0cc0df;
    color: white;
}
```

动态修改属性后，Qt 样式引擎可能不会自动刷新控件样式。需要提供统一工具方法执行刷新：

```python
style = widget.style()
style.unpolish(widget)
style.polish(widget)
widget.update()
```

执行窗口实现 `ThemeManager` 时，应提供类似 `refresh_widget_style(widget)` 的辅助方法，避免 UI 文件里重复写这段逻辑。

---

## 4. Event Bus 兼容策略

当前项目已有 `src/utils/signals.py`：

```python
class AppSignals(QObject):
    skin_changed = pyqtSignal()

global_signals = AppSignals()
```

第一批允许将其扩展为全局事件总线，但必须后向兼容。

硬性约束：

- 保留 `global_signals` 实例名。
- 保留无参数 `skin_changed = pyqtSignal()`。
- 不修改旧信号签名。
- 新信号只能新增，不能替换旧信号。
- 第一批只提供事件通道，不要求旧窗口全部迁移到事件总线。

建议新增信号：

```python
class GlobalEventBus(QObject):
    skin_changed = pyqtSignal()          # 旧无参信号，必须保留
    theme_changed = pyqtSignal(str)      # 新主题信号
    schedule_added = pyqtSignal(object)
    schedule_updated = pyqtSignal(object)
    schedule_deleted = pyqtSignal(int)
    category_changed = pyqtSignal()
```

后续四象限视图优先监听事件总线，而不是直接依赖主窗口、周窗口、月窗口实例。

---

## 5. MatrixClassificationService 排期

四象限视图需要分类服务，但不放进第一批基建任务。

排期建议：

- 放入阶段 2 的业务服务抽取。
- 可以作为阶段 2E，或并入阶段 2B 的排序/日期过滤服务之后。
- 先做纯逻辑服务，不接 UI。

职责边界：

- 输入：Schedule 列表、当前时间。
- 输出：四个列表：重要紧急、重要不紧急、紧急不重要、不重要不紧急。
- 依据：现有 `priority`、`start_time`、`end_time` 等字段。
- 不新增数据库字段。
- 不依赖 QWidget。
- UI 层不得写复杂象限判断，只负责展示服务返回的数据。

---

## 6. 首批执行任务

执行窗口 B 第一轮建议严格按以下 7 步开工。

### 1. 建立目录骨架

新增目录：

```text
src/models/
src/repositories/
src/services/
src/controllers/
src/theme/
```

每个 Python 包目录添加 `__init__.py`。

注意：

- `src/models/` 只放 DTO、枚举、常量等轻量模型。
- Peewee ORM 模型暂时仍留在 `src/data/database.py`，或后续拆到 `src/data/models.py`。
- 第一批不迁移 Peewee 模型到 `src/models/`。

### 2. 新增 ThemeManager 和基础 QSS

新增建议文件：

```text
src/theme/__init__.py
src/theme/theme_manager.py
src/theme/light.qss
src/theme/dark.qss
```

第一批目标：

- 提供读取 QSS 的能力。
- 提供应用 QSS 到 `QApplication` 的能力。
- 提供刷新动态属性样式的方法。
- 保留旧 `src/utils/styles.py`，不强行迁移旧样式。

第一批不做：

- 不批量替换旧 UI 中的 `setStyleSheet(...)`。
- 不实现完整换肤 UI。
- 不改变现有默认视觉效果。

### 3. 扩展 signals.py 为兼容式事件总线

修改 `src/utils/signals.py`：

- 保留 `global_signals`。
- 保留无参 `skin_changed`。
- 新增 `theme_changed`、`schedule_added`、`schedule_updated`、`schedule_deleted`、`category_changed`。

第一批不要求旧窗口改为事件总线刷新。

### 4. 新增 Repository

新增建议文件：

```text
src/repositories/__init__.py
src/repositories/schedule_repository.py
src/repositories/category_repository.py
```

目标：

- 将 `Schedule`、`Category` 的基础查询和写入封装进 repository。
- repository 可以暂时引用 `src/data/database.py` 中的 Peewee 模型。
- 不改变数据库字段含义。
- 不改变旧查询结果语义。

### 5. DatabaseManager 内部委托 Repository

修改 `src/data/database.py`：

- `DatabaseManager` 保留现有公开方法。
- UI 仍然继续调用 `db_manager`。
- `DatabaseManager` 内部逐步委托 `ScheduleRepository`、`CategoryRepository`。
- 公开方法名、参数、返回类型、返回语义必须保持兼容。

第一批目标是“内部结构变化，外部行为不变”。

### 6. 修复 _migrate_db 的 migrator 作用域风险

现有迁移逻辑中存在 `migrator` 可能未定义的风险。第一批应顺手修复。

要求：

- 不改变迁移目标。
- 不删除已有迁移逻辑。
- 只修正作用域与健壮性。

### 7. 基础验证

第一批完成后，至少做以下验证：

- 应用可以启动。
- 数据库初始化不报错。
- 日程新增、读取、更新、删除基础路径可用。
- 清单新增、读取、删除基础路径可用。
- 旧 UI 仍通过 `db_manager` 正常工作。
- `global_signals.skin_changed` 旧无参信号仍可连接和触发。
- 新增 QSS/ThemeManager 不影响默认显示。

---

## 7. 禁止事项

第一批明确禁止：

- 不实现四象限 UI。
- 不实现完整换肤 UI。
- 不实现搜索、筛选、导出、同步等占位功能。
- 不大面积拆分 `main_window.py`、`todo_board.py`、`week_window.py`。
- 不批量替换旧 UI 样式。
- 不修改数据库字段含义。
- 不修改旧信号签名。
- 不让 UI 大面积直接改调 repository。

---

## 8. 给执行窗口 B 的一句话任务

请按本文第 6 节执行首批架构改写：只建立目录骨架、ThemeManager/QSS 基础设施、兼容式 GlobalEventBus、Repository 层，并让 `DatabaseManager` 内部委托 Repository，同时修复 `_migrate_db` 的 migrator 作用域风险。保持 UI 行为和 `db_manager` 对外接口不变，不实现新功能。
---

# 最终目标版本

本节来自旧 Work_Formulation.md 的长期架构设想，用作架构改写的最终演进方向。当前阶段不直接按本节一次性落地，而是先按上方“首批执行任务”进行兼容式改写，再逐步向本节目标靠近。

## C. 推荐目标框架

推荐采用“兼容式分层重构”，不要一次性重写 UI。核心原则是：先保留 UI 行为和信号协议，再逐步把数据访问、业务规则、路由协调搬到更合适的位置。

建议目标结构：

```text
src/
  app/
    bootstrap.py              # QApplication、窗口创建、全局装配
    main_controller.py         # 主窗口级路由与跨视图协调
    view_router.py             # day/week/month/todo/add/picker 切换
    refresh_bus.py             # 跨视图刷新信号总线

  domain/
    models.py                  # 轻量领域对象/枚举/状态常量
    schedule_rules.py          # 重复日程、日期计算、过期判断
    sorting.py                 # 日程/待办排序规则
    reminders.py               # 提醒触发判断

  data/
    models.py                  # Peewee Schedule/Category
    database.py                # db 连接、初始化、迁移
    schedule_repository.py     # 日程 CRUD
    category_repository.py     # 清单 CRUD

  services/
    schedule_service.py        # 新建、编辑、重复日程批量逻辑
    category_service.py        # 清单删除规则
    reminder_service.py        # 提醒扫描、触发记录
    weather_service.py         # 现有天气服务
    window_service.py          # 24H2 修复、置顶、挂起辅助

  ui/
    ...                        # 尽量保留现有页面代码
```

### 设计原则

- UI 文件先尽量少动。
- 保留现有 PyQt 信号名称和参数，除非同步修改所有调用方。
- 保留 `db_manager` 兼容接口，旧 UI 代码可以继续调用。
- 把纯业务规则先抽出来，例如重复日程、排序、过滤、提醒判断。
- 把数据库 CRUD 与业务规则分开。
- 把跨视图刷新和页面切换逐步移出 `MainWindow`。
- 占位功能继续标注为占位，不在重构中伪实现。

## D. 迁移顺序建议

### 阶段 0：准备与保护

- 确认 `Work_Formulation.md` 作为行为基线。
- 在 `manage_instruction/Work_Log.md` 中记录执行窗口每次操作。
- 使用 git 创建重构前检查点。
- 每次迁移只处理一个边界。

### 阶段 1：拆 data 层，但保留兼容接口

- 从 `src/data/database.py` 中拆出 Peewee 模型到 `src/data/models.py`。
- 保留数据库连接、建表、迁移逻辑到 `src/data/database.py`。
- 新增 `schedule_repository.py` 和 `category_repository.py`。
- 保留 `db_manager`，让旧调用方暂时不改或少改。
- 验收重点：应用仍能启动，新增/查询/编辑/删除日程和清单不变。

### 阶段 2：抽纯业务规则

- 抽重复日程生成和修改逻辑到 `domain/schedule_rules.py` 或 `services/schedule_service.py`。
- 抽日期过滤、过期判断、排序规则。
- 抽清单删除状态判断。
- UI 仍通过 `db_manager` 或 service 兼容层调用。

### 阶段 3：抽提醒服务

- 把提醒扫描、已触发集合、触发条件判断从 `MainWindow` 中移出。
- 保留提醒弹窗和声音行为不变。
- 验收重点：提醒时间到达仍会弹窗，闹钟仍播放系统声音。

### 阶段 4：抽主窗口路由与刷新协调

- 把视图切换、添加页来源记录、picker 返回逻辑逐步移到 controller/router。
- 把跨视图刷新信号集中到 refresh bus 或 controller。
- 保持现有页面信号协议。

### 阶段 5：整理 UI 页面

- 等数据层、业务层、路由层稳定后，再清理 UI 内重复组件。
- 优先合并重复的 picker/week picker、tooltip、图标加载等公共代码。
- 不在此阶段引入新功能。

---

# Git 本地版本保存策略

Git 可以在本地保存项目历史版本，不需要联网，也不需要 GitHub。每一次 `commit` 都相当于给当前项目拍一张可回退的快照。

本项目做架构改写时，Git 的主要用途不是协作，而是防止重构中途把项目改坏后无法回到之前状态。

## 1. 基本概念

- 工作区：你当前文件夹里的真实文件。
- 暂存区：准备放进下一次快照的文件列表。
- commit：一次本地历史快照。
- branch：一条独立修改路线。

最常用的理解方式：

```text
修改文件 -> git add -> git commit
```

`git add` 表示“这次快照我要包括这些文件”。  
`git commit` 表示“正式保存这次快照”。

## 2. 每次开工前先看状态

在项目根目录运行：

```powershell
cd D:\CodeProjects\DesktopSchedule\DesktopSchedule
git status
```

重点看：

- 哪些文件被修改。
- 哪些文件是新文件。
- 有没有你不认识的改动。

如果有不确定的改动，不要急着覆盖或回退，先弄清楚它是不是另一个窗口刚写的。

## 3. 重构前创建检查点

第一次正式改源码前，建议先做一个检查点：

```powershell
git status
git add .
git commit -m "checkpoint: before architecture refactor"
```

这表示：在架构改写前保存一次完整状态。后续如果改坏，可以回到这个点。

## 4. 每一小轮改完就提交

不要等很多天后一次性提交。推荐每完成一个小闭环就提交一次。

示例：

```powershell
git status
git add .
git commit -m "refactor: add repositories and db manager delegation"
```

适合提交的节点：

- 创建目录骨架后。
- repository + `db_manager` 委托完成并验证后。
- ThemeManager/EventBus 完成并验证后。
- 每个 service 抽取完成并验证后。
- 每次大 UI 文件拆分完成并验证后。

提交信息建议写清楚“做了什么”，不要只写 `update`。

## 5. 查看历史和改动

查看提交历史：

```powershell
git log --oneline
```

查看当前还没提交的改动：

```powershell
git diff
```

查看某个文件的改动：

```powershell
git diff -- src\data\database.py
```

查看某次提交做了什么：

```powershell
git show <commit_id>
```

## 6. 出问题时怎么处理

如果只是想看当前有哪些改动：

```powershell
git status
```

如果某个文件改坏了，但还没提交，可以恢复单个文件：

```powershell
git restore src\data\database.py
```

如果想撤销所有尚未提交的改动，必须非常谨慎：

```powershell
git restore .
```

这会丢掉当前未提交改动。执行前必须确认这些改动不需要保留。

如果某次提交已经保存，但后来发现不该做，推荐用：

```powershell
git revert <commit_id>
```

`git revert` 会创建一个新的提交来抵消旧提交，历史还在，比较安全。

不建议随便使用：

```powershell
git reset --hard <commit_id>
```

`git reset --hard` 会强制回到某个版本，并丢弃之后的未保存改动。只有非常确定时再用。

## 7. 推荐工作流

每次让执行窗口开工前：

```powershell
git status
```

确认状态干净或知道哪些文件已有改动。

执行窗口完成一轮后：

```powershell
git status
```

确认改了哪些文件，然后进行手工验证。

验证通过后：

```powershell
git add .
git commit -m "refactor: describe this small step"
```

最后让执行窗口更新 `manage_instruction/Work_Log.md`，记录这轮改了什么、怎么验证、还有什么风险。

## 8. 不建议提交的内容

通常不建议把以下内容作为正式源码历史的一部分，除非你明确需要：

- `.venv/`
- `__pycache__/`
- 临时日志
- 大型生成文件
- 不想公开的密钥文件

`.env` 里如果包含 API key，提交前要特别小心。本项目是本地私用时问题不大，但如果以后推到 GitHub，必须先处理 `.env`。

## 2026-05-14 阶段进度补充

第一轮 B 已完成（B-1 ~ B-14 委托落地，B-15 整体技术验收通过）。

---

# 架构改写轮次路线图

生成日期：2026-05-14

本路线图用于把“首批施工蓝图”和“最终目标版本”之间的过渡路径明确下来。后续 `Work_Instruction.md` 应按本路线图逐轮发布阶段指令；执行窗口仍按小工单推进，不一次性执行整轮。

## 总体判断

当前项目不适合一次性改到最终架构。更合适的方式是继续采用兼容式渐进重构：

- 每一轮只移动一个主要责任边界。
- 每一轮都保留 `db_manager` 或现有 UI 信号作为兼容接口。
- UI 行为不变优先于目录“看起来漂亮”。
- 新功能暂时不混入架构迁移，除非该轮明确以新功能为目标。
- 每轮结束都做 Git checkpoint。

## 当前已完成：第一轮

第一轮目标是“打地基，不动产品行为”。

已完成内容：

- 新建 `src/models/`、`src/repositories/`、`src/services/`、`src/controllers/`、`src/theme/`。
- 新增 `ThemeManager`、`light.qss`、`dark.qss`。
- 兼容式扩展 `global_signals`，保留无参 `skin_changed`。
- 新增 `ScheduleRepository`、`CategoryRepository`。
- `DatabaseManager` 低风险公开方法已逐步委托到 repository。
- 修复 `_migrate_db` 中 `migrator` 作用域风险。
- 通过 B-15 整体验收和人工启动检查。

当前结构可理解为：

```text
UI -> db_manager 兼容门面 -> Repository -> Peewee Model/database.py
```

## 第二轮：Data 层整理与模型拆分

目标：把数据库模型、连接、迁移、仓储职责进一步分清，但仍不改变 UI 调用。

建议范围：

- 从 `src/data/database.py` 拆出 Peewee 模型到 `src/data/models.py`。
- `src/data/database.py` 只保留数据库连接、初始化、迁移、`DatabaseManager` 兼容门面。
- 调整 `src/repositories/` 只依赖 `src/data/models.py` 和数据库连接，不再反向依赖 `DatabaseManager`。
- 保留 `src/repositories/` 这个当前位置，暂不为了目录洁癖移动到 `src/data/`，避免无收益路径震荡。
- 修正或记录 `__pycache__`、临时文件、依赖缺漏等工程卫生问题。

验收重点：

- 应用可启动。
- `db_manager` 对外 API 不变。
- 日程/清单基础增删改查不变。
- repository import 不产生循环依赖。

不做：

- 不抽业务 service。
- 不拆 UI。
- 不实现新功能。

## 第三轮：纯业务查询与排序服务

目标：把“怎么筛选、怎么排序、怎么分类”的纯逻辑从 UI 和 repository 中分离。

建议新增/完善：

- `src/services/schedule_query_service.py`
- `src/services/schedule_sort_service.py`
- `src/services/category_policy_service.py`
- `src/services/matrix_classification_service.py`

优先顺序：

1. 日期过滤与日程/待办区分。
2. 日视图、周视图、待办看板排序规则。
3. 清单状态判断和删除策略。
4. 四象限分类纯逻辑。

验收重点：

- 服务函数可以脱离 QWidget 单独验证。
- UI 展示顺序和旧逻辑一致。
- 四象限只产生数据分类结果，不做 UI。

不做：

- 不迁移重复日程写入逻辑。
- 不接四象限界面。

## 第四轮：日程写入与重复规则服务

目标：把高风险写入逻辑从 `DatabaseManager` 中逐步迁到 service，但继续由 `db_manager` 对外兜住旧接口。

建议范围：

- 新增或完善 `src/services/schedule_service.py`。
- 迁移 `add_schedule`。
- 迁移 `update_schedule_with_repeat`。
- 迁移 `_add_months` 或相关日期计算到规则模块。
- 明确重复日程 group_id、update_future、repeat_rule 的行为基线。

验收重点：

- 单次日程新增不变。
- 每日、每周、每月、每年重复生成不变。
- 编辑重复日程时“只改本条/改后续”行为不变。
- 不改变数据库字段含义。

说明：这是前几轮中风险最高的一轮，必须拆成多个小工单。

## 第五轮：提醒与运行期状态服务

目标：把提醒扫描、触发去重、提醒弹窗调用条件从 `MainWindow` 中分离。

建议新增：

- `src/services/reminder_service.py`

迁移范围：

- 提醒扫描逻辑。
- `triggered_reminders` 本次运行内去重逻辑。
- 提醒时间判断。
- 过期/无提醒/不提醒状态判断。

验收重点：

- 到点仍弹提醒。
- 关闭/停止按钮仍停止声音。
- 本次运行内不重复弹同一个提醒。
- 重启后去重状态不持久化，保持旧行为。

不做：

- 不改提醒弹窗 UI。
- 不新增提醒持久化功能。

## 第六轮：Controller / Router / EventBus 接管跨视图协调

目标：逐步降低 `MainWindow`、`WeekWindow`、`TodoBoardWindow`、`MonthWindow` 之间的互相引用和直接刷新耦合。

建议新增/完善：

- `src/controllers/main_controller.py`
- `src/controllers/view_router.py`
- `src/controllers/refresh_coordinator.py`

迁移范围：

- 视图切换。
- 添加页来源记录。
- picker 返回流程。
- 日程/清单变更后的跨视图刷新。
- 新增视图优先监听 `global_signals` 新信号。

验收重点：

- 日、周、月、待办之间切换不变。
- 添加、编辑、删除后相关视图刷新不变。
- 已打开详情弹窗刷新行为不变。

不做：

- 不一次性重写窗口结构。
- 不修改旧信号签名。

## 第七轮：Theme/QSS 接入与样式债务控制

目标：让主题系统开始真正参与应用，但先控制新增代码和新组件，不追求一口气清完旧样式。

主题路线：本轮应按“颜色皮肤 / Skin Preset”设计，不按每套皮肤再拆 light/dark 双模式设计。深色主题作为深色皮肤处理即可。

建议范围：

- 在应用启动处接入 `ThemeManager` 默认主题加载。
- 建立 QSS 动态属性命名规范。
- 为新视图、新组件使用 `role`/`state` 等动态属性。
- 选择少量公共按钮、卡片、输入框做样式试点。

验收重点：

- 默认视觉尽量保持。
- 动态属性刷新可用。
- 不出现大面积字体、颜色、布局突变。

不做：

- 不批量删除所有旧 `setStyleSheet(...)`。
- 不在本轮实现完整换肤设置页，除非后续明确把它作为功能轮。

## 第八轮：UI 大文件拆分与公共组件沉淀

目标：在数据层、服务层、控制层稳定后，再拆 UI 大文件，降低复制旧逻辑的风险。

优先对象：

- `src/ui/todo_board.py`
- `src/ui/week_window.py`
- `src/ui/main_window.py`
- picker、tooltip、icon loader、toast、schedule card、folder card 等公共组件。

建议拆分方向：

- `src/ui/components/`
- `src/ui/views/`
- `src/ui/dialogs/` 或 `src/ui/popups/`

验收重点：

- 页面显示不变。
- 拖拽、右键菜单、弹窗、排序、置顶、删除不变。
- 不引入新功能。

说明：这一轮看起来最像“整理代码”，但应该放在业务和协调逻辑稳定之后，否则容易把旧耦合复制到更多文件。

## 第九轮：新功能准备与四象限视图

目标：在架构已经能承载新功能后，再开始补功能。

优先功能：

- 四象限视图。
- 主题/换肤 UI。
- 搜索和筛选。
- 导出、同步等占位功能再单独评估。

四象限建议路径：

- 先用 `MatrixClassificationService` 提供四类数据。
- UI 只负责四个容器展示，不写复杂判断。
- 日程/待办变更后通过 EventBus 刷新。
- 不新增数据库字段，优先基于现有 `priority` 和时间字段。

## 建议轮次数量

如果只算“把当前已实现功能迁移到比较理想的架构，不补新功能”，建议至少按 8 轮走：

1. 第一轮：基建 + repository + db_manager 兼容委托（已完成）。
2. 第二轮：Data 层整理与 Peewee 模型拆分。
3. 第三轮：查询、排序、清单策略等纯业务服务。
4. 第四轮：日程写入与重复规则服务。
5. 第五轮：提醒服务。
6. 第六轮：Controller / Router / EventBus 协调层。
7. 第七轮：Theme/QSS 接入与样式规范落地。
8. 第八轮：UI 大文件拆分与公共组件沉淀。

如果把“四象限、换肤 UI、搜索筛选、导出同步”等新功能也算入最终目标，则至少再加第九轮及后续功能轮。

## 下一步建议

下一阶段建议发布“第二轮：Data 层整理与模型拆分”的阶段指令。

推荐先拆成小工单：

1. 只创建 `src/data/models.py` 并移动 Peewee `BaseModel`、`Category`、`Schedule`。
2. 调整 `database.py`、repository import，保持 `db_manager` 可用。
3. 单独验证迁移、建表、基础读写。
4. 再考虑是否需要整理数据库连接和迁移工具函数。

第二轮开始前应先确认：

- `git status` 干净。
- 第一轮 checkpoint 已提交。
- `Work_Instruction.md` 写入第二轮阶段合同。
