# -*- coding: utf-8 -*-

from cromlech.zodb.utils import init_db, eval_loader
from cromlech.zodb.controled import Connection, transaction_wrapper


def zodb_app_factory(
    app, db, key, transaction, transaction_key='transaction.manager'):

    if transaction:
        app = transaction_wrapper(app, transaction_key)

    # Add a retry when possible.
    #if retry:
    #    app = retry_on_fail(app, retry)

    def zodb_app(environ, start_response):
        with Connection(key, db) as connect:
            return connect(environ, start_response, app)

    return zodb_app


def zodb_filter_middleware(
    global_conf,  # A dict containing the ['DEFAULT'] section of the ini.
    key="zodb.connection", app, configuration, initializer,
    transaction=True, transaction_key='transaction.manager'):
    """This middleware factory is compatible with the filter_app
    prototype from `PasteDeploy`. It can, however, be used with
    any WSGI server if properly called. For a less specific implementation
    have a look at ``cromlech.zodb.middleware:zodb_app_factory``.
    """
    # initializer is a string: py_module_path:class_or_function
    initializer = eval_loader(initializer)

    # configuration is an XML-based ZODB conf
    db = init_db(configuration, initializer)
    
    return zodb_app_factory(app, db, key, transaction)
