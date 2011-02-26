##############################################################################
#
# Copyright (c) 2004-2009 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import doctest
from zope.testing import renormalizing
import os
import pkg_resources
import re
import shutil
import sys
import tempfile
import unittest
import zc.buildout.easy_install
import zc.buildout.testing
import zc.buildout.testselectingpython
import zipfile

os_path_sep = os.path.sep
if os_path_sep == '\\':
    os_path_sep *= 2


def develop_w_non_setuptools_setup_scripts():
    """
We should be able to deal with setup scripts that aren't setuptools based.

    >>> mkdir('foo')
    >>> write('foo', 'setup.py',
    ... '''
    ... from distutils.core import setup
    ... setup(name="foo")
    ... ''')

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = foo
    ... parts =
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/foo'

    >>> ls('develop-eggs')
    -  foo.egg-link
    -  z3c.recipe.scripts.egg-link
    -  zc.recipe.egg.egg-link

    """

def develop_verbose():
    """
We should be able to deal with setup scripts that aren't setuptools based.

    >>> mkdir('foo')
    >>> write('foo', 'setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(name="foo")
    ... ''')

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = foo
    ... parts =
    ... ''')

    >>> print system(join('bin', 'buildout')+' -vv'), # doctest: +ELLIPSIS
    Installing...
    Develop: '/sample-buildout/foo'
    ...
    Installed /sample-buildout/foo
    ...

    >>> ls('develop-eggs')
    -  foo.egg-link
    -  z3c.recipe.scripts.egg-link
    -  zc.recipe.egg.egg-link

    >>> print system(join('bin', 'buildout')+' -vvv'), # doctest: +ELLIPSIS
    Installing...
    Develop: '/sample-buildout/foo'
    in: '/sample-buildout/foo'
    ... -q develop -mxN -d /sample-buildout/develop-eggs/...


    """

def buildout_error_handling():
    r"""Buildout error handling

Asking for a section that doesn't exist, yields a missing section error:

    >>> import os
    >>> os.chdir(sample_buildout)
    >>> import zc.buildout.buildout
    >>> buildout = zc.buildout.buildout.Buildout('buildout.cfg', [])
    >>> buildout['eek']
    Traceback (most recent call last):
    ...
    MissingSection: The referenced section, 'eek', was not defined.

Asking for an option that doesn't exist, a MissingOption error is raised:

    >>> buildout['buildout']['eek']
    Traceback (most recent call last):
    ...
    MissingOption: Missing option: buildout:eek

It is an error to create a variable-reference cycle:

    >>> write(sample_buildout, 'buildout.cfg',
    ... '''
    ... [buildout]
    ... parts =
    ... x = ${buildout:y}
    ... y = ${buildout:z}
    ... z = ${buildout:x}
    ... ''')

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout')),
    ... # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
    While:
      Initializing.
      Getting section buildout.
      Initializing section buildout.
      Getting option buildout:y.
      Getting option buildout:z.
      Getting option buildout:x.
      Getting option buildout:y.
    Error: Circular reference in substitutions.

It is an error to use funny characters in variable refereces:

    >>> write(sample_buildout, 'buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = recipes
    ... parts = data_dir debug
    ... x = ${bui$ldout:y}
    ... ''')

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout')),
    While:
      Initializing.
      Getting section buildout.
      Initializing section buildout.
      Getting option buildout:x.
    Error: The section name in substitution, ${bui$ldout:y},
    has invalid characters.

    >>> write(sample_buildout, 'buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = recipes
    ... parts = data_dir debug
    ... x = ${buildout:y{z}
    ... ''')

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout')),
    While:
      Initializing.
      Getting section buildout.
      Initializing section buildout.
      Getting option buildout:x.
    Error: The option name in substitution, ${buildout:y{z},
    has invalid characters.

and too have too many or too few colons:

    >>> write(sample_buildout, 'buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = recipes
    ... parts = data_dir debug
    ... x = ${parts}
    ... ''')

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout')),
    While:
      Initializing.
      Getting section buildout.
      Initializing section buildout.
      Getting option buildout:x.
    Error: The substitution, ${parts},
    doesn't contain a colon.

    >>> write(sample_buildout, 'buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = recipes
    ... parts = data_dir debug
    ... x = ${buildout:y:z}
    ... ''')

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout')),
    While:
      Initializing.
      Getting section buildout.
      Initializing section buildout.
      Getting option buildout:x.
    Error: The substitution, ${buildout:y:z},
    has too many colons.

Al parts have to have a section:

    >>> write(sample_buildout, 'buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = x
    ... ''')

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout')),
    While:
      Installing.
      Getting section x.
    Error: The referenced section, 'x', was not defined.

and all parts have to have a specified recipe:


    >>> write(sample_buildout, 'buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = x
    ...
    ... [x]
    ... foo = 1
    ... ''')

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout')),
    While:
      Installing.
    Error: Missing option: x:recipe

"""

make_dist_that_requires_setup_py_template = """
from setuptools import setup
setup(name=%r, version=%r,
      install_requires=%r,
      )
"""

def make_dist_that_requires(dest, name, requires=[], version=1, egg=''):
    os.mkdir(os.path.join(dest, name))
    open(os.path.join(dest, name, 'setup.py'), 'w').write(
        make_dist_that_requires_setup_py_template
        % (name, version, requires)
        )

def show_who_requires_when_there_is_a_conflict():
    """
It's a pain when we require eggs that have requirements that are
incompatible. We want the error we get to tell us what is missing.

Let's make a few develop distros, some of which have incompatible
requirements.

    >>> make_dist_that_requires(sample_buildout, 'sampley',
    ...                         ['demoneeded ==1.0'])
    >>> make_dist_that_requires(sample_buildout, 'samplez',
    ...                         ['demoneeded ==1.1'])

Now, let's create a buildout that requires y and z:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = eggs
    ... develop = sampley samplez
    ... find-links = %(link_server)s
    ...
    ... [eggs]
    ... recipe = zc.recipe.egg
    ... eggs = sampley
    ...        samplez
    ... ''' % globals())

    >>> print system(buildout),
    Develop: '/sample-buildout/sampley'
    Develop: '/sample-buildout/samplez'
    Installing eggs.
    Getting distribution for 'demoneeded==1.1'.
    Got demoneeded 1.1.
    While:
      Installing eggs.
    Error: There is a version conflict.
    We already have: demoneeded 1.1
    but sampley 1 requires 'demoneeded==1.0'.

Here, we see that sampley required an older version of demoneeded. What
if we hadn't required sampley ourselves:

    >>> make_dist_that_requires(sample_buildout, 'samplea', ['sampleb'])
    >>> make_dist_that_requires(sample_buildout, 'sampleb',
    ...                         ['sampley', 'samplea'])
    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = eggs
    ... develop = sampley samplez samplea sampleb
    ... find-links = %(link_server)s
    ...
    ... [eggs]
    ... recipe = zc.recipe.egg
    ... eggs = samplea
    ...        samplez
    ... ''' % globals())

If we use the verbose switch, we can see where requirements are coming from:

    >>> print system(buildout+' -v'), # doctest: +ELLIPSIS
    Installing 'zc.buildout', 'setuptools'.
    We have a develop egg: zc.buildout 1.0.0
    We have the best distribution that satisfies 'setuptools'.
    Picked: setuptools = 0.6
    Develop: '/sample-buildout/sampley'
    Develop: '/sample-buildout/samplez'
    Develop: '/sample-buildout/samplea'
    Develop: '/sample-buildout/sampleb'
    ...Installing eggs.
    Installing 'samplea', 'samplez'.
    We have a develop egg: samplea 1
    We have a develop egg: samplez 1
    Getting required 'demoneeded==1.1'
      required by samplez 1.
    We have the distribution that satisfies 'demoneeded==1.1'.
    Getting required 'sampleb'
      required by samplea 1.
    We have a develop egg: sampleb 1
    Getting required 'sampley'
      required by sampleb 1.
    We have a develop egg: sampley 1
    While:
      Installing eggs.
    Error: There is a version conflict.
    We already have: demoneeded 1.1
    but sampley 1 requires 'demoneeded==1.0'.
    """

def show_who_requires_missing_distributions():
    """

When working with a lot of eggs, which require eggs recursively, it can
be hard to tell why we're requiring things we can't find. Fortunately,
buildout will tell us who's asking for something that we can't find.

    >>> make_dist_that_requires(sample_buildout, 'sampley', ['demoneeded'])
    >>> make_dist_that_requires(sample_buildout, 'samplea', ['sampleb'])
    >>> make_dist_that_requires(sample_buildout, 'sampleb',
    ...                         ['sampley', 'samplea'])
    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = eggs
    ... develop = sampley samplea sampleb
    ...
    ... [eggs]
    ... recipe = zc.recipe.egg
    ... eggs = samplea
    ... ''')

    >>> print system(buildout),
    Develop: '/sample-buildout/sampley'
    Develop: '/sample-buildout/samplea'
    Develop: '/sample-buildout/sampleb'
    Installing eggs.
    Couldn't find index page for 'demoneeded' (maybe misspelled?)
    Getting distribution for 'demoneeded'.
    While:
      Installing eggs.
      Getting distribution for 'demoneeded'.
    Error: Couldn't find a distribution for 'demoneeded'.
    """

def show_eggs_from_site_packages():
    """
Sometimes you want to know what eggs are coming from site-packages.  This
might be for a diagnostic, or so that you can get a starting value for the
allowed-eggs-from-site-packages option.  The -v flag will also include this
information.

Our "py_path" has the "demoneeded," "demo"
packages available.  We'll ask for "bigdemo," which will get both of them.

Here's our set up.

    >>> py_path, site_packages_path = make_py()
    >>> create_sample_sys_install(site_packages_path)

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = eggs
    ... prefer-final = true
    ... find-links = %(link_server)s
    ...
    ... [primed_python]
    ... executable = %(py_path)s
    ...
    ... [eggs]
    ... recipe = zc.recipe.egg:eggs
    ... python = primed_python
    ... eggs = bigdemo
    ... ''' % globals())

Now here is the output.  The lines that begin with "Egg from site-packages:"
indicate the eggs from site-packages that have been selected.  You'll see
we have two: demo 0.3 and demoneeded 1.1.

    >>> print system(buildout+" -v"),
    Installing 'zc.buildout', 'setuptools'.
    We have a develop egg: zc.buildout V
    We have the best distribution that satisfies 'setuptools'.
    Picked: setuptools = V
    Installing 'zc.recipe.egg'.
    We have a develop egg: zc.recipe.egg V
    Installing eggs.
    Installing 'bigdemo'.
    We have no distributions for bigdemo that satisfies 'bigdemo'.
    Getting distribution for 'bigdemo'.
    Got bigdemo 0.1.
    Picked: bigdemo = 0.1
    Getting required 'demo'
      required by bigdemo 0.1.
    We have the best distribution that satisfies 'demo'.
    Egg from site-packages: demo 0.3
    Getting required 'demoneeded'
      required by demo 0.3.
    We have the best distribution that satisfies 'demoneeded'.
    Egg from site-packages: demoneeded 1.1
    """

def test_comparing_saved_options_with_funny_characters():
    """
If an option has newlines, extra/odd spaces or a %, we need to make sure
the comparison with the saved value works correctly.

    >>> mkdir(sample_buildout, 'recipes')
    >>> write(sample_buildout, 'recipes', 'debug.py',
    ... '''
    ... class Debug:
    ...     def __init__(self, buildout, name, options):
    ...         options['debug'] = \"\"\"  <zodb>
    ...
    ...   <filestorage>
    ...     path foo
    ...   </filestorage>
    ...
    ... </zodb>
    ...      \"\"\"
    ...         options['debug1'] = \"\"\"
    ... <zodb>
    ...
    ...   <filestorage>
    ...     path foo
    ...   </filestorage>
    ...
    ... </zodb>
    ... \"\"\"
    ...         options['debug2'] = '  x  '
    ...         options['debug3'] = '42'
    ...         options['format'] = '%3d'
    ...
    ...     def install(self):
    ...         open('t', 'w').write('t')
    ...         return 't'
    ...
    ...     update = install
    ... ''')


    >>> write(sample_buildout, 'recipes', 'setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(
    ...     name = "recipes",
    ...     entry_points = {'zc.buildout': ['default = debug:Debug']},
    ...     )
    ... ''')

    >>> write(sample_buildout, 'recipes', 'README.txt', " ")

    >>> write(sample_buildout, 'buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = recipes
    ... parts = debug
    ...
    ... [debug]
    ... recipe = recipes
    ... ''')

    >>> os.chdir(sample_buildout)
    >>> buildout = os.path.join(sample_buildout, 'bin', 'buildout')

    >>> print system(buildout),
    Develop: '/sample-buildout/recipes'
    Installing debug.

If we run the buildout again, we shoudn't get a message about
uninstalling anything because the configuration hasn't changed.

    >>> print system(buildout),
    Develop: '/sample-buildout/recipes'
    Updating debug.
"""

def finding_eggs_as_local_directories():
    r"""
It is possible to set up find-links so that we could install from
a local directory that may contained unzipped eggs.

    >>> src = tmpdir('src')
    >>> write(src, 'setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(name='demo', py_modules=[''],
    ...    zip_safe=False, version='1.0', author='bob', url='bob',
    ...    author_email='bob')
    ... ''')

    >>> write(src, 't.py', '#\n')
    >>> write(src, 'README.txt', '')
    >>> _ = system(join('bin', 'buildout')+' setup ' + src + ' bdist_egg')

Install it so it gets unzipped:

    >>> d1 = tmpdir('d1')
    >>> ws = zc.buildout.easy_install.install(
    ...     ['demo'], d1, links=[join(src, 'dist')],
    ...     )

    >>> ls(d1)
    d  demo-1.0-py2.4.egg

Then try to install it again:

    >>> d2 = tmpdir('d2')
    >>> ws = zc.buildout.easy_install.install(
    ...     ['demo'], d2, links=[d1],
    ...     )

    >>> ls(d2)
    d  demo-1.0-py2.4.egg

    """

def make_sure__get_version_works_with_2_digit_python_versions():
    """

This is a test of an internal function used by higher-level machinery.

We'll start by creating a faux 'python' that executable that prints a
2-digit version. This is a bit of a pain to do portably. :(

    >>> mkdir('demo')
    >>> write('demo', 'setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(name='demo',
    ...       entry_points = {'console_scripts': ['demo = demo:main']},
    ...       )
    ... ''')
    >>> write('demo', 'demo.py',
    ... '''
    ... def main():
    ...     print 'Python 2.5'
    ... ''')

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo
    ... parts =
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/demo'

    >>> import zc.buildout.easy_install
    >>> ws = zc.buildout.easy_install.working_set(
    ...    ['demo'], sys.executable, ['develop-eggs'])
    >>> bool(zc.buildout.easy_install.scripts(
    ...      ['demo'], ws, sys.executable, 'bin'))
    True

    >>> print system(join('bin', 'demo')),
    Python 2.5

Now, finally, let's test _get_version:

    >>> zc.buildout.easy_install._get_version(join('bin', 'demo'))
    '2.5'

    """

def create_sections_on_command_line():
    """
    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts =
    ... x = ${foo:bar}
    ... ''')

    >>> print system(buildout + ' foo:bar=1 -vv'), # doctest: +ELLIPSIS
    Installing 'zc.buildout', 'setuptools'.
    ...
    [foo]
    bar = 1
    ...

    """

