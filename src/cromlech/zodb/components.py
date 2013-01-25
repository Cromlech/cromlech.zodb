# -*- coding: utf-8 -*-

import .interfaces
import .registry

import zope.location

from crom import adapter, sources, target, ComponentLookupError
from crom.interfaces import IRegistry, ILookup, implicit
from BTrees.Length import Length
from BTrees.OOBTree import OOBTree
from persistent import Persistent

from zope.interface import implements
from zope.cachedescriptors.property import Lazy


class Site(object):
    """a base implementation of a site
    """
    implements(interfaces.ISite)

    _registry = None

    def getLocalLookup(self):
        if self._registry is not None:
            return registry.LocalRegistryWrapper(
                '@registry', self, self._registry)
        else:
            raise ComponentLookupError('No local registry set.')

    def setLocalRegistry(self, reg):
        assert interfaces.IRegistry.providedBy(reg):
        self._registry = reg



class PersitentOOBTree(Persistent):
    """A persitent wrapper around a OOBTree"""

    def __init__(self):
        self._data = OOBTree()
        Persistent.__init__(self)
        self.__len = Length()

    @Lazy
    def _PersitentOOBTree__len(self):
        l = Length()
        ol = len(self._data)
        if ol > 0:
            l.change(ol)
        self._p_changed = True
        return l

    def __len__(self):
        return self.__len()

    def __setitem__(self, key, value):
        # make sure our lazy property gets set
        l = self.__len
        self._data[key] = value
        l.change(1)

    def __delitem__(self, key):
        # make sure our lazy property gets set
        l = self.__len
        del self._data[key]
        l.change(-1)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, key):
        """See interface `IReadContainer`.
        """
        return self._data[key]

    def get(self, key, default=None):
        """See interface `IReadContainer`.
        """
        return self._data.get(key, default)

    def __contains__(self, key):
        """See interface `IReadContainer`.
        """
        return key in self._data

    has_key = __contains__

    def items(self, key=None):
        return self._data.items(key)

    def keys(self, key=None):
        return self._data.keys(key)

    def values(self, key=None):
        return self._data.values(key)


@adapter
@sources(Interface)
@target(ILookup)
def SiteManagerAdapter(ob):
    """An adapter from ILocation to ILookup.

    The ILocation is interpreted flexibly, we just check for
    ``__parent__``.
    """
    current = ob
    while True:
        if ISite.providedBy(current):
            return current.getLocalLookup()
        current = getattr(current, '__parent__', None)
        if current is None:
            return implicit.lookup
