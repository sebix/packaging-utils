#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the xarray changelog conversion
"""

import unittest
from packaging_utils.changelog_extractor.changelog_extractor import convert_base, convert_base_after, convert_rst

xarray_original = """
.. currentmodule:: xarray

What's New
==========

.. ipython:: python
   :suppress:

    import numpy as np
    np.random.seed(123456)

.. _whats-new.0.12.2:

v0.12.2 (29 June 2019)
----------------------

New functions/methods
~~~~~~~~~~~~~~~~~~~~~

- Two new functions, :py:func:`~xarray.combine_nested` and
  :py:func:`~xarray.combine_by_coords`, allow for combining datasets along any
  number of dimensions, instead of the one-dimensional list of datasets
  supported by :py:func:`~xarray.concat`.

- Something else

Enhancements to existing functionality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Add ``keepdims`` argument for reduce operations (:issue:`2170`)
  By `Scott Wales <https://github.com/ScottWales>`_.
- Enable ``@`` operator for DataArray. This is equivalent to :py:meth:`DataArray.dot`
  By `Maximilian Roos <https://github.com/max-sixty>`_.

IO related enhancements
~~~~~~~~~~~~~~~~~~~~~~~

- Implement :py:func:`~xarray.load_dataset` and

Bug fixes
~~~~~~~~~

- Rolling operations on xarray objects containing dask arrays could silently
- Don't set encoding attributes on bounds variables when writing to netCDF.
  By `Deepak Cherian <https://github.com/dcherian>`_.

.. _whats-new.0.12.1:

v0.12.1 (4 April 2019)
----------------------

Enhancements
~~~~~~~~~~~~

- Allow ``expand_dims`` method to support inserting/broadcasting dimensions

Bug fixes
~~~~~~~~~

- Dataset.copy(deep=True) now creates a deep copy of the attrs (:issue:`2835`).
  By `Andras Gefferth <https://github.com/kefirbandi>`_.
"""

xarray_expected = """
- update to version 0.12.2:
 - New functions/methods:
  - Two new functions, :py:func:`~xarray.combine_nested` and
    :py:func:`~xarray.combine_by_coords`, allow for combining datasets along any
    number of dimensions, instead of the one-dimensional list of datasets
    supported by :py:func:`~xarray.concat`.
  - Something else
 - Enhancements to existing functionality:
  - Add ``keepdims`` argument for reduce operations (:issue:`2170`)
    By `Scott Wales <https://github.com/ScottWales>`_.
  - Enable ``@`` operator for DataArray. This is equivalent to :py:meth:`DataArray.dot`
    By `Maximilian Roos <https://github.com/max-sixty>`_.
 - IO related enhancements:
  - Implement :py:func:`~xarray.load_dataset` and
 - Bug fixes:
  - Rolling operations on xarray objects containing dask arrays could silently
  - Don't set encoding attributes on bounds variables when writing to netCDF.
    By `Deepak Cherian <https://github.com/dcherian>`_.
- update to version 0.12.1:
 - Enhancements:
  - Allow ``expand_dims`` method to support inserting/broadcasting dimensions
 - Bug fixes:
  - Dataset.copy(deep=True) now creates a deep copy of the attrs (:issue:`2835`).
    By `Andras Gefferth <https://github.com/kefirbandi>`_.
""".strip()

expected = """

""".strip()

class TextXarray(unittest.TestCase):
    def test_conversion(self):
        self.assertEqual(convert_base_after(convert_rst(convert_base(xarray_original,
                                                                     'xarray')),
                                            '0.12.0'),
                         xarray_expected)