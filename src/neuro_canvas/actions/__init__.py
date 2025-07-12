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
    if check_permission(action_class.permission) == True:
        all_actions.append(action_class())

# todo:
# - Make this check for the respective permission within config.json
# - Get each action class to have a new property that just returns the permission it's attached to. (this ideally will be the exact key value it needs to look at)