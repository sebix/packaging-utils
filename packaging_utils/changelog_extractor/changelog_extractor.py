# -*- coding: utf-8 -*-
"""

TODOs: Generic Markdown conversions
"""
import argparse
import glob
import re
import select
import sys
import tarfile

def convert_base(changelog, softwarename):
    changelog = changelog.replace('\r\n', '\n')
    changelog = re.sub(r"^\.\. .*$", "", changelog, flags=re.MULTILINE) # some rst thing
    changelog = re.sub("^#? ?(%s )?change ?log.*$" % softwarename, "", changelog, count=0, flags=re.MULTILINE | re.IGNORECASE)
    return changelog

def convert_base_after(changelog, previous_version):
    changelog = re.sub("\n(\s*\n)+", "\n", changelog)

    author_pattern = "^[^a-z]*authors?:?"
    # find authors section:
    authors = re.search(author_pattern + "$", changelog, flags=re.IGNORECASE | re.MULTILINE)
    if authors:
        print("found authors %r" % authors[0], file=sys.stderr)
        spaces = len(re.search("^ *", authors[0])[0])
        changelog = re.sub(author_pattern + ".*?^( {,%d}-)" % spaces, r"\1", changelog, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)

    if previous_version:
        changelog = changelog[:changelog.find("- update to version %s" % previous_version)]

    # ornamental lines
    changelog = re.sub(r"^[=~-]+$", "", changelog, flags=re.MULTILINE)

    return changelog.strip()


