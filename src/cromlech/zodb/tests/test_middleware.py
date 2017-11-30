import transaction
from webtest import TestApp as App
from ZODB import DB
from ZODB.DemoStorage import DemoStorage

from ..testing import make_app
from ..middleware import ZODBApp


def test_middleware_simple():
    """
    """
    def simple_app(environ, start_response):
        assert (environ['transaction.manager'] ==
                transaction.manager)
        assert environ['zodb'].root()['myapp']() == b'running !'
        start_response('200 OK', [('Content-Type', 'plain/text')])
        return [environ['zodb'].root()['myapp']()]

    db = DB(DemoStorage())
    make_app(db)
    app = App(ZODBApp(simple_app, db, 'zodb'))

    assert app.get('/').body == b'running !'


class IterResponse(object):

    closed = False

    def __iter__(self):
        yield b'3, '
        yield b'2, '
        yield b'1, '
        yield b'FIRE'

    def close(self):
        self.closed = True


def test_middleware_iter_and_close():
    """
    test middleware with iteration and close
    """
    iter_response = IterResponse()

    def iter_app(environ, start_response):
        start_response('200 OK', [('Content-Type', 'plain/text')])
        return iter_response

    db = DB(DemoStorage())
    make_app(db)
    app = App(ZODBApp(iter_app, db, 'zodb'))

    assert not iter_response.closed
    result = app.get('/').body
    assert result == b'3, 2, 1, FIRE'
    assert iter_response.closed
