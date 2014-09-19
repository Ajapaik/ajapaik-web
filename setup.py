#!/usr/bin/env python
from setuptools import setup, find_packages

#May need this fix: https://github.com/buildout/buildout/issues/130

setup(
    name="project",
    version="1.0",
    url='',
    license='BSD',
    description="",
    author='',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['setuptools'],
)