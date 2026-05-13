# Work Instruction

本文件用于决策窗口向执行窗口下达具体执行指令。

当前主架构改写方案见 `Work_Formulation.md`；架构改写前行为和目录快照见 `Work_Snapshot.md`；执行过程记录写入 `Work_Log.md`。

## 执行日志硬性要求

执行窗口每次完成一轮操作后，必须更新 `manage_instruction/Work_Log.md`。

日志至少记录：

- 本轮任务名称。
- 实际修改的文件。
- 执行过的验证命令或人工验证结果。
- 未完成事项。
- 风险、疑点或需要决策窗口确认的问题。

如果任务中途失败，也必须写入失败位置、错误信息摘要和已回滚/未回滚状态。

---

# 当前执行任务：第一轮 A - 架构骨架 + 主题/EventBus 基建

## 任务目标

执行第一轮 A，只建立低风险基础设施，不触碰数据库逻辑，不接入旧 UI，不实现新功能。

本轮完成后，项目外部行为应保持不变。

## 允许修改

- `src/models/`
- `src/repositories/`
- `src/services/`
- `src/controllers/`
- `src/theme/`
- `src/utils/signals.py`
- `manage_instruction/Work_Log.md`

如发现必须修改上述范围以外的文件，请先停止并在窗口中说明原因，不要擅自扩大范围。

## 禁止修改

- 不修改 `src/data/database.py`。
- 不修改任何现有 UI 页面逻辑。
- 不替换旧 UI 中已有的 `setStyleSheet(...)`。
- 不接入换肤 UI。
- 不实现搜索、筛选、导出、同步、四象限等新功能。
- 不修改数据库字段、迁移逻辑或 `schedule.db`。
- 不修改 `Work_Snapshot.md`，除非决策窗口另行要求。

## 具体要求

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

## 验收要求

执行窗口完成后至少验证：

- 应用仍可启动。
- `from src.utils.signals import global_signals` 可用。
- `global_signals.skin_changed` 仍是无参信号，可连接无参 slot 并 emit。
- `ThemeManager` 可被 import。
- `ThemeManager` 能读取 `light.qss` 和 `dark.qss`。
- 没有修改 `src/data/database.py`。
- 已更新 `manage_instruction/Work_Log.md`。

## 建议验证命令

可使用类似命令做 import 和信号兼容检查：

```powershell
python -c "from src.utils.signals import global_signals; global_signals.skin_changed.connect(lambda: None); global_signals.skin_changed.emit(); print('signals ok')"
python -c "from src.theme.theme_manager import ThemeManager; print('theme manager ok')"
```

如果启动 GUI 验证会被当前环境限制，请记录限制原因，并至少完成 import 级验证。
