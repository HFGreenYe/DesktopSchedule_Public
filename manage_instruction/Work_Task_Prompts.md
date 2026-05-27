# Work Task Prompts

## 第八轮 8-3b：MainWindow toast 单点提取

```markdown
请执行第八轮 8-3b：MainWindow toast 单点提取。本轮只提取一个低风险 toast helper，并只替换 `src/ui/main_window.py::show_toast` 这一处调用边界。

## 1. 本轮目标

基于 8-3a 静态审查结论，新增一个最小 toast helper，并让 `MainWindow.show_toast(message)` 保持原方法名、参数和行为语义不变，只把内部创建/显示 QLabel 的逻辑委托给 helper。

本轮目标：

- 新增 `src/ui/common/toast.py`。
- 只实现 MainWindow 当前 toast 需要的最小 helper。
- 只修改 `src/ui/main_window.py::show_toast(message)`。
- 保持 MainWindow 对外 `show_toast(message)` 方法不变。
- 保持原 toast 行为不变：
  - parent 仍为 `self`
  - 属性仍为 `self.toast_label`
  - 已有 toast 显示时先 close
  - QLabel 文案不变
  - 样式不变
  - 居中位置计算不变
  - `WA_TransparentForMouseEvents` 不变
  - 自动关闭时间仍为 500ms
- 不处理 `week_window.py` / `month_window.py` / `todo_board.py` 的 toast。
- 不处理 tooltip。
- 不修改 QSS。
- 不改变 UI 布局、交互、刷新链路、业务逻辑。

## 2. 允许/禁止

本轮允许修改：

- `src/ui/common/toast.py`
- `src/ui/main_window.py`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`（仅在需要维护复核锚点时）

本轮禁止修改：

- `src/ui/week_window.py`
- `src/ui/month_window.py`
- `src/ui/todo_board.py`
- `src/ui/header.py`
- `src/ui/components.py`
- `src/ui/list_picker.py`
- `src/ui/add_view.py`
- `src/ui/add_view_week.py`
- `src/ui/alarm_picker.py`
- `src/ui/alarm_picker_week.py`
- 除 `src/ui/main_window.py` 与 `src/ui/common/toast.py` 外的任何 `src/ui/` 文件
- `src/theme/`
- `src/data/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `src/utils/signals.py`
- `src/utils/styles.py`
- `assets/`
- `main.py`
- `requirements.txt`
- `schedule.db`
- `Work_Snapshot.md`
- `Work_Formulation.md`

禁止事项：

- 不创建 `src/ui/common/tooltip.py`。
- 不迁移 `CustomToolTip` / `ToolTipFilter`。
- 不统一所有 toast。
- 不修改 1500ms toast 路径。
- 不修改 MainWindow 除 `show_toast` 必要委托外的其它逻辑。
- 不清理 8-2b 遗留的 `header.py` unused import。
- 不提交 Git。

若开工前已有 diff，需在 `Work_Log.md` 单独记录，不视为本轮源码问题。

## 3. 具体任务

1. 读取当前基线：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Log.md -Encoding UTF8
    Get-Content -Path manage_instruction\Work_Task_Prompts.md -Encoding UTF8
    Get-Content -Path src\ui\main_window.py -Encoding UTF8

2. 新增 `src/ui/common/toast.py`。

    建议 helper 函数：

    `show_center_toast(parent, message, attr_name="toast_label", duration_ms=500)`

    语义要求：

    - 输入：
      - `parent`：承载 toast 的 QWidget。
      - `message`：显示文本。
      - `attr_name`：保存 toast QLabel 的 parent 属性名，默认 `"toast_label"`。
      - `duration_ms`：自动关闭时间，默认 `500`。
    - 输出：
      - 返回创建的 `QLabel`。
    - 行为：
      - 若 `parent` 上已有 `attr_name` 且可见，则先 close。
      - 创建 `QLabel(message, parent)`。
      - 将 QLabel 设置回 `setattr(parent, attr_name, label)`。
      - 样式必须与当前 `MainWindow.show_toast` 内联样式一致。
      - `setAlignment(Qt.AlignmentFlag.AlignCenter)` 保持一致。
      - `adjustSize()` 保持一致。
      - `WA_TransparentForMouseEvents` 保持一致。
      - 居中位置计算保持一致：
        - `x = (parent.width() - label.width()) // 2`
        - `y = (parent.height() - label.height()) // 2`
      - `QTimer.singleShot(duration_ms, label.close)`。
      - 不依赖 `MainWindow` 类型。
      - 不连接业务信号。
      - 不访问 db_manager / Repository / Service。
      - 不触发 QApplication。

3. 修改 `src/ui/main_window.py`。

    只允许做以下最小改动：

    - 从 `src.ui.common.toast` 或相对路径导入 helper。
    - 保留 `def show_toast(self, message):` 方法名与参数。
    - 将 `show_toast` 方法体改为委托 helper：
      - `self.toast_label = show_center_toast(self, message, attr_name="toast_label", duration_ms=500)`
      - 或等价写法。
    - 不改变 `show_toast` 的调用方。
    - 不修改其它 MainWindow 方法。
    - 不修改视图切换、提醒、挂起、详情弹窗、刷新链路。

