# -*- coding: utf-8 -*-

import transaction
from webtest import TestApp
from ZODB import DB
from ZODB.DemoStorage import DemoStorage
from cromlech.zodb import LookupNode
from persistent import Persistent
from ..middleware import ZODBApp


class MyApp(LookupNode, Persistent):
    """An application
    """
    foo = 'spam'

    def __call__(self):
        return "running !"

    def dofail(self):
        raise Exception('failed !')


def test_middleware_simple():
    """
    """
    def simple_app(environ, start_response):
        assert (environ['transaction.manager'] ==
                transaction.manager)
        assert environ['zodb'].root()['myapp']() == 'running !'
        start_response('200 OK', [('Content-Type', 'plain/text')])
        return [environ['zodb'].root()['myapp']()]

    db = DB(DemoStorage())

    with transaction.manager:
        conn = db.open()
        conn.root()['myapp'] = MyApp()
    
    app = TestApp(ZODBApp(simple_app, db, 'zodb'))
    assert app.get('/').body == 'running !'
