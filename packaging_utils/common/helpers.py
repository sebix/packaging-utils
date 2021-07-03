"""
Detect software name from directory
"""

import os
import pathlib


def detect_softwarename() -> str:
    dirname = pathlib.Path(os.getcwd()).parts[-1]
    if dirname.startswith('python-'):
        dirname = dirname[7:]
    return dirname
