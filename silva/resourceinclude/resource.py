# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 2
from Products.Five.browser import resource as resource_support
import Acquisition

# Zope 3
from five import grok
from zope import interface, component
from zope.publisher.browser import BrowserPage
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.datetime import rfc1123_date
from zope.datetime import time as timeFromDateTimeString

# Silva
from silva.core.views.interfaces import IVirtualSite
from silva.resourceinclude.interfaces import IResource

import mimetypes
import time
import os


class ResourcePage(BrowserPage,  Acquisition.Explicit, grok.MultiAdapter):
    grok.adapts(IResource, IBrowserRequest)
    grok.baseclass()
    grok.provides(interface.Interface)

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


class ResourceView(ResourcePage):
    """View used to download the resource file.
    """

    def __call__(self):
        virtual_site = component.getAdapter(self.request, IVirtualSite)
        return "%s/++resource++%s/%s" % (
            virtual_site.get_root_url(),
            self.context.basename,
            self.context.filename)

    def GET(self):
        """Download resource.
        """
        response = self.request.response
        header = self.request.environ.get('HTTP_IF_MODIFIED_SINCE', None)
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


class FileResource(object):
    """A resource representing a file on the FS.
    """
    grok.implements(IResource)

    def __init__(self, name, path):
        self.filename = name
        self.path = path
        self.__file = open(path, 'r')
        self.content_type = mimetypes.guess_extension(path)[0]
        self.lmt = os.stat(path)[8]

    def data(self):
        self.__file.seek(0)
        return self.__file.read()


class DirectoryResource(object):
    """A resource representing a directory on the FS.
    """
    grok.implements(IResource)

    def __init__(self, name, path):
        self.filename = name
        self.path = path
        self.content_type = None
        self.lmt = os.stat(path)[8]

    def data(self):
        return ''


class DirectoryResourceView(ResourceView):
    """View on a merged resource: give access to the directory where
    all the merged resources where, or download the resource itself.
    """
    grok.adapts(DirectoryResource, IBrowserRequest)

    def resource(self, name):
        path = os.path.join(self.context.path, name)
        isfile = os.path.isfile(path)
        isdir = os.path.isdir(path)

        if not (isfile or isdir):
            return super(DirectoryResourceView, self).publishTraverse(
                request, name)

        if isfile:
            factory = FileResource
        else:
            factory = DirectoryResource
        return factory(name, path)

    def publishTraverse(self, request, name):
        resource = self.get_resource(name)
        return component.getMultiAdapter((resource, request,), Interface)


class MergedResource(object):
    """Represent a merged resource.
    """
    grok.implements(IResource)

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


class MergedDirectoryResource(DirectoryResource):
    """Report a directory containing a merged resource.
    """
    grok.implements(IResource)

    def __init__(self, merged_resource):
        self.resource = merged_resource

    def __getattr__(self, key):
        if not key in self.__dict__:
            return getattr(self.resource, key)
        return super(MergedDirectoryResource, self).__getattr__(key)


class MergedDirectoryResourceView(DirectoryResourceView):
    """View on a merged resource: give access to the directory where
    all the merged resources where, or download the resource itself.
    """
    grok.adapts(MergedDirectoryResource, IBrowserRequest)

    def resource(self, name):
        if name == self.context.filename:
            return self.context.resource
        return super(MergedDirectoryResourceView, self).get_resource(name)


class ResourceFactory(object):
    """Resource factory.
    """

    def __init__(self, resource):
        self.__resource = resource

    def __call__(self, request):
        return component.getMultiAdapter(
            (self.__resource, request,), Interface)
