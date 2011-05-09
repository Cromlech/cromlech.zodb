from BTrees.OOBTree import OOBTree
import zope.component.interfaces
import zope.component.persistentregistry
import zope.interface
import zope.location

import interfaces


class PossibleSite(object):
    """a base implementation of a possible site, to be used as 
    a mixin
    """
    zope.interface.implements(zope.component.interfaces.IPossibleSite)

    _sm = None
    
    def getSiteManager(self):
        if self._sm is not None:
            return self._sm
        else:
            raise ComponentLookupError('no site manager defined')


    def setSiteManager(self, sm):
        if zope.component.interfaces.ISite.providedBy(self):
            raise TypeError("Already a site")

        if zope.component.interfaces.IComponentLookup.providedBy(sm):
            self._sm = sm
        else:
            raise ValueError('setSiteManager requires an IComponentLookup')

        zope.interface.alsoProvides(self, zope.component.interfaces.ISite)


class _LocalAdapterRegistry(
    zope.component.persistentregistry.PersistentAdapterRegistry,
    zope.location.Location,
    ):
    """
    a location adapter registry used by LocalSiteManager
    """


class LocalSiteManager(
    OOBTree,
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
        OOBTree.__init__(self)
        zope.component.persistentregistry.PersistentComponents.__init__(self)

        # Set base site manager
        # ATM in cromlech we are always the root
        next = zope.component.getGlobalSiteManager()
        self.__bases__ = (next, )
        
        # Locate the site manager
        site.setSiteManager(self)
        self.__parent__ = site
        self.__name__ = '++etc++site'  # FIXME provide traverser ?

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



@zope.component.provideAdapter
@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(zope.component.interfaces.IComponentLookup)
def SiteManagerAdapter(ob):
    """An adapter from ILocation to IComponentLookup.

    The ILocation is interpreted flexibly, we just check for
    ``__parent__``.
    """
    current = ob
    while True:
        if zope.component.interfaces.ISite.providedBy(current):
            return current.getSiteManager()
        current = getattr(current, '__parent__', None)
        if current is None:
            # It is not a location or has no parent, so we return the global
            # site manager
            return zope.component.getGlobalSiteManager()


#~ def changeSiteConfigurationAfterMove(site, event):
    #~ """After a site is moved, its site manager links have to be updated."""
    #~ if event.newParent is not None:
        #~ next = _findNextSiteManager(site)
        #~ if next is None:
            #~ next = zope.component.getGlobalSiteManager()
        #~ site.getSiteManager().__bases__ = (next, )
#~ 
#~ 
#~ @zope.component.adapter(
    #~ PossibleSite,
    #~ zope.container.interfaces.IObjectMovedEvent)
#~ def siteManagerContainerRemoved(container, event):
    #~ # The relation between SiteManagerContainer and LocalSiteManager is a
    #~ # kind of containment hierarchy, but it is not expressed via containment,
    #~ # but rather via an attribute (_sm).
    #~ #
    #~ # When the parent is deleted, this needs to be propagated to the children,
    #~ # and since we don't have "real" containment, we need to do that manually.
#~ 
    #~ try:
        #~ sm = container.getSiteManager()
    #~ except ComponentLookupError:
        #~ pass
    #~ else:
        #~ for ignored in zope.component.subscribers((sm, event), None):
            #~ pass # work happens during adapter fetch
