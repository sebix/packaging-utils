Packaging utils
===============

A bunch of scripts I use for keeping track of packages I maintain and for work with rpm dependency trees.

Some of them are focused on openSUSE, but feel free to adapt them to you OS or even open pull requests!

Tools
-----

* `check_anitya`: Checks latest version on anitya and compares it with locally available version.
* `license_rewriter`: Rewrites RPM specfiles to use %license macro (not needed anymore).
* `branch-and-fix-license`: Branches a package at the OpenBuildService, fixes %license and submits the packages (not needed anymore).
* `changelog_extractor`: Extracts the changelog from a file in an archive, shows the changes sinnce the last version found in the changes file and converts it to the RPM changelog format.
* `librariesio-latest-version`: Retrieves the latest version from libraries.io (currently only PyPI is supported) for the given software. The name of the software can be detected from the current working directory.
* `specfile-version-updater`: Updates the version in the spec file, remove the old tarball and add the new one.
* `update-packages`: If called with the name of a package, it searches for it in `$PACKAGING_DIR` (defaults to `~/packaging/`), excluding `home:*`-directories, calls `specfile-version-updater`, tries to build it, calls `changelog-extractor`, applies it, and commits the updated package.

Configuration
-------------

Some scripts require a configuration. The file used is `.config/packaging_utils.ini`.

### For `librariesio-latest-version` / `specfile-version-updater`

You can get your API key here: https://libraries.io/account

```ini
[libraries.io]
api_key = INSERT API KEY HERE
```