def test_help():
    """
    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout')+' -h'),
    ... # doctest: +ELLIPSIS
    Usage: buildout [options] [assignments] [command [command arguments]]
    <BLANKLINE>
    Options:
    <BLANKLINE>
      -h, --help
    ...

    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout')
    ...              +' --help'),
    ... # doctest: +ELLIPSIS
    Usage: buildout [options] [assignments] [command [command arguments]]
    <BLANKLINE>
    Options:
    <BLANKLINE>
      -h, --help
    ...
    """

def test_bootstrap_with_extension():
    """
We had a problem running a bootstrap with an extension.  Let's make
sure it is fixed.  Basically, we don't load extensions when
bootstrapping.

    >>> d = tmpdir('sample-bootstrap')

    >>> write(d, 'buildout.cfg',
    ... '''
    ... [buildout]
    ... extensions = some_awsome_extension
    ... parts =
    ... ''')

    >>> os.chdir(d)
    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout')
    ...              + ' bootstrap'),
    Creating directory '/sample-bootstrap/bin'.
    Creating directory '/sample-bootstrap/parts'.
    Creating directory '/sample-bootstrap/eggs'.
    Creating directory '/sample-bootstrap/develop-eggs'.
    Generated script '/sample-bootstrap/bin/buildout'.
    """


def bug_92891_bootstrap_crashes_with_egg_recipe_in_buildout_section():
    """
    >>> d = tmpdir('sample-bootstrap')

    >>> write(d, 'buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = buildout
    ... eggs-directory = eggs
    ...
    ... [buildout]
    ... recipe = zc.recipe.egg
    ... eggs = zc.buildout
    ... scripts = buildout=buildout
    ... ''')

    >>> os.chdir(d)
    >>> print system(os.path.join(sample_buildout, 'bin', 'buildout')
    ...              + ' bootstrap'),
    Creating directory '/sample-bootstrap/bin'.
    Creating directory '/sample-bootstrap/parts'.
    Creating directory '/sample-bootstrap/eggs'.
    Creating directory '/sample-bootstrap/develop-eggs'.
    Generated script '/sample-bootstrap/bin/buildout'.

    >>> print system(os.path.join('bin', 'buildout')),
    Unused options for buildout: 'scripts' 'eggs'.

    """

def removing_eggs_from_develop_section_causes_egg_link_to_be_removed():
    '''
    >>> cd(sample_buildout)

Create a develop egg:

    >>> mkdir('foo')
    >>> write('foo', 'setup.py',
    ... """
    ... from setuptools import setup
    ... setup(name='foox')
    ... """)
    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... develop = foo
    ... parts =
    ... """)

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/foo'

    >>> ls('develop-eggs')
    -  foox.egg-link
    -  z3c.recipe.scripts.egg-link
    -  zc.recipe.egg.egg-link

Create another:

    >>> mkdir('bar')
    >>> write('bar', 'setup.py',
    ... """
    ... from setuptools import setup
    ... setup(name='fooy')
    ... """)
    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... develop = foo bar
    ... parts =
    ... """)

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/foo'
    Develop: '/sample-buildout/bar'

    >>> ls('develop-eggs')
    -  foox.egg-link
    -  fooy.egg-link
    -  z3c.recipe.scripts.egg-link
    -  zc.recipe.egg.egg-link

Remove one:

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... develop = bar
    ... parts =
    ... """)
    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/bar'

It is gone

    >>> ls('develop-eggs')
    -  fooy.egg-link
    -  z3c.recipe.scripts.egg-link
    -  zc.recipe.egg.egg-link

Remove the other:

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts =
    ... """)
    >>> print system(join('bin', 'buildout')),

All gone

    >>> ls('develop-eggs')
    -  z3c.recipe.scripts.egg-link
    -  zc.recipe.egg.egg-link
    '''


def add_setuptools_to_dependencies_when_namespace_packages():
    '''
Often, a package depends on setuptools soley by virtue of using
namespace packages. In this situation, package authors often forget to
declare setuptools as a dependency. This is a mistake, but,
unfortunately, a common one that we need to work around.  If an egg
uses namespace packages and does not include setuptools as a depenency,
we will still include setuptools in the working set.  If we see this for
a devlop egg, we will also generate a warning.

    >>> mkdir('foo')
    >>> mkdir('foo', 'src')
    >>> mkdir('foo', 'src', 'stuff')
    >>> write('foo', 'src', 'stuff', '__init__.py',
    ... """__import__('pkg_resources').declare_namespace(__name__)
    ... """)
    >>> mkdir('foo', 'src', 'stuff', 'foox')
    >>> write('foo', 'src', 'stuff', 'foox', '__init__.py', '')
    >>> write('foo', 'setup.py',
    ... """
    ... from setuptools import setup
    ... setup(name='foox',
    ...       namespace_packages = ['stuff'],
    ...       package_dir = {'': 'src'},
    ...       packages = ['stuff', 'stuff.foox'],
    ...       )
    ... """)
    >>> write('foo', 'README.txt', '')

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... develop = foo
    ... parts =
    ... """)

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/foo'

Now, if we generate a working set using the egg link, we will get a warning
and we will get setuptools included in the working set.

    >>> import logging, zope.testing.loggingsupport
    >>> handler = zope.testing.loggingsupport.InstalledHandler(
    ...        'zc.buildout.easy_install', level=logging.WARNING)
    >>> logging.getLogger('zc.buildout.easy_install').propagate = False

    >>> [dist.project_name
    ...  for dist in zc.buildout.easy_install.working_set(
    ...    ['foox'], sys.executable,
    ...    [join(sample_buildout, 'eggs'),
    ...     join(sample_buildout, 'develop-eggs'),
    ...     ])]
    ['foox', 'setuptools']

    >>> print handler
    zc.buildout.easy_install WARNING
      Develop distribution: foox 0.0.0
    uses namespace packages but the distribution does not require setuptools.

    >>> handler.clear()

On the other hand, if we have a regular egg, rather than a develop egg:

    >>> os.remove(join('develop-eggs', 'foox.egg-link'))

    >>> _ = system(join('bin', 'buildout') + ' setup foo bdist_egg -d'
    ...            + join(sample_buildout, 'eggs'))

    >>> ls('develop-eggs')
    -  z3c.recipe.scripts.egg-link
    -  zc.recipe.egg.egg-link

    >>> print 'START ->'; ls('eggs') # doctest: +ELLIPSIS
    START...
    -  foox-0.0.0-py2.4.egg
    ...

We do not get a warning, but we do get setuptools included in the working set:

    >>> [dist.project_name
    ...  for dist in zc.buildout.easy_install.working_set(
    ...    ['foox'], sys.executable,
    ...    [join(sample_buildout, 'eggs'),
    ...     join(sample_buildout, 'develop-eggs'),
    ...     ])]
    ['foox', 'setuptools']

    >>> print handler,

We get the same behavior if the it is a depedency that uses a
namespace package.


    >>> mkdir('bar')
    >>> write('bar', 'setup.py',
    ... """
    ... from setuptools import setup
    ... setup(name='bar', install_requires = ['foox'])
    ... """)
    >>> write('bar', 'README.txt', '')

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... develop = foo bar
    ... parts =
    ... """)

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/foo'
    Develop: '/sample-buildout/bar'

    >>> [dist.project_name
    ...  for dist in zc.buildout.easy_install.working_set(
    ...    ['bar'], sys.executable,
    ...    [join(sample_buildout, 'eggs'),
    ...     join(sample_buildout, 'develop-eggs'),
    ...     ])]
    ['bar', 'foox', 'setuptools']

    >>> print handler,
    zc.buildout.easy_install WARNING
      Develop distribution: foox 0.0.0
    uses namespace packages but the distribution does not require setuptools.


    >>> logging.getLogger('zc.buildout.easy_install').propagate = True
    >>> handler.uninstall()

    '''

def develop_preserves_existing_setup_cfg():
    """

See "Handling custom build options for extensions in develop eggs" in
easy_install.txt.  This will be very similar except that we'll have an
existing setup.cfg:

    >>> write(extdemo, "setup.cfg",
    ... '''
    ... # sampe cfg file
    ...
    ... [foo]
    ... bar = 1
    ...
    ... [build_ext]
    ... define = X,Y
    ... ''')

    >>> mkdir('include')
    >>> write('include', 'extdemo.h',
    ... '''
    ... #define EXTDEMO 42
    ... ''')

    >>> dest = tmpdir('dest')
    >>> zc.buildout.easy_install.develop(
    ...   extdemo, dest,
    ...   {'include-dirs': os.path.join(sample_buildout, 'include')})
    '/dest/extdemo.egg-link'

    >>> ls(dest)
    -  extdemo.egg-link

    >>> cat(extdemo, "setup.cfg")
    <BLANKLINE>
    # sampe cfg file
    <BLANKLINE>
    [foo]
    bar = 1
    <BLANKLINE>
    [build_ext]
    define = X,Y

"""

def uninstall_recipes_used_for_removal():
    """
Uninstall recipes need to be called when a part is removed too:

    >>> mkdir("recipes")
    >>> write("recipes", "setup.py",
    ... '''
    ... from setuptools import setup
    ... setup(name='recipes',
    ...       entry_points={
    ...          'zc.buildout': ["demo=demo:Install"],
    ...          'zc.buildout.uninstall': ["demo=demo:uninstall"],
    ...          })
    ... ''')

    >>> write("recipes", "demo.py",
    ... '''
    ... class Install:
    ...     def __init__(*args): pass
    ...     def install(self):
    ...         print 'installing'
    ...         return ()
    ... def uninstall(name, options): print 'uninstalling'
    ... ''')

    >>> write('buildout.cfg', '''
    ... [buildout]
    ... develop = recipes
    ... parts = demo
    ... [demo]
    ... recipe = recipes:demo
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/recipes'
    Installing demo.
    installing


    >>> write('buildout.cfg', '''
    ... [buildout]
    ... develop = recipes
    ... parts = demo
    ... [demo]
    ... recipe = recipes:demo
    ... x = 1
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/recipes'
    Uninstalling demo.
    Running uninstall recipe.
    uninstalling
    Installing demo.
    installing


    >>> write('buildout.cfg', '''
    ... [buildout]
    ... develop = recipes
    ... parts =
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/recipes'
    Uninstalling demo.
    Running uninstall recipe.
    uninstalling

"""

def extensions_installed_as_eggs_work_in_offline_mode():
    '''
    >>> mkdir('demo')

    >>> write('demo', 'demo.py',
    ... """
    ... def ext(buildout):
    ...     print 'ext', list(buildout)
    ... """)

    >>> write('demo', 'setup.py',
    ... """
    ... from setuptools import setup
    ...
    ... setup(
    ...     name = "demo",
    ...     py_modules=['demo'],
    ...     entry_points = {'zc.buildout.extension': ['ext = demo:ext']},
    ...     )
    ... """)

    >>> bdist_egg(join(sample_buildout, "demo"), sys.executable,
    ...           join(sample_buildout, "eggs"))

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... extensions = demo
    ... parts =
    ... offline = true
    ... """)

    >>> print system(join(sample_buildout, 'bin', 'buildout')),
    ext ['buildout']


    '''

def changes_in_svn_or_CVS_dont_affect_sig():
    """

If we have a develop recipe, it's signature shouldn't be affected to
changes in .svn or CVS directories.

    >>> mkdir('recipe')
    >>> write('recipe', 'setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(name='recipe',
    ...       entry_points={'zc.buildout': ['default=foo:Foo']})
    ... ''')
    >>> write('recipe', 'foo.py',
    ... '''
    ... class Foo:
    ...     def __init__(*args): pass
    ...     def install(*args): return ()
    ...     update = install
    ... ''')

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = recipe
    ... parts = foo
    ...
    ... [foo]
    ... recipe = recipe
    ... ''')


    >>> print system(join(sample_buildout, 'bin', 'buildout')),
    Develop: '/sample-buildout/recipe'
    Installing foo.

    >>> mkdir('recipe', '.svn')
    >>> mkdir('recipe', 'CVS')
    >>> print system(join(sample_buildout, 'bin', 'buildout')),
    Develop: '/sample-buildout/recipe'
    Updating foo.

    >>> write('recipe', '.svn', 'x', '1')
    >>> write('recipe', 'CVS', 'x', '1')

    >>> print system(join(sample_buildout, 'bin', 'buildout')),
    Develop: '/sample-buildout/recipe'
    Updating foo.

    """

if hasattr(os, 'symlink'):
    def bug_250537_broken_symlink_doesnt_affect_sig():
        """
If we have a develop recipe, it's signature shouldn't be affected by
broken symlinks, and better yet, computing the hash should not break
because of the missing target file.

    >>> mkdir('recipe')
    >>> write('recipe', 'setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(name='recipe',
    ...       entry_points={'zc.buildout': ['default=foo:Foo']})
    ... ''')
    >>> write('recipe', 'foo.py',
    ... '''
    ... class Foo:
    ...     def __init__(*args): pass
    ...     def install(*args): return ()
    ...     update = install
    ... ''')

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = recipe
    ... parts = foo
    ...
    ... [foo]
    ... recipe = recipe
    ... ''')


    >>> print system(join(sample_buildout, 'bin', 'buildout')),
    Develop: '/sample-buildout/recipe'
    Installing foo.

    >>> write('recipe', 'some-file', '1')
    >>> os.symlink(join('recipe', 'some-file'),
    ...            join('recipe', 'another-file'))
    >>> ls('recipe')
    l  another-file
    -  foo.py
    -  foo.pyc
    d  recipe.egg-info
    -  setup.py
    -  some-file

    >>> remove('recipe', 'some-file')

    >>> print system(join(sample_buildout, 'bin', 'buildout')),
    Develop: '/sample-buildout/recipe'
    Updating foo.

    """

def o_option_sets_offline():
    """
    >>> print system(join(sample_buildout, 'bin', 'buildout')+' -vvo'),
    ... # doctest: +ELLIPSIS
    <BLANKLINE>
    ...
    offline = true
    ...
    """

def recipe_upgrade():
    """

The buildout will upgrade recipes in newest (and non-offline) mode.

Let's create a recipe egg

    >>> mkdir('recipe')
    >>> write('recipe', 'recipe.py',
    ... '''
    ... class Recipe:
    ...     def __init__(*a): pass
    ...     def install(self):
    ...         print 'recipe v1'
    ...         return ()
    ...     update = install
    ... ''')

    >>> write('recipe', 'setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(name='recipe', version='1', py_modules=['recipe'],
    ...       entry_points={'zc.buildout': ['default = recipe:Recipe']},
    ...       )
    ... ''')

    >>> write('recipe', 'README', '')

    >>> print system(buildout+' setup recipe bdist_egg'), # doctest: +ELLIPSIS
    Running setup script 'recipe/setup.py'.
    ...

    >>> rmdir('recipe', 'build')

And update our buildout to use it.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo
    ... find-links = %s
    ...
    ... [foo]
    ... recipe = recipe
    ... ''' % join('recipe', 'dist'))

    >>> print system(buildout),
    Getting distribution for 'recipe'.
    Got recipe 1.
    Installing foo.
    recipe v1

Now, if we update the recipe egg:

    >>> write('recipe', 'recipe.py',
    ... '''
    ... class Recipe:
    ...     def __init__(*a): pass
    ...     def install(self):
    ...         print 'recipe v2'
    ...         return ()
    ...     update = install
    ... ''')

    >>> write('recipe', 'setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(name='recipe', version='2', py_modules=['recipe'],
    ...       entry_points={'zc.buildout': ['default = recipe:Recipe']},
    ...       )
    ... ''')


    >>> print system(buildout+' setup recipe bdist_egg'), # doctest: +ELLIPSIS
    Running setup script 'recipe/setup.py'.
    ...

We won't get the update if we specify -N:

    >>> print system(buildout+' -N'),
    Updating foo.
    recipe v1

or if we use -o:

    >>> print system(buildout+' -o'),
    Updating foo.
    recipe v1

But we will if we use neither of these:

    >>> print system(buildout),
    Getting distribution for 'recipe'.
    Got recipe 2.
    Uninstalling foo.
    Installing foo.
    recipe v2

We can also select a particular recipe version:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo
    ... find-links = %s
    ...
    ... [foo]
    ... recipe = recipe ==1
    ... ''' % join('recipe', 'dist'))

    >>> print system(buildout),
    Uninstalling foo.
    Installing foo.
    recipe v1

    """

