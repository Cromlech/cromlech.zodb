# -*- coding: utf-8 -*-

from cromlech.io.interfaces import IPublicationRoot
from zope.interface import alsoProvides


class Connection(object):

    def __init__(self, key, db):
        self.key = key
        self.conn = db.open()       

    def __enter__(self, environ, start_response, app):
        environ[self.key] = self.conn
        result = app(environ, start_response)
        del environ[self.key]
        return result

    def __exit__(self, type, value, traceback):
        self.conn.close()



class ZodbSite(object):
    """Controled execution, using a ZODB-dwelling object as
    a publication root. This relies on `zc.zodbwsgi` to extract
    the connection pointer from the WSGI environ.
    """

    def __init__(self, environ, name):
        self.environ = environ
        self.name = name

    def __enter__(self):
        root = self.environ['zodb.connection'].root()
        site = root.get(self.name)
        if site is None:
            self.environ['zodb.connection'].transaction_manager.get().abort()
            self.environ['zodb.connection'].close()
            raise RuntimeError("Site %r doesn't exist" % self.name)
        alsoProvides(site, IPublicationRoot)
        return site

    def __exit__(self, type, value, traceback):
        conn = self.environ['zodb.connection']
        if type is None:
            conn.transaction_manager.get().commit()
        else:
            conn.transaction_manager.get().abort()
        conn.close()
