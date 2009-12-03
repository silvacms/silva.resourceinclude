
from zope import interface


class IResourceCollector(interface.Interface):
    """A resource collector is responsible for gathering resources
    that are available for it. It's usually instantiated with a
    browser request."""

    def collect():
        """Returns an ordered list of resources available for this
        collector."""

    def sort(resources):
        """Sort resources."""

    def merge(resources):
        """Merge resources."""

class IResourceManager(interface.Interface):
    """A resource manager is a container for resource registrations."""

    names = interface.Attribute(
        """The names of the resources that are registered with this manager.""")

    def add(name):
        """Adds a resource to the manager."""

    def available():
        """Returns a boolean value whether this manager is available."""
