#!/usr/bin/python

import transaction
from pkg_resources import iter_entry_points
from zope.component.interfaces import ISite

from components import LocalSiteManager


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
    root = conn.root()
    apps = list_applications()
    with transaction:
        for name, factory in apps.items():
            if not name in root:
                application = root[name] = factory()
                if not ISite.providedBy(application):
                    site_manager = LocalSiteManager(application)
                    application.setSiteManager(site_manager)

                print "initialized %r" % name
    conn.close()
