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
CONTENT_TYPES = {'js': 'application/javascript', 'css': 'text/css'}
MERGED_BY_PATHS = {'js': False, 'css': True}
logger = logging.getLogger('silva.resourceinclude')


ID = 1

class Node(object):
    """Sorting tree.

    Add algorithm might create None nodes. Those are to be ignored.
    """
    parents = []
    children = []
    data = None
    visited = False

    def __init__(self, data, parents, children):
        global ID
        self.nid = ID
        ID += 1
        self.data = data
        self.parents = parents
        self.children = children

    def key(self):
        # Sorting key is the first data element.
        return self.data[0]

    def add(self, d):
        """Create a new node containing d somewhere as a relative child of
        node.
        """
        for position, child in enumerate(self.children):
            if child is None:
                continue
            if child.key().issuperset(d[0]):
                # We are a subset of the current node, but a super set of
                # one of its child. So we need to be the new parent of the
                # child, and the child of the current node.
                new_child_list = [child]
                new_node = self.__class__(d, [self], new_child_list)
                self.children[position] = new_node
                for other_position, other in enumerate(self.children[position + 1:]):
                    if other is None:
                        continue
                    if other.key().issuperset(d[0]):
                        new_child_list.append(other)
                        self.children[position + other_position + 1] = None
                for new_child in new_child_list:
                    # Update parent list in child list of new_node
                    parent_position = new_child.parents.index(self)
                    new_child.parents[parent_position] = new_node
                return new_node
            if child.key().issubset(d[0]):
                # We are a subset of that node. Go add had ourselves as
                # child of this one.
                new_node = child.add(d)
                # But we might be as well a subset of the other nodes, in
                # that case we need to be added as parents as well.
                for other_position, other in enumerate(self.children[position + 1:]):
                    if other is None:
                        continue
                    # XXX I don't know
                    if other.key().issubset(d[0]):
                        # XXX order, order, order.
                        new_node.parents.append(other)
                return new_node
        else:
            # We are not connected to any other children at this
            # level, so we get adopted.
            new_node = self.__class__(d, [self], [])

            # However, we can still be parents of other children childrens.
            for other in self.children:
                if other is None:
                    continue

                def parentify(node):
                    if node.key().issuperset(d[0]):
                        # Extra check
                        if not new_node in node.parents:
                            node.parents.append(new_node)
                            new_node.children.append(node)
                            node.visitor(lambda n: None, children_only=True)

                other.visitor(parentify)

            self.children.append(new_node)
            self.reset()
            return new_node

    def dump(self, result):
        """Do a left-hand run through the graph to dump its content in
        order.
        """
        self.visitor(lambda n: result.append(n.data))

    def visitor(self, action, children_only=False):
        """Visit nodes in order and execute the given action on them.
        """
        if self.visited:
            return
        self.visited = True

        def visit(nodes):
            for node in nodes:
                if node is not None:
                    node.visitor(action, children_only=children_only)

        if not children_only:
            visit(self.parents)
        action(self)
        visit(self.children)

    def reset(self):
        """Reset the visit marker.
        """
        if not self.visited:
            return
        self.visited = False

        def reset(nodes):
            for node in nodes:
                if node is not None:
                    node.reset()

        reset(self.parents)
        reset(self.children)

    def dot(self):
        nodes = []
        rels = []

        def dot_visitor(node):
            nodes.append('%s [label="%r"];' % (node.nid, node.key()))
            for child in node.children:
                if child is not None:
                    rels.append('%s -> %s;' % (node.nid, child.nid))

        self.visitor(dot_visitor)
        return 'digraph resources {\n' + '\n'.join(nodes + rels) + '}'



def sort_tuple(data):
    """Build a set of directed graphs based on the inclusion relation
    of the first set of each element of data in order to sort them.

    As the graph represent Python class, we cannot get cycles.
    """
    root = Node((set(),), [], [])
    for d in data:
        root.add(d)
    result = []
    root.dump(result)
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
            ordering.append((set(layer), set(context), data, [], True))
        ordering = sort_tuple(ordering)
        generated = []

        def generate(layer, context):
            info = (layer, context)
            if info not in generated:
                generated.append(info)
                ordering.append((layer, context, [], [], False))

        for layer1, context1, data1, full_data1, original1 in ordering:
            for layer2, context2, data2, full_data2, original2 in ordering:
                if layer2.issubset(layer1):
                    if data2:
                        if context2.issubset(context1):
                            full_data1.extend(data2)
                            if context1 != context2 and original1:
                                generate(layer1, context2)
                        elif layer1 != layer2 and original2:
                            # If we are not on the same entry and that
                            # entry is not generated, generate one
                            # possible combinaison
                            generate(layer1, context2)
        for layer, context, data, full_data, original in ordering:
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

        if not MERGED_BY_PATHS[extension]:
            merged_manager.add(
                merge_and_register_resources('/', resources, content_type))
        else:
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
