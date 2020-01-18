# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 21:11:40 2019

@author: sebix@sebix.at
"""

import unittest
from packaging_utils.changelog_extractor.changelog_extractor import convert_misp

misp_original = """
Changelog
=========


v2.4.111.2 (2019-07-22)
-----------------------

New
~~~
- [Sightings] Delete method. [Raphaël Vinot]

  Fix #230
- [tests] non-exportable tags. [Raphaël Vinot]
"""

misp_expected = """
Changelog
=========


v2.4.111.2 (2019-07-22)
-----------------------
 - New
  - [Sightings] Delete method. [Raphaël Vinot]

    Fix #230
  - [tests] non-exportable tags. [Raphaël Vinot]
"""


class TextMisp(unittest.TestCase):
    maxDiff = None
    def test_conversion(self):
        self.assertEqual(convert_misp(misp_original, with_markdown=False),
                         misp_expected)
