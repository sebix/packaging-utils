#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 13:11:15 2019

@author: ele
"""

import unittest
from packaging_utils.changelog_extractor.changelog_extractor import convert_base, convert_base_after, convert_markdown

shodan_original = """
CHANGELOG
=========

1.14.0
----------
* New command **shodan version** (#104).
* Only change api_key file permissions if needed (#103)

1.13.0
------
* New command **shodan domain** to lookup a domain in Shodan's DNS database
* Override environment configured settings if explicit proxy settings are supplied (@cudeso)

1.12.1
------
* Fix Excel file conversion that resulted in empty .xlsx files

1.12.0
------
* Add new methods to ignore/ unignore trigger notifications
"""

shodan_expected = """
- update to version 1.14.0:
 - New command **shodan version** (#104).
 - Only change api_key file permissions if needed (#103)
""".strip()


passivetotal = """
## v2.5.1

#### Enhancements

- Adds support for the Illuminate CTI module with Intel Profile API library
  calls and `analzyer` objects. Includes support for all API parameters and
  handles pagination automatically.

#### Bug Fixes

- Filter methods on RecordList objects now consistently return lists instead of
  filters.


## v2.5.0

#### Enhancements:

- Raise `AnalyzerAPIError` when a non-200 response is returned from the API.
""".strip()
passivetotal_expected = """
- update to version 2.5.1:
 - Enhancements:
  - Adds support for the Illuminate CTI module with Intel Profile API library
    calls and `analzyer` objects. Includes support for all API parameters and
    handles pagination automatically.
 - Bug Fixes:
  - Filter methods on RecordList objects now consistently return lists instead of
    filters.
- update to version 2.5.0:
 - Enhancements:
  - Raise `AnalyzerAPIError` when a non-200 response is returned from the API.
""".strip()


class TextMd(unittest.TestCase):
    maxDiff = None

    def test_shodan(self):
        self.assertEqual(convert_base_after(convert_markdown(convert_base(shodan_original,
                                                             'shodan')),
                                            '1.13.0'),
                         shodan_expected)

    def test_passivetotal(self):
        """
        passivetotal has weird sectioning, skipping ###, let's just live with that.
        Also, one time the section header has a trainling comma, the other has not.
        """
        self.assertEqual(convert_base_after(convert_markdown(passivetotal)),
                         passivetotal_expected)
