# -*- coding: utf-8 -*-

import pytest
import transaction

from ZODB import DB
from ZODB.DemoStorage import DemoStorage
from persistent import Persistent

from cromlech.io.interfaces import IPublicationRoot
from cromlech.zodb.controled import ZODBSiteWithTransaction
from cromlech.zodb.components import PossibleSite


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

    with ZODBSiteWithTransaction(db, 'zodb.connection', 'myapp') as manager:
        site = manager(environ)
        site.foo = 'bar'
        assert site() == "running !"

    assert db.open().root()['myapp'].foo == 'bar'  # transaction was commited


def test_context_manager_aborting():
    db = DB(DemoStorage())
    make_app(db)
    environ = {}

    with pytest.raises(Exception):
        with ZODBSiteWithTransaction(db, 'zodb.connection', 'myapp') as manager:
            site = manager(environ)
            site.foo = 'bar'
            site.dofail()

    assert db.open().root()['myapp'].foo == 'spam'  # transaction was aborted


def test_no_application():
    db = DB(DemoStorage())
    make_app(db)
    environ = {}

    with pytest.raises(RuntimeError):
        with ZODBSiteWithTransaction(db, 'zodb.connection', u'ZÜG') as manager:
            site = manager(environ)
