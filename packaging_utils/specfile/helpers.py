"""
specfile helpers
"""

import os
import subprocess
from pathlib import Path


def detect_specfile() -> str:
    cwd = Path(os.getcwd()).parts[-1]
    specfilename = f'{cwd}.spec'
    if Path(specfilename).is_file():
        return specfilename
    else:
        raise ValueError(f'Unable to detect name of specfile. Assumed {specfilename}')


def get_source_filename(specfilename) -> str:
    for source_tag_name in ('Source', 'Source0'):
        result = subprocess.run(['rpmspec', '--srpm', '-q', '--qf', '%%{%s}\n' % source_tag_name, specfilename],
                                stdout=subprocess.PIPE)
        if result.stderr:
            continue
        else:
            return result.stdout.decode().strip()
    else:
        raise ValueError(result.stderr)
