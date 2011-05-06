import zope.component.interfaces
import zope.component.persistentregistry
import zope.interface
import zope.location
from dolmen.container.components import BTreeContainer

import interfaces


class _LocalAdapterRegistry(
    zope.component.persistentregistry.PersistentAdapterRegistry,
    zope.location.Location,
    ):
    """
    a location adapter registry used by LocalSiteManager
    """


class LocalSiteManager(
    BTreeContainer,
    zope.component.persistentregistry.PersistentComponents,
    ):
    """Local Site Manager implementation for zodb
    
    Use this to have an application with eg. local utility"""
    zope.interface.implements(interfaces.ILocalSiteManager)

    subs = ()

    def _setBases(self, bases):

        # Update base subs
        for base in self.__bases__:
            if ((base not in bases)
                and interfaces.ILocalSiteManager.providedBy(base)
                ):
                base.removeSub(self)

        for base in bases:
            if ((base not in self.__bases__)
                and interfaces.ILocalSiteManager.providedBy(base)
                ):
                base.addSub(self)

        super(LocalSiteManager, self)._setBases(bases)

    def __init__(self, site):
        BTreeContainer.__init__(self)
        zope.component.persistentregistry.PersistentComponents.__init__(self)

        # Locate the site manager
        self.__parent__ = site
        self.__name__ = '++etc++site'

        # Set base site manager
        # ATM in cromlech we are always the root
        next = zope.component.getGlobalSiteManager()
        self.__bases__ = (next, )

    def _init_registries(self):
        self.adapters = _LocalAdapterRegistry()
        self.utilities = _LocalAdapterRegistry()
        self.adapters.__parent__ = self.utilities.__parent__ = self
        self.adapters.__name__ = u'adapters'
        self.utilities.__name__ = u'utilities'

    def addSub(self, sub):
        """See interfaces.registration.ILocatedRegistry"""
        self.subs += (sub, )

    def removeSub(self, sub):
        """See interfaces.registration.ILocatedRegistry"""
        self.subs = tuple(
            [s for s in self.subs if s is not sub] )
