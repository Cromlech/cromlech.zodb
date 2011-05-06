import zope.component.interfaces


class ILocalSiteManager(zope.component.interfaces.IComponents):
    """Site Managers act as containers for registerable components.

    If a Site Manager is asked for an adapter or utility, it checks for those
    it contains before using a context-based lookup to find another site
    manager to delegate to.  If no other site manager is found they defer to
    the global site manager which contains file based utilities and adapters.
    
    Note : taken from zope.site
    """
