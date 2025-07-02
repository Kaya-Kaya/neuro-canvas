from typing import Optional

import pygame

from ..canvas import Canvas
from ..constants import *
from ._abc import AbstractAction, override

class BucketFillAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "bucket_fill"

    @property
    @override
    def desc(self) -> str:
        return (
            "Fills the empty area connected to the point you selected with the currently loaded colour."
        )

    @property
    @override
    def schema(self) -> dict[str, object]:
        return {
            "type": "object",
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
            },
            "required": ["x", "y"]
        }

    @override
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        assert data, "'data' was expected but was set to None"
        x = data["x"]
        y = data["y"]
        Canvas().bucket_fill((x, y))
        return True, f"Bucket filled at {(x, y)}"

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
    def schema(self) -> dict[str, object]:
        return {}

    @override
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        if Canvas().undo():
            return True, f"Performed undo"
        else:
            return False, "There is nothing to undo"

class ExportAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "export"

    @property
    @override
    def desc(self) -> str:
        return "Saves your drawing as a PNG. Do not include a .png extension when using this action."

    @property
    @override
    def schema(self) -> dict[str, object]:
        return {
            "type": "object",
            "properties": { "filename": { "type": "string" } },
            "required": ["filename"]
        }

    @override
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        assert data, "'data' was expected but was set to None"
        filename = data["filename"]

        try:
            Canvas().export(filename)
            return True, f"Drawing saved as {filename}.png"
        except pygame.error as e:
            return False, f"Saving failed. '{filename}' is likely not a valid filename. Error: {str(e)}"