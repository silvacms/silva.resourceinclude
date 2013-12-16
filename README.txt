=====================
silva.resourceinclude
=====================

``silva.resourceinclude`` collect and merge resources files (CSS, KSS,
JS) on layers. It was based on `z3c.resourceinclude`_. It's used by
``silva.core.layout`` to easily include resources in Silva themes for
Silva 2.x. In Silva 3, ``silva.fanstatic`` replaces this extension.

It provides as well a full implementation of the Zope resource export
mechanism for Zope 2, that properly implement HEAD requests and are
optimized for caching purpose.

Please refer to the official Silva documentation to see how to use it.

Code repository
===============

You can find the source code for this extension in Git:
https://github.com/silvacms/silva.resourceinclude


.. _z3c.resourceinclude: http://pypi.python.org/pypi/z3c.resourceinclude
