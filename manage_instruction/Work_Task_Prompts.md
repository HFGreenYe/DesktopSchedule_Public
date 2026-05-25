请执行第七轮 7-0：主题与样式债务静态审查。本轮只做代码阅读、搜索、分析和日志记录，不改源码。

## 1. 本轮目标

基于 manage_instruction/Work_Instruction.md 中第七轮阶段合同，审查当前主题系统、QSS 文件、StyleManager、内联 setStyleSheet 分布和样式债务，为后续 Theme/QSS 小步接入建立基线。

本轮只读审查，不接入 ThemeManager，不改 QSS，不改 UI。

重点审查：

- src/theme/theme_manager.py 当前能力与缺口。
- src/theme/light.qss / src/theme/dark.qss 当前内容。
- main.py 当前 QApplication 启动流程。
- src/utils/styles.py 当前 StyleManager 职责。
- src/ui/ 下 setStyleSheet 高频分布。
- 当前已有 global_signals.skin_changed / theme_changed 是否满足第七轮信号兼容需求。
- 哪些控件适合作为低风险 QSS 动态属性试点。
- 哪些样式债务应推迟到第八轮 UI 大文件拆分。

本轮必须输出：

- ThemeManager 能力/缺口清单。
- QSS 文件状态。
- StyleManager 职责地图。
- setStyleSheet 热点文件和热点类型。
- 低风险试点候选项。
- 不适合第七轮处理、应推迟的样式债务。
- 对 7-1 / 7-2 / 7-3 的建议。

## 2. 允许/禁止

本轮允许修改：

- manage_instruction/Work_Log.md
- manage_instruction/Work_Task_Prompts.md（仅在需要维护本轮复核锚点时）

本轮禁止修改：

- src/
- main.py
- requirements.txt
- schedule.db
- Work_Snapshot.md
- Work_Formulation.md

禁止事项：

- 不修改 ThemeManager。
- 不修改 light.qss / dark.qss。
- 不修改 main.py。
- 不修改 StyleManager。
- 不修改任何 UI 文件。
- 不新增动态属性。
- 不新增或修改信号。
- 不接入 ThemeManager。
- 不运行换肤 UI。
- 不批量清理 setStyleSheet。
- 不提交 Git。

若开工前已有 manage_instruction/Work_Instruction.md 或其他管理文档 diff，需要在 Work_Log.md 中单独记录为开工前既有状态，不视为本轮源码改动。

## 3. 具体任务

1. 读取第七轮阶段合同：

    Get-Content -Path manage_instruction\Work_Instruction.md -Encoding UTF8

2. 审查 theme 目录：

    Get-ChildItem -Path src\theme -Force

    Get-Content -Path src\theme\theme_manager.py -Encoding UTF8

    Get-Content -Path src\theme\light.qss -Encoding UTF8

    Get-Content -Path src\theme\dark.qss -Encoding UTF8

    Get-Content -Path src\theme\__init__.py -Encoding UTF8

3. 审查 QApplication 启动流程：

    Get-Content -Path main.py -Encoding UTF8

4. 审查 StyleManager：

    Get-Content -Path src\utils\styles.py -Encoding UTF8

5. 审查现有信号：

    Get-Content -Path src\utils\signals.py -Encoding UTF8

6. 搜索 ThemeManager / QSS / theme 使用情况：

    rg -n "ThemeManager|apply_theme|apply_qss|read_qss|theme_changed|skin_changed|global_signals|light\.qss|dark\.qss|\.qss|QSS|theme" src main.py

7. 搜索 setStyleSheet 高频分布：

    rg -n "setStyleSheet\(" src

8. 搜索 StyleManager 使用点：

    rg -n "StyleManager\.|get_tooltip_style|get_button_style|get_menu_style|get_header_container_style|get_search_input_style|get_window_control_style" src

9. 搜索动态属性使用情况：

    rg -n "setProperty\(|property\(|dynamicProperty|role|state|variant" src

