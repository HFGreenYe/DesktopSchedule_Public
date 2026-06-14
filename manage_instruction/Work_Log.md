# Work Log

用途：记录当前阶段执行过程、验证结果、风险和结论。

---

# 当前状态：暂无活动阶段日志

月界面功能补齐阶段已于 2026-06-04 归档。

归档位置：

- `manage_instruction/History_Instruction.md`
- `manage_instruction/History_Log.md`

当前工作区等待下一阶段规划。

---

## 2026-06-04 月界面功能补齐阶段归档

- 归档内容：
  - `M-0` 到 `M-7` 阶段合同摘要已追加到 `History_Instruction.md`。
  - `M-0` 到 `M-7` 执行与验收摘要已追加到 `History_Log.md`。
- 当前工作文档重置：
  - `Work_Formulation.md`：暂无活动阶段。
  - `Work_Instruction.md`：暂无待执行阶段合同。
  - `Work_Task_Prompts.md`：暂无待执行提示词。
- 后续建议：
  - 不继续向月界面功能补齐阶段追加任务。
  - 若处理界面适配问题，应另开 UI 适配 / 布局债务整理阶段。

---

## 2026-06-13 坐标显示入口调整记录

- 背景：
  - 后续四象限不再按完整独立视图推进，暂调整为“坐标显示”入口。
  - 本次只做入口和显示形式调整，不实现坐标/象限看板内容。
- 已完成提交：
  - `77a7fde refactor: simplify view selectors`
    - 从主界面、周界面、月界面和右键菜单的视图切换入口中移除“四象限/象限”显示项。
    - 周视图拓展框改为短文案 `日 / 周 / 月 / 待办`，并固定宽度到 124px，使右侧与上方工具按钮组对齐。
  - `61788b8 feat: add axis display menu entry`
    - 在右上角 `SharedMoreMenu` 中新增 `坐标显示` 菜单项。
    - 新增 `assets/icons/axis.svg`。
    - 当前点击行为为占位打印，不打开新窗口，不实现坐标看板。
- 验证记录：
  - `rg -n "四象限|象限" src\ui src\controllers`：源码 UI / controller 范围无旧显示文案命中。
  - `py_compile` 覆盖 `dashboard.py`、`week_window.py`、`month_window.py`、`main_window.py`、`action_context_menu.py`、`components.py`、`main.py`：通过。
  - offscreen 构造验证：
    - `ViewSelectorCard` 仅包含 `day/week/month/todo`。
    - `ActionContextMenu.view_actions_by_id` 仅包含 `day/week/month/todo`。
    - `WeekWindow` 视图拓展按钮为 `['日', '周', '月', '待办']`，拓展框宽度为 124px。
    - `SharedMoreMenu` 菜单项包含 `坐标显示`。
- 风险或后续：
  - `坐标显示` 仍是入口占位，后续实现坐标看板前需先确认紧急性轴和重要性轴的数据来源。
  - 当前数据模型中 `priority` 语义仍存在“紧急性/重要性”混用历史，不能直接固化为双轴规则。

---

## 2026-06-13 待办看板文字与紧凑视图拓展状态小修

- 背景：
  - 待办看板便签视图中，长标题存在截断策略不一致、pin 图标随文字换行下移的问题。
  - 待办看板文件夹视图中，长文件夹名会撑开布局并导致最右列被滚动条或窗口边界裁剪。
  - 主界面和待办界面复用的视图拓展框缺少当前视图状态提示，日视图和待办视图容易混淆。
- 已完成提交：
  - `6879a03 fix: adapt todo board card titles`
    - `StickyNoteCard` 标题改为固定高度区域内显示，pin 图标保持左上角固定。
    - 长标题先换行，再按需缩小字号，避免不同卡片出现不一致截断。
    - `FolderCard` 文件夹名限制在卡片内部，先缩小字号，仍无法完整显示时省略。
    - `FolderViewContainer` 按可用宽度控制三列卡片宽度，并给右侧滚动条留安全边距，避免最右列显示不全。
  - `1524615 refactor: highlight active compact view selector`
    - `ViewSelectorCard` 增加当前视图状态。
    - `MainWindow.switch_view(...)` 同步日 / 周 / 月 / 待办状态到主界面和待办界面的视图拓展框。
    - 当前视图文字保持白色，非当前视图文字改为浅灰色；已取消高亮块、白边和金色文字方案。