4. 更新 `manage_instruction/Work_Log.md`。

## 4. 验收命令

定位 helper 与替换：

    rg -n "show_center_toast|show_toast|toast_label|WA_TransparentForMouseEvents|singleShot|500" src/ui/common/toast.py src/ui/main_window.py

确认未创建 tooltip 文件：

    Test-Path src\ui\common\tooltip.py

helper import 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.common.toast import show_center_toast; print('toast helper import ok', show_center_toast)"

helper offscreen 行为验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication, QWidget; from src.ui.common.toast import show_center_toast; app=QApplication([]); parent=QWidget(); parent.resize(400, 300); label=show_center_toast(parent, 'hello', duration_ms=500); print('label text', label.text()); print('same attr', getattr(parent, 'toast_label') is label); print('visible', label.isVisible()); print('transparent', label.testAttribute(label.WidgetAttribute.WA_TransparentForMouseEvents)); print('pos', label.x(), label.y()); assert label.text() == 'hello'; assert getattr(parent, 'toast_label') is label; assert label.testAttribute(label.WidgetAttribute.WA_TransparentForMouseEvents); label2=show_center_toast(parent, 'world', duration_ms=500); print('new label text', label2.text()); print('old closed or hidden', not label.isVisible()); assert label2.text() == 'world'; assert getattr(parent, 'toast_label') is label2"

MainWindow import 验证：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.main_window import MainWindow; print('main window import ok', MainWindow)"

MainWindow offscreen show_toast 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); w.resize(500, 400); w.show_toast('toast check'); print('toast attr', hasattr(w, 'toast_label')); print('toast text', w.toast_label.text()); print('toast visible', w.toast_label.isVisible()); print('transparent', w.toast_label.testAttribute(w.toast_label.WidgetAttribute.WA_TransparentForMouseEvents)); assert hasattr(w, 'toast_label'); assert w.toast_label.text() == 'toast check'; assert w.toast_label.testAttribute(w.toast_label.WidgetAttribute.WA_TransparentForMouseEvents)"

确认其它 toast 文件未改：

    git diff --name-only -- src/ui/week_window.py
    git diff --name-only -- src/ui/month_window.py
    git diff --name-only -- src/ui/todo_board.py
    git diff --name-only -- src/ui/header.py
    git diff --name-only -- src/ui/components.py
    git diff --name-only -- src/ui/list_picker.py
    git diff --name-only -- src/ui/add_view.py
    git diff --name-only -- src/ui/add_view_week.py
    git diff --name-only -- src/ui/alarm_picker.py
    git diff --name-only -- src/ui/alarm_picker_week.py

语法检查：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/common/toast.py src/ui/main_window.py main.py

默认入口 import 回归：

    D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; import main; print('main import ok')"

范围检查：

    git diff --name-only -- src/theme
    git diff --name-only -- src/data
    git diff --name-only -- src/repositories
    git diff --name-only -- src/services
    git diff --name-only -- src/controllers
    git diff --name-only -- src/utils/signals.py
    git diff --name-only -- src/utils/styles.py
    git diff --name-only -- assets
    git diff --name-only -- main.py
    git diff --name-only -- requirements.txt
    git diff --name-only -- schedule.db
    git diff --name-only -- src/ui

预期 `src/ui` diff 仅允许：

    src/ui/common/toast.py
    src/ui/main_window.py

总范围检查：

    git diff --name-only
    git status --short --branch

预期最终只允许：

- `src/ui/common/toast.py`
- `src/ui/main_window.py`
- `manage_instruction/Work_Log.md`
- 必要时 `manage_instruction/Work_Task_Prompts.md`

## 5. Work_Log.md 记录要求

更新 `manage_instruction/Work_Log.md`，至少记录：

- 本轮任务名称：第八轮 8-3b（MainWindow toast 单点提取）
- 开工前 git 状态
- 实际修改文件
- 新增 helper 文件和函数名
- helper 签名与职责
- helper 是否依赖 MainWindow
- helper 是否访问 db_manager / Repository / Service
- `MainWindow.show_toast(message)` 兼容性说明
- 确认未修改 `show_toast` 调用方
- 确认未修改 week/month/todo_board toast
- 确认未创建 tooltip 文件
- helper import 验证结果
- helper offscreen 行为验证结果
- MainWindow import 验证结果
- MainWindow offscreen show_toast 回归结果
- py_compile 结果
- main import 回归结果
- diff 范围检查结果
- 未完成事项
- 风险或疑点

特别记录：

- 本轮只提取 MainWindow toast。
- 本轮不统一全部 toast。
- 本轮不处理 tooltip。
- 本轮不修改 QSS。
- 本轮不修改 1500ms toast 路径。
- 本轮不清理 8-2b 遗留的 `header.py` unused import。

如果 Python 验证受沙箱权限影响，请申请沙箱外权限运行；若仍受限，请写明需用户本地 CMD 复跑命令。

完成后不要提交 Git，等待顾问窗口复核。
```
