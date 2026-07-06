# Work Log

用途：记录当前阶段执行过程、验证结果、风险和结论。

---

# 当前状态：暂无活动阶段日志

最近一组功能补充与 UI 细修记录已于 2026-06-17 归档。

归档位置：

- `manage_instruction/History_Log.md`

归档范围：

- 坐标显示入口调整。
- 待办看板文字截断与紧凑视图状态修正。
- 添加表单重要性文案与选项显示修正。
- 右键菜单视图子菜单图标替换。
- 天气服务失败兜底与 loading 过渡。
- 月界面日期弹窗 toggle 与标题色细节。
- 日界面详情框视觉与滚动条调整。
- 更多菜单使用帮助入口和分隔线一致性修正。
- 更多菜单卡片模式 / 课表模式入口壳。

当前工作区等待下一项功能或 UI 适配任务。

---

## 2026-06-20 月界面时间选择器裁切与圆角修正

任务来源：

- 用户反馈月界面时间选择器在日历展开时，启用开始时间开关和结束时间选择区域右侧会被裁切；收起日历后又能完整显示。
- 用户要求开关缩小并与“启用开始时间”文字垂直居中，右沿与日期栏、日历右沿对齐；时间区域在单结束时间和开始/结束双时间形态下均不得裁切；时间框和快捷时长按钮圆角需要缩小。

原因定位：

- 月专用时间页虽然把日期栏固定为 `136px`，但日历仍使用横向 `Expanding` 策略；`QCalendarWidget` 展开后的 size hint 会把滚动内容页撑宽。
- 时间页横向滚动条被禁用，因此超出月界面 `136px` 左栏的右侧内容会直接被裁切；日历收起后该宽度约束消失，所以控件又恢复完整显示。
- 共享 `IOSSwitch` 固定为 `50×28px`，其滑块坐标也是按该尺寸写定，不能只缩放控件外框，否则滑块会被裁切。

实际修改：

- `src/ui/month_window.py`
  - 新增月界面局部 `MonthCompactSwitch(IOSSwitch)`，尺寸为 `38×24px`；滑块直径、左右端点和动画终点按自身尺寸计算，不修改共享 `IOSSwitch`。
  - 月时间页用紧凑开关替换原实例，并重新连接原 `_on_switch_toggled()`，保留开始时间组和快捷时长显隐逻辑。
  - “启用开始时间”文字与紧凑开关垂直居中；开关右沿固定为左栏 `x=136px`，与日期栏和日历右沿一致。
  - 日历固定为 `136×122px` 且使用固定横向策略，阻止展开状态改变滚动内容宽度。
  - 时间选择容器和快捷时长区域均固定为 `136px` 宽；开始/完成两个时间组各固定为 `65px`，单结束时间和双时间形态均留在可视范围内。
  - 时间选择容器和快捷时长按钮圆角由胶囊式圆角缩小为 `4px`。

隔离范围：

- 未修改 `src/ui/time_picker.py`、`src/ui/components.py` 或日/周界面添加页。
- 共享 `TimePickerView` 继续使用原 `50×28px` 的 `IOSSwitch` 和原日历、时间容器样式。
- 未修改日期选择、日历展开/收起、开始时间启用、快捷时长计算和确认信号逻辑。

验证记录：

- PyQt6 offscreen 展开/收起验证：两种状态下月时间页内容宽度均为 `136px`；日期栏、日历、紧凑开关和时间容器右沿均为 `136px`。
- 紧凑开关尺寸为 `38×24px`，与“启用开始时间”文字中心线一致；开关启用后开始时间组和快捷时长区域正常显示。
- 开始/完成时间双组和全部快捷时长按钮的右边界均未超过 `136px`。
- 对照构造共享 `TimePickerView`，其开关仍为 `50×28px`，确认未影响日/周界面。
- offscreen 展开与收起截图目检：未发现右侧裁切或控件重叠；真实 Windows 字体与细节间距仍由用户运行后确认。

---

## 2026-06-20 月界面时间选择器紧凑 UI 调整

任务来源：

- 用户要求参照月界面专用清单选择器，单独调整月界面添加与详情修改流程中的时间选择器 UI，不影响日界面和周界面共享的时间选择器。
- 设置态标题需要紧凑显示为“设置时间”，详情编辑态显示为“修改时间”；日期栏参考月清单卡片；底部取消/确定按钮与月添加表单取消/保存按钮保持相同尺寸、横向位置和下沿距离。

实际修改：

- `src/ui/month_window.py`
  - 新增月界面局部子类 `MonthTimePickerView(TimePickerView)`；月界面实例改用该子类，未修改共享 `src/ui/time_picker.py`。
  - 标题栏高度调整为 `28px`，标题使用左上角 `12px` 字体；设置态显示“设置时间”，任何以“修改”开头的详情编辑标题在月界面紧凑显示为“修改时间”。
  - 挂起按钮继续隐藏；保留原关闭按钮和取消返回路径，未改变现有返回行为。
  - 日期栏固定为 `136×28px`，与月清单卡片内容区同宽；保留点击日期栏展开/收起日历的原功能。
  - 日历、时间滚轮、开始/完成时间标签和快捷时长按钮仅在月界面实例中压缩，未修改时间值、日期选择、持续时长或确认信号逻辑。
  - 底部取消/确定按钮调整为 `64×24px`，横坐标为 `0 / 72`，与月添加表单取消/保存按钮完全一致；两组按钮距月窗口下沿均为 `40px`。
  - 月专用时间页高度继续对齐月添加表单高度，避免底部按钮悬在左栏中部。

隔离范围：

- 未修改 `src/ui/time_picker.py`、`src/ui/add_view.py`、`src/ui/add_view_week.py`。
- 日界面和周界面继续直接使用共享 `TimePickerView`；共享实例仍保持 `60px` 标题栏、`45px` 日期按钮和 `40px` 底部按钮。
- 未修改数据库、Repository、Service、时间字段或保存逻辑。

验证记录：

- 项目 `.venv` 执行 `python -m py_compile src/ui/month_window.py src/ui/time_picker.py main.py`：通过。
- PyQt6 offscreen 几何验证：月时间页与月清单页标题横坐标均为 `4px`；日期栏与清单内容区均为 `136px` 宽。
- PyQt6 offscreen 底部按钮验证：月添加页与月时间页按钮尺寸均为 `64×24px`，横坐标均为 `0 / 72`，窗口内下沿坐标均为 `439px`。
- PyQt6 offscreen 交互验证：日期栏连续点击可展开并收回日历；详情编辑标题可归一化为“修改时间”；取消/确认信号连接沿用共享实现。
- 对照构造共享 `TimePickerView`，确认其标题栏、日期按钮和底部按钮尺寸未变化。
- offscreen 截图目检：月界面左栏内日期栏、日历、时间滚轮、快捷时长和底部按钮无重叠；中文在 offscreen 字体环境中显示为方框，不影响几何检查，仍需用户在真实 Windows 界面中确认最终视觉间距。

---

## 2026-06-20 详情弹窗编辑请求跟随当前视图

任务来源：

- 用户要求已跨视图保留的详情弹窗在双击时间、提醒或清单时，由当前正在显示的视图承接编辑，而不是回到弹窗最初创建的视图。
- 原问题表现为：周界面创建的弹窗保留到日界面后，双击清单会让隐藏的周界面进入修改状态；日界面没有可见变化。

原因定位：

- `ScheduleDetailPop.source_view` 在弹窗创建时固定，用于区分来源和配色。
- `MainWindow.go_to_time_picker_for_edit()`、`go_to_alarm_picker_for_edit()`、`go_to_list_picker_for_edit()` 同时把该固定来源当作路由目标，因此弹窗跨视图存在后，编辑请求仍返回原窗口。
- 月界面此前只有添加态 picker，没有详情编辑模式和保存返回链，不能仅靠修改一个路由条件承接编辑。

实际修改：

- `src/ui/main_window.py`
  - 新增 `_resolve_detail_edit_target()`，编辑请求发生时按当前可见状态判断目标：周窗口可见时走周界面，月窗口可见时走月界面，主窗口待办页可见时走待办，否则走日界面。
  - `source_view` 继续保留为弹窗展示语义，并只在没有可见视图时作为兜底，不再直接决定日/周/月编辑目标。
  - 时间、提醒、清单三条详情编辑入口统一使用动态目标。
  - 主窗口 picker 新增当前页返回记录：从待办页进入编辑后返回待办，从日界面进入则返回日界面。
  - 待办看板独立窗口保持其现有清单编辑承接；看板可见且弹窗来源为看板时仍优先回到看板，避免改变独立看板流程。
  - 月界面编辑完成后复用现有外部视图更新处理，刷新详情弹窗字段。
- `src/ui/month_window.py`
  - 新增 `schedule_updated` 信号以及时间、提醒、清单三种 picker 的编辑模式状态。
  - 新增 `go_to_time_picker_for_edit()`、`go_to_alarm_picker_for_edit()`、`go_to_list_picker_for_edit()`，直接复用月界面左栏现有 picker，不新增 UI 页面。
  - 编辑取消后回到月历基础状态，不误回月界面添加表单。
  - 编辑确认沿用现有字段：时间更新 `start_time/end_time`，提醒更新 `reminder_time/is_alarm/alarm_duration`，清单更新 `category_id`。
  - 重复日程继续提供“修改所有 / 仅修改本次 / 取消”判断；修改完成后刷新月格 marker cache 并通知主窗口刷新详情弹窗。

范围说明：

- 未改变详情弹窗的配色来源、位置和跨视图持久显示规则。
- 未新增数据库字段，未修改 Repository、Service 或重复日程数据库接口。
- 未把月界面添加态 picker 与编辑态状态混用；两种模式分别返回各自页面。

验证记录：

- 项目 `.venv` 执行 `python -m py_compile src/ui/main_window.py src/ui/month_window.py src/ui/week_window.py src/ui/schedule_detail_pop.py main.py`：通过。
- PyQt6 offscreen 路由验证：旧来源为 `week` 时，当前日/待办/月/周状态分别解析为 `day/todo/month/week`。
- PyQt6 offscreen 月界面验证：时间、提醒、清单三种编辑页均可进入，标题与模式正确，取消后恢复 `add` 状态。
- 使用 monkeypatch 替代数据库写入验证三种确认 payload 和 `schedule_updated` 信号：通过；未写 `schedule.db`。
- 测试窗口主动关闭并处理事件后进程退出码为 `0`。
- 仍需真实 Windows 交互复测完整路径：周界面打开详情弹窗→切换日/待办/月→分别双击时间、提醒、清单；当前可见界面应立即进入对应编辑页，确认或取消后留在当前视图。

---

## 2026-06-19 月界面清单选择器紧凑 UI 调整

任务来源：

- 用户要求只调整月界面添加流程中的清单选择器，不影响日界面和周界面复用的 `ListPickerView`。
- 月界面左栏宽度仅 `136px`，原共享选择器使用 `24px` 标题、`50px` 清单卡片和三枚 `85×40px` 按钮，导致标题截断、按钮重叠和内容溢出。

实际修改：

- `src/ui/month_window.py`
  - 新增月界面局部子类 `MonthListPickerView`，共享 `ListPickerView` 源码和其他界面实例均未修改。
  - 标题栏高度调整为 `28px`，标题使用左上角 `12px` 字体；未来传入“修改【名称】清单”等修改标题时，月界面紧凑显示为“修改清单”。
  - 月界面实例隐藏挂起键和右上角关闭键；返回统一使用底部“取消”按钮。
  - “+ 新建 / 取消 / 确定”三键统一为 `38×24px`，高度与月界面添加表单的取消/保存按钮一致；横向位置为 `x=0 / 56 / 98`，均位于 `136px` 左栏内且互不重叠。
  - 复测发现清单页仍按自身较小的 `135px` 高度布局，导致按钮距窗口下沿 `199px`，未满足与添加页 footer 对齐的要求；已改为复用月界面添加页 `294px` 的页面高度，使两组按钮使用相同纵向基线。
  - 清单卡片调整为 `136×28px`，与月界面标题输入框同宽；圆点、文字、选中标记和内部边距同步缩小，但保留原清单编号、名称、选中和删除行为。
  - 新建清单输入区同步压缩为 `28px` 高，未修改新建、删除、选择、确认和数据库逻辑。

隔离范围：

- 日界面和周界面继续直接使用共享 `ListPickerView`，其 `60px` 标题栏、`50px` 清单卡片和 `85×40px` 底部按钮保持不变。
- 未修改 `src/ui/list_picker.py`、数据库、Repository、Service 或清单回填字段。

验证记录：

- 项目 `.venv` 执行 `python -m py_compile src/ui/month_window.py main.py`：通过。
- PyQt6 offscreen 几何验证：月界面标题栏 `28px`；关闭/挂起按钮隐藏；三枚底部按钮均为 `38×24px` 且无重叠；清单卡片为 `136×28px`。
- PyQt6 offscreen 纵向基线复测：调整前添加页/清单页按钮距窗口下沿分别为 `40px / 199px`；修正页面高度后两者均为 `40px`。
- 对照验证共享 `ListPickerView` 仍为 `60px` 标题栏和 `85px` 按钮宽度，确认本轮未影响日/周界面。

跨视图详情弹窗编辑路由当时评估（后续已完成）：

- 以下内容记录 2026-06-19 的实施前判断；动态路由与月界面编辑承接已于 2026-06-20 完成，当前结果以本日志顶部“详情弹窗编辑请求跟随当前视图”为准。

- 当前详情弹窗创建时会固定记录 `source_view`；`MainWindow.go_to_time_picker_for_edit()`、`go_to_alarm_picker_for_edit()`、`go_to_list_picker_for_edit()` 根据这个来源把编辑请求送回原窗口。
- 因此周界面创建的详情弹窗即使保留到日界面，双击清单仍会让隐藏的 `WeekWindow` 进入编辑状态；这与用户观察一致。
- 改为“跟随当前可见视图”属于中等复杂度、边界清晰的独立工单：需要记录当前路由，并让时间/提醒/清单三条编辑链在信号触发时选择当前窗口，而不是弹窗创建来源。
- 日/周/待办已有各自编辑承接链，可统一路由；月界面当前只有添加态 picker，尚无完整的详情编辑模式、保存和返回链，因此若要求弹窗在月界面也可编辑，需要补齐月界面编辑承接，不能只改一个条件分支。
- 建议保留“切换视图后弹窗继续显示”的目标，后续单独实现当前视图编辑路由；仅在该工单验证失败时再退回“切换视图关闭弹窗”的低成本方案。

---

## 2026-06-19 跨视图详情弹窗持久显示修复

任务来源：

- 用户要求日 / 周 / 月 / 待办视图切换时，已打开的日程详情弹窗继续存在，只有用户主动点击弹窗关闭按钮时才关闭。
- 当前表现不稳定：首次日转周、周转日时弹窗可能随原窗口隐藏，后续切换又可能继续显示；非今天日程更容易暴露该问题。

原因定位：

- `ScheduleDetailPop` 是无显式父窗口的 `Qt.Tool` 顶级窗口，Windows / Qt 可能根据创建时的活跃窗口建立临时 owner 关系。
- `MainWindow.switch_view()` 会依次隐藏和显示不同顶级窗口，但此前没有显式管理详情弹窗的可见状态。
- 前几次自动消失属于 owner 窗口隐藏时的附带行为，并非业务代码主动关闭；随着活跃窗口和原生 owner 状态变化，后续行为不再一致。
- `DashboardView.open_popups` 此前依赖 `isVisible()` 清理列表，但 native owner 隐藏不等于用户主动关闭，容易误删应保留的弹窗。

实际修改：

- `src/ui/schedule_detail_pop.py`
  - 新增 `popup_closed` 信号。
  - 用户或程序真正执行 `close()` 时由 `closeEvent()`发出自身对象，供管理列表移除。
- `src/ui/dashboard.py`
  - 创建详情弹窗时连接 `popup_closed`，用户主动关闭后从 `open_popups` 移除。
  - 不再使用 `isVisible()` 清理弹窗列表。
  - 再次点击同一日程时复用已有弹窗，并执行 `show()` / `raise_()` / `activateWindow()`。
  - 新增 `restore_detail_popups()`：保留对象、位置和编辑状态，通过 `hide()` / `show()` 强制恢复可能被原生 owner 隐藏的工具窗口。
- `src/ui/todo.py`
  - 待办列表独立维护的详情弹窗同步采用相同生命周期：不再按 `isVisible()` 丢弃，主动关闭时从列表移除，并提供切换视图后的恢复入口。
- `src/ui/main_window.py`
  - 日 / 周 / 月 / 待办视图切换完成后，通过 `QTimer.singleShot(0, ...)` 统一恢复日程与待办两组仍在管理列表中的详情弹窗。
  - 不关闭、不清空详情弹窗，也不改变弹窗位置。

范围说明：

- 未修改日程数据、弹窗内容编辑或保存逻辑。
- 未修改视图路由顺序和窗口位置计算。
- 未强制将弹窗置顶；只恢复视图切换期间被系统隐藏的弹窗。

验证记录：

- 使用 Codex bundled Python 执行 `python -m py_compile src/ui/schedule_detail_pop.py src/ui/dashboard.py src/ui/todo.py src/ui/main_window.py main.py`：通过。
- AST 生命周期接线检查：`ScheduleDetailPop.closeEvent()`、日程/待办两组移除与恢复方法、`MainWindow` 统一恢复入口均存在并通过断言。
- 沙箱外使用项目 `.venv\Scripts\python.exe` 复跑相同 `py_compile`：通过；解释器为项目虚拟环境，PyQt6 来自 `.venv\Lib\site-packages`。
- PyQt6 offscreen 生命周期验证：日程与待办两组恢复方法均按 `hide → show → move → raise` 执行，保留原位置；主动关闭后的移除路径可清空对应管理项。
- `git diff --check`：通过，仅有 Git 的 LF/CRLF 工作区提示。
- 静态检查确认 `isVisible()` 清理路径已删除，手动关闭信号、列表移除方法和视图切换后恢复调用均已接入。
- Codex 沙箱内直接启动项目 `.venv` 会被托管环境限制并报告无法创建基础 Python 进程；沙箱外验证确认基础 Python 实际存在，项目 `.venv` 本身可正常使用。此前“基础 Python 已不存在”的判断已纠正。
- 真实 Windows 复测需覆盖用户给出的完整序列，并优先使用非今天日程：日开弹窗→周→周开弹窗→日→再次日开弹窗→周→周开弹窗→日；所有未手动关闭的弹窗均应持续显示。
- 还需单独确认用户点击关闭按钮后，该弹窗不会在后续视图切换时重新出现。

---

## 2026-06-19 周界面翻周按钮命中区扩展

任务来源：

- 用户反馈周界面左右翻周按钮命中范围偏窄，点击边缘时容易误选当前周最左或最右日期。

实际修改：

- 修改 `src/ui/week_window.py`。
- 左右翻周按钮宽度由 `20px` 增加到 `32px`，高度继续保持 `36px`。
- 左按钮外侧位置保持 `x=4`，新增宽度只向右侧扩展；使用左对齐和 `6px` 左内边距，保持箭头靠近原视觉位置。
- 右按钮外侧继续保留 `4px` 边距，位置由 `width - 24` 调整为 `width - 36`，新增宽度只向左侧扩展；使用右对齐和 `6px` 右内边距。
- 未修改翻周函数、日期选择信号、双击跳转、日程卡片或顶部日期布局。

验证记录：

- 使用 Codex bundled Python 执行 `python -m py_compile src/ui/week_window.py main.py`：通过。
- 静态检查确认左右按钮均为 `32×36px`，右按钮位置与新宽度匹配。
- `git diff --check` 初次发现新增行尾空格，已清理后复跑通过。
- 实际命中范围和箭头视觉位置仍需用户在周窗口中点击两侧边缘验证。

---

## 2026-06-19 周界面清单页控件精简与详情框样式统一

任务来源：

- 用户反馈周界面进入“选择清单”页面时，嵌入页面额外显示一个居中的挂起按钮和一个偏右的关闭按钮，与周窗口自身顶部控件重复。
- 用户反馈从周界面打开的日程详情弹窗使用白底灰字，而主界面及其他日程详情使用青底白字，要求统一。

原因定位：

- 两个多余按钮来自 `ListPickerView._setup_window_controls()` 创建的 `btn_suspend` 和 `btn_close`；该页面嵌入 `WeekWindow.body_stack` 后仍保留了按独立窗口设计的控制按钮。
- `ScheduleDetailPop` 根据 `source_view in ["week", "month"]` 明确设置白色详情框和灰色文字，因此该差异不是数据内容、空详情或编辑状态造成，而是来源视图样式分支。

实际修改：

- `src/ui/week_window.py`
  - `WeekWindow` 创建 `page_list` 后隐藏其 `btn_suspend` 和 `btn_close`。
  - 保留周窗口自己的顶部挂起、同步和关闭按钮。
  - 保留清单页底部“新建 / 退出 / 确定”操作和清单选择逻辑。
- `src/ui/schedule_detail_pop.py`
  - 删除周/月来源专用的白底详情框分支。
  - 所有来源统一使用 `#11c1df` 青色背景、`rgba(255, 255, 255, 0.6)` 边框。
  - 有详情时统一使用 90% 白色文字，无详情占位文本使用 60% 白色文字。
  - 编辑完成后仍通过同一 `_get_desc_color()` 刷新，避免保存后重新出现灰字。

范围说明：

- 未修改清单数据、清单选择和回填逻辑。
- 未修改日程详情字段、保存逻辑或数据库。
- 未修改详情弹窗标题、底部信息、置顶和关闭行为。

验证记录：

- 使用 Codex bundled Python 执行 `python -m py_compile src/ui/week_window.py src/ui/schedule_detail_pop.py main.py`：通过。
- `git diff --check`：通过，仅有 Git 的 LF/CRLF 工作区提示。
- 静态检查确认周界面仅隐藏嵌入清单页的两个窗口控制按钮；详情框不再包含周/月来源专用配色分支。
- 真实界面仍需用户复测周界面“新增日程选清单”和“详情弹窗修改清单”两条入口，以及周/月来源详情弹窗的显示和编辑后样式。

后续视觉语义修正：

- 用户确认周界面下半部分为白色，周界面来源的详情弹窗使用白底灰字是有意保持视觉协调，并非需要统一删除的异常样式。
- 原实现确实按 `source_view in ["week", "month"]` 分叉；其中将月界面一并归入白底分支不再符合当前月窗口的全青色渐变结构。
- 调整为仅 `source_view == "week"` 使用白底灰字：有详情使用 `#666666`，无详情占位使用 `#999999`。
- 日界面、月界面、待办看板及其他来源继续使用青底白字。
- 编辑框和编辑完成后的显示继续调用 `_get_desc_color()`，因此周界面保存详情后仍保持白底灰字，不会切回青底白字。
- 修正后使用 Codex bundled Python 执行 `python -m py_compile src/ui/schedule_detail_pop.py main.py`：通过。
- 修正后 `git diff --check`：通过，仅有 Git 的 LF/CRLF 工作区提示。

---

## 2026-06-19 窗口边界试点与 WeekWindow 内侧轮廓

任务来源：

- 用户确认更多菜单层级 Bug 暂缓处理，先试验窗口与同色桌面 / 下层软件背景之间的边界区分效果。
- 目标是参考常规 Windows 应用，通过细边框和既有 DWM 阴影提高窗口轮廓辨识度。

开工前状态：

- `manage_instruction/Final_Formulation.md` 与 `manage_instruction/Work_Log.md` 已有本轮管理文档 diff。
- 开工前源码工作区干净；上述管理文档 diff 不属于本次边框源码试点。

第一版试点：

- 曾为 `apply_24h2_border_fix()` 增加可选系统默认 DWM 边框，并只在 `MainWindow` 启用。
- 用户本地复测未观察到可见效果；该方案依赖 Windows 对 frameless/translucent 窗口是否实际绘制默认边框，不能满足稳定区分需求。
- 第一版源码修改已完整回退：`src/utils/win_api.py` 和 `src/ui/main_window.py` 恢复原调用与原无边框行为。

第二版试点：

- 修改 `src/ui/week_window.py`，将重点转到白色内容区容易与白色背景混合的周界面。
- 初步新增覆盖全窗口的 `window_outline` 透明 `QFrame`，绘制 `1px solid rgba(0, 0, 0, 0.24)` 内侧轮廓。
- 用户本地复测发现该覆盖层造成阻断性回归：打开周界面更多菜单并点击别处关闭后，周界面无法再点击任何功能。
- 同时确认 DWM 外部阴影仍不可见，且 `rgba(0, 0, 0, 0.24)` 明显深于更多菜单边框。
- 已完整移除 `window_outline`、对应 `resizeEvent()` 处理及全窗口覆盖方案，不再依赖 `WA_TransparentForMouseEvents` 穿透。

第三版试点：

- 读取 `StyleManager.get_menu_style()`，确认更多菜单边框颜色为 `rgba(0, 0, 0, 0.1)`。
- 不新增覆盖控件，改为在周窗口已有 `top_container` 与 `content_area` 上分别绘制边框。
- 顶部区域绘制上、左、右三边；白色内容区绘制左、右、下三边，并保留原 `8px` 上下圆角组合。
- 编辑模式切换时同步保留 `content_area` 边框，避免进入添加 / picker 页面后边界消失。
- 本方案没有位于所有控件上方的额外 QWidget，不应再阻断菜单关闭后的点击事件。
- 继续保留 `qframelesswindow` / DWM 现有阴影链路，但本轮不再声称已实现可见外部阴影；若必须增加明显阴影，需要另行评估透明外边距容器，不能再使用覆盖层模拟。

边框推广：

- 用户确认周界面轮廓方向可继续推广，要求其他主要界面使用相同边框。
- `MainWindow`、`MonthWindow`、`TodoBoardWindow` 均已有自身 `paintEvent()` 和圆角背景路径，本轮直接在原填充路径后追加 `1px` 描边，不新增覆盖控件。
- 描边统一使用 `QColor(0, 0, 0, 26)`，等价于更多菜单的 `rgba(0, 0, 0, 0.1)`。
- `MainWindow` 覆盖日界面和主窗口内待办界面；`MonthWindow` 覆盖独立月窗口；`TodoBoardWindow` 覆盖带 10px 透明外边距的待办看板面板。
- 周界面继续使用顶部容器与白色内容容器的同色边框，不恢复全窗口覆盖层。

窗口置顶闪烁原因：

- `SharedMoreMenu.toggle_pin_mode()` 当前先关闭菜单，再调用 `parent_window.setWindowFlags(new_flags)`，随后调用 `show()` 并重新应用 DWM 修复。
- Qt 在 Windows 上变更顶级窗口 flags 时会销毁并重新创建 native HWND；窗口短暂从桌面合成树移除后重新加入，因此日程窗口本身会闪烁。
- 日程窗口短暂消失时，其背后的软件区域先暴露并触发 Windows DWM 重绘，随后又被重新显示的日程窗口覆盖，所以视觉上会感觉背后软件也闪了一次。
- 当前实现还使用 `QTimer` 延迟重建和重新打开菜单，使该过程更容易被肉眼观察到。
- 本轮只记录原因，不修改置顶逻辑。后续若处理，应优先使用 Windows `SetWindowPos(HWND_TOPMOST/HWND_NOTOPMOST, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)` 原地调整 z-order，避免通过 `setWindowFlags()` 重建 HWND；该方案属于 Windows 专用逻辑，需单独验收。

范围与风险：

- 本轮仍是单窗口视觉试点，不修改业务逻辑、数据库或更多菜单。
- 当前轮廓颜色与更多菜单保持一致；后续换肤阶段仍应抽取为主题 token，不能长期写死在 `WeekWindow`。
- 需要用户重点观察周窗口白色内容区右侧和底部，以及青色顶部区域的边框是否过深。
- 视觉确认前不推广到 `MonthWindow`、`MainWindow` 或 `TodoBoardWindow`。

验证记录：

- 第一版曾使用 Codex bundled Python 通过 `src/utils/win_api.py`、`src/ui/main_window.py`、`main.py` 的 `py_compile`；本地视觉验收未通过，因此已回退。
- 使用 Codex bundled Python 执行 `python -m py_compile src/ui/week_window.py main.py`：通过。
- `git diff --check`：通过，仅有 Git 的 LF/CRLF 工作区提示。
- 尝试复用项目 `.venv` 的 PyQt6 进行 offscreen 构造，但 bundled Python 为 3.12，而项目 PyQt6/SIP 二进制属于原 Python 3.11 环境，导入时报 `ModuleNotFoundError: No module named 'PyQt6.sip'`；本次无法完成构造级验证。
- 当前功能性源码 diff 仅为 `src/ui/week_window.py`；`src/utils/win_api.py` 仅残留文件末尾换行差异，不包含第一版 DWM 逻辑。
- 应用内轮廓的实际线条深浅仍以用户本地桌面背景目测为准。
- 第三版调整后再次执行 `python -m py_compile src/ui/week_window.py main.py`：通过。
- 第三版调整后 `git diff --check`：通过，仅有 Git 的 LF/CRLF 工作区提示。
- 静态检查确认 `window_outline`、`rgba(0, 0, 0, 0.24)` 和覆盖层 resize 逻辑均已移除；当前周窗口边框仅依附于既有顶部与内容容器。
- 菜单关闭后的点击恢复必须由用户在真实 Windows 窗口中复测；当前环境无法用 offscreen 验证 native popup 关闭后的鼠标抓取状态。
- 边框推广后使用 Codex bundled Python 执行 `python -m py_compile src/ui/main_window.py src/ui/week_window.py src/ui/month_window.py src/ui/todo_board.py main.py`：通过。
- 边框推广后 `git diff --check`：通过，仅有 Git 的 LF/CRLF 工作区提示。
- 静态检查确认四类主要窗口均使用与更多菜单一致的 10% 黑色轮廓；周界面仍无覆盖层残留。

---

## 2026-06-19 更多菜单层级 Bug 暂缓与窗口边界显示评估

任务来源：

- 用户确认更多菜单层级后移问题暂不继续修改，要求写入最终规划末尾的待修复 Bug。
- 用户反馈应用窗口与桌面或下层软件背景颜色接近时边界不明显，希望参考 Codex 使用轮廓线和阴影区分窗口。

规划记录：

- 已在 `manage_instruction/Final_Formulation.md` 新增“待修复 Bug”章节。
- 记录更多菜单层级后移只在日界面和待办界面确认复现，周界面和月界面当前未受影响。
- 记录两条真实复现路径、第一版 `WindowStaysOnTopHint + raise_()` 方案无效及已回退的事实。
- 记录后续优先使用应用失焦关闭 popup 链、复位 lock/timer/hover 状态的修复方向；本轮不实施。

窗口边界显示代码评估：

- `MainWindow`、`WeekWindow`、`MonthWindow` 均继承 `qframelesswindow.FramelessMainWindow`，使用 `FramelessWindowHint` 和 `WA_TranslucentBackground`。
- `qframelesswindow` 在 Windows 下已经调用 DWM shadow 接口；项目自己的 `apply_24h2_border_fix()` 同时将 DWM frame 扩展到全窗口，并通过 `DWMWA_BORDER_COLOR = DWMWA_COLOR_NONE` 明确关闭系统边框颜色。
- 当前可见内容贴满透明顶级窗口，Qt 内部没有为 `QGraphicsDropShadowEffect` 预留外侧 margin；直接给 central widget 加 Qt 阴影会被顶级窗口边界裁切。
- 最小可行方案是先恢复一个主题可控的 Windows DWM 1px 中性边框，并保留现有 DWM shadow；这最接近 Codex 的原生轮廓和阴影效果。
- `TodoBoardWindow` 是独立的 frameless `QWidget`，未调用当前 DWM helper；后续若做全局窗口边界统一，需要单独接入同一 helper，不能假定它会继承 `FramelessMainWindow` 的处理。
- 若 Windows DWM 阴影在目标系统仍不稳定，第二阶段才考虑“透明外层窗口 + 带 margin 的内层内容面板 + QGraphicsDropShadowEffect”；该方案更可控，但会改变窗口外框尺寸、命中区域和现有布局，风险高于 DWM 方案。

范围说明：

- 本轮仅修改 `manage_instruction/Final_Formulation.md` 与 `manage_instruction/Work_Log.md`。
- 未修改窗口源码、DWM helper、QSS、业务逻辑或数据库。

---

