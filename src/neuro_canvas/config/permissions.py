from .load import config, default_config

permissions = config.get("permissions")
if permissions is None:
    permissions = default_config["settings"]

def check_permission(permission: str) -> bool:
    req_perm = permissions.get(permission)
    if req_perm == True:
        return True
    else:
        return False