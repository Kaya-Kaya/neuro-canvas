from typing import Optional

from ..canvas import Canvas
from ..constants import *
from ._abc import AbstractAction, override

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
    
    @property
    @override
    def permission(self) -> str:
        return "layers"

    @override
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        assert data, "'data' was expected but was set to None"

        color = COLORS[data["color"]]
        assert data["color"] in COLORS

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
                        }
                    }
                },
            }
        }
    
    @property
    @override
    def permission(self) -> str:
        return "layers"

    @override
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        assert data, "'data' was expected but was set to None"

        r = data["color"]["r"]
        g = data["color"]["g"]
        b = data["color"]["b"]
        color = Color(r, g, b)

        Canvas().set_background(color)

        return True, f"Set background color to {color}"