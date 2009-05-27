# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Five.browser import resource
from z3c.resourceinclude import collector
import Acquisition
import time

from zope import interface
from zope import component

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.browser import TestRequest
from zope.app.publisher.browser.resource import Resource
from zope.publisher.interfaces import NotFound
from zope.datetime import rfc1123_date
from zope.datetime import time as timeFromDateTimeString

from z3c.resourceinclude.interfaces import IResourceCollector
from z3c.resourceinclude.interfaces import IResourceManager
from zope.traversing.browser.interfaces import IAbsoluteURL

from silva.core.views.interfaces import IVirtualSite

import mimetypes
import tempfile
import sha
import time
import urllib
import os.path

import Globals

class TemporaryResource(resource.FileResource):
    """A publishable file-based resource"""

    def __init__(self, request, merged_file, content_type, lmt):
        self.request = request
        self.__file = merged_file
        self.content_type = content_type
        self.lmt = lmt

    def browserDefault(self, request):
        return self.__browser_default__(request)

    def __call__(self):
        return self.__parent__.__call__()

    def GET(self):
        """Zope 2.
        """
        lmt = self.lmt

        request = self.request
        response = request.RESPONSE
        header = request.environ.get('If-Modified-Since', None)
        if header is not None:
            header = header.split(';')[0]
            try:    mod_since=long(timeFromDateTimeString(header))
            except: mod_since=None
            if mod_since is not None:
                last_mode = long(self.lmt)
                if last_mod > 0 and last_mod <= mod_since:
                    response.setStatus(304)
                    return ''

        # set response headers
        response.setHeader('Content-Type', self.content_type)
        response.setHeader('Last-Modified', rfc1123_date(lmt))

        secs = 31536000 # one year - never expire
        t = time.time() + secs
        response.setHeader('Cache-Control', 'public,max-age=%s' % secs)
        response.setHeader(
            'Expires',
            time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(t)))

        self.__file.seek(0)
        return self.__file.read()

    def HEAD(self):
        """Zope 2.
        """
        response = self.request.response
        response.setHeader('Content-Type', self.content_type)
        response.setHeader('Last-Modified', self.lmt)
        response.setHeader('Cache-Control', 'public,max-age=31536000')
        return ''


_marker = object()

class TemporaryDirectoryResource(resource.DirectoryResource):

    def __init__(self, context, request, merged_file,
                 content_type, extension, path, lmt):
        super(TemporaryDirectoryResource, self).__init__(context, request)
        self.__file = merged_file
        self.__merged_name = 'resource' + extension
        self.__extension = extension
        self.__path = path
        self.content_type = content_type
        self.lmt = lmt

    def __call__(self):
        name = self.__name__
        container = self.__parent__
        virtual_site = component.getMultiAdapter(
            (container, self.request,), IVirtualSite)
        root = virtual_site.get_root()
        return "%s/++resource++%s/%s" % (
            root.absolute_url(), name, self.__merged_name)

    def get(self, name, default=_marker):
        if name == self.__merged_name:
            resource = TemporaryResource(
                self.request, self.__file, self.content_type, self.lmt)
            resource.__name__ = self.__merged_name
        else:
            filename = os.path.join(self.__path, name)
            isfile = os.path.isfile(filename)
            isdir = os.path.isdir(filename)

            if not (isfile or isdir):
                if default is _marker:
                    raise KeyError(name)
                return default

            if isfile:
                ext = name.split('.')[-1]
                factory = self.resource_factories.get(ext, self.default_factory)
            else:
                factory = resource.DirectoryResourceFactory

            resource = factory(name, filename)(self.request)
            resource.__name__ = name
        resource.__parent__ = self
        # XXX __of__ wrapping is usually done on traversal.
        # However, we don't want to subclass Traversable (or do we?)
        # The right thing should probably be a specific (and very simple)
        # traverser that does __getitem__ and __of__.
        return resource.__of__(self)


class TemporaryResourceFactory(object):

    def __init__(self, context, merged_file, name, content_type, path):
        self.__file = merged_file
        self.__name = name
        self.__extension = mimetypes.guess_extension(content_type)
        self.__path = path
        self.context = context
        self.content_type = content_type
        self.lmt = time.time()

    def __call__(self, request):
        resource = TemporaryDirectoryResource(
            self.context, request, self.__file, self.content_type,
            self.__extension, self.__path, self.lmt)
        resource.__name__ = self.__name
        resource.__parent__ = self.context
        return resource


class ResourceCollector(collector.ResourceCollector, Acquisition.Implicit):

    def _get_request(self):
        return self.request

    def _get_managers(self):
        parent = self.aq_parent
        return [(name, manager.__of__(parent)) for name, manager in \
                    super(ResourceCollector, self)._get_managers()]

    def collect(self):
        resources = []
        names = []

        request = self._get_request()

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
        #if Globals.DevelopmentMode:
        #    return

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
                base_path = '/'.join(resource.context.path.split('/')[:-1])
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

                # check if resource is already registered
                existing_resource = component.queryAdapter(
                    (self.request,), name=name)

                if existing_resource is None:
                    factory = TemporaryResourceFactory(
                        context, merged_file, name, content_type, base_path)

                    # register factory
                    component.provideAdapter(
                        factory, (IBrowserRequest,), interface.Interface, name=name)

                    existing_resource = factory(self.request)

                merged.append(existing_resource.__of__(context))
