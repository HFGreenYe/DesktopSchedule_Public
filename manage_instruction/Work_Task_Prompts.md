请执行第七轮 7-3b：Skin Preset 命名语义收口。本轮只修正主题 preset 命名方向，避免误导为 light/dark mode matrix；不接真实业务 UI，不做控件试点。

## 1. 本轮目标

基于第七轮阶段合同、7-0 到 7-3 的结果，收口主题系统的命名语义。

项目方向必须明确：

- 第七轮采用 Skin Preset 路线。
- 不采用“每个皮肤再拆 light/dark 双模式”的矩阵设计。
- `DEFAULT_PRESET` 表示默认皮肤，不表示亮色模式。
- 后续 preset 命名应偏向皮肤名，例如 `default.qss`、`glass.qss`、`minimal.qss`、`warm.qss`。
- 当前 `light.qss` / `dark.qss` 属于历史命名遗留，容易误导，应在本轮收口。

本轮目标：

- 将默认 preset 语义从 `light.qss` 收口为默认皮肤。
- 优先新增或改用 `default.qss` 作为默认 preset。
- 保留 `light.qss` / `dark.qss` 的兼容读取能力，或明确它们只是 legacy/test preset。
- 不把 `dark.qss` 设计成“每个皮肤都必须有 dark 版本”的制度。
- 不删除 `light.qss` / `dark.qss`，避免破坏兼容 smoke 和历史引用。
- 不修改真实业务 UI。
- 不做 7-4 控件试点。
- 不实现换肤 UI。

## 2. 允许/禁止

本轮允许修改：

- `src/theme/theme_manager.py`
- `src/theme/__init__.py`（仅当导出说明确实需要极小调整时）
- `src/theme/default.qss`（如采用新增默认皮肤文件）
- `src/theme/light.qss`（仅用于兼容注释或内容迁移；不做大视觉改造）
- `src/theme/dark.qss`（仅用于兼容注释或测试 preset 说明；不做完整深色主题）
- `main.py`（仅当 `DEFAULT_PRESET` 改名后需要保持默认启动接入可用；不改启动结构，不硬编码具体 preset 文件名）
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护本轮复核锚点时）

本轮禁止修改：

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
- 不修改真实 UI 布局、文案、交互。
- 不批量替换 `setStyleSheet(...)`。
- 不提交 Git。

若开工前已有 diff，需在 `Work_Log.md` 单独记录，不视为本轮新增问题。

## 3. 具体任务

1. 读取当前基线：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
    Get-Content -Path src\theme\theme_manager.py -Encoding UTF8
    Get-Content -Path src\theme\light.qss -Encoding UTF8
    Get-Content -Path src\theme\dark.qss -Encoding UTF8
    Get-Content -Path main.py -Encoding UTF8

2. 确认命名收口方案。

    推荐方案：

    - 新增 `src/theme/default.qss`。
    - 将当前 `light.qss` 中 7-3 动态属性规则复制或迁移到 `default.qss`。
    - `ThemeManager.DEFAULT_PRESET` 改为 `"default.qss"`。
    - `ThemeManager.SUPPORTED_PRESETS` 至少包含：
      - `"default.qss"`
      - `"light.qss"`（legacy compatibility）
      - `"dark.qss"`（legacy/test preset）
    - `resolve_preset(None)` 和非法值回落到 `"default.qss"`。
    - `main.py` 继续使用 `ThemeManager.DEFAULT_PRESET`，不硬编码具体文件名。

3. 对 `light.qss` / `dark.qss` 做语义说明。

    可选做法：

    - 在 `light.qss` 文件注释中标明：legacy compatibility preset，不代表未来每个 skin 都要有 light 版本。
    - 在 `dark.qss` 文件注释中标明：legacy/test dark preset，不代表完整 dark mode 体系。
    - 不要求删除这两个文件，避免破坏已有 smoke 和兼容路径。

