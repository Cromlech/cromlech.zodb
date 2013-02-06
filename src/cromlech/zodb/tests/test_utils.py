# -*- coding: utf-8 -*-


import pytest
import ZConfig
import transaction
from ..interfaces import IDBInitializer
from crom import testing, implicit
from ZODB import DB
from ZODB.interfaces import IDatabase
from ZODB.DemoStorage import DemoStorage
from ..utils import init_db


foo = object()


def add_foo(db):
    tm = transaction.TransactionManager()
    conn = db.open(tm)
    conn.root()['foo'] = foo
    tm.get().commit()
    conn.close()


def setup_function(method):
    testing.setup()
    implicit.lookup.registry.subscribe(
        (IDatabase,), IDBInitializer, add_foo)


def teardown_function(method):
    testing.teardown()


def test_init_db():
    configuration = """
        <zodb>
        <demostorage>
        </demostorage>
        </zodb>"""
    db = init_db(configuration)
    conn = db.open()
    assert conn.root()['foo'] is foo


def test_init_db_bad_conf():
    configuration = """
        <zodb>
            <UNKNOWN_storage>
            </UNKNOWN_storage>
        </zodb>"""
    with pytest.raises(ZConfig.ConfigurationSyntaxError):
        init_db(configuration)
