# Work Log

用途：记录当前活动小工单的执行过程、验证结果和待复核事项。

---

# 当前状态：整卡滚动与日 / 周卡片多选已完成

## 2026-07-19：只读审查与方案

- 日界面卡片固定高度为 `60px`，列表间隙为 `8px`；周界面卡片固定高度为 `46px`，每列间隙为 `2px`。
- 两处原先均使用普通 `QScrollArea` 的像素滚动，隐藏滚动条但没有整卡吸附，因此滚动值会停在任意像素，导致顶部和底部出现残缺卡片。
- 方案采用共享 `CardStepScrollArea`：滚轮按“卡片高度 + 间隙”移动，窗口变化和数据刷新后重算吸附点；内容溢出时缩减实际 viewport 的底部余量，使可视高度只容纳整数张完整卡片。
- 修改范围限定为日 / 周卡片模式，不接触课表、数据库、查询和拖拽写回。

## 2026-07-19：实现与验证

- 新增 `src/ui/common/card_step_scroll_area.py`，按当前滚动值最近的整卡吸附点计算下一步，并支持单次滚轮多格输入。
- 日、周卡片高度改为类常量，但实际尺寸仍分别保持 `60px / 46px`；列表原间隙仍保持 `8px / 2px`。
- 日界面渲染卡片后同步当前卡片数；周界面每列加载完成后分别统计卡片数并同步各自滚动区。
- 内容超过 viewport 时，以可完整显示的卡片数计算底部 viewport 余量和最大吸附值；窗口变化后自动重算并保留最近行位置。
- 项目 `.venv` 对新增组件、日界面和周界面完成 `py_compile`。
- PyQt6 offscreen 几何回归通过：日界面 `68px` 单步、周界面 `48px` 单步；两者连续滚至末端后首卡完整贴顶、末卡下沿恰好贴合 viewport 下沿。
- 补充 resize / 数据量变化回归通过：日滚动区由 `350px` 调整到 `420px` 后，完整可见卡片数由 5 张重算为 6 张，最大吸附值由 `340px` 调整为 `272px`；卡片数降至 4 张后底部余量和滚动范围均恢复为 0。

## 2026-07-19：日界面头部多选入口追补

- 用户截图命中的是 `HeaderBar` 头部右键菜单，而不是下方 `DashboardView` 空白区域菜单；后者已传入 `show_multiple_choice=True`，前者的独立构造漏传该参数。
- `HeaderBar` 现在保存主窗口同步的卡片 / 课表模式，只在当前为日视图且处于卡片模式时显示“多选”；日课表、待办和其他视图保持不显示。
- 多选仍为后续批量操作的菜单入口壳，本轮不绑定选择业务。
- 项目 `.venv` 语法检查通过；真实 `HeaderBar` 离屏验证确认日卡片菜单包含 `multiple_choice`，切换日课表或非日视图后均不包含该入口。

## 2026-07-19：日界面卡片多选实现

- `ActionContextMenu` 的“多选”由纯入口壳改为发出 `multiple_choice` 动作；激活后同一位置显示两字“退出”。日卡片下方空白菜单和主窗口头部菜单均复用该状态。
- 初版曾新增 `DayMultiSelectActionCard` 固定操作卡；该实现现已被独立弹窗取代，类和界面占位均已删除。
- `ScheduleCard` 在多选模式把原优先级圆点改为选择圆：未选中为白色，选中为当前主题上沿色 `65%` 透明度；再次点击取消。
- 当前选择使用 `schedule_id` 集合维护，刷新、排序和查询重绘后只保留仍实际显示的卡片；弹窗版进入多选时保持当前滚动位置，退出时关闭弹窗并恢复优先级颜色。
- 全选 / 全不选覆盖当前实际显示的日卡片。完成在存在未完成选中项时启用，撤销在存在已完成选中项时启用，删除在存在任意选择时启用；混合状态下完成和撤销可同时启用。
- Repository 新增批量状态和批量删除原子方法，UI 每次批量动作只刷新一次并发出一次全局刷新；重复实例仍按选中 ID 单独处理。
- 切换日课表或离开日视图自动退出。
- 初版固定操作卡的 PyQt6 offscreen 回归曾通过；当前验收以之后记录的独立弹窗视觉和交互回归为准。
- Peewee 内存数据库验证批量完成和批量删除成功，未产生部分写入。

