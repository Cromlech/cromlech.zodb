# -*- coding: utf-8 -*-

from transaction import manager
from cromlech.zodb import LookupNode
from persistent import Persistent
from zope.interface import implements


class SimpleApp(LookupNode, Persistent):

    def __call__(self):
        return "simply running !"


def store_app(db, app):
    """add a MyApp instance to db root under 'myapp'
    """
    with manager:
        conn = db.open()
        conn.root()['myapp'] = app
