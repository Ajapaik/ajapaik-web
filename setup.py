#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name = "RePhoto",
    version = "1.0",
    url = '',
    license = 'BSD',
    description = "",
    author = '',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
)
