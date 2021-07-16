"""
Detect software name from directory
"""

import os

from pathlib import Path

PACKAGE_PREFIXES = \
    {
        'python-': 'python',
        'python3-': 'python',
    }


def detect_softwarename() -> str:
    dirname = Path(os.getcwd()).parts[-1]
    for prefix in PACKAGE_PREFIXES.keys():
        if dirname.startswith(prefix):
            dirname = dirname[len(prefix):]
            break
    return dirname
