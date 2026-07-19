# DesktopSchedule

DesktopSchedule 是一个面向 Windows 桌面的 PyQt6 日程与待办管理应用。项目以本地 SQLite 数据库为核心，提供日视图、周视图、月视图、待办列表、待办看板、提醒弹窗、天气信息和无边框桌面窗口体验。

项目采用分层架构（UI → Controller → Service → Repository → Data），支持主题切换、多视图多模式、拖拽交互和批量操作。

## 功能概览

### 日程与待办

- 日视图：支持卡片模式与课表模式（时间轴），日程拖拽调整时间、多选批量操作、完成状态、置顶、详情弹窗和提醒信息。
- 周视图：独立周窗口，支持卡片模式与课表模式，日程拖拽调整日期/跨周翻页、多选批量操作（含按天筛选范围）、暗色模式。
- 月视图：月视图窗口、挂起窗口入口、左侧空白区右键菜单。
- 待办列表：支持待办展示、分类、置顶、完成状态、排序和编辑。
- 待办看板：支持便签视图、文件夹视图、分类管理、卡片排序和独立窗口。
- 分类清单：支持日程/待办分类创建、更新、软删除、硬删除和状态判断。
- 纪念日期：支持日期标注、提醒、排序、删除和启动时到期提示。
- 日程导出：支持 Markdown、PDF、PNG、真实预览、默认/自定义背景裁剪和独立样式记忆。
- 右键菜单：日/周/月视图全面支持右键快捷操作（模式切换、视图切换、换肤、添加日程等）。
- 卡片滚动吸附：日/周视图卡片列表支持滚轮整卡步进吸附，操作更流畅。

### 重复日程

- 支持重复规则：`每天`、`每周`、`每月`
- 支持重复组 `group_id`
- 编辑重复日程时区分：仅修改当前项 / 修改当前及未来项 / 取消重复

### 提醒、天气与窗口

- 提醒弹窗：支持倒计时、已开始状态和置顶工具窗口。
- 天气信息：通过和风天气 API 获取天气数据。
- 主窗口：无边框窗口、自定义标题栏、Windows 11 DWM 边框修复。
- 挂起窗口：支持主窗口、周视图、月视图的挂起/恢复入口。
- 主题系统：已接入 `ThemeManager` 和 skin preset QSS，默认 preset 为 `default.qss`。

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
git clone https://github.com/HFGreenYe/DesktopSchedule_Public.git
cd DesktopSchedule_Public
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

4. 配置环境变量（可选）：

在项目根目录创建 `.env` 文件：

```env
QWEATHER_API_KEY=your_api_key_here
QWEATHER_API_HOST=devapi.qweather.com
```

天气功能依赖以上配置。没有配置时，应用主体仍可正常运行，但天气模块不会获取实时数据。

5. 启动应用：

```bash
python main.py
```

## 目录结构

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

项目采用适合 PyQt 桌面应用的分层架构：

- **UI 层**：负责窗口、控件、交互和展示。
- **Controller 层**：提供视图路由、刷新协调和跨视图协作边界。
- **Service 层**：承载纯业务逻辑和可复用规则（查询过滤、排序、重复日期计划、分类策略）。
- **Repository 层**：封装模型查询和基础 CRUD。
- **Data 层**：管理数据库连接、Peewee 模型、迁移和 `DatabaseManager` 兼容入口。
- **Theme 层**：集中读取和应用 QSS skin preset。

## 数据与隐私

以下文件不会提交到 Git：

- `.env`（API 密钥等敏感配置）
- `schedule.db`（本地数据库）
- `.venv/`（虚拟环境）
- `__pycache__/`（Python 缓存）

使用前请注意：

- 不要提交真实 API Key。
- 不要提交本地数据库 `schedule.db`。
- 天气图标和第三方图标资源在公开分发前应确认授权。

## 开发状态

已完成：

- 数据层模型拆分与 Peewee ORM 集成。
- Repository / Service / Controller 分层架构。
- 日/周/月/待办/看板多视图体系。
- 卡片模式与课表模式双模式。
- 多选批量操作与批量数据库事务。
- 日程拖拽调整（日视图时间、周视图日期/跨周翻页）。
- 卡片滚动吸附（CardStepScrollArea）。
- 周界面暗色模式及详情弹窗独立暗色切换。
- 全局右键菜单体系。
- 主题皮肤系统（ThemeManager + QSS preset）。
- 纪念日期功能闭环。
- Markdown / PDF / PNG 日程导出。

待补充：

- 同步功能。
- 完整的字体/颜色设置 UI。
- 四象限视图。
- `每年` / `yearly` 重复日程。
- 更系统的自动化测试。

## 备注

本项目主要面向 Windows 桌面环境开发。`src/utils/win_api.py` 中包含 Windows 11 DWM 相关修复逻辑，其他系统上不保证完整视觉效果。
