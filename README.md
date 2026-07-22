# 烂柯日程表（DesktopSchedule）

烂柯日程表是一个面向 Windows 桌面的 PyQt6 日程与待办管理应用。项目以本地 SQLite 数据库为核心，提供日视图、周视图、月视图、待办列表、待办看板、纪念日期、提醒、导出、天气信息和无边框桌面窗口体验。

当前代码已经完成主要架构整理和一轮核心功能补全：数据模型、Repository、Service、Controller、Theme、UI 拆分骨架已经建立，旧 UI 仍保持兼容运行。后续开发重点转向自动化测试、本地数据安全、云同步和最终 UI 统一。

## 功能概览

### 日程与待办

- 日视图：支持卡片模式与课表模式（时间轴）、日程拖拽调整时间、卡片多选批量完成/撤销/删除、整卡步进滚动、详情弹窗和提醒信息。
- 周视图：支持卡片模式与课表模式、按天筛选的卡片多选批量操作、整卡步进滚动，以及日程块跨日期/跨周拖拽和时间调整。
- 月视图：支持月历状态标记、日期持久弹窗、卡片/课表模式、当日课表拖拽调整、紧凑添加面板、提醒与清单选择，以及日期空白区右键菜单。
- 多日期创建：日、周、月添加界面均支持单选/多选日期、单击切换、长按拖动连续选择、已选日期时间预览、逐条提醒和原子批量保存。
- 待办列表：支持待办展示、分类、置顶、完成状态、排序和编辑。
- 待办看板：支持便签视图、文件夹视图、分类管理、卡片排序和独立窗口。
- 分类清单：支持日程/待办分类创建、更新、软删除、硬删除和状态判断。
- 纪念日期：支持创建、专用日历标注、提前提醒、倒计时排序、过期置底、右键删除和启动时到期提示。
- 日程导出：支持 Markdown、PDF、PNG、分页真实预览、Ctrl+滚轮缩放、默认/自定义背景裁剪、PNG 多页文件夹输出和各格式独立样式记忆。
- 右键菜单：日/周/月视图全面支持右键快捷操作（模式切换、视图切换、换肤、添加日程等）。
- 卡片滚动吸附：日/周视图卡片列表支持滚轮整卡步进吸附，操作更流畅。

### 重复日程

- 支持旧语义下的重复规则：
  - `每天`
  - `每周`
  - `每月`
- 日、周、月添加界面均支持由多日期选择自动派生的 `自定义` 规则；固定重复与多日期自定义状态互斥，自定义组中的具体日程可单独拆出并改为固定重复，生成时会跳过原组内已占用日期。
- 非重复规则兼容：
  - `none`
  - `无`
  - `不重复`
  - 空字符串
- 支持重复组 `group_id`。
- 支持编辑重复日程时区分：
  - 仅修改当前项
  - 修改当前及未来项
  - 取消重复

当前代码没有实现 `每年` / `yearly` 的重复生成逻辑，也没有 `parent_id` 字段；自定义日期组直接使用现有 `group_id` 和实际日程记录表达。

### 提醒、天气与窗口

- 提醒弹窗：支持倒计时、已开始状态和置顶工具窗口。
- 天气信息：通过和风天气 API 获取天气数据。
- 主窗口：无边框窗口、自定义标题栏、Windows 11 DWM 边框修复。
- 挂起窗口：支持主窗口、周视图、月视图的挂起/恢复入口。
- 主题系统：已接入 `ThemeManager` 和 skin preset QSS，默认 preset 为 `default.qss`。当前只启用浅色主题，深浅色切换将在云同步之后作为统一主题专项实现。

## 技术栈

- Python 3.11+
- PyQt6
- PyQt6-Frameless-Window
- SQLite
- Peewee ORM
- Requests
- python-dotenv
- win11toast / Windows Runtime 相关包

完整依赖见 [requirements.txt](requirements.txt)。

## 运行方式

1. 克隆仓库：

```bash
git clone https://github.com/HFGreenYe/DesktopSchedule.git
cd DesktopSchedule
```

2. 创建并启用虚拟环境：

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 配置环境变量：

在项目根目录创建 `.env` 文件：

```env
QWEATHER_API_KEY=your_api_key_here
QWEATHER_API_HOST=devapi.qweather.com
```

天气功能依赖以上配置。没有配置时，应用主体仍应可以运行，但天气模块不会正常获取实时数据。

