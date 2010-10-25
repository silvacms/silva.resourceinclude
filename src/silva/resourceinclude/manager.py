# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import interface
from zope import component

from silva.resourceinclude.interfaces import IResourceManager

import logging

logger = logging.getLogger('silva.resourceinclude')


class ResourceManager(object):
    """This collect a set of resource.
    """

    interface.implements(IResourceManager)

    def __init__(self, request, context, identifier, names):
        self.request = request
        self.context = context
        self.names = names
        self.identifier = identifier

    def get_resources(self):
        resources = []

        for name in self.names:
            if '/' in name:
                name, path = name.split('/', 1)
            else:
                path = None

            resource = self.search_resource(name)
            if resource is None:
                logger.debug('Missing declare resource %s' % name)
                continue

            if path is not None:
                # Broken
                resource = resource.publishTraverse(self.request, path)
                name = "/".join((name, path))

            resources.append(resource)

        return resources

    def search_resource(self, name):
        return component.queryAdapter(self.request, name=name)


class ResourceManagerFactory(object):
    """This register a set of resource together and create a given
    resource manager binded to a request.
    """

    def __init__(self, identifier):
        self.identifier = identifier
        self.names = []

    def add(self, name):
        if name not in self.names:
            self.names.append(name)

    def __call__(self, request, context):
        return ResourceManager(request, context, self.identifier, self.names)