def update_adds_to_uninstall_list():
    """

Paths returned by the update method are added to the list of paths to
uninstall

    >>> mkdir('recipe')
    >>> write('recipe', 'setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(name='recipe',
    ...       entry_points={'zc.buildout': ['default = recipe:Recipe']},
    ...       )
    ... ''')

    >>> write('recipe', 'recipe.py',
    ... '''
    ... import os
    ... class Recipe:
    ...     def __init__(*_): pass
    ...     def install(self):
    ...         r = ('a', 'b', 'c')
    ...         for p in r: os.mkdir(p)
    ...         return r
    ...     def update(self):
    ...         r = ('c', 'd', 'e')
    ...         for p in r:
    ...             if not os.path.exists(p):
    ...                os.mkdir(p)
    ...         return r
    ... ''')

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = recipe
    ... parts = foo
    ...
    ... [foo]
    ... recipe = recipe
    ... ''')

    >>> print system(buildout),
    Develop: '/sample-buildout/recipe'
    Installing foo.

    >>> print system(buildout),
    Develop: '/sample-buildout/recipe'
    Updating foo.

    >>> cat('.installed.cfg') # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    [buildout]
    ...
    [foo]
    __buildout_installed__ = a
    	b
    	c
    	d
    	e
    __buildout_signature__ = ...

"""

def log_when_there_are_not_local_distros():
    """
    >>> from zope.testing.loggingsupport import InstalledHandler
    >>> handler = InstalledHandler('zc.buildout.easy_install')
    >>> import logging
    >>> logger = logging.getLogger('zc.buildout.easy_install')
    >>> old_propogate = logger.propagate
    >>> logger.propagate = False

    >>> dest = tmpdir('sample-install')
    >>> import zc.buildout.easy_install
    >>> ws = zc.buildout.easy_install.install(
    ...     ['demo==0.2'], dest,
    ...     links=[link_server], index=link_server+'index/')

    >>> print handler # doctest: +ELLIPSIS
    zc.buildout.easy_install DEBUG
      Installing 'demo==0.2'.
    zc.buildout.easy_install DEBUG
      We have no distributions for demo that satisfies 'demo==0.2'.
    ...

    >>> handler.uninstall()
    >>> logger.propagate = old_propogate

    """

def internal_errors():
    """Internal errors are clearly marked and don't generate tracebacks:

    >>> mkdir(sample_buildout, 'recipes')

    >>> write(sample_buildout, 'recipes', 'mkdir.py',
    ... '''
    ... class Mkdir:
    ...     def __init__(self, buildout, name, options):
    ...         self.name, self.options = name, options
    ...         options['path'] = os.path.join(
    ...                               buildout['buildout']['directory'],
    ...                               options['path'],
    ...                               )
    ... ''')

    >>> write(sample_buildout, 'recipes', 'setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(name = "recipes",
    ...       entry_points = {'zc.buildout': ['mkdir = mkdir:Mkdir']},
    ...       )
    ... ''')

    >>> write(sample_buildout, 'buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = recipes
    ... parts = data-dir
    ...
    ... [data-dir]
    ... recipe = recipes:mkdir
    ... ''')

    >>> print system(buildout), # doctest: +ELLIPSIS
    Develop: '/sample-buildout/recipes'
    While:
      Installing.
      Getting section data-dir.
      Initializing part data-dir.
    <BLANKLINE>
    An internal error occurred due to a bug in either zc.buildout or in a
    recipe being used:
    Traceback (most recent call last):
    ...
    NameError: global name 'os' is not defined
    """

def whine_about_unused_options():
    '''

    >>> write('foo.py',
    ... """
    ... class Foo:
    ...
    ...     def __init__(self, buildout, name, options):
    ...         self.name, self.options = name, options
    ...         options['x']
    ...
    ...     def install(self):
    ...         self.options['y']
    ...         return ()
    ... """)

    >>> write('setup.py',
    ... """
    ... from setuptools import setup
    ... setup(name = "foo",
    ...       entry_points = {'zc.buildout': ['default = foo:Foo']},
    ...       )
    ... """)

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... develop = .
    ... parts = foo
    ... a = 1
    ...
    ... [foo]
    ... recipe = foo
    ... x = 1
    ... y = 1
    ... z = 1
    ... """)

    >>> print system(buildout),
    Develop: '/sample-buildout/.'
    Unused options for buildout: 'a'.
    Installing foo.
    Unused options for foo: 'z'.
    '''

def abnormal_exit():
    """
People sometimes hit control-c while running a builout. We need to make
sure that the installed database Isn't corrupted.  To test this, we'll create
some evil recipes that exit uncleanly:

    >>> mkdir('recipes')
    >>> write('recipes', 'recipes.py',
    ... '''
    ... import os
    ...
    ... class Clean:
    ...     def __init__(*_): pass
    ...     def install(_): return ()
    ...     def update(_): pass
    ...
    ... class EvilInstall(Clean):
    ...     def install(_): os._exit(1)
    ...
    ... class EvilUpdate(Clean):
    ...     def update(_): os._exit(1)
    ... ''')

    >>> write('recipes', 'setup.py',
    ... '''
    ... import setuptools
    ... setuptools.setup(name='recipes',
    ...    entry_points = {
    ...      'zc.buildout': [
    ...          'clean = recipes:Clean',
    ...          'evil_install = recipes:EvilInstall',
    ...          'evil_update = recipes:EvilUpdate',
    ...          'evil_uninstall = recipes:Clean',
    ...          ],
    ...       },
    ...     )
    ... ''')

Now let's look at 3 cases:

1. We exit during installation after installing some other parts:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = recipes
    ... parts = p1 p2 p3 p4
    ...
    ... [p1]
    ... recipe = recipes:clean
    ...
    ... [p2]
    ... recipe = recipes:clean
    ...
    ... [p3]
    ... recipe = recipes:evil_install
    ...
    ... [p4]
    ... recipe = recipes:clean
    ... ''')

    >>> print system(buildout),
    Develop: '/sample-buildout/recipes'
    Installing p1.
    Installing p2.
    Installing p3.

    >>> print system(buildout),
    Develop: '/sample-buildout/recipes'
    Updating p1.
    Updating p2.
    Installing p3.

    >>> print system(buildout+' buildout:parts='),
    Develop: '/sample-buildout/recipes'
    Uninstalling p2.
    Uninstalling p1.

2. We exit while updating:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = recipes
    ... parts = p1 p2 p3 p4
    ...
    ... [p1]
    ... recipe = recipes:clean
    ...
    ... [p2]
    ... recipe = recipes:clean
    ...
    ... [p3]
    ... recipe = recipes:evil_update
    ...
    ... [p4]
    ... recipe = recipes:clean
    ... ''')

    >>> print system(buildout),
    Develop: '/sample-buildout/recipes'
    Installing p1.
    Installing p2.
    Installing p3.
    Installing p4.

    >>> print system(buildout),
    Develop: '/sample-buildout/recipes'
    Updating p1.
    Updating p2.
    Updating p3.

    >>> print system(buildout+' buildout:parts='),
    Develop: '/sample-buildout/recipes'
    Uninstalling p2.
    Uninstalling p1.
    Uninstalling p4.
    Uninstalling p3.

3. We exit while installing or updating after uninstalling:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = recipes
    ... parts = p1 p2 p3 p4
    ...
    ... [p1]
    ... recipe = recipes:evil_update
    ...
    ... [p2]
    ... recipe = recipes:clean
    ...
    ... [p3]
    ... recipe = recipes:clean
    ...
    ... [p4]
    ... recipe = recipes:clean
    ... ''')

    >>> print system(buildout),
    Develop: '/sample-buildout/recipes'
    Installing p1.
    Installing p2.
    Installing p3.
    Installing p4.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = recipes
    ... parts = p1 p2 p3 p4
    ...
    ... [p1]
    ... recipe = recipes:evil_update
    ...
    ... [p2]
    ... recipe = recipes:clean
    ...
    ... [p3]
    ... recipe = recipes:clean
    ...
    ... [p4]
    ... recipe = recipes:clean
    ... x = 1
    ... ''')

    >>> print system(buildout),
    Develop: '/sample-buildout/recipes'
    Uninstalling p4.
    Updating p1.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = recipes
    ... parts = p1 p2 p3 p4
    ...
    ... [p1]
    ... recipe = recipes:clean
    ...
    ... [p2]
    ... recipe = recipes:clean
    ...
    ... [p3]
    ... recipe = recipes:clean
    ...
    ... [p4]
    ... recipe = recipes:clean
    ... ''')

    >>> print system(buildout),
    Develop: '/sample-buildout/recipes'
    Uninstalling p1.
    Installing p1.
    Updating p2.
    Updating p3.
    Installing p4.

    """

def install_source_dist_with_bad_py():
    """

    >>> mkdir('badegg')
    >>> mkdir('badegg', 'badegg')
    >>> write('badegg', 'badegg', '__init__.py', '#\\n')
    >>> mkdir('badegg', 'badegg', 'scripts')
    >>> write('badegg', 'badegg', 'scripts', '__init__.py', '#\\n')
    >>> write('badegg', 'badegg', 'scripts', 'one.py',
    ... '''
    ... return 1
    ... ''')

    >>> write('badegg', 'setup.py',
    ... '''
    ... from setuptools import setup, find_packages
    ... setup(
    ...     name='badegg',
    ...     version='1',
    ...     packages = find_packages('.'),
    ...     zip_safe=False)
    ... ''')

    >>> print system(buildout+' setup badegg sdist'), # doctest: +ELLIPSIS
    Running setup script 'badegg/setup.py'.
    ...

    >>> dist = join('badegg', 'dist')

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = eggs bo
    ... find-links = %(dist)s
    ...
    ... [eggs]
    ... recipe = zc.recipe.egg
    ... eggs = badegg
    ...
    ... [bo]
    ... recipe = zc.recipe.egg
    ... eggs = zc.buildout
    ... scripts = buildout=bo
    ... ''' % globals())

    >>> print system(buildout);print 'X' # doctest: +ELLIPSIS
    Installing eggs.
    Getting distribution for 'badegg'.
    Got badegg 1.
    Installing bo.
    ...
    SyntaxError: ...'return' outside function...
    ...
    SyntaxError: ...'return' outside function...
    ...

    >>> ls('eggs') # doctest: +ELLIPSIS
    d  badegg-1-py2.4.egg
    ...

    >>> ls('bin')
    -  bo
    -  buildout
    """

def version_requirements_in_build_honored():
    '''

    >>> update_extdemo()
    >>> dest = tmpdir('sample-install')
    >>> mkdir('include')
    >>> write('include', 'extdemo.h',
    ... """
    ... #define EXTDEMO 42
    ... """)

    >>> zc.buildout.easy_install.build(
    ...   'extdemo ==1.4', dest,
    ...   {'include-dirs': os.path.join(sample_buildout, 'include')},
    ...   links=[link_server], index=link_server+'index/',
    ...   newest=False)
    ['/sample-install/extdemo-1.4-py2.4-linux-i686.egg']

    '''

def bug_105081_Specific_egg_versions_are_ignored_when_newer_eggs_are_around():
    """
    Buildout might ignore a specific egg requirement for a recipe:

    - Have a newer version of an egg in your eggs directory
    - Use 'recipe==olderversion' in your buildout.cfg to request an
      older version

    Buildout will go and fetch the older version, but it will *use*
    the newer version when installing a part with this recipe.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = x
    ... find-links = %(sample_eggs)s
    ...
    ... [x]
    ... recipe = zc.recipe.egg
    ... eggs = demo
    ... ''' % globals())

    >>> print system(buildout),
    Installing x.
    Getting distribution for 'demo'.
    Got demo 0.4c1.
    Getting distribution for 'demoneeded'.
    Got demoneeded 1.2c1.
    Generated script '/sample-buildout/bin/demo'.

    >>> print system(join('bin', 'demo')),
    4 2

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = x
    ... find-links = %(sample_eggs)s
    ...
    ... [x]
    ... recipe = zc.recipe.egg
    ... eggs = demo ==0.1
    ... ''' % globals())

    >>> print system(buildout),
    Uninstalling x.
    Installing x.
    Getting distribution for 'demo==0.1'.
    Got demo 0.1.
    Generated script '/sample-buildout/bin/demo'.

    >>> print system(join('bin', 'demo')),
    1 2
    """

def versions_section_ignored_for_dependency_in_favor_of_site_packages():
    r"""
This is a test for a bugfix.

The error showed itself when at least two dependencies were in a shared
location like site-packages, and the first one met the "versions" setting.  The
first dependency would be added, but subsequent dependencies from the same
location (e.g., site-packages) would use the version of the package found in
the shared location, ignoring the version setting.

We begin with a Python that has demoneeded version 1.1 installed and a
demo version 0.3, all in a site-packages-like shared directory.  We need
to create this.  ``eggrecipedemo.main()`` shows the number after the dot
(that is, ``X`` in ``1.X``), for the demo package and the demoneeded
package, so this demonstrates that our Python does in fact have demo
version 0.3 and demoneeded version 1.1.

    >>> py_path = make_py_with_system_install(make_py, sample_eggs)
    >>> print call_py(
    ...     py_path,
    ...     "import tellmy.version; print tellmy.version.__version__"),
    1.1

Now here's a setup that would expose the bug, using the
zc.buildout.easy_install API.

    >>> example_dest = tmpdir('example_dest')
    >>> workingset = zc.buildout.easy_install.install(
    ...     ['tellmy.version'], example_dest, links=[sample_eggs],
    ...     executable=py_path,
    ...     index=None,
    ...     versions={'tellmy.version': '1.0'})
    >>> for dist in workingset:
    ...     res = str(dist)
    ...     if res.startswith('tellmy.version'):
    ...         print res
    ...         break
    tellmy.version 1.0

Before the bugfix, the desired tellmy.version distribution would have
been blocked the one in site-packages.
"""

