# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# XXX needs improvements. We replace the grok implementation of
# resources with ours.

from zope import component, interface
from silva.resourceinclude.resource import ResourceFactory, DirectoryResource

def _register_resource(config, resource_path, name, layer):
    resource_factory = ResourceFactory(DirectoryResource(
            name, resource_path))
    adapts = (layer,)
    provides = interface.Interface

    config.action(
        discriminator=('adapter', adapts, provides, name),
        callable=component.provideAdapter,
        args=(resource_factory, adapts, provides, name),
        )
    return True


import five.grok.meta
five.grok.meta._register_resource = _register_resource