10. 搜索 add view 中“设置字体”与 theme_color 相关既有缺口：

    rg -n "设置字体|btn_font|theme_color|font|color" src/ui/add_view.py src/ui/add_view_week.py src/data/models.py src/data/database.py src/repositories src/services

11. 统计或归纳 setStyleSheet 热点文件。

建议至少关注：

- src/ui/add_view.py
- src/ui/add_view_week.py
- src/ui/main_window.py
- src/ui/header.py
- src/ui/list_picker.py
- src/ui/month_window.py
- src/ui/todo_board.py
- src/ui/week_window.py
- src/ui/calendar_pop.py
- src/ui/schedule_detail_pop.py
- src/utils/styles.py

12. 形成 ThemeManager 能力/缺口清单，至少判断：

- 是否能读取 QSS。
- 是否能 apply 到 QApplication。
- 是否能刷新 QWidget 动态属性样式。
- 是否能列出 skin preset。
- 是否有默认主题名。
- 是否有失败兜底。
- 是否依赖 UI/db/Repository。
- 是否已接入 main.py。

13. 形成 QSS 文件状态，至少记录：

- light.qss 当前是否为占位。
- dark.qss 当前是否为占位。
- 是否已有动态属性选择器。
- 是否已有全局基础规则。
- 是否适合直接应用到生产 UI。

14. 形成 StyleManager 职责地图，至少记录：

- 哪些公共样式仍在 StyleManager。
- 哪些 UI 直接使用 StyleManager。
- 哪些 UI 完全内联 setStyleSheet。
- 哪些样式适合未来迁到 QSS。
- 哪些样式本轮不应移动。

15. 形成低风险试点候选项。

建议按风险分级：

- 低风险：
  - tooltip / toast / 单个非业务按钮 / 窗口控制按钮 role 动态属性。
- 中风险：
  - Header 局部输入框或按钮。
  - ListPicker 单个按钮。
- 高风险：
  - add_view / week_window / todo_board / month_window 大块内联样式。
  - CalendarPop 内部主题切换逻辑。
  - ScheduleDetailPop source_view 样式分支。
  - theme_color / 设置字体功能闭环。

16. 输出对后续小工单的建议：

- 7-1 应如何完善 ThemeManager。
- 7-2 默认 QSS 接入应采用哪个默认 skin preset。
- 7-3 动态属性规范应采用哪些命名。
- 7-4 试点控件建议选哪个，为什么。
- 哪些内容应明确推迟到第八轮 UI 拆分或第九轮功能轮。

## 4. 验收命令

完成审查和日志记录后执行范围检查：

    git diff --name-only -- src

    git diff --name-only -- main.py

    git diff --name-only -- requirements.txt

    git diff --name-only -- schedule.db

    git diff --name-only

    git status --short --branch

预期：

- src 无 diff。
- main.py 无 diff。
- requirements.txt 无 diff。
- schedule.db 无 diff。
- 最终只允许 manage_instruction/Work_Log.md，以及必要时的 manage_instruction/Work_Task_Prompts.md。
- 如果开工前已有 manage_instruction/Work_Instruction.md diff，需要在日志中明确说明它是开工前既有状态，不属于 7-0 执行改动。

## 5. 日志要求

更新 manage_instruction/Work_Log.md，至少记录：

- 本轮任务名称：第七轮 7-0（主题与样式债务静态审查）
- 开工前 git 状态
- 实际修改文件
- 读取的第七轮阶段合同结论
- 静态搜索命令和关键结果
- ThemeManager 能力/缺口清单
- QSS 文件状态
- main.py 启动流程中的主题接入现状
- StyleManager 职责地图
- setStyleSheet 热点文件和热点类型
- 动态属性使用现状
- skin_changed / theme_changed 信号现状
- theme_color / 设置字体相关既有缺口
- 低风险试点候选项
- 中/高风险样式债务
- 建议推迟到第八轮 UI 拆分或第九轮功能轮的内容
- 对 7-1 / 7-2 / 7-3 / 7-4 的建议
- diff 范围检查结果
- 未完成事项
- 风险或疑点

完成后不要提交 Git，等待顾问窗口复核。
