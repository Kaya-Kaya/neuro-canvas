from .load import config, default_config
from typing import Any

settings = config.get("settings")
if settings == None:
    settings = default_config["settings"]

def get_setting(setting: str) -> (type[ValueError] | Any):
    req_set = settings.get(setting)
    if req_set is None:
        return ValueError
    else:
        return req_set