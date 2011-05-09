from persistent.mapping import PersistentMapping
from zope.interface import Interface, implements
from zope.component import getUtility, getSiteManager, getGlobalSiteManager
from ZODB import DB
from ZODB.DemoStorage import DemoStorage
import transaction

from cromlech.zodb import components



class IDummyUtil(Interface):
    """dummy utility"""

    def callme():
        """Da method"""


class GlobalDummyUtil(object):
    implements(IDummyUtil)

    def callme(self):
        return "Globally, yes"



class PeculiarDummyUtil(object):
    implements(IDummyUtil)

    answer = "yes"

    def callme(self):
        return "Perculiarly, %s" % self.answer


class SimpleSite(components.PossibleSite, PersistentMapping):
    """simple site"""


def setup_site():
    """can we query utilities inside our lsm ?"""
    # just the global one
    site = components.PossibleSite()
    components.LocalSiteManager(site)
    return site


def test_get_site_manager():
    site = setup_site()
    # do we get it through zope.component ?
    lsm = getSiteManager(context=site)
    assert lsm is site._sm


def test_global_available():
    site = setup_site()
    # no local utility means we fetch the global one
    getGlobalSiteManager().registerUtility(GlobalDummyUtil())
    dummy = getUtility(IDummyUtil, context=site)
    assert dummy.callme() == "Globally, yes"


def test_local_shadows_global():
    site = setup_site()
    getGlobalSiteManager().registerUtility(GlobalDummyUtil())
    getSiteManager(context=site).registerUtility(PeculiarDummyUtil())
    dummy = getUtility(IDummyUtil, context=site)
    assert dummy.callme() == "Perculiarly, yes"


def test_local_utility_persitent():
    db = DB(DemoStorage('test_storage'))
    connection = db.open()
    root = connection.root()
    site = root['site'] = SimpleSite()
    components.LocalSiteManager(site)
    transaction.commit()

    getSiteManager(context=site).registerUtility(PeculiarDummyUtil())
    dummy = getUtility(IDummyUtil, context=site)
    dummy.answer = 'no'
    assert dummy.callme() == "Perculiarly, no"
    transaction.commit()
    del site
    del dummy
    connection = db.open()
    site = connection.root()['site']
    dummy = getUtility(IDummyUtil, context=site)
    assert dummy.callme() == "Perculiarly, no"
    # and aborting does not save state
    dummy.answer = 'yes'
    assert dummy.callme() == "Perculiarly, yes"
    transaction.abort
    connection = db.open()
    site = connection.root()['site']
    dummy = getUtility(IDummyUtil, context=site)
    assert dummy.callme() == "Perculiarly, no"
    db.close()
