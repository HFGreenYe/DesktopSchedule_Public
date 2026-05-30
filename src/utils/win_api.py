#src/utils/win_api.py
import ctypes
from ctypes import wintypes

# 加载系统库
dwmapi = ctypes.windll.dwmapi

# Windows DWM 常量
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWA_BORDER_COLOR = 34
DWMWA_COLOR_NONE = 0xFFFFFFFE  # 无色

# 圆角偏好枚举
DWMWCP_DONOTROUND = 1  # 关键：强制直角
DWMWCP_ROUND = 2

class MARGINS(ctypes.Structure):
    
    _fields_ = [
        ("cxLeftWidth", ctypes.c_int),
        ("cxRightWidth", ctypes.c_int),
        ("cyTopHeight", ctypes.c_int),
        ("cyBottomHeight", ctypes.c_int),
    ]

def apply_24h2_border_fix(hwnd):
    """
    针对 Windows 11 24H2 的终极修复：
    1. 扩展 Frame -> 解决透明背景变黑 (Black Artifacts)
    2. 禁用系统圆角 -> 解决灰色伪影/灰边 (Gray Border)
    3. 隐藏系统边框 -> 双重保险
    """
    try:
        # 1. 扩展玻璃效果到全窗口，用以解决黑屏的核心
        margins = MARGINS(-1, -1, -1, -1)
        dwmapi.DwmExtendFrameIntoClientArea(wintypes.HWND(hwnd), ctypes.byref(margins))
        
        # 2. 告诉系统：这是一个直角窗口。尝试摆脱灰色边框
        corner_pref = ctypes.c_int(DWMWCP_DONOTROUND)
        dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            wintypes.DWORD(DWMWA_WINDOW_CORNER_PREFERENCE),
            ctypes.byref(corner_pref),
            ctypes.sizeof(corner_pref)
        )
        
        # 3. 显式禁用边框颜色，双重保险
        color = ctypes.c_int(DWMWA_COLOR_NONE)
        dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            wintypes.DWORD(DWMWA_BORDER_COLOR),
            ctypes.byref(color),
            ctypes.sizeof(color)
        )
    except Exception as e:
        print(f"WinAPI Error: {e}")