- 验证记录：
  - `py_compile` 覆盖 `src/ui/todo_board.py`、`src/ui/dashboard.py`、`src/ui/todo.py`、`src/ui/main_window.py`、`main.py`：通过。
  - offscreen 构造验证：
    - `FolderCard` 长文件夹名不会撑开卡片宽度，超长内容使用省略文本。
    - `FolderViewContainer` 三列卡片宽度受控。
    - `StickyNoteCard` 长标题区域高度稳定。
    - `ViewSelectorCard` 可在 `day/todo` 状态间切换，当前项白字、非当前项浅灰。
- 风险或后续：
  - 本次仅修复待办看板文字适配和紧凑视图拓展状态，不处理待办看板整体 UI 重排。
  - `main.py` 当前仍有既有未提交改动，本次日志不包含也不解释该改动。

---

## 2026-06-14 添加表单重要性与月界面选项显示小修

- 背景：
  - `priority` 实际更接近“重要性”；“紧急性”应由截止时间或时间距离推导。
  - 月界面左侧添加表单空间较窄，`紧急性`、`每天`、`每周`、`每月` 等文字显示拥挤。
  - 月界面下拉弹窗在当前样式下存在白底白字不可读风险。
  - 月界面摘要三行已有外层信息框，小文本背景框显得拥挤。
- 本次代码改动：
  - `src/ui/add_view.py`：日界面添加表单 `紧急性：` 改为 `重要性：`。
  - `src/ui/add_view_week.py`：周界面添加表单 `紧急性：` 改为 `重要性：`，同步相关注释。
  - `src/ui/month_window.py`：
    - 月界面添加表单 `紧急性` 改为 `重要性`。
    - 月界面重要性显示项改为 `高 / 中 / 低`，默认仍为低。
    - 月界面重复显示项改为 `无 / 日 / 周 / 月`。
    - 新增显示值到保存值映射：`日 -> 每天`，`周 -> 每周`，`月 -> 每月`。
    - 下拉弹窗文字颜色对齐日 / 周添加页，使用灰色 `#333333`；选中项仍为青底白字。
    - 摘要三行小文本框改为透明背景、无边框；外层信息框保留。
  - 二次微调：
    - 月界面重要性 / 重复行改为固定 label 与 combo 宽度，避免 `重要性` 与短选项被压缩截断。
    - 月界面 `QComboBox` 隐藏下拉箭头区域，给短文案留出完整显示空间。
  - 三次微调：
    - 周界面添加页的 `QComboBox` 取消前置空格假居中，改为非 editable 的自绘居中显示。
    - 周界面下拉列表项也设置为居中显示，并保留 Qt 原生点击弹出行为。
    - 日界面本次仅保留 `紧急性：` 到 `重要性：` 的文案调整，不改变原有下拉框显示实现。
    - 月界面重要性 / 重复行继续压缩 label 宽度和控件间距，两个短下拉框均缩窄为 30px，并改为非 editable 的自绘居中显示，避免重复框贴到右侧边界。
  - 纠偏记录：
    - 曾临时尝试把日界面添加页下拉框也改为居中实现；复核后确认日界面原本已满足显示要求，已回退。
    - 当前 `src/ui/add_view.py` 实际代码差异只保留 `紧急性：` 到 `重要性：` 的文案改动，以及文件末尾换行规范化；未保留任何 `QComboBox` 行为或样式改动。
