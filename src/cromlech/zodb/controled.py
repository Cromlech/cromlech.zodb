# -*- coding: utf-8 -*-

from cromlech.io.interfaces import IPublicationRoot
from zope.interface import alsoProvides


class ZodbSite(object):
    """Controled execution, using a ZODB-dwelling object as
    a publication root. This relies on `zc.zodbwsgi` to extract
    the connection pointer from the WSGI environ.
    """

    def __init__(self, environ, name):
        """
        """
        self.environ = environ
        self.name = name

    def __enter__(self):
        root = self.environ['zodb.connection'].root()
        site = root.get(self.name)
        alsoProvides(site, IPublicationRoot)
        if site is None:
            raise RuntimeError("Site %r doesn't exist" % self.name)
        return site

    def __exit__(self, type, value, traceback):
        self.environ['zodb.connection'].close()
