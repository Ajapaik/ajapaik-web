# Copyright (c) 2007-2008 Infrae. All rights reserved.
# $Id: Native.py 33170 2009-01-21 15:46:45Z sylvain $

from pysvn import wc_status_kind, opt_revision_kind, wc_notify_action
import pysvn

from Common import BaseRecipe, prepareURLs
from Common import checkAddedPaths, checkExistPath, reportInvalidFiles

import os
import re
import getpass


def createSVNClient(recipe):
    """Create a pysvn client, and setup some callback and options.
    """

    def callback_ssl(info):
        print "-------- SECURITY WARNING --------"
        print "There is no valid SSL certificat for %s." % info['realm']
        print "Check that the files are correct after being fetched."
        print "-------- SECURITY WARNING --------"
        return True, 0, False

    def callback_login(realm, username, may_save):
        print 'Authentication realm: ' + realm
        user = raw_input('Username: ')
        password = getpass.getpass('Password for ' + "'" + user + "': ")
        return True, user, password, True

    def callback_notify(info):
        if info['action'] == wc_notify_action.update_completed:
            path = info['path']
            url = recipe.urls.get(path, None)
            if not (url is None):
                recipe._updateRevisionInformation(url, path, info['revision'])

    client = pysvn.Client()
    client.set_interactive(True)
    client.callback_ssl_server_trust_prompt = callback_ssl
    client.callback_get_login = callback_login
    if not (recipe is None):
        client.callback_notify = callback_notify
    return client


class Recipe(BaseRecipe):
    """infrae.subversion recipe.
    """

    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)
        if self.verbose:
            print 'Using pysvn implementation.'
        self.client = createSVNClient(self)
        if not self.export:
            self._updateAllRevisionInformation()
        self._exportInformationToOptions()

    def _updateRevisionInformation(self, link, path, revision=None):
        """Update revision information on a path.
        """
        if revision is None:
            if self.export:
                return
            info = self.client.info(path)
            revision = info['revision']

        assert (revision.kind == opt_revision_kind.number)
        super(Recipe, self)._updateRevisionInformation(link, revision.number)

    def _updatePath(self, link, path):
        """Update a single path.
        """
        self.client.update(path)

    def _parseRevisionInUrl(self, url):
        """Parse URL to extract revision number. This is not done by
        pysvn, so we have to do it by ourself.
        """
        num_release = re.compile('(.*)@([0-9]+)$')
        match = num_release.match(url)
        if match:
            return (match.group(1),
                    pysvn.Revision(opt_revision_kind.number,
                                   int(match.group(2))))
        return (url, pysvn.Revision(opt_revision_kind.head))

    def _installPath(self, link, path):
        """Checkout a single entry.
        """
        link, wanted_revision = self._parseRevisionInUrl(link)
        if self.export:
            method = self.client.export
        else:
            method = self.client.checkout
        method(link, path, revision=wanted_revision, recurse=True)


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
    client = createSVNClient(None)

    bad_svn_status = [wc_status_kind.modified,
                      wc_status_kind.missing,
                      wc_status_kind.unversioned, ]

    if not checkExistPath(location):
        return

    checkAddedPaths(location, urls)

    for path in urls.keys():
        if not checkExistPath(path):
            continue

        badfiles = filter(lambda e: e['text_status'] in bad_svn_status,
                          client.status(path))
        reportInvalidFiles(path, name, [file['path'] for file in badfiles])