- 验证记录：
  - `py_compile` 覆盖 `src/ui/add_view.py`、`src/ui/add_view_week.py`、`src/ui/month_window.py`、`main.py`：通过。
  - offscreen 构造验证：
    - `InlineAddViewMonth.lbl_priority == "重要性"`。
    - 月界面重要性显示项为 `['高', '中', '低']`，默认 index 为 `2`（低）。
    - 月界面重复显示项为 `['无', '日', '周', '月']`。
    - 月界面重要性 / 重复下拉框宽度均为 30px，文本居中。
    - 周界面重要性与重复下拉框文本居中，显示项保持原有真实文案。
    - 日 / 周 / 月三处下拉框均保持非 editable，避免 editable 方案影响点击弹出。
    - 日界面重要性下拉仍沿用原有显示方式。
    - 摘要标签样式包含透明背景和无边框。
    - `AddScheduleView` / `AddScheduleViewWeek` 可构造。
  - monkeypatch 保存验证：
    - 月界面显示 `高 + 日` 时，保存数据为 `priority=2`、`repeat_rule="每天"`。
    - 验证过程未写入数据库。
- 范围说明：
  - 本次不调整日界面 / 周界面的重复项。
  - 本次不改数据模型、不改数据库、不改重复规则服务。
  - 本次只处理添加表单文案、月界面显示短文案和下拉 / 摘要局部样式。
- 风险或后续：
  - 月界面整体左侧布局仍需后续 UI 适配。
  - `priority` 字段历史语义仍存在“紧急性 / 重要性”混用，后续坐标显示或课程表视图规划时需继续区分。

---

## 2026-06-14 右键菜单视图子菜单图标替换

- 背景：
  - 用户已将 `interface-day.svg`、`interface-week.svg`、`interface-month.svg` 放入 `assets/icons/`。
  - 右键弹窗的视图子菜单仍使用旧的日历 / 周视图图标，和新图标资源不一致。
- 本次代码改动：
  - `src/ui/common/action_context_menu.py`：
    - `日视图` 优先使用 `interface-day.svg`，保留 `Calendar.svg` 作为 fallback。
    - `周视图` 优先使用 `interface-week.svg`，保留 `week_top_color.svg` / `view.svg` 作为 fallback。
    - `月视图` 优先使用 `interface-month.svg`，保留 `Calendar.svg` 作为 fallback。
- 范围说明：
  - 本次不修改右键菜单交互行为。
  - 本次不修改主界面 / 周界面 / 月界面的右键接入逻辑。
  - 本次不修改待办图标。
  - 新增图标文件由用户放入 `assets/icons/`，当前作为待提交资源。

---

## 2026-06-14 天气服务失败兜底小修

- 背景：
  - 运行期曾出现 `天气服务错误: Expecting value: line 1 column 1 (char 0)`。
  - 原因判断：定位服务或天气服务返回空响应 / 非 JSON 响应时，`response.json()` 会抛异常。
  - 原实现失败后只打印错误并 `emit({})`，`HeaderBar` / `WeekWindow` / `MonthWindow` 会直接忽略空数据，界面可能停留在旧天气或等待态。
- 本次代码改动：
  - `src/services/weather_service.py`：
    - 新增 `_read_json_response(response, source_name)`。
    - 对 HTTP 状态、空响应、非 JSON 响应做显式校验。
    - 对缺失 API 配置、定位失败、缺少经纬度、天气 API code 非 `200`、缺少 `now.temp/icon/text` 做明确错误。
    - 新增 `_fallback_result(error_message)`，失败时发出结构完整的兜底天气数据：
      - `temp: "--"`
      - `icon: "999"`
      - `text: "天气暂不可用"`
      - `city: "未知位置"`
      - `available: False`
      - `error: <失败原因>`
    - 成功数据新增 `available: True`。
- 兼容说明：
  - 本次不修改 `HeaderBar` / `WeekWindow` / `MonthWindow` 的天气布局和数据绑定方式。
  - fallback 数据保留既有 `temp`、`icon`、`text`、`city` 字段，现有 UI 可继续使用同一更新路径。
  - fallback icon `999` 对应 `assets/weather/999-fill.svg`，作为天气不可用图标。
  - 若 `999-fill.svg` 异常缺失，则清空天气图标，不再使用普通问号或 emoji。
