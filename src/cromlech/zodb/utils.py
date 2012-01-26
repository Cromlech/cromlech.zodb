#!/usr/bin/python

import ZODB.config
from cromlech.zodb import LocalSiteManager
from pkg_resources import iter_entry_points
from transaction import manager as transaction_manager
from zope.component.interfaces import ISite, IPossibleSite

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


def list_applications():
    apps = {}
    for ept in iter_entry_points(group='cromlech.application'):
        if ept.name in apps:
            raise KeyError(
                'Application name `%s` is defined more than once' % ept.name)
        apps[ept.name] = ept.load()
    return apps


def initialize_applications(db):
    conn = db.open()

    try:
        root = conn.root()
        apps = list_applications()

        with transaction_manager:
            for name, factory in apps.items():
                if not name in root:
                    application = root[name] = factory()
                    if (not ISite.providedBy(application) and
                        IPossibleSite.providedBy(application)):
                        LocalSiteManager(application)
    finally:
        conn.close()
