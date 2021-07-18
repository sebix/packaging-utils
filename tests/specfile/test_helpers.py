"""
test specfile helpers
"""
import unittest
from pathlib import Path
from packaging_utils.specfile import helpers


class TestSpecfileHelpers(unittest.TestCase):
    def test_source_filenames_diffoscope(self):
        source_path = Path(__file__).parent / 'diffoscope.spec'
        self.assertListEqual(
            helpers.get_source_filename(str(source_path)),
            ['diffoscope-177.tar.bz2', 'diffoscope-177.tar.bz2.asc'])

    def test_source_urls_diffoscope(self):
        source_path = Path(__file__).parent / 'diffoscope.spec'
        self.assertEqual(
            helpers.get_source_urls(str(source_path)),
            ['https://diffoscope.org/archive/diffoscope-177.tar.bz2',
             'https://diffoscope.org/archive/diffoscope-177.tar.bz2.asc'])
