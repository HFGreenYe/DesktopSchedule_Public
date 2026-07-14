# History Instruction

用途：归档已经完成或废弃的阶段合同、执行指令和重要规划结论。

本文件只存历史，不作为当前执行依据。当前执行依据见：

- `Work_Formulation.md`
- `Work_Instruction.md`
- `Work_Task_Prompts.md`

---

## 归档规则

- 每个阶段结束后，由主窗口确认可归档。
- 归档内容应包含阶段目标、允许/禁止范围、关键小工单、验收结论。
- 已归档内容不得在当前阶段直接修改；如需引用，只读查看。
- 旧架构改写阶段的完整历史已移入 `ReconstructionDolder/`。

---

## 当前归档索引

### 2026-06-01：右键上下文菜单阶段

阶段名称：功能补充 - 主界面 / 周界面右键上下文菜单。

归档结论：

- 右键上下文菜单阶段已完成并通过 CM-4 整体验收。
- 本阶段可归档。
- 后续可继续进入月界面功能补齐或新的功能补充规划。

阶段目标：

- 主界面日程空状态区域和列表空白区域支持页面级右键菜单。
- 周界面日期白色空白区域支持页面级右键菜单。
- 菜单采用公共 `ActionContextMenu` 组件。
- 已实装动作：
  - 添加
  - 日 / 周 / 月 / 待办视图切换
- 保持禁用或占位：
  - 换肤
  - 排序
  - 筛选
  - 四象限视图

关键小工单：

- `CM-0`：右键菜单现状审查与精确边界。
- `CM-1`：公共 icon-text 上下文菜单组件试点。
- `CM-2`：主界面日程区域右键菜单接入。
- `CM-3`：周界面日期空白区域右键菜单接入。
- `CM-4`：右键上下文菜单整体验收与归档准备。

关键提交：

- `8a6c551 docs: record cm-0 context menu boundary review`
- `6fb847f refactor: add reusable action context menu`
- `3481655 feat: add dashboard context menu bridge`
- `76f2f94 feat: add week empty area context menu`
- `bae834e docs: close context menu validation`

保留边界：

- 未实现真实换肤 UI。
- 未实现排序和筛选完整功能。
- 未实现四象限视图。
- 未修改数据库字段。
- 未改变 `ScheduleCard` / `WeekScheduleCard` 既有右键菜单。
- 未改变周界面左键选中、双击跳日视图和卡片拖拽排序。

---

### 2026-06-04：月界面功能补齐阶段

阶段名称：功能补充 - 月界面功能补齐。

归档结论：

- 月界面功能补齐阶段已完成并通过 M-7 整体验收。
- 本阶段可归档。
- 后续不应继续在本阶段追加零散功能，应进入下一阶段规划或单独开启 UI 适配阶段。

阶段目标：

- 月格显示日程状态摘要，不在小格内塞完整日程文本。
- 今天只用日期数字金色表示，不再默认整格高亮。
- 单击日期表示用户选中，选中态使用整格高亮。
- 双击 / activated 日期跳转对应日视图，并关闭所有月界面持久浮窗。
- hover 日期显示只读预览，移出后隐藏。
- 单击日期显示月界面外侧持久 panel。
- 添加按钮优先使用用户选中日期，过去日期不可添加。
- 月界面左侧添加表单补齐 time / alarm / list picker 承接和保存结构。
- 月界面右键菜单复用 `ActionContextMenu`，只实装“添加”和“视图”。

关键小工单：

- `M-0`：月界面现状审查与交互边界定位。
- `M-1`：月格状态 marker 与今天金色日期。
- `M-2`：月格单击选中与双击跳日视图。
- `M-3`：hover 只读预览弹窗。
- `M-4`：单击日期持久 panel 壳。
- `M-5`：添加按钮使用选中日期。
- `M-5b`：月界面添加表单能力只读审查与 picker 承接方案确认。
- `M-5c`：月界面添加表单 UI 壳补齐。
- `M-5d`：月界面 time picker 接入。
- `M-5e`：月界面 alarm / list picker 接入。
- `M-5f`：月界面 priority / repeat / 保存结构对齐。
- `M-5g`：月界面添加能力整体验收。
- `M-6`：月界面右键菜单接入。
- `M-7`：月界面功能补齐整体验收。

关键提交：

