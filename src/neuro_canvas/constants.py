"""Constants - Neuro's Canvas global constants."""

from typing import Final

import pygame

APP_NAME: Final = "Neuro's Canvas"

SCREEN_WIDTH: Final = 500
SCREEN_HEIGHT: Final = 500

COLOR_MAX_VAL: Final = 255

colors: Final[dict[str, pygame.Color]] = {
    "black": pygame.Color(0, 0, 0),
    "white": pygame.Color(255, 255, 255),
    "red": pygame.Color(255, 0, 0),
    "green": pygame.Color(0, 255, 0),
    "blue": pygame.Color(0, 0, 255),
    "pink": pygame.Color(255, 0, 255),
    "cyan": pygame.Color(0, 255, 255),
    "yellow": pygame.Color(255, 255, 0),
    "purple": pygame.Color(155, 0, 255),
    "brown": pygame.Color(102, 51, 0),
    "orange": pygame.Color(255, 165, 0)
}