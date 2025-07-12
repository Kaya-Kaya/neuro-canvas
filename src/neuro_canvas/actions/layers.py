from typing import Optional
from ..canvas import Canvas
from ._abc import AbstractAction, override

class AddLayerAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "add_layer"

    @property
    @override
    def desc(self) -> str:
        return "Adds a new layer with the specified name."

    @property
    @override
    def schema(self) -> dict[str, object]:
        return {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string"}
            }
        }
    
    @property
    @override
    def permission(self) -> str:
        return 'layers'

    @override
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        assert data is not None, "'data' was expected but was set to None"
        layer_name = data["name"]
        canvas = Canvas()
        if canvas.layer_exists(layer_name):
            return False, f"Layer '{layer_name}' already exists."
        canvas.add_layer(layer_name)
        return True, f"Added layer: {layer_name}"

class RemoveLayerAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "remove_layer"

    @property
    @override
    def desc(self) -> str:
        return "Removes the specified layer (except the base or background layers)."

    @property
    @override
    def schema(self) -> dict[str, object]:
        return {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string"}
            }
        }
    
    @property
    @override
    def permission(self) -> str:
        return 'layers'

    @override
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        assert data is not None, "'data' was expected but was set to None"
        layer_name = data["name"]
        canvas = Canvas()
        if not canvas.layer_exists(layer_name):
            return False, f"Layer '{layer_name}' does not exist."
        if layer_name in ["base", "background"]:
            return False, f"Cannot remove '{layer_name}' layer."
        canvas.remove_layer(layer_name)
        return True, f"Removed layer: {layer_name}"

class SetLayerVisibilityAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "set_layer_visibility"

    @property
    @override
    def desc(self) -> str:
        return "Sets the visibility of the specified layer using a value between 0 (invisible) and 1 (fully visible)."

    @property
    @override
    def schema(self) -> dict[str, object]:
        return {
            "type": "object",
            "required": ["name", "visibility"],
            "properties": {
                "name": {"type": "string"},
                "visibility": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                }
            }
        }
    
    @property
    @override
    def permission(self) -> str:
        return 'layers'

    @override
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        assert data is not None, "'data' was expected but was set to None"
        layer_name = data["name"]
        if layer_name == "background":
            return False, f"Can't change background layer visibility"
        visibility = data["visibility"]
        try:
            Canvas().set_layer_visibility(layer_name, visibility)
            return True, f"Set visibility of layer '{layer_name}' to {visibility}"
        except ValueError as e:
            return False, str(e)

class SwitchActiveLayerAction(AbstractAction):
    @property
    @override
    def name(self) -> str:
        return "switch_active_layer"

    @property
    @override
    def desc(self) -> str:
        return "Switches the active layer to the specified layer."

    @property
    @override
    def schema(self) -> dict[str, object]:
        return {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string"}
            }
        }
    
    @property
    @override
    def permission(self) -> str:
        return 'layers'

    @override
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        assert data is not None, "'data' was expected but was set to None"
        layer_name = data["name"]
        canvas = Canvas()
        if not canvas.layer_exists(layer_name):
            return False, f"Layer '{layer_name}' does not exist."
        if layer_name == "background":
            return False, f"Cannot switch to layer '{layer_name}'."
        canvas.switch_active_layer(layer_name)
        return True, f"Switched active layer to: {layer_name}"