import transaction
from webtest import TestApp
from ZODB import DB
from ZODB.DemoStorage import DemoStorage

from .testing import make_app
from ..middleware import ZODBApp


def middleware_simple_test():
    """
    """
    def simple_app(environ, start_respons()):
        assert (environ['transaction_manager'] ==
                transaction.transaction_manager)
        assert environ['zodb'].root()['myapp'] == 'running !'

    db = DB(DemoStorage())
    make_app(db)
    app = TestApp(ZODBApp(simple_app, db, 'zodb',
                    use_transaction,
                    transaction_manager_key))
global_conf,  # A dict containing the ['DEFAULT'] section of the ini.
    configuration,
    initializer=None,
    key="zodb.connection",
    transaction='true',
    transaction_key='transaction.manager')
