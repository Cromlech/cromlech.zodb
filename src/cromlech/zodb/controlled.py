# -*- coding: utf-8 -*-

import transaction


def transaction_wrapper(app, transaction_manager):
    def transaction_aware_app(environ, start_response):
        try:
            result = app(environ, start_response)
        except:
            transaction_manager.get().abort()
            raise
        else:
            transaction_manager.get().commit()
        return result
    return transaction_aware_app


class Connection(object):

    conn = None

    def __init__(self, db, connection_key):
        self.db = db
        self.connection_key = connection_key

    def __enter__(self):
        def wrapper(app, environ, start_response):
            self.conn = environ[self.connection_key] = self.db.open()
            try:
                return app(environ, start_response)
            finally:
                del environ[self.connection_key]
        return wrapper

    def __exit__(self, type, value, traceback):
        if self.conn is not None:
            self.conn.close()


class ConnectionWithTransaction(Connection):

    tm_factory = transaction.TransactionManager

    def __init__(self, db, connection_key, transaction_key):
        Connection.__init__(self, db, connection_key)
        self.transaction_key = transaction_key

    def __enter__(self):
        def wrapper(app, environ, start_response):
            tm = environ[self.transaction_key] = self.tm_factory()
            self.conn = environ[self.connection_key] = self.db.open(tm)
            app = transaction_wrapper(app, tm)
            try:
                return app(environ, start_response)
            finally:
                del environ[self.transaction_key]
                del environ[self.connection_key]
        return wrapper


class ZODBSiteManager(object):
    """This simple factory is a way to retrieve a site from the DB conn.
    """
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


class ZODBSiteWithTransaction(ZODBSiteManager):
    """This execution controller is mainly used outside of the context
    of a wsgi application. It assumes that you don't have a current
    active transaction. The controller returns a factory, using the environ.
    """

    connection = None
    transaction_manager = None
    tm_factory = transaction.TransactionManager

    def __init__(self, db, key, name):
        self.db = db
        self.key = key
        self.name = name

    def __enter__(self):
        def transaction_site(environ):
            self.transaction_manager = environ[self.key] = self.tm_factory()
            self.connection = self.db.open(self.transaction_manager)
            site = self.get_from_conn(self.connection)
            self.transaction_manager.begin()
            return site
        return transaction_site

    def __exit__(self, type, value, traceback):
        if self.transaction_manager is not None:
            if value:
                self.transaction_manager.get().abort()
            else:
                self.transaction_manager.get().commit()
        if self.connection is not None:
            self.connection.close()
