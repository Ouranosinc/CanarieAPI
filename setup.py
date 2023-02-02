#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import sys
from distutils.version import LooseVersion

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    # typing only available builtin starting with Python3
    # cannot employ it during setup, but will be installed afterwards with backport
    from typing import TYPE_CHECKING  # noqa
    if TYPE_CHECKING:
        # pylint: disable=W0611,unused-import
        from typing import Iterable, Set, Tuple, Union  # noqa: F401
except ImportError:
    pass

ROOT_DIR = os.path.dirname(__file__)
PKG_NAME = "canarieapi"
PKG_DIR = os.path.join(ROOT_DIR, PKG_NAME)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, PKG_DIR)
# do not use "from canarieapi" to avoid import error on not yet installed packages
import __meta__  # isort:skip # noqa: E402

LOGGER = logging.getLogger("{}.setup".format(PKG_NAME))
if logging.StreamHandler not in LOGGER.handlers:
    LOGGER.addHandler(logging.StreamHandler(sys.stdout))  # type: ignore # noqa
LOGGER.setLevel(logging.INFO)
LOGGER.info("starting setup")


with open("README.rst", mode="r", encoding="utf-8") as readme_file:
    README = readme_file.read()

with open("CHANGES.rst", mode="r", encoding="utf-8") as changes_file:
    CHANGES = changes_file.read().replace(".. :changelog:", "")


def _split_requirement(requirement, version=False, python=False, merge=False):
    # type: (str, bool, bool, bool) -> Union[str, Tuple[str, str]]
    """
    Splits a requirement package definition into it's name and version specification.

    Returns the appropriate part(s) according to :paramref:`version`. If ``True``, returns the operator and version
    string. The returned version in this case would be either the package's or the environment python's version string
    according to the value of :paramref:`python`. Otherwise, only returns the 'other part' of the requirement, which
    will be the plain package name without version or the complete ``package+version`` without ``python_version`` part.

    Package requirement format::

        package [<|<=|==|>|>=|!= x.y.z][; python_version <|<=|==|>|>=|!= "x.y.z"]

    Returned values with provided arguments::

        default:                                "<package>"
        python=True                             n/a
        version=True:                           ([pkg-op], [pkg-ver])
        version=True,python=True:               ([py-op], [py-ver])
        version=True,merge=True:                "<package> [pkg-op] [pkg-ver]"
        version=True,python=True,merge=True:    "[python_version] [py-op] [py-ver]"

    :param requirement: full package string requirement.
    :param version:
        Retrieves the version operator and version number instead of only the package's name (without specifications).
    :param python:
        Retrieves the python operator and python version instead of the package's version.
        Must be combined with :paramref:`version`, otherwise doesn't do anything.
    :param merge:
        Nothing done if ``False`` (other arguments behave normally).
        If only :paramref:`version` is ``True``, merges the package name back with the version operator and number into
        a single string (if any version part), but without the python version part (if any).
        If both :paramref:`version` and :paramref:`python` are ``True`` combines back the part after ``;`` to form
        the python version specifier.
    :return: Extracted requirement part(s). Emtpy strings if parts cannot be found.
    """
    idx_pyv = -1 if python else 0
    if python and "python_version" not in requirement:
        return ("", "") if version and not merge else ""
    requirement = requirement.split("python_version")[idx_pyv].replace(";", "").replace("\"", "")
    requirement = requirement.split(" #")[0]    # ignore comments, space important because 'pkg#egg=' is valid
    op_str = ""
    pkg_name = requirement
    for operator in [">=", ">", "<=", "<", "!=", "==", "="]:
        if operator in requirement:
            op_str = operator
            pkg_name, requirement = requirement.split(operator, 1)
            break
    if not version:
        return pkg_name.strip()
    if op_str == "":
        pkg_name = requirement
        requirement = ""
    parts = (op_str, requirement.strip())
    if merge and python:
        return "python_version {} \"{}\"".format(parts[0], parts[1])
    if merge and version:
        return "{}{}{}".format(pkg_name, parts[0], parts[1])
    return parts


