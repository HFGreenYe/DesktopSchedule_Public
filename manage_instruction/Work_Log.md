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
