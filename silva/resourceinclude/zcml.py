from zope import interface
from zope import component

from zope.configuration.fields import Tokens, GlobalObject, GlobalInterface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema import TextLine

from silva.resourceinclude.manager import ResourceManagerFactory
from silva.resourceinclude.interfaces import IResourceManager

managers = {}

class IResourceIncludeDirective(interface.Interface):
    include = Tokens(
        title=u"Files to include",
        description=u"The files containing the resource data.",
        required=True,
        value_type=TextLine())

    base = TextLine(
        title=u"Base path for includes",
        required=False)

    layer = GlobalInterface(
        title=u"The layer the resource should be found in",
        description=u"""
        For information on layers, see the documentation for the skin
        directive. Defaults to "default".""",
        required=False)

    manager = GlobalObject(
        title=u"Include manager",
        required=False)


def includeDirective(_context, include,
                     base=u"",
                     layer=IDefaultBrowserLayer,
                     manager=None):
    if base:
        include = [base+'/'+name for name in include]

    _context.action(
        discriminator = ('resourceInclude', IBrowserRequest, layer, "".join(include)),
        callable = handler,
        args = (include, layer, manager, _context.info),)


def handler(include, layer, manager, info):
    """Set up includes.
    """

    global managers

    manager_override = manager is not None

    for path in include:
        try:
            extension =  path.rsplit('.', 1)[1]
        except IndexError:
            extension = None

        key = (layer, extension)

        if not manager_override:
            manager = managers.get(key)

        if manager is None:
            # create new resource manager
            managers[key] = manager = ResourceManagerFactory()

            # maintain order by creating a name that corresponds to
            # the current number of resource managers
            name = "%s-resource-manager-%03d" % (extension, len(managers))

            # register as an adapter
            component.provideAdapter(
                manager, (layer,), IResourceManager, name=name)

        manager.add(path)


