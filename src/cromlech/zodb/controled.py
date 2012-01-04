# -*- coding: utf-8 -*-

import transaction
from cromlech.io.interfaces import IPublicationRoot
from zope.interface import alsoProvides


def transaction_wrapper(app, key):
    def transaction_aware_app(environ, start_response):
        tm = environ[key] = transaction.TransactionManager()
        try:
            try:
                print "running the transaction aware app"
                result = app(environ, start_response)
            except:
                tm.get().abort()
                raise
            else:
                tm.get().commit()
            return result
        finally:
            del environ[key]
    return transaction_aware_app


class Connection(object):

    def __init__(self, key, db):
        self.key = key
        self.conn = db.open()

    def __enter__(self):
        def wrapper(environ, start_response, app):
            environ[self.key] = self.conn
            result = app(environ, start_response)
            del environ[self.key]
            return result
        return wrapper

    def __exit__(self, type, value, traceback):
        self.conn.close()


class ZODBSiteManager(object):

    def __init__(self, key, name):
        self.name = name
        self.key = key

    def get_from_conn(self, conn):
        root = conn.root()
        site = root.get(self.name)
        if site is None:
            raise RuntimeError("Site %s doesn't exist in the current ZODB.")
        return site

    def __call__(self, environ):
        conn = environ[self.key]
        return self.get_from_conn(conn)
