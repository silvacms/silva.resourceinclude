# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from itertools import repeat
import hashlib
import logging
import operator
import os.path
import cssmin
import tempfile

from five import grok
from zope import component
from zope.configuration.fields import Tokens, GlobalInterface
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.processlifetime import IProcessStarting
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import TextLine

from silva.resourceinclude.manager import ResourceManagerFactory
from silva.resourceinclude.interfaces import IDevelopmentResourceManager
from silva.resourceinclude.interfaces import IProductionResourceManager
from silva.core.conf.martiansupport import directives as silvaconf
from silva.resourceinclude.resource import (
    MergedResource, MergedDirectoryResource, ResourceFactory)


MANAGERS = {}
SLIMMERS = {'text/css': cssmin.cssmin}
CONTENT_TYPES = {'js': 'application/javascript',
                 'css': 'text/css'}
_marker = object()
logger = logging.getLogger('silva.resourceinclude')


class IResourceIncludeDirective(Interface):
    include = Tokens(
        title=u"Files to include",
        description=u"The files containing the resource data.",
        required=True,
        value_type=TextLine())
    base = TextLine(
        title=u"Base path for includes",
        required=False)
    layer = GlobalInterface(
        title=u"The layer the resource should be found in",
        description=u"""
        For information on layers, see the documentation for the skin
        directive. Defaults to "default".""",
        required=False)
    context = GlobalInterface(
        title=u"The type of content for which the resource should be found",
        required=False)


class IResourcesIncludeDirective(Interface):
    resources = GlobalInterface(
        title=u"Interface with resources attached to it",
        description=u"Interface from which a list of resources "\
            u"can be collected from",
        required=True)
    layer = GlobalInterface(
        title=u"The layer the resource should be found in",
        description=u"""
        For information on layers, see the documentation for the skin
        directive. Defaults to "default".""",
        required=False)
    context = GlobalInterface(
        title=u"The type of content for which the resource should be found",
        required=False)


def include_directive(
    _context, include, base=u"", layer=IDefaultBrowserLayer, context=Interface):
    if not base:
        # Always properly set base to include things from the static directory
        base = _context.package.__name__
    include = ['/'.join((base, name)) for name in include]

    _context.action(
        discriminator = (
            'resourceInclude', layer, context, "".join(include)),
        callable = handler,
        args = (include, layer, context, _context.info),)


def list_base_layers(interface):
    yield interface
    for base in interface.__bases__:
        if base in (
            IDefaultBrowserLayer, IBrowserSkinType, IBrowserRequest, Interface):
            continue
        for base_base in list_base_layers(base):
            yield base_base

def list_base_interfaces(interface):
    yield interface
    for base in interface.__bases__:
        for base_base in list_base_interfaces(base):
            yield base_base


def include_layer_directive(
    _context, resources, layer=IDefaultBrowserLayer, context=Interface):

    for base in list_base_layers(resources):
        files = silvaconf.resource.bind(default=_marker).get(base)
        if not files:
            continue

        base = base.__module__.rsplit('.', 1)[0]
        files = map(lambda (a, b): '/'.join((a, b)), zip(repeat(base), files))

        _context.action(
            discriminator = (
                'resourceInclude', layer, context, "".join(files)),
            callable = handler,
            args = (files, layer, context, _context.info),)


def handler(include, layer, context, info):
    """Set up includes.
    """
    global MANAGERS

    for path in include:
        try:
            extension =  path.rsplit('.', 1)[1]
        except IndexError:
            extension = None

        key = (layer, context, extension)

        manager = MANAGERS.get(key)
        if manager is None:
            # maintain order by creating a name that corresponds to
            # the current number of resource managers
            name = "%s-resource-manager-%03d" % (extension, len(MANAGERS))

            # create new resource manager
            MANAGERS[key] = manager = ResourceManagerFactory(name)

            # register as an adapter
            component.provideAdapter(
                manager, (layer, context), IDevelopmentResourceManager, name=name)

        manager.add(path)


def lookup_resources(managers):
    best_interface = lambda i1, i2: i1 if i1.extends(i2) else i2
    by_extension = {}
    managers = MANAGERS.items()
    managers.sort(key=lambda (k, m): m.identifier, reverse=True)
    for key, manager in managers:
        layer, context, extension = key
        by_layer = by_extension.setdefault(extension, {})
        managers = by_layer.setdefault(
            (tuple(set(list_base_layers(layer))),
             tuple(set(list_base_interfaces(context)))),
            [])
        managers.append(manager)
    for extension, layers in by_extension.iteritems():
        ordering = []
        for (layer, context), data in layers.iteritems():
            ordering.append((set(layer), set(context), data, []))
        ordering.sort(key=operator.itemgetter(0))
        for layer1, context1, data1, full_data1 in ordering:
            for layer2, context2, data2, full_data2 in ordering:
                if layer2.issubset(layer1):
                    if context2.issubset(context1):
                        full_data1.extend(data2)
                    elif data2 and layer1 != layer2:
                        # If we are not on the same entry and that
                        # entry is not generated, generate one
                        # possible combinaison.
                        ordering.append((layer1, context2, [], []))
        for layer, context, data, full_data in ordering:
            yield (reduce(best_interface, layer),
                   reduce(best_interface, context),
                   full_data,
                   extension)


@grok.subscribe(IProcessStarting)
def prepare_resources(event):
    global MANAGERS
    logger.info('Merging and packing resources ...')
    manager_count = 0
    for layer, context, managers, extension in lookup_resources(MANAGERS):
        logger.info('Merging: for %s and %s files %s (%s)' % (
                layer.__name__,
                context.__name__,
                ', '.join(
                    reduce(operator.add,
                           map(operator.attrgetter('names'), managers))),
                extension))

        merged_manager = ResourceManagerFactory('%s-merged-resources-%03d' % (
                extension, manager_count))
        manager_count += 1
        request = TestRequest()
        alsoProvides(request, layer)
        resources = []
        content_type = CONTENT_TYPES.get(extension)
        for manager in managers:
            resources.extend(filter(
                    lambda r: r.context.content_type == content_type,
                    manager(request, object()).get_resources()))

        by_path = {}
        previous_path = None
        order_path = []
        content_slimmer = SLIMMERS.get(content_type, lambda s:s)
        for resource in resources:
            base_path = os.path.sep.join(
                resource.context.path.split(os.path.sep)[:-1])
            if previous_path != base_path:
                order_path.append(base_path)
            by_path.setdefault(base_path, []).append(resource)
            previous_path = base_path

        for path in order_path:
            resources = by_path[path]
            merged_file = tempfile.TemporaryFile()

            for resource in resources:
                resource_file = open(resource.context.path, 'rb')
                print >> merged_file, "/* %s */" % resource.context.filename
                merged_file.write(content_slimmer(resource_file.read()))
                print >> merged_file, ""
                resource_file.close()

            # generate filename
            merged_file.seek(0)
            name = hashlib.sha1(merged_file.read()).hexdigest()

            existing_resource = component.queryAdapter(
                (TestRequest(),), name=name)
            if existing_resource is None:
                logger.debug('Registering merging of %s into %s (path %s)'  % (
                        ', '.join(map(lambda r: '/'.join(r.get_relative_path()),
                                      resources)),
                        name,
                        path))
                resource = MergedDirectoryResource(
                    name, path, MergedResource(merged_file, content_type))

                # register factory
                component.provideAdapter(
                    ResourceFactory(resource),
                    (IBrowserRequest,), Interface, name=name)

            merged_manager.add(name)

        component.provideAdapter(
            merged_manager,
            (layer, context), IProductionResourceManager, name=content_type)
