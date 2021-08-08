#!/usr/bin/python3
"""
Checks anitya (release-monitoring.org) for updates.
"""
import argparse
import concurrent.futures
import re
import sys
from typing import List, Optional, Tuple

import requests
import tabulate

from ..common import config, zypper
from ..common.conversion import Version

ANITYA_SEARCH_URL = 'https://release-monitoring.org/projects/search/?pattern=%s'
ANITYA_PROJECT_REGEX = 'https://release-monitoring.org/project/([0-9]+)'


def anitya_find_project_id(proj_name: str) -> Optional[int]:
    """
    Returns the anitya project ID with given name.
    """
    search_url = ANITYA_SEARCH_URL % proj_name
    search = requests.get(search_url)
    if search.url == search_url:
        matches = re.findall(r'<a href="/project/([0-9]+)/">\s+%s\s+</a>' % proj_name,
                             search.text)
        if len(matches) == 1:
            return int(matches[0])
        else:
            print("No exact or more than one match found for %s. Have a look at %r."
                  "" % (proj_name, search.url), file=sys.stderr)
            return None
    else:
        return int(re.match(ANITYA_PROJECT_REGEX, search.url).groups()[0])


def do_project(project: str) -> Optional[Tuple[str, str, str]]:
    """
    Query Anitya and zypper for current version.
    """
    max_version = None
    prog_id = anitya_find_project_id(proj_name=project)
    if prog_id:
        res = requests.get('https://release-monitoring.org/project/%d/' % prog_id)
        res.raise_for_status()
        lines = res.text.splitlines()
        for line in lines:
            if "doap:revision" in line:
                version = Version(line[line.find('>') + 1:line.rfind('<')])
                if version and (max_version is None or version > max_version):
                    max_version = version
    opensuse_version = zypper.package_version(project)
    return (project,
            str(max_version) if max_version else '',
            str(opensuse_version) if opensuse_version else '')


def iter_projects(*projects: List[str]):
    """
    Iterates over a list of projects and compares versions.
    """
    versions = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        get_ids = {executor.submit(do_project, prog_name): prog_name for prog_name in projects}
        for future in concurrent.futures.as_completed(get_ids):
            project_versions = future.result()
            if project_versions:
                versions.append(project_versions)
    if versions:
        print(tabulate.tabulate(versions, headers=('name', 'anitya', 'opensuse')))


def main():
    """
    Main program.
    """
    parser = argparse.ArgumentParser(description='Check anitya for project versions.')
    parser.add_argument('projects', nargs='*',
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
