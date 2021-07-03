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

Configuration
-------------

Some scripts require a configuration. The file used is `.config/packaging_utils.ini`.
