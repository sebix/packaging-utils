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

time_machine = """
=======
History
=======

2.2.0 (2021-07-02)
------------------

* Include type hints.

* Convert C module to use PEP 489 multi-phase extension module initialization.
  This makes the module ready for Python sub-interpreters.

* Release now includes a universal2 wheel for Python 3.9 on macOS, to work on
  Apple Silicon.

* Stop distributing tests to reduce package size. Tests are not intended to be
  run outside of the tox setup in the repository. Repackagers can use GitHub's
  tarballs per tag.

2.1.0 (2021-02-19)
------------------

* Release now includes wheels for ARM on Linux.
""".strip()

time_machine_expected = """
- update to version 2.2.0:
 - Include type hints.
 - Convert C module to use PEP 489 multi-phase extension module initialization.
   This makes the module ready for Python sub-interpreters.
 - Release now includes a universal2 wheel for Python 3.9 on macOS, to work on
   Apple Silicon.
 - Stop distributing tests to reduce package size. Tests are not intended to be
   run outside of the tox setup in the repository. Repackagers can use GitHub's
   tarballs per tag.
""".strip()

geoip2 = """
.. :changelog:

History
-------

4.4.0 (2021-09-24)
++++++++++++++++++

* The public API on ``geoip2.database`` is now explicitly defined by
  setting ``__all__``.
* The return type of the ``metadata()`` method on ``Reader`` is now
  ``maxminddb.reader.Metadata`` rather than a union type.

4.3.0 (2021-09-20)
++++++++++++++++++

* Previously, the ``py.typed`` file was not being added to the source
  distribution. It is now explicitly specified in the manifest.
* The type hints for the database file in the ``Reader`` constructor have
  been expanded to match those specified by ``maxmindb.open_database``. In
  particular, ``os.PathLike`` and ``IO`` have been added.
* Corrected the type hint for the ``metadata()`` method on ``Reader``. It
  will return a ``maxminddb.extension.Metadata`` if the C extension is being
  used.
""".strip()
geoip2_expected = """
- update to version 4.4.0:
 - The public API on ``geoip2.database`` is now explicitly defined by
   setting ``__all__``.
 - The return type of the ``metadata()`` method on ``Reader`` is now
   ``maxminddb.reader.Metadata`` rather than a union type.
- update to version 4.3.0:
 - Previously, the ``py.typed`` file was not being added to the source
   distribution. It is now explicitly specified in the manifest.
 - The type hints for the database file in the ``Reader`` constructor have
   been expanded to match those specified by ``maxmindb.open_database``. In
   particular, ``os.PathLike`` and ``IO`` have been added.
 - Corrected the type hint for the ``metadata()`` method on ``Reader``. It
   will return a ``maxminddb.extension.Metadata`` if the C extension is being
   used.
""".strip()


class TextRst(unittest.TestCase):
    maxDiff = None

    def test_xarray(self):
        self.assertEqual(convert_base_after(convert_rst(convert_base(xarray_original,
                                                                     'xarray')),
                                            '0.12.0'),
                         xarray_expected)

    def test_time_machine(self):
        self.assertEqual(convert_base_after(convert_rst(convert_base(time_machine,
                                                                     'time-machine')),
                                            '2.1.0'),
                         time_machine_expected)

    def test_geoip2(self):
        self.assertEqual(convert_base_after(convert_rst(convert_base(geoip2)),
                                            '4.2.0'),
                         geoip2_expected)
