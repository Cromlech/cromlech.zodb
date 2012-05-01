# -*- coding: utf-8 -*-

from cromlech.zodb.utils import init_db, eval_loader
from cromlech.zodb.controlled import Connection, ConnectionWithTransaction


_marker = object()


class ZODBApp(object):
    """
    A middleware to open a ZODB connection and set it in environnement
    """

    tm_factory = transaction.TransactionManager
    """
    factory used to create a transaction manager if environ does
    not contain one. defaults to :py:class:transaction.TransactionManager
    """

    def __init__(app, db, key,
                 use_transaction,
                 transaction_manager_key='transaction.manager'):
        """
        :param app: the wrapped application
        :param db: the ZODB object
        :param key: the key to store the connection in environ
        :param use_transaction: if True wrap in a transaction
        :param transaction_manager_key: the key where to find or store
            the transaction manager
        """
        self.app = app
        self.db = db
        self.envkey = key
        self.use_transaction = use_transaction
        self.transaction_key = transaction_key

    def run_app(self, app, environ, start_response):
        response = conn(app, environ, start_response)
        for chunk in response:
            yield chunk
        close = getattr(response, 'close', None)
        if close is not None:
            close()

    def __call__(environ, start_response):
        if self.transaction:
            try:
                transaction_manager = environ.[transaction_key]
            except KeyError:
                transaction_manager = environ[transaction_key] = (
                    self.tm_factory())
        else:
            transaction_manager = None

        with Connection(self.db,
                        transaction_manager=transaction_manager) as conn:
            environ[key] = conn
            try:
                if transaction_manager is not None:
                    with transaction_manager:
                        for chunk in self.run_app(app, environ, start_response):
                            yield chunk
                else:
                    for chunk in self.run_app(app, environ, start_response):
                        yield chunk
            except:
                del environ[key]


def zodb_filter_middleware(
    app,
    global_conf,  # A dict containing the ['DEFAULT'] section of the ini.
    configuration,
    initializer=None,
    key="zodb.connection",
    transaction='true',
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
        transaction.lower() in ('true', 'y', 'yes'),
        transaction_key=transaction_key)