- UI 图标替换：
  - 新增 `src/ui/common/weather_icon_label.py`：
    - 使用双层隔离结构：loading label 只负责沙漏动画，weather label 只负责真实天气 / `999-fill.svg`。
    - 使用 `assets/icons/hourglass.svg` 作为加载中图标。
    - 使用 `QTimer` 按固定帧率做上下翻转动画，翻转轴为沙漏画布几何中心的水平线。
    - 沙漏按 loading 画布 78% 尺寸居中绘制；上下翻转不会产生外接矩形裁剪问题。
    - 修正高 DPI source rect：翻转绘制时使用 `_loading_base.rect()` 读取完整物理 pixmap，避免 DPR>1 时只采样左上角导致沙漏天生显示不全。
    - `HeaderBar` 保持天气图标 label 原有固定高度和右上对齐；过渡动画隔离在 loading label 中，不改变真实天气图标布局。
    - 加载动画最长显示 3000ms，超时后自动切换到 `assets/weather/999-fill.svg`。
    - loading 期间若先收到 fallback `999-fill.svg`，不立即打断沙漏动画，仍等待 3000ms 后切换；真实天气图标返回时则立即停止动画并显示真实天气。
    - 收到真实天气图标后停止动画并显示 API 对应天气 SVG。
  - `src/ui/header.py`：天气 SVG 加载失败时使用 `assets/weather/999-fill.svg`。
  - `src/ui/week_window.py`：天气 SVG 加载失败时使用 `assets/weather/999-fill.svg`。
  - `src/ui/month_window.py`：天气 SVG 加载失败时使用 `assets/weather/999-fill.svg`。
  - `HeaderBar` / `WeekWindow` / `MonthWindow` 的初始化天气图标改为上下翻转 `hourglass.svg`，去除网络失败前短暂显示 emoji 中间态。
  - 新增资源：`assets/icons/hourglass.svg`。
- 验证记录：
  - `py_compile` 覆盖 `src/ui/common/weather_icon_label.py`、`src/services/weather_service.py`、`src/ui/header.py`、`src/ui/week_window.py`、`src/ui/month_window.py`、`main.py`：通过。
  - `_fallback_result(...)` 直接验证：通过。
  - monkeypatch 成功路径验证：
    - 模拟定位成功与天气 API 成功，输出 `available=True`、`temp=18`、`city=测试城`。
  - monkeypatch 空响应验证：
    - 模拟定位服务空响应，输出 `available=False`、`temp=--`，错误包含 `响应为空`。
  - monkeypatch 非 JSON 验证：
    - 模拟定位服务返回 HTML，输出 `available=False`，错误包含 `非 JSON`。
  - 缺失 API 配置验证：
    - `WeatherWorker('', '')` 输出 fallback，错误包含 `配置缺失`。
  - 999-fill SVG 验证：
    - `assets/weather/999-fill.svg` 可加载并染色为白色 pixmap。
  - hourglass SVG 验证：
    - `assets/icons/hourglass.svg` 可加载并染色为白色 pixmap。
    - `WeatherIconLabel.start_loading()` 会启动上下翻转动画。
    - 1100ms 时动画仍保持运行。
    - 3150ms 后动画自动停止，并切换到 `assets/weather/999-fill.svg` pixmap。
    - loading 期间提前收到 `assets/weather/999-fill.svg` 时，仍等到 3150ms 后切换，不再短暂显示普通问号或提前结束。
    - 0/18/36/54/72/90/126/180/234/270/315 翻转相位边缘 alpha 均为 0，确认沙漏翻转不触边裁剪。
    - `HeaderBar` 初始化验证：天气图标 label 保持固定高度 70，loading pixmap 存在且动画运行。
  - UI fallback 验证：
    - `HeaderBar.update_weather_ui(...)` 使用 fallback 数据时，天气图标显示 `assets/weather/999-fill.svg`，温度显示 `--°C`。
    - `WeekWindow.update_weather_ui(...)` 使用 fallback 数据时，天气图标显示 `assets/weather/999-fill.svg`，温度显示 `--°C`。
    - `MonthWindow.update_weather_ui(...)` 使用 fallback 数据时，天气图标显示 `assets/weather/999-fill.svg`，温度显示 `--°C`。
  - UI 初始化态验证：
    - `HeaderBar`、`WeekWindow`、`MonthWindow` 初始化天气图标不再显示 emoji 中间态，直接启动 `hourglass.svg` 上下翻转动画。
  - 真实天气图标回归：
    - `WeatherIconLabel.set_weather_icon('assets/weather/100-fill.svg')` 会停止动画并显示真实天气图标。
