#!/usr/bin/python3
"""
Rewrites specfiles to fix the %licsens
"""
import argparse
import sys

from pathlib import Path
from subprocess import run

from ..common.helpers import detect_softwarename
from .helpers import detect_specfile, get_source_filename, get_current_version, VERSION_MATCH
from ..librariesio.get_latest_version import get_latest_version


def version_updater(softwareversion: str):
    """
    Updates the specfile, removes the old tarball, adds the new one
    """
    specfilename = detect_specfile()
    current_version = get_current_version(specfilename)
    if current_version == softwareversion:
        print(f'No version change (specfile has {current_version}, latest/given is {softwareversion}). Nothing to do.')
        return 2

    source_names = get_source_filename(specfilename, current_version)
    if not source_names:
        print('No source names detected in specfile.')
        return 2
    for source_name in source_names:
        print(f'deleting old source {source_name}')
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
    parser.add_argument('-n', '--softwarename', nargs='?', default=detect_softwarename())
    parser.add_argument('-V', '--softwareversion', nargs='?')
    args = parser.parse_args()
    # only query from libraries.io if necessary
    if args.softwareversion:
        softwareversion = args.softwareversion
    else:
        softwareversion = get_latest_version(softwarename=args.softwarename)
    return version_updater(softwareversion)


if __name__ == '__main__':
    sys.exit(main())
