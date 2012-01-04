# -*- coding: utf-8 -*-
"""Inspired by ``zc.zodbwsgi``, published under the ZPL.
Credits: Jim Fulton
Copyright (c) Zope Foundation and Contributors.
"""
import transaction
import ZODB.config
from cromlech.zodb.controled import Connection, transaction_wrapper


def eval_loader(expr):
    module, expr = expr.split(':', 1)
    if module:
        d = __import__(module, {}, {}, ['*']).__dict__
    else:
        d = {}
    return eval(expr, d)


def init_db(configuration, initializer=None):
    db = ZODB.config.databaseFromString(configuration)
    if initializer is not None:
        initializer(db)
    return db


def zodb_app(app, db, key, transaction, transaction_key='transaction.manager'):

    if transaction:
        app = transaction_wrapper(app, transaction_key)

    # Add a retry when possible.
    #if retry:
    #    app = retry_on_fail(app, retry)

    def zodb_app(environ, start_response):
        with Connection(key, db) as connect:
            return connect(environ, start_response, app)

    return zodb_app


def zodb_middleware(app, configuration, initializer,
                    key="zodb.connection", transaction=True):

    # initializer is a string: py_module_path:class_or_function
    initializer = eval_loader(initializer)

    # configuration is an XML-based ZODB conf
    db = init_db(configuration, initializer)
    
    return zodb_app(app, db, key, transaction)
