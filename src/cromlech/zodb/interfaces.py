# -*- coding: utf-8 -*-

from zope.interface import Interface
from crom import IRegistry


class ILocalRegistry(IRegistry):
    """FIXME
    """


class ILookupNode(Interface):
    """A lookup node is a part of a lookup chain. Mainly, it's used as
    an abstraction for the persistant registries.
    """

    def setLocalRegistry(registry):
        """FIXME
        """

    def getLocalRegistry():
        """FIXME
        """


class IDBInitializer(Interface):
    """FIXME.
    """
    def __call__(db):
        """FIXME
        """