def handle_namespace_package_in_both_site_packages_and_buildout_eggs():
    r"""
If you have the same namespace package in both site-packages and in
buildout, we need to be very careful that faux-Python-executables and
scripts generated by easy_install.sitepackage_safe_scripts correctly
combine the two. We show this with the local recipe that uses the
function, z3c.recipe.scripts.

To demonstrate this, we will create three packages: tellmy.version 1.0,
tellmy.version 1.1, and tellmy.fortune 1.0.  tellmy.version 1.1 is installed.

    >>> py_path = make_py_with_system_install(make_py, sample_eggs)
    >>> print call_py(
    ...     py_path,
    ...     "import tellmy.version; print tellmy.version.__version__")
    1.1
    <BLANKLINE>

Now we will create a buildout that creates a script and a faux-Python script.
We want to see that both can successfully import the specified versions of
tellmy.version and tellmy.fortune.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = eggs
    ... find-links = %(link_server)s
    ...
    ... [primed_python]
    ... executable = %(py_path)s
    ...
    ... [eggs]
    ... recipe = z3c.recipe.scripts
    ... python = primed_python
    ... interpreter = py
    ... include-site-packages = true
    ... eggs = tellmy.version == 1.0
    ...        tellmy.fortune == 1.0
    ...        demo
    ... script-initialization =
    ...     import tellmy.version
    ...     print tellmy.version.__version__
    ...     import tellmy.fortune
    ...     print tellmy.fortune.__version__
    ... ''' % globals())

    >>> print system(buildout)
    Installing eggs.
    Getting distribution for 'tellmy.version==1.0'.
    Got tellmy.version 1.0.
    Getting distribution for 'tellmy.fortune==1.0'.
    Got tellmy.fortune 1.0.
    Getting distribution for 'demo'.
    Got demo 0.4c1.
    Getting distribution for 'demoneeded'.
    Got demoneeded 1.2c1.
    Generated script '/sample-buildout/bin/demo'.
    Generated interpreter '/sample-buildout/bin/py'.
    <BLANKLINE>

Finally, we are ready to see if it worked.  Prior to the bug fix that
this tests, the results of both calls below was the following::

    1.1
    Traceback (most recent call last):
      ...
    ImportError: No module named fortune
    <BLANKLINE>

In other words, we got the site-packages version of tellmy.version, and
we could not import tellmy.fortune at all.  The following are the correct
results for the interpreter and for the script.

    >>> print call_py(
    ...     join('bin', 'py'),
    ...     "import tellmy.version; " +
    ...     "print tellmy.version.__version__; " +
    ...     "import tellmy.fortune; " +
    ...     "print tellmy.fortune.__version__") # doctest: +ELLIPSIS
    1.0
    1.0...

    >>> print system(join('bin', 'demo'))
    1.0
    1.0
    4 2
    <BLANKLINE>
    """

def handle_sys_path_version_hack():
    r"""
This is a test for a bugfix.

If you use a Python that has a different version of one of your
dependencies, and the new package tries to do sys.path tricks in the
setup.py to get a __version__, and it uses namespace packages, the older
package will be loaded first, making the setup version the wrong number.
While very arguably packages simply shouldn't do this, some do, and we
don't want buildout to fall over when they do.

To demonstrate this, we will need to create a distribution that has one of
these unpleasant tricks, and a Python that has an older version installed.

    >>> py_path, site_packages_path = make_py()
    >>> for version in ('1.0', '1.1'):
    ...     tmp = tempfile.mkdtemp()
    ...     try:
    ...         write(tmp, 'README.txt', '')
    ...         mkdir(tmp, 'src')
    ...         mkdir(tmp, 'src', 'tellmy')
    ...         write(tmp, 'src', 'tellmy', '__init__.py',
    ...             "__import__("
    ...             "'pkg_resources').declare_namespace(__name__)\n")
    ...         mkdir(tmp, 'src', 'tellmy', 'version')
    ...         write(tmp, 'src', 'tellmy', 'version',
    ...               '__init__.py', '__version__=%r\n' % version)
    ...         write(
    ...             tmp, 'setup.py',
    ...             "from setuptools import setup\n"
    ...             "import sys\n"
    ...             "sys.path.insert(0, 'src')\n"
    ...             "from tellmy.version import __version__\n"
    ...             "setup(\n"
    ...             " name='tellmy.version',\n"
    ...             " package_dir = {'': 'src'},\n"
    ...             " packages = ['tellmy', 'tellmy.version'],\n"
    ...             " install_requires = ['setuptools'],\n"
    ...             " namespace_packages=['tellmy'],\n"
    ...             " zip_safe=True, version=__version__,\n"
    ...             " author='bob', url='bob', author_email='bob')\n"
    ...             )
    ...         zc.buildout.testing.sdist(tmp, sample_eggs)
    ...         if version == '1.0':
    ...             # We install the 1.0 version in site packages the way a
    ...             # system packaging system (debs, rpms) would do it.
    ...             zc.buildout.testing.sys_install(tmp, site_packages_path)
    ...     finally:
    ...         shutil.rmtree(tmp)
    >>> print call_py(
    ...     py_path,
    ...     "import tellmy.version; print tellmy.version.__version__")
    1.0
    <BLANKLINE>
    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = eggs
    ... find-links = %(sample_eggs)s
    ...
    ... [primed_python]
    ... executable = %(py_path)s
    ...
    ... [eggs]
    ... recipe = zc.recipe.egg:eggs
    ... python = primed_python
    ... eggs = tellmy.version == 1.1
    ... ''' % globals())

Before the bugfix, running this buildout would generate this error:

    Installing eggs.
    Getting distribution for 'tellmy.version==1.1'.
    Installing tellmy.version 1.1
    Caused installation of a distribution:
    tellmy.version 1.0
    with a different version.
    Got None.
    While:
      Installing eggs.
    Error: There is a version conflict.
    We already have: tellmy.version 1.0
    <BLANKLINE>

You can see the copiously commented fix for this in easy_install.py (see
zc.buildout.easy_install.Installer._call_easy_install and particularly
the comment leading up to zc.buildout.easy_install._easy_install_cmd).
Now the install works correctly, as seen here.

    >>> print system(buildout)
    Installing eggs.
    Getting distribution for 'tellmy.version==1.1'.
    Got tellmy.version 1.1.
    <BLANKLINE>

    """

def isolated_include_site_packages():
    """

This is an isolated test of the include_site_packages functionality, passing
the argument directly to install, overriding a default.

Our "py_path" has the "demoneeded" and "demo" packages available.  We'll
simply be asking for "demoneeded" here.

    >>> py_path, site_packages_path = make_py()
    >>> create_sample_sys_install(site_packages_path)
    >>> zc.buildout.easy_install.include_site_packages(False)
    True

    >>> example_dest = tmpdir('site-packages-example-install')
    >>> workingset = zc.buildout.easy_install.install(
    ...     ['demoneeded'], example_dest, links=[], executable=py_path,
    ...     index=None, include_site_packages=True)
    >>> [dist.project_name for dist in workingset]
    ['demoneeded']

That worked fine.  Let's try again with site packages not allowed (and
reversing the default).

    >>> zc.buildout.easy_install.include_site_packages(True)
    False

    >>> zc.buildout.easy_install.clear_index_cache()
    >>> rmdir(example_dest)
    >>> example_dest = tmpdir('site-packages-example-install')
    >>> workingset = zc.buildout.easy_install.install(
    ...     ['demoneeded'], example_dest, links=[], executable=py_path,
    ...     index=None, include_site_packages=False)
    Traceback (most recent call last):
        ...
    MissingDistribution: Couldn't find a distribution for 'demoneeded'.

That's a failure, as expected.

Now we explore an important edge case.

Some system Pythons include setuptools (and other Python packages) in their
site-packages (or equivalent) using a .egg-info directory.  The pkg_resources
module (from setuptools) considers a package installed using .egg-info to be a
develop egg.

zc.buildout.buildout.Buildout.bootstrap will make setuptools and zc.buildout
available to the buildout via the eggs directory, for normal eggs; or the
develop-eggs directory, for develop-eggs.

If setuptools or zc.buildout is found in site-packages and considered by
pkg_resources to be a develop egg, then the bootstrap code will use a .egg-link
in the local develop-eggs, pointing to site-packages, in its entirety.  Because
develop-eggs must always be available for searching for distributions, this
indirectly brings site-packages back into the search path for distributions.

Because of this, we have to take special care that we still exclude
site-packages even in this case.  See the comments about site packages in the
Installer._satisfied and Installer._obtain methods for the implementation
(as of this writing).

In this demonstration, we insert a link to the "demoneeded" distribution
in our develop-eggs, which would bring the package back in, except for
the special care we have taken to exclude it.

    >>> zc.buildout.easy_install.clear_index_cache()
    >>> rmdir(example_dest)
    >>> example_dest = tmpdir('site-packages-example-install')
    >>> mkdir(example_dest, 'develop-eggs')
    >>> write(example_dest, 'develop-eggs', 'demoneeded.egg-link',
    ...       site_packages_path)
    >>> workingset = zc.buildout.easy_install.install(
    ...     ['demoneeded'], example_dest, links=[],
    ...     path=[join(example_dest, 'develop-eggs')],
    ...     executable=py_path,
    ...     index=None, include_site_packages=False)
    Traceback (most recent call last):
        ...
    MissingDistribution: Couldn't find a distribution for 'demoneeded'.

The MissingDistribution error shows that buildout correctly excluded the
"site-packages" source even though it was indirectly included in the path
via a .egg-link file.

    """

def include_site_packages_bug_623590():
    """
As mentioned in isolated_include_site_packages, some system Pythons
include various Python packages in their site-packages (or equivalent)
using a .egg-info directory.  The pkg_resources module (from setuptools)
considers a package installed using .egg-info to be a develop egg

We generally prefer develop eggs when we are selecting dependencies, because
we expect them to be eggs that buildout has been told to develop.  However,
we should not consider these site-packages eggs as develop eggs--they should
not have automatic precedence over eggs available elsewhere.

We have specific code to handle this case, as identified in bug 623590.
See zc.buildout.easy_install.Installer._satisfied, as of this writing,
for the pertinent code. Here's the test for the bugfix.

    >>> py_path, site_packages_path = make_py()
    >>> create_sample_sys_install(site_packages_path)
    >>> zc.buildout.easy_install.include_site_packages(False)
    True

    >>> example_dest = tmpdir('site-packages-example-install')
    >>> workingset = zc.buildout.easy_install.install(
    ...     ['demo'], example_dest, links=[sample_eggs], executable=py_path,
    ...     index=None, include_site_packages=True, prefer_final=False)
    >>> [(dist.project_name, dist.version) for dist in workingset]
    [('demo', '0.4c1'), ('demoneeded', '1.2c1')]
"""

def allowed_eggs_from_site_packages():
    """
Sometimes you need or want to control what eggs from site-packages are used.
The allowed-eggs-from-site-packages option allows you to specify a whitelist of
project names that may be included from site-packages.  You can use globs to
specify the value.  It defaults to a single value of '*', indicating that any
package may come from site-packages.

This option interacts with include-site-packages in the following ways.

If include-site-packages is true, then allowed-eggs-from-site-packages filters
what eggs from site-packages may be chosen.  If allowed-eggs-from-site-packages
is an empty list, then no eggs from site-packages are chosen, but site-packages
will still be included at the end of path lists.

If include-site-packages is false, allowed-eggs-from-site-packages is
irrelevant.

This test shows the interaction with the zc.buildout.easy_install API.  Another
test below (allow_site_package_eggs_option) shows using it with a buildout.cfg.

Our "py_path" has the "demoneeded" and "demo" packages available.  We'll
simply be asking for "demoneeded" here.

    >>> py_path, site_packages_path = make_py()
    >>> create_sample_sys_install(site_packages_path)

    >>> example_dest = tmpdir('site-packages-example-install')
    >>> workingset = zc.buildout.easy_install.install(
    ...     ['demoneeded'], example_dest, links=[], executable=py_path,
    ...     index=None,
    ...     allowed_eggs_from_site_packages=['demoneeded', 'other'])
    >>> [dist.project_name for dist in workingset]
    ['demoneeded']

That worked fine.  It would work fine for a glob too.

    >>> zc.buildout.easy_install.clear_index_cache()
    >>> rmdir(example_dest)
    >>> example_dest = tmpdir('site-packages-example-install')
    >>> workingset = zc.buildout.easy_install.install(
    ...     ['demoneeded'], example_dest, links=[], executable=py_path,
    ...     index=None,
    ...     allowed_eggs_from_site_packages=['?emon*', 'other'])
    >>> [dist.project_name for dist in workingset]
    ['demoneeded']

But now let's try again with 'demoneeded' not allowed.

    >>> zc.buildout.easy_install.clear_index_cache()
    >>> rmdir(example_dest)
    >>> example_dest = tmpdir('site-packages-example-install')
    >>> workingset = zc.buildout.easy_install.install(
    ...     ['demoneeded'], example_dest, links=[], executable=py_path,
    ...     index=None,
    ...     allowed_eggs_from_site_packages=['demo'])
    Traceback (most recent call last):
        ...
    MissingDistribution: Couldn't find a distribution for 'demoneeded'.

Here's the same, but with an empty list.

    >>> zc.buildout.easy_install.clear_index_cache()
    >>> rmdir(example_dest)
    >>> example_dest = tmpdir('site-packages-example-install')
    >>> workingset = zc.buildout.easy_install.install(
    ...     ['demoneeded'], example_dest, links=[], executable=py_path,
    ...     index=None,
    ...     allowed_eggs_from_site_packages=[])
    Traceback (most recent call last):
        ...
    MissingDistribution: Couldn't find a distribution for 'demoneeded'.

Of course, this doesn't stop us from getting a package from elsewhere.  Here,
we add a link server.

    >>> zc.buildout.easy_install.clear_index_cache()
    >>> rmdir(example_dest)
    >>> example_dest = tmpdir('site-packages-example-install')
    >>> workingset = zc.buildout.easy_install.install(
    ...     ['demoneeded'], example_dest, executable=py_path,
    ...     links=[link_server], index=link_server+'index/',
    ...     allowed_eggs_from_site_packages=['other'])
    >>> [dist.project_name for dist in workingset]
    ['demoneeded']
    >>> [dist.location for dist in workingset]
    ['/site-packages-example-install/demoneeded-1.1-py2.6.egg']

Finally, here's an example of an interaction: we say that it is OK to
allow the "demoneeded" egg to come from site-packages, but we don't
include-site-packages.

    >>> zc.buildout.easy_install.clear_index_cache()
    >>> rmdir(example_dest)
    >>> example_dest = tmpdir('site-packages-example-install')
    >>> workingset = zc.buildout.easy_install.install(
    ...     ['demoneeded'], example_dest, links=[], executable=py_path,
    ...     index=None, include_site_packages=False,
    ...     allowed_eggs_from_site_packages=['demoneeded'])
    Traceback (most recent call last):
        ...
    MissingDistribution: Couldn't find a distribution for 'demoneeded'.

    """

def allowed_eggs_from_site_packages_dependencies_bugfix():
    """
If you specify that a package with a dependency may come from site-packages,
that doesn't mean that the dependency may come from site-packages.  This
is a test for a bug fix to verify that this is true.

    >>> py_path, site_packages_path = make_py()
    >>> create_sample_sys_install(site_packages_path)
    >>> interpreter_dir = tmpdir('interpreter')
    >>> interpreter_parts_dir = os.path.join(
    ...     interpreter_dir, 'parts', 'interpreter')
    >>> interpreter_bin_dir = os.path.join(interpreter_dir, 'bin')
    >>> mkdir(interpreter_bin_dir)
    >>> mkdir(interpreter_dir, 'eggs')
    >>> mkdir(interpreter_dir, 'parts')
    >>> mkdir(interpreter_parts_dir)
    >>> ws = zc.buildout.easy_install.install(
    ...     ['demo'], join(interpreter_dir, 'eggs'), executable=py_path,
    ...     links=[link_server], index=link_server+'index/',
    ...     allowed_eggs_from_site_packages=['demo'])
    >>> [dist.project_name for dist in ws]
    ['demo', 'demoneeded']
    >>> from pprint import pprint
    >>> pprint([dist.location for dist in ws])
    ['/executable_buildout/site-packages',
     '/interpreter/eggs/demoneeded-1.1-pyN.N.egg']

    """