- 范围说明：
  - 本次只处理天气服务失败兜底。
  - 不新增网络请求。
  - 不修改天气 UI 布局，仅替换天气图标 label 的内部显示状态。
  - 不修改 `.env` 或 API 配置读取方式。

---

## 2026-06-15 月界面日期弹窗 toggle 与右键菜单细节小修

- 背景：
  - 月界面日期格当前单击会打开该日期持久弹窗，但再次点击同一日期只会重新激活弹窗，不能收回。
  - 月界面 hover 预览弹窗的日期标题颜色仍为普通文本色，用户希望与主题青色保持一致。
  - 页面级右键菜单图标需要继续向更多菜单的图标行风格收口。
- 本次代码改动：
  - `src/ui/month_window.py`：
    - `_on_calendar_date_clicked(qdate)` 增加同日期弹窗检测。
    - 如果该日期持久弹窗已打开，再次单击会关闭该弹窗并返回。
    - `calendar.activated` 双击 / 激活跳日视图链路保持不变，仍会关闭所有持久弹窗并发出 `date_selected`。
  - `src/ui/popups/month_day_hover_preview.py`：
    - hover 预览弹窗日期标题改为主题青色 `#0cc0df`。
    - 正文颜色和白底圆角弹窗样式保持不变。
  - `src/ui/popups/month_day_panel.py`：
    - 单击日期打开的持久弹窗日期标题改为主题青色 `#0cc0df`。
    - 正文颜色、关闭按钮和白底圆角样式保持不变。
  - `src/ui/common/action_context_menu.py`：
    - `_MenuRow` 增加统一 `ICON_SIZE = 18`。
    - 图标 label 固定槽位并居中。
    - 禁用项图标使用禁用灰 `#777777`，启用项仍使用 `#333333`。
- 范围说明：
  - 本次不修改右键菜单信号、动作 id 或主/周/月接入逻辑。
  - 本次不修改月界面添加、保存、picker、marker、hover cache 或数据库逻辑。
  - 本次不改 `ActionContextMenu` 菜单尺寸和子菜单关闭策略。
  - 右键菜单图标仍存在轻微模糊感，本次暂缓处理，后续应单独比较 `QPixmap` 直载与 `load_colored_svg_pixmap` 染色路径。
- 验证记录：
  - `py_compile` 覆盖 `src/ui/month_window.py`、`src/ui/popups/month_day_hover_preview.py`、`src/ui/common/action_context_menu.py`、`main.py`：通过。
  - offscreen 验证月界面同日期 panel 第一次点击打开、第二次点击关闭：通过。
  - offscreen 验证月界面 `activated` 跳转会关闭已打开 panel 并发出 `date_selected`：通过。
  - offscreen 验证 hover 预览标题样式包含 `#0cc0df`：通过。
  - offscreen 验证持久弹窗日期标题样式包含 `#0cc0df`：通过。
  - offscreen 验证 `ActionContextMenu` 可构造，`skin/sort/filter` 仍禁用，`add` 和视图项仍启用：通过。
