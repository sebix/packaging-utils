#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Test the base conversion
"""

import unittest
from packaging_utils.changelog_extractor.changelog_extractor import convert_base


history_header = """
=======
History
=======
""".strip()


class TextBase(unittest.TestCase):
    def test_history_header(self):
        self.assertEqual(convert_base(history_header), '')
