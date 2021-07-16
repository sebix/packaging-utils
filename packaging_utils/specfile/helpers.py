"""
specfile helpers
"""

import os
import re
import subprocess
from pathlib import Path


VERSION_MATCH = re.compile(r'^(Version:\s+)(.*?)$', flags=re.MULTILINE)
SOURCE_FILENAME = re.compile(r'Source[0-9]*:\s+(.*)', flags=re.IGNORECASE)


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


def get_source_filename(specfilename) -> str:
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
    for spec_line in result.stdout.decode().splitlines():
        source_name = SOURCE_FILENAME.match(spec_line)
        if source_name:
            url = source_name.group(1)
            if '/' not in url:
                return url
            slash = url.rfind('/')
            return url[slash + 1:]