# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import interface


class IResource(interface.Interface):
    """A resource.
    """
    filename = interface.Attribute(
        "Published name of the resource")
    path = interface.Attribute(
        "Filesystem path to the resource")
    content_type = interface.Attribute(
        "Content type of the resource")
    lmt = interface.Attribute(
        "Last modification time for the resource")


class IResourceCollector(interface.Interface):
    """A resource collector is responsible for gathering resources
    that are available for it. It's usually instantiated with a
    browser request.
    """
    def collect():
        """Returns an ordered list of resources available for this
        collector.
        """

    def sort(resources):
        """Sort resources.
        """

    def merge(resources):
        """Merge resources.
        """


class IResourceManager(interface.Interface):
    """A resource manager is a container for resource registrations.
    """
    names = interface.Attribute(
        "Names of the resources that are registered with this manager.")

    def add(name):
        """Adds a resource to the manager.
        """

    def available():
        """Returns a boolean value whether this manager is available.
        """
