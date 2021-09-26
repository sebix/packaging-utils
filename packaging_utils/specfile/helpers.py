"""
specfile helpers
"""

import os
import re
import subprocess
from pathlib import Path

from typing import List, Optional


VERSION_MATCH = re.compile(r'^(Version:\s+)(.*?)$', flags=re.MULTILINE)
SOURCE_FILENAME = re.compile(r'Source[0-9]*:\s+(.*)', flags=re.IGNORECASE)
RE_SPECFILE_URL = re.compile(r'URL:\s+(.*)', flags=re.IGNORECASE)
SOURCE_VERSION_INDICATORS = ('%version', '%{version}', '%VERSION', '%{VERSION}')
# catch-all group at the end is required to get at least one group so that we can always query a group
RE_GITHUB_ARCHIVE_PREFIX = re.compile(r'^https://github.com/[^/]+/[^/]+/archive/(v)?(.*)')
RE_GITHUB_ARCHIVE_REF_PREFIX = re.compile(r'^https://github.com/[^/]+/[^/]+/archive/refs/tags/(v)?(.*)')


def detect_specfile() -> str:
    cwd = Path(os.getcwd()).parts[-1]
    specfilename = f'{cwd}.spec'
    if Path(specfilename).is_file():
        return specfilename
    else:
        raise ValueError(f'Unable to detect name of specfile. Assumed {specfilename}')


def get_current_version(specfilename: str) -> str:
    with open(specfilename) as handle:
        version = VERSION_MATCH.search(handle.read()).group(2)
    return version


def get_source_urls(specfilename: str, version: Optional[str] = None) -> List[str]:
    """
    Querying the Source tag directly gives weird results. With mypy, Source0 and Source 99 exist.
    `rpmspec --srpm -q --qf "%{Source}" mypy.spec` gives the value of Source99
    Any other tag (Source0, Source 99 included) give `error: incorrect format: unknown tag: "Source0"`
    So let's do it ourself
    """
    result = subprocess.run(['rpmspec', '-P', specfilename],
                            stdout=subprocess.PIPE)
    if result.stderr:
        raise ValueError(result.stderr)

    if not version:
        version = get_current_version(specfilename)

    urls = []
    for spec_line in result.stdout.decode().splitlines():
        source_name = SOURCE_FILENAME.match(spec_line)
        if not source_name:
            continue
        url = source_name.group(1)
        if not any(marker in url for marker in SOURCE_VERSION_INDICATORS) and version not in url:
            continue
        urls.append(url)
    return urls


def get_source_filename(specfilename: str, version: Optional[str] = None) -> List[str]:
    filenames = []
    for url in get_source_urls(specfilename, version):
        if '/' not in url:
            filenames.append(url)
        else:
            slash = url.rfind('/')
            filenames.append(url[slash + 1:])
    return filenames


def detect_github_tag_prefix(specfilename: str) -> str:
    """
    Supports
    https://github.com/asottile/pyupgrade/archive/refs/tags/v%{version}.tar.gz
    and
    https://github.com/asottile/pyupgrade/archive/v%{version}.tar.gz
    URLs
    """
    urls = get_source_urls(specfilename=specfilename)
    for url in urls:
        if 'refs/tags' in url:
            parsed = RE_GITHUB_ARCHIVE_REF_PREFIX.match(url)
        else:
            parsed = RE_GITHUB_ARCHIVE_PREFIX.match(url)
        if parsed:
            if parsed.group(1) == 'v':
                return 'v'
            else:
                return ''
    raise ValueError('Unable to parse GitHub archive URLs.')


def get_url(specfilename: str) -> Optional[str]:
    """
    Get's the URL from a specfile.
    """
    result = subprocess.run(['rpmspec', '-P', specfilename],
                            stdout=subprocess.PIPE)
    if result.stderr:
        raise ValueError(result.stderr)

    for spec_line in result.stdout.decode().splitlines():
        url = RE_SPECFILE_URL.match(spec_line)
        if not url:
            continue
        return url.group(1)