def _parse_requirements(file_path, requirements, links):
    # type: (str, Set[str], Set[str]) -> None
    """
    Parses a requirements file to extra packages and links.

    If a python version specific is present, requirements are added only if they match the current environment.

    :param file_path: file path to the requirements file.
    :param requirements: pre-initialized set in which to store extracted package requirements.
    :param links: pre-initialized set in which to store extracted link reference requirements.
    :returns: None
    """
    with open(file_path, mode="r", encoding="utf-8") as requirements_file:
        for line in requirements_file:
            # ignore empty line, comment line or reference to other requirements file (-r flag)
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            if "python_version" in line:
                operator, py_ver = _split_requirement(line, version=True, python=True)
                op_map = {
                    "==": LooseVersion(sys.version) == LooseVersion(py_ver),
                    ">=": LooseVersion(sys.version) >= LooseVersion(py_ver),
                    "<=": LooseVersion(sys.version) <= LooseVersion(py_ver),
                    "!=": LooseVersion(sys.version) != LooseVersion(py_ver),
                    ">": LooseVersion(sys.version) > LooseVersion(py_ver),
                    "<": LooseVersion(sys.version) < LooseVersion(py_ver),
                }
                # skip requirement if not fulfilling python version
                if not op_map[operator]:
                    continue
                # remove only python part if any present
                line = _split_requirement(line, version=True, merge=True)
            if "git+https" in line:
                pkg = line.split("#")[-1]
                links.add(line.strip())
                requirements.add(pkg.replace("egg=", "").rstrip())
            elif line.startswith("http"):
                links.add(line.strip())
            else:
                requirements.add(line.strip())


def _extra_requirements(base_requirements, other_requirements):
    # type: (Iterable[str], Iterable[str]) -> Set[str]
    """
    Extracts only the extra requirements not already defined within the base requirements.

    :param base_requirements: base package requirements.
    :param other_requirements: other set of requirements referring to additional dependencies.
    """
    raw_requirements = set()
    for req in base_requirements:
        raw_req = _split_requirement(req, version=True, merge=True)
        raw_requirements.add(raw_req)
    filtered_requirements = set()
    for req in other_requirements:
        raw_req = _split_requirement(req, version=True, merge=True)
        if raw_req and raw_req not in raw_requirements:
            filtered_requirements.add(req)
    return filtered_requirements


LOGGER.info("reading requirements")

# See https://github.com/pypa/pip/issues/3610
# use set to have unique packages by name
LINKS = set()
REQUIREMENTS = set()
DOCS_REQUIREMENTS = set()
TEST_REQUIREMENTS = set()
_parse_requirements("requirements.txt", REQUIREMENTS, LINKS)
_parse_requirements("requirements-doc.txt", DOCS_REQUIREMENTS, LINKS)
_parse_requirements("requirements-dev.txt", TEST_REQUIREMENTS, LINKS)
LINKS = list(LINKS)
REQUIREMENTS = list(REQUIREMENTS)
DOCS_REQUIREMENTS = list(_extra_requirements(REQUIREMENTS, DOCS_REQUIREMENTS))
TEST_REQUIREMENTS = list(_extra_requirements(REQUIREMENTS, TEST_REQUIREMENTS))

LOGGER.info("base requirements: %s", REQUIREMENTS)
LOGGER.info("docs requirements: %s", DOCS_REQUIREMENTS)
LOGGER.info("test requirements: %s", TEST_REQUIREMENTS)
LOGGER.info("link requirements: %s", LINKS)

setup(
    # -- meta information --------------------------------------------------
    name="CanarieAPI",
    version=__meta__.__version__,
    description=__meta__.__description__,
    long_description=README + "\n\n" + CHANGES,
    author=__meta__.__author__,
    author_email=__meta__.__email__,
    url="https://github.com/Ouranosinc/CanarieAPI",
    platforms=["linux_x86_64"],
    license="ISCL",
    keywords="CanarieAPI",
    python_requires=">=2.7,!=3.0,!=3.1,!=3.2,!=3.3,!=3.4,<4",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],

    # -- Package structure -------------------------------------------------
    packages=[PKG_NAME],
    package_dir={PKG_NAME: PKG_NAME},
    include_package_data=True,
    install_requires=REQUIREMENTS,
    zip_safe=False,

    # -- self - tests --------------------------------------------------------
    test_suite="tests",
    tests_require=TEST_REQUIREMENTS,
)
