#!/usr/bin/python3
"""
Rewrites specfiles to fix the %licsens
"""
import argparse
import re
import sys


LICENSE_MATCH = re.compile(r'((copying|licenses?(/[^\s]*)?)(.(md|rst|txt))?)',
                           flags=re.IGNORECASE)
EMPTY_DOC = re.compile(r'^%doc\s*$')


def fix_license(filename: str, dry_run: bool = False):
    """
    Reads and writes the filename inserting %license.
    """
    with open(filename, 'rt') as original_fh:
        lines = original_fh.read().splitlines()
    if any((line.startswith('%license') for line in lines)):
        print('Found %license. Aborting.', file=sys.stderr)
        return 0
    doc_lines = (ind for ind, line in enumerate(lines)
                 if line.startswith('%doc'))
    if not doc_lines:
        print('No %doc lines found. Aborting', file=sys.stderr)
        return 2
    licenses = []
    for doc_line in doc_lines:
        doc_line_split = re.split(r'\s+', lines[doc_line])
        new_doc_line = []
        old_license_count = len(licenses)
        for doc_line_fragment in doc_line_split:
            license_filenames = LICENSE_MATCH.findall(doc_line_fragment)
            if len(license_filenames) == 0:
                new_doc_line.append(doc_line_fragment)
                continue
            licenses.append(license_filenames[0][0])
        if old_license_count != len(licenses):  # something changed
            lines[doc_line] = ' '.join(new_doc_line)
            if EMPTY_DOC.match(lines[doc_line]):
                del lines[doc_line]
                doc_line -= 1
            break
    else:
        print('No license found. Aborting.', file=sys.stderr)
        return 2
    print('Licenses found:', ' '.join(licenses))
    lines.insert(doc_line + 1,
                 '%license' + (' %s' * len(licenses)) % tuple(licenses))

    output = '\n'.join(lines)
    if dry_run:
        print(output)
        return 0

    with open(filename, 'wt') as new_handle:
        new_handle.write(output)
    return 0


def main():
    """
    Main program.
    """
    parser = argparse.ArgumentParser(description='Rewrites given specfile to fix license.')
    parser.add_argument('filename', nargs='+',
                        help='paths to filenames')
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help='Simulate only')
    args = parser.parse_args()
    max_retval = 0
    for filename in args.filename:
        max_retval = max((max_retval,
                          fix_license(filename, dry_run=args.dry_run)))
    return max_retval


if __name__ == '__main__':
    sys.exit(main())
