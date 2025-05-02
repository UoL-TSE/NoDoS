import json
from typing import Any


class Config:
    """
    Load config from JSON file for now

    SECURITY WARNING: Any field (non-method) defined here will be modifiable through the config file
    This means that a potential attacker may be able to modify these fields by modifying the configuration
    This file will be replaced by a database entry but for now be careful adding sensitive fields here
    """
    def __init__(self):
        # Take this object as a dictionary and load each field from its corresponding entry in config.json
        config_dict: dict[str, Any] = json.loads(open("config.json").read())

        for field in config_dict.keys():
            setattr(self, field, config_dict.get(field))

    host: str = ""
    port: int = 0
    real_host: str = ""
    real_port: int = 0
    max_bytes_per_request: int = 0
    max_bytes_per_response: int = 0
    max_requests_per_second: float = 0.0


config: Config = Config()
