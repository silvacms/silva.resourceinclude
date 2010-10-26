# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
"""
You can list layers and skins for a layer and skin:

  >>> from silva.resourceinclude.utils import list_base_layers
  >>> from silva.resourceinclude.tests.merging.listing import (
  ...     IMyExtraSkin, IMyExtraLayer, IMyViewLayer, IContext, Interface)

  >>> list(list_base_layers(IMyExtraSkin))
  [<InterfaceClass silva.resourceinclude.tests.merging.listing.IMyExtraSkin>,
   <InterfaceClass silva.resourceinclude.tests.merging.listing.IMyViewLayer>,
   <InterfaceClass silva.resourceinclude.tests.merging.listing.IMyResourceLayer>,
   <InterfaceClass silva.resourceinclude.tests.merging.listing.IMyExtraLayer>]

  >>> list(list_base_layers(IMyExtraLayer))
  [<InterfaceClass silva.resourceinclude.tests.merging.listing.IMyExtraLayer>]

  >>> list(list_base_layers(IMyViewLayer))
  [<InterfaceClass silva.resourceinclude.tests.merging.listing.IMyViewLayer>,
   <InterfaceClass silva.resourceinclude.tests.merging.listing.IMyResourceLayer>]

  >>> list(list_base_layers(IContext))
  []

  >>> list(list_base_layers(object()))
  []

And from an interface its parents:

  >>> from silva.resourceinclude.utils import list_base_interfaces

  >>> list(list_base_interfaces(IContext))
  [<InterfaceClass silva.resourceinclude.tests.merging.listing.IContext>,
   <InterfaceClass zope.interface.Interface>]

  >>> list(list_base_interfaces(Interface))
  [<InterfaceClass zope.interface.Interface>]

  >>> list(list_base_interfaces(object()))
  []


Now Grok the examples, and compute all production bundle we can
make. Resources should appear in order they are registered, plus the
order of inheritence of the layers:

  >>> grok('silva.resourceinclude.tests.merging.listing')
  >>> from silva.resourceinclude.merging import list_production_resources
  >>> from silva.resourceinclude.zcml import MANAGERS
  >>> import operator
  >>> import os.path

  >>> def display((layer, context, managers, type),):
  ...   resources = ', '.join(map(lambda p: os.path.basename(p),
  ...                             reduce(operator.add,
  ...                                    map(operator.attrgetter('names'),
  ...                                        managers))))
  ...   print "%s: (%s, %s) <%s>" % (type, layer.__name__, context.__name__, resources)

  >>> len(map(display, sorted(list_production_resources(MANAGERS))))
  css: (IMyExtraLayer, Interface) <extra.css>
  js: (IMyExtraLayer, Interface) <extra.js>
  css: (IMyResourceLayer, Interface) <cleanup.css, resource.css>
  js: (IMyResourceLayer, Interface) <resource.js>
  css: (IMySkin, Interface) <cleanup.css, resource.css, view.css, integration.css>
  css: (IMyViewLayer, Interface) <cleanup.css, resource.css, view.css>
  6

"""

from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from silva.core import conf as silvaconf


class IMyResourceLayer(IDefaultBrowserLayer):
    silvaconf.resource('cleanup.css')
    silvaconf.resource('resource.css')
    silvaconf.resource('resource.js')


class IMyViewLayer(IMyResourceLayer):
    silvaconf.resource('view.css')


class IMyExtraLayer(IDefaultBrowserLayer):
    silvaconf.resource('extra.css')
    silvaconf.resource('extra.js')


class IMySkin(IMyViewLayer, IBrowserSkinType):
    silvaconf.resource('integration.css')


class IMyExtraSkin(IMyViewLayer, IMyExtraLayer, IBrowserSkinType):
    pass


class IContext(Interface):
    pass
