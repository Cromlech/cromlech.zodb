#!/usr/bin/python

import ZODB.config
from cromlech.zodb import LocalSiteManager
from pkg_resources import iter_entry_points
from transaction import manager as transaction_manager
from zope.component.interfaces import ISite, IPossibleSite


marker = object()


def eval_loader(expr):
    """load  a class / function

    :param expr: dotted name of the module ':' name of the class / function
    :raises RuntimeError: if expr is not a valid expression
    :raises ImportError: if module or object not found
    """
    modname, elt = expr.split(':', 1)
    if modname:
        try:
            module = __import__(modname, {}, {}, ['*'])
            val = getattr(module, elt, marker)
            if val is marker:
                raise ImportError('')
            return val
        except ImportError:
            raise ImportError(
                    "Bad specification %s: no item name %s in %s." %
                    (expr, elt, modname))
    else:
        raise RuntimeError("Bad specification %s: no module name." % expr)


def init_db(configuration, initializer=None):
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
    if initializer is not None:
        initializer(db)
    return db


def get_site(conn, name):
    """Get a site in a database.

    it simply fetch object under key 'name' at the root.

    :param conn: the ZODB connection
    :param name: name of the site
    :raises KeyError: the site does not exist
    :raises TypeError: the object is not an ISite
    """
    root = conn.root()
    site = root[name]  
    if not ISite.providedBy(site):
        raise TypeError("Site %r does not exist in the current ZODB." % name)
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


def initialize_applications(db, list_applications=list_applications,
                            transaction_manager=transaction_manager):
    """
    This utility setup applications in a database.

    The list of application to create is given by py:fun:list_applications

    For each application to create:

    - it creates the application thanks to the factory
    - it eventually makes it a LocalSiteManager

    You may use it as the :py:fun:init_db initializer parameter,
    or cook your own.

    :param db: the ZODB database
    :param list_applications: a callable that return a dict of applications
        factory indexed by their name
    :param transaction_manager: if not provided
         use :py:mod:transaction default one
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