## 2026-06-19 更多菜单模式图标裁切修复与层级后移只读排查

任务来源：

- 用户反馈更多菜单中的“模式切换”和二级菜单“课表模式”图标底部被裁掉少量像素。
- 用户反馈打开更多菜单后偶发菜单掉到主窗口后方，仅窗口外侧部分可见，要求先检查原因，不修改该行为。

图标修复：

- 修改 `src/ui/components.py`。
- `model_switch.svg` 的路径最低点接近 viewBox 底边，`timetable.svg` 的路径直接到达 `1024` 底边；原实现将图标强制铺满 `18×18` QLabel，高 DPI 平滑采样时末端像素容易被裁切。
- 为公共菜单图标构造函数增加可选 `icon_inset`，仅对“模式切换”和“课表模式”设置 `1px` 内缩。
- 两个目标图标现在按 `16×16` 平滑缩放并在 `18×18` QLabel 中居中；卡片模式及其他菜单图标尺寸保持不变。
- 未修改 SVG 源文件。

菜单层级后移只读排查：

- 用户澄清图中异常不是父窗口位移，而是更多菜单被主窗口覆盖；仅菜单位于主窗口外侧的部分仍可见。
- `MainWindow` 默认带 `WindowStaysOnTopHint`，属于置顶顶级窗口。
- `SharedMoreMenu`、`mode_menu` 和 `help_menu` 均被设置为独立 native `Qt.Popup`，但窗口 flags 中没有同步 `WindowStaysOnTopHint`。
- `show_menu()` 只计算锚点、应用 DWM 边框修复并调用 `exec()`；没有显式同步父窗口 topmost 状态，也没有调用 `raise_()` 或设置原生 z-order。
- `apply_24h2_border_fix()` 只调整 DWM frame、圆角和边框颜色，不操作窗口位置或 z-order，不是直接原因。
- 在 Windows 的焦点或 native z-order 重新排序发生时，非 topmost popup 可能落到 topmost 主窗口之后；截图中菜单与主窗口重叠区域被遮挡、窗口外区域仍可见，与该风险一致。
- 当前最高概率原因是父窗口与 popup 的 topmost / owner 层级没有显式保持一致；具体触发时机可能与焦点切换、子菜单显示或 Windows 原生窗口重排有关，仍需复现并记录 HWND/z-order 才能完全确认。
- 用户建立提交回档点 `33a0bfe` 后尝试第一版层级修复：同步父窗口的 `WindowStaysOnTopHint`，并在 popup/exec 后调用 `raise_()`。
- 本地复测确认第一版方案无效；已完整回退该源码改动，`components.py` 恢复到提交 `33a0bfe` 的状态。
- 第一版失败说明问题并非“菜单首次显示时层级不足”，而是应用失去焦点后 popup 生命周期和层级状态发生变化。

验证记录：

- offscreen 图标检查：“模式切换”和“课表模式”pixmap 均为 `16×16`，居中放入 `18×18` QLabel，且关闭 `scaledContents`，保留四周 1px 空间。
- “卡片模式”图标继续沿用原缩放方式，确认本轮未扩大到其他菜单图标。
- `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/components.py main.py`：通过。
- `git diff --check`：通过，仅有 Git 的 LF/CRLF 工作区提示。
- diff 范围：仅 `src/ui/components.py` 与 `manage_instruction/Work_Log.md`。
- 第一版 flags 同步的 offscreen 验证曾通过，但 Windows 本地复测仍能触发层级后移，因此该验证不足以覆盖真实失焦场景。
- 用户确认的触发路径一：打开更多菜单后按 `Shift+Win+S`，应用失去激活状态，菜单随后落到主窗口后面。
- 用户确认的触发路径二：单击“模式切换”锁定并打开子菜单，随后点击其他应用输入框使本应用失焦；返回后再次点击“模式切换”可触发，且存在相近变体。
- 以上路径共同特征是：主菜单或锁定子菜单存活期间，应用发生 `ApplicationDeactivate/WindowDeactivate`，随后 popup 状态没有被完整清理。
- 源码回退确认：`src/ui/components.py` 的工作区 blob 与 `HEAD` blob 均为 `fd36382c733222b7ad279bc51ef88522c2a9df9b`；第一版 z-order 修复未残留任何源码差异。
- 回退后在 Codex 受限沙箱内尝试复跑 `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/components.py main.py` 未能启动；后续已确认原因是沙箱无法访问用户目录基础解释器，不是项目虚拟环境失效。源码与已提交且此前通过语法检查的 `HEAD` blob 完全一致。
- 回退后 `git diff --check`：通过，仅有管理日志的 LF/CRLF 工作区提示。
- 回退后 diff 范围：仅 `manage_instruction/Work_Log.md`；源码无 diff。

后续拟议方案（本轮未实施，等待用户确认）：

- 不再尝试通过 `WindowStaysOnTopHint` 或单次 `raise_()` 强行维持层级；第一版实测已证明这种处理只覆盖弹出瞬间，不能处理后续应用失焦导致的原生窗口重排。
- 在 `SharedMoreMenu` 生命周期内监听 `QApplication.applicationStateChanged` 或等价的 `ApplicationDeactivate` 事件。
- 应用失去激活时立即关闭主菜单、模式子菜单和帮助子菜单，停止两个 hover timer，清除 hover 状态，并将 `_mode_menu_locked` / `_help_menu_locked` 复位。
- 为 `mode_menu` / `help_menu` 的 `aboutToHide` 增加完整清理处理，避免子菜单独立关闭后仍残留锁定标记；当前连接只清除主菜单行的 hover 样式，没有复位 lock 和 timer。
- 首轮仍保留主菜单现有阻塞式 `exec()`，只修复失焦关闭和状态清理；若真实 Windows 复测仍失败，再单独评估将主菜单改为非阻塞 `popup()`，避免一次修改同时改变菜单调用模型。

---

## 2026-06-17 日界面详情框与月日期弹窗拖动小修

任务来源：

- 用户反馈日界面添加页详情输入框背景偏灰、白字辨识度受影响，希望与日程详情弹窗中的详情框背景风格对齐。
- 用户反馈月界面单击日期打开的持久弹窗不能拖动，希望改为可拖动。

实际修改：

- `src/ui/add_view.py`
  - 将 `AddScheduleView.txt_details` 背景从半透明黑色改为 `rgba(12, 192, 223, 0.9)`。
  - 将边框调整为 `rgba(255, 255, 255, 0.6)`，focus 时提高到 `rgba(255, 255, 255, 0.9)`。
  - 目的：对齐界面顶部主青色和 `schedule_detail_pop.py` 中主界面日程详情框的青色系背景，避免灰脏感，并为后续换肤抽取主题色留出一致入口。
- `src/ui/popups/month_day_panel.py`
  - 为 `MonthDayPanel` 增加左键拖动逻辑。
  - 新增 `_drag_offset` 状态。
  - 新增 `mousePressEvent` / `mouseMoveEvent` / `mouseReleaseEvent`。
  - 保持关闭按钮、标题色、白底圆角、外置 Tool 弹窗逻辑不变。

范围说明：

- 未修改周界面。
- 未修改月界面 hover 预览弹窗。
- 未修改月界面日期点击、双击跳转、panel 打开/关闭管理逻辑。
- 未修改数据库、服务层、主题文件或图标资源。

验证记录：

- `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/add_view.py src/ui/popups/month_day_panel.py main.py`：通过。
- offscreen 构造检查：`AddScheduleView` 可构造，`txt_details.styleSheet()` 包含 `rgba(12, 192, 223, 0.9)`；`MonthDayPanel` 可构造并包含拖动事件方法。
- offscreen 拖动事件模拟：左键 press/move/release 后 panel 从 `(100,100)` 移动到 `(130,140)`，`_drag_offset` 正常复位。
- diff 范围检查：仅 `src/ui/add_view.py`、`src/ui/popups/month_day_panel.py`、`manage_instruction/Work_Log.md` 有 diff。

---

## 2026-06-19 月界面左栏添加表单布局调整

任务来源：

- 用户反馈月界面左栏添加表单的控件纵向分配不均，详情框偏矮，取消/保存按钮距离左栏下沿过远。
- 用户要求添加表单不要替代或遮挡搜索框，而应显示在搜索框下方。

实际修改：

- `src/ui/month_window.py`
  - 将 `InlineAddViewMonth.input_desc` 固定高度从 `50px` 调整为 `75px`，即原高度的 3/2。
  - 月界面顶部添加按钮进入表单时，显式保持 `search_box` 显示。
  - 月界面日期右键菜单进入添加表单时，同样显式保持 `search_box` 显示。
  - 保持现有布局顺序不变：搜索框在上，`InlineAddViewMonth` 在下。
  - 初步将 `InlineAddViewMonth` 内部布局顶边距从 `0px` 调整为 `24px`，使标题输入框及其下方全部控件整体向下移动一个取消按钮高度。
  - 根据后续视觉反馈，将表单顶边距由 `24px` 收回到 `12px`，使标题输入框至状态摘要框整体上移半个取消按钮高度。
  - 同时将底部按钮行顶边距由 `0px` 调整为 `12px`，使取消/保存按钮位置基本保持不变，并扩大按钮与状态摘要框之间的间隔。
  - 再次根据实际间距测量，将表单顶边距由 `12px` 调整为 `0px`，使搜索框到标题输入框的距离与工具按钮组到搜索框的距离一致。
  - 将底部按钮行顶边距由 `12px` 同步增加到 `24px`，继续保持取消/保存按钮位置，并让标题至状态摘要框部分再上移 `12px`。
  - 根据图标本体小于按钮控件导致的视觉留白反馈，将表单顶边距由 `0px` 微调为 `3px`，并将按钮行顶边距由 `24px` 调整为 `21px`；中间控件整体下移 `3px`，按钮位置保持不变。
  - 上述边距仅属于添加表单本身；表单隐藏时不会影响时间、提醒、清单 picker 的位置。
  - 在时间、提醒、清单按钮之后新增字体按钮，复用 `assets/icons/theme.svg`，当前仅作为待接入 UI 入口，不写入表单状态。
  - 图标行移除尾部 stretch，四个 `22px` 图标按钮分别放入四个等宽布局单元并水平居中，使其按详情框宽度均匀排列。

范围说明：

- 未修改日界面或周界面的添加表单。
- 未修改时间、提醒、清单 picker 的业务和回填逻辑。
- 未修改保存字段、数据库、服务层或主题配置。

验证记录：

- `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/month_window.py main.py`：通过。
- offscreen 顶部添加入口检查：详情框高度为 `75px`；进入添加状态后搜索框与表单同时可见；关闭表单后搜索框仍正常显示。
- offscreen 调整前基线：标题输入框顶边为 `170`，状态摘要框底边为 `407`，取消按钮顶边为 `416`，状态框到按钮间距为 `8px`。
- offscreen 中间态复核：添加表单顶边距为 `12px`；标题输入框顶边为 `158`，状态摘要框底边为 `395`，两者均上移 `12px`；取消按钮顶边仍为 `416`，状态框到按钮间距扩大为 `20px`。
- offscreen第二次中间态复核：工具按钮组到搜索框间距为 `4px`，搜索框到标题输入框间距也为 `4px`；标题输入框顶边为 `146`，取消按钮顶边仍为 `416`，状态框到按钮间距扩大为 `32px`。
- offscreen 最终布局复核：视觉微调后搜索框到标题输入框间距为 `7px`，标题输入框顶边为 `149`；取消按钮顶边仍为 `416`，状态框到按钮间距为 `29px`。
- offscreen 图标行复核：详情框宽度为 `136px`；时间、提醒、清单、字体四个按钮均为 `22px`，中心点分别为 `14 / 49 / 84 / 119`，相邻中心间距均为 `35px`。
- offscreen 右键添加入口检查：搜索框与表单同时可见，布局顺序保持为搜索框在上、添加表单在下。
- 首次右键入口几何断言命令无输出并以非零状态退出；改用无断言即时输出复核后通过，未发现代码或布局异常。
- diff 范围检查：仅本轮月表单、更多菜单、周/月菜单调用点、节日图标和管理文档有 diff。

规划同步：

- 更新 `manage_instruction/Final_Formulation.md`。
- 在云功能之前新增“完成字体功能”阶段，原云功能顺延。
- 记录添加 / 编辑入口的“当前单条 / 同类型全部 / 全部”三种应用范围。
- 记录更多菜单入口的“当前页面对应类型 / 全部”两种应用范围。
- 明确单条字体可能涉及数据迁移；同类型和全局字体应优先保存为显示偏好，不应逐条批量改写历史记录。

更多菜单与规划调整：

- 新增用户提供的 `assets/icons/festival.svg`。
- `SharedMoreMenu` 删除“显示周数”，将“显示农历”替换为“显示节日”。
- `SharedMoreMenu` 新增 `show_festival_option` 显式参数；仅周界面、月界面及其挂起窗口传入 `True`。
- 在“待办显示”下方新增“修改字体”入口壳，复用 `theme.svg` 并运行时染为 `#333333`；当前仅记录点击，不实现字体业务。
- 移除“模式切换”和“使用帮助”之间的分隔线，使两个同类二级菜单入口连续排列；其他功能分组线保持不变。
- `Final_Formulation.md` 在字体功能前新增“完成节假日显示”，原字体功能和云功能顺延。

验证记录：

- `py_compile`：`components.py`、`month_window.py`、`week_window.py`、周/月挂起窗口与 `main.py` 均通过。
- offscreen 菜单检查：默认菜单不包含“显示节日”；启用 `show_festival_option=True` 的菜单包含“显示节日”；所有菜单均不再包含“显示周数”或“显示农历”。
- offscreen 菜单顺序检查：“待办显示”之后是“修改字体”，其后为“导出日程”。
- offscreen 二级菜单分组检查：“模式切换”和“使用帮助”在 action 顺序中直接相邻，中间无分隔线。
- 图标检查：`festival.svg` 的 checkbox icon 非空；`theme.svg` 运行时染色后的字体图标非空。
- 首次菜单验证因 Windows GBK 控制台无法打印二级菜单箭头 `›` 而退出；去除该字符输出后同一逻辑验证通过，不是组件错误。
- 月添加表单最终几何检查：标题输入框顶边 `149`、取消按钮顶边 `416`、状态框到按钮间距 `29px`；四个图标按钮等距关系保持不变。
- `git diff --check` 初次发现 `suspend_window_week.py` 文件末尾旧空格因补齐 EOF 换行进入 diff；已只清理该空格行，未格式化其他代码。
- 清理后 `git diff --check` 通过，仅有 Git 的 LF/CRLF 工作区提示。
- 最终源码范围：`components.py`、`month_window.py`、`week_window.py`、`suspend_window_month.py`、`suspend_window_week.py`；资源范围新增 `festival.svg`；文档范围为 `Final_Formulation.md` 与 `Work_Log.md`。

---

## 2026-06-23 月界面时间选择启用开始时间开关缩小

任务来源：

- 用户反馈月界面添加功能的设置时间界面中，“启用开始时间”右侧开关仍偏大。
- 用户要求开关等比例缩到原本约 `1/4` 的视觉面积，右侧仍与日期显示框、日历右沿处于同一垂直线，并且开关与“启用开始时间”文本的几何中心保持同一水平线。

开工前状态：

- `git status --short --branch` 显示当前分支 `main...temp/main [ahead 96]`。
- 开工前已有非本轮未提交改动：`manage_instruction/Final_Formulation.md`、`src/ui/dashboard.py`、`src/ui/main_window.py`、`src/ui/schedule_detail_pop.py`、`src/ui/todo.py`、`src/ui/todo_board.py`、`src/ui/week_window.py`、`src/utils/win_api.py`。
- `src/ui/month_window.py` 开工前未显示为 dirty，本轮新增该文件改动。

实际修改：

- `src/ui/month_window.py`
  - 仅调整月界面专用 `MonthCompactSwitch`，不修改共享 `IOSSwitch`。
  - 将月界面时间 picker 的开关尺寸由 `38x24` 调整为 `19x12`，按宽高各缩小一半处理，即视觉面积约为原来的 `1/4`。
  - 将圆角半径同步由 `12` 调整为 `6`。
  - 将滑块直径由 `18` 调整为 `9`，内边距由 `3` 调整为 `1.5`。
  - 绘制滑块时改用 `QRectF`，避免小尺寸下整数取整导致圆点偏移。
  - 将“启用开始时间”整行包进 `136px` 固定宽度容器，使开关右侧与日期显示框、日历右沿保持同一垂直线。
  - 保持文本、stretch、开关的横向结构，使文本和开关几何中心位于同一水平线。
  - 不改变日/周时间选择器，也不改变月界面时间选择业务逻辑。

验证记录：

- `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/month_window.py main.py`：通过。
- offscreen 构造与开关几何检查：`MonthTimePickerView` 可构造；`MonthCompactSwitch` 尺寸为 `19x12`；滑块直径/内边距为 `9.0 / 1.5`；“启用开始时间”文本中心 `y=199`，开关中心 `y=199`；日期框右沿与开关右沿差值为 `0`；开关行容器宽度为 `136px`。
- diff 范围检查：当前工作区仍包含开工前已有的 `manage_instruction/Final_Formulation.md`、`src/ui/dashboard.py`、`src/ui/main_window.py`、`src/ui/schedule_detail_pop.py`、`src/ui/todo.py`、`src/ui/todo_board.py`、`src/ui/week_window.py`、`src/utils/win_api.py` 未提交改动；本轮新增 `src/ui/month_window.py` 和 `manage_instruction/Work_Log.md` 改动。

---

## 2026-06-23 月界面清单选择页右上关闭键补回

任务来源：

- 用户确认月界面设置时间页右上角 `X` 虽然最初属于未去除的小插曲，但实际比底部取消键更方便。
- 用户要求月界面添加功能的设置清单页，在与设置时间页相同位置补回右上角 `X`，底部取消键保留。

实际修改：

- `src/ui/month_window.py`
  - 仅修改月界面专用 `MonthListPickerView`。
  - 将此前隐藏的 `btn_close` 重新显示，并设置为 `24x24`、`12x12` 图标尺寸，位置沿用清单页原本的右上角窗口控制布局。
  - 将标题栏右侧留白改为 `30px`，避免“选择清单/修改清单”标题与右上角关闭键重叠。
  - 断开 `ListPickerView` 默认的 `window().close()` 行为，改为发出 `back_requested`，使右上角 `X` 与月界面清单页底部“取消”语义一致，只返回添加表单，不关闭月窗口。
  - 未修改日界面、周界面或共享 `ListPickerView`。

验证记录：

- `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/month_window.py main.py`：通过。
- offscreen 构造与按钮行为检查：`MonthListPickerView` 可构造；`btn_close.isVisible()` 为 `True`；按钮尺寸为 `24x24`，图标尺寸为 `12x12`；标题栏右侧 margin 为 `30px`；点击 `btn_close` 后收到一次 `back_requested`。
- diff 范围检查：当前工作区仍包含开工前已有的 `manage_instruction/Final_Formulation.md`、`src/ui/dashboard.py`、`src/ui/main_window.py`、`src/ui/schedule_detail_pop.py`、`src/ui/todo.py`、`src/ui/todo_board.py`、`src/ui/week_window.py`、`src/utils/win_api.py` 未提交改动；本轮实际修改仍集中在 `src/ui/month_window.py` 与 `manage_instruction/Work_Log.md`。

---

## 2026-06-23 月界面提醒选择页紧凑化

任务来源：

- 用户要求月界面添加功能的“设置提醒”页面按前面“设置时间”页面作为样板调整。
- 重点要求：标题文字大小与位置对齐“设置时间”；底部“取消/确定”按钮大小和位置对齐“设置时间”；提醒时间选择框外型参考设置时间页里的时间选择框。
- 明确不影响日界面、周界面或共享提醒选择页。

开工前状态：

- `git status --short --branch` 显示当前分支 `main...temp/main [ahead 98]`。
- 开工前工作区干净；本轮新增 `src/ui/month_window.py` 与 `manage_instruction/Work_Log.md` 改动。

实际修改：

- `src/ui/month_window.py`
  - 新增月界面专用 `MonthAlarmPickerView(AlarmPickerView)`，保留共享 `AlarmPickerView` 不变。
  - 月界面 `self.page_alarm` 从共享 `AlarmPickerView` 切换为 `MonthAlarmPickerView`。
  - 标题栏压缩到 `28px` 高度，标题文本按 `12px` 白色粗体显示“设置提醒/修改提醒”，右上关闭按钮保留 `24x24`、`12x12` 图标尺寸。
  - 提醒时间滚轮容器调整为 `136x80`，背景、圆角和滚轮字体参考月界面设置时间页的紧凑视觉。
  - 将“设置为前一天”和“强提醒”开关替换为月界面专用 `MonthCompactSwitch`，尺寸为 `19x12`，不修改共享 `IOSSwitch`。
  - 快捷提醒按钮与强提醒时长按钮统一压缩为 `20px` 高，使用更小圆角和字体。
  - 底部“取消/确定”按钮统一为 `24px` 高、横向均分，样式与月界面设置时间页一致。
  - 不修改日界面、周界面提醒选择器，也不修改提醒保存逻辑。

验证记录：

- `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/month_window.py main.py`：通过。
- offscreen 构造检查：`MonthAlarmPickerView` 可构造；标题文本断言为“设置提醒”；提醒时间容器为 `136x80`；取消/确定按钮高度均为 `24px`；两个紧凑开关均为 `19x12`；快捷按钮高度集合为 `[20]`。
- `MonthWindow` offscreen 构造检查：`page_alarm` 实际实例为 `MonthAlarmPickerView`；提醒时间容器宽度为 `136px`；确定按钮高度为 `24px`。

---

## 2026-06-23 月界面三个添加子页右上关闭键统一

任务来源：

- 用户反馈月界面添加功能中的设置时间、设置提醒、设置清单三个子页右上角 `X` 大小和位置不一致。
- 用户要求以设置清单页的 `X` 大小和位置为基准统一。

开工前状态：

- `git status --short --branch` 显示当前分支 `main...temp/main [ahead 98]`。
- 开工前已有上一小步未提交改动：`src/ui/month_window.py` 与 `manage_instruction/Work_Log.md`。
- 本轮继续在同两个文件上做窄范围补充。

实际修改：

- `src/ui/month_window.py`
  - 在月界面专用 `MonthTimePickerView` 中补齐关闭键配置：显示 `btn_close`、按钮尺寸 `24x24`、图标尺寸 `12x12`，并 `raise_()` 到上层。
  - 在月界面专用 `MonthAlarmPickerView` 中补齐 `btn_close.show()` 与 `raise_()`。
  - 保持 `MonthListPickerView` 作为基准不变。
  - 三个子页继续共用 `28px` 标题栏高度和右侧 `30px` 留白。
  - 不修改日界面、周界面或共享 picker 类。

验证记录：

- `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/month_window.py main.py`：通过。
- offscreen 构造对比：`MonthListPickerView`、`MonthTimePickerView`、`MonthAlarmPickerView` 的关闭键均为 `24x24`，图标均为 `12x12`，在 `200px` 宽测试窗口中位置均为 `(170, 0)`，且均可见。

---

## 2026-06-23 calendar 图标小写路径与时间选择按钮配色

任务来源：

- 用户确认下载的新日历图标文件名为小写 `calendar.svg`，要求项目引用也统一使用小写路径。
- 用户要求月界面添加功能的设置时间页日期按钮内的 `calendar.svg` 图标显示为白色。
- 用户要求主界面/共享时间选择页的日期按钮颜色与月界面设置时间页一致，包括背景框、文字和图标颜色。

实际修改：

- `assets/icons/Calendar.svg` 通过 Git 大小写改名记录为 `assets/icons/calendar.svg`，并保留用户替换后的新图标内容。
- `src/ui/common/action_context_menu.py`
  - 将右键菜单日视图/月视图 fallback 图标路径从 `Calendar.svg` 改为 `calendar.svg`。
- `src/ui/time_picker.py`
  - 将日期按钮图标改为运行时白色染色的 `calendar.svg`。
  - 将日期按钮背景改为 `rgba(255, 255, 255, 0.18)`、边框改为 `rgba(255, 255, 255, 0.2)`、文字改为白色，hover 改为 `rgba(255, 255, 255, 0.28)`。
- `src/ui/month_window.py`
  - 月界面专用 `MonthTimePickerView` 中显式将日期按钮图标染为白色，避免新 `calendar.svg` 默认黑色直接显示。

说明：

- 物理文件已是小写 `calendar.svg`；Windows 下 Git 对大小写改名会以 `D assets/icons/Calendar.svg` 与 `A assets/icons/calendar.svg` 显示，提交后仓库路径即统一为小写。
- 图标本体不强行写死白色，按钮使用时运行时染色，便于后续继续替换图标或接入换肤。

---

## 2026-06-24 Final_Formulation 进度状态同步

任务来源：

- 用户要求重新阅读 `Final_Formulation.md`，判断当前项目进度是否需要更新。

实际修改：

- `manage_instruction/Final_Formulation.md`
  - 将当前状态从“暂无活动阶段”更新为“近期处于月界面 UI 细调、更多菜单壳完善和局部视觉小修阶段，尚未启动新的大型功能阶段”。
  - 在“当前完成状态”中补充更多菜单与显示入口小修：
    - 使用帮助入口和使用手册 / 帮助助手二级菜单壳。
    - 模式切换入口和卡片模式 / 课表模式二级菜单壳。
    - 修改字体入口壳。
    - 移除显示周数，显示节日仅保留在周 / 月相关窗口。
  - 在“当前完成状态”中补充月界面 UI 细调小修：
    - 持久日期弹窗拖动和主题色标题。
    - 左侧添加表单紧凑化。
    - 月界面专用清单 / 时间 / 提醒 picker 紧凑化。
    - 三个添加子页右上角关闭键统一。
    - `calendar.svg` 小写路径和白色日期按钮图标。
  - 更新 `Month View` 技术债：标记“已完成一轮紧凑化，但仍需整体视觉适配和截图级验收”。
  - 更新后续建议第 1 项为“继续修整月界面的功能 UI”，避免后续重复规划已完成的 picker 紧凑化。

验证记录：

- 本轮只修改管理文档，不修改源码。

---

## 2026-06-24 MP-0：现状审查与路由边界定位

任务来源：

- 按 `manage_instruction/Work_Task_Prompts.md` 当前待执行提示词执行 `MP-0`。
- 本轮只做静态审查、代码阅读、搜索、import 验证和日志记录，不修改 `src/`。

开工前 git 状态：

- `git status --short --branch`：`## main...temp/main [ahead 101]`
- 开工前已有 diff：`manage_instruction/Work_Task_Prompts.md`
- 本轮将该脏状态视为开工前既有管理文档改动，不计为本轮源码问题。

实际修改文件：

- `manage_instruction/Work_Log.md`

读取的规划/历史文件：

- `manage_instruction/Final_Formulation.md`
- `manage_instruction/Work_Instruction.md`
- `manage_instruction/Work_Log.md`
- `manage_instruction/Work_Task_Prompts.md`
- `manage_instruction/ReconstructionDolder/Work_Formulation.md`
- `manage_instruction/ReconstructionDolder/History_Instruction.md`

确认的架构原则：

- 新功能优先兼容式旁路，不一次性替换旧 UI 流程。
- 新公共 UI 组件优先进入 `src/ui/common/` 或 `src/ui/utils/`。
- 路由、添加来源、详情弹窗回流优先复用既有入口，不应把大段新流程硬塞进 `MainWindow` / `WeekWindow` / `MonthWindow`。
- 复杂 popup 生命周期、picker 回流、跨视图刷新必须先做边界审查，再拆分小工单。
- 未确认低风险闭环前，不应直接改 `ScheduleDetailPop`、详情回流链路或多窗口同步逻辑。

本轮读取/搜索的代码文件：

- `src/ui/popups/month_day_panel.py`
- `src/ui/schedule_detail_pop.py`
- `src/ui/main_window.py`
- `src/ui/month_window.py`
- `src/ui/dashboard.py`
- `src/ui/week_window.py`
- `src/ui/todo.py`
- `src/ui/todo_board.py`

静态搜索命令与结果摘要：

- `rg -n "MonthDayPanel|open_day_panels|_open_day_panel|_find_open_day_panel|_remove_day_panel|close_day_panels|hideEvent|closeEvent|_on_calendar_date_clicked|_on_calendar_date_activated|date_selected.emit|view_selected.emit|context_menu_date|_handle_context_view" src/ui/month_window.py src/ui/popups/month_day_panel.py`
  - 命中 `MonthWindow` 的日期点击/双击、面板查找、打开、移除、统一关闭、右键目标日期保存和 `hideEvent/closeEvent` 清理路径。
- `rg -n "class ScheduleDetailPop|source_view|pyqtSignal|req_|emit|closeEvent|delete|status|time|alarm|list|refresh|ScheduleDetailPop\(" src/ui/schedule_detail_pop.py src/ui/dashboard.py src/ui/week_window.py src/ui/todo.py src/ui/todo_board.py src/ui/main_window.py`
  - 命中 `ScheduleDetailPop` 的 4 个对外信号、`source_view` 分支、双击编辑发射点，以及 Dashboard / Todo / Week / TodoBoard 的详情弹窗入口。
- `rg -n "_resolve_detail_edit_target|current_view|switch_view|go_to_time_picker_for_edit|go_to_alarm_picker_for_edit|go_to_list_picker_for_edit|req_edit_time|req_edit_alarm|req_edit_list|source_view|page_dashboard|week_window|month_window|todo_board" src/ui/main_window.py src/ui/schedule_detail_pop.py src/ui/dashboard.py src/ui/week_window.py src/ui/month_window.py src/ui/todo.py src/ui/todo_board.py src/controllers`
  - 命中 `MainWindow._resolve_detail_edit_target(...)`、MainWindow 对 week/month/todo_board 的 picker 分发，以及 Dashboard/Todo 的 source_view 转发。
- `rg -n "go_to_time_picker_for_edit|go_to_alarm_picker_for_edit|go_to_list_picker_for_edit|editing_schedule|update_schedule_with_repeat|on_time_confirmed|on_alarm_confirmed|on_list_confirmed|page_time|page_alarm|page_list" src/ui/month_window.py`
  - 命中 `MonthWindow` 的三条 edit picker 路径、`editing_schedule` 和 `update_schedule_with_repeat(...)` 写回链路。
- `rg -n "_refresh_schedule_marker_cache|_build_schedule_marker_cache|_build_hover_schedule_cache|refresh_data|refresh|req_refresh|req_refresh_all|global_signals|schedule_updated|schedule_deleted|_on_schedule_saved|on_time_confirmed|on_alarm_confirmed|on_list_confirmed" src/ui/main_window.py src/ui/month_window.py src/ui/dashboard.py src/ui/week_window.py src/ui/todo.py src/ui/todo_board.py src/utils/signals.py src/controllers`
  - 命中第六轮后的 `RefreshCoordinator` 接入点、`req_refresh_all` 旧链路、`schedule_updated` 旧链路，以及 `MonthWindow.schedule_updated` / `WeekWindow.schedule_updated` 回流。

MonthDayPanel 生命周期与月界面日期弹层结论：

- `MonthDayPanel` 是独立 `QWidget(Qt.Tool | FramelessWindowHint)`，只持有：
  - `panel_date`
  - 文本展示数据
  - `closed = pyqtSignal(object)`
- `MonthWindow` 持有 `self.open_day_panels`，通过：
  - `_find_open_day_panel(qdate)` 查重
  - `_open_day_panel(qdate)` 创建/显示
  - `_remove_day_panel(panel)` 从列表移除
  - `close_day_panels()` 统一关闭
- `_on_calendar_date_clicked(qdate)`：
  - 只刷新 marker / hover 状态；
  - 若该日期面板已开则关闭；否则打开日弹层。
- `_on_calendar_date_activated(qdate)`：
  - 关闭全部 day panel；
  - `date_selected.emit(qdate)` 给主窗口做“跳日视图”。
- 右键菜单路径 `_handle_context_view('day')` 也会先 `close_day_panels()`，再 `date_selected.emit(target_date)`。
- `MonthWindow.hideEvent(...)` 与 `closeEvent(...)` 都会执行：
  - `close_day_panels()`
  - `_hide_hover_preview()`
- 这意味着当前真实行为是：月视图一旦 `hide()`，所有 `MonthDayPanel` 都会被关掉。
- 因此若后续需求是“视图切换时不关闭 day panel”，会直接与现有 `hideEvent/closeEvent` 清理策略冲突；这应单独拆到后续 popup 生命周期工单，而不应和右键菜单/跳转逻辑混改。