def allowed_eggs_from_site_packages_bug_592524():
    """
When we use allowed_eggs_from_site_packages, we need to make sure that the
site-packages paths are not inserted with the normal egg paths.  They already
included at the end, and including them along with the normal egg paths will
possibly mask subsequent egg paths.  This affects interpreters and scripts
generated by sitepackage_safe_scripts.

Our "py_path" has the "demoneeded" and "demo" packages available.

    >>> py_path, site_packages_path = make_py()
    >>> create_sample_sys_install(site_packages_path)
    >>> interpreter_dir = tmpdir('interpreter')
    >>> interpreter_parts_dir = os.path.join(
    ...     interpreter_dir, 'parts', 'interpreter')
    >>> interpreter_bin_dir = os.path.join(interpreter_dir, 'bin')
    >>> mkdir(interpreter_bin_dir)
    >>> mkdir(interpreter_dir, 'eggs')
    >>> mkdir(interpreter_dir, 'parts')
    >>> mkdir(interpreter_parts_dir)
    >>> ws = zc.buildout.easy_install.install(
    ...     ['demo', 'other'], join(interpreter_dir, 'eggs'), executable=py_path,
    ...     links=[link_server], index=link_server+'index/',
    ...     allowed_eggs_from_site_packages=['demo'])
    >>> generated = zc.buildout.easy_install.sitepackage_safe_scripts(
    ...     interpreter_bin_dir, ws, py_path, interpreter_parts_dir,
    ...     interpreter='py', include_site_packages=True)

Now we will look at the paths in the site.py we generated.  Notice that the
site-packages are at the end.  They were not before this bugfix.

    >>> test = 'import pprint, sys; pprint.pprint(sys.path[-4:])'
    >>> print call_py(join(interpreter_bin_dir, 'py'), test)
    ['/interpreter/eggs/other-1.0-pyN.N.egg',
     '/interpreter/eggs/demoneeded-1.1-pyN.N.egg',
     '/executable_buildout/eggs/setuptools-0.0-pyN.N.egg',
     '/executable_buildout/site-packages']
    <BLANKLINE>
    """

def subprocesses_have_same_environment_by_default():
    """
The scripts generated by sitepackage_safe_scripts set the PYTHONPATH so that,
if the environment is maintained (the default behavior), subprocesses get
the same Python packages.

First, we set up a script and an interpreter.

    >>> interpreter_dir = tmpdir('interpreter')
    >>> interpreter_parts_dir = os.path.join(
    ...     interpreter_dir, 'parts', 'interpreter')
    >>> interpreter_bin_dir = os.path.join(interpreter_dir, 'bin')
    >>> mkdir(interpreter_bin_dir)
    >>> mkdir(interpreter_dir, 'eggs')
    >>> mkdir(interpreter_dir, 'parts')
    >>> mkdir(interpreter_parts_dir)
    >>> ws = zc.buildout.easy_install.install(
    ...     ['demo'], join(interpreter_dir, 'eggs'), links=[link_server],
    ...     index=link_server+'index/')
    >>> test = (
    ...     "import subprocess, sys; subprocess.call("
    ...     "[sys.executable, '-c', "
    ...     "'import eggrecipedemo; print eggrecipedemo.x'])")
    >>> generated = zc.buildout.easy_install.sitepackage_safe_scripts(
    ...     interpreter_bin_dir, ws, sys.executable, interpreter_parts_dir,
    ...     reqs=['demo'], interpreter='py',
    ...     script_initialization=test + '; sys.exit(0)')

This works for the script.

    >>> print system(join(interpreter_bin_dir, 'demo'))
    3
    <BLANKLINE>

This also works for the generated interpreter.

    >>> print call_py(join(interpreter_bin_dir, 'py'), test)
    3
    <BLANKLINE>

If you have a PYTHONPATH in your environment, it will be honored, after
the buildout-generated path.

    >>> original_pythonpath = os.environ.get('PYTHONPATH')
    >>> os.environ['PYTHONPATH'] = 'foo'
    >>> test = (
    ...     "import subprocess, sys; subprocess.call("
    ...     "[sys.executable, '-c', "
    ...     "'import sys, pprint; pprint.pprint(sys.path)'])")
    >>> generated = zc.buildout.easy_install.sitepackage_safe_scripts(
    ...     interpreter_bin_dir, ws, sys.executable, interpreter_parts_dir,
    ...     reqs=['demo'], interpreter='py',
    ...     script_initialization=test + '; sys.exit(0)')

This works for the script.  As you can see, /sample_buildout/foo is included
right after the "parts" directory that contains site.py and sitecustomize.py.
You can also see, actually more easily than in the other example, that we
have the desired eggs available.

    >>> print system(join(interpreter_bin_dir, 'demo')), # doctest: +ELLIPSIS
    ['',
     '/interpreter/parts/interpreter',
     '/sample-buildout/foo',
     ...
     '/interpreter/eggs/demo-0.3-pyN.N.egg',
     '/interpreter/eggs/demoneeded-1.1-pyN.N.egg']

This also works for the generated interpreter, with identical results.

    >>> print call_py(join(interpreter_bin_dir, 'py'), test),
    ... # doctest: +ELLIPSIS
    ['',
     '/interpreter/parts/interpreter',
     '/sample-buildout/foo',
     ...
     '/interpreter/eggs/demo-0.3-pyN.N.egg',
     '/interpreter/eggs/demoneeded-1.1-pyN.N.egg']

    >>> # Cleanup
    >>> if original_pythonpath:
    ...     os.environ['PYTHONPATH'] = original_pythonpath
    ... else:
    ...     del os.environ['PYTHONPATH']
    ...

    """

def bootstrap_makes_buildout_that_works_with_system_python():
    r"""
In order to work smoothly with a system Python, bootstrapping creates
the buildout script with
zc.buildout.easy_install.sitepackage_safe_scripts. If it did not, a
variety of problems might happen.  For instance, if another version of
buildout or setuptools is installed in the site-packages than is
desired, it may cause a problem.

A problem actually experienced in the field is when
a recipe wants a different version of a dependency that is installed in
site-packages.  We will create a similar situation, and show that it is now
handled.

First let's write a dummy recipe.

    >>> mkdir(sample_buildout, 'recipes')
    >>> write(sample_buildout, 'recipes', 'dummy.py',
    ... '''
    ... import logging, os, zc.buildout
    ... class Dummy:
    ...     def __init__(self, buildout, name, options):
    ...         pass
    ...     def install(self):
    ...         return ()
    ...     def update(self):
    ...         pass
    ... ''')
    >>> write(sample_buildout, 'recipes', 'setup.py',
    ... '''
    ... from setuptools import setup
    ...
    ... setup(
    ...     name = "recipes",
    ...     entry_points = {'zc.buildout': ['dummy = dummy:Dummy']},
    ...     install_requires = 'demoneeded==1.2c1',
    ...     )
    ... ''')
    >>> write(sample_buildout, 'recipes', 'README.txt', " ")

Now we'll try to use it with a Python that has a different version of
demoneeded installed.

    >>> py_path, site_packages_path = make_py()
    >>> create_sample_sys_install(site_packages_path)
    >>> rmdir('develop-eggs')
    >>> from zc.buildout.testing import make_buildout
    >>> make_buildout(executable=py_path)
    >>> write(sample_buildout, 'buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = recipes
    ... parts = dummy
    ... find-links = %(link_server)s
    ... executable = %(py_path)s
    ...
    ... [dummy]
    ... recipe = recipes:dummy
    ... ''' % globals())

Now we actually run the buildout.  Before the change, we got the following
error:

    Develop: '/sample-buildout/recipes'
    While:
      Installing.
      Getting section dummy.
      Initializing section dummy.
      Installing recipe recipes.
    Error: There is a version conflict.
    We already have: demoneeded 1.1
    but recipes 0.0.0 requires 'demoneeded==1.2c1'.

Now, it is handled smoothly.

    >>> print system(buildout)
    Develop: '/sample-buildout/recipes'
    Getting distribution for 'demoneeded==1.2c1'.
    Got demoneeded 1.2c1.
    Installing dummy.
    <BLANKLINE>

Here's the same story with a namespace package, which has some additional
complications behind the scenes.  First, a recipe, in the "tellmy" namespace.

    >>> mkdir(sample_buildout, 'ns')
    >>> mkdir(sample_buildout, 'ns', 'tellmy')
    >>> write(sample_buildout, 'ns', 'tellmy', '__init__.py',
    ...       "__import__('pkg_resources').declare_namespace(__name__)\n")
    >>> mkdir(sample_buildout, 'ns', 'tellmy', 'recipes')
    >>> write(sample_buildout, 'ns', 'tellmy', 'recipes', '__init__.py', ' ')
    >>> write(sample_buildout, 'ns', 'tellmy', 'recipes', 'dummy.py',
    ... '''
    ... import logging, os, zc.buildout
    ... class Dummy:
    ...     def __init__(self, buildout, name, options):
    ...         pass
    ...     def install(self):
    ...         return ()
    ...     def update(self):
    ...         pass
    ... ''')
    >>> write(sample_buildout, 'ns', 'setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(
    ...     name="tellmy.recipes",
    ...     packages=['tellmy', 'tellmy.recipes'],
    ...     install_requires=['setuptools'],
    ...     namespace_packages=['tellmy'],
    ...     entry_points = {'zc.buildout':
    ...                     ['dummy = tellmy.recipes.dummy:Dummy']},
    ...     )
    ... ''')

Now, a buildout that uses it.

    >>> create_sample_namespace_eggs(sample_eggs, site_packages_path)
    >>> rmdir('develop-eggs')
    >>> from zc.buildout.testing import make_buildout
    >>> make_buildout(executable=py_path)
    >>> write(sample_buildout, 'buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = ns
    ...           recipes
    ... parts = dummy
    ... find-links = %(link_server)s
    ... executable = %(py_path)s
    ...
    ... [dummy]
    ... recipe = tellmy.recipes:dummy
    ... ''' % globals())

Now we actually run the buildout.

    >>> print system(buildout)
    Develop: '/sample-buildout/ns'
    Develop: '/sample-buildout/recipes'
    Uninstalling dummy.
    Installing dummy.
    <BLANKLINE>

    """

if sys.version_info > (2, 4):
    def test_exit_codes():
        """
        >>> import subprocess
        >>> def call(s):
        ...     p = subprocess.Popen(s, stdin=subprocess.PIPE,
        ...                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        ...     p.stdin.close()
        ...     print p.stdout.read()
        ...     print 'Exit:', bool(p.wait())

        >>> call(buildout)
        <BLANKLINE>
        Exit: False

        >>> write('buildout.cfg',
        ... '''
        ... [buildout]
        ... parts = x
        ... ''')

        >>> call(buildout) # doctest: +NORMALIZE_WHITESPACE
        While:
          Installing.
          Getting section x.
        Error: The referenced section, 'x', was not defined.
        <BLANKLINE>
        Exit: True

        >>> write('setup.py',
        ... '''
        ... from setuptools import setup
        ... setup(name='zc.buildout.testexit', entry_points={
        ...    'zc.buildout': ['default = testexitrecipe:x']})
        ... ''')

        >>> write('testexitrecipe.py',
        ... '''
        ... x y
        ... ''')

        >>> write('buildout.cfg',
        ... '''
        ... [buildout]
        ... parts = x
        ... develop = .
        ...
        ... [x]
        ... recipe = zc.buildout.testexit
        ... ''')

        >>> call(buildout) # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
        Develop: '/sample-buildout/.'
        While:
          Installing.
          Getting section x.
          Initializing section x.
          Loading zc.buildout recipe entry zc.buildout.testexit:default.
        <BLANKLINE>
        An internal error occurred due to a bug in either zc.buildout or in a
        recipe being used:
        Traceback (most recent call last):
        ...
             x y
               ^
         SyntaxError: invalid syntax
        <BLANKLINE>
        Exit: True
        """

def bug_59270_recipes_always_start_in_buildout_dir():
    """
    Recipes can rely on running from buildout directory

    >>> mkdir('bad_start')
    >>> write('bad_recipe.py',
    ... '''
    ... import os
    ... class Bad:
    ...     def __init__(self, *_):
    ...         print os.getcwd()
    ...     def install(self):
    ...         print os.getcwd()
    ...         os.chdir('bad_start')
    ...         print os.getcwd()
    ...         return ()
    ... ''')

    >>> write('setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(name='bad.test',
    ...       entry_points={'zc.buildout': ['default=bad_recipe:Bad']},)
    ... ''')

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = .
    ... parts = b1 b2
    ... [b1]
    ... recipe = bad.test
    ... [b2]
    ... recipe = bad.test
    ... ''')

    >>> os.chdir('bad_start')
    >>> print system(join(sample_buildout, 'bin', 'buildout')
    ...              +' -c '+join(sample_buildout, 'buildout.cfg')),
    Develop: '/sample-buildout/.'
    /sample-buildout
    /sample-buildout
    Installing b1.
    /sample-buildout
    /sample-buildout/bad_start
    Installing b2.
    /sample-buildout
    /sample-buildout/bad_start

    """

def bug_61890_file_urls_dont_seem_to_work_in_find_dash_links():
    """

    This bug arises from the fact that setuptools is overly restrictive
    about file urls, requiring that file urls pointing at directories
    must end in a slash.

    >>> dest = tmpdir('sample-install')
    >>> import zc.buildout.easy_install
    >>> sample_eggs = sample_eggs.replace(os.path.sep, '/')
    >>> ws = zc.buildout.easy_install.install(
    ...     ['demo==0.2'], dest,
    ...     links=['file://'+sample_eggs], index=link_server+'index/')


    >>> for dist in ws:
    ...     print dist
    demo 0.2
    demoneeded 1.1

    >>> ls(dest)
    -  demo-0.2-py2.4.egg
    -  demoneeded-1.1-py2.4.egg

    """

def bug_75607_buildout_should_not_run_if_it_creates_an_empty_buildout_cfg():
    """
    >>> remove('buildout.cfg')
    >>> print system(buildout),
    While:
      Initializing.
    Error: Couldn't open /sample-buildout/buildout.cfg



    """

