# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 2
import Acquisition
import Globals

# Zope 3
from zope import interface, component
from zope.publisher.interfaces.browser import IBrowserRequest

# Silva
from silva.resourceinclude.interfaces import IResourceCollector, \
    IResourceManager
from silva.resourceinclude.resource import (
    MergedResource, MergedDirectoryResource, ResourceFactory)

import tempfile
import sha
import os.path

import threading
lock = threading.Lock()



class ResourceCollector(Acquisition.Implicit):
    interface.implements(IResourceCollector)
    component.adapts(IBrowserRequest)

    def __init__(self, request):
        self.request = request

    def sort(self, resources):
        resources.sort(key=lambda resource: resource.context.content_type)

    def _get_managers(self):
        parent = self.aq_parent
        managers = [(name, manager.__of__(parent)) for name, manager in
                    component.getAdapters((self.request,), IResourceManager)
                    if manager.available()]

        managers.sort(key=lambda (name, manager): name)
        return managers


    def collect(self):
        resources = []
        names = []

        request = self.request

        for name, manager in self._get_managers():
            items = manager.getResources(request)

            # filter out duplicates
            rs = [resource for name, resource in items if name not in names]
            names.extend((name for name, resource in items))

            resources.extend(rs)

        # sort & merge
        self.sort(resources)
        self.merge(resources)
        return tuple(resources)


    def merge(self, resources):
        if Globals.DevelopmentMode:
           return

        context = self.aq_parent.context
        by_type = {}
        for resource in resources:
            by_type.setdefault(
                resource.context.content_type, []).append(resource)

        del resources[:]
        merged = resources

        for content_type, resources in by_type.items():
            by_path = {}
            previous_path = None
            order_path = []
            for resource in resources:
                base_path = os.path.sep.join(
                    resource.context.path.split(os.path.sep)[:-1])
                if previous_path != base_path:
                    order_path.append(base_path)
                by_path.setdefault(base_path, []).append(resource)
                previous_path = base_path

            for base_path in order_path:
                resources = by_path[base_path]
                merged_file = tempfile.TemporaryFile()

                for resource in resources:
                    resource_file = open(resource.context.path, 'rb')
                    print >> merged_file, "/* %s */" % resource.__name__
                    merged_file.write(resource_file.read())
                    print >> merged_file, ""
                    resource_file.close()

                # generate filename
                merged_file.seek(0)
                digest = sha.new(merged_file.read()).hexdigest()
                name = digest

                lock.acquire()
                try:
                    # check if resource is already registered
                    existing_resource = component.queryAdapter(
                        (self.request,), name=name)

                    if existing_resource is None:
                        resource = MergedDirectoryResource(
                            name,
                            base_path,
                            MergedResource(merged_file, content_type))

                        factory = ResourceFactory(resource)

                        # register factory
                        component.provideAdapter(
                            factory,
                            (IBrowserRequest,),
                            interface.Interface,
                            name=name)

                        existing_resource = factory(self.request)
                finally:
                    lock.release()

                merged.append(existing_resource.__of__(context))
