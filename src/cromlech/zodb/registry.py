# -*- coding: utf-8 -*-

from crom.registry import Registry
from persistent import Persistent
from zope.location import Location


class PersistentAdapterRegistry(AdapterRegistry, Persistent):
    """FIXME
    """

    def changed(self, originally_changed):
        if originally_changed is self:
            self._p_changed = True
        super(PersistentRegistry, self).changed(originally_changed)

    def __getstate__(self):
        state = super(PersistentRegistry, self).__getstate__().copy()
        for name in self._delegated:
            state.pop(name, 0)
        return state

    def __setstate__(self, state):
        super(PersistentRegistry, self).__setstate__(state)
        self._createLookup()
        self._v_lookup.changed(self)


class LocalRegistryWrapper(Location):
    """FIXME
    """
    def __init__(self, name, parent, registry):
        self.registry = registry
