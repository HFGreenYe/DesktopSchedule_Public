# Work Task Prompts

## 第八轮 8-2a：公共 icon loader 静态定位与提取基线

```markdown
请执行第八轮 8-2a：公共 icon loader 静态定位与提取基线。本轮只做只读审查和日志记录，不提取代码，不改源码。

## 1. 本轮目标

基于 `manage_instruction/Work_Instruction.md` 第八轮阶段合同，以及 `Work_Log.md` 的 8-0/8-1 结论，定位当前 UI 中重复的 icon loader / SVG recolor / QIcon/QPixmap 创建逻辑。

本轮目标：

- 找出所有图标加载、SVG 着色、QPixmap/QIcon 创建相关逻辑。
- 对比这些实现的输入、输出、颜色参数、尺寸参数、fallback 行为。
- 判断哪些逻辑适合后续抽到 `src/ui/utils/icon_loader.py`。
- 判断后续 8-2b 是否可以只替换一个低风险调用点。
- 不改源码。
- 不改 assets。
- 不新增 `icon_loader.py`。

本轮不做：

- 不创建 `src/ui/utils/icon_loader.py`。
- 不替换任何调用方。
- 不修改 `header.py`。
- 不修改 `todo_board.py`。
- 不修改 `schedule_detail_pop.py`。
- 不修改 `time_picker.py` / `time_picker_week.py`。
- 不修改 `components.py`。
- 不改 QSS。
- 不改业务逻辑。

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

具体禁止：

- 不新增 `src/ui/utils/icon_loader.py`。
- 不移动任何函数。
- 不替换任何 import。
- 不改任何现有 UI 文件。
- 不提交 Git。

若开工前已有 diff，需在 `Work_Log.md` 单独记录，不视为本轮源码改动。

## 3. 具体任务

1. 读取当前基线：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8

2. 定位图标加载相关函数和方法：

    - `get_colored_icon`
    - `_get_icon`
    - `_load_colored_svg`
    - `QSvgRenderer`
    - `QPixmap`
    - `QIcon`
    - `setIcon`
    - `setPixmap`
    - `assets/icons`
    - `assets/weather`

3. 重点审查以下文件：

    - `src/ui/components.py`
    - `src/ui/header.py`
    - `src/ui/todo_board.py`
    - `src/ui/schedule_detail_pop.py`
    - `src/ui/time_picker.py`
    - `src/ui/time_picker_week.py`
    - `src/ui/week_window.py`
    - `src/ui/month_window.py`

4. 输出 icon loader 职责地图：

    每个命中点至少记录：

    - 文件路径
    - 函数/方法名
    - 输入参数
    - 输出类型
    - 是否依赖 QWidget/self
    - 是否依赖 QPainter/QSvgRenderer
    - 是否读取 assets
    - fallback 行为
    - 是否适合抽为纯 helper
    - 风险等级

5. 判断后续 8-2b 的最小候选：

    建议优先选择低风险、无业务行为、无写库、无状态机的单个调用点。

    需要明确：

    - 是否建议优先提取 `components.py::get_colored_icon`
    - 是否建议优先替换 `header.py::_load_colored_svg`
    - 是否应暂缓 `todo_board.py::_get_icon`
    - 是否应暂缓 `schedule_detail_pop.py::_get_icon`
    - 是否应暂缓 time picker 系列

6. 更新 `manage_instruction/Work_Log.md`。

## 4. 建议静态搜索命令

图标加载全局定位：

    rg -n "get_colored_icon|_get_icon|_load_colored_svg|QSvgRenderer|QPixmap|QIcon|setIcon|setPixmap|assets/icons|assets/weather" src/ui

重点函数定位：

    rg -n "def get_colored_icon|def _get_icon|def _load_colored_svg" src/ui

按文件查看重点区域：

    rg -n "get_colored_icon|_get_icon|_load_colored_svg|QSvgRenderer|QPixmap|QIcon|setIcon|setPixmap" src/ui/components.py src/ui/header.py src/ui/todo_board.py src/ui/schedule_detail_pop.py src/ui/time_picker.py src/ui/time_picker_week.py src/ui/week_window.py src/ui/month_window.py

检查是否已有新 UI utils：

    Get-ChildItem -Path src\ui\utils -Force

确认本轮无源码 diff：

    git diff --name-only -- src
    git diff --name-only -- assets
    git diff --name-only -- main.py
    git diff --name-only -- requirements.txt
    git diff --name-only -- schedule.db
    git diff --name-only
    git status --short --branch

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第八轮 8-2a（公共 icon loader 静态定位与提取基线）
- 开工前 git 状态
- 实际修改文件
- 静态搜索命令和结果
- icon loader 命中点清单
- 各命中点职责地图
- 重复逻辑对比：
  - 输入参数
  - 输出类型
  - 颜色处理
  - 尺寸处理
  - fallback 行为
  - 是否依赖 QWidget/self
- 低风险提取候选
- 中风险候选
- 高风险暂缓项
- 是否建议执行 8-2b
- 8-2b 建议的唯一替换调用点
- diff 范围检查结果
- 未完成事项
- 风险或疑点

特别记录：

- 本轮只读审查，不改源码。
- 不创建 `src/ui/utils/icon_loader.py`。
- 不替换任何调用方。
- 不修改 assets。
- 后续若进入 8-2b，必须只提取一个 helper 并只替换一个低风险调用点。

完成后不要提交 Git，等待顾问窗口复核。
```
