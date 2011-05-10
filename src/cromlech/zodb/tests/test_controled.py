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

    def __call__(self):
        return "running !"


def make_app(db):
    """add a MyApp instance to db root under 'myapp'"""
    conn = db.open()
    conn.root()['myapp'] = MyApp()
    transaction.commit()


def test_context_manager():
    db = DB(DemoStorage())
    make_app(db)
    environ = {}
    environ['zodb.connection'] = db.open()
    with controled.ZodbSite(environ, 'myapp') as site:
        assert site == "running !"
        assert IPublicationRoot.providedBy(site)
    assert not hasattr(db, 'storage')  # meaning db is closed


def test_no_application():
    db = DB(DemoStorage())
    make_app(db)
    environ = {}
    environ['zodb.connection'] = db.open()
    with pytest.raises(RuntimeError):
        with controled.ZodbSite(environ, 'unexisting_app') as site:
            pass
    assert not hasattr(db, 'storage')  # meaning db is closed
