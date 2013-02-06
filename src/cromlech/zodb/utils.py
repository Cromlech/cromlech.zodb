# -*- coding: utf-8 -*-

import ZODB.config
from .interfaces import IDBInitializer


def init_db(configuration):
    """
    This bootstrap the ZODB using initializer

    :param configuration: The zodb configuration as written
        in zope.conf files
    :ptype configuration: string

    :param initializer: an optional method
        which will be passed the ZODB as parameter
        in order to eg. create basic initial objects if they do not exists.

    :raises ConfigurationSyntaxError: on bad configuration string

    .. seealso::
       :py:fun:initialize_applications (sample initializer)
    """
    db = ZODB.config.databaseFromString(configuration)
    for init in IDBInitializer.subscription(db):
        init_report = init(db)
        # do log the report or something.
    return db
