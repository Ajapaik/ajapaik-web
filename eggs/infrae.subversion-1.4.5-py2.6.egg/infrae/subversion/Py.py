# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: Py.py 32775 2009-01-05 10:53:29Z sylvain $

import os
import py

from Common import BaseRecipe, prepareURLs
from Common import checkAddedPaths, checkExistPath, reportInvalidFiles


class Recipe(BaseRecipe):
    """infrae.subversion recipe.
    """

    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)
        if self.verbose:
            print 'Using py implementation.'
        if not self.offline:    # Py is not able to do svn status
                                # without asking something on a
                                # server.
            self._updateAllRevisionInformation()
        self._exportInformationToOptions()

    def _updateRevisionInformation(self, link, path):
        """Update revision information on a path.
        """
        if isinstance(path, str):
            path = py.path.svnwc(path)

        revision = path.status().rev
        super(Recipe, self)._updateRevisionInformation(link, revision)

    def _updatePath(self, link, path):
        """Update a single path.
        """
        wc = py.path.svnwc(path)
        wc.update()
        self._updateRevisionInformation(link, wc)

    def _installPath(self, link, path):
        """Checkout a single entry.
        """
        if self.export:
            raise NotImplementedError
        wc = py.path.svnwc(path)
        wc.checkout(link)
        self._updateRevisionInformation(link, wc)


def uninstall(name, options):
    r"""
    This is an uninstallation hook for the 'infrae.subversion' recipe.

    Its only job is to raise an exception when there are changes in a
    subversion tree that a user might not want to lose.  This function
    does *not* delete or otherwise touch any files.

    The location of the path is passed as options['location'].
    """
    if bool(options.get('export', False)):
        return                  # SVN Export, there is nothing to check.

    if bool(options.get('ignore_verification', False)):
        return                  # Verification disabled.


    # XXX This makes the assumption that we're in the buildout
    #     directory and that our part is in 'parts'.  We don't have
    #     options['buildout'] available so no
    #     'buildout:parts-directory'.
    location = options.get('location', os.path.join('.', 'parts', name))
    urls = prepareURLs(location, options['urls'])

    if not checkExistPath(location):
        return

    checkAddedPaths(location, urls)

    for path in urls.keys():
        if not checkExistPath(path):
            continue

        wc = py.path.svnwc(path)
        status = wc.status(rec=1)
        badfiles = [] + status.modified + status.incomplete + status.unknown
        reportInvalidFiles(path, name, [file.strpath for file in badfiles])