def convert_isort(changelog):
    # TOOD: Not complete
    changelog = re.sub(r"^### ([0-9\.]+) (.*)$", r"- update to version \1:", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^=+$", "", changelog, flags=re.MULTILINE)
    return changelog


def convert_keep_a_changelog(changelog):
    changelog = re.sub(r"^(.*?)#", "#", changelog, flags=re.DOTALL)
    changelog = re.sub(r"^## \[v([0-9\.]+)\] (.*)$", r"- update to version \1:", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^## \[unreleased\]$", "", changelog, flags=re.MULTILINE | re.IGNORECASE)

    changelog = re.sub(r"^### (.*)$", r" - \1:", changelog, flags=re.MULTILINE)
    return changelog


def convert_textile(changelog):
    changelog = re.sub(r"^h2. Version ([0-9\.]+)$", r"- update to version \1:", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^h1.(.*)", "", changelog, flags=re.MULTILINE | re.IGNORECASE)
    changelog = re.sub(r"^\* (.*)$", r" - \1", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^\*\* (.*)$", r"  - \1", changelog, flags=re.MULTILINE)
    return changelog


def convert_debian(changelog):
    changelog = re.sub(r"^ ", " ", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^[^ ]+ \(([0-9\.-]+)\) .*?$", r"- update to version \1:", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^-- .*?$", "", changelog, flags=re.MULTILINE)
    return changelog


def convert_axel(changelog):
    changelog = re.sub(r"^Version: ([0-9\.]+), [0-9-]{10}$", r"- update to version \1:", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^\* (.*)$", r" - \1", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^\    -(.*)$", r"  - \1", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^\s*\[ [\w\s]+ \]$", "", changelog, flags=re.MULTILINE)
    return changelog


def convert_rst(changelog):
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

    # versions, with or without date
    changelog = re.sub(r"^v([0-9\.]+)( \(.*?\))?$", r"- update to version \1:", changelog, flags=re.MULTILINE)

    # sections
    changelog = re.sub(r"^\*?\*?([A-Za-z]+.*?):?\*?\*?$", r" - \1:", changelog, flags=re.MULTILINE)

    # normal entries
    changelog = re.sub("^  ", "    ", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^[-\*] (.*)$", r"  - \1", changelog, flags=re.MULTILINE)

    return changelog


def convert_markdown(changelog):
    """
    Tested with spyder (-related) software only
    """
    # preface, everything until first header
    changelog = re.sub(r"^(.*?)#", "#", changelog, flags=re.DOTALL)

    # first heading
    changelog = re.sub(r"^# History of changes$", "", changelog, flags=re.MULTILINE | re.IGNORECASE)

    changelog = re.sub(r"^## (?:v|version )?([0-9\.]+) (.*)$", r"- update to version \1:", changelog,
                       flags=re.MULTILINE | re.IGNORECASE)
    changelog = re.sub(r"^### (.*):?$", r" - \1:", changelog, flags=re.MULTILINE)

    # normal entries
    changelog = re.sub(r"^  (.*)$", r"    \1", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^\* (.*)$", r"  - \1", changelog, flags=re.MULTILINE)
    changelog = re.sub(r"^(\w)(.*)$", r"  - \1\2", changelog, flags=re.MULTILINE)
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
    'isort': convert_isort,
    'axel': convert_axel,
    'xonsh': convert_rst,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('style', nargs='?', default='automatic',
                        choices=tuple(STYLES.keys()) + ('automatic', ))
    parser.add_argument('-v', '--verbose', action='store_const', const=True)
    args = parser.parse_args()

    files = glob.glob("*.tar.*z")
    if not files:
        sys.exit("No *.tar.*z file found!")
    elif len(files) != 1:
        sys.exit("More than one *.tar.*z file found!")
    archivefilename = files[0]
    softwarename = archivefilename[:archivefilename.rfind('-')]
    if softwarename.startswith('python-'):
        softwarename = softwarename[7:]
    if select.select([sys.stdin,],[],[],0.0)[0]:  # stdin
        archivefilename = "<stdin>"

    files = glob.glob("*.changes")
    if not files:
        sys.exit("No *.changes.* file found!")
    elif len(files) > 1:
        sys.exit("More than one *.changes.* file found!")
    changesfilename = files[0]

    print("Found %r and %r of %s." % (archivefilename, changesfilename, softwarename), file=sys.stderr)

    with open(changesfilename) as changes:
        while True:
            line = changes.readline()
            previous_version = re.search('[0-9]+\.[0-9]+(\.[0-9]+)?', line)
            if line.startswith ('- update') and previous_version:
                previous_version = previous_version[0]
                break
        print("Found previous version %s" % previous_version, file=sys.stderr)

    if archivefilename != '<stdin>':
        with tarfile.open(archivefilename, 'r') as archive:
            # find the changelog file with the smallest number of slashes in it's path
            candidates = list(filter(lambda filename: re.search('(changes|changelog|history|whats.new)[^/]*', filename, flags=re.IGNORECASE), archive.getnames()))
            if not candidates:
                sys.exit('Found no changelog in archive :/')
            if args.verbose:
                print('Changelog candidates:\n*', '\n* '.join(candidates), file=sys.stderr)
            number_of_slashes = [filename.count('/') for filename in candidates]
            smallest = min(number_of_slashes)
            candidate = list(candidates)[list(number_of_slashes).index(smallest)]
            print("Found changelog file %r." % candidate, file=sys.stderr)
            changelog = archive.extractfile(candidate).read().decode()
    else:
        changelog = sys.stdin.read()

    if args.style == 'automatic':
        if changesfilename.endswith('debian/changelog'):
            args.style = 'debian'
        elif softwarename in STYLES:
            args.style = softwarename
        elif candidate.endswith('.rst'):
            args.style = 'rst'
        elif candidate.endswith('.md'):
            args.style = 'markdown'
        else:
            exit('Could not determine which conversion to use.')
        print('Using autodetected style %r' % args.style, file=sys.stderr)

    changelog = convert_base(changelog, softwarename)
    changelog = STYLES[args.style](changelog)
    changelog = convert_base_after(changelog, previous_version)
    try:
        print(changelog)
    except BrokenPipeError:
        pass


if __name__ == '__main__':
    main()
