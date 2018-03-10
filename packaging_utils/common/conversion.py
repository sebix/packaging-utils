# -*- coding: utf-8 -*-
"""
Common functions dealing with type conversions.
"""
import re
from typing import Union, Optional


def int_safe(value: str) -> Union[str, int]:
    """
    Returns int of string if possible, otherwise the original variable.
    """
    try:
        return int(value)
    except ValueError:
        return value


class Version(tuple):
    def __new__(self, value=Optional[str]):
        """
        Returns a tuple of integers and strings of a given string version.
        
        Non-numeric prefixes are removed.
        """
        if isinstance(value, str):
            value = re.sub('^[a-z]*-?', '', value)
        original_value = value
        if isinstance(value, str):
             value = tuple(int_safe(subval) for subval in value.split('.~'))
        new_class = super(Version, self).__new__(Version, value)
        new_class.original_value = original_value
        return new_class

    def __str__(self) -> str:
        return self.original_value