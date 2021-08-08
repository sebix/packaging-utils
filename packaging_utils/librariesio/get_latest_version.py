#!/usr/bin/python3
"""
Retrieves the latest version from libraries.io
"""
import argparse
import sys

import requests

from ..common.config import get_librariesio_api_key
from ..common.helpers import detect_softwarename


def get_latest_version(softwarename: str):
    """
    Retrieves the latest version number from libraries.io
    """
    api_key = get_librariesio_api_key()
    response = requests.get(f'https://libraries.io/api/pypi/{softwarename}?api_key={api_key}')
    try:
        return response.json()['latest_release_number']
    except KeyError as exc:
        raise ValueError(f'Unable to retrieve the latest version number for {softwarename}.') from exc


def main():
    """
    Main program.
    """
    parser = argparse.ArgumentParser(description='Retrieves the lates version number from libraries.io.')
    parser.add_argument('softwarename', nargs='?', default=detect_softwarename())
    args = parser.parse_args()
    return get_latest_version(args.softwarename)


if __name__ == '__main__':
    sys.exit(main())
