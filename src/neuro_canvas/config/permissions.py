from .load import config, default_config

permissions = config.get("permissions")
if permissions is None:
    permissions = default_config["permissions"]

def check_permission(permission: str) -> bool:
    """
    Checks if the given permission is allowed based on the nested structure of the permissions object.
    Supports dot-separated keys for nested properties (e.g., "draw.line").
    Returns False in all circumstances except when the permission is explicitly set to True.
    """
    keys = permission.split(".")  # Split the permission string into keys
    current = permissions

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return False  # Key not found or invalid structure

    return current is True