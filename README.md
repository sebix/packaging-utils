Packaging utils
===============

A bunch of scripts I use for keeping track of packages I maintain and for work with rpm dependency trees.

They currently release on openSUSE, but feel free to adapt them to you OS or even open pull requests!

Tools
-----

* `check_anitya`: Checks latest version on anitya and compares it with locally available version.
* `license_rewriter`: Rewrites specfiles to use %license macro.
* `branch-and-fix-license`: Branches a package at the open build services, fixes %license and submits the packages
* `changelog_extractor`: Extracts the changelog from a file in an archive, shows the changes sinnce the last version found in the changes file and converts it to the rpm format