- `ba1a7f5 docs: plan month view feature phase`
- `1057220 docs: record m-0 month view boundary review`
- `0d3f375 feat: add month view schedule markers`
- `44bff9f feat: update month date click behavior`
- `9002bd7 feat: add month day hover preview`
- `de35fe7 feat: add month day persistent panel shell`
- `4726625 feat: use selected month date for add action`
- `20eb377 feat: add month add form shell`
- `c7db4fa feat: connect month add time picker`
- `af76634 feat: connect month add alarm and list pickers`
- `bd0c378 feat: align month add save fields`
- `166b2c3 feat: add month view context menu`
- `742b6be docs: close month view feature validation`

保留边界：

- 未实现四象限视图。
- 未实现真实换肤 UI。
- 未实现排序和筛选完整功能。
- 未修改数据库字段。
- 未进行像素级 UI 适配和布局重排。
- 未做真实写库自动化验收；保存结构通过 mock / monkeypatch 验证。
- 周视图右键切换仍不携带“跳到指定周”的上下文，保持既有主路由边界。

---

### 2026-06-24 至 2026-06-25：月日程持久 panel 详情与编辑路由阶段

阶段名称：月日程持久 panel 详情与编辑路由，代号 `MP`。

归档结论：

- `MP-0` 到 `MP-5` 已完成并通过阶段验收。
- 月日程 panel 的列表承载、共享详情打开、跨视图生命周期、动态编辑路由和保存后刷新均达到阶段目标。
- 本阶段可归档；后续月界面视觉细调不再继续追加到 `MP` 合同。

阶段目标：

- 将月界面单击日期产生的持久 panel 改造成可承载日程列表的紧凑界面。
- 日程项双击打开共享 `ScheduleDetailPop`，并维护父 panel 与子详情生命周期。
- 普通日 / 周 / 月 / 待办视图切换不销毁月 panel；显式关闭和应用退出继续清理。
- 详情编辑按当前可见视图路由，不把创建时 `source_view` 作为最终决策。
- 保存后刷新月格 marker、hover cache、已打开 panel、子详情和相关视图。

关键小工单：

- `MP-0`：现状审查与路由边界定位。
- `MP-1`：月日程 panel 紧凑列表 UI 与数据承载。
- `MP-2`：日程项双击打开共享详情弹窗。
- `MP-3`：panel 生命周期与跨视图保留规则。
- `MP-4`：详情编辑请求按当前可见视图动态路由。
- `MP-5`：保存后多视图刷新与阶段整体验收。

关键提交：

- `d40ed8d docs: plan month day panel detail routing stage`
- `c655633 docs: record mp-0 month panel routing review`
- `f75e3b4 refactor: compact month day panel list ui`
- `0887b1c feat: open schedule detail from month day panel`
- `527a021 fix: retain month day panels on view hide`
- `affecc7 docs: record mp-4 detail edit routing validation`
- `7fbd018 fix: refresh month panel detail changes`
- `1d4607e fix: retain month day panels across view switches`

保留边界：

- 未修改数据库字段、重复规则写入语义或 `db_manager` 对外 API。
- `ScheduleDetailPop` 不直接调用具体页面；`MainWindow` 继续承担路由和刷新协调。
- 未进行真实写库自动化验收；使用 fake schedule / monkeypatch / offscreen smoke 验证。
- `MainWindow` 完整 offscreen 进程曾在断言完成后以 code 1 收尾，刷新断言本身通过；真实桌面环境仍保留回归检查。

---

### 2026-06-29 至 2026-07-06：坐标看板与主题选色弹窗第一版

阶段名称：坐标看板与主题选色弹窗收尾。

归档结论：

- 坐标看板第一版核心功能已完成并接入“更多 -> 坐标看板”。
- 真实日程投影、显示设置、颜色覆盖、持久化、详情交互、刷新和窗口交互达到第一版使用标准。
- 主题选色弹窗完成单窗口化、主题化、几何对齐及自定义颜色槽持久化。
- 本阶段可归档；后续只按独立增强处理完成日程开关、驻留定时刷新、自动扩窗和高 DPI / 多屏回归。

阶段目标与完成范围：

- 使用以“现在”为原点的单条水平时间轴展示过去与未来日程。
- DDL / 单时间点使用竖线，时间段使用横条；按清单颜色、重要性和完成状态绘制。
- 支持线性与 `log(t+1)` 非均匀映射、未来 / 双向 / 过去及五档时间范围。
- 对范围外点日程执行筛除，对跨边界时间段执行裁剪；hover 仍显示原始完整时间。
- 支持重叠轨道避让、画布拖动、滚轮缩放、窗口拖动、四边 / 四角 resize、置顶和关闭。
- hover 显示只读信息和时间辅助线；单击打开共享详情并复用跨视图编辑与刷新链。
- 设置页支持数轴、字体、清单颜色与透明度并实时驱动真实画布。
- 使用独立 `QSettings` 保存方向、跨度、非均匀映射、轴体 / 字体外观和按 `category_id` 建立的清单覆盖。
- 选色弹窗采用单一非原生 Qt 顶级窗口，不使用 `QGraphicsProxyWidget` 嵌套 `QColorDialog`。

