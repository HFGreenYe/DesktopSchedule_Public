# History Instruction

本文件用于归档已经完成或废弃的历史执行指令，避免 `Work_Instruction.md` 长期累积内容、增加后续窗口读取成本。

使用规则：

- `Work_Instruction.md` 只保留当前正在执行或下一步即将执行的指令。
- 当前指令完成、验收并提交 Git 后，再将该指令移动到本文件归档。
- 归档时保留任务标题、执行日期、对应 Git commit、结果摘要和后续备注。
- 不把未完成的当前任务提前归档。

---

## 归档记录

## 2026-05-13 第一轮 A - 架构骨架 + 主题/EventBus 基建

状态：已完成。

对应提交：执行日志记录用户侧已提交 `2803436 fix: add missing zhdate dependency`；第一轮 A 代码本身在读取时工作区已干净，具体提交号请以 `git log` 为准。

### 任务目标

执行第一轮 A，只建立低风险基础设施，不触碰数据库逻辑，不接入旧 UI，不实现新功能。

本轮完成后，项目外部行为应保持不变。

### 允许修改

- `src/models/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `src/theme/`
- `src/utils/signals.py`
- `manage_instruction/Work_Log.md`

如发现必须修改上述范围以外的文件，需要先停止并说明原因，不得擅自扩大范围。

### 禁止修改

- 不修改 `src/data/database.py`。
- 不修改任何现有 UI 页面逻辑。
- 不替换旧 UI 中已有的 `setStyleSheet(...)`。
- 不接入换肤 UI。
- 不实现搜索、筛选、导出、同步、四象限等新功能。
- 不修改数据库字段、迁移逻辑或 `schedule.db`。
- 不修改 `Work_Snapshot.md`，除非决策窗口另行要求。

### 具体要求

1. 建立以下目录，并添加 `__init__.py`：

```text
src/models/
src/repositories/
src/services/
src/controllers/
src/theme/
```

2. 新增主题基础文件：

```text
src/theme/theme_manager.py
src/theme/light.qss
src/theme/dark.qss
```

3. `ThemeManager` 只提供基础能力：

- 读取 QSS 文件。
- 应用 QSS 到 `QApplication`。
- 刷新动态属性样式，例如对 widget 执行 `unpolish/polish/update`。

4. `ThemeManager` 本轮不做的事：

- 不主动应用到现有应用启动流程。
- 不替换旧页面样式。
- 不实现完整换肤 UI。
- 不改变当前默认视觉效果。

5. 扩展 `src/utils/signals.py` 为兼容式事件总线。

硬性兼容要求：

- 必须保留 `global_signals` 名称。
- 必须保留无参 `skin_changed = pyqtSignal()`。
- 不修改旧信号签名。

6. 可新增以下信号：

```python
theme_changed = pyqtSignal(str)
schedule_added = pyqtSignal(object)
schedule_updated = pyqtSignal(object)
schedule_deleted = pyqtSignal(int)
category_changed = pyqtSignal()
```

7. 本轮只提供事件通道，不要求旧窗口迁移到事件总线。

### 验收要求

- 应用仍可启动。
- `from src.utils.signals import global_signals` 可用。
- `global_signals.skin_changed` 仍是无参信号，可连接无参 slot 并 emit。
- `ThemeManager` 可被 import。
- `ThemeManager` 能读取 `light.qss` 和 `dark.qss`。
- 没有修改 `src/data/database.py`。
- 已更新 `manage_instruction/Work_Log.md`。

### 验收摘要

- 执行窗口按步骤完成目录骨架、Theme 基础文件、`ThemeManager` 和 `signals.py` 兼容式扩展。
- `signals.py` 保留 `global_signals` 和无参 `skin_changed`，新增事件总线信号。
- `ThemeManager` 提供读取 QSS、应用 QSS、刷新 widget 样式能力。
- 初期 Python 验证受沙箱/解释器路径限制失败，后续用户本地 CMD 验证通过。
- 用户侧验证记录：
  - signals import 输出 `signals ok`。
  - ThemeManager 读取 QSS 输出 `theme ok`。
  - `.\.venv\Scripts\python.exe .\main.py` 应用成功启动，图标正常。
- 执行窗口后续确认沙箱外权限下 signals 验证通过。

### 后续备注

- 第一轮 A 不接入旧 UI，不改变默认视觉效果。
- 后续任务切换 `Work_Instruction.md` 前，应先把已完成指令归档到本文件。
