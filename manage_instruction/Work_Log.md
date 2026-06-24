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
- 回退后尝试复跑 `D:\CodeProjects\DesktopSchedule\DesktopSchedule\.venv\Scripts\python.exe -m py_compile src/ui/components.py main.py`，但该虚拟环境启动器仍指向已不存在的 `C:\Users\hfgre\AppData\Local\Programs\Python\Python311\python.exe`，本次未能重新执行；源码与已提交且此前通过语法检查的 `HEAD` blob 完全一致。
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
