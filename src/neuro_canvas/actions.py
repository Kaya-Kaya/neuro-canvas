"""Actions - Actions to let Neuro interact with the canvas."""

from typing import Optional, Callable, Tuple, Any, Coroutine, Dict, override, Final
from abc import ABC, abstractmethod

from neuro_api.command import Action
from neuro_api.api import NeuroAction

import json
from jsonschema import validate, ValidationError

from .constants import *
from .canvas import Canvas

import logging

BEZIER_STEPS: Final = 4

logger = logging.getLogger(__name__)

def handle_json(
    action_function: Callable[[Dict], Coroutine[Any, Any, Tuple[bool, Optional[str]]]],
    schema: Optional[Dict[str, object]]
) -> Callable[[NeuroAction], Coroutine[Any, Any, Tuple[bool, Optional[str]]]]:
    """
    Decorator that parses JSON data from the NeuroAction, validates it against the action's schema,
    and calls the specified action function.
    
    It handles JSON decoding errors and unexpected exceptions, returning appropriate error messages.
    """
    async def wrapper(action: NeuroAction) -> Tuple[bool, Optional[str]]:
        try:
            if schema is not None:
                data = json.loads(action.data)
            
                validate(data, schema)
            else:
                data = None

            logger.info(f"Executing action {action.name} with args {data}")
            return await action_function(data)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning(f"Received invalid JSON: {str(e)}")
            return False, f"Invalid JSON: {str(e)}"
        except Exception as e:
            logger.warning(f"Unexpected error: {str(e)}")
            return False, f"Unexpected error: {str(e)}"
    return wrapper


class AbstractAction(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def desc(self) -> str:
        pass

    @property
    @abstractmethod
    def schema(self) -> Optional[Dict[str, object]]:
        return None

    def get_action(self) -> Action:
        """
        Returns an Action object containing the name, description, and schema of the action.
        """
        return Action(self.name, self.desc, self.schema)
    
    def get_handler(self) -> Callable[[NeuroAction], Coroutine[Any, Any, Tuple[bool, Optional[str]]]]:
        return handle_json(self.perform_action, self.schema)

    @abstractmethod
    async def perform_action(self, data: Optional[dict]) -> Tuple[bool, Optional[str]]:
        """
        Carries out the action.
        """
        pass
    

class DrawLineAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "draw_line"
    
    @property
    @override
    def desc(self) -> str:
        return "Draws a straight line between two points, \"start\" and \"end\"."

    @property
    @override
    def schema(self) -> Optional[Dict[str, object]]:
        return {
            "type": "object",
            "required": ["start", "end"],
            "properties": {
                "start": { 
                    "type": "object",
                    "required": ["x", "y"],
                    "properties": {
                        "x": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": SCREEN_WIDTH
                        },
                        "y": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": SCREEN_HEIGHT
                        }
                    }
                },
                "end": { 
                    "type": "object",
                    "required": ["x", "y"],
                    "properties": {
                        "x": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": SCREEN_WIDTH
                        },
                        "y": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": SCREEN_HEIGHT
                        }
                    }
                }
            }
        }
    
    @override
    async def perform_action(self, data: dict) -> Tuple[bool, Optional[str]]:
        start = data["start"]["x"], data["start"]["y"]
        end = data["end"]["x"], data["end"]["y"]

        Canvas().draw_line(start, end)

        return True, f"Drew line from {start} to {end}"

class DrawLinesAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "draw_lines"
    
    @property
    @override
    def desc(self) -> str:
        return (
            "Draws a sequence of straight lines through \"points\". "
            "If \"closed\" is true, draws a final line connecting the first and last lines."
        )

    @property
    @override
    def schema(self) -> Optional[Dict[str, object]]:
        return {
            "type": "object",
            "required": ["points", "closed"],
            "properties": {
                "points": { 
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["x", "y"],
                        "properties": {
                            "x": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": SCREEN_WIDTH
                            },
                            "y": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": SCREEN_HEIGHT
                            }
                        }
                    },
                    "minItems": 3
                },
                "closed": { "type": "boolean" }
            }
        }
    
    @override
    async def perform_action(self, data: dict) -> Tuple[bool, Optional[str]]:
        points = [(point["x"], point["y"]) for point in data["points"]]
        closed = data["closed"]

        Canvas().draw_lines(points, closed)

        return True, f"Drew a {"" if closed else "non-"}closed set of lines through {points}"

class DrawCurveAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "draw_curve"
    
    @property
    @override
    def desc(self) -> str:
        return "Draws a curve through \"points\"."

    @property
    @override
    def schema(self) -> Optional[Dict[str, object]]:
        return {
            "type": "object",
            "required": ["points"],
            "properties": {
                "points": { 
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["x", "y"],
                        "properties": {
                            "x": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": SCREEN_WIDTH
                            },
                            "y": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": SCREEN_HEIGHT
                            }
                        }
                    },
                    "minItems": 3
                }
            }
        }
    
    @override
    async def perform_action(self, data: dict) -> Tuple[bool, Optional[str]]:
        points = [(point["x"], point["y"]) for point in data["points"]]

        Canvas().draw_curve(points, BEZIER_STEPS)

        return True, f"Drew a curve through {points}"
    
class DrawCircleAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "draw_circle"
    
    @property
    @override
    def desc(self) -> str:
        return "Draws a circle at \"center\" with radius \"radius\"."

    @property
    @override
    def schema(self) -> Optional[Dict[str, object]]:
        return {
            "type": "object",
            "required": ["center", "radius"],
            "properties": {
                "center": { 
                    "type": "object",
                    "required": ["x", "y"],
                    "properties": {
                        "x": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": SCREEN_WIDTH
                        },
                        "y": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": SCREEN_HEIGHT
                        }
                    }
                },
                "radius": { 
                    "type": "integer",
                    "exclusiveMinimum": 0,
                    "maximum": max(SCREEN_HEIGHT, SCREEN_WIDTH)
                }
            }
        }
    
    @override
    async def perform_action(self, data: dict) -> Tuple[bool, Optional[str]]:
        center = data["center"]["x"], data["center"]["y"]
        radius = data["radius"]

        Canvas().draw_circle(center, radius)

        return True, f"Drew line at {center} with {radius = }"
    
class SetBrushColorAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "set_brush_color"
    
    @property
    @override
    def desc(self) -> str:
        return "Changes the brush to the specified color."

    @property
    @override
    def schema(self) -> Optional[Dict[str, object]]:
        return {
            "type": "object",
            "required": ["color"],
            "properties": {
                "color": { 
                    "type": "string",
                    "enum": list(colors.keys())
                },
            }
        }
    
    @override
    async def perform_action(self, data: dict) -> Tuple[bool, Optional[str]]:
        color = colors[data["color"]]
        assert data["color"] in colors

        Canvas().set_brush_color(color)

        return True, f"Set brush color to {color}"
    
class SetCustomBrushColorAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "set_custom_brush_color"
    
    @property
    @override
    def desc(self) -> str:
        return "Changes the brush to the specified rgb."

    @property
    @override
    def schema(self) -> Optional[Dict[str, object]]:
        return {
            "type": "object",
            "required": ["color"],
            "properties": {
                "color": { 
                    "type": "object",
                    "required": ["r", "g", "b"],
                    "properties": {
                        "r": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": COLOR_MAX_VAL
                        },
                        "g": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": COLOR_MAX_VAL
                        },
                        "b": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": COLOR_MAX_VAL
                        },
                        "a": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": COLOR_MAX_VAL
                        }
                    }
                },
            }
        }
    
    @override
    async def perform_action(self, data: dict) -> Tuple[bool, Optional[str]]:
        r = data["color"]["r"]
        g = data["color"]["g"]
        b = data["color"]["b"]
        a = data["color"].get("a", COLOR_MAX_VAL)
        color = pygame.Color(r, g, b, a)

        Canvas().set_brush_color(color)

        return True, f"Set brush color to {color}"
    
class SetBackgroundColorAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "set_background_color"
    
    @property
    @override
    def desc(self) -> str:
        return "Changes the background to the specified color."

    @property
    @override
    def schema(self) -> Optional[Dict[str, object]]:
        return {
            "type": "object",
            "required": ["color"],
            "properties": {
                "color": { 
                    "type": "string",
                    "enum": list(colors.keys())
                },
            }
        }
    
    @override
    async def perform_action(self, data: dict) -> Tuple[bool, Optional[str]]:
        color = colors[data["color"]]
        assert data["color"] in colors

        Canvas().set_background(color)

        return True, f"Set background color to {color}"
    
class SetCustomBackgroundColorAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "set_custom_background_color"
    
    @property
    @override
    def desc(self) -> str:
        return "Changes the background to the specified rgb."

    @property
    @override
    def schema(self) -> Optional[Dict[str, object]]:
        return {
            "type": "object",
            "required": ["color"],
            "properties": {
                "color": { 
                    "type": "object",
                    "required": ["r", "g", "b"],
                    "properties": {
                        "r": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": COLOR_MAX_VAL
                        },
                        "g": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": COLOR_MAX_VAL
                        },
                        "b": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": COLOR_MAX_VAL
                        }
                    }
                },
            }
        }
    
    @override
    async def perform_action(self, data: dict) -> Tuple[bool, Optional[str]]:
        r = data["color"]["r"]
        g = data["color"]["g"]
        b = data["color"]["b"]
        color = pygame.Color(r, g, b)

        Canvas().set_background(color)

        return True, f"Set background color to {color}"
    
class UndoAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "undo"
    
    @property
    @override
    def desc(self) -> str:
        return "Undoes the last change."

    @property
    @override
    def schema(self) -> Optional[Dict[str, object]]:
        return None
    
    @override
    async def perform_action(self, data: dict) -> Tuple[bool, Optional[str]]:
        Canvas().undo()

        return True, f"Performed undo"
    
class DrawRectangleAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "draw_rectangle"
    
    @property
    @override
    def desc(self) -> str:
        return (
            "Draws a rectangle at a given point."
            "\"left\" refers to the x position of the left side of the rectangle, "
            "\"top\" refers to the y position of the top side of the rectangle, "
            "\"width\" refers to the width of the rectangle, "
            "and \"height\" refers to the height of the rectangle."
        )

    @property
    @override
    def schema(self) -> Optional[Dict[str, object]]:
        return {
            "type": "object",
            "required": ["left", "top", "width", "height"],
            "properties": {
                "left": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": SCREEN_WIDTH
                },
                "top": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": SCREEN_HEIGHT
                },
                "width": {
                   "type": "integer",
                    "minimum": 0,
                    "maximum": SCREEN_WIDTH
                },
                "height": {
                   "type": "integer",
                    "minimum": 0,
                    "maximum": SCREEN_WIDTH
                }, 
            }
        }
    
    @override
    async def perform_action(self, data: dict) -> Tuple[bool, Optional[str]]:
        left_top = data["left"], data["top"]
        width_height = data["width"], data["height"]

        Canvas().draw_rectangle(left_top, width_height)

        return True, f"Drew rectangle at {left_top} with dimensions {width_height}"

all_actions = [action_class() for action_class in AbstractAction.__subclasses__()]