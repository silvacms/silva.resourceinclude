# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import operator

# Zope 3
from five import grok
from zope import interface, component
from zope.publisher.interfaces.browser import IBrowserRequest

import Globals

# Silva
from silva.resourceinclude.interfaces import IResourceCollector
from silva.resourceinclude.interfaces import IDevelopmentResourceManager
from silva.resourceinclude.interfaces import IProductionResourceManager


class ResourceCollector(grok.MultiAdapter):
    grok.implements(IResourceCollector)
    grok.provides(IResourceCollector)
    grok.adapts(interface.Interface, IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def order_by_type(self, resources):
        resources.sort(key=lambda resource: resource.context.content_type)

    def get_managers(self):
        #the IProductionResourceManager does not work, so commenting it out
        #interface = IProductionResourceManager
        #if Globals.DevelopmentMode:
        #the development one does, and is just as good as not using resource
        # collecting, so use it always
        interface = IDevelopmentResourceManager
        managers = map(
            operator.itemgetter(1),
            component.getAdapters((self.request, self.context), interface))
        managers.sort(key=operator.attrgetter('identifier'))
        return managers

    def collect(self):
        resources = []
        for manager in self.get_managers():
            resources.extend(manager.get_resources())
        self.order_by_type(resources)
        return tuple(resources)
