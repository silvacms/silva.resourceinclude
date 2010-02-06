# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok
from zope import interface, component
from zope.datetime import rfc1123_date
from zope.datetime import time as timeFromDateTimeString
from zope.publisher.browser import BrowserPage
from zope.publisher.interfaces.browser import IBrowserRequest

# Silva
from silva.core.views.interfaces import IVirtualSite
from silva.resourceinclude.interfaces import IResource

import mimetypes
import time
import os

CACHE_TIME = 31536000 # one year - never expire


class ResourceView(BrowserPage, grok.MultiAdapter):
    """View used to download the resource file.
    """
    grok.adapts(IResource, IBrowserRequest)
    grok.provides(interface.Interface)

    def browserDefault(self, request):
        # HEAD and GET request are managed by methods on the object
        if request.method in ('GET', 'HEAD'):
            return self, (request.method,)
        return super(ResourceView, self).browserDefault(request)

    def publishTraverse(self, request, name):
        # Traverse to methods GET and HEAD
        if request.method == name and hasattr(self, name):
            return getattr(self, name)
        # Traverse to sub-resources
        try:
            resource = self.context[name]
        except KeyError:
            # No sub-resources, default to default behavior
            return super(ResourceView, self).publishTraverse(request, name)
        return component.getMultiAdapter(
            (resource, request,), interface.Interface)

    def get_relative_path(self):
        """Return the relative path of the resource from the begining
        of the resource tree.
        """
        resource = self.context
        resource_path = [resource.filename,]
        while hasattr(resource, '__parent__'):
            resource = resource.__parent__
            resource_path.append(resource.filename)
        return resource_path

    def __call__(self):
        """Compute resource URL.
        """
        virtual_site = component.getAdapter(self.request, IVirtualSite)
        return u"%s/++resource++%s" % (
            virtual_site.get_root_url(), u'/'.join(self.get_relative_path()))

    def __set_http_headers(self):
        """Set HTTP headers on the reply.
        """
        response = self.request.response
        expires = time.time() + CACHE_TIME
        # set response headers
        response.setHeader('Content-Type', self.context.content_type)
        response.setHeader('Cache-Control', 'public,max-age=%s' % CACHE_TIME)
        response.setHeader('Last-Modified', rfc1123_date(self.context.lmt))
        response.setHeader('Expires', rfc1123_date(expires))

    def GET(self):
        """Download the resource if it have been modified.
        """
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
                    self.request.response.setStatus(304)
                    return u''

        self.__set_http_headers()
        return self.context.data()

    def HEAD(self):
        """Give information about the resource.
        """
        self.__set_http_headers()
        return u''


class FileResource(object):
    """A resource representing a file on the file system.
    """
    grok.implements(IResource)

    def __init__(self, name, path):
        self.filename = name
        self.path = path
        self.content_type = mimetypes.guess_type(path)[0]
        self.lmt = os.stat(path)[8]

    def __getitem__(self, name):
        raise KeyError(name)

    def data(self):
        file = open(path, 'r')
        data = file.read()
        file.close()
        return data


class DirectoryResource(object):
    """A resource representing a directory on the file system. You can
    access subdirectories and files as resources.
    """
    grok.implements(IResource)

    def __init__(self, name, path):
        self.filename = name
        self.path = path
        self.content_type = None
        self.lmt = os.stat(path)[8]

    def __getitem__(self, name):
        path = os.path.join(self.path, name)
        isfile = os.path.isfile(path)
        isdir = os.path.isdir(path)

        if not (isfile or isdir):
            raise KeyError(name)

        if isfile:
            factory = FileResource
        else:
            factory = DirectoryResource
        resource = factory(name, path)
        resource.__parent__ = self
        return resource

    def data(self):
        return u''


class MergedResource(object):
    """Represent a merged resource.
    """
    grok.implements(IResource)

    def __init__(self, merged_file, content_type):
        self.__file = merged_file
        self.__extension = mimetypes.guess_extension(content_type)
        self.filename = 'resource' + self.__extension
        self.path = None
        self.content_type = content_type
        self.lmt = time.time()

    def data(self):
        self.__file.seek(0)
        return self.__file.read()


class MergedDirectoryResource(DirectoryResource):
    """Report a directory containing a merged resource.
    """
    grok.implements(IResource)

    def __init__(self, name, path, merged_resource):
        self.resource = merged_resource
        self.resource.__parent__ = self
        self.filename = name
        self.path = path
        self.content_type = self.resource.content_type
        self.lmt = time.time()

    def __getitem__(self, name):
        if name == self.resource.filename:
            return self.resource
        return super(MergedDirectoryResource, self).__getitem__(name)


class MergedDirectoryResourceView(ResourceView):
    """View used to access a merged resource.
    """
    grok.adapts(MergedDirectoryResource, IBrowserRequest)

    def get_relative_path(self):
        path = super(MergedDirectoryResourceView, self).get_relative_path()
        path.append(self.context.resource.filename)
        return path


class ResourceFactory(object):
    """Resource factory. We are not returning the resource itself, but
    a view on it.
    """

    def __init__(self, resource):
        self.__resource = resource

    def __call__(self, request):
        return component.getMultiAdapter(
            (self.__resource, request,), interface.Interface)
