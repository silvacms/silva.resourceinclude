# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from martian.error import GrokError
import martian

from zope.interface.interface import InterfaceClass
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from silva.resourceinclude.zcml import register_development_resources
from silva.core.conf.martiansupport import directives as silvaconf

_marker = object()


class ResourceIncludeGrokker(martian.InstanceGrokker):
    martian.component(InterfaceClass)

    def grok(self, name, interface, module_info, config, **kw):
        resources = silvaconf.resource.bind(default=_marker).get(interface)
        if resources is _marker:
            return False
        if not interface.extends(IDefaultBrowserLayer):
            raise GrokError(
                "A resource can be included only on a layer.", interface)

        if module_info.isPackage():
            resource_dir = module_info.getModule().__name__
        else:
            base = module_info.getModule().__name__
            resource_dir = '.'.join(base.split('.')[:-1])

        resources = [resource_dir + '/' + r for r in resources]
        context = silvaconf.only_for.bind().get(interface)

        config.action(
            discriminator = (
                'resourceInclude', interface, context, "".join(resources)),
            callable = register_development_resources,
            args = (resources, interface, context, None))

        return True
