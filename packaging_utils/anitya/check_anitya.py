#!/usr/bin/python3
"""
Checks anitya (release-monitoring.org) for updates.
"""
import argparse
import re
import subprocess
import sys
from typing import Optional

import requests
import tabulate

from ..common import config

PROGRAMS = ['tcpflow', 'ddrescueview', 'html-xml-utils', 'fred', 'H2rename', 'chntpw']
ANITYA_SEARCH_URL = 'https://release-monitoring.org/projects/search/?pattern=%s'
ANITYA_PROJECT_REGEX = 'https://release-monitoring.org/project/([0-9]+)'


def anitya_find_project_id(proj_name: str) -> Optional[int]:
    """
    Returns the anitya project ID with given name.
    """
    search_url = ANITYA_SEARCH_URL % proj_name
    search = requests.get(search_url)
    if search.url == search_url:
        print("No exact match found for %s." % proj_name, file=sys.stderr)
        return None
    return int(re.match(ANITYA_PROJECT_REGEX, search.url).groups()[0])

def iter_projects(*projects):
    """
    Iterates over a list of projects and compares versions.
    """
    versions = []
    for prog_name in projects:
        prog_id = anitya_find_project_id(proj_name=prog_name)
        res = requests.get('https://release-monitoring.org/project/%d/' % prog_id)
        res.raise_for_status()
        lines = res.text.splitlines()
        max_version = None
        for line in lines:
            if "doap:revision" in line:
                version = line[line.find('>')+1:line.rfind('<')].split('.')
                if max_version is None or version > max_version:
                    max_version = version
        res = subprocess.run(['zypper', 'if', prog_name], stdout=subprocess.PIPE)
        for line in res.stdout.splitlines():
            if line.startswith(b'Version'):
                opensuse_version = line[line.find(b':')+2:line.find(b'-')].decode().split('.')
                break
        versions.append((prog_name, '.'.join(max_version), '.'.join(opensuse_version)))
    print(tabulate.tabulate(versions, headers=('name', 'anitya', 'opensuse')))

def main():
    """
    Main program.
    """
    parser = argparse.ArgumentParser(description='Check anitya for project versions.')
    parser.add_argument('projects', type=int, nargs='*',
                        help='name of projects to check')
    args = parser.parse_args()
    if args.projects:
        iter_projects(*args.projects)
    else:
        projects = config.read_config('check_anitya')
        if projects:
            iter_projects(*projects.splitlines())
        else:
            print("No projects got as parameter and nothing configured.")

if __name__ == '__main__':
    main()
