# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
"""
    First we need to grok our test and the test resources:
    >>> grok('silva.resourceinclude.tests.collector')

    We need a test request:
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()

    If we adapts the request with the IResourceCollector we should
    get one:
    >>> from zope import component
    >>> from silva.resourceinclude.interfaces import IResourceCollector
    >>> collector = component.getMultiAdapter(
    ...      (object(), request), IResourceCollector)
    >>> collector
    <silva.resourceinclude.collector.ResourceCollector object at ...>
    >>> verifyObject(IResourceCollector, collector)
    True

    Our request in our case doesn't have any layer by default, so we
    don't have any resources associated:
    >>> collector.collect()
    ()

    Now let's get a request which use our test layer:
    >>> from silva.resourceinclude.tests.collector.collector import ITestLayer
    >>> request = TestRequest(skin=ITestLayer)
    >>> collector = component.getMultiAdapter(
    ...      (object(), request), IResourceCollector)

    There is some resources now:
    >>> collector.collect()
    ()

"""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from silva.core import conf as silvaconf


class ITestLayer(IDefaultBrowserLayer):
    silvaconf.resource('styles.css')


