"""Canvas - The canvas for Neuro to draw in."""

from pygame import gfxdraw, Rect
import math

from functools import partial

from typing import Callable, Tuple, Any, List

from .constants import *

Coordinate = Tuple[int, int]

class Canvas:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Canvas, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.actions: List[Callable] = []
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.set_brush_color(colors["black"])
        self.set_brush_width(1)
        self.clear_canvas()
        pygame.display.set_caption(APP_NAME) 
        self._initialized = True

    @staticmethod
    def record_action(fn: Callable) -> Callable:
        """
        Decorator to update the display after the function is called.
        """
        def wrapper(self, *args, **kwargs) -> Any:
            fn(self, *args, **kwargs)
            
            self.actions.append(partial(fn, self, *args, **kwargs))

        return wrapper
    
    @staticmethod
    def update_display(fn: Callable) -> Callable:
        """
        Decorator to update the display after the function is called.
        """
        def wrapper(self, *args, **kwargs) -> Any:
            fn(self, *args, **kwargs)

            pygame.display.update()

        return wrapper
    
    @update_display
    def undo(self) -> None:
        self.actions = self.actions[:-1]

        for action in self.actions:
            action()
    
    @update_display
    @record_action
    def clear_canvas(self) -> None:
        self.screen.fill(colors["white"])

    @update_display
    @record_action
    def set_background(self, color: pygame.Color) -> None:
        self.screen.fill(color)

        for action in self.actions:
            if action.func.__name__ != "set_background" and action.func.__name__ != "clear_canvas":
                action()

    @record_action
    def set_brush_color(self, color: pygame.Color) -> None:
        self.brush_color = color

    @record_action
    def set_brush_width(self, width: int) -> None:
        self.brush_width = width

    @update_display
    @record_action
    def draw_line(self, start_pos: Coordinate, end_pos: Coordinate) -> None:
        pygame.draw.aaline(self.screen, self.brush_color, start_pos, end_pos)

    @update_display
    @record_action
    def draw_lines(self, points: List[Coordinate], closed: bool) -> None:
        pygame.draw.aalines(self.screen, self.brush_color, closed, points)

    @update_display
    @record_action
    def draw_curve(self, points: List[Coordinate], steps: int) -> None:
        gfxdraw.bezier(self.screen, points, steps, self.brush_color)

    @update_display
    @record_action
    def draw_circle(self, center: Coordinate, radius: int) -> None:
        gfxdraw.aacircle(self.screen, center[0], center[1], radius, self.brush_color)

    @update_display
    @record_action
    def draw_rectangle(self, left_top: Coordinate, width_height: Coordinate) -> None:
        gfxdraw.rectangle(self.screen, Rect(left_top, width_height), self.brush_color)

    @update_display
    @record_action
    def draw_triangle(self, center: Coordinate, size: int, rotation: int | float) -> None:
        # Calculate the three vertices for an equilateral triangle
        # using angles -90°, 30°, and 150° so that one vertex is at the top.
        cx, cy = center
        # Base angles for an equilateral triangle (in radians)
        base_angles = [math.radians(-90), math.radians(30), math.radians(150)]
        rotation_radians = math.radians(rotation)
        # Add the rotation offset to each base angle
        rotated_angles = [angle + rotation_radians for angle in base_angles]
        vertices = [
            (int(cx + size * math.cos(angle)), int(cy + size * math.sin(angle)))
            for angle in rotated_angles
        ]
        # Draw lines between the vertices to form the triangle.
        pygame.draw.aalines(self.screen, self.brush_color, True, vertices)
