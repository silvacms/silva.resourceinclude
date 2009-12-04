# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 2
from Products.Five.browser import resource as resource_support
import Acquisition

# Zope 3
from zope import component
from zope.publisher.browser import BrowserPage
from zope.datetime import rfc1123_date
from zope.datetime import time as timeFromDateTimeString

# Silva
from silva.core.views.interfaces import IVirtualSite

import mimetypes
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
