import re
import sys
from ..specfile.helpers import detect_specfile, get_source_urls, detect_github_tag_prefix, get_current_version
from urllib.parse import urlparse

import requests


RE_GITHUB_PATH_REPO = re.compile('^/([^/]+/[^/]+)/')


def detect_previous_version(changes):
    for line in changes:
        previous_version_match = re.match('^- +(?:version )?update(?: to)?(?: version)? ([0-9.]+)', line, re.IGNORECASE)
        if previous_version_match:
            previous_version = previous_version_match[1]
            break
    else:
        sys.exit("Could not determine the last mentioned version from the changes file.")
    return previous_version


def get_changelog_from_github(previous_version: str) -> dict:
    specfilename = detect_specfile()
    current_version = get_current_version(specfilename=specfilename)

    urls = get_source_urls(specfilename=specfilename)
    for url in urls:
        parsed = urlparse(url)
        if parsed.hostname == 'github.com' and 'archive' in parsed.path:
            repo_path = RE_GITHUB_PATH_REPO.match(parsed.path).group(1)
            break
    else:
        sys.exit('Found not source URL with GitHub archive.')

    tag_prefix = detect_github_tag_prefix(specfilename=specfilename)

    url = f'https://api.github.com/repos/{repo_path}/compare/{tag_prefix}{previous_version}...{tag_prefix}{current_version}'
    print(f'Downloading from: {url}', file=sys.stderr)
    compare = requests.get(url)
    compare.raise_for_status()
    return compare.json()
