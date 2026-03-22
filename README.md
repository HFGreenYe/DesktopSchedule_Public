# Wanji Schedule (万机 - 桌面日程表)

## Introduction

Wanji Schedule 是一款专为 Windows 11 (特别是 24H2 版本) 架构深度优化的现代化桌面日程与待办管理应用。

项目旨在提供一个美观、无干扰且功能强大的桌面效率工具。它摒弃了传统的系统窗口边框，主界面采用 9:16 的类手机屏幕比例布局，并支持无缝扩展至宽屏周视图与独立的待办看板。通过深度集成实时天气服务与本地数据库，万机致力于打造浑然一体的桌面微件体验。

## Tech Stack

* Core Language: Python 3.11+
* GUI Framework: PyQt6 (6.7.0+)
* System Adaptation: Windows 11 Win32 API (ctypes, dwmapi)
* Data Storage: SQLite3 (Peewee ORM)

## Key Features

### Visuals & Interaction
* 无边框磨砂玻璃 UI: 彻底移除系统原生标题栏，采用自定义绘图与布局。
* Win11 24H2 渲染修复: 底层调用 DWM API，解决了 24H2 版本特有的透明窗口变黑、白边溢出及圆角锯齿问题。
* 桌面挂件模式 (Suspend Mode): 支持一键“挂起”为迷你条状悬浮窗，节省屏幕空间，同时保留拖拽与一键还原功能。
* 沉浸式标题栏: 顶部集成实时天气、数字时钟、农历显示及自定义窗口控制键。
* 动态 UI 渲染: 支持 SVG 图标的高清动态重绘与染色，完美适配不同背景色彩。

### Schedule & Task Management
* 核心日视图 (Dashboard): 直观的纵向日程流，包含优先级标识、完成状态切换及实时倒计时气泡提示。
* 宽屏周视图 (Week View): 独立的大屏日历面板。支持跨天拖拽日程，系统将自动计算并平移开始、结束及提醒时间。
* 独立待办看板 (Todo Board): 独立的 Kanban 界面，提供“便签视图”与“文件夹视图”。支持卡片的自由拖拽排序与跨列插空。
* 高级提醒系统: 支持自定义提醒时间、有声强提醒（系统闹钟）及多种持续响铃时长选择。
* 循环日程引擎: 支持创建每天、每周、每月的重复规则，并在修改时智能区分“仅修改本次”与“修改未来”。
* 清单分类管理: 可创建多组分类清单，待办事项与常规日程均可归档至不同清单中。
* 窗口层级控制: 支持一键窗口置顶，防止被其他应用遮挡。

## Installation & Setup

1. 克隆项目到本地:
   git clone https://github.com/yourusername/Wanji_Schedule.git
   cd Wanji_Schedule

2. 配置虚拟环境并安装依赖:
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt

3. 环境变量配置 (.env):
   在项目根目录下新建 `.env` 文件，填入您的 QWeather (和风天气) API 凭证，以启用天气模块：
   QWEATHER_API_KEY=your_api_key_here
   QWEATHER_API_HOST=devapi.qweather.com

4. 运行应用:
   python src/main.py

## Project Structure

```text
Wanji_Schedule/
├── assets/                 # 静态资源 (SVG 图标、天气图标库)
├── src/                    # 源代码
│   ├── data/               # 数据层 (database.py 包含 Peewee ORM 模型)
│   ├── services/           # 异步服务层 (weather_service.py)
│   ├── ui/                 # UI 界面与交互层
│   │   ├── main_window.py  # 核心主窗口路由
│   │   ├── dashboard.py    # 日视图主面板
│   │   ├── week_window.py  # 宽屏周视图
│   │   ├── todo_board.py   # 独立待办看板
│   │   └── ...             # 其他各类选择器与弹窗组件
│   ├── utils/              # 核心工具库 (win_api.py, styles.py)
│   ├── config.py           # 全局尺寸与色彩配置
│   └── main.py             # 程序启动入口
├── .gitignore              # Git 忽略配置
└── requirements.txt        # Python 依赖清单
```

## Roadmap

* 导出功能: 支持将日程数据导出为 PDF 或 Excel 文件。
* 云端同步: 搭建后端 API，实现多端设备的数据互通。
* AI 辅助: 接入大语言模型，支持识别自然语言文本并一键创建日程。
* 更多视图支持: 开发月视图 (Month View) 与四象限矩阵视图 (Eisenhower Matrix)。

## Notes for Developers

* Windows 11 DWM 兼容性: `src/utils/win_api.py` 包含了针对 Windows 11 DWM 的硬核补丁。每次动态修改窗口状态 (如切换置顶 `WindowStaysOnTopHint`) 时，必须重新调用 `apply_24h2_border_fix`，否则界面会出现黑色伪影。
* 拖拽重排逻辑: 看板视图的拖拽排序使用了基于中心点距离的实时推挤算法，排序权重 (`sort_order`) 采用浮点数取中值计算，避免了频繁的数据库批量更新。