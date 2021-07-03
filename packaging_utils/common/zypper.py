# -*- coding: utf-8 -*-
"""
Common functions to deal with zypper.
"""
import subprocess
from typing import Optional

from .conversion import Version


def package_version(package_name: str) -> Optional[Version]:
    """
    Returns version of package as reported by `zypper info`.
    """
    result = subprocess.run(['zypper', 'info', package_name],
                            stdout=subprocess.PIPE)
    for line in result.stdout.splitlines():
        if line.startswith(b'Version'):
            return Version(line[line.find(b':') + 2:line.find(b'-')].decode())