ScheduleDetailPop 信号、source_view 与职责边界：

- `ScheduleDetailPop` 当前对外信号：
  - `schedule_updated = pyqtSignal()`
  - `req_edit_time = pyqtSignal(object)`
  - `req_edit_alarm = pyqtSignal(object)`
  - `req_edit_list = pyqtSignal(object)`
  - `popup_closed = pyqtSignal(object)`
- `source_view` 当前语义不是路由器，而是 popup 自身 UI/行为分支输入：
  - `week`：详情区背景、边框、文字颜色特殊处理。
  - `todo_board`：顶部额外显示便签来源图标。
  - 其余默认按 dashboard 风格处理。
- popup 内部实际双击编辑发射点：
  - 双击时间 -> `req_edit_time.emit(self.data)`
  - 双击提醒 -> `req_edit_alarm.emit(self.data)`
  - 双击清单 -> `req_edit_list.emit(self.data)`
- popup 内部直接写库路径仍存在，且每次成功后 `schedule_updated.emit()`：
  - 标题编辑 `_finish_edit_title()`
  - 详情编辑 `_finish_edit_desc()`
  - 优先级编辑 `_finish_edit_priority()`
  - 重复规则编辑 `_finish_edit_repeat()`
- `closeEvent(...)` 只负责 `popup_closed.emit(self)`，不负责跨视图刷新。

详情弹窗打开来源地图：

- `DashboardView._show_detail_popup(schedule_data, source_view='dashboard')`
  - 创建 `ScheduleDetailPop(schedule_data, source_view=source_view)`。
  - `schedule_updated -> refresh_data + req_refresh_all.emit()`。
  - `req_edit_time/alarm/list` 通过 lambda 连带 `source_view` 向上转发。
- `TodoView._show_detail_popup(schedule_data, source_view='todo')`
  - 创建 `ScheduleDetailPop(..., source_view='todo')`。
  - `schedule_updated -> refresh_data + req_refresh_all.emit()`。
  - 仅 `req_edit_list` 向上转发，时间/提醒不在 TodoView 承接。
- `WeekWindow.request_schedule_detail.emit(schedule_obj)`
  - 在 `MainWindow.__init__` 中被接成 `lambda data: self.page_dashboard._show_detail_popup(data, source_view='week')`。
  - 即 Week 来源详情弹窗仍借道 Dashboard popup 机制。
- `TodoBoardWindow._show_detail_popup(schedule_data)`
  - 直接调用 `main_win.page_dashboard._show_detail_popup(schedule_data, source_view='todo_board')`。
  - 弹窗位置再被强制挪到 TodoBoard 右侧。

MainWindow 动态路由与 `_resolve_detail_edit_target(...)` 结论：

- `_resolve_detail_edit_target(source_view='dashboard')` 不是单纯按 source_view 决策，而是优先按当前可见窗口决策：
  - `week_window.isVisible()` -> `week`
  - `month_window.isVisible()` -> `month`
  - `source_view == 'todo_board'` 且 `todo_board.isVisible()` -> `todo_board`
  - `body_stack.currentWidget() == page_todo` -> `todo`
  - `self.isVisible()` -> `day`
  - 否则回退到 `source_view` 或 `day`
- 结论：该方法当前是“按当前可见宿主窗口承接详情编辑”的动态路由，不是“严格按详情来源视图回流”。
- 这能兼容 week/month/todo_board 借道 dashboard 打开 popup 的现状，但也意味着：
  - popup 的 `source_view` 仍是 UI 来源标识；
  - 真正 picker 承接窗口由 `MainWindow` 运行时可见性决定。
- 因此后续若要改详情编辑回流，不应先动 `ScheduleDetailPop`，而应先明确 `MainWindow` 是否继续保留这层动态决策。

MonthWindow 是否具备 edit picker 承接能力：

- 已具备三条独立 edit picker 路径：
  - `go_to_time_picker_for_edit(schedule_data)`
  - `go_to_alarm_picker_for_edit(schedule_data)`
  - `go_to_list_picker_for_edit(schedule_data)`
- 已持有 `self.editing_schedule` 和三种 mode：
  - `time_picker_mode`
  - `alarm_picker_mode`
  - `list_picker_mode`
- 三条确认路径均支持：
  - `db_manager.update_schedule_with_repeat(...)`
  - `if not update_future: schedule.group_id = None`
  - `_complete_schedule_edit(schedule)`
  - `schedule_updated.emit(schedule)`
- `_complete_schedule_edit(schedule)` 只做：
  - `_refresh_schedule_marker_cache()`
  - `schedule_updated.emit(schedule)`
- 结论：MonthWindow 现在已经是“可独立承接详情编辑 picker + 本地写回 + 向 MainWindow 回流刷新”的完整闭环，不再只是 add-only 页面。

保存与刷新回流链路结论：

- Dashboard：
  - 详情弹窗 `schedule_updated` -> `DashboardView.refresh_data()` + `req_refresh_all.emit()`。
- Todo：
  - 详情弹窗 `schedule_updated` -> `TodoView.refresh_data()` + `req_refresh_all.emit()`。
- Week：
  - picker/edit 成功后 `refresh_week_data()` + `schedule_updated.emit(schedule or None)`。
  - `MainWindow._on_week_schedule_updated(...)` 当前只直接 `page_dashboard.refresh_data()`，再局部刷新 dashboard open_popups；没有走第六轮三连刷新协调。
- Month：
  - picker/edit 成功后 `_refresh_schedule_marker_cache()` + `schedule_updated.emit(schedule)`。
  - `MainWindow` 复用同一个 `_on_week_schedule_updated(...)` 处理 `month_window.schedule_updated`。
  - 该路径同样只直刷 dashboard，不会自动刷新 todo 或 week。
- MainWindow 自身 add/edit 页：
  - `on_schedule_saved()`、`on_time_confirmed(edit)`、`on_alarm_confirmed(edit)`、`on_list_confirmed(edit)` 已切到 `_refresh_dashboard_todo_week()`，即第六轮协调边界。
- TodoBoard：
  - `notify_main_window_refresh()` 仍直接：`page_todo.refresh_data()` + `page_dashboard.req_refresh_all.emit()`。
  - 仍未接入第六轮 `RefreshCoordinator`。
- 结论：当前“add/edit 主链路”与“详情弹窗/board 借道链路”存在两套并行刷新体系；MP-0 只记录现状，不建议在同一工单里合并。

主风险点与边界判断：

- `MonthDayPanel` 生命周期与“视图切走是否保留面板”冲突：中高风险，必须单拆 popup 生命周期工单。
- `ScheduleDetailPop` 既管显示，又直接写库，又发编辑请求，又依赖 `source_view` 分支：高风险，不适合在 MP-1 直接改。
- `MainWindow._resolve_detail_edit_target(...)` 当前承担跨宿主动态路由：中风险；若后续要改，建议先做只读基线再拆最小接管。
- `WeekWindow -> MainWindow lambda -> Dashboard popup` 与 `TodoBoard -> page_dashboard._show_detail_popup(...)` 都是直接耦合点：高风险，应保留旁路兼容策略。
- `MonthWindow` 已有 edit picker 承接能力，说明月视图详情编辑回流更适合“复用现有承接窗口”，不适合新造一套 popup 编辑逻辑。

对后续 MP-1 ~ MP-5 的建议：

- `MP-1`：建议只做 `MonthDayPanel` / 月视图 day panel 生命周期与显示规则基线，不改详情弹窗。
- `MP-2`：建议只处理 `MonthWindow` 到 `MainWindow` 的“跳日视图 / 视图切换 / 右键目标日期”边界，不碰 popup 编辑回流。
- `MP-3`：若要动详情弹窗，建议先只做 `source_view` / 编辑承接路由基线，不直接改 `ScheduleDetailPop` 写库逻辑。
- `MP-4`：若要补月视图详情编辑闭环，优先复用 `MonthWindow.go_to_*_picker_for_edit(...)` 和 `schedule_updated` 现有路径，不要新造 picker 页面。
- `MP-5`：刷新统一建议最后做，只在前述 popup / picker / 路由边界稳定后，评估是否把 month/detail/todo_board 回流接到第六轮协调层。
- 建议继续拆分 `MP-1 / MP-2 / MP-3 / MP-4 / MP-5`；当前边界仍然过大，不建议合并执行。

import 验证结果：

- `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.month_window import MonthWindow; from src.ui.popups.month_day_panel import MonthDayPanel; from src.ui.schedule_detail_pop import ScheduleDetailPop; from src.ui.main_window import MainWindow; print('mp0 imports ok', MonthWindow, MonthDayPanel, ScheduleDetailPop, MainWindow)"`
- 结果：通过，输出 `mp0 imports ok ...`。

diff 范围检查结果：

- `git diff --name-only -- src`：无输出。
- `git diff --name-only -- assets`：无输出。
- `git diff --name-only -- main.py`：无输出。
- `git diff --name-only -- requirements.txt`：无输出。
- `git diff --name-only -- schedule.db`：无输出。
- `git diff --check`：通过，仅有 Git 的 LF/CRLF 工作区提示，无 whitespace error。
- `git diff --name-only`：仅 `manage_instruction/Work_Task_Prompts.md`（开工前既有）与本轮新增的 `manage_instruction/Work_Log.md`。
- `git status --short --branch`：主分支 `ahead 101`；脏文件为 `manage_instruction/Work_Log.md`、`manage_instruction/Work_Task_Prompts.md`。

未完成事项：

- 本轮只完成 MP-0 基线审查，未开始 MP-1 及后续执行。
- 未对 MonthDayPanel 生命周期、详情弹窗回流、MainWindow 动态编辑路由做任何源码调整。

风险或疑点：

- `MainWindow._on_week_schedule_updated(...)` 同时承接 week 与 month 的 `schedule_updated`，但当前仅直刷 dashboard；这与第六轮三连刷新边界并不一致，后续若补修需要单独验收。
- `TodoBoardWindow` 仍直接借用 `page_dashboard._show_detail_popup(...)`；若未来要清理该耦合，应单独开工单，避免和月视图改造串联。
- `MonthWindow.hideEvent(...)` 当前无条件 `close_day_panels()`；若后续产品要求“切视图保留弹层”，将不是小修级改动。

---

## 2026-06-24 MP-1：月日程弹窗青色渐变 UI 与列表承载

任务来源：

- 按 `manage_instruction/Work_Task_Prompts.md` 当前待执行提示词执行 `MP-1`。
- 本轮只改造 `MonthDayPanel` 自身 UI 和只读列表承载，不接 `ScheduleDetailPop`，不改跨视图编辑路由，不改 popup 生命周期规则。

开工前 git 状态：

- `git status --short --branch`：`## main...temp/main [ahead 102]`
- `git diff --name-only`：`manage_instruction/Work_Task_Prompts.md`
- 存在开工前 diff：`manage_instruction/Work_Task_Prompts.md`
- 该 diff 视为开工前既有管理文档改动，不计为本轮源码问题。

实际修改文件：

- `src/ui/popups/month_day_panel.py`
- `manage_instruction/Work_Log.md`

基线确认：

- 本轮只执行 MP-1，不执行 MP-2 ~ MP-5。
- `MP-0` 已记录 panel 生命周期与详情/路由边界。
- `MonthDayPanel` 原本已接收 `qdate, schedules`，本轮保持该入口不变。
- 本轮不触碰 `ScheduleDetailPop`。
- 本轮不处理“普通视图切换时 panel 保留”的生命周期问题，该问题继续留给 MP-3。

MonthDayPanel UI 改造说明：

- 保持 `class MonthDayPanel(QWidget)` 不变。
- 保持 `Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint` 不变。
- 保持 `WA_ShowWithoutActivating` 与 `WA_TranslucentBackground` 不变。
- `paintEvent(...)` 改为青色渐变圆角浮窗：
  - 顶部到底部渐变：`#0cc0df -> #71dce8`
  - 半透明白色边框
  - 圆角半径 `12px`
- 顶部 header 仍保留：
  - 日期标题
  - 关闭按钮
- 中部从单一 `body_label` 升级为只读列表承载：
  - `QScrollArea`
  - 透明内容容器
  - 多个日程 item `QFrame`
- 底部新增摘要文本，用于显示 `共 N 条` 或 `... 共 N 条`。
- `setFixedWidth(320)`，避免内容把 panel 撑成异常宽度。
- 未引入外部依赖，未读写 QSS 文件，未新增资源。

日程项展示字段说明：

- 时间：
  - 优先 `start_time.strftime('%H:%M')`
  - 否则 `end_time.strftime('%H:%M')`
  - 都没有则 `--:--`
- 标题：
  - `schedule.title`
  - 空标题回退为 `未命名日程`
- 重要性：
  - `priority == 2` -> `高`
  - `priority == 1` -> `中`
  - 其他 -> `低`
- 状态：
  - `status == 1` -> `已完成`
  - 其他 -> `未完成`
- 展示顺序保持传入 `schedules` 的原顺序。
- panel 内不重新查数据库。

空状态与数量限制说明：

- 无日程时显示 `当日暂无日程`。
- 多日程时最多渲染前 `8` 条。
- 超过 `8` 条时显示 `... 共 N 条`。
- 未改 `MonthWindow` 的过滤、排序和缓存构建规则。

兼容性保持说明：

- 保持 `closed = pyqtSignal(object)`。
- 保持 `closeEvent(...)` 中只 emit 一次 `closed`。
- 保持 `btn_close.clicked.connect(self.close)`。
- 保持左键拖动能力：
  - `mousePressEvent(...)`
  - `mouseMoveEvent(...)`
  - `mouseReleaseEvent(...)`
- 保持 `panel_date` 更新逻辑。
- 保持 `set_panel_data(qdate, schedules)` 作为唯一对外刷新入口。
- 未接 `ScheduleDetailPop`。
- 未新增详情请求信号。
- 未改编辑路由。
- 未改 popup 生命周期规则。
- `src/ui/month_window.py` 最终无需修改。

验证命令与结果：

- 静态定位：
  - `rg -n "class MonthDayPanel|closed|set_panel_data|paintEvent|closeEvent|mousePressEvent|mouseMoveEvent|mouseReleaseEvent|btn_close|panel_date" src/ui/popups/month_day_panel.py`
  - 结果：`closed`、`set_panel_data(...)`、拖动事件、`paintEvent(...)`、`btn_close` 均仍存在。
- 禁止依赖检查：
  - `rg -n "ScheduleDetailPop|db_manager|MainWindow|mouseDoubleClickEvent|doubleClicked|detail_requested" src/ui/popups/month_day_panel.py`
  - 结果：无输出；未引入 `ScheduleDetailPop`、`db_manager` 或 `MainWindow`。
- MonthWindow 生命周期定位：
  - `rg -n "close_day_panels|_remove_day_panel|_find_open_day_panel|hideEvent|closeEvent|_open_day_panel" src/ui/month_window.py`
  - 结果：生命周期方法仍在 `MonthWindow` 内，且本轮未改其语义。
- import 验证：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.popups.month_day_panel import MonthDayPanel; from src.ui.month_window import MonthWindow; print('mp1 imports ok', MonthDayPanel, MonthWindow)"`
  - 结果：通过。
- offscreen 构造与空状态验证：
  - `MonthDayPanel(QDate.currentDate(), [])` 可构造。
  - `panel_date` 可更新。
  - `closed` 与 `set_panel_data` 属性存在。
  - 结果：通过，输出 `empty state ok`。
- offscreen 日程列表展示验证：
  - 使用 `SimpleNamespace` 假对象构造两条日程。
  - `set_panel_data(q, schedules)` 可成功承载列表数据。
  - 结果：通过，输出 `panel list smoke ok`。
- 生命周期 smoke：
  - `closed` 信号连接后 `show() -> close()`。
  - 结果：通过，`closed hits 1`，且命中对象为同一 panel。
- 月界面复用链路 smoke：
  - `MonthWindow._open_day_panel(q)` 连续两次同日期调用。
  - 结果：通过，`count1 == 1`、`count2 == 1`；`close_day_panels()` 后 `open_day_panels == []`。
- `py_compile`：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/popups/month_day_panel.py src/ui/month_window.py main.py`
  - 结果：通过。

diff 范围检查结果：

- 禁止范围检查：
  - `src/ui/schedule_detail_pop.py` 无 diff
  - `src/ui/main_window.py` 无 diff
  - `src/ui/dashboard.py` 无 diff
  - `src/ui/week_window.py` 无 diff
  - `src/ui/todo.py` 无 diff
  - `src/ui/todo_board.py` 无 diff
  - `src/controllers` 无 diff
  - `src/data` 无 diff
  - `src/repositories` 无 diff
  - `src/services` 无 diff
  - `src/theme` 无 diff
  - `src/utils/signals.py` 无 diff
  - `src/utils/styles.py` 无 diff
  - `assets` 无 diff
  - `main.py` 无 diff
  - `requirements.txt` 无 diff
  - `schedule.db` 无 diff
- `git diff --check`：通过，仅有 Git 的 LF/CRLF 工作区提示，无 whitespace error。
- `git diff --name-only` 预期范围：
  - `src/ui/popups/month_day_panel.py`
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有）

未完成事项：

- 本轮未接 `ScheduleDetailPop`。
- 本轮未给月日程项增加双击详情行为。
- 本轮未处理普通视图切换时 panel 保留规则。
- 本轮未统一详情保存后的多视图刷新。

风险或疑点：

- 当前 `MonthDayPanel` 仍只负责展示，不负责详情打开；这与 MP-1 目标一致，但 MP-2 接入详情时需要单独设计 item 信号和子 popup 生命周期。
- `MonthWindow.hideEvent(...)` 仍会 `close_day_panels()`；本轮明确不改，MP-3 若处理跨视图保留，必须单独验收。
- 当前列表承载使用 `QScrollArea`，如果后续 MP-2 需要在 item 上接更多交互，建议继续保持 panel 只做 UI 容器，不向其中塞入主窗口业务路由。

---

## 2026-06-24：MonthDayPanel 紧凑化 UI 返修

任务背景：

- 用户反馈 MP-1 后的月界面单击日期弹窗视觉过重，白底卡片感强，像“小广告贴”。
- 日程项单条占用高度过大，不符合“辅助对比弹窗，可同时打开多个”的定位。
- 本次为直接 UI 返修，不进入三窗口流程。

实际修改文件：

- `src/ui/popups/month_day_panel.py`
- `manage_instruction/Work_Log.md`

修改内容：

- 将 `MonthDayPanel` 固定宽度调整为 `280px`，降低弹窗占用。
- 保持弹窗本体青色渐变背景和白色标题，不回退到白底样式。
- 将日程项从多行大卡片改为单行紧凑行：
  - 左侧显示时间。
  - 中间显示标题。
  - 右侧显示 `重要性/完成状态`。
- 单条日程行高度调整为 `30px`，列表项间距调整为 `4px`。
- 日程项背景改为轻量半透明白，弱化卡片边界。
- 使用 `QFrame#monthDayPanelItem` 精确限定日程项样式，避免 `QLabel` 继承 `QFrame` 后被错误套上背景框。
- `QScrollArea` 保持透明背景，并保留细滚动条以承载多日程。
- 未修改 `MonthWindow` 生命周期逻辑。
- 未接入 `ScheduleDetailPop`。
- 未修改详情编辑路由。
- 未修改数据库、服务层、控制层或主题文件。

验证结果：

- offscreen 空状态构造验证：通过。
- offscreen 两条日程列表构造验证：通过，输出宽度 `280`，列表高度 `66`。
- offscreen `closed` 信号验证：通过，`closed hits 1`。
- `py_compile src/ui/popups/month_day_panel.py src/ui/month_window.py main.py`：通过。

范围检查：

- 本次源码 diff 仅涉及 `src/ui/popups/month_day_panel.py`。
- `src/ui/month_window.py` 无本次 diff。
- `src/ui/schedule_detail_pop.py` 无 diff。
- `src/ui/main_window.py` 无 diff。
- `assets`、`main.py`、`requirements.txt`、`schedule.db` 无 diff。

未完成事项：

- 本次只做紧凑化视觉返修，未做日程项双击打开详情弹窗。
- 真实视觉效果仍需用户在桌面环境中运行确认。

风险或疑点：

- 单行标题在极长文本下会被裁切；这是为紧凑化弹窗刻意保留的取舍。
- 后续 MP-2 接入双击详情时，需要继续保持 `MonthDayPanel` 只负责展示和轻量信号，不直接承接主窗口路由。

---

## 2026-06-25 MP-2：月日程弹窗日程项双击打开共享详情弹窗

任务来源：

- 按 `manage_instruction/Work_Task_Prompts.md` 当前待执行提示词执行 `MP-2`。
- 本轮只增加“月日程弹窗内日程项双击请求详情”与“主窗口统一打开共享 `ScheduleDetailPop`”的最小链路。
- 本轮不改跨视图编辑路由，不改普通视图切换时 panel 保留/关闭规则。

开工前 git 状态：

- `git status --short --branch`：`## main...temp/main [ahead 103]`
- `git diff --name-only`：`manage_instruction/Work_Task_Prompts.md`
- 存在开工前 diff：`manage_instruction/Work_Task_Prompts.md`
- 该 diff 属于开工前既有管理文档改动，不计为本轮源码问题。

实际修改文件：

- `src/ui/popups/month_day_panel.py`
- `src/ui/month_window.py`
- `src/ui/main_window.py`
- `manage_instruction/Work_Log.md`

基线确认：

- 本轮只执行 `MP-2`，不执行 `MP-3 / MP-4 / MP-5`。
- `MonthDayPanel` 基线为：只负责展示、关闭信号和拖动。
- `MainWindow` 已存在 `_resolve_detail_edit_target(...)`，本轮未重写。
- 当前共享详情弹窗仍为 `ScheduleDetailPop`。
- `DashboardView._show_detail_popup(...)` 仍不返回 popup，本轮未复用它作为月 panel 详情入口。

MonthDayPanel 新增信号/双击入口说明：

- 新增信号：`schedule_double_clicked = pyqtSignal(object, object)`
  - 第一个参数：schedule 对象。
  - 第二个参数：当前 `MonthDayPanel` 实例。
- 新增内部轻量 item 类：`_MonthScheduleItemFrame(QFrame)`。
  - 每个 item 保存 `self.schedule`。
  - 左键双击时发出 `double_clicked(schedule)`。
- `MonthDayPanel` 内新增 `_emit_schedule_double_clicked(schedule)`：
  - 统一发出 `self.schedule_double_clicked.emit(schedule, self)`。
- 保持：
  - `set_panel_data(qdate, schedules)` 对外入口不变。
  - 列表展示顺序不变。
  - panel 内不查数据库。
  - 不导入 `MainWindow` / `db_manager` / Repository / Service。

MonthDayPanel 子详情弹窗生命周期管理说明：

- 新增：`self.child_detail_popups = []`。
- 新增：`register_child_detail_popup(popup)`。
  - 只登记由当前 panel 打开的详情弹窗。
  - 重复登记会被跳过。
  - 登记前先 `_prune_child_detail_popups()` 清理失效引用。
- 新增：
  - `_handle_child_popup_closed(popup)`
  - `_unregister_child_detail_popup(popup)`
  - `_prune_child_detail_popups()`
  - `_close_child_detail_popups()`
- 生命周期规则：
  - 若 popup 带 `popup_closed` 信号，则关闭时自动从 `child_detail_popups` 移除。
  - 同时连接 `destroyed` 做兜底移除。
  - panel `closeEvent(...)` 中先关闭自己登记的子详情弹窗，再按旧语义只 emit 一次 `closed`。
- 本轮只保证“panel 手动关闭时关闭其子详情弹窗”。
- 本轮不处理普通视图切换导致的 panel / 子详情保留问题；仍留给 `MP-3`。

同 `owner_panel + schedule.id` 的重复详情弹窗复用策略：

- 复用范围限定为同一个 `owner_panel`。
- `MainWindow.open_schedule_detail_from_month_panel(...)` 会先遍历：
  - `owner_panel.child_detail_popups`
- 若找到 `popup.data.id == schedule.id` 的现有 popup：
  - `show()`
  - `raise_()`
  - `activateWindow()`
  - 直接复用，不再创建新 popup。
- 不会把 Dashboard / Week / Todo 已打开的 popup 注册到 `owner_panel`。
- 新建成功后会：
  - `owner_panel.register_child_detail_popup(popup)`
  - `popup.owner_panel = owner_panel`

MonthWindow 转发信号说明：

- 在 `MonthWindow` 类上新增：
  - `schedule_detail_requested = pyqtSignal(object, object)`
- 在 `_open_day_panel(qdate)` 中创建 panel 后新增连接：
  - `panel.schedule_double_clicked.connect(self.schedule_detail_requested.emit)`
- `MonthWindow` 仍不直接创建 `ScheduleDetailPop`。
- `MonthWindow` 仍不直接调用 `MainWindow` 方法。
- 未改变 `_open_day_panel(...)` 的定位和同日复用逻辑。

MainWindow 详情打开桥接说明：

- `MainWindow.__init__` 中新增连接：
  - `self.month_window.schedule_detail_requested.connect(self.open_schedule_detail_from_month_panel)`
- 新增方法：
  - `open_schedule_detail_from_month_panel(self, schedule_data, owner_panel=None)`
- 该桥接方法职责：
  - 在 `MainWindow` 内创建 / 复用共享 `ScheduleDetailPop`。
  - `source_view='month'`。
  - 连接现有编辑入口：
    - `go_to_time_picker_for_edit(data, 'month')`
    - `go_to_alarm_picker_for_edit(data, 'month')`
    - `go_to_list_picker_for_edit(data, 'month')`
  - 若存在 `owner_panel`，则把 popup 注册回该 panel，并将 popup 定位到 panel 右侧。
- 本轮未重写 `_resolve_detail_edit_target(...)`。
- 本轮未扩展“保存后多视图刷新”策略。

范围与边界确认：

- 未复用 `DashboardView._show_detail_popup(...)`。
- 未修改 `src/ui/dashboard.py`。
- 未修改 `_resolve_detail_edit_target(...)`。
- 未修改 `MonthWindow.hideEvent(...) / closeEvent(...) / close_day_panels(...)`。
- 未修改 Dashboard / Week / Todo 既有详情打开链路。
- 未修改 `src/ui/schedule_detail_pop.py`。

静态依赖检查结果：

- `rg -n "MainWindow|db_manager|Repository|Service|ScheduleRepository|CategoryRepository|switch_view|_resolve_detail_edit_target" src/ui/popups/month_day_panel.py`
  - 结果：无输出。
  - 结论：`month_day_panel.py` 未引入主窗口、数据库或路由耦合。
- `rg -n "db_manager|Repository|ScheduleRepository|CategoryRepository" src/ui/popups/month_day_panel.py src/ui/month_window.py`
  - 结果：命中仅来自 `month_window.py` 的既有 `db_manager` 读写逻辑，不是本轮新增依赖。
  - `month_day_panel.py` 无数据库依赖。
- `rg -n "_show_detail_popup" src/ui/month_window.py src/ui/popups/month_day_panel.py`
  - 结果：无输出。
  - 结论：本轮未让 `MonthWindow` / `MonthDayPanel` 直接调用 `_show_detail_popup(...)`。

验证命令与结果：

- 静态定位：
  - `rg -n "schedule_double_clicked|register_child_detail_popup|child_detail_popups|_emit_schedule_double_clicked|mouseDoubleClickEvent|closed|set_panel_data" src/ui/popups/month_day_panel.py`
  - `rg -n "schedule_detail_requested|schedule_double_clicked|_open_day_panel|close_day_panels|hideEvent|closeEvent" src/ui/month_window.py`
  - `rg -n "open_schedule_detail_from_month_panel|schedule_detail_requested|ScheduleDetailPop|_resolve_detail_edit_target|go_to_time_picker_for_edit|go_to_alarm_picker_for_edit|go_to_list_picker_for_edit|_show_detail_popup" src/ui/main_window.py`
  - 结果：新增信号、桥接入口和 month 转发链路均可定位。
- import 验证：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.popups.month_day_panel import MonthDayPanel; from src.ui.month_window import MonthWindow; from src.ui.main_window import MainWindow; from src.ui.schedule_detail_pop import ScheduleDetailPop; print('mp2 imports ok', MonthDayPanel, MonthWindow, MainWindow, ScheduleDetailPop)"`
  - 结果：通过。
- MonthDayPanel 双击信号 offscreen 验证：
  - 使用 `SimpleNamespace(id=123, title='mp2 sample', priority=1, status=0)`。
  - 通过 `p._emit_schedule_double_clicked(schedule)` 触发。
  - 结果：通过，`hits == [(schedule, p)]`。
- 子详情弹窗生命周期 offscreen 验证：
  - 使用假 `QWidget` 作为 child popup。
  - `register_child_detail_popup(child)` 后 `child in p.child_detail_popups` 成立。
  - `p.close()` 后 `child_detail_popups` 被清空。
  - `destroyed` 信号在该 offscreen 场景下未稳定触发，`destroy hits == 0`。
  - 本轮以“列表清理 + `close()` 调用不报错”为主判定通过。
- MonthWindow 转发信号 offscreen 验证：
  - `MonthWindow._open_day_panel(q)` 后拿到 `panel`。
  - `panel._emit_schedule_double_clicked(schedule)` 后，`w.schedule_detail_requested` 收到 `(schedule, panel)`。
  - 结果：通过。
- MainWindow 桥接静态验证：
  - `assert hasattr(MainWindow, 'open_schedule_detail_from_month_panel')`
  - `assert hasattr(MainWindow, '_resolve_detail_edit_target')`
  - 结果：通过，输出 `main bridge exists`。
- MainWindow offscreen bridge smoke：
  - `MainWindow()` 可构造。
  - `w.month_window` 上存在 `schedule_detail_requested`。
  - 结果：通过，输出 `main window bridge smoke ok`。
- 同 owner panel 重复打开复用验证：
  - 使用补足字段的 `SimpleNamespace`：
    - `id/title/description/start_time/end_time/priority/status/item_type/category_id/is_alarm/alarm_duration/reminder_time/repeat_rule/created_at`
  - 连续两次调用 `w.open_schedule_detail_from_month_panel(schedule, panel)`。
  - 结果：通过，`same owner popup count == 1`。
  - 顾问窗口复核补充：原提示词示例命令中 `created_at=None` 不符合当前 `ScheduleDetailPop.refresh_created_display()` 对 `created_at.strftime(...)` 的要求，因此该合成假对象命令会失败。
  - 复核改用 `created_at=datetime.now()` 的等价真实字段假对象与数据库真实日程各跑一次，均通过 `same owner popup count == 1` / `real schedule popup count == 1`。
- `py_compile`：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/popups/month_day_panel.py src/ui/month_window.py src/ui/main_window.py src/ui/schedule_detail_pop.py main.py`
  - 结果：通过。

diff 范围检查结果：

- 禁止范围检查：
  - `src/ui/dashboard.py` 无 diff
  - `src/ui/week_window.py` 无 diff
  - `src/ui/todo.py` 无 diff
  - `src/ui/todo_board.py` 无 diff
  - `src/controllers` 无 diff
  - `src/data` 无 diff
  - `src/repositories` 无 diff
  - `src/services` 无 diff
  - `src/theme` 无 diff
  - `src/utils/signals.py` 无 diff
  - `src/utils/styles.py` 无 diff
  - `assets` 无 diff
  - `main.py` 无 diff
  - `requirements.txt` 无 diff
  - `schedule.db` 无 diff
- `git diff --check`：通过，仅有 Git 的 LF/CRLF 工作区提示，无 whitespace error。
- `git diff --name-only`：
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
  - `src/ui/main_window.py`
  - `src/ui/month_window.py`
  - `src/ui/popups/month_day_panel.py`
  - `manage_instruction/Work_Log.md`
- `git status --short --branch`：
  - `## main...temp/main [ahead 103]`
  - `M manage_instruction/Work_Task_Prompts.md`
  - `M src/ui/main_window.py`
  - `M src/ui/month_window.py`
  - `M src/ui/popups/month_day_panel.py`
  - `M manage_instruction/Work_Log.md`

未完成事项：

- 本轮未处理普通视图切换时 panel / 子详情保留规则。
- 本轮未重构详情编辑路由。
- 本轮未统一保存后的多视图刷新策略。
- 本轮未让 month 详情链路接入 `DashboardView` 既有 popup 管理体系。

