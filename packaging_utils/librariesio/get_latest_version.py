#!/usr/bin/python3
"""
Retrieves the latest version from libraries.io
"""
import argparse
import sys

from ..common.config import get_librariesio_api_key
from ..common.helpers import detect_softwarename

import requests


def get_latest_version(softwarename: str):
    """
    Retrieves the lates version number from libraries.io
    """
    api_key = get_librariesio_api_key()
    response = requests.get(f'https://libraries.io/api/pypi/{softwarename}?api_key={api_key}')
    return response.json()['latest_release_number']


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
