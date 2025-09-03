from typing import Optional

from pygame import Color

from ..canvas import Canvas
from ..constants import COLORS, COLOR_MAX_VAL
from ._abc import AbstractAction, override


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
    def schema(self) -> dict[str, object]:
        return {
            "type": "object",
            "required": ["color"],
            "properties": {
                "color": {
                    "type": "string",
                    "enum": list(COLORS.keys())
                },
            }
        }

    @override
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        assert data, "'data' was expected but was set to None"

        color = COLORS[data["color"]]
        assert data["color"] in COLORS, f"'{data["color"]}' is not in the COLORS dictionary"

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
    def schema(self) -> dict[str, object]:
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
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        assert data, "'data' was expected but was set to None"

        r = data["color"]["r"]
        g = data["color"]["g"]
        b = data["color"]["b"]
        a = data["color"].get("a", COLOR_MAX_VAL)
        color = Color(r, g, b, a)

        Canvas().set_brush_color(color)

        return True, f"Set brush color to {color}"
