from .load import config
from typing import Any

settings = config["settings"]

def get_setting(setting: str) -> (type[ValueError] | Any):
    req_set = settings.get(setting)
    if req_set is None:
        return ValueError
    else:
        return req_set