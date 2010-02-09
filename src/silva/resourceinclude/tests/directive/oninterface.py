# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
"""
    We can only use resource martian directive on a layer:
    >>> grok('silva.resourceinclude.tests.directive.oninterface')
    Traceback (most recent call last):
        ...
    GrokError: A resource can be included only on a layer.

"""

from zope.interface import Interface
from silva.core import conf as silvaconf


class ITestLayer(Interface):
    silvaconf.resource('styles.css')


