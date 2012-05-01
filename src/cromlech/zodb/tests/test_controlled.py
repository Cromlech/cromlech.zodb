# -*- coding: utf-8 -*-

import pytest
import transaction

from ZODB import DB
from ZODB.DemoStorage import DemoStorage
from persistent import Persistent

from cromlech.zodb.components import PossibleSite
from cromlech.zodb.controlled import Connection, Site


class MyApp(PossibleSite, Persistent):
    """An application
    """
    foo = 'spam'

    def __call__(self):
        return "running !"

    def dofail(self):
        raise Exception('failed !')


def make_app(db):
    """add a MyApp instance to db root under 'myapp'
    """
    conn = db.open()
    conn.root()['myapp'] = MyApp()
    transaction.commit()


def test_context_manager():
    db = DB(DemoStorage())
    make_app(db)
    environ = {}

    tm = transaction.TransactionManager()

    with Connection(db, transaction_manager=tm) as conn:
        with tm as transaction_:
            conn.root()['foo'] = 'bar'

    assert db.open().root()['foo'] == 'bar'  # transaction was commited


def test_context_manager_connection_inside():
    db = DB(DemoStorage())
    make_app(db)
    environ = {}

    tm = transaction.TransactionManager()

    # we need to close after commit
    def close(conn):
        def close_hook(success, conn):
            #conn.close()
            pass
        tm.get().addAfterCommitHook(close_hook, conn)

    with tm as transaction_:
        with Connection(db, transaction_manager=tm, close=close) as conn:
            conn.root()['foo'] = 'bar'

    assert db.open().root()['foo'] == 'bar'  # transaction was commited


def test_context_manager_aborting():
    db = DB(DemoStorage())
    make_app(db)
    environ = {}

    tm = transaction.TransactionManager()

    with Connection(db, transaction_manager=tm) as conn:
        with tm as transaction_:
            conn.root()['foo'] = 'bar'
            transaction_.abort()
    assert db.open().root().get('foo') is None  # transaction was aborted


def test_no_application():
    db = DB(DemoStorage())
    make_app(db)
    environ = {}

    with pytest.raises(RuntimeError):
        with ZODBSiteWithTransaction(db, 'zodb.connection', u'ZÜG') as manager:
            site = manager(environ)
