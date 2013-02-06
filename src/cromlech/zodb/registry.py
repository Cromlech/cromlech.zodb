# -*- coding: utf-8 -*-

from crom.registry import Registry
from persistent import Persistent
from zope.interface.adapter import VerifyingAdapterRegistry
from zope.location import Location


class PersistentAdapterRegistry(VerifyingAdapterRegistry, Persistent):
    """FIXME
    """

    def changed(self, originally_changed):
        if originally_changed is self:
            self._p_changed = True
        super(PersistentAdapterRegistry, self).changed(originally_changed)

    def __getstate__(self):
        state = super(PersistentAdapterRegistry, self).__getstate__().copy()
        for name in self._delegated:
            state.pop(name, 0)
        return state

    def __setstate__(self, state):
        super(PersistentAdapterRegistry, self).__setstate__(state)
        self._createLookup()
        self._v_lookup.changed(self)


class PersistentRegistry(Location, Registry):
    
    def __init__(self):
        self.registry = PersistentAdapterRegistry()
