from ZODB import DB
from ZODB.DemoStorage import DemoStorage
import transaction

import pytest

from cromlech.zodb import components


def test_persistancy():
    db = DB(DemoStorage('test_storage'))
    connection = db.open()
    root = connection.root()
    f = root['folder'] = components.PersitentOOBTree()
    f['foo'] = 'bar'
    f['spam'] = 1
    transaction.commit()
    del f
    connection = db.open()
    f = connection.root()['folder']
    assert f['foo'] == 'bar'
    assert f['spam'] == 1

    # overwritting' adding, removing
    f['foo'] = 'baz'
    del f['spam']
    f['ham'] = 2
    transaction.commit()
    connection = db.open()
    f = connection.root()['folder']
    assert f['foo'] == 'baz'
    with pytest.raises(KeyError):
        f['spam']
    assert f['ham'] == 2

    # aborting does not save
    f['foo'] == 'bar again'
    f['spam'] = 1
    del f['ham']
    transaction.abort()
    connection = db.open()
    f = connection.root()['folder']
    assert f['foo'] == 'baz'
    with pytest.raises(KeyError):
        f['spam']
    assert f['ham'] == 2

    db.close()


def test_len():
    folder = components.PersitentOOBTree()
    folder["bar"] = folder["foo"] = object()
    assert len(folder) == 2

    folder["x"] = 1
    assert len(folder) == 3

    del folder["bar"]
    assert len(folder) == 2


def test_iterators():
    folder = components.PersitentOOBTree()
    o = folder["bar"] = folder["foo"] = object()
    assert set([k for k in folder]) == set(["foo", "bar"])
    assert set(folder.keys()) == set(["foo", "bar"])
    assert set(folder.items()) == set([("foo", o), ("bar",o)])
    assert list(folder.values()) == [o, o]

    folder["spam"] = 1
    del folder["bar"]
    assert set([k for k in folder]) == set(["foo", "spam"])
    assert set(folder.keys()) == set(["foo", "spam"])
    assert set(folder.items()) == set([("foo", o), ("spam",1)])
    assert set(folder.values()) == set([o, 1])