风险或疑点：

- 当前 month 详情 popup 由 `MainWindow` 直接创建，但未纳入 `page_dashboard.open_popups`；这符合本轮“不要复用 dashboard 详情入口”的收窄要求，但意味着 MP-5 如需统一刷新，仍需单独处理。
- `register_child_detail_popup(...)` 对真实 `ScheduleDetailPop` 依赖 `popup_closed` 做关闭后移除；对普通 `QWidget` 只能依赖 `close()` 后的显式列表清空或销毁信号兜底，因此 offscreen 假对象只验证到“关闭不报错 + 列表清理”。
- 复用验证若使用合成 schedule 对象，`created_at` 必须使用可 `strftime(...)` 的 `datetime` 值；`created_at=None` 是测试数据不严谨，不代表 MP-2 主链路失败。
- `month_window.py` 本身已有大量 `db_manager` 依赖；本轮新增逻辑未扩大这部分耦合，但静态依赖命令会命中既有代码，需要在复核时按“既有依赖”理解，而不是本轮新增问题。

---

## 2026-06-25 MP-3：月日程弹窗生命周期与跨视图保留规则

任务来源：

- 按 `manage_instruction/Work_Task_Prompts.md` 当前待执行提示词执行 `MP-3`。
- 本轮只处理月日程持久 panel 及其子详情弹窗的生命周期规则，不改编辑路由，不改详情内容，不改保存刷新策略。

开工前 git 状态：

- `git status --short --branch`：`## main...temp/main [ahead 104]`
- `git diff --name-only`：`manage_instruction/Work_Task_Prompts.md`
- 开工前已有 diff：`manage_instruction/Work_Task_Prompts.md`
- 结论：当前看不到 MP-2 未提交源码 diff；本轮按“MP-2 已提交，仅 `Work_Task_Prompts.md` 存在开工前既有管理文档 diff”处理。

实际修改文件：

- `src/ui/month_window.py`
- `manage_instruction/Work_Log.md`

基线确认：

- 本轮只执行 `MP-3`，不执行 `MP-4 / MP-5`。
- `MonthWindow.hideEvent(...)` 基线中仍调用 `close_day_panels()`。
- `MonthWindow.closeEvent(...)` 基线中仍调用 `close_day_panels()`。
- `MonthWindow.close_day_panels()` 仍负责显式关闭全部 panel。
- `MonthDayPanel.closeEvent(...)` 基线中仍调用 `_close_child_detail_popups()`，可在 panel 手动关闭时关闭子详情。
- `MonthDayPanel.register_child_detail_popup(...)` 仍存在。
- 显式调用 `close_day_panels()` 的路径包括：
  - `_on_calendar_date_activated(...)`
  - `_handle_context_view('day')`
  - `go_to_time_picker(...)`
  - `go_to_alarm_picker(...)`
  - `go_to_list_picker(...)`
  - `_show_edit_picker(...)`

MonthWindow.hideEvent(...) 调整说明：

- 本轮唯一源码行为改动：
  - `MonthWindow.hideEvent(...)` 不再调用 `self.close_day_panels()`。
  - 保留 `self._hide_hover_preview()`。
  - 保留 `super().hideEvent(event)`。
- 目标：仅修正“普通 `hide()` 被 `MainWindow.switch_view(...)` 触发时误清理 panel”的问题。

MonthWindow.closeEvent(...) / close_day_panels(...) 保持说明：

- `MonthWindow.closeEvent(...)` 仍调用 `close_day_panels()`。
- `close_day_panels()` 方法仍存在，仍负责显式关闭全部 panel。
- 本轮未改变以下显式清理路径：
  - 双击月格跳日 `_on_calendar_date_activated(...)`
  - 右键菜单跳日 `_handle_context_view('day')`
  - 进入月界面 picker：`go_to_time_picker(...)` / `go_to_alarm_picker(...)` / `go_to_list_picker(...)`
  - 进入月界面 edit picker：`_show_edit_picker(...)`
- 结论：本轮只修正普通 `hide()` 误清理，不扩大到显式清理路径。

panel / 子详情弹窗生命周期结论：

- panel 手动关闭：仍关闭它登记的子详情弹窗。
- 子详情弹窗手动关闭：不关闭父 panel。
- 子详情弹窗手动关闭后：仍会从父 panel 的 `child_detail_popups` 中移除。
- `MonthDayPanel` 本轮无需修改；既有生命周期实现已满足 MP-3 的 panel-child 关系要求。

验证命令与结果：

- 静态定位：
  - `rg -n "def hideEvent|def closeEvent|close_day_panels|_on_calendar_date_activated|_handle_context_view|go_to_time_picker|go_to_alarm_picker|go_to_list_picker|_show_edit_picker" src/ui/month_window.py`
  - `rg -n "register_child_detail_popup|child_detail_popups|_close_child_detail_popups|closeEvent|popup_closed|schedule_double_clicked" src/ui/popups/month_day_panel.py`
  - `rg -n "popup_closed|closeEvent" src/ui/schedule_detail_pop.py`
  - 结果：
    - `hideEvent(...)` 已不再调用 `close_day_panels()`。
    - `closeEvent(...)` 仍调用 `close_day_panels()`。
    - 显式调用 `close_day_panels()` 的路径仍可定位。
    - `MonthDayPanel.closeEvent(...)` 仍关闭子详情弹窗。
    - `MonthDayPanel.register_child_detail_popup(...)` 仍存在。
- import 验证：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.month_window import MonthWindow; from src.ui.popups.month_day_panel import MonthDayPanel; from src.ui.schedule_detail_pop import ScheduleDetailPop; print('mp3 imports ok', MonthWindow, MonthDayPanel, ScheduleDetailPop)"`
  - 结果：通过。
- 普通 hide 不清理 panel 验证：
  - `MonthWindow.show()` 后 `_open_day_panel(q)`，随后 `w.hide()`。
  - 结果：通过，`panel count after hide 1`。
- closeEvent 仍清理 panel 验证：
  - `_open_day_panel(q)` 后 `w.close()`。
  - 结果：通过，`panel count after close 0`。
- 显式 `close_day_panels()` 仍清理验证：
  - `_open_day_panel(q)` 后调用 `w.close_day_panels()`。
  - 结果：通过，`panel count after explicit close 0`。
- panel 手动关闭仍关闭子详情验证：
  - 使用假 `QWidget` child popup。
  - `p.register_child_detail_popup(child)` 后 `p.close()`。
  - 结果：通过，`child count after panel close 0`。
- 子详情手动关闭不关闭父 panel 验证：
  - 原提示词给出的单行 `python -c` 内联 `class` 写法在 Windows shell 下出现 `SyntaxError`，属于命令转义问题，不是代码问题。
  - 之后改用 `exec(...)` 方式在同一 `python -c` 中定义 `FakeDetailPopup` 复跑。
  - 结果：通过，输出：
    - `panel visible True`
    - `child count 0`
  - 另有 `DeprecationWarning: sipPyTypeDict()`，不影响本轮逻辑验收。
- 双击跳日显式清理保持验证：
  - `_open_day_panel(q)` 后调用 `_on_calendar_date_activated(q)`。
  - 结果：通过，`panel count after activated 0`，`date hits 1`。
- 进入月界面 picker 显式清理保持验证：
  - `_open_day_panel(q)` 后调用 `go_to_time_picker(start, end)`。
  - 结果：通过，`panel count after picker 0`。
- `py_compile`：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/month_window.py src/ui/popups/month_day_panel.py src/ui/schedule_detail_pop.py main.py`
  - 结果：通过。

diff 范围检查结果：

- `git diff --name-only -- src/ui/main_window.py`：无输出。
- `git diff --name-only -- src/ui/dashboard.py`：无输出。
- `git diff --name-only -- src/ui/week_window.py`：无输出。
- `git diff --name-only -- src/ui/todo.py`：无输出。
- `git diff --name-only -- src/ui/todo_board.py`：无输出。
- `git diff --name-only -- src/controllers`：无输出。
- `git diff --name-only -- src/data`：无输出。
- `git diff --name-only -- src/repositories`：无输出。
- `git diff --name-only -- src/services`：无输出。
- `git diff --name-only -- src/theme`：无输出。
- `git diff --name-only -- src/utils/signals.py`：无输出。
- `git diff --name-only -- src/utils/styles.py`：无输出。
- `git diff --name-only -- assets`：无输出。
- `git diff --name-only -- main.py`：无输出。
- `git diff --name-only -- requirements.txt`：无输出。
- `git diff --name-only -- schedule.db`：无输出。
- `git diff --check`：通过，仅有 Git 的 LF/CRLF 工作区提示，无 whitespace error。
- `git diff --name-only`：
  - `manage_instruction/Work_Task_Prompts.md`（开工前既有）
  - `src/ui/month_window.py`
  - `manage_instruction/Work_Log.md`
- `git status --short --branch`：
  - `## main...temp/main [ahead 104]`
  - `M manage_instruction/Work_Task_Prompts.md`
  - `M src/ui/month_window.py`
  - `M manage_instruction/Work_Log.md`

未完成事项：

- 本轮未处理详情编辑路由；继续留给 `MP-4`。
- 本轮未处理保存后多视图刷新策略；继续留给 `MP-5`。
- 本轮未改变双击跳日/右键跳日/进入 picker 时的显式清理产品规则。

风险或疑点：

- 目前“普通视图切换保留 panel”与“显式跳日 / picker 清理 panel”已经在代码路径上区分开：前者依赖 `hideEvent(...)`，后者依赖显式 `close_day_panels()`；本轮未发现需要暂停的规则冲突。
- 子详情手动关闭验证在 Windows 单行 `python -c` 下需要绕开 shell 对内联 `class` 的限制；复核时应按“验证方式调整”理解，而不是代码缺陷。
- `manage_instruction/Work_Task_Prompts.md` 仍为开工前既有 diff，不属于 MP-3 本轮新增修改。

---

## 2026-06-25 MP-4：详情编辑请求按当前可见视图路由

任务来源：

- 按 `manage_instruction/Work_Task_Prompts.md` 当前待执行提示词执行 `MP-4`。
- 本轮先做现有动态路由验证；只有发现明确缺口时才允许最小修正源码。

开工前 git 状态：

- `git status --short --branch`：`## main...temp/main [ahead 105]`
- `git diff --name-only`：`manage_instruction/Work_Task_Prompts.md`
- 开工前已有 diff：`manage_instruction/Work_Task_Prompts.md`
- 结论：开工前无 `src/` 相关 diff，本轮不回退、不清理该既有管理文档 diff。

实际修改文件：

- `manage_instruction/Work_Log.md`

是否修改源码：

- 未修改源码。
- 结论：`MP-4` 无需源码修正，现有 `_resolve_detail_edit_target(...)` 已满足当前动态路由要求。

`ScheduleDetailPop` 信号边界检查结果：

- `ScheduleDetailPop` 仍只发：
  - `req_edit_time`
  - `req_edit_alarm`
  - `req_edit_list`
- `ScheduleDetailPop` 未直接调用 `MainWindow`、`MonthWindow`、`WeekWindow`、`DashboardView`、`TodoView`、`TodoBoardWindow`。
- `source_view` 当前仍用于弹窗内部样式/展示分支，但不是详情编辑请求信号的直接业务调用入口。

`MainWindow._resolve_detail_edit_target(...)` 判断顺序检查结果：

- 当前顺序为：
  1. `week_window.isVisible()` -> `week`
  2. `month_window.isVisible()` -> `month`
  3. `source_view == "todo_board"` 且 `todo_board.isVisible()` -> `todo_board`
  4. `body_stack.currentWidget() == page_todo` -> `todo`
  5. `MainWindow.isVisible()` -> `day`
  6. 最后才以 `source_view` 作为 fallback
- 结论：当前可见视图优先级已经覆盖固定 `source_view`，满足 MP-4 的核心要求。

time / alarm / list 三类编辑请求静态检查结果：

- `MainWindow.go_to_time_picker_for_edit(...)` 调用 `_resolve_detail_edit_target(...)`。
- `MainWindow.go_to_alarm_picker_for_edit(...)` 调用 `_resolve_detail_edit_target(...)`。
- `MainWindow.go_to_list_picker_for_edit(...)` 调用 `_resolve_detail_edit_target(...)`。
- `MonthWindow` 仍有：
  - `go_to_time_picker_for_edit(...)`
  - `go_to_alarm_picker_for_edit(...)`
  - `go_to_list_picker_for_edit(...)`
- `WeekWindow` 仍有：
  - `go_to_time_picker_for_edit(...)`
  - `go_to_alarm_picker_for_edit(...)`
  - `go_to_list_picker_for_edit(...)`
- `TodoBoardWindow` 仍保留既有 `go_to_list_picker_for_edit(...)` 入口，仅作现状记录，本轮未扩展。

月 panel 详情桥接检查结果：

- `MainWindow.open_schedule_detail_from_month_panel(...)` 仍创建：
  - `ScheduleDetailPop(schedule_data, source_view="month")`
- 并将编辑信号连接为：
  - `go_to_time_picker_for_edit(data, "month")`
  - `go_to_alarm_picker_for_edit(data, "month")`
  - `go_to_list_picker_for_edit(data, "month")`
- 结论：虽然桥接时固定传入 `source_view="month"`，但因为 `MainWindow.go_to_*_picker_for_edit(...)` 内部统一调用 `_resolve_detail_edit_target(...)`，该固定值不会锁死动态路由。

day / week / month / todo / todo_board 路由验证结果：

- `_resolve_detail_edit_target(...)` offscreen 验证输出：
  - `day`
  - `month`
  - `week`
  - `todo`
- 说明：
  - 主窗口可见且默认日视图时，`source_view="month"` 仍解析到 `day`
  - `month_window` 可见时解析到 `month`
  - `week_window` 可见时解析到 `week`
  - `page_todo` 当前可见时解析到 `todo`
- `time` 编辑请求 smoke：通过
  - `month_window` 可见时命中 `month`
  - `week_window` 可见时命中 `week`
  - 主窗口日视图可见时进入主窗口 `edit` 链路
- `alarm` 编辑请求 smoke：通过
  - `month_window` 可见时命中 `month`
  - `week_window` 可见时命中 `week`
  - 主窗口日视图可见时进入主窗口 `edit` 链路
- `list` 编辑请求 smoke：通过
  - `month_window` 可见时命中 `month`
  - `week_window` 可见时命中 `week`
  - `page_todo` 当前可见时回到主窗口既有 `todo` 返回链路，`list_picker_source == "todo"`
- `todo_board`：
  - 静态代码显示 `_resolve_detail_edit_target(...)` 仍保留 `source_view == "todo_board"` 且 `todo_board.isVisible()` 时返回 `todo_board`
  - 本轮未额外构造 `TodoBoardWindow` 做运行 smoke，仅记录现状，不扩展验证范围

月 panel 固定 `source_view="month"` 是否会锁死路由：

- 结论：不会锁死。
- 依据：
  1. `open_schedule_detail_from_month_panel(...)` 的三条编辑连接最终都进入 `MainWindow.go_to_*_picker_for_edit(..., "month")`
  2. 三个 `go_to_*_picker_for_edit(...)` 都统一调用 `_resolve_detail_edit_target("month")`
  3. 已通过 direct-source smoke 证明：即使传入 `"month"`，当前可见周界面时仍会改路由到 `week`，当前可见主窗口时仍会改路由到 `day`

是否未改 MP-3 生命周期：

- 是。
- 未修改：
  - `src/ui/month_window.py`
  - `src/ui/popups/month_day_panel.py`
  - `src/ui/schedule_detail_pop.py`
- 普通 hide 不清理 panel 的 MP-3 规则保持不变。

验证命令与结果：

- 静态定位：
  - `rg -n "def _resolve_detail_edit_target|go_to_time_picker_for_edit|go_to_alarm_picker_for_edit|go_to_list_picker_for_edit|open_schedule_detail_from_month_panel|source_view|ScheduleDetailPop|req_edit_time|req_edit_alarm|req_edit_list" src/ui/main_window.py src/ui/schedule_detail_pop.py`
  - `rg -n "go_to_time_picker_for_edit|go_to_alarm_picker_for_edit|go_to_list_picker_for_edit" src/ui/month_window.py src/ui/week_window.py src/ui/todo_board.py`
  - `rg -n "req_edit_time|req_edit_alarm|req_edit_list|_show_detail_popup|ScheduleDetailPop" src/ui/dashboard.py src/ui/todo.py`
  - 结果：通过，静态链路与 MP-4 目标一致。
- import 验证：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.main_window import MainWindow; from src.ui.schedule_detail_pop import ScheduleDetailPop; from src.ui.month_window import MonthWindow; from src.ui.week_window import WeekWindow; print('mp4 imports ok', MainWindow, ScheduleDetailPop, MonthWindow, WeekWindow)"`
  - 结果：通过。
- `_resolve_detail_edit_target(...)` offscreen 验证：
  - 结果输出：`day` / `month` / `week` / `todo`
  - 结论：通过。
- time 编辑请求路由 smoke：
  - 结果：通过，输出 `time route ok [...]`
- alarm 编辑请求路由 smoke：
  - 结果：通过，输出 `alarm route ok [...]`
- list 编辑请求路由 smoke：
  - 结果：通过，输出 `list route ok [...] todo`
- 月 panel popup 动态路由专门 smoke：
  - 直接构造 `MonthDayPanel + ScheduleDetailPop` 并 `emit` 的 offscreen 命令在当前环境下退出码为 1，未回显 Python traceback。
  - 结合本地环境已知的 `.venv` 启动器不稳定问题，本轮将其记录为“专项 smoke 命令环境不稳定”，不据此判断源码缺陷。
  - 等价依据已由以下两项覆盖：
    1. `open_schedule_detail_from_month_panel(...)` 三条桥接 lambda 的静态检查
    2. `source_view="month"` 下的 direct-source time/alarm/list 路由 smoke 全部通过
  - 顾问窗口复核补充：加入分步输出和显式 `close()` / `app.quit()` 后，专项 smoke 通过。
    - 输出：`target before first day`、`after first emit edit`、`target before second week`、`after second emit [('week', ...)]`。
    - 结论：月 panel 打开的详情弹窗即使固定 `source_view="month"`，在当前日视图可见时走 day，在周界面可见时走 week，不会锁死到 month。
- `py_compile`：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/main_window.py src/ui/schedule_detail_pop.py src/ui/month_window.py src/ui/week_window.py main.py`
  - 结果：通过。

diff 范围检查结果：

- `git diff --name-only -- src/ui/popups/month_day_panel.py`：无输出。
- `git diff --name-only -- src/ui/month_window.py`：无输出。
- `git diff --name-only -- src/ui/dashboard.py`：无输出。
- `git diff --name-only -- src/ui/week_window.py`：无输出。
- `git diff --name-only -- src/ui/todo.py`：无输出。
- `git diff --name-only -- src/ui/todo_board.py`：无输出。
- `git diff --name-only -- src/controllers`：无输出。
- `git diff --name-only -- src/data`：无输出。
- `git diff --name-only -- src/repositories`：无输出。
- `git diff --name-only -- src/services`：无输出。
- `git diff --name-only -- src/theme`：无输出。
- `git diff --name-only -- src/utils/signals.py`：无输出。
- `git diff --name-only -- src/utils/styles.py`：无输出。
- `git diff --name-only -- assets`：无输出。
- `git diff --name-only -- main.py`：无输出。
- `git diff --name-only -- requirements.txt`：无输出。
- `git diff --name-only -- schedule.db`：无输出。

未完成事项：

- 本轮未处理保存后多视图刷新；继续留给 `MP-5`。
- 本轮未扩大 `todo_board` 运行态验证；仅记录现有 fallback 分支。

风险或疑点：

- 第一版月 panel 专项 popup emit 命令曾在进程收尾阶段无 traceback 退出；顾问窗口使用显式关闭/退出的命令复跑通过，判断为验证命令收尾问题，不是 MP-4 路由缺陷。
- `ScheduleDetailPop.source_view` 仍参与内部 UI/样式分支；本轮只确认其不会锁死编辑路由，不处理该字段的长期语义收敛。

---

## 2026-06-25 MP-5：保存后多视图刷新与阶段整体验收

任务来源：

- 按 `manage_instruction/Work_Task_Prompts.md` 当前待执行提示词执行 `MP-5`。
- 本轮先做刷新链路审查和验收，只有发现明确刷新缺口时才做最小源码修正。

开工前 git 状态：

- `git status --short --branch`：`## main...temp/main [ahead 106]`
- `git diff --name-only`：`manage_instruction/Work_Task_Prompts.md`
- 开工前已有 diff：`manage_instruction/Work_Task_Prompts.md`
- 结论：开工前无 `src/` 相关 diff，本轮不回退、不清理该既有管理文档 diff。

实际修改文件：

- `src/ui/month_window.py`
- `src/ui/main_window.py`
- `manage_instruction/Work_Log.md`

是否修改源码：

- 已做最小源码修正。
- 原因：现有刷新链路存在明确缺口，不能满足 MP-5 的“marker / hover cache / open panel / child popup / 当前可见相关视图”一致刷新要求。

现有刷新链路审查结果：

- `MonthWindow._complete_schedule_edit(...)` 基线只做：
  - `_refresh_schedule_marker_cache()`
  - `schedule_updated.emit(schedule)`
- 基线缺口：
  1. 不刷新 `open_day_panels`
  2. 不刷新 `child_detail_popups`
  3. `MainWindow.open_schedule_detail_from_month_panel(...)` 基线未把 month panel 子 `ScheduleDetailPop.schedule_updated` 接回月界面刷新链路
  4. `MainWindow._on_week_schedule_updated(...)` 基线只刷新 dashboard，不足以覆盖跨视图保留后“当前可见 week / todo”的刷新

marker / hover cache 刷新结论：

- `MonthWindow._refresh_schedule_marker_cache()` 已同时刷新：
  - `schedule_marker_cache`
  - `schedule_marker_count_cache`
  - `hover_schedule_cache`
- 本轮保留该实现，作为月界面刷新链的底层入口。

open day panels 刷新结论：

- 基线无刷新已打开 panel 的 helper。
- 本轮新增：
  - `MonthWindow.refresh_open_day_panels()`
- 策略：
  - 遍历 `open_day_panels`
  - 按 `panel.panel_date` 从最新 `hover_schedule_cache` 重新取列表
  - 调用 `panel.set_panel_data(panel_date, schedules)` 重新渲染
- 结果：
  - 日程时间跨日期后，旧日期 panel 会按最新数据重载，不再长期显示脏数据
  - 标题 / 时间 / 重要性 / 状态变化也会同步回 panel 列表

child detail popups 刷新结论：

- 基线 `MonthDayPanel` 已有：
  - `child_detail_popups`
  - `register_child_detail_popup(...)`
  - `_prune_child_detail_popups()`
- 但基线没有 month 级 helper 去刷新这些子详情 popup。
- 本轮新增：
  - `MonthWindow.refresh_month_detail_popups(updated_schedule=None)`
- 策略：
  - 遍历所有 open panel 的 `child_detail_popups`
  - 若传入 `updated_schedule`，只刷新同 `id` popup
  - 对命中的 popup 调用已存在刷新方法：
    - `refresh_time_display`
    - `refresh_alarm_display`
    - `refresh_list_display`
    - `refresh_created_display`
    - `refresh_priority_display`
    - `refresh_repeat_display`
  - 若 popup 当前 `data.id` 命中 `updated_schedule.id`，先将 `popup.data = updated_schedule`
- 说明：
  - 未直接改 `ScheduleDetailPop`。
  - 顾问复核时发现初版 helper 只调用时间 / 提醒 / 清单 / 创建时间 / 重要性 / 重复刷新方法；若同一日程存在多个月 panel 子详情 popup，标题与详情说明可能仍显示旧值。
  - 已补充 `refresh_month_detail_popups(...)` 对命中 popup 的 `lbl_title`、`edit_title`、`lbl_desc`、`edit_desc` 同步更新，并沿用 `ScheduleDetailPop._get_desc_color(...)` 计算详情文字颜色。
  - 复核命令构造同 id 的 old/new fake schedule 后调用 `refresh_month_detail_popups(new)`，确认 popup 标题从 `old title` 更新为 `new title`，详情从 `old desc` 更新为 `new desc`。

月 panel 子 `ScheduleDetailPop.schedule_updated` 连接结论：

- 基线缺口：
  - `MainWindow.open_schedule_detail_from_month_panel(...)` 只连接了 `req_edit_time / req_edit_alarm / req_edit_list`
  - 没有把 `popup.schedule_updated` 接回 month 刷新链
- 本轮补齐：
  - `popup.schedule_updated.connect(lambda popup_ref=popup: self.month_window.refresh_after_schedule_change(getattr(popup_ref, "data", None)))`
- 结果：
  - month panel 子详情 popup 内直接修改标题 / 详情 / 重要性 / 重复后，会立刻回接 month 界面刷新链

统一刷新 helper 与调用点：

- 本轮新增：
  - `MonthWindow.refresh_after_schedule_change(updated_schedule=None)`
- 策略：
  1. `_refresh_schedule_marker_cache()`
  2. `refresh_open_day_panels()`
  3. `refresh_month_detail_popups(updated_schedule)`
  4. `schedule_updated.emit(updated_schedule)`
- 调用点：
  - `MonthWindow._complete_schedule_edit(schedule)` 现在改为调用 `refresh_after_schedule_change(schedule)`
  - `MainWindow.open_schedule_detail_from_month_panel(...)` 中 month 子 popup 的 `schedule_updated` 也回接到该 helper

day / week / month / todo 相关刷新结论：

- `MonthWindow.schedule_updated` 仍连接到 `MainWindow._on_week_schedule_updated(...)`
- 基线缺口：
  - `_on_week_schedule_updated(...)` 原本只 `page_dashboard.refresh_data()`
  - 无法覆盖当前可见 `week` / `todo`
- 本轮补齐：
  - `_on_week_schedule_updated(...)` 先调用 `_refresh_dashboard_todo_week()`
- 结果：
  - day：通过 `dashboard` 刷新
  - todo：通过 `todo` 刷新
  - week：通过 `week_if_visible` 刷新
  - month：由 `MonthWindow.refresh_after_schedule_change(...)` 自身负责
- 说明：
  - 本轮复用既有 RefreshCoordinator 边界，没有新增全局 EventBus，也没有改 MP-4 路由规则。

是否未改 MP-3 生命周期：

- 是。
- 未修改普通视图切换保留 panel 的规则。
- 未修改：
  - panel 手动关闭清理子详情
  - 普通 `hide()` 不清理 panel
  - 显式跳日 / picker 仍显式清理 panel

是否未改 MP-4 动态路由：

- 是。
- `MainWindow._resolve_detail_edit_target(...)` 未修改。
- `ScheduleDetailPop` 的编辑请求路由规则未修改。

验证命令与结果：

- 静态定位：
  - `rg -n "_complete_schedule_edit|_refresh_schedule_marker_cache|open_day_panels|set_panel_data|child_detail_popups|schedule_updated|refresh_open|refresh_after|refresh_month|refresh_data|refresh_week_data|refresh_time_display|refresh_alarm_display|refresh_list_display|refresh_created_display" src/ui/main_window.py src/ui/month_window.py src/ui/popups/month_day_panel.py src/ui/schedule_detail_pop.py src/ui/dashboard.py src/ui/week_window.py src/ui/todo.py src/ui/todo_board.py`
  - 结果：通过，可定位新增 helper 和 month/month-popup/main refresh 链。
- import 验证：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "from src.ui.main_window import MainWindow; from src.ui.month_window import MonthWindow; from src.ui.popups.month_day_panel import MonthDayPanel; from src.ui.schedule_detail_pop import ScheduleDetailPop; print('mp5 imports ok', MainWindow, MonthWindow, MonthDayPanel, ScheduleDetailPop)"`
  - 结果：通过。
- 月 panel 可重复刷新列表验证：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from datetime import datetime; from types import SimpleNamespace; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.popups.month_day_panel import MonthDayPanel; app=QApplication([]); q=QDate.currentDate(); s1=SimpleNamespace(id=1, title='old title', start_time=datetime.now(), end_time=None, priority=0, status=0); s2=SimpleNamespace(id=1, title='new title', start_time=datetime.now(), end_time=None, priority=2, status=1); p=MonthDayPanel(q, [s1]); p.set_panel_data(q, [s2]); print('panel refresh ok', p.panel_date.toString('yyyy-MM-dd')); assert p.panel_date == q; p.close(); app.quit()"`
  - 结果：通过。
- MonthWindow marker/cache 刷新 smoke：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); w._refresh_schedule_marker_cache(); print('marker cache type', type(w.hover_schedule_cache).__name__); assert isinstance(w.hover_schedule_cache, dict); w.close(); app.quit()"`
  - 结果：通过。
- open panel 刷新 helper 验证：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); q=QDate.currentDate().addDays(1); w._open_day_panel(q); assert len(w.open_day_panels) == 1; assert hasattr(w, 'refresh_open_day_panels'); w.refresh_open_day_panels(); print('open panel refresh helper ok', len(w.open_day_panels)); assert len(w.open_day_panels) == 1; w.close_day_panels(); w.close(); app.quit()"`
  - 结果：通过。
- detail popup 刷新 helper 验证：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from datetime import datetime; from types import SimpleNamespace; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; from src.ui.popups.month_day_panel import MonthDayPanel; from src.ui.schedule_detail_pop import ScheduleDetailPop; app=QApplication([]); w=MonthWindow(); panel=MonthDayPanel(QDate.currentDate(), []); s=SimpleNamespace(id=55, title='mp5', description='', start_time=None, end_time=None, priority=0, status=0, item_type='schedule', category_id=None, is_alarm=False, alarm_duration=0, reminder_time=None, repeat_rule='无', created_at=datetime.now()); pop=ScheduleDetailPop(s, source_view='month'); panel.register_child_detail_popup(pop); w.open_day_panels.append(panel); assert hasattr(w, 'refresh_month_detail_popups'); w.refresh_month_detail_popups(s); print('detail popup refresh helper ok'); panel.close(); w.close(); app.quit()"`
  - 结果：通过。
- 统一刷新 helper 验证：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; app=QApplication([]); w=MonthWindow(); q=QDate.currentDate().addDays(1); w._open_day_panel(q); assert hasattr(w, 'refresh_after_schedule_change'); w.refresh_after_schedule_change(); print('refresh after schedule change ok', len(w.open_day_panels), type(w.hover_schedule_cache).__name__); w.close_day_panels(); w.close(); app.quit()"`
  - 结果：通过。
- MainWindow 现有 `schedule_updated` 链路 smoke：
  - 初版 monkeypatch 直接替换 `page_dashboard.refresh_data` / `page_todo.refresh_data` 后断言失败。
  - 原因：`RefreshCoordinator` 在构造阶段已注册旧的 bound method，后置 monkeypatch 不会自动覆盖已注册 callable。
  - 复跑方式：monkeypatch 后执行 `w._register_refresh_targets()` 再测。
  - 复跑命令：
    - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from types import SimpleNamespace; from PyQt6.QtWidgets import QApplication; from src.ui.main_window import MainWindow; app=QApplication([]); w=MainWindow(); hits=[]; w.page_dashboard.refresh_data=lambda: hits.append('dashboard'); w.page_todo.refresh_data=lambda: hits.append('todo'); w.week_window.refresh_week_data=lambda: hits.append('week'); w._register_refresh_targets(); w.week_window.show(); app.processEvents(); w._on_week_schedule_updated(SimpleNamespace(id=-999)); print('refresh hits', hits); assert 'dashboard' in hits; assert 'todo' in hits; assert 'week' in hits; w.close(); app.quit()"`
  - 结果：通过，输出 `refresh hits ['week', 'dashboard', 'todo', 'week']`。
- 月 panel 子详情 popup 的 `schedule_updated` 连接验证：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from datetime import datetime; from types import SimpleNamespace; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.main_window import MainWindow; from src.ui.popups.month_day_panel import MonthDayPanel; app=QApplication([]); w=MainWindow(); calls=[]; w.month_window.refresh_after_schedule_change=lambda updated_schedule=None: calls.append(getattr(updated_schedule,'id',None)); panel=MonthDayPanel(QDate.currentDate(), []); s=SimpleNamespace(id=88,title='mp5',description='',start_time=None,end_time=None,priority=0,status=0,item_type='schedule',category_id=None,is_alarm=False,alarm_duration=0,reminder_time=None,repeat_rule='无',created_at=datetime.now()); pop=w.open_schedule_detail_from_month_panel(s, panel); pop.schedule_updated.emit(); print('popup refresh calls', calls); assert calls == [88]; panel.close(); w.close(); app.quit()"`
  - 结果：通过，输出 `popup refresh calls [88]`。
