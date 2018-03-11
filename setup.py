#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as handle:
    README = handle.read()

setup(
    name='intelmq',
    version='0.1.0',
    maintainer='Sebastian Wagner',
    maintainer_email='sebix@sebix.at',
    python_requires='>=3.3',
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
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: System :: Archiving :: Packaging',
    ],
    keywords='packaging update check anitya release-monitoring opensuse',
    entry_points={
        'console_scripts': [
            'check-anitya = packaging_utils.anitya.check_anitya:main',
            'license-rewriter = packaging_utils.specfile.license_rewriter:main',
        ],
    },
)
