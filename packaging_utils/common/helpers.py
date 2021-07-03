"""
Detect software name from directory
"""

import os

from pathlib import Path


def detect_softwarename() -> str:
    dirname = Path(os.getcwd()).parts[-1]
    if dirname.startswith('python-'):
        dirname = dirname[7:]
    return dirname
