请执行第七轮 7-6：第七轮整体验收与归档准备。本轮只做总体验收、结论汇总和日志记录，不新增功能，不改源码。

## 1. 本轮目标

基于第七轮阶段合同，以及 7-0 到 7-5 的执行结果，完成第七轮整体验收与归档准备。

本轮目标：

- 汇总第七轮 Theme / QSS 接入结果。
- 复跑 ThemeManager preset 行为。
- 复跑默认启动接入。
- 复跑 signals 兼容性。
- 复跑 7-4 `btn_sync` 单点试点。
- 确认禁止范围无 diff。
- 判断第七轮是否可归档。
- 判断是否可以进入第八轮 UI 拆分规划。

本轮不做：

- 不新增功能。
- 不修改源码。
- 不修改 QSS。
- 不扩大 UI 试点范围。
- 不连接真实换肤 UI。
- 不做第八轮 UI 拆分。
- 不做 light/dark mode matrix。

## 2. 允许/禁止

本轮允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- `src/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

具体禁止：

- 不修改 `src/theme/theme_manager.py`
- 不修改 `src/theme/default.qss`
- 不修改 `src/theme/light.qss`
- 不修改 `src/theme/dark.qss`
- 不修改 `src/ui/`
- 不修改 `src/utils/signals.py`
- 不修改 `src/utils/styles.py`
- 不修改 `src/data/`
- 不修改 `src/repositories/`
- 不修改 `src/services/`
- 不修改 `src/controllers/`

禁止事项：

- 不新增 signal。
- 不改变 `global_signals.skin_changed` 无参签名。
- 不改变 `global_signals.theme_changed(str)` 签名。
- 不连接真实 UI 换肤入口。
- 不修改 `btn_sync` 试点。
- 不新增皮肤文件。
- 不删除 `light.qss` / `dark.qss`。
- 不提交 Git。

若开工前已有 diff，需在 `Work_Log.md` 单独记录，不视为本轮新增问题。

## 3. 具体任务

1. 读取当前基线：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
    Get-Content -Path src\theme\theme_manager.py -Encoding UTF8
    Get-Content -Path src\theme\default.qss -Encoding UTF8
    Get-Content -Path src\utils\signals.py -Encoding UTF8
    Get-Content -Path main.py -Encoding UTF8

2. 汇总 7-0 到 7-5 结果：

    - 7-0：主题与样式债务静态审查。
    - 7-1：ThemeManager 与 Skin Preset 边界确认。
    - 7-2：默认 QSS 启动接入。
    - 7-3：动态属性命名规范与刷新验证。
    - 7-3b：Skin Preset 命名语义收口。
    - 7-4：`btn_sync` 单个真实控件动态属性试点。
    - 7-5：Theme signals 兼容与手动 preset 切换 smoke。

3. 复跑关键验收：

    - ThemeManager preset 行为。
    - 默认启动接入。
    - signals 兼容。
    - 7-4 `btn_sync` 试点。
    - py_compile。
    - diff 范围。

4. 判断第七轮可归档性：

    可归档条件：

    - ThemeManager 可 import。
    - 默认 preset 为 `default.qss`。
    - `default.qss` 可读取和 apply。
    - `light.qss` / `dark.qss` 仍为兼容/test preset。
    - 不存在 light/dark mode matrix 倾向。
    - `main.py` 默认启动接入可 import smoke。
    - `skin_changed` / `theme_changed(str)` 兼容。
    - `btn_sync` 试点属性仍可验证。
    - 禁止范围无 diff。
    - 当前工作区最终只包含管理文档变更。

5. 记录第八轮准备事项：

    第八轮应重点处理 UI 拆分与样式债务，不应在第七轮继续扩大范围。

    需要记录：

    - 第八轮可以基于 `default.qss / skin preset`。
    - 第八轮 UI 拆分时应继续遵守 `role/state/variant` 动态属性规范。
    - 大块 UI 样式迁移仍应拆小，不应一次性迁移 `todo_board.py` / `week_window.py` / `month_window.py` / `add_view.py`。
    - `theme_color/设置字体` 功能闭环仍属于后续功能轮，不属于第八轮默认任务。
    - 真实换肤 UI 仍未接入，需要后续单独规划。

6. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

ThemeManager preset 行为：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.theme import ThemeManager; tm=ThemeManager(); print('default', ThemeManager.DEFAULT_PRESET); print('presets', tm.get_available_presets()); print('resolve none', tm.resolve_preset(None)); print('resolve bad', tm.resolve_preset('bad.qss')); assert ThemeManager.DEFAULT_PRESET == 'default.qss'; assert tm.resolve_preset(None) == 'default.qss'; assert tm.resolve_preset('bad.qss') == 'default.qss'; assert 'default.qss' in tm.get_available_presets()"

ThemeManager apply smoke：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.theme import ThemeManager; app=QApplication([]); tm=ThemeManager(); results=[]; [tm.apply_theme(app, preset) or results.append((preset, isinstance(app.styleSheet(), str), len(app.styleSheet()))) for preset in ('default.qss','light.qss','dark.qss')]; print('apply results', results); assert all(ok for _, ok, _ in results); assert results[0][0] == 'default.qss'"

signals 兼容：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.utils.signals import global_signals; calls=[]; global_signals.skin_changed.connect(lambda: calls.append('skin')); global_signals.theme_changed.connect(lambda name: calls.append(('theme', name))); global_signals.skin_changed.emit(); global_signals.theme_changed.emit('default.qss'); print('signals calls', calls); assert 'skin' in calls; assert ('theme', 'default.qss') in calls"

默认启动接入回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; import main; print('main import ok')"

7-4 `btn_sync` 试点回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication, QWidget; from src.theme import ThemeManager; from src.ui.header import HeaderBar; app=QApplication([]); ThemeManager().apply_theme(app, ThemeManager.DEFAULT_PRESET); parent=QWidget(); h=HeaderBar(parent); print('sync role', h.btn_sync.property('role')); print('sync variant', h.btn_sync.property('variant')); print('sync state', h.btn_sync.property('state')); assert h.btn_sync.property('role') == 'windowControl'; assert h.btn_sync.property('variant') == 'toolbar'; assert h.btn_sync.property('state') == 'normal'"

语法检查：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile main.py src/theme/theme_manager.py src/theme/__init__.py src/utils/signals.py src/ui/header.py

禁止范围检查：

    git diff --name-only -- src
    git diff --name-only -- main.py
    git diff --name-only -- requirements.txt
    git diff --name-only -- schedule.db

细分范围检查：

    git diff --name-only -- src/theme
    git diff --name-only -- src/ui
    git diff --name-only -- src/utils
    git diff --name-only -- src/data
    git diff --name-only -- src/repositories
    git diff --name-only -- src/services
    git diff --name-only -- src/controllers

总范围检查：

    git diff --name-only
    git status --short --branch

预期：

- `src` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- 最终只允许：
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第七轮 7-6（第七轮整体验收与归档准备）
- 开工前 git 状态
- 实际修改文件
- 7-0 到 7-5 完成摘要
- ThemeManager preset 行为验证结果
- `default.qss` canonical 默认 skin 结论
- `light.qss` / `dark.qss` 兼容/test preset 结论
- 默认启动接入验证结果
- signals 兼容验证结果
- 7-4 `btn_sync` 试点回归结果
- py_compile 结果
- diff 范围检查结果
- 第七轮未完成事项
- 第七轮风险或疑点
- 是否建议归档第七轮
- 是否建议进入第八轮 UI 拆分规划

特别记录：

- 第七轮没有实现真实换肤 UI。
- 第七轮没有建立 light/dark mode matrix。
- 第七轮只做了一个真实控件试点：`src/ui/header.py` 的 `btn_sync`。
- 第八轮应继续保持小工单策略，不应一次性拆大 UI 文件。
- `theme_color/设置字体` 功能闭环继续留待后续功能轮。

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
