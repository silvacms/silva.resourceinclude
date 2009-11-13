# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


"""
    Grokking the module...
    >>> grok('silva.resourceinclude.tests.resources.collector')
    
    We need a test request.
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    
    If we adapts the request with the IResourceCollector we should
    get one.
    >>> from z3c.resourceinclude.interfaces import IResourceCollector
    >>> collector = IResourceCollector(request)
    >>> collector
    <silva.resourceinclude.collector.ResourceCollector object at ...>
"""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from silva.core import conf as silvaconf

class ITestLayer(IDefaultBrowserLayer):
    silvaconf.resource('styles.css')


