# src/utils/styles.py
import os
import re
import tempfile
from pathlib import Path

from ..config import AppConfig
from PyQt6.QtGui import QColor

class StyleManager:
    @staticmethod
    def mix_colors(primary, secondary="#ffffff", primary_ratio=0.5):
        primary_color = QColor(primary)
        secondary_color = QColor(secondary)
        if not primary_color.isValid():
            primary_color = QColor("#0cc0df")
        if not secondary_color.isValid():
            secondary_color = QColor("#ffffff")

        ratio = max(0.0, min(float(primary_ratio), 1.0))
        inverse = 1.0 - ratio
        return QColor(
            round(primary_color.red() * ratio + secondary_color.red() * inverse),
            round(primary_color.green() * ratio + secondary_color.green() * inverse),
            round(primary_color.blue() * ratio + secondary_color.blue() * inverse),
        ).name()

    @staticmethod
    def theme_accent_color():
        color = QColor(AppConfig.COLOR_GRADIENT_START)
        if not color.isValid():
            color = QColor("#0cc0df")
        return color.name()

    @staticmethod
    def color_to_rgba(color_hex, alpha):
        color = QColor(color_hex)
        if not color.isValid():
            color = QColor(AppConfig.COLOR_GRADIENT_START)
        alpha = max(0.0, min(float(alpha), 1.0))
        return f"rgba({color.red()}, {color.green()}, {color.blue()}, {alpha:.2f})"

    @classmethod
    def theme_overlay_rgba(cls, alpha=0.10):
        return cls.color_to_rgba(cls.theme_accent_color(), alpha)

    @classmethod
    def get_tinted_svg_icon_path(cls, icon_name, color_hex=None):
        color = QColor(color_hex or cls.theme_accent_color())
        if not color.isValid():
            color = QColor(cls.theme_accent_color())
        source_path = Path(os.getcwd()) / "assets" / "icons" / icon_name
        if not source_path.exists():
            return str(source_path).replace("\\", "/")

        safe_color = color.name().lstrip("#")
        cache_dir = Path(tempfile.gettempdir()) / "desktop_schedule_tinted_icons"
        cache_dir.mkdir(parents=True, exist_ok=True)
        target_path = cache_dir / f"{source_path.stem}_{safe_color}{source_path.suffix}"
        if target_path.exists() and target_path.stat().st_mtime >= source_path.stat().st_mtime:
            return str(target_path).replace("\\", "/")

        text = source_path.read_text(encoding="utf-8")
        if re.search(r'fill="[^"]*"', text):
            text = re.sub(r'fill="[^"]*"', f'fill="{color.name()}"', text)
        else:
            text = text.replace("<path ", f'<path fill="{color.name()}" ', 1)
        target_path.write_text(text, encoding="utf-8")
        return str(target_path).replace("\\", "/")

    @staticmethod
    def derive_surface_rgba(base_color=None, dark_factor=115, alpha=0.9):
        color = QColor(base_color or AppConfig.COLOR_GRADIENT_START)
        if not color.isValid():
            color = QColor("#0cc0df")
        color = color.darker(max(100, int(dark_factor)))
        alpha = max(0.0, min(float(alpha), 1.0))
        return f"rgba({color.red()}, {color.green()}, {color.blue()}, {alpha:.2f})"

    @classmethod
    def get_detail_editor_style(cls):
        background = cls.derive_surface_rgba(
            AppConfig.COLOR_GRADIENT_START,
            dark_factor=115,
            alpha=0.9,
        )
        return f"""
            QTextEdit {{
                background-color: {background};
                border: 1px solid rgba(255, 255, 255, 0.6);
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-family: 'Microsoft YaHei';
                padding: 8px;
            }}
            QTextEdit:focus {{
                border: 1px solid rgba(255, 255, 255, 0.9);
                background-color: {background};
            }}
        """

    @staticmethod
    def get_main_window_style():
        return f"""
        QWidget#CentralWidget {{
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 {AppConfig.COLOR_GRADIENT_START},
                stop:1 {AppConfig.COLOR_GRADIENT_END});
            border-radius: 12px;
        }}
        """

    @staticmethod
    def get_glass_style(is_input=False):
        base_style = f"""
            background-color: {AppConfig.GLASS_BG_COLOR};
            border: 1px solid {AppConfig.GLASS_BORDER_COLOR};
            border-radius: 15px;
            color: {AppConfig.TEXT_COLOR_PRIMARY};
            font-family: '{AppConfig.FONT_FAMILY}';
            padding: 5px 15px;
        """
        if is_input:
            base_style += """
            QLineEdit:focus {
                background-color: rgba(255, 255, 255, 50);
                border: 1px solid #FFFFFF;
            }
            """
        return f"QFrame, QLineEdit, QLabel {{ {base_style} }}"

    @staticmethod
    def get_button_style(is_close=False):
        hover_bg = AppConfig.BTN_CLOSE_HOVER if is_close else AppConfig.BTN_NORMAL_HOVER
        return f"""
        QPushButton {{
            background-color: transparent;
            border: none;
            border-radius: 5px;
            color: {AppConfig.TEXT_COLOR_PRIMARY};
            font-family: '{AppConfig.FONT_FAMILY}';
            font-weight: bold;
            font-size: 13px;
            padding: 4px 8px;
        }}
        QPushButton:hover {{
            background-color: {hover_bg};
        }}
        QPushButton:pressed {{
            background-color: rgba(0, 0, 0, 20);
        }}
        """
    
    @staticmethod
    def get_menu_style():
        """获取菜单样式 (浅色/深色磨砂)"""
        icon_path = StyleManager.get_tinted_svg_icon_path(
            "check.svg",
            AppConfig.COLOR_GRADIENT_START,
        )
        bg_color = "rgba(255, 255, 255, 0.95)"
        text_color = "#333333"
        border_color = "rgba(0, 0, 0, 0.1)"
        hover_bg = StyleManager.theme_overlay_rgba(0.10)
        hover_text = StyleManager.theme_accent_color()

        return f"""
            QMenu {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 5px;
                padding: 6px;
                color: {text_color};
            }}
            QMenu::item {{
                background-color: transparent;
                padding: 8px 24px 8px 34px;
                border-radius: 8px;
                margin: 2px 4px;
                font-family: "Microsoft YaHei UI";
                font-size: 13px;
                color: {text_color};
            }}
            QMenu::item:selected {{
                background-color: {hover_bg};
                color: {hover_text};
            }}
            
            QCheckBox {{
                color: {text_color};
                font-family: 'Microsoft YaHei UI';
                font-size: 13px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px; height: 16px;
                border: 1px solid #999;
                border-radius: 4px;
                background: transparent;
            }}
            
            /* 选中状态：修复了之前的语法错误，并使用了绝对路径 */
            QCheckBox::indicator:checked {{
                background-color: #ffffff;
                border: 1px solid #999;
                image: url('{icon_path}');
            }}
            
            QMenu::separator {{
                height: 1px;
                background: {border_color};
                margin: 4px 10px;
            }}
        """

    @staticmethod
    def get_header_container_style():
        """Header 整体容器背景样式"""
        return """
            QFrame#header_container {
                background-color: #0cc0df; 
                border-bottom: 1px solid rgba(0, 0, 0, 0.05);
            }
            /* 确保 Header 里的 Label 默认白色 */
            QLabel {
                color: white;
                background: transparent;
                border: none;
            }
        """

    @staticmethod
    def get_search_input_style():
        """获取搜索框样式"""
        return """
            QLineEdit {
                /* 🟢 背景：改回极淡的透明白，甚至可以直接用 transparent */
                background-color: rgba(255, 255, 255, 0.2); 
                
                /* 🟢 边框：2px 纯白，找回那种“高亮”的感觉 */
                border: 2px solid #FFFFFF; 
                
                border-radius: 6px; /* 圆角稍微大一点点 */
                color: white;
                
                /* 保持左边距，给图标留位 */
                padding-left: 0px; 
                padding-right: 8px;
                padding-top: 2px;
                padding-bottom: 3px;
                
                font-family: "Microsoft YaHei UI";
                font-size: 13px;
            }
            QLineEdit:hover {
                /* 悬停时稍微亮一点，但不要太白 */
                background-color: rgba(255, 255, 255, 0.15);
                border: 2px solid #FFFFFF;
            }
            QLineEdit:focus {
                /* 聚焦时变实心白 */
                background-color: rgba(255, 255, 255, 0.2); 
                color: white; 
                border: 2px solid white;
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.7);
            }
        """

    @staticmethod
    def get_tool_button_style():
        """功能按钮样式"""
        return """
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.2); 
            }
            QToolButton:pressed {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """

    @staticmethod
    def get_window_control_style(is_close=False):
        """获取右上角窗口控制按钮样式 (修复：圆角 + 居中)"""
        if is_close:
            # 关闭按钮：悬停变红
            return """
                QToolButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 6px; /* 🟢 找回圆角：6px 看起来比较圆润 */
                    margin: 0px;        /* 🟢 修复下移：清除外边距 */
                    padding: 0px;       /* 🟢 修复下移：清除内边距，确保图标绝对居中 */
                }
                QToolButton:hover {
                    background-color: #ff4d4f; 
                }
                QToolButton:pressed {
                    background-color: #d9363e;
                }
            """
        else:
            # 最小化/云同步等：悬停变白
            return """
                QToolButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 6px; /* 🟢 找回圆角 */
                    margin: 0px;
                    padding: 0px;
                }
                QToolButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
                QToolButton:pressed {
                    background-color: rgba(255, 255, 255, 0.3);
                }
            """
        

    @staticmethod
    def get_tooltip_style():
        """全局美化 ToolTip (鼠标悬停提示框)"""
        return """
            QToolTip {
                /* 🎨 背景：纯白，稍微带点透明度看起来更高级 */
                background-color: #ffffff;
                
                /* 🔡 文字：深灰色，清晰易读 */
                color: #333333;
                
                /* 🖼️ 边框：青色细边框，呼应主题 */
                border: 1px solid __THEME_PRIMARY__;
                
                /* ✨ 圆角和内边距 */
                border-radius: 2px;
                padding: 1px 3px;
                
                /* 字体设置 */
                font-family: "Microsoft YaHei UI";
                font-size: 12px;
            }
        """.replace("__THEME_PRIMARY__", AppConfig.COLOR_GRADIENT_START)
    
    @classmethod
    def get_calendar_style(cls):
        """QCalendarWidget 深度美化"""
        weekday_background = cls.mix_colors(
            AppConfig.COLOR_GRADIENT_START,
            "#ffffff",
            primary_ratio=0.2,
        )
        return """
            QCalendarWidget QWidget { 
                alternate-background-color: __WEEKDAY_BACKGROUND__;
                background-color: white;
            }
            /* 导航条 (顶部 年/月) */
            QCalendarWidget QWidget#qt_calendar_navigationbar { 
                background-color: white; 
                border-bottom: 1px solid #eee;
            }
            /* 导航条上的按钮 (左右箭头) */
            QToolButton {
                color: #333;
                background-color: transparent;
                border: none;
                font-weight: bold;
                icon-size: 20px; 
            }
            QToolButton:hover {
                background-color: #f0f0f0;
                border-radius: 4px;
            }
            /* 年月选择的下拉菜单 */
            QToolButton::menu-indicator { 
                image: none; 
            }
            /* 日期格子 */
            QCalendarWidget QAbstractItemView:enabled {
                color: #333;
                background-color: white;
                selection-background-color: __THEME_PRIMARY__;
                selection-color: white;
                border: none;
                outline: 0;
            }
            /* 星期标题 (周一、周二...) */
            QCalendarWidget QTableHeaderView::section {
                background-color: __WEEKDAY_BACKGROUND__;
                color: #999;
                padding: 4px;
                border: none;
                font-weight: bold;
            }
        """.replace(
            "__THEME_PRIMARY__",
            AppConfig.COLOR_GRADIENT_START,
        ).replace(
            "__WEEKDAY_BACKGROUND__",
            weekday_background,
        )
