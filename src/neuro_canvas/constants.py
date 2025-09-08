"""Constants - Neuro's Canvas global constants."""

from typing import Final
from pygame import Color

APP_NAME: Final = "Neuro's Canvas"

SCREEN_WIDTH: Final = 500
SCREEN_HEIGHT: Final = 500

COLOR_MAX_VAL: Final = 255

COLORS: Final[dict[str, Color]] = {
    "black": Color(0, 0, 0),
    "white": Color(255, 255, 255),
    "red": Color(255, 0, 0),
    "green": Color(0, 255, 0),
    "blue": Color(0, 0, 255),
    "pink": Color(255, 0, 255),
    "cyan": Color(0, 255, 255),
    "yellow": Color(255, 255, 0),
    "purple": Color(155, 0, 255),
    "brown": Color(102, 51, 0),
    "orange": Color(255, 165, 0)
}

ERROR_SUFFIX: Final = "\nSomeone tell the maintainers at https://github.com/Kaya-Kaya/neuro-canvas that there's an issue with their app!"
