# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from silva.core import conf as silvaconf


class ITestLayer(IDefaultBrowserLayer):
    silvaconf.resource('style.css')
    silvaconf.resource('file1.js')
    silvaconf.resource('file2.js')
