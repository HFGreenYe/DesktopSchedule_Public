请执行第七轮 7-4：低风险真实控件动态属性样式试点。本轮只选择一个真实业务界面中的低风险控件做 QSS 动态属性试点，不做全局控件样式，不做 light/dark 模式切换。

## 1. 本轮目标

基于第七轮阶段合同、7-0 到 7-3b 的结果，选择一个低风险真实控件验证：

- `default.qss` 中的 skin preset 样式可以作用到真实 UI 控件。
- 真实 UI 控件可以通过 `role/state/variant` 动态属性接入 QSS。
- 不改变业务逻辑、路由、刷新链路、数据库行为。
- 不批量迁移旧 `setStyleSheet(...)`。
- 不建立 light/dark mode matrix。
- 不围绕 `light.qss` / `dark.qss` 做模式切换。

本轮试点控件限定为：

- `src/ui/header.py` 中的 `btn_sync` 云同步窗口控制按钮。

选择理由：

- 该按钮是窗口控制区的低风险控件。
- 不涉及数据库写入。
- 不涉及路由切换。
- 不涉及添加、编辑、删除、提醒、详情弹窗回流。
- 相比大块页面样式，单点可回滚。

本轮不处理：

- `btn_more`
- `btn_close`
- tooltip 全局样式
- `todo_board.py`
- `week_window.py`
- `month_window.py`
- `add_view.py`
- `add_view_week.py`
- `StyleManager` 大范围重构

## 2. 允许/禁止

本轮允许修改：

- `src/theme/default.qss`
- `src/ui/header.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- `src/theme/light.qss`
- `src/theme/dark.qss`
- `src/theme/theme_manager.py`
- `main.py`
- `src/utils/signals.py`
- `src/utils/styles.py`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- 除 `src/ui/header.py` 外的任何 `src/ui/` 文件
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不新增 signal。
- 不改变 `global_signals.skin_changed` 无参签名。
- 不改变 `global_signals.theme_changed(str)` 签名。
- 不改数据库字段。
- 不改业务逻辑。
- 不改路由、刷新、picker、详情弹窗回流行为。
- 不修改 `btn_sync` 点击连接关系。
- 不修改 `btn_more` / `btn_close` 行为。
- 不修改 header 布局结构。
- 不提交 Git。

若开工前已有 diff，需在 `Work_Log.md` 单独记录，不视为本轮新增问题。

## 3. 具体任务

1. 读取当前基线：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
    Get-Content -Path src\theme\default.qss -Encoding UTF8
    Get-Content -Path src\ui\header.py -Encoding UTF8
    Get-Content -Path src\utils\styles.py -Encoding UTF8

2. 在 `default.qss` 中新增仅针对窗口控制按钮试点的动态属性选择器。

    建议选择器：

    - `QToolButton[role="windowControl"][variant="toolbar"]`
    - `QToolButton[role="windowControl"][variant="toolbar"]:hover`
    - `QToolButton[role="windowControl"][variant="toolbar"]:pressed`

    要求：

    - 只作用于设置了 `role="windowControl"` 且 `variant="toolbar"` 的 `QToolButton`。
    - 不新增全局 `QToolButton` 默认规则。
    - 不影响没有动态属性的旧控件。
    - 样式尽量对齐 `StyleManager.get_window_control_style(is_close=False)` 的现有视觉：
      - transparent background
      - no border
      - border-radius 6px
      - hover 使用 `rgba(255, 255, 255, 0.2)` 或接近值
      - pressed 使用 `rgba(255, 255, 255, 0.3)` 或接近值

3. 在 `src/ui/header.py` 中只对 `btn_sync` 做最小试点。

    允许做法：

    - 创建 `self.btn_sync` 后设置：
      - `role = "windowControl"`
      - `variant = "toolbar"`
      - `state = "normal"`（可选）
    - 让 `btn_sync` 使用 `default.qss` 中的动态属性样式。
    - 如果 `btn_sync` 原本的局部 `setStyleSheet(...)` 会覆盖应用级 QSS，允许仅对 `btn_sync` 清除或避免局部样式。
    - 不改变 `btn_sync` 的 icon、size、tooltip、layout、信号连接。

    禁止做法：

    - 不修改 `_create_control_btn(...)` 影响所有窗口控制按钮，除非仅为支持 `btn_sync` 做可选参数且默认行为完全不变。
    - 不修改 `btn_more`。
    - 不修改 `btn_close`。
    - 不改 `StyleManager.get_window_control_style(...)`。
    - 不引入 `ThemeManager` 到 `header.py`，除非确有必要；默认不需要。

4. 不修改 `light.qss` / `dark.qss`。

5. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

定位试点选择器：

    rg -n "windowControl|variant=\"toolbar\"|role=\"windowControl\"|QToolButton\\[role" src/theme/default.qss src/ui/header.py

确认未修改 light/dark preset：

    git diff --name-only -- src/theme/light.qss
    git diff --name-only -- src/theme/dark.qss

Header import 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.header import HeaderBar; print('header import ok', HeaderBar)"

Header offscreen 实例化与属性验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.theme import ThemeManager; from src.ui.header import HeaderBar; app=QApplication([]); ThemeManager().apply_theme(app, ThemeManager.DEFAULT_PRESET); h=HeaderBar(); print('has sync', hasattr(h, 'btn_sync')); print('sync role', h.btn_sync.property('role')); print('sync variant', h.btn_sync.property('variant')); print('sync state', h.btn_sync.property('state')); assert h.btn_sync.property('role') == 'windowControl'; assert h.btn_sync.property('variant') == 'toolbar'"

默认启动接入回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; import main; print('main import ok')"

语法检查：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/header.py main.py src/theme/theme_manager.py src/theme/__init__.py

禁止范围检查：

    git diff --name-only -- src/theme/light.qss
    git diff --name-only -- src/theme/dark.qss
    git diff --name-only -- src/theme/theme_manager.py
    git diff --name-only -- main.py
    git diff --name-only -- src/utils/signals.py
    git diff --name-only -- src/utils/styles.py
    git diff --name-only -- src/data
    git diff --name-only -- src/repositories
    git diff --name-only -- src/services
    git diff --name-only -- src/controllers
    git diff --name-only -- requirements.txt
    git diff --name-only -- schedule.db

确认除 header 外无 UI diff：

    git diff --name-only -- src/ui

预期 `src/ui` diff 中只允许：

    src/ui/header.py

总范围检查：

    git diff --name-only
    git status --short --branch

预期最终只允许：

- `src/theme/default.qss`
- `src/ui/header.py`
- `manage_instruction/Work_Log.md`
- 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第七轮 7-4（低风险真实控件动态属性样式试点）
- 开工前 git 状态
- 实际修改文件
- 试点控件：
  - `src/ui/header.py`
  - `btn_sync`
- 为什么选择该控件
- `default.qss` 新增选择器说明
- `btn_sync` 设置的动态属性：
  - `role`
  - `variant`
  - `state`（如有）
- 是否清除或避免了 `btn_sync` 的局部 stylesheet，如有需说明原因
- 确认未修改 `btn_more` / `btn_close` 行为
- Header import 验证结果
- Header offscreen 实例化与属性验证结果
- 默认启动接入回归结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

特别记录：

- 本轮基于 `default.qss / skin preset`。
- 本轮不围绕 `light.qss` / `dark.qss` 做模式切换。
- 本轮只做单个真实控件试点，不做全局控件样式。
- 后续若要扩大范围，必须另开小工单。

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
