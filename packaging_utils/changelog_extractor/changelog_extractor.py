# -*- coding: utf-8 -*-
"""
"""
import argparse
import glob
from pathlib import Path
import re
import select
import subprocess
import sys
import tarfile
import traceback
import zipfile

from typing import Optional
from itertools import compress
from .helpers import get_changelog_from_github, detect_previous_version


# accepts formats like "[3.3.2]"
VERSION_REGEX = r"(?:v|version )?\[?([0-9\.]+)\]?(.*)"
RE_VERSION_REGEX_START = re.compile(f'^{VERSION_REGEX}')
RE_TWO_DASHES = re.compile(r'.*?\-.*?\-.*?')

VERBOSE = False


def convert_base(changelog: str, softwarename: str = '') -> str:
    if not isinstance(changelog, str):
        return changelog

    changelog = changelog.replace('\r\n', '\n')
    # generic history headers
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
        previous_version_position = changelog.find(f"- update to version {previous_version}:")
        # if the previous_version is not found, there's nothing to scrap.
        if previous_version_position != -1:
            changelog = changelog[:previous_version_position]

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
    # format: [packagename] ([versionumber]-[optionalrevision]) [irrelevant information]
    changelog = re.sub(r"^[^ ]+ \(([0-9\.-]+)(-.*?)?\) .*?$", r"- update to version \1:", changelog, flags=re.MULTILINE)
    # irrelevant author information: "  [ Author name ]""
    changelog = re.sub(r"^  \[[^\]]+\]$", "", changelog, flags=re.MULTILINE)
    # signatures
    changelog = re.sub(r"^ ?-- .*?$", "", changelog, flags=re.MULTILINE)
    # list items
    changelog = re.sub(r"^    (.+?)$", r"   \1", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^  \* (.+?)$", r" - \1", changelog, flags=re.MULTILINE)
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
    # ignore rst blocks:
    changelog = re.sub(r"^\.\. .*$", "", changelog, flags=re.MULTILINE)

    # xarray preface until first verion
    changelog = re.sub(r"^(.*?)\nv", "v", changelog, flags=re.DOTALL)

    # first level headers
    changelog = re.sub(r"^\nhistory\n-+$", "", changelog, flags=re.MULTILINE | re.IGNORECASE)

    # normal list entries
    # Are ~ headers used?
    if re.search('[a-z0-9]\n~+\n', changelog, flags=re.MULTILINE | re.IGNORECASE):
        changelog = re.sub("^  ", "    ", changelog, flags=re.MULTILINE)
        changelog = re.sub(r"^[-\*] (.*)$", r"  - \1", changelog, flags=re.MULTILINE)
    else:
        changelog = re.sub("^ ", "  ", changelog, flags=re.MULTILINE)
        changelog = re.sub(r"^[-\*] (.*)$", r" - \1", changelog, flags=re.MULTILINE)

    # versions, with or without date
    # following line may be a '+' line
    changelog = re.sub(r"^v?([0-9\.]+)( \(.*?\))?(\n[+]+)?$", r"- update to version \1:", changelog, flags=re.MULTILINE)

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
            if VERBOSE:
                print(f'Markdown converter: Using {prefix} as version header prefix.', file=sys.stderr)
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


def convert_confluence(changelog: str, softwarename: Optional[str] = None):
    """
    Generic confluence conversion
    """

    # preface, everything until first list item
    changelog = re.sub(r"^(.*?)\*", "*", changelog, flags=re.DOTALL)

    version_prefix = f' {softwarename}' if softwarename else ' (?:[^ ]+)'
    changelog = re.sub(fr"^[\*]{version_prefix} {VERSION_REGEX}$", r"- update to version \1:",
                       changelog,
                       flags=re.MULTILINE | re.IGNORECASE)

    # normal entries
    changelog = re.sub(r"^\*\*", " -", changelog, flags=re.MULTILINE)
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
    changelog = re.sub(r"^ - (new )?release (of )?([a-z]+-)?([0-9\.]+?)([.:]*)$",
                       r"- update to version \4:",
                       changelog, flags=re.MULTILINE | re.IGNORECASE)
    return changelog


def convert_github(changelog: dict) -> str:
    changelog = [entry['commit']['message'] for entry in changelog['commits']]
    changelog.reverse()  # most current to top

    result = []
    for line in changelog:
        if line.startswith('[pre-commit.ci]'):
            continue
        if line.startswith('Merge pull request'):
            continue
        re_version = RE_VERSION_REGEX_START.match(line)
        if re_version:
            result.append(f'- update to version {re_version.group(1)}:')
        else:
            line = line.strip()
            line = line.replace('\n\n', '\n')
            line = line.replace('\n', '\n   ')
            result.append(f' - {line}')

    return '\n'.join(result)


def convert_github_releases(changelog: dict) -> str:
    changelog = [entry['commit']['message'] for entry in changelog['commits']]
    changelog.reverse()  # most current to top

    result = []
    for line in changelog:
        if line.startswith('[pre-commit.ci]'):
            continue
        if line.startswith('Merge pull request'):
            continue
        re_version = RE_VERSION_REGEX_START.match(line)
        if re_version:
            result.append(f'- update to version {re_version.group(1)}:')
        else:
            line = line.strip()
            line = line.replace('\n\n', '\n')
            line = line.replace('\n', '\n   ')
            result.append(f' - {line}')

    return '\n'.join(result)


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
    'confluence': convert_confluence,
    'github': convert_github,
    'github_releases': convert_github_releases,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('style', nargs='?', default='automatic',
                        choices=tuple(STYLES.keys()) + ('automatic', ))
    parser.add_argument('-v', '--verbose', action='store_const', const=True)
    parser.add_argument('-p', '--previous-version', help='Previous version string to use instead of extraction from *.changes file.')
    parser.add_argument('-a', '--archive', help='The code archive to use and search changelog for.',
                        type=argparse.FileType('r'))
    parser.add_argument('--github-current-version',
                        help='Use this as current version for the GitHub extraction. Could be a commit id or tag.')
    parser.add_argument('--vc',
                        help='Put the changelog into the changes file with `osc vc` if extraction suceeded.',
                        action='store_true')
    args = parser.parse_args()
    global VERBOSE
    VERBOSE = args.verbose

    if not args.archive:
        files = glob.glob("*.tar.*") or glob.glob("*.zip")
        if not files:
            sys.exit("No *.tar.* or *.zip file found!")
        elif len(files) > 1:
            # Filter out all names without numbers (indicating version numbers)
            files = list(filter(lambda fname: re.search('[0-9]', fname), files))
            # Filter out all names ending with .asc
            files = list(filter(lambda fname: not fname.endswith('.asc'), files))
            if len(files) > 1 or not files:
                sys.exit(f"More than one *.tar.* file found ({files!r})! Could not determine which one to use. Try '-a'.")
        archivefilename = files[0]
    else:
        archivefilename = args.archive.name
        print(args.archive.name, type(args.archive.name))
    if archivefilename.endswith(".zip"):
        archive_opener = zipfile.ZipFile
    else:
        archive_opener = tarfile.open
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
            previous_version = detect_previous_version(changes)
            print("Found previous version %s" % previous_version, file=sys.stderr)
    else:
        previous_version = args.previous_version

    # find and read changelog from archive
    changelog_from_github = False
    try_github = False
    if archivefilename != '<stdin>' and not args.style.startswith('github'):
        with archive_opener(archivefilename, 'r') as archive:
            # get a list of files matching the pattern
            candidates = list(filter(lambda filename: re.search('(changes|changelog|history(of changes)?|whats.new|news)[^/]*$',
                                                                filename,
                                                                flags=re.IGNORECASE),
                                     [member.name for member in archive.getmembers() if member.isfile()]))
            print('Changelog candidates:\n*', '\n* '.join(candidates), file=sys.stderr)
            if candidates:
                # remove hidden files (in root directory and in subdirectories). './' is allowed though
                candidates = tuple(filter(lambda name: not re.search(r'(^\.(^/)|/\.)', name), candidates))
                if args.verbose:
                    print('Changelog candidates:\n*', '\n* '.join(candidates), file=sys.stderr)
                # Remove empty files
                empty_files = tuple(not archive.extractfile(candidate).read().strip() for candidate in candidates)
                if any(empty_files):
                    if args.verbose:
                        print('Ignoring empty files:', tuple(compress(candidates, empty_files)), file=sys.stderr)
                    candidates = tuple(compress(candidates, tuple(map(lambda x: not x, empty_files))))
                # Remove files with two dashes in filename
                # example subnetcalc: false-positive "filter-debian-changelog"
                dashes = tuple(RE_TWO_DASHES.match(Path(candidate).name) for candidate in candidates)
                if any(dashes):
                    if args.verbose:
                        print('Ignoring files with dashes in filenames:', tuple(compress(candidates, dashes)), file=sys.stderr)
                    candidates = tuple(compress(candidates, tuple(map(lambda x: not x, dashes))))
                # find the changelog file with the smallest number of slashes in it's path
                if args.verbose:
                    print('Selecting file with smallest number of slashes in path.', file=sys.stderr)
                number_of_slashes = [filename.count('/') for filename in candidates]
                smallest = min(number_of_slashes)
                candidate = tuple(candidates)[tuple(number_of_slashes).index(smallest)]
                print("Found changelog file %r." % candidate, file=sys.stderr)
                changelog = archive.extractfile(candidate).read().decode()
            else:
                try_github = True
    else:
        changelog = sys.stdin.read()

    if try_github or args.style.startswith('github'):
        changelog = None
        try:
            changelog = get_changelog_from_github(previous_version=previous_version, current_version=args.github_current_version)
        except Exception:
            if args.verbose or args.style == 'github':
                print(traceback.format_exc(), file=sys.stderr)
            sys.exit('Found no changelog in archive and extraction from GitHub failed as well :/')
        else:
            if changelog:
                changelog_from_github = True
            else:
                sys.exit('Found no changelog in archive :/')

    if args.style == 'automatic':
        if changelog_from_github:
            args.style = 'github'
        elif candidate.endswith('debian/changelog'):
            args.style = 'debian'
        elif softwarename in STYLES:
            args.style = softwarename
        elif candidate.endswith('.rst') or changelog.startswith('.. '):
            args.style = 'rst'
        elif candidate.endswith('.md') or (len(changelog.splitlines()) >= 1 and changelog.splitlines()[1].startswith('==')):
            args.style = 'markdown'
        elif changelog.startswith('commit '):
            args.style = 'git'
        elif '\n** ' in changelog:
            args.style = 'confluence'
        else:
            sys.exit('Could not determine which conversion to use.')
        print('Using autodetected style %r' % args.style, file=sys.stderr)

    changelog = convert_base(changelog, softwarename)
    changelog = STYLES[args.style](changelog)
#    print(changelog[:200])
    changelog = convert_base_after(changelog, previous_version)
    try:
        if args.vc:
            subprocess.call(('osc', 'vc', '-m', changelog))
        else:
            print(changelog)
    except BrokenPipeError:
        pass


if __name__ == '__main__':
    main()
