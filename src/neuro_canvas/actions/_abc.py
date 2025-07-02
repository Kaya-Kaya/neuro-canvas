import sys

if sys.version_info >= (3, 12):
    from typing import override
else:
    # For compatibility with Python versions below 3.12, use the backported override
    from typing_extensions import override

from typing import Optional, Any, Final
from collections.abc import Callable, Coroutine
from abc import ABC, abstractmethod

from neuro_api.command import Action
from neuro_api.api import NeuroAction

import json
from jsonschema import validate, ValidationError

from ..constants import *

import logging

BEZIER_STEPS: Final = 4

logger = logging.getLogger(__name__)

def handle_json(
    action_function: Callable[[Optional[dict]], Coroutine[Any, Any, tuple[bool, Optional[str]]]],
    schema: dict[str, object]
) -> Callable[[NeuroAction], Coroutine[Any, Any, tuple[bool, Optional[str]]]]:
    """
    Decorator that parses JSON data from the NeuroAction, validates it against the action's schema,
    and calls the specified action function.

    It handles JSON decoding errors and unexpected exceptions, returning appropriate error messages.
    """
    async def wrapper(action: NeuroAction) -> tuple[bool, Optional[str]]:
        try:
            if action.data is None:
                data = None
            else:
                data = json.loads(action.data)

            validate(data, schema)

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
    def schema(self) -> dict[str, object]:
        pass

    def get_action(self) -> Action:
        """
        Returns an Action object containing the name, description, and schema of the action.
        """
        return Action(self.name, self.desc, self.schema)

    def get_handler(self) -> Callable[[NeuroAction], Coroutine[Any, Any, tuple[bool, Optional[str]]]]:
        return handle_json(self.perform_action, self.schema)

    @abstractmethod
    async def perform_action(self, data: Optional[dict]) -> tuple[bool, Optional[str]]:
        """
        Carries out the action.
        """
        pass
