# -*- coding: utf-8 -*-


def close(conn):
    """This is the default callback to close a connection.
    """
    if conn is not None:
        conn.close()


def deffered_close(conn):
    pass


class Connection(object):
    """The Connection context manager does open and close the database.
    The connection is provided with a transaction manager and is assured
    to be closed by the given `close` callback function.
    """
    conn = None

    def __init__(self, db, transaction_manager=None, close=close):
        """
        :param db: the zodb database object
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
