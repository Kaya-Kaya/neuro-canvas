"""Canvas - The canvas for Neuro to draw in."""

from pygame import gfxdraw, Rect
import math

from functools import partial

from typing import Callable, Tuple, Any, List, Dict

import pygame  # ensure pygame is imported at the top

from .constants import *

# New Layer class
class Layer:
    def __init__(self, name: str, width: int, height: int):
        self.name = name
        # Create a surface with per-pixel alpha so that layers can be transparent
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        # By default, a layer is visible
        self.visible = True

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
        # Layer support: dictionary of layers and a list for layer order.
        self.layers: Dict[str, Layer] = {}
        self.layers_order: List[str] = []
        # Create a dedicated "background" layer followed by a "base" layer for drawings.
        self.add_layer("background")
        self.add_layer("base")
        # Set the active layer to "base" so that drawing actions are applied there.
        self.active_layer = "base"

        self.set_brush_color(colors["black"])
        self.set_brush_width(1)
        self.clear_canvas()
        pygame.display.set_caption(APP_NAME)
        self._initialized = True

    def _get_active_surface(self) -> pygame.Surface:
        return self.layers[self.active_layer].surface

    def _composite_layers(self) -> None:
        # Clear the main screen to the default background
        self.screen.fill(colors["white"])
        for layer_name in self.layers_order:
            layer = self.layers[layer_name]
            if layer.visible:
                self.screen.blit(layer.surface, (0, 0))

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

            self._composite_layers()
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
        # Clear all layers
        for layer in self.layers.values():
            layer.surface.fill((0, 0, 0, 0))  # Clear to transparent
        # Fill the "background" layer with white by default.
        self.layers["background"].surface.fill(colors["white"])

    @update_display
    @record_action
    def set_background(self, color: pygame.Color) -> None:
        # Set background only on the "background" layer.
        self.layers["background"].surface.fill(color)

    @record_action
    def set_brush_color(self, color: pygame.Color) -> None:
        self.brush_color = color

    @record_action
    def set_brush_width(self, width: int) -> None:
        self.brush_width = width

    @update_display
    @record_action
    def draw_line(self, start_pos: Coordinate, end_pos: Coordinate) -> None:
        pygame.draw.line(self._get_active_surface(), self.brush_color, start_pos, end_pos)

    @update_display
    @record_action
    def draw_lines(self, points: List[Coordinate], closed: bool) -> None:
        pygame.draw.lines(self._get_active_surface(), self.brush_color, closed, points)

    @update_display
    @record_action
    def draw_curve(self, points: List[Coordinate], steps: int) -> None:
        gfxdraw.bezier(self._get_active_surface(), points, steps, self.brush_color)

    @update_display
    @record_action
    def draw_circle(self, center: Coordinate, radius: int) -> None:
        gfxdraw.circle(self._get_active_surface(), center[0], center[1], radius, self.brush_color)

    @update_display
    @record_action
    def draw_rectangle(self, left_top: Coordinate, width_height: Coordinate) -> None:
        gfxdraw.rectangle(self._get_active_surface(), Rect(left_top, width_height), self.brush_color)

    @update_display
    @record_action
    def draw_triangle(self, center: Coordinate, side_length: int, rotation: int | float) -> None:
        # Calculate circumradius from side length
        size = side_length / math.sqrt(3)
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
        pygame.draw.lines(self._get_active_surface(), self.brush_color, True, vertices)

    @update_display
    @record_action
    def bucket_fill(self, point: Coordinate) -> None:
        target_color = self._get_active_surface().get_at(point)
        fill_color = self.brush_color
        if target_color == fill_color:
            return
        stack = [point]
        width, height = self._get_active_surface().get_size()
        while stack:
            x, y = stack.pop()
            if x < 0 or x >= width or y < 0 or y >= height:
                continue
            if self._get_active_surface().get_at((x, y)) == target_color:
                self._get_active_surface().set_at((x, y), fill_color)
                stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
    
    @update_display
    def add_layer(self, name: str) -> None:
        if name in self.layers: 
            return
        new_layer = Layer(name, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.layers[name] = new_layer
        self.layers_order.append(name)

    @update_display
    def remove_layer(self, name: str) -> None:
        if name in self.layers and name != "base":
            del self.layers[name]
            self.layers_order.remove(name)
            # Reset active layer if needed.
            if self.active_layer == name:
                self.active_layer = "base"

    @update_display
    def set_layer_visibility(self, name: str, visibility: float) -> None:
        """
        Sets the visibility of a layer using a value between 0 (invisible) and 1 (fully visible).
        """
        if name not in self.layers:
            raise ValueError(f"Layer '{name}' does not exist.")
        
        layer = self.layers[name]
        layer.visible = visibility > 0  # Treat visibility > 0 as "visible"
        layer.surface.set_alpha(int(visibility * 255))  # Scale visibility to alpha (0-255)
        self._composite_layers()  # Re-composite layers to reflect the change

    def switch_active_layer(self, name: str) -> None:
        if name in self.layers:
            self.active_layer = name

    def export(self, filename: str) -> None:
        pygame.image.save(self.screen, f"{filename}.png")
