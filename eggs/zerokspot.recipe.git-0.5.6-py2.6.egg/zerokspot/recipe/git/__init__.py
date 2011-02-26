"""
zerokspot.recipe.git is a small recipe that allows you to use git
repositories in a similar way like iw.recipe.subversion does for
subversion repositories::

    [myapp]
    recipe = zerokspot.recipe.git
    repository = <url-of-repository>
    paths = <relative-paths-to-packages-inside-repository>
    branch = <name-of-branch> # default: "master"
    rev = <name-of-revision> # default: None
    newest = [true|false] # default: false, stay up to date even when
                          # when updating unless rev is set
    as_egg = [true|false] # default: false, install the fetched repo as
                          # egg
    cache-name = <name-in-download-cache> # default: None

This would store the cloned repository in ${buildout:directory}/parts/myapp.
"""

import subprocess
import os.path
import zc.buildout
import shutil


def git(operation, args, message, ignore_errnos=None, verbose=False):
    """
    Execute a git operation with the given arguments. If it fails, raise an
    exception with the given message. If ignore_errnos is a list of status
    codes, they will be not handled as errors if returned by git.
    """
    if verbose:
        real_args = list(args)
    else:
        real_args = ['-q'] + list(args)
    
    command = r'git %s ' + ' '.join(('"%s"', ) * len(real_args))
    command = command % ((operation, ) + tuple(real_args))
    status = subprocess.call(command, shell=True)
    if ignore_errnos is None:
        ignore_errnos = []
    if status != 0 and status not in ignore_errnos:
        raise zc.buildout.UserError(message)


def get_reponame(url, branch = None, rev = None):
    """
    Given the URL of a repository, this function returns the name of it after
    a clone process.
    """
    base = filter(lambda x: len(x), url.split('/'))[-1]
    if base.endswith('.git'):
        base = base[:-4]

    if rev != None or branch != None:
        base = base + '@' + (rev or branch)
    return base


class Recipe(object):
    """
    This recipe supports following options:

    repository
        Path to the repository that should be cloned

    branch
        Which branch should be cloned. If none is given, "master" is used by
        default.

    rev
        Revision that should be used. This is useful if you want to freeze
        the source at a given revision. If this is used, an update won't do
        all that much when executed.
        
    paths
        List of relative paths to packages to develop. Must be used together
        with as_egg=true.
        
    as_egg
        Set to True if you want the checkout to be registered as a
        development egg in your buildout.
        
    """

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.repository = options['repository']
        self.branch = options.get('branch', 'master')
        self.rev = options.get('rev', None)
        self.newest = options.get('newest',
                buildout['buildout'].get('newest', "false")).lower() == 'true'
        self.offline = options.get('offline', 'false').lower() == 'true'
        self.cache_install = self.offline or options.get('install-from-cache',
                buildout['buildout'].get('install-from-cache', 'false')) \
                        .lower() == 'true'
        self.cache_name = options.get('cache-name',
                get_reponame(self.repository))
        self.download_cache = self.buildout['buildout'] \
                .get('download-cache', None)
        if self.download_cache:
            self.cache_path = os.path.join(
                    buildout['buildout']['download-cache'],
                    self.cache_name)
        else:
            self.cache_path = None
        options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], name)
        self.as_egg = options.get('as_egg', 'false').lower() == 'true'
        self.root_dir = self.buildout['buildout']['directory']
        self.cache_created = False
        self.cache_updated = False
        self.part_updated = False
        self.cache_cloned = False
        self.installed_from_cache = False
        self.paths = options.get('paths', None)
        self.verbose = int(buildout['buildout'].get('verbosity', 0)) > 0

    def install(self):
        """
        Method called when installing a part (or when the part's config
        was changed. It clones the the given git repository and checks
        out the requested branch or commit.

        Returns the path to the part's directory.
        """
        if self.cache_install:
            if not self.download_cache:
                raise zc.buildout.UserError("Offline mode requested and no "
                                            "download-cache specified")
            if os.path.exists(self.cache_path):
                self._clone_cache()
                self.installed_from_cache = True
            else:
                raise zc.buildout.UserError("No repository in the download "
                                            "cache directory.")
        else:
            if self.download_cache:
                if not os.path.exists(self.cache_path):
                    self._clone_upstream()
                if self.newest:
                    # Update the cache first
                    self._update_cache()
                else:
                    self.installed_from_cache = True
                self._clone_cache()
            else:
                self._clone(self.repository, self.options['location'])
        if self.as_egg:
            self._install_as_egg()
        return self.options['location']

    def update(self):
        """
        Called when the buildout is called again without the local
        configuration having been altered. If no revision was
        requested and the newest-option enabled it tries to update the
        requested branch.
        """
        if self.rev is None and self.newest:
            # Do an update of the current branch
            if self.verbose:
                print "Pulling updates from origin"
            if not self.cache_install and self.download_cache:
                self._update_cache()
            self._update_part()
            os.chdir(self.options['location'])
            if self.as_egg:
                self._install_as_egg()
        else:
            # "newest" is also automatically disabled if "offline"
            # is set.
            if self.verbose:
                print "Pulling disable for this part"

    def _clone(self, from_, to):
        """
        Clone a repository located at ``from_`` to ``to``.
        """
        try:
            git('clone', (from_, to), "Couldn't clone %s into %s" % (
                    from_, to, ))
            os.chdir(to)

            if self.branch != 'master':
                if not '[branch "%s"]' % self.branch in open(os.path.join('.git', 'config')).read():
                    git('branch', ('--track', self.branch, 'origin/%s' % self.branch),
                        "Failed to set up to track remote branch", verbose=True)
                if not "ref: refs/heads/%s" % self.branch in open(os.path.join('.git', 'HEAD')).read():
                    git('checkout', (self.branch,), "Failed to switch to branch '%s'" % self.branch,
                        ignore_errnos=[128])

            if self.rev is not None:
                git('checkout', (self.rev, ), "Failed to checkout revision")
        finally:
            os.chdir(self.root_dir)

    def _clone_cache(self):
        """
        Clone the cache into the parts directory.
        """
        if not os.path.exists(self.cache_path):
            self._clone_upstream()
        self._clone(self.cache_path, self.options['location'])
        self.cache_cloned = True

    def _clone_upstream(self):
        """
        Clone the upstream repository into the cache
        """
        self._clone(self.repository, self.cache_path)
        self.cache_created = True

    def _update_cache(self):
        """
        Updates the cached repository.
        """
        self._update_repository(self.cache_path)
        self.cache_updated = True

    def _update_part(self):
        """
        Updates the repository in the buildout's parts directory.
        """
        self._update_repository(self.options['location'])
        self.part_updated = True

    def _update_repository(self, path):
        """
        Update the repository from the given path
        """
        try:
            os.chdir(path)
            git('pull', ('origin', self.branch, ),
                    "Failed to update repository")
        finally:
            os.chdir(self.root_dir)

    def _install_as_egg(self):
        """
        Install clone as development egg.
        """
        def _install(path, target):
            zc.buildout.easy_install.develop(path, target)
            
        target = self.buildout['buildout']['develop-eggs-directory']
        if self.paths:
            for path in self.paths.split():
                path = os.path.join(self.options['location'], path.strip())
                _install(path, target)
        else:
            _install(self.options['location'], target)
