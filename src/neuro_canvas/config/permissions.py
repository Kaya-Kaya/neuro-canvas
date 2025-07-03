from .load import config
from typing import Literal

PermissionTypes = Literal[
    "layers",
    "misc",
    "shapes",
    "colour"
]

permissions = config.get("permissions")

def check_permission(permission: PermissionTypes) -> bool:
    req_perm = permissions.get(permission)
    if req_perm == True:
        return True
    else:
        return False