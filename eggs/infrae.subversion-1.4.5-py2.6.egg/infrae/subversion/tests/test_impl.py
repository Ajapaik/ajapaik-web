## -*- coding: utf-8 -*-

__author__ = "sylvain@infrae.com"
__format__ = "plaintext"
__version__ = "$Id: test_impl.py 31670 2008-10-31 10:21:14Z sylvain $"

import doctest
import os
import os.path
import sys
import unittest
from doctest import DocFileSuite

import py
import svnhelper.testing
import svnhelper.tests
import zc.buildout.testing
from svnhelper.core import helper

import infrae.subversion


def setUp(test):
    test_package = os.path.dirname(svnhelper.tests.__file__)
    test_package = os.path.join(test_package, 'tests', 'my.testing')
    tested_package = os.path.dirname(infrae.subversion.__file__)

    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install('py', test)
    zc.buildout.testing.install_develop('infrae.subversion', test)
    svnhelper.testing.setUpRepository(test)
    test.globs['init_test_package'](test_package)
    helper.import_to(test_package,
                     test.globs['repository'])
    helper.import_to(tested_package,
                     test.globs['repository'] + '/infrae.subversion/trunk/infrae.subversion')

def tearDown(test):
    svnhelper.testing.tearDownRepository(test)
    zc.buildout.testing.buildoutTearDown(test)

flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
         doctest.REPORT_ONLY_FIRST_FAILURE | doctest.REPORT_NDIFF)

def have_pysvn():
    impl = os.getenv('INFRAE_SUBVERSION_IMPL', 'PYSVN')
    if impl == 'PYSVN':
        try:
            import pysvn
            return True
        except:
            pass
    return False

def test_file(name):
    return os.path.join(os.path.dirname(__file__), name)

def test_suite():
    tests = [DocFileSuite(test_file('IMPL.txt'),
                          optionflags=flags,
                          globs=globals(),
                          setUp=setUp,
                          tearDown=tearDown,
                          module_relative=False)]
    if have_pysvn():
        tests += [DocFileSuite(test_file('EXPORT.txt'),
                               optionflags=flags,
                               globs=globals(),
                               setUp=setUp,
                               tearDown=tearDown,
                               module_relative=False)]
    return unittest.TestSuite(tests)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
