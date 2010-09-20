# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import component
from zope.configuration.fields import Tokens, GlobalInterface
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import TextLine

from silva.resourceinclude.manager import ResourceManagerFactory
from silva.resourceinclude.interfaces import IResourceManager

MANAGERS = {}


class IResourceIncludeDirective(Interface):
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
    context = GlobalInterface(
        title=u"The type of content for which the resource should be found",
        required=False)


def includeDirective(
    _context, include, base=u"", layer=IDefaultBrowserLayer, context=Interface):
    if not base:
        # Always properly set base to include things from the static directory
        base = _context.package.__name__
    include = ['/'.join((base, name)) for name in include]

    _context.action(
        discriminator = (
            'resourceInclude', layer, context, "".join(include)),
        callable = handler,
        args = (include, layer, context, _context.info),)


def handler(include, layer, context, info):
    """Set up includes.
    """
    global MANAGERS

    for path in include:
        try:
            extension =  path.rsplit('.', 1)[1]
        except IndexError:
            extension = None

        key = (layer, context, extension)

        manager = MANAGERS.get(key)
        if manager is None:
            # create new resource manager
            MANAGERS[key] = manager = ResourceManagerFactory()

            # maintain order by creating a name that corresponds to
            # the current number of resource managers
            name = "%s-resource-manager-%03d" % (extension, len(MANAGERS))

            # register as an adapter
            component.provideAdapter(
                manager, (layer, context), IResourceManager, name=name)

        manager.add(path)