- 顾问复核补充：子详情 popup 标题 / 详情同步验证：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -c "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from datetime import datetime; from types import SimpleNamespace; from PyQt6.QtWidgets import QApplication; from PyQt6.QtCore import QDate; from src.ui.month_window import MonthWindow; from src.ui.popups.month_day_panel import MonthDayPanel; from src.ui.schedule_detail_pop import ScheduleDetailPop; app=QApplication([]); w=MonthWindow(); panel=MonthDayPanel(QDate.currentDate(), []); old=SimpleNamespace(id=55,title='old title',description='old desc',start_time=None,end_time=None,priority=0,status=0,item_type='schedule',category_id=None,is_alarm=False,alarm_duration=0,reminder_time=None,repeat_rule='无',created_at=datetime.now()); new=SimpleNamespace(id=55,title='new title',description='new desc',start_time=None,end_time=None,priority=2,status=0,item_type='schedule',category_id=None,is_alarm=False,alarm_duration=0,reminder_time=None,repeat_rule='每天',created_at=datetime.now()); pop=ScheduleDetailPop(old, source_view='month'); panel.register_child_detail_popup(pop); w.open_day_panels.append(panel); w.refresh_month_detail_popups(new); title=getattr(pop,'lbl_title').text(); desc=getattr(pop,'lbl_desc').text(); print('popup text after refresh', title, '|', desc); assert title == 'new title'; assert desc == 'new desc'; panel.close(); w.close(); app.quit()"`
  - 结果：通过，输出 `popup text after refresh new title | new desc`。
- `py_compile`：
  - `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/main_window.py src/ui/month_window.py src/ui/popups/month_day_panel.py src/ui/schedule_detail_pop.py src/ui/dashboard.py src/ui/week_window.py src/ui/todo.py src/ui/todo_board.py main.py`
  - 结果：通过。

diff 范围检查结果：

- `git diff --name-only -- src/controllers`：无输出。
- `git diff --name-only -- src/data`：无输出。
- `git diff --name-only -- src/repositories`：无输出。
- `git diff --name-only -- src/services`：无输出。
- `git diff --name-only -- src/theme`：无输出。
- `git diff --name-only -- src/utils/signals.py`：无输出。
- `git diff --name-only -- src/utils/styles.py`：无输出。
- `git diff --name-only -- assets`：无输出。
- `git diff --name-only -- main.py`：无输出。
- `git diff --name-only -- requirements.txt`：无输出。
- `git diff --name-only -- schedule.db`：无输出。

MP-0 ~ MP-5 阶段完成结论：

- MP-0：完成，现状审查与边界定位已完成。
- MP-1：完成，月日程 panel UI 与列表承载已完成。
- MP-2：完成，panel 内双击打开共享 `ScheduleDetailPop` 已完成。
- MP-3：完成，panel 生命周期与跨视图保留规则已完成。
- MP-4：完成，详情编辑请求按当前可见视图动态路由已验收通过。
- MP-5：完成，本轮已补齐 month marker / hover cache / open panel / child popup / 当前可见相关视图的刷新链。

阶段目标达成结论：

- 月日程 panel UI：达到阶段目标。
- 详情打开：达到阶段目标。
- 生命周期：达到阶段目标。
- 动态路由：达到阶段目标。
- 刷新验收：达到阶段目标。
- 结论：`MP` 阶段可归档。

未完成事项：

- 本轮未扩展 `todo_board` 专项运行态刷新验证；仍沿用既有 todo_board 链路。
- 本轮未做真实写库验收；按提示词默认策略，仅做无写库 smoke。

风险或疑点：

- `MainWindow` 统一刷新链 smoke 的断言已通过并输出 `refresh hits ['week', 'dashboard', 'todo', 'week']`，但完整 `MainWindow` offscreen 进程在 `done` 后仍返回 code 1；判断为 Qt 窗口 / 后台对象收尾不稳定，不是刷新断言失败。手动验收仍需重点复测实际 GUI 中月 panel 子详情编辑后的跨视图刷新。
- MainWindow 的 week/month 共用 `_on_week_schedule_updated(...)` 名称现在已经覆盖 month 刷新后的跨视图联动，但方法名语义仍偏旧；本轮不改名，只做最小补修。

---

## 2026-06-28 月日程 panel 跨视图可见性修复

任务目标：

- 核查月界面只打开某日 panel、未打开具体日程详情时，切换到日/周/待办视图后 panel 看似关闭的问题。
- 目标行为：普通视图切换后，某日 panel 无论是否存在子详情 popup 都继续显示；显式关闭规则保持不变。

开工前 git 状态：

- `git status --short --branch`：`## main...temp/main [ahead 107]`
- 工作区无未提交 diff。

原因确认：

- `MonthWindow.hideEvent(...)` 已按 MP-3 规则不再调用 `close_day_panels()`，因此普通视图切换并未真正销毁 panel。
- `MainWindow.switch_view(...)` 在目标窗口显示后只通过 `_restore_detail_popups()` 恢复日/待办详情 popup，没有恢复或提升 `MonthWindow.open_day_panels` 的窗口层级。
- 无子详情 popup 时，月日程 panel 容易落到新显示的顶层窗口后方，视觉上表现为“关闭”；打开子详情后，详情 popup 的恢复/层级行为使现象不一致。

实际修改文件：

- `src/ui/month_window.py`
- `src/ui/main_window.py`
- `manage_instruction/Work_Log.md`

实现说明：

- `MonthWindow` 新增 `restore_open_day_panels()`：
  - 对仍登记在 `open_day_panels` 的 panel 执行 `show()` 和 `raise_()`。
  - 清理失效的子详情引用后，对仍存在的子详情 popup 执行 `show()` 和 `raise_()`，保持详情位于所属 panel 上方。
  - 不调用 `activateWindow()`，避免普通视图切换时抢占输入焦点。
- `MainWindow._restore_detail_popups()` 在恢复日/待办详情 popup 后调用 `month_window.restore_open_day_panels()`。
- 继续复用 `switch_view(...)` 既有 `QTimer.singleShot(0, ...)`，确保目标视图窗口完成显示后再恢复 popup 层级。

保持不变的行为：

- 月格再次单击同日仍可手动关闭该 panel。
- 双击月格跳日、右键跳日、进入时间/提醒/清单 picker 和月窗口真正关闭时，既有显式 `close_day_panels()` 规则不变。
- panel 手动关闭时仍关闭其所属子详情 popup。
- 本轮未修改 MP-4 当前可见视图编辑路由和 MP-5 保存刷新链。

验证结果：

- `py_compile`：`src/ui/main_window.py`、`src/ui/month_window.py`、`src/ui/popups/month_day_panel.py`、`main.py` 通过。
- 无子详情 panel 跨窗口恢复 offscreen：
  - 打开某日 panel，隐藏月窗口并显示另一个顶层窗口，再调用 `restore_open_day_panels()`。
  - 结果：`panel retained True`、`panel visible True`。
- 主窗口恢复桥接 smoke：
  - 结果：`restore hits ['day', 'todo', 'month']`，确认月 panel 已纳入既有恢复回调。
- 显式关闭回归：调用 `close_day_panels()` 后结果 `explicit close count 0`。
- 禁止范围检查：`src/controllers`、`src/data`、`src/repositories`、`src/services`、`src/theme`、`assets`、`main.py`、`requirements.txt`、`schedule.db` 均无 diff。
- `git diff --check`：仅 LF/CRLF 提示，无 whitespace error。

未完成事项与风险：

- Qt offscreen 无法直接断言 Windows 桌面真实 Z-order；已验证对象保留、可见状态与恢复调用。仍建议手动复测“月 -> 日/周/待办 -> 月”以及无子详情/有子详情两种路径。
- 本轮不提交 Git，等待用户检查实际界面后决定提交。

---

## 2026-06-29 Final_Formulation 进度同步

核查结论：

- `Final_Formulation.md` 已记录旧 `M-0 ~ M-7` 月界面功能补齐阶段，但尚未记录随后完成的 `MP-0 ~ MP-5` 月日程持久 panel 详情与编辑路由阶段。
- 文档仍把“持久弹窗编辑能力”列为未完成缺口，与当前代码和阶段日志不一致。

实际修改文件：

- `manage_instruction/Final_Formulation.md`
- `manage_instruction/Work_Log.md`

更新内容：

- 在当前状态和已完成阶段中补入 `MP-0 ~ MP-5`：
  - 紧凑列表 UI 与数据承载。
  - 双击日程项打开共享详情弹窗。
  - 普通视图切换保留 panel、显式关闭继续清理。
  - 编辑请求按当前可见视图动态路由。
  - 保存后 marker、cache、panel、子详情及相关视图统一刷新。
- 记录无子详情 panel 在普通视图切换后的层级恢复补修。
- 将“持久弹窗编辑能力未完成”修正为“编辑主链已完成，剩余视觉与布局验收”。
- 同步 Month View 技术债和后续第 1 项说明，不改变坐标看板、课表模式、搜索、导出、换肤、自定义重复、弹窗美化、节假日、字体和云功能的既定顺序。

范围说明：

- 本次进度同步不修改源码。
- 当前源码 diff 仍仅来自上一项月日程 panel 跨视图可见性修复。
- `Work_Instruction.md` 仍保留为本轮 MP 阶段合同，后续归档时再处理，不在本次进度同步中改写。

---

## 2026-06-29 月界面 UI 集中验收

任务目标：

- 在继续凭观感调整 UI 之前，对当前月界面的主要状态做集中截图和交互验收。
- 本轮不修改业务源码，只记录实际发现的问题。

开工前状态：

- `git status --short --branch`：`## main...temp/main [ahead 108]`
- 工作区干净。
- 最新提交：`1d4607e fix: retain month day panels across view switches`。

验收环境与方法：

- 使用项目 `.venv` 和 Windows 原生 Qt 平台自动构造月界面状态。
- 逻辑窗口尺寸：`720x480`。
- 原生截图尺寸：`900x600`，对应当前系统约 125% 显示缩放。
- 截图状态：
  1. 默认月历。
  2. 带长标题和长详情的月添加表单。
  3. 时间 picker 日历展开状态。
  4. 时间 picker 日历收起状态。
  5. 提醒 picker。
  6. 清单 picker。
  7. 含 8 条日程及长标题的持久 panel。
  8. 含多条日程及长标题的 hover 预览。
- 临时截图与验收脚本位于仓库外 `D:\CodeProjects\DesktopSchedule\_month_ui_acceptance*`，不属于项目源码，验收后删除。

通过项：

- 默认月历：星期标题、日期格、周末红字、非本月灰字、今天金色字和日程数量角标未发现阻断性重叠或裁切。
- 月添加表单：标题、详情、功能图标、重要性、重复、状态框、取消/保存按钮均位于左栏范围内。
- 时间 picker：日历展开和收起两种状态下，日期按钮、开始时间开关、时间滚轮、快捷时长和底部按钮均未越出左栏。
- 提醒 picker：时间滚轮、快捷提醒、强提醒开关和底部按钮未发现裁切。
- 清单 picker：单条清单状态下底部“新建/取消/确定”位置稳定；空白区域较大但属于内容数量少，不判定为布局错误。
- 持久 panel：8 条日程时使用紧凑行和竖向滚动，长标题不会把 panel 横向撑出固定 `280px` 宽度。
- 所有月侧栏主要状态的几何范围一致：`x=12, y=146, width=136, height=294`，右边界 `148`、下边界 `440`，未越出 `720x480` 月窗口。
- 单击同日第二次关闭 panel、同时打开两个日期 panel、普通隐藏后恢复 panel 均通过。
- `py_compile`：`month_window.py`、`month_day_panel.py`、`month_day_hover_preview.py`、`main_window.py`、`main.py` 通过。

发现项：

1. 中优先级：hover 预览宽度和屏幕边界。
   - `MonthDayHoverPreview.set_preview_data(...)` 直接调用 `adjustSize()`，没有最大宽度。
   - `_show_hover_preview(...)` 固定放在月格右下角 `+8px`，没有按可用屏幕区域回退。
   - 本轮普通长标题截图宽度约 `296px`；合成长标题验证可达到 `462px`。
   - 靠近屏幕右侧/底部时可能越界，并可能复现既有 `QWindowsWindow::setGeometry` 系统修正警告。
2. 低优先级：月添加详情框滚动条样式。
   - 长详情会出现 Qt 原生竖向滚动条。
   - 功能正常，无内容丢失，但滚动条与青色渐变界面的视觉风格不统一。

验收结论：

- 未发现阻断后续主线的月界面 UI 问题。
- 月界面可以结束当前集中验收，不需要继续无目标地调整间距和尺寸。
- 建议只补一个小工单处理 hover 预览最大宽度、自动换行和屏幕边界回退；详情框滚动条样式可并入后续统一弹窗/QSS 美化阶段。
- 本轮不修改业务源码，不提交临时截图或验收脚本。

---

## 2026-06-29 月界面 hover 预览宽度与屏幕边界修复

任务来源：

- 根据月界面 UI 集中验收发现项，修复 hover 只读预览的最大宽度、长文本自动换行和屏幕边界回退。
- 本轮不修改待办看板和月界面单击日期持久 panel。

开工前状态：

- `git status --short --branch`：`## main...temp/main [ahead 109]`
- 工作区干净。

实际修改文件：

- `src/ui/popups/month_day_hover_preview.py`
- `src/ui/month_window.py`
- `manage_instruction/Final_Formulation.md`
- `manage_instruction/Work_Log.md`

实现内容：

- `MonthDayHoverPreview`：
  - 最小宽度设为 `150px`。
  - 最大宽度设为 `260px`。
  - 正文标签最大宽度设为 `238px`，配合既有 `wordWrap=True` 让长标题和多条日程自动换行增高。
- `MonthWindow._show_hover_preview(...)`：
  - 不再固定使用日期格右下角坐标直接移动。
  - 新增 `_get_hover_preview_position(...)` 计算预览位置。
  - 默认仍显示在日期格右下方，保持原交互方向。
  - 右侧越界时回退到日期格左侧。
  - 底部越界时回退到日期格上方。
  - 最后按当前屏幕 `availableGeometry()` 夹紧，避免多屏或任务栏区域越界。
  - 不调用 `activateWindow()`，不改变 hover 预览只读、鼠标穿透和移出立即隐藏的行为。

验证结果：

- 极端长标题换行：
  - 合成 `“超长标题” * 30` 的单条日程。
  - 显示后 popup 为 `253x123`，正文为 `231x89`，正文实际高度等于换行后的 `sizeHint`。
  - 结果：宽度小于 `260px`，正文无纵向裁切。
- 屏幕右下角边界：
  - offscreen 可用区域为 `800x800`。
  - 将月窗口放到右下角，以日历 viewport 右下角单元格计算长标题 popup 位置。
  - 结果：popup `253x123`，最终坐标 `(517,647)`，四边均位于可用区域内。
- `py_compile`：
  - `month_day_hover_preview.py`
  - `month_window.py`
  - `main_window.py`
  - `main.py`
  - 结果：通过。

保持不变：

- hover 预览仍最多展示 6 条日程，超过时显示总数提示。
- 鼠标离开日期网格后仍立即隐藏。
- 单击日期 panel、共享详情弹窗、右键菜单、添加/picker 和数据库逻辑均未修改。

未完成事项与风险：

- Qt offscreen 已验证尺寸和屏幕夹紧；真实 Windows 多显示器、负坐标副屏仍建议用户手动观察一次。
- 月添加详情框原生滚动条仍属于后续统一 QSS 美化项，本轮未处理。

---

## 2026-06-29 月界面持久 panel 长标题省略

任务目标：

- 修复月界面单击日期持久 panel 中，长日程标题挤占右侧状态列并超出单行可用空间的问题。
- 本轮只修改持久 panel 日程行，不修改 hover 预览和待办看板。

实际修改文件：

- `src/ui/popups/month_day_panel.py`
- `manage_instruction/Final_Formulation.md`
- `manage_instruction/Work_Log.md`

实现内容：

- 新增 `_ElidedTitleLabel`：
  - 保存完整标题文本。
  - 根据控件实时宽度使用 `QFontMetrics.elidedText(..., ElideRight, width)` 生成右侧省略文本。
  - resize 时重新计算，适配滚动条出现或布局宽度变化。
  - tooltip 保留完整标题，鼠标停留时仍可查看全文。
  - `sizeHint()` / `minimumSizeHint()` 的宽度返回 0，并使用水平 `Ignored` size policy，让标题只占时间列与状态列之间的剩余空间。
- 时间列固定 `40px`、状态列固定 `66px` 的既有规则保持不变。

验证结果：

- 合成长中文标题显示为右侧省略文本，断言末尾为省略号通过。
- 标题实际可用宽度约 `116px`，完整文本保留在 tooltip。
- 右侧 `高/未完成` 状态标签仍存在，未被长标题挤出。
- `py_compile`：`month_day_panel.py`、`month_day_hover_preview.py`、`month_window.py`、`main.py` 通过。

保持不变：

- 日程行固定高度、时间、状态、双击打开共享详情、滚动和 panel 尺寸均未修改。
- 本轮未改数据库、服务层、待办看板、日界面或周界面。

---

## 2026-06-29 坐标显示单时间轴看板样本

任务目标：

- 将“更多 -> 坐标显示”从占位输出接为可直接打开的辅助看板样本。
- 看板参考待办看板的尺寸和青色渐变背景，只使用一条以当前时间为原点的水平时间轴。
- 纳入用户补充构想：过去负轴、点 / 时间段线段、hover 只读详情、单击共享可编辑详情，以及由最远日程决定的动态时间范围。

开工前状态：

- `git status --short --branch`：`## main...temp/main [ahead 111]`
- 工作区干净。

实际修改文件：

- `src/services/schedule_axis_service.py`（新增）
- `src/ui/popups/schedule_axis_board.py`（新增）
- `src/ui/components.py`
- `manage_instruction/Final_Formulation.md`
- `manage_instruction/Work_Log.md`

实现内容：

- 新增 `ScheduleAxisService`：
  - 通过 `ScheduleRepository` / `CategoryRepository` 读取日程与清单，不让看板 UI 直接访问 `db_manager`。
  - 只投影 `item_type == "schedule"` 且 `status != 2`、至少具有一个时间字段的数据。
  - 单时间数据投影为点；开始和结束时间不同的数据投影为时间段。
  - 以当前时间为 0，过去使用负值、未来使用正值。
  - 使用带符号的 `log(1 + |t|)` 映射横坐标。
  - 时间范围取所有投影开始 / 结束时间绝对距离的最大值，最小 24 小时，最大 365 天；超出一年时夹紧到边界。
- 新增 `ScheduleAxisBoard`：
  - 独立无边框窗口，固定样本尺寸 `380x300`，使用项目青色渐变和圆角边框。
  - 中心为“现在”，左右分别为过去和未来，并显示当前动态范围。
  - 清单颜色控制标记颜色；重要性低 / 中 / 高分别使用 `8 / 12 / 16px` 点尺寸。
  - 时间段以有圆形端点的线段表示；单时间日程以圆点表示。
  - 碰撞时分配上下轨道，但横坐标只由时间决定，因此相同时间仍处于同一垂直线上。
  - hover 显示只读详情，移开隐藏。
  - 单击优先复用 `MainWindow.open_schedule_detail_from_month_panel(...)` 打开共享 `ScheduleDetailPop`，并沿用既有动态编辑路由；找不到主窗口桥接时才降级为可手动关闭的只读详情样本。
  - 同一日程再次单击时复用已创建的共享详情弹窗，避免重复创建。
  - 看板和详情弹窗均做当前屏幕可用区域夹紧。
- `SharedMoreMenu._on_show_axis(...)`：
  - 首次点击创建并定位看板，再次点击切换隐藏 / 显示。
  - 显示前刷新数据，优先放在来源窗口右侧，空间不足时回退到左侧并夹紧屏幕。

验证结果：

- 合成数据投影验证通过：
  - 待办和隐藏日程被排除。
  - 过去时间段与远期单时间日程均被正确投影。
  - 超过一年的时间范围被限制为 `8760` 小时。
  - `-24h / 0 / +24h` 在 24 小时范围内映射为 `0 / 50 / 100`。
- 使用可用 Python 3.12 对 4 个相关文件执行定向 `py_compile`，临时字节码写入系统临时目录后清理，结果通过。
- 静态依赖检查确认看板 UI 未直接依赖数据层或写库接口。
- `git diff --check`：已跟踪文件无 whitespace error，仅有 Git 的 LF/CRLF 提示。

环境限制：

- Codex 受限沙箱当时无法访问 `.venv` 记录的用户目录基础解释器，因此未能在沙箱内执行 PyQt offscreen 构造和截图验证；这不是用户项目环境失效。
- Codex 自带 Python 3.12 可做语法检查，但未安装 PyQt6，不能替代项目运行环境。
- 需要用户在可正常启动项目的终端中，通过“更多 -> 坐标显示”进行真实 Windows 视觉和交互验收。

保持不变：

- 未修改数据库结构、日程写入、删除、状态更新和编辑路由。
- 未把待办纳入坐标样本。
- 单击详情不新增写库实现，直接复用既有 `ScheduleDetailPop` 和 `MainWindow` 编辑桥接。
- 未修改日 / 周 / 月现有日程渲染。

后续事项：

- 根据真实运行效果调整轨道、点 / 线段密度、文字和窗口尺寸。
- 明确已完成日程是否默认显示、过滤或单独弱化。
- 真实 Windows 环境复核共享详情弹窗的位置、重复打开和编辑回流。
- 后续自动验证应在获得沙箱外执行权限后直接使用项目 `.venv`，不需要用户修复 Python 3.11 环境。

---

## 2026-06-29 月界面详情编辑时保留日期 panel 与子详情弹窗

问题现象：

- 月界面单击日期打开 `MonthDayPanel`，再双击日程项打开共享 `ScheduleDetailPop`。
- 在共享详情中双击修改清单时，月界面会进入“修改清单”页，但日期 panel 和共享详情弹窗同时消失。
- 修改时间、提醒与清单共用同一编辑 picker 入口，因此存在相同问题。

原因定位：

- `MonthWindow.go_to_time_picker_for_edit(...)`、`go_to_alarm_picker_for_edit(...)`、`go_to_list_picker_for_edit(...)` 最终都会调用 `_show_edit_picker(...)`。
- `_show_edit_picker(...)` 原先无条件调用 `close_day_panels()`。
- `close_day_panels()` 会关闭 `MonthDayPanel`；而 `MonthDayPanel.closeEvent(...)` 会继续关闭其登记的全部子 `ScheduleDetailPop`。
- 因此消失是编辑 picker 的显式清理链造成的，不是清单数据加载或保存失败。

实际修改文件：

- `src/ui/month_window.py`
- `manage_instruction/Work_Log.md`

修改内容：

- 从 `_show_edit_picker(...)` 删除 `close_day_panels()`，使修改时间、提醒和清单时不再销毁日期 panel 及其子详情弹窗。
- picker 显示状态切换完成后，通过 `QTimer.singleShot(0, restore_open_day_panels)` 恢复 panel 和子详情的可见层级。
- 月界面新增日程时进入时间 / 提醒 / 清单 picker 的 `go_to_*_picker(...)` 仍保留原有 `close_day_panels()`；本轮只改变“从详情弹窗进入编辑”的路径。

保持不变：

- 不修改清单、时间、提醒的写库和重复日程更新逻辑。
- 不修改显式关闭日期 panel 时同步关闭所属子详情的规则。
- 不修改双击日期跳日视图、右键跳转和关闭月窗口等显式清理路径。
- 不修改日界面、周界面和待办界面的 picker 行为。

验证要求：

- 从月界面日期 panel 的共享详情分别进入修改时间、修改提醒、修改清单，日期 panel 和详情弹窗都应继续显示。
- 保存或取消 picker 后，原 panel 和详情仍保留；保存后内容按既有刷新链更新。
- 手动关闭日期 panel 时，其所属详情弹窗仍应同步关闭。

---

## 2026-06-29 共享详情重要性 / 重复编辑即时显示修复

问题现象：

- 从月界面日期 panel 打开共享详情后，双击修改重要性，数据库值已经改变，但当前弹窗仍显示旧重要性。
- 编辑位置残留一个带边框的控件；关闭并重新打开弹窗后才显示新值。
- 重复规则使用相同的下拉编辑流程，存在同类风险。

原因定位：

- `_finish_edit_priority(...)` 和 `_finish_edit_repeat(...)` 原先在隐藏编辑用 `QComboBox`、恢复普通 `QLabel` 之前先发出 `schedule_updated`。
- 月界面收到信号后会同步刷新日期 panel、当前子详情和相关视图，形成同步重入；刷新发生时下拉编辑控件仍处于可见状态。
- 截图中的边框来自残留的 `QComboBox`，不是普通重要性文本标签。
- 现有月界面刷新链已经调用 `refresh_priority_display()` / `refresh_repeat_display()`，缺口在编辑控件收尾顺序，而不是缺少刷新方法。

实际修改文件：

- `src/ui/schedule_detail_pop.py`
- `manage_instruction/Work_Log.md`

修改内容：

- 重要性编辑完成后先执行 `hidePopup()`、隐藏 `combo_priority`、恢复 `lbl_priority`，再发出 `schedule_updated`。
- 重复规则编辑完成后先关闭下拉 popup、隐藏 `combo_repeat`、恢复 `lbl_repeat`、隐藏重复说明，再发出 `schedule_updated`。
- 重复规则范围确认选择“取消”时，也统一关闭下拉 popup 和完整说明容器。
- 仅在值真实变化时发出刷新信号；选择原值时只负责退出编辑态。

保持不变：

- 不修改重要性和重复规则的存储值、写库接口和重复日程更新范围确认逻辑。
- 不修改月界面 panel 数据刷新、marker cache 或跨视图编辑路由。
- 该修复位于共享 `ScheduleDetailPop`，因此日 / 周 / 月来源的详情弹窗统一采用正确收尾顺序。

验证要求：

- 修改重要性后，当前详情弹窗立即显示新值，且不残留下拉框边框。
- 修改重复规则后，当前详情立即显示新规则，重复说明和下拉框正确收起。
- 日期 panel 中的重要性 / 状态摘要按既有刷新链同步更新。

真实复测结果：

- 用户复测后问题仍存在：当前详情仍显示旧重要性，带边框编辑控件残留，且残留后无法再次双击进入编辑。
- 因此本节代码调整暂不能判定为修复完成，保持未提交并进入进一步审查。
- 当前源码静态搜索确认：除 `eventFilter(...)` 处理普通标签双击外，没有其他路径会调用 `combo_priority.show()` / `combo_repeat.show()`；月界面刷新函数只调用显示刷新方法，不会主动显示下拉框。
- 下一步必须在完全退出并重启应用后复测，同时观察终端是否出现 Python 异常。若干净重启后仍复现，应记录 `_finish_edit_priority(...)` / `_finish_edit_repeat(...)` 进入、退出以及下一轮事件循环的控件可见状态，再决定采用延迟收尾还是改为显式堆栈容器。

第二次审查与修正：

- 用户完全重启应用后仍复现，终端只有 `QWindowsWindow::setGeometry` 尺寸协商 warning，没有 Python traceback。
- 因此排除旧进程和 Python 信号回调异常，问题进一步收敛为 `QComboBox.activated` 所处的原生 popup 事件回合。
- `_finish_edit_priority(...)` / `_finish_edit_repeat(...)` 现在只更新数据，并通过 `QTimer.singleShot(0, ...)` 将控件收尾推迟到下一轮 Qt 事件循环。
- 延迟收尾中统一执行：关闭 combo popup、隐藏 combo、按最新数据刷新普通标签、显示并抬高标签，最后再发 `schedule_updated`。
- 临时增加终端状态输出，例如：
  - `[ScheduleDetailPop] priority editor finalized: combo_visible=False, label_visible=True, text=高重要性`
  - `[ScheduleDetailPop] repeat editor finalized: combo_visible=False, label_visible=True, text=每周`
- 该输出用于判断延迟收尾后的真实控件状态；用户确认后可移除诊断输出。

第三次审查与修正：

- 用户终端输出确认延迟收尾后的真实状态为 `combo_visible=False, label_visible=True, text=高重要性`，但界面仍存在边框且无法再次双击。
- 该证据排除了“QComboBox 仍可见”的判断；剩余问题位于恢复后的普通标签样式和鼠标命中入口。
- 为 `lbl_priority` / `lbl_repeat` 显式设置 `background: transparent; border: none; padding: 0px`，不再依赖继承样式。
- 将 `priority_editor_container` / `repeat_editor_container` 保存为实例属性，显式清除其背景和边框，并安装同一事件过滤器。
- 双击文字标签或其稳定外层容器均可进入编辑；进入时重新启用并显示对应 combo。
- 本轮不修改数据保存、刷新链和月界面 panel 生命周期。

第四次审查与修正：

- 用户提供的完整终端记录显示：重要性和重复规则的完成函数均执行，数据值可正确变化；问题不在写库或刷新方法。
- 重要性修改后不仅自身不能再次编辑，重复规则也无法点击，说明可能存在覆盖整个底部信息区的原生 popup 输入层。
- `QComboBox.isVisible() == False` 只代表组合框主体不可见，不能证明其私有 `QListView` popup 容器窗口已经关闭。
- 新增 `_close_inline_combo(...)`：显式关闭 combo popup、隐藏 `combo.view()`、隐藏其独立 popup window，并让隐藏的 combo 透明于鼠标事件。
- 再次进入编辑时恢复 combo 的鼠标事件接收能力。
- 终端诊断扩展为同时输出：
  - `combo_visible`
  - `view_visible`
  - `popup_window_visible`
  - `active_popup`
  - `label_visible`
  - 当前文本
- 若修正成功，预期所有可见性均为 `False`，`active_popup=None`，普通标签为 `True`。

第五次审查与修正：

- 用户复测输出确认 `combo_visible=False`、`view_visible=False`、`popup_window_visible=False`、`active_popup=None`、`label_visible=True`，但屏幕仍显示旧文字和旧边框，旧位置无法点击。
- 因此排除组合框主体、下拉 view、私有 popup window 或活动 popup 继续覆盖鼠标的判断。
- “旧像素仍显示但不可交互”结合持续出现的 `QWindowsWindow::setGeometry` warning，更符合半透明无边框窗口在子控件隐藏 / 布局变化后未完整重绘形成的残影。
- 回退第四次修正中无效的私有 popup window 隐藏与鼠标透明设置，避免继续干预 Qt 私有控件生命周期。
- 新增 `_refresh_inline_editor_layout(...)`：
  - 重新 invalidate / activate 重要性和重复编辑容器布局。
  - 重新激活详情弹窗主布局。
  - 重要性切换不再调用无必要的 `adjustSize()`，避免触发额外窗口尺寸协商。
  - 重复规则因说明容器显隐仍按需 `adjustSize()`。
  - 强制执行 `updateGeometry()`、`update()`、同步 `repaint()`，并在下一轮事件循环再次 `repaint()`。
- 目标是清除不可交互的旧控件像素，并让恢复后的真实标签位置与屏幕显示一致。

第六次审查与结构性修正：

- 用户在第五次修正后再次实测，问题仍存在：重要性修改一次后保留不可交互边框，重要性和重复规则都无法再次修改，必须关闭详情弹窗后才能恢复。
- 这说明继续对内嵌 `QComboBox` 追加隐藏、延迟和重绘处理不能解决该窗口组合下的残影与事件命中问题。
- 本次不再切换详情布局中的标签 / 下拉框，而是移除重要性和重复规则的内嵌 `QComboBox`：
  - 详情弹窗布局始终保留普通文字标签，不再因编辑发生控件显隐和尺寸重排。
  - 双击重要性后弹出独立 `QMenu`，选择后复用原写库与 `schedule_updated` 刷新链。
  - 双击重复规则后弹出独立 `QMenu`，保留选项悬停说明、重复范围确认和既有写库逻辑。
  - 菜单关闭后才执行更新，避免原生下拉 popup 的 activated 事件与详情窗口同步刷新重入。
