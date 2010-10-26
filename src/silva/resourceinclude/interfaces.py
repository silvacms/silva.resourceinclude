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
    content_length = interface.Attribute(
        "Content length of the resource")
    lmt = interface.Attribute(
        "Last modification time for the resource")

    def __getitem__(name):
        """Return sub-resource packaged in that one.
        """

    def data():
        """Return data to send to the client.
        """


class IResourceCollector(interface.Interface):
    """A resource collector is responsible for gathering resources
    that are available for it. It's usually instantiated with a
    browser request.
    """

    def get_managers():
        """Return the list of manager providing resources for this
        collector.

        Manager should by sorted by order of inclusion of the
        resources.
        """

    def collect():
        """Returns an ordered list of resources available for this
        collector.
        """


class IResourceManager(interface.Interface):
    """A resource manager is a container for resource registrations.
    """
    identifier = interface.Attribute(
        "Unique identifier for this manager.")
    names = interface.Attribute(
        "Names of the resources that are registered with this manager.")

    def get_resources():
        """Return resources of the manager.
        """

    def search_resource(name):
        """Look for the given resource.
        """


class IDevelopmentResourceManager(IResourceManager):
    """Contains all resources for development, i.e. all files not
    merged. Usally for a layer and a context, more than one
    development resource manager is found and used.
    """


class IProductionResourceManager(IResourceManager):
    """Contains all resources for production, i.e. merged and
    compressed files. Usually for a alyer and a context, only one
    production manager is found.
    """

