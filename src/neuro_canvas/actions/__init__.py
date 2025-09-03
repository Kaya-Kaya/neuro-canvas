"""Actions - Actions to let Neuro interact with the canvas."""

import importlib
import pkgutil
from pathlib import Path

from ._abc import AbstractAction

for module in pkgutil.iter_modules([Path(__file__).parent]):
    if not module.name.startswith("_"):
        importlib.import_module(f".{module.name}", package=__name__)

all_actions = [action_class() for action_class in AbstractAction.__subclasses__()]
