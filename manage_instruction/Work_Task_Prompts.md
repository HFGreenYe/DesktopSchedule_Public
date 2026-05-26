请执行第七轮 7-3：动态属性命名规范与刷新验证。本轮只建立 QSS 动态属性规范，并用临时控件验证刷新闭环，不修改真实业务 UI。

## 1. 本轮目标

基于第七轮阶段合同、7-0 样式债务审查结论、7-1 ThemeManager 边界、7-2 默认 QSS 启动接入结果，建立最小动态属性命名规范，并验证 `ThemeManager.refresh_widget_style(...)` 可以刷新动态属性样式。

本轮目标：

- 在 QSS 中建立最小动态属性选择器规范。
- 推荐属性名：`role`、`state`、`variant`。
- 用临时 `QWidget` / `QPushButton` 在 offscreen 进程中验证：
  - `setProperty(...)`
  - `ThemeManager.refresh_widget_style(...)`
  - QSS 动态属性选择器可被加载
- 保持 `ThemeManager` import / apply / refresh 能力可用。
- 不修改任何真实业务 UI 文件。
- 不做公共控件试点。
- 不实现换肤 UI。

本轮不做：

- 不修改 `main.py`。
- 不修改 `src/ui/`。
- 不批量替换 `setStyleSheet(...)`。
- 不改 `StyleManager`。
- 不连接 `theme_changed` / `skin_changed`。
- 不做字体/颜色选择闭环。

## 2. 允许/禁止

本轮允许修改：

- `src/theme/light.qss`
- `src/theme/dark.qss`
- `src/theme/theme_manager.py`（仅当刷新验证发现必须做极小兼容修正时）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

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
- 不改数据库字段。
- 不改业务逻辑。
- 不改路由、刷新、picker、详情弹窗回流行为。
- 不改真实 UI 布局、文案、交互。
- 不提交 Git。

若开工前已有 diff，需在 `Work_Log.md` 单独记录，不视为本轮新增问题。

## 3. 具体任务

1. 读取当前基线：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
    Get-Content -Path src\theme\theme_manager.py -Encoding UTF8
    Get-Content -Path src\theme\light.qss -Encoding UTF8
    Get-Content -Path src\theme\dark.qss -Encoding UTF8

2. 在 `light.qss` 和 `dark.qss` 中加入低侵入动态属性选择器示例。

    建议只加入临时验证/未来试点可用的轻量规则，不要影响现有业务 UI 的大面积视觉。

    推荐命名规范：

    - `role`：组件角色，例如 `primaryButton`、`ghostButton`、`panel`、`input`
    - `state`：状态，例如 `normal`、`active`、`warning`、`danger`
    - `variant`：变体，例如 `compact`、`toolbar`

    推荐选择器示例：

    - `QPushButton[role="primaryButton"]`
    - `QPushButton[role="ghostButton"]`
    - `QWidget[role="panel"]`
    - `*[state="warning"]`
    - `*[state="danger"]`
    - `*[variant="compact"]`

    注意：

    - 不要加入会改变全局 `QWidget`、`QPushButton`、`QLabel` 默认样式的大范围规则。
    - 选择器必须尽量依赖动态属性，避免影响未设置属性的旧 UI。
    - `dark.qss` 可以加入对应深色 preset 的同名选择器，但不要实现完整深色主题。

3. 只有在确实必要时，才允许极小修改 `ThemeManager.refresh_widget_style(...)`。

    默认预期：不需要修改 `ThemeManager`。

4. 使用临时控件验证刷新闭环：

    - 创建 offscreen `QApplication`。
    - 加载 `light.qss`。
    - 创建 `QPushButton`。
    - 设置 `role="primaryButton"`。
    - 调用 `refresh_widget_style(button)`。
    - 再切换 `state` 或 `variant`。
    - 再次调用 `refresh_widget_style(button)`。
    - 验证过程不抛异常。

5. 不修改任何 `src/ui/` 文件。

6. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

定位动态属性选择器：

    rg -n "role=|state=|variant=|primaryButton|ghostButton|panel|warning|danger|compact" src/theme/light.qss src/theme/dark.qss

ThemeManager import 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.theme import ThemeManager; print('theme import ok', ThemeManager.DEFAULT_PRESET, ThemeManager().get_available_presets())"

动态属性刷新 smoke：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication, QPushButton, QWidget; from src.theme import ThemeManager; app=QApplication([]); tm=ThemeManager(); tm.apply_theme(app, 'light.qss'); btn=QPushButton('test'); btn.setProperty('role','primaryButton'); tm.refresh_widget_style(btn); btn.setProperty('state','warning'); tm.refresh_widget_style(btn); panel=QWidget(); panel.setProperty('role','panel'); panel.setProperty('variant','compact'); tm.refresh_widget_style(panel); print('dynamic property refresh ok', btn.property('role'), btn.property('state'), panel.property('role'), panel.property('variant'))"

dark preset 动态属性 smoke：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication, QPushButton; from src.theme import ThemeManager; app=QApplication([]); tm=ThemeManager(); tm.apply_theme(app, 'dark.qss'); btn=QPushButton('test'); btn.setProperty('role','ghostButton'); btn.setProperty('state','danger'); tm.refresh_widget_style(btn); print('dark dynamic refresh ok', btn.property('role'), btn.property('state'), isinstance(app.styleSheet(), str))"

默认启动接入回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; import main; print('main import ok')"

语法检查：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile main.py src/theme/theme_manager.py src/theme/__init__.py

禁止范围检查：

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

- `main.py` 无 diff。
- `src/ui` 无 diff。
- `signals.py` 无 diff。
- `styles.py` 无 diff。
- `src/data` / `src/repositories` / `src/services` / `src/controllers` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- 最终只允许：
  - `src/theme/light.qss`
  - `src/theme/dark.qss`
  - 必要时 `src/theme/theme_manager.py`
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第七轮 7-3（动态属性命名规范与刷新验证）
- 开工前 git 状态
- 实际修改文件
- 动态属性命名规范：
  - `role`
  - `state`
  - `variant`
- `light.qss` 新增选择器说明
- `dark.qss` 新增选择器说明
- 是否修改 `ThemeManager`，如修改需说明原因
- 临时控件动态属性刷新验证结果
- dark preset 动态属性 smoke 结果
- 默认启动接入回归结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
