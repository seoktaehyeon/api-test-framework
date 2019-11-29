#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup
import os
import shutil


setup(
    name='ApiTestFramework',
    version='0.1',
    packages=find_packages(),
)

local_path = os.path.join('.', 'atf-exec')
bin_path = os.path.join('/', 'usr', 'local', 'bin', 'atf-exec')
shutil.copyfile(local_path, bin_path)
os.system('chmod +x %s' % bin_path)
