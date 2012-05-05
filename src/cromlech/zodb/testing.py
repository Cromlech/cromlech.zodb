from cromlech.zodb import PossibleSite
import transaction
from persistent import Persistent
from zope.interface import implements
from zope.component.interfaces import ISite


class SimpleApp(PossibleSite, Persistent):

    def __call__(self):
        return "simply running !"


class MyApp(PossibleSite, Persistent):
    """An application
    """
    foo = 'spam'

    def __call__(self):
        return "running !"

    def dofail(self):
        raise Exception('failed !')


def make_app(db):
    """add a MyApp instance to db root under 'myapp'
    """
    conn = db.open()
    conn.root()['myapp'] = MyApp()
    transaction.commit()


class DummySite(Persistent):
    implements(ISite)

    def getSiteManager(self):
        return self
