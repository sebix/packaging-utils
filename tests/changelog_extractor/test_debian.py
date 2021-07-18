"""
Test debian changelog parsing
"""

import unittest
from packaging_utils.changelog_extractor.changelog_extractor import convert_debian, convert_base, convert_base_after


diffoscope = """
diffoscope (178) unstable; urgency=medium

  [ Chris Lamb ]
  * Don't traceback on an broken symlink in a directory.
    (Closes: reproducible-builds/diffoscope#269)

  [ Balint Reczey ]
  * Support .deb package members compressed with the Zstandard algorithm.
    (LP: #1923845)

 -- Chris Lamb <lamby@debian.org>  Fri, 16 Jul 2021 15:37:59 +0100

diffoscope (177) unstable; urgency=medium

  [ Keith Smiley ]
  * Improve support for Apple "provisioning profiles".
  * Fix ignoring objdump tests on MacOS.

 -- Chris Lamb <lamby@debian.org>  Fri, 04 Jun 2021 10:03:04 +0100
""".strip()
diffoscope_expected = """
- update to version 178:
 - Don't traceback on an broken symlink in a directory.
   (Closes: reproducible-builds/diffoscope#269)
 - Support .deb package members compressed with the Zstandard algorithm.
   (LP: #1923845)
- update to version 177:
 - Improve support for Apple "provisioning profiles".
 - Fix ignoring objdump tests on MacOS.
""".strip()


class TestDebianConversion(unittest.TestCase):
    maxDiff = None
    def test_diffoscope(self):
        self.assertEqual(convert_base_after(convert_debian(convert_base(diffoscope))),
                         diffoscope_expected)
