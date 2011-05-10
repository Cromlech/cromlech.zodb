from cromlech.io.interfaces import IPublicationRoot
from persistent import Persistent
import transaction
from ZODB import DB
from ZODB.DemoStorage import DemoStorage

import pytest

from cromlech.zodb import controled
from cromlech.zodb.components import PossibleSite


class MyApp(PossibleSite, Persistent):
    """An application"""

    foo = 'spam'

    def __call__(self):
        return "running !"

    def dofail(self):
        raise Exception('failed !')


def make_app(db):
    """add a MyApp instance to db root under 'myapp'"""
    conn = db.open()
    conn.root()['myapp'] = MyApp()
    transaction.commit()


class ConnexionVerifier():
    closed = False

    def __init__(self, conn):
        conn.onCloseCallback(self.callback)

    def callback(self):
        self.closed = True


def test_context_manager():
    db = DB(DemoStorage())
    make_app(db)
    environ = {}
    conn = environ['zodb.connection'] = db.open()
    verifier = ConnexionVerifier(conn)
    with controled.ZodbSite(environ, 'myapp') as site:
        assert site() == "running !"
        site.foo = 'bar'
        assert IPublicationRoot.providedBy(site)
    assert db.open().root()['myapp'].foo == 'bar'  # transaction was commited
    assert verifier.closed


def test_context_manager_aborting():
    db = DB(DemoStorage())
    make_app(db)
    environ = {}
    conn = environ['zodb.connection'] = db.open()
    verifier = ConnexionVerifier(conn)
    with pytest.raises(Exception):
        with controled.ZodbSite(environ, 'myapp') as site:
            site.foo = 'bar'
            site.dofail()
    assert db.open().root()['myapp'].foo == 'spam'  # transaction was aborted
    assert verifier.closed


def test_no_application():
    db = DB(DemoStorage())
    make_app(db)
    environ = {}
    conn = environ['zodb.connection'] = db.open()
    verifier = ConnexionVerifier(conn)
    with pytest.raises(RuntimeError):
        with controled.ZodbSite(environ, 'unexisting_app') as site:
            pass
    assert verifier.closed
