# -*- coding: utf-8 -*-
import transaction

from cromlech.zodb.utils import init_db, eval_loader
from cromlech.zodb.controlled import Connection


_marker = object()


def environ_transaction_manager(name, tm_factory=lambda: transaction.manager):
    def from_environ(environ):
        tm = environ.setdefault(name, tm_factory())
    return from_environ

def default_transaction_manager_factory(environ):
    return transaction.manager

class ZODBApp(object):
    """
    A middleware to open a ZODB connection and set it in environnement
    """

    """
    factory used to create a transaction manager if environ does
    not contain one. defaults to :py:class:transaction.TransactionManager
    """

    def __init__(self, app, db, key,
                 manage_transaction=True,
                 transaction_manager_factory=None):
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
        self.manage_transaction = manage_transaction
        self.tm_factory = transaction_manager_factory

    def __call__(self, environ, start_response):
        self.transaction_manager_factory(environ)

        with Connection(self.db,
                        transaction_manager=transaction_manager) as conn:
            environ[self.envkey] = conn
            try:
                with transaction_manager:
                    response = self.app(environ, start_response)
                    for chunk in response:
                        yield chunk
                    close = getattr(response, 'close', None)
                    if close is not None:
                        close()
            except:
                del environ[self.envkey]
        

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
    :param transaction: does the middelware needs to manage the transaction

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
        transaction_key=transaction_key,
        transaction_manager_factory=from_environ(transaction_key))
