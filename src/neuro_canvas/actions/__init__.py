"""Actions - Actions to let Neuro interact with the canvas."""

import importlib
import pkgutil
from pathlib import Path
from ..config.permissions import check_permission

from ._abc import AbstractAction

all_actions = []

for module in pkgutil.iter_modules([Path(__file__).parent]):
    if not module.name.startswith("_"):
        importlib.import_module(f".{module.name}", package=__name__)

for action_class in AbstractAction.__subclasses__():
    try:
        # Instantiate the action class
        action_instance = action_class()

        # Check permission using the property method
        if check_permission(action_instance.permission):
            all_actions.append(action_instance)
    except AttributeError as e:
        raise RuntimeError(f"An error happened during runtime: {e}")
