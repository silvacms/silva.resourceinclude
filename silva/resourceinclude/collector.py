# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 2
from Products.Five.browser import resource as resource_support
import Acquisition
import Globals

# Zope 3
from zope import interface, component
from zope.publisher.browser import BrowserPage
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.datetime import rfc1123_date
from zope.datetime import time as timeFromDateTimeString

# Silva
from silva.core.views.interfaces import IVirtualSite
from silva.resourceinclude.interfaces import IResourceCollector, \
    IResourceManager


import mimetypes
import tempfile
import sha
import time
import os.path


class ResourcePage(BrowserPage,  Acquisition.Explicit):

    def browserDefault(self, request):
        # HEAD and GET request are managed by methods on the object
        if request.method in ('GET', 'HEAD'):
            return self, (request.method,)
        return super(ResourcePage, self).browserDefault(request)

    def publishTraverse(self, request, name):
        # Let people traverse to method who have the same name that
        # method name
        if request.method == name and hasattr(self, name):
            return getattr(self, name)
        return super(ResourcePage, self).publishTraverse(request, name)


class MergedResourceDownloadView(ResourcePage):
    """View used to download the resource file.
    """

    def GET(self):
        """Download the merged file
        """
        response = self.request.response
        header = self.request.environ.get('If-Modified-Since', None)
        if header is not None:
            header = header.split(';')[0]
            try:
                mod_since = long(timeFromDateTimeString(header))
            except:
                mod_since = None
            if mod_since is not None:
                last_mod = long(self.context.lmt)
                if last_mod > 0 and last_mod <= mod_since:
                    response.setStatus(304)
                    return ''

        # set response headers
        response.setHeader('Content-Type', self.context.content_type)
        response.setHeader('Last-Modified', rfc1123_date(self.context.lmt))

        secs = 31536000 # one year - never expire
        t = time.time() + secs
        response.setHeader('Cache-Control', 'public,max-age=%s' % secs)
        response.setHeader(
            'Expires',
            time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(t)))

        return self.context.data()

    def HEAD(self):
        """Give cache information about the merged file
        """
        response = self.request.response
        response.setHeader('Content-Type', self.context.content_type)
        response.setHeader('Last-Modified', rfc1123_date(self.context.lmt))
        response.setHeader('Cache-Control', 'public,max-age=31536000')
        return ''


class MergedResource(object):
    """Represent a merged resource.
    """

    def __init__(self, name, file, content_type, path):
        self.basename = name
        self.__file = file
        self.__extension = mimetypes.guess_extension(content_type)
        self.filename = 'resource' + self.__extension
        self.path = path
        self.content_type = content_type
        self.lmt = time.time()

    def data(self):
        self.__file.seek(0)
        return self.__file.read()


class MergedResourceView(ResourcePage):
    """View on a merged resource: give access to the directory where
    all the merged resources where, or download the resource itself.
    """

    resource_factories = {
        'gif':  resource_support.ImageResourceFactory,
        'png':  resource_support.ImageResourceFactory,
        'jpg':  resource_support.ImageResourceFactory,
        }
    default_factory = resource_support.FileResourceFactory,

    def __call__(self):
        virtual_site = component.getAdapter(self.request, IVirtualSite)
        return "%s/++resource++%s/%s" % (
            virtual_site.get_root_url(),
            self.context.basename,
            self.context.filename)

    def publishTraverse(self, request, name):
        if name == self.context.filename:
            return MergedResourceDownloadView(self.context, request)

        filename = os.path.join(self.context.path, name)
        isfile = os.path.isfile(filename)
        isdir = os.path.isdir(filename)

        if not (isfile or isdir):
            return super(MergedResourceView, self).publishTraverse(
                request, name)

        if isfile:
            ext = name.split('.')[-1]
            factory = self.resource_factories.get(ext, self.default_factory)
        else:
            factory = resource_support.DirectoryResourceFactory
        return factory(name, filename)(self.request)

    def GET(self):
        """Return nothing when viewing the directory itself.
        """
        return ''

    def HEAD(self):
        """Return nothing when viewing the directory itself.
        """
        return ''



class MergedResourceFactory(object):
    """View resource factory for merged resource.
    """

    def __init__(self, resource):
        self.__resource = resource

    def __call__(self, request):
        return MergedResourceView(self.__resource, request)


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
        #return
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
                    resource = MergedResource(
                        name, merged_file, content_type, base_path)

                    factory = MergedResourceFactory(resource)

                    # register factory
                    component.provideAdapter(
                        factory,
                        (IBrowserRequest,),
                        interface.Interface,
                        name=name)

                    existing_resource = factory(self.request)

                merged.append(existing_resource.__of__(context))
