# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
from zope import interface
from zope import component

from silva.resourceinclude.interfaces import IResourceManager

import Acquisition

class ResourceManager(Acquisition.Implicit):

    interface.implements(IResourceManager)

    def __init__(self):
        self.names = []

    def __call__(self, request):
        return self

    def available(self):
        return True

    def add(self, name):
        if name not in self.names:
            self.names.append(name)

    def getResources(self, request):
        resources = []

        for name in self.names:
            if '/' in name:
                name, path = name.split('/', 1)
            else:
                path = None

            resource = self.searchResource(request, name)

            if path is not None:
                resource = resource[path]
                name = "/".join((name, path))

            resources.append((name, resource))

        return resources

    def searchResource(self, request, name):
        resource = component.queryAdapter(request, name=name)
        if resource:
            parent = self.aq_parent
            return resource.__of__(parent)
        return resource