4. 保持动态属性规范不变。

    - `role`
    - `state`
    - `variant`

    不改变 7-3 已验证的选择器语义。

5. 不修改真实业务 UI。

6. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

文件与 preset 定位：

    Get-ChildItem src\theme
    rg -n "DEFAULT_PRESET|SUPPORTED_PRESETS|default\\.qss|light\\.qss|dark\\.qss|Skin|skin|legacy|mode|dark mode|light mode" src/theme/theme_manager.py src/theme/*.qss main.py

ThemeManager import 与默认 preset 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.theme import ThemeManager; tm=ThemeManager(); print('default', ThemeManager.DEFAULT_PRESET); print('presets', tm.get_available_presets()); print('resolve none', tm.resolve_preset(None)); print('resolve bad', tm.resolve_preset('bad.qss')); assert ThemeManager.DEFAULT_PRESET == 'default.qss'; assert tm.resolve_preset(None) == 'default.qss'; assert tm.resolve_preset('bad.qss') == 'default.qss'; assert 'default.qss' in tm.get_available_presets()"

默认 QSS 读取验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.theme import ThemeManager; tm=ThemeManager(); qss=tm.read_qss_safe(ThemeManager.DEFAULT_PRESET); print('default qss len', len(qss)); assert isinstance(qss, str); assert len(qss) > 0"

兼容 preset 读取验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.theme import ThemeManager; tm=ThemeManager(); print('light len', len(tm.read_qss_safe('light.qss'))); print('dark len', len(tm.read_qss_safe('dark.qss'))); assert isinstance(tm.read_qss_safe('light.qss'), str); assert isinstance(tm.read_qss_safe('dark.qss'), str)"

动态属性刷新回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication, QPushButton, QWidget; from src.theme import ThemeManager; app=QApplication([]); tm=ThemeManager(); tm.apply_theme(app, ThemeManager.DEFAULT_PRESET); btn=QPushButton('test'); btn.setProperty('role','primaryButton'); tm.refresh_widget_style(btn); btn.setProperty('state','warning'); tm.refresh_widget_style(btn); panel=QWidget(); panel.setProperty('role','panel'); panel.setProperty('variant','compact'); tm.refresh_widget_style(panel); print('default skin dynamic refresh ok', btn.property('role'), btn.property('state'), panel.property('role'), panel.property('variant'))"

默认启动接入回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; import main; print('main import ok')"

语法检查：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile main.py src/theme/theme_manager.py src/theme/__init__.py

禁止范围检查：

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

- `src/ui` 无 diff。
- `signals.py` 无 diff。
- `styles.py` 无 diff。
- `src/data` / `src/repositories` / `src/services` / `src/controllers` 无 diff。
- `requirements.txt` 无 diff。
- `schedule.db` 无 tracked diff。
- 最终只允许：
  - `src/theme/theme_manager.py`
  - `src/theme/default.qss`
  - 必要时 `src/theme/light.qss`
  - 必要时 `src/theme/dark.qss`
  - 必要时 `main.py`
  - `manage_instruction/Work_Log.md`
  - 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. 日志要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第七轮 7-3b（Skin Preset 命名语义收口）
- 开工前 git 状态
- 实际修改文件
- 最终默认 preset 名称
- `SUPPORTED_PRESETS` 清单
- `light.qss` / `dark.qss` 的兼容定位说明
- 是否新增 `default.qss`
- 是否修改 `main.py`，如修改需说明原因
- `resolve_preset(None)` 与非法值回落结果
- 默认 QSS 读取验证结果
- 兼容 preset 读取验证结果
- 动态属性刷新回归结果
- 默认启动接入回归结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

特别记录：

- 第七轮采用 Skin Preset 路线。
- 本轮不建立 light/dark mode matrix。
- `dark.qss` 不代表每个皮肤都需要暗色版本。
- 后续 7-4 控件试点应基于默认 skin preset，而不是基于 light/dark 模式切换。

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
