# -*- coding: utf-8 -*-
"""
"""
import argparse
import glob
import re
import select
import sys
import tarfile

from typing import Optional
from itertools import compress


VERSION_REGEX = r"(?:v|version )?([0-9\.]+)(.*)"


def convert_base(changelog: str, softwarename: str = '') -> str:
    changelog = changelog.replace('\r\n', '\n')
    # ignore rst blocks:
    changelog = re.sub(r"^\.\. .*$", "", changelog, flags=re.MULTILINE)
    # rst history header
    changelog = re.sub(r"^=+\nhistory\n=+$", "", changelog, flags=re.MULTILINE | re.IGNORECASE)
    changelog = re.sub("^#? ?(%s )?change ?log.*$" % softwarename, "", changelog, count=0, flags=re.MULTILINE | re.IGNORECASE)
    return changelog


def convert_base_after(changelog: str, previous_version: Optional[str] = None):
    changelog = re.sub(r"\n(\s*\n)+", "\n", changelog)

    author_pattern = "^[^a-z]*authors?:?"
    # find authors section:
    authors = re.search(author_pattern + "$", changelog, flags=re.IGNORECASE | re.MULTILINE)
    if authors:
        print("found authors %r" % authors[0], file=sys.stderr)
        spaces = len(re.search("^ *", authors[0])[0])
        changelog = re.sub(author_pattern + ".*?^( {,%d}-)" % spaces, r"\1", changelog, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)

    if previous_version:
        changelog = changelog[:changelog.find("- update to version %s:" % previous_version)]

    # ornamental lines or heading leftovers
    changelog = re.sub(r"^[=~-]+$", "", changelog, flags=re.MULTILINE)

    # empty lines
    changelog = re.sub(r"\n{2,}", r"\n", changelog)

    return changelog.strip()


