import pygame

import os
import sys
import traceback
import logging
from typing import Optional, Callable, Tuple, Any, Coroutine, Final, Dict, override
from abc import ABC, abstractmethod

import trio
from libcomponent.component import Event, ExternalRaiseManager

from neuro_api.command import Action
from neuro_api.event import NeuroAPIComponent
from neuro_api.api import NeuroAction

import json
from jsonschema import validate, ValidationError

# For compatibility with Python versions below 3.11, use the backported ExceptionGroup
if sys.version_info < (3, 11):
    from exceptiongroup import ExceptionGroup

WEBSOCKET_ENV_VAR = "NEURO_SDK_WS_URL"
WEBSOCKET_CONNECTION_WAIT_TIME = 0.05

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

colors: Final[Dict[str, pygame.Color]] = {
    "black": pygame.Color(0, 0, 0),
    "white": pygame.Color(255, 255, 255),
    "red": pygame.Color(255, 0, 0),
    "green": pygame.Color(0, 255, 0),
    "blue": pygame.Color(0, 0, 255)
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def update_display(fn: Callable) -> Callable:
    """
    Decorator to update the display after the function is called.
    """
    def wrapper(*args, **kwargs) -> Any:
        fn(*args, **kwargs)
        pygame.display.flip()

    return wrapper

class Canvas:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Canvas, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.brush_color = colors["black"]
        self.set_background(colors["white"])
        self.brush_width = 1

    @update_display
    def set_background(self, color: pygame.Color):
        self.screen.fill(color)

    def set_brush_color(self, color: pygame.Color):
        self.brush_color = color

    def set_brush_width(self, width: int):
        self.brush_width = width

    @update_display
    def draw_line(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float]) -> None:
        pygame.draw.line(self.screen, self.brush_color, start_pos, end_pos, self.brush_width)


def handle_action(
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
            data = json.loads(action.data)

            if schema is not None:
                validate(data, schema)

            return await action_function(data)
        except (json.JSONDecodeError, ValidationError) as e:
            return False, f"Invalid JSON: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    return wrapper


class NeuroActionWrapper(ABC):
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
        return handle_action(self.perform_action, self.schema)

    @abstractmethod
    async def perform_action(self, data: dict) -> Tuple[bool, Optional[str]]:
        """
        Carries out an action
        """
        pass
    

class DrawLineAction(NeuroActionWrapper):
    @property
    @override
    def name(self) -> str:
        return "draw_line"
    
    @property
    @override
    def desc(self) -> str:
        return (
            "Draws a straight line between two points. "
            f"All given x coords must be within 0-{SCREEN_WIDTH}, "
            f"and all given y coords must be within 0-{SCREEN_HEIGHT}."
        )

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
                            "type": "number",
                            "minimum": 0,
                            "maximum": SCREEN_WIDTH
                        },
                        "y": {
                            "type": "number",
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
                            "type": "number",
                            "minimum": 0,
                            "maximum": SCREEN_WIDTH
                        },
                        "y": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": SCREEN_HEIGHT
                        }
                    }
                }
            }
        }
    
    @override
    async def perform_action(self, data: dict) -> Tuple[bool, Optional[str]]:
        """
        Action to draw a straight line between two points on the canvas.
        """
        start = data["start"]["x"], data["start"]["y"]
        end = data["end"]["x"], data["end"]["y"]

        Canvas().draw_line(start, end)

        return True, f"Drew line from {start} to {end}"


async def run() -> None:
    """
    Main asynchronous function to run the app.
    """
    websocket_url = os.environ.get(WEBSOCKET_ENV_VAR, "ws://localhost:8000")

    async with trio.open_nursery(strict_exception_groups=True) as nursery:
        manager = ExternalRaiseManager("name", nursery)
        neuro_component = NeuroAPIComponent("neuro_api", "Paint")

        try:
            manager.add_component(neuro_component)

            neuro_component.register_handler(
                "connect",
                neuro_component.handle_connect,
            )

            # Attempt to connect to the Neuro API
            await manager.raise_event(Event("connect", websocket_url))
            await trio.sleep(WEBSOCKET_CONNECTION_WAIT_TIME)

            if neuro_component.not_connected:
                logger.error("Neuro API connection failed")
                return
            
            await neuro_component.send_startup_command()

            Canvas() # Initialize canvas to have it appear on start-up

            actions = [DrawLineAction()]

            await neuro_component.register_neuro_actions([(action.get_action(), action.get_handler()) for action in actions])

            running = True
  
            while running: 
                for event in pygame.event.get(): 
                    if event.type == pygame.QUIT: 
                        running = False
            
        except (KeyboardInterrupt, trio.Cancelled):
            logger.info("Shutting down...")
            return
        finally:
            await neuro_component.stop()
            logger.info("Cleanup complete")


if __name__ == "__main__":
    try:
        trio.run(run)
    except ExceptionGroup as exc:
        traceback.print_exception(exc)