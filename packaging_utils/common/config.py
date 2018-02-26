"""
Common methods to deal with configs
"""
import os.path
from typing import Optional

CONFIG_DIR = os.path.expanduser("~/.config/packaging_utils/")

def read_config(config_name: str) -> Optional[str]:
    """
    Returns content of configuration file or None if it does not exist.
    """
    config_path = os.path.join(CONFIG_DIR, '%s.conf' % config_name)
    if os.path.exists(config_path):
        with open(config_path, 'rt') as config_handle:
            config = config_handle.read()
        return config
    return None
