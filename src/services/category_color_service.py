import colorsys
import random
import re


class CategoryColorService:
    """Assign distinct initial colors to newly created categories."""

    PALETTE = (
        "#0cc0df",
        "#ff6b6b",
        "#4d96ff",
        "#6bcb77",
        "#ffd93d",
        "#9b5de5",
        "#f15bb5",
        "#00bbf9",
        "#00f5d4",
        "#ff9f1c",
        "#845ec2",
        "#2ec4b6",
        "#e76f51",
        "#577590",
        "#90be6d",
        "#f94144",
    )
    _HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")
    _random = random.SystemRandom()

    @classmethod
    def normalize_color(cls, color):
        value = str(color or "").strip()
        if not cls._HEX_COLOR_PATTERN.fullmatch(value):
            return None
        return value.lower()

    @classmethod
    def choose_initial_color(cls, used_colors):
        used = {
            normalized
            for color in used_colors
            if (normalized := cls.normalize_color(color)) is not None
        }
        available = [color for color in cls.PALETTE if color not in used]
        if available:
            return cls._random.choice(available)

        for _attempt in range(256):
            hue = cls._random.random()
            saturation = cls._random.uniform(0.55, 0.82)
            value = cls._random.uniform(0.72, 0.95)
            red, green, blue = colorsys.hsv_to_rgb(hue, saturation, value)
            candidate = "#{:02x}{:02x}{:02x}".format(
                round(red * 255),
                round(green * 255),
                round(blue * 255),
            )
            if candidate not in used:
                return candidate

        while True:
            candidate = f"#{cls._random.randrange(0x1000000):06x}"
            if candidate not in used:
                return candidate
