
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

from Products.Silva.interfaces import  IVirtualHosting

import mimetypes
import tempfile
import sha
import time
import urllib

import Globals

class TemporaryResource(resource.FileResource):
    """A publishable file-based resource"""

    def __init__(self, request, f, content_type, lmt):
        self.request = request
        self.__file = f
        self.content_type = content_type
        self.lmt = lmt
        self.context = self

    def browserDefault(self, request):
        return self.__browser_default__(request)

    def __call__(self):
        name = self.__name__
        container = self.aq_parent.context
        root = IVirtualHosting(container).getSilvaOrVirtualRoot()
        return "%s/++resource++%s" % (root.absolute_url(), name)

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
                last_mod = long(lmt)
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
            'Expires', time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(t)))

        f = self.__file
        f.seek(0)
        return f.read()

    def HEAD(self):
        file = self.context
        response = self.request.response
        response.setHeader('Content-Type', self.content_type)
        response.setHeader('Last-Modified', self.lmt)
        # Cache for one day
        response.setHeader('Cache-Control', 'public,max-age=31536000')
        return ''



class TemporaryResourceFactory(object):
    def __init__(self, f, resource, content_type, name):
        self.__file = f
        self.__name = name
        self.__parent = resource.__parent__
        self.content_type = content_type
        self.lmt = time.time()

    def __call__(self, request):
        resource = TemporaryResource(request, self.__file, self.content_type, self.lmt)
        resource.__name__ = self.__name
        resource.__parent__ = self.__parent
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
        if Globals.DevelopmentMode:
            return

        parent = self.aq_parent
        by_type = {}
        for resource in resources:
            by_type.setdefault(resource.context.content_type, []).append(resource)

        del resources[:]
        merged = resources

        for content_type, resources in by_type.items():
            f = tempfile.TemporaryFile()

            for resource in resources:
                resource_file = open(resource.context.path, 'rb')
                print >> f, "/* %s */" % resource.__name__
                f.write(resource_file.read())
                print >> f, ""
                resource_file.close()

            # generate filename
            ext = mimetypes.guess_extension(content_type)
            f.seek(0)
            digest = sha.new(f.read()).hexdigest()
            name = digest + ext

            # check if resource is already registered
            res = component.queryAdapter((self.request,), name=name)

            if res is None:
                factory = TemporaryResourceFactory(f, resource, content_type, name)

                # register factory
                component.provideAdapter(
                    factory, (IBrowserRequest,), interface.Interface, name=name)

                res = factory(self.request)

            merged.append(res.__of__(parent))
