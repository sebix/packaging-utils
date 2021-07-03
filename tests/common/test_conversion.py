import unittest

from packaging_utils.common.conversion import Version


class TestVersion(unittest.TestCase):
    def test_alpha_only(self):
        self.assertIsNone(Version('disable-globalcfg'))

    def test_normal(self):
        self.assertEqual(Version('1.2.3'), (1, 2, 3))

    def test_postfixes(self):
        self.assertEqual(Version('1.0.0-rc1'), (1, 0, 0, 'rc1'))
        self.assertEqual(Version('0.4~alpha3'), (0, 4, 'alpha3'))
#        self.assertEqual(Version('1.5.0alpha'), (1, 5, 0, 'alpha'))

    def test_version_prefix(self):
        self.assertEqual(Version('v1'), (1, ))
        self.assertEqual(Version('v-1'), (1, ))
