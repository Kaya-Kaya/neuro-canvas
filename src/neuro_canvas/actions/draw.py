from typing import Optional, Final

from ..canvas import Canvas
from ..constants import SCREEN_WIDTH, SCREEN_HEIGHT, BEZIER_STEPS
from ._abc import AbstractAction, override


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
    def schema(self) -> dict[str, object]:
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
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        assert data, "'data' was expected but was set to None"

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
    def schema(self) -> dict[str, object]:
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
                "closed": {"type": "boolean"}
            }
        }

    @override
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        assert data, "'data' was expected but was set to None"

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
    def schema(self) -> dict[str, object]:
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
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        assert data, "'data' was expected but was set to None"

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
    def schema(self) -> dict[str, object]:
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
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        assert data, "'data' was expected but was set to None"

        center = data["center"]["x"], data["center"]["y"]
        radius = data["radius"]

        Canvas().draw_circle(center, radius)

        return True, f"Drew line at {center} with {radius = }"  # noqa: E202


class DrawTriangleAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "draw_triangle"

    @property
    @override
    def desc(self) -> str:
        return (
            "Draw an equilateral triangle. "
            "Use \"center\" to set the triangle's center. "
            "Use \"side_length\" to set the size of the triangle. "
            "Use \"rotation\" to rotate the triangle."
        )

    @property
    @override
    def schema(self) -> dict[str, object]:
        return {
            "type": "object",
            "required": ["center", "side_length", "rotation"],
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
                "side_length": {
                    "type": "integer",
                    "exclusiveMinimum": 0,
                    "maximum": max(SCREEN_HEIGHT, SCREEN_WIDTH)
                },
                "rotation": {
                    "type": "number",
                    "minimum": 0,
                    "exclusiveMaximum": 120
                }
            }
        }

    @override
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        assert data, "'data' was expected but was set to None"

        center = (data["center"]["x"], data["center"]["y"])
        side_length = data["side_length"]
        rotation = data["rotation"]

        Canvas().draw_triangle(center, side_length, rotation)

        return True, (f"Drew triangle with center {center}, with side length {side_length}, "
                      f"and rotated {rotation} degrees.")


class DrawRectangleAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "draw_rectangle"

    @property
    @override
    def desc(self) -> str:
        return (
            "Draws a rectangle at a given point. "
            "\"left\" refers to the x position of the left side of the rectangle, "
            "\"top\" refers to the y position of the top side of the rectangle, "
            "\"width\" refers to the width of the rectangle, "
            "and \"height\" refers to the height of the rectangle."
        )

    @property
    @override
    def schema(self) -> dict[str, object]:
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
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        assert data, "'data' was expected but was set to None"

        left_top = data["left"], data["top"]
        width_height = data["width"], data["height"]

        Canvas().draw_rectangle(left_top, width_height)

        return True, f"Drew rectangle at {left_top} with dimensions {width_height}"
