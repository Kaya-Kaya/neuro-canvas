"""Application - Application runner for Neuro's Canvas."""

import pygame

import os
import sys
import traceback
import logging
from typing import Final

import trio
from libcomponent.component import Event, ExternalRaiseManager

from neuro_api.event import NeuroAPIComponent

from .actions import all_actions
from .canvas import Canvas
from .constants import *

# For compatibility with Python versions below 3.11, use the backported ExceptionGroup
if sys.version_info < (3, 11):
    from exceptiongroup import ExceptionGroup

WEBSOCKET_ENV_VAR: Final = "NEURO_SDK_WS_URL"
DEFAULT_WEBSOCKET: Final = "ws://localhost:8000"
WEBSOCKET_CONNECTION_WAIT_TIME: Final = 0.1

STARTUP_MESSAGE: Final = "This is a painting app, feel free to draw anything you want!"
CONNECTION_FAILURE_MSG: Final = "Neuro API connection failed"
SHUTDOWN_MSG: Final = "Shutting down..."
CLEANUP_MSG: Final = "Cleanup complete"

logger = logging.getLogger(__name__)

async def run() -> None:
    """
    Main asynchronous function to run the app.
    """
    websocket_url = os.environ.get(WEBSOCKET_ENV_VAR, DEFAULT_WEBSOCKET)

    async with trio.open_nursery(strict_exception_groups=True) as nursery:
        manager = ExternalRaiseManager(APP_NAME, nursery)
        neuro_component = NeuroAPIComponent("neuro_api", APP_NAME)

        try:
            manager.add_component(neuro_component)

            neuro_component.register_handler(
                "connect",
                neuro_component.handle_connect,
            )

            await manager.raise_event(Event("connect", websocket_url))
            await trio.sleep(WEBSOCKET_CONNECTION_WAIT_TIME)

            if neuro_component.not_connected:
                logger.error(CONNECTION_FAILURE_MSG)
                return
            
            await neuro_component.send_startup_command()

            await neuro_component.send_context(STARTUP_MESSAGE)

            Canvas() # Initialize canvas to have it appear on start-up

            await neuro_component.register_neuro_actions([(action.get_action(), action.get_handler()) for action in all_actions])

            running = True
  
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                await trio.sleep(0)  # Yield control to the event loop
            
        except (KeyboardInterrupt, trio.Cancelled):
            logger.info(SHUTDOWN_MSG)
            return
        finally:
            await neuro_component.stop()
            pygame.quit()
            logger.info(CLEANUP_MSG)

def start() -> None:
    try:
        trio.run(run)
    except ExceptionGroup as exc:
        traceback.print_exception(exc)