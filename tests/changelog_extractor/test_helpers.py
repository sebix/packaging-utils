import io
import unittest
from packaging_utils.changelog_extractor.helpers import detect_previous_version


class TestDetectPreviousVersion(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(detect_previous_version(io.StringIO('- update to version 1.0:')),
                         '1.0')

    def test_whitespace_prefix(self):
        self.assertEqual(detect_previous_version(io.StringIO('-  update to version 1.0:')),
                         '1.0')

    def test_missing_colon(self):
        self.assertEqual(detect_previous_version(io.StringIO('- update to version 1.0')),
                         '1.0')
