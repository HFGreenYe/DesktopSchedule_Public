# Work Task Prompts

## 第八轮 8-2b：公共 icon loader 最小提取与 Header 单点替换

```markdown
请执行第八轮 8-2b：公共 icon loader 最小提取与 Header 单点替换。本轮只新增一个 icon helper，并只替换 `src/ui/header.py::_load_colored_svg` 的内部实现，不改其他调用方。

## 1. 本轮目标

基于 8-2a 的只读基线结论，执行最小 icon loader 提取。

本轮目标：

- 新增 `src/ui/utils/icon_loader.py`。
- 在其中实现一个低风险 `QPixmap` helper，用于渲染并染色 SVG。
- 只让 `src/ui/header.py::_load_colored_svg(...)` 委托这个 helper。
- 保持 `header.py` 现有 `_load_colored_svg(...)` 方法名、参数、返回语义不变。
- 不修改 `header.py` 中 `_load_colored_svg(...)` 的所有调用点。
- 不修改 `components.py::get_colored_icon`。
- 不修改 `todo_board.py`、`schedule_detail_pop.py`、`week_window.py`、`month_window.py`、`time_picker*.py`。
- 不修改 assets。
- 不改业务逻辑。

本轮不做：

- 不统一所有 icon loader。
- 不替换多个调用方。
- 不处理 `QIcon` 返回路径。
- 不处理 PNG/JPG 位图分支。
- 不改 UI 布局、信号、tooltip、天气逻辑、窗口控制行为。
- 不改 QSS。

## 2. 允许/禁止

本轮允许修改：

- `src/ui/utils/icon_loader.py`
- `src/ui/header.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

本轮禁止修改：

- `src/ui/components.py`
- `src/ui/todo_board.py`
- `src/ui/schedule_detail_pop.py`
- `src/ui/time_picker.py`
- `src/ui/time_picker_week.py`
- `src/ui/week_window.py`
- `src/ui/month_window.py`
- 除 `src/ui/header.py` 和 `src/ui/utils/icon_loader.py` 外的任何 `src/ui/` 文件
- `assets/`
- `src/theme/`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `src/utils/signals.py`
- `src/utils/styles.py`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不新增功能。
- 不移动 UI 类。
- 不改 `HeaderBar` 构造流程。
- 不改变 `btn_sync` 7-4 动态属性试点。
- 不创建与现有 `src/ui/*.py` 同名的包目录。
- 不提交 Git。

若开工前已有 diff，需在 `Work_Log.md` 单独记录，不视为本轮新增问题。

## 3. 具体任务

1. 读取当前基线：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
    Get-Content -Path src\ui\header.py -Encoding UTF8

2. 新增 `src/ui/utils/icon_loader.py`。

    建议 helper 签名：

    `load_colored_svg_pixmap(icon_path, color_hex, width, height, device_pixel_ratio=1.0)`

    语义要求：

    - 输入：
      - `icon_path`：完整 SVG 路径字符串。
      - `color_hex`：颜色字符串。
      - `width` / `height`：逻辑尺寸。
      - `device_pixel_ratio`：DPR，默认 `1.0`。
    - 输出：
      - `QPixmap`
    - 行为：
      - 使用 `QSvgRenderer` 读取 SVG。
      - renderer 无效时返回空 `QPixmap()`。
      - 按 DPR 创建实际像素尺寸。
      - 保留高 DPI 行为：`pixmap.setDevicePixelRatio(device_pixel_ratio)`。
      - 使用 `QPainter.CompositionMode_SourceIn` 做染色。
      - 不依赖 QWidget。
      - 不触发 QApplication。
      - 不读取或修改全局状态。
      - 不写日志，不连接信号。

3. 修改 `src/ui/header.py`。

    只允许做以下最小改动：

    - 从 `src.ui.utils.icon_loader` 导入 helper。
    - 保留 `_load_colored_svg(self, icon_path, color_hex, width, height)` 方法。
    - 将 `_load_colored_svg(...)` 方法体改为调用 helper：
      - DPR 仍从 `self.devicePixelRatio()` 获取。
      - 返回 helper 的 `QPixmap`。
    - 不修改 `_load_colored_svg(...)` 的调用方。
    - 不修改 `update_weather_ui(...)`。
    - 不修改 `btn_sync` 动态属性。
    - 不修改 `_create_control_btn(...)`。
    - 不修改 `_load_colored_svg(...)` 之外的 header 行为。

4. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

