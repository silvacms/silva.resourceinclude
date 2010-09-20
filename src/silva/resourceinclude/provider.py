# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import os.path

from five import grok
from zope import component, interface

from chameleon.zpt.template import PageTemplateFile
from plone.memoize import ram
from silva.core.views import views as silvaviews
from silva.resourceinclude.interfaces import IResourceCollector


def local_file(filename):
    return os.path.join(os.path.dirname(__file__), filename)


def interfaces_identifiers(obj):
    return tuple(map(lambda i: i.__identifier__, obj.__provides__.interfaces()))


def cache_key(method, obj):
    return interfaces_identifiers(obj.request) + \
        interfaces_identifiers(obj.context) + \
        (obj.request['HTTP_HOST'],)


class ResourceIncludeProvider(silvaviews.ContentProvider):
    grok.context(interface.Interface)
    grok.name('resources')

    template = PageTemplateFile(local_file("provider.pt"))

    @ram.cache(cache_key)
    def render(self):
        collector = component.getMultiAdapter(
            (self.context, self.request), IResourceCollector)
        resources = [
            {'content_type': resource.context.content_type,
             'url': resource()} for
            resource in collector.collect()]

        return self.template(resources=resources)
