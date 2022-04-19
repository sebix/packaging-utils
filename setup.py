#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as handle:
    README = handle.read()

setup(
    name='packaging_utils',
    version='0.2.0',
    maintainer='Sebastian Wagner',
    maintainer_email='sebix@sebix.at',
    python_requires='>=3.6',
    install_requires=['requests'],
    packages=find_packages(),
    license='ISC',
    description='My packaging utilites.',
    long_description=README,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: System :: Archiving :: Packaging',
    ],
    keywords='packaging update check anitya release-monitoring opensuse',
    entry_points={
        'console_scripts': [
            'check-anitya = packaging_utils.anitya.check_anitya:main',
            'license-rewriter = packaging_utils.specfile.license_rewriter:main',
            'changelog-extractor= packaging_utils.changelog_extractor.changelog_extractor:main',
            'librariesio-latest-version = packaging_utils.librariesio.get_latest_version:main',
            'specfile-version-updater = packaging_utils.specfile.version_updater:main',
        ],
    },
    scripts=[
        'scripts/branch-and-fix-license.sh',
        'scripts/update-packages.sh',
    ],
    test_suite='tests',
)
