请执行第七轮 7-1：ThemeManager 与 Skin Preset 边界确认。本轮只完善 ThemeManager 最小边界，不接入 main.py，不改 UI。

## 1. 本轮目标

基于 `manage_instruction/Work_Instruction.md` 第七轮阶段合同，以及 `Work_Log.md` 中 7-0 的审查结论，补齐 ThemeManager 的最小可用边界。

本轮目标：

- 仅在 `src/theme/theme_manager.py` 内完善主题能力边界。
- 明确 skin preset 白名单与默认主题名。
- 增加读取 QSS 的安全兜底（文件缺失/读取失败不抛到 UI 层）。
- 保持 `apply_qss/apply_theme/refresh_widget_style` 语义兼容。
- 不接入 `main.py`。
- 不修改任何 UI 文件。

本轮不做：

- 不修改 `light.qss` / `dark.qss` 内容。
- 不接入应用启动。
- 不做动态属性试点。
- 不做换肤 UI。

## 2. 允许/禁止

本轮允许修改：

- `src/theme/theme_manager.py`
- `src/theme/__init__.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

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

- 不接入 QApplication 启动流程。
- 不新增/修改任何 signal。
- 不改业务逻辑。
- 不改 db_manager API。
- 不提交 Git。

若开工前已有管理文档 diff，需在 `Work_Log.md` 单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取合同和日志基线：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8

    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8

2. 读取 ThemeManager 现状：

    Get-Content -Path src\theme\theme_manager.py -Encoding UTF8

    Get-Content -Path src\theme\__init__.py -Encoding UTF8

3. 在 `src/theme/theme_manager.py` 做最小增强，建议保留/新增以下边界（方法名可微调，但语义必须覆盖）：

- 默认主题常量：`DEFAULT_PRESET = "light.qss"`
- 白名单方法：`get_available_presets() -> tuple[str, ...]`，至少包含 `("light.qss", "dark.qss")`
- 校验方法：`is_supported_preset(file_name: str) -> bool`
- 解析方法：`resolve_preset(file_name: str | None) -> str`，非法输入回落默认 preset
- 安全读取方法：`read_qss_safe(file_name: str | None, fallback: str = "") -> str`
  - 读取失败返回 `fallback`（默认空字符串）
  - 不抛异常到调用方
  - 只捕获文件读取相关异常，例如 `OSError`、`UnicodeDecodeError`；不要用宽泛的 `except Exception` 吞掉代码错误
- `apply_theme(...)` 内部使用 `resolve_preset + read_qss_safe`
  - 保持调用后可 `app.setStyleSheet(...)`
  - 本轮 smoke 可接受读取失败时应用空样式或 fallback，不中断流程
  - 后续 7-2 真实启动接入前，需要再明确失败时是“应用空样式”还是“保留当前样式”

职责边界必须明确：

- `resolve_preset(...)` 只负责 preset 合法性判断与非法值回落默认 preset。
- `read_qss_safe(...)` 只负责读取文件，并在真实文件读取失败时返回 fallback。
- `apply_theme(...)` 负责组合 `resolve_preset(...)` 与 `read_qss_safe(...)` 后调用 `apply_qss(...)`。
- 不要让 `read_qss_safe(...)` 用宽泛 `except Exception` 吞掉代码错误。
- 不要在 `read_qss_safe(...)` 中混入 UI、信号、应用启动或业务逻辑。

要求：

- 不依赖 UI 文件。
- 不依赖 db_manager / Repository / Service。
- 不写数据库。
- 保持 `refresh_widget_style(widget)` 可用。

4. 更新 `src/theme/__init__.py`：

- 轻量导出 `ThemeManager`。
- 不触发副作用（不创建 QApplication，不读取文件，不连接信号）。

5. 不修改 `light.qss` / `dark.qss`。

6. 不修改 `main.py`。

7. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

读取与定位：

    Get-Content -Path src\theme\theme_manager.py -Encoding UTF8

    rg -n "DEFAULT|preset|available|resolve|read_qss|read_qss_safe|apply_theme|apply_qss|refresh_widget_style" src/theme/theme_manager.py src/theme/__init__.py

import 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.theme.theme_manager import ThemeManager; from src.theme import ThemeManager as ThemeManager2; print('theme manager import ok', ThemeManager is ThemeManager2)"

行为验证（白名单/回落/安全读取）：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.theme.theme_manager import ThemeManager; tm=ThemeManager(); presets=tm.get_available_presets() if hasattr(tm,'get_available_presets') else (); print('presets', presets); assert 'light.qss' in presets and 'dark.qss' in presets; rp=tm.resolve_preset('light.qss') if hasattr(tm,'resolve_preset') else 'light.qss'; print('resolve light', rp); assert rp=='light.qss'; rp2=tm.resolve_preset('bad.qss') if hasattr(tm,'resolve_preset') else None; print('resolve bad', rp2); assert rp2 in ('light.qss','dark.qss'); txt=tm.read_qss_safe('light.qss') if hasattr(tm,'read_qss_safe') else tm.read_qss('light.qss'); print('light len', len(txt)); txt2=tm.read_qss_safe('missing.qss','') if hasattr(tm,'read_qss_safe') else ''; print('missing len', len(txt2)); assert isinstance(txt2,str)"

QApplication apply 烟测（仅临时进程，不改业务）：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.theme.theme_manager import ThemeManager; app=QApplication([]); tm=ThemeManager(); tm.apply_theme(app, 'light.qss'); print('applied light', isinstance(app.styleSheet(), str)); tm.apply_theme(app, 'missing.qss'); print('applied missing fallback', isinstance(app.styleSheet(), str));"

静态依赖检查（ThemeManager 不依赖 UI/db/Repository/Service）：

    rg -n "src\.ui|MainWindow|WeekWindow|MonthWindow|Todo|db_manager|src\.repositories|Repository|src\.services|ScheduleRepository|CategoryRepository" src/theme/theme_manager.py src/theme/__init__.py

预期：无输出（若 `rg` 退出码 1 但无输出，视为通过）。

语法检查：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/theme/theme_manager.py src/theme/__init__.py

范围检查：

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

    git diff --name-only

    git status --short --branch

预期：

- `light.qss` 无 diff。
- `dark.qss` 无 diff。
- `main.py` 无 diff。
- `src/ui` 无 diff。
- `signals.py` 无 diff。
- `styles.py` 无 diff。
- `src/data` / `src/repositories` / `src/services` / `src/controllers` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- 最终只允许：
  - `src/theme/theme_manager.py`
  - `src/theme/__init__.py`
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第七轮 7-1（ThemeManager 与 Skin Preset 边界确认）
- 开工前 git 状态
- 实际修改文件
- ThemeManager 新增/调整的方法清单
- skin preset 白名单与默认 preset
- 非法 preset 回落策略
- QSS 读取失败兜底策略
- `apply_theme` 兼容行为说明
- `refresh_widget_style` 是否保持可用
- `__init__.py` 导出说明
- import 验证结果
- 行为验证结果
- QApplication apply 烟测结果
- 静态依赖检查结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
