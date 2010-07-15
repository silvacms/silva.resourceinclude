silva.resourceinclude
=====================

silva.resourceinclude collect and merge resources files (CSS, KSS, JS)
on layers. It was based on `z3c.resourceinclude`_. It's used by
``silva.core.layout`` to easily include resources in Silva Layouts.

It provides as well a full implementation of the Zope resource export
mechanism for Zope 2, that properly implement HEAD requests and are
optimized for caching purpose.

.. _z3c.resourceinclude: http://pypi.python.org/pypi/z3c.resourceinclude