## 2026-07-19：多选快捷退出与长拖拽崩溃修复

- 初版固定操作卡曾支持双击空白退出；独立弹窗版现统一使用退出图标或右上角关闭键退出。
- 长时间拖拽崩溃根因确定为日界面 `30000ms` 自动刷新计时器：`QDrag.exec()` 会运行嵌套事件循环，计时器仍会触发 `refresh_data()`，随后列表重绘对活动 `ScheduleCard` 执行 `deleteLater()`；原位置随即生成新卡片，而原 `QDrag` 仍持有已销毁源对象，表现为卡片黏住鼠标并最终触发 Qt 原生崩溃。
- `ScheduleCard` 新增拖拽开始 / 结束生命周期信号，日界面在活动拖拽期间将自动刷新、搜索、筛选和排序重绘合并为一个待处理刷新，拖拽结束后延迟补执行。
- 多选期间的拖拽限制已移除。操作卡现位于日程列表之外，`TodoListContainer` 的分组边界和日界面的写回顺序只处理日程卡片，因此不会污染日程排序索引。
- PyQt6 offscreen 回归模拟了拖拽嵌套循环中的自动刷新：活动源卡片保持在布局中，结束后补刷新；同时确认多选状态可以发起拖拽、双击空白可退出。
- 日卡片多选期间，单击卡片主体不再打开详情，改为双击打开；选择圆单击和卡片拖拽行为保持不变，普通日卡片模式仍为单击打开详情。
- 固定层过渡方案现已删除；独立弹窗不计入整卡滚动数量，滚轮滚动、拖拽和排序只处理实际日程卡片。

## 2026-07-19：周界面卡片多选

- 周头部原有两段弹性空白中的右段被复用为固定多选面板宿主；未进入多选时仍保持透明空白，进入后显示两行图标，不改变 `125px` 头部和 `680×414` 窗口尺寸。
- 第一行八个日期范围按钮使用 `mon.svg` 至 `sun.svg` 和 `all.svg`；默认整周选中，七天与“全部”双向联动且允许清空范围。
- 第二行五个功能按钮使用 `Multiplechoice.svg / all_no.svg、finished.svg、withdraw.svg、delete.svg、exit.svg`；全选状态切换图标，完成 / 撤销 / 删除按当前选择状态灰化。
- 两行采用固定 `20×20px` 按钮、`16×16px` 图标和行内等距弹簧，实测两行首尾中心误差不超过 `1px`，未遮挡挂起、更多、同步或关闭键。
- `WeekScheduleCard` 新增多选选择圆和按 ID 保持的选择状态；多选期间单击主体不打开详情，双击打开详情，原同列及跨日期拖拽继续可用。
- 第一行只控制全选范围；完成、撤销和删除复用批量原子接口并在成功后刷新周窗口、通知主界面同步。
- 真实周窗口 PyQt6 offscreen 回归通过：整周 / 单日 / 全部范围联动、全选 / 全不选图标切换、完成 / 撤销按钮矩阵、批量状态 / 删除调用、多选拖拽信号和退出恢复均符合合同。

## 2026-07-19：日 / 周多选固定菜单改为独立弹窗

