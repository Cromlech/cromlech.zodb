# -*- coding: utf-8 -*-

import transaction
from persistent import Persistent
from zope.interface import implements


class SimpleApp(Persistent):

    def __call__(self):
        return b"simply running !"


class MyApp(Persistent):
    """An application
    """
    foo = 'spam'

    def __call__(self):
        return b"running !"

    def dofail(self):
        raise Exception('failed !')


def make_app(db):
    """add a MyApp instance to db root under 'myapp'
    """
    conn = db.open()
    conn.root()['myapp'] = MyApp()
    transaction.commit()


class DummySite(Persistent):
    pass
