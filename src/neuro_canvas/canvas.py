"""Canvas - The canvas for Neuro to draw in."""

from pygame import gfxdraw, Rect
import pygame

import math

from functools import partial
from typing import Any
from collections.abc import Callable

from .constants import *

# New Layer class
class Layer:
    def __init__(self, name: str, width: int, height: int):
        self.name = name
        # Create a surface with per-pixel alpha so that layers can be transparent
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        # By default, a layer is visible
        self.visible = True

Coordinate = tuple[int, int]

class Canvas:
    class Attributes():
        def __init__(self):
            self.brush_color: pygame.Color = colors["black"]
            self.brush_width: int = 1
            self.active_layer: str = "base"
            self.layers: dict[str, Layer] = {}
            self.layers_order: list[str] = []

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Canvas, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return

        self._attributes = Canvas.Attributes()

        self._actions: list[partial] = []
        self._screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Create a dedicated "background" layer followed by a "base" layer for drawings.
        self.add_layer("background")
        self.add_layer("base")

        self.clear_canvas()

        # Add marker between setup and user actions
        marker = partial(lambda: None)
        marker.func.__name__ = "finish_setup"
        self._actions.append(marker)

        pygame.display.set_caption(APP_NAME)
        self._initialized = True

    def _get_active_surface(self) -> pygame.Surface:
        return self._attributes.layers[self._attributes.active_layer].surface

    def _composite_layers(self) -> None:
        # Clear the main screen to the default background
        self._screen.fill(colors["white"])
        for layer_name in self._attributes.layers_order:
            layer = self._attributes.layers[layer_name]
            if layer.visible:
                self._screen.blit(layer.surface, (0, 0))

    @staticmethod
    def action(update_display: bool = True, record: bool = True) -> Callable:
        """
        Decorator for Canvas methods that perform actions on the canvas.

        This decorator wraps methods to automatically handle display updates and action recording.
        It provides a consistent way to manage canvas state changes and maintain an action history
        for undo/redo functionality.

        Args:
            update_display (bool, optional): Whether to update the display after the action.
                Defaults to True. When True, composites all layers and updates the pygame display.
            record (bool, optional): Whether to record this action in the action history.
                Defaults to True. When True, stores the action as a partial function for replay.

        Returns:
            Callable: A decorator function that wraps the target method.
        """
        def inner(fn: Callable) -> Callable:
            if fn.__name__ == "finish_setup":
                raise ValueError("Cannot have an action named finish_setup, that name is reserved")

            def wrapper(self: 'Canvas', *args, **kwargs) -> Any:
                return_val = fn(self, *args, **kwargs)

                if record:
                    self._actions.append(partial(fn, self, *args, **kwargs))

                if update_display:
                    self._composite_layers()
                    pygame.display.update()

                return return_val

            return wrapper

        return inner

    @action(record=False)
    def undo(self) -> bool:
        if self._actions[-1].func.__name__ == "finish_setup":
            return False

        # Remove last action
        self._actions.pop()

        # Reset canvas attributes and re-perform actions
        self._attributes = Canvas.Attributes()
        for action in self._actions:
            action()

        return True

    @action()
    def clear_canvas(self) -> None:
        # Clear all layers
        for layer in self._attributes.layers.values():
            layer.surface.fill((0, 0, 0, 0))  # Clear to transparent
        # Fill the "background" layer with white by default.
        self._attributes.layers["background"].surface.fill(colors["white"])

    @action()
    def set_background(self, color: pygame.Color) -> None:
        # Set background only on the "background" layer.
        self._attributes.layers["background"].surface.fill(color)

    @action(update_display=False)
    def set_brush_color(self, color: pygame.Color) -> None:
        self._attributes.brush_color = color

    @action(update_display=False)
    def set_brush_width(self, width: int) -> None:
        self._attributes.brush_width = width

    @action()
    def draw_line(self, start_pos: Coordinate, end_pos: Coordinate) -> None:
        pygame.draw.line(self._get_active_surface(), self._attributes.brush_color, start_pos, end_pos)

    @action()
    def draw_lines(self, points: list[Coordinate], closed: bool) -> None:
        pygame.draw.lines(self._get_active_surface(), self._attributes.brush_color, closed, points)

    @action()
    def draw_curve(self, points: list[Coordinate], steps: int) -> None:
        gfxdraw.bezier(self._get_active_surface(), points, steps, self._attributes.brush_color)

    @action()
    def draw_circle(self, center: Coordinate, radius: int) -> None:
        gfxdraw.circle(self._get_active_surface(), center[0], center[1], radius, self._attributes.brush_color)

    @action()
    def draw_rectangle(self, left_top: Coordinate, width_height: Coordinate) -> None:
        gfxdraw.rectangle(self._get_active_surface(), Rect(left_top, width_height), self._attributes.brush_color)

    @action()
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
        pygame.draw.lines(self._get_active_surface(), self._attributes.brush_color, True, vertices)

    @action()
    def bucket_fill(self, point: Coordinate) -> None:
        target_color = self._get_active_surface().get_at(point)
        fill_color = self._attributes.brush_color
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

    @action(update_display=False)
    def add_layer(self, name: str) -> None:
        if name in self._attributes.layers:
            return
        new_layer = Layer(name, SCREEN_WIDTH, SCREEN_HEIGHT)
        self._attributes.layers[name] = new_layer
        self._attributes.layers_order.append(name)

    @action()
    def remove_layer(self, name: str) -> None:
        if name in self._attributes.layers and name != "base":
            del self._attributes.layers[name]
            self._attributes.layers_order.remove(name)
            # Reset active layer if needed.
            if self._attributes.active_layer == name:
                self._attributes.active_layer = "base"

    @action()
    def set_layer_visibility(self, name: str, visibility: float) -> None:
        """
        Sets the visibility of a layer using a value between 0 (invisible) and 1 (fully visible).
        """
        if not self.layer_exists(name):
            raise ValueError(f"Layer '{name}' does not exist.")

        layer = self._attributes.layers[name]
        layer.visible = visibility > 0  # Treat visibility > 0 as "visible"
        layer.surface.set_alpha(int(visibility * 255))  # Scale visibility to alpha (0-255)
        self._composite_layers()  # Re-composite layers to reflect the change

    @action(update_display=False)
    def switch_active_layer(self, name: str) -> None:
        if name in self._attributes.layers:
            self._attributes.active_layer = name

    def layer_exists(self, layer_name: str) -> bool:
        return layer_name in self._attributes.layers

    def export(self, filename: str) -> None:
        pygame.image.save(self._screen, f"{filename}.png")