- 新增共享 `ScheduleMultiSelectPopup`：背景使用主题上下沿渐变，头部以下覆盖 `70%` 白色遮罩；标题在左，置顶和关闭键以零间距紧贴右上角。
- 弹窗置顶初始值读取主窗口置顶偏好，切换时只调用自身窗口标志，不写回主窗口设置；置顶图标为白色，未置顶为灰色。
- 日弹窗为一行五个 `36×36px` 方形图标按钮，背景使用主题上下沿中值；全选后 `Multiplechoice.svg` 切换为 `all_no.svg`，完成 / 撤销 / 删除按状态显示白色或灰色图标。
- 周弹窗为双行：第一行 `Mon` 至 `Sun` 和 `All` 使用 `34×34px` 圆形透明文本按钮，选中显示 `2px` 白边；第二行复用日弹窗功能按钮，两行首尾中心误差不超过 `1px`。
- 删除日界面列表上方固定操作卡和周界面头部固定双行面板；进入多选不再改变日界面滚动位置、周头部布局或卡片可视数量。
- 弹窗关闭键、系统关闭和退出图标都会同步退出对应多选状态并恢复卡片优先级圆点；切换课表 / 视图和周添加页仍自动关闭。
- 共享弹窗、日界面和真实周窗口 PyQt6 offscreen 回归通过，视觉抓图确认遮罩、按钮背景、圆形白边及右上角控制键位置符合合同。

## 2026-07-19：Claude Code 审查与拖拽保护修复

### 审查触发

用户在 Kimi Code（Kimi K3）中对未提交变更执行了代码审查，Kimi 完成了项目结构梳理、git diff 归纳、依赖核对和 py_compile 验证，但在运行时冒烟测试阶段卡住（`CardStepScrollArea` 的 `QTimer.singleShot(0)` 延迟同步导致测试时 `_snap_points` 仍为 `[0]`，断言反复失败）。用户将 Kimi 输出贴给 Claude Code 要求复核。

### Claude Code 审查结果

**编译**: ✅ 全部 9 个源文件 `py_compile` 通过
**Git**: 未提交变更 `dfd7730`，25 文件 +1475/-62 行

**确认 Bug #1（中高危）— 已修复**:

`src/ui/week_window.py:395-408` — `WeekScheduleCard.mouseMoveEvent` 中拖拽清理逻辑**未受 try/finally 保护**，与日界面 `ScheduleCard`（`dashboard.py:282-295`）已修复的写法不一致：

```python
# 修复前 — 周界面（崩溃不清理）
self.drag_started.emit(self)
drag_result = drag.exec(Qt.DropAction.MoveAction)
self.drag_finished.emit(self, drag_result)
# 恢复样式和组件…  ← 若 drag.exec() 抛异常，以下永不执行
```

```python
# 修复后 — 周界面（与日界面一致）
drag_result = Qt.DropAction.IgnoreAction
try:
    drag_result = drag.exec(Qt.DropAction.MoveAction)
finally:
    # 恢复样式、显示组件、清理状态
    self.drag_finished.emit(self, drag_result)
```

- 若 `drag.exec()` 崩溃，`drag_result` 保持 `Qt.DropAction.IgnoreAction`，`_finish_card_drag` 收到后走取消逻辑——行为正确
- 影响范围：仅 `src/ui/week_window.py` 第 395-408 行，`py_compile` 通过

**确认 Bug #3（非问题）— 无需修改**:

`dashboard.py:_clear_schedule_cards` 从 `takeAt(0)` 改为 `reversed + isinstance(ScheduleCard)` 不是 bug。`list_layout` 仅含 `ScheduleCard` widget 和一个 `QSpacerItem`（stretch）。`QSpacerItem` 不是 `QWidget`，`item.widget()` 返回 `None`，`isinstance(None, ScheduleCard)` 为 `False`——stretch 被正确跳过。新写法比旧 `takeAt(0)` 更精确安全：将来即使 layout 多了非 ScheduleCard widget，也不会被误删。

### 未修复的已知项（低优先级）

- **CardStepScrollArea 初始化竞态**: `QTimer.singleShot(0)` 是 Qt 标准惯用模式，生产环境的事件循环自然顺序保证 sync 远在用户滚轮操作之前完成。仅在无事件循环的单元测试中需手动 `QApplication.processEvents()`。
- **日/周 drag_finished 信号签名不一致**: 日 `pyqtSignal(object)` 单参，周 `pyqtSignal(object, object)` 双参（card + drag_result）。旧代码遗留差异，本次未统一。
