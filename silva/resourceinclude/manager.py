# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import interface
from zope import component

from silva.resourceinclude.interfaces import IResourceManager


class ResourceManager(object):

    def __init__(self, request, names):
        self.request = request
        self.names = names

    def get_resources(self):
        resources = []

        for name in self.names:
            if '/' in name:
                name, path = name.split('/', 1)
            else:
                path = None

            resource = self.search_resource(name)

            if path is not None:
                # Broken
                resource = resource[path]
                name = "/".join((name, path))

            resources.append((name, resource))

        return resources

    def search_resource(self, name):
        return component.queryAdapter(self.request, name=name)


class ResourceManagerFactory(object):

    interface.implements(IResourceManager)

    def __init__(self):
        self.names = []

    def add(self, name):
        if name not in self.names:
            self.names.append(name)

    def __call__(self, request):
        return ResourceManager(request, self.names)