def dealing_with_extremely_insane_dependencies():
    r"""

    There was a problem with analysis of dependencies taking a long
    time, in part because the analysis would get repeated every time a
    package was encountered in a dependency list.  Now, we don't do
    the analysis any more:

    >>> import os
    >>> for i in range(5):
    ...     p = 'pack%s' % i
    ...     deps = [('pack%s' % j) for j in range(5) if j is not i]
    ...     if i == 4:
    ...         deps.append('pack5')
    ...     mkdir(p)
    ...     write(p, 'setup.py',
    ...           'from setuptools import setup\n'
    ...           'setup(name=%r, install_requires=%r,\n'
    ...           '      url="u", author="a", author_email="e")\n'
    ...           % (p, deps))

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = pack0 pack1 pack2 pack3 pack4
    ... parts = pack1
    ...
    ... [pack1]
    ... recipe = zc.recipe.egg:eggs
    ... eggs = pack0
    ... ''')

    >>> print system(buildout),
    Develop: '/sample-buildout/pack0'
    Develop: '/sample-buildout/pack1'
    Develop: '/sample-buildout/pack2'
    Develop: '/sample-buildout/pack3'
    Develop: '/sample-buildout/pack4'
    Installing pack1.
    Couldn't find index page for 'pack5' (maybe misspelled?)
    Getting distribution for 'pack5'.
    While:
      Installing pack1.
      Getting distribution for 'pack5'.
    Error: Couldn't find a distribution for 'pack5'.

    However, if we run in verbose mode, we can see why packages were included:

    >>> print system(buildout+' -v'), # doctest: +ELLIPSIS
    Installing 'zc.buildout', 'setuptools'.
    We have a develop egg: zc.buildout 1.0.0
    We have the best distribution that satisfies 'setuptools'.
    Picked: setuptools = 0.6
    Develop: '/sample-buildout/pack0'
    Develop: '/sample-buildout/pack1'
    Develop: '/sample-buildout/pack2'
    Develop: '/sample-buildout/pack3'
    Develop: '/sample-buildout/pack4'
    ...Installing pack1.
    Installing 'pack0'.
    We have a develop egg: pack0 0.0.0
    Getting required 'pack4'
      required by pack0 0.0.0.
    We have a develop egg: pack4 0.0.0
    Getting required 'pack3'
      required by pack0 0.0.0.
      required by pack4 0.0.0.
    We have a develop egg: pack3 0.0.0
    Getting required 'pack2'
      required by pack0 0.0.0.
      required by pack3 0.0.0.
      required by pack4 0.0.0.
    We have a develop egg: pack2 0.0.0
    Getting required 'pack1'
      required by pack0 0.0.0.
      required by pack2 0.0.0.
      required by pack3 0.0.0.
      required by pack4 0.0.0.
    We have a develop egg: pack1 0.0.0
    Getting required 'pack5'
      required by pack4 0.0.0.
    We have no distributions for pack5 that satisfies 'pack5'.
    Couldn't find index page for 'pack5' (maybe misspelled?)
    Getting distribution for 'pack5'.
    While:
      Installing pack1.
      Getting distribution for 'pack5'.
    Error: Couldn't find a distribution for 'pack5'.
    """

def read_find_links_to_load_extensions():
    """
We'll create a wacky buildout extension that is just another name for http:

    >>> src = tmpdir('src')
    >>> write(src, 'wacky_handler.py',
    ... '''
    ... import urllib2
    ... class Wacky(urllib2.HTTPHandler):
    ...     wacky_open = urllib2.HTTPHandler.http_open
    ... def install(buildout=None):
    ...     urllib2.install_opener(urllib2.build_opener(Wacky))
    ... ''')
    >>> write(src, 'setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(name='wackyextension', version='1',
    ...       py_modules=['wacky_handler'],
    ...       entry_points = {'zc.buildout.extension':
    ...             ['default = wacky_handler:install']
    ...             },
    ...       )
    ... ''')
    >>> print system(buildout+' setup '+src+' bdist_egg'),
    ... # doctest: +ELLIPSIS
    Running setup ...
    creating 'dist/wackyextension-1-...

Now we'll create a buildout that uses this extension to load other packages:

    >>> wacky_server = link_server.replace('http', 'wacky')
    >>> dist = 'file://' + join(src, 'dist').replace(os.path.sep, '/')
    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = demo
    ... extensions = wackyextension
    ... find-links = %(wacky_server)s/demoneeded-1.0.zip
    ...              %(dist)s
    ... [demo]
    ... recipe = zc.recipe.egg
    ... eggs = demoneeded
    ... ''' % globals())

When we run the buildout. it will load the extension from the dist
directory and then use the wacky extension to load the demo package

    >>> print system(buildout),
    Getting distribution for 'wackyextension'.
    Got wackyextension 1.
    Installing demo.
    Getting distribution for 'demoneeded'.
    Got demoneeded 1.0.

    """

def distributions_from_local_find_links_make_it_to_download_cache():
    """

If we specify a local directory in find links, distors found there
need to make it to the download cache.

    >>> mkdir('test')
    >>> write('test', 'setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(name='foo')
    ... ''')

    >>> print system(buildout+' setup test bdist_egg'), # doctest: +ELLIPSIS
    Running setup script 'test/setup.py'.
    ...


    >>> mkdir('cache')
    >>> old_cache = zc.buildout.easy_install.download_cache('cache')
    >>> list(zc.buildout.easy_install.install(['foo'], 'eggs',
    ...          links=[join('test', 'dist')])) # doctest: +ELLIPSIS
    [foo 0.0.0 ...

    >>> ls('cache')
    -  foo-0.0.0-py2.4.egg

    >>> _ = zc.buildout.easy_install.download_cache(old_cache)

    """

def create_egg(name, version, dest, install_requires=None,
               dependency_links=None):
    d = tempfile.mkdtemp()
    if dest=='available':
        extras = dict(x=['x'])
    else:
        extras = {}
    if dependency_links:
        links = 'dependency_links = %s, ' % dependency_links
    else:
        links = ''
    if install_requires:
        requires = 'install_requires = %s, ' % install_requires
    else:
        requires = ''
    try:
        open(os.path.join(d, 'setup.py'), 'w').write(
            'from setuptools import setup\n'
            'setup(name=%r, version=%r, extras_require=%r, zip_safe=True,\n'
            '      %s %s py_modules=["setup"]\n)'
            % (name, str(version), extras, requires, links)
            )
        zc.buildout.testing.bdist_egg(d, sys.executable, os.path.abspath(dest))
    finally:
        shutil.rmtree(d)

def prefer_final_permutation(existing, available):
    for d in ('existing', 'available'):
        if os.path.exists(d):
            shutil.rmtree(d)
        os.mkdir(d)
    for version in existing:
        create_egg('spam', version, 'existing')
    for version in available:
        create_egg('spam', version, 'available')

    zc.buildout.easy_install.clear_index_cache()
    [dist] = list(
        zc.buildout.easy_install.install(['spam'], 'existing', ['available'],
                                         always_unzip=True)
        )

    if dist.extras:
        print 'downloaded', dist.version
    else:
        print 'had', dist.version
    sys.path_importer_cache.clear()

def prefer_final():
    """
This test tests several permutations:

Using different version numbers to work around zip importer cache problems. :(

- With prefer final:

    - no existing and newer dev available
    >>> prefer_final_permutation((), [1, '2a1'])
    downloaded 1

    - no existing and only dev available
    >>> prefer_final_permutation((), ['3a1'])
    downloaded 3a1

    - final existing and only dev acailable
    >>> prefer_final_permutation([4], ['5a1'])
    had 4

    - final existing and newer final available
    >>> prefer_final_permutation([6], [7])
    downloaded 7

    - final existing and same final available
    >>> prefer_final_permutation([8], [8])
    had 8

    - final existing and older final available
    >>> prefer_final_permutation([10], [9])
    had 10

    - only dev existing and final available
    >>> prefer_final_permutation(['12a1'], [11])
    downloaded 11

    - only dev existing and no final available newer dev available
    >>> prefer_final_permutation(['13a1'], ['13a2'])
    downloaded 13a2

    - only dev existing and no final available older dev available
    >>> prefer_final_permutation(['15a1'], ['14a1'])
    had 15a1

    - only dev existing and no final available same dev available
    >>> prefer_final_permutation(['16a1'], ['16a1'])
    had 16a1

- Without prefer final:

    >>> _ = zc.buildout.easy_install.prefer_final(False)

    - no existing and newer dev available
    >>> prefer_final_permutation((), [18, '19a1'])
    downloaded 19a1

    - no existing and only dev available
    >>> prefer_final_permutation((), ['20a1'])
    downloaded 20a1

    - final existing and only dev acailable
    >>> prefer_final_permutation([21], ['22a1'])
    downloaded 22a1

    - final existing and newer final available
    >>> prefer_final_permutation([23], [24])
    downloaded 24

    - final existing and same final available
    >>> prefer_final_permutation([25], [25])
    had 25

    - final existing and older final available
    >>> prefer_final_permutation([27], [26])
    had 27

    - only dev existing and final available
    >>> prefer_final_permutation(['29a1'], [28])
    had 29a1

    - only dev existing and no final available newer dev available
    >>> prefer_final_permutation(['30a1'], ['30a2'])
    downloaded 30a2

    - only dev existing and no final available older dev available
    >>> prefer_final_permutation(['32a1'], ['31a1'])
    had 32a1

    - only dev existing and no final available same dev available
    >>> prefer_final_permutation(['33a1'], ['33a1'])
    had 33a1

    >>> _ = zc.buildout.easy_install.prefer_final(True)

    """

def buildout_prefer_final_option():
    """
The prefer-final buildout option can be used for override the default
preference for newer distributions.

The default is prefer-final = false:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = eggs
    ... find-links = %(link_server)s
    ...
    ... [eggs]
    ... recipe = zc.recipe.egg:eggs
    ... eggs = demo
    ... ''' % globals())

    >>> print system(buildout+' -v'), # doctest: +ELLIPSIS
    Installing 'zc.buildout', 'setuptools'.
    ...
    Picked: demo = 0.4c1
    ...
    Picked: demoneeded = 1.2c1

Here we see that the final versions of demo and demoneeded are used.
We get the same behavior if we add prefer-final = false

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = eggs
    ... find-links = %(link_server)s
    ... prefer-final = false
    ...
    ... [eggs]
    ... recipe = zc.recipe.egg:eggs
    ... eggs = demo
    ... ''' % globals())

    >>> print system(buildout+' -v'), # doctest: +ELLIPSIS
    Installing 'zc.buildout', 'setuptools'.
    ...
    Picked: demo = 0.4c1
    ...
    Picked: demoneeded = 1.2c1

If we specify prefer-final = true, we'll get the newest
distributions:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = eggs
    ... find-links = %(link_server)s
    ... prefer-final = true
    ...
    ... [eggs]
    ... recipe = zc.recipe.egg:eggs
    ... eggs = demo
    ... ''' % globals())

    >>> print system(buildout+' -v'), # doctest: +ELLIPSIS
    Installing 'zc.buildout', 'setuptools'.
    ...
    Picked: demo = 0.3
    ...
    Picked: demoneeded = 1.1

We get an error if we specify anything but true or false:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = eggs
    ... find-links = %(link_server)s
    ... prefer-final = no
    ...
    ... [eggs]
    ... recipe = zc.recipe.egg:eggs
    ... eggs = demo
    ... ''' % globals())

    >>> print system(buildout+' -v'), # doctest: +ELLIPSIS
    While:
      Initializing.
    Error: Invalid value for prefer-final option: no

    """

def buildout_prefer_final_build_system_option():
    """
The accept-buildout-test-releases buildout option can be used for overriding
the default preference for final distributions for recipes, buildout
extensions, and buildout itself.  It is usually controlled via the bootstrap
script rather than in the configuration file, but we will test the machinery
using the file.

Set up.  This creates sdists for demorecipe 1.0 and 1.1b1, and for
demoextension 1.0 and 1.1b1.

    >>> create_sample_recipe_sdists(sample_eggs)
    >>> create_sample_extension_sdists(sample_eggs)

The default is accept-buildout-test-releases = false:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = demo
    ... find-links = %(link_server)s
    ... extensions = demoextension
    ...
    ... [demo]
    ... recipe = demorecipe
    ... ''' % globals())

    >>> print system(buildout+' -v'), # doctest: +ELLIPSIS
    Installing ...
    Picked: demoextension = 1.0
    ...
    Picked: demorecipe = 1.0
    ...

Here we see that the final versions of demorecipe and demoextension were used.

We get the same behavior if we explicitly state that
accept-buildout-test-releases = false.

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = demo
    ... find-links = %(link_server)s
    ... extensions = demoextension
    ... accept-buildout-test-releases = false
    ...
    ... [demo]
    ... recipe = demorecipe
    ... ''' % globals())

    >>> print system(buildout+' -v'), # doctest: +ELLIPSIS
    Installing ...
    Picked: demoextension = 1.0
    ...
    Picked: demorecipe = 1.0
    ...

If we specify accept-buildout-test-releases = true, we'll get the newest
distributions in the build system:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = demo
    ... find-links = %(link_server)s
    ... extensions = demoextension
    ... accept-buildout-test-releases = true
    ...
    ... [demo]
    ... recipe = demorecipe
    ... ''' % globals())

    >>> print system(buildout+' -v'), # doctest: +ELLIPSIS
    Installing ...
    Picked: demoextension = 1.1b1
    ...
    Picked: demorecipe = 1.1b1
    ...

We get an error if we specify anything but true or false:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = demo
    ... find-links = %(link_server)s
    ... extensions = demoextension
    ... accept-buildout-test-releases = no
    ...
    ... [demo]
    ... recipe = demorecipe
    ... ''' % globals())

    >>> print system(buildout+' -v'), # doctest: +ELLIPSIS
    While:
      Initializing.
    Error: Invalid value for accept-buildout-test-releases option: no

    """

def develop_with_modules():
    """
Distribution setup scripts can import modules in the distribution directory:

    >>> mkdir('foo')
    >>> write('foo', 'bar.py',
    ... '''# empty
    ... ''')

    >>> write('foo', 'setup.py',
    ... '''
    ... import bar
    ... from setuptools import setup
    ... setup(name="foo")
    ... ''')

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = foo
    ... parts =
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Develop: '/sample-buildout/foo'

    >>> ls('develop-eggs')
    -  foo.egg-link
    -  z3c.recipe.scripts.egg-link
    -  zc.recipe.egg.egg-link

    """

def dont_pick_setuptools_if_version_is_specified_when_required_by_src_dist():
    """
When installing a source distribution, we got setuptools without
honoring our version specification.

    >>> mkdir('dist')
    >>> write('setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(name='foo', version='1', py_modules=['foo'], zip_safe=True)
    ... ''')
    >>> write('foo.py', '')
    >>> _ = system(buildout+' setup . sdist')

    >>> if zc.buildout.easy_install.is_distribute:
    ...     distribute_version = 'distribute = %s' % (
    ...         pkg_resources.working_set.find(
    ...             pkg_resources.Requirement.parse('distribute')).version,)
    ... else:
    ...     distribute_version = ''
    ...
    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = foo
    ... find-links = dist
    ... versions = versions
    ... allow-picked-versions = false
    ...
    ... [versions]
    ... setuptools = %s
    ... foo = 1
    ... %s
    ...
    ... [foo]
    ... recipe = zc.recipe.egg
    ... eggs = foo
    ... ''' % (pkg_resources.working_set.find(
    ...         pkg_resources.Requirement.parse('setuptools')).version,
    ...        distribute_version))

    >>> print system(buildout),
    Installing foo.
    Getting distribution for 'foo==1'.
    Got foo 1.

    """

