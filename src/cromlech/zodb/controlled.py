# -*- coding: utf-8 -*-
from zope.component.hooks import setSite


def close(conn):
    """This is the default callback() to close a connection

    it just close it !
    """
    if conn is not None:
        conn.close()


class Connection(object):

    conn = None

    def __init__(self, db, transaction_manager=None, close=close):
        """
        :name: the name of the zodb database
        :param envkey: is an optional key
            where the zodb connection will be pushed
        :param transaction_manager: the transaction manager or None
        :param close: an optionnal callback responsible to close
            the connexion.
        """
        self.db = db
        self.transaction_manager = transaction_manager
        self.close = close

    def __enter__(self):
        self.conn = self.db.open(self.transaction_manager)
        return self.conn

    def __exit__(self, type, value, traceback):
        self.close(self.conn)


class Site(object):
    """A context manager to work in a site

    This simply setSite àla zope
    (see :py:func:zope.component.hooks.setSite)
    """

    def __init__(self, site):
        """
        :ptype site: a :py:func:zope.component.interfaces.ISite
        """
        self.site = site

    def __enter__(self):
        setSite(self.site)
        return self.site

    def __exit__(self, type, value, traceback):
        setSite(None)
