# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import hashlib
import logging
import operator
import os.path
import cssmin
import tempfile

from zope import component
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest

from silva.resourceinclude.interfaces import IProductionResourceManager
from silva.resourceinclude.manager import ResourceManagerFactory
from silva.resourceinclude.utils import list_base_interfaces
from silva.resourceinclude.utils import list_base_layers
from silva.resourceinclude.resource import (
    MergedResource, MergedDirectoryResource, ResourceFactory)


SLIMMERS = {'text/css': cssmin.cssmin}
CONTENT_TYPES = {'js': 'application/javascript',
                 'css': 'text/css'}
logger = logging.getLogger('silva.resourceinclude')


def build_stack(master_level, d):
    for position, level in enumerate(master_level[1]):
        if level is None:
            continue
        if level[0][0].issuperset(d[0]):
            new_child = [level]
            master_level[1][position] = (d, [level])
            for other_position, other in enumerate(master_level[1][position + 1:]):
                if other is None:
                    continue
                if other[0][0].issuperset(d[0]):
                    new_child.append(other)
                    master_level[1][position + other_position + 1] = None
            break
        if level[0][0].issubset(d[0]):
            build_stack(level, d)
            break
    else:
        master_level[1].append((d, []))


def dump_stack(level, result):
    if level is None:
        return
    result.append(level[0])
    map(lambda l: dump_stack(l, result), level[1])


def partitioned_stack_sort(data):
    stack = ((set(),), [])
    for d in data:
        build_stack(stack, d)
    result = []
    dump_stack(stack, result)
    return result[1:]


def list_production_resources(managers):
    """This list for each different resource type all the couple of
    (layers, context) that can be used in production with all needed
    resources managers to include all needed resources for those
    couples.
    """
    best_interface = lambda i1, i2: i1 if i1.extends(i2) else i2
    by_extension = {}
    managers = managers.items()
    managers.sort(key=lambda (k, m): m.identifier)
    for (layer, context, extension), manager in managers:
        resources = by_extension.setdefault(extension, {})
        managers = resources.setdefault(
            (tuple(set(list_base_layers(layer))),
             tuple(set(list_base_interfaces(context)))),
            [])
        managers.append(manager)
    for extension, layers in by_extension.iteritems():
        ordering = []
        for (layer, context), data in layers.iteritems():
            ordering.append((set(layer), set(context), data, []))
        ordering = partitioned_stack_sort(ordering)
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


def merge_and_register_resources(path, resources, content_type):
    """Merge the different resources of the given path, and register
    them if it is not already done. Return the created name for the
    merged resource.
    """
    merged_file = tempfile.TemporaryFile()
    content_slimmer = SLIMMERS.get(content_type, lambda s:s)

    for resource in resources:
        resource_file = open(resource.context.path, 'rb')
        print >> merged_file, "/* %s */" % resource.context.filename
        merged_file.write(content_slimmer(resource_file.read()))
        print >> merged_file, ""
        resource_file.close()

    # generate filename
    merged_file.seek(0)
    name = hashlib.sha1(merged_file.read()).hexdigest()

    existing_resource = component.queryAdapter((TestRequest(),), name=name)
    if existing_resource is None:
        logger.debug('Registering merging of %s into %s (path %s)'  % (
                ', '.join(map(lambda r: '/'.join(r.get_relative_path()),
                              resources)),
                name,
                path))
        merged_resource = MergedDirectoryResource(
            name, path, MergedResource(merged_file, content_type))

        # register factory
        component.provideAdapter(
            ResourceFactory(merged_resource),
            (IBrowserRequest,), Interface, name=name)
    return name


def register_production_resources(development_managers):
    """Create and register production (aka merged and minized)
    resources out of the given development resources.
    """
    manager_count = 0
    for layer, context, managers, extension in list_production_resources(development_managers):
        logger.info('Inclusion for %s and %s files %s (%s)' % (
                layer.__name__,
                context.__name__,
                ', '.join(
                    reduce(operator.add,
                           map(operator.attrgetter('names'), managers))),
                extension))

        merged_manager = ResourceManagerFactory(
            '%s-merged-resources-%03d' % (extension, manager_count))
        manager_count += 1
        content_type = CONTENT_TYPES.get(extension)
        request = TestRequest()
        alsoProvides(request, layer)
        resources = []
        for manager in managers:
            resources.extend(filter(
                    lambda r: r.context.content_type == content_type,
                    manager(request, object()).get_resources()))

        by_path = {}
        order_path = []
        previous_path = None
        for resource in resources:
            base_path = os.path.sep.join(
                resource.context.path.split(os.path.sep)[:-1])
            if previous_path != base_path:
                order_path.append(base_path)
            by_path.setdefault(base_path, []).append(resource)
            previous_path = base_path

        for path in order_path:
            merged_manager.add(
                merge_and_register_resources(path, by_path[path], content_type))

        component.provideAdapter(
            merged_manager,
            (layer, context), IProductionResourceManager, name=content_type)
