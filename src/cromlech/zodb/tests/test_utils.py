# -*- coding: utf-8 -*-

import pytest
import ZConfig
import transaction

from collections import OrderedDict

from ZODB import DB
from ZODB.DemoStorage import DemoStorage
from cromlech.zodb.utils import eval_loader, init_db
from cromlech.zodb.utils import initialize_applications

from ..testing import DummySite, MyApp, SimpleApp


def test_eval_loader():
    assert eval_loader('cromlech.zodb.utils:eval_loader') is eval_loader
    assert (eval_loader('cromlech.zodb.tests.fixture:Foo').__doc__ ==
            "class to test eval_loader")
    with pytest.raises(RuntimeError):
        eval_loader(':foo')
    with pytest.raises(ImportError):
        # module does not exists
        eval_loader('cromlech.zodb.doesnotexiste:id')
    with pytest.raises(ImportError):
        # object inside module does not exists
        eval_loader('cromlech.zodb.tests.fixture:Bar')


foo = object()


def add_foo(db):
    tm = transaction.TransactionManager()
    conn = db.open(tm)
    conn.root()['foo'] = foo
    tm.get().commit()
    conn.close()


def test_init_db():
    configuration = """
        <zodb>
        <demostorage>
        </demostorage>
        </zodb>"""
    db = init_db(configuration, add_foo)
    conn = db.open()
    assert conn.root()['foo'] is foo


def test_init_db_bad_conf():
    configuration = """
        <zodb>
            <UNKNOWN_storage>
            </UNKNOWN_storage>
        </zodb>"""
    with pytest.raises(ZConfig.ConfigurationSyntaxError):
        init_db(configuration, add_foo)


def test_initialize_applications():

    def apps():
        return {'mine':MyApp, 'app': SimpleApp, 'app2': SimpleApp,
                'obj':tuple}

    def failing_apps():
        return OrderedDict((('foo', SimpleApp), ('spam', lambda: 1/0)))

    db = DB(DemoStorage())
    initialize_applications(db, apps)
    conn = db.open()
    root = conn.root()
    assert root['mine']() == b"running !"
    assert root['app']() == b"simply running !"
    assert root['app2']() == b"simply running !"
    assert isinstance(root['obj'], tuple)
    transaction.abort()
    conn.close()

    # verify it's all or nothing
    try:
        initialize_applications(db, failing_apps)
    except ZeroDivisionError:
        pass
    conn = db.open()
    root = conn.root()
    assert 'foo' not in root
    conn.close()
