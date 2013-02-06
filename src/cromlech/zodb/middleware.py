# -*- coding: utf-8 -*-

import transaction
from cromlech.zodb.utils import init_db
from cromlech.zodb.controlled import Connection


def environ_transaction_manager(environ, key, default=transaction.manager):
    try:
        tm = environ[key]
    except KeyError:
        tm = environ[key] = default
    return tm


class ZODBApp(object):
    """A middleware to open a ZODB connection and set it in environment.
    """

    def __init__(self, app, db, key, transaction_key='transaction.manager',
                 transaction_manager_factory=environ_transaction_manager):
        """
        :param app: the wrapped application
        :param db: the ZODB object
        :param transaction_key: a key to find or store the transaction manager
        :param transaction_manager_factory: a callable function that takes
        the environ and transaction_key and returns a transaction manager.
        """
        self.app = app
        self.db = db
        self.key = key
        self.transaction_key = transaction_key
        self.transaction_manager_factory = transaction_manager_factory

    def __call__(self, environ, start_response):
        tm = self.transaction_manager_factory(environ, self.transaction_key)

        with Connection(self.db, transaction_manager=tm) as conn:
            environ[self.key] = conn
            try:
                with tm:
                    response = self.app(environ, start_response)
                    for chunk in response:
                        yield chunk
                    close = getattr(response, 'close', None)
                    if close is not None:
                        close()
            finally:
                del environ[self.key]


def zodb_filter_middleware(
    app,
    global_conf,  # A dict containing the ['DEFAULT'] section of the ini.
    configuration,
    initializer=None,
    key="zodb.connection",
    transaction_key='transaction.manager'):
    """
    factory for :py:class:ZODBApp

    This middleware factory is compatible with the filter_app
    prototype from `PasteDeploy`. It can, however, be used with
    any WSGI server if properly called.

    :param configuration: XML-based ZODB conf
    :param initializer: callable that takes 'db' as a parameter.
    :param key: environ key used to retrieve an existing connection
    :param transaction_key: environ key used to pass the transaction around.

    for other params see :py:meth:ZODBApp.__init__
    """
    db = init_db(configuration, initializer)

    return ZODBApp(
        app, db, key, transaction_key,
        transaction_manager_factory=environ_transaction_manager)
