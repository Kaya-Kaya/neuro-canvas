from pathlib import Path
import json
from jsonschema import validate, ValidationError, SchemaError
from ..constants import error_suffix

config_path = Path.cwd() / 'config.json'
# Schema is part of the app - get path relative to this file
schema_path = Path(__file__).parent / '..' / 'schema/config.schema.json'
# Supported config versions
supported_config_versions = [1]

default_config: object = {
    "configVersion": 1,
    "settings": {
        'allowed_save_file_formats': ['png', 'jpg'],
        'canvas_size': {
            'height': 1920, # Allowed integer values: 0 -> screen height?
            'width': 1080, # Allow integer values: 0 -> screen width?
            # Setting a value to 0 will prompt Neuro to input her decision
        },
    },
    "permissions": {}
}

# Don't initialize config - let it be undefined until explicitly set
config = None

try:
    # Load the config file
    with open(config_path, 'r') as f:
        loaded_config = json.load(f)
    
    # Load the schema file
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    # Validate config against schema
    validate(loaded_config, schema)

    # Validate config version
    if loaded_config.configVersion not in supported_config_versions:
        raise KeyError("Config version not supported!")
    
    # Only assign if validation passes
    config = loaded_config
    
except FileNotFoundError as e:
    if "config.json" in str(e):
        print(f"Config file not found: {config_path}\nProceeding with default configs...")
        config = default_config
    else:
        raise RuntimeError(f"Schema file not found: {schema_path}" + error_suffix)
        
except ValidationError as e:
    raise ValueError(f"Config validation failed! {e.message}\nDouble-check your config file!")

except SchemaError as e:
    raise RuntimeError(f"Validation schema for config file has an issue! {e.message}" + error_suffix)
    
except Exception as e:
    raise RuntimeError(f"An exception occurred while loading config.json! ({e})")

# Final safety check
if config is None:
    raise RuntimeError("CRITICAL: No configuration was loaded. Application cannot start safely.")
