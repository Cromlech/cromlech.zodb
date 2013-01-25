# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.interface.interfaces import IRegistry


class ILocalRegistry(IRegistry):
    """FIXME
    """


class ISite(Interface):

    def setLocalRegistry(registry):
        """FIXME
        """

    def getLocalRegistry():
        """FIXME
        """
