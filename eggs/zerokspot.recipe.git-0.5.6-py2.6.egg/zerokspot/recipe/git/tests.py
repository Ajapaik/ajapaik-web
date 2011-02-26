from __future__ import with_statement
import unittest
import sys
import os
import tempfile
from zc.buildout import testing
import zc.buildout

FILE = os.path.abspath(__file__)

def do_buildout(buildout_file, options=None):
    if options is None:
        options = []
    build = zc.buildout.buildout.Buildout(buildout_file, options)
    build.init(None)
    build.install(None)
    return build

class UtilsTests(unittest.TestCase):
    """
    Test cases for the utility functions.
    """

    def test_repo_url(self):
        """
        Tests for get_reponame.
        """

        from zerokspot.recipe.git import get_reponame
        tests = (
                'http://domain.com/test/', 
                'http://domain.com/test.git', 
                'http://domain.com/test.git/',
                'http://domain.com/test',
                '/Users/test/repos/test'
                )
        for t in tests:
            self.assertEqual('test', get_reponame(t))

    def testBranch(self):
        """
        Test reponame with branch
        """
        from zerokspot.recipe.git import get_reponame
        self.assertEqual(
            'test@cool-feature', get_reponame('http://domain.com/test.git', 'cool-feature'))

    def testRev(self):
        """
        Test reponame with revision
        """
        from zerokspot.recipe.git import get_reponame
        self.assertEqual(
            'test@1234', get_reponame('http://domain.com/test.git', rev = '1234'))

    def testBranchAndRev(self):
        """
        Test reponame with branch and revision
        """
        from zerokspot.recipe.git import get_reponame
        self.assertEqual(
            'test@1234', get_reponame('http://domain.com/test.git', 'cool-feature', '1234'))


class RecipeTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.tempdir, 'downloads'))

        self.tempcache = tempfile.mkdtemp()
        self.temprepos = tempfile.mkdtemp()
        self.repo_name = 'testrepo'
        self.temprepo = os.path.join(self.temprepos, self.repo_name)

        testing.mkdir(self.temprepo)

        os.chdir(self.tempdir)

        testing.system('cd %s && git init' % self.temprepo)
        testing.write(self.temprepo, 'test.txt', 'TEST')
        testing.system('cd %s && git add test.txt && git commit -m "Init"' % self.temprepo)
        testing.write(self.temprepo, 'test2.txt', 'TEST')
        testing.system('cd %s && git checkout -b test && git add test2.txt && git commit -m "Test-branch" && git checkout master' % self.temprepo)

    def tearDown(self):
        testing.rmdir(self.tempdir)
        testing.rmdir(self.tempcache)
        testing.rmdir(self.temprepos)

    def _buildout(self, options=None):
        return do_buildout(os.path.join(self.tempdir, 'buildout.cfg'), options)

    def testFetch(self):
        """
        Tests if the basic cloning and updating of the repository works.
        """

        testing.write(self.tempdir, 'buildout.cfg', """
[buildout]
parts = gittest

[gittest]
recipe = zerokspot.recipe.git
repository = %(repo)s
        """ % {'repo' : self.temprepo})
        self._buildout()
        self.assertTrue(os.path.exists(os.path.join(self.tempdir, 'parts', 'gittest', 'test.txt')))
        self._buildout()

    def testRaiseExceptionOnAbsentCache(self):
        """
        install-from-cache without cache should raise an exception
        """
        testing.write(self.tempdir, 'buildout.cfg', """
[buildout]
parts = gittest
download-cache = %(cache)s
install-from-cache = true

[gittest]
recipe = zerokspot.recipe.git
repository = %(repo)s
        """ % {'repo' : self.temprepo, 'cache': self.tempcache})

        build = zc.buildout.buildout.Buildout(
                    os.path.join(self.tempdir, 'buildout.cfg'), [])
        self.assertRaises(zc.buildout.UserError, build.install, None)


    def testOffline(self):
        """
        Tests if install from the dowload-cache works.
        """
        testing.write(self.tempdir, 'buildout.cfg', """
[buildout]
parts = gittest
download-cache = %(cache)s

[gittest]
recipe = zerokspot.recipe.git
repository = %(repo)s
        """ % {'repo' : self.temprepo, 'cache': self.tempcache})

        # First install as usual
        build = self._buildout()
        self.assertFalse(build['gittest'].recipe.installed_from_cache)

        # clear buildout
        os.unlink(os.path.join(build['buildout']['directory'], '.installed.cfg'))
        testing.rmdir(build['buildout']['directory'], 'parts')

        # now install from cache
        build = self._buildout([('buildout', 'install-from-cache', 'true')])
        self.assertTrue(build['gittest'].recipe.installed_from_cache)
        build = self._buildout([('buildout', 'install-from-cache', 'true')])

    def testNonstandardBranch(self):
        """
        Tests if install from the dowload-cache works with a non-standard branch.
        """
        testing.write(self.tempdir, 'buildout.cfg', """
[buildout]
parts = gittest
download-cache = %(cache)s

[gittest]
recipe = zerokspot.recipe.git
branch = test
repository = %(repo)s
        """ % {'repo' : self.temprepo, 'cache': self.tempcache})
        build = self._buildout()
        recipe = build['gittest'].recipe
        self.assertTrue(os.path.exists(os.path.join(recipe.cache_path, 'test2.txt')))
        self.assertTrue(os.path.exists(os.path.join(recipe.options['location'], 'test2.txt')))
        self._buildout()

    def testSingleEgg(self):
        repo = os.path.join(os.path.dirname(FILE), '../../../')
        testing.write(self.tempdir, 'buildout.cfg', """
[buildout]
parts = gittest

[gittest]
recipe = zerokspot.recipe.git
repository = %(repo)s
as_egg = true
        """ % {'repo': repo})
        buildout = self._buildout()
        installs = os.listdir(buildout['buildout']['develop-eggs-directory'])
        self.assertTrue('zerokspot.recipe.git.egg-link' in installs)

class MultiEggTests(unittest.TestCase):
    def setUp(self):
        self.projectdir = tempfile.mkdtemp()
        self.temprepo = tempfile.mkdtemp()
        for i in range(2):
            base_dir = os.path.join(self.temprepo, 'project%d' % (i, ))
            testing.mkdir(base_dir)
            setup_py = '''from setuptools import setup
setup(name='project%(num)d', version='1.0', py_modules=['test'])''' % {'num': i}
            with open(os.path.join(base_dir, 'setup.py'), 'w+') as fp:
                fp.write(setup_py)
            with open(os.path.join(base_dir, 'test.py'), 'w+') as fp:
                fp.write('# Dummy module')
        testing.system('cd %s && git init && git add * && git commit -m "Test"' % self.temprepo)

    def testBasic(self):
        testing.write(self.projectdir, 'buildout.cfg', """
[buildout]
parts = gittest

[gittest]
recipe = zerokspot.recipe.git
repository = %(repo)s
as_egg = true
paths = 
    project0
    project1
""" % {'repo': self.temprepo})
        buildout = do_buildout(os.path.join(self.projectdir, 'buildout.cfg'))
        installs = os.listdir(buildout['buildout']['develop-eggs-directory'])
        self.assertTrue('project0.egg-link' in installs)
        self.assertTrue('project1.egg-link' in installs)

    def tearDown(self):
        testing.rmdir(self.temprepo)
        testing.rmdir(self.projectdir)

if __name__ == '__main__':
    sys.path.insert(0,  os.path.normpath(
                            os.path.join(
                                os.path.dirname(__file__) or os.getcwd(),
                                '../../../'
                            )))
    unittest.main()
