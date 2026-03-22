# src/utils/styles.py
from ..config import AppConfig

class StyleManager:
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
        import os
        base_path = os.getcwd().replace('\\', '/')
        # 计算 check.svg 的绝对路径
        icon_path = f"{base_path}/assets/icons/check.svg" 
        bg_color = "rgba(255, 255, 255, 0.95)"
        text_color = "#333333"
        border_color = "rgba(0, 0, 0, 0.1)"
        hover_bg = "rgba(12, 192, 223, 0.1)"
        hover_text = "#0cc0df"

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
                border: 1px solid #0cc0df;
                
                /* ✨ 圆角和内边距 */
                border-radius: 2px;
                padding: 1px 3px;
                
                /* 字体设置 */
                font-family: "Microsoft YaHei UI";
                font-size: 12px;
            }
        """
    
    @staticmethod
    def get_calendar_style():
        """QCalendarWidget 深度美化"""
        return """
            QCalendarWidget QWidget { 
                alternate-background-color: #e3fcf9; 
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
                selection-background-color: #0cc0df; /* 选中青色 */
                selection-color: white;
                border: none;
                outline: 0;
            }
            /* 星期标题 (周一、周二...) */
            QCalendarWidget QTableHeaderView::section {
                background-color: white;
                color: #999;
                padding: 4px;
                border: none;
                font-weight: bold;
            }
        """