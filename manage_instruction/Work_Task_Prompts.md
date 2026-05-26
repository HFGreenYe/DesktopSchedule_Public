请执行第七轮 7-2：默认 QSS 启动接入。本轮只把默认 skin preset 接入应用启动流程，不实现换肤 UI，不改业务 UI。

## 1. 本轮目标

基于第七轮阶段合同、7-0 样式债务审查结论、7-1 ThemeManager 边界结果，在应用启动处接入默认 QSS。

本轮目标：

- 在 `main.py` 的 QApplication 启动流程中接入 `ThemeManager`。
- 默认加载 `ThemeManager.DEFAULT_PRESET`，当前应为 `light.qss`。
- 保持默认视觉尽量不变。
- 保持应用启动流程可用。
- 明确 QSS 读取失败时的启动期处理策略。
- 不实现换肤 UI。
- 不连接 `theme_changed` / `skin_changed`。
- 不修改任何业务 UI 文件。

本轮不做：

- 不做动态属性试点。
- 不做公共控件样式迁移。
- 不批量替换 `setStyleSheet(...)`。
- 不改 `StyleManager`。
- 不实现字体/颜色选择闭环。

## 2. 允许/禁止

本轮允许修改：

- `main.py`
- `src/theme/theme_manager.py`（仅当启动接入发现必须做极小兼容修正时）
- `src/theme/light.qss`（仅允许低侵入基础内容或注释整理；如无必要可不改）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- `src/ui/`
- `src/utils/signals.py`
- `src/utils/styles.py`
- `src/theme/dark.qss`
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
- 不改数据库字段。
- 不改业务逻辑。
- 不改路由、刷新、picker、详情弹窗回流行为。
- 不提交 Git。

若开工前已有 diff，需在 `Work_Log.md` 单独记录，不视为本轮新增问题。

## 3. 具体任务

1. 读取当前基线：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
    Get-Content -Path main.py -Encoding UTF8
    Get-Content -Path src\theme\theme_manager.py -Encoding UTF8
    Get-Content -Path src\theme\light.qss -Encoding UTF8

2. 在 `main.py` 中最小接入 ThemeManager：

    - 保留现有 `QApplication` 创建流程。
    - 保留现有 `app.setStyle("Fusion")`。
    - 在 QApplication 创建后、主窗口显示前，调用 ThemeManager 加载默认 preset。
    - 推荐逻辑：
      - `from src.theme import ThemeManager`
      - `theme_manager = ThemeManager()`
      - `theme_manager.apply_theme(app, ThemeManager.DEFAULT_PRESET)`

3. QSS 读取失败策略：

    - 本轮启动接入阶段采用保守策略：QSS 读取失败不得阻断应用启动。
    - 当前 `apply_theme` 读取失败会应用 fallback 空字符串；由于本轮只在 QApplication 初始化早期加载默认 QSS，允许该行为作为启动期兜底。
    - 不新增复杂日志系统。
    - 如果你认为需要调整 `ThemeManager`，只能做极小兼容修正，并在日志说明原因。
    - 不要把失败处理扩展成完整主题管理系统。

4. `light.qss` 处理：

    - 优先保持现有低侵入内容，不制造视觉突变。
    - 如需修改，只允许加入基础注释或极低风险基础规则。
    - 不添加会大面积改变字体、颜色、间距、圆角的规则。
    - 不修改 `dark.qss`。

5. 不修改任何 `src/ui/` 文件。

6. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

读取接入位置：

    rg -n "ThemeManager|apply_theme|DEFAULT_PRESET|setStyle\\(" main.py src/theme/theme_manager.py

ThemeManager import 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.theme import ThemeManager; print('theme import ok', ThemeManager.DEFAULT_PRESET, ThemeManager().resolve_preset(None))"

main import 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; import main; print('main import ok')"

QApplication 启动接入 smoke：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.theme import ThemeManager; app=QApplication([]); app.setStyle('Fusion'); before=app.styleSheet(); tm=ThemeManager(); tm.apply_theme(app, ThemeManager.DEFAULT_PRESET); after=app.styleSheet(); print('default preset', ThemeManager.DEFAULT_PRESET); print('before len', len(before)); print('after len', len(after)); print('stylesheet type ok', isinstance(after, str))"

QSS 文件验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.theme import ThemeManager; tm=ThemeManager(); qss=tm.read_qss_safe(ThemeManager.DEFAULT_PRESET); print('qss len', len(qss)); assert isinstance(qss, str)"

语法检查：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile main.py src/theme/theme_manager.py src/theme/__init__.py

禁止范围检查：

    git diff --name-only -- src/ui
    git diff --name-only -- src/utils/signals.py
    git diff --name-only -- src/utils/styles.py
    git diff --name-only -- src/theme/dark.qss
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

- `src/ui` 无 diff。
- `signals.py` 无 diff。
- `styles.py` 无 diff。
- `dark.qss` 无 diff。
- `src/data` / `src/repositories` / `src/services` / `src/controllers` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- 最终只允许：
  - `main.py`
  - 必要时 `src/theme/theme_manager.py`
  - 必要时 `src/theme/light.qss`
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第七轮 7-2（默认 QSS 启动接入）
- 开工前 git 状态
- 实际修改文件
- 默认 skin preset 名称
- `main.py` 接入位置
- 是否修改 `ThemeManager`，如修改需说明原因
- 是否修改 `light.qss`，如修改需说明内容和视觉风险
- QSS 读取失败时的启动期处理策略
- import 验证结果
- QApplication smoke 结果
- QSS 文件验证结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
