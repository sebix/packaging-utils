# -*- coding: utf-8 -*-
"""
Common functions to deal with zypper.
"""
import subprocess


def package_version(package_name: str) -> str:
    """
    Returns version of package as reported by `zypper info`.
    """
    result = subprocess.run(['zypper', 'info', package_name],
                            stdout=subprocess.PIPE)
    for line in result.stdout.splitlines():
        if line.startswith(b'Version'):
            version = line[line.find(b':')+2:line.find(b'-')].decode().split('.')
            break
    if not version:
        return None
    return version
