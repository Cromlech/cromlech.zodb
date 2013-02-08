# -*- coding: utf-8 -*-

import ZODB.config
from .interfaces import IDBInitializer


def init_db(configuration):
    """This bootstrap the ZODB using IDBInitializer subscriptions if any.
    """
    db = ZODB.config.databaseFromString(configuration)
    for init in IDBInitializer.subscription(db):
        init(db)
    return db