5. 启动应用：

```bash
python main.py
```

## 当前目录结构

```text
DesktopSchedule/
├── assets/                  # 图标与天气图标资源
├── main.py                  # 应用入口
├── requirements.txt         # Python 依赖
├── src/
│   ├── controllers/         # 视图路由与刷新协调边界
│   ├── data/                # 数据连接、Peewee 模型、DatabaseManager
│   ├── models/              # 预留模型包
│   ├── repositories/        # Schedule / Category 数据访问层
│   ├── services/            # 查询、排序、重复规则、写入协调、天气等服务
│   ├── theme/               # ThemeManager 与 QSS skin preset
│   ├── ui/                  # PyQt UI 窗口、页面、弹窗和公共组件
│   │   ├── common/          # 已拆出的公共 UI 组件
│   │   ├── dialogs/         # 对话框包预留
│   │   ├── popups/          # 弹窗包预留
│   │   ├── utils/           # UI 工具
│   │   └── views/           # 视图包预留
│   └── utils/               # 信号、样式、Win32/DWM 工具
└── README.md
```

## 架构说明

当前项目不是教科书式 MVC，而是更适合 PyQt 桌面应用的分层架构：

- UI 层：负责窗口、控件、交互和展示。
- Controller 层：提供视图路由、刷新协调和跨视图协作边界。
- Service 层：承载纯业务逻辑和可复用规则，例如查询过滤、排序、重复日期计划、分类策略。
- Repository 层：封装模型查询和基础 CRUD。
- Data 层：管理数据库连接、Peewee 模型、迁移和 `DatabaseManager` 兼容入口。
- Theme 层：集中读取和应用 QSS skin preset。

目前 `DatabaseManager` 仍保留为旧 UI 的兼容入口，UI 也仍有部分历史耦合。新的代码应优先复用已有 Service / Repository / Controller 边界，避免继续把业务规则写回 UI。

## 数据与隐私

以下文件不会提交到 Git：

- `.env`
- `schedule.db`
- `.venv/`
- `__pycache__/`
- `manage_instruction/`

公开仓库前需要注意：

- 不要提交真实 API Key。
- 不要提交本地数据库 `schedule.db`。
- 不要提交本地工作日志、提示词、同步指南等 `manage_instruction/` 内容。
- 天气图标和第三方图标资源在公开分发前应确认授权。

## 开发状态

已完成：

- 数据层模型拆分。
- Repository 委托。
- 查询、排序、分类策略服务抽取。
- 重复规则计划服务和部分写入协调服务。
- Controller / Router / RefreshCoordinator 边界。
- ThemeManager 与默认 skin preset 接入。
- UI 包目录骨架和部分公共组件拆分。
- 纪念日期功能闭环。
- Markdown、PDF、PNG 导出及背景裁剪、自定义背景和样式记忆。
- 日/周视图卡片多选批量操作（完成、撤销完成、删除）与批量数据库事务。
- 日/周/月添加界面的多日期选择、自定义重复、逐条提醒和原子批量保存。
- 日/周视图课表模式（时间轴视图）。
- 月界面日期持久弹窗的卡片/课表模式，以及当日课表拖拽调整。
- 卡片滚动吸附（CardStepScrollArea）。
- 日程拖拽调整（日视图调整时间、周视图调整日期/跨周翻页）。
- 全局右键菜单体系（模式切换、视图切换、空白区右键、HeaderBar 右键）。
- 排序/筛选弹窗置顶键。
- 数据库加密方案设计（SQLCipher + PBKDF2，待实施）。

待补充：

- 自动化测试与 CI 基线，重点覆盖固定重复、自定义多日期、拆组派生和冲突跳过。
- `每年` / `yearly` 重复日程。
- 本地备份/恢复、字体与 Skin Preset 的完整用户操作流程。
- 数据库加密和本地多账号落地实施。
- 云同步、设备管理与冲突解决闭环。
- 云同步之后的统一 UI 审美、高 DPI 回归和深浅色主题专项。

最终阶段安排：云同步及其他功能完整实装后，再集中进行 UI 审美统一和主要窗口、弹窗、高 DPI 环境的整体回归；功能开发期间只修复影响操作和可读性的局部 UI 问题。

## 备注

本项目主要面向 Windows 桌面环境开发。`src/utils/win_api.py` 中包含 Windows 11 DWM 相关修复逻辑，其他系统上不保证完整视觉效果。
