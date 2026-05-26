# Work Task Prompts

## 第八轮 8-3a：公共 tooltip / toast 边界静态定位

```markdown
请执行第八轮 8-3a：公共 tooltip / toast 边界静态定位。本轮只做静态审查、代码阅读、搜索和日志记录，不改源码。

## 1. 本轮目标

基于第八轮阶段合同和 8-0 到 8-2b 的结论，定位当前 UI 中 tooltip / toast / 临时提示组件的分布、重复逻辑、生命周期和可拆边界。

本轮目标：

- 定位 `CustomToolTip`、`ToolTipFilter`、`CountdownToolTip`、`CountdownToolTipFilter` 等 tooltip 相关实现。
- 定位 `show_toast`、`toast_label`、`toast_widget`、toast timer、临时提示 QLabel 等 toast/提示条逻辑。
- 记录每个实现的：
  - 所在文件
  - 输入参数
  - parent 依赖
  - timer / eventFilter / hide / close 行为
  - 显示位置策略
  - 文案来源
  - 是否依赖具体窗口状态
  - 是否适合第八轮提取
- 输出 tooltip / toast 职责地图。
- 输出低风险、中风险、高风险候选。
- 判断是否适合进入 8-3b 单点提取。
- 不创建 `tooltip.py` / `toast.py`。
- 不迁移任何类。
- 不替换任何调用方。
- 不改变 UI 行为。

## 2. 允许/禁止

本轮允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

本轮禁止修改：

- `src/`
- `assets/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不新增 `src/ui/common/tooltip.py`。
- 不新增 `src/ui/common/toast.py`。
- 不修改任何 `src/ui/*.py`。
- 不修改 `src/theme/default.qss`。
- 不修改 icon loader。
- 不清理 `header.py` 中的 import 残留。
- 不提交 Git。

若开工前已有 diff，需在 `Work_Log.md` 单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取当前基线：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8

2. 搜索 tooltip 相关实现：

    rg -n "CustomToolTip|ToolTipFilter|CountdownToolTip|CountdownToolTipFilter|QToolTip|tooltip|toolTip|setToolTip|eventFilter|Enter|Leave|Hover" src/ui

3. 搜索 toast / 临时提示相关实现：

    rg -n "show_toast|toast|Toast|toast_label|toast_widget|QTimer|singleShot|hide\\(|close\\(|临时|提示|成功|失败" src/ui

4. 重点检查以下文件中的 tooltip / toast / 临时提示逻辑：

    src/ui/header.py
    src/ui/components.py
    src/ui/widgets.py
    src/ui/dashboard.py
    src/ui/main_window.py
    src/ui/week_window.py
    src/ui/month_window.py
    src/ui/todo.py
    src/ui/todo_board.py
    src/ui/list_picker.py
    src/ui/alarm_picker.py
    src/ui/alarm_picker_week.py
    src/ui/add_view.py
    src/ui/add_view_week.py
    src/ui/schedule_detail_pop.py
    src/ui/hanging_widget.py

5. 建立 tooltip 职责地图：

    对每个 tooltip 实现记录：

    - 文件与类/函数名
    - 是自定义 widget、eventFilter，还是 Qt 原生 tooltip
    - 触发方式
    - parent / target widget 依赖
    - timer 依赖
    - 显示位置计算方式
    - 关闭/隐藏方式
    - 是否复用或重复
    - 风险等级
    - 是否适合 8-3b 单点提取

6. 建立 toast 职责地图：

    对每个 toast / 临时提示实现记录：

    - 文件与函数/成员变量名
    - 创建方式
    - 显示位置
    - 持续时间
    - timer 生命周期
    - parent 依赖
    - 文案来源
    - 是否影响业务流程
    - 风险等级
    - 是否适合 8-3b 单点提取

7. 输出候选建议：

    - 低风险候选：可在 8-3b 单点提取。
    - 中风险候选：需要先做行为基线或只读验证。
    - 高风险候选：推迟到后续 UI 拆分或功能轮。

8. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

tooltip 搜索：

    rg -n "CustomToolTip|ToolTipFilter|CountdownToolTip|CountdownToolTipFilter|QToolTip|tooltip|toolTip|setToolTip|eventFilter|Enter|Leave|Hover" src/ui

toast 搜索：

    rg -n "show_toast|toast|Toast|toast_label|toast_widget|QTimer|singleShot|hide\\(|close\\(|临时|提示|成功|失败" src/ui

确认本轮未创建公共 tooltip/toast 文件：

    Test-Path src\ui\common\tooltip.py
    Test-Path src\ui\common\toast.py

确认 UI 包骨架仍可 import：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import src.ui.common, src.ui.views, src.ui.dialogs, src.ui.popups, src.ui.utils; print('ui package skeleton import ok')"

确认 8-2b icon loader 仍可 import：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.utils.icon_loader import load_colored_svg_pixmap; print('icon loader import ok', load_colored_svg_pixmap)"

范围检查：

    git diff --name-only -- src
    git diff --name-only -- assets
    git diff --name-only -- main.py
    git diff --name-only -- requirements.txt
    git diff --name-only -- schedule.db
    git diff --name-only
    git status --short --branch

预期：

- `src` 无 diff。
- `assets` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 diff。
- 最终只允许：
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第八轮 8-3a（公共 tooltip / toast 边界静态定位）
- 开工前 git 状态
- 实际修改文件
- tooltip 搜索命令和结果摘要
- toast 搜索命令和结果摘要
- tooltip 职责地图
- toast 职责地图
- parent / timer / eventFilter / 显示位置 / 关闭行为分析
- 低风险候选
- 中风险候选
- 高风险暂缓项
- 是否建议进入 8-3b
- 8-3b 建议的唯一单点提取目标
- UI 包骨架 import 验证结果
- icon loader import 回归结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

特别记录：

- 本轮只读审查，不改源码。
- 本轮不创建 `tooltip.py` / `toast.py`。
- 本轮不替换任何调用方。
- 本轮不修改 QSS。
- 本轮不处理 icon loader 后续统一。
- 本轮不清理 8-2b 遗留的 `header.py` unused import，若需要清理必须另开小工单。

完成后不要提交 Git，等待顾问窗口复核。
```
