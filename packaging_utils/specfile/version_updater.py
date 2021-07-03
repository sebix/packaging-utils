#!/usr/bin/python3
"""
Rewrites specfiles to fix the %licsens
"""
import argparse
import re
import sys

from pathlib import Path
from subprocess import run

from ..common.helpers import detect_softwarename
from .helpers import detect_specfile, get_source_filename
from ..librariesio.get_latest_version import get_latest_version

VERSION_MATCH = re.compile(r'^(Version:\s+)(.*?)$', flags=re.MULTILINE)


def version_updater(softwarename: str, softwareversion: str):
    """
    Updates the specfile, removes the old tarball, adds the new one
    """
    specfilename = detect_specfile()
    source_name = get_source_filename(specfilename)
    Path(source_name).unlink()
    with open(specfilename, 'r+') as specfile:
        newfile = VERSION_MATCH.sub(r'\g<1>%s' % softwareversion, specfile.read())
        specfile.seek(0)
        specfile.truncate()
        specfile.write(newfile)

    run(('osc', 'service', 'runall', 'download_files')).check_returncode()
    run(('osc', 'addremove')).check_returncode()


def main():
    """
    Main program.
    """
    parser = argparse.ArgumentParser(description='Updates the specfile, removes the old tarball, adds the new one.')
    parser.add_argument('softwarename', nargs='?', default=detect_softwarename())
    parser.add_argument('softwareversion', nargs='?')
    args = parser.parse_args()
    # only query from libraries.io if necessary
    if args.softwareversion:
        softwareversion = args.softwareversion
    else:
        softwareversion = get_latest_version(softwarename=args.softwarename)
    return version_updater(args.softwarename, softwareversion)


if __name__ == '__main__':
    sys.exit(main())
