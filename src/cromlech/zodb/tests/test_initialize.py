import os.path
import pkg_resources
from persistent import Persistent
from ZODB import DB
from ZODB.DemoStorage import DemoStorage

from cromlech.zodb import utils
from cromlech.zodb.components import PossibleSite

import pytest

testDataPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')


class EntryPointMocker(object):
    """provide your own entry points in a list
    """

    def __init__(self, entries):
        self.entries = entries

    def __enter__(self):
        pkg_resources.working_set.add_entry(testDataPath)
        def mocked_iter_entry_points(group, name=None):
            """simulate that a package provide an entry_point
            """
            if group == 'cromlech.application':
                for e in self.entries:
                    yield pkg_resources.EntryPoint.parse(e,
                                            dist=pkg_resources.Distribution())

        # monkey patch
        self.original = utils.iter_entry_points
        utils.iter_entry_points = mocked_iter_entry_points

    def __exit__(self, type, value, traceback):
        utils.iter_entry_points = self.original


class MyApp(PossibleSite, Persistent):
    """An application"""

    def __call__(self):
        return "running !"

class YourApp(MyApp):
    """An application"""

    def __call__(self):
        return "Also running !"

def test_initialize():
    with EntryPointMocker(['myapp=cromlech.zodb.tests.test_initialize:MyApp',
                       'yourapp=cromlech.zodb.tests.test_initialize:YourApp']):
        db = DB(DemoStorage())
        utils.initialize_applications(db)

        conn = db.open()
        assert 'myapp' in conn.root()
        assert isinstance(conn.root()['myapp'], MyApp)
        assert conn.root()['myapp']() == 'running !'
        assert 'yourapp' in conn.root()
        assert isinstance(conn.root()['yourapp'], YourApp)
        assert conn.root()['yourapp']() == 'Also running !'


def test_no_implementation_fails():
    with EntryPointMocker(
                ['myapp=cromlech.zodb.tests.test_initialize:NotExistingApp']):
        db = DB(DemoStorage())
        with pytest.raises(ImportError):
            utils.initialize_applications(db)


def test_same_name_fails():
     with EntryPointMocker(['myapp=cromlech.zodb.tests.test_initialize:MyApp',
                        'myapp=cromlech.zodb.tests.test_initialize:MyApp']):
        db = DB(DemoStorage())
        with pytest.raises(KeyError):
            utils.initialize_applications(db)


def second_init():
    with EntryPointMocker(['myapp=cromlech.zodb.tests.test_initialize:MyApp']):
        db = DB(DemoStorage())
        utils.initialize_applications(db)

        conn = db.open()
        app = conn.root()['myapp']

        # again
        utils.initialize_applications(db)
        conn = db.open()
        assert app is conn.root()['myapp']
