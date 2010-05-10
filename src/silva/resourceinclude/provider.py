# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope import component, interface
from zope.publisher.interfaces.browser import IBrowserView

from chameleon.zpt.template import PageTemplateFile
from plone.memoize import ram
from silva.core.views import views as silvaviews
from silva.resourceinclude.interfaces import IResourceCollector

import os.path
import mimetypes
if not '.kss' in mimetypes.types_map:
    mimetypes.add_type('text/kss', '.kss')


def local_file(filename):
    return os.path.join(os.path.dirname(__file__), filename)


def _render_cachekey(method, obj):
    return tuple(map(lambda i: i.__identifier__,
                     obj.request.__provides__.interfaces()))


class ResourceIncludeProvider(silvaviews.ContentProvider):
    grok.context(interface.Interface)
    grok.name('resources')

    template = PageTemplateFile(local_file("provider.pt"))

    def update(self):
        self.collector = component.getMultiAdapter(
            (self.context, self.request), IResourceCollector)

    @ram.cache(_render_cachekey)
    def render(self):
        resources = [
            {'content_type': resource.context.content_type,
             'url': resource()} for
            resource in self.collector.collect()]

        return self.template(resources=resources)