- 删除前几次诊断用的控件可见性输出、延迟收尾、强制布局重绘和已失效的 combo 清理分支。
- 本次目标是从结构上消除详情弹窗内部的下拉框残影，并恢复重要性 / 重复规则可连续多次编辑。
- 自动验证只覆盖导入、语法和无写库 smoke；真实 Windows 交互仍需用户复测后才能判定修复完成。

第六次自动验证结果：

- `src/ui/schedule_detail_pop.py` 通过项目虚拟环境 `py_compile`。
- 无写库 offscreen smoke 在同一个 `ScheduleDetailPop` 实例中连续执行：
  - 重要性：中 -> 高 -> 低，普通标签分别即时更新为“高重要性”“低重要性”。
  - 重复规则：不重复 -> 每天 -> 每周，普通标签分别即时更新为“每天”“每周”。
  - 每次真实变化均发出 `schedule_updated`。
  - 实例不再包含 `combo_priority` / `combo_repeat`，不存在旧内嵌下拉框再次残留的路径。
- 自动验证未写入 `schedule.db`；数据库更新方法和 `Schedule.get_by_id(...)` 均在 smoke 中替换为内存桩。
- 仍需在真实 Windows 窗口中复测菜单点击、重复多次编辑和月界面刷新后，才能将问题标记为最终关闭。

第七次实测反馈与修正：

- 用户真实复测确认重要性已经可以连续修改；重复规则前几次正常，但反复修改后仍会卡住，无法继续点击。
- 终端没有 Python traceback，但 `ScheduleDetailPopClassWindow` 的目标高度持续在 `373` 与 `335` 之间切换，并重复出现 `QWindowsWindow::setGeometry` warning。
- 对比两条菜单路径发现，重复规则额外在菜单项 `hovered` 时显示说明容器，并通过 `QTimer.singleShot(0, adjustSize)` 改变整个半透明顶层窗口高度；菜单关闭时又隐藏说明并再次调整高度。
- 多次悬停和选择会累积菜单事件与异步窗口几何调整，重要性菜单没有这条链，因此只有重复规则在多次操作后卡住。
- 本次将重复规则改为与重要性相同的固定几何流程：
  - 删除详情窗口内部会展开 / 收起的 `repeat_status_widget` 及其异步 `adjustSize()`。
  - 重复选项说明迁移为 `QMenu` action tooltip，不再改变详情窗口布局。
  - 重复菜单只负责弹出、选择、关闭，再执行原有重复范围确认和写库刷新。
- 不修改重复规则存储值、重复组范围确认或数据库更新接口。
- 真实连续编辑是否完全恢复仍需用户复测后确认。

第七次自动验证结果：

- `src/ui/schedule_detail_pop.py` 通过项目虚拟环境 `py_compile`。
- 无写库 offscreen 验证连续执行 20 次重复菜单弹出、选项触发和菜单关闭，进程正常完成。
- 验证过程中数据库更新与重新查询均使用内存桩，不修改 `schedule.db`。
- 静态检查确认重复菜单路径不再引用 `repeat_status_widget` 或悬停触发的窗口 `adjustSize()`。

---

## 2026-06-30 坐标显示看板架构收口

任务目标：

- 在继续调整坐标看板视觉和交互前，检查并修正样板实现与 `Final_Formulation.md` 最终架构的偏差。
- 保留已经可用的对数时间投影、点 / 线段绘制、命中检测和预览，不删除后重写。

开工前 Git 状态：

- `assets/icons/axis.svg` 已存在未提交修改，本轮不修改该文件，不将其视为本轮源码问题。
- 其余坐标看板相关源码开工前无 diff。

审查结论：

- `ScheduleAxisService` 通过 Repository 获取日程和清单数据，纯投影方法负责过滤、范围计算和带符号 `log(1 + |t|)` 映射，符合 Service / Repository 分层方向。
- `ScheduleAxisBoard` 位于 `src/ui/popups/`，作为独立辅助看板而非主视图，符合 UI 包规划。
- 原实现的主要偏差在协调边界：`SharedMoreMenu` 直接导入并创建看板、按当前窗口分别保存实例、扫描 `QApplication.topLevelWidgets()` 查找月面板详情桥接；看板也未进入统一刷新链。

实际修改文件：

- `src/utils/signals.py`
- `src/ui/components.py`
- `src/ui/main_window.py`
- `manage_instruction/Final_Formulation.md`
- `manage_instruction/Work_Log.md`

修改内容：

- `global_signals` 新增 `axis_board_requested(object)`，携带菜单所在窗口作为首次定位锚点。
- `SharedMoreMenu._on_show_axis()` 只发送显示请求，不再创建看板、不再持有看板实例、不再扫描顶层窗口或绑定详情回调。
- `MainWindow` 统一持有唯一 `axis_board` 实例，并负责首次定位、显示 / 隐藏和应用退出时关闭。
- 新增 `MainWindow.open_schedule_detail_from_axis(...)`，坐标看板不再复用语义错误的 `open_schedule_detail_from_month_panel(...)`。
- 坐标详情仍复用共享 `ScheduleDetailPop`；时间、提醒、清单编辑继续通过 `_resolve_detail_edit_target(...)` 按当前可见视图承接。
- 在既有 `MainController / RefreshCoordinator` 注册 `axis_if_visible`；日程更新统一刷新 dashboard、todo、可见周界面和可见坐标看板。
- 坐标详情内直接修改标题、描述、重要性或重复规则后，复用月界面刷新入口同步 marker / panel，再由现有信号链刷新其他视图和坐标看板。
- `Final_Formulation.md` 将旧的 `matrix_classification_service.py` 目标更正为当前实际的 `schedule_axis_service.py`，并消除“尚未实现”与“样本已接入”的状态冲突。

保持不变：

- 不修改坐标映射、动态范围、点 / 线段绘制、颜色、尺寸、纵向轨道和命中检测逻辑。
- 不修改数据库、Repository、日程字段或重复日程写入规则。
- 不修改开工前已有 diff `assets/icons/axis.svg`。

待验证：

- 从日 / 周 / 月 / 挂起窗口的更多菜单打开时，均应切换同一个坐标看板实例。
- 在共享详情中修改时间、清单或重要性后，可见看板应立即更新位置、颜色或点大小。
- 关闭主窗口时，独立坐标看板应同步关闭。
- 后续仍需确定完成日程展示策略并继续视觉细调。

自动验证结果：

- `src/utils/signals.py`、`src/ui/components.py`、`src/ui/main_window.py` 通过独立 `py_compile`。
- PyQt offscreen 请求验证通过：任意 `SharedMoreMenu._on_show_axis()` 只发出一次 `axis_board_requested(anchor_window)`，不创建局部看板实例。
- `MainWindow`、`ScheduleAxisBoard` 和 `SharedMoreMenu` 组合 import 通过。
- 静态搜索确认 `src/ui/components.py` 已无 `parent_window.axis_board`、`QApplication.topLevelWidgets()` 和月面板详情桥接依赖。
- `git diff --check` 无 whitespace error，仅有 Windows LF / CRLF 提示。

### 坐标看板右上角控制组补充

开工前状态补充：

- 用户正在试验主界面配色，`src/config.py` 已有未提交修改，本任务不修改该文件。
- `assets/icons/axis.svg` 仍为前序未提交修改，本任务不修改该文件。
- `assets/icons/set.svg` 为用户在本任务前准备的未跟踪图标，本任务正式接入坐标看板。

实际修改：

- `src/ui/popups/schedule_axis_board.py`
- `manage_instruction/Final_Formulation.md`
- `manage_instruction/Work_Log.md`
- 接入用户提供的 `assets/icons/set.svg`，文件内容不做改写。

实现内容：

- 参考待办看板，在坐标看板右上角形成“显示设置 / 置顶 / 关闭”按钮组。
- 显示设置按钮使用 `assets/icons/set.svg`，当前仅提供可点击 UI 壳和 tooltip，不保存或修改显示配置。
- 置顶按钮复用待办看板行为：切换 `WindowStaysOnTopHint`，重新显示并抬高窗口。
- 置顶状态通过 pin 图标颜色区分：未置顶为半透明灰白，置顶为纯白。
- 图标统一复用 `load_colored_svg_pixmap(...)` 进行 DPR 渲染，不在坐标看板内复制新的 SVG 染色实现。
- 关闭按钮保留原有关闭行为，并与新增按钮统一尺寸和 hover 形态。

待验证：

- 设置、pin、关闭三个按钮在不同 DPI 下不应裁切或挤压范围文字。
- pin 连续切换后窗口应保持可见，且置顶状态和图标颜色一致。
- 设置按钮当前点击无业务动作，符合占位边界。

自动验证结果：

- 使用空投影替代 Repository 数据完成 PyQt offscreen 构造，不读取或写入 `schedule.db`。
- `set.svg` 与 `pin.svg` 均成功生成非空图标。
- pin 连续点击两次后，`is_pinned` 与 `WindowStaysOnTopHint` 分别正确进入和退出置顶状态。
- 设置按钮占位点击不产生异常。

真实界面反馈与样式统一：

- 用户对照坐标看板和待办看板后确认，首版按钮组的尺寸、关闭符号和间距仍不一致。
- 坐标看板右上角按钮组改为严格复用待办看板规格：
  - 设置键、pin 键、关闭键统一为 `30x30`。
  - 设置与 pin 图标统一为 `16x16`。
  - 关闭键不再使用文本“×”，改用待办看板相同的 `assets/icons/close.png`，图标尺寸 `12x12`。
  - 设置与 pin 使用透明背景、4px 圆角和 `rgba(255,255,255,0.2)` hover。
  - 关闭键沿用右上角圆角和红色 hover。
  - 三个按钮之间取消额外 layout 间距，范围文字与按钮组之间保留 6px 间隔。
- 本次只统一视觉规格，不改变设置占位和 pin 置顶逻辑。
- PyQt offscreen 验证确认三个按钮均为 `30x30`，设置 / pin 图标为 `16x16`，关闭图标为 `12x12`，且三个图标均成功加载。

第二次真实界面反馈与定位修正：

- 用户指出待办看板按钮组紧贴窗口右上角，而坐标看板首版仍受标题内部 layout 边距约束，整体向左、向下缩进。
- 原因是首版只复用了按钮尺寸和样式，没有复用待办看板“按钮作为顶层窗口子控件并绝对定位”的方式。
- 坐标看板三个按钮改为直接以看板窗口为父对象，不再加入标题布局。
- 完全对齐待办看板定位规则：`y=10`，关闭键右边距 `10px`，pin 与设置键依次每隔 `30px` 向左排列。
- 新增 resize 定位刷新，后续若调整看板宽度，按钮组仍保持贴合右上角。
- 标题布局预留右侧 90px，防止范围文字进入按钮命中区域。
- PyQt offscreen 验证确认：显示后以及宽度变化后，关闭 / pin / 设置按钮始终分别保持右边距 `10 / 40 / 70px`，纵坐标均为 `10px`。

第三次真实界面反馈与范围文字定位修正：

- 用户实测发现“范围 ±N天”仍由标题 layout 管理，而按钮已采用窗口绝对定位，两套布局互不约束，导致范围文字覆盖设置与 pin 图标。
- 范围文字改为坐标看板的直接子控件，与按钮组采用同一定位坐标系。
- 范围文字固定在设置键正左侧，保留 6px 间距，并与 `30px` 高按钮组垂直居中。
- 每次数据范围变化、看板显示或宽度变化都会重新计算范围文字和按钮组位置。
- 标题布局不再为范围文字和按钮组承担定位，避免 layout 最小宽度把文字挤入绝对定位区域。
- PyQt offscreen 几何验证确认范围文字右沿与设置键之间保持至少 6px，二者垂直中心误差不超过 1px。

### 坐标看板按完成状态分区

- 新增显示规则：未完成日程只显示在时间轴上方，已完成日程只显示在时间轴下方。
- `AxisScheduleProjection` 新增只读字段 `is_completed`，由 `ScheduleAxisService` 根据 `status == 1` 统一计算，画布不直接解释数据库状态值。
- `_ScheduleAxisCanvas` 将轨道拆为上方未完成轨道和下方已完成轨道；同一状态区域内重叠时继续分配不同纵向轨道，不改变横向时间位置。
- `status == 2` 的隐藏日程仍不进入看板，无时间日程和待办过滤规则不变。
- 看板底部图例同步标明“线上：未完成 / 线下：已完成”。
- 本轮不改变对数映射、动态时间范围、清单颜色、重要性尺寸和详情交互。
- 修正测试输入后完成四条 marker 的 offscreen 轨道验证：两条未完成日程分别位于 `y=90/62`（轴上方），两条已完成日程分别位于 `y=150/178`（轴下方），同侧重叠成功分配到不同轨道。

### 坐标看板跨视图实时刷新与白色画布

刷新链审查：

- 周界面和月界面的 `schedule_updated` 已连接 `MainWindow._on_week_schedule_updated(...)`，会进入包含 `axis_if_visible` 的统一刷新链。
- 主界面新增、picker 修改等主窗口路径已调用 `_refresh_dashboard_todo_week()`，同样覆盖可见坐标看板。
- 缺口位于日界面卡片内部操作、完成状态切换和日界面详情直接修改：这些路径只发出 `DashboardView.req_refresh_all`，此前没有连接 `axis_if_visible`。

实际修改：

- `DashboardView.req_refresh_all` 增加到 `MainWindow._refresh_axis_if_visible` 的连接，覆盖日界面卡片删除、状态变化、拖拽排序和共享详情直接修改。
- `TodoView.req_refresh_all` 同步连接可见坐标看板刷新，避免日程 / 待办共用数据更新路径留下显示差异；待办本身仍不会投影到坐标轴。
- 周、月已有刷新连接保持不变，不复制第二套刷新逻辑。

视觉修改：

- 坐标画布区域绘制近纯白背景和轻微边框，外层看板标题区仍保留当前主题渐变。
- 坐标轴、箭头、中心刻度、时间范围文字、连接虚线和空状态文字改用 `AppConfig.COLOR_GRADIENT_START` 主题青色及其透明变体。
- 圆点和时间段主体继续读取所属清单颜色。
- 为避免白色或浅色清单 marker 消失，圆点使用主题青色细描边；时间段先绘制略宽的主题青色底线，再叠加清单色主体线。

待验证：

- 看板保持显示时，分别从日、周、月界面修改时间、清单、重要性和完成状态，marker 应即时更新。
- 白色画布上青色坐标轴、浅色清单 marker 和深色清单 marker 均应清晰可见。

自动验证结果：

- 静态连接检查确认日界面 `req_refresh_all`、周界面 `schedule_updated`、月界面 `schedule_updated` 均可到达包含 `axis_if_visible` 的刷新路径。
- 画布像素验证得到：背景 `#ffffff`、抗锯齿后的主题青色轴 `#49d0e7`、测试清单红色 marker `#ff0000`。
- `src/ui/main_window.py` 与 `src/ui/popups/schedule_axis_board.py` 通过独立 `py_compile`。

### 坐标看板下一阶段需求记录

- 本次只记录后续需求，不修改源码。
- 下一阶段需要完善截止时间（DDL）日程与起止时间段日程的不同表现：截止时间使用单点，时间段使用起止线段，其余边界语义另行审查。
- 设置按钮后续打开显示设置面板，至少包含：
  - 显示过去日程。
  - 显示完成日程。
  - 显示时间范围：1天、1周、1月、1年，四项互斥。
  - 清单及其对应颜色设置，默认沿用清单颜色；是否支持看板专用覆盖色待定。
- 看板后续根据时间范围、日程数量和上下轨道数量自适应宽高，同时受最小尺寸、最大尺寸和屏幕可用区域约束。
- 设置变化应在现有全局看板实例内重算投影、轨道和尺寸，不重新创建看板。
- 该需求已经同步写入 `Final_Formulation.md` 的坐标显示阶段，等待后续拆分执行。

## 2026-07-01 坐标轴灰色调整与月日程 panel 完成入口

### 开工状态与范围

- 本次任务开始前工作区已存在坐标看板阶段的未提交修改，涉及 `Final_Formulation.md`、坐标看板 service / signal / UI、`MainWindow`、`SharedMoreMenu`、`axis.svg` 和用户提供的 `set.svg`；另有用户自行调整的 `src/config.py`。
- 本次没有回退或覆盖上述既有修改。
- 本次新增修改文件：
  - `src/ui/popups/schedule_axis_board.py`
  - `src/ui/popups/month_day_panel.py`
  - `src/ui/month_window.py`
  - `manage_instruction/Work_Log.md`

### 坐标看板轴色调整

- `_ScheduleAxisCanvas` 新增固定轴色 `AXIS_COLOR = "#333333"`。
- 数轴主线、左右箭头、中心刻度、过去 / 现在 / 未来文字、空状态文字、marker 到数轴的连接虚线，以及浅色 marker 的轮廓统一改为该灰色及其透明变体。
- 日程圆点和时间段主体仍使用所属清单颜色，白色画布和外层主题渐变保持不变。

### 月日程 panel 右键完成状态切换

- `_MonthScheduleItemFrame` 新增右键菜单，只提供日程完成状态切换，不提供置顶、删除等额外功能。
- 未完成日程显示“完成日程”，选择后写入 `status=1`；已完成日程显示“未完成”，选择后恢复为 `status=0`。
- “完成日程”使用 `check.svg`，“未完成”使用用户新增的 `uncheck.svg`；图标和文字使用 `#333333`，选中背景使用轻量主题青色。
- `MonthDayPanel` 只新增 `schedule_status_requested(object, int)` 信号并转发行组件请求，不导入数据库，不直接写状态。
- `MonthWindow` 接收请求后调用现有 `db_manager.update_schedule_status(schedule_id, new_status)`；成功后更新当前对象状态并复用 `refresh_after_schedule_change(schedule)`。
- 完成后的统一刷新覆盖月格 marker、打开的同日 panel、对应详情弹窗和 `schedule_updated` 上游协调链，因此可见坐标看板及其他已接入视图也能同步刷新。
- 更新失败时只显示失败 toast，不伪造完成状态。

### 验证结果与限制

- `check.svg` 存在性检查通过。
- 使用 Miniconda Python 3.13 和独立临时 pycache 完成三个修改文件的 `py_compile`，语法检查通过；临时 pycache 已清理。
- 静态搜索确认完整请求链：行组件 `status_change_requested` -> `MonthDayPanel.schedule_status_requested` -> `MonthWindow._change_schedule_status_from_day_panel` -> `update_schedule_status(...)` -> `refresh_after_schedule_change(...)`。
- `git diff --check` 未发现空白错误，仅有仓库既有 LF / CRLF 提示。
- 本轮早期在 Codex 受限沙箱内启动项目 `.venv` 失败，后续已确认这是沙箱无法访问用户目录基础解释器造成的限制，不是项目 `.venv` 损坏；需要 PyQt 验证时应申请沙箱外执行。
- 需要用户实机复测：
  - 坐标轴及辅助线是否统一为 `#333333`，清单色 marker 是否仍清晰。
  - 月界面单击日期 panel 中，未完成日程右键“完成日程”后是否立即变为已完成，并同步更新月格、详情弹窗和可见坐标看板。
  - 已完成日程右键“未完成”后是否恢复未完成，并触发同一刷新链。

### 月格三角角标数字颜色调整

- 保留三角角标及原有日期日程数量缓存，不改变三角形的状态颜色规则。
- 用户进一步明确数字仍需可见，只是要接近数字所在日期格的背景色；因此数量文本最终改用月界面渐变起始色 `AppConfig.COLOR_GRADIENT_START`。
- 进一步按三角形颜色区分：白色三角形的数字使用 `AppConfig.COLOR_GRADIENT_START`，当前主题下为 `#0cc0df`；红、黄、绿、灰等其他三角形继续使用白色数字。
- 该规则避免白色三角形中的白字消失，同时保留彩色三角形原有的高对比度。
- 数量统计结构保持不变。

### 月日程 panel 完成状态图标核对

- `assets/icons/check.svg` 用于将未完成日程标记为完成。
- 用户新增的 `assets/icons/uncheck.svg` 用于将已完成日程恢复为未完成。
- 两个 SVG 均通过现有 icon loader 染为 `#333333`，不再依赖仓库中缺失的 `undo.svg`。

## 2026-07-02 坐标看板画布半透明遮罩

- 工作区开工前干净，当前分支相对 `temp/main` ahead 115。
- `src/ui/popups/schedule_axis_board.py` 中坐标画布背景由接近纯白的 `QColor(255, 255, 255, 248)` 改为 `QColor(255, 255, 255, 190)`，约为 75% 不透明度。
- 白色遮罩仍覆盖整个坐标显示框，但允许外层主题渐变轻微透出；画布尺寸、圆角、边框、数轴、marker 和交互逻辑均未改变。
- `Final_Formulation.md` 同步修正为“半透明白色遮罩 + `#333333` 数轴”，移除已过期的“纯白背景 + 主题青色数轴”描述。
- 后续 marker 视觉规则记录：DDL 竖条和时间段方块的高度按低 / 中 / 高重要性使用 `3:4:5` 比例；本次只记录，不修改 marker 形态与尺寸。

## 2026-07-02 坐标看板设置页切换动画壳

### 实际修改

- 坐标看板设置键由静态占位按钮改为可切换显示页的按钮，真实设置选项仍未实现。
- 点击设置键时，齿轮图标使用 `QVariantAnimation` 在 `0°` 与 `180°` 之间旋转，打开和关闭设置页时方向互逆。
- 齿轮使用固定 `24x24` 透明画布承载 `16x16` 图形，旋转中心固定在图标几何中心，避免旋转过程裁切或按钮布局抖动。
- 原坐标画布和图例被收纳到 `display_page`；新增透明 `settings_page`，当前只显示“显示设置 / 选项内容待实现”占位文字。
- 两个页面由 `QStackedWidget` 管理，不创建新窗口，也不改变坐标看板实例所有权。
- 页面切换采用两段 `QPropertyAnimation`：当前内容由原高度收缩到 `0`，交换页面后再从 `0` 展开到原高度。
- 看板窗口尺寸、标题区、范围文字、pin 键和关闭键均不参与收缩；切换期间会隐藏 hover 预览，避免只读浮窗残留。
- 动画执行期间忽略重复点击，完成后才允许下一次切换，避免多个动画同时修改页面几何。

### 文档同步

- `Final_Formulation.md` 已将“设置占位键”更新为“动画切换壳已完成、真实选项未实现”。

### 验证

- `src/ui/popups/schedule_axis_board.py` 通过 Python 语法编译检查。
- 静态检查确认设置按钮已连接 `_toggle_settings_page()`，收缩、页面交换、展开和状态收口方法均存在。
- `git diff --check` 未发现空白错误，仅有仓库既有 LF / CRLF 提示。
- 沙箱外执行 `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe --version` 返回 `Python 3.11.9`，确认项目 `.venv` 正常，先前失败属于 Codex 沙箱限制。
- 使用项目 `.venv` 完成 PyQt offscreen 动画验证：设置页打开后 `_settings_open=True`、当前页为设置页、齿轮角度为 `180°`；反向切换后恢复显示页和 `0°`。
- 动画前后窗口保持 `412x300`，内容区高度保持 `233px`，收缩 / 展开没有改变窗口或最终显示区域尺寸。
- 自动验证通过后仍建议用户实机观察动画视觉节奏和齿轮图形旋转中心。

### 设置动画实机反馈修正

- 用户实测发现收缩期间“坐标显示”标题会先向下移动再弹回，原因是承载标题的主 `panel` 未以 stretch 方式固定填满窗口，内容高度变化会触发外层布局重新分配。
- 外层布局改为 `outer.addWidget(panel, 1)`，主 panel 始终填满窗口可用区域；标题保存为 `self.title_label`，便于几何验证并保持顶部位置稳定。
- 用户实测发现打开设置页后底部图例说明消失，原因是图例此前属于被切换隐藏的 `display_page`。
- 图例已移出 `QStackedWidget`，并进一步脱离会受页面高度动画影响的布局，改为看板直接子控件，固定在底部位置；内容布局预留对应底部空间。
- 现在只有坐标画布和设置内容参与收缩 / 展开，标题、图例和右上角按钮均保持可见且位置固定。
- 使用项目 `.venv` 进行最终 PyQt offscreen 中间帧验证：动画前、中间帧、设置页展开后，标题纵坐标始终为 `22`，图例纵坐标始终为 `269`，图例保持可见，窗口尺寸始终为 `380x300`。
- 用户真实界面仍观察到标题在部分动画帧发生位移，说明仅固定主 panel 尺寸仍不能完全隔离 Windows 实际布局重排。
- “坐标显示”标题进一步脱离 `panel` 和 header layout，改为看板直接子控件，固定在 `(26, 22)`；header 仅保留 `24px` 高度占位，确保中间内容不会上移覆盖标题。
- 标题现在与右上按钮、范围文字和底部图例使用同一顶层坐标系，页面栈高度动画不再能改变其位置。
- 使用项目 `.venv` 对设置页打开过程按每 `20ms` 采样一次、连续检查 `25` 帧：标题始终位于 `(26, 22)`，图例始终位于 `(26, 269)`，窗口始终为 `380x300`，逐帧固定验证通过。

### 设置内容框收缩方向修正

- 用户实测指出页面栈原先会从上下两侧同时向中间收缩，不符合“从上向下收起”的设计。
- 原因是布局通过 `maximumHeight` 改变页面高度时，会自动重新分配上下剩余空间，导致页面的顶边和底边同时移动。
- 新增固定尺寸的 `content_host` 作为中间显示视口，`QStackedWidget` 改为该视口的直接子控件，不再由垂直布局控制动画位置。
- 收缩与展开改为直接动画 `content_stack.geometry`：顶边始终固定在视口 `y=0`，收缩时只有底边向上移动，切换页面后由顶部向下展开。
- `content_host` 尺寸变化时通过 event filter 同步页面几何；动画期间暂停自动同步，避免覆盖动画帧。
- 项目 `.venv` 的 PyQt offscreen 逐帧验证确认：页面栈相对看板的纵坐标始终为 `46`，高度从 `214` 降至接近 `0` 后恢复到 `214`；正反切换最终分别进入设置页和显示页，窗口始终保持 `380x300`。

### 设置占位文字固定层

- 用户实测发现“显示设置 / 选项内容待实现”仍属于设置页布局，会在设置页展开时随页面高度移动，不能直接稳定显示在中间。
- 占位文字从 `settings_page` 布局中移除，改为 `content_host` 的直接子控件，几何范围始终与固定显示视口一致并使用居中对齐。
- 打开设置时，坐标画布先收缩到零；页面交换时才显示固定占位文字。关闭设置时，文字保持固定直到页面交换，再隐藏并展开坐标画布。
- 占位文字不参与 `content_stack.geometry` 动画，并设置鼠标事件穿透，为后续在设置页放置真实交互控件保留空间。
- 项目 `.venv` 的 PyQt offscreen 逐帧验证获得 `16` 个文字可见动画帧，所有帧均固定在 `(26, 46)`、尺寸均为 `328x214`，与 `content_host` 完全一致；关闭设置后文字正确隐藏。

## 2026-07-02 坐标看板命名统一

- 更多菜单用户可见入口由“坐标显示”改为“坐标看板”。
- 独立看板左上标题由“坐标显示”改为“坐标看板”，与“待办看板”的命名方式保持一致。
- 内部 `ScheduleAxisBoard`、`axis_board_requested`、`ScheduleAxisService` 等代码标识保持不变，不为显示文案制造无意义重命名。
- `Final_Formulation.md` 中面向阶段和功能的旧称同步统一为“坐标看板”；历史日志保留原执行名称。
- 本次不修改用户正在试验的 `src/config.py` 配色内容。

## 2026-07-02 主窗口置顶偏好同步与过期日程透明度调整

### 开工前状态

- 当前分支相对 `temp/main` ahead 115。
- 开工前已有 diff：`manage_instruction/Final_Formulation.md`、`manage_instruction/Work_Log.md`、`src/config.py`、`src/ui/components.py`、`src/ui/popups/schedule_axis_board.py`。
- 本轮保留既有坐标看板与文档改动，不修改用户正在试验的 `src/config.py` 配色。

### 主窗口置顶偏好

- 新增 `src/utils/window_preferences.py`，使用 `QSettings("Wanji", "DesktopSchedule")` 持久化 `window/primary_always_on_top`。
- 未写入过偏好时默认保持项目原行为，即主窗口置顶。
- 日界面和待办界面共用 `MainWindow`；周界面、月界面在构造时读取同一偏好。
- `SharedMoreMenu` 和旧的 `MainWindow.toggle_pin_mode()` 入口现在都会写入同一偏好，并通过 `global_signals.primary_window_pin_changed(bool)` 同步主窗口、周窗口和月窗口。
- 主窗口偏好下次启动仍会恢复，不再由 `MainWindow` 写死为始终置顶。

### 独立看板置顶规则

- 坐标看板和待办看板新增显式 `set_pinned(enabled)` 接口，现有 pin 按钮仍只改变当前看板实例的临时状态。
- 两个看板每次从隐藏状态重新打开时，都读取主窗口持久化偏好并重置默认置顶状态。
- 看板打开后可以独立取消或开启置顶；该临时操作不写入主窗口偏好，也不影响年月日/待办主视图。
- 看板关闭或隐藏后再次打开，仍以当时的主窗口偏好为准，符合“默认跟随、使用期间可独立调整”的边界。

### 未完成过期日程视觉

- 用户澄清目标是日界面中“未完成且已过期”的日程卡片，不是已完成日程，也不是待办项目。
- 日界面 `ScheduleCard` 的已完成标题、时间、提醒图标透明度全部恢复原状。
- 待办界面 `TodoCard` 的已完成标题恢复原状，且不新增过期判断；待办没有日程时间轴语义。
- 仅将日界面未完成过期日程卡片背景由实色 `#bebebe` 改为 `rgba(190, 190, 190, 0.7)`，即灰色 70% 不透明、30% 透明。
- 过期判断、文字颜色、边框、排序、数据库字段和完成/未完成切换逻辑均未改变。

### 验证

- `window_preferences.py`、signals、components、main/week/month、两个看板和日界面卡片相关文件均通过 `py_compile`。
- `QSettings` 往返验证通过：临时切换偏好后可读取新值，并已恢复测试前值。
- PyQt offscreen 验证通过：`MainWindow`、`WeekWindow`、`MonthWindow` 能同时接收并应用同一置顶状态。
- PyQt offscreen 验证通过：坐标看板和待办看板可在本次打开期间独立取消置顶，隐藏后再次打开会恢复为主窗口偏好。
- 最终 diff 核对确认 `src/ui/todo.py` 无本轮差异，`src/ui/dashboard.py` 只保留未完成过期卡片背景透明度调整。

## 2026-07-02 待办看板标题统一与天气看板交互壳

### 待办看板置顶便签标题

- `StickyNoteCard` 置顶状态不再把标题改为金色 `#FFD700`，置顶和普通便签标题统一使用白色。
- 置顶便签原有的较亮背景、白色边框、排序和右键操作保持不变，仅取消标题颜色差异。

### 天气看板交互壳

- 新增 `src/ui/popups/weather_board.py`，提供独立、可拖动的渐变天气看板壳和关闭键。
- `WeatherIconLabel` 新增 `double_clicked` 信号；内部 loading/weather 两个标签层设置鼠标事件穿透，确保真实双击由外层天气控件统一接收。
- 日界面和待办界面共用主 Header 天气图标；周界面和月界面使用各自天气图标，四个入口统一由 `MainWindow` 控制同一个天气看板实例。
- 双击天气图标时切换天气看板显示/隐藏；关闭键可直接关闭。重新打开时按当前可见主界面定位到窗口右侧，并执行屏幕边界回退。
- 天气看板每次打开时跟随主窗口置顶偏好；本轮未增加独立 pin 按钮。
- 主窗口关闭时同步关闭天气看板，未改天气 API 请求、刷新定时器和现有实时天气显示。

### 看板内记录的后续天气规则

- 过去日期统一显示问号天气图标，温度显示 `--°C`。
- 今天显示当前实时天气和当前温度。
- 明天及以后在 API 实际提供的预报天数内显示预报天气；超出预报上限后显示问号天气图标。
- 非今天日期的温度统一显示 `--°C`。
- 天气看板最终可展示的天数以后以 API 实际返回范围为准，不在本轮写死 14 或 15 天。

### 验证

