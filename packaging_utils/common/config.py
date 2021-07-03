"""
Common methods to deal with configs
"""
import configparser
import os.path
from typing import Optional

CONFIG_FILE = os.path.expanduser("~/.config/packaging_utils.ini")


def read_config(section: str) -> Optional[str]:
    """
    Returns content of configuration file or None if it does not exist.
    """
    if not os.path.exists(CONFIG_FILE):
        return

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if section:
        return config[section]
    else:
        return config


def get_librariesio_api_key() -> Optional[str]:
    """
    Returns the libraries.io API key
    """
    return read_config('libraries.io')['api_key']
