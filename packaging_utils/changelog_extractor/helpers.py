import re
import sys
from ..specfile.helpers import detect_specfile, get_source_urls, detect_github_tag_prefix, get_current_version, get_url
from enum import Enum
from urllib.parse import urlparse
from typing import Optional, Tuple, Union

import requests


RE_GITHUB_PATH_REPO = re.compile('^/([^/]+/[^/]+)/?')
RE_GIT_COMMIT = re.compile('^[a-f0-9]{40}$')


class github_type(Enum):
    COMPARE = 1
    RELEASE = 2


def detect_previous_version(changes):
    for line in changes:
        previous_version_match = re.match('^- +(?:version )?update(?: to)?(?: version)? ([0-9.]+)', line, re.IGNORECASE)
        if previous_version_match:
            previous_version = previous_version_match[1]
            break
    else:
        sys.exit("Could not determine the last mentioned version from the changes file.")
    return previous_version


def get_changelog_from_github(previous_version: str, current_version: Optional[str] = None) -> Tuple[Union[dict, str], github_type]:
    """
    First, get the GitHub URL by interpreting the Source tags and the URL tag.
    Then, detect the tag-prefix.
    At the end, download the diff.
    """
    specfilename = detect_specfile()
    if not current_version:
        current_version = get_current_version(specfilename=specfilename)

    urls = get_source_urls(specfilename=specfilename)
    for url in urls:
        parsed = urlparse(url)
        if parsed.hostname == 'github.com' and 'archive' in parsed.path:
            repo_path = RE_GITHUB_PATH_REPO.match(parsed.path).group(1)
            tag_prefix = detect_github_tag_prefix(specfilename=specfilename)
            break
    else:
        url = get_url(specfilename=specfilename)
        parsed = urlparse(url)
        if parsed.hostname == 'github.com':
            repo_path = RE_GITHUB_PATH_REPO.match(parsed.path).group(1)
            tags = requests.get(f'https://api.github.com/repos/{repo_path}/releases/latest')
            tags.raise_for_status()
            if tags.json()['name'].startswith('v'):
                tag_prefix = 'v'
            else:
                tag_prefix = ''
        else:
            sys.exit('Also found no Source URL or URL for GitHub.')

    if not RE_GIT_COMMIT.match(current_version):
        current_version = tag_prefix + current_version

    release_url = f'https://api.github.com/repos/{repo_path}/releases/tags/{current_version}'
    print(f'Downloading from: {release_url}', file=sys.stderr)
    release = requests.get(release_url)
    release.raise_for_status()
    release_body = release.json()['body']
    if release_body.count('\n') > 2:
        return release_body, github_type.RELEASE

    print('GitHub release body appears too short, fallback to diff')
    compare_url = f'https://api.github.com/repos/{repo_path}/compare/{tag_prefix}{previous_version}...{current_version}'
    print(f'Downloading from: {compare_url}', file=sys.stderr)
    compare = requests.get(compare_url)
    compare.raise_for_status()
    return compare.json(), github_type.COMPARE


def get_changelog_from_github_releases(previous_version: str, current_version: Optional[str] = None) -> dict:
    """
    First, get the GitHub URL by interpreting the Source tags and the URL tag.
    Then, detect the tag-prefix.
    At the end, download the diff.
    """
    specfilename = detect_specfile()
    if not current_version:
        current_version = get_current_version(specfilename=specfilename)

    urls = get_source_urls(specfilename=specfilename)
    for url in urls:
        parsed = urlparse(url)
        if parsed.hostname == 'github.com' and 'archive' in parsed.path:
            repo_path = RE_GITHUB_PATH_REPO.match(parsed.path).group(1)
            tag_prefix = detect_github_tag_prefix(specfilename=specfilename)
            break
    else:
        url = get_url(specfilename=specfilename)
        parsed = urlparse(url)
        if parsed.hostname == 'github.com':
            repo_path = RE_GITHUB_PATH_REPO.match(parsed.path).group(1)
            releases = requests.get(f'https://api.github.com/repos/{repo_path}/releases')
            releases.raise_for_status()
            if releases.json()[0]['name'].startswith('v'):
                tag_prefix = 'v'
            else:
                tag_prefix = ''
        else:
            sys.exit('Also found no Source URL or URL for GitHub.')

    return {release['tag']: release['body'] for release in releases.json()}
