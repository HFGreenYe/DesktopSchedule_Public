# src/config.py

class AppConfig:
    
    APP_NAME = "万机 - Wanji Desktop Schedule"

    DEFAULT_WIDTH = 324
    DEFAULT_HEIGHT = 576
    
    # --- 2. Windows 11 24H2 DWM 渲染修复常量 [2] ---
    # 强制压制系统边框与圆角，物理消除黑角与白边
    DWMWA_BORDER_COLOR = 34
    DWMWA_WINDOW_CORNER_PREFERENCE = 33
    DWMWA_COLOR_NONE = 0xFFFFFFFE # 禁用边框染色
    DWMWCP_DONOTROUND = 1         # 禁用系统圆角，由应用 QSS 自行切圆角
    
    # --- 3. 视觉主题：青色渐变视界 ---
    #COLOR_GRADIENT_START = "#3A29FF"
    #COLOR_GRADIENT_END = "#6150FF"

    COLOR_GRADIENT_START = "#0cc0df" #湖青
    COLOR_GRADIENT_END = "#78DCED" #"#99E4F1"

    #COLOR_GRADIENT_START = "#4FA23B" #芽绿
    #COLOR_GRADIENT_END = "#B9EB7B"

    #COLOR_GRADIENT_START = "#1485EE"
    #COLOR_GRADIENT_END = "#06B8FF"

    #COLOR_GRADIENT_START = "#0066CC" #幽蓝
    #COLOR_GRADIENT_END = "#0099CC"

    #COLOR_GRADIENT_START = "#17BE7B" #"#17BE7B" #茂绿
    #COLOR_GRADIENT_END = "#36C38A"   #"#2DC387"

    SUSPEND_GRADIENT_START = "#0cc0df"  # 上半部分
    SUSPEND_GRADIENT_END = "#13C2E0"    # 下半部分
    TEXT_COLOR_PRIMARY = "#FFFFFF"
    TEXT_COLOR_SECONDARY = "rgba(255, 255, 255, 200)"
    GLASS_BG_COLOR = "rgba(255, 255, 255, 35)"
    GLASS_BORDER_COLOR = "rgba(255, 255, 255, 60)"
    FONT_FAMILY = "Segoe UI"
    
    # --- 4. 按钮交互颜色 ---
    BTN_CLOSE_HOVER = "#ff5252"
    BTN_NORMAL_HOVER = "rgba(255, 255, 255, 50)"
    
    # --- 5. 头部布局顺序定义 ---
    # 用于 HeaderBar 动态生成组件

    HEADER_ITEMS = [
        "hang_up",    # 挂起
        "more",       # 更多
        "minimize",   # 最小化
        "close",      # 关闭
        "time",       # 时间
        "date",       # 日期
        "week",       # 星期
        "weather",    # 天气
        "search"      # 搜索框
    ]
    
    # --- 6. 皮肤模式定义 ---
    SKIN_MODE_SOLID = "solid"
    SKIN_MODE_GRADIENT = "gradient"
    SKIN_MODE_IMAGE = "image"
    SKIN_MODE_TRANSPARENT = "transparent"

    # --- 挂起功能常量 ---
    MINI_MODE_HEIGHT = 60       # 挂起后的条状高度
    ANIMATION_DURATION = 400    # 动画时间(ms)
    

    ICON_HANG_UP = "assets/icons/hang_up.png"   # 图3 (向上箭头)
    ICON_RESTORE = "assets/icons/restore.png"   # 图4 (下拉键)