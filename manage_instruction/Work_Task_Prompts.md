请执行第七轮 7-5：Theme 信号兼容与手动 Skin Preset 切换 smoke。本轮只做兼容性验证和日志记录，不扩大 UI 试点范围，不连接真实换肤 UI。

## 1. 本轮目标

基于第七轮阶段合同、7-0 到 7-4 的结果，验证 ThemeManager 与既有 global_signals 的兼容性，并做手动 skin preset 切换 smoke。

本轮目标：

- 验证 `global_signals.skin_changed` 仍为无参信号且可 emit。
- 验证 `global_signals.theme_changed(str)` 仍可 emit。
- 验证 `ThemeManager` 可手动 apply `default.qss`。
- 验证兼容/test preset `light.qss` / `dark.qss` 可手动 apply。
- 确认当前路线是 `default.qss / skin preset`。
- 确认 `light.qss` / `dark.qss` 仍只是兼容或测试 preset，不代表 light/dark mode matrix。
- 不修改真实业务 UI。
- 不扩大 7-4 的 `btn_sync` 试点范围。
- 不实现换肤 UI。
- 不连接真实主题切换链路。

本轮预期不改源码。

## 2. 允许/禁止

本轮允许修改：

- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮原则上禁止修改源码。

本轮禁止修改：

- `src/theme/theme_manager.py`
- `src/theme/default.qss`
- `src/theme/light.qss`
- `src/theme/dark.qss`
- `main.py`
- `src/ui/`
- `src/utils/signals.py`
- `src/utils/styles.py`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不新增 signal。
- 不改变 `global_signals.skin_changed` 无参签名。
- 不改变 `global_signals.theme_changed(str)` 签名。
- 不连接真实 UI 换肤入口。
- 不修改 `btn_sync` 试点。
- 不修改 `btn_more` / `btn_close`。
- 不新增皮肤文件。
- 不删除 `light.qss` / `dark.qss`。
- 不建立 light/dark mode matrix。
- 不提交 Git。

若开工前已有 diff，需在 `Work_Log.md` 单独记录，不视为本轮新增问题。

## 3. 具体任务

1. 读取当前基线：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
    Get-Content -Path src\utils\signals.py -Encoding UTF8
    Get-Content -Path src\theme\theme_manager.py -Encoding UTF8
    Get-Content -Path src\theme\default.qss -Encoding UTF8
    Get-Content -Path src\theme\light.qss -Encoding UTF8
    Get-Content -Path src\theme\dark.qss -Encoding UTF8

2. 验证 signal 兼容性：

    - `global_signals.skin_changed` 必须可无参 emit。
    - `global_signals.theme_changed` 必须可带一个字符串参数 emit。
    - 不修改 `signals.py`。
    - 不连接真实 UI。

3. 验证手动 skin preset apply：

    - 在 offscreen `QApplication` 中手动 apply `default.qss`。
    - 再手动 apply `light.qss`。
    - 再手动 apply `dark.qss`。
    - 验证每次 apply 后 `app.styleSheet()` 是字符串。
    - 验证 `ThemeManager.resolve_preset(None)` 和非法值仍回落到 `default.qss`。

4. 验证 7-4 单点试点仍可用：

    - offscreen 实例化 `HeaderBar`。
    - 确认 `btn_sync` 动态属性仍为：
      - `role = "windowControl"`
      - `variant = "toolbar"`
      - `state = "normal"`
    - 不修改 `header.py`。

5. 记录结论：

    - 第七轮主题路线是 skin preset。
    - `default.qss` 是 canonical 默认皮肤。
    - `light.qss` / `dark.qss` 是兼容/test preset。
    - 本轮不实现换肤 UI。
    - 本轮不扩大真实控件试点。

6. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

信号定义定位：

    rg -n "skin_changed|theme_changed|global_signals" src/utils/signals.py

