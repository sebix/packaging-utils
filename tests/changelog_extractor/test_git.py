#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 20:41:24 2019

@author: ele
"""
import unittest
from packaging_utils.changelog_extractor.changelog_extractor import convert_base, convert_base_after, convert_git

git_original = """
commit 9fd935c5f7a0c96d3eabf37459ebfd60dff7aad5
Author: Thomas Dreibholz <dreibh@simula.no>
Date:   Wed Aug 14 15:31:42 2019 +0200

    Removed FreeBSD dependency on GeoIP, since it is not available any more.

commit 9f0577366bbc79b43cba918501a7acfa7b4569cc
Author: Thomas Dreibholz <dreibh@simula.no>
Date:   Wed Aug 14 15:30:52 2019 +0200

    CMakeLists.txt for FreeBSD builds.
    
    And some more text
    Third line

commit 2eca6eb3a08f107195e71affd858148f49a64cac
Merge: a144888 31a8c60
Author: Thomas Dreibholz <dreibh@simula.no>
Date:   Wed Aug 14 14:04:23 2019 +0200

    Merge branch 'master' of github.com:dreibh/subnetcalc

commit e31c3f081e7f2c59fb30561193277ecb431b58a9
Author: Thomas Dreibholz <dreibh@simula.no>
Date:   Wed Aug 7 17:41:09 2019 +0200

    New release subnetcalc-2.4.13.

commit 7f7cce13aa0f6fe1575c18a08962f8a69ae760d9
Author: Thomas Dreibholz <dreibh@simula.no>
Date:   Fri Jul 26 09:37:25 2019 +0200

    New release subnetcalc-2.4.12.

""".strip()
git_expected = """ - Removed FreeBSD dependency on GeoIP, since it is not available any more.
 - CMakeLists.txt for FreeBSD builds.
   And some more text
   Third line
- update to version 2.4.13:
- update to version 2.4.12:"""

class TextGit(unittest.TestCase):
    maxDiff = None
    def test_conversion(self):
        self.assertEqual(convert_git(convert_base(git_original,
                                                  'subnetcalc')),
                         git_expected)