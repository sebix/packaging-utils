# -*- coding: utf-8 -*-
"""
Common functions dealing with type conversions.
"""
import re
from typing import Union, Optional


SPLIT_PATTERN = re.compile(r'\.|-|~')
ANY_INT_PATTERN = re.compile('[0-9]')


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
        return super().__eq__(other)

    def __ge__(self, other):
        if isinstance(other, str):
            return str(self) >= other
        return super().__ge__(other)

    def __gt__(self, other):
        if isinstance(other, str):
            return str(self) > other
        return super().__gt__(other)

    def __le__(self, other):
        if isinstance(other, str):
            return str(self) <= other
        return super().__le__(other)

    def __lt__(self, other):
        if isinstance(other, str):
            return str(self) < other
        return super().__lt__(other)

    def __ne__(self, other):
        if isinstance(other, str):
            return str(self) != other
        return super().__ne__(other)


class Version(tuple):

    original_value: str = ''

    def __new__(cls, value=Optional[str]):
        """
        Returns a tuple of integers and strings of a given string version.

        Non-numeric prefixes are removed.
        """
        if isinstance(value, str):
            value = re.sub('^[a-z]*-?', '', value)
        original_value = value
        if isinstance(value, str):
            value = tuple(int_safe(subval) for subval in SPLIT_PATTERN.split(value))

        if not ANY_INT_PATTERN.search(str(value)):
            return None

        new_class = super().__new__(Version, value)
        new_class.original_value = original_value

        return new_class

    def __str__(self) -> str:
        return self.original_value

    def __repr__(self) -> str:
        retval = super().__repr__()
        return '%s <%r>)' % (retval[:-1], self.original_value)
