import transaction
from webtest import TestApp
from ZODB import DB
from ZODB.DemoStorage import DemoStorage

from .testing import make_app
from ..middleware import ZODBApp


def test_middleware_simple():
    """
    """
    def simple_app(environ, start_response):
        assert (environ['transaction_manager'] ==
                transaction.transaction_manager)
        assert environ['zodb'].root()['myapp'] == 'running !'
        start_response('200 OK', {})
        return [environ['zodb'].root()['myapp']]

    db = DB(DemoStorage())
    make_app(db)
    app = TestApp(ZODBApp(simple_app, db, 'zodb'))

    assert app.get('/') == 'running !'
