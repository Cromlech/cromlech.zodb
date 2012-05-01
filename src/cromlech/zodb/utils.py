#!/usr/bin/python

import ZODB.config
from cromlech.zodb import LocalSiteManager
from pkg_resources import iter_entry_points
from transaction import manager as transaction_manager
from zope.component.interfaces import ISite, IPossibleSite

marker = object()

def eval_loader(expr):
    """load  a class / function, and call it if it is callable.

    :param expr: dotted name of the module ':' name of the class / function
    """
    modname, elt = expr.split(':', 1)
    if modname:
        val = __import__(modname, {}, {}, ['*']).get(elt, marker)
        if val is marker:
            raise RuntimeError(
                "Bad specification %s: no item name %s in %s." %
                (expr, elt, modname))
        if callable(val):
            val = val()
        return val
    else:
        raise RuntimeError("Bad specification %s: no module name." % expr)
        


def init_db(configuration, initializer=None):
    """
    This bootstrap the ZODB listed in configuration

    :param configuration: The zodb configuration as written
        in zope.conf files
    :ptype configuration: string

    :param initializer: an optional method
        which will be passed the ZODB as parameter
        in order to eg. create basic initial objects if they do not exists.

    .. seealso::
       :py:fun:initialize_applications (sample initializer)
    """
    db = ZODB.config.databaseFromString(configuration)
    if initializer is not None:
        initializer(db)
    return db


def get_site(conn, name):
    """Get a site in a database.

    it simply fetch object under key 'name' at the root.

    :param conn: the ZODB connection
    :param name: name of the site
    :raises RuntimeError: if the site does not exist
    """
    root = conn.root()
    site = root.get(self.name)
    if site is None:
        raise RuntimeError("Site %s doesn't exist in the current ZODB." % name)
    return site


def list_applications():
    """List for cromlech applications declared as
    cromlech.application entry points
    """
    apps = {}
    for ept in iter_entry_points(group='cromlech.application'):
        if ept.name in apps:
            raise KeyError(
                'Application name `%s` is defined more than once' % ept.name)
        apps[ept.name] = ept.load()
    return apps


def initialize_applications(db):
    """
    This utility setup applications in a database.

    The list of application to create is given by py:fun:list_applications

    For each application to create:

    - it creates the application thanks to the factory
    - it eventually makes it a LocalSiteManager

    You may use it as the :py:fun:init_db initializer parameter,
    or cook your own.

    :param db: the ZODB database
    """
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