- 天气控件、天气看板、主窗口、日界面卡片、待办界面和待办看板相关文件通过 `py_compile`。
- PyQt offscreen 验证通过：日、周、月、待办四个入口均可打开同一天气看板；再次双击可收回，关闭键可关闭。
- PyQt offscreen 验证通过：待办看板置顶便签标题保持白色。
- PyQt offscreen 验证通过：仅日界面未完成过期日程使用 `rgba(190, 190, 190, 0.7)` 背景；已完成日程和待办完成态保持原样。

## 2026-07-03 坐标看板前后一月交互 demo

### 开工前状态

- 当前分支相对 `temp/main` ahead 116，上一阶段看板、置顶偏好、天气看板等改动已提交。
- 开工前仅 `src/config.py` 存在用户配色试验 diff；本轮不修改该文件。

### 月度范围与动态尺寸

- 本轮固定演示范围为“过去一个月到未来一个月”，每侧按 30 天计算。
- 看板不再采用固定 `380px` 或固定扩大 `4/3` 的宽度。
- 月度虚拟数轴总长度按当前屏幕可用宽度的 `1/2` 生成。
- 默认看板显示框按屏幕可用宽度的 `3/8` 生成，因此初次打开只显示原点前后约一周，月内其余内容保留在虚拟画布外。
- 看板设置最小尺寸 `420x260`；窗口四边和四角均可拖动缩放，显示框通过现有布局始终保持外层左右间距。

### 对称对数映射

- `ScheduleAxisService.map_delta_to_x(...)` 增加可配置 `log_scale`，并新增逆映射 `map_x_to_delta(...)`。
- 新增 `solve_log_scale(...)`，按月度总范围和默认一周视口求解对数参数。
- 过去和未来分别映射到数轴左右两半，使用相同参数并以原点镜像对称。
- 当前月度 demo 数值验证：在虚拟轴长度 `1280px`、默认可见比例 `0.75` 时，`-7天/+7天` 分别映射到左右对称位置，正反映射误差低于 `1e-6`。

### 虚拟画布交互

- `_ScheduleAxisCanvas` 新增独立的虚拟轴宽度、视口中心、缩放比例和纵向偏移，不再把数据范围直接压进当前控件宽度。
- 鼠标在空白区域按住拖动可同时平移时间范围和纵向轨道；拖动期间使用闭合手型，普通空白区域使用张开手型。
- 鼠标滚轮以光标所在位置为缩放锚点，支持 `0.1~8.0` 范围内缩放，并限制视口中心不越出虚拟数轴。
- 看板横向拉宽时显示更多时间内容，纵向拉高时显示更多轨道；调整窗口大小不改变选定的前后一月数据范围。
- 数轴左右文字显示当前视口边界对应的过去/未来时长，不再误写成整个虚拟范围边界。

### 日程 marker demo

- 原点纵向位置改为显示框高度的约 70%，未完成日程在轴上方，已完成日程在轴下方。
- DDL / 单时间日程使用 `2px` 宽的纯色竖线；起止时间日程使用宽度与映射后持续时间对应的纯色横条。
- 两类 marker 本体均不使用描边或圆角；默认状态不常驻显示到数轴的虚线，低/中/高重要性厚度分别为 `9px / 12px / 15px`，保持 `3:4:5` 比例。
- 同一区域日程使用动态轨道避让，不再限制为固定三条轨道；轨道按实际 marker 高度紧凑排列，相邻日程边缘至少保留 `1px` 间隙。
- 同一时刻、同一清单颜色的多个 DDL 会进入不同纵向轨道，不会重叠成一条线；超出当前高度的内容可通过纵向拖动或拉高看板查看。
- marker 颜色继续来自所属清单，悬停只读预览和单击详情弹窗入口保持不变。
- 鼠标悬停 DDL / 单时间 marker 时，显示从竖线到数轴的辅助虚线，并在数轴附近显示具体时间；移走鼠标立即隐藏。
- 鼠标悬停时间段 marker 时，起止两端分别显示到数轴的辅助虚线，并分别标注开始时间和结束时间；生命周期与既有 hover 只读预览一致。
- 当前数据库内 3 个有效日程清单的颜色字段均为 `#0cc0df`，因此当前 marker 实际显示为同色；绘制逻辑仍逐项读取清单 `color` 字段，没有写死统一颜色。

### 显示框与看板布局修正

- 显示框外沿改为纯白 `2px` 边框，用于区分半透明白色显示框与渐变看板背景。
- 原底部说明文字与“范围 ±1个月”合并为顶部单行新标注，顺序为说明在前、范围在后。
- 顶部新标注按标题和设置键之间的实际可用宽度做右侧省略；缩窄窗口时不换行、不覆盖按键。
- 移除底部说明占位后，将显示框底边距由 `30px` 改为 `16px`，现在显示框左、右、下三侧到看板可见边沿的距离一致。

### 窗口拉伸修正

- 第一版曾新增四边和四角共 8 个独立透明拖拽控件，将命中宽度扩大到 `12px`；实机复核确认命中改善，但拖动时控件自身随窗口反复重新定位，边角出现晃动。
- 已删除上述 8 个移动控件，改为给看板现有子控件统一安装边缘事件过滤；鼠标位于看板四边或四角 `12px` 范围内时，由事件过滤器识别对应方向。
- Windows / Qt 支持时优先调用 `QWindow.startSystemResize(...)`，将拖动过程交给系统窗口管理器，避免 Python 端每次鼠标移动都重排事件接收控件。
- 若当前平台不支持原生缩放，则回退到原有“初始矩形 + 全局鼠标位移 + setGeometry()”路径；父窗口自身的边缘判断也继续保留。
- 拖动标题栏、显示框内部平移和滚轮缩放逻辑不变。Windows 实机是否完全消除晃动仍需用户手动复核。

### 标题位置微调

- 将“坐标看板”标题的固定纵坐标由 `22px` 调整为 `18px`，整体上移 `4px`；顶部新标注和右上角按键位置保持不变。
- 顶部新标注不再按右上角按键组高度垂直居中，改为根据“坐标看板”标题的实际底边计算纵坐标，使两段文字的下沿处于同一水平线。

## 2026-07-03 日界面添加页详情区高度修正

- `AddScheduleView` 展开详情时，后续重要性和重复下拉框的上沿仍会露在滚动区域底部，形成两个不完整的圆角边框。
- 日界面详情文本框曾由 `80px` 提高为 `110px`；实机复核发现“收起”按钮下沿被遮挡，最终调整为 `100px`，兼顾属性行裁剪和详情区底部控件完整显示。
- 详情框不再写死旧青色 `rgba(12, 192, 223, 0.9)`；新增 `StyleManager.derive_surface_rgba(...)`，默认读取 `AppConfig.COLOR_GRADIENT_START`，通过 `QColor.darker(115)` 降低亮度并应用 `0.9` 透明度。
- 新增 `StyleManager.get_detail_editor_style()` 统一生成详情框普通态和聚焦态 QSS，为后续主题语义色及 JSON 局部覆盖预留单一入口。
- 本轮不修改周界面和月界面添加页，不修改重要性、重复控件及保存逻辑。

## 2026-07-03 皮肤 JSON 架构补充与周界面工具栏定位修正

### 皮肤架构文档

- 对照 `Final_Formulation.md` 既有 ThemeManager / Skin Preset / QSS 路线，确认 JSON 局部覆盖适合作为主题数据层，不应替代 QSS 或允许注入任意样式。
- 在“实现皮肤功能”下补充完整的默认令牌、JSON 局部覆盖、派生颜色、显式语义覆盖、白名单校验和运行时 Theme Tokens 方案。
- 明确主题合并顺序，保证普通皮肤只修改基础主色即可自动生成协调组件颜色，复杂撞色皮肤可只覆盖需要特殊处理的语义键。

### 周界面五键组定位

- 原搜索框固定高度为 `18px`，视图选择器固定高度为 `22px`；二者切换时改变 `tools_layout` 的内容总高度，垂直居中布局随之把上方五键组向上移动。
- 新增固定高度 `22px` 的 `bottom_action_container`，将搜索框和视图选择器放入同一个固定承载区并垂直居中。
- 搜索框尺寸仍为 `123x18px`，视图选择器仍为 `124x22px`；只固定布局占位高度，使五键组始终保持视图选择器展开状态下的纵向位置。
- PyQt offscreen 验证通过：搜索框状态与视图选择器展开状态下，`btn_view_toggle` 相对周窗口的纵坐标均为 `10px`；固定承载区高度为 `22px`。
- `week_window.py`、`add_view.py`、`styles.py` 通过 `py_compile`，`git diff --check` 无内容错误。

### 验证

- `schedule_axis_service.py` 与 `schedule_axis_board.py` 通过 `py_compile`。
- 月度对数映射、逆映射和左右对称数值验证通过。
- PyQt offscreen 验证确认默认视口左右边界约为 `-168h/+168h`，即原点前后一周。
- PyQt offscreen 验证确认窗口横向增加 `120px`、纵向增加 `80px` 后尺寸和内部显示框同步更新。
- PyQt offscreen 模拟拖动后视口中心和纵向偏移正确变化；滚轮后缩放比例由 `1.0` 增至 `1.18`。
- PyQt offscreen 构造同一时刻的低/中/高三个 DDL，确认厚度为 `9/12/15px`、分配到三条不同轨道；后续按 UI 复核将轨道边缘最小间距调整为 `1px`。
- 临时渲染复核确认 DDL 为平头竖线、时间段为直角横条，未残留圆角、外描边或虚线连接。
- PyQt offscreen hover 时间段 marker 验证通过：进入时绘制起止两侧辅助虚线和时间标签，移到空白区域后 hover 状态立即清除。
- PyQt offscreen 像素检查确认显示框中线边缘为白色；布局检查确认显示框左、右、下三侧间距均为 `16px`。
- PyQt offscreen 将看板缩至最小 `420px` 宽，确认顶部新标注以省略号结束；右边缘拉伸验证将宽度稳定增加到 `500px`。
- PyQt offscreen 环境不支持 `startSystemResize()`，验证其可正确返回失败并进入手动回退；右边缘回退缩放将窗口宽度由 `500px` 增至 `580px`。
- 确认当前看板 12 个既有子控件均已安装边缘事件过滤，没有残留独立透明拖拽控件。
- 临时渲染截图检查完成后已删除，没有留下测试图片或数据库写入。
## 2026-07-03 日界面时间选择页顶部间距微调

- 本轮仅调整日界面添加日程使用的 `TimePickerView`，不修改周界面、月界面时间选择页。
- 将“设置时间”标题栏固定高度由 `60px` 调整为 `70px`，使标题与日期按钮/日历区域之间增加 `10px` 垂直距离。
- 目的：启用开始时间后，将页面底部的快捷时长按钮继续压在当前可视范围之外，避免按钮上沿局部露出。
- 本轮只审查既有颜色来源，不修改日界面保存按钮、日历箭头、星期栏、选中日期、启用开关或确定按钮的颜色。
- `py_compile src/ui/time_picker.py` 通过。
- `400x600` offscreen 构造确认日期按钮相对页面纵坐标为 `80px`，较原布局下移 `10px`；启用开始时间后快捷时长区仍约有 `21px` 与滚动视口相交，需以实机观感决定是否继续增加间距或改为显式裁剪。
- 颜色审查确认：日界面保存按钮和时间页确定按钮均为白底、旧青色 `#0cc0df` 文字；日历选中日期及共享 `IOSSwitch` 启用背景写死为 `#0cc0df`；日历左右箭头写死为相近但不同的 `#11c1df`。日历内部水平表头实际隐藏，界面中可见的星期行主要使用 `alternate-background-color: #e3fcf9`，不是后备 `QTableHeaderView::section` 中的白底。上述颜色均未读取当前主题渐变上下沿，且不是主题色半透明值。

## 2026-07-03 日界面添加与时间控件主色动态化

- 将日界面添加页“保存”按钮文字、时间选择页“确定”按钮文字改为读取 `AppConfig.COLOR_GRADIENT_START`；按钮白色背景保持不变。
- 将 `StyleManager.get_calendar_style()` 的选中日期背景改为读取 `AppConfig.COLOR_GRADIENT_START`。
- 将共享 `IOSSwitch` 的启用背景改为读取 `AppConfig.COLOR_GRADIENT_START`；关闭态灰色和白色滑块保持不变。
- 本轮不修改日历左右箭头 `#11c1df`，也不修改星期栏的实际绘制颜色；仅继续审查其与主题色的关系。
- `py_compile` 通过；offscreen 构造确认当前测试主题上沿 `#3A29FF` 已进入保存按钮、确定按钮和日历选中背景，启用状态的共享开关实际采样颜色同为 `#3A29FF`。
- offscreen 检查确认 `QCalendarWidget` 的内部水平表头处于隐藏状态，因此截图中的浅青色星期行来源是 `alternate-background-color: #e3fcf9`，不是 `QTableHeaderView::section` 的白色后备规则。

## 2026-07-03 日界面时间日历派生色试版

- 新增 `StyleManager.mix_colors(...)`，按固定比例混合两个颜色，为主题语义色提供统一计算入口。
- 日界面时间选择器的左右月份箭头不再写死 `#11c1df`，改为“渐变上沿主题色 98% + 白色 2%”。
- 日历星期栏不再写死浅青色 `#e3fcf9`，改为“渐变上沿主题色 10% + 白色 90%”。
- 同时更新实际生效的 `alternate-background-color` 与隐藏水平表头的后备背景，避免不同平台出现两套颜色。
- 本轮不修改周界面时间选择器中独立设置的左右箭头颜色。
- `py_compile` 与 offscreen 日历构造通过；当前主题上沿 `#3A29FF` 派生箭头为 `#3e2dff`、星期栏为 `#ebeaff`，图标像素和 QSS 均验证命中。
- 以旧主题上沿 `#0cc0df` 计算时，箭头为 `#11c1e0`、星期栏为 `#e7f9fc`，与原写死的 `#11c1df`、`#e3fcf9` 保持相近视觉。
- 根据实机观感试调，星期栏背景混合比例由“主题上沿 10% + 白色 90%”改为“主题上沿 20% + 白色 80%”；箭头比例不变。
- `py_compile` 与派生值检查通过；当前配色生成星期栏 `#dcecd8`，旧青色主题 `#0cc0df` 下会生成 `#cef2f9`。

## 2026-07-03 挂起窗口顶部渐变切片同步

- 日、周、月三个挂起窗口不再使用固定旧青色 `SUSPEND_GRADIENT_START/END`，统一读取主界面的 `COLOR_GRADIENT_START/END`。
- 挂起窗口不再把完整渐变压缩进 `24/30px`，改为保存原界面的完整渐变跨度，只绘制其顶部与挂起条等高的颜色切片。
- 日界面挂起前传入当前主窗口高度；月界面传入月窗口高度；周界面普通态传入 `top_container` 高度，编辑态传入整个周窗口高度。
- 周、月挂起窗口补齐 `skin_changed -> update`，与日界面挂起窗口保持一致。
- 保留 `SUSPEND_GRADIENT_START/END` 配置字段但当前默认绘制不再使用，为后续 JSON 特殊覆盖方案预留迁移空间。
- `py_compile` 通过；offscreen 分别以日 `600px`、周普通态 `125px`、月 `480px` 为源渐变高度进行像素验证，挂起条中部实际颜色与原渐变同一纵坐标的理论颜色 RGB 差值均为 `0`。

## 2026-07-03 周界面操作按钮主题色同步

- 周界面日期选中方块暂不修改；确认原 `rgba(0, 100, 100, 0.4)` 为手工固定深青色，不存在唯一的旧主色反推公式。
- 备选换算方案：主题上沿与黑色约各混合 `50%`，再以 `40%` 透明度覆盖原渐变，可保持选中块与不同主题处于同一色系。
- 周添加页“保存”按钮文字、周时间页“确定”按钮文字、周提醒页“确定”按钮文字与已选提醒预设背景改为读取 `AppConfig.COLOR_GRADIENT_START`。
- 周时间页左右月份箭头与日界面保持一致，使用“主题上沿 98% + 白色 2%”派生色。
- 公共清单选择器的“确定”文字及新建清单确认按钮改为主题上沿色；后者悬停色为主题上沿与黑色按 `90%/10%` 混合。该公共组件改动同步作用于日、周、月入口。
- 公共清单选择器中的清单项圆点当前仍固定为 `#0cc0df`，并未读取数据库清单颜色；它不属于本轮按钮范围，因此暂不修改。
- `py_compile` 与 offscreen 构造通过；当前主题上沿 `#4FA23B` 已进入周保存、时间确定、提醒确定/已选预设、清单确定/新建确认，周时间箭头实际像素命中派生色 `#53a43f`。

## 2026-07-03 周日期选中块主题派生与清单圆点审查

- 周日期选中块不再固定使用 `rgba(0, 100, 100, 0.4)`；改为先将主题渐变上沿与黑色按 `50%/50%` 混合，再以 `40%` 透明度覆盖原背景。
- 今天日期的金色文字、普通日期透明背景及白色半透明 hover 效果保持不变。
- 日界面和周界面的清单选择页都直接使用公共 `ListPickerView`；其 `CategoryCard` 圆点固定为 `#0cc0df`，构造函数只接收清单 ID、名称和选中状态，没有接收数据库颜色。
- 月界面使用 `MonthListPickerView(ListPickerView)`；父类创建卡片后，月界面又把圆点缩为 `6px` 并再次固定为 `#0cc0df`。
- 数据层的 Category 已保存 `color` 字段，`get_active_categories(...)` 返回的清单对象也包含该字段；当前断点在 UI：`load_data(...)` 创建 `CategoryCard` 时未传 `cat.color`。
- 新建清单的数据层默认颜色同样是 `#0cc0df`。后续若要展示真实清单色，需要给 `CategoryCard` 增加颜色参数、由公共 `load_data(...)` 传入 `cat.color`，并取消月界面的旧青色覆盖；本轮只审查，不修改圆点。
- `py_compile` 与 offscreen 构造通过；当前主题上沿 `#4FA23B` 派生选中基础色 `#28511e`，最终 QSS 为 `rgba(40, 81, 30, 0.4)`；旧青色主题按同一公式派生为 `#066070`。

## 2026-07-03 周选中块亮度与月添加控件主题适配

- 周日期选中基础色由“主题上沿 50% + 黑色 50%”调整为“主题上沿 70% + 黑色 30%”，最终透明度仍为 `40%`，降低选中块的黑重感。
- 月界面紧凑清单页的新建确认按钮、确定按钮及选中勾改为主题上沿色；清单圆点仍保留原状，等待单独接入清单业务颜色。
- 月界面紧凑开关启用背景、时间页确定按钮、提醒页已选预设与确定按钮、添加页保存按钮、重要性/重复下拉选中项全部改为读取 `AppConfig.COLOR_GRADIENT_START`。
- 月界面新建清单确认按钮的 hover 色按“主题上沿 90% + 黑色 10%”派生。
- 月界面左栏专用时间日历设置为 `SingleLetterDayNames`，星期标题显示为“一、二、三、四、五、六、日”，不修改日界面和周界面日历格式。
- `py_compile` 与 offscreen 构造通过；当前主题下周选中基础色派生为 `#0f7d51`，最终 QSS 为 `rgba(15, 125, 81, 0.4)`。
- 月清单、时间、提醒、添加四个组件的目标控件均验证命中当前主题上沿；`month_window.py` 中剩余的唯一旧青色 `#0cc0df` 是本轮明确保留的清单圆点。
- 日历模型星期行代码点验证为 `一、二、三、四、五、六、日`，确认不是仅修改枚举但仍显示省略号。

## 2026-07-03 月时间日历中文单字星期与清单圆点主题化

- 实机确认 `SingleLetterDayNames` 在当前 locale 下显示为英文 `M/T/W/T/F/S/S`；问题不是宽度不足，而是日历语言环境未固定。
- 月界面左栏专用时间日历显式设置为中文（中国）locale，并继续使用 `SingleLetterDayNames`，目标星期行为“一、二、三、四、五、六、日”；日、周日历不受影响。
- 根据本轮明确规则，公共 `CategoryCard` 圆点由固定 `#0cc0df` 改为 `AppConfig.COLOR_GRADIENT_START`，因此日、周清单页随主题上沿变化。
- 月界面紧凑清单页仍保留 `6px` 圆点尺寸，但颜色同样改为主题上沿；本轮不接入数据库 `cat.color`。
- 当前 PyQt6 使用 `QLocale.Country.China` 枚举；设置中文 locale 后显式恢复周一为每周首日，避免默认顺序变成“日、一、二、三、四、五、六”。
- `py_compile` 与 offscreen 构造通过；日历模型星期代码点最终为“一、二、三、四、五、六、日”。当前主题上沿 `#16B374` 已同时进入公共 `8px` 圆点和月界面紧凑 `6px` 圆点。

## 2026-07-03 小型提示弹窗与月日程弹窗主题同步

- 月界面鼠标悬停预览的日期标题不再固定使用旧青色 `#0cc0df`，改为读取 `AppConfig.COLOR_GRADIENT_START`；白底、深灰正文和既有边框保持不变。
- 月界面单击日期打开的 `MonthDayPanel` 不再固定使用旧青色渐变 `#0cc0df -> #71dce8`，改为读取当前主题的 `COLOR_GRADIENT_START -> COLOR_GRADIENT_END`。
- 全局原生 `QToolTip` 边框及顶栏自绘天气提示框边框改为主题上沿色，因此天气提示等小型信息框会随主题变化。
- 日、周添加页和公共清单页的普通自绘提示框默认边框同步读取主题上沿色；明确传入的错误提示红色 `#ff4d4f` 保持不变。
- 日程详情弹窗外壳原本已读取当前主题渐变；非周界面的详情框背景仍固定为 `#11c1df`，周界面详情框仍为白底。本轮只审查，不修改该分支。
- 颜色关系评估：旧主题上沿 `#0cc0df` 与详情框 `#11c1df` 的通道差为 `(+5, +1, 0)`；用“主题上沿 98% + 白色 2%”计算得到 `#11c1e0`，仅蓝通道相差 1，可作为跨主题近似复现原设计的稳定公式。若后续需要更明显层次，应改为独立 `detail_surface` 语义色覆盖，而不是继续堆固定色。
- 使用工作区 bundled Python 完成上述 Python 文件的 `py_compile`，语法检查通过。
- 后续已在沙箱外使用项目 `.venv` 补齐 `py_compile` 与 PyQt offscreen 构造验证：当前主题 `#17BE7B -> #36C38A` 已进入月 hover 标题、全局 tooltip、日/周/清单普通自绘提示框；月单击 panel 顶部/底部采样分别为 `#18be7b/#35c38a`，与主题渐变端点仅存在绘制插值取整差异。

## 2026-07-04 月/周界面广域窗口拖动

- 新增公共 `WindowDragController`，通过应用级事件过滤覆盖窗口现有及后续动态创建的子控件，不再要求鼠标必须按住顶栏才能移动月、周窗口。
- 拖动采用系统 `startDragDistance()` 阈值：按下后未移动仍执行原单击/双击；超过阈值才移动窗口，并在实际拖动后吞掉释放事件，避免工具按钮被误触。
- 月界面的日期格、天气图标、工具按钮、普通文字和空白区域均可作为拖动起点；开始拖动时关闭月 hover 预览和视图选择器。
- 周界面的日期块、七列空白区域、天气图标、工具按钮、普通文字和背景均可拖动；七列空白原有按下选中日期逻辑保持不变。
- 明确排除文本输入框、详情编辑框、下拉框、数值/时间滚轮、滑动条及其子控件；周日程卡片及其全部子控件额外按类名排除，保留原跨日期拖动行为。
- 删除月窗口“仅顶部 24px”手工拖动逻辑和周窗口“仅顶部区域”手工拖动逻辑，统一由公共控制器处理；周窗口点击空白关闭视图选择器的既有行为保留。
- 项目 `.venv` 下 `py_compile` 通过。
- PyQt offscreen 拖动验证通过：月日期格、月天气图标、月工具按钮和周空白列均按 `35x24px` 位移窗口；拖动工具按钮未触发其点击信号；月搜索框不移动窗口；周日程卡片后代被正确排除。
- PyQt offscreen 点击回归通过：月工具按钮单击、天气图标双击、月日期格单击、周日期块单击及周空白列选日均保持原行为。

## 2026-07-04 广域拖动 helper 架构收口

- 对照 `Final_Formulation.md` 的“纯 UI helper 优先进入 `src/ui/utils/`”规则，将 `WindowDragController` 从 `src/ui/common/` 移至 `src/ui/utils/`，月、周窗口同步更新导入路径。
- 删除公共 helper 的 `excluded_class_names` 参数和按类名字符串判断逻辑，避免组件重命名后排除规则静默失效。
- `WeekScheduleCard` 改为设置动态属性 `windowDragDisabled=True`；公共 helper 只识别通用属性和输入控件类型，不依赖具体业务窗口或卡片类。
- 删除 `MonthWindow`、`WeekWindow` 中已不再使用的旧 `drag_pos` 实例状态。
- 行为边界未改变：月/周广域拖动、日期点击、天气双击、工具按钮点击及周日程卡片跨日期拖动规则沿用上一轮验证结果。
- 项目 `.venv` 下 `py_compile` 通过；PyQt offscreen 冒烟确认月/周控制器均来自 `src.ui.utils.window_drag_controller`，周日程卡片动态属性和排除判断生效。

## 2026-07-04 坐标看板端点裁剪与主题轴色

- 坐标看板 marker 的实际显示范围限制在当前可见数轴的左右端点之间。
- 完全位于当前数轴端点外的单时间点和时间段不再参与轨道分配、绘制或鼠标命中，避免隐藏日程挤占可见轨道。
- 跨越可见端点的时间段会截断到端点后显示；DDL 竖线仍按原宽度绘制，并由画布 clip 防止半像素越界。
- marker 命中区域同步裁剪到数轴端点；hover 辅助虚线和时间标签与 marker 一起受水平 clip 限制。
- 数轴、两端箭头、中心刻度、范围文字、hover 虚线及时间标签由固定 `#333333` 改为读取 `AppConfig.COLOR_GRADIENT_START`。
- 项目 `.venv` 下 `py_compile` 通过。
- PyQt offscreen 验证：完全位于左端点外的 marker 被过滤，跨左端点时间段截为 `20px -> 200px`，可见 DDL 位于 `200px`；全部 marker 与命中区域均处于 `20px -> 380px` 范围。当前主题顶部色为 `#0066cc`，1.5px 抗锯齿轴线采样为 `#3f8bd8`，其 RGB 距离明显更接近主题色而非旧 `#333333`。

## 2026-07-04 日程详情框主题适配与来源窗口置顶继承

- 开工前已有未提交 diff：`src/ui/popups/schedule_axis_board.py` 和 `manage_instruction/Work_Log.md`，属于上一轮坐标看板端点裁剪与主题轴色工作；本轮保留且未改写其行为。
- 共享 `ScheduleDetailPop` 的非周界面详情框不再固定使用旧青色 `#11c1df`，改为复用日界面添加页详情填写框的语义公式：主题渐变上沿加深 `115%`，透明度 `0.9`。
- 周界面详情弹窗继续保留白底详情框和灰色文字，避免破坏周界面白色内容区的既有适配。
- `ScheduleDetailPop` 新增统一 `set_pinned(...)`，内部复用 `set_window_pin_state(...)`；用户打开弹窗后仍可独立切换置顶，不会反向修改来源窗口。
- 日界面日程详情弹窗创建时读取当前主窗口 `WindowStaysOnTopHint`，初始置顶与日界面一致。
- 周界面日程详情弹窗创建时显式读取当前 `WeekWindow` 的置顶状态，避免因共用 `DashboardView` 而错误继承隐藏的日界面窗口状态。
- 坐标看板衍生日程详情弹窗创建时读取坐标看板当前 `is_pinned`，因此看板临时取消或启用置顶都会作用于随后新打开的详情弹窗。
- 本轮未修改待办页和月界面详情弹窗的初始置顶规则，保持任务范围精确。
- 项目 `.venv` 下 `py_compile` 通过。后续补齐真实日期测试夹具并完成 PyQt offscreen 验证：日界面与坐标看板来源的详情框均命中主题派生色 `rgba(0, 89, 177, 0.90)`，周界面仍为白底；弹窗在显示前继承置顶以及显示后独立取消置顶均通过。

## 2026-07-04 日界面日历弹窗强调色主题适配

- 日界面 `CalendarPop` 的顶部导航栏、日期选中背景和日历菜单边框不再固定使用旧青色 `#11c1df`。
- 三处统一使用“主题渐变上沿 98% + 白色 2%”派生的 `calendar_accent`，保持旧青色主题下的原有视觉关系并适配其他主题。
- 每次 `show_at(...)` 弹出日历前重新执行 `_apply_theme()`，保证运行时更换主题后再次打开日历会使用最新主题色。
- 后续实机发现顶部拖动失效；核查确认颜色 diff 未删除拖动代码，而是原 `eventFilter(...)` 缺少鼠标按下时初始化 `drag_pos` 的分支。现已补齐导航栏左键按下、移动、释放的完整拖动链路。
- 今天及未来未完成日程的状态圆点改为复用同一个 `calendar_accent`；过去未完成的灰色 `#999999` 和全部完成的绿色 `#05e92a` 保持不变。
- 翻月后相同日号出现的浅色框确认是 `QCalendarWidget` 私有表格保留的键盘当前索引。曾尝试在翻月后清空该索引并恢复真实选择项，但实机复测导致后续月份日期网格无法绘制，因此该方案已完整回退，保留 Qt 原生浅色焦点框。
- 项目 `.venv` 下 `py_compile` 和 PyQt offscreen 验证通过：当前主题上沿 `#0066cc` 派生 `#0569cd`，旧主题上沿 `#0cc0df` 派生 `#11c1e0`；顶部拖动恢复，八月日期模型与网格渲染恢复正常。

## 2026-07-04 日界面时间页日期按钮内容居中

- 日界面 `TimePickerView` 的日期开关键原本显式设置 `text-align: left`、左侧 `15px` padding，并在日期文本前加入两个空格，因此图标和日期文字整体靠左。
- 删除左对齐、左 padding 和日期文本前导空格，恢复 `QPushButton` 默认的图标与文字内容组整体居中。
- 本轮只修改日界面 `src/ui/time_picker.py`，不影响周界面和月界面的独立时间选择器。
- 项目 `.venv` 下 `py_compile` 通过；offscreen 按钮抓图确认日历图标与 `2026年07月18日` 文字作为整体居中，临时验证图片已删除。

## 2026-07-04 日界面日历浅色焦点框 NoFocus 试点

- 开工前先将既有主题适配、详情弹窗置顶、坐标轴裁剪、日历主题及日期按钮居中改动提交为检查点 `4303cf5`，便于本轮方案不满意时单独撤回。
- 不再操作 `QCalendarWidget` 私有模型的 current index；仅将日历控件及其内部日期 `QTableView` 的焦点策略设为 `NoFocus`，从视觉来源上阻止点击后持续出现键盘焦点框。
- 鼠标选择日期、前后翻月、顶部拖动和日期选择信号保持不变；代价仅是取消方向键、PageUp/PageDown 等键盘导航入口。
- 本轮源码只修改 `src/ui/calendar_pop.py`，当前保持未提交。
- 项目 `.venv` 下 `py_compile` 与 PyQt offscreen 回归通过：鼠标点击正确选择 `2026-07-05` 且表格不取得焦点，八月日期模型完整，顶部拖动仍可将窗口从 `(100,100)` 移至 `(140,150)`。

## 2026-07-04 坐标看板轴线比例与设置页白框

