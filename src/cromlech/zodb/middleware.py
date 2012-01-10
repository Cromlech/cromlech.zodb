# -*- coding: utf-8 -*-

from cromlech.zodb.utils import init_db, eval_loader
from cromlech.zodb.controlled import Connection, ConnectionWithTransaction


def zodb_app_factory(app, db, key,
                     transaction, transaction_key='transaction.manager'):

    if transaction:
        conn_manager = ConnectionWithTransaction(db, key, transaction_key)
    else:
        conn_manager = Connection(db, key)

    # Add a retry when possible.
    #if retry:
    #    app = retry_on_fail(app, retry)

    def zodb_app(environ, start_response):
        with conn_manager as connect:
            return connect(app, environ, start_response)

    return zodb_app


def zodb_filter_middleware(
    app,
    global_conf,  # A dict containing the ['DEFAULT'] section of the ini.
    configuration, initializer=None, key="zodb.connection",
    transaction=True, transaction_key='transaction.manager'):
    """This middleware factory is compatible with the filter_app
    prototype from `PasteDeploy`. It can, however, be used with
    any WSGI server if properly called. For a less specific implementation
    have a look at ``cromlech.zodb.middleware:zodb_app_factory``.
    """
    if initializer is not None:
        # initializer is a string: py_module_path:class_or_function
        initializer = eval_loader(initializer)

    # configuration is an XML-based ZODB conf
    db = init_db(configuration, initializer)

    return zodb_app_factory(
        app, db, key,
        transaction in (True, 'true', 'y', 'yes'),
        transaction_key=transaction_key)