def pyc_and_pyo_files_have_correct_paths():
    r"""

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = eggs
    ... find-links = %(link_server)s
    ... unzip = true
    ...
    ... [eggs]
    ... recipe = zc.recipe.egg
    ... eggs = demo
    ... interpreter = py
    ... ''' % globals())

    >>> _ = system(buildout)

    >>> write('t.py',
    ... '''
    ... import eggrecipedemo, eggrecipedemoneeded
    ... print eggrecipedemo.main.func_code.co_filename
    ... print eggrecipedemoneeded.f.func_code.co_filename
    ... ''')

    >>> print system(join('bin', 'py')+ ' t.py'),
    /sample-buildout/eggs/demo-0.4c1-py2.4.egg/eggrecipedemo.py
    /sample-buildout/eggs/demoneeded-1.2c1-py2.4.egg/eggrecipedemoneeded.py

    >>> import os
    >>> for name in os.listdir('eggs'):
    ...     if name.startswith('demoneeded'):
    ...         ls('eggs', name)
    d  EGG-INFO
    -  eggrecipedemoneeded.py
    -  eggrecipedemoneeded.pyc
    -  eggrecipedemoneeded.pyo

    """

def dont_mess_with_standard_dirs_with_variable_refs():
    """
    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... eggs-directory = ${buildout:directory}/develop-eggs
    ... parts =
    ... ''' % globals())
    >>> print system(buildout),

    """

def expand_shell_patterns_in_develop_paths():
    """
    Sometimes we want to include a number of eggs in some directory as
    develop eggs, without explicitly listing all of them in our
    buildout.cfg

    >>> make_dist_that_requires(sample_buildout, 'sampley')
    >>> make_dist_that_requires(sample_buildout, 'samplez')

    Now, let's create a buildout that has a shell pattern that matches
    both:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = eggs
    ... develop = sample*
    ... find-links = %(link_server)s
    ...
    ... [eggs]
    ... recipe = zc.recipe.egg
    ... eggs = sampley
    ...        samplez
    ... ''' % globals())

    We can see that both eggs were found:

    >>> print system(buildout),
    Develop: '/sample-buildout/sampley'
    Develop: '/sample-buildout/samplez'
    Installing eggs.

    """

def warn_users_when_expanding_shell_patterns_yields_no_results():
    """
    Sometimes shell patterns do not match anything, so we want to warn
    our users about it...

    >>> make_dist_that_requires(sample_buildout, 'samplea')

    So if we have 2 patterns, one that has a matching directory, and
    another one that does not

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = eggs
    ... develop = samplea grumble*
    ... find-links = %(link_server)s
    ...
    ... [eggs]
    ... recipe = zc.recipe.egg
    ... eggs = samplea
    ... ''' % globals())

    We should get one of the eggs, and a warning for the pattern that
    did not match anything.

    >>> print system(buildout),
    Develop: '/sample-buildout/samplea'
    Couldn't develop '/sample-buildout/grumble*' (not found)
    Installing eggs.

    """

def make_sure_versions_dont_cancel_extras():
    """
    There was a bug that caused extras in requirements to be lost.

    >>> open('setup.py', 'w').write('''
    ... from setuptools import setup
    ... setup(name='extraversiondemo', version='1.0',
    ...       url='x', author='x', author_email='x',
    ...       extras_require=dict(foo=['demo']), py_modules=['t'])
    ... ''')
    >>> open('README', 'w').close()
    >>> open('t.py', 'w').close()

    >>> sdist('.', sample_eggs)
    >>> mkdir('dest')
    >>> ws = zc.buildout.easy_install.install(
    ...     ['extraversiondemo[foo]'], 'dest', links=[sample_eggs],
    ...     versions = dict(extraversiondemo='1.0')
    ... )
    >>> sorted(dist.key for dist in ws)
    ['demo', 'demoneeded', 'extraversiondemo']
    """

def increment_buildout_options():
    r"""
    >>> write('b1.cfg', '''
    ... [buildout]
    ... parts = p1
    ... x = 1
    ... y = a
    ...     b
    ...
    ... [p1]
    ... recipe = zc.buildout:debug
    ... foo = ${buildout:x} ${buildout:y}
    ... ''')

    >>> write('buildout.cfg', '''
    ... [buildout]
    ... extends = b1.cfg
    ... parts += p2
    ... x += 2
    ... y -= a
    ...
    ... [p2]
    ... <= p1
    ... ''')

    >>> print system(buildout),
    Installing p1.
      foo='1\n2 b'
      recipe='zc.buildout:debug'
    Installing p2.
      foo='1\n2 b'
      recipe='zc.buildout:debug'
    """

def increment_buildout_with_multiple_extended_files_421022():
    r"""
    >>> write('foo.cfg', '''
    ... [buildout]
    ... foo-option = foo
    ... [other]
    ... foo-option = foo
    ... ''')
    >>> write('bar.cfg', '''
    ... [buildout]
    ... bar-option = bar
    ... [other]
    ... bar-option = bar
    ... ''')
    >>> write('buildout.cfg', '''
    ... [buildout]
    ... parts = p other
    ... extends = bar.cfg foo.cfg
    ... bar-option += baz
    ... foo-option += ham
    ...
    ... [other]
    ... recipe = zc.buildout:debug
    ... bar-option += baz
    ... foo-option += ham
    ...
    ... [p]
    ... recipe = zc.buildout:debug
    ... x = ${buildout:bar-option} ${buildout:foo-option}
    ... ''')

    >>> print system(buildout),
    Installing p.
      recipe='zc.buildout:debug'
      x='bar\nbaz foo\nham'
    Installing other.
      bar-option='bar\nbaz'
      foo-option='foo\nham'
      recipe='zc.buildout:debug'
    """

def increment_on_command_line():
    r"""
    >>> write('buildout.cfg', '''
    ... [buildout]
    ... parts = p1
    ... x = 1
    ... y = a
    ...     b
    ...
    ... [p1]
    ... recipe = zc.buildout:debug
    ... foo = ${buildout:x} ${buildout:y}
    ...
    ... [p2]
    ... <= p1
    ... ''')

    >>> print system(buildout+' buildout:parts+=p2 p1:foo+=bar'),
    Installing p1.
      foo='1 a\nb\nbar'
      recipe='zc.buildout:debug'
    Installing p2.
      foo='1 a\nb\nbar'
      recipe='zc.buildout:debug'
    """

######################################################################

def make_py_with_system_install(make_py, sample_eggs):
    py_path, site_packages_path = make_py()
    create_sample_namespace_eggs(sample_eggs, site_packages_path)
    return py_path

def create_sample_namespace_eggs(dest, site_packages_path=None):
    from zc.buildout.testing import write, mkdir
    for pkg, version in (('version', '1.0'), ('version', '1.1'),
                         ('fortune', '1.0')):
        tmp = tempfile.mkdtemp()
        try:
            write(tmp, 'README.txt', '')
            mkdir(tmp, 'src')
            mkdir(tmp, 'src', 'tellmy')
            write(tmp, 'src', 'tellmy', '__init__.py',
                "__import__("
                "'pkg_resources').declare_namespace(__name__)\n")
            mkdir(tmp, 'src', 'tellmy', pkg)
            write(tmp, 'src', 'tellmy', pkg,
                  '__init__.py', '__version__=%r\n' % version)
            write(
                tmp, 'setup.py',
                "from setuptools import setup\n"
                "setup(\n"
                " name='tellmy.%(pkg)s',\n"
                " package_dir = {'': 'src'},\n"
                " packages = ['tellmy', 'tellmy.%(pkg)s'],\n"
                " install_requires = ['setuptools'],\n"
                " namespace_packages=['tellmy'],\n"
                " zip_safe=True, version=%(version)r,\n"
                " author='bob', url='bob', author_email='bob')\n"
                % locals()
                )
            zc.buildout.testing.sdist(tmp, dest)
            if (site_packages_path and pkg == 'version' and version == '1.1'):
                # We install the 1.1 version in site packages the way a
                # system packaging system (debs, rpms) would do it.
                zc.buildout.testing.sys_install(tmp, site_packages_path)
        finally:
            shutil.rmtree(tmp)

def create_sample_extension_sdists(dest):
    from zc.buildout.testing import write, mkdir
    name = 'demoextension'
    for version in ('1.0', '1.1b1'):
        tmp = tempfile.mkdtemp()
        try:
            write(tmp, 'README.txt', '')
            write(tmp, name + '.py',
                  "def ext(buildout):\n"
                  "    pass\n"
                  "def unload(buildout):\n"
                  "    pass\n"
                  % locals())
            write(tmp, 'setup.py',
                  "from setuptools import setup\n"
                  "setup(\n"
                  "    name = %(name)r,\n"
                  "    py_modules = [%(name)r],\n"
                  "    entry_points = {\n"
                  "       'zc.buildout.extension': "
                              "['ext = %(name)s:ext'],\n"
                  "       'zc.buildout.unloadextension': "
                              "['ext = %(name)s:unload'],\n"
                  "       },\n"
                  "    zip_safe=True, version=%(version)r,\n"
                  "    author='bob', url='bob', author_email='bob')\n"
                  % locals())
            zc.buildout.testing.sdist(tmp, dest)
        finally:
            shutil.rmtree(tmp)

def create_sample_recipe_sdists(dest):
    from zc.buildout.testing import write, mkdir
    name = 'demorecipe'
    for version in ('1.0', '1.1b1'):
        tmp = tempfile.mkdtemp()
        try:
            write(tmp, 'README.txt', '')
            write(tmp, name + '.py',
                  "import logging, os, zc.buildout\n"
                  "class Demorecipe:\n"
                  "    def __init__(self, buildout, name, options):\n"
                  "        self.name, self.options = name, options\n"
                  "    def install(self):\n"
                  "        return ()\n"
                  "    def update(self):\n"
                  "        pass\n"
                  % locals())
            write(tmp, 'setup.py',
                  "from setuptools import setup\n"
                  "setup(\n"
                  "    name = %(name)r,\n"
                  "    py_modules = [%(name)r],\n"
                  "    entry_points = {'zc.buildout': "
                                       "['default = %(name)s:Demorecipe']},\n"
                  "    zip_safe=True, version=%(version)r,\n"
                  "    author='bob', url='bob', author_email='bob')\n"
                  % locals())
            zc.buildout.testing.sdist(tmp, dest)
        finally:
            shutil.rmtree(tmp)

def _write_eggrecipedemoneeded(tmp, minor_version, suffix=''):
    from zc.buildout.testing import write
    write(tmp, 'README.txt', '')
    write(tmp, 'eggrecipedemoneeded.py',
          'y=%s\ndef f():\n  pass' % minor_version)
    write(
        tmp, 'setup.py',
        "from setuptools import setup\n"
        "setup(name='demoneeded', py_modules=['eggrecipedemoneeded'],"
        " zip_safe=True, version='1.%s%s', author='bob', url='bob', "
        "author_email='bob')\n"
        % (minor_version, suffix)
        )

def _write_eggrecipedemo(tmp, minor_version, suffix=''):
    from zc.buildout.testing import write
    write(tmp, 'README.txt', '')
    write(
        tmp, 'eggrecipedemo.py',
        'import eggrecipedemoneeded\n'
        'x=%s\n'
        'def main(): print x, eggrecipedemoneeded.y\n'
        % minor_version)
    write(
        tmp, 'setup.py',
        "from setuptools import setup\n"
        "setup(name='demo', py_modules=['eggrecipedemo'],"
        " install_requires = 'demoneeded',"
        " entry_points={'console_scripts': "
             "['demo = eggrecipedemo:main']},"
        " zip_safe=True, version='0.%s%s')\n" % (minor_version, suffix)
        )

def create_sample_sys_install(site_packages_path):
    for creator, minor_version in (
        (_write_eggrecipedemoneeded, 1),
        (_write_eggrecipedemo, 3)):
        # Write the files and install in site_packages_path.
        tmp = tempfile.mkdtemp()
        try:
            creator(tmp, minor_version)
            zc.buildout.testing.sys_install(tmp, site_packages_path)
        finally:
            shutil.rmtree(tmp)

def create_sample_eggs(test, executable=sys.executable):
    from zc.buildout.testing import write
    dest = test.globs['sample_eggs']
    tmp = tempfile.mkdtemp()
    try:
        for i in (0, 1, 2):
            suffix = i==2 and 'c1' or ''
            _write_eggrecipedemoneeded(tmp, i, suffix)
            zc.buildout.testing.sdist(tmp, dest)

        write(
            tmp, 'setup.py',
            "from setuptools import setup\n"
            "setup(name='other', zip_safe=False, version='1.0', "
            "py_modules=['eggrecipedemoneeded'])\n"
            )
        zc.buildout.testing.bdist_egg(tmp, executable, dest)

        os.remove(os.path.join(tmp, 'eggrecipedemoneeded.py'))

        for i in (1, 2, 3, 4):
            suffix = i==4 and 'c1' or ''
            _write_eggrecipedemo(tmp, i, suffix)
            zc.buildout.testing.bdist_egg(tmp, executable, dest)

        write(tmp, 'eggrecipebigdemo.py', 'import eggrecipedemo')
        write(
            tmp, 'setup.py',
            "from setuptools import setup\n"
            "setup(name='bigdemo', "
            " install_requires = 'demo',"
            " py_modules=['eggrecipebigdemo'], "
            " zip_safe=True, version='0.1')\n"
            )
        zc.buildout.testing.bdist_egg(tmp, executable, dest)

    finally:
        shutil.rmtree(tmp)

extdemo_c = """
#include <Python.h>
#include <extdemo.h>

static PyMethodDef methods[] = {{NULL}};

PyMODINIT_FUNC
initextdemo(void)
{
    PyObject *m;
    m = Py_InitModule3("extdemo", methods, "");
#ifdef TWO
    PyModule_AddObject(m, "val", PyInt_FromLong(2));
#else
    PyModule_AddObject(m, "val", PyInt_FromLong(EXTDEMO));
#endif
}
"""

extdemo_setup_py = """
import os
from distutils.core import setup, Extension

if os.environ.get('test-variable'):
    print "Have environment test-variable:", os.environ['test-variable']

setup(name = "extdemo", version = "%s", url="http://www.zope.org",
      author="Demo", author_email="demo@demo.com",
      ext_modules = [Extension('extdemo', ['extdemo.c'])],
      )
"""

def add_source_dist(test, version=1.4):

    if 'extdemo' not in test.globs:
        test.globs['extdemo'] = test.globs['tmpdir']('extdemo')

    tmp = test.globs['extdemo']
    write = test.globs['write']
    try:
        write(tmp, 'extdemo.c', extdemo_c);
        write(tmp, 'setup.py', extdemo_setup_py % version);
        write(tmp, 'README', "");
        write(tmp, 'MANIFEST.in', "include *.c\n");
        test.globs['sdist'](tmp, test.globs['sample_eggs'])
    except:
        shutil.rmtree(tmp)

def easy_install_SetUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    sample_eggs = test.globs['tmpdir']('sample_eggs')
    test.globs['sample_eggs'] = sample_eggs
    os.mkdir(os.path.join(sample_eggs, 'index'))
    create_sample_eggs(test)
    add_source_dist(test)
    test.globs['link_server'] = test.globs['start_server'](
        test.globs['sample_eggs'])
    test.globs['update_extdemo'] = lambda : add_source_dist(test, 1.5)
    zc.buildout.testing.install_develop('zc.recipe.egg', test)
    zc.buildout.testing.install_develop('z3c.recipe.scripts', test)

egg_parse = re.compile('([0-9a-zA-Z_.]+)-([0-9a-zA-Z_.]+)-py(\d[.]\d).egg$'
                       ).match
