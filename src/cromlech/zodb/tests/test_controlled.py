# -*- coding: utf-8 -*-
import transaction

from ZODB import DB
from ZODB.DemoStorage import DemoStorage
from zope.component.hooks import getSite
from zope.component.interfaces import ISite
from zope.interface import implements
from persistent import Persistent

from cromlech.zodb.components import PossibleSite
from cromlech.zodb.controlled import Connection, Site

from .testing import DummySite


def test_connection_manager_default_transaction():
    db = DB(DemoStorage())

    with Connection(db) as conn:
        conn.root()['foo'] = 'bar'
        transaction.commit()

    assert db.open().root()['foo'] == 'bar'


def test_connection_manager_transaction():
    db = DB(DemoStorage())
    tm = transaction.TransactionManager()

    with Connection(db, transaction_manager=tm) as conn:
        with tm as transaction_:
            conn.root()['foo'] = 'bar'

    assert db.open().root()['foo'] == 'bar'  # transaction was commited


def test_connection_manager_connection_inside():
    db = DB(DemoStorage())
    tm = transaction.TransactionManager()

    # we need to close after commit
    def close(conn):
        def close_hook(success, conn):
            conn.close()
        conn.transaction_manager.get().addAfterCommitHook(close_hook, (conn,))

    with tm as transaction_:
        with Connection(db, transaction_manager=tm, close=close) as conn:
            conn.root()['foo'] = 'bar'

    assert db.open().root()['foo'] == 'bar'  # transaction was commited


def test_connection_manager_aborting():
    db = DB(DemoStorage())
    tm = transaction.TransactionManager()

    with Connection(db, transaction_manager=tm) as conn:
        with tm as transaction_:
            conn.root()['foo'] = 'bar'
            transaction_.abort()
    assert db.open().root().get('foo') is None  # transaction was aborted


def test_site():

    site = DummySite()

    with Site(site):
        assert getSite() is site
    assert getSite() is not site

    try:
        with Site(site):
            assert getSite() is site
            raise RuntimeError('')
    except RuntimeError:
        pass
    assert getSite() is not site
