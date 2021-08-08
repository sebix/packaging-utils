# -*- coding: utf-8 -*-
import unittest
from packaging_utils.changelog_extractor.changelog_extractor import convert_base, convert_base_after, convert_confluence

workrave = """
Workrave NEWS -- history of user-visible changes. 03 August 2021
Copyright (C) 2001-2020 Rob Caelers, Raymond Penners, Ray Satiro
See the end for copying conditions.

Please report Workrave bug reports. Visit our bug tracker located at:
https://github.com/rcaelers/workrave/issues

* Workrave 1.10.48

** Fixed GNOME Shell applet on Ubuntu 18.04 (#281)

* Workrave 1.10.47

** Fixed a crash of the GNOME Shell applet (#281)
** Adds support for GNOME Shell 40 (#288)
** Fixed issue where the installer would fail when installing as system user
   (#291)
** Fixed incorrect disabling of postpone/skip button (#301)
** Warn if operation mode is not 'normal' after unlocking the screen (Windows
   only for now)
""".strip()
workrave_expected = """
- update to version 1.10.48:
 - Fixed GNOME Shell applet on Ubuntu 18.04 (#281)
- update to version 1.10.47:
 - Fixed a crash of the GNOME Shell applet (#281)
 - Adds support for GNOME Shell 40 (#288)
 - Fixed issue where the installer would fail when installing as system user
   (#291)
 - Fixed incorrect disabling of postpone/skip button (#301)
 - Warn if operation mode is not 'normal' after unlocking the screen (Windows
   only for now)
""".strip()


class TextConfluence(unittest.TestCase):
    maxDiff = None

    def test_workrave_with_known_name(self):
        """
        Test workrave changelog with confluence syntax and no headings
        """
        self.assertEqual(convert_base_after(convert_confluence(convert_base(workrave, 'workrave'), softwarename='workrave')),
                         workrave_expected)

    def test_workrave_without_known_name(self):
        """
        Test workrave changelog with confluence syntax and no headings
        """
        self.assertEqual(convert_base_after(convert_confluence(convert_base(workrave, 'workrave'))),
                         workrave_expected)