def makeNewRelease(project, ws, dest, version='99.99'):
    dist = ws.find(pkg_resources.Requirement.parse(project))
    eggname, oldver, pyver = egg_parse(
        os.path.basename(dist.location)
        ).groups()
    dest = os.path.join(dest, "%s-%s-py%s.egg" % (eggname, version, pyver))
    if os.path.isfile(dist.location):
        shutil.copy(dist.location, dest)
        zip = zipfile.ZipFile(dest, 'a')
        zip.writestr(
            'EGG-INFO/PKG-INFO',
            zip.read('EGG-INFO/PKG-INFO').replace("Version: %s" % oldver,
                                                  "Version: %s" % version)
            )
        zip.close()
    else:
        shutil.copytree(dist.location, dest)
        info_path = os.path.join(dest, 'EGG-INFO', 'PKG-INFO')
        info = open(info_path).read().replace("Version: %s" % oldver,
                                              "Version: %s" % version)
        open(info_path, 'w').write(info)

def getWorkingSetWithBuildoutEgg(test):
    sample_buildout = test.globs['sample_buildout']
    eggs = os.path.join(sample_buildout, 'eggs')

    # If the zc.buildout dist is a develop dist, convert it to a
    # regular egg in the sample buildout
    req = pkg_resources.Requirement.parse('zc.buildout')
    dist = pkg_resources.working_set.find(req)
    if dist.precedence == pkg_resources.DEVELOP_DIST:
        # We have a develop egg, create a real egg for it:
        here = os.getcwd()
        os.chdir(os.path.dirname(dist.location))
        assert os.spawnle(
            os.P_WAIT, sys.executable,
            zc.buildout.easy_install._safe_arg(sys.executable),
            os.path.join(os.path.dirname(dist.location), 'setup.py'),
            '-q', 'bdist_egg', '-d', eggs,
            dict(os.environ,
                 PYTHONPATH=pkg_resources.working_set.find(
                               pkg_resources.Requirement.parse('setuptools')
                               ).location,
                 ),
            ) == 0
        os.chdir(here)
        os.remove(os.path.join(eggs, 'zc.buildout.egg-link'))

        # Rebuild the buildout script
        ws = pkg_resources.WorkingSet([eggs])
        ws.require('zc.buildout')
        zc.buildout.easy_install.scripts(
            ['zc.buildout'], ws, sys.executable,
            os.path.join(sample_buildout, 'bin'))
    else:
        ws = pkg_resources.working_set
    return ws

def updateSetup(test):
    zc.buildout.testing.buildoutSetUp(test)
    new_releases = test.globs['tmpdir']('new_releases')
    test.globs['new_releases'] = new_releases
    ws = getWorkingSetWithBuildoutEgg(test)
    # now let's make the new releases
    makeNewRelease('zc.buildout', ws, new_releases)
    makeNewRelease('zc.buildout', ws, new_releases, '100.0b1')
    os.mkdir(os.path.join(new_releases, 'zc.buildout'))
    if zc.buildout.easy_install.is_distribute:
        makeNewRelease('distribute', ws, new_releases)
        os.mkdir(os.path.join(new_releases, 'distribute'))
    else:
        makeNewRelease('setuptools', ws, new_releases)
        os.mkdir(os.path.join(new_releases, 'setuptools'))

def bootstrapSetup(test):
    easy_install_SetUp(test)
    sample_eggs = test.globs['sample_eggs']
    ws = getWorkingSetWithBuildoutEgg(test)
    makeNewRelease('zc.buildout', ws, sample_eggs)
    makeNewRelease('zc.buildout', ws, sample_eggs, '100.0b1')
    os.environ['bootstrap-testing-find-links'] = test.globs['link_server']

normalize_bang = (
    re.compile(re.escape('#!'+
                         zc.buildout.easy_install._safe_arg(sys.executable))),
    '#!/usr/local/bin/python2.4',
    )

hide_distribute_additions = (re.compile('install_dir .+\n'), '')
hide_zip_safe_message = (
    # This comes in a different place in the output in Python 2.7.  It's not
    # important to our tests.  Hide it.
    re.compile(
        '((?<=\n)\n)?zip_safe flag not set; analyzing archive contents...\n'),
    '')
hide_first_index_page_message = (
    # This comes in a different place in the output in Python 2.7.  It's not
    # important to our tests.  Hide it.
    re.compile(
        "Couldn't find index page for '[^']+' \(maybe misspelled\?\)\n"),
    '')
def test_suite():
    test_suite = [
        doctest.DocFileSuite(
            'buildout.txt', 'runsetup.txt', 'repeatable.txt', 'setup.txt',
            setUp=zc.buildout.testing.buildoutSetUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            checker=renormalizing.RENormalizing([
                zc.buildout.testing.normalize_path,
                zc.buildout.testing.normalize_endings,
                zc.buildout.testing.normalize_script,
                zc.buildout.testing.normalize_egg_py,
                zc.buildout.tests.hide_distribute_additions,
                hide_zip_safe_message,
                (re.compile('__buildout_signature__ = recipes-\S+'),
                 '__buildout_signature__ = recipes-SSSSSSSSSSS'),
                (re.compile('executable = [\S ]+python\S*', re.I),
                 'executable = python'),
                (re.compile('[-d]  (setuptools|distribute)-\S+[.]egg'),
                 'setuptools.egg'),
                (re.compile('zc.buildout(-\S+)?[.]egg(-link)?'),
                 'zc.buildout.egg'),
                (re.compile('creating \S*setup.cfg'), 'creating setup.cfg'),
                (re.compile('hello\%ssetup' % os.path.sep), 'hello/setup'),
                (re.compile('Picked: (\S+) = \S+'),
                 'Picked: \\1 = V.V'),
                (re.compile(r'We have a develop egg: zc.buildout (\S+)'),
                 'We have a develop egg: zc.buildout X.X.'),
                (re.compile(r'\\[\\]?'), '/'),
                (re.compile('WindowsError'), 'OSError'),
                (re.compile(r'\[Error \d+\] Cannot create a file '
                            r'when that file already exists: '),
                 '[Errno 17] File exists: '
                 ),
                (re.compile('distribute'), 'setuptools'),
                ])
            ),
        doctest.DocFileSuite(
            'debugging.txt',
            setUp=zc.buildout.testing.buildoutSetUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            checker=renormalizing.RENormalizing([
                zc.buildout.testing.normalize_path,
                zc.buildout.testing.normalize_endings,
                zc.buildout.tests.hide_distribute_additions,
                (re.compile(r'\S+buildout.py'), 'buildout.py'),
                (re.compile(r'line \d+'), 'line NNN'),
                (re.compile(r'py\(\d+\)'), 'py(NNN)'),
                ])
            ),

        doctest.DocFileSuite(
            'update.txt',
            setUp=updateSetup,
            tearDown=zc.buildout.testing.buildoutTearDown,
            checker=renormalizing.RENormalizing([
                zc.buildout.testing.normalize_path,
                zc.buildout.testing.normalize_endings,
                zc.buildout.testing.normalize_script,
                zc.buildout.testing.normalize_egg_py,
                normalize_bang,
                zc.buildout.tests.hide_distribute_additions,
                (re.compile('99[.]99'), 'NINETYNINE.NINETYNINE'),
                (re.compile('(zc.buildout|setuptools)-\d+[.]\d+\S*'
                            '-py\d.\d.egg'),
                 '\\1.egg'),
                (re.compile('distribute-\d+[.]\d+\S*'
                            '-py\d.\d.egg'),
                 'setuptools.egg'),
                (re.compile('(zc.buildout|setuptools)( version)? \d+[.]\d+\S*'),
                 '\\1 V.V'),
                (re.compile('distribute( version)? \d+[.]\d+\S*'),
                 'setuptools V.V'),
                (re.compile('[-d]  (setuptools|distribute)'), '-  setuptools'),
                (re.compile('distribute'), 'setuptools'),
                (re.compile("\nUnused options for buildout: "
                            "'(distribute|setuptools)\-version'\."),
                 '')
                ])
            ),

        doctest.DocFileSuite(
            'easy_install.txt', 'downloadcache.txt', 'dependencylinks.txt',
            'allowhosts.txt', 'unzip.txt', 'upgrading_distribute.txt',
            setUp=easy_install_SetUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            checker=renormalizing.RENormalizing([
                zc.buildout.testing.normalize_path,
                zc.buildout.testing.normalize_endings,
                zc.buildout.testing.normalize_script,
                zc.buildout.testing.normalize_egg_py,
                normalize_bang,
                hide_first_index_page_message,
                zc.buildout.tests.hide_distribute_additions,
                (re.compile('extdemo[.]pyd'), 'extdemo.so'),
                (re.compile('[-d]  (setuptools|distribute)-\S+[.]egg'),
                 'setuptools.egg'),
                (re.compile(r'\\[\\]?'), '/'),
                (re.compile(r'\#!\S+\bpython\S*'), '#!/usr/bin/python'),
                # Normalize generate_script's Windows interpreter to UNIX:
                (re.compile(r'\nimport subprocess\n'), '\n'),
                (re.compile('subprocess\\.call\\(argv, env=environ\\)'),
                 'os.execve(sys.executable, argv, environ)'),
                (re.compile('distribute'), 'setuptools'),
                # Distribute unzips eggs by default.
                (re.compile('\-  demoneeded'), 'd  demoneeded'),
                ]+(sys.version_info < (2, 5) and [
                   (re.compile('.*No module named runpy.*', re.S), ''),
                   (re.compile('.*usage: pdb.py scriptfile .*', re.S), ''),
                   (re.compile('.*Error: what does not exist.*', re.S), ''),
                   ] or [])),
            ),

        doctest.DocFileSuite(
            'download.txt', 'extends-cache.txt',
            setUp=easy_install_SetUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
            checker=renormalizing.RENormalizing([
               (re.compile(' at -?0x[^>]+'), '<MEM ADDRESS>'),
               (re.compile('http://localhost:[0-9]{4,5}/'),
                'http://localhost/'),
               (re.compile('[0-9a-f]{32}'), '<MD5 CHECKSUM>'),
               zc.buildout.testing.normalize_path,
               ]),
            ),

        doctest.DocTestSuite(
            setUp=easy_install_SetUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            checker=renormalizing.RENormalizing([
                zc.buildout.testing.normalize_path,
                zc.buildout.testing.normalize_endings,
                zc.buildout.testing.normalize_script,
                zc.buildout.testing.normalize_egg_py,
                zc.buildout.tests.hide_distribute_additions,
                hide_first_index_page_message,
                (re.compile("buildout: Running \S*setup.py"),
                 'buildout: Running setup.py'),
                (re.compile('(setuptools|distribute)-\S+-'),
                 'setuptools.egg'),
                (re.compile('zc.buildout-\S+-'),
                 'zc.buildout.egg'),
                (re.compile('File "\S+one.py"'),
                 'File "one.py"'),
                (re.compile(r'We have a develop egg: (\S+) (\S+)'),
                 r'We have a develop egg: \1 V'),
                (re.compile('Picked: (setuptools|distribute) = \S+'),
                 'Picked: setuptools = V'),
                (re.compile(r'\\[\\]?'), '/'),
                (re.compile(
                    '-q develop -mxN -d "/sample-buildout/develop-eggs'),
                    '-q develop -mxN -d /sample-buildout/develop-eggs'
                 ),
                (re.compile(r'^[*]...'), '...'),
                # for bug_92891_bootstrap_crashes_with_egg_recipe_in_buildout_section
                (re.compile(r"Unused options for buildout: 'eggs' 'scripts'\."),
                 "Unused options for buildout: 'scripts' 'eggs'."),
                (re.compile('distribute'), 'setuptools'),
                # Distribute unzips eggs by default.
                (re.compile('\-  demoneeded'), 'd  demoneeded'),
                ]),
            ),
        zc.buildout.testselectingpython.test_suite(),
        zc.buildout.rmtree.test_suite(),
        doctest.DocFileSuite(
            'windows.txt',
            setUp=zc.buildout.testing.buildoutSetUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            checker=renormalizing.RENormalizing([
                zc.buildout.testing.normalize_path,
                zc.buildout.testing.normalize_endings,
                zc.buildout.testing.normalize_script,
                zc.buildout.testing.normalize_egg_py,
                zc.buildout.tests.hide_distribute_additions,
                (re.compile('__buildout_signature__ = recipes-\S+'),
                 '__buildout_signature__ = recipes-SSSSSSSSSSS'),
                (re.compile('[-d]  setuptools-\S+[.]egg'), 'setuptools.egg'),
                (re.compile('zc.buildout(-\S+)?[.]egg(-link)?'),
                 'zc.buildout.egg'),
                (re.compile('creating \S*setup.cfg'), 'creating setup.cfg'),
                (re.compile('hello\%ssetup' % os.path.sep), 'hello/setup'),
                (re.compile('Picked: (\S+) = \S+'),
                 'Picked: \\1 = V.V'),
                (re.compile(r'We have a develop egg: zc.buildout (\S+)'),
                 'We have a develop egg: zc.buildout X.X.'),
                (re.compile(r'\\[\\]?'), '/'),
                (re.compile('WindowsError'), 'OSError'),
                (re.compile(r'\[Error 17\] Cannot create a file '
                            r'when that file already exists: '),
                 '[Errno 17] File exists: '
                 ),
                ])
            ),
        doctest.DocFileSuite(
            'testing_bugfix.txt',
            checker=renormalizing.RENormalizing([
                # Python 2.7
                (re.compile(
                    re.escape(
                        'testrunner.logsupport.NullHandler instance at')),
                 'testrunner.logsupport.NullHandler object at'),
                (re.compile(re.escape('logging.StreamHandler instance at')),
                 'logging.StreamHandler object at'),
                ])
            ),
    ]

    # adding bootstrap.txt doctest to the suite
    # only if bootstrap.py is present
    bootstrap_py = os.path.join(
       os.path.dirname(
          os.path.dirname(
             os.path.dirname(
                os.path.dirname(zc.buildout.__file__)
                )
             )
          ),
       'bootstrap', 'bootstrap.py')

    if os.path.exists(bootstrap_py):
        test_suite.append(doctest.DocFileSuite(
            'bootstrap.txt',
            setUp=bootstrapSetup,
            tearDown=zc.buildout.testing.buildoutTearDown,
            checker=renormalizing.RENormalizing([
                zc.buildout.testing.normalize_path,
                zc.buildout.testing.normalize_endings,
                zc.buildout.testing.normalize_script,
                zc.buildout.testing.normalize_egg_py,
                normalize_bang,
                (re.compile('Downloading.*setuptools.*egg\n'), ''),
                (re.compile('options:'), 'Options:'),
                (re.compile('usage:'), 'Usage:'),
                ]),
            ))
        test_suite.append(doctest.DocFileSuite(
            'virtualenv.txt',
            setUp=easy_install_SetUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            checker=renormalizing.RENormalizing([
                zc.buildout.testing.normalize_path,
                zc.buildout.testing.normalize_endings,
                zc.buildout.testing.normalize_script,
                zc.buildout.testing.normalize_egg_py,
                zc.buildout.tests.hide_distribute_additions,
                (re.compile('(setuptools|distribute)-\S+-'),
                 'setuptools.egg'),
                (re.compile('zc.buildout-\S+-'),
                 'zc.buildout.egg'),
                (re.compile(re.escape('#!"/executable_buildout/bin/py"')),
                 '#!/executable_buildout/bin/py'), # Windows.
                (re.compile(re.escape('/broken_s/')),
                 '/broken_S/'), # Windows.
                ]),
            ))

    return unittest.TestSuite(test_suite)
