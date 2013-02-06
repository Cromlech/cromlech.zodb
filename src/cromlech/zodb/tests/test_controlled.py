# -*- coding: utf-8 -*-

import pytest
import transaction

from crom import implicit, testing, LookupContext, ComponentLookupError
from crom import Registry, ChainedLookup, LookupChainLink

from ZODB import DB
from ZODB.DemoStorage import DemoStorage
from zope.interface import implements
from persistent import Persistent

from ..components import LookupNode
from ..controlled import Connection
from ..registry import PersistentRegistry
from persistent import Persistent
from zope.interface import Interface, implements


class Site(LookupNode, Persistent):
    pass


def dummy():
    pass


def dummy2():
    pass


def dummy3():
    pass


def setup_function(method):
    testing.setup()
    implicit.lookup.register((Interface,), Interface, 'dummy', dummy)


def teardown_function(method):
    testing.teardown()


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
        with conn.transaction_manager:
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


def test_persistent_registry():
    db = DB(DemoStorage())
    tm = transaction.TransactionManager()

    registry = PersistentRegistry()
    siteobj = Site()

    with Connection(db, transaction_manager=tm) as conn:
        with tm:
            conn.root()['site'] = siteobj
            siteobj.setLocalRegistry(registry)
            registry.register((Interface,), Interface, 'dummy2', dummy2)

    with Connection(db) as conn:
        site = conn.root()['site']
        reg = site.getLocalRegistry()
        assert reg is registry
        assert reg.lookup((Interface,), Interface, 'dummy2') == dummy2

    with Connection(db) as conn:
        site = conn.root()['site']
        reg = site.getLocalRegistry()

        assert Interface.component((Interface,), name='dummy') == dummy
        with pytest.raises(ComponentLookupError):
            Interface.component((Interface,), name='dummy2')

        with LookupContext(reg):
            assert Interface.component((Interface,), name='dummy2') == dummy2
            with pytest.raises(ComponentLookupError):
                Interface.component((Interface,), name='dummy')

        with pytest.raises(ComponentLookupError):
            Interface.component((Interface,), name='dummy2')

    chain = ChainedLookup()
    chain.add(implicit.lookup)
    implicit.lookup = chain

    with Connection(db) as conn:
        site = conn.root()['site']
        reg = site.getLocalRegistry()

        with LookupChainLink(reg):
            assert Interface.component((Interface,), name='dummy2') == dummy2
            assert Interface.component((Interface,), name='dummy') == dummy

        with pytest.raises(ComponentLookupError):
            Interface.component((Interface,), name='dummy2')

    link = Registry()
    link.register((Interface,), Interface, 'dummy', dummy3)

    with Connection(db) as conn:
        site = conn.root()['site']
        reg = site.getLocalRegistry()

        with LookupChainLink(reg):
            with LookupChainLink(link):
                assert Interface.component((Interface,), name='dummy2') == dummy2
                assert Interface.component((Interface,), name='dummy') == dummy3

                with LookupContext(link):
                    with pytest.raises(ComponentLookupError):
                        assert Interface.component((Interface,), name='dummy2') == dummy2
                    assert Interface.component((Interface,), name='dummy') == dummy3

                with pytest.raises(KeyError):
                    with LookupChainLink(link):
                        pass

                assert Interface.component((Interface,), name='dummy2') == dummy2
                assert Interface.component((Interface,), name='dummy') == dummy3
                    
            assert Interface.component((Interface,), name='dummy2') == dummy2
            assert Interface.component((Interface,), name='dummy') == dummy
