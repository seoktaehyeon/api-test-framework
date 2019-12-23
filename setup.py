#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup
import os


URL = 'https://github.com/seoktaehyeon/api-test-framework'
NAME = 'ApiTestFramework'
VERSION = '0.1.2'
DESCRIPTION = 'Api test framework in Linux'
if os.path.exists('README.md'):
    with open('README.md', encoding='utf-8') as f:
        LONG_DESCRIPTION = f.read()
else:
    LONG_DESCRIPTION = DESCRIPTION
AUTHOR = 'Will'
AUTHOR_EMAIL = 'v.stone@163.com'
LICENSE = 'MIT'
PLATFORMS = [
    'linux',
]
REQUIRES = [
    'PyYAML>=5.2',
    'requests>=2.22.0',
    'pytest>=5.3.2',
    'pytest-html>=2.0.1',
]
CONSOLE_SCRIPT = 'atf-exec=ApiTestFramework.atf_exec:main'

setup(
    name=NAME,
    version=VERSION,
    description=(
        DESCRIPTION
    ),
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    license=LICENSE,
    packages=find_packages(),
    platforms=PLATFORMS,
    url=URL,
    install_requires=REQUIRES,
    entry_points={
        'console_scripts': [CONSOLE_SCRIPT],
    }
)

