from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer


def load_colored_svg_pixmap(icon_path, color_hex, width, height, device_pixel_ratio=1.0):
    """Render an SVG path to a colored QPixmap with optional DPR scaling."""
    renderer = QSvgRenderer(icon_path)
    if not renderer.isValid():
        return QPixmap()

    pixel_width = int(width * device_pixel_ratio)
    pixel_height = int(height * device_pixel_ratio)
    pixmap = QPixmap(pixel_width, pixel_height)
    pixmap.fill(Qt.GlobalColor.transparent)
    pixmap.setDevicePixelRatio(device_pixel_ratio)

    painter = QPainter(pixmap)
    renderer.render(painter, QRectF(0, 0, width, height))
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(QRectF(0, 0, width, height), QColor(color_hex))
    painter.end()
    return pixmap
