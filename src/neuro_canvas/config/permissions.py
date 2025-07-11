from .load import config, default_config
from typing import Literal

PermissionTypes = Literal[
    "layers",
    "misc",
    "shapes",
    "colour"
]

permissions = config.get("permissions")
if permissions is None:
    permissions = default_config["settings"]

def check_permission(permission: PermissionTypes) -> bool:
    req_perm = permissions.get(permission)
    if req_perm == True:
        return True
    else:
        return False