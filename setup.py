#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from canarieapi import __version__, __author__, __email__

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
    version=__version__,
    description="CanarieAPI is a REST service for self-describing Canarie services and platforms",
    long_description=README + '\n\n' + HISTORY,
    author=__author__,
    author_email=__email__,
    url='https://github.com/Ouranosinc/CanarieAPI',
    platforms=['linux_x86_64'],
    license="ISCL",
    keywords='CanarieAPI',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    # -- Package structure -------------------------------------------------
    packages=find_packages(),
    package_dir={'canarieapi':
                 'canarieapi'},
    include_package_data=True,
    install_requires=REQUIREMENTS,
    zip_safe=False,

    # -- self - tests --------------------------------------------------------
    test_suite='tests',
    tests_require=TEST_REQUIREMENTS,
)