def convert_keep_a_changelog(changelog: str):
    changelog = re.sub(r"^(.*?)#", "#", changelog, flags=re.DOTALL)
    changelog = re.sub(r"^## \[v([0-9\.]+)\] (.*)$", r"- update to version \1:", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^## \[unreleased\]$", "", changelog, flags=re.MULTILINE | re.IGNORECASE)

    changelog = re.sub(r"^### (.*)$", r" - \1:", changelog, flags=re.MULTILINE)
    return changelog


def convert_textile(changelog: str):
    changelog = re.sub(r"^h2. Version ([0-9\.]+)$", r"- update to version \1:", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^h1.(.*)", "", changelog, flags=re.MULTILINE | re.IGNORECASE)
    changelog = re.sub(r"^\* (.*)$", r" - \1", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^\*\* (.*)$", r"  - \1", changelog, flags=re.MULTILINE)
    return changelog


def convert_debian(changelog: str):
    changelog = re.sub(r"^ ", " ", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^[^ ]+ \(([0-9\.-]+)-(0ubuntu1)?\) .*?$", r"- update to version \1:", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^ ?-- .*?$", "", changelog, flags=re.MULTILINE)
    return changelog


def convert_axel(changelog: str):
    changelog = re.sub(r"^Version: ([0-9\.]+), [0-9-]{10}$", r"- update to version \1:", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^\* (.*)$", r" - \1", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^\    -(.*)$", r"  - \1", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^\s*\[ [\w\s]+ \]$", "", changelog, flags=re.MULTILINE)
    return changelog


def convert_rst(changelog: str):
    """
    Generic RST conversion

    Xarray:
    ignore everything until the first version
    headers:
    v0.12.2 (29 June 2019)
    ----------------------

    New functions/methods
    ~~~~~~~~~~~~~~~~~~~~~

    Xonsh headers:
    **Header:**
    """
    # xarray preface until first verion (rst?)
    changelog = re.sub(r"^(.*?)\nv", "v", changelog, flags=re.DOTALL)


    # normal list entries
    # Are ~ headers used?
    if re.search('[a-z0-9]\n~+\n', changelog, flags=re.MULTILINE | re.IGNORECASE):
        changelog = re.sub("^  ", "    ", changelog, flags=re.MULTILINE)
        changelog = re.sub(r"^[-\*] (.*)$", r"  - \1", changelog, flags=re.MULTILINE)
    else:
        changelog = re.sub("^ ", "  ", changelog, flags=re.MULTILINE)
        changelog = re.sub(r"^[-\*] (.*)$", r" - \1", changelog, flags=re.MULTILINE)

    # versions, with or without date
    changelog = re.sub(r"^v?([0-9\.]+)( \(.*?\))?$", r"- update to version \1:", changelog, flags=re.MULTILINE)

    # sections
    changelog = re.sub(r"^\*?\*?([A-Za-z]+.*?):?\*?\*?$", r" - \1:", changelog, flags=re.MULTILINE)

    return changelog


def convert_markdown(changelog: str):
    """
    Generic markdown conversion
    """

    # Normalize headings
    changelog = re.sub(r"(\n|^)(.+?)\n=+\n", r"# \2\n", changelog)
    changelog = re.sub(r"(\n|^)(.+?)\n-+\n", r"## \2\n", changelog)

    # preface, everything until first header
    changelog = re.sub(r"^(.*?)#", "#", changelog, flags=re.DOTALL)

    for version_hash_count in range(1, 4):
        prefix = '#' * version_hash_count
        changelog, version_replacements = re.subn(fr"^{prefix} %s$" % VERSION_REGEX, r"- update to version \1:",
                                                  changelog,
                                                  flags=re.MULTILINE | re.IGNORECASE)
        if version_replacements:
            break
    else:
        print('Unable to detect version headers.', file=sys.stderr)

    # must be a tuple as used twice
    headers = tuple('\n' + '#' * headers_hash_count for headers_hash_count in range(version_hash_count + 1, 7))
    headers_used = tuple(header + ' ' in changelog for header in headers)
    headers = tuple(compress(headers, headers_used))
    # get rid of the heading newline
    headers = map(str.strip, headers)
    default_whitespace_prefix = ' ' * sum(headers_used)

    for num_whitespaces, header in enumerate(headers):
        whitespaces = ' ' * num_whitespaces
        changelog = re.sub(fr"^{header} (.*?):?$", fr" {whitespaces}- \1:", changelog, flags=re.MULTILINE)

    # normal entries
    changelog = re.sub(r"^  (.*)$", fr" {default_whitespace_prefix}  \1", changelog, flags=re.MULTILINE)
    # translate all normal entries, except for the "- update to version" lines
    changelog = re.sub(r"^[\*-] ((?!update to version).*)$", fr" {default_whitespace_prefix}- \1", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^(\w)(.*)$", fr" {default_whitespace_prefix}- \1\2", changelog, flags=re.MULTILINE)
    return changelog


def convert_misp(changelog, with_markdown=True):
    """
    Also has third-level headings with ~~~
    """
    # Indent all the list items
    changelog = re.sub(r"^( .|-[^-])", r"  \1", changelog, flags=re.MULTILINE)

    # Normalize misp-special headers
    changelog = re.sub(r"(\n|^)(.+?)\n~+\n", r" - \2\n", changelog)
    if with_markdown:
        return convert_markdown(changelog)
    else:
        return changelog


def convert_git(changelog: str):
    """
    Converts git logs.

    Assumption: no empty lines without whitespace (seems to hold)
    """
    version_template = """
    New release [].?([0-9\.]+)(.*)
"""
    strip_template = """commit [0-9A-Fa-f]{40}(
Merge: [0-9A-Fa-f ]+)?
Author: .*? <.*?>
Date:   .*?
"""
    # remove git stuff
    changelog = re.sub(strip_template, '', changelog)
    # make first line of commit summary the list item
    changelog = re.sub('\n\n    ', '\n - ', changelog)
    # ensure we start with a list item
    changelog = re.sub('^\n    ', ' - ', changelog)
    # subsequent lines of commit summaries
    changelog = re.sub("\n    \n    ", "\n   ", changelog, flags=re.MULTILINE)
    changelog = re.sub("\n    ", "\n   ", changelog, flags=re.MULTILINE)
    # merges
    changelog = re.sub('^ - Merge branch \'.*?\' of .*?$', '', changelog,
                       flags=re.IGNORECASE | re.MULTILINE)
    # empty lines
    changelog = re.sub(r"\n{2,}", r"\n", changelog)
    # releases
    changelog = re.sub("^ - (new )?release (of )?([a-z]+-)?([0-9\.]+?)([.:]*)$",
                       r"- update to version \4:",
                       changelog, flags=re.MULTILINE | re.IGNORECASE)
    return changelog


STYLES = {
    # generic
    'debian': convert_debian,
    'keepachangelog': convert_keep_a_changelog,
    'md': convert_markdown,
    'markdown': convert_markdown,
    'rst': convert_rst,
    'textile': convert_textile,
    # specific
    'axel': convert_axel,
    'xonsh': convert_rst,
    'misp': convert_misp,
    'pymisp': convert_misp,
    'git': convert_git,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('style', nargs='?', default='automatic',
                        choices=tuple(STYLES.keys()) + ('automatic', ))
    parser.add_argument('-v', '--verbose', action='store_const', const=True)
    parser.add_argument('-p', '--previous-version', help='Previous version string to use instead of extraction from *.changes file.')
    parser.add_argument('-a', '--archive', help='The code archive to use and search changelog for.',
                        type=argparse.FileType('r'))
    args = parser.parse_args()

    if not args.archive:
        files = glob.glob("*.tar.*z")
        if not files:
            sys.exit("No *.tar.*z file found!")
        elif len(files) > 1:
            # Try to filter out all names without dots (indicating version numbers)
            files = list(filter(lambda fname: re.search('[0-9]', fname), files))
            if len(files) > 1 or not files:
                print(files)
                sys.exit("More than one *.tar.*z file found! Could not determine which one to use. Try '-a'.")
        archivefilename = files[0]
    else:
        archivefilename = args.archive.name
    softwarename = archivefilename[:archivefilename.rfind('-')]
    if softwarename.startswith('python-'):
        softwarename = softwarename[7:]
    if select.select([sys.stdin, ], [], [], 0.0)[0]:  # stdin
        archivefilename = "<stdin>"

    if not args.previous_version:
        files = glob.glob("*.changes")
        if not files:
            sys.exit("No *.changes.* file found!")
        elif len(files) > 1:
            sys.exit("More than one *.changes.* file found!")
        changesfilename = files[0]

    print("Found %r and %r of %s." % (archivefilename, args.previous_version or changesfilename, softwarename), file=sys.stderr)

    if not args.previous_version:
        # Find previous version in changes file
        with open(changesfilename) as changes:
            line = changes.readline()
            while line:
                previous_version = re.search('[0-9]+\.[0-9]+(\.[0-9]+)?', line)
                if re.match('^- (version )?update( to)?( version)?', line, re.IGNORECASE) and previous_version:
                    previous_version = previous_version[0]
                    break
                line = changes.readline()
            else:
                sys.exit("Could not determine the last mentioned version from the changes file.")
            print("Found previous version %s" % previous_version, file=sys.stderr)
    else:
        previous_version = args.previous_version

    # find and read changelog from archive
    if archivefilename != '<stdin>':
        with tarfile.open(archivefilename, 'r') as archive:
            # get a list of files matching the pattern
            candidates = list(filter(lambda filename: re.search('(changes|changelog|history(of changes)?|whats.new|news)[^/]*$',
                                                                filename,
                                                                flags=re.IGNORECASE),
                                     [member.name for member in archive.getmembers() if member.isfile()]))
            if not candidates:
                sys.exit('Found no changelog in archive :/')
            # remove hidden files (in root directory and in subdirectories)
            candidates = list(filter(lambda name: not re.search('(^\.|/\.)', name), candidates))
            if args.verbose:
                print('Changelog candidates:\n*', '\n* '.join(candidates), file=sys.stderr)
            # find the changelog file with the smallest number of slashes in it's path
            number_of_slashes = [filename.count('/') for filename in candidates]
            smallest = min(number_of_slashes)
            candidate = list(candidates)[list(number_of_slashes).index(smallest)]
            print("Found changelog file %r." % candidate, file=sys.stderr)
            changelog = archive.extractfile(candidate).read().decode()
    else:
        changelog = sys.stdin.read()

    if args.style == 'automatic':
        if candidate.endswith('debian/changelog'):
            args.style = 'debian'
        elif softwarename in STYLES:
            args.style = softwarename
        elif candidate.endswith('.rst'):
            args.style = 'rst'
        elif candidate.endswith('.md'):
            args.style = 'markdown'
        elif changelog.startswith('commit '):
            args.style = 'git'
        else:
            exit('Could not determine which conversion to use.')
        print('Using autodetected style %r' % args.style, file=sys.stderr)

    changelog = convert_base(changelog, softwarename)
    changelog = STYLES[args.style](changelog)
#    print(changelog[:200])
    changelog = convert_base_after(changelog, previous_version)
    try:
        print(changelog)
    except BrokenPipeError:
        pass


if __name__ == '__main__':
    main()
