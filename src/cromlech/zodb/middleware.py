# -*- coding: utf-8 -*-

import transaction
from cromlech.zodb.utils import init_db, eval_loader
from cromlech.zodb.controlled import Connection, ConnectionWithTransaction


def get_transaction_manager_factory(key):
    """
    """
    def extract_from_environ(environ):
        try:
            tm = environ[key]
        except KeyError:
            tm = environ[key] = transaction.manager
        return tm
    return extract_from_environ


class ZODBApp(object):
    """A middleware to open a ZODB connection and set it in environment.
    """

    def __init__(app, db, key, transaction_manager_factory):
        """
        :param app: the wrapped application
        :param db: the ZODB object
        :param use_transaction: if True wrap in a transaction
        :param transaction_manager_key: the key where to find or store
            the transaction manager
        """
        self.app = app
        self.db = db
        self.key = key
        self.use_transaction = use_transaction
        self.transaction_manager_factory = transaction_manager_factory 

    def __call__(environ, start_response):
        tm = self.transaction_manager_factory(environ)

        with Connection(self.db, transaction_manager=tm) as conn:
            environ[key] = conn
            try:
                with tm:
                    response = app(environ, start_response)
                    for chunk in response:
                        yield chunk
                        close = getattr(response, 'close', None)
                        if close is not None:
                            close()
            finally:
                del environ[key]


def zodb_filter_middleware(
    app,
    global_conf,  # A dict containing the ['DEFAULT'] section of the ini.
    configuration,
    initializer=None,
    key="zodb.connection",
    transaction_key='transaction.manager'):
    """
    factory for :py:class:ZODBAppFactory

    This middleware factory is compatible with the filter_app
    prototype from `PasteDeploy`. It can, however, be used with
    any WSGI server if properly called.

    :param initializer: an optional ZODB initializer
      module.dotted.name:callable,
      eg: 'cromlech.zodb.utils:initialize_applications'

    for other params see :py:meth:ZODBApp.__init__
    """
    if initializer is not None:
        # initializer is a string: py_module_path:class_or_function
        initializer = eval_loader(initializer)

    # configuration is an XML-based ZODB conf
    db = init_db(configuration, initializer)

    return ZODBApp(
        app, db, key,
        transaction_manager_factory=get_transaction_manager_factory(
            transaction_key))