保留边界：

- 第一版不提供独立的“显示完成日程”开关，范围内已完成日程固定显示在轴下方。
- 第一版不在看板持续打开且数据无变化时按分钟重算“现在”；打开和数据变化时刷新。
- 第一版不按轨道数量自动扩大窗口；保留屏幕边界回退、最小尺寸和手动 resize。
- Windows 高 DPI、多屏边界、系统拾色和原生 resize 继续作为 UI 回归项，不阻塞阶段归档。
- 看板暂不展示待办和无有效时间的条目，不新增数据库字段。

---

### 2026-07-06：坐标看板归档后增强与最终回归

阶段名称：坐标看板第一版归档后增强收尾。

归档结论：

- 第一版归档时保留的完成日程开关、驻留刷新、轨道自动扩窗和高 DPI / 多屏回归均已完成。
- 设置页布局、未分类颜色、窗口拖动、resize 时间跨度和弹窗边界一并收口。
- 本阶段可归档；坐标看板不再保留当前活动工单，后续仅在出现真实缺陷时单独修复。

完成范围：

- 增加“已完成显示”开关，并与真实画布、效果预览、顶部说明和 `QSettings` 接线。
- 看板可见时每分钟重算相对时间；隐藏或关闭后停止定时器。
- 按当前可见轨道自动增高窗口，只增不缩，并受当前屏幕可用高度限制。
- 恢复设置齿轮旋转；设置页非交互区域及显示框外侧空白支持窗口拖动，最外 `12px` 保持 resize 优先。
- 最低高度设为 `320px`；清单颜色首列最多 4 项，第 5 项进入后续列。
- 清单颜色组增加“默认”项，控制无清单 / 未分类日程颜色与透明度并持久化。
- 外框 resize 不改变数轴两端时间跨度；只有显示框内滚轮主动缩放时间。
- 完成 Qt `1.0 / 1.5 / 2.0` 缩放、Windows DPR `1.25`、负坐标双屏和原生 resize 回退验证。

保留边界：

- 坐标看板仍不展示待办和无有效时间的条目。
- 不新增数据库字段，不把看板颜色覆盖写回清单表。
- 真实物理环境只有一块显示器；多屏使用负坐标双屏矩形覆盖边界算法，后续新增硬件环境时继续做人工回归。
- `schedule_axis_board.py` 仍是大型 UI 文件；未来扩展前先补测试再拆分，不在本阶段重构。

---

### 2026-07-08 至 2026-07-14：课程表模式阶段归档
阶段名称：日 / 周 / 月持久弹窗课程表模式阶段。
归档结论：
- 日界面课程表模式已完成真实日程渲染、颜色持久化、详情弹窗改色、完成 / 删除菜单、单击选中、双击详情、时间段拖拽 / 拉伸、DDL / 单时间线段拖拽、贴边滚动和拖拉刻度设置。
- 周界面课程表模式已完成 7 日并列渲染、每日独立滚动、真实日程块 / DDL 线段绘制、悬停预览、详情弹窗、右键菜单、选中态、时间段拖拽 / 拉伸、DDL 跨日拖拽和拖动自动翻周。
- 月界面持久日期弹窗在课表模式且当日有日程时已切换为只读课表框；无日程日期和卡片模式保持原样，并支持局部暗色切换。
- 模式选择、课表颜色、默认颜色和拖拉刻度均使用独立 `timetable_preferences` 持久化，不与坐标看板配置混用。
- 本阶段可归档；后续只在出现真实缺陷时单独修复，不继续追加拖拽、拉伸或暗色细修作为本阶段内容。
关键范围：
- `src/ui/dashboard.py`
- `src/ui/week_window.py`
- `src/ui/month_window.py`
- `src/ui/popups/month_day_panel.py`
- `src/ui/main_window.py`
- `src/ui/schedule_detail_pop.py`
- `src/utils/timetable_preferences.py`
- `assets/icons/drag.svg`
- `assets/icons/refresh.svg`
- `assets/icons/1.svg`
- `assets/icons/5.svg`
保留边界：
- 不把月格本体改为课表视图。
- 不在本阶段继续推进完整暗色模式；暗色模式已转入皮肤功能后的独立规划。
- 不实现搜索 / 筛选、导出、换肤、加密、云同步或自动化测试体系。