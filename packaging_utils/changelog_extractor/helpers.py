import re
import sys


def detect_previous_version(changes):
    for line in changes:
        previous_version_match = re.match('^- +(?:version )?update(?: to)?(?: version)? ([0-9.]+)', line, re.IGNORECASE)
        if previous_version_match:
            previous_version = previous_version_match[1]
            break
    else:
        sys.exit("Could not determine the last mentioned version from the changes file.")
    return previous_version
