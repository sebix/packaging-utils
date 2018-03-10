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
        return IntStr(value)
    except ValueError:
        return value


class IntStr(int):
    def __eq__(self, other):
        if isinstance(other, str):
            return str(self) == other
        return super(IntStr, self).__eq__(other)

    def __ge__(self, other):
        if isinstance(other, str):
            return str(self) >= other
        return super(IntStr, self).__ge__(other)

    def __gt__(self, other):
        if isinstance(other, str):
            return str(self) > other
        return super(IntStr, self).__gt__(other)

    def __le__(self, other):
        if isinstance(other, str):
            return str(self) <= other
        return super(IntStr, self).__le__(other)

    def __lt__(self, other):
        if isinstance(other, str):
            return str(self) < other
        return super(IntStr, self).__lt__(other)

    def __ne__(self, other):
        if isinstance(other, str):
            return str(self) != other
        return super(IntStr, self).__ne__(other)


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
            value = tuple(int_safe(subval) for subval in value.split('.'))
        new_class = super(Version, self).__new__(Version, value)
        new_class.original_value = original_value
        return new_class

    def __str__(self) -> str:
        return self.original_value

    def __repr__(self) -> str:
        retval = super(Version, self).__repr__()
        return '%s <%r>)' % (retval[:-1], self.original_value)
