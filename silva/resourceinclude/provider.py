# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from z3c.resourceinclude import provider
from silva.core.views import views
from silva.core import conf as silvaconf

class ResourceIncludeProvider(provider.ResourceIncludeProvider, views.ContentProvider):

    silvaconf.name('resources')

    def update(self):
        super(ResourceIncludeProvider, self).update()
        self.collector = self.collector.__of__(self.context)
