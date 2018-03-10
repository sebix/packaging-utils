# -*- coding: utf-8 -*-
"""
Common functions dealing with type conversions.
"""
import re
from typing import Union
import traceback


def int_safe(value: str) -> Union[str, int]:
    """
    Returns int of string if possible, otherwise the original variable.
    """
    try:
        return int(value)
    except ValueError:
        return value


class Version(tuple):
    def __new__(self, value=None):
        """
        Returns a tuple of integers and strings of a given string version.
        
        Non-numeric prefixes are removed.
        """
        try:
            value = re.sub('^[a-z]*-?', '', value)
        except Exception as exc:
            traceback.print_exc()
            print(value)
        self.original_value = value
        if isinstance(value, str):
             value = tuple(int_safe(subval) for subval in value.split('.~'))
        return super(Version, self).__new__(Version, value)

    def __str__(self) -> str:
        return self.original_value