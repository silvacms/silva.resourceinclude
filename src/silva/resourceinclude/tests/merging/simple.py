# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
"""
You can list layers and skins for a layer and skin:

  >>> from silva.resourceinclude.utils import list_base_layers
  >>> from silva.resourceinclude.tests.merging.simple import (
  ...     IMyExtraSkin, IMyExtraLayer, IMyViewLayer, IContext, Interface)

  >>> list(list_base_layers(IMyExtraSkin))
  [<InterfaceClass silva.resourceinclude.tests.merging.simple.IMyExtraSkin>,
   <InterfaceClass silva.resourceinclude.tests.merging.simple.IMyViewLayer>,
   <InterfaceClass silva.resourceinclude.tests.merging.simple.IMyResourceLayer>,
   <InterfaceClass silva.resourceinclude.tests.merging.simple.IMyExtraLayer>]

  >>> list(list_base_layers(IMyExtraLayer))
  [<InterfaceClass silva.resourceinclude.tests.merging.simple.IMyExtraLayer>]

  >>> list(list_base_layers(IMyViewLayer))
  [<InterfaceClass silva.resourceinclude.tests.merging.simple.IMyViewLayer>,
   <InterfaceClass silva.resourceinclude.tests.merging.simple.IMyResourceLayer>]

  >>> list(list_base_layers(IContext))
  []

  >>> list(list_base_layers(object()))
  []

And from an interface its parents:

  >>> from silva.resourceinclude.utils import list_base_interfaces

  >>> list(list_base_interfaces(IContext))
  [<InterfaceClass silva.resourceinclude.tests.merging.simple.IContext>,
   <InterfaceClass zope.interface.Interface>]

  >>> list(list_base_interfaces(Interface))
  [<InterfaceClass zope.interface.Interface>]

  >>> list(list_base_interfaces(object()))
  []


Now Grok the examples, and compute all production bundle we can
make. Resources should appear in order they are registered, plus the
order of inheritence of the layers:

  >>> grok('silva.resourceinclude.tests.merging.simple')
  >>> from silva.resourceinclude.merging import list_production_resources
  >>> from silva.resourceinclude.zcml import MANAGERS

  >>> from silva.resourceinclude.tests.merging import (
  ...    display_resources, filter_resources)

  >>> resources = list(list_production_resources(MANAGERS))
  >>> len(map(display_resources, filter_resources(resources, 'css')))
  css: (IMyExtraLayer, IContext) <extra.css>
  css: (IMyExtraSkin, IContext) <cleanup.css, resource.css, view.css, extra.css, integration.css>
  css: (IMyExtraSkin, Interface) <cleanup.css, resource.css, view.css, integration.css>
  css: (IMyResourceLayer, Interface) <cleanup.css, resource.css>
  css: (IMySkin, Interface) <cleanup.css, resource.css, view.css, integration.css>
  css: (IMyViewLayer, Interface) <cleanup.css, resource.css, view.css>
  6

  >>> len(map(display_resources, filter_resources(resources, 'js')))
  js: (IMyExtraLayer, IContext) <extra.js>
  js: (IMyResourceLayer, Interface) <resource.js>
  2


"""

from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from silva.core import conf as silvaconf


class IContext(Interface):
    pass


class IMyResourceLayer(IDefaultBrowserLayer):
    silvaconf.resource('cleanup.css')
    silvaconf.resource('resource.css')
    silvaconf.resource('resource.js')


class IMyViewLayer(IMyResourceLayer):
    silvaconf.resource('view.css')


class IMyExtraLayer(IDefaultBrowserLayer):
    silvaconf.only_for(IContext)
    silvaconf.resource('extra.css')
    silvaconf.resource('extra.js')


class IMySkin(IMyViewLayer, IBrowserSkinType):
    silvaconf.resource('integration.css')


class IMyExtraSkin(IMyViewLayer, IMyExtraLayer, IBrowserSkinType):
    silvaconf.resource('integration.css')

