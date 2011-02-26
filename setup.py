from setuptools import setup, find_packages

setup(
    name = "project",
    version = "1.0",
    url = 'http://github.com/jacobian/django-shorturls',
    license = 'BSD',
    description = "A base project.",
    author = 'Kristjan Heinaste',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
)