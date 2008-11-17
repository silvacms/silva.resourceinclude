# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.app.testing.placelesssetup import tearDown as _cleanUp
def cleanUp():
    """Cleans up the component architecture.
    """
    _cleanUp()
    import Products.Five.zcml as zcml
    zcml._initialized = 0

def setDebugMode(mode):
    """Allows manual setting of Five's inspection of debug mode
    to allow for ZCML to fail meaningfully.
    """
    import Products.Five.fiveconfigure as fc
    fc.debug_mode = mode

import five.resourceinclude
def loadSite():
    """Loads extension.
    """
    cleanUp()
    setDebugMode(1)
    import Products.Five.zcml as zcml
    zcml.load_site()
    zcml.load_config('meta.zcml', silva.resourceinclude)
    zcml.load_config('configure.zcml', silva.resourceinclude)
    setDebugMode(0)


from Testing.ZopeTestCase.layer import ZopeLite

class ResourceIncludeLayer(ZopeLite):

    @classmethod
    def setUp(self):
        loadSite()

    @classmethod
    def tearDown(self):
        cleanUp()