ThemeManager preset 定位：

    rg -n "DEFAULT_PRESET|SUPPORTED_PRESETS|default\\.qss|light\\.qss|dark\\.qss" src/theme/theme_manager.py src/theme/default.qss src/theme/light.qss src/theme/dark.qss

signals import 与 emit smoke：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.utils.signals import global_signals; print('signals import ok'); calls=[]; global_signals.skin_changed.connect(lambda: calls.append('skin')); global_signals.theme_changed.connect(lambda name: calls.append(('theme', name))); global_signals.skin_changed.emit(); global_signals.theme_changed.emit('default.qss'); print('calls', calls); assert 'skin' in calls; assert ('theme', 'default.qss') in calls"

ThemeManager 手动切换 smoke：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.theme import ThemeManager; app=QApplication([]); tm=ThemeManager(); print('default', ThemeManager.DEFAULT_PRESET); print('presets', tm.get_available_presets()); assert ThemeManager.DEFAULT_PRESET == 'default.qss'; assert tm.resolve_preset(None) == 'default.qss'; assert tm.resolve_preset('bad.qss') == 'default.qss'; results=[]; [tm.apply_theme(app, preset) or results.append((preset, isinstance(app.styleSheet(), str), len(app.styleSheet()))) for preset in ('default.qss','light.qss','dark.qss')]; print('apply results', results); assert all(ok for _, ok, _ in results)"

7-4 试点回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication, QWidget; from src.theme import ThemeManager; from src.ui.header import HeaderBar; app=QApplication([]); ThemeManager().apply_theme(app, ThemeManager.DEFAULT_PRESET); parent=QWidget(); h=HeaderBar(parent); print('sync role', h.btn_sync.property('role')); print('sync variant', h.btn_sync.property('variant')); print('sync state', h.btn_sync.property('state')); assert h.btn_sync.property('role') == 'windowControl'; assert h.btn_sync.property('variant') == 'toolbar'; assert h.btn_sync.property('state') == 'normal'"

默认启动接入回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; import main; print('main import ok')"

语法检查：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile main.py src/theme/theme_manager.py src/theme/__init__.py src/utils/signals.py src/ui/header.py

禁止范围检查：

    git diff --name-only -- src/theme/theme_manager.py
    git diff --name-only -- src/theme/default.qss
    git diff --name-only -- src/theme/light.qss
    git diff --name-only -- src/theme/dark.qss
    git diff --name-only -- main.py
    git diff --name-only -- src/ui
    git diff --name-only -- src/utils/signals.py
    git diff --name-only -- src/utils/styles.py
    git diff --name-only -- src/data
    git diff --name-only -- src/repositories
    git diff --name-only -- src/services
    git diff --name-only -- src/controllers
    git diff --name-only -- requirements.txt
    git diff --name-only -- schedule.db

总范围检查：

    git diff --name-only
    git status --short --branch

预期：

- 所有源码与 QSS 文件无 diff。
- `src/ui` 无 diff。
- `src/theme` 无 diff。
- `signals.py` 无 diff。
- `main.py` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- 最终只允许：
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第七轮 7-5（Theme 信号兼容与手动 Skin Preset 切换 smoke）
- 开工前 git 状态
- 实际修改文件
- `skin_changed` 无参 emit 验证结果
- `theme_changed(str)` emit 验证结果
- `ThemeManager.DEFAULT_PRESET` 当前值
- `SUPPORTED_PRESETS` 当前清单
- `resolve_preset(None)` 与非法值回落结果
- `default.qss` 手动 apply 结果
- `light.qss` 兼容 preset 手动 apply 结果
- `dark.qss` test preset 手动 apply 结果
- 7-4 `btn_sync` 试点回归结果
- 默认启动接入回归结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

特别记录：

- 本轮只做信号兼容和手动 preset 切换 smoke。
- 本轮不连接真实换肤 UI。
- 本轮不扩大 7-4 控件试点范围。
- `default.qss` 是 canonical 默认 skin preset。
- `light.qss` / `dark.qss` 只是兼容/test preset，不代表 light/dark mode matrix。

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