定位 helper 与 header 替换：

    rg -n "load_colored_svg_pixmap|_load_colored_svg|QSvgRenderer|CompositionMode_SourceIn|devicePixelRatio" src/ui/utils/icon_loader.py src/ui/header.py

helper import 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.utils.icon_loader import load_colored_svg_pixmap; print('icon loader import ok', load_colored_svg_pixmap)"

helper offscreen 渲染验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.utils.icon_loader import load_colored_svg_pixmap; app=QApplication([]); pm=load_colored_svg_pixmap('assets/icons/search.svg', '#FFFFFF', 24, 24, 1.0); print('pixmap null', pm.isNull(), 'size', pm.width(), pm.height(), 'dpr', pm.devicePixelRatio()); assert not pm.isNull(); bad=load_colored_svg_pixmap('assets/icons/__missing__.svg', '#FFFFFF', 24, 24, 1.0); print('missing null', bad.isNull()); assert bad.isNull()"

Header import 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.header import HeaderBar; print('header import ok', HeaderBar)"

Header offscreen 实例化与 icon helper 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication, QWidget; from src.theme import ThemeManager; from src.ui.header import HeaderBar; app=QApplication([]); ThemeManager().apply_theme(app, ThemeManager.DEFAULT_PRESET); parent=QWidget(); h=HeaderBar(parent); pm=h._load_colored_svg('assets/icons/search.svg', '#FFFFFF', 24, 24); print('header pixmap null', pm.isNull(), 'size', pm.width(), pm.height()); print('sync role', h.btn_sync.property('role')); print('sync variant', h.btn_sync.property('variant')); print('sync state', h.btn_sync.property('state')); assert not pm.isNull(); assert h.btn_sync.property('role') == 'windowControl'; assert h.btn_sync.property('variant') == 'toolbar'; assert h.btn_sync.property('state') == 'normal'"

旧 `src.ui.components` 导入回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.components import SharedMoreMenu, get_colored_icon; print('components import ok', SharedMoreMenu, get_colored_icon)"

默认启动接入回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; import main; print('main import ok')"

语法检查：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/utils/icon_loader.py src/ui/header.py main.py

禁止范围检查：

    git diff --name-only -- assets
    git diff --name-only -- src/ui/components.py
    git diff --name-only -- src/ui/todo_board.py
    git diff --name-only -- src/ui/schedule_detail_pop.py
    git diff --name-only -- src/ui/time_picker.py
    git diff --name-only -- src/ui/time_picker_week.py
    git diff --name-only -- src/ui/week_window.py
    git diff --name-only -- src/ui/month_window.py
    git diff --name-only -- src/theme
    git diff --name-only -- src/data
    git diff --name-only -- src/repositories
    git diff --name-only -- src/services
    git diff --name-only -- src/controllers
    git diff --name-only -- src/utils/signals.py
    git diff --name-only -- src/utils/styles.py
    git diff --name-only -- main.py
    git diff --name-only -- requirements.txt
    git diff --name-only -- schedule.db

允许范围检查：

    git diff --name-only -- src/ui

预期 `src/ui` diff 仅允许：

    src/ui/header.py
    src/ui/utils/icon_loader.py

总范围检查：

    git diff --name-only
    git status --short --branch

预期最终只允许：

- `src/ui/utils/icon_loader.py`
- `src/ui/header.py`
- `manage_instruction/Work_Log.md`
- 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第八轮 8-2b（公共 icon loader 最小提取与 Header 单点替换）
- 开工前 git 状态
- 实际修改文件
- 新增 helper 文件和函数名
- helper 签名与职责
- helper fallback 行为
- 是否依赖 QWidget/self
- `header.py::_load_colored_svg(...)` 保持兼容的说明
- 确认未修改 `_load_colored_svg(...)` 调用方
- 确认未修改 `btn_sync` 试点
- helper import 验证结果
- helper offscreen 渲染验证结果
- Header import 验证结果
- Header offscreen 实例化与 icon helper 回归结果
- 旧 `src.ui.components` 导入回归结果
- 默认启动接入回归结果
- py_compile 结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

特别记录：

- 本轮只新增一个 helper。
- 本轮只替换 `header.py::_load_colored_svg(...)` 这一个低风险调用边界。
- 本轮不统一所有 icon loader。
- 本轮不修改 assets。
- 本轮不处理 `QIcon` 返回路径。
- 本轮不处理 `todo_board.py` / `schedule_detail_pop.py` / `time_picker*.py`。

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
```
