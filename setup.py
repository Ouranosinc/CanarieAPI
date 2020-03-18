#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from setuptools import find_packages
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

ROOT_DIR = os.path.dirname(__file__)
PKG_NAME = 'canarieapi'
PKG_DIR = os.path.join(ROOT_DIR, PKG_NAME)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, PKG_DIR)
import __meta__  # noqa

with open('README.rst') as readme_file:
    README = readme_file.read()

with open('HISTORY.rst') as history_file:
    HISTORY = history_file.read().replace('.. :changelog:', '')

REQUIREMENTS = [
    "flask",
]

TEST_REQUIREMENTS = [
    'nose',
    # TODO: put package test requirements here
]

setup(
    # -- meta information --------------------------------------------------
    name='CanarieAPI',
    version=__meta__.__version__,
    description=__meta__.__description__,
    long_description=README + '\n\n' + HISTORY,
    author=__meta__.__author__,
    author_email=__meta__.__email__,
    url='https://github.com/Ouranosinc/CanarieAPI',
    platforms=['linux_x86_64'],
    license="ISCL",
    keywords='CanarieAPI',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    # -- Package structure -------------------------------------------------
    packages=find_packages(),
    package_dir={PKG_NAME: PKG_NAME},
    include_package_data=True,
    install_requires=REQUIREMENTS,
    zip_safe=False,

    # -- self - tests --------------------------------------------------------
    test_suite='tests',
    tests_require=TEST_REQUIREMENTS,
)