- 坐标轴默认纵向位置由画布高度的 `70%` 上移至 `61.8%`，提取为 `_ScheduleAxisCanvas.AXIS_VERTICAL_RATIO = 0.618`；完成日程仍在轴下方，未完成日程仍在轴上方。
- “隐藏已完成日程时改为 9:1”仅作为后续设置联动规则，本轮未实现。
- “现在”原点竖刻度由轴线上下各 `10px` 对称缩短为上下各 `5px`，总几何高度减半；没有单独删除上半段或下半段。
- 设置动画切换后的 `settings_page` 由透明空页改为与显示画布同范围的半透明白底框，使用白色 `2px` 边框和 `6px` 圆角，为后续真实设置控件预留布局区域。
- 设置页占位文字改为深灰色 `#333333`，避免白底白字；原齿轮旋转和画布收缩/展开动画保持不变。
- 项目 `.venv` 下 `py_compile` 与 PyQt offscreen 动画验证通过：设置页展开后与原 `content_host` 同为 `400x228`，页面、堆栈和宿主几何一致，白底与 `2px` 白框样式命中；临时验证图片已删除。
- 根据后续交互调整，设置页不再放入 `QStackedWidget` 参与“收起后换页再展开”的两段动画，而是固定铺在 `content_host` 底层；显示页作为独立前景层位于其上。
- 打开设置时只让前景显示页从下向上收起，底层设置白框自然露出；关闭设置时前景显示页从上向下展开并重新覆盖设置页。设置白框自身始终保持原位置和完整尺寸，不参与位移或缩放。
- PyQt offscreen 前后层动画回归通过：宿主高度 `228px`，打开和关闭动画中间态前景高度分别为 `204px/207px`；打开完成后前景隐藏且底层设置页完整可见，关闭完成后设置页隐藏且前景恢复完整宿主几何。

## 2026-07-04 坐标看板显示设置 UI 壳

- 开工前先提交既有前后层动画为检查点 `c91fc74`，本轮设置页实现尚未提交。
- `ScheduleAxisService` 新增只读 `AxisCategoryOption` 和 `load_category_options()`，经 `CategoryRepository` 读取日程清单名称与颜色；坐标看板 UI 不直接访问数据库。
- 设置页左侧新增“显示设置”标题和“范围”区域：方向组选项为“未来 / 未来&过去 / 过去”，时间组选项为“一天 / 一周 / 两周 / 一月 / 一年”；两组均使用互斥单选圆点和左侧主题色竖线。
- 中部“颜色”区域按清单动态生成名称、颜色方块和透明度输入框；清单数量超过单列可用高度时自动向右新增列，每列左侧保留同组竖线，并可通过横向滚动查看溢出列。
- 右侧新增白色“效果预览”框；范围区和颜色区保持固定宽度，看板拉宽时新增空间只分配给预览区，避免设置控件重新排版。
- 修正动态分列测量时机：滚动区完成父布局后在下一轮事件循环读取最终 viewport 尺寸，再计算每列行数，避免按初始化阶段的旧高度错误地把全部清单塞进一列。
- 本轮仅实现设置 UI 壳。方向、时间、清单颜色和透明度只保存在当前控件状态；不持久化、不修改清单数据、不改变数轴投影，预览框暂不绘制真实效果。
- 多清单 PyQt offscreen 验证通过：`700x220` 设置页中，最终 viewport 为 `336x162`，15 个清单按每列 6 行分成 3 列；页面拉宽至 `1000px` 后预览区由 `184px` 增至 `484px`，两组单选项各保持一个选中值。
- 交互冒烟通过：方向切换到 `future`、时间切换到 `week` 后本地状态同步更新；单个清单透明度可在控件内改为 `65%`，初始颜色 `#123456` 保持不变，未触发持久化。
- 真实 `ScheduleAxisBoard` offscreen 动画验证通过：`900x340` 看板打开设置后，底层设置页保持可见、前景显示页收起，设置面板尺寸为 `844x264`，预览区宽度为 `500px`；当前 3 个真实清单均成功构造。
- 未完成事项：设置值持久化、显示完成日程开关、线性/`log(t+1)` 刻度模式、隐藏完成日程时轴线改为 9:1、清单颜色覆盖实际 marker、真实预览绘制。

## 2026-07-04 坐标看板设置页响应式布局修订

- 修改前先将第一版设置 UI 壳提交为回退检查点 `8c4112b`。
- “范围”和“时间”不再依赖普通纵向布局及底部 stretch；两组共用同一个选项间距计算，3 个方向选项与 5 个时间选项的中心间距保持一致，时间组竖线下沿与效果预览框下沿对齐。
- 效果预览框上沿提升到与“显示设置”标题文字上沿一致；预览框仍作为弹性填充区，最小宽度明确为 `100px`。
- 范围、时间和颜色控件归入独立 `controls_container`，由设置页统一计算密度，避免各列自行压缩后产生不一致间距。
- 颜色列竖线高度改为按实际可见行数计算；例如 15 个清单按 `7/7/1` 分为三列时，三条竖线高度分别为 `172/172/22px`，末列不再延伸到设置框下沿。
- 横向空间按固定优先级处理：预览框先缩至最小宽度；随后范围列、颜色列、列间距和竖线到内容的距离按统一密度压缩；清单名称通过右侧省略号适配剩余宽度；仍不足时隐藏最右侧完整颜色列，并用最后一个可见位置的 `…` 表示未显示清单。
- 删除颜色区横向滚动容器，改为基于最终可用宽度的一次性分栏和隐藏计算；隐藏整列后释放的空间重新由效果预览框吸收。
- PyQt offscreen 多尺寸验证通过：`1000px` 设置页完整显示 3 列且预览宽 `312px`；`700px` 完整显示 3 列、统一压缩后预览宽 `103px`；`420px` 只显示 1 列并出现省略标记，预览宽 `102px`，无控件重叠。
- 真实 `ScheduleAxisBoard` 在 `900px` 和最小 `420px` 宽度下完成设置动画验证，预览宽分别为 `500px/101px`；标题与预览上沿、时间竖线与预览下沿均对齐。
- 本轮仍只修改设置 UI 布局，不绑定筛选、颜色覆盖、透明度持久化或真实预览功能。

## 2026-07-04 周日程卡片拖拽边缘自动翻周

- Git 历史核查确认：项目此前只实现周内跨日期拖放和顶部区域滚轮翻周，从未实现拖拽卡片到左右边缘时自动切换上一周/下一周；本轮属于新增能力，不是恢复被删代码。
- `WeekScheduleCard` 新增拖拽开始/结束信号，`WeekWindow` 建立独立拖拽会话，记录当前拖拽源卡片并启动 `60ms` 边缘检测计时器。
- 卡片拖到窗口左侧或右侧 `28px` 区域并停留约 `0.45s` 后，分别切换上一周或下一周；继续停留时以至少 `0.7s` 间隔继续翻周，离开边缘立即取消当前方向计时。
- 翻周刷新时不销毁正在作为 `QDrag` 源的卡片，而是将其暂时移出可见区域；新一周内容照常加载并跳过该日程的重复副本，目标列继续使用原虚线卡片参与落点排序。
- 向右翻周后可把鼠标移到左侧边缘返回上一周；翻周时同步平移当前选中日期 7 天，保持选中星期位置一致。
- 落下卡片后继续复用既有 `_handle_card_drop(...)`：按目标列日期平移开始时间、结束时间和提醒时间，跨周仍视为单次修改并脱离重复组；过去日期禁止落入的既有规则保持不变。
- 拖拽取消、无效落点或过去日期拒绝时统一清理拖拽会话并重新加载当前周，避免隐藏源卡片或 `current_drag_widget` 残留。
- 项目 `.venv` 下 `py_compile` 通过。PyQt offscreen 无数据库写入验证通过：`2026-07-06 -> 2026-07-13 -> 2026-07-06` 可往返翻周；源卡片在刷新中保持存活；模拟落入下一周周一后日程日期更新为 `2026-07-13`，两次字段更新调用完成且拖拽状态清空。
- 鼠标边缘检测单独验证通过：右侧停留触发下一周，随后左侧停留返回原周。

## 2026-07-05 更多菜单开机自启与坐标看板设置分组

- 更多菜单在“显示节日”之后新增带复选框的“开机自启”，复用 `assets/icons/Turn_on.svg`；不显示节日选项的日/待办界面也保留开机自启入口。
- 新增 `src/utils/startup_manager.py`，通过当前用户的 Windows `HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run` 注册项实现真实开机自启，不需要管理员权限。
- 源码运行时启动命令使用项目 `.venv/Scripts/pythonw.exe`、`main.py` 和项目根目录工作路径；冻结程序则使用可执行文件所在目录作为工作路径。更多菜单每次打开时重新读取真实注册状态，设置失败时复选框回退到实际状态。
- 坐标看板设置切换去掉前景显示框收起/展开动画：点击齿轮后显示框立即隐藏、设置框立即出现；再次点击立即恢复。齿轮角度同步瞬间切换为 `180°/0°`。
- 设置页第一列标题“时间”改为“跨度”，原“一天/一周/两周/一月/一年”选项保持不变。
- 原“颜色”区拆分为上下两个组：上方“数轴”包含“轴体/字体”两项，下方“清单”继续按当前日程清单动态生成颜色和透明度控件；两组均使用随实际行数变化的主题色竖线。
- 新增数轴组后，清单区按剩余高度重新计算每列容量，既有预览优先压缩、统一间距压缩、名称省略和右侧整列隐藏规则保持生效。
- 项目 `.venv` 下相关文件 `py_compile` 通过。PyQt offscreen 验证：更多菜单复选项顺序为“窗口置顶/显示节日/开机自启”，自启图标加载成功且状态回读生效；设置页标签为“跨度/数轴/清单”，轴体与字体两行成功构造；显示/设置页可即时往返切换。
- 真实宽窄看板验证通过：`900px/420px` 下数轴组竖线均为两行实际高度 `47px`，当前 3 个清单竖线为 `72px`，预览框分别保持 `500px/101px`，无控件重叠；临时截图已删除。
- 颜色弹窗确认使用 Qt `QColorDialog`，原黑色主体来自应用 `Fusion` 样式继承的系统调色板；新增公共 `ThemedColorDialog` 封装，强制使用 Qt 非原生颜色面板，顶部自绘标题栏跟随 `AppConfig.COLOR_GRADIENT_START`，主体改为白底深色文字，输入选中状态同步使用主题上沿色。
- 坐标看板清单颜色按钮改为调用 `ThemedColorDialog`，仍保留原有选色确认/取消语义，不在本轮持久化颜色设置。
- 项目 `.venv` 下 `py_compile` 通过；PyQt offscreen 构造验证确认非原生选项生效、窗口底色为 `#ffffff`、选中高亮为当前主题上沿色 `#0066cc`、自绘标题栏高度为 `36px`；清单颜色入口调用链验证确认选色结果可同步更新本地颜色值与色块样式。临时验证截图已删除。

## 2026-07-05 坐标看板设置效果预览

- 开工前先将既有开机自启、设置页响应式布局、周拖拽翻页和主题颜色弹窗提交为检查点 `6dd7987`，本轮预览实现形成独立 diff。
- 设置页原“效果预览”占位文字替换为轻量绘制画布，不读取数据库、不构造真实日程，也不写入设置。
- 每个日程清单只生成一个预览元素，类型为 DDL 竖线或时间段矩形二选一；清单 ID 与名称经稳定校验值生成类型、位置、完成状态和重要性，因此同一组清单重复打开或重绘时结果保持一致，不会随机跳动。
- 重要性沿用真实坐标看板的三档高度 `9/12/15px`，DDL 沿用 `2px` 线宽；预览数轴使用当前“轴体”颜色，文字使用当前“字体”颜色，marker 使用对应清单颜色与透明度。
- 各清单分配独立横向槽位，预览元素之间不重叠；未完成元素位于轴上方，完成元素位于轴下方，保持与真实看板一致。
- 清单颜色或透明度在设置页变化时会立即触发预览重绘，但本轮仍不持久化这些设置，也不影响真实数轴 marker。
- 项目 `.venv` 下 `py_compile` 通过。PyQt offscreen 验证 4 个清单生成恰好 4 个稳定元素，类型均为竖线/矩形二选一，高度只取 `9/12/15px`，元素矩形互不相交；透明度从 `100%` 改为 `55%` 后预览颜色 alpha 同步为 `140/255`。
- `900px` 与 `420px` 宽度截图验证通过，预览框随剩余空间伸缩，所有示例元素保持在框内；临时截图已删除。
- 预览时间段宽度改为受当前“跨度”控制，不再占满清单横向槽位；一天、一周、两周、一月、一年分别使用逐级缩小的轴宽比例区间，跨度越长，同一示例时间段在数轴上越窄。
- 预览数轴补齐左右双向箭头；切换跨度单选项后立即触发预览重绘，DDL 线宽和三档重要性高度不受跨度影响。
- 单清单宽预览验证中，同一时间段在一天/一周/两周/一月/一年下的宽度依次为 `109.13/58.02/39.83/27.05/12.64px`，满足严格递减；一天与一年截图确认箭头、中心刻度及时间段比例正常，临时截图已删除。
- 日/周共用清单选择页的选中卡片边框和右侧勾由写死的 `#0cc0df` 改为 `AppConfig.COLOR_GRADIENT_START`，随当前主题上沿色变化；未选中样式和清单数据逻辑不变。
- 坐标看板设置页在“范围”上方新增“非均匀显示”开关，默认开启；增加开关行后重新压缩范围与跨度两组选项的统一间距，保持时间组竖线仍落到设置内容下沿。
- “非均匀显示”已接入真实数轴：开启时沿用当前 `log(t+1)` 映射，关闭时使用近似零曲率的线性映射，切换后立即重绘；该状态本轮不持久化。
- 项目 `.venv` 下 `py_compile` 通过。PyQt offscreen 验证清单选中边框/勾均包含当前主题色 `#0066CC`；非均匀开关默认开启，关闭后数轴 `log_scale=1e-12`，重新开启恢复原比例。以 24 小时为例，线性/非线性映射位置分别为 `516.67/713.23px`；设置页截图确认新增开关及压缩布局无重叠，临时截图已删除。
- 清单选择页新建输入框残留的 `#0cc0df` 边框改为 `AppConfig.COLOR_GRADIENT_START`；确认按钮原本已随主题变化，本轮未改其交互。
- 坐标看板补齐清单实时同步：`refresh_data()` 会重新读取当前日程清单；清单新增、软删除和硬删除成功后同时发出既有 `global_signals.category_changed`，已打开的坐标看板无需关闭即可更新设置行和效果预览。
- 清单同步采用按 `category_id` 差量复用：已有清单保留用户在设置页临时修改的颜色和透明度，名称变化会更新文字；新增清单创建新行，删除清单移除旧行，清单顺序跟随当前查询结果。
- 项目 `.venv` 下 `py_compile` 通过。纯内存 offscreen 验证完成 `1/2 -> 1/3 -> 3` 的新增与删除同步，既有清单本地颜色 `#abcdef`、透明度 `55%` 和改名结果均被保留；模拟清单创建入口确认成功新增后只发出一次 `category_changed`，测试未写真实数据库。
- 坐标看板设置页清单列改为按当前可用高度均匀分配满列行距：清单项高度保持 `22px`，满列竖线延伸到清单区域下沿，与左侧“跨度”竖线下沿对齐；最后一个未满列仍只按实际项目数量绘制竖线。
- PyQt offscreen 三行容量验证通过：5 个清单按 `3+2` 分列，第一列项目纵坐标为 `0/32/64px`，满列竖线高度 `86px`，与跨度竖线全局下沿同为 `201px`；第二列竖线按两项缩短为 `54px`。在更高的五行容量下，单列 5 项同样与跨度下沿对齐；临时截图已删除。
- “不均匀显示”改为复用“范围/跨度/数轴/清单”的小标题样式，字体大小、字重和颜色保持一致。
- 清单分栏改为不对称顶部容量：第一列仍从“清单”标题下开始；第二列及后续列从颜色区域顶端开始，与“数轴”标题顶端齐平，利用原先被轴体/字体组占据后在右侧形成的空白区域。
- 新分栏模型分别计算第一列和后续列容量，满列仍均匀分配行距并对齐底部，最后未满列按实际项目缩短；窄布局的右侧整列隐藏与省略标记规则保持不变。
- PyQt offscreen 验证：`900x220` 下第一列容量为 3、后续列容量为 7，第一/第二列竖线顶端分别为 `92/0px`，第一列与跨度竖线全局下沿同为 `201px`；缩到 `420px` 后只显示一列并正确出现溢出状态。标题样式一致性和临时截图检查通过，截图已删除。
- 设置预览接入“范围/跨度”联动：未来模式原点位于数轴左端，过去模式位于右端，未来&过去模式位于中点；两端与原点文字根据方向隐藏或显示，避免无效的另一侧范围标注。
- 跨度标注统一使用“一天/一周/两周/一月/一年”对应的 `1天/1周/2周/1个月/1年`，预览两端文字随单选项即时更新；已有时间段宽度分级规则继续同步使用同一跨度状态。
- 坐标看板顶部说明最后一段不再写死“范围 ±1个月”，而是按设置状态生成 `范围 ±跨度`、`范围 未来跨度` 或 `范围 过去跨度`；设置项变化后立即重新计算省略文本和按钮间可用宽度。
- 本轮只绑定设置预览和顶部说明，未改变真实数轴的数据筛选范围。PyQt offscreen 已遍历 3 种方向与 5 种跨度共 15 组原点/文字组合；模拟点击验证顶部说明可由“范围 ±1个月”更新为“范围 未来1年”，三种方向截图检查通过并已删除。
- 预览箭头按方向修正：未来模式左端为原点，不再绘制左箭头，只保留右侧未来箭头；过去模式右端为原点，不再绘制右箭头，只保留左侧过去箭头；未来&过去模式继续保留双向箭头。
- 设置项“不均匀显示”更名为“非均匀显示”。预览数轴新增跨度刻度：一天/一周/两周/一月/一年每个有效方向分别绘制 `2/4/6/8/11` 个内部刻度，跨度越大刻度越密；双向范围在原点两侧镜像绘制。
- 均匀模式的逻辑刻度等距分布；非均匀模式对相同逻辑刻度使用归一化 `log(t+1)` 映射，靠近原点的时间区间获得更大显示距离、远端刻度逐渐变密。普通刻度总高 `4px`，小于原点刻度总高 `6px`。
- 项目 `.venv` 下 `py_compile` 通过；PyQt offscreen 验证跨度刻度数量严格为 `2/4/6/8/11`，双向模式左右镜像，非均匀模式从原点向远端的相邻间距依次缩小。均匀与非均匀预览截图检查通过，临时截图已清理。
- 设置预览数轴两端标签移除“过去/未来”前缀，单向模式显示“现在”和跨度，双向模式显示“跨度 / 现在 / 跨度”，避免窄预览框中文字互相挤压。
- 清单颜色行高由 `22px` 缩至 `20px`、基础行距由 `3px` 缩至 `2px`；数轴组与清单组同步使用该密度，现有设置框高度下首个清单列可容纳 4 项，后续列仍沿用顶部对齐及溢出省略规则。
- 项目 `.venv` 下 `py_compile` 通过；PyQt offscreen 在 `900x220` 与 `520x220` 两种设置页尺寸下验证首列容量均为 4，5 个清单按 `4+1` 分列且无控件重叠；双向一月标签验证为 `1个月 / 现在 / 1个月`。宽窄截图检查通过，临时截图已清理。
## 2026-07-05 主题选色弹窗紧凑化与坐标看板打开状态复位

- `ThemedColorDialog` 改为外层主题窗口承载 Qt 非原生 `QColorDialog`：完整保留色板、色谱、屏幕拾色、自定义颜色、HSV/RGB/HTML 输入和确认/取消逻辑，主体统一按 `0.75` 缩放；窗口由原约 `652x428px` 缩至 `489x323px`。
- 外层窗口使用与坐标看板一致的 `12px` 圆角、`30x30px` 关闭热区和 `12px` 关闭图标；顶部主题色栏继续支持拖动，左右内容边距统一。
- 选色标题按入口动态生成：数轴轴体、数轴字体分别显示“选择数轴轴体颜色”“选择数轴字体颜色”，普通清单显示“选择清单+清单名+颜色”，避免固定标题造成对象歧义。
- Qt 面板文本本地化为“基本颜色、拾取屏幕颜色、自定义颜色、添加到自定义颜色、色相、饱和度、明度、R/G/B、透明度、确定、取消”。其中“自定义颜色”仍表示可保存并复用的用户色块槽位。
- 双击顶部主题色栏可在白色内容主题与深色内容主题之间切换；深色主题同步改为白色文字。六个可见数值框移除原生边框和横线式步进按钮，改为数字右侧垂直排列的上下三角；浅色主题使用主题上沿色，深色主题使用白色。
- 下方内容区未启用整区拖动：色块、色谱、亮度条、数值输入和操作按钮覆盖了绝大部分区域，直接拦截拖动会与选色和输入冲突；后续若需要，只适合对明确空白区域单独增加拖动命中。
- 坐标看板每次重新显示时强制恢复显示页：清除设置打开状态、复位齿轮角度、隐藏设置页并显示数轴页，不再继承上次关闭时的页面状态。
- 项目 `.venv` 下 `py_compile` 通过；PyQt offscreen 验证中文文本、动态标题、数值步进、确认信号、深浅主题切换、圆角遮罩及坐标看板显示页复位均通过。浅色和深色截图检查通过，临时截图已清理。
## 2026-07-05 主题选色弹窗双窗口修复与最终规划更新

- 修复前先将坐标看板设置、清单主题色、选色弹窗第一版和当前“笋绿”主题提交为检查点 `1123cc0`，提交说明为 `feat: refine axis board settings and color dialog`。
- 实机问题确认：通过 `QGraphicsProxyWidget` 嵌入 `QColorDialog` 时，内部 `QColorDialog` 仍保留顶级原生窗口身份，Windows 因此同时显示一个空白 `Select Color` 窗口；代理缩放还会使覆盖在 `QSpinBox` 上的自定义三角按钮继承错误几何位置而不可见。
- 修复方案：移除 `QGraphicsScene / QGraphicsView / QGraphicsProxyWidget` 嵌套，`ThemedColorDialog` 恢复为唯一顶级的 Qt 非原生 `QColorDialog`；通过中文短标签、压缩 HSV/RGB 数值区、缩小色谱尺寸和布局间距实现紧凑化，不再用图形代理强制整体缩放。
- 修复后窗口约为 `552x361px`，相比原约 `652x428px` 明显缩小；由于 Qt 基础 / 自定义色块网格存在私有最小尺寸，本轮优先保证完整显示和单窗口稳定性，不再强求严格 `75%` 尺寸。
- 数值上下三角改为直接挂在真实 `QSpinBox` 上，并在控件 `Resize / Show` 时重新定位；浅色主题使用主题上沿色，深色主题使用白色。白色主体改由真实窗口调色板填充，圆角继续使用 `12px` mask。
- PyQt offscreen 验证只存在一个可见顶级 `ThemedColorDialog`，动态标题、中文文本、上下三角、深浅主题、确认信号和圆角遮罩均通过；浅色截图确认主体为白色且控件完整。系统级“拾取屏幕颜色”仍需 Windows 实机手工验收。
- `Final_Formulation.md` 已同步当前进度和技术债：记录坐标看板已完成项与尚未接入真实画布的设置项，补充零正式测试、UI 大文件、直接数据访问和坐标看板拆分风险，并明确 Python 本地桌面应用不以消息队列 / 容器 / 多人服务端作为当前完成标准。
- 最新主线顺序更新为：坐标看板与选色弹窗收尾 → 日 / 周课程表模式 → 搜索 / 筛选 → Markdown / PDF / PNG 导出 → 自动化测试与 CI → 自定义重复规则 → 换肤及其余后续阶段。测试阶段必须早于自定义重复规则真实写入改造。

## 2026-07-06 主题选色弹窗圆角与内部布局修正

- 复核两种圆角实现：选色弹窗原先使用 `QPainterPath -> QRegion` 整数像素遮罩裁剪，Windows 分数 DPI 下容易在边角出现不规则白色像素；主界面和看板采用透明顶级窗口配合 `QPainter` 抗锯齿路径直接绘制圆角背景，边缘更稳定。
- 选色弹窗改为 `WA_TranslucentBackground`，由同一个 `paintEvent`、同一条圆角裁剪路径绘制白色 / 深色主体和主题色标题栏；标题栏控件自身改为透明，避免父级白底和标题栏 QSS 圆角叠加造成四角白边。
- 隐藏 Qt 屏幕拾色期间动态写入的光标坐标状态标签，保留“拾取屏幕颜色”功能本身，避免压缩布局后状态文字覆盖“自定义颜色”。
- 右侧色谱和亮度条扩大，并在显示 / 缩放后以数值框最右侧为目标动态校准亮度条右沿；确认 / 取消按钮组使用同一目标右边界，减少右侧无效空白。
- 初步将 HSV / RGB / HTML 区域由过度压缩的 `300x100px` 调整为 `340x140px`，增加行列间距、色块预览高度和输入框高度；自定义上下三角同步扩大并按真实 `QSpinBox` 尺寸重新定位。
- 实机复测发现上述固定高度仍会破坏 Qt 私有 HSV / RGB 网格的自然行高，表现为数值行提前、标签与 HTML 行错位，且固定宽度按钮盒被布局放到左侧。后续修正为仅固定右侧区域宽度，数值容器使用 `SetMinimumSize` 和自然高度，预览色块不再强制拉高；输入框只保留宽度与最小高度约束，确认 / 取消按钮盒明确右对齐。
- HTML 输入框不再保留过宽的固定最小宽度；显示后读取左侧 HSV 数值列的实际右边界，并动态收窄 HTML 输入框，使其右沿与色相 / 饱和度 / 明度三角步进按钮右沿对齐。
- 新增 `src/utils/color_preferences.py`，沿用 `QSettings("Wanji", "DesktopSchedule")` 保存固定自定义色槽，键为 `color_dialog/custom_colors`；颜色使用 `#AARRGGBB` 字符串列表，不写入业务数据库。
- `ThemedColorDialog` 在进程内首次创建前恢复全部有效色槽，并在确认、取消或关闭等 `done(...)` 路径保存 Qt 当前全部固定色槽；色槽数量仍由 `QColorDialog.customCount()` 决定，填满后继续使用 Qt 的选择槽位 / 循环覆盖机制，不会增长界面或内存结构。
- 确认 / 取消按钮盒从 `QColorDialog` 根布局的独立底行移入 HSV / RGB 数值容器，垂直中心与 HTML 输入框对齐、右沿继续与数值三角按钮对齐；移除独立底行后窗口高度由 `sizeHint()` 自动缩短，减少底部空白。
- 左侧基础色区域的统一行距由 `2px` 收紧为 `0px`，“基本颜色”标题高度压到实际字体高度，在不改变色块和拾色按钮尺寸的前提下回收顶部空隙，使“拾取屏幕颜色”按钮下沿上移并接近右侧渐变取色板下沿。
- 已使用工作区 Python 对源码执行无缓存语法编译，`git diff --check` 无 whitespace error。当前项目 `.venv` 启动器在本会话仍指向不存在的旧 Python 3.11 路径，未声明 PyQt offscreen 视觉验证通过；需在 Windows 实机复测圆角、屏幕拾色、右侧三线对齐和深浅主题切换。
- 后续实机截图暴露出 Qt 左栏弹簧和私有布局会重新分配标签高度，直接对布局管理中的控件调用 `move(...)` 无法稳定保持四组边界。最终方案在 Qt 完成布局后，将“基本颜色”标签、基础色块、屏幕拾色按钮、“自定义颜色”标签和添加自定义颜色按钮从左侧布局中脱离，同时插入等高占位保留原弹簧计算，再统一按对照控件定位。
- 最终几何规则固定为：“基本颜色”上沿对齐右侧渐变色谱上沿；“拾取屏幕颜色”按钮下沿对齐色谱下沿；“自定义颜色”标签上沿和高度均对齐“色相”标签；“添加到自定义颜色”按钮下沿对齐确定 / 取消按钮组下沿。
- 重叠根因确认：Qt 曾给“自定义颜色”标签分配 `58px` 高度，而可见“色相”标签高度为 `22px`；即使上沿相同，文字也会因垂直居中下沉并覆盖下方色块。脱离布局后将该标签固定为色相标签的实际高度，重叠消失。
- 最终 PyQt offscreen 延迟 `1000ms` 几何验收通过：基本颜色 / 色谱上沿均为 `49px`；拾色按钮 / 色谱下沿均为 `239px`；自定义颜色 / 色相标签均为 `y=252px, height=22px`；添加按钮 / 确定取消按钮组下沿均为 `353px`。无缓存语法编译和 `git diff --check` 同步通过，临时验证截图已清理。

## 2026-07-06 坐标看板真实画布接入显示设置

- 开工前确认真实看板已经读取数据库日程并沿用既有跨视图刷新链，本轮不新增日程快照、显示模型或定时刷新层，只处理设置页到真实画布的接线和已确认的新增刷新缺口。
- `ScheduleAxisService` 增加一天、一周、两周、一月、一年的统一小时映射，以及未来、过去、双向三种显示边界；既有 `map_delta_to_x(...)` / `map_x_to_delta(...)` 扩展为支持单向和双向的线性 / 归一化 `log(t+1)` 往返映射，默认双向调用保持兼容。
- 真实画布不再写死前后各一月。设置中的方向、跨度和“非均匀显示”会立即更新筛选边界、原点位置、单/双向箭头、内部刻度、边缘时间文字、顶部范围说明和日程投影；切换设置后复位到对应方向的默认观察位置，既有拖动、滚轮缩放、纵向轨道和详情交互保持不变。
- 范围语义固定为：未来 `[0, +跨度]`、过去 `[-跨度, 0]`、双向 `[-跨度, +跨度]`。点日程必须落入边界；时间段只要与边界相交就保留，超出部分在映射时夹紧到边缘。悬停预览和详情仍读取原始日程，因此跨界时间段显示完整开始 / 结束时间。
- 设置页“轴体”和“字体”的颜色及透明度已接入真实轴线、箭头、刻度、时间标签和悬停辅助线；各清单颜色及透明度按 `category_id` 覆盖真实 marker。覆盖只保存在当前看板控件状态，不修改清单数据库，也不做重启持久化。
- 周视图和月视图新增日程成功后补发既有 `schedule_updated(None)`，由 `MainWindow` 继续复用 `_refresh_dashboard_todo_week()` 刷新可见坐标看板；编辑、删除、完成状态和主窗口新增的既有刷新链未改写。
- 纯逻辑验证通过：五档跨度映射正确；未来 / 过去 / 双向在线性与非线性下的端点和中间值均可完成坐标往返；方向边界分别为单侧或双侧预期范围。
- Python 3.11 PyQt offscreen 验证通过：未来一天只保留未来点和跨越当前时刻的时间段，过去一天只保留过去点和跨越当前时刻的时间段，双向一天同时保留两侧日程；三种方向渲染的原点和箭头正确，轴体 / 字体 / 清单颜色及 `60% / 70% / 50%` 透明度即时进入真实画布，顶部说明更新为对应范围。
- 验证使用本机实际 Python 3.11 解释器运行，目标源码无缓存 `py_compile` 通过，`git diff --check` 无 whitespace error；项目 `.venv` 在普通沙箱中会因基解释器位于工作区外而被阻止启动，该现象不代表环境或路径损坏。临时验证脚本、截图和缓存已清理。
- 本轮未实现完成日程显示开关、设置持久化、自动时间流逝定时刷新或看板拆文件；这些仍按后续独立任务处理。

## 2026-07-06 坐标看板文字绘制层级与虚拟环境核验

- 核对 `.venv/pyvenv.cfg`、虚拟环境启动器和基解释器文件：项目环境指向现存的 `C:\Users\hfgre\AppData\Local\Programs\Python\Python311\python.exe`，配置为 Python `3.11.9`，并非错误版本或损坏环境。
- 普通沙箱内运行 `.venv/Scripts/python.exe` 会出现 `Unable to create process`；使用沙箱外执行权限后，同一启动器正常报告虚拟环境 Python `3.11.9`、基解释器 Python 3.11 和 Qt `6.4.2`。后续需要项目依赖或 PyQt 的验证应直接使用 `.venv` 并申请该权限，不再把此错误解释为环境损坏，也不改用 Python 3.12 执行 PyQt 验证。
- 真实数轴原先先画“现在”和左右边缘时间文字，再画日程 marker，完成日程位于轴下方时可能覆盖文字。本轮将数轴文字集中到 `_draw_axis_text(...)`，在日程 marker、悬停辅助线和时间标签完成后最后绘制。
- 只调整文字的绘制层级和遮挡关系，不改变文字位置、日程轨道、范围筛选、坐标映射、颜色设置或悬停详情数据。
- 使用项目 `.venv` 完成无缓存 `py_compile` 和 PyQt offscreen 重叠场景验证：已完成时间段横条覆盖整个过去一天轴下区域时，“过去 1天”和“现在”仍绘制在横条上层。临时脚本、截图和缓存已清理。